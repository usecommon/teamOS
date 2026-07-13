"""WO-1: earned-autonomy enforcement for the gate (kept out of gate.py to hold
its 300-line reviewability budget, X-1).

A clean, side-effectful action is auto-permitted only once the principal has
EARNED autonomy in that category — the envelope level, raised by
principal-attributed acceptances (FK6b). Below the floor the gate ASKS (the
high-touch labeling period, §7.4). Read-only: the gate READS the level, never
writes it (the state file is a protected path — the agent can't widen its own
envelope). Unset/absent/corrupt state => unconfigured => no envelope gating
(safety findings in the gate still bite). Deterministic; no model (SE-1)."""

import json
import os
from pathlib import Path

ENFORCE_LEVEL = 1
CATEGORY = {"write": "write", "edit": "write", "send": "send",
            "execute": "execute", "schedule": "schedule"}


def level(action_class):
    """Earned level for the action's category, or None when unconfigured (no
    state path / missing / unreadable) — None means no envelope gating."""
    state_path = os.environ.get("TEAMOS_ENVELOPE_STATE")
    category = CATEGORY.get(action_class)
    if not state_path or category is None:
        return None
    try:
        state = json.loads(Path(state_path).read_text())
        lvl = state.get("levels", {}).get(category)
        return lvl if isinstance(lvl, int) else None
    except (OSError, ValueError):
        return None


def apply(action_class, verdict, rule_id, checks, findings):
    """Downgrade a clean side-effectful permit to ask when the category's earned
    level is below the floor. Only ever ADDS friction — never turns a safety
    ask/deny into a permit — so the envelope cannot weaken the gate. Mutates
    checks/findings; returns the (possibly adjusted) (verdict, rule_id)."""
    if verdict != "permit" or action_class not in CATEGORY:
        return verdict, rule_id
    lvl = level(action_class)
    if lvl is None or lvl >= ENFORCE_LEVEL:
        return verdict, rule_id
    checks.append("envelope-level-check")
    findings.append(f"envelope:{CATEGORY[action_class]}={lvl}<{ENFORCE_LEVEL}")
    return "ask", "envelope-hold"
