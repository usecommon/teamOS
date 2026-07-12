"""Day One Brief (FK5). A scheduled headless run assembles, unrequested:
  1. a digest (summary-level, links back into the store — m2),
  2. a ✓/✗ job draft from the compiled job graph,
  3. the first compiled deliverable (rendered into the store, linked from the DM),
and delivers it to a Slack DM. The send traverses the FK2 gate (emits L2). ✓/✗
reactions are harvested deterministically (SE-1: reactions.get only, no language
model, principal-authenticated per CN-1) into L8. Missed schedule => catch-up.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "hooks"))

import hashchain  # noqa: E402
import gate  # noqa: E402
import principal_auth  # noqa: E402

BRIEF_AGENT_ID = "teamos-brief/0.1"
# Slack emoji -> signal
ACCEPT_EMOJI = "white_check_mark"
REJECT_EMOJI = "x"


class GateBlocked(PermissionError):
    """The gate denied the send (e.g. circuit breaker open). A subclass of
    PermissionError so existing `except PermissionError` handlers still catch it,
    but run_if_due() distinguishes it (E3): a safety halt PAUSES the scheduled
    loop gracefully instead of crashing it. A post-permit send FAILURE stays a
    plain PermissionError — that is a real error, not a halt."""


# --- 1. assembly (summary-level with links; compiled content stays in store) ---

def assemble_brief(job_graph, out_dir, store_prefix="stores"):
    """Build the brief structure + render the first deliverable into the store.

    The DM carries a digest + job draft + a LINK to the deliverable; the full
    compiled content lives in the governed store, not in the message (m2).
    """
    out_dir = Path(out_dir)
    (out_dir / "deliverables").mkdir(parents=True, exist_ok=True)
    nodes = job_graph.get("nodes", [])

    digest = [f"{n['task_type']}: {n['occurrences']} seen, {n['cadence']}, "
              f"source {', '.join(n['sources'])}" for n in nodes]

    job_draft = [{
        "task_type": n["task_type"],
        "cadence": n["cadence"],
        "default": "propose",   # principal taps ✓ to accept / ✗ to reject
        "link": f"{store_prefix}/job_graph.json#{n['task_type']}",
    } for n in nodes]

    first_deliverable = None
    if nodes:
        top = max(nodes, key=lambda n: n["occurrences"])
        draft_path = out_dir / "deliverables" / f"{top['task_type']}-draft.md"
        # rendered from the node's exemplar REFERENCES (no raw bodies inlined)
        draft_path.write_text(
            f"# {top['task_type']} (compiled draft)\n\n"
            f"cadence: {top['cadence']} · sources: {', '.join(top['sources'])}\n"
            f"built from {top['occurrences']} prior exemplars "
            f"(see job_graph.json#{top['task_type']}).\n")
        first_deliverable = {
            "task_type": top["task_type"],
            "link": f"{store_prefix}/deliverables/{top['task_type']}-draft.md",
            "summary": f"First {top['task_type']} drafted from {top['occurrences']} exemplars.",
        }

    return {"digest": digest, "job_draft": job_draft,
            "first_deliverable": first_deliverable}


def render_dm(brief):
    """Render the brief to DM text — summary + links only, never raw content."""
    lines = ["*Day One Brief* (unrequested)", "", "*Recurring work found:*"]
    lines += [f"• {d}" for d in brief["digest"]]
    lines += ["", "*Job draft* — ✓ to accept, ✗ to reject:"]
    lines += [f"• {j['task_type']} ({j['cadence']}) → {j['link']}" for j in brief["job_draft"]]
    if brief["first_deliverable"]:
        fd = brief["first_deliverable"]
        lines += ["", f"*First deliverable:* {fd['summary']}", f"→ {fd['link']}"]
    return "\n".join(lines)


# --- 2. delivery (through the gate; emits L2) ---------------------------------

def _prior_successful_send(ledger_dir, payload_digest):
    """Return the ts of an already-succeeded send-receipt for this exact payload
    (D3 idempotency), or None. Deterministic ledger read — no model in the path."""
    l2 = Path(ledger_dir) / "l2.jsonl"
    if not l2.exists():
        return None
    for line in l2.read_text().splitlines():
        if not line.strip():
            continue
        try:
            r = json.loads(line)
        except ValueError:
            continue
        if (r.get("rule_id") == "send-receipt"
                and r.get("outcome") == "send_succeeded"
                and r.get("proposed_action", {}).get("payload_digest") == payload_digest):
            target = r["proposed_action"].get("target", "")
            return target.split("/", 1)[1] if "/" in target else target
    return None


def deliver(brief, channel, slack, ledger_dir, policy=None):
    """Send the brief DM. The send traverses the FK2 gate (L2) before posting.

    Returns (ts, l2_record). Raises GateBlocked if the gate blocks the send.
    Idempotent: an identical payload already send-receipted returns the prior ts.
    """
    ledger_dir = Path(ledger_dir)
    text = render_dm(brief)
    tool_input = {"channel": channel, "text": text, "blocks": []}

    prev_ledger = gate.LEDGER_DIR
    gate.LEDGER_DIR = ledger_dir
    try:
        decision = gate.process(
            {"tool_name": "slack_post_message", "tool_input": tool_input},
            policy or gate.load_policy())
    finally:
        gate.LEDGER_DIR = prev_ledger
    l2 = json.loads((ledger_dir / "l2.jsonl").read_text().splitlines()[-1])
    if decision["hookSpecificOutput"]["permissionDecision"] != "allow":
        # E3: a gate deny (e.g. breaker open) is a HALT, not a failure — raise a
        # distinct type so the scheduled loop can pause instead of crashing.
        raise GateBlocked(f"gate blocked the brief send: {l2['rule_id']}")

    # D3 — at-most-once at the send path: if a send-receipt for this exact
    # payload already succeeded, a prior run (or a crash-after-effect rerun)
    # already delivered it. Return that ts without re-posting. Scheduled-brief
    # content varies per slot, so an identical payload is a true duplicate.
    digest = hashchain.sha256_str(text)
    prior_ts = _prior_successful_send(ledger_dir, digest)
    if prior_ts is not None:
        return prior_ts, l2

    # T13 — record the OUTCOME, not only the decision: a permitted-but-failed
    # or double send is visible in the ledger (send-receipt record).
    try:
        ts = slack.post_message(channel, text=text)
        receipt_outcome, receipt_target = "send_succeeded", f"{channel}/{ts}"
    except Exception as exc:
        receipt_outcome, receipt_target = "send_failed", f"{channel}/{type(exc).__name__}"
        ts = None
    hashchain.append(ledger_dir / "l2.jsonl", {
        "proposed_action": {"tool": "slack_post_message",
                            "action_class": "send", "target": receipt_target,
                            "payload_digest": hashchain.sha256_str(text)},
        "verdict": "permit", "policy_version": l2["policy_version"],
        "rule_id": "send-receipt",
        "inspection": {"checks_run": ["send-receipt"], "findings": []},
        "outcome": receipt_outcome,
    }, BRIEF_AGENT_ID)
    if ts is None:
        raise PermissionError("send failed after permit — receipt ledgered")
    return ts, l2


# --- 3. reaction harvest (deterministic, principal-authenticated) -------------

def harvest_reactions(channel, ts, principal_user_id, slack, ledger_dir,
                      artifact_link="brief"):
    """Read reactions via the API only; count ✓/✗ ONLY from the principal's
    authenticated user id (CN-1). Others logged as unattributed, never counted.
    Point-in-time (OB-4): a later removal does not retract. No language model."""
    ledger_dir = Path(ledger_dir)
    reactions = slack.reactions_get(channel, ts)  # API, not message text (SE-1)
    harvested_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    records = []
    for r in reactions:
        if r["name"] not in (ACCEPT_EMOJI, REJECT_EMOJI):
            continue
        for user in r["users"]:
            principal = (user == principal_user_id)
            signal = "endorsement" if r["name"] == ACCEPT_EMOJI else "rejection"
            outcome = "accepted" if r["name"] == ACCEPT_EMOJI else "rejected"
            body = {
                "signal_type": signal,
                "artifact_ref": {"store": "brief", "path": f"{channel}/{ts}",
                                 "content_hash": hashchain.sha256_str(artifact_link)},
                "principal_id": user,
                "attribution": "principal_authenticated" if principal else "unattributed",
                "outcome": outcome,
                "harvest": {"method": "slack-reactions-get", "harvested_at": harvested_at},
            }
            if principal:
                # T7: API-verified identity gets the crypto stamp when a
                # principal keydir is configured — consumers verify, not trust
                sig = principal_auth.sign(body)
                if sig:
                    body["auth_sig"] = sig
            rec = hashchain.append(ledger_dir / "l8.jsonl", body, BRIEF_AGENT_ID)
            records.append(rec)
    return records


def count_accepted(records):
    """Count only principal-authenticated acceptances (the envelope's input)."""
    return sum(1 for r in records
               if r["attribution"] == "principal_authenticated"
               and r["outcome"] == "accepted")


# --- 4. scheduled catch-up (never a silent skip) ------------------------------

def run_if_due(task_name, interval_seconds, state_dir, action, now=None):
    """Run `action` if due or if a scheduled run was MISSED (catch-up). Never
    silently skips a missed run. Returns (ran, catch_up, result)."""
    state_dir = Path(state_dir)
    state_dir.mkdir(parents=True, exist_ok=True)
    state_file = state_dir / f"{task_name}.state.json"
    now = now or datetime.now(timezone.utc)
    last = None
    if state_file.exists():
        last = datetime.fromisoformat(json.loads(state_file.read_text())["last_run"])
    if last is None:
        due, catch_up = True, False
    else:
        elapsed = (now - last).total_seconds()
        due = elapsed >= interval_seconds
        catch_up = elapsed > interval_seconds * 1.5  # a scheduled slot was missed
    if not due:
        return False, False, None
    # T13 — claim the slot BEFORE the side effect is observable: a crash after
    # the action can no longer double-send on the rerun (at-most-once). The
    # claim is atomic; a failed action leaves the claim + failure marker.
    from fsutil import atomic_write_text
    prior_state = state_file.read_text() if state_file.exists() else None
    atomic_write_text(state_file, json.dumps(
        {"last_run": now.isoformat(), "catch_up": catch_up, "status": "claimed"}))
    try:
        result = action()
    except GateBlocked:
        # E3: a safety halt (breaker open) PAUSES the loop — it does not crash.
        # Roll back the slot claim so the run stays due and retries once the
        # breaker closes, instead of dying and retry-crashing every tick.
        if prior_state is None:
            state_file.unlink(missing_ok=True)
        else:
            atomic_write_text(state_file, prior_state)
        return False, catch_up, None
    except Exception:
        atomic_write_text(state_file, json.dumps(
            {"last_run": now.isoformat(), "catch_up": catch_up, "status": "failed"}))
        raise
    atomic_write_text(state_file, json.dumps(
        {"last_run": now.isoformat(), "catch_up": catch_up, "status": "completed"}))
    return True, catch_up, result
