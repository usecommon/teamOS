"""Circuit breaker — a halt switch any principal OR the safety agent can trip.
When OPEN, the gate denies every side-effectful action (write/edit/send/execute/
schedule); reads stay allowed. Trips and resets are ledgered (L2), so the halt
itself is auditable. Autonomy is bounded by construction: an agent can spin up
subagents and act freely, but the breaker is the always-present kill switch.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hashchain  # noqa: E402

CB_AGENT_ID = "teamos-circuit-breaker/0.1"
SIDE_EFFECTS = ("write", "edit", "send", "execute", "schedule")


def load(state_path):
    p = Path(state_path)
    if p.exists():
        return json.loads(p.read_text())
    return {"state": "closed", "tripped_by": None, "reason": None, "at": None}


def is_open(state_path):
    return load(state_path)["state"] == "open"


def _ledger(ledger_dir, verdict, rule, by, reason):
    hashchain.append(Path(ledger_dir) / "l2.jsonl", {
        "proposed_action": {"tool": "circuit_breaker", "action_class": "config",
                            "target": f"{rule}:{by}",
                            "payload_digest": hashchain.sha256_str(str(reason))},
        "verdict": verdict, "policy_version": "circuit-breaker:0.1", "rule_id": rule,
        "inspection": {"checks_run": ["breaker-transition"], "findings": [str(reason)] if reason else []},
        "outcome": "gate_blocked" if verdict == "deny" else "gate_passed",
    }, CB_AGENT_ID)


def trip(ledger_dir, state_path, by, reason):
    """Open the breaker. `by` = a principal id or 'safety-agent'."""
    Path(state_path).write_text(json.dumps(
        {"state": "open", "tripped_by": by, "reason": reason, "at": hashchain.utc_now()}))
    _ledger(ledger_dir, "deny", "circuit-breaker-trip", by, reason)


def reset(ledger_dir, state_path, by):
    """Close the breaker (manual — resetting is never automatic)."""
    Path(state_path).write_text(json.dumps(
        {"state": "closed", "tripped_by": None, "reason": None, "at": hashchain.utc_now()}))
    _ledger(ledger_dir, "permit", "circuit-breaker-reset", by, None)
