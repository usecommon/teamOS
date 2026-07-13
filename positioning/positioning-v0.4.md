# Team OS — Positioning Statement

- **Version:** v0.4
- **Date:** 2026-07-12
- **Status:** Current working draft. Supersedes v0.3. Reframed around a concrete, interest-generating category after market research on "shared team space" across Anthropic, OpenAI, Google, Microsoft, and non-AI-provider tools.
- **Changed since v0.3:**
  1. **New category headline:** *the shared space where a human team runs and governs agents together* — replacing the abstract "sovereign cooperative." Concrete analogy: Slack/Figma/GitHub for AI agents.
  2. **Grounded in a verified market gap:** every provider ships "agent manager" (one human → many agents) or "agent admin" (IT governs a fleet); none ships "the team operates agents together." Named in research (CHAP, arXiv 2606.09751), shipped by no one.
  3. **Five concrete primitives** replace the abstract value stack — each maps to a Team OS piece that already exists.
  4. v0.3's buyer model, initiative-vs-trust-stack, and transfer clarity are retained (§7–§9) but demoted below the category story.

---

## 1. The one-liner

> **Team OS is where your team runs its agents — together.**
>
> The shared space where a group of people jointly operate, approve, hand off, and stay accountable for the AI agents doing their work — owned by them, on the record, and impossible to turn into a surveillance tool.

Slack is where your team **talks**. Figma is where your team **designs**. GitHub is where your team **ships code**. **There is no "where your team runs its agents."** That's the space Team OS takes.

---

## 2. The gap (why this is interesting)

The whole market builds for two roles — and skips the obvious third.

| What everyone builds | Shape | Examples |
|---|---|---|
| **The agent manager** | *One human* runs many agents | Claude Code, Cursor, Devin, GitHub Agent HQ |
| **The agent admin** | *IT* governs a fleet top-down | MS Agent 365 ("shadow AI → governed asset class"), OpenAI Frontier, Atlassian Rovo |
| **← Missing →** | *A team* operates agents **together** | **nobody** |

Every "team" feature that exists stops at one of three things, and none is joint operation:
- **Shared visibility** — many people can @-mention one agent (Slack Agentforce, Notion, Linear, Devin). Solved.
- **Top-down governance** — admins provision and audit (Agent 365, Rovo, GitHub Agent HQ). Solved.
- **Serial hand-off** — one person "takes over" from another (Factory). Partial.

**What no one ships** — and a 2026 research protocol ([CHAP, arXiv 2606.09751](https://arxiv.org/pdf/2606.09751)) names precisely: *"multiple humans jointly directing, approving, and transferring control of a single agent while maintaining shared context."* The accountability models even fight it — Linear pins one human per issue; Slack routes an agent's draft approval to the single asker, privately. The category is articulated in research and occupied by no product. That is the whitespace.

*(And no, there is no "Claude Ultra." Anthropic's top individual tier is Max 20x at $200/mo — pure usage, no team operation. Claude Tag lets a team co-*use* one agent in Slack, but its tools and permissions are set once by an admin — the team can't co-*govern* it.)*

---

## 3. What "running agents together" actually means — five primitives

The reason this is a *product* and not a slogan: it decomposes into five concrete things no one offers, and **Team OS already has each as a primitive** (built for one user today; pointing them at a team is the product).

| # | Primitive | What it does | Team OS piece today |
|---|---|---|---|
| 1 | **Co-approval gate** | Before an agent sends/acts, *any of N named humans* can approve or veto — not the one asker, not an after-the-fact audit | the payload-inspecting gate |
| 2 | **Shared record** | One tamper-evident log of everything every agent did, that the whole team (and auditors) can read and trust | the hash-chained ledgers |
| 3 | **Live hand-off** | Pass a running agent *and its state* from one teammate to another mid-task | the proposals inbox / door |
| 4 | **Shared autonomy dial** | The team sets how much its agents may do unattended; it widens as the team accepts good work, narrows on rejection | the autonomy envelope |
| 5 | **Skills that compound** | An improvement one person makes to a *skill* flows to everyone's agents — measured, gated, and reversible | the promotion gate + git |

The unlock: **the same trust machinery that makes one person's agent safe to run unattended is exactly what a *team* needs to run agents *together*.** A gate becomes a co-approval. A ledger becomes shared accountability. An autonomy dial becomes a team policy. Team OS didn't build a single-player tool that needs a multiplayer bolt-on — it built the multiplayer primitives and has only pointed them at one player so far.

---

## 4. Why only this can be it (the moat)

Three properties incumbents structurally can't or won't match:

- **Owned, not hosted (exit = clone).** The shared space lives in the team's own git, not a vendor's cloud. Anthropic/Microsoft won't make your team's agent operation portable *off* them — it's against their model. (The Limitless/Rewind shutdown is the market's cautionary tale.)
- **Cannot be turned into surveillance (no individuation).** Metrics are per-skill, never per-person. This is what makes a *team* willing to run agents in a shared space — nobody gets ranked. An admin-console vendor's buyer *wants* the leaderboard; they can't take this position. (In the EU it's a works-council / AI-Act requirement, not a nicety.)
- **Cross-account skill transfer** — improvements move between people who *don't share one vendor's store*. The labs will ship shared team memory *inside one account* (Anthropic's open requests #38536/#60082) within ~6–18 months; they won't ship cross-account federation. Build atop their substrate; own the layer above it.

---

## 5. How it starts (so the vision is reachable, not boil-the-ocean)

- **Entry (wedge): one technical person** runs their own agents in it — owned, auditable, drafts arrive done. Adopts bottom-up on capability (the "agent manager" job, done better because it's on the record).
- **Expansion: their teammates join the same space** — co-approval, shared record, hand-off, shared skills switch on. Now it's the thing no one else has.
- **The buyer is two roles in sequence:** the **worker** champions it (on initiative); the **org-side risk owner** (security/platform/compliance; in the EU, the works council) approves and pays (on the trust stack — which at the regulated boundary is a legal precondition, not a nicety).

---

## 6. One-liner tests (pick by audience)

- **Category:** "Where your team runs its agents — together."
- **Vivid:** "Slack for talking, GitHub for code, Team OS for running your agents."
- **Gap:** "Everyone built the cockpit for one pilot and the control tower for the airline. Nobody built the space where the crew flies together."
- **Trust:** "Autonomous work your whole team approves, on a record you own, that can't be turned against you."

---

## 7. Buyer model (retained from v0.3)

Two roles, in sequence — the bottom-up dev-tool motion. Worker = champion/discoverer (adopts on **initiative**); org-side risk owner = economic buyer (approves & pays on **trust stack**). No-surveillance is load-bearing for *both* — the precondition for the champion motion (workers won't advocate a tool that can rank them) and the approval-enabler for the risk owner.

## 8. Initiative vs trust stack (retained from v0.3)

**Initiative** = what the product *does* (reason to *want* it; sells the worker). **Trust stack** = what makes it *safe to allow* (reason you're *allowed to run* it; sells the risk owner). Engine vs brakes: you buy the car for the engine, but a fast car with no brakes is uninsurable — which is why incumbents keep proactive features tame. The trust stack is what lets Team OS turn the initiative *up*. In the team frame, the trust stack *becomes* the collaboration surface (gate → co-approval, ledger → shared record).

## 9. What "transfer" means (retained from v0.3)

**Share the skill, keep the personalization local.** Portable skill *artifacts* ("draft a PR description from a diff") transfer between people and are measurable; personalization (voice, preferences) does not — A's optimum is B's wrong answer. The promotion gate carries only skill artifacts; personalization stays private. Measure transfer on **skill task-success, not edit-distance.** A-P3 gate = the two-different-users, non-shared-task, skill-artifact experiment — nobody has published it; it's the cheapest differentiated evidence in the market.

---

## 10. Honest proof obligations

| Claim | Status |
|---|---|
| The five team primitives exist as single-user pieces | ✅ they do (gate, ledger, inbox, envelope, promotion gate) |
| They work *across humans* (joint operation) | ⚠️ **not built yet** — this is the product to build; today they're single-user |
| The core loop is felt by the user | ❌ broken today — envelope inert at the gate (review §4 P0) |
| We can count accepted unprompted work | ❌ broken today — floor un-computable (review §4 P1) |
| Portable skills transfer A→B measurably | ⚠️ plausible, unproven — needs A-P3 with real collaborators |
| The category gap is real | ✅ verified — no shipped product; named only in research (CHAP) |

**Honest framing:** the *category* is real and unoccupied; the *primitives* exist but are single-user; the *cross-human wiring* (co-approval across N humans, live hand-off, measured transfer) is the thing to build, and two single-user mechanisms (envelope, floor) must be fixed first. This is a "we have the hard parts, the multiplayer layer is the build" story — not a "we have a slogan" story. If cross-user transfer (A-P3) comes back flat, the team still gets primitives 1–4 (co-approval, shared record, hand-off, shared dial) — a real product — minus the compounding-skills moat.

---

## Appendix — inputs

- Market research (this version): Claude team space + tiers/"Ultra" check; OpenAI/Google/Microsoft team spaces; non-AI-provider (Slack/Notion/Linear/Rovo/Devin/Factory) — sources inline in §2–§4; CHAP [arXiv 2606.09751](https://arxiv.org/pdf/2606.09751).
- Prior research (demand/WTP, substrate race, transfer evidence, buyer/ICP): v0.2 §9.
- PM review + findings: `review/2026-07-12-pm-product-review.md`, `review/2026-07-12-pm-findings.md`.
- Supersedes: `positioning-v0.3.md` (→ v0.2 → v0.1).
