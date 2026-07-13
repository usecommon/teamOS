# Team OS — Positioning Statement

- **Version:** v0.6
- **Date:** 2026-07-12
- **Status:** Current working draft. Supersedes v0.5. Adds a competitive reckoning with **Hermes Agent** (Nous Research) — the strongest existing analog — which sharpens (narrows) the single-user wedge and explicitly cedes "capability" as contested ground.
- **Changed since v0.5:**
  1. **New §2 — competitive truth vs Hermes.** Hermes already ships the proactive, self-improving, self-hosted single-user agent (with autonomous skill generation Team OS only aspires to). Do not fight on capability.
  2. **Single-user wedge narrowed** (§1): the *uncontested* reason isn't "unattended work" (Hermes has that) — it's "unattended work you can **prove and answer for**, on data that matters." The beachhead single-user is the **governance-conscious technical user**, not the general IC.
  3. **Capability ceded, governance + team operation affirmed as the moat** — the two things Hermes structurally lacks and its anti-restriction brand won't let it build.

---

## 1. Why a single user adopts this (wedge — narrowed after the Hermes check)

Adoption is single-user → team → org, so this must answer "why would ONE person use this?" first. But the honest version now accounts for Hermes Agent, which *already* gives a single user a proactive, self-improving, self-hosted agent (§2). So the wedge is not "an agent that acts unattended" — that exists. It's:

> **The agent you can let off the leash *and prove exactly what it did* — safe to point at real, regulated, or shared data.**

The three single-user deltas, re-ranked for what's actually *uncontested*:

1. **Provable, answerable autonomy (the uncontested cold-start reason).** Not "it acts unattended" (Hermes does) — but "it acts unattended *and every move is on a tamper-evident record with lineage*, so when it's wrong you can reconstruct what it did and why, and when data must go it's provably erased." This is the reason a **governance-conscious user** starts — someone who *will not* run an ungoverned agent on real work data.
2. **Owned and un-takeable (retention).** Files in git, exit = clone; not stranded when a vendor sunsets. (Hermes shares this — self-hosted, MIT — so it's parity, not edge, at the single-user level.)
3. **Earned, calibrated autonomy (differentiation).** A graduated trust envelope, not a static toggle or endless confirmations.

**The beachhead single-user is specific:** the security/privacy/compliance-minded technical IC (the "Ravi" archetype) who can't run an unaudited agent on real data. To that person, an uncensored, unaudited, no-deletion agent isn't capable — it's *unusable*. The general capability-maximalist IC may prefer Hermes; that user is not the beachhead.

**Load-bearing tension (unchanged):** the mechanism behind "earned autonomy" (the envelope) is *inert at the gate today* (review §4 P0). Fixing it is priority zero — it's the single-user reason and the broken thing at once.

**Single-user headline:** *The proactive agent you can leave running — on data that matters — because every move is gated, on a record you own.*

---

## 2. Competitive truth: Hermes Agent (do not fight on capability)

**Hermes Agent** (Nous Research, open-sourced Feb 2026, MIT; ~214k GitHub stars, $50M Paradigm, $1B token valuation) is the closest existing analog and, on capability and momentum, **ahead of Team OS.** It ships:
- a **self-improving skill loop** — the agent autonomously writes its own reusable skill files (the thing Team OS only aspires to);
- persistent hierarchical memory, a cron scheduler for unprompted work, subagents, 40+ tools, six sandbox backends, many chat gateways;
- self-hosted, model-agnostic, single-curl install.

**This is the "everyone promises agency, few deliver" exception — Hermes delivers, for the single user.** So the honest strategic read:

| | **Hermes** | **Team OS** |
|---|---|---|
| Core bet | **Capability** — most autonomous, self-improving, unrestricted | **Governance** — most *trustworthy* autonomy |
| Safety | Capability *guardrails* (allowlist, sandbox, injection scan, undo) | Enforced *trust layer* (payload gate, tamper-evident ledger, lineage, provable deletion, envelope) |
| "What did it do & why?" | Not reconstructable — no audit ledger | Every action on a tamper-evident record |
| Provable deletion (GDPR) | Not documented | Designed invariant |
| Team model | Single-principal | Co-approval + shared record + governed transfer + no-individuation |
| Brand | **"Aligned to you, not corporate policy," uncensored** | Governance-first, regulator-legible |

**The tell is the last row.** Hermes's anti-restriction brand is catnip for the individual power-user and **disqualifying for the org-side risk owner.** They aim at opposite buyers, and *Hermes cannot pivot to Team OS's buyer without abandoning its identity.* Hermes validates the category (self-hosted, files-as-skills, proactive agents are real and adopted) while leaving the governed/team half wide open.

**Rules this sets:**
1. **Never compete on capability or momentum — you lose.** Cede it explicitly.
2. **Compete on provable governance + team operation** — Hermes structurally lacks both.
3. **One-liner:** *Hermes is the most capable agent you can run; Team OS is the most capable agent you can run **on data that matters and answer for afterward** — and the only one a team can run together.*

---

## 3. Where it goes: the shared space where a team runs its agents — together

The single user (governance-conscious) is the entry; the **category** is the destination and the uncontested ground.

> **Team OS is where your team runs its agents — together.**

Slack is where your team talks. Figma is where it designs. GitHub is where it ships code. **There is no "where your team runs its agents."** Hermes doesn't build it (single-principal, no governed transfer). Neither does anyone else.

Adoption path = strategy: **one governance-conscious user runs an agent they can prove (wedge) → teammates join the owned, on-the-record space (team) → the org standardizes (expansion).** The single-user trust machinery *is* the team collaboration surface — no rebuild.

---

## 4. The gap (why the team category is interesting)

| What everyone builds | Shape | Examples |
|---|---|---|
| **Agent manager** | *One human* runs many agents | Claude Code, Cursor, Devin, **Hermes** |
| **Agent admin** | *IT* governs a fleet top-down | MS Agent 365, OpenAI Frontier, Rovo |
| **← Missing →** | *A team* operates agents **together** | **nobody** |

Every "team" feature stops at shared visibility (@-mention one agent), top-down governance (admins provision/audit), or serial hand-off (Factory). **No one ships joint operation** — named in a 2026 research protocol ([CHAP, arXiv 2606.09751](https://arxiv.org/pdf/2606.09751)), shipped by no product. (No "Claude Ultra" exists; Anthropic's top individual tier is Max 20x/$200, usage-only; Claude Tag lets a team co-*use* one Slack agent, not co-*govern* it.)

---

## 5. The five team primitives (same machinery, pointed at a team)

| # | Primitive | What it does | Single-user piece today |
|---|---|---|---|
| 1 | **Co-approval gate** | Any of N humans approves/vetoes an action *before it fires* | the payload-inspecting gate |
| 2 | **Shared record** | One tamper-evident log of everything every agent did | the hash-chained ledgers |
| 3 | **Live hand-off** | Pass a running agent + its state between teammates | the proposals inbox / door |
| 4 | **Shared autonomy dial** | The team sets how much its agents may do unattended | the autonomy envelope |
| 5 | **Skills that compound** | One person's improvement flows to everyone's agents | the promotion gate + git |

**Unlock:** the same trust machinery that makes one agent safe to run unattended is exactly what a team needs to run agents together. Gate → co-approval; ledger → shared accountability; dial → team policy.

---

## 6. Why only this can be it (the moat)

- **Owned, not hosted (exit = clone).** Team's own git; labs won't make agent operation portable off them. (Parity with Hermes at single-user; edge is at team scale.)
- **Cannot become surveillance (no individuation).** Per-skill, never per-person — what lets a *team* run agents in a shared space; EU works-council / AI-Act requirement. Admin-console vendors' buyers *want* the leaderboard.
- **Cross-account skill transfer.** Improvements move between people who don't share one store. Labs ship shared memory *inside one account* (Anthropic #38536/#60082) in ~6–18mo; not cross-account. Hermes doesn't do it at all (single-principal). Build atop the substrate; own the layer above.

---

## 7. Buyer model (matches adoption path)

Worker = champion/discoverer (adopts on §1 — provable, answerable autonomy). Org-side risk owner = economic buyer (security/platform/compliance; EU works council; approves & pays on the trust stack — a legal precondition at the regulated boundary: EU AI Act Art. 12, GDPR). No-surveillance is load-bearing for both.

## 8. Initiative vs trust stack

**Initiative** = what it *does* (reason to want it; sells the worker). **Trust stack** = what makes it *safe to allow* (reason you're allowed to run it; sells the risk owner). Engine vs brakes. Against Hermes specifically: Hermes is engine-forward with light brakes; Team OS's brakes are the product — they're what let the initiative be turned up on data that matters, and what become the team collaboration surface.

## 9. What "transfer" means

**Share the skill, keep the personalization local.** Portable skill *artifacts* transfer between people and are measurable; personalization (voice/preferences) does not. Promotion gate carries only skill artifacts; measure transfer on **skill task-success, not edit-distance.** A-P3 = the two-user, non-shared-task, skill-artifact experiment; unpublished; cheapest differentiated evidence. (Note: Hermes ships single-agent self-improvement, but *not* cross-person transfer — that remains open.)

---

## 10. Honest proof obligations

| Claim | Status |
|---|---|
| A governance-conscious single user has a cold-start reason (provable unattended work) | ⚠️ reason is right; envelope inert (review §4 P0) — fix first |
| Owned record + exit=clone (single-user retention) | ✅ real today; parity with Hermes |
| We out-*capability* Hermes | ❌ no — cede it; compete on governance + team |
| The team category gap is real | ✅ verified; no shipped product (incl. Hermes); named only in research |
| The five primitives exist as single-user pieces | ✅ they do |
| They work across humans (joint operation) | ⚠️ not built — the multiplayer layer is the build |
| Portable skills transfer A→B measurably | ⚠️ plausible, unproven — A-P3 with real collaborators |

**Honest framing:** Hermes proves the capability half of the single-user category is delivered and moving fast. Team OS should not chase it. Its defensible ground is (a) *provable, answerable* single-user autonomy for the governance-conscious user, and (b) the team-operation layer no one — Hermes included — builds. Both depend on fixing the inert envelope first; the team layer and cross-user transfer are the build; A-P3 is the unproven moat. If A-P3 comes back flat, a governance-conscious single user still gets "the agent you can prove," and a team still gets co-approval + shared record + hand-off — minus the compounding-skills moat.

---

## 11. One-liner tests

- **Single user (governance-conscious):** "The proactive agent you can leave running — on data that matters." / "Autonomy you can answer for."
- **vs Hermes:** "Hermes is the most capable agent you can run; Team OS is the one you can run on data that matters and answer for — and the only one a team can run together."
- **Team category:** "Where your team runs its agents — together."
- **Gap:** "Everyone built the cockpit for one pilot and the control tower for the airline. Nobody built the space where the crew flies together."

---

## Appendix — inputs

- Hermes Agent research (this version): [github.com/nousresearch/hermes-agent](https://github.com/nousresearch/hermes-agent), [hermes-agent.nousresearch.com](https://hermes-agent.nousresearch.com/), [turingpost](https://www.turingpost.com/p/hermes), [bitcoin.com](https://news.bitcoin.com/what-is-hermes-agent-nous-researchs-self-improving-ai-explained/), [chaincatcher](https://www.chaincatcher.com/en/article/2257617).
- Market research (team spaces, tiers/"Ultra", CHAP): v0.4 §2–§4. Prior research (demand/WTP, substrate race, transfer, buyer/ICP): v0.2 §9.
- Adoption path single-user-first (memory: `adoption-single-user-first`). PM review: `review/2026-07-12-pm-product-review.md`.
- Supersedes: `positioning-v0.5.md` (→ v0.4 → v0.3 → v0.2 → v0.1).
