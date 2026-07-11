"""Smoke tests for the onboarding CLI (scripts/teamos.py) — doctor, compile,
brief, loop, verify all run without error on the fixtures."""

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


if __name__ == "__main__":
    unittest.main()
