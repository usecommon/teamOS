"""FK6 measurement: L7 scoring (keyed to L6 versions), the weekly pulse
instrument, and the initiative-floor drift test. Instruments only — they measure,
they never fabricate a result (A-tests are earned, not faked). No language model.
"""

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hashchain  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
SCORER_AGENT_ID = "teamos-scorer/0.1"
PULSE_AGENT_ID = "teamos-pulse/0.1"
LIGHT_EDIT = 0.2  # R-11


def l6_version(path):
    """L6 key = latest git sha touching `path` (git IS Ledger 6)."""
    out = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "log", "-1", "--format=%H", "--", str(path)],
        capture_output=True, text=True).stdout.strip()
    return out or "uncommitted"


def score_deliverable(deliverable_path, skill_id, skill_version, invocation_id,
                      ledger_dir, metric="shadow_completeness"):
    """Score a shadow deliverable -> L7 record keyed to L6 (skill_version).
    Deterministic proxy: fraction of expected structural markers present."""
    ledger_dir = Path(ledger_dir)
    text = Path(deliverable_path).read_text()
    markers = ["#", "cadence", "source"]
    score = round(sum(1 for m in markers if m in text) / len(markers), 3)
    return hashchain.append(ledger_dir / "l7.jsonl", {
        "skill_id": skill_id,
        "skill_version": skill_version,      # joins performance to the version
        "invocation_id": invocation_id,
        "metric": metric,
        "score": score,
        "sample_ref": {"store": "deliverables", "path": str(deliverable_path),
                       "content_hash": hashchain.sha256_str(text)},
    }, SCORER_AGENT_ID)


def emit_pulse(question, ledger_dir, week_id):
    """Record that the weekly 1-question pulse was ASKED (instrument, not answer)."""
    ledger_dir = Path(ledger_dir)
    path = ledger_dir / "pulse" / f"{week_id}.question.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"week_id": week_id, "question": question,
                                "asked_at": _utc()}))
    return path


def record_pulse_response(value, principal_id, ledger_dir, week_id):
    """Record the principal's pulse answer -> L8 pulse_response (principal-auth)."""
    ledger_dir = Path(ledger_dir)
    return hashchain.append(ledger_dir / "l8.jsonl", {
        "signal_type": "pulse_response",
        "artifact_ref": {"store": "pulse", "path": f"{week_id}",
                         "content_hash": hashchain.sha256_str(str(value))},
        "principal_id": principal_id,
        "attribution": "principal_authenticated",
        "outcome": str(value),
        "harvest": {"method": "weekly-pulse", "harvested_at": _utc()},
    }, PULSE_AGENT_ID)


def weekly_accepted(ledger_dir, since_iso=None, until_iso=None):
    """Initiative floor (FR6): count accepted unprompted deliverables in a window.

    accepted = ✓ (endorsement) AND principal_authenticated AND lightly-or-not
    edited (edit distance <= 0.2 or no edit). Returns (count, records).
    """
    ledger_dir = Path(ledger_dir)
    l8 = ledger_dir / "l8.jsonl"
    if not l8.exists():
        return 0, []
    hits = []
    for line in l8.read_text().splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        if since_iso and r["ts"] < since_iso:
            continue
        if until_iso and r["ts"] > until_iso:
            continue
        if r["signal_type"] != "endorsement":
            continue
        if r["attribution"] != "principal_authenticated":
            continue
        dist = r.get("edit_distance_normalized")
        if dist is not None and dist > LIGHT_EDIT:
            continue
        hits.append(r)
    return len(hits), hits


def floor_met(count, floor=3):
    return count >= floor


def _utc():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
