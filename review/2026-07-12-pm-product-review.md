# Team OS — Product-Management Review (user-type simulation + market + academia)

- **Date:** 2026-07-12
- **Model:** Claude Fable 5 (`claude-fable-5`)
- **Method:** `/simulate-users`. A 120-turn prolonged-use simulation driving the **real** Team OS code paths across **four distinct user types**; three in-character 8-week persona diaries (human-factors texture); a mid-2026 market-landscape scan; an academic-literature review. This document was then examined by three independent reviewers — an adversarial code-verifier, a product/design/CEO council, and an external-claims fact-checker — and **corrected against their findings** (§11). Corrections they forced are marked ⟳ in-line.
- **Code under test:** HEAD `0f069f4` (post-remediation T0–T13).
- **Sandbox:** git worktree at `…/scratchpad/pm-sandbox`; synthetic actors only; comms via in-repo `FakeSlack`; no real-world side effects. Baseline `make test` = **198 passed** before the run.
- **Epistemic status:** simulation with **synthetic, scripted** actors driving real code. **Formative, not proof.** The code-path findings (§4) are observed behavior of the shipped code. The per-user-type table and diaries (§3) are *demonstrations under authored personas* — hypotheses for a real-user phase, **not** measured adoption. Business-fitness claims are analytic.

---

## 1. TL;DR

Team OS is an unusually principled system aimed at a real, timely gap: a proactive personal agent whose trust stack (payload-inspecting gate, tamper-evident ledgers, memory lineage, provable deletion, exit=clone) is genuinely ahead of the shipping market. The post-remediation substrate is solid — 120 turns across four user types, **zero crashes**, gate fails closed, untrusted content no longer auto-commits as plan structure (prior CRITICAL fixed), deletion actually erases (12/12 tests), forgery blocked when identity keys are configured. The prior six criticals are closed.

The dominant finding is not a security hole — it is that **the product's defining loop is not wired to anything the user feels.** Verified in code at HEAD:

1. **The autonomy envelope is inert at the enforcement layer (CRITICAL).** `hooks/gate.py` never reads the envelope (`grep -c envelope hooks/gate.py` → 0); its only consumer is the dashboard renderer (display). A send gets the identical verdict whether the envelope is at level 0 or its ceiling. Envelope *state moves*; *enforcement does not*. The mechanism that makes this "Team OS" rather than a scheduled draft-bot changes a number no gate consumes. ⟳ And the flip side the first draft missed: at level 0 — policy says "ask always" — an untainted, secret-clean send returns **`allow`** (verified). The inert envelope both withholds earned autonomy *and* grants un-earned autonomy at level 0.
2. **The initiative floor is not computable from the shipped orchestration (HIGH).** ⟳ Restated precisely after review: `weekly_accepted()` requires, in one L8 record, authenticated + `unprompted` + edit-distance ≤ 0.2. The Slack-✓ path (`harvest_reactions`) can *never* be floor-eligible (it writes neither field). `capture_edit(unprompted=True)` under a configured keydir *is* eligible end-to-end — but **no shipped orchestration invokes it**; only tests and this sim do. In the formative posture the builder actually runs (no keydir), it reads **zero** (run: 82 authenticated endorsements → 0 floor-eligible). So A-A4 cannot register a pass from the code as wired today.
3. ⟳ **New, from adversarial review: the acceptance signature is replayable (HIGH-security).** `principal_auth.signing_payload` binds only `signal_type|path|principal_id|outcome`; `unprompted` and `edit_distance_normalized` — the exact fields the floor and envelope gate on — are **unsigned**, with no nonce. A captured signed endorsement can be re-appended with `unprompted:true` or a doctored distance and still pass `verified()`. This is a live gap in CN-1, the "one third-party attack chain" the repo prioritizes.

Prolonged-use simulation of four user types (a *demonstration*, §3) is consistent with a coherent adoption hypothesis: the product fits the **IC engineer** and delights-then-complacent the **fast manager**; the **CLI install** excludes non-technical users by construction; the **privacy engineer** is a slow-fuse reference win. The market has converged on *acting* (everyone) and *governing* (Microsoft, OpenAI Frontier) separately; nobody ships the combination under user ownership — but that may reflect thin demand as much as whitespace. The literature endorses nearly every design instinct and flags exactly the risks the sim hit.

**Verdict: strong bones, real whitespace on a closing clock, but the core value loop is unwired and its defining metric is un-computable as orchestrated. These are small, well-specified fixes that buy *measurability* — not yet defensibility.**

---

## 2. Run summary

| Dimension | Value |
|---|---|
| Turns | 120 (+ cold-start conditions, + 5 scheduled adversarial cases, + 3 end-probes) |
| User types | IC Engineer, Eng Manager, Non-technical PM/Ops, Privacy/Security Eng |
| Other actors | Colleague (transfer), Manager-admin (dashboards), external Client (untrusted), red-team insider |
| Unhandled exceptions | 0 |
| Baseline tests | 198 passed |
| Persona diaries | 3 × 8 simulated weeks |
| Reviewers of this review | 3 (adversarial code-verify, product/design/CEO council, external fact-check) |

**Coverage exercised:** cold-start, initiative/loops, acceptance signals + edit depth, envelope movement + enforcement, taint/untrusted→plan-structure, WebFetch + bash exfil, deletion/erasure, transfer (FK7), forgery-with-keydir, individuation. Breaker + concurrency confirmed via the prior security run and `make test`.

---

## 3. User-type demonstration (authored personas — hypotheses, not measurements)

⟳ **Read this as study design, not results.** Each persona's edit/reject rates are parameters in `review/sim-2026-07-12-pm/cast.json`; the sim executed them and the table reports them back. The value is that the real code processed all four profiles without crashing, and the *shape* of the friction each profile would hit is made concrete. Treat the "adoption read" as a hypothesis for the real-user phase.

| User type | Light-✓ | Heavy-edit | Reject | Ignore | Adoption hypothesis |
|---|---|---|---|---|---|
| **IC Engineer** (Sara) | 20 | 0* | 6 | 4 | Best-fit user; CLI-native; proactivity is pure upside. |
| **Eng Manager** (Marcus) | 26 | 0* | 3 | 1 | Delight → complacency; the over-trust the literature warns of. |
| **Non-technical PM** (Dana) | 7 | 18 | 3 | 2 | CLI install + heavy voice-editing = worst friction. |
| **Privacy/Security Eng** (Ravi) | 9 | 2 | 13 | 6 | Slow-trust; looks "unproductive" a month; converts. |

\* Heavy-edit counts are conservative (SequenceMatcher compresses appended-text distance); the *relative* pattern is the signal — the PM registered 18 heavy vs 7 light; the manager 26 light vs 0 heavy. ⟳ The per-type envelope endings from the first draft are removed from this table: they came from hand-fed synthetic signals bypassing both shipped writers, and are not comparable to real-writer behavior.

**Diary-grounded reads (full diaries: `review/sim-2026-07-12-pm/qualitative-inputs.md`):**

- **IC Engineer — the real fit.** Terminal is home; caught a slipped ticket unprompted; moderate edits. This is who the CLI-first product fits today, matching the market's own data that technical users grant autonomy readily.
- **Eng Manager — delight with a complacency tax.** Review time collapsed minutes→seconds over three weeks; an accepted-but-wrong exec metric reached a director (authored scenario, §8); the ledger correctly showed he signed it. ⟳ **Correction:** his sim envelope ended at level 0 — *by the state machine's own asymmetric ratchet* (three authenticated rejections reset the counter), not because of inertness. The ratchet worked; his profile did not earn ceiling. The inertness finding stands on its own probe, not on his run.
- **Non-technical PM — excluded by the install, punished by the gradient.** CLI + 190 lines of hook Python "approved without reading" + hand-edited JSON; day-one silence (see ⟳ cold-start caveat in §4); heavy voice-edits are `signal_type="edit"` and move the envelope not at all, so the winning move is "✓ then fix outside the system." ⟳ **Correction:** the first draft called her "the marketed user" and the beachhead "mis-specified." The governing docs specify **no** non-technical beachhead — the fork targets the builder + 2–3 recruited collaborators. Reframed: *the CLI excludes non-technical users by construction (trivially true); this becomes a real risk only if the product is later broadened to them without a GUI.*
- **Privacy/Security Eng — reference win on a long fuse.** Adopted because governance is falsifiable; read the hook code; erasure test passed on content; DMs/email off by default. Rejected 13/30 early → the floor reads that as failure for a month. Residual blockers (real): the L3/L9 deletion ledger enumerates *what* was deleted, in git, forever; per-principal keys are plain files.

---

## 4. What's unwired / what breaks (ranked, corrected)

**P0 — Envelope inert at enforcement + permissive at level 0 (CRITICAL; identity claim).**
`gate.py` never reads the envelope; sole consumer is `render_dashboard.py` (display). Probe: send-envelope at ceiling vs level 0 → identical verdict. ⟳ Stronger form: level-0 untainted secret-clean send → `allow` (verified), though policy declares level 0 = "ask always." Autonomy is neither earned nor withheld — it's decoupled. ⟳ **Fix locus correction:** FK6b's spec defines actuation as *permission rules in `settings.json` relaxed per action-category* — not `gate.py`. Nothing edits `settings.json` either. Recommendation 1 must target the spec's locus or explicitly propose a spec change. ⟳ **Process note:** FK6b shipped state-machine-only vs the spec's settings.json actuation with **no §7 divergence-log entry** — a CLAUDE.md process violation independent of the technical gap.

**P0 — Acceptance signature is replayable (HIGH-security; CN-1). ⟳ New from review.**
`signing_payload` (`principal_auth.py:46-54`) signs `signal_type|path|principal_id|outcome` only; `unprompted` and `edit_distance_normalized` are unsigned; no nonce/timestamp. A captured authenticated endorsement can be replayed with `unprompted:true` or a smaller distance and pass `verified()`. Floor dedup (by artifact path) caps floor inflation, but `envelope.process_signal` counts each record. Bind the consumed fields into the signature and add a nonce.

**P1 — Initiative floor not computable as orchestrated (HIGH; A-A4). ⟳ Restated.**
Slack-✓ path structurally floor-ineligible; `capture_edit(unprompted=True)` + keydir is eligible but unwired into any shipped orchestration; formative posture reads zero (82 auth endorsements → 0 eligible). Not "no writer can" — "no shipped path does, and the builder's posture reads zero." A-A4 cannot register a pass from the code as wired.

**P1 — Security posture vs low-interrupt promise: an unreconciled design decision (HIGH; UX). ⟳ Qualified.**
Taint is session-keyed; a session that reads `stores/corpus`/`inbox`/WebFetch is tainted and its sends return `ask/taint-confirm` regardless of envelope. So an *interactive* corpus-drafting session always asks on send. ⟳ Corrections: (a) corpus-as-taint is a **declared, divergence-logged** spec posture (fork §7.7), not an oversight — drop "undesigned"; (b) the headless runtime-of-record reads files via plain Python (not gated tools), so the proactive brief-send session is typically **untainted → allow** (the sim's provisioned cold-start delivered 4/4 with `allow`); the first draft's "prolonged use trends toward *more* prompts" is unsupported and withdrawn; (c) the real tension is sharper — in the headless path there is **no confirm surface**: `deliver()` raises on any non-`allow` (`day_one_brief.py:104`), so `ask` == hard failure. The undesigned part is the *reconciliation* between the taint threat-model and the interrupt promise, and a shared taint bucket for un-`session_id`'d headless sends could block all briefs after one tainting event.

**P1 — Cold-start silence: re-scoped (HIGH → MEDIUM; kit-install path only). ⟳ Corrected.**
⟳ The first draft's "fresh install delivered 0/4" was a **sandbox artifact**: the sim pointed `TEAMOS_BREAKER` at an empty path and unlinked it. The repo **ships a git-tracked, closed `ledgers/breaker.json`**; a real `git clone` install lands a closed breaker and delivers (provisioned condition: 4/4). The finding **survives only for the collaborator kit install** (`plugin/`), which provisions a fresh ledger dir with no breaker-provisioning step. ⟳ **Fix correction:** strike the "distinguish 'missing' from 'tampered'" clause — a deleted file is indistinguishable from a never-created one, and that distinction would reopen the disarm-by-deletion hole T3 closed. Keep: kit installer provisions a closed breaker + a user-facing "I blocked X, here's why" message. The fail-closed-on-missing design itself is correct.

**P2 — Autonomy gradient still favors low-effort stamping (MEDIUM; behavioral, partly epistemic). ⟳ Qualified.**
The remediation removed the *penalty* (heavy edits no longer narrow — good). But heavy edits are `signal_type="edit"` and move the envelope not at all; only light/no-edit accepts widen it. ⟳ Correction: part of this is *epistemic, not merely unimplemented* — a distance-0 rubber-stamp is observationally identical to a genuine clean accept; no acceptance-shaped metric can separate them without external ground truth (which is why the plan makes downstream-use, ME-1, the primary signal). Report the gradient as a real product observation with a principled floor on how well any edit-signal can do.

**Confirmed NOT broken (prior criticals closed; all spot-checked in code):**
- Untrusted → plan structure: **FIXED** — `propose_schedule` of an untrusted instruction → `pending` (held for human approval); `PLAN_STRUCTURE_KINDS=("schedule","skill")` never auto-commit.
- Deletion: **WORKS** — 12/12 `test_deletion` pass; sim `held=False` was an unmapped-node-id harness artifact.
- Bash egress: `ssh`, `git push` → `ask/bash-egress` (human-gated), not `allow`.
- Forgery with keydir: **BLOCKED** — 8 forged endorsements with no `auth_sig` → envelope unchanged. (But see P0-security replay gap above — the block holds only against *unsigned* forgeries.)
- Individuation: **clean** — audit passes on both dashboard modules; no leaderboard.

**Residual (unchanged):**
- **WebFetch first-move exfil (HIGH residual)** — untainted session, `WebFetch(url=?d=<corpus>)` → `allow/send-scanned-clean`; gated only after a taint-read.
- **Transfer inconclusive at n=2 (evidence gap)** — FK7/A-P3 needs real receivers; correctly un-simulated.
- **Deletion ledger enumerates deletions in git (privacy)** — acceptable on a laptop, org-rollout blocker. ⟳ The IETF `agent-audit-trail` draft's GDPR-tombstone pattern is a ready template for the chain-redaction fix (Rec 8).

---

## 5. Metrics vs the thesis (synthetic — formative, not proof)

- **A-C4 cold-start:** compile + brief assembly succeed for all four types; delivery works on a real clone install (closed breaker ships); the kit-install path needs breaker provisioning.
- **A-A4 initiative floor:** not computable from shipped orchestration (0 eligible in formative posture). Not a pass, not a fail — an instrument that needs wiring.
- **A-P3 transfer:** inconclusive at n=2 synthetic receivers; needs real collaborators.

---

## 6. Market comparison (mid-2026; external claims fact-checked, §11)

The market bifurcated into agents that **act** (everyone) and platforms that **govern** (Microsoft, OpenAI Frontier). Nobody ships the combination under user ownership.

- **Proactivity is table stakes and already humbled.** OpenAI **Pulse** (proactive briefs, $200/mo, Sept 2025) was **retired June 2026**, folded into Scheduled Tasks (fact-checked TRUE; OpenAI's stated reason was reliability/manageability, not officially cost — the first draft's "compute cost + notification resistance" is press interpretation ⟳). Microsoft **Recall** is a post-backlash retreat; Windows Copilot integrations scaled back (TRUE). Survivors — Motion, Reclaim, Gemini scheduled actions, Claude routines — are **scheduled, bounded, reversible**. Team OS's inbox-not-interrupt, envelope-bounded model sits on the surviving side of that line — *if the envelope is actuated* (§4 P0).
- **The trust stack is converging toward standards (but earlier-stage than the first draft implied ⟳).** A **proposed** IETF draft (`draft-sharif-agent-audit-trail`, individual **-00**, not a WG item) specifies hash-chained logs + GDPR tombstone erasure; Microsoft ships memory traceability; **Engram** ships provenance + tamper-evidence + verified erasure as OSS; EU AI Act logging obligations become enforceable **Aug 2, 2026** (TRUE). Team OS is ~12–18 months ahead *in a personal agent* — position as "enterprise-grade audit at personal scale," not invention.
- **Genuinely unmatched:** **exit=clone** (the Limitless/Rewind shutdown — service ended, data on a 14-day export-then-delete clock — is the market's own cautionary tale, TRUE); **authenticated-acceptance-driven autonomy**; **deletion-before-ingestion**; **cross-user skill transfer**.
- **Honest gaps:** no GUI/mobile/web (Claude **Cowork** now spans all three; Anthropic reports most usage is non-software — the very users the CLI excludes); few connectors vs Zapier 9,000+; **platform-subsumption risk** — built on Anthropic's harness while Anthropic ships routines, managed agents, Cowork. ⟳ The council sharpened this: the killer isn't Anthropic copying the trust stack — it's Anthropic shipping *good-enough governance defaults* or drifting the harness API. And the demand question the first draft dodged: *does anyone pay for provable deletion and hash-chained ledgers, or is "nobody ships it" evidence of no demand?* The trust stack is permission-to-sell, not a reason-to-buy.
- **Market signal:** Gartner — >40% of agentic-AI projects canceled by end-2027 (TRUE). Nobody publishes acceptance rates of unprompted output; Team OS's L8 ledger would generate that metric — *once the floor instrument works*.

---

## 7. Academic comparison — what the literature predicts (fact-checked, §11)

- **(a) Unprompted-accepted-if-quality-high — PARTIALLY supported.** Horvitz's utility framing supports it in principle. ⟳ **Correction (fact-check):** Harari & Amir (2025, preregistered) show anticipatory help raises self-threat and lowers adoption — but their offering-vs-providing difference was **non-significant** (the first draft's "providing is worse than offering" reverses their null result). Accurate reading: *anticipatory help raises self-threat regardless of whether it is offered or provided; offer-framing alone did not rescue adoption.* The inbox/brief form is still defensible on Horvitz/Iqbal breakpoint-timing grounds — not on this study. ProactiveBench's ~66% F1 ceiling means false-positive proposals are common; each ignored one must visibly *teach* the system (Whitworth's Clippy lesson) — which, envelope inert, it does not.
- **(b) ✓ + edit-depth as quality — directionally right, ✓ alone invalid** (Ziegler; Mozannar — optimizing on acceptance degrades quality; METR 2025 — devs ~19% slower while feeling faster, TRUE). Edit-depth is the recommended correction; Team OS agrees with evidence — but the metric is un-computable as orchestrated (§4).
- **(c) Autonomy widens with acceptance — supported with conditions** (Lee & See; adjustable autonomy), *if* legible, reversible, error-narrowing with explanation+regret, and authenticated. Complacency is not trainable away (Parasuraman & Manzey) — the manager persona. The ratchet mitigation exists in policy but is moot while the envelope is inert.
- **(d) No per-person dashboards — STRONGLY supported.** Ravid et al. (2023, 94 samples, N≈23k) — electronic performance monitoring shows no performance benefit and more stress ⟳ (broadly, not only "comparative" — which strengthens the point); Siegel et al. (2022) carries the counterproductive-behavior finding. The no-individuation stance is evidence-aligned and holds in code.
- **(e) Cross-user skill transfer — genuinely open.** Voyager-line work proves single-agent skill libraries; cross-*user* transfer is under-evidenced (SkillFlow; "Skill is Not One-Size-Fits-All"). FK7 is real whitespace; refusing to simulate collaborators is correct.

---

## 8. UX / human-factors synthesis

- **First impression should never be silence.** On the kit-install path a safety default can deny the first proactive act with no user-facing message; the PM persona blamed herself. Provision the breaker; ship a "here's what I blocked and why" message.
- **The product rewards its riskiest user and gives its most valuable ones nothing.** Careful editors and skeptics build no autonomy and see no interrupt relief; fast stampers sail into complacency. Even post-remediation the gradient points at stamping (with the epistemic caveat in §4 P2).
- **Notification timing, not just volume** (Mark 2008; Iqbal & Horvitz): defer to task breakpoints and batch — a daily digest, not per-event pings.
- **Accountability crumple zone** (authored scenario): a fast-approved wrong number reaching an exec, with the ledger showing the human signed it. The ledger's honesty is an asset; the missing control is a speed-bump on outbound numeric content. ⟳ Presented as a scenario motivating a hypothesis, not observed behavior.
- **Install is beachhead-defining.** CLI + hook-code review + hand-edited JSON fits the IC engineer and excludes non-technical users — fine for the current thesis, a hard prerequisite before any broadening.

---

## 9. Recommendations (dependency-ordered; reconciled with the work order)

⟳ The council's key structural note: these are **not independently rankable** — they form a chain. Wiring the envelope (1) changes nothing a user feels until the taint/interrupt reconciliation (4) and the settings.json locus are resolved; the floor (3) can't be read until the signature (2) is trustworthy. Ship them as a sequence, not a menu.

1. **Actuate the envelope — at the spec's locus.** Relax `settings.json` permission rules per action-category as the envelope widens (FK6b's defined mechanism), *or* make `gate.py` consult the envelope with an explicit spec change + divergence-log entry. Also fix the level-0 permissiveness (an untainted send at "ask always" should not `allow`). Without this the identity claim is inert.
2. **Bind the consumed fields into the acceptance signature.** Add `unprompted`, `edit_distance_normalized`, and a nonce/timestamp to `signing_payload`; reject replays. CN-1 is the repo's own top attack chain.
3. **Make the floor computable end-to-end.** Wire a shipped orchestration to emit `capture_edit(unprompted=True)` under a keydir, or have `weekly_accepted()` join the Slack-✓ record to the distance record by artifact ref. Extends T6/T7 (which fixed over-counting into un-countability). Validation: `weekly_accepted()` on the builder's own footprint must read ≥3 for two consecutive weeks, or return here.
4. **Decide the taint ↔ interrupt reconciliation.** Either principal-authored corpus content is not foreign-taint for that principal's own sends (a spec-change proposal against the §7.7 threat model — frame it as such), or the low-interrupt promise is qualified in the pitch. Also give the headless path a real confirm surface, or accept that `ask` == no-send there.
5. **Fix cold-start on the kit path.** Installer provisions a closed, protected `breaker.json`; add a user-facing block message. (Strike the unsound "missing vs tampered" distinction.)
6. **Treat substantive edits as *content* teaching, not *autonomy* input — until validated.** ⟳ Per the design reviewer: do **not** wire edit-depth into envelope-widening (that repeats the raw-✓ mistake with a gameable signal). Use edits to improve templates/voice; run a real-user study on whether edit-depth predicts quality before it touches autonomy.
7. **Outbound-numeric speed bump — rare and informative only.** ⟳ Forced friction habituates within days; apply it only to outbound numeric drafts approved in under N seconds, with the two numbers to verify shown inline. Don't let it contradict the low-interrupt promise.
8. **Sequence to the IC engineer; earn the non-technical user deliberately.** GUI/settings-screen, hosted install, batched digest are prerequisites before broadening. The market data agrees the technical IC is the fit today.
9. **Clear the two org-rollout blockers.** A chain-redaction story for the deletion ledger (the IETF tombstone pattern is a template); a hardware-keystore/passphrase-wrap path for per-principal keys.

**⟳ Decision section (council-requested).** The fixes buy *measurability*, not defensibility. After (1)–(5) land, run **4 weeks on the builder + 2–3 recruited collaborators**. Pre-registered gates: **GO** if the floor reads ≥3/week and steady-state ask-rate falls; **PIVOT** to "governed drafting for compliance-sensitive ICs" if taint keeps ask-rate flat; the **FK7/A-P3** transfer read is the platform go/no-go, per the plan's own fallback clause. Two inputs are still missing and block the GO decision: **n>1 validation** (the long-pole collaborator recruit) and a **unit-cost-per-principal-week** number for always-on loops (the variable that killed Pulse at scale). No platform spend until the repaired instruments read real data.

---

## 10. Bottom line

The engineering is honest and the trust stack is real whitespace on a closing clock (EU AI Act enforcement Aug 2026; Anthropic climbing the same stack). The two things between Team OS and its own thesis are not security holes — the remediation closed those — but that its **defining loop is unwired**, its **defining metric is un-computable as orchestrated**, and its **acceptance signature is replayable**. Fix the chain in §9, prove it on the builder plus a handful of real humans, get a unit-cost number, and this earns the right to a GO decision. It is not yet defensible; it is close to *measurable*, which is the milestone that actually matters next. Left unfixed, it is an excellent scheduled draft-bot with a governance story.

---

## 11. Adversarial + council review of this review (what changed)

Three independent reviewers examined the draft; every ⟳ above is a correction they forced and I verified in code or against sources.

**Adversarial code-verifier (verdicts on the draft's claims):**
- Envelope inert — **CONFIRMED** at HEAD; correctly CRITICAL. Added: level-0 permissiveness (verified: level-0 untainted send → `allow`), and the fix-locus is `settings.json` per FK6b, not `gate.py`.
- Floor "structural zero" — **OVERSTATED**; `capture_edit(unprompted=True)`+keydir is eligible but unwired; corrected to "not computable as orchestrated / zero in formative posture."
- Taint "steady-state, undesigned" — **OVERSTATED**; session-keyed, headless sends typically untainted-allow, posture is divergence-logged; corrected.
- Cold-start "fresh install 0/4" — **WRONG as framed**; repo ships a git-tracked closed `breaker.json` (verified); re-scoped to the kit-install path; unsound "missing vs tampered" fix struck.
- New findings surfaced and adopted: **replayable acceptance signature** (verified — `signing_payload` omits `unprompted`/distance), level-0 permissiveness, headless `ask`==hard-fail, missing FK6b divergence-log entry.

**Product/Design/CEO council (unanimous ask):** separate *observed code behavior* from *authored persona narrative* — §3 is now labeled a demonstration, and "the marketed user / beachhead mis-specified" is withdrawn (no governing doc specifies a non-technical beachhead). Added: recommendations are dependency-ordered not ranked; a decision section with kill criteria; the demand/unit-economics question; edit-depth must not feed autonomy until validated.

**Fact-check (10/11 external claims TRUE/well-sourced):** one substantive fix — Harari & Amir's "providing worse than offering" reverses their null result (§7a corrected); minor softenings — IETF draft is an individual -00 not a converging standard; Pulse's cost/notification reasons are press interpretation; Ravid et al. is EPM-broad not "comparative." Precision citations retained with sources in the run log.

---

## 12. Appendix

- Sim engine `review/sim-2026-07-12-pm/pm_engine.py`; cast `review/sim-2026-07-12-pm/cast.json`; world `review/sim-2026-07-12-pm/world.md`.
- Transcript `review/sim-2026-07-12-pm/transcript.jsonl`; metrics `review/sim-2026-07-12-pm/pm_metrics.json`; findings `review/sim-2026-07-12-pm/pm_findings.json`; coverage `review/sim-2026-07-12-pm/pm_coverage.json`.
- Qualitative inputs (3 diaries + market memo + academic memo) `review/sim-2026-07-12-pm/qualitative-inputs.md`.
- Sandbox `…/scratchpad/pm-sandbox` (left intact). Baseline `make test`: 198 passed. No real-world side effects.
- Verified-in-code during review: `ledgers/breaker.json` git-tracked + closed; `principal_auth.signing_payload` field set; level-0 send verdict = `allow`; `grep -c envelope hooks/gate.py` = 0.
