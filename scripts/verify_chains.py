"""Verify every hash chain under the ledger dir. Exit non-zero on any break.
Note: side-store content is NOT hashed into the chain body — the chain hashes
REFERENCES (SE-2), so erasing side-store content never breaks verification.
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hashchain  # noqa: E402
import anchor  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent


def main(ledger_dir=None, anchor_dir=None):
    ledger_dir = Path(ledger_dir or os.environ.get("TEAMOS_LEDGER_DIR", REPO_ROOT / "ledgers"))
    anchor_dir = Path(anchor_dir or os.environ.get("TEAMOS_ANCHOR_DIR", ledger_dir / "anchors"))
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
    # E2/SE-6: a whole-file deletion starts a fresh chain that verify() passes.
    # Cross-check the off-box anchor: an anchored head absent from the current
    # chain means history was truncated/rewritten — surface it, don't pass.
    truncated = anchor.detect_truncation(ledger_dir, anchor_dir)
    for name in truncated:
        failures += 1
        print(f"FAIL: {name}: anchored head absent — history truncated since last anchor (E2)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
