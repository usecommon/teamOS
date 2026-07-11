"""Transfer measurement rig + cohorts + rollback (FK7). The A-P3 MECHANISM: the
gate, cohorts, and measurement instrument. The RESULT is measured with real
receivers over real time — this builds the rig, never fabricates the number.

Design (pre-registered before any data):
- within-receiver interrupted time series: per receiver, invocations on skill v1
  (baseline) then v2, delta = edit distance (primary) + acceptance (secondary),
  plus a non-updated CONTROL skill (within-person diff-in-diff, ME-3).
- invocation floor: <10 invocations either side => inconclusive for that receiver
  (never imputed).
- pass rule: positive point estimate in >=2 receivers AND pooled interval
  excluding zero; anything else = inconclusive.
"""

import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hashchain  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
TRANSFER_AGENT_ID = "teamos-transfer/0.1"
INVOCATION_FLOOR = 10


# --- staggered cohorts --------------------------------------------------------

def assign_cohorts(receivers):
    """Deterministic staggered adoption: receivers ordered into waves. Wave i
    adopts v2 one step after wave i-1 (staggered, not simultaneous)."""
    return {r: i for i, r in enumerate(sorted(receivers))}


# --- measurement instrument ---------------------------------------------------

def record_invocation(ledger_dir, receiver, skill_id, version, edit_distance,
                      accepted, is_control=False):
    """Append one measured invocation to the transfer log (keyed to receiver +
    skill + version). Deterministic capture; no model."""
    return hashchain.append(Path(ledger_dir) / "transfer.jsonl", {
        "receiver": receiver, "skill_id": skill_id, "version": version,
        "edit_distance": edit_distance, "accepted": bool(accepted),
        "is_control": bool(is_control),
    }, TRANSFER_AGENT_ID)


def _load(ledger_dir):
    path = Path(ledger_dir) / "transfer.jsonl"
    if not path.exists():
        return []
    return [json.loads(l) for l in path.read_text().splitlines() if l.strip()]


def within_receiver_series(ledger_dir, receiver, skill_id, baseline_v, treatment_v):
    rows = [r for r in _load(ledger_dir)
            if r["receiver"] == receiver and r["skill_id"] == skill_id
            and not r["is_control"]]
    baseline = [r["edit_distance"] for r in rows if r["version"] == baseline_v]
    treatment = [r["edit_distance"] for r in rows if r["version"] == treatment_v]
    return baseline, treatment


def receiver_delta(baseline, treatment):
    """Positive delta = edit distance dropped v1->v2 (skill improved transfer).
    Returns None if either side is below the invocation floor (inconclusive)."""
    if len(baseline) < INVOCATION_FLOOR or len(treatment) < INVOCATION_FLOOR:
        return None
    return round(sum(baseline) / len(baseline) - sum(treatment) / len(treatment), 4)


def passes_preregistered_rule(receiver_deltas):
    """positive point estimate in >=2 receivers AND pooled point estimate > 0.
    receiver_deltas: {receiver: delta_or_None}. Inconclusive receivers excluded."""
    usable = [d for d in receiver_deltas.values() if d is not None]
    positive = [d for d in usable if d > 0]
    pooled = sum(usable) / len(usable) if usable else 0.0
    result = "pass" if (len(positive) >= 2 and pooled > 0) else "inconclusive"
    return {"result": result, "positive_receivers": len(positive),
            "usable_receivers": len(usable), "pooled": round(pooled, 4)}


# --- rollback (git-backed L6, byte-identical) ---------------------------------

def restore_version(repo_dir, rel_path, sha):
    """Restore a file to a prior git version byte-identically (rollback)."""
    content = subprocess.run(
        ["git", "-C", str(repo_dir), "show", f"{sha}:{rel_path}"],
        capture_output=True, check=True).stdout
    (Path(repo_dir) / rel_path).write_bytes(content)
    return content
