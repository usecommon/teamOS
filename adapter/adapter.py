"""Harness -> mainline-schema translation. See package docstring.

Every produced object validates against docs/schemas/. Lineage rule: every
corpus/skill object gets a PROV-lite sidecar (source, evidence, transformation,
confidence) — an unlabelled write is rejected by construction, so the adapter
never emits one.
"""

import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import hashchain  # noqa: E402 — the single chain implementation (FK2)

SCHEMA_VERSION = "0.1"
ADAPTER_AGENT_ID = "teamos-adapter/0.1"
REPO_ROOT = Path(__file__).resolve().parent.parent
PIN_PATH = Path(__file__).resolve().parent / "harness_pin.json"


class HarnessPinError(RuntimeError):
    pass


def load_pin():
    return json.loads(PIN_PATH.read_text())


def _harness_version_from_cli():
    out = subprocess.run(
        ["claude", "--version"], capture_output=True, text=True, timeout=30
    ).stdout.strip()
    m = re.search(r"(\d+\.\d+\.\d+)", out)
    if not m:
        raise HarnessPinError(f"cannot parse harness version from: {out!r}")
    return m.group(1)


def assert_harness(version=None, surface=None):
    """FR5 startup assert: version (major.minor) and surface must match the pin.

    A mismatch raises — callers HALT rather than run on an unvalidated harness
    (SE-5: version-assert failure at run start = HALT, streak paused).
    """
    pin = load_pin()
    version = version or _harness_version_from_cli()
    surface = surface or pin["surface"]
    want = pin["version"].split(".")[:2]
    got = version.split(".")[:2]
    if got != want:
        raise HarnessPinError(
            f"harness version {version} does not match pin {pin['version']} "
            f"(major.minor); re-run the FK1 adapter suite and FK2 headless-hook "
            f"test, then update the pin"
        )
    if surface != pin["surface"]:
        raise HarnessPinError(
            f"surface {surface!r} is not the runtime of record {pin['surface']!r}; "
            f"every other surface is a divergence-log entry until it passes its "
            f"own FK2-class test"
        )
    return version


# --- helpers -----------------------------------------------------------------


def _utc(ts=None):
    dt = ts or datetime.now(timezone.utc)
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _file_mtime_utc(path):
    return _utc(datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc))


def _sha256(data):
    if isinstance(data, str):
        data = data.encode("utf-8")
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def chain_envelope(record, prev_hash, record_id, ts):
    """Attach the ledger-common envelope with hash chaining (delegates to the
    single chain implementation in scripts/hashchain.py)."""
    return hashchain.envelope(
        record, prev_hash, record_id, ts, ADAPTER_AGENT_ID, SCHEMA_VERSION
    )


def _sidecar(entity_id, source_path, content, transformation):
    """PROV-lite sidecar for a deterministic adapter translation.

    Confidence is 'high': the content is a verbatim-or-mechanical translation of
    an artifact the principal authored on their own machine (source_type
    harness-artifact).
    """
    return {
        "entity_id": entity_id,
        "generated_by": {"transformation": transformation, "at": _utc()},
        "agent": ADAPTER_AGENT_ID,
        "sources": [
            {
                "source_type": "harness-artifact",
                "locator": str(source_path),
                "content_hash": _sha256(content),
            }
        ],
        "evidence": [str(source_path)],
        "confidence": "high",
        "update_history": [],
    }


def _parse_frontmatter(text):
    """Return (frontmatter_dict, body). Tolerates files without frontmatter."""
    m = re.match(r"\A---\n(.*?)\n---\n?(.*)\Z", text, re.DOTALL)
    if not m:
        return {}, text
    return (yaml.safe_load(m.group(1)) or {}), m.group(2)


# --- commands -> skills (skill.schema.json) ----------------------------------

# Field-miss (divergence log, class field-miss): the harness command format
# declares no capture-surface tier. Commands execute with local file access, so
# the import defaults to the full tier; the value is a DEFAULT, not a mapping.
DEFAULT_CAPTURE_SURFACE = "cloud+synced+local-folders"


def _split_allowed_tools(raw):
    """Split 'Bash(git log:*), Read, Write' on top-level commas only."""
    tools, buf, depth = [], "", 0
    for ch in raw:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == "," and depth == 0:
            tools.append(buf.strip())
            buf = ""
        else:
            buf += ch
    if buf.strip():
        tools.append(buf.strip())
    return tools


def commands_to_skills(footprint_dir):
    """Translate ~/.claude/commands/*.md into skill registry entries + sidecars.

    Returns list of (skill_dict, sidecar_dict, body_text).
    """
    commands_dir = Path(footprint_dir) / "commands"
    out = []
    for path in sorted(commands_dir.glob("*.md")):
        text = path.read_text()
        fm, body = _parse_frontmatter(text)
        name = path.stem
        skill_id = f"personal/{name}"
        raw_tools = fm.get("allowed-tools", "")
        tools = _split_allowed_tools(raw_tools) if raw_tools else []
        skill = {
            "skill_id": skill_id,
            "name": name,
            "description": fm.get("description", body.strip().splitlines()[0] if body.strip() else name),
            "namespace": "personal",
            "version": _sha256(text),
            "capability_manifest": {
                "capture_surface": DEFAULT_CAPTURE_SURFACE,
                "tools": tools,
            },
            "evidence_links": [],
            "body_path": f"stores/skills/{name}/SKILL.md",
            "lineage_sidecar": f"stores/skills/{name}/SKILL.lineage.json",
        }
        sidecar = _sidecar(skill_id, path, text, "adapter-translation:command-to-skill")
        out.append((skill, sidecar, body))
    return out


def skill_to_command_md(skill, body):
    """Render a skill entry back to harness command format (round-trip check)."""
    fm = {"description": skill["description"]}
    if skill["capability_manifest"]["tools"]:
        fm["allowed-tools"] = ", ".join(skill["capability_manifest"]["tools"])
    fm_text = yaml.safe_dump(fm, sort_keys=False, default_flow_style=False).strip()
    return f"---\n{fm_text}\n---\n{body}"


# --- CLAUDE.md cascade -> scopes + corpus entries -----------------------------

# The harness cascade (enterprise -> project -> user) maps onto the five-scope
# model's (company -> team -> individual) subset. Division/org levels have no
# harness counterpart at fork scale (n<=3) — scope-LEVEL gap, not a field gap.
CASCADE_MAP = {"user": "individual", "project": "team", "enterprise": "company"}


def _md_to_blocks(body):
    """Split markdown into addressable blocks (one per heading section)."""
    blocks, current = [], []
    for line in body.splitlines():
        if line.startswith("#") and current:
            blocks.append("\n".join(current).strip())
            current = [line]
        else:
            current.append(line)
    if current:
        blocks.append("\n".join(current).strip())
    return [
        {"block_id": f"b{i + 1}", "text": text}
        for i, text in enumerate(b for b in blocks if b)
    ]


def claude_md_to_scopes(user_claude_md=None, project_claude_md=None):
    """Translate CLAUDE.md cascade files into scope nodes + typed corpus entries.

    Returns (scopes, entries) where entries is a list of
    (corpus_entry_dict, sidecar_dict).
    """
    scopes, entries = [], []
    specs = []
    if project_claude_md:
        specs.append(("project", Path(project_claude_md), "context"))
    if user_claude_md:
        specs.append(("user", Path(user_claude_md), "profile"))

    parent_for = {"team": None, "individual": None}
    for harness_level, path, entry_type in specs:
        level = CASCADE_MAP[harness_level]
        text = path.read_text()
        title = next(
            (l.lstrip("# ").strip() for l in text.splitlines() if l.startswith("#")),
            path.name,
        )
        entry_id = f"{level}/claude-md-{path.parent.name or 'root'}"
        entry = {
            "entry_id": entry_id,
            "entry_type": entry_type,
            "title": title,
            "scope": level,
            "status": "active",
            "created": _file_mtime_utc(path),
            "updated": _file_mtime_utc(path),
            "blocks": _md_to_blocks(text),
            "lineage_sidecar": f"stores/corpus/{level}/{path.stem}.lineage.json",
        }
        sidecar = _sidecar(entry_id, path, text, "adapter-translation:claude-md-to-corpus")
        entries.append((entry, sidecar))

        scope = {
            "scope_id": f"scope/{level}",
            "level": level,
            "parent_scope_id": parent_for.get(level),
            "context": [entry_id] if entry_type == "context" else [],
            "profile": [entry_id] if entry_type == "profile" else [],
            "experience": [],
        }
        scopes.append(scope)

    # Wire individual under team when both exist (cascade nesting, §3.1).
    by_level = {s["level"]: s for s in scopes}
    if "individual" in by_level and "team" in by_level:
        by_level["individual"]["parent_scope_id"] = by_level["team"]["scope_id"]
    return scopes, entries


# --- transcripts (JSONL) -> L1 execution-trace spans ---------------------------


def transcript_to_l1_spans(jsonl_path):
    """Compile a harness session transcript into hash-chained L1 span records.

    Content is never inlined: content_ref points back into the transcript file
    by line, with a content hash (arch §5 L1 minimization).
    """
    path = Path(jsonl_path)
    lines = path.read_text().splitlines()
    events = []
    for n, line in enumerate(lines, start=1):
        if line.strip():
            events.append((n, line, json.loads(line)))

    spans, prev_hash = [], None
    trace_id = None
    counter = 0

    # tool_use_id -> error flag, from the tool_result blocks in user events
    result_errors = {}
    for _, _, ev in events:
        if ev.get("type") != "user":
            continue
        content = ev.get("message", {}).get("content")
        if isinstance(content, list):
            for block in content:
                if block.get("type") == "tool_result":
                    result_errors[block.get("tool_use_id")] = bool(
                        block.get("is_error", False)
                    )

    def next_ts(i):
        for m in range(i + 1, len(events)):
            ts = events[m][2].get("timestamp")
            if ts:
                return ts
        return events[i][2].get("timestamp")

    for i, (lineno, raw, ev) in enumerate(events):
        if ev.get("type") != "assistant":
            continue
        msg = ev.get("message", {})
        trace_id = trace_id or ev.get("sessionId", "unknown-session")
        content = msg.get("content", [])
        content_blocks = content if isinstance(content, list) else []
        tool_uses = [b for b in content_blocks if b.get("type") == "tool_use"]

        def make_span(operation, name, tool_name=None, span_suffix=None, status="ok"):
            nonlocal prev_hash, counter
            counter += 1
            attributes = {}
            if msg.get("model"):
                attributes["gen_ai_request_model"] = msg["model"]
                attributes["gen_ai_response_model"] = msg["model"]
            usage = msg.get("usage", {})
            if "input_tokens" in usage:
                attributes["gen_ai_usage_input_tokens"] = usage["input_tokens"]
            if "output_tokens" in usage:
                attributes["gen_ai_usage_output_tokens"] = usage["output_tokens"]
            if tool_name:
                attributes["gen_ai_tool_name"] = tool_name
            span = {
                "trace_id": trace_id,
                "span_id": span_suffix or ev.get("uuid", f"span-{counter}"),
                "parent_span_id": ev.get("parentUuid"),
                "name": name,
                "operation": operation,
                "start_time": ev.get("timestamp"),
                "end_time": next_ts(i),
                "status": status,
                "session_id": ev.get("sessionId", "unknown-session"),
                "attributes": attributes,
                "content_ref": {
                    "store": "harness-transcripts",
                    "path": f"{path}#L{lineno}",
                    "content_hash": _sha256(raw),
                },
            }
            prev_hash_local = prev_hash
            record = chain_envelope(
                span, prev_hash_local, f"l1-{trace_id}-{counter}", _utc()
            )
            prev_hash = record["hash"]
            return record

        if tool_uses:
            for tu in tool_uses:
                spans.append(
                    make_span(
                        "execute_tool",
                        tu.get("name", "unknown-tool"),
                        tool_name=tu.get("name"),
                        span_suffix=tu.get("id"),
                        status="error" if result_errors.get(tu.get("id")) else "ok",
                    )
                )
        else:
            spans.append(make_span("chat", "assistant-turn"))
    return spans


def main():
    version = assert_harness()
    print(f"harness pin OK: {version} on {load_pin()['surface']}")


if __name__ == "__main__":
    main()
