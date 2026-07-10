"""Transcript -> L1 compiler (FK2). Wraps the adapter translation and appends
onto the persistent l1.jsonl chain (adapter emits per-file chains from genesis;
this re-chains onto the ledger head).

Usage: python3 scripts/l1_compile.py <transcript.jsonl> [...]
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import hashchain  # noqa: E402
from adapter import adapter  # noqa: E402

L1_ENVELOPE_FIELDS = ("record_id", "ts", "schema_version", "agent_id", "prev_hash", "hash")


def compile_transcript(transcript_path, ledger_dir=None):
    ledger_dir = Path(ledger_dir or REPO_ROOT / "ledgers")
    records = []
    for span in adapter.transcript_to_l1_spans(transcript_path):
        body = {k: v for k, v in span.items() if k not in L1_ENVELOPE_FIELDS}
        records.append(
            hashchain.append(
                ledger_dir / "l1.jsonl", body, adapter.ADAPTER_AGENT_ID,
                record_id=span["record_id"],
            )
        )
    return records


if __name__ == "__main__":
    total = sum(len(compile_transcript(p)) for p in sys.argv[1:])
    print(f"compiled {total} spans into l1.jsonl")
