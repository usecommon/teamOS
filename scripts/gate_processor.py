"""Inbox gate processor (FK6c) — the SOLE writer. Pulls the proposals inbox,
validates each proposal against the parser-probe set (SE-3), runs it through the
IDENTICAL FK2 gate rule set (one implementation, two entry points), and commits
only clean ones into the store with L3 lineage. Deterministic code (CN-2): no
language model in the commit path — a crafted proposal has no model to inject.

Parser probes rejected by construction:
- path traversal (target escapes the allowed store root)
- symlinked proposal file
- unicode/case-normalization aimed at a protected path (whitelist by resolved
  real path, not string compare)
- YAML/JSON parser-abuse / malformed structure
"""

import json
import os
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "hooks"))
import hashchain  # noqa: E402
import gate  # noqa: E402

PROC_AGENT_ID = "teamos-gate-processor/0.1"
ALLOWED_ROOTS = ("stores/corpus", "schedules", "stores/skills")
# T9 / §7.7: proposals that ADD PLAN STRUCTURE (a scheduled step, a loadable
# skill) never auto-commit — they wait for explicit human approval. Corpus
# entries are values and flow through the parser + FK2 gate as before.
PLAN_STRUCTURE_KINDS = ("schedule", "skill")


def approve(inbox_dir, proposal_id, approver="principal"):
    """The human-approval step: drop an approval marker for a proposal. Meant
    to be called by the principal (CLI/console), never by the agent."""
    d = Path(inbox_dir) / "approvals"
    d.mkdir(parents=True, exist_ok=True)
    path = d / f"{proposal_id}.approved"
    path.write_text(json.dumps({"approver": approver,
                                "at": hashchain.utc_now()}))
    return path


def _approved(inbox_dir, proposal_id):
    return (Path(inbox_dir) / "approvals" / f"{proposal_id}.approved").exists()


class ProposalRejected(ValueError):
    def __init__(self, rule, msg):
        super().__init__(msg)
        self.rule = rule


def _reject(ledger_dir, proposal_path, rule, detail):
    hashchain.append(Path(ledger_dir) / "l2.jsonl", {
        "proposed_action": {"tool": "gate_processor", "action_class": "write",
                            "target": str(proposal_path)[:200],
                            "payload_digest": hashchain.sha256_str(detail)},
        "verdict": "deny", "policy_version": "proposal-parser:0.1", "rule_id": rule,
        "inspection": {"checks_run": ["proposal-parser"], "findings": [detail]},
        "outcome": "gate_blocked",
    }, PROC_AGENT_ID)


def _validate_structure(proposal):
    if not isinstance(proposal, dict):
        raise ProposalRejected("parser-abuse", "proposal is not an object")
    kind = proposal.get("kind")
    if kind not in ("corpus_entry", "schedule", "skill"):
        raise ProposalRejected("parser-abuse", f"unknown kind {kind!r}")
    target = proposal.get("target")
    if not isinstance(target, str) or not target:
        raise ProposalRejected("parser-abuse", "missing/invalid target")
    if kind == "corpus_entry" and not isinstance(proposal.get("blocks"), list):
        raise ProposalRejected("parser-abuse", "corpus_entry needs blocks[]")
    if kind == "skill" and not (proposal.get("name") and proposal.get("purpose")):
        raise ProposalRejected("parser-abuse", "skill needs name + purpose")
    return kind, target


def _safe_target(repo_root, target):
    # normalize (defeat unicode/case homoglyph attempts), then whitelist by
    # RESOLVED real path under an allowed root — string tricks can't escape.
    norm = unicodedata.normalize("NFKC", target)
    resolved = (Path(repo_root) / norm).resolve()
    for root in ALLOWED_ROOTS:
        allowed = (Path(repo_root) / root).resolve()
        if str(resolved) == str(allowed) or str(resolved).startswith(str(allowed) + os.sep):
            return resolved
    raise ProposalRejected("path-traversal", f"target escapes allowed roots: {target}")


def _commit(proposal, resolved, repo_root, ledger_dir, kind):
    resolved.parent.mkdir(parents=True, exist_ok=True)
    if kind == "corpus_entry":
        body = f"# {proposal['title']}\n\n" + "\n\n".join(
            b if isinstance(b, str) else b.get("text", "") for b in proposal["blocks"])
        resolved.write_text(body)
    elif kind == "skill":
        name, purpose = proposal["name"], proposal["purpose"]
        tools = proposal.get("tools", [])
        resolved.write_text(f"---\ndescription: {purpose}\n---\n\n# {name}\n\n{purpose}\n")
        skill_dir = resolved.parent
        (skill_dir / "skill.json").write_text(json.dumps({
            "skill_id": f"personal/{skill_dir.name}", "name": skill_dir.name,
            "description": purpose, "namespace": "personal",
            "version": hashchain.sha256_str(purpose),
            "capability_manifest": {"capture_surface": "cloud+synced+local-folders", "tools": tools},
            "evidence_links": [], "body_path": f"stores/skills/{skill_dir.name}/SKILL.md",
            "lineage_sidecar": f"stores/skills/{skill_dir.name}/SKILL.lineage.json"}, indent=2))
        (skill_dir / "SKILL.lineage.json").write_text(hashchain.canonical({
            "entity_id": f"personal/{skill_dir.name}",
            "generated_by": {"transformation": "skill-proposal", "at": "2026-07-11T00:00:00Z"},
            "agent": PROC_AGENT_ID,
            "sources": [{"source_type": "agent-derivation", "locator": proposal["proposal_id"],
                         "content_hash": hashchain.sha256_str(purpose), "basis": "inferred"}],
            "evidence": [proposal["proposal_id"]], "confidence": "medium",
            "basis": "inferred", "update_history": []}))
    else:
        resolved.write_text(json.dumps(
            {k: proposal[k] for k in ("name", "cron", "prompt")}, indent=2))
    lin = proposal.get("lineage", {})
    hashchain.append(Path(ledger_dir) / "l3.jsonl", {
        "target_id": str(resolved.relative_to(Path(repo_root).resolve())),
        "source_type": lin.get("source_type", "door"),
        "authoring_agent": PROC_AGENT_ID,
        "evidence": [{"store": "inbox", "path": proposal["proposal_id"],
                      "content_hash": hashchain.sha256_str(json.dumps(proposal, sort_keys=True)),
                      "basis": lin.get("basis", "ambiguous")}],
        "transformation": lin.get("transformation", "door-proposal"),
        "confidence": lin.get("confidence", "medium"),
        # door content is untrusted → ambiguous unless the proposal declares otherwise;
        # the human-approval step IS the ambiguous→review route (T9).
        "basis": lin.get("basis", "ambiguous"),
        "update_history_ref": {"store": "git", "path": str(resolved), "content_hash": "sha256:0"},
        "parent_ids": [],
    }, PROC_AGENT_ID)


def process_inbox(inbox_dir, repo_root, ledger_dir, policy=None):
    """Process every proposal. Returns {committed, rejected, pending}.
    Schedule/skill proposals WAIT (pending) until a human approval marker
    exists — untrusted content never adds plan structure unconfirmed (T9)."""
    inbox = Path(inbox_dir) / "proposals"
    committed, rejected, pending = [], [], []
    if not inbox.exists():
        return {"committed": committed, "rejected": rejected, "pending": pending}
    policy = policy or gate.load_policy()
    prev_ledger = gate.LEDGER_DIR
    gate.LEDGER_DIR = Path(ledger_dir)
    try:
        for path in sorted(inbox.glob("*.json")):
            try:
                if path.is_symlink():           # symlink-in-inbox probe
                    raise ProposalRejected("symlink", "proposal file is a symlink")
                proposal = json.loads(path.read_text())
                kind, target = _validate_structure(proposal)
                resolved = _safe_target(repo_root, target)
                if kind in PLAN_STRUCTURE_KINDS \
                        and not _approved(inbox_dir, proposal["proposal_id"]):
                    pending.append(proposal["proposal_id"])
                    continue  # stays in the inbox awaiting the human
                # run the IDENTICAL FK2 gate on the resolved write (protected
                # paths / payload inspection apply exactly as in the loop path)
                decision = gate.process({"tool_name": "Write",
                    "tool_input": {"file_path": str(resolved),
                                   "content": json.dumps(proposal.get("blocks", proposal))}},
                    policy)
                if decision["hookSpecificOutput"]["permissionDecision"] != "allow":
                    raise ProposalRejected("gate-blocked", "FK2 gate did not permit")
                _commit(proposal, resolved, repo_root, ledger_dir, kind)
                committed.append(proposal["proposal_id"])
                _move(path, inbox.parent / "processed")
            except ProposalRejected as exc:
                _reject(ledger_dir, path, exc.rule, str(exc))
                rejected.append((path.stem, exc.rule))
                _move(path, inbox.parent / "rejected")
            except (json.JSONDecodeError, KeyError) as exc:
                _reject(ledger_dir, path, "parser-abuse", str(exc))
                rejected.append((path.stem, "parser-abuse"))
                _move(path, inbox.parent / "rejected")
    finally:
        gate.LEDGER_DIR = prev_ledger
    return {"committed": committed, "rejected": rejected, "pending": pending}


def _move(path, dest_dir):
    dest_dir.mkdir(parents=True, exist_ok=True)
    if path.exists() or path.is_symlink():
        path.replace(dest_dir / path.name)
