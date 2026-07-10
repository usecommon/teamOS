"""G/FK1 functional gate: the adapter round-trips fixture harness artifacts into
valid mainline-schema objects; the harness pin asserts; content never inlines;
hash chains verify and break on tampering."""

import hashlib
import json
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from adapter import adapter  # noqa: E402
from schema_registry import validator_for  # noqa: E402

FOOTPRINT = REPO_ROOT / "fixtures" / "harness-footprint" / "dot-claude"
PROJECT = REPO_ROOT / "fixtures" / "harness-footprint" / "project"
TRANSCRIPT = FOOTPRINT / "projects" / "fixture-project" / "session-0001.jsonl"


class HarnessPin(unittest.TestCase):
    def test_matching_pin_passes(self):
        pin = adapter.load_pin()
        self.assertEqual(adapter.assert_harness(version=pin["version"]), pin["version"])

    def test_patch_drift_within_pin_passes(self):
        pin = adapter.load_pin()
        major, minor, _ = pin["version"].split(".")
        adapter.assert_harness(version=f"{major}.{minor}.999")

    def test_version_mismatch_halts(self):
        with self.assertRaises(adapter.HarnessPinError):
            adapter.assert_harness(version="99.0.0")

    def test_surface_mismatch_halts(self):
        pin = adapter.load_pin()
        with self.assertRaises(adapter.HarnessPinError):
            adapter.assert_harness(version=pin["version"], surface="cowork-cloud")


class CommandsToSkills(unittest.TestCase):
    def setUp(self):
        self.results = adapter.commands_to_skills(FOOTPRINT)

    def test_all_fixture_commands_translate(self):
        self.assertEqual(
            [s["name"] for s, _, _ in self.results], ["standup-notes", "weekly-digest"]
        )

    def test_skills_validate_against_schema(self):
        v = validator_for("skill.schema.json")
        for skill, _, _ in self.results:
            v.validate(skill)

    def test_sidecars_validate_and_carry_lineage(self):
        v = validator_for("lineage-sidecar.schema.json")
        for skill, sidecar, _ in self.results:
            v.validate(sidecar)
            self.assertEqual(sidecar["entity_id"], skill["skill_id"])
            self.assertEqual(sidecar["sources"][0]["source_type"], "harness-artifact")

    def test_allowed_tools_parse_with_parenthesized_commas(self):
        digest = next(s for s, _, _ in self.results if s["name"] == "weekly-digest")
        self.assertEqual(
            digest["capability_manifest"]["tools"],
            ["Bash(git log:*)", "Read", "Write"],
        )

    def test_round_trip_semantic_equality(self):
        for skill, _, body in self.results:
            rendered = adapter.skill_to_command_md(skill, body)
            fm, body2 = adapter._parse_frontmatter(rendered)
            self.assertEqual(fm.get("description"), skill["description"])
            tools = (
                adapter._split_allowed_tools(fm["allowed-tools"])
                if "allowed-tools" in fm
                else []
            )
            self.assertEqual(tools, skill["capability_manifest"]["tools"])
            self.assertEqual(body2.strip(), body.strip())


class ClaudeMdToScopes(unittest.TestCase):
    def setUp(self):
        self.scopes, self.entries = adapter.claude_md_to_scopes(
            user_claude_md=FOOTPRINT / "CLAUDE.md",
            project_claude_md=PROJECT / "CLAUDE.md",
        )

    def test_scopes_validate(self):
        v = validator_for("scope.schema.json")
        for scope in self.scopes:
            v.validate(scope)

    def test_entries_and_sidecars_validate(self):
        ve = validator_for("corpus-entry.schema.json")
        vs = validator_for("lineage-sidecar.schema.json")
        for entry, sidecar in self.entries:
            ve.validate(entry)
            vs.validate(sidecar)

    def test_cascade_levels_and_nesting(self):
        by_level = {s["level"]: s for s in self.scopes}
        self.assertEqual(set(by_level), {"team", "individual"})
        self.assertEqual(
            by_level["individual"]["parent_scope_id"], by_level["team"]["scope_id"]
        )

    def test_entry_types_follow_cascade_position(self):
        types = {e["scope"]: e["entry_type"] for e, _ in self.entries}
        self.assertEqual(types, {"team": "context", "individual": "profile"})

    def test_blocks_are_addressable(self):
        for entry, _ in self.entries:
            self.assertGreater(len(entry["blocks"]), 1)
            ids = [b["block_id"] for b in entry["blocks"]]
            self.assertEqual(len(ids), len(set(ids)))


class TranscriptToL1(unittest.TestCase):
    def setUp(self):
        self.spans = adapter.transcript_to_l1_spans(TRANSCRIPT)

    def test_spans_validate(self):
        v = validator_for("ledger-l1-execution-trace.schema.json")
        for span in self.spans:
            v.validate(span)

    def test_tool_use_becomes_execute_tool_spans(self):
        ops = [s["operation"] for s in self.spans]
        self.assertEqual(ops.count("execute_tool"), 2)
        self.assertEqual(ops.count("chat"), 1)
        tools = {
            s["attributes"]["gen_ai_tool_name"]
            for s in self.spans
            if s["operation"] == "execute_tool"
        }
        self.assertEqual(tools, {"Bash", "Write"})

    def test_content_never_inlined(self):
        # arch §5 L1 minimization: span content lives behind content_ref only.
        transcript_text = TRANSCRIPT.read_text()
        for span in self.spans:
            serialized = json.dumps(
                {k: v for k, v in span.items() if k != "content_ref"}
            )
            self.assertNotIn("git log --since", serialized)
            self.assertNotIn("Weekly digest", serialized)
        for span in self.spans:
            path, _, lineno = span["content_ref"]["path"].partition("#L")
            line = transcript_text.splitlines()[int(lineno) - 1]
            self.assertEqual(
                span["content_ref"]["content_hash"],
                "sha256:" + hashlib.sha256(line.encode()).hexdigest(),
            )

    def test_hash_chain_verifies_and_breaks_on_tamper(self):
        prev = None
        for span in self.spans:
            body = {k: v for k, v in span.items() if k != "hash"}
            expected = "sha256:" + hashlib.sha256(
                ((prev or "") + json.dumps(body, sort_keys=True, separators=(",", ":"))).encode()
            ).hexdigest()
            self.assertEqual(span["hash"], expected)
            prev = span["hash"]
        # Tamper: mutate a mid-chain record -> its hash no longer matches.
        tampered = json.loads(json.dumps(self.spans[1]))
        tampered["name"] = "forged-tool"
        body = {k: v for k, v in tampered.items() if k != "hash"}
        recomputed = "sha256:" + hashlib.sha256(
            ((self.spans[0]["hash"]) + json.dumps(body, sort_keys=True, separators=(",", ":"))).encode()
        ).hexdigest()
        self.assertNotEqual(tampered["hash"], recomputed)

    def test_usage_and_model_attributes_mapped(self):
        for span in self.spans:
            self.assertEqual(span["attributes"]["gen_ai_request_model"], "claude-fixture-1")
            self.assertIn("gen_ai_usage_input_tokens", span["attributes"])


if __name__ == "__main__":
    unittest.main()
