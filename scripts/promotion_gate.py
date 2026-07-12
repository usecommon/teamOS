"""Skill promotion gate (FK7) — the PR gate CI runs before a personal skill
enters the shared team namespace. Default-deny sharing: nothing is promoted
except through this gate.

Checks (all must pass):
  1. PII scan — no emails/phones/SSNs seeded into the skill.
  2. Eval floor — the skill has L7 evidence at or above the floor.
  3. Signing-lite (CN-3) — signed commit + reproducible build + the collaborator's
     hook-diff review attested (the builder is in every collaborator's TCB).

A block is ledgered (L2 deny). A pass writes the skill into the team namespace
and records an L6 version. Deterministic; no language model.
"""

import json
import re
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hashchain  # noqa: E402

PROMO_AGENT_ID = "teamos-promotion/0.1"
EVAL_FLOOR = 0.5

PII_PATTERNS = {
    "email": r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
    "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
    "phone": r"\b\(?\d{3}\)?[-.\s]\d{3}[-.\s]\d{4}\b",
}


def pii_scan(text):
    return [f"{k}" for k, pat in PII_PATTERNS.items() if re.search(pat, text)]


def eval_score(skill_id, ledger_dir):
    """Mean of LOAD-BEARING L7 scores only (T8). Scaffold metrics (the
    gameable structural-marker fraction) are excluded by construction: a stub
    deliverable containing three magic strings can never clear promotion."""
    path = Path(ledger_dir) / "l7.jsonl"
    if not path.exists():
        return None
    scores = []
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        if r["skill_id"] == skill_id and r.get("load_bearing", False):
            scores.append(r["score"])
    return round(statistics.mean(scores), 3) if scores else None


def _ledger(ledger_dir, skill_id, verdict, rule, findings):
    hashchain.append(Path(ledger_dir) / "l2.jsonl", {
        "proposed_action": {"tool": "promotion_gate", "action_class": "promote",
                            "target": skill_id,
                            "payload_digest": hashchain.sha256_str(skill_id)},
        "verdict": verdict, "policy_version": "promotion:0.1", "rule_id": rule,
        "inspection": {"checks_run": ["pii", "eval-floor", "signing-lite"],
                       "findings": findings},
        "outcome": "gate_passed" if verdict == "permit" else "gate_blocked",
    }, PROMO_AGENT_ID)


def promote(skill_id, skill_text, meta, ledger_dir, team_dir, floor=EVAL_FLOOR):
    """Run the gate. Returns (promoted, reasons). Writes to team_dir on pass."""
    reasons = []
    pii = pii_scan(skill_text)
    if pii:
        reasons.append(f"pii:{','.join(pii)}")
    score = eval_score(skill_id, ledger_dir)
    if score is None or score < floor:
        reasons.append(f"eval-floor:{score}<{floor}")
    if not (meta.get("signed_commit") and meta.get("reproducible_build")
            and meta.get("hook_diff_reviewed")):
        reasons.append("signing-lite:incomplete")

    if reasons:
        _ledger(ledger_dir, skill_id, "deny", "promotion-blocked", reasons)
        return False, reasons

    team_dir = Path(team_dir)
    team_dir.mkdir(parents=True, exist_ok=True)
    (team_dir / f"{skill_id}.md").write_text(skill_text)
    _ledger(ledger_dir, skill_id, "permit", "promotion-clean", [])
    hashchain.append(Path(ledger_dir) / "l6.jsonl", {
        "object_type": "skill", "object_id": f"team/{skill_id}",
        "version": hashchain.sha256_str(skill_text), "prev_version": None,
        "change_ref": "promotion",
    }, PROMO_AGENT_ID)
    return True, []
