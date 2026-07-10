<!-- VERSION: v2.5 | 2026-07-10 | reference-only — outer map (superseded for execution by fork docs) | History: v1.0 created → v2.0 M2 dual paths, M6 console → v2.5 errata + FK mapping corrections + floor fix -->
**`v2.5 — 2026-07-10`** *(reference-only — outer map (superseded for execution by fork docs))*

# Team OS — Modular Build & Validation Roadmap
*Companion to the fork plan (team-os-fork-validation-plan.md) and mainline plan. **Errata: FK IDs in the fork plan override module placement wherever they disagree (e.g., FK3b sits at the M0/M1 seam; "Ledger-9 deletion" = FK3/C6).** This document re-cuts the work into MODULES: each is independently shippable, independently useful (stands alone even if the next module is never built), and validates a specific claim before the next is funded. Modules gate on evidence, not calendar. Every module writes mainline-schema ledgers so nothing is thrown away.*

---

## Design rules for modularity

1. **Each module delivers standalone value** — if you stopped after any module, what exists is still useful to its user. No module is pure scaffolding whose payoff is deferred.
2. **Each module validates one load-bearing claim** — with a go/no-go gate. A red gate stops or redirects; it does not get waved through.
3. **Modules stack, never fork the data** — later modules read earlier modules' stores; nothing is rebuilt.
4. **Value before governance, but never real-others'-data before protection** — the ordering law from remediation holds inside the modular cut.
5. **Initiative before interface** — the identity claim as a build constraint: proactive loops ship before the MCP door in every module where both appear.

---

## The seven modules (dependency-ordered)

```
M0 Ledgered Agent ──► M1 Job Compiler ──► M2 Proactive Loops ──► M3 The Door
   (works, recorded)   (knows your job)     (acts unasked)         (use anywhere)
                                                   │
                                                   ▼
                              M4 Two-Person Transfer ──► M5 Governed Sharing ──► M6 Fleet
                                 (learning moves)          (safe at scale)         (compounds)
```

Modules 0–3 are **single-user product** (validates: does a proactive personal agent deliver value?). Modules 4–6 are **Team OS proper** (validates: does learning compound across people under governance?). The seam between M3 and M4 is the honest decision point: **if M0–M3 delight and M4 fails, you have shipped an excellent proactive personal agent** — a real product, just not a Team OS. That is a good outcome discovered cheaply, not a failure.

---

## MODULE 0 — The Ledgered Agent
**Standalone value:** an agent that runs tasks with every action gated, recorded, and reversible — a *trustworthy* agent, usable by one person today.
**Validates:** the trust substrate works on borrowed runtime without eating the value (R18/FR2 — hooks are a sufficient, unbypassable gate).
**Build (fork FK1–FK2; FK3b + FK4-pre land at the M0/M1 seam):** adapter module; pre-tool-use hook = gate + Ledger 2; transcript→Ledger 1 compiler; edit-diff→Ledger 8; git=Ledger 6; hash-chaining; threat-model-lite + lawful-basis note.
**Gate G0:** a scripted session runs fully gated + ledgered; hook-bypass probe fails to find an ungated path; overhead < 10%. **Red = the fork can't make trust claims → gates move to a proxy layer or the vehicle is wrong.**
**Ships to:** you. **Effort:** small (days).

## MODULE 1 — The Job Compiler
**Standalone value:** point it at your history; it hands back a map of your recurring work + a first draft of one deliverable "built from your last N." Useful even with zero further automation — it's a mirror of your job.
**Validates the #2 assumption (R2):** jobs are compilable from artifact history.
**Build (fork FK3 + FK3b + FK4):** Ledger-9 deletion first (gates ingestion); compilation skill → job graph + profile/voice + pre-built skills; distill-then-discard; imperative-content quarantine; Claude Code footprint import.
**Gate G1 (thesis gate A-C2/A-C4):** on your real footprint, ≥3 genuine recurring tasks found with correct sources; first draft rated "recognizably mine"; injection fixture quarantined; deletion verified. **Red = zero-training cold start is wrong → revisit §11; the product reverts to observe-and-propose.**
**Ships to:** you (+ anyone who'll grant a footprint). **Effort:** medium — this is the module with the most novel risk.

## MODULE 2 — Proactive Loops
**Standalone value:** the deliverables now arrive *unasked* — the Thursday doc drafts itself on Thursday, the morning digest is waiting. This is the first module where the identity claim is visible: the agent works while you don't.
**Validates the production-as-eval thesis (A-A4)** and the initiative floor (FR6).
**Build (fork FK5–FK6, FK6b; FK6c kit+door follows the loops):** Day One Brief as a scheduled headless run; Class A loops on cron/launchd; scoring→Ledger 7; weekly pulse instrument; checkpoint-file shim; envelope-by-script.
**Two delivery paths for the loops:** (a) *self-hosted* — cron/launchd on the always-on box (needs owned inference: API key or local model); (b) *subscription-scheduled (low-friction)* — ship the loops as **scheduled-task templates inside the Team OS plugin** (fork §9), run on Anthropic's cloud on the user's subscription, no daemon, no always-on machine, no API key. Path (b) is likely the real M2-for-normal-people; requires the stores reachable as a remote connector (not local-only).
**Gate G2 (thesis gate):** 4 weeks unattended; edit-distance/acceptance correlate with the pulse (estimate-with-interval); **initiative floor: ≥3 accepted unprompted deliverables/week (per FR6's absolute-floor definition — not a ratio)**; checkpoint shim loses no work across restarts. **Red on A-A4 = production isn't a usable eval → pillar 3 has no signal. Red on FR6 = drifted into a memory product → re-sequence.**
**Ships to:** you, as a daily-driver. **Effort:** medium.

**★ Milestone: end of M2 = a complete, validated, single-user proactive agent.** Everything above is a shippable product on its own. M3 makes it reachable; M4+ make it a Team OS.

## MODULE 3 — The Door (MCP)
**Standalone value:** turn the agent on inside Claude (and ChatGPT) — query your corpus, check what the loops produced, from any client, any device, including mobile.
**Validates:** the sidecar-brain thesis — that Team OS is usable *through* existing clients with no new interface (and the multi-vendor claim).
**Build (fork FK6c):** stateless MCP server over the M0–M2 stores; `propose_*` → proposals inbox, never the corpus; OAuth per principal; read tools carry readOnlyHint; `propose_*` writes route through the M0 gate (semi-trusted taint tier); thin cloud relay if self-hosted.
**Gate G3:** connector toggles on in claude.ai + ChatGPT; reads work; a write proposal lands in the gate queue (never direct); relay holds no state. **Red = the door leaks state or bypasses gates → it's a second brain, redesign.**
**Ships to:** anyone with a Claude/ChatGPT account (the distribution wedge). **Effort:** small-medium.

**★ Milestone: end of M3 = shippable single-user product with distribution.** This is the honest "real product" line. Fund M4 only if M0–M3 earned it.

## MODULE 4 — Two-Person Transfer
**Standalone value:** a second person's agent benefits from a skill the first person's agent proved — the first tangible "we, not me" moment.
**Validates the pillar-3 thesis (A-P3) — the whitespace claim.**
**Prerequisite (fork FK2.5 / FK7-pre — BEFORE any second person's data):** per-principal encryption, keys out of shared repo; access self-ledgering; no individuation surface. **Recruit the 2–3 collaborators during M0, not now — the long pole.**
**Build (fork FK7):** shared skills repo; PR promotion gate (CI = PII scan + eval floor + signing-lite); staggered adoption cohorts.
**Gate G4 (terminal thesis gate):** a skill improvement proven on agent A produces a measured positive delta on agent B (estimate-with-interval, honest about n). **Red = pillar 3 is false → you have an excellent personal agent (M0–M3), not a Team OS. Decision made before any platform spend.**
**Ships to:** a 2–3 person pilot cell. **Effort:** medium + the human cost of recruitment.

## MODULE 5 — Governed Sharing
**Standalone value:** knowledge flows across the pilot group *safely* — the corpus grows, third parties are protected, deletion works across people.
**Validates:** the governance holds when real multi-person data moves (the councils' central concern).
**Build:** full sharing gates 0–5 + Gate 3.5 signing/sandbox; third-party data-subject rights surface (V1); CI flow map (V2); ledger minimization (V3); coercion-resistance battery (V5); taint at multi-user volume.
**Gate G5:** an independent (pre-registered) attempt to leak sensitive lineage across a boundary fails; a colleague DSAR round-trips; rug-pull fixture caught by sandbox. **Red = governance is theater at scale → do not widen past the pilot cell.**
**Ships to:** the pilot cell, now trustworthy enough to widen. **Effort:** medium-large — this is where most remediation items land.

## MODULE 6 — The Fleet
**Standalone value:** the system gets measurably better across everyone as anyone uses it — role templates provision new people fast; structural insights surface; the loop compounds.
**Validates:** the compounding claim + external validity (A-Z1).
**Build:** Tier-3 pooled learning (DP epsilon budget, secure aggregation, V4); role templates + guild curation; structural-insight proposals routed to affected teams first; detection/IR + fleet-freeze; **operator console (S9 — fleet/security/compliance ops, structural-absence-audited); ownerless agent members (S10)**; the managed-tier trust battery if productizing.
**Gate G6 (A-Z1, terminal external gate):** a team *not containing the builder* adopts and retains 60 days; individuation provably impossible; pooled outputs resist re-identification. **Red = internal gates measured the wrong thing → re-examine the eval philosophy itself.**
**Ships to:** first real external team / managed-tier GA. **Effort:** large — this is the platform.

---

## Modularity properties (why this cut is honest)

- **Every ★ milestone is a stopping point with a shipped artifact** — M2 (proactive agent), M3 (+ distribution), M6 (Team OS). You can raise money, recruit, or quit at any of the three with something real in hand.
- **The riskiest thesis is validated third, not last** — A-P3 (G4) is the make-or-break, and the modular cut reaches it after only M0–M3 of build, so the R1 "personal agent vs. Team OS" decision is made on ~40% of the total effort, not 100%.
- **Governance tracks data reality** — modules touching only your data (M0–M3) carry lite governance; the module introducing a second person (M4) is *preceded* by its protection prerequisite; the module moving real shared data (M5) carries the full council remediation. No protection is built before it's needed, none after.
- **Initiative precedes interface everywhere** — M2 (loops) ships before M3 (door). The identity claim is enforced by sequence.
- **Each gate maps to a register row** — G0→R18/FR2, G1→R2, G2→R3/FR6, G4→R1, G6→A-Z1 — so a red gate has a pre-written "if false" consequence; nothing fails ambiguously.

## Recruitment (the one non-code critical path)
The 2–3 collaborators gate G4 and cannot be simulated (sims verify F-tests, never A-tests). **Start recruiting at M0.** Best source: co-builders on a shared side project (real overlapping work). They sign the M1 data notice before any footprint flows and the M4 prerequisite protects them before any shared-scope flow. If recruitment stalls, M0–M3 still ship as the single-user product — recruitment gates the *Team OS* claim, not the *product*.

## One-line summary
**Build a trustworthy agent (M0), teach it your job (M1), let it work unasked (M2), reach it anywhere (M3) — that's a product; then prove learning transfers (M4), make it safe across people (M5), and let it compound (M6) — that's Team OS. Stop at any star with something shipped.**
