"""Hash-chained append-only JSONL ledgers (FK2). ONE implementation, every
entry point (adapter, gate hook, L3/L8 writers) imports this — two drifting
chain implementations is the FR2 failure mode.

Formula: hash = sha256((prev_hash or "") + canonical(record_without_hash)).
"""

import fcntl
import hashlib
import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def sha256_str(data):
    if isinstance(data, str):
        data = data.encode("utf-8")
    return "sha256:" + hashlib.sha256(data).hexdigest()


def utc_now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def record_hash(prev_hash, body):
    return sha256_str((prev_hash or "") + canonical(body))


def envelope(record, prev_hash, record_id, ts, agent_id, schema_version):
    record.update(
        record_id=record_id,
        ts=ts,
        schema_version=schema_version,
        agent_id=agent_id,
        prev_hash=prev_hash,
    )
    record["hash"] = record_hash(prev_hash, record)
    return record


def _iter_tail_lines(f, chunk=65536):
    """Yield non-empty lines from the end backward (bytes). O(tail) per line."""
    f.seek(0, os.SEEK_END)
    pos = f.tell()
    buf = b""
    while pos > 0:
        step = min(chunk, pos)
        pos -= step
        f.seek(pos)
        buf = f.read(step) + buf
        parts = buf.split(b"\n")
        buf = parts[0]  # possibly-incomplete leading fragment; carry to next read
        for line in reversed(parts[1:]):
            if line.strip():
                yield line
    if buf.strip():
        yield buf


def _last_valid_hash(f):
    """Last record's hash, tolerant of a torn TRAILING fragment (E1): a crash
    mid-append leaves a partial last line — skip trailing lines that don't parse
    to a record with a "hash" and return the last valid one. Interior corruption
    is NOT skipped here; verify() still catches it."""
    for line in _iter_tail_lines(f):
        try:
            rec = json.loads(line)
        except (ValueError, UnicodeDecodeError):
            continue  # torn/partial fragment from a crashed write — skip
        if isinstance(rec, dict) and "hash" in rec:
            return rec["hash"]
    return None


def _truncate_torn_tail(f):
    """Remove trailing bytes with no terminating newline (E1). Complete records
    are always '\\n'-terminated + fsynced; bytes after the final newline are a
    crashed partial write — drop them so the chain stays clean and append can
    proceed. Leaves all complete records (and any interior corruption) intact."""
    f.seek(0, os.SEEK_END)
    size = f.tell()
    if size == 0:
        return
    f.seek(size - 1)
    if f.read(1) == b"\n":
        return  # ends cleanly on a record boundary
    pos, chunk, buf = size, 65536, b""
    while pos > 0:
        step = min(chunk, pos)
        pos -= step
        f.seek(pos)
        buf = f.read(step) + buf
        idx = buf.rfind(b"\n")
        if idx != -1:
            f.truncate(pos + idx + 1)
            return
    f.truncate(0)  # no newline anywhere — the whole file is a torn fragment


def last_hash(path):
    path = Path(path)
    if not path.exists() or path.stat().st_size == 0:
        return None
    with path.open("rb") as f:
        return _last_valid_hash(f)


def append(path, body, agent_id, schema_version="0.1", record_id=None):
    """Chain `body` onto the ledger at `path`. Returns the full record.

    Serialized: an exclusive flock spans read-last-hash + write, so parallel
    writers (subagents, hooks, loops) can never fork the chain (T5). A torn
    trailing fragment from a crashed prior append is healed before writing (E1)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+b") as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        try:
            _truncate_torn_tail(f)
            prev = _last_valid_hash(f)
            record = envelope(
                dict(body),
                prev,
                record_id or f"{path.stem}-{uuid.uuid4().hex[:12]}",
                utc_now(),
                agent_id,
                schema_version,
            )
            f.seek(0, os.SEEK_END)
            f.write((canonical(record) + "\n").encode("utf-8"))
            f.flush()
            os.fsync(f.fileno())
        finally:
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    return record


def verify(path):
    """Verify the whole chain. Returns record count; raises on any break."""
    path = Path(path)
    prev, count = None, 0
    with path.open() as f:
        for n, line in enumerate(f, start=1):
            if not line.strip():
                continue
            record = json.loads(line)
            body = {k: v for k, v in record.items() if k != "hash"}
            if record.get("prev_hash") != prev:
                raise ValueError(f"{path}:{n}: prev_hash mismatch — chain broken")
            if record["hash"] != record_hash(prev, body):
                raise ValueError(f"{path}:{n}: hash mismatch — record tampered")
            prev = record["hash"]
            count += 1
    return count
