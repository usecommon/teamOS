"""L8 edit-diff capture (FK2, SE-2). Records OUTCOMES; edited content never
inlines — the diff lives in an erasable side-store, the chain hashes the
reference. Deterministic code; no language model in the evidence path (SE-1).
"""

import difflib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hashchain  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
L8_AGENT_ID = "teamos-l8-capture/0.1"
LIGHT_EDIT_THRESHOLD = 0.2  # R-11, arbitrary-pending-baseline


def capture_edit(draft_path, edited_path, principal_id, ledger_dir=None,
                 attribution="principal_authenticated"):
    """Diff draft vs principal-edited artifact -> side-store + one L8 record."""
    ledger_dir = Path(ledger_dir or REPO_ROOT / "ledgers")
    sidestore = ledger_dir / "sidestore"
    sidestore.mkdir(parents=True, exist_ok=True)

    draft = Path(draft_path).read_text()
    edited = Path(edited_path).read_text()
    diff = "".join(
        difflib.unified_diff(
            draft.splitlines(keepends=True),
            edited.splitlines(keepends=True),
            fromfile="draft",
            tofile="edited",
        )
    )
    distance = round(1.0 - difflib.SequenceMatcher(None, draft, edited).ratio(), 4)
    diff_hash = hashchain.sha256_str(diff)
    diff_file = sidestore / f"{diff_hash.split(':')[1]}.diff"
    diff_file.write_text(diff)

    if distance == 0:
        outcome = "accepted"
    elif distance <= LIGHT_EDIT_THRESHOLD:
        outcome = "edited-lightly"
    else:
        outcome = "edited-heavily"

    return hashchain.append(
        ledger_dir / "l8.jsonl",
        {
            "signal_type": "edit",
            "artifact_ref": {
                "store": "stores",
                "path": str(edited_path),
                "content_hash": hashchain.sha256_str(edited),
            },
            "principal_id": principal_id,
            "attribution": attribution,
            "outcome": outcome,
            "edit_distance_normalized": distance,
            "diff_ref": {
                "store": "l8-sidestore",
                "path": str(diff_file.relative_to(ledger_dir)),
                "content_hash": diff_hash,
            },
            "harvest": {"method": "edit-diff-capture", "harvested_at": hashchain.utc_now()},
        },
        L8_AGENT_ID,
    )
