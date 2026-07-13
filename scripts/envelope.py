"""Autonomy envelope-by-script (FK6b). Permission levels per action-category,
relaxed on PRINCIPAL-ATTRIBUTED L8 evidence only (CN-1).

Asymmetric trust (OB-1): narrowing is AUTOMATED and immediate — one
principal-attributed rejection above the severity class steps the envelope down
a notch at once. Widening is SLOW — it accumulates principal-attributed
acceptances to a threshold, and during FK6 the threshold is multiplied
(builder-footprint handicap, OB-3) so collaborators don't inherit an autonomy
trajectory calibrated on the builder's effort-inflated ✓ rate.

The script may raise a level only WITHIN its pre-declared ceiling
(config/envelope-policy.json, a protected path); it can never touch its own
ceiling. Every change emits an L2 record and is reversible. A forged /
unattributed reaction never widens (CN-1). No language model.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hashchain  # noqa: E402
import principal_auth  # noqa: E402
from fsutil import atomic_write_text  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
POLICY_PATH = REPO_ROOT / "config" / "envelope-policy.json"
ENV_AGENT_ID = "teamos-envelope/0.1"
LIGHT_EDIT = 0.2


def load_policy(path=None):
    return json.loads(Path(path or POLICY_PATH).read_text())


def _policy_version(path=None):
    return hashchain.sha256_str(Path(path or POLICY_PATH).read_text())


def load_state(state_path, policy):
    state_path = Path(state_path)
    if state_path.exists():
        return json.loads(state_path.read_text())
    return {
        "levels": {c: v["base"] for c, v in policy["categories"].items()},
        "accept_counters": {c: 0 for c in policy["categories"]},
        "history": [],
    }


def _save(state, state_path):
    atomic_write_text(state_path, json.dumps(state, indent=2))


def _ledger_change(ledger_dir, category, frm, to, rule, policy_path):
    hashchain.append(Path(ledger_dir) / "l2.jsonl", {
        "proposed_action": {
            "tool": "envelope",
            "action_class": "config",
            "target": f"{category}:{frm}->{to}",
            "payload_digest": hashchain.sha256_str(f"{category}:{frm}:{to}:{rule}"),
        },
        "verdict": "permit",
        "policy_version": _policy_version(policy_path),
        "rule_id": rule,
        "inspection": {"checks_run": ["envelope-transition"], "findings": []},
        "outcome": "gate_passed",
    }, ENV_AGENT_ID)


def _widen_threshold(policy, posture):
    t = policy["widen_threshold"]
    return t * policy["fk6_widen_multiplier"] if posture == "fk6" else t


def process_signal(l8_record, category, ledger_dir, state_path,
                   policy_path=None, posture="fk6"):
    """Feed one L8 signal for `category`. Returns the new level for that category.

    Widen only on principal-attributed, light-edited acceptances at threshold.
    Narrow immediately on a principal-attributed rejection (or heavy edit).
    Unattributed signals are ignored for both directions (CN-1).
    """
    policy = load_policy(policy_path)
    state = load_state(state_path, policy)
    ceiling = policy["categories"][category]["ceiling"]
    level = state["levels"][category]

    # CN-1/T7: cryptographically verified when a principal keydir is
    # configured; a bare attribution field is a claim, not evidence.
    # WO-2: verified_fresh also refuses a replayed or stale signature — the
    # envelope is the one consumer that WIDENS, so it must not act twice on a
    # captured ✓. Nonces are spent in a store beside the ledger.
    principal = principal_auth.verified_fresh(
        l8_record, Path(ledger_dir) / "seen-nonces")
    signal = l8_record.get("signal_type")
    dist = l8_record.get("edit_distance_normalized")

    if not principal:
        state["history"].append({"category": category, "action": "ignored-unattributed"})
        _save(state, state_path)
        return level  # forged/unattributed never moves the envelope (CN-1)

    # T6 — no engagement penalty: only an EXPLICIT rejection narrows. A heavy
    # edit is the principal investing in the draft, not distrust; punishing it
    # taught rubber-stamping (rejected-then-narrowed = more interrupts).
    is_rejection = signal == "rejection"
    # widening stays slow AND measured: an endorsement without a recorded edit
    # distance is not evidence of acceptance (fail safe, T6)
    is_acceptance = (signal == "endorsement"
                     and dist is not None and dist <= LIGHT_EDIT)

    if is_rejection:
        if level > 0:
            new = level - 1
            state["levels"][category] = new
            state["accept_counters"][category] = 0
            state["history"].append({"category": category, "from": level, "to": new,
                                     "rule": "narrow"})
            _ledger_change(ledger_dir, category, level, new, "narrow", policy_path)
            _save(state, state_path)
            return new
        state["accept_counters"][category] = 0
        _save(state, state_path)
        return level

    if is_acceptance:
        state["accept_counters"][category] += 1
        if state["accept_counters"][category] >= _widen_threshold(policy, posture) \
                and level < ceiling:
            new = level + 1
            state["levels"][category] = new
            state["accept_counters"][category] = 0
            state["history"].append({"category": category, "from": level, "to": new,
                                     "rule": "widen"})
            _ledger_change(ledger_dir, category, level, new, "widen", policy_path)
            _save(state, state_path)
            return new

    _save(state, state_path)
    return state["levels"][category]


def reset(category, ledger_dir, state_path, policy_path=None):
    """Manual reset of a category to its base level. Ledgered, reversible."""
    policy = load_policy(policy_path)
    state = load_state(state_path, policy)
    base = policy["categories"][category]["base"]
    frm = state["levels"][category]
    state["levels"][category] = base
    state["accept_counters"][category] = 0
    state["history"].append({"category": category, "from": frm, "to": base, "rule": "reset"})
    _ledger_change(ledger_dir, category, frm, base, "reset", policy_path)
    _save(state, state_path)
    return base
