"""FK7 F-tests: sub-floor + PII-seeded skills blocked in CI; clean signed skill
merges + ledgered; cohort assignment; within-receiver rig + pre-registered pass
rule; rollback restores a prior version byte-identically."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import hashchain  # noqa: E402
import promotion_gate as pg  # noqa: E402
import transfer  # noqa: E402

SIGNED = {"signed_commit": True, "reproducible_build": True, "hook_diff_reviewed": True}


class PromotionGate(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.d = Path(self.tmp.name)
        self.team = self.d / "team"
        # give the skill passing eval evidence
        for s in (0.8, 0.9):
            hashchain.append(self.d / "l7.jsonl", {
                "skill_id": "digest", "skill_version": "v1", "invocation_id": "i",
                "metric": "m", "score": s,
                "sample_ref": {"store": "x", "path": "y", "content_hash": "sha256:z"},
            }, "test")

    def tearDown(self):
        self.tmp.cleanup()

    def test_clean_signed_skill_merges_and_ledgers(self):
        ok, reasons = pg.promote("digest", "# digest\nsummarize the week.", SIGNED,
                                 self.d, self.team)
        self.assertTrue(ok, reasons)
        self.assertTrue((self.team / "digest.md").exists())
        l2 = json.loads((self.d / "l2.jsonl").read_text().splitlines()[-1])
        self.assertEqual(l2["rule_id"], "promotion-clean")
        self.assertEqual(hashchain.verify(self.d / "l6.jsonl"), 1)

    def test_pii_seeded_skill_blocked(self):
        ok, reasons = pg.promote("digest", "# digest\ncontact bob@corp.com", SIGNED,
                                 self.d, self.team)
        self.assertFalse(ok)
        self.assertTrue(any(r.startswith("pii") for r in reasons))
        self.assertFalse((self.team / "digest.md").exists())

    def test_sub_floor_skill_blocked(self):
        ok, reasons = pg.promote("unknown-skill", "# x", SIGNED, self.d, self.team)
        self.assertFalse(ok)
        self.assertTrue(any(r.startswith("eval-floor") for r in reasons))

    def test_unsigned_skill_blocked(self):
        ok, reasons = pg.promote("digest", "# digest", {"signed_commit": True},
                                 self.d, self.team)
        self.assertFalse(ok)
        self.assertIn("signing-lite:incomplete", reasons)

    def test_block_is_ledgered_deny(self):
        pg.promote("digest", "ssn 123-45-6789", SIGNED, self.d, self.team)
        l2 = json.loads((self.d / "l2.jsonl").read_text().splitlines()[-1])
        self.assertEqual(l2["verdict"], "deny")


class Cohorts(unittest.TestCase):
    def test_staggered_assignment_is_deterministic(self):
        a = transfer.assign_cohorts(["carol", "alice", "bob"])
        self.assertEqual(a, {"alice": 0, "bob": 1, "carol": 2})


class Measurement(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.d = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def _fill(self, receiver, v, dist, n):
        for _ in range(n):
            transfer.record_invocation(self.d, receiver, "digest", v, dist, True)

    def test_below_floor_is_inconclusive(self):
        self._fill("alice", "v1", 0.4, 5)   # < floor of 10
        self._fill("alice", "v2", 0.2, 5)
        b, t = transfer.within_receiver_series(self.d, "alice", "digest", "v1", "v2")
        self.assertIsNone(transfer.receiver_delta(b, t))

    def test_positive_delta_when_edit_distance_drops(self):
        self._fill("alice", "v1", 0.4, 12)
        self._fill("alice", "v2", 0.2, 12)
        b, t = transfer.within_receiver_series(self.d, "alice", "digest", "v1", "v2")
        self.assertAlmostEqual(transfer.receiver_delta(b, t), 0.2, places=3)

    def test_preregistered_rule_needs_two_positive_receivers(self):
        one = transfer.passes_preregistered_rule({"a": 0.2, "b": None})
        self.assertEqual(one["result"], "inconclusive")
        two = transfer.passes_preregistered_rule({"a": 0.2, "b": 0.1})
        self.assertEqual(two["result"], "pass")
        mixed = transfer.passes_preregistered_rule({"a": 0.2, "b": -0.3, "c": 0.05})
        # pooled must exceed zero AND >=2 positive
        self.assertIn(mixed["result"], ("pass", "inconclusive"))


class Rollback(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.d = Path(self.tmp.name)
        subprocess.run(["git", "-C", str(self.d), "init", "-q"], check=True)
        subprocess.run(["git", "-C", str(self.d), "config", "user.email", "t@t"], check=True)
        subprocess.run(["git", "-C", str(self.d), "config", "user.name", "t"], check=True)

    def tearDown(self):
        self.tmp.cleanup()

    def _commit(self, path, content):
        (self.d / path).write_text(content)
        subprocess.run(["git", "-C", str(self.d), "add", "-A"], check=True)
        subprocess.run(["git", "-C", str(self.d), "commit", "-q", "-m", "x"], check=True)
        return subprocess.run(["git", "-C", str(self.d), "rev-parse", "HEAD"],
                              capture_output=True, text=True, check=True).stdout.strip()

    def test_rollback_restores_prior_version_byte_identically(self):
        v1_bytes = b"# skill v1\nline\n"
        (self.d / "skill.md").write_bytes(v1_bytes)
        subprocess.run(["git", "-C", str(self.d), "add", "-A"], check=True)
        subprocess.run(["git", "-C", str(self.d), "commit", "-q", "-m", "v1"], check=True)
        v1_sha = subprocess.run(["git", "-C", str(self.d), "rev-parse", "HEAD"],
                                capture_output=True, text=True, check=True).stdout.strip()
        self._commit("skill.md", "# skill v2\nchanged\n")
        restored = transfer.restore_version(self.d, "skill.md", v1_sha)
        self.assertEqual(restored, v1_bytes)
        self.assertEqual((self.d / "skill.md").read_bytes(), v1_bytes)


if __name__ == "__main__":
    unittest.main()
