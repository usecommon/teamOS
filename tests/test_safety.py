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
        spawn.record(self.d, "loops", "worker-1", "draft")
        spawn.record(self.d, "worker-1", "worker-2", "subtask")
        self.assertEqual(spawn.stats(self.d), {"count": 2, "max_depth": 2})
        self.assertEqual(hashchain.verify(self.d / "spawns.jsonl"), 2)

    def test_spawn_depth_enforced_not_self_reported(self):
        # T9: depth computed from the parent chain; the 4th level refuses —
        # and a liar passing depth=1 doesn't matter, the param is ignored
        spawn.record(self.d, "loops", "a", "t")
        spawn.record(self.d, "a", "b", "t")
        spawn.record(self.d, "b", "c", "t", depth=1)   # actual depth 3, ok
        with self.assertRaises(spawn.SpawnRefused):
            spawn.record(self.d, "c", "d", "t", depth=1)  # actual 4 -> refused

    def test_spawn_rate_enforced_at_record(self):
        for i in range(spawn.MAX_RATE):
            spawn.record(self.d, "loops", f"w{i}", "t")
        with self.assertRaises(spawn.SpawnRefused):
            spawn.record(self.d, "loops", "one-too-many", "t")

    def _old_denial_line(self, path, ts):
        # raw line with a controlled old timestamp (window test; _count-style
        # readers don't verify the chain)
        rec = {"verdict": "deny", "rule_id": "bash-exfil", "ts": ts,
               "proposed_action": {"tool": "Bash", "action_class": "execute",
                                   "target": "x", "payload_digest": "sha256:x"},
               "inspection": {"checks_run": [], "findings": []},
               "outcome": "gate_blocked", "hash": "sha256:x", "prev_hash": None,
               "record_id": "x", "schema_version": "0.1", "agent_id": "t"}
        with path.open("a") as f:
            f.write(json.dumps(rec) + "\n")

    def test_windowed_counters_recover_after_reset(self):
        # T9: 5 old denials outside the window; after a human reset the safety
        # agent must NOT re-trip on lifetime totals (the stuck-open deadlock)
        for _ in range(5):
            self._old_denial_line(self.d / "l2.jsonl", "2026-01-01T00:00:00Z")
        result = safety_agent.check(self.d, self.d / "safety.jsonl", self.state)
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["metrics"]["gate_denials"], 0)

    def test_unattributed_rejections_never_halt(self):
        # CN-1: a stranger's ✗ spike cannot trip a permanent halt
        for i in range(6):
            hashchain.append(self.d / "l8.jsonl", {
                "signal_type": "rejection", "attribution": "unattributed",
                "principal_id": f"stranger-{i}",
                "artifact_ref": {"store": "b", "path": "p",
                                 "content_hash": "sha256:x"},
                "outcome": "rejected",
                "harvest": {"method": "m", "harvested_at": "2026-07-11T00:00:00Z"},
            }, "test")
        result = safety_agent.check(self.d, self.d / "safety.jsonl", self.state)
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["metrics"]["rejections"], 0)


if __name__ == "__main__":
    unittest.main()
