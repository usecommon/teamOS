#!/usr/bin/env python3
"""Team OS gate — PreToolUse hook (FK2). Behavior spec: hooks/BEHAVIOR.md.
Line budget (X-1): <=300 lines, reviewable in ~15 minutes.

stdin: harness hook JSON {tool_name, tool_input, session_id, ...}
stdout: permission decision JSON. Side effect: hash-chained L2 record.

FR2: the gate looks INSIDE the action — bash egress scan, sensitive-read scan,
synced-path-as-send, tool-parameter scan, mandatory outbound-content scan on
sends. Payload inspection is always-on; posture only changes what happens
AFTER a finding, never whether inspection runs.
"""

import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import hashchain  # noqa: E402
import taint  # noqa: E402 — FR2 Layer A (same protected dir)

import yaml  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
POLICY_PATH = Path(os.environ.get("TEAMOS_POLICY", REPO_ROOT / "hooks" / "policy.yaml"))
LEDGER_DIR = Path(os.environ.get("TEAMOS_LEDGER_DIR", REPO_ROOT / "ledgers"))
POSTURE = os.environ.get("TEAMOS_POSTURE", "attended")
GATE_AGENT_ID = "teamos-gate/0.1"


def load_policy():
    text = POLICY_PATH.read_text()
    policy = yaml.safe_load(text)
    policy["_version"] = hashchain.sha256_str(text)
    return policy


def _breaker_open():
    """Circuit breaker check — UNCONDITIONAL (T3). The stop is always wired:
    a corrupt, missing, or unreadable breaker file counts as OPEN (deny), so
    deleting or mangling the state file bricks instead of disarming."""
    path = Path(os.environ.get("TEAMOS_BREAKER",
                               REPO_ROOT / "ledgers" / "breaker.json"))
    try:
        return json.loads(path.read_text()).get("state") != "closed"
    except (ValueError, OSError):
        return True  # fail closed


def flatten_strings(value):
    """Every string anywhere in the tool input — the parameter scan surface."""
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for v in value.values():
            yield from flatten_strings(v)
    elif isinstance(value, list):
        for v in value:
            yield from flatten_strings(v)


def scan_secrets(policy, texts):
    found = []
    for pattern in policy["secret_patterns"]:
        for text in texts:
            if re.search(pattern, text):
                found.append(f"secret-pattern:{pattern[:24]}")
                break
    return found


def classify(policy, tool_name):
    """Returns (action_class, known). Unknown tools default to SEND-class
    (scan + ask, FR2 Layer B) — never a silent pass-through 'tool' class."""
    if tool_name in policy["action_classes"]:
        return policy["action_classes"][tool_name], True
    lower = tool_name.lower()
    if any(m in lower for m in policy["send_tool_markers"]):
        return "send", True
    return "send", False


def protected_hits(policy, path_str):
    """Protected-path match on the RESOLVED real path (T3): symlinks and
    unicode tricks can't dodge the compare (mirrors gate_processor._safe_target).
    Relative policy entries match repo-relative resolved paths; absolute/~
    entries match by prefix."""
    if not path_str:
        return []
    p = Path(path_str).expanduser()
    resolved = p.resolve() if p.is_absolute() else (REPO_ROOT / p).resolve()
    s = str(resolved)
    rel = s[len(str(REPO_ROOT)) + 1:] if s.startswith(str(REPO_ROOT) + os.sep) else s
    hits = []
    for entry in policy["protected_paths"]:
        e = str(Path(entry).expanduser())
        if entry.startswith(("~", "/")):
            if s == e or s.startswith(e.rstrip("/") + os.sep):
                hits.append(entry)
        elif rel.startswith(entry) or entry in rel:
            hits.append(entry)
    return hits


def target_of(tool_input):
    for key in ("file_path", "path", "url", "command", "channel", "recipient"):
        if key in tool_input:
            return str(tool_input[key])[:200]
    return ""


def inspect(policy, tool_name, action_class, tool_input, known=True,
            session_id="unknown"):
    """Returns (checks_run, findings, verdict, rule_id)."""
    checks, findings = [], []
    # Circuit breaker: when open, every side-effectful action is halted (still
    # ledgered). Reads pass so the operator can inspect while halted.
    if action_class in ("write", "edit", "send", "execute", "schedule") and _breaker_open():
        return ["circuit-breaker"], ["breaker-open"], "deny", "circuit-open"
    texts = list(flatten_strings(tool_input))
    # scan through one base64 layer too (FR2 Layer B)
    texts += taint.decode_base64_blobs(texts)
    tainted = taint.is_tainted(LEDGER_DIR / "taint", session_id)

    # tool-parameter scan — every call, every string param (FR2 probe #3)
    checks.append("tool-parameter-scan")
    findings += [f"param:{f}" for f in scan_secrets(policy, texts)]

    if tool_name == "Bash":
        command = str(tool_input.get("command", ""))
        norm = taint.normalize_command(command)  # defeat quoting obfuscation
        checks.append("bash-egress-scan")
        egress = [p for p in policy["egress_patterns"] if p in norm]
        if egress:
            findings += [f"egress:{p.strip()}" for p in egress]
        checks.append("bash-sensitive-read-scan")
        sensitive = [p for p in policy["sensitive_read_paths"] if p in norm]
        if sensitive:
            findings += [f"sensitive-read:{p}" for p in sensitive]
        if egress and (sensitive or scan_secrets(policy, texts)):
            return checks, findings, "deny", "bash-exfil"
        if egress:
            return checks, findings, "ask", "bash-egress"
        if sensitive:
            return checks, findings, "ask", "sensitive-read"
        # a bash command touching a cloud-synced root IS a send (FR2)
        checks.append("bash-synced-path-scan")
        raw = taint.normalize_command(command, lower=False)
        synced = [p for p in policy["synced_paths"] if p in command or p in raw]
        if synced:
            findings += [f"synced-path:{p}" for p in synced]
            secrets = scan_secrets(policy, texts)
            findings += secrets
            return checks, findings, ("deny" if secrets else "ask"), "bash-synced-path"

    if action_class in ("write", "edit"):
        path = str(tool_input.get("file_path", tool_input.get("path", "")))
        checks.append("protected-path-check")
        hits = protected_hits(policy, path)
        if hits:
            findings += [f"protected-path:{p}" for p in hits]
            return checks, findings, "ask", "protected-path"
        checks.append("synced-path-check")
        synced = [p for p in policy["synced_paths"] if p in path]
        if synced:
            # A write into a cloud-synced dir IS a send: content scan mandatory
            findings += [f"synced-path:{p}" for p in synced]
            checks.append("outbound-content-scan")
            secrets = scan_secrets(policy, texts)
            findings += secrets
            verdict = "deny" if secrets else "ask"
            return checks, findings, verdict, "synced-path-send"

    if action_class == "send":
        checks.append("outbound-content-scan")  # mandatory, AT-6
        secrets = scan_secrets(policy, texts)
        if secrets:
            findings += secrets
            return checks, findings, "deny", "outbound-secret"
        if findings:  # param-scan already hit
            return checks, findings, "deny", "outbound-secret"
        if not known:
            # unknown tool: egress-capable until proven otherwise (Layer B)
            return checks, findings, "ask", "unknown-tool-send"
        if tainted:
            # Layer A: untrusted content is in-session; the send's target may
            # be attacker-chosen plan structure — require confirmation (§7.7)
            checks.append("taint-check")
            findings.append("taint:session")
            return checks, findings, "ask", "taint-confirm"
        return checks, findings, "permit", "send-scanned-clean"

    if action_class == "schedule" and tainted:
        # untrusted content cannot add a step without confirmation (§7.7)
        checks.append("taint-check")
        findings.append("taint:session")
        return checks, findings, "ask", "taint-confirm"

    if findings:
        return checks, findings, "ask", "param-secret"
    return checks, findings, "permit", "default-permit"


VERDICT_TO_DECISION = {"permit": "allow", "deny": "deny", "ask": "ask", "escalate": "ask"}
VERDICT_TO_OUTCOME = {
    "permit": "gate_passed",
    "deny": "gate_blocked",
    "ask": "escalated_to_human",
    "escalate": "escalated_to_human",
}


def process(hook_input, policy=None):
    policy = policy or load_policy()
    tool_name = hook_input.get("tool_name", "unknown")
    tool_input = hook_input.get("tool_input", {}) or {}
    session_id = hook_input.get("session_id", "unknown")
    action_class, known = classify(policy, tool_name)
    checks, findings, verdict, rule_id = inspect(
        policy, tool_name, action_class, tool_input, known, session_id)

    # mark taint AFTER inspection: a permitted/asked read of untrusted content
    # (corpus, inbox, external fetch) taints the session going forward
    if verdict != "deny":
        src = taint.taints(policy, tool_name, action_class, target_of(tool_input))
        if src:
            taint.mark(LEDGER_DIR / "taint", session_id, src)

    record_body = {
        "proposed_action": {
            "tool": tool_name,
            "action_class": action_class,
            "target": target_of(tool_input),
            "payload_digest": hashchain.sha256_str(hashchain.canonical(tool_input)),
        },
        "verdict": verdict,
        "policy_version": policy["_version"],
        "rule_id": rule_id,
        "inspection": {"checks_run": checks, "findings": findings},
        "outcome": VERDICT_TO_OUTCOME[verdict],
        "posture": POSTURE,
    }
    hashchain.append(LEDGER_DIR / "l2.jsonl", record_body, GATE_AGENT_ID)

    reason = f"teamos-gate: {rule_id}" + (f" [{'; '.join(findings[:4])}]" if findings else "")
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": VERDICT_TO_DECISION[verdict],
            "permissionDecisionReason": reason,
        }
    }


def _deny_response(reason):
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }


def main():
    """Fail CLOSED: a gate crash must never become a permit. Any exception
    (malformed stdin, broken policy, unwritable ledger) => deny + best-effort
    gate-error L2 record."""
    try:
        hook_input = json.load(sys.stdin)
        print(json.dumps(process(hook_input)))
    except Exception as exc:  # noqa: BLE001 — everything denies
        try:
            hashchain.append(LEDGER_DIR / "l2.jsonl", {
                "proposed_action": {"tool": "unknown", "action_class": "unknown",
                                    "target": "", "payload_digest": "sha256:0"},
                "verdict": "deny",
                "policy_version": "gate-error",
                "rule_id": "gate-error",
                "inspection": {"checks_run": ["gate-crash-handler"],
                               "findings": [f"gate-error:{type(exc).__name__}"]},
                "outcome": "gate_blocked",
                "posture": POSTURE,
            }, GATE_AGENT_ID)
        except Exception:  # noqa: BLE001 — ledger down: still deny
            pass
        # stdout deny JSON (exit-0 path) AND exit 2 (blocking-error path):
        # whichever the harness honors, the tool call is blocked.
        print(json.dumps(_deny_response(
            f"teamos-gate: gate-error ({type(exc).__name__}) — failing closed")))
        print(f"teamos-gate: gate-error ({type(exc).__name__}) — failing closed",
              file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
