"""Work log (arch §7.6 work objects) — what each agent member started and
finished. Append-only, hash-chained. 'working' entries with no matching 'done'
are in progress; the Activity surface reads this to show current + completed
work. Deterministic; agents write it as they run.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hashchain  # noqa: E402

WORKLOG_AGENT_ID = "teamos-worklog/0.1"


def _append(ledger_dir, body):
    return hashchain.append(Path(ledger_dir) / "worklog.jsonl", body, WORKLOG_AGENT_ID)


def start(ledger_dir, agent, task, artifact=None):
    return _append(ledger_dir, {"agent": agent, "task": task, "status": "working",
                                "artifact": artifact, "outcome": None})


def done(ledger_dir, agent, task, artifact=None, outcome="done"):
    return _append(ledger_dir, {"agent": agent, "task": task, "status": "done",
                                "artifact": artifact, "outcome": outcome})


def load(ledger_dir):
    path = Path(ledger_dir) / "worklog.jsonl"
    if not path.exists():
        return []
    import json
    return [json.loads(l) for l in path.read_text().splitlines() if l.strip()]


def current_and_completed(ledger_dir):
    """Return (working, completed). An agent+task marked done removes it from
    working; anything working without a done is in progress."""
    rows = load(ledger_dir)
    done_keys = {(r["agent"], r["task"]) for r in rows if r["status"] == "done"}
    working = [r for r in rows if r["status"] == "working"
               and (r["agent"], r["task"]) not in done_keys]
    completed = [r for r in rows if r["status"] == "done"]
    return working, completed
