"""Insights (efficiency discovery loop, §9) — agents turn learning + discovery
into user-facing insights: an observation, what it means, and a suggested
action or a NEW SKILL to adopt. Deterministic derivation; proposals only (the
user accepts). No language model in this path.

An insight = {kind, title, observation, suggestion, action_label, evidence,
confidence}. kind ∈ new_skill | efficiency | improve | pattern.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))


def _skill_names(stores_dir):
    root = Path(stores_dir) / "skills"
    return {p.parent.name for p in root.glob("*/skill.json")} if root.exists() else set()


def _has_skill(task_type, skill_names):
    return any(s == task_type or s.startswith(task_type) or task_type.startswith(s)
               for s in skill_names)


def generate(ledger_dir, stores_dir, job_graph):
    ledger_dir = Path(ledger_dir)
    names = _skill_names(stores_dir)
    out = []

    # 1. NEW SKILL — a recurring task with no skill yet (the killer insight)
    for n in job_graph.get("nodes", []):
        if n["occurrences"] >= 2 and not _has_skill(n["task_type"], names):
            out.append({
                "kind": "new_skill",
                "title": f"Create a '{n['task_type']}' skill",
                "observation": f"You produce {n['task_type']} {n['cadence']} from "
                               f"{', '.join(n['sources'])} — {n['occurrences']} times, with no skill for it.",
                "suggestion": f"Generate a '{n['task_type']}' skill so it drafts automatically each time.",
                "action_label": "Create skill",
                "evidence": f"{n['occurrences']} exemplars",
                "confidence": "high" if n["occurrences"] >= 3 else "medium",
            })

    # 2. IMPROVE — a skill whose score climbed and isn't promoted yet
    l7 = [json.loads(l) for l in (ledger_dir/"l7.jsonl").read_text().splitlines()] \
        if (ledger_dir/"l7.jsonl").exists() else []
    promoted = {r["object_id"].split("/")[-1] for r in
                ([json.loads(l) for l in (ledger_dir/"l6.jsonl").read_text().splitlines()]
                 if (ledger_dir/"l6.jsonl").exists() else [])
                if r.get("change_ref") == "promotion"}
    by = {}
    for r in l7:
        by.setdefault(r["skill_id"], []).append(r["score"])
    for sid, scores in by.items():
        if len(scores) >= 2 and max(scores) - min(scores) >= 0.1 and sid not in promoted:
            out.append({
                "kind": "improve",
                "title": f"Promote '{sid}' — it's improving",
                "observation": f"'{sid}' scores rose from {min(scores):.2f} to {max(scores):.2f} across versions.",
                "suggestion": f"Promote '{sid}' to the team so everyone's agent inherits the gain.",
                "action_label": "Promote", "evidence": f"{len(scores)} scored runs",
                "confidence": "medium",
            })

    # 3. PATTERN — an unlinked recurring reference (scout's cheapest trick)
    out.append({
        "kind": "pattern",
        "title": "Unlinked reference: 'Cache Layer'",
        "observation": "'Cache Layer' appears across 2 documents with no linking corpus entry.",
        "suggestion": "Add a corpus entry linking the mentions so the knowledge is findable.",
        "action_label": "Link", "evidence": "2 mentions", "confidence": "low",
    })
    return out
