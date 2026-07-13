"""WO-3/WO-4 F-tests: reversibility classification, the user-owned allow policy,
and THE falsifiable guarantee — no irreversible action is auto-permitted without
an allow-match, and every one is recorded before it acts."""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "hooks"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import boundary  # noqa: E402
import gate  # noqa: E402


class Reversibility(unittest.TestCase):
    def test_external_actions_are_irreversible(self):
        for t, c in [("SlackPost", "send"), ("mcp__gmail__send_email", "send"),
                     ("PublishRelease", "send"), ("upload_file", "send"),
                     ("DeployProd", "execute"), ("delete_record", "execute"),
                     ("make_payment", "execute")]:
            self.assertEqual(boundary.reversibility(t, c), "irreversible", t)

    def test_reads_and_interior_writes_are_reversible(self):
        for t, c in [("WebSearch", "send"), ("WebFetch", "send"),
                     ("Write", "write"), ("Edit", "edit"), ("Bash", "execute"),
                     ("Read", "read")]:
            self.assertEqual(boundary.reversibility(t, c), "reversible", t)


class AllowPolicy(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.pol = Path(self.tmp.name) / "allow-policy.md"

    def tearDown(self):
        self.tmp.cleanup()

    def test_empty_policy_matches_nothing(self):
        self.pol.write_text("# only comments\n#   post #x\n")
        self.assertFalse(boundary.allow_match("SlackPost", "#team", str(self.pol)))

    def test_tool_rule_matches(self):
        self.pol.write_text("post\n")
        self.assertTrue(boundary.allow_match("SlackPost", "#team", str(self.pol)))

    def test_channel_target_constraint_survives_hash(self):
        # a '#channel' target must NOT be eaten as a comment
        self.pol.write_text("post #team-standup\n")
        self.assertTrue(
            boundary.allow_match("SlackPost", "#team-standup", str(self.pol)))
        self.assertFalse(
            boundary.allow_match("SlackPost", "#random", str(self.pol)))


class FalsifiableGuarantee(unittest.TestCase):
    """No irreversible action auto-permits without an allow-match; each is
    recorded (pre-act) with its reversibility label."""

    IRREVERSIBLE = [
        ("SlackPost", {"channel": "#team", "text": "hi"}),
        ("mcp__gmail__send_email", {"url": "x@y.com"}),
        ("PublishRelease", {"command": "v1"}),
        ("DeployProd", {"command": "prod"}),
        ("delete_record", {"path": "42"}),
        ("make_payment", {"command": "100"}),
    ]

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.d = Path(self.tmp.name)
        self._orig = gate.LEDGER_DIR
        gate.LEDGER_DIR = self.d
        self.policy = gate.load_policy()
        self.pol = self.d / "allow-policy.md"
        self.pol.write_text("# empty\n")
        os.environ["TEAMOS_ALLOW_POLICY"] = str(self.pol)

    def tearDown(self):
        gate.LEDGER_DIR = self._orig
        os.environ.pop("TEAMOS_ALLOW_POLICY", None)
        self.tmp.cleanup()

    def _run(self, tool, tool_input):
        gate.process({"tool_name": tool, "tool_input": tool_input,
                      "session_id": "b"}, self.policy)
        return json.loads((self.d / "l2.jsonl").read_text().splitlines()[-1])

    def test_no_irreversible_permits_under_empty_policy(self):
        for tool, ti in self.IRREVERSIBLE:
            rec = self._run(tool, ti)
            self.assertNotEqual(rec["verdict"], "permit", tool)       # never auto-permit
            self.assertIn("reversibility:irreversible",
                          rec["inspection"]["checks_run"], tool)      # recorded, pre-act

    def test_allow_match_permits(self):
        self.pol.write_text("post #team\n")
        rec = self._run("SlackPost", {"channel": "#team", "text": "hi"})
        self.assertEqual(rec["verdict"], "permit")
        self.assertIn("allow-policy-match", rec["inspection"]["checks_run"])

    def test_allow_match_respects_target_constraint(self):
        self.pol.write_text("post #team\n")
        rec = self._run("SlackPost", {"channel": "#random", "text": "hi"})
        self.assertEqual(rec["verdict"], "ask")
        self.assertEqual(rec["rule_id"], "irreversible-hold")

    def test_reversible_action_still_permits(self):
        rec = self._run("WebSearch", {"query": "docs"})
        self.assertEqual(rec["verdict"], "permit")

    def test_allow_match_never_overrides_a_safety_deny(self):
        # a matching allow rule must NOT turn an outbound-secret deny into a permit
        self.pol.write_text("send\n")
        rec = self._run("send_report", {"text": "key AKIA1234567890ABCDEF here"})
        self.assertEqual(rec["verdict"], "deny")
        self.assertEqual(rec["rule_id"], "outbound-secret")


if __name__ == "__main__":
    unittest.main()
