"""CI wrapper (T12): run the no-individuation audit against the ACTUAL UI
generators, not only the aggregation module. Fails the build on any per-person
comparative identifier in a rendering surface."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dashboard  # noqa: E402

SURFACES = ["scripts/dashboard.py", "scripts/render_dashboard.py"]


def main():
    failures = []
    for module in SURFACES:
        clean, findings = dashboard.audit_no_individuation(module)
        status = "clean" if clean else f"FAIL ({len(findings)} findings)"
        print(f"individuation audit: {module}: {status}")
        if not clean:
            for f in findings[:20]:
                print(f"  {f}")
            failures.append(module)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
