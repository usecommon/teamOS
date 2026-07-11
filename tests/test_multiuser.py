"""FK7-pre F-tests: cross-principal read fails + self-ledgers; keys never in the
shared repo; owner can view their own everything; dashboard renders per-skill
only and the code audit finds no per-person comparative join."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import crypto_store as cs  # noqa: E402
import dashboard  # noqa: E402
import hashchain  # noqa: E402


class PerPrincipalEncryption(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.d = Path(self.tmp.name)
        self.store = self.d / "shared-store"        # shareable / cloneable
        self.keydir = self.d / "keys"               # OUTSIDE the repo
        self.repo = self.d / "repo"
        self.repo.mkdir()
        self.alice_key = cs.load_or_create_key(self.keydir, "alice", self.repo)
        self.bob_key = cs.load_or_create_key(self.keydir, "bob", self.repo)
        cs.write_personal_store("alice", "alice private calibration", self.store,
                                self.alice_key)

    def tearDown(self):
        self.tmp.cleanup()

    def test_owner_reads_own_store(self):
        text = cs.read_personal_store("alice", "alice", self.store, self.alice_key, self.d)
        self.assertEqual(text, "alice private calibration")

    def test_cross_principal_read_denied_and_self_ledgered(self):
        with self.assertRaises(cs.CrossPrincipalDenied):
            cs.read_personal_store("bob", "alice", self.store, self.bob_key, self.d)
        # the denied read lands in ALICE's feed (self-ledgering)
        feed = self.d / "feeds" / "alice.jsonl"
        rec = json.loads(feed.read_text().splitlines()[-1])
        self.assertEqual(rec["reader"], "bob")
        self.assertEqual(rec["owner"], "alice")
        self.assertFalse(rec["granted"])
        self.assertEqual(hashchain.verify(feed), 1)

    def test_successful_read_also_self_ledgers(self):
        cs.read_personal_store("alice", "alice", self.store, self.alice_key, self.d)
        rec = json.loads((self.d / "feeds" / "alice.jsonl").read_text().splitlines()[-1])
        self.assertTrue(rec["granted"])

    def test_store_holds_only_ciphertext(self):
        raw = (self.store / "personal" / "alice" / "store.enc").read_bytes()
        self.assertNotIn(b"alice private calibration", raw)

    def test_keys_never_in_repo(self):
        with self.assertRaises(cs.KeyInRepoError):
            cs.load_or_create_key(self.repo / "keys", "mallory", self.repo)


class NoIndividuation(unittest.TestCase):
    def test_dashboard_renders_per_skill_only(self):
        l7 = [
            {"skill_id": "compile", "skill_version": "v1", "score": 0.8},
            {"skill_id": "compile", "skill_version": "v1", "score": 1.0},
            {"skill_id": "digest", "skill_version": "v2", "score": 0.6},
        ]
        out = dashboard.render_skill_dashboard(l7)
        self.assertEqual(set(out["per_skill"]), {"compile", "digest"})
        self.assertEqual(out["per_skill"]["compile"]["n"], 2)
        # no principal / person keys anywhere in the output
        self.assertNotIn("principal", json.dumps(out).lower())

    def test_code_audit_finds_no_person_comparative_join(self):
        clean, findings = dashboard.audit_no_individuation()
        self.assertTrue(clean, findings)

    def test_audit_catches_a_planted_individuation_construct(self):
        # sanity: the audit actually fires on a per-person construct
        tmp = tempfile.NamedTemporaryFile("w", suffix=".py", delete=False)
        tmp.write("def rank():\n    return group_by_principal_id(scores)\n")
        tmp.close()
        clean, findings = dashboard.audit_no_individuation(tmp.name)
        self.assertFalse(clean)
        Path(tmp.name).unlink()


if __name__ == "__main__":
    unittest.main()
