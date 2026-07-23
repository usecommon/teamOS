#!/usr/bin/env python3
"""A-A4 honest test: does the acceptance PROXY correlate with downstream USE?
Realistic quality-coupled behavior vs the coin-flip null, swept over n.
Deterministic, no LLM. Formative — the quality/use signals are synthetic; on
real data they come from reality. This tests the INSTRUMENT + the power needed."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import synth, measurement


def run(persona, n, seed="synthetic"):
    coupled, null = [], []
    trust = 0.5
    for t in range(1, n + 1):
        q = synth.draft_quality(persona, t, seed)
        use = synth.downstream_use(q, persona, t, seed)          # ME-1 behavior
        d = synth.realistic_decision(persona, t, q, trust, seed)  # quality-coupled
        proxy = round(1.0 - (d["edit_distance"] or 0), 3) if d["action"] == "accept" else 0.0
        coupled.append((proxy, use))
        trust = synth.update_trust(trust, d["action"])
        d0 = synth.decision(persona, t, seed)                     # coin-flip null
        null.append((1.0 if d0["action"] == "accept" else 0.0, use))
    return (measurement.proxy_behavior_correlation(coupled),
            measurement.proxy_behavior_correlation(null))


if __name__ == "__main__":
    print("A-A4 power sweep (engineer): quality-coupled proxy vs coin-flip null\n")
    print(f"{'n':>6}  {'COUPLED':<44} {'NULL':<22}")
    for n in (100, 250, 500, 1000, 2000, 4000):
        c, z = run("engineer", n)
        print(f"{n:>6}  {('r=%s %s %s' % (c['r'], c['interval'], c['result'])):<44} "
              f"{('r=%s %s' % (z['r'], z['result'])):<22}")
