"""WO-3/WO-4: the irreversible boundary + the user-owned allow policy.

Severity × reversibility (architecture §7.3; vision §3/§5). Every action is
either REVERSIBLE (the interior — a draft, a corpus write, a local edit; git +
lineage is the rewind) or IRREVERSIBLE (it left the system for good — external
communication, external mutation, disclosure, destruction, spend).

- Reversible interior -> the earned-autonomy envelope (WO-1) is the only friction.
- Irreversible boundary -> DENY-BY-DEFAULT: auto-permits ONLY on a match in the
  user's allow policy (config/allow-policy.md — a protected path; ships with just
  ONE rule, the agent's delivery to its own principal), otherwise ASKS.

The one falsifiable guarantee: no irreversible action is auto-permitted without
an allow-match or a hand, and the gate records it before it acts. Deterministic;
no model (SE-1). Kept out of gate.py to hold its 300-line budget (X-1)."""

import os
import re
from pathlib import Path

import envelope_gate

REPO_ROOT = Path(__file__).resolve().parent.parent
ALLOW_POLICY_ENV = "TEAMOS_ALLOW_POLICY"
DEFAULT_ALLOW_POLICY = REPO_ROOT / "config" / "allow-policy.md"

# "Left the building" markers -> irreversible. Matched as whole TOKENS (not
# substrings) so "pay" doesn't fire on "display" and "mail" fires on "gmail".
IRREVERSIBLE_MARKERS = frozenset((
    "send", "post", "message", "mail", "email", "publish", "upload", "share",
    "deploy", "delete", "destroy", "pay", "payment", "purchase", "transfer",
    "wire", "charge", "refund", "provision", "terminate"))


def _tokens(name):
    """Split a tool name into lowercase tokens on non-alphanumerics AND camelCase
    (SlackPost -> slack, post; mcp__gmail__send_email -> mcp, gmail, send, email)."""
    out = []
    for part in re.split(r"[^A-Za-z0-9]+", name):
        out += re.findall(r"[A-Z]+(?=[A-Z][a-z])|[A-Z]?[a-z]+|[A-Z]+|[0-9]+", part)
    return [t.lower() for t in out if t]


def reversibility(tool_name, action_class):
    """"irreversible" if the action leaves the system (external comms / mutation
    / disclosure / destruction / spend), else "reversible". Web reads
    (WebFetch/WebSearch) are reversible here — their exfil risk is carried by
    taint + the outbound-content scan, not by the allow-policy boundary."""
    if action_class == "delete" or IRREVERSIBLE_MARKERS.intersection(_tokens(tool_name)):
        return "irreversible"
    return "reversible"


def _rules(policy_path=None):
    path = Path(policy_path or os.environ.get(ALLOW_POLICY_ENV) or DEFAULT_ALLOW_POLICY)
    try:
        lines = path.read_text().splitlines()
    except OSError:
        return []  # no policy file -> no rules -> deny-by-default (everything asks)
    # A line is a comment only if it STARTS with '#' (so a '#channel' target in a
    # rule survives); blank lines ignored. Everything else is a rule.
    rules = []
    for ln in lines:
        s = ln.strip()
        if s and not s.startswith("#"):
            rules.append(s.split())
    return rules


def allow_match(tool_name, target, policy_path=None):
    """A rule = `<tool-substring> [target-substring ...]`. Matches when the tool
    substring is in the tool name AND every target token is in the target.
    Empty policy -> no match -> every irreversible action asks. No model."""
    low, tgt = tool_name.lower(), (target or "").lower()
    for rule in _rules(policy_path):
        if rule[0].lower() in low and all(c.lower() in tgt for c in rule[1:]):
            return True
    return False


def apply(tool_name, action_class, target, verdict, rule_id, checks, findings,
          policy_path=None):
    """Post-inspection autonomy gate. Reversible -> earned-autonomy envelope
    (WO-1). Irreversible -> deny-by-default allow-policy boundary (WO-4). Only
    ever ADDS friction; never turns a safety ask/deny into a permit."""
    rev = reversibility(tool_name, action_class)
    checks.append(f"reversibility:{rev}")            # WO-3: labeled in the record
    if rev == "reversible":
        return envelope_gate.apply(action_class, verdict, rule_id, checks, findings)
    if verdict != "permit":
        return verdict, rule_id                      # already ask/deny: boundary met
    if allow_match(tool_name, target, policy_path):
        checks.append("allow-policy-match")
        return "permit", rule_id                     # user pre-authorized this act
    findings.append("boundary:needs-allow-or-confirmation")
    return "ask", "irreversible-hold"
