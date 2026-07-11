"""FK8 F-tests: planted pattern detected + proposed; texture excluded; proposals
enter as gated inbox files (committed via the gate processor); <=2/run rate
limit; A-D3-lite acceptance floor (>=9 before a rate)."""

import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import discovery  # noqa: E402
import gate_processor as gp  # noqa: E402


class Scout(unittest.TestCase):
    def test_detects_recurring_unlinked_entity(self):
        items = [
            {"path": "a.md", "content": "We shipped the Cache Layer today."},
            {"path": "b.md", "content": "The Cache Layer needs monitoring."},
            {"path": "c.md", "content": "Unrelated note."},
        ]
        obs = discovery.corpus_scout(items)
        ids = [o["pattern_id"] for o in obs]
        self.assertIn("entity:Cache Layer", ids)


class Mine(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.d = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def _obs(self, pid, toil):
        return {"pattern_id": pid, "kind": "corpus_entry", "toil": toil,
                "title": pid, "evidence": ["x", "y"]}

    def test_texture_guard_excludes_non_toil(self):
        obs = [self._obs("toil-task", True), self._obs("brainstorm-texture", False)]
        emitted = discovery.mine(obs, self.d / "inbox")
        self.assertIn("toil-task", emitted)
        self.assertNotIn("brainstorm-texture", emitted)

    def test_rate_limited_to_two_per_run(self):
        obs = [self._obs(f"t{i}", True) for i in range(5)]
        emitted = discovery.mine(obs, self.d / "inbox")
        self.assertEqual(len(emitted), 2)

    def test_seen_patterns_not_reproposed(self):
        obs = [self._obs("t1", True)]
        discovery.mine(obs, self.d / "inbox", seen={"t1"})
        proposals = list((self.d / "inbox" / "proposals").glob("*.json")) \
            if (self.d / "inbox" / "proposals").exists() else []
        self.assertEqual(proposals, [])

    def test_proposals_enter_as_gated_files(self):
        # scout proposals go through the SAME inbox -> gate processor path
        repo = self.d / "repo"
        (repo / "stores" / "corpus").mkdir(parents=True)
        discovery.mine([self._obs("toil-x", True)], self.d / "inbox")
        result = gp.process_inbox(self.d / "inbox", repo, self.d)
        self.assertEqual(len(result["committed"]), 1)
        self.assertEqual(result["rejected"], [])


class Acceptance(unittest.TestCase):
    def test_below_floor_inconclusive(self):
        self.assertEqual(discovery.acceptance_rate(5, 3)["result"], "inconclusive")

    def test_at_floor_measured(self):
        r = discovery.acceptance_rate(9, 3)
        self.assertEqual(r["result"], "measured")
        self.assertTrue(r["meets_floor"])           # 3/9 = 1-in-3

    def test_below_one_in_three_fails_floor(self):
        r = discovery.acceptance_rate(12, 2)
        self.assertFalse(r["meets_floor"])


if __name__ == "__main__":
    unittest.main()
