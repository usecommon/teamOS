#!/usr/bin/env python3
"""teamos — thin onboarding CLI wiring the existing modules. The FK6c kit
automates this; until then it is the hand-assembled path (NEW-1) a non-builder
follows to run FK4/FK5/FK6.

    python3 scripts/teamos.py doctor
    python3 scripts/teamos.py compile  --footprint <dir> [--cc ~/.claude] [--out stores]
    python3 scripts/teamos.py brief     [--out stores]
    python3 scripts/teamos.py loop      [--out stores]
    python3 scripts/teamos.py verify
"""

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(HERE))


def cmd_doctor(args):
    ok = True
    print("teamos doctor")
    print(f"  python: {sys.version.split()[0]} {'ok' if sys.version_info >= (3,10) else 'NEED >=3.10'}")
    for mod in ("jsonschema", "referencing", "yaml", "cryptography"):
        try:
            __import__(mod)
            print(f"  dep {mod}: ok")
        except ImportError:
            print(f"  dep {mod}: MISSING (pip install -r requirements.txt)")
            ok = False
    import shutil
    print(f"  git: {'ok' if shutil.which('git') else 'MISSING'}")
    print(f"  claude (harness): {'ok' if shutil.which('claude') else 'not found (only needed to run live)'}")
    try:
        import connectors
        cfg = connectors.load_config()
        print(f"  connectors.json: valid; inference={cfg['inference']['mode']}; "
              f"sources on={[s['source_id'] for s in cfg['sources'] if s['enabled']] or 'none (opt-in off)'}")
        ch = connectors.notification_channel(cfg)
        print(f"  Slack DM target: {'set' if ch else 'UNSET (edit config/connectors.json before live delivery)'}")
    except Exception as e:  # noqa: BLE001
        print(f"  connectors.json: ERROR {e}"); ok = False
    settings = REPO / ".claude" / "settings.json"
    active = settings.exists() and "PreToolUse" in settings.read_text()
    print(f"  gate activated: {'yes' if active else 'NO — merge hooks/settings-fragment.json into .claude/settings.json after reviewing hooks/gate.py vs hooks/BEHAVIOR.md'}")
    print("  keys: store your per-principal key dir OUTSIDE this repo (see docs/INSTALL.md)")
    return 0 if ok else 1


def cmd_compile(args):
    import compile_footprint as cf
    out = Path(args.out)
    items = cf.load_footprint(args.footprint)
    cc = Path(args.cc).expanduser() if args.cc else None
    result = cf.compile_footprint(
        items, out, REPO / "ledgers",
        cc_footprint_dir=cc if cc and cc.exists() else None,
        cc_user_claude_md=(cc / "CLAUDE.md") if cc and (cc / "CLAUDE.md").exists() else None)
    print(f"compiled {len(result['nodes'])} recurring task(s); "
          f"{len(result['skills'])} skill(s); {len(result['quarantined'])} quarantined")
    print(f"job graph: {out / 'job_graph.json'}")
    return 0


def cmd_brief(args):
    import day_one_brief as brief
    out = Path(args.out)
    jg = json.loads((out / "job_graph.json").read_text())
    b = brief.assemble_brief(jg, out)
    print(brief.render_dm(b))
    print("\n(dry run — set a Slack DM target + activate the gate to deliver live)")
    return 0


def cmd_loop(args):
    import loop
    out = Path(args.out)
    jg = json.loads((out / "job_graph.json").read_text())
    m = loop.run_daily_loop(jg, out, REPO / "ledgers", REPO / "ledgers" / "anchors",
                            run_id=args.run_id)
    print(f"loop {m['run_id']}: {m['count']} shadow deliverable(s) scored; anchored.")
    return 0


def cmd_verify(args):
    import verify_chains
    return verify_chains.main()


def main():
    p = argparse.ArgumentParser(prog="teamos")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("doctor").set_defaults(fn=cmd_doctor)
    c = sub.add_parser("compile"); c.add_argument("--footprint", required=True)
    c.add_argument("--cc", default="~/.claude"); c.add_argument("--out", default="stores")
    c.set_defaults(fn=cmd_compile)
    b = sub.add_parser("brief"); b.add_argument("--out", default="stores"); b.set_defaults(fn=cmd_brief)
    l = sub.add_parser("loop"); l.add_argument("--out", default="stores")
    l.add_argument("--run-id", default="loop-1"); l.set_defaults(fn=cmd_loop)
    sub.add_parser("verify").set_defaults(fn=cmd_verify)
    args = p.parse_args()
    sys.exit(args.fn(args))


if __name__ == "__main__":
    main()
