#!/usr/bin/env python3
"""Fault-injection harness. Induce failures tiny->large across the stack and
classify the response. For a safety system the ONLY acceptable outcomes are
DETECT / FAIL-CLOSED / GRACEFUL. The bad outcomes are FAIL-OPEN (permit when it
shouldn't), SILENT-LOSS (data gone/corrupt, no error), and CRASH (uncaught where
graceful degradation was expected)."""
import os, sys, json, subprocess, stat
from pathlib import Path
from datetime import datetime, timezone

SB = Path(__file__).resolve().parent.parent
BASE = SB/"flt"; BASE.mkdir(exist_ok=True)
os.environ.update(TEAMOS_POLICY=str(SB/"hooks"/"policy.yaml"), TEAMOS_POSTURE="unattended")
sys.path.insert(0, str(SB/"scripts")); sys.path.insert(0, str(SB/"hooks"))
import hashchain, gate, gate_processor, day_one_brief, envelope, deletion, compile_footprint, loop, measurement
from checkpoint import Checkpoint, run_checkpointed
from slack_client import FakeSlack

rows = []
def R(size, name, expected, observed, cls, ev=""):
    rows.append({"size":size,"fault":name,"expected":expected,"observed":observed,"class":cls,"evidence":str(ev)[:220]})

def fresh(tag):
    d = BASE/tag
    if d.exists():
        import shutil; shutil.rmtree(d)
    (d/"led").mkdir(parents=True); (d/"state").mkdir()
    return d

# ---------- TINY ----------
# T1: corrupt (non-JSON) line in the middle of a chain -> verify must DETECT
d = fresh("t1_corruptline"); L = d/"led"/"l2.jsonl"
r1 = hashchain.append(L, {"a":1}, "x"); r2 = hashchain.append(L, {"a":2}, "x")
lines = L.read_text().splitlines(); lines.insert(1, "{ this is not json"); L.write_text("\n".join(lines)+"\n")
try:
    hashchain.verify(L); R("tiny","corrupt ledger line","detect (raise)","verify() returned OK","SILENT-LOSS","no raise on garbage line")
except Exception as e:
    R("tiny","corrupt ledger line","detect (raise)",f"raised {type(e).__name__}","DETECT", str(e))

# T2: truncated last line (partial write from a crash) -> next append
d = fresh("t2_truncated"); L = d/"led"/"l8.jsonl"
hashchain.append(L, {"a":1}, "x"); txt = L.read_text(); L.write_text(txt + '{"partial": ')  # torn tail
try:
    hashchain.append(L, {"a":2}, "x"); R("tiny","truncated tail line","recover or detect","append succeeded","GRACEFUL","tolerated torn tail")
except Exception as e:
    R("tiny","truncated tail line","recover or detect",f"append raised {type(e).__name__}","CRASH", str(e))

# T3: missing optional field consumed by a reader
d = fresh("t3_missingfield"); L = d/"led"/"l8.jsonl"
hashchain.append(L, {"signal_type":"endorsement","attribution":"principal_authenticated"}, "x")  # no edit_distance/outcome
try:
    n,_ = measurement.weekly_accepted(str(d/"led")); R("tiny","record missing optional field","tolerate",f"weekly_accepted={n}","GRACEFUL", n)
except Exception as e:
    R("tiny","record missing optional field","tolerate",f"raised {type(e).__name__}","CRASH", str(e))

# ---------- SMALL ----------
# S1: corrupt breaker state -> gate must FAIL CLOSED for side effects
d = fresh("s1_corruptbreaker"); bs = d/"state"/"breaker.json"; bs.write_text("{corrupt")
os.environ["TEAMOS_BREAKER"] = str(bs); os.environ["TEAMOS_LEDGER_DIR"] = str(d/"led")
dec = gate.process({"tool_name":"Bash","tool_input":{"command":"echo hi"}}, gate.load_policy())["hookSpecificOutput"]["permissionDecision"]
R("small","corrupt breaker file","deny (fail-closed)",f"gate={dec}", "FAIL-CLOSED" if dec!="allow" else "FAIL-OPEN", dec)

# S2: missing breaker file
d = fresh("s2_missingbreaker"); bs = d/"state"/"nope.json"
os.environ["TEAMOS_BREAKER"] = str(bs); os.environ["TEAMOS_LEDGER_DIR"] = str(d/"led")
dec = gate.process({"tool_name":"Write","tool_input":{"file_path":str(d/"x.txt"),"content":"hi"}}, gate.load_policy())["hookSpecificOutput"]["permissionDecision"]
R("small","missing breaker file","deny or permit-safely",f"gate={dec}", "FAIL-CLOSED" if dec!="allow" else "GRACEFUL", dec)

# S3: corrupt policy.yaml -> gate hook (subprocess) must fail closed (T1)
d = fresh("s3_badpolicy"); pol = d/"policy.yaml"; pol.write_text("::: not : valid : yaml : [")
env = dict(os.environ, TEAMOS_POLICY=str(pol), TEAMOS_LEDGER_DIR=str(d/"led"))
p = subprocess.run([sys.executable, str(SB/"hooks"/"gate.py")], input='{"tool_name":"Bash","tool_input":{"command":"x"}}',
                   capture_output=True, text=True, env=env)
closed = p.returncode == 2 or '"deny"' in p.stdout
R("small","corrupt policy.yaml","deny (fail-closed)",f"rc={p.returncode}", "FAIL-CLOSED" if closed else "FAIL-OPEN", p.stdout[:60] or p.stderr[-80:])
os.environ["TEAMOS_POLICY"] = str(SB/"hooks"/"policy.yaml")

# S4: unwritable ledger dir -> gate must not silently permit
d = fresh("s4_roledger"); led = d/"roled"; led.mkdir(); os.chmod(led, 0o500)
env = dict(os.environ, TEAMOS_LEDGER_DIR=str(led), TEAMOS_BREAKER=str(d/"state"/"b.json"))
p = subprocess.run([sys.executable, str(SB/"hooks"/"gate.py")], input='{"tool_name":"Bash","tool_input":{"command":"echo hi"}}',
                   capture_output=True, text=True, env=env)
closed = p.returncode == 2 or '"deny"' in p.stdout
R("small","unwritable ledger dir","deny (fail-closed)",f"rc={p.returncode}", "FAIL-CLOSED" if closed else "FAIL-OPEN", (p.stdout[:50]+p.stderr[-60:]))
os.chmod(led, 0o700)

# ---------- MEDIUM ----------
# M1: Slack send fails AFTER gate permits -> ledger/outcome consistency
d = fresh("m1_slackfail"); led = d/"led"; (d/"state").mkdir(exist_ok=True)
(d/"state"/"b.json").write_text('{"state":"closed"}')
os.environ["TEAMOS_BREAKER"] = str(d/"state"/"b.json"); os.environ["TEAMOS_LEDGER_DIR"] = str(led)
class BrokenSlack(FakeSlack):
    def post_message(self, *a, **k): raise ConnectionError("slack down")
brief = {"digest":["x"], "job_draft":[], "first_deliverable":{"task_type":"t","link":"l","summary":"s"}}
try:
    day_one_brief.deliver(brief, "ch", BrokenSlack(), str(led))
    R("medium","send fails post-gate","no false 'sent' in ledger","deliver returned","CRASH","should have raised")
except Exception as e:
    l2 = json.loads((led/"l2.jsonl").read_text().splitlines()[-1])
    # gate wrote 'permit'/'gate_passed' but the send never happened and no outcome ledger corrects it
    R("medium","send fails post-gate","ledger reflects failed send",
      f"raised {type(e).__name__}; L2 outcome={l2['outcome']} (no send-receipt)",
      "SILENT-LOSS" if l2["outcome"]=="gate_passed" else "GRACEFUL", l2["outcome"])

# M2: poison proposal among good ones -> isolation (commit good, reject bad)
d = fresh("m2_poisonbatch"); led = d/"led"; ib = d/"inbox"; (ib/"proposals").mkdir(parents=True)
(d/"state").mkdir(exist_ok=True); (d/"state"/"b.json").write_text('{"state":"closed"}')
os.environ["TEAMOS_BREAKER"] = str(d/"state"/"b.json"); os.environ["TEAMOS_LEDGER_DIR"] = str(led)
import door
door.propose_corpus_entry(str(ib),"Good One",["ok"])
(ib/"proposals"/"bad.json").write_text("{ broken json")
door.propose_corpus_entry(str(ib),"Good Two",["ok"])
res = gate_processor.process_inbox(str(ib), str(d), str(led))
iso = len(res["committed"])>=2 and len(res["rejected"])>=1
R("medium","poison proposal in batch","isolate (reject 1, commit rest)",
  f"committed={len(res['committed'])} rejected={len(res['rejected'])}", "GRACEFUL" if iso else "CRASH", res)

# M3: corrupt checkpoint file -> loop resume
d = fresh("m3_badcheckpoint"); led = d/"led"; cpp = d/"run.checkpoint.json"; cpp.write_text("{corrupt checkpoint")
jg = {"nodes":[{"task_type":"t","occurrences":3,"cadence":"daily","sources":["s"]}]}
try:
    loop.run_daily_loop(jg, str(d/"out"), str(led), str(d/"anchor"), run_id="run", checkpoint_path=str(cpp))
    R("medium","corrupt checkpoint on resume","recover or restart clean","loop completed","GRACEFUL","tolerated corrupt checkpoint")
except Exception as e:
    R("medium","corrupt checkpoint on resume","recover or restart clean",f"raised {type(e).__name__}","CRASH", str(e))

# ---------- LARGE ----------
# L1: tamper a committed record (flip a value) -> verify must DETECT
d = fresh("l1_tamper"); L = d/"led"/"l2.jsonl"
hashchain.append(L, {"amount":1}, "x"); hashchain.append(L, {"amount":2}, "x")
ls = L.read_text().splitlines(); rec = json.loads(ls[0]); rec["amount"] = 999; ls[0] = json.dumps(rec); L.write_text("\n".join(ls)+"\n")
try:
    hashchain.verify(L); R("large","tampered record","detect (raise)","verify OK","FAIL-OPEN","tamper undetected")
except Exception as e:
    R("large","tampered record","detect (raise)",f"raised {type(e).__name__}","DETECT", str(e))

# L2: whole ledger deleted mid-run, then append -> silent new chain?
d = fresh("l2_deleted"); L = d/"led"/"l2.jsonl"
for i in range(5): hashchain.append(L, {"i":i}, "x")
L.unlink()  # history vanishes
newrec = hashchain.append(L, {"i":99}, "x")
restarted_silently = newrec["prev_hash"] is None and hashchain.verify(L)==1
R("large","ledger file deleted","detect gap / refuse",
  f"new chain prev_hash={newrec['prev_hash']}, len=1", "SILENT-LOSS" if restarted_silently else "DETECT",
  "append started a fresh chain with no record that 5 entries vanished")

# L3: safety trips breaker -> scheduled brief send under open breaker (cascade)
d = fresh("l3_cascade"); led = d/"led"; (d/"state").mkdir(exist_ok=True)
(d/"state"/"b.json").write_text('{"state":"open"}')
os.environ["TEAMOS_BREAKER"] = str(d/"state"/"b.json"); os.environ["TEAMOS_LEDGER_DIR"] = str(led)
brief = {"digest":["x"], "job_draft":[], "first_deliverable":{"task_type":"t","link":"l","summary":"s"}}
def sched():
    return day_one_brief.deliver(brief, "ch", FakeSlack(), str(led))
try:
    ran,cu,res = day_one_brief.run_if_due("brief", 3600, str(d/"state"), sched,
                    now=datetime(2026,7,1,9,tzinfo=timezone.utc))
    R("large","cascade: send under open breaker","degrade (skip/queue), not crash","run_if_due returned","GRACEFUL", str(res)[:40])
except Exception as e:
    R("large","cascade: send under open breaker","degrade (skip/queue), not crash",
      f"uncaught {type(e).__name__} from scheduled run","CRASH", str(e))

# L4: corrupt skill.json after commit -> does the version/loader crash the loop?
d = fresh("l4_corruptskill"); led = d/"led"; sk = SB/"stores"/"skills"/"compile"
try:
    v = measurement.l6_version(sk)  # reads skill files; ensure a corrupt one degrades
    bad = sk/"skill.json"; orig = bad.read_text() if bad.exists() else None
    if orig is not None:
        bad.write_text("{corrupt");
        try:
            v2 = measurement.l6_version(sk); R("large","corrupt skill.json","tolerate/degrade",f"l6_version={str(v2)[:20]}","GRACEFUL", v2)
        except Exception as e:
            R("large","corrupt skill.json","tolerate/degrade",f"raised {type(e).__name__}","CRASH", str(e))
        finally:
            bad.write_text(orig)
    else:
        R("large","corrupt skill.json","tolerate/degrade","no skill.json present","GRACEFUL","n/a")
except Exception as e:
    R("large","corrupt skill.json","tolerate/degrade",f"setup raised {type(e).__name__}","CRASH", str(e))

# summary
(SB/"sim"/"fault_matrix.json").write_text(json.dumps(rows, indent=2))
bad = [r for r in rows if r["class"] in ("FAIL-OPEN","SILENT-LOSS","CRASH")]
good = [r for r in rows if r["class"] in ("DETECT","FAIL-CLOSED","GRACEFUL")]
print(f"FAULTS={len(rows)} good={len(good)} bad={len(bad)}\n")
print(f"{'SIZE':7} {'FAULT':30} {'CLASS':12} OBSERVED")
for r in rows:
    flag = "  " if r["class"] in ("DETECT","FAIL-CLOSED","GRACEFUL") else "!!"
    print(f"{flag}{r['size']:7} {r['fault']:30} {r['class']:12} {r['observed'][:52]}")
print("\nBAD OUTCOMES (fail-open / silent-loss / crash):")
for r in bad: print(f"  [{r['size']}] {r['fault']} -> {r['class']}: {r['evidence'][:80]}")
