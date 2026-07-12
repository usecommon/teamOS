"""Subagent spawn ledger — agents may spin up subagents as needed, and every
spawn is recorded (parent → child, task, depth) so the autonomy is auditable.

T9: depth and rate are ENFORCED at record time, not self-reported — depth is
computed from the parent's recorded depth in the ledger, and a spawn past the
depth or rate bound raises SpawnRefused (the safety agent additionally trips
the breaker when the recorded ledger shows a breach).
"""

import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hashchain  # noqa: E402

SPAWN_AGENT_ID = "teamos-spawn/0.1"
MAX_DEPTH = 3   # arbitrary-pending-baseline
MAX_RATE = 20   # spawns per window
RATE_WINDOW_HOURS = 1


class SpawnRefused(RuntimeError):
    pass


def record(ledger_dir, parent, child, task, depth=None, now=None):
    """Record a spawn. Depth is COMPUTED from the parent's ledger entry
    (self-reported `depth` is ignored); refuses depth > MAX_DEPTH and more
    than MAX_RATE spawns inside the rate window."""
    rows = load(ledger_dir)
    known_depths = {r["child"]: r["depth"] for r in rows}
    actual_depth = known_depths.get(parent, 0) + 1
    if actual_depth > MAX_DEPTH:
        raise SpawnRefused(
            f"spawn depth {actual_depth} exceeds MAX_DEPTH={MAX_DEPTH} "
            f"({parent} -> {child})")
    now = now or datetime.now(timezone.utc)
    cutoff = (now - timedelta(hours=RATE_WINDOW_HOURS)).isoformat().replace(
        "+00:00", "Z")
    recent = [r for r in rows if r.get("ts", "") >= cutoff]
    if len(recent) >= MAX_RATE:
        raise SpawnRefused(
            f"spawn rate {len(recent) + 1} exceeds MAX_RATE={MAX_RATE} "
            f"per {RATE_WINDOW_HOURS}h window")
    return hashchain.append(Path(ledger_dir) / "spawns.jsonl", {
        "parent": parent, "child": child, "task": task, "depth": actual_depth,
    }, SPAWN_AGENT_ID)


def load(ledger_dir):
    p = Path(ledger_dir) / "spawns.jsonl"
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()] if p.exists() else []


def stats(ledger_dir):
    rows = load(ledger_dir)
    return {"count": len(rows), "max_depth": max((r["depth"] for r in rows), default=0)}
