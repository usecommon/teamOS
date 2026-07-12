"""Subagent spawn ledger — agents may spin up subagents as needed, and every
spawn is recorded (parent → child, task, depth) so the autonomy is auditable.
Depth and rate bounds are checked by the safety agent, which trips the breaker
if they're exceeded.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hashchain  # noqa: E402

SPAWN_AGENT_ID = "teamos-spawn/0.1"
MAX_DEPTH = 3   # arbitrary-pending-baseline
MAX_RATE = 20   # spawns per window


def record(ledger_dir, parent, child, task, depth=1):
    return hashchain.append(Path(ledger_dir) / "spawns.jsonl", {
        "parent": parent, "child": child, "task": task, "depth": depth,
    }, SPAWN_AGENT_ID)


def load(ledger_dir):
    p = Path(ledger_dir) / "spawns.jsonl"
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()] if p.exists() else []


def stats(ledger_dir):
    rows = load(ledger_dir)
    return {"count": len(rows), "max_depth": max((r["depth"] for r in rows), default=0)}
