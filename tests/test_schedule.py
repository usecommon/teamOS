"""Path-(a) local schedule rendering (FK6). Deterministic crontab generation."""
import json
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import schedule  # noqa: E402

TEMPLATES = REPO / "plugin" / "schedule-templates" / "local-schedules.json"


class LocalSchedule(unittest.TestCase):
    def test_template_valid_and_covers_the_loop(self):
        ts = schedule.load(TEMPLATES)
        args = {t["args"] for t in ts}
        # the streak loop: deliver + harvest at minimum
        self.assertIn("deliver", args)
        self.assertIn("harvest", args)
        for t in ts:
            self.assertRegex(t["cron"], r"^[\d\*/, -]+( [\d\*/, -]+){4}$")  # 5 cron fields

    def test_render_produces_runnable_crontab(self):
        ts = schedule.load(TEMPLATES)
        out = schedule.render_crontab(ts, repo="/repo", python="python3")
        # one runnable line per task, with cron + the teamos subcommand + a log
        self.assertIn("0 7 * * * cd /repo && python3 scripts/teamos.py deliver", out)
        self.assertIn("scripts/teamos.py harvest", out)
        self.assertIn(">>", out)  # logging
        # cron-env gotcha is surfaced (no login shell under cron)
        self.assertIn("SLACK_BOT_TOKEN", out)
        for t in ts:
            self.assertIn(t["name"], out)


if __name__ == "__main__":
    unittest.main()
