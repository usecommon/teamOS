"""Git IS Ledger 6 (fork spec §2). This script renders the normalized L6 view
from git history for the versioned stores. The JSONL is DERIVED and rebuildable
— git stays authoritative (files-as-truth).

Usage: python3 scripts/l6_from_git.py [path ...]  (default: stores/ docs/schemas/)
"""

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hashchain  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
L6_AGENT_ID = "teamos-l6-view/0.1"

OBJECT_TYPES = {
    "stores/skills": "skill",
    "stores/corpus": "context",
    "stores/profile": "profile",
    "stores/templates": "skill",
    "docs/schemas": "schema",
    "hooks": "hook",
    "adapter": "policy",
}


def object_type_for(path):
    for prefix, otype in OBJECT_TYPES.items():
        if str(path).startswith(prefix):
            return otype
    return "context"


def records_for_path(path, ledger_dir=None):
    """One L6 record per commit touching `path` (oldest first)."""
    ledger_dir = Path(ledger_dir or REPO_ROOT / "ledgers")
    log = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "log", "--reverse", "--format=%H", "--", str(path)],
        capture_output=True, text=True, check=True,
    ).stdout.split()
    records, prev = [], None
    for sha in log:
        records.append(
            hashchain.append(
                ledger_dir / "l6.jsonl",
                {
                    "object_type": object_type_for(path),
                    "object_id": str(path),
                    "version": sha,
                    "prev_version": prev,
                    "change_ref": f"git:{sha}",
                },
                L6_AGENT_ID,
            )
        )
        prev = sha
    return records


if __name__ == "__main__":
    paths = sys.argv[1:] or ["stores", "docs/schemas"]
    total = sum(len(records_for_path(p)) for p in paths)
    print(f"rendered {total} L6 records")
