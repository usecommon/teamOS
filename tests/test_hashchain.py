"""E1 remediation: a torn trailing fragment (crash mid-append) must not brick
the writer, and must not mask interior tampering."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import hashchain  # noqa: E402


class TornTail(unittest.TestCase):
    def setUp(self):
        self.d = Path(tempfile.mkdtemp())
        self.L = self.d / "l.jsonl"

    def test_torn_trailing_fragment_does_not_brick_append(self):
        hashchain.append(self.L, {"a": 1}, "w")
        r2 = hashchain.append(self.L, {"a": 2}, "w")
        # simulate a crash mid-append: a partial line with no terminating newline
        with self.L.open("a") as f:
            f.write('{"partial": tru')
        # a subsequent append must succeed (heals the torn tail) ...
        r3 = hashchain.append(self.L, {"a": 3}, "w")
        self.assertEqual(r3["prev_hash"], r2["hash"])
        # ... and the chain verifies over the 3 intact records
        self.assertEqual(hashchain.verify(self.L), 3)

    def test_torn_tail_with_no_newline_at_all(self):
        with self.L.open("w") as f:
            f.write('{"totally torn fragment')   # bare torn fragment, no newline
        rec = hashchain.append(self.L, {"a": 1}, "w")
        self.assertIsNone(rec["prev_hash"])       # torn fragment dropped, fresh start
        self.assertEqual(hashchain.verify(self.L), 1)

    def test_interior_tampering_still_detected(self):
        for i in range(4):
            hashchain.append(self.L, {"i": i}, "w")
        lines = self.L.read_text().splitlines()
        row = json.loads(lines[1]); row["i"] = 999          # tamper an interior record
        lines[1] = json.dumps(row)
        self.L.write_text("\n".join(lines) + "\n")
        with self.assertRaises(ValueError):
            hashchain.verify(self.L)


if __name__ == "__main__":
    unittest.main()
