"""Live dashboard reads the REAL ledgers and renders health — aggregate only,
never per-person (individuation check: no principal_id leaks into the output)."""
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import hashchain  # noqa: E402
import observe  # noqa: E402

SECRET_PRINCIPAL = "U_SECRET_PERSON_ID"


def _populate(led):
    led.mkdir(parents=True, exist_ok=True)
    # L2: a permit + two denies
    for v, rule in [("permit", "read-allowed"), ("deny", "circuit-open"), ("deny", "send-scanned")]:
        hashchain.append(led / "l2.jsonl", {
            "proposed_action": {"tool": "X", "action_class": "send", "target": "t", "payload_digest": "d"},
            "verdict": v, "policy_version": "p", "rule_id": rule,
            "inspection": {"checks_run": [], "findings": []}, "outcome": "gate_passed"}, "test/0")
    # L7: two scores for one skill
    for s in (0.8, 1.0):
        hashchain.append(led / "l7.jsonl", {"skill_id": "digest", "skill_version": "v1",
            "invocation_id": "i", "metric": "quality", "score": s, "aggregate": "mean",
            "sample_ref": {"store": "x", "path": "y", "content_hash": "h"}}, "test/0")
    # L8: an authenticated endorsement carrying a principal_id (must NOT surface)
    hashchain.append(led / "l8.jsonl", {
        "signal_type": "endorsement", "attribution": "principal_authenticated",
        "principal_id": SECRET_PRINCIPAL, "outcome": "accepted",
        "edit_distance_normalized": 0.0, "unprompted": True,
        "artifact_ref": {"store": "b", "path": "p", "content_hash": "h"}}, "test/0")


class Observe(unittest.TestCase):
    def test_gather_reads_real_ledgers(self):
        with tempfile.TemporaryDirectory() as t:
            led = Path(t) / "led"
            _populate(led)
            h = observe.gather(led)
            self.assertEqual(h["gate"]["verdicts"]["deny"], 2)
            self.assertEqual(h["gate"]["verdicts"]["permit"], 1)
            self.assertIn("digest", h["skills"])                  # per-skill quality
            self.assertEqual(h["accept"]["principal_accepted"], 1)
            self.assertTrue(all(isinstance(v, int) for v in h["chains"].values()))  # chains verify

    def test_no_per_person_leak(self):
        with tempfile.TemporaryDirectory() as t:
            led = Path(t) / "led"
            _populate(led)
            h = observe.gather(led)
            txt = observe.render_text(h)
            html = observe.render_html(h, "2026-07-20T00:00:00Z")
            # the principal id is in the ledger but must never reach a rendered surface
            self.assertNotIn(SECRET_PRINCIPAL, txt)
            self.assertNotIn(SECRET_PRINCIPAL, html)
            self.assertIn("system health", txt)
            self.assertIn("Gate decisions", html)

    def test_empty_ledger_dir_is_graceful(self):
        with tempfile.TemporaryDirectory() as t:
            h = observe.gather(Path(t) / "empty")
            self.assertIsInstance(observe.render_text(h), str)   # no crash on a fresh install


if __name__ == "__main__":
    unittest.main()
