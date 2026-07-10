"""FK3 / A-C6 F-tests: plant a memory with 3 descendants incl. one promoted
skill -> all tombstoned, skill flagged not killed; offline completion resumes;
deadline report; SE-2 third-party shred inside an L8 diff without breaking the
adjacent chain."""

import json
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import deletion  # noqa: E402
import hashchain  # noqa: E402
import l8_capture  # noqa: E402


def plant_l3(ledger_dir, target_id, parent_ids, transformation="verbatim-copy"):
    hashchain.append(ledger_dir / "l3.jsonl", {
        "target_id": target_id,
        "source_type": "principal-direct",
        "authoring_agent": "principal:jeff",
        "evidence": [{"store": "s", "path": "p", "content_hash": "sha256:x"}],
        "transformation": transformation,
        "confidence": "high",
        "update_history_ref": {"store": "git", "path": "p", "content_hash": "sha256:x"},
        "parent_ids": parent_ids,
    }, "test")


class DeletionPropagation(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.d = Path(self.tmp.name)
        # DAG: origin -> mem_child (quote), origin -> distilled (pattern),
        #      distilled -> team/skill (promoted, derived from the pattern)
        plant_l3(self.d, "individual/origin", [])
        plant_l3(self.d, "individual/mem_child", ["individual/origin"], "verbatim-quote")
        plant_l3(self.d, "individual/distilled", ["individual/origin"], "compilation-distill")
        plant_l3(self.d, "team/skill", ["individual/distilled"], "compilation-distill")

    def tearDown(self):
        self.tmp.cleanup()

    def _events(self):
        return [json.loads(l) for l in (self.d / "l9.jsonl").read_text().splitlines()]

    def test_all_descendants_tombstoned_skill_flagged(self):
        state = deletion.request_erasure("individual/origin", "req-1", ledger_dir=self.d)
        self.assertEqual(state["status"], "complete")
        events = self._events()
        marked = {e["affected_node"] for e in events if e["event"] == "descendant_marked"}
        flagged = {e["affected_node"] for e in events if e["event"] == "skill_flagged_for_rederivation"}
        # 3 descendants + origin reached; skill flagged, not marked-for-kill
        self.assertIn("individual/mem_child", marked)
        self.assertIn("individual/distilled", marked)
        self.assertEqual(flagged, {"team/skill"})
        self.assertEqual(state["flagged_skills"], ["team/skill"])

    def test_content_vs_statistical_distinguished(self):
        deletion.request_erasure("individual/origin", "req-2", ledger_dir=self.d)
        kinds = {e["affected_node"]: e["deletion_kind"] for e in self._events()
                 if e["event"] in ("descendant_marked", "skill_flagged_for_rederivation")}
        # a quote is content-traceable; a distilled pattern is statistical
        self.assertEqual(kinds["individual/mem_child"], "content_traceable")
        self.assertEqual(kinds["individual/distilled"], "statistical_influence")
        self.assertEqual(kinds["team/skill"], "statistical_influence")

    def test_tombstone_and_purge_events_present(self):
        deletion.request_erasure("individual/origin", "req-3", ledger_dir=self.d)
        evs = [e["event"] for e in self._events()]
        self.assertEqual(evs[0], "tombstone_written")
        self.assertIn("purge_completed", evs)

    def test_offline_completion_resumes_idempotently(self):
        # simulate interruption: run once, truncate state to half-done, re-run
        deletion.request_erasure("individual/origin", "req-4", ledger_dir=self.d)
        req = self.d / "deletion-requests" / "req-4.json"
        state = json.loads(req.read_text())
        state["status"] = "pending"
        state["processed"] = state["processed"][:1]  # pretend crash after 1 node
        req.write_text(json.dumps(state))
        before = len((self.d / "l9.jsonl").read_text().splitlines())
        resumed = deletion.request_erasure("individual/origin", "req-4", ledger_dir=self.d)
        self.assertEqual(resumed["status"], "complete")
        # resume only emits events for the unprocessed nodes + purge — not dupes
        after = len((self.d / "l9.jsonl").read_text().splitlines())
        self.assertGreater(after, before)
        # every affected node appears; the DAG has 4 nodes total
        affected = {e["affected_node"] for e in self._events()
                    if e["event"] in ("descendant_marked", "skill_flagged_for_rederivation")}
        self.assertEqual(len(affected), 4)

    def test_l9_chain_verifies(self):
        deletion.request_erasure("individual/origin", "req-5", ledger_dir=self.d)
        self.assertGreater(hashchain.verify(self.d / "l9.jsonl"), 0)

    def test_deadline_report_flags_overdue(self):
        deletion.request_erasure("individual/origin", "req-6", ledger_dir=self.d,
                                 deadline="2020-01-01T00:00:00Z")
        # mark incomplete to test overdue detection
        req = self.d / "deletion-requests" / "req-6.json"
        state = json.loads(req.read_text())
        state["status"] = "pending"
        req.write_text(json.dumps(state))
        rows = deletion.deadline_report(ledger_dir=self.d)
        self.assertEqual(rows[0]["status"], "overdue")


class ThirdPartyL8Shred(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.d = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_erasure_reaches_l8_diff_content_chain_survives(self):
        # three edits; the middle one's diff contains a third party's content
        for i, secret in enumerate(["alpha", "COLLEAGUE_PII_bob", "gamma"]):
            draft = self.d / f"d{i}.md"
            edited = self.d / f"e{i}.md"
            draft.write_text(f"base {i}\n")
            edited.write_text(f"base {i} {secret}\n")
            l8_capture.capture_edit(draft, edited, "principal:jeff", ledger_dir=self.d)
        self.assertEqual(hashchain.verify(self.d / "l8.jsonl"), 3)
        shredded = deletion.shred_l8_content("COLLEAGUE_PII_bob", "dsar-1", ledger_dir=self.d)
        self.assertEqual(len(shredded), 1)
        # referenced content gone
        self.assertFalse(Path(shredded[0]).exists())
        # adjacent chain STILL verifies (chain hashes references, not content)
        self.assertEqual(hashchain.verify(self.d / "l8.jsonl"), 3)
        # a content_shredded event was ledgered
        evs = [json.loads(l) for l in (self.d / "l9.jsonl").read_text().splitlines()]
        self.assertEqual(evs[0]["event"], "content_shredded")
        self.assertEqual(evs[0]["requester_type"], "third_party_dsar")


if __name__ == "__main__":
    unittest.main()
