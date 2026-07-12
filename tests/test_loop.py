"""FK6 F-tests: loop produces >=3 shadow deliverables; each L7 joins to a
version; checkpoint resumes after a mid-run kill with nothing lost and no step
repeated; chain heads anchored off-box each run; pulse instrument; initiative
floor counts only accepted principal-authenticated deliverables."""

import json
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import compile_footprint as cf  # noqa: E402
import hashchain  # noqa: E402
import loop  # noqa: E402
import measurement  # noqa: E402
from checkpoint import Checkpoint, run_checkpointed  # noqa: E402
from schema_registry import validator_for  # noqa: E402

FOOTPRINT = REPO_ROOT / "fixtures" / "footprint"


class LoopRun(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.d = Path(self.tmp.name)
        self.out = self.d / "out"
        items = cf.load_footprint(FOOTPRINT / "artifacts")
        self.jg = cf.compile_footprint(items, self.out, self.d)["job_graph"]
        self.manifest = loop.run_daily_loop(
            self.jg, self.out, self.d, self.d / "anchors", "run-1",
            skill_version="deadbeef")

    def tearDown(self):
        self.tmp.cleanup()

    def test_at_least_3_shadow_deliverables(self):
        self.assertGreaterEqual(self.manifest["count"], 3)  # CN-6 floor
        drafts = list((self.out / "deliverables").glob("*-shadow.md"))
        self.assertEqual(len(drafts), self.manifest["count"])

    def test_l7_records_join_to_version_and_validate(self):
        recs = [json.loads(l) for l in (self.d / "l7.jsonl").read_text().splitlines()]
        self.assertGreaterEqual(len(recs), 3)
        v = validator_for("ledger-l7-eval.schema.json")
        for r in recs:
            v.validate(r)
            self.assertEqual(r["skill_version"], "deadbeef")  # L7 -> L6 join
        self.assertEqual(hashchain.verify(self.d / "l7.jsonl"), len(recs))

    def test_chain_heads_anchored_off_box(self):
        anchors = list((self.d / "anchors").glob("*.anchor.json"))
        self.assertEqual(len(anchors), 1)
        anchor = json.loads(anchors[0].read_text())
        self.assertIn("l7.jsonl", anchor["heads"])
        self.assertEqual(anchor["heads"]["l7.jsonl"],
                         hashchain.last_hash(self.d / "l7.jsonl"))


class CheckpointResume(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.d = Path(self.tmp.name)
        self.cp = self.d / "cp.json"
        self.side_effects = []

    def tearDown(self):
        self.tmp.cleanup()

    def _steps(self, crash_on=None):
        def mk(name):
            def fn(_r):
                if name == crash_on:
                    raise RuntimeError("simulated kill")
                self.side_effects.append(name)
                return {"ok": name}
            return (name, fn)
        return [mk("a"), mk("b"), mk("c")]

    def test_resume_loses_nothing_and_repeats_nothing(self):
        # first run crashes on step b (a completed and is durably recorded)
        with self.assertRaises(RuntimeError):
            run_checkpointed(self._steps(crash_on="b"), self.cp)
        self.assertEqual(self.side_effects, ["a"])
        # resume: a is skipped, b and c run
        results = run_checkpointed(self._steps(crash_on=None), self.cp)
        self.assertEqual(self.side_effects, ["a", "b", "c"])  # a not repeated
        self.assertEqual(set(results), {"a", "b", "c"})       # nothing lost

    def test_completed_flow_is_idempotent(self):
        run_checkpointed(self._steps(), self.cp)
        self.side_effects.clear()
        run_checkpointed(self._steps(), self.cp)  # all done -> no re-run
        self.assertEqual(self.side_effects, [])


class Measurement(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.d = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def _accept(self, path="x", dist=0.0, attribution="principal_authenticated",
                signal="endorsement", unprompted=True):
        # write an L8 record directly with a controlled timestamp
        rec = hashchain.append(self.d / "l8.jsonl", {
            "signal_type": signal,
            "artifact_ref": {"store": "brief", "path": path, "content_hash": "sha256:x"},
            "principal_id": "U", "attribution": attribution,
            "outcome": "accepted" if signal == "endorsement" else "other",
            "edit_distance_normalized": dist,
            "unprompted": unprompted,
            "harvest": {"method": "slack-reactions-get", "harvested_at": "2026-07-10T00:00:00Z"},
        }, "test")
        return rec

    def test_initiative_floor_counts_only_accepted_principal_light_edit(self):
        self._accept(path="a", dist=0.0)                          # counts
        self._accept(path="b", dist=0.1)                          # counts (light)
        self._accept(path="c", dist=0.0)                          # counts
        self._accept(path="d", dist=0.5)                          # NOT (heavy edit)
        self._accept(path="e", dist=0.0, attribution="unattributed")  # NOT
        self._accept(path="f", dist=0.0, signal="rejection")     # NOT (rejection)
        count, hits = measurement.weekly_accepted(self.d)
        self.assertEqual(count, 3)
        self.assertTrue(measurement.floor_met(count))

    def test_prompted_work_never_inflates_the_floor(self):
        # T6: the user asked for these on Tuesday — not initiative
        for p in ("a", "b", "c"):
            self._accept(path=p, unprompted=False)
        count, _ = measurement.weekly_accepted(self.d)
        self.assertEqual(count, 0)

    def test_missing_edit_distance_is_not_accepted(self):
        self._accept(path="a", dist=None)                        # fail safe: NOT
        self._accept(path="b", dist=0.0)
        count, _ = measurement.weekly_accepted(self.d)
        self.assertEqual(count, 1)

    def test_recurring_digest_counts_once(self):
        # T6 dedupe: re-endorsing the same deliverable pads nothing
        for _ in range(5):
            self._accept(path="deliverables/daily-digest.md", dist=0.0)
        self._accept(path="deliverables/retro.md", dist=0.0)
        count, _ = measurement.weekly_accepted(self.d)
        self.assertEqual(count, 2)

    def test_rejection_does_not_reduce_the_floor_count(self):
        # honest ✗ costs nothing: floor counts accepted work, independent of
        # the envelope
        for p in ("a", "b", "c"):
            self._accept(path=p, dist=0.0)
        before, _ = measurement.weekly_accepted(self.d)
        for p in ("x", "y", "z"):
            self._accept(path=p, signal="rejection")
        after, _ = measurement.weekly_accepted(self.d)
        self.assertEqual(before, after)

    def test_pulse_instrument_records_question_and_response(self):
        q = measurement.emit_pulse("How useful was this week's output?", self.d, "2026-W28")
        self.assertTrue(Path(q).exists())
        rec = measurement.record_pulse_response(4, "U", self.d, "2026-W28")
        validator_for("ledger-l8-human-signal.schema.json").validate(rec)
        self.assertEqual(rec["signal_type"], "pulse_response")
        self.assertEqual(rec["outcome"], "4")


if __name__ == "__main__":
    unittest.main()
