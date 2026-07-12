#!/usr/bin/env python3
"""Session-granular taint tracking (FR2 Layer A, fork §7.7).

Untrusted content (corpus, inbox, external fetches, A2A, historical) supplies
VALUES, never plan structure. At session granularity (in scope at n<=3;
datum-granular is mainline-deferred) that means: once a session has read
untrusted content, any send/schedule whose target could derive from it requires
human confirmation. This is the compensating layer the verbatim-secret scan
explicitly does not carry (X-2) — it is what stops paraphrase-exfil and
attacker-chosen recipients (e.g. WebFetch(url=...?d=<corpus paraphrase>)).

Also holds the scan-hardening helpers (Layer B): shell-quoting normalization
and base64-blob decoding, so gate.py stays inside its line budget.

Deterministic code; no language model. State: one JSON file per session under
<ledger_dir>/taint/.
"""

import base64
import binascii
import json
import re
from pathlib import Path

# candidate base64 runs worth decoding (std + urlsafe alphabets)
_B64_RUN = re.compile(r"[A-Za-z0-9+/_-]{32,}={0,2}")
# characters attackers interleave to break substring matches: cu'r'l, cu"r"l, cu\rl
_QUOTING = re.compile(r"""["'`\\]""")
_WS = re.compile(r"\s+")


def _state_path(taint_dir, session_id):
    safe = re.sub(r"[^A-Za-z0-9_.-]", "_", str(session_id) or "unknown")
    return Path(taint_dir) / f"{safe}.json"


def mark(taint_dir, session_id, source, detail=""):
    """Record that untrusted content entered this session."""
    path = _state_path(taint_dir, session_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    state = {"tainted": True, "sources": []}
    if path.exists():
        try:
            state = json.loads(path.read_text())
        except ValueError:
            pass  # corrupt state stays tainted-true below
    state["tainted"] = True
    entry = {"source": source, "detail": str(detail)[:200]}
    if entry not in state.setdefault("sources", []):
        state["sources"].append(entry)
    path.write_text(json.dumps(state))
    return state


def is_tainted(taint_dir, session_id):
    """True if the session has read untrusted content. A corrupt/unreadable
    state file counts as TAINTED (fail closed)."""
    path = _state_path(taint_dir, session_id)
    if not path.exists():
        return False
    try:
        return bool(json.loads(path.read_text()).get("tainted", True))
    except (ValueError, OSError):
        return True


def taints(policy, tool_name, action_class, target):
    """Does this call bring untrusted content into the session?
    Returns a source label or None."""
    if tool_name in policy.get("taint_source_tools", []):
        return f"tool:{tool_name}"
    if action_class == "read":
        for root in policy.get("taint_source_paths", []):
            if root in str(target):
                return f"path:{root}"
    return None


def normalize_command(command, lower=True):
    """Defeat quoting/whitespace obfuscation before substring matching:
    strip quote/escape chars, collapse whitespace, optionally casefold."""
    text = _QUOTING.sub("", str(command))
    text = _WS.sub(" ", text)
    return text.casefold() if lower else text


_WORD = re.compile(r"[a-z0-9]+")
_CORPUS_CACHE = {}  # (dir, files-mtime-signature) -> frozenset(shingle strings)


def _shingles(text, k):
    toks = _WORD.findall(str(text).lower())
    return {" ".join(toks[i:i + k]) for i in range(len(toks) - k + 1)}


def _corpus_shingles(corpus_dir, k):
    """k-word shingle set of all stored corpus text, cached by file mtimes.
    Rebuilt only when the corpus changes."""
    p = Path(corpus_dir)
    if not p.exists():
        return frozenset()
    files = sorted(f for f in p.rglob("*") if f.is_file())
    sig = tuple((str(f), f.stat().st_mtime_ns) for f in files)
    key = (str(corpus_dir), sig)
    if key in _CORPUS_CACHE:
        return _CORPUS_CACHE[key]
    sh = set()
    for f in files:
        try:
            sh |= _shingles(f.read_text(errors="ignore"), k)
        except OSError:
            continue
    fs = frozenset(sh)
    _CORPUS_CACHE.clear()          # keep only the latest corpus snapshot
    _CORPUS_CACHE[key] = fs
    return fs


def matches_corpus(policy, texts, repo_root):
    """A7 / Option-B: does outbound content carry a distinctive run of STORED
    corpus text? Catches corpus exfil on an UNTAINTED first move — before any
    in-session corpus read — which the taint layer alone misses (e.g. attacker-
    injected WebFetch(url=...?d=<verbatim corpus>)). Word-shingle overlap, so
    URL-encoding / underscores / casing collapse to the same tokens. Heuristic
    defense-in-depth; the session taint layer remains the primary control. The
    caller folds this into the taint-confirm ask (gate.py stays within budget)."""
    cfg = policy.get("corpus_fingerprint") or {}
    if not cfg.get("enabled"):
        return False
    k = cfg.get("shingle_k", 6)
    need = cfg.get("min_shingles", 1)
    corpus = _corpus_shingles(Path(repo_root) / cfg.get("corpus_dir", "stores/corpus"), k)
    if not corpus:
        return False
    out = set()
    for t in texts:
        out |= _shingles(t, k)
        if len(out & corpus) >= need:
            return True
    return False


def decode_base64_blobs(texts, limit=32):
    """Best-effort decode of base64-looking runs so the secret scan sees
    through one encoding layer. Returns decoded strings (utf-8, lossy)."""
    decoded = []
    for text in texts:
        for run in _B64_RUN.findall(str(text))[:limit]:
            for decoder in (base64.b64decode, base64.urlsafe_b64decode):
                try:
                    raw = decoder(run + "=" * (-len(run) % 4))
                except (binascii.Error, ValueError):
                    continue
                out = raw.decode("utf-8", errors="ignore")
                if len(out) >= 8:
                    decoded.append(out)
                break
    return decoded
