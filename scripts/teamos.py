#!/usr/bin/env python3
"""teamos — thin onboarding + operator CLI wiring the existing modules. The FK6c
kit automates this; until then it is the hand-assembled path (NEW-1) a non-builder
follows to run FK4/FK5/FK6 — and the operator surface a principal reaches for in
an incident. Every control below is the principal invoking already-tested library
code directly (never the agent through the gate); the state files these write are
protected paths the gate can only READ.

    onboarding / run:
      python3 scripts/teamos.py doctor
      python3 scripts/teamos.py onboard   [--footprint <dir>] [--extract]   # readiness preflight
      python3 scripts/teamos.py install   [--apply]        # activate the gate hook (preview by default)
      python3 scripts/teamos.py compile  --footprint <dir> [--cc ~/.claude] [--out stores] [--extract]
      python3 scripts/teamos.py brief     [--out stores]
      python3 scripts/teamos.py deliver   [--out stores]   # live brief (dry-run until configured)
      python3 scripts/teamos.py harvest                    # ✓/✗ reactions on last brief -> L8
      python3 scripts/teamos.py loop      [--out stores]
      python3 scripts/teamos.py schedule                   # print path-(a) crontab (deliver/harvest/loop)
      python3 scripts/teamos.py synth     --list | --persona <id> --out <dir> [--weeks N]  # synthetic test data
      python3 scripts/teamos.py verify

    operator controls (the frightened-user surface):
      python3 scripts/teamos.py status
      python3 scripts/teamos.py breaker  {status|trip --reason R|reset} [--by ID]
      python3 scripts/teamos.py envelope {status|reset --category C} [--by ID]
      python3 scripts/teamos.py inbox    {list|approve PROPOSAL_ID|process} [--by ID]
      python3 scripts/teamos.py undo      --path REL --sha SHA
      python3 scripts/teamos.py erase     --node NODE_ID --request REQ_ID
"""

import argparse
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(HERE))


def _ledger_dir(args):
    return Path(args.ledger_dir)


def _breaker_path(args):
    return Path(os.environ.get("TEAMOS_BREAKER", _ledger_dir(args) / "breaker.json"))


def _envelope_path(args):
    return Path(os.environ.get("TEAMOS_ENVELOPE_STATE",
                               _ledger_dir(args) / "envelope-state.json"))


def _inbox_dir(args):
    return Path(args.inbox)


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
    print(f"  gate activated: {'yes' if active else 'NO — review hooks/gate.py vs hooks/BEHAVIOR.md, then run: teamos install --apply'}")
    print("  keys: store your per-principal key dir OUTSIDE this repo (see docs/INSTALL.md)")
    return 0 if ok else 1


def cmd_compile(args):
    import compile_footprint as cf
    import extract
    out = Path(args.out)
    if args.extract and not extract.available():
        print("  note: --extract set but markitdown not installed; run "
              "`pip install markitdown` for real-footprint extraction. Markdown only for now.")
    items = cf.load_footprint(args.footprint, extract_nonmd=args.extract)
    n_extracted = sum(1 for i in items if i["provenance"].get("extracted_via", "").startswith("markitdown"))
    if args.extract:
        print(f"  extracted {n_extracted} non-markdown file(s) via markitdown (local, deterministic)")
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


def cmd_synth(args):
    """Generate synthetic test data / list persona + actor types. No real data
    (CLAUDE.md hygiene); deterministic, reproducible. Use the generated footprint
    with `teamos compile --footprint <dir>`."""
    import synth
    if args.list:
        print("Principal personas (agent types under test):")
        for pid, role in synth.list_personas().items():
            print(f"  {pid:<12} {role}")
        print("\nNon-principal actor types (multi-actor scenarios):")
        for aid, role in synth.list_actors().items():
            print(f"  {aid:<12} {role}")
        return 0
    if not args.persona or not args.out:
        print("usage: teamos synth --list | --persona <id> --out <dir> [--weeks N]")
        return 2
    try:
        paths = synth.generate_footprint(args.persona, args.out, weeks=args.weeks)
    except KeyError as e:
        print(str(e)); return 2
    print(f"wrote {len(paths)} synthetic artifact(s) for '{args.persona}' to {args.out}")
    print(f"next: python3 scripts/teamos.py compile --footprint {args.out} --out <stores>")
    return 0


def cmd_onboard(args):
    """FK6c readiness preflight: deps + gate + connectors + a compile-once smoke,
    all READ-ONLY (temp dirs; no real stores/ledgers/.claude touched). Reports
    what's ready and exactly what's missing to start the A-A4 streak."""
    import shutil as _sh
    import tempfile
    import compile_footprint as cf
    import connectors
    import extract
    import install
    import schedule
    checks = []  # (label, status: True ok / False blocker / None warn, detail)

    checks.append(("python >=3.10", sys.version_info >= (3, 10), sys.version.split()[0]))
    for mod in ("jsonschema", "yaml", "cryptography"):
        try:
            __import__(mod); checks.append((f"dep {mod}", True, ""))
        except ImportError:
            checks.append((f"dep {mod}", False, "pip install -r requirements.txt"))
    checks.append(("git", bool(_sh.which("git")), ""))

    res = install.activate(REPO / ".claude", REPO / "hooks" / "settings-fragment.json", apply=False)
    checks.append(("gate activated", not res["changed"],
                   "" if not res["changed"] else "run: teamos install --apply"))

    # compile-once acceptance (the FK6c 'fires compile once' gate) into a temp dir
    fp = Path(args.footprint) if args.footprint else REPO / "fixtures" / "footprint" / "artifacts"
    tmp = Path(tempfile.mkdtemp(prefix="teamos-onboard-"))
    try:
        items = cf.load_footprint(fp, extract_nonmd=args.extract)
        r = cf.compile_footprint(items, tmp / "stores", tmp / "ledgers")
        n = len(r["job_graph"].get("nodes", []))
        checks.append((f"compile fires ({fp.name})", n >= 1,
                       f"{n} recurring task(s), {len(r.get('quarantined', []))} quarantined"))
    except Exception as e:  # noqa: BLE001
        checks.append(("compile fires", False, str(e)))
    finally:
        _sh.rmtree(tmp, ignore_errors=True)

    # warnings — needed for LIVE delivery, not for a governed dry-run
    checks.append(("markitdown (for --extract)", extract.available() or None,
                   "" if extract.available() else "pip install markitdown"))
    checks.append(("claude harness", bool(_sh.which("claude")) or None,
                   "" if _sh.which("claude") else "not found (needed to run live)"))
    try:
        cfg = connectors.load_config()
        on = [s["source_id"] for s in cfg["sources"] if s["enabled"]]
        checks.append(("sources enabled", bool(on) or None,
                       ", ".join(on) or "none — enable in config/connectors.json"))
        ch = connectors.notification_channel()
        tgt = bool(ch and not str(ch.get("target", "")).startswith("SET_"))
        checks.append(("Slack DM target", tgt or None,
                       "" if tgt else "set target + enabled:true in config/connectors.json"))
    except Exception as e:  # noqa: BLE001
        checks.append(("connectors.json", False, str(e)))
    checks.append(("SLACK_BOT_TOKEN", bool(os.environ.get("SLACK_BOT_TOKEN")) or None,
                   "" if os.environ.get("SLACK_BOT_TOKEN") else "export for live sends (dry-run without)"))
    checks.append(("TEAMOS_KEYDIR", bool(os.environ.get("TEAMOS_KEYDIR")) or None,
                   "" if os.environ.get("TEAMOS_KEYDIR") else "set for principal-authenticated ✓ (CN-1)"))
    try:
        st = schedule.load(REPO / "plugin" / "schedule-templates" / "local-schedules.json")
        checks.append(("schedule template", True, ", ".join(t["args"] for t in st)))
    except Exception as e:  # noqa: BLE001
        checks.append(("schedule template", False, str(e)))

    sym = {True: "✓", False: "✗", None: "⚠"}
    print("teamos onboard — readiness preflight\n")
    for label, ok, detail in checks:
        print(f"  {sym[ok]} {label}" + (f" — {detail}" if detail else ""))
    blockers = [l for l, ok, _ in checks if ok is False]
    warns = [l for l, ok, _ in checks if ok is None]
    print()
    if blockers:
        print(f"NOT READY — fix {len(blockers)} blocker(s): {', '.join(blockers)}")
    else:
        print("READY (governed). The tool installs, is gated, and compiles.")
    if warns:
        print(f"For full LIVE delivery, also set: {', '.join(warns)}")
    return 0 if not blockers else 1


def cmd_install(args):
    """Activate the FK2 gate hook by merging hooks/settings-fragment.json into
    .claude/settings.json. Previews by default; --apply writes (keeps a .bak).
    Review hooks/gate.py against hooks/BEHAVIOR.md before applying (X-1)."""
    import install
    res = install.activate(REPO / ".claude", REPO / "hooks" / "settings-fragment.json",
                           apply=args.apply)
    if not res["changed"]:
        print(f"gate already active in {res['path']} — nothing to do.")
        return 0
    if not args.apply:
        print(f"Would activate the Team OS gate hook in {res['path']}:\n")
        print(json.dumps(res["merged"].get("hooks", {}), indent=2))
        print("\nReview hooks/gate.py vs hooks/BEHAVIOR.md first (X-1), then re-run with --apply.")
        return 0
    print(f"Activated the gate hook in {res['path']} (backup: settings.json.bak).")
    print("\nNext:")
    print("  1) enable a Slack DM target in config/connectors.json + export SLACK_BOT_TOKEN")
    print("  2) teamos compile --footprint <your folder> --extract")
    print("  3) teamos schedule >> mycron && crontab mycron   # start the A-A4 streak")
    return 0


def cmd_schedule(args):
    """Print the path-(a) local crontab that runs deliver/harvest/loop/verify at
    the runtime of record — the loops that start the A-A4 streak. Print-only;
    review and install yourself (`teamos schedule >> mycron && crontab mycron`)."""
    import schedule
    templates = schedule.load(REPO / "plugin" / "schedule-templates" / "local-schedules.json")
    print(schedule.render_crontab(templates, repo=str(REPO), python=sys.executable))
    return 0


def cmd_deliver(args):
    """Deliver the Day One Brief live (FK5/FK6): assemble -> gated send. Dry-run
    until config/connectors.json has an enabled Slack DM target AND SLACK_BOT_TOKEN
    is set. The send traverses the FK2 gate before any post (breaker/envelope/
    payload-scan apply). This is how the A-A4 streak starts on a real footprint."""
    import day_one_brief as brief
    import connectors
    import slack_client
    out = Path(args.out)
    jg = json.loads((out / "job_graph.json").read_text())
    b = brief.assemble_brief(jg, out)
    ch = connectors.notification_channel()
    if not ch or str(ch.get("target", "")).startswith("SET_"):
        print(brief.render_dm(b))
        print("\n(dry run — set an enabled Slack DM target in config/connectors.json to deliver live)")
        return 0
    client = slack_client.from_env_or_dry()
    dry = isinstance(client, slack_client.DryRunSlack)
    try:
        ts, _ = brief.deliver(b, ch["target"], client, _ledger_dir(args))
        print(f"delivered to {ch['target']} (ts={ts}){' [dry-run — no SLACK_BOT_TOKEN]' if dry else ''}")
        return 0
    except brief.GateBlocked as gb:
        print(f"gate blocked the send (breaker/envelope): {gb}")
        return 1


def cmd_harvest(args):
    """Harvest ✓/✗ reactions on the most recently delivered brief -> L8.
    Deterministic (reactions.get only, no model, SE-1) and principal-authenticated
    (only the principal's reactions count, CN-1). No-op in dry-run / no reactions."""
    import day_one_brief as brief
    import connectors
    import slack_client
    ch = connectors.notification_channel()
    if not ch or str(ch.get("target", "")).startswith("SET_"):
        print("(no enabled Slack DM target — nothing to harvest)")
        return 0
    principal = ch.get("principal_user_id") or ch["target"]
    l2 = _ledger_dir(args) / "l2.jsonl"
    channel_ts = None
    if l2.exists():
        for line in reversed(l2.read_text().splitlines()):
            try:
                r = json.loads(line)
            except ValueError:
                continue
            if r.get("rule_id") == "send-receipt" and r.get("outcome") == "send_succeeded":
                tgt = r["proposed_action"].get("target", "")
                if "/" in tgt:
                    channel_ts = tgt.rsplit("/", 1)
                    break
    if not channel_ts:
        print("(no delivered brief found in the ledger to harvest)")
        return 0
    channel, ts = channel_ts
    client = slack_client.from_env_or_dry()
    recs = brief.harvest_reactions(channel, ts, principal, client, _ledger_dir(args))
    accepted = brief.count_accepted(recs)
    print(f"harvested {len(recs)} reaction(s) from {channel}/{ts}; "
          f"{accepted} principal-authenticated ✓ recorded to L8")
    return 0


# --- operator controls: the incident surface (principal-invoked, direct) ------

def cmd_status(args):
    import circuit_breaker as cb
    b = cb.load(_breaker_path(args))
    print("teamos status")
    if b["state"] == "open":
        print(f"  circuit breaker: OPEN — side-effectful actions denied "
              f"(tripped by {b['tripped_by']}: {b['reason']})")
    else:
        print("  circuit breaker: closed")
    env_p = _envelope_path(args)
    if env_p.exists():
        lv = json.loads(env_p.read_text()).get("levels", {})
        print("  envelope levels: " + ", ".join(f"{c}={lv[c]}" for c in lv))
    else:
        print("  envelope levels: unconfigured (no gating — gate ASKS on clean sends)")
    prop = _inbox_dir(args) / "proposals"
    pend = len(list(prop.glob("*.json"))) if prop.exists() else 0
    print(f"  inbox proposals waiting: {pend}")
    settings = REPO / ".claude" / "settings.json"
    active = settings.exists() and "PreToolUse" in settings.read_text()
    print(f"  gate activated: {'yes' if active else 'NO'}")
    return 0


def cmd_breaker(args):
    import circuit_breaker as cb
    ld, state = _ledger_dir(args), _breaker_path(args)
    if args.action == "status":
        print(json.dumps(cb.load(state), indent=2))
    elif args.action == "trip":
        cb.trip(ld, state, args.by, args.reason)
        print(f"breaker OPEN — every write/edit/send/execute/schedule now denied (by {args.by})")
    elif args.action == "reset":
        cb.reset(ld, state, args.by)
        print(f"breaker CLOSED — side-effectful actions permitted again (by {args.by})")
    return 0


def cmd_envelope(args):
    import envelope as env
    ld, state = _ledger_dir(args), _envelope_path(args)
    if args.action == "status":
        if not state.exists():
            print("envelope: unconfigured (state file absent → no envelope gating)")
            return 0
        print(json.dumps(json.loads(state.read_text()).get("levels", {}), indent=2))
    elif args.action == "reset":
        env.reset(args.category, ld, state)
        print(f"envelope category '{args.category}' reset to base (by {args.by})")
    return 0


def cmd_inbox(args):
    import gate_processor as gp
    inbox, ld = _inbox_dir(args), _ledger_dir(args)
    if args.action == "list":
        prop = inbox / "proposals"
        rows = sorted(prop.glob("*.json")) if prop.exists() else []
        if not rows:
            print("inbox: no proposals waiting")
        for p in rows:
            d = json.loads(p.read_text())
            pid = d.get("proposal_id", p.stem)
            approved = (inbox / "approvals" / f"{pid}.approved").exists()
            print(f"  {pid}  kind={d.get('kind', '?')}  approved={approved}")
    elif args.action == "approve":
        gp.approve(inbox, args.proposal_id, args.by)
        print(f"approved {args.proposal_id} — release it with: teamos inbox process")
    elif args.action == "process":
        res = gp.process_inbox(inbox, REPO, ld)
        print(f"committed={res['committed']}  pending={res['pending']}  rejected={res['rejected']}")
    return 0


def cmd_undo(args):
    import transfer
    transfer.restore_version(REPO, args.path, args.sha)
    print(f"restored {args.path} to {args.sha} (byte-identical, git-backed L6)")
    return 0


def cmd_erase(args):
    import deletion
    state = deletion.request_erasure(args.node, args.request,
                                     ledger_dir=_ledger_dir(args), store_root=REPO)
    print(f"erasure {args.request}: {state.get('status', 'requested')} "
          f"(content removed + L9 tombstones; deadline {state.get('deadline', '?')})")
    return 0


def main():
    p = argparse.ArgumentParser(prog="teamos")
    p.add_argument("--ledger-dir", default=str(REPO / "ledgers"))
    p.add_argument("--inbox", default=str(REPO / "inbox"))
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("doctor").set_defaults(fn=cmd_doctor)
    ob = sub.add_parser("onboard"); ob.add_argument("--footprint", default=None)
    ob.add_argument("--extract", action="store_true"); ob.set_defaults(fn=cmd_onboard)
    ins = sub.add_parser("install"); ins.add_argument("--apply", action="store_true")
    ins.set_defaults(fn=cmd_install)
    c = sub.add_parser("compile"); c.add_argument("--footprint", required=True)
    c.add_argument("--cc", default="~/.claude"); c.add_argument("--out", default="stores")
    c.add_argument("--extract", action="store_true",
                   help="also ingest non-markdown files (pdf/docx/…) via local markitdown")
    c.set_defaults(fn=cmd_compile)
    b = sub.add_parser("brief"); b.add_argument("--out", default="stores"); b.set_defaults(fn=cmd_brief)
    dv = sub.add_parser("deliver"); dv.add_argument("--out", default="stores"); dv.set_defaults(fn=cmd_deliver)
    hv = sub.add_parser("harvest"); hv.set_defaults(fn=cmd_harvest)
    l = sub.add_parser("loop"); l.add_argument("--out", default="stores")
    l.add_argument("--run-id", default="loop-1"); l.set_defaults(fn=cmd_loop)
    sub.add_parser("verify").set_defaults(fn=cmd_verify)
    sub.add_parser("schedule").set_defaults(fn=cmd_schedule)
    sy = sub.add_parser("synth"); sy.add_argument("--list", action="store_true")
    sy.add_argument("--persona"); sy.add_argument("--out"); sy.add_argument("--weeks", type=int, default=6)
    sy.set_defaults(fn=cmd_synth)

    # operator controls
    sub.add_parser("status").set_defaults(fn=cmd_status)

    bk = sub.add_parser("breaker"); bk.add_argument("action", choices=["status", "trip", "reset"])
    bk.add_argument("--reason", default="manual halt"); bk.add_argument("--by", default="principal")
    bk.set_defaults(fn=cmd_breaker)

    ev = sub.add_parser("envelope"); ev.add_argument("action", choices=["status", "reset"])
    ev.add_argument("--category", default="write",
                    choices=["read", "write", "send", "execute", "schedule"])
    ev.add_argument("--by", default="principal"); ev.set_defaults(fn=cmd_envelope)

    ib = sub.add_parser("inbox"); ib.add_argument("action", choices=["list", "approve", "process"])
    ib.add_argument("proposal_id", nargs="?"); ib.add_argument("--by", default="principal")
    ib.set_defaults(fn=cmd_inbox)

    u = sub.add_parser("undo"); u.add_argument("--path", required=True)
    u.add_argument("--sha", required=True); u.set_defaults(fn=cmd_undo)

    e = sub.add_parser("erase"); e.add_argument("--node", required=True)
    e.add_argument("--request", required=True); e.set_defaults(fn=cmd_erase)

    args = p.parse_args()
    if getattr(args, "cmd", None) == "inbox" and args.action == "approve" and not args.proposal_id:
        p.error("inbox approve requires a PROPOSAL_ID")
    sys.exit(args.fn(args))


if __name__ == "__main__":
    main()
