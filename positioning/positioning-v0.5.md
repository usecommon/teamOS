# Team OS — Positioning Statement

- **Version:** v0.5
- **Date:** 2026-07-12
- **Status:** Current working draft. Supersedes v0.4. Reordered to lead with the **single-user wedge** — the product is adopted by one user first, then shared with a team, then the org, so the positioning must answer "why would ONE person use this?" before the team story.
- **Changed since v0.4:**
  1. **New §1 — the single-user reason** ("the agent you can actually let off the leash") now leads. The team category is reframed as the *destination*, not the entry.
  2. **Adoption path made explicit:** single user → team → org. Every claim is ordered by that path.
  3. **Sharpened the honest tension:** the single strongest reason a single user adopts (#1, unattended work you'd permit) is *the same mechanism the review found broken* (inert envelope). That reorders the roadmap — fixing it is the entry-point fix, not a team-scale nicety.

---

## 1. Why a single user adopts this (the wedge — answer this first)

A single user already has Claude Code, Cowork, ChatGPT, free scheduled tasks. The reason to add Team OS has to be a delta over *those*, for one person, today.

> **It's the agent you can actually let off the leash.**

Everyone's agent can *do* things. Nobody's agent can be safely *left alone*. That's the single-user pain, and it's what the whole build solves. Three reasons, strongest first:

1. **Unattended work you'd actually permit (the core delta — the only cold-start reason).** Incumbent proactive features are tame or babysat: ChatGPT confirms consequential actions, Claude routines run in a cloud you don't govern, and real autonomy means you end up watching — which deletes the savings. Structural reason: engines without brakes, so autonomy stays turned down. Team OS's gate + ledger + breaker exist so *one* user can say "send my standup every morning without asking me" and sleep. **The value isn't "it drafts" — it's "it drafts and sends, unattended, and you're not scared of it."**
2. **A record you own of what your agent did (the confidence delta — retention).** When an agent does something wrong on your behalf, you need "what did it do and why?" Cowork/ChatGPT can't reconstruct that. Team OS gives one person a tamper-evident, greppable log with lineage — the confidence to delegate at all, and the ability to catch the agent when it drifts.
3. **It's yours and can't be taken (the ownership delta — differentiation/retention).** Files in git; exit = clone. A user who spends months teaching an agent their work won't have it stranded when a vendor sunsets the product (Pulse, Limitless/Rewind). Same instinct that picks Obsidian over Notion.

**Order matters:** #2 and #3 are *why you trust it and stay*; only **#1 pulls a user in cold.** Lead the single-user pitch with #1.

**The honest tension (load-bearing):** #1 — the one reason strong enough to make someone install it — is *the exact thing the product review found broken.* The autonomy envelope is inert at the gate, so today the agent can't actually earn "send unattended": it either asks every time (taint-on-send) or the dial moves nothing. **The single-user reason to adopt and the single-user thing that's broken are the same mechanism.** So fixing the envelope isn't a team-scale enabler — it's what gives *anyone* a reason to start. That reorders the roadmap.

**Single-user headline:** *The proactive agent you can leave running — because every move is gated, on a record you own.*

---

## 2. Where it goes: the shared space where a team runs its agents — together

The single user is the entry. The **category** — the destination once they share it — is the unoccupied one.

> **Team OS is where your team runs its agents — together.**

Slack is where your team **talks**. Figma is where it **designs**. GitHub is where it **ships code**. **There is no "where your team runs its agents."** That's the space Team OS grows into.

The adoption path is the whole strategy: **one user leaves an agent running (wedge) → teammates join the same owned, on-the-record space (team) → the org standardizes on it (expansion).** The single-user trust machinery *is* the team collaboration surface — you don't rebuild anything.

---

## 3. The gap (why the team category is interesting)

The market builds for two roles and skips the third.

| What everyone builds | Shape | Examples |
|---|---|---|
| **The agent manager** | *One human* runs many agents | Claude Code, Cursor, Devin, GitHub Agent HQ |
| **The agent admin** | *IT* governs a fleet top-down | MS Agent 365, OpenAI Frontier, Atlassian Rovo |
| **← Missing →** | *A team* operates agents **together** | **nobody** |

Every "team" feature stops at shared visibility (@-mention one agent), top-down governance (admins provision/audit), or serial hand-off (Factory take-over). **No one ships joint operation** — the exact thing named in a 2026 research protocol ([CHAP, arXiv 2606.09751](https://arxiv.org/pdf/2606.09751)) and shipped by no product. (No "Claude Ultra" exists; Anthropic's top individual tier is Max 20x at $200/mo, usage-only. Claude Tag lets a team co-*use* one agent in Slack but not co-*govern* it.)

---

## 4. The five team primitives (the same machinery, pointed at a team)

Each is a Team OS piece that already exists for one user; the team layer is the build.

| # | Primitive | What it does | Single-user piece today |
|---|---|---|---|
| 1 | **Co-approval gate** | Any of N named humans approves/vetoes an action *before it fires* | the payload-inspecting gate |
| 2 | **Shared record** | One tamper-evident log of everything every agent did | the hash-chained ledgers |
| 3 | **Live hand-off** | Pass a running agent + its state between teammates | the proposals inbox / door |
| 4 | **Shared autonomy dial** | The team sets how much its agents may do unattended | the autonomy envelope |
| 5 | **Skills that compound** | One person's improvement flows to everyone's agents | the promotion gate + git |

**The unlock:** the same trust machinery that makes one person's agent safe to run unattended (§1) is exactly what a team needs to run agents together. A gate *becomes* co-approval; a ledger *becomes* shared accountability; the autonomy dial *becomes* team policy. Built the multiplayer primitives; only pointed them at one player so far.

---

## 5. Why only this can be it (the moat)

- **Owned, not hosted (exit = clone).** Lives in the team's own git; the labs won't make agent operation portable *off* them.
- **Cannot become surveillance (no individuation).** Per-skill metrics, never per-person — what makes a *team* willing to run agents in a shared space, and (in the EU) a works-council / AI-Act requirement. Admin-console vendors' buyers *want* the leaderboard; they can't take this position.
- **Cross-account skill transfer.** Improvements move between people who don't share one vendor's store. The labs will ship shared memory *inside one account* (Anthropic #38536/#60082) in ~6–18mo; not cross-account. Build atop their substrate; own the layer above.

---

## 6. Buyer model — matches the adoption path

Two roles, in sequence:
- **Worker = champion/discoverer.** Adopts on §1 (the agent you can let off the leash). The distribution engine.
- **Org-side risk owner = economic buyer** (security/platform/compliance; EU works council). Approves & pays on the trust stack, which at the regulated boundary is a legal precondition (EU AI Act Art. 12, GDPR).

**No-surveillance is load-bearing for both** — the precondition for the champion motion (workers won't advocate a tool that can rank them) and the approval-enabler for the risk owner.

---

## 7. Initiative vs trust stack (retained)

**Initiative** = what it *does* (reason to *want* it; sells the worker). **Trust stack** = what makes it *safe to allow* (reason you're *allowed to run* it; sells the risk owner). Engine vs brakes — a fast car with no brakes is uninsurable, which is why incumbents keep proactive features tame. The trust stack is what lets Team OS turn the initiative *up*, and in the team frame it *becomes* the collaboration surface.

## 8. What "transfer" means (retained)

**Share the skill, keep the personalization local.** Portable skill *artifacts* transfer between people and are measurable; personalization (voice/preferences) does not — A's optimum is B's wrong answer. Promotion gate carries only skill artifacts; measure transfer on **skill task-success, not edit-distance.** A-P3 gate = the two-user, non-shared-task, skill-artifact experiment; nobody has published it.

---

## 9. Honest proof obligations

| Claim | Status |
|---|---|
| A single user has a cold-start reason (unattended work you'd permit) | ⚠️ **the reason is right, the mechanism is broken** — envelope inert (review §4 P0). Fix this first; it's the entry-point fix. |
| Owned record + exit=clone give a single user confidence/retention | ✅ real today (ledgers, git) |
| The team category gap is real | ✅ verified — no shipped product; named only in research (CHAP) |
| The five primitives exist as single-user pieces | ✅ they do |
| They work *across humans* (joint operation) | ⚠️ not built — the multiplayer layer is the build |
| Portable skills transfer A→B measurably | ⚠️ plausible, unproven — needs A-P3 with real collaborators |

**Honest framing:** the adoption path is single-user → team → org. The single-user entry reason is right but currently broken (envelope) — fixing it is priority zero because it's what makes the product worth starting for one person, *before* any team story. The team category is real and unoccupied; its primitives exist single-user; the cross-human wiring is the build. If cross-user transfer (A-P3) comes back flat, a single user still gets "the agent you can let off the leash, on a record you own" — a real product — and a team still gets co-approval + shared record + hand-off, minus the compounding-skills moat.

---

## 10. One-liner tests

- **Single user:** "The proactive agent you can leave running." / "The agent you can actually let off the leash."
- **Team category:** "Where your team runs its agents — together." / "Slack for talking, GitHub for code, Team OS for running your agents."
- **Gap:** "Everyone built the cockpit for one pilot and the control tower for the airline. Nobody built the space where the crew flies together."

---

## Appendix — inputs

- Single-user wedge (this version): from the "why would one user use this" analysis, 2026-07-12; adoption path is single-user-first (memory: `adoption-single-user-first`).
- Market research: Claude/OpenAI/Google/Microsoft/non-AI-provider team spaces + tiers/"Ultra" check; CHAP [arXiv 2606.09751](https://arxiv.org/pdf/2606.09751). Prior research (demand/WTP, substrate race, transfer, buyer/ICP): v0.2 §9.
- PM review + findings: `review/2026-07-12-pm-product-review.md`, `review/2026-07-12-pm-findings.md`.
- Supersedes: `positioning-v0.4.md` (→ v0.3 → v0.2 → v0.1).
