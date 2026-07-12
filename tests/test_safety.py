"""Circuit breaker + safety agent + spawn audit (autonomy is bounded and
auditable). Breaker open => gate denies side-effects (reads still pass); safety
agent trips on threshold breach; spawns are recorded and chain-verify; only a
human resets."""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(REPO / "hooks"))

import circuit_breaker as cb  # noqa: E402
import gate  # noqa: E402
import hashchain  # noqa: E402
import safety_agent  # noqa: E402
import spawn  # noqa: E402


class Breaker(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.d = Path(self.tmp.name)
        self.state = self.d / "breaker.json"
        gate.LEDGER_DIR = self.d
        self.policy = gate.load_policy()
        os.environ["TEAMOS_BREAKER"] = str(self.state)

    def tearDown(self):
        os.environ.pop("TEAMOS_BREAKER", None)
        self.tmp.cleanup()

    def _write(self):
        return gate.process({"tool_name": "Write",
                             "tool_input": {"file_path": "notes.md", "content": "x"}}, self.policy)

    def test_open_breaker_denies_side_effects(self):
        cb.trip(self.d, self.state, "principal:jeff", "manual halt")
        d = self._write()
        self.assertEqual(d["hookSpecificOutput"]["permissionDecision"], "deny")
        rec = json.loads((self.d / "l2.jsonl").read_text().splitlines()[-1])
        self.assertEqual(rec["rule_id"], "circuit-open")

    def test_reads_still_pass_while_open(self):
        cb.trip(self.d, self.state, "principal:jeff", "manual halt")
        d = gate.process({"tool_name": "Read", "tool_input": {"file_path": "notes.md"}}, self.policy)
        self.assertEqual(d["hookSpecificOutput"]["permissionDecision"], "allow")

    def test_reset_restores_side_effects(self):
        cb.trip(self.d, self.state, "principal:jeff", "manual halt")
        cb.reset(self.d, self.state, "principal:jeff")
        d = self._write()
        self.assertEqual(d["hookSpecificOutput"]["permissionDecision"], "allow")

    def test_trip_and_reset_are_ledgered(self):
        cb.trip(self.d, self.state, "safety-agent", "breach")
        cb.reset(self.d, self.state, "principal:jeff")
        rules = [json.loads(l)["rule_id"] for l in (self.d/"l2.jsonl").read_text().splitlines()]
        self.assertIn("circuit-breaker-trip", rules)
        self.assertIn("circuit-breaker-reset", rules)


class Safety(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.d = Path(self.tmp.name)
        self.state = self.d / "breaker.json"

    def tearDown(self):
        self.tmp.cleanup()

    def test_safety_agent_trips_on_denial_spike(self):
        # seed the gate ledger with 5 denials (not circuit rules)
        for _ in range(5):
            hashchain.append(self.d / "l2.jsonl", {
                "proposed_action": {"tool": "Bash", "action_class": "execute",
                                    "target": "x", "payload_digest": "sha256:x"},
                "verdict": "deny", "policy_version": "p", "rule_id": "bash-exfil",
                "inspection": {"checks_run": [], "findings": []}, "outcome": "gate_blocked"},
                "test")
        result = safety_agent.check(self.d, self.d / "safety.jsonl", self.state)
        self.assertEqual(result["status"], "tripped")
        self.assertIn("gate_denials", result["breaches"])
        self.assertTrue(cb.is_open(self.state))          # breaker actually opened

    def test_safety_agent_clear_when_under_thresholds(self):
        result = safety_agent.check(self.d, self.d / "safety.jsonl", self.state)
        self.assertEqual(result["status"], "ok")
        self.assertFalse(cb.is_open(self.state))

    def test_spawns_recorded_and_chain_verifies(self):
        spawn.record(self.d, "loops", "worker-1", "draft", 1)
        spawn.record(self.d, "worker-1", "worker-2", "subtask", 2)
        self.assertEqual(spawn.stats(self.d), {"count": 2, "max_depth": 2})
        self.assertEqual(hashchain.verify(self.d / "spawns.jsonl"), 2)


if __name__ == "__main__":
    unittest.main()
