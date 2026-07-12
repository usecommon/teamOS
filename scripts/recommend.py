"""Recommendations (agent → user) — the initiative surface. Agents record
suggested ACTIONS with a rationale and confidence; the user accepts or dismisses.
Proposals-only: a recommendation never acts on its own (§7.7/§16 leash). Append-
only, hash-chained. Deterministic; no language model in this path.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hashchain  # noqa: E402

REC_AGENT_ID = "teamos-recommend/0.1"


def record(ledger_dir, agent, action, rationale, confidence="medium", kind="action"):
    return hashchain.append(Path(ledger_dir) / "recommendations.jsonl", {
        "agent": agent, "action": action, "rationale": rationale,
        "confidence": confidence, "kind": kind, "status": "open",
    }, REC_AGENT_ID)


def load(ledger_dir):
    import json
    p = Path(ledger_dir) / "recommendations.jsonl"
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()] if p.exists() else []
