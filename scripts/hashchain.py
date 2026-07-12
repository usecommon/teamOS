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


def _tail_line(f, chunk=65536):
    """Last non-empty line via seek from the end — O(tail), not O(file)."""
    f.seek(0, os.SEEK_END)
    size = f.tell()
    if size == 0:
        return None
    buf = b""
    pos = size
    while pos > 0:
        step = min(chunk, pos)
        pos -= step
        f.seek(pos)
        buf = f.read(step) + buf
        lines = [l for l in buf.split(b"\n") if l.strip()]
        if len(lines) >= 2 or (lines and pos == 0):
            return lines[-1].decode("utf-8")
    return None


def last_hash(path):
    path = Path(path)
    if not path.exists() or path.stat().st_size == 0:
        return None
    with path.open("rb") as f:
        last = _tail_line(f)
    return json.loads(last)["hash"] if last else None


def append(path, body, agent_id, schema_version="0.1", record_id=None):
    """Chain `body` onto the ledger at `path`. Returns the full record.

    Serialized: an exclusive flock spans read-last-hash + write, so parallel
    writers (subagents, hooks, loops) can never fork the chain (T5)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+b") as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        try:
            last = _tail_line(f)
            prev = json.loads(last)["hash"] if last else None
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
