# Team OS — Positioning Statement

- **Version:** v0.7
- **Date:** 2026-07-12
- **Status:** Current working draft. Supersedes v0.6. Establishes the **layer** framing: Team OS is not a harness/agent — it is the trust-and-team **layer that sits on top of a harness** (Claude Code, Hermes, any MCP-capable runtime). Adds the distribution-vs-architecture strategy.
- **Changed since v0.6:**
  1. **New §1 — Team OS is a layer, not a harness.** It sits on top of both Claude Code *and* Hermes. This reframes Hermes from "competitor to cede capability to" → "runtime we ride and make answerable."
  2. **New §2 — distribution vs architecture:** weld to Claude for *distribution* ("add Team OS to Claude"); **harness-agnostic** by *architecture* (MCP door + the FR5 adapter seam). Any harness, any inference (subscription/API/local).
  3. **Two governance tiers made explicit:** full payload-gating on a hooked harness (Claude Code); door-scoped on MCP-only harnesses (Hermes, ChatGPT). Don't oversell "full governance everywhere."
  4. **Subsumption hedge named:** harness-agnostic is the survival architecture against the labs commoditizing the substrate.

---

## 1. What Team OS *is*: the layer above the harness

Team OS is **not** an agent and **not** a harness. Harnesses/runtimes — **Claude Code, Hermes Agent, Cursor, ChatGPT's agent mode** — are the engines that run models and dispatch tools. **Team OS is the trust-and-team layer that sits *on top of* a harness** and adds what none of them have: provable governance and joint team operation.

> **Team OS sits on top of both Claude Code and Hermes.** It doesn't compete with the runtime — it rides it and makes it answerable and shareable.

This is why the earlier "cede capability to Hermes" was half-wrong. The right move isn't to lose the capability race — it's to **not enter it**: run on top of the most capable runtime (whichever the user already has) and wrap it in the gate + ledger + team operation. *The most capable agent, made provable and shareable.*

**The seam already exists in the fork.** FR5 insulation mandates that **one adapter (FK1) is the only code touching harness internals** — the core (gate, ledger, envelope, transfer) is *already harness-independent by design*. Going multi-harness isn't a rewrite; it's a **second adapter** behind the same seam.

---

## 2. Distribution vs architecture (the strategy)

Two different bets, sequenced — not in tension:

- **Distribution: weld to Claude. "Install = add Team OS to Claude."** Piggyback Claude's install base, trust, and billing; no new runtime to sell. This is the FK6c kit (plugin + marketplace = a GitHub repo). It's the frictionless on-ramp *and* the one harness that supports the full trust stack today.
- **Architecture: harness-agnostic underneath.** The layer binds to any runtime via the **MCP door**, and to any inference source — **subscription, API, or local model** (the fork's own rule: "hooks fire locally, not who bills the tokens"). Open or closed, cloud or on-box.

**Two-line pitch:**
> **Entry:** "Add Team OS to Claude."
> **Ability:** "Team OS runs on any agent you already use — any harness, any model, your subscription or your API or your own hardware."

**The honest nuance — governance has two tiers by harness capability:**

| Tier | Requires | Governance strength | Harnesses today |
|---|---|---|---|
| **Full-trust** | Local hooks that fire on *every* tool call | Gate inspects every payload; ledger complete | **Claude Code** |
| **Door-scoped (reduced-trust, disclosed)** | Just MCP | Governs only Team OS door actions; the harness's *native* tools are ungoverned | **Hermes, ChatGPT, Cursor**, any MCP client |

So the precise claim is: **"Team OS reaches any harness via MCP, and delivers full provable governance on any harness that exposes hooks."** Don't flatten it to "full governance everywhere" — that oversells, and the honesty is the brand. (Inference-agnosticism — subscription/API/local — is clean and unqualified.)

---

## 3. Hermes: substrate *and* competitor (hold both)

Hermes Agent (Nous Research, open-source, ~214k stars, $50M Paradigm) is a **harness** — a model-agnostic agent runtime — not a model, not an assistant. Its relationship to Team OS is **both**:

- **As a runtime → a substrate Team OS sits on.** Ride its capability (self-improving skill loop, 40+ tools, six sandboxes); add the gate + ledger + team layer it lacks. Door-scoped governance via Hermes's MCP integration today; full if Hermes ever exposes hooks.
- **As an out-of-box product → a competitor only for the user who wants *no* governance.** Its brand is explicitly anti-restriction ("aligned to you, not corporate policy," uncensored) — which wins the individual power-user and is *disqualifying* for the org-side risk owner. Team OS is the mirror image; Hermes cannot pivot to Team OS's buyer without abandoning its identity.

**Net:** don't fight Hermes on capability — *sit on top of it.* It validates the category (self-hosted, files-as-skills, proactive agents are real and adopted) and leaves the governed/team half wide open.

---

## 4. Why a single user adopts this (wedge — narrowed to the governance-conscious user)

Adoption is single-user → team → org, so answer "why would ONE person use this?" first. Hermes already gives a single user a proactive, self-improving, self-hosted agent — so the wedge is not "an agent that acts unattended." It's:

> **The agent you can let off the leash *and prove exactly what it did* — safe to point at real, regulated, or shared data.**

Deltas, ranked by what's *uncontested*:
1. **Provable, answerable autonomy (the cold-start reason).** It acts unattended *and* every move is on a tamper-evident record with lineage; when it's wrong you can reconstruct why; when data must go, it's provably erased. The reason a **governance-conscious user** (the "Ravi" archetype) starts — someone who won't run an ungoverned agent on real work data.
2. **Owned and un-takeable (retention).** Files in git, exit = clone. (Parity with Hermes at single-user; edge is at team scale.)
3. **Earned, calibrated autonomy (differentiation).** A graduated trust envelope, not a static toggle.

**Load-bearing tension:** the envelope behind "earned autonomy" is *inert at the gate today* (review §4 P0). Fixing it is priority zero — it's the single-user reason and the broken thing at once.

**Single-user headline:** *The proactive agent you can leave running — on data that matters — because every move is gated, on a record you own.*

---

## 5. Where it goes: the shared space where a team runs its agents — together

Entry = one governance-conscious user; the **category** is the destination and the uncontested ground.

> **Team OS is where your team runs its agents — together.**

Slack is where your team talks. Figma is where it designs. GitHub is where it ships code. **There is no "where your team runs its agents."** No harness builds it (they're single-principal runtimes); no admin console builds it (top-down governance ≠ joint operation). Named in research ([CHAP, arXiv 2606.09751](https://arxiv.org/pdf/2606.09751)), shipped by no product.

Adoption path = strategy: **one governance-conscious user runs an agent they can prove (wedge) → teammates join the owned, on-the-record space (team) → the org standardizes (expansion).** The single-user trust machinery *is* the team collaboration surface — no rebuild.

---

## 6. The market gap

| What everyone builds | Shape | Examples |
|---|---|---|
| **Agent manager** | *One human* runs many agents | Claude Code, Cursor, Devin, **Hermes** |
| **Agent admin** | *IT* governs a fleet top-down | MS Agent 365, OpenAI Frontier, Rovo |
| **← Missing →** | *A team* operates agents **together** | **nobody** |

Every "team" feature stops at shared visibility (@-mention one agent), top-down governance, or serial hand-off (Factory take-over). No one ships **joint operation**. (No "Claude Ultra" exists; Anthropic's top individual tier is Max 20x/$200, usage-only; Claude Tag lets a team co-*use* one Slack agent, not co-*govern* it.)

---

## 7. The five team primitives (same machinery, pointed at a team)

| # | Primitive | What it does | Single-user piece today |
|---|---|---|---|
| 1 | **Co-approval gate** | Any of N humans approves/vetoes an action *before it fires* | the payload-inspecting gate |
| 2 | **Shared record** | One tamper-evident log of everything every agent did | the hash-chained ledgers |
| 3 | **Live hand-off** | Pass a running agent + its state between teammates | the proposals inbox / door |
| 4 | **Shared autonomy dial** | The team sets how much its agents may do unattended | the autonomy envelope |
| 5 | **Skills that compound** | One person's improvement flows to everyone's agents | the promotion gate + git |

**Unlock:** the same trust machinery that makes one agent safe to run unattended is exactly what a team needs to run agents together. Gate → co-approval; ledger → shared accountability; dial → team policy.

---

## 8. Why only this can be it (the moat)

- **Owned, not hosted (exit = clone).** Team's own git; the labs won't make agent operation portable off them.
- **Cannot become surveillance (no individuation).** Per-skill, never per-person — what lets a *team* run agents in a shared space; an EU works-council / AI-Act requirement. Admin-console vendors' buyers *want* the leaderboard.
- **Cross-account skill transfer.** Improvements move between people who don't share one store — labs ship shared memory *inside one account* (Anthropic #38536/#60082) in ~6–18mo, not cross-account; Hermes doesn't at all (single-principal).
- **Harness-agnostic = the subsumption hedge.** If welded only to Claude, Anthropic shipping team memory subsumes you. As the portable layer above the harness, you move to whatever runtime the customer uses and your value (governance + team operation) travels with you. Given the substrate race, this is survival architecture, not gold-plating.

---

## 9. Buyer model · initiative vs trust stack · transfer (retained)

- **Buyer = two roles in sequence.** Worker = champion (adopts on provable autonomy); org-side risk owner = economic buyer (approves/pays on the trust stack — a legal precondition at the regulated boundary: EU AI Act Art. 12, GDPR). No-surveillance is load-bearing for both.
- **Initiative vs trust stack.** Initiative = what it *does* (reason to want it; sells the worker). Trust stack = what makes it *safe to allow* (reason you're allowed to run it; sells the risk owner). Engine vs brakes; the brakes are what let the initiative be turned up on data that matters, and become the team collaboration surface.
- **Transfer.** Share the skill, keep the personalization local. Portable skill *artifacts* transfer and are measurable; personalization (voice/preferences) does not. Measure on **skill task-success, not edit-distance.** A-P3 = the two-user, non-shared-task, skill-artifact experiment; unpublished; cheapest differentiated evidence.

---

## 10. Honest proof obligations

| Claim | Status |
|---|---|
| Team OS is a layer, not a harness; core is harness-independent | ✅ by FR5/adapter design |
| Sits on Claude Code with full governance | ✅ (hooks) — but envelope inert today (review §4 P0), fix first |
| Sits on Hermes / other harnesses (door-scoped) | ⚠️ architecturally yes; second adapter not built |
| Governance-conscious single user has a cold-start reason | ⚠️ reason right; envelope inert — priority zero |
| The team category gap is real | ✅ verified; no shipped product (incl. Hermes); named only in research |
| Five primitives exist single-user | ✅ they do |
| Joint operation across humans | ⚠️ not built — the multiplayer layer is the build |
| Portable skills transfer A→B measurably | ⚠️ plausible, unproven — A-P3 with real collaborators |

**Honest framing:** Team OS is the governance + team-operation *layer* above the harness. Claude-first for distribution; harness-agnostic (via the FR5 adapter + MCP door) for durability and to hedge subsumption. The layer's value depends on fixing the inert envelope (single-user reason) and building the cross-human wiring (team reason); the second adapter (Hermes/other) is architecturally seeded but unbuilt. If cross-user transfer (A-P3) comes back flat, a governance-conscious single user still gets "the agent you can prove," on any harness — a real product — minus the compounding-skills moat.

---

## 11. One-liner tests

- **What it is:** "The trust-and-team layer that sits on top of your agent — any agent."
- **Distribution:** "Add Team OS to Claude." → **Ability:** "Runs on any harness, any model, your subscription or API or hardware."
- **vs Hermes:** "We don't compete with Hermes — we run on top of it and make it answerable."
- **Single user:** "The proactive agent you can leave running — on data that matters."
- **Team category:** "Where your team runs its agents — together."
- **Gap:** "Everyone built the cockpit for one pilot and the control tower for the airline. Nobody built the space where the crew flies together."

---

## Appendix — inputs

- Harness-vs-layer + distribution strategy (this version): from the in-conversation strategy exchange, 2026-07-12; fork FR5/adapter (FK1) and path-a/path-b (`docs/team-os-fork-harness-native.md`).
- Hermes research: v0.6 appendix. Market/team-space research: v0.4 §2–§4. Demand/substrate/transfer/ICP: v0.2 §9. CHAP: [arXiv 2606.09751](https://arxiv.org/pdf/2606.09751).
- PM review: `review/2026-07-12-pm-product-review.md`. Adoption path (memory): `adoption-single-user-first`.
- Supersedes: `positioning-v0.6.md` (→ v0.5 → v0.4 → v0.3 → v0.2 → v0.1).
