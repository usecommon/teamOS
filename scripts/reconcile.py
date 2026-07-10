"""Schedule reconciliation loop (FK6c). One bootstrap task compares desired vs
actual schedules and repairs drift — self-healing on both tiers. Deterministic."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import loop_linter  # noqa: E402


def reconcile(desired_templates, actual_names):
    """Return the repair plan. Desired schedules whose prompt fails the linter
    are NOT proposed for creation (fenced). Returns {create, ok, blocked}."""
    actual = set(actual_names)
    create, ok, blocked = [], [], []
    for t in desired_templates:
        clean, findings = loop_linter.lint_template(t)
        if not clean:
            blocked.append({"name": t["name"], "findings": findings})
            continue
        if t["name"] in actual:
            ok.append(t["name"])
        else:
            create.append(t["name"])   # drift: a desired schedule is missing
    return {"create": create, "ok": ok, "blocked": blocked}
