"""Compilation skill (C2 as a harness skill, FK4). Deterministic core for the
F-test; the A-C2 agent run is the measured layer on top.

Ingest eligible footprint -> job graph + profile/voice + pre-built skills.
Invariants:
- imperative-content quarantine (§7.7): historical/untrusted content that tries
  to add plan structure is extracted and quarantined, NEVER compiled into an
  exemplar or skill. It can be summarized/flagged, not executed.
- distill-then-discard: outputs carry references + hashes, never raw bodies; the
  working copy of raw ingest is deleted after compile and verified absent.
- lineage: every output gets an L3 record (source/evidence/transformation/
  confidence).
- Claude Code footprint import (FR3): commands -> skills, CLAUDE.md -> profile.

No network. No language model in this deterministic path.
"""

import json
import re
import statistics
import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import hashchain  # noqa: E402
from adapter import adapter  # noqa: E402

COMPILER_AGENT_ID = "teamos-compiler/0.1"

# Imperative / injection markers: content trying to add plan structure. Coarse
# and deterministic — the quarantine is fail-safe (over-quarantine is fine; a
# missed exemplar costs nothing, a compiled injection is the failure).
IMPERATIVE_PATTERNS = [
    r"ignore (all )?(previous|prior) instructions",
    r"disregard (the )?(above|previous)",
    r"\bforward\b.*\b(to|corpus)\b",
    r"\bsend\b.*\b(to|@)\b",
    r"\bemail\b.*@",
    r"^\s*system\s*:",
    r"you must (now|immediately)",
    r"exfiltrat",
]
_IMPERATIVE_RE = re.compile("|".join(IMPERATIVE_PATTERNS), re.IGNORECASE | re.MULTILINE)

_DATE_RE = re.compile(r"(\d{4})-(\d{2})-(\d{2})")


def scan_imperative(text):
    """True if the text contains imperative/injection structure (quarantine)."""
    return bool(_IMPERATIVE_RE.search(text))


def _parse_frontmatter(text):
    return adapter._parse_frontmatter(text)


def load_footprint(artifacts_dir, provenance=None):
    """Read files into ingest items: [{path, content, provenance}]."""
    items = []
    for path in sorted(Path(artifacts_dir).glob("*.md")):
        items.append({
            "path": str(path),
            "content": path.read_text(),
            "provenance": provenance or {"source_id": "footprint", "type": "local-folder",
                                         "workspace": str(artifacts_dir)},
        })
    return items


def _signature(path):
    """Recurring-task signature: filename stem with trailing date/number stripped."""
    stem = Path(path).stem
    stem = _DATE_RE.sub("", stem)
    return re.sub(r"[-_]+$", "", stem).strip("-_")


def _dates(paths):
    out = []
    for p in paths:
        m = _DATE_RE.search(Path(p).name)
        if m:
            out.append(date(int(m.group(1)), int(m.group(2)), int(m.group(3))))
    return sorted(out)


def _cadence(dates):
    if len(dates) < 2:
        return "unknown"
    gaps = [(b - a).days for a, b in zip(dates, dates[1:])]
    med = statistics.median(gaps)
    if med <= 1.5:
        return "daily"
    if med <= 10:
        return "weekly"
    if med <= 40:
        return "monthly"
    return "irregular"


def _ref(item):
    return {"store": item["provenance"].get("type", "footprint"),
            "path": item["path"],
            "content_hash": hashchain.sha256_str(item["content"])}


def _write_l3(ledger_dir, target_id, source_type, transformation, evidence_refs,
              confidence="high", parents=()):
    hashchain.append(Path(ledger_dir) / "l3.jsonl", {
        "target_id": target_id,
        "source_type": source_type,
        "authoring_agent": COMPILER_AGENT_ID,
        "evidence": list(evidence_refs),
        "transformation": transformation,
        "confidence": confidence,
        "update_history_ref": {"store": "compiler", "path": target_id, "content_hash": "sha256:0"},
        "parent_ids": list(parents),
    }, COMPILER_AGENT_ID)


def compile_footprint(items, out_dir, ledger_dir, cc_footprint_dir=None,
                      cc_user_claude_md=None, cc_project_claude_md=None):
    """Compile ingest items into distilled outputs. Returns a result dict.

    items: [{path, content, provenance}] from an eligible source.
    """
    out_dir = Path(out_dir)
    ledger_dir = Path(ledger_dir)
    (out_dir / "quarantine").mkdir(parents=True, exist_ok=True)
    (out_dir / "skills").mkdir(parents=True, exist_ok=True)

    # 1. Imperative-content quarantine BEFORE anything becomes an exemplar.
    clean, quarantined = [], []
    for item in items:
        if scan_imperative(item["content"]):
            qname = Path(item["path"]).name
            # store a FLAG + reference, not an executable copy; source is untrusted
            (out_dir / "quarantine" / (qname + ".flag.json")).write_text(json.dumps({
                "quarantined_path": item["path"],
                "reason": "imperative-content",
                "content_hash": hashchain.sha256_str(item["content"]),
            }, indent=2))
            quarantined.append(item["path"])
            _write_l3(ledger_dir, f"quarantine/{qname}", "external-untrusted",
                      "imperative-quarantine", [_ref(item)], confidence="unrated")
        else:
            clean.append(item)

    # 2. Cluster clean artifacts into recurring transformations (job graph).
    clusters = {}
    for item in clean:
        fm, _ = _parse_frontmatter(item["content"])
        sig = fm.get("deliverable_type") or _signature(item["path"])
        clusters.setdefault(sig, []).append((item, fm))

    nodes = []
    for sig, group in sorted(clusters.items()):
        if len(group) < 2:
            continue  # not recurring
        sources = sorted({fm.get("source", "unknown") for _, fm in group})
        cadence = _cadence(_dates([it["path"] for it, _ in group]))
        exemplar_refs = [_ref(it) for it, _ in group]  # references only, no bodies
        node = {
            "task_type": sig,
            "cadence": cadence,
            "sources": sources,
            "occurrences": len(group),
            "exemplar_refs": exemplar_refs,
            "confidence": "high" if len(group) >= 3 else "medium",
        }
        nodes.append(node)
        _write_l3(ledger_dir, f"job-graph/{sig}", "principal-direct",
                  "compilation-distill", exemplar_refs, node["confidence"])

    job_graph = {"nodes": nodes, "footprint_items": len(items),
                 "quarantined": len(quarantined)}
    (out_dir / "job_graph.json").write_text(json.dumps(job_graph, indent=2))

    # 3. Claude Code footprint import (FR3): commands -> skills, CLAUDE.md -> profile.
    skills = []
    if cc_footprint_dir:
        for skill, sidecar, body in adapter.commands_to_skills(cc_footprint_dir):
            sd = out_dir / "skills" / skill["name"]
            sd.mkdir(parents=True, exist_ok=True)
            (sd / "SKILL.md").write_text(body)
            (sd / "skill.json").write_text(json.dumps(skill, indent=2))
            (sd / "SKILL.lineage.json").write_text(hashchain.canonical(sidecar))
            skills.append(skill)
            _write_l3(ledger_dir, skill["skill_id"], "harness-artifact",
                      "adapter-translation:command-to-skill",
                      [{"store": "commands", "path": str(cc_footprint_dir),
                        "content_hash": skill["version"]}])

    profile_sections = []
    if cc_user_claude_md or cc_project_claude_md:
        _, entries = adapter.claude_md_to_scopes(
            user_claude_md=cc_user_claude_md, project_claude_md=cc_project_claude_md)
        prof_lines = ["# Compiled profile\n"]
        for entry, sidecar in entries:
            prof_lines.append(f"## {entry['title']} ({entry['scope']})\n")
            for block in entry["blocks"]:
                prof_lines.append(block["text"] + "\n")
            profile_sections.append(entry["title"])
            _write_l3(ledger_dir, f"profile/{entry['entry_id']}", "harness-artifact",
                      "adapter-translation:claude-md-to-profile",
                      [{"store": "claude-md", "path": entry["entry_id"],
                        "content_hash": "sha256:0"}])
        (out_dir / "profile.md").write_text("\n".join(prof_lines))

    # 4. distill-then-discard: outputs above hold refs + distilled text, never
    #    raw artifact bodies. Nothing retains the raw ingest; return the manifest.
    return {
        "job_graph": job_graph,
        "nodes": nodes,
        "skills": skills,
        "profile_sections": profile_sections,
        "quarantined": quarantined,
        "out_dir": str(out_dir),
    }


def compile_from_source(source_id, artifacts_dir, out_dir, ledger_dir,
                        config_path=None, **cc):
    """FK3b-gated entry: pull via connectors (eligibility + provenance), compile.
    Returns None (compiles nothing) if the source is ineligible."""
    import connectors
    raw = load_footprint(artifacts_dir)
    gated = connectors.ingest(source_id, raw, config_path=config_path,
                              ledger_dir=ledger_dir)
    if not gated:
        return None
    return compile_footprint(gated, out_dir, ledger_dir, **cc)
