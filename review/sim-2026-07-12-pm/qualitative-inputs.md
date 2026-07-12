# Qualitative inputs to the PM review

Three prolonged-use persona diaries (8 simulated weeks each) and two research memos (market, academia) that fed the review. Personas are synthetic; diaries are role-played narrative, used for human-factors texture, not as measured data.

## Persona synthesis (full diaries in run log)

**Dana Okafor — Non-technical PM/Ops (marketed user, worst experience).**
Setup required a technical chaperone; "approved 190 lines of Python I couldn't read"; broke the JSON settings file twice. Day one: first brief silently blocked by the safety default — "the tool's first impression was silence, and I spent the day thinking I was the failure." Facts consistently right (caught a slipped Linear ticket unprompted) but voice wrong; heavy voice-edits read as low acceptance → more approval pings. Discovered the winning move is to ✓ then fix the doc outside the system ("lie to it"). Ended using it as a research assistant only — "maybe 30% of the promised value." What almost worked: the proactivity itself is real magic; facts reliable; approval-before-send is the right instinct — she wants the gate to *learn* from her edits.

**Marcus Feng — Eng Manager (delight → complacency).**
Deployed the kit himself in ~2h. Monday roundup 85% right, saved 45 min. 1:1 prep with pulled evidence = highest-ROI feature. Review time collapsed minutes→seconds over three weeks; the envelope widening "actively rewarded my inattention." Week 4: accepted-but-wrong exec metric (4.2 vs 2.8 deploys/day) reached a director; ledger showed he signed it, same minute, unedited — "I couldn't even be mad at the tool. It showed its work. I just didn't look." Wanted a per-report productivity leaderboard; refused by design; came around ("I've seen dashboards ruin teams"). Verdict: keeping it. Wants a speed-bump on sub-N-second approvals of outbound numbers, and to be shown his own complacency curve.

**Ravi Subramanian — Privacy/Security Eng (reference win, long fuse).**
Adopted because governance is falsifiable ("trust = verified, bounded, auditable, not believed"). Read the hook code before enabling; payload inspector caught his curl-exfil probe. DMs/email off by default, ledgered — glad. Daily ritual: git log the ledgers, diff corpus, spot-check lineage; found a memory write labeled `confidence:0.4`. Erasure test: content verifiably gone from store + rebuilt indexes. Rejected most proposals for a month → looked "unproductive," which he considers the correct curve. First AI assistant he'd trust with work data. Residual blockers: the L3/L9 deletion ledger enumerates *what* was deleted, in git, forever (metadata trail surviving the erasure); per-principal keys are plain files (no hardware keystore).

## Market memo (mid-2026) — headline points

- Proactivity went mainstream then got humbled: OpenAI **Pulse** sunset (cost + notification resistance); MS **Recall** internal failure; Windows Copilot integrations scaled back. Survivors (Motion, Reclaim, Gemini scheduled actions, Claude routines) are all **scheduled, bounded, reversible**.
- Trust stack is converging into standards: IETF `agent-audit-trail` draft (hash-chained logs + GDPR tombstones), MS memory traceability, **Engram** OSS (provenance + tamper-evident + verified erasure), EU AI Act logging enforcement Aug 2 2026. Team OS is ~12–18 months ahead in a *personal* agent, not a permanent moat.
- Genuinely unmatched: **exit=clone** (Limitless/Rewind shutdown is the cautionary tale), **authenticated-acceptance-driven autonomy**, **deletion-before-ingestion**, **cross-user skill transfer**.
- Gaps: no GUI/mobile/web (Claude **Cowork** now spans all three, >90% non-software usage); few connectors vs Zapier 9,000+; **platform-subsumption risk** (built on Anthropic's harness while Anthropic ships routines/Cowork); no social proof.
- Gartner: >40% agentic-AI projects canceled by end-2027. Nobody publishes acceptance rates of unprompted output — Team OS's L8 ledger would generate a metric the market lacks.

## Academic memo — what the literature predicts for the 5 bets

- (a) Unprompted-accepted-if-quality-high: **partial** — Horvitz supports in principle; Harari & Amir (2025) show anticipatory help raises self-threat independent of quality, providing worse than offering; ProactiveBench ~66% F1 ceiling → frequent false positives.
- (b) ✓+edit-depth as quality: **directionally right, ✓ alone invalid** (Ziegler; Mozannar — optimizing on acceptance degrades quality; METR 2025 — devs 19% slower while feeling faster).
- (c) Autonomy widens with acceptance: **supported with conditions** (Lee & See; adjustable autonomy) but complacency not trainable away (Parasuraman & Manzey); ratchet (slow-widen/fast-narrow) is the mitigation.
- (d) No per-person dashboards: **strongly supported** (Ravid et al. 2023, 94 studies; Siegel et al. 2022 — comparative monitoring adds stress, no benefit).
- (e) Cross-user skill transfer: **genuinely open** — Voyager proves single-agent skill libraries; cross-*user* transfer under-evidenced; FK7 is real whitespace.
