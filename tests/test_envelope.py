"""FK6b F-tests: widen only on principal-attributed evidence; forged/third-party
✓ never widens (CN-1); single principal rejection narrows immediately (OB-1);
widening bounded by ceiling and can't touch its own ceiling; FK6 handicap raises
the widen threshold (OB-3); manual reset; every change emits L2; the gate
protects the ceiling file."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "hooks"))

import envelope  # noqa: E402
import hashchain  # noqa: E402
import gate  # noqa: E402


def sig(attribution="principal_authenticated", signal="endorsement", dist=0.0):
    return {"signal_type": signal, "attribution": attribution,
            "edit_distance_normalized": dist}


class Envelope(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.d = Path(self.tmp.name)
        self.state = self.d / "envelope-state.json"
        # non-fk6 posture -> threshold = widen_threshold (3) for simpler math
        self.posture = "steady"

    def tearDown(self):
        self.tmp.cleanup()

    def _feed(self, s, category="send", n=1):
        level = None
        for _ in range(n):
            level = envelope.process_signal(s, category, self.d, self.state,
                                            posture=self.posture)
        return level

    def test_widen_on_principal_acceptances_at_threshold(self):
        self.assertEqual(self._feed(sig(), "send", n=2), 0)  # below threshold
        self.assertEqual(self._feed(sig(), "send", n=1), 1)  # 3rd -> widen to 1
        l2 = [json.loads(l) for l in (self.d / "l2.jsonl").read_text().splitlines()]
        widen = [r for r in l2 if r["rule_id"] == "widen"]
        self.assertEqual(len(widen), 1)
        self.assertEqual(widen[0]["proposed_action"]["target"], "send:0->1")

    def test_forged_third_party_check_never_widens(self):
        # CN-1: unattributed ✓ x many -> level stays 0, no widen record
        level = self._feed(sig(attribution="unattributed"), "send", n=10)
        self.assertEqual(level, 0)
        self.assertFalse((self.d / "l2.jsonl").exists()
                         and any(json.loads(l)["rule_id"] == "widen"
                                 for l in (self.d / "l2.jsonl").read_text().splitlines()))

    def test_single_principal_rejection_narrows_immediately(self):
        self._feed(sig(), "send", n=3)                       # widen to 1
        new = self._feed(sig(signal="rejection"), "send", n=1)
        self.assertEqual(new, 0)                             # narrowed a notch at once
        l2 = [json.loads(l) for l in (self.d / "l2.jsonl").read_text().splitlines()]
        self.assertTrue(any(r["rule_id"] == "narrow" for r in l2))

    def test_heavy_edit_does_not_narrow_no_engagement_penalty(self):
        # T6: a heavy edit is engagement, not distrust — level holds; only an
        # explicit rejection narrows
        self._feed(sig(), "read", n=3)                       # read ceiling 2, level 1
        held = self._feed(sig(dist=0.7), "read", n=1)        # heavy edit -> no narrow
        self.assertEqual(held, 1)
        narrowed = self._feed(sig(signal="rejection"), "read", n=1)
        self.assertEqual(narrowed, 0)

    def test_endorsement_without_measured_distance_never_widens(self):
        # T6 fail-safe: missing edit_distance is not evidence of acceptance
        level = self._feed(sig(dist=None), "send", n=10)
        self.assertEqual(level, 0)

    def test_widen_bounded_by_ceiling(self):
        # send ceiling = 1; keep feeding acceptances -> never exceeds 1
        self._feed(sig(), "send", n=3)                       # -> 1
        level = self._feed(sig(), "send", n=6)               # would-be widen blocked
        self.assertEqual(level, 1)

    def test_fk6_handicap_raises_threshold(self):
        # fk6 posture -> threshold = 3 * 2 = 6; 5 acceptances do NOT widen
        level = None
        for _ in range(5):
            level = envelope.process_signal(sig(), "send", self.d, self.state,
                                            posture="fk6")
        self.assertEqual(level, 0)
        level = envelope.process_signal(sig(), "send", self.d, self.state, posture="fk6")
        self.assertEqual(level, 1)                           # 6th widens

    def test_manual_reset_restores_base_and_ledgers(self):
        self._feed(sig(), "send", n=3)                       # -> 1
        base = envelope.reset("send", self.d, self.state)
        self.assertEqual(base, 0)
        l2 = [json.loads(l) for l in (self.d / "l2.jsonl").read_text().splitlines()]
        self.assertTrue(any(r["rule_id"] == "reset" for r in l2))

    def test_every_change_is_ledgered_and_chain_verifies(self):
        self._feed(sig(), "send", n=3)
        self._feed(sig(signal="rejection"), "send", n=1)
        envelope.reset("send", self.d, self.state)
        self.assertGreater(hashchain.verify(self.d / "l2.jsonl"), 0)


class CeilingProtected(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.d = Path(self.tmp.name)
        gate.LEDGER_DIR = self.d
        self.policy = gate.load_policy()

    def test_gate_blocks_direct_edit_of_ceiling_file(self):
        # the script can never touch its own ceiling: a write to the policy file
        # is a protected path -> gate asks for human approval.
        decision = gate.process({
            "tool_name": "Write",
            "tool_input": {"file_path": str(REPO_ROOT / "config" / "envelope-policy.json"),
                           "content": "{}"},
        }, self.policy)
        self.assertEqual(decision["hookSpecificOutput"]["permissionDecision"], "ask")
        record = json.loads((self.d / "l2.jsonl").read_text().splitlines()[-1])
        self.assertEqual(record["rule_id"], "protected-path")


if __name__ == "__main__":
    unittest.main()
