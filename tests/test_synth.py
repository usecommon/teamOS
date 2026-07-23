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


class RealisticFootprint(unittest.TestCase):
    def test_is_delabeled_and_noised_with_junk(self):
        with tempfile.TemporaryDirectory() as t:
            paths = synth.generate_realistic_footprint("engineer", t, weeks=6, junk_ratio=4)
            # NO deliverable_type frontmatter anywhere (the whole point)
            for p in paths:
                self.assertNotIn("deliverable_type", p.read_text())
            # opaque filenames: type never in the stem
            for typ in ("standup", "pr-summary", "release-notes"):
                self.assertFalse(any(typ in p.name for p in paths), typ)
            # junk inflates volume well beyond the deliverable count
            self.assertGreater(len(paths), 4 * 3)

    def test_compiler_cannot_recover_true_types_from_realistic_data(self):
        # THE FINDING: clean data -> 3 true tasks; realistic -> the compiler
        # recovers none of the true deliverable types (needs the model layer).
        with tempfile.TemporaryDirectory() as t:
            clean = Path(t) / "clean"
            synth.generate_footprint("ops", clean, weeks=6)
            n_clean = len(cf.compile_footprint(cf.load_footprint(clean),
                          Path(t) / "cs", Path(t) / "cl")["job_graph"]["nodes"])
            real = Path(t) / "real"
            synth.generate_realistic_footprint("ops", real, weeks=6)
            nodes = cf.compile_footprint(cf.load_footprint(real),
                        Path(t) / "rs", Path(t) / "rl")["job_graph"]["nodes"]
            true_types = {d["type"] for d in synth.PERSONAS["ops"]["deliverables"]}
            found = {n["task_type"] for n in nodes}
            self.assertEqual(n_clean, 3)                       # labeled: works
            self.assertEqual(true_types & found, set())         # realistic: recovers 0 true types


class RealisticBehavior(unittest.TestCase):
    def test_acceptance_is_quality_coupled(self):
        # high-quality drafts accepted far more often than low-quality ones
        hi = sum(synth.realistic_decision("engineer", t, 0.9)["action"] == "accept" for t in range(300))
        lo = sum(synth.realistic_decision("engineer", t, 0.15)["action"] == "accept" for t in range(300))
        self.assertGreater(hi, lo + 60)

    def test_downstream_use_tracks_quality(self):
        hi = sum(synth.downstream_use(0.9, "e", t) for t in range(300))
        lo = sum(synth.downstream_use(0.15, "e", t) for t in range(300))
        self.assertGreater(hi, lo + 60)

    def test_instrument_separates_coupled_from_null(self):
        import measurement
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "aa4exp", REPO / "review" / "2026-07-23-aa4-behavior-experiment.py")
        exp = importlib.util.module_from_spec(spec); spec.loader.exec_module(exp)
        coupled, null = exp.run("engineer", 2000)
        # THE FINDING: quality-coupled -> instrument detects it; coin-flip -> not
        self.assertEqual(coupled["result"], "correlated")
        self.assertGreater(coupled["interval"][0], 0)      # interval excludes zero
        self.assertEqual(null["result"], "inconclusive")

    def test_trust_is_nonstationary_asymmetric(self):
        # earned slowly, dropped fast (OB-1)
        self.assertLess(synth.update_trust(0.5, "accept") - 0.5,
                        0.5 - synth.update_trust(0.5, "reject"))


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
