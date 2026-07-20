"""L3 lineage writer (FK2). THE write path for corpus/memory content.

Invariant: an unlabelled write is rejected by construction (CN-12) — a write
missing any lineage field is refused AND the rejection itself is ledgered.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hashchain  # noqa: E402
from schema_registry import validator_for  # noqa: E402

from jsonschema import ValidationError  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
L3_AGENT_ID = "teamos-l3-writer/0.1"


class LineageRejected(ValueError):
    pass


# Graphify-borrow: every derivation edge is EXTRACTED / INFERRED / AMBIGUOUS — you
# always know what was read directly vs guessed. A missing edge basis is read as
# the most cautious value (ambiguous). The entity basis is the weakest edge.
_BASIS_RANK = {"extracted": 0, "inferred": 1, "ambiguous": 2}


def edge_basis(source):
    b = source.get("basis", "ambiguous")
    return b if b in _BASIS_RANK else "ambiguous"


def entity_basis(sources):
    """Weakest basis across all derivation edges; no sources → ambiguous."""
    if not sources:
        return "ambiguous"
    return max((edge_basis(s) for s in sources), key=lambda b: _BASIS_RANK[b])


def write_with_lineage(entry_path, content, sidecar, ledger_dir=None, parent_ids=()):
    """Write `content` to `entry_path` + its sidecar + one L3 record.

    Rejects (and ledgers the rejection) unless the sidecar carries the full
    lineage set (schema-validated).
    """
    ledger_dir = Path(ledger_dir or REPO_ROOT / "ledgers")
    entry_path = Path(entry_path)

    try:
        validator_for("lineage-sidecar.schema.json").validate(sidecar)
    except ValidationError as exc:
        hashchain.append(
            ledger_dir / "l2.jsonl",
            {
                "proposed_action": {
                    "tool": "l3_writer",
                    "action_class": "write",
                    "target": str(entry_path)[:200],
                    "payload_digest": hashchain.sha256_str(str(content)),
                },
                "verdict": "deny",
                "policy_version": "lineage-schema:" + "0.1",
                "rule_id": "lineage-required",
                "inspection": {
                    "checks_run": ["lineage-completeness"],
                    "findings": [f"missing-or-invalid:{exc.json_path}"],
                },
                "outcome": "gate_blocked",
            },
            L3_AGENT_ID,
        )
        raise LineageRejected(f"write rejected, rejection ledgered: {exc.message}") from exc

    entry_path.parent.mkdir(parents=True, exist_ok=True)
    entry_path.write_text(content)
    sidecar_path = entry_path.with_suffix(entry_path.suffix + ".lineage.json")
    sidecar_path.write_text(hashchain.canonical(sidecar))

    record = hashchain.append(
        ledger_dir / "l3.jsonl",
        {
            "target_id": sidecar["entity_id"],
            "source_type": sidecar["sources"][0]["source_type"]
            if sidecar["sources"]
            else "agent-derivation",
            "authoring_agent": sidecar["agent"],
            "evidence": [
                {
                    "store": "sources",
                    "path": s["locator"],
                    "content_hash": s["content_hash"],
                    "basis": edge_basis(s),
                }
                for s in sidecar["sources"]
            ],
            "transformation": sidecar["generated_by"]["transformation"],
            "confidence": sidecar["confidence"],
            "basis": entity_basis(sidecar["sources"]),
            "update_history_ref": {
                "store": "git",
                "path": str(entry_path.relative_to(REPO_ROOT))
                if entry_path.is_relative_to(REPO_ROOT)
                else str(entry_path),
                "content_hash": hashchain.sha256_str(content),
            },
            "parent_ids": list(parent_ids),
            "trust_label": hashchain.sha256_str(hashchain.canonical(sidecar)),
        },
        L3_AGENT_ID,
    )
    return record
