"""Scoring dashboard (FK7-pre) — renders PER-SKILL, never per-person-comparative.

No individuation surface (§8.6): the dashboard consumes L7 (which is keyed to
skill_id + skill_version and carries no principal) and aggregates by skill only.
It must not join in L8's principal_id to compare people. `audit_no_individuation`
statically enforces that this module contains no per-person comparative machinery
(the "dashboard code audit" F-test).
"""

import io
import json
import statistics
import tokenize
from pathlib import Path

# Identifier substrings that indicate a per-person / comparative surface. The
# audit scans IDENTIFIERS (function/variable/attribute names) — not strings or
# comments — so a per-person construct in the CODE fails the guard while prose
# in docstrings does not produce false hits.
FORBIDDEN_IDENT = ["principal", "leaderboard", "per_person", "perperson",
                   "byperson", "personrank"]


def render_skill_dashboard(l7_records):
    """Aggregate L7 by skill_id + version. Returns per-skill stats only."""
    by_skill = {}
    for r in l7_records:
        key = r["skill_id"]
        by_skill.setdefault(key, {"scores": [], "versions": set()})
        by_skill[key]["scores"].append(r["score"])
        by_skill[key]["versions"].add(r["skill_version"])
    out = {}
    for skill, data in sorted(by_skill.items()):
        out[skill] = {
            "n": len(data["scores"]),
            "mean_score": round(statistics.mean(data["scores"]), 3),
            "versions": sorted(data["versions"]),
        }
    return {"per_skill": out}


def load_l7(ledger_dir):
    path = Path(ledger_dir) / "l7.jsonl"
    if not path.exists():
        return []
    return [json.loads(l) for l in path.read_text().splitlines() if l.strip()]


def audit_no_individuation(module_path=None):
    """Return (clean, findings): tokenize the dashboard source and flag any
    IDENTIFIER (name/attribute) containing a forbidden per-person substring. The
    FORBIDDEN_IDENT list itself is a string literal, so it is not scanned."""
    module_path = Path(module_path or __file__)
    findings = []
    src = module_path.read_text()
    for tok in tokenize.generate_tokens(io.StringIO(src).readline):
        if tok.type != tokenize.NAME:
            continue
        name = tok.string.lower()
        for pat in FORBIDDEN_IDENT:
            if pat in name:
                findings.append(f"{tok.start[0]}: {tok.string}")
    return (not findings), findings
