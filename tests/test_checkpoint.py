"""E4 remediation: a corrupt checkpoint must not brick resume — restart clean,
preserve the corrupt bytes for audit."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import checkpoint  # noqa: E402


class CorruptCheckpoint(unittest.TestCase):
    def setUp(self):
        self.d = Path(tempfile.mkdtemp())
        self.p = self.d / "cp.json"

    def test_torn_checkpoint_restarts_clean_and_preserves_bytes(self):
        self.p.write_text('{"done": ["a"], "resu')          # torn write
        cp = checkpoint.Checkpoint(self.p)
        self.assertEqual(cp.state, {"done": [], "results": {}})   # clean restart
        self.assertTrue(self.p.with_suffix(".json.corrupt").exists())  # preserved

    def test_wrong_shape_treated_as_corrupt(self):
        self.p.write_text('[1, 2, 3]')                       # valid JSON, wrong shape
        cp = checkpoint.Checkpoint(self.p)
        self.assertEqual(cp.state, {"done": [], "results": {}})
        self.assertTrue(self.p.with_suffix(".json.corrupt").exists())

    def test_valid_checkpoint_still_resumes(self):
        checkpoint.run_checkpointed([("s1", lambda r: 1)], self.p)
        cp = checkpoint.Checkpoint(self.p)
        self.assertTrue(cp.is_done("s1"))
        self.assertEqual(cp.state["results"]["s1"], 1)


if __name__ == "__main__":
    unittest.main()
