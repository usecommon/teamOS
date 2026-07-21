"""Synthetic data + persona/actor types: deterministic, ingestable by FK4,
and behaviorally varied. Synthetic only — no real data (CLAUDE.md hygiene)."""
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import synth  # noqa: E402
import compile_footprint as cf  # noqa: E402


class Personas(unittest.TestCase):
    def test_persona_catalog_well_formed(self):
        self.assertIn("engineer", synth.PERSONAS)
        for pid, p in synth.PERSONAS.items():
            self.assertGreaterEqual(len(p["deliverables"]), 3, pid)  # >=3 recurring tasks
            self.assertTrue(0 < p["accept"] <= 1, pid)
            self.assertIn(p["edit_style"], synth.EDIT_DISTANCE, pid)
            for d in p["deliverables"]:
                self.assertTrue({"type", "source", "cadence_days"} <= set(d), pid)

    def test_actor_types_present(self):
        for a in ("colleague", "red-team", "manager", "client"):
            self.assertIn(a, synth.ACTORS)


class FootprintGeneration(unittest.TestCase):
    def test_generates_valid_ingestable_footprint(self):
        with tempfile.TemporaryDirectory() as t:
            paths = synth.generate_footprint("engineer", t, weeks=6)
            self.assertTrue(paths)
            # valid dates (regression: earlier bug generated 2026-06-36)
            for p in paths:
                self.assertTrue(p.name.endswith(".md"))
            # FK4 compiles it into >=3 recurring tasks (the A-C2 threshold)
            items = cf.load_footprint(t)
            res = cf.compile_footprint(items, Path(t) / "stores", Path(t) / "ledgers")
            self.assertGreaterEqual(len(res["job_graph"]["nodes"]), 3)

    def test_generation_is_deterministic(self):
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            pa = synth.generate_footprint("pm", a, weeks=4)
            pb = synth.generate_footprint("pm", b, weeks=4)
            self.assertEqual([p.name for p in pa], [p.name for p in pb])
            self.assertEqual((pa[0]).read_text(), (pb[0]).read_text())

    def test_unknown_persona_raises(self):
        with self.assertRaises(KeyError):
            synth.generate_footprint("nobody", tempfile.gettempdir())


class Behavior(unittest.TestCase):
    def test_decision_deterministic_and_varied(self):
        d1 = synth.decision("engineer", 5)
        d2 = synth.decision("engineer", 5)
        self.assertEqual(d1, d2)                       # reproducible
        actions = {synth.decision("engineer", t)["action"] for t in range(60)}
        self.assertTrue({"accept", "reject", "ignore"} & actions)
        # an accept carries an edit distance within the persona's style band
        lo, hi = synth.EDIT_DISTANCE["light"]
        for t in range(60):
            d = synth.decision("engineer", t)
            if d["action"] == "accept":
                self.assertTrue(lo <= d["edit_distance"] <= hi)


if __name__ == "__main__":
    unittest.main()
