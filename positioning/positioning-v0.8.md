# Team OS — Positioning Statement

- **Version:** v0.8 — **ANCHOR**
- **Date:** 2026-07-12
- **Status:** Current working draft. Supersedes v0.7. **This is the anchored positioning.** It re-leads on a single category — **the solo agent control plane you own** — and demotes the team/collaboration story to a *secondary growth hook* (v0.7 led with it; solo users don't adopt for their team). It folds in the full model developed 2026-07-12: the control-plane category, the two-axis posture model, the routed multi-model portfolio, *govern-the-seam-not-the-server*, and the door as a nesting-parent + fan-in MCP chokepoint.
- **Reconciled against the build 2026-07-12** (§12 + `positioning-v0.8-build-reconciliation.md`). Core anchor stands on tested code; two elements (earned autonomy; harness-agnostic §7 door) are ahead of the build and read forward-looking until shipped.
- **Changed since v0.7:**
  1. **New anchor (§1–§3):** the lead is no longer "layer above the harness" or "where your team runs agents." It is **"the control plane you own for your whole agent fleet"** — an *analyst-named category* (Gartner AMP, Forrester agent control plane, Dec 2025) whose **solo lane is unclaimed.**
  2. **Team demoted to §10 growth hook.** Solo-first is the adoption law: one power user finds it indispensable → brings the team. No enterprise sales motion.
  3. **Two-axis posture model (§4):** execution locus → trust tier; inference source → a *routed portfolio* (subscription / API / local / mix), orthogonal to trust.
  4. **Coverage model made precise (§6–§7):** *govern the seam, not the server*; two control points; the shadow-agent boundary stated honestly; the door as a **nesting parent MCP + fan-in chokepoint** — the concrete harness-agnostic mechanism, with the one-door rule and three conditions.
  5. **Multi-model portfolio (§8)** is now a headline strength, not an edge case.

---

## 1. What Team OS *is*: the control plane you own for your agent fleet

**Team OS is the control plane for the agents you already run** — one gate, one record, one policy over every action they take, on infrastructure you own.

The distinction the category rests on:

> **Observability tells you what happened. A control plane governs what *can* happen.**

Not a model, not a harness, not a dashboard. A **control plane** sits *outside* the runtime and decides, per action, before it fires: allow, ask, deny — inspecting the action's actual payload (its command, its target, its recipient), recording every decision on a tamper-evident ledger you hold, and bounding how much the fleet may do unattended.

**This is a named market, not a metaphor.** Gartner calls it the **AI Agent Management Platform** ("the most valuable real estate in AI," Oct 2025); Forrester coined **"agent control plane"** (Dec 2025) — "inventories, governs, orchestrates, and assures heterogeneous agents across vendors." Category born Q4 2025; no Magic Quadrant or Wave yet. **Every analyst frame is the enterprise IT buyer. The individual/solo control plane is unclaimed in the research.** That unclaimed lane is the anchor.

---

## 2. The pain — solo, real, and now

A solo power user in 2026 no longer runs *an* agent. They run a **fleet**: a primary coding/planning agent, plus others they route work to — review, test, research — often across different models and vendors. The established center of gravity is **software development** (Claude Code $2.5B run-rate, Cursor $2B ARR; no non-coding agent within an order of magnitude), and inside it the frontier is **solo multi-agent orchestration**.

The sharpest unmet pain sits exactly there: **as agents shift from suggesting to acting** — commit, push, PR, run commands, hit APIs, touch infra, spend tokens across vendors — **the operator has no single point of control or record over the fleet.** Each harness governs only its own actions; nothing governs the workflow that crosses them. Developer *trust* in agent output fell **40% → 29% YoY even as usage climbed** — people are using agents they don't trust, and reaching for defensive guardrails by hand (never commit to main, feature-branch isolation, read-only DB, pipe everything to a SIEM).

> **The pain is not coding. It's orchestration — controlling a multi-model agent fleet you can't fully see or trust.** Coding is just where that fleet already runs hardest today. That's the beachhead, not the category.

---

## 3. The anchor claim

> **Team OS is the solo agent control plane you own — one gate, one record, one policy over your whole model portfolio, governing as hard as your setup allows.**

Three load-bearing words:
- **Solo** — adopted by one person, on their own machine, no admin and no procurement. (Team is where it *goes*, §10 — not why it's bought.)
- **Own** — files in git, exit = clone, per-principal encrypted; not a hosted console renting you visibility into your own agents.
- **Governing as hard as your setup allows** — *posture-adaptive* (§4). It doesn't promise uniform magic; it delivers the strongest control your harness + inference topology permits, and tells you exactly where the edge is.

---

## 4. The two axes (the posture model)

Two orthogonal properties of a user's setup. Conflating them is the mistake v0.7 half-made.

**Axis 1 — execution locus → sets the trust tier.**
*Where the action executes* determines how deeply Team OS can govern it. A locally-hooked harness → full-surface payload gating. An MCP-only harness → door-scoped governance. This is the trust axis (§5).

**Axis 2 — inference source → a routed portfolio, orthogonal to trust.**
*Which model bills the tokens* is a cost/privacy/capability choice, **not** a trust choice. "Hooks fire locally, not who bills the tokens." And it isn't a single selection — it's a **portfolio the user routes across**:
- a **primary subscription** (e.g., Claude Max),
- **secondary subscriptions** at similar/lower tier (e.g., ChatGPT Plus),
- **multiple closed-model API keys** (DeepSeek, Gemini…) for testing/validation,
- and/or **local models** on-box.

Each model gets assigned a **role** — plan, code, review, test — and the user orchestrates across them. A subscription user running local Claude Code still gets *full-trust*; an API user is not "less trusted." The two axes move independently.

> **Team OS runs on your setup — your harness, your inference portfolio — and gives you the strongest control that setup allows.**

---

## 5. The three trust tiers (execution locus)

| Tier | Requires | Governance strength | Where today |
|---|---|---|---|
| **B — Full-trust** | A harness whose **local hooks** fire on *every* tool call | Gate inspects every payload across the full surface (bash, file, MCP, synced-path); ledger complete; envelope enforceable | **Claude Code** |
| **A — Door-scoped** | Just **MCP** | Governs everything routed *through the Team OS door*; the harness's *native* tools stay outside it (reduced-trust, disclosed) | **ChatGPT, Hermes, Cursor**, any MCP client |
| **C — Hookless & un-doored** | — | **Blocked.** No hooks, nothing routed through the door → off-plane. **Degrades to A** the moment the harness points at the door | a hookless harness acting on its own |

Precise claim: **"Team OS reaches any harness via MCP, and delivers full provable governance on any harness that exposes hooks."** Never flatten to "full governance everywhere" — the honesty *is* the brand.

---

## 6. Govern the seam, not the server

The rule that resolves every "multiple MCPs / multiple harnesses" question:

**Team OS sees an action at exactly two control points —**
1. **the local PreToolUse hook** inside a hooked harness (every tool call, incl. MCP), and
2. **the Team OS door** (an MCP server it exposes — anything that calls it is gated + ledgered, whatever client made the call).

**An action is governed if and only if it crosses one of those.** An MCP being "installed somewhere" means nothing on its own; what matters is whether its calls cross a seam.

**The honest boundary (the solo shadow-agent problem).** A parallel *hookless* harness with its own MCPs — a second app touching the same files/system outside your gate — is a **bypass**. Your control plane's coverage equals the fraction of your fleet that routes through its seams. This is the solo version of what Microsoft Agent 365 built shadow-agent quarantine for. We say it plainly: *Team OS governs what routes through it; an agent you stand up in a separate hookless harness is off-plane until you point it at the door.* Naming the boundary is what makes the claim credible instead of hand-wavy.

---

## 7. The door: nesting parent + fan-in chokepoint (the harness-agnostic mechanism)

MCP composes two ways, and both are load-bearing:

1. **It nests** — an MCP server is also an MCP *client*. A door can front *other* doors. So **Team OS's door is the one MCP every harness installs, and it proxies all the other MCPs.** "The door to inputs" and "the gateway to other MCPs" are the same server.
2. **It fans in** — one MCP server can be reached by many harnesses at once. Claude Code + ChatGPT + a cloud runner all connect to the same door → **one gate, one ledger across the whole fleet, without hooking any of them.**

You don't consolidate the *harnesses*. You consolidate the **door**. And it stacks: the **shared door is the universal floor** (Tier A for every harness); a **hooked harness stacks full-surface local gating on top** (Tier B) — defense in depth.

**The anti-pattern to avoid:** *multiple doors to the same MCP from different harnesses* — each harness independently installing the same raw MCP directly. That's fan-**out** to many bypasses: same resource, many ungoverned paths, no single record. The pattern you want is the inverse — **one shared door, direct installs removed.**

**Three conditions for the shared door to actually govern:**
1. **The door is the *only* path** — remove duplicate direct MCP installs, or that path stays ungoverned.
2. **Per-connection principal auth (CN-1)** — many harnesses on one door means each inbound connection must be authenticated and attributed to a principal, or the ledger blurs and acceptance signals become forgeable (the one autonomy-expansion attack chain).
3. **It's Tier-A, door-scoped** — governs what flows *through* it, not each harness's own local surface; a remotely-hosted door is itself the disclosed reduced-trust posture.

This is what makes "harness-agnostic" concrete instead of aspirational: **a shared parent-MCP chokepoint**, with the local hook stacking full-trust wherever it fires.

---

## 8. The multi-model portfolio — where the product is *most* clearly the only answer

The routed portfolio (§4) is the strongest case, not an edge case. Concrete pattern:

```
Claude (primary sub)  →  plan + code
   │ hook
   ▼
ChatGPT (secondary sub) →  review the plan / diff
   │ hook
   ▼
DeepSeek (closed API)   →  run / validate tests
```

Orchestrated from **one locally-hooked conductor** (Claude Code calling the others as tool/API/egress calls), **every cross-provider call passes through the local gate** — full-trust governance across all three vendors, in one ledger with lineage (*Claude produced X → sent to ChatGPT → review Y → sent to DeepSeek → result Z*).

Everything that's merely nice with one provider becomes load-bearing with several:
- **More egress boundaries = more leak surface.** Sending proprietary code to DeepSeek or ChatGPT is a real data-egress event. Payload inspection answers "should *this* code go to *this* provider?" — per-provider data policy. Nobody else gates that.
- **Cross-model provenance is a mess by default.** For testing/validation across models, the unified record *is* the deliverable.
- **It's literally the orchestration pain (§2).** Each vendor governs only its own actions; the cross-vendor workflow is ungoverned — Team OS governs it, because it sits at the seam.

> **The control plane over your whole model portfolio — one gate, one record, one policy across every subscription and API your workflow routes through.** The multi-provider power user has the most to govern and is where Team OS is most clearly the only answer.

---

## 9. The four-corner whitespace

Does any product hold all four at once: **(a) action-level payload gating + (b) owned/self-hosted + (c) harness-agnostic + (d) solo-usable**?

| Product | (a) Payload gating | (b) Self-hosted | (c) Harness-agnostic | (d) Solo |
|---|---|---|---|---|
| Glean Access Policies | Yes | Yes (cloud-prem) | No | No (enterprise) |
| AWS AgentCore Policy | Yes | No (AWS) | Partial | Yes |
| Google Gemini Enterprise | Yes | Yes (GDC) | Via registry | No |
| **Conductor** | **approvals only, no payload** | Yes (local) | Yes | Yes |
| **Invariant MCP-scan** | Yes (arg-value) | Yes (OSS) | **MCP-only** | Yes |
| **Claude Code hooks (raw)** | Yes | Yes | **No (CC-locked)** | Yes |
| Devin CLI perms | Yes | No | No | Yes |
| GitHub Agent HQ | No (PR/branch-level) | No (hosted) | No (GitHub-locked) | Partial |
| **Team OS (target)** | **Yes (full surface)** | **Yes** | **Yes (seam + door, §7)** | **Yes** |

Every commercial row misses ≥1 corner. Conductor hits a/b/c/d but does **no payload inspection**. OSS gateways hit a/b/d but are **MCP-scoped**. Raw Claude Code hooks hit a/b/d but are **Claude-locked**. **No product occupies all four with true payload inspection for a solo self-hosting user.** Team OS's harness-agnostic corner is the seam-and-door mechanism of §7 — the piece that turns 3/4 into 4/4.

---

## 10. Where it goes — the team, as a *secondary* growth hook

Adoption law: **one power user adopts for themselves; the team is the expansion, never the lead.** No solo user installs a control plane "to help their team." They install it to control *their own* fleet — then, because it's already the owned, on-the-record space where their agents run, teammates join.

**Solo → team → org, and the same machinery turns:**
- the payload gate → **co-approval** (any of N humans vetoes before an action fires),
- the ledger → **shared accountability** (one log of everything every agent did),
- the envelope → **team autonomy policy** (the team sets how much its agents may do unattended),
- the promotion gate + git → **skills that compound** (one person's improvement flows to everyone's agents).

The category destination — **"where your team runs its agents, together"** — is genuinely uncontested (agent *managers* and agent *admins* exist; joint *operation* is named only in research, [CHAP arXiv 2606.09751](https://arxiv.org/pdf/2606.09751)). But it is the *land-and-expand outcome*, reached because the solo control plane was already good enough to spread. **Growth is secondary; the solo hook is primary.**

---

## 11. The moat

- **Owned, not hosted (exit = clone).** Your git; per-principal encrypted; leavers take their scope, never others'. The labs won't make agent operation portable off themselves.
- **Payload inspection across the full surface**, not approvals-only (vs Conductor), not MCP-only (vs Invariant), not PR/branch-level (vs Agent HQ).
- **Harness-agnostic via the seam + shared door** (§7) — the subsumption hedge: if a lab ships fleet governance *inside its own account*, the portable control plane moves to whatever runtime the user has and the value travels.
- **No individuation surface.** Per-skill, never per-person-comparative — what lets a *team* share the space (an EU works-council / AI-Act posture); admin-console vendors' buyers *want* the leaderboard, so they can't follow here.
- **Cross-account skill transfer** — improvements move between people who don't share a store; labs ship shared memory inside one account (~6–18mo), not across.

---

## 12. Proof obligations — reconciled against the build (2026-07-12)

**Reconciled by direct code inspection + `make test` (214 pass, 16 schemas clean, chains verify).** Full evidence with `file:line` in `positioning-v0.8-build-reconciliation.md`. Verdicts:

| Claim | Verdict | Evidence |
|---|---|---|
| Payload-inspecting gate, full surface | ✅ **built & tested** | `gate.py:115` (egress/read/synced/param/base64/taint/paths/outbound-scan); fail-closed `:268`; unconditional breaker `:41` |
| Owned / exit=clone / per-principal encrypted | ✅ **built** | `crypto_store.py` Fernet; `_assert_key_outside_repo:37`; keys 0o600 |
| Tamper-evident ledger with lineage | ✅ **built** | `hashchain.py:31` prev-hash link; `verify():144`; `verify_chains` green |
| Provable deletion | ✅ **built** | `deletion.py:100` unlinks content + `content_shredded` L9 |
| Earned autonomy (envelope) enforced at the gate | ❌ **INERT — confirmed** | envelope computes/persists levels (`envelope.py:76`) but **gate never reads them**; only `render_dashboard.py:277` consumes `levels`. Static gating only. **#1 fix.** |
| Principal auth (CN-1) | ✅ built, ⚠️ **replayable** | `principal_auth.py` HMAC; but `signing_payload:46` binds no nonce/timestamp & leaves `edit_distance` unsigned → forged/replayed reaction can move autonomy. **#2 fix.** |
| Door as nesting-parent + fan-in chokepoint (§7) | ❌ **unbuilt** | `door.py` = read + propose-to-inbox (single-writer ✅); no proxy/parent, no per-connection auth. §7 = design direction. **#3 fix.** |
| Harness-agnostic (2nd adapter / MCP proxy) | ❌ **unbuilt** | FR5 seam exists (`adapter/`); 2nd adapter + proxy path not built |
| Multi-model portfolio governed end-to-end (§8) | 🟡 **mechanism real** | gate's `bash-egress-scan`+`outbound-content-scan` (`:132,177`) already inspect a conductor's outbound API calls; named/tested path missing (upgraded from ⚠️) |
| Team / joint operation (§10) | ❌ **unbuilt** | single-user primitives only; multiplayer wiring is the build |
| Cross-account transfer measurably works | 🟡 **instrument built, result unproven** | `transfer.py` cohorts/deltas/pre-reg rule; needs real collaborators (A-P3) |

**Framing (verified):** the anchor **stands on built, tested ground** — for a Claude Code user, the gate + record + policy + deletion + ownership are real. Two positioning elements are **ahead of the build** and must read as forward-looking until shipped: **(1) "earned, calibrated autonomy"** (envelope is display-only — the differentiator that separates the anchor from "hooks + a policy file"), and **(2) harness-agnostic via the §7 door** (today: Claude-Code full-trust + a minimal read/propose door). One element is **safer than drafted**: multi-model governance via a hooked conductor already works at the mechanism level. **Fix order:** envelope→gate (solo differentiator) → sign full L8 payload w/ nonce (close replayable-sig) → door §7 topology (fleet/harness-agnostic). If cross-user transfer (§10/A-P3) comes back flat, the solo control plane is still real and differentiated — minus the compounding-skills expansion.

---

## 13. One-liner tests

- **What it is:** "The control plane you own for your whole agent fleet — one gate, one record, one policy over every action."
- **Anchor:** "The solo agent control plane you own — governs as hard as your setup allows."
- **The distinction:** "Observability tells you what happened. A control plane governs what *can* happen."
- **The pain:** "You're running five agents across three vendors and nothing controls the workflow that crosses them. This does."
- **Multi-model:** "One gate over Claude, ChatGPT, and your DeepSeek API key — payload-inspected, on a record you own."
- **Coverage honesty:** "It governs what routes through it. Point your fleet at one door, and it governs the fleet."
- **vs Conductor:** "Conductor asks yes/no. We look inside the action — and keep the record."
- **vs the admin consoles:** "They built the control tower for the airline's IT department. We built the one *you* own for *your* agents."
- **Growth (secondary):** "Good enough that you'll want your team on it — and when they join, the same gate becomes co-approval."

---

## Appendix — inputs

- Anchor + two-axis + seam/door mechanism (this version): in-conversation strategy exchange, 2026-07-12.
- Control-plane category & sizing: `research/2026-07-12-control-plane-market-sizing.md`. Competitive landscape / four-corner test: `research/2026-07-12-control-plane-landscape.md`. Agent HQ: `research/2026-07-12-agent-hq-deep-dive.md`. Solo use cases: `research/2026-07-12-solo-agent-use-cases.md`. Hermes: `research/2026-07-12-hermes-agent.md`.
- Fork mechanics (seam FR5/FK1, path-a/path-b, door): `docs/team-os-fork-harness-native.md`. Gate: `hooks/gate.py`. Door: `scripts/door.py`.
- PM review: `review/2026-07-12-pm-product-review.md`. Adoption law (memory): `adoption-single-user-first`.
- Supersedes: `positioning-v0.7.md` (→ v0.6 → … → v0.1).
