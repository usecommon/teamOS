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

import hashlib
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import hashchain  # noqa: E402

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
    if tool_name in policy["action_classes"]:
        return policy["action_classes"][tool_name]
    lower = tool_name.lower()
    if any(m in lower for m in policy["send_tool_markers"]):
        return "send"
    return "tool"


def target_of(tool_input):
    for key in ("file_path", "path", "url", "command", "channel", "recipient"):
        if key in tool_input:
            return str(tool_input[key])[:200]
    return ""


def inspect(policy, tool_name, action_class, tool_input):
    """Returns (checks_run, findings, verdict, rule_id)."""
    checks, findings = [], []
    texts = list(flatten_strings(tool_input))
    joined = " ".join(texts)

    # tool-parameter scan — every call, every string param (FR2 probe #3)
    checks.append("tool-parameter-scan")
    findings += [f"param:{f}" for f in scan_secrets(policy, texts)]

    if tool_name == "Bash":
        command = str(tool_input.get("command", ""))
        checks.append("bash-egress-scan")
        egress = [p for p in policy["egress_patterns"] if p in command]
        if egress:
            findings += [f"egress:{p.strip()}" for p in egress]
        checks.append("bash-sensitive-read-scan")
        sensitive = [p for p in policy["sensitive_read_paths"] if p in command]
        if sensitive:
            findings += [f"sensitive-read:{p}" for p in sensitive]
        if egress and (sensitive or scan_secrets(policy, [command])):
            return checks, findings, "deny", "bash-exfil"
        if egress:
            return checks, findings, "ask", "bash-egress"
        if sensitive:
            return checks, findings, "ask", "sensitive-read"

    if action_class in ("write", "edit"):
        path = str(tool_input.get("file_path", tool_input.get("path", "")))
        checks.append("protected-path-check")
        rel = path.replace(str(REPO_ROOT) + "/", "")
        hits = [p for p in policy["protected_paths"] if rel.startswith(p) or p in rel]
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
        return checks, findings, "permit", "send-scanned-clean"

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
    action_class = classify(policy, tool_name)
    checks, findings, verdict, rule_id = inspect(policy, tool_name, action_class, tool_input)

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


def main():
    hook_input = json.load(sys.stdin)
    print(json.dumps(process(hook_input)))


if __name__ == "__main__":
    main()
