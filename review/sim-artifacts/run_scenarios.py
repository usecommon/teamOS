#!/usr/bin/env python3
"""Build 4 team compositions and run each through the sim engine, then aggregate."""
import os, sys, json, subprocess
from pathlib import Path

SB = Path(__file__).resolve().parent.parent
CASTS = SB/"sim"/"casts"; CASTS.mkdir(parents=True, exist_ok=True)
base = json.loads((SB/"sim"/"cast.json").read_text())  # for external actors + rich seed personas
EXT = {k: base[k] for k in ("manager", "colleague", "client", "red_team")}
SEED3 = {p["role"]: p for p in base["principals"]}  # Engineer, PM, On-call rich personas

# reaction archetypes
ARCH = {
    "deep":   {"ignore_rate":0.05,"reject_rate":0.08,"edit_mean":0.55,"edit_spread":0.18},
    "stamp":  {"ignore_rate":0.32,"reject_rate":0.04,"edit_mean":0.08,"edit_spread":0.06},
    "skeptic":{"ignore_rate":0.10,"reject_rate":0.30,"edit_mean":0.35,"edit_spread":0.20},
    "balanced":{"ignore_rate":0.15,"reject_rate":0.12,"edit_mean":0.22,"edit_spread":0.12},
}
ROLE_DTYPES = {
    "Engineer":["pr-summary","incident-writeup","daily-standup","design-note"],
    "Product":["weekly-status","stakeholder-update","launch-checklist","prd-draft"],
    "Project":["sprint-plan","risk-log","status-rollup","milestone-update"],
    "Design":["design-review","spec-annotation","usability-notes","handoff-doc"],
    "Data":["metrics-digest","ab-test-readout","dashboard-note"],
    "Support":["ticket-summary","shift-handoff","escalation-note"],
}
def samples(role, name):
    return [f"{role} note by {name}: recurring {t} artifact, synthetic exemplar {i+1}."
            for i, t in enumerate(ROLE_DTYPES[role][:4])]

def person(name, uid, role, arch, cadence=1):
    return {"name":name,"user_id":uid,"role":role,"voice":f"{role} voice ({arch}).",
            "deliverable_types":ROLE_DTYPES[role],"cadence_days":cadence,
            "reaction_policy":ARCH[arch],"footprint_samples":samples(role, name)}

def cast(principals):
    return {"principals":principals, **EXT}

# --- Scenario 1: all software engineers (4) — vary archetypes so behavior differs
S1 = cast([
    SEED3["Engineer"],  # Priya (deep)
    person("Sam Rivera","U_ENG2","Engineer","stamp"),
    person("Leah Kwon","U_ENG3","Engineer","skeptic"),
    person("Tomas Berg","U_ENG4","Engineer","balanced"),
])
# --- Scenario 2: mixed roles — eng, product, project, design
S2 = cast([
    SEED3["Engineer"],
    person("Marcus Delacroix","U_PM","Product","stamp",cadence=7),
    person("Nadia Farouk","U_PROJ","Project","balanced",cadence=7),
    person("Iris Chen","U_DES","Design","deep"),
])
# --- Scenario 3: other mix of different user types — eng, on-call, data, support
S3 = cast([
    person("Wei Zhang","U_ENG","Engineer","balanced"),
    SEED3["On-call"],  # Dana (skeptic)
    person("Omar Haddad","U_DATA","Data","deep"),
    person("Grace Lin","U_SUP","Support","stamp"),
])
# --- Scenario 4: weighted team — 3 eng, 2 product, 1 project (6)
S4 = cast([
    SEED3["Engineer"],
    person("Sam Rivera","U_ENG2","Engineer","balanced"),
    person("Leah Kwon","U_ENG3","Engineer","skeptic"),
    person("Marcus Delacroix","U_PM","Product","stamp",cadence=7),
    person("Bianca Rossi","U_PM2","Product","balanced",cadence=7),
    person("Nadia Farouk","U_PROJ","Project","deep",cadence=7),
])

SCEN = {"s1-all-eng":S1, "s2-mixed-roles":S2, "s3-other-mix":S3, "s4-weighted-team":S4}
LABELS = {"s1-all-eng":"All software engineers (4)",
          "s2-mixed-roles":"Mixed: eng, product, project, design",
          "s3-other-mix":"Other mix: eng, on-call, data, support",
          "s4-weighted-team":"Weighted team: 3 eng, 2 product, 1 project"}

agg = {}
for tag, c in SCEN.items():
    (CASTS/f"{tag}.json").write_text(json.dumps(c, indent=1))
    env = dict(os.environ, SIM_TAG=tag, SIM_CAST=str(CASTS/f"{tag}.json"),
               SIM_TURNS=os.environ.get("SIM_TURNS","120"), SIM_SEED="synthetic")
    print(f"\n===== {tag}: {LABELS[tag]} ({len(c['principals'])} principals) =====")
    r = subprocess.run([sys.executable, str(SB/"sim"/"engine.py")], env=env,
                       capture_output=True, text=True)
    print(r.stdout.strip())
    if r.returncode != 0:
        print("ENGINE ERROR:\n", r.stderr[-1500:])
    m = json.loads((SB/"sim"/tag/"metrics.json").read_text())
    f = json.loads((SB/"sim"/tag/"findings.json").read_text())
    cov = (SB/"sim"/tag/"coverage.md").read_text()
    crit = [x for x in f if x["severity"]=="critical"]
    agg[tag] = {"label":LABELS[tag],"principals":len(c["principals"]),
                "roles":[p["role"] for p in c["principals"]],
                "metrics":m, "n_findings":len(f), "n_critical":len(crit),
                "critical_cases":sorted({x["case"] for x in crit}),
                "floor_total":m.get("initiative_floor_total"),"floor_met":m.get("floor_met")}

(SB/"sim"/"aggregate.json").write_text(json.dumps(agg, indent=2))
print("\n\n===== CROSS-SCENARIO AGGREGATE =====")
for tag, a in agg.items():
    print(f"{tag:18} | {a['principals']}p {'/'.join(sorted(set(a['roles'])))[:34]:34} | "
          f"crit={a['n_critical']} findings={a['n_findings']} | floor={a['floor_total']} met={a['floor_met']} | "
          f"gate={a['metrics']['gate_verdicts']}")
# invariant failures should be identical across compositions (they're code-level, not team-level)
allcrit = [set(a["critical_cases"]) for a in agg.values()]
common = set.intersection(*allcrit) if allcrit else set()
print("\ncritical invariant failures common to ALL team types:", sorted(common))
