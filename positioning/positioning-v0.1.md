# Team OS — Positioning Statement

- **Version:** v0.1
- **Date:** 2026-07-12
- **Status:** DRAFT — pre-research. This captures the working hypothesis *before* the four gating research threads return. Every claim marked ⚠️ is a bet not yet validated.
- **Changed since:** (initial version)
- **Author basis:** the 120-turn PM simulation, market + academic memos, the Claude multi-human boundary check, and the repo's own identity claim (`docs/team-os-architecture.md` §1, `docs/team-os-fork-harness-native.md`).

---

## 0. The trap we are steering away from

Calling Team OS a **"proactive personal assistant"** files it next to Lindy, ChatGPT, Copilot, Superhuman — a category where the unit of value is *"it drafts my email,"* every incumbent ships it, and it is priced to zero. The repo's own architecture doc warns against exactly this: *"read this before filing the product in a category… Team OS is a proactive, action-driven system, not a memory or corpus product… if it ships recall without initiative it drifts into the crowded category and loses the whitespace."* The positioning below deliberately moves **up the stack** and **toward the team**, where the ground is unoccupied.

---

## 1. One-line positioning (candidate)

> **Team OS is the compounding, self-owned work layer for a team of AI agents — a runtime that *originates* work on your team's behalf, keeps a provable record of everything it did, makes every agent better from what the others learned, and can never be turned against the people using it.**

Shorter, for a deck:

> **The team agent layer your team owns — and that can't be used to watch them.**

---

## 2. Category framing: not an assistant, not an admin console

There are three shapes of "team AI tool." Two are taken or compromised; the third is open.

| Shape | Example | Why it's not us |
|---|---|---|
| **The shared bot** — one agent everyone queries | Dust org agents, a shared Slackbot | Collapses back into memory/RAG; no individual ownership; violates the identity claim |
| **The admin console** — one manager governs everyone's agents | MS Agent 365, OpenAI Frontier | Built for *control over* people; top-down; an IT product done *to* workers |
| **The sovereign cooperative** — individually-owned agents sharing *improvements* through a governed, consent-based, non-surveilling channel | *(open)* | **This is Team OS.** |

Team OS is closer to **"CI/CD + audit log + a shared skill library for autonomous work"** than to "an AI helper." The assistant is the delivery vehicle; the product is the **governed-initiative infrastructure and the cross-agent improvement loop.**

---

## 3. What we actually sell (the value stack, in priority order)

1. **Initiative that compounds across a team (lead).** ⚠️ Your team's way of doing things becomes versioned, measured, shippable **skills**; an improvement learned on one person's agent lifts everyone's. This is the FK7/A-P3 bet — *the* differentiator, and unproven.
2. **A provable record of autonomous work (backing).** Every agent action is gated (payload-inspected), ledgered (tamper-evident), lineage-tracked, and erasable. "On the record" at personal/team scale, owned — not an enterprise admin console over someone else's cloud.
3. **Sovereignty as the moat (the durable edge).** You own it (exit = git clone); it structurally **cannot surveil** (per-skill metrics, never per-person — no leaderboard, by construction); governance answers to the *worker*, not the org. These are the parts a platform vendor is structurally reluctant to ship because they cut against SaaS lock-in and the admin buyer.

---

## 4. Why now / why us (the wedge)

- **The market bifurcated into "act" (everyone) and "govern" (Microsoft, OpenAI Frontier).** Nobody ships the combination — proactive + owned + auditable + leavable — under user ownership.
- **Claude's own boundary (verified):** Claude gives teams the *distribution rails* (git, skill marketplace, shared Projects) and *central admin*, but **not** a learning substrate where A's *usage* auto-improves B's agent. That exact cell is unoccupied. Their skill-sharing is *a human hand-packaging a static file and republishing it* — Team OS's bet is a *measured loop from real use.* The word that separates them is **"measured."**
- **Regulatory tailwind:** ⚠️ EU AI Act logging obligations (enforce Aug 2, 2026), GDPR erasure — may create a *forced* buyer for the trust stack. (Demand research pending.)
- **Post-lock-in moment:** the Limitless/Rewind shutdown (users stranded when Meta pulled the plug) is the market's own cautionary tale for "exit = clone."

---

## 5. The strategic thesis in one move

**Race the substrate; moat the sovereignty.**

- The *technical* substrate (cross-human learning transfer) is a **race** — Anthropic has open feature requests for shared team memory (#38536) and multi-user sessions (#60082), and "Memory for Managed Agents" already shares learning across agents in one workspace. "Nobody ships it" is not a stable moat on the technology. ⚠️ (Substrate-race research pending — how fast the window closes.)
- The *defensible* position is the ring around it: **ownership + non-surveillance + worker-sovereign governance** — things Anthropic and the admin-console vendors won't build because they hurt their own model.
- So: **lead the pitch with the compounding loop, but moat on the sovereignty.**

---

## 6. Beachhead & sequencing (from the sim + market read)

- **Beachhead user: the technical IC / small dev team.** CLI-first fits them; the market data agrees technical users grant agent autonomy readily. Do **not** market to non-technical PMs until there's a GUI/hosted install — the CLI excludes them by construction.
- **Cold-start on-ramp:** the **MCP door + cloud routines (path b)** is the frictionless entry for subscription-only users (value in minutes); **graduate to the local runtime (path a)** for the full gated, on-the-record posture. Onboarding narrative: *easy on-ramp → owned runtime.* (Caveat: path b is reduced-trust/disclosed — only Team OS door actions are gated there.)
- ⚠️ **Buyer/ICP for the sovereignty pitch is unconfirmed** (research pending).

---

## 7. Proof obligations (what must be true for this positioning to hold)

| Claim | Status | Evidence gate |
|---|---|---|
| Initiative compounds across people (A→B transfer) | ⚠️ **unproven** | FK7/A-P3: measured lift on a 2nd person's agent — needs real collaborators |
| The core loop is felt by the user | ❌ **currently broken** | Envelope is inert at the gate; must be actuated (review §4 P0) |
| We can count accepted unprompted work | ❌ **currently broken** | Initiative floor un-computable as orchestrated (review §4 P1) |
| People pay for the trust stack | ⚠️ **unknown** | Demand/WTP research pending |
| A reachable paying ICP exists for sovereignty | ⚠️ **unknown** | ICP research pending |

**Honest framing:** today Team OS is an excellent *owned, auditable personal* agent with strong bones and two unwired core mechanisms. The *team* positioning above is a direction the evidence permits but does not yet support. If transfer (A-P3) comes back flat, the honest positioning collapses to shape-1-for-one-person: "the AI agent you own and can audit" — still real, much smaller.

---

## 8. Messaging tests (to refine in later versions)

- "Not a personal assistant — the team agent layer you own and that can't watch you."
- "Git for how your team's work gets done."
- "Autonomous work, on the record, in your repo."
- "Every agent gets better from what the others learned — and no one gets ranked for it."

---

## Appendix — inputs feeding this version

- PM product review: `review/2026-07-12-pm-product-review.md`
- Findings: `review/2026-07-12-pm-findings.md`
- Market/academia/persona inputs: `review/sim-2026-07-12-pm/qualitative-inputs.md`
- Claude multi-human boundary check (in-conversation, 2026-07-12)
- **Pending (v0.2 inputs):** demand/WTP, substrate-race, transfer-evidence, buyer/ICP research
