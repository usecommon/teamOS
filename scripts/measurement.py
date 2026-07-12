"""FK6 measurement: L7 scoring (keyed to L6 versions), the weekly pulse
instrument, and the initiative-floor drift test. Instruments only — they measure,
they never fabricate a result (A-tests are earned, not faked). No language model.
"""

import json
import math
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hashchain  # noqa: E402
import principal_auth  # noqa: E402

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
                      ledger_dir, metric="structural_markers_scaffold"):
    """Score a shadow deliverable -> L7 record keyed to L6 (skill_version).

    T8 — SCAFFOLDING, NOT LOAD-BEARING: the structural-marker fraction is
    trivially gameable (three magic strings -> 1.0), so the record carries
    load_bearing=false and the promotion gate REFUSES to count it toward the
    eval floor. It exists only to exercise the L7 plumbing until a real
    metric (principal acceptance keyed to invocations) produces load-bearing
    records via record_eval()."""
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
        "load_bearing": False,               # promotion must not rely on this
        "sample_ref": {"store": "deliverables", "path": str(deliverable_path),
                       "content_hash": hashchain.sha256_str(text)},
    }, SCORER_AGENT_ID)


def record_eval(skill_id, skill_version, invocation_id, metric, score,
                sample_ref, ledger_dir):
    """Write a LOAD-BEARING L7 record — for real, earned metrics only
    (e.g. verified principal acceptance keyed to an invocation). This is the
    only kind of record the promotion eval floor counts (T8)."""
    return hashchain.append(Path(ledger_dir) / "l7.jsonl", {
        "skill_id": skill_id,
        "skill_version": skill_version,
        "invocation_id": invocation_id,
        "metric": metric,
        "score": score,
        "load_bearing": True,
        "sample_ref": sample_ref,
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
    """Initiative floor (FR6): count accepted UNPROMPTED deliverables in a window.

    accepted = ✓ (endorsement) AND principal_authenticated AND unprompted=true
    AND measured-lightly-or-not edited (edit distance PRESENT and <= 0.2 —
    a missing distance is NOT accepted, fail safe). Each distinct deliverable
    (artifact path) counts once per window: re-endorsing a recurring digest or
    padding duplicates never inflates the floor (T6). Returns (count, records).
    """
    ledger_dir = Path(ledger_dir)
    l8 = ledger_dir / "l8.jsonl"
    if not l8.exists():
        return 0, []
    hits, seen_artifacts = [], set()
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
        if not principal_auth.verified(r):
            continue  # T7: crypto-verified when a keydir is configured
        if not r.get("unprompted", False):
            continue  # prompted work never inflates the floor
        dist = r.get("edit_distance_normalized")
        if dist is None or dist > LIGHT_EDIT:
            continue  # unmeasured = not accepted (fail safe)
        key = (r.get("artifact_ref") or {}).get("path", r["record_id"])
        if key in seen_artifacts:
            continue  # dedupe: one deliverable, one floor count
        seen_artifacts.add(key)
        hits.append(r)
    return len(hits), hits


def floor_met(count, floor=3):
    return count >= floor


def proxy_behavior_correlation(pairs):
    """A-A4 primary (ME-1): correlation between the production proxy and
    downstream-use behavior, reported WITH its interval (pre-registered: never
    a bare point estimate). pairs: [(proxy_score, behavior_value), ...].
    Pearson r + Fisher-z 95% CI; n<4 or zero variance => inconclusive."""
    n = len(pairs)
    out = {"n": n, "r": None, "interval": None, "result": "inconclusive"}
    if n < 4:
        return out
    xs, ys = [p[0] for p in pairs], [p[1] for p in pairs]
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in ys)
    if sxx == 0 or syy == 0:
        return out
    r = sum((x - mx) * (y - my) for x, y in pairs) / math.sqrt(sxx * syy)
    r = max(-0.999999, min(0.999999, r))
    z = 0.5 * math.log((1 + r) / (1 - r))
    se = 1 / math.sqrt(n - 3)
    lo, hi = math.tanh(z - 1.96 * se), math.tanh(z + 1.96 * se)
    out.update(r=round(r, 4), interval=[round(lo, 4), round(hi, 4)])
    if lo > 0:
        out["result"] = "correlated"
    return out


def _utc():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
