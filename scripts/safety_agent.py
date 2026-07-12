"""Safety agent — a common, always-running monitor over the other agents. It
watches the ledgers (gate denials, human rejections, subagent spawn depth/rate)
and TRIPS THE CIRCUIT BREAKER when a threshold is crossed. Deterministic rules,
no language model (a monitor that could be prompt-injected is not a monitor).
It can only trip (halt) — it can never widen autonomy or reset the breaker.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import circuit_breaker
import hashchain
import spawn as spawnmod

SAFETY_AGENT_ID = "teamos-safety/0.1"
THRESHOLDS = {
    "gate_denials": 5,      # gate denials in the window
    "rejections": 5,        # principal rejections (L8) in the window
    "spawn_depth": spawnmod.MAX_DEPTH,
    "spawn_rate": spawnmod.MAX_RATE,
}


def _count(path, pred):
    if not Path(path).exists():
        return 0
    return sum(1 for l in Path(path).read_text().splitlines()
               if l.strip() and pred(json.loads(l)))


def check(ledger_dir, safety_log, breaker_state):
    ledger_dir = Path(ledger_dir)
    metrics = {
        "gate_denials": _count(ledger_dir/"l2.jsonl",
                               lambda r: r["verdict"] == "deny" and not r["rule_id"].startswith("circuit")),
        "rejections": _count(ledger_dir/"l8.jsonl", lambda r: r.get("signal_type") == "rejection"),
        "spawn_depth": spawnmod.stats(ledger_dir)["max_depth"],
        "spawn_rate": spawnmod.stats(ledger_dir)["count"],
    }
    breaches = [k for k, v in metrics.items() if v >= THRESHOLDS[k]]
    status = "tripped" if breaches else "ok"
    if breaches:
        circuit_breaker.trip(ledger_dir, breaker_state, "safety-agent",
                             f"threshold breach: {', '.join(breaches)}")
    hashchain.append(Path(safety_log), {
        "status": status, "metrics": metrics, "thresholds": THRESHOLDS,
        "breaches": breaches,
        "checked_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }, SAFETY_AGENT_ID)
    return {"status": status, "metrics": metrics, "breaches": breaches}
