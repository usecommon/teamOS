"""E2 remediation: a whole-file ledger deletion is silent at the append layer
(fresh chain, verify passes). The off-box anchor witness must catch it."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import hashchain  # noqa: E402
import anchor  # noqa: E402
import verify_chains  # noqa: E402


class Truncation(unittest.TestCase):
    def setUp(self):
        self.d = Path(tempfile.mkdtemp())
        self.led = self.d / "led"; self.led.mkdir()
        self.anc = self.d / "anchors"

    def test_deleted_ledger_flagged_by_anchor(self):
        L = self.led / "l7.jsonl"
        for i in range(5):
            hashchain.append(L, {"i": i}, "w")
        anchor.anchor_heads(self.led, self.anc, "run-1")     # off-box head recorded
        L.unlink()                                           # whole-file deletion
        hashchain.append(L, {"i": 99}, "w")                  # fresh chain, verify() ok
        self.assertEqual(hashchain.verify(L), 1)             # local verify is blind
        flagged = anchor.detect_truncation(self.led, self.anc)
        self.assertIn("l7.jsonl", flagged)                   # anchor is not blind
        self.assertEqual(verify_chains.main(self.led, self.anc), 1)  # chains step fails

    def test_intact_chain_not_flagged(self):
        L = self.led / "l7.jsonl"
        for i in range(3):
            hashchain.append(L, {"i": i}, "w")
        anchor.anchor_heads(self.led, self.anc, "run-1")
        hashchain.append(L, {"i": 3}, "w")                   # legitimate growth
        self.assertEqual(anchor.detect_truncation(self.led, self.anc), [])
        self.assertEqual(verify_chains.main(self.led, self.anc), 0)

    def test_no_anchor_is_not_a_failure(self):
        L = self.led / "l7.jsonl"
        hashchain.append(L, {"i": 0}, "w")
        self.assertEqual(verify_chains.main(self.led, self.anc), 0)


if __name__ == "__main__":
    unittest.main()
