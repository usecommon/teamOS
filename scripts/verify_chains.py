"""Verify every hash chain under the ledger dir. Exit non-zero on any break.
Note: side-store content is NOT hashed into the chain body — the chain hashes
REFERENCES (SE-2), so erasing side-store content never breaks verification.
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hashchain  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent


def main(ledger_dir=None):
    ledger_dir = Path(ledger_dir or os.environ.get("TEAMOS_LEDGER_DIR", REPO_ROOT / "ledgers"))
    files = sorted(ledger_dir.glob("*.jsonl"))
    if not files:
        print(f"no ledgers under {ledger_dir} — nothing to verify")
        return 0
    failures = 0
    for f in files:
        try:
            n = hashchain.verify(f)
            print(f"ok: {f.name} ({n} records)")
        except ValueError as exc:
            failures += 1
            print(f"FAIL: {exc}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
