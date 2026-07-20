"""Smoke tests for the onboarding CLI (scripts/teamos.py) — doctor, compile,
brief, loop, verify all run without error on the fixtures."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CLI = REPO / "scripts" / "teamos.py"
FOOTPRINT = REPO / "fixtures" / "footprint" / "artifacts"
CC = REPO / "fixtures" / "harness-footprint" / "dot-claude"


def run(*args):
    return subprocess.run([sys.executable, str(CLI), *args],
                          capture_output=True, text=True)


class CLISmoke(unittest.TestCase):
    def test_doctor_runs(self):
        r = run("doctor")
        self.assertIn("teamos doctor", r.stdout)

    def test_compile_then_brief(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "stores"
            c = run("compile", "--footprint", str(FOOTPRINT), "--cc", str(CC),
                    "--out", str(out))
            self.assertEqual(c.returncode, 0, c.stderr)
            self.assertIn("recurring task", c.stdout)
            b = run("brief", "--out", str(out))
            self.assertEqual(b.returncode, 0, b.stderr)
            self.assertIn("Day One Brief", b.stdout)

    def test_compile_extract_flag_runs(self):
        # --extract is backward-safe on a markdown-only footprint
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "stores"
            c = run("compile", "--footprint", str(FOOTPRINT), "--cc", str(CC),
                    "--out", str(out), "--extract")
            self.assertEqual(c.returncode, 0, c.stderr)
            self.assertIn("extracted", c.stdout)

    def test_onboard_preflight_runs_and_fires_compile(self):
        r = run("onboard")
        self.assertIn("readiness preflight", r.stdout)
        self.assertIn("compile fires", r.stdout)
        self.assertIn("recurring task", r.stdout)   # the FK6c compile-once acceptance
        self.assertIn(r.returncode, (0, 1))

    def test_harvest_noop_without_target(self):
        # no enabled DM target in shipped config -> graceful no-op, exit 0
        with tempfile.TemporaryDirectory() as tmp:
            r = run("--ledger-dir", tmp, "harvest")
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn("nothing to harvest", r.stdout)


class OperatorControls(unittest.TestCase):
    """The incident surface: breaker/envelope/inbox reachable from the CLI, and
    the breaker state the CLI writes is the file gate.py reads."""

    def _run(self, tmp, *args):
        return run("--ledger-dir", str(tmp), "--inbox", str(Path(tmp) / "inbox"), *args)

    def test_breaker_trip_reset_roundtrip_is_reachable_and_ledgered(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertIn("closed", self._run(tmp, "status").stdout)
            t = self._run(tmp, "breaker", "trip", "--reason", "spooked", "--by", "jeff")
            self.assertEqual(t.returncode, 0, t.stderr)
            # the file the CLI wrote is exactly what gate.py reads (default path)
            state = json.loads((Path(tmp) / "breaker.json").read_text())
            self.assertEqual(state["state"], "open")
            self.assertIn("OPEN", self._run(tmp, "status").stdout)
            self._run(tmp, "breaker", "reset", "--by", "jeff")
            self.assertEqual(json.loads((Path(tmp) / "breaker.json").read_text())["state"], "closed")
            # trip + reset both hit the L2 ledger
            self.assertEqual(len((Path(tmp) / "l2.jsonl").read_text().splitlines()), 2)

    def test_envelope_reset_and_inbox_list(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertIn("unconfigured", self._run(tmp, "envelope", "status").stdout)
            r = self._run(tmp, "envelope", "reset", "--category", "send")
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertTrue((Path(tmp) / "envelope-state.json").exists())
            self.assertIn("no proposals waiting", self._run(tmp, "inbox", "list").stdout)

    def test_inbox_approve_requires_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = self._run(tmp, "inbox", "approve")
            self.assertNotEqual(r.returncode, 0)


if __name__ == "__main__":
    unittest.main()
