"""Team OS MCP door (FK6c) — the minimal door. Read tools (readOnlyHint set) +
`propose_*` tools that append to the PROPOSALS INBOX, never the corpus. Cloud /
any-client sessions get read + propose only; the gate processor at the runtime
of record is the sole writer (single-writer preserved).
"""

import json
import re
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hashchain  # noqa: E402

# Tool specs the door advertises. Read tools carry readOnlyHint (MCP contract).
TOOL_SPECS = {
    "read_corpus":            {"readOnlyHint": True},
    "read_job_graph":         {"readOnlyHint": True},
    "list_desired_schedules": {"readOnlyHint": True},
    "propose_corpus_entry":   {"readOnlyHint": False},
    "propose_schedule":       {"readOnlyHint": False},
}
DOOR_TOOLS = set(TOOL_SPECS)


def _slug(title):
    return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-") or "entry"


def _write_proposal(inbox_dir, proposal):
    inbox_dir = Path(inbox_dir) / "proposals"
    inbox_dir.mkdir(parents=True, exist_ok=True)
    pid = f"prop-{uuid.uuid4().hex[:12]}"
    proposal["proposal_id"] = pid
    proposal["proposed_at"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    path = inbox_dir / f"{pid}.json"
    path.write_text(json.dumps(proposal, indent=2))
    return path


# --- read tools (readOnlyHint) ------------------------------------------------

def read_corpus(store_root, query=None):
    root = Path(store_root) / "corpus"
    out = []
    if root.exists():
        for p in sorted(root.glob("*.md")):
            if query is None or query.lower() in p.read_text().lower():
                out.append({"path": str(p), "title": p.stem})
    return out


def read_job_graph(out_dir):
    jg = Path(out_dir) / "job_graph.json"
    return json.loads(jg.read_text()) if jg.exists() else {"nodes": []}


def list_desired_schedules(templates_path):
    """Templates served AS DATA (the user's first conversation creates them via
    the platform's own scheduling tools — the door never registers schedules)."""
    return json.loads(Path(templates_path).read_text())


# --- propose_* tools (append to inbox, NEVER the corpus) ----------------------

def propose_corpus_entry(inbox_dir, title, blocks, source="door", confidence="medium"):
    return _write_proposal(inbox_dir, {
        "kind": "corpus_entry",
        "target": f"stores/corpus/{_slug(title)}.md",
        "title": title,
        "blocks": blocks,
        "lineage": {"source_type": f"door:{source}", "transformation": "door-proposal",
                    "confidence": confidence},
    })


def propose_skill(inbox_dir, name, purpose, tools=None, source="scout"):
    """Propose creating a NEW skill (efficiency discovery, §9). Lands in the inbox;
    the gate processor creates the skill folder only on approval."""
    return _write_proposal(inbox_dir, {
        "kind": "skill",
        "target": f"stores/skills/{_slug(name)}/SKILL.md",
        "name": name, "purpose": purpose, "tools": tools or [],
        "lineage": {"source_type": f"door:{source}", "transformation": "skill-proposal",
                    "confidence": "medium"},
    })


def propose_schedule(inbox_dir, name, cron, prompt):
    return _write_proposal(inbox_dir, {
        "kind": "schedule",
        "target": f"schedules/{_slug(name)}.json",
        "name": name, "cron": cron, "prompt": prompt,
        "lineage": {"source_type": "door", "transformation": "door-proposal",
                    "confidence": "medium"},
    })
