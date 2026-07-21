"""Live observability — reads the REAL ledgers and renders system health.
Terminal-first; optional self-contained HTML. Deterministic, no LLM. Per-SKILL,
never per-person (no individuation): L8 is aggregated in totals only, quality is
keyed by skill_id, and no principal_id is ever broken out.
"""
import json
import os
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import hashchain  # noqa: E402
import dashboard as skilldash  # noqa: E402
import measurement  # noqa: E402


def _load(path):
    p = Path(path)
    if not p.exists():
        return []
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()]


def _breaker_path(led):
    return Path(os.environ.get("TEAMOS_BREAKER", Path(led) / "breaker.json"))


def _envelope_path(led):
    return Path(os.environ.get("TEAMOS_ENVELOPE_STATE", Path(led) / "envelope-state.json"))


def gather(ledger_dir):
    """Read every observation surface into one health snapshot (real data)."""
    led = Path(ledger_dir)
    l2 = _load(led / "l2.jsonl")
    l8 = _load(led / "l8.jsonl")
    l7 = _load(led / "l7.jsonl")
    l9 = _load(led / "l9.jsonl")
    safety = _load(led / "safety-log.jsonl")

    # gate: verdict histogram + top deny rules (payload inspection working?)
    verdicts = Counter(r.get("verdict") for r in l2)
    denies = Counter(r.get("rule_id") for r in l2 if r.get("verdict") == "deny")
    permit = verdicts.get("permit", 0)
    gate = {"total": len(l2), "verdicts": dict(verdicts),
            "permit_pct": round(100 * permit / len(l2)) if l2 else None,
            "top_deny": denies.most_common(5)}

    # acceptance / initiative — AGGREGATE ONLY (never per-principal)
    endors = [r for r in l8 if r.get("signal_type") == "endorsement"]
    rejects = [r for r in l8 if r.get("signal_type") == "rejection"]
    auth_accepts = [r for r in endors if r.get("attribution") == "principal_authenticated"]
    # real rolling 7-day floor (honest: NOT cumulative) from the latest L8 ts
    week = None
    if l8:
        latest = max((r.get("ts", "") for r in l8), default="")
        if latest:
            since = (datetime.fromisoformat(latest.replace("Z", "+00:00")) - timedelta(days=7)
                     ).isoformat().replace("+00:00", "Z")
            wk, _ = measurement.weekly_accepted(led, since_iso=since)
            week = wk
    accept = {"endorsements": len(endors), "rejections": len(rejects),
              "principal_accepted": len(auth_accepts),
              "floor_7d": week, "floor_met": (week is not None and week >= 3)}

    # skill quality — per-skill dict {skill_id: {n, mean_score, versions}} (safe surface)
    skills = skilldash.render_skill_dashboard(l7).get("per_skill", {}) if l7 else {}

    # envelope levels (per category), breaker, safety
    env = None
    ep = _envelope_path(led)
    if ep.exists():
        try:
            env = json.loads(ep.read_text()).get("levels")
        except (ValueError, OSError):
            env = None
    bp = _breaker_path(led)
    breaker = "closed"
    if bp.exists():
        try:
            breaker = json.loads(bp.read_text()).get("state", "closed")
        except (ValueError, OSError):
            breaker = "unreadable"
    safe = safety[-1] if safety else None

    # chain integrity across every ledger
    chains = {}
    for f in sorted(led.glob("*.jsonl")):
        try:
            chains[f.name] = hashchain.verify(f)
        except Exception as e:  # noqa: BLE001
            chains[f.name] = f"BROKEN: {e}"

    return {
        "ledger_dir": str(led), "gate": gate, "accept": accept, "skills": skills,
        "envelope": env, "breaker": breaker, "safety": safe, "deletions": len(l9),
        "chains": chains,
        "volumes": {f.name: len(_load(f)) for f in sorted(led.glob("*.jsonl"))},
    }


def render_text(h):
    L = []
    L.append(f"Team OS — system health  (live from {h['ledger_dir']})")
    L.append("")
    bk = h["breaker"]
    L.append(f"  breaker:   {'OPEN — side-effects HALTED' if bk == 'open' else bk}")
    g = h["gate"]
    if g["total"]:
        vh = " ".join(f"{k} {v}" for k, v in sorted(g["verdicts"].items()))
        L.append(f"  gate:      {g['total']} decisions · {g['permit_pct']}% permit · [{vh}]")
        if g["top_deny"]:
            L.append("             denied: " + ", ".join(f"{r}×{n}" for r, n in g["top_deny"]))
    else:
        L.append("  gate:      no decisions recorded yet")
    a = h["accept"]
    floor = "—" if a["floor_7d"] is None else f"{a['floor_7d']} ({'MET' if a['floor_met'] else 'below floor 3'})"
    L.append(f"  accept:    {a['principal_accepted']} authenticated ✓ · {a['rejections']} ✗ · "
             f"initiative floor (7d): {floor}")
    if h["envelope"]:
        L.append("  envelope:  " + ", ".join(f"{c}={lv}" for c, lv in h["envelope"].items()))
    else:
        L.append("  envelope:  unconfigured")
    if h["safety"]:
        s = h["safety"]
        L.append(f"  safety:    {s.get('status')}" + (f" — breaches {s.get('breaches')}" if s.get("breaches") else ""))
    L.append(f"  deletions: {h['deletions']} erasure event(s)")
    if h["skills"]:
        L.append("  skills (per-skill quality):")
        for sid, st in list(h["skills"].items())[:8]:
            L.append(f"             {sid} v{st['versions'][-1]}: mean {st['mean_score']} (n={st['n']})")
    bad = [n for n, v in h["chains"].items() if not isinstance(v, int)]
    L.append(f"  integrity: {'ALL chains verify' if not bad else 'BROKEN: ' + ', '.join(bad)} "
             f"({len(h['chains'])} ledgers)")
    return "\n".join(L)


def render_html(h, generated_at):
    def esc(s):
        return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    g, a = h["gate"], h["accept"]
    bk = h["breaker"]
    bk_ok = bk == "closed"
    # gate verdict bar
    order = [("permit", "var(--good)"), ("ask", "var(--warn)"), ("deny", "var(--bad)")]
    total = g["total"] or 1
    seg = "".join(
        f'<span style="width:{100*g["verdicts"].get(k,0)/total:.1f}%;background:{c}"></span>'
        for k, c in order)
    skills_rows = "".join(
        f"<tr><td>{esc(sid)}</td><td>v{esc(st['versions'][-1])}</td>"
        f"<td class='num'>{esc(st['mean_score'])}</td></tr>"
        for sid, st in list(h["skills"].items())[:12]) or "<tr><td colspan=3 class='muted'>no L7 scores yet</td></tr>"
    env = ("".join(f"<span class='chip'>{esc(c)} {esc(lv)}</span>" for c, lv in h["envelope"].items())
           if h["envelope"] else "<span class='muted'>unconfigured</span>")
    chains_bad = [n for n, v in h["chains"].items() if not isinstance(v, int)]
    floor_txt = "—" if a["floor_7d"] is None else str(a["floor_7d"])
    safety = h["safety"] or {}
    return f"""<!doctype html><html><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>Team OS — health</title><style>
:root{{--bg:#0d1117;--card:#161b22;--line:#232b34;--ink:#e6edf3;--mut:#8b949e;
--good:#3fb950;--warn:#d29922;--bad:#f85149;--acc:#e3a34b}}
@media(prefers-color-scheme:light){{:root{{--bg:#f6f8fa;--card:#fff;--line:#d0d7de;--ink:#1f2328;--mut:#636c76}}}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);
font:14px/1.5 ui-monospace,Menlo,Consolas,monospace;padding:24px}}
.wrap{{max-width:820px;margin:0 auto}}h1{{font-size:1.2rem;margin:0 0 2px}}
.sub{{color:var(--mut);margin:0 0 18px;font-size:.8rem}}
.tiles{{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:14px}}
.tile{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px}}
.tile .k{{color:var(--mut);font-size:.62rem;letter-spacing:.08em;text-transform:uppercase}}
.tile .v{{font-size:1.3rem;font-weight:600;margin-top:3px}}
.card{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px;margin-bottom:12px}}
.card h2{{font-size:.7rem;letter-spacing:.1em;text-transform:uppercase;color:var(--mut);margin:0 0 10px}}
.bar{{display:flex;height:14px;border-radius:7px;overflow:hidden;background:var(--line)}}
.bar span{{display:block}}
table{{width:100%;border-collapse:collapse}}td{{padding:4px 8px;border-bottom:1px solid var(--line)}}
.num{{text-align:right;font-variant-numeric:tabular-nums}}.muted{{color:var(--mut)}}
.chip{{display:inline-block;border:1px solid var(--line);border-radius:6px;padding:2px 7px;margin:2px}}
.ok{{color:var(--good)}}.bad{{color:var(--bad)}}.warn{{color:var(--warn)}}
.legend{{color:var(--mut);font-size:.7rem;margin-top:6px}}
footer{{color:var(--mut);font-size:.68rem;margin-top:14px;border-top:1px solid var(--line);padding-top:10px}}
</style></head><body><div class=wrap>
<h1>Team OS — system health</h1>
<p class=sub>live from {esc(h['ledger_dir'])} · generated {esc(generated_at)}</p>
<div class=tiles>
  <div class=tile><div class=k>Breaker</div><div class="v {'ok' if bk_ok else 'bad'}">{esc(bk).upper()}</div></div>
  <div class=tile><div class=k>Gate permit</div><div class=v>{g['permit_pct'] if g['permit_pct'] is not None else '—'}%</div></div>
  <div class=tile><div class=k>Initiative floor 7d</div><div class="v {'ok' if a['floor_met'] else 'warn'}">{floor_txt}</div></div>
  <div class=tile><div class=k>Chains</div><div class="v {'ok' if not chains_bad else 'bad'}">{'OK' if not chains_bad else str(len(chains_bad))+' BROKEN'}</div></div>
</div>
<div class=card><h2>Gate decisions ({g['total']})</h2>
  <div class=bar>{seg}</div>
  <div class=legend><span class=ok>■</span> permit {g['verdicts'].get('permit',0)} &nbsp;
    <span class=warn>■</span> ask {g['verdicts'].get('ask',0)} &nbsp;
    <span class=bad>■</span> deny {g['verdicts'].get('deny',0)}
    {'· denied: '+esc(', '.join(f'{r}×{n}' for r,n in g['top_deny'])) if g['top_deny'] else ''}</div></div>
<div class=card><h2>Acceptance (aggregate — never per-person)</h2>
  {a['principal_accepted']} authenticated ✓ &nbsp; {a['rejections']} ✗ &nbsp;
  initiative floor (rolling 7d): <b class="{'ok' if a['floor_met'] else 'warn'}">{floor_txt}</b> / 3</div>
<div class=card><h2>Envelope (earned autonomy)</h2>{env}</div>
<div class=card><h2>Skill quality (per-skill)</h2>
  <table><tr><td class=muted>skill</td><td class=muted>ver</td><td class="num muted">score</td></tr>{skills_rows}</table></div>
<div class=card><h2>Safety &amp; deletion</h2>
  safety: <b>{esc(safety.get('status','—'))}</b>{(' · breaches '+esc(safety.get('breaches'))) if safety.get('breaches') else ''}
  &nbsp;·&nbsp; deletions: {h['deletions']} erasure event(s)</div>
<footer>Per-skill, never per-person · reads real hash-chained ledgers · deterministic, no model.
Chain integrity: {'all verify' if not chains_bad else 'BROKEN: '+esc(', '.join(chains_bad))}.</footer>
</div></body></html>"""
