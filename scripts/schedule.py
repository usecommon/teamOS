"""Path-(a) local schedule rendering (FK6). Turns the local-schedule template
into crontab lines that run the teamos CLI at the runtime of record. Print-only
by design — the user installs it; nothing here mutates the system crontab.

Path (a) is the runtime of record (all A-A4 validation runs here); path (b) is the
door-fenced cloud variant (plugin/schedule-templates/desired-schedules.json)."""
import json
from pathlib import Path

# env cron does NOT inherit from the login shell — these must be set for the gate,
# envelope, and live delivery to work under cron.
ENV_KEYS = ("TEAMOS_KEYDIR", "TEAMOS_ENVELOPE_STATE", "TEAMOS_BREAKER",
            "TEAMOS_POSTURE", "SLACK_BOT_TOKEN")


def load(path):
    return json.loads(Path(path).read_text())


def render_crontab(templates, repo, python="python3", logdir="~/.teamos/logs"):
    """Return a ready-to-install crontab block (as a string). Deterministic."""
    lines = [
        "# Team OS — local schedules (path a, the runtime of record).",
        "# Install: `teamos schedule >> mycron && crontab mycron` (review first).",
        "# cron has NO login-shell env — set what the gate/delivery need here:",
        "#   " + "  ".join(f"{k}=..." for k in ENV_KEYS),
        f"# Logs: {logdir}/<name>.log",
        "",
    ]
    for t in templates:
        cmd = f"cd {repo} && {python} scripts/teamos.py {t['args']}"
        log = f"{logdir}/{t['name']}.log"
        lines.append(f"# {t['name']}: {t.get('desc', '')}")
        lines.append(f"{t['cron']} {cmd} >> {log} 2>&1")
    return "\n".join(lines) + "\n"
