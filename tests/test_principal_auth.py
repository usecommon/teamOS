"""WO-2 F-tests: the L8 signature binds the FULL evidentiary payload
(edit_distance, nonce, timestamp), and the envelope's consumer (verified_fresh)
refuses a replayed or stale signature. Closes the fork's one third-party attack
chain — a forged/replayed reaction widening autonomy (CN-1)."""

import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import hashchain  # noqa: E402
import principal_auth  # noqa: E402


def _record(principal="principal:jeff", dist=0.0, nonce="n-1", ts=None):
    return {
        "signal_type": "endorsement",
        "artifact_ref": {"store": "stores", "path": "p.md", "content_hash": "sha256:x"},
        "principal_id": principal,
        "attribution": "principal_authenticated",
        "outcome": "accepted",
        "edit_distance_normalized": dist,
        "nonce": nonce,
        "harvest": {"method": "edit-diff-capture",
                    "harvested_at": ts or hashchain.utc_now()},
    }


class SignatureBindsPayload(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.keydir = Path(self.tmp.name) / "keys"
        principal_auth.ensure_key("principal:jeff", self.keydir)

    def tearDown(self):
        self.tmp.cleanup()

    def _sign(self, rec):
        rec = dict(rec)
        rec["auth_sig"] = principal_auth.sign(rec, self.keydir)
        return rec

    def test_valid_record_verifies(self):
        self.assertTrue(principal_auth.verified(self._sign(_record()), self.keydir))

    def test_tampered_edit_distance_fails(self):
        # THE forged-widen: hold a valid heavy-edit sig, flip distance to 0 so it
        # reads as an acceptance. Now that edit_distance is signed, this fails.
        rec = self._sign(_record(dist=0.9))
        rec["edit_distance_normalized"] = 0.0
        self.assertFalse(principal_auth.verified(rec, self.keydir))

    def test_tampered_nonce_fails(self):
        rec = self._sign(_record(nonce="n-1"))
        rec["nonce"] = "n-2"
        self.assertFalse(principal_auth.verified(rec, self.keydir))

    def test_tampered_timestamp_fails(self):
        rec = self._sign(_record())
        rec["harvest"]["harvested_at"] = "2020-01-01T00:00:00Z"
        self.assertFalse(principal_auth.verified(rec, self.keydir))


class ReplayAndFreshness(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.d = Path(self.tmp.name)
        self.keydir = self.d / "keys"
        self.seen = self.d / "seen"
        principal_auth.ensure_key("principal:jeff", self.keydir)

    def tearDown(self):
        self.tmp.cleanup()

    def _sign(self, rec):
        rec = dict(rec)
        rec["auth_sig"] = principal_auth.sign(rec, self.keydir)
        return rec

    def test_fresh_signed_record_accepted_once(self):
        rec = self._sign(_record(nonce="once"))
        self.assertTrue(principal_auth.verified_fresh(rec, self.seen, self.keydir))

    def test_replayed_nonce_refused(self):
        rec = self._sign(_record(nonce="spend"))
        self.assertTrue(principal_auth.verified_fresh(rec, self.seen, self.keydir))
        self.assertFalse(principal_auth.verified_fresh(rec, self.seen, self.keydir))

    def test_stale_timestamp_refused(self):
        rec = self._sign(_record(nonce="old", ts="2020-01-01T00:00:00Z"))
        # signature is valid (it binds the old stamp) but it is outside the window
        self.assertTrue(principal_auth.verified(rec, self.keydir))
        self.assertFalse(principal_auth.verified_fresh(rec, self.seen, self.keydir))

    def test_formative_no_keydir_still_trusts_field(self):
        # builder-as-subject: no keydir -> attribution field trusted; the freshness
        # layer must not block the formative path
        rec = _record(nonce="f1")
        self.assertTrue(principal_auth.verified_fresh(rec, self.seen, keydir=None))

    def test_unattributed_never_verifies(self):
        rec = _record(nonce="u1")
        rec["attribution"] = "unattributed"
        self.assertFalse(principal_auth.verified_fresh(rec, self.seen, self.keydir))


if __name__ == "__main__":
    unittest.main()
