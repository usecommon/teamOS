"""FK4 F-tests: 5 planted transformations -> >=4 found w/ correct sources; raw
ingest provably absent (distill-then-discard); 2024-dated imperative doc
quarantined not compiled; Claude Code footprint imports as valid skills/profile
(FR3); FK3b gate respected."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import compile_footprint as cf  # noqa: E402
import hashchain  # noqa: E402
from schema_registry import validator_for  # noqa: E402

FOOTPRINT = REPO_ROOT / "fixtures" / "footprint"
CC = REPO_ROOT / "fixtures" / "harness-footprint" / "dot-claude"
CC_PROJECT = REPO_ROOT / "fixtures" / "harness-footprint" / "project"

PLANTED = {  # type -> (expected source, expected cadence)
    "weekly-digest": ("git-commits", "weekly"),
    "standup": ("transcripts", "daily"),
    "meeting-summary": ("meeting-notes", "weekly"),
    "status-update": ("task-tracker", "weekly"),
    "release-notes": ("git-tags", "monthly"),
}


class Compile(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.d = Path(self.tmp.name)
        self.out = self.d / "out"
        items = cf.load_footprint(FOOTPRINT / "artifacts")
        items += cf.load_footprint(FOOTPRINT / "docs")  # includes the injection doc
        self.result = cf.compile_footprint(
            items, self.out, self.d,
            cc_footprint_dir=CC,
            cc_user_claude_md=CC / "CLAUDE.md",
            cc_project_claude_md=CC_PROJECT / "CLAUDE.md",
        )

    def tearDown(self):
        self.tmp.cleanup()

    def test_finds_at_least_4_of_5_with_correct_sources(self):
        by_type = {n["task_type"]: n for n in self.result["nodes"]}
        found = [t for t in PLANTED if t in by_type]
        self.assertGreaterEqual(len(found), 4, f"found {found}")
        for t in found:
            self.assertEqual(by_type[t]["sources"], [PLANTED[t][0]], t)

    def test_cadence_inferred(self):
        by_type = {n["task_type"]: n for n in self.result["nodes"]}
        for t, (_, cadence) in PLANTED.items():
            if t in by_type:
                self.assertEqual(by_type[t]["cadence"], cadence, t)

    def test_imperative_doc_quarantined_not_compiled(self):
        q = [Path(p).name for p in self.result["quarantined"]]
        self.assertIn("old-vendor-note-2024-03-01.md", q)
        # never became a job node or skill
        types = {n["task_type"] for n in self.result["nodes"]}
        self.assertNotIn("old-vendor-note", types)
        # a flag file exists; the executable instruction is not turned into an exemplar
        flags = list((self.out / "quarantine").glob("*.flag.json"))
        self.assertEqual(len(flags), 1)
        flag = json.loads(flags[0].read_text())
        self.assertEqual(flag["reason"], "imperative-content")

    def test_clean_artifacts_not_false_quarantined(self):
        self.assertEqual(len(self.result["quarantined"]), 1)  # only the injection doc

    def test_raw_ingest_provably_absent(self):
        # distill-then-discard: a unique raw body phrase must not appear in the
        # compiled job graph (which holds references + hashes only).
        jg = (self.out / "job_graph.json").read_text()
        self.assertNotIn("Shipped: parser fix", jg)
        self.assertNotIn("attacker@evil.example", jg)
        # nodes carry exemplar REFERENCES with hashes, not bodies
        for node in self.result["nodes"]:
            for ref in node["exemplar_refs"]:
                self.assertIn("content_hash", ref)
                self.assertTrue(ref["content_hash"].startswith("sha256:"))

    def test_cc_footprint_imports_usable_skills_and_profile(self):
        # FR3: the Claude Code footprint contributes >=1 usable skill or profile
        self.assertGreaterEqual(len(self.result["skills"]), 1)
        v = validator_for("skill.schema.json")
        for skill in self.result["skills"]:
            v.validate(skill)
        self.assertTrue((self.out / "profile.md").exists())
        self.assertGreaterEqual(len(self.result["profile_sections"]), 1)

    def test_lineage_written_and_chained(self):
        self.assertGreater(hashchain.verify(self.d / "l3.jsonl"), 0)
        # quarantined content is lineaged as external-untrusted
        l3 = [json.loads(l) for l in (self.d / "l3.jsonl").read_text().splitlines()]
        q = [r for r in l3 if r["transformation"] == "imperative-quarantine"]
        self.assertEqual(len(q), 1)
        self.assertEqual(q[0]["source_type"], "external-untrusted")


class FK3bGate(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.d = Path(self.tmp.name)
        import copy
        import connectors
        self.connectors = connectors
        cfg = copy.deepcopy(connectors.load_config())
        self.cfg_path = self.d / "connectors.json"
        connectors.save_config(cfg, self.cfg_path)

    def tearDown(self):
        self.tmp.cleanup()

    def test_ineligible_source_compiles_nothing(self):
        # source off by default -> compile_from_source returns None
        result = cf.compile_from_source(
            "local-claude-footprint", FOOTPRINT / "artifacts", self.d / "out",
            self.d, config_path=self.cfg_path)
        self.assertIsNone(result)

    def test_eligible_source_compiles_with_provenance(self):
        self.connectors.toggle("local-claude-footprint", True,
                               config_path=self.cfg_path, ledger_dir=self.d)
        result = cf.compile_from_source(
            "local-claude-footprint", FOOTPRINT / "artifacts", self.d / "out",
            self.d, config_path=self.cfg_path)
        self.assertIsNotNone(result)
        self.assertGreaterEqual(len(result["nodes"]), 4)


if __name__ == "__main__":
    unittest.main()
