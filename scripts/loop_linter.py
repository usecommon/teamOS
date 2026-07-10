"""Loop-prompt linter (FK6c). Validates scheduled-task templates/prompts against
a door-tools-only allowlist BEFORE install/registration. Rule set: Team OS door
tools only, no third-party MCP names, no raw URLs. This is the path-(b) fence in
code (the residual — non-door usage in a cloud session is unobservable
server-side — is carried by disclosure, §9)."""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from door import DOOR_TOOLS  # noqa: E402

_MCP_TOOL_RE = re.compile(r"\bmcp__([a-z0-9_]+)", re.IGNORECASE)
_URL_RE = re.compile(r"https?://", re.IGNORECASE)
_TEAMOS_MCP_PREFIXES = ("teamos", "team_os", "teamos_door")


def lint_prompt(prompt):
    """Return (ok, findings). ok=True means safe to install."""
    findings = []
    for m in _MCP_TOOL_RE.finditer(prompt):
        server = m.group(1).lower()
        if not server.startswith(_TEAMOS_MCP_PREFIXES):
            findings.append(f"third-party-mcp:{m.group(0)}")
    if _URL_RE.search(prompt):
        findings.append("raw-url")
    # any explicit tool call must be a door tool
    for m in re.finditer(r"\b(propose_\w+|read_\w+|list_desired_schedules)\b", prompt):
        if m.group(1) not in DOOR_TOOLS:
            findings.append(f"non-door-tool:{m.group(1)}")
    return (not findings), findings


def lint_template(template):
    return lint_prompt(template.get("prompt", ""))
