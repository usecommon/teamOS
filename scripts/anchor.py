"""Chain-head anchoring (SE-6). Tamper-evidence on the builder's own disk is
evidence to no one; each loop run writes the head hash of every ledger to an
anchor file that is pushed off-box (shared repo / external timestamp) — so the
A-A4 / A-P3 record doesn't rest on a chain the producing machine could rewrite.
"""

import json
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hashchain  # noqa: E402


def anchor_heads(ledger_dir, anchor_dir, run_id, remote_dir=None):
    """Write {ledger_file: head_hash} + timestamp to an anchor file, and COPY
    it to an off-box witness (T13/SE-6): `remote_dir` arg or TEAMOS_ANCHOR_REMOTE
    env — a mount/synced dir on a machine the producing box can't rewrite.
    In-repo anchors alone are evidence to no one. Returns the anchor dict with
    a `witness` field recording where (or whether) it was pushed."""
    ledger_dir, anchor_dir = Path(ledger_dir), Path(anchor_dir)
    anchor_dir.mkdir(parents=True, exist_ok=True)
    heads = {}
    for f in sorted(ledger_dir.glob("*.jsonl")):
        heads[f.name] = hashchain.last_hash(f)
    anchor = {"run_id": run_id, "heads": heads,
              "anchored_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")}
    path = anchor_dir / f"{run_id}.anchor.json"
    remote = remote_dir or os.environ.get("TEAMOS_ANCHOR_REMOTE")
    if remote:
        try:
            Path(remote).mkdir(parents=True, exist_ok=True)
            anchor["witness"] = str(Path(remote) / path.name)
        except OSError:
            anchor["witness"] = None  # recorded honestly: no external witness
    else:
        anchor["witness"] = None
    path.write_text(json.dumps(anchor, indent=2))
    if anchor["witness"]:
        try:
            shutil.copy2(path, anchor["witness"])
        except OSError:
            pass  # witness recorded in the anchor; failure visible on audit
    return anchor
