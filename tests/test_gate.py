"""A-FK2 / FR2 gate F-tests: payload inspection blocks the exfil probe set
(canonical + obfuscated), benign controls pass, every call is ledgered,
inspection runs regardless of posture, distinct outcome recording."""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "hooks"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import gate  # noqa: E402
import hashchain  # noqa: E402

PROBES = json.loads((REPO_ROOT / "fixtures" / "exfil-probes.json").read_text())


class GateBase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.ledger_dir = Path(self.tmp.name)
        self._orig = gate.LEDGER_DIR
        gate.LEDGER_DIR = self.ledger_dir
        self.policy = gate.load_policy()

    def tearDown(self):
        gate.LEDGER_DIR = self._orig
        self.tmp.cleanup()

    def run_probe(self, probe):
        return gate.process(
            {"tool_name": probe["tool_name"], "tool_input": probe["tool_input"],
             "session_id": "test"},
            self.policy,
        )


class ProbeSet(GateBase):
    def _check(self, probe):
        gate.process(
            {"tool_name": probe["tool_name"], "tool_input": probe["tool_input"]},
            self.policy,
        )
        record = json.loads((self.ledger_dir / "l2.jsonl").read_text().splitlines()[-1])
        self.assertEqual(record["verdict"], probe["expect_verdict"], probe["name"])
        self.assertEqual(record["rule_id"], probe["expect_rule"], probe["name"])
        # every probe is ledgered with a non-empty inspection
        self.assertIn("checks_run", record["inspection"])
        self.assertTrue(record["inspection"]["checks_run"], probe["name"])
        return record

    def test_canonical_probes_blocked_and_ledgered(self):
        for probe in PROBES["canonical"]:
            record = self._check(probe)
            self.assertNotEqual(record["verdict"], "permit", probe["name"])

    def test_obfuscated_probes_blocked_and_ledgered(self):
        for probe in PROBES["obfuscated"]:
            record = self._check(probe)
            self.assertNotEqual(record["verdict"], "permit", probe["name"])

    def test_benign_controls_permitted(self):
        for probe in PROBES["benign_controls"]:
            record = self._check(probe)
            self.assertEqual(record["verdict"], "permit", probe["name"])

    def test_l2_chain_verifies_after_probe_set(self):
        for probe in PROBES["canonical"] + PROBES["obfuscated"] + PROBES["benign_controls"]:
            self.run_probe(probe)
        self.assertGreater(hashchain.verify(self.ledger_dir / "l2.jsonl"), 0)


class InspectionAlwaysOn(GateBase):
    def test_inspection_runs_under_unattended_posture(self):
        # Posture changes the RECORD, never whether inspection runs (FR2).
        orig = gate.POSTURE
        try:
            gate.POSTURE = "unattended-guarded"
            probe = PROBES["canonical"][0]
            gate.process(
                {"tool_name": probe["tool_name"], "tool_input": probe["tool_input"]},
                self.policy,
            )
            record = json.loads((self.ledger_dir / "l2.jsonl").read_text().splitlines()[-1])
            self.assertEqual(record["posture"], "unattended-guarded")
            self.assertEqual(record["verdict"], "deny")
            self.assertIn("bash-egress-scan", record["inspection"]["checks_run"])
        finally:
            gate.POSTURE = orig

    def test_outcome_distinct_from_verdict(self):
        deny = self.run_probe(PROBES["canonical"][0])
        permit = self.run_probe(PROBES["benign_controls"][0])
        self.assertIn("deny", deny["hookSpecificOutput"]["permissionDecision"])
        self.assertIn("allow", permit["hookSpecificOutput"]["permissionDecision"])
        records = [
            json.loads(l) for l in (self.ledger_dir / "l2.jsonl").read_text().splitlines()
        ]
        outcomes = {r["rule_id"]: r["outcome"] for r in records}
        self.assertEqual(outcomes["bash-exfil"], "gate_blocked")
        self.assertEqual(outcomes["default-permit"], "gate_passed")

    def test_headless_mode_identical(self):
        # Headless = no tty; process() takes plain dict input, no interactive
        # dependency. Same input -> same verdict as attended.
        probe = PROBES["canonical"][1]
        a = self.run_probe(probe)
        b = self.run_probe(probe)
        self.assertEqual(
            a["hookSpecificOutput"]["permissionDecision"],
            b["hookSpecificOutput"]["permissionDecision"],
        )


if __name__ == "__main__":
    unittest.main()
