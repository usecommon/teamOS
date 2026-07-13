"""WO-5 F-test: the two connection planes and their priority (architecture §7.5).

Plane A (PRIMARY) — Team OS acts as its OWN MCP client, ambiently, on the
principal's behalf; every such action is gated locally and lands on the record
(full-trust). Plane B (SECONDARY) — the door: other clients reach IN; it only
PROPOSES to the inbox and is never a writer (the gate processor at the runtime of
record is the sole writer). This test pins that distinction so the positioning
(which leads Plane A) matches the build."""

import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "hooks"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import door  # noqa: E402
import gate  # noqa: E402


class Planes(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.d = Path(self.tmp.name)
        (self.d / "stores" / "corpus").mkdir(parents=True)
        self._orig = gate.LEDGER_DIR
        gate.LEDGER_DIR = self.d

    def tearDown(self):
        gate.LEDGER_DIR = self._orig
        self.tmp.cleanup()

    def test_plane_a_action_is_gated_and_ledgered(self):
        # PRIMARY: a Team OS outbound action traverses the local gate and is
        # recorded — full-trust — regardless of the verdict.
        gate.process({"tool_name": "slack_post_message",
                      "tool_input": {"channel": "D_ME", "text": "brief"},
                      "session_id": "a"}, gate.load_policy())
        recs = (self.d / "l2.jsonl").read_text().splitlines()
        self.assertEqual(len(recs), 1)

    def test_plane_b_door_only_proposes_and_writes_no_ledger(self):
        # SECONDARY: the door writes a proposal to the inbox, never the corpus,
        # and is not itself a gate/writer (no L2 commit from the door).
        door.propose_corpus_entry(self.d / "inbox", "A Decision", ["we chose X"])
        proposals = list((self.d / "inbox" / "proposals").glob("*.json"))
        self.assertEqual(len(proposals), 1)
        self.assertEqual(list((self.d / "stores" / "corpus").glob("*.md")), [])
        self.assertFalse((self.d / "l2.jsonl").exists())


if __name__ == "__main__":
    unittest.main()
