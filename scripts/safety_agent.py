"""Safety agent — a common, always-running monitor over the other agents. It
watches the ledgers (gate denials, human rejections, subagent spawn depth/rate)
and TRIPS THE CIRCUIT BREAKER when a threshold is crossed. Deterministic rules,
no language model (a monitor that could be prompt-injected is not a monitor).
It can only trip (halt) — it can never widen autonomy or reset the breaker.

T9: counters are WINDOWED (sliding ts window, default 24h) so a human reset
recovers instead of re-tripping forever on lifetime totals; rejections are
counted only from verified principal identity (CN-1) so a stranger's ✗ spike
can't halt the system. Invoked on the loop pre-flight path (loop.py), not
only in tests.
"""

import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import circuit_breaker
import hashchain
import principal_auth
import spawn as spawnmod

SAFETY_AGENT_ID = "teamos-safety/0.1"
WINDOW_HOURS = 24
THRESHOLDS = {
    "gate_denials": 5,      # gate denials in the window
    "rejections": 5,        # verified principal rejections (L8) in the window
    "spawn_depth": spawnmod.MAX_DEPTH,
    "spawn_rate": spawnmod.MAX_RATE,
}


def _iso(dt):
    return dt.isoformat().replace("+00:00", "Z")


def _rows(path):
    p = Path(path)
    if not p.exists():
        return []
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()]


def check(ledger_dir, safety_log, breaker_state, window_hours=WINDOW_HOURS,
          now=None):
    ledger_dir = Path(ledger_dir)
    now = now or datetime.now(timezone.utc)
    cutoff = _iso(now - timedelta(hours=window_hours))

    def windowed(rows):
        return [r for r in rows if r.get("ts", "") >= cutoff]

    l2 = windowed(_rows(ledger_dir / "l2.jsonl"))
    l8 = windowed(_rows(ledger_dir / "l8.jsonl"))
    spawns = windowed(spawnmod.load(ledger_dir))
    metrics = {
        "gate_denials": sum(1 for r in l2 if r["verdict"] == "deny"
                            and not r["rule_id"].startswith("circuit")),
        # CN-1: an unattributed/forged ✗ never counts toward a halt
        "rejections": sum(1 for r in l8 if r.get("signal_type") == "rejection"
                          and principal_auth.verified(r)),
        "spawn_depth": max((r["depth"] for r in spawns), default=0),
        "spawn_rate": len(spawns),
    }
    breaches = [k for k, v in metrics.items() if v >= THRESHOLDS[k]]
    status = "tripped" if breaches else "ok"
    if breaches:
        circuit_breaker.trip(ledger_dir, breaker_state, "safety-agent",
                             f"threshold breach: {', '.join(breaches)}")
    hashchain.append(Path(safety_log), {
        "status": status, "metrics": metrics, "thresholds": THRESHOLDS,
        "breaches": breaches, "window_hours": window_hours,
        "checked_at": _iso(now),
    }, SAFETY_AGENT_ID)
    return {"status": status, "metrics": metrics, "breaches": breaches}
