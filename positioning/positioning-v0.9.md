# Team OS — Positioning Statement

- **Version:** v0.9 — **ANCHOR (human-centric reland)**
- **Date:** 2026-07-12
- **Status:** Current. Supersedes v0.8. Same market wedge (the agent control plane), **re-centered on the human** after the doc-alignment review found v0.8 had drifted agent-centric while the frozen architecture and the GitHub README were human-centric all along. Folds in the reconciliation of every framing tension and the two positioning assets from the vision doc.
- **What changed from v0.8:**
  1. **Human-centric, not agent-focused.** The unit is the *person*; the payoff is the *team getting better together*. Agents are the fabric, not the point. (v0.8's "control plane for your agent fleet" over-centered agents.)
  2. **Both/and, not either/or.** Control-plane AND initiative (the control plane is what lets you *unleash* a proactive agent). Govern AND free — and adjustable.
  3. **"Command-and-control you can loosen to a lab."** Ships tight/safe (solo C&C default); every dial is user-owned — interior (autonomy envelope) and exterior (allow-policy + auto-approve) — so it is never actually a cage.
  4. **Leads Plane A** (Team OS as its own ambient MCP client) with the door secondary — matching `architecture.md §7.5`.
  5. **Adopts two assets:** the reversible/irreversible split (control the boundary hard, run the interior free) and the **one falsifiable guarantee**.
  6. **Solo differentiators now built:** WO-1 (envelope enforced at the gate) and WO-2 (replay-proof authenticated autonomy) shipped and tested — the anchor stands on tested code, not intent.

---

## 1. What Team OS *is*

**Team OS is how a person — then their team — runs their agents: on the record, under gates they own, with autonomy they can dial from tight command-and-control up to a free-running lab.**

It is a **human-centric team product.** The unit is the person; the agents are the fabric that carries what the person and the team know. The recognizable *entry* is a control plane for a solo user's agents — but the *subject* is always the human, and the *destination* is the team getting better together. Not an agent-management console for its own sake.

The market wedge, stated in the category's own language:
> **Observability tells you what happened. A control plane governs what *can* happen.**

But the reason a person *wants* that control plane is not restraint — it's **initiative they can trust**. The frozen identity claim (`architecture.md §1`): Team OS *originates* — drafts arrive done, loops fire on the world's schedule, proposals appear unrequested. **The control plane is what lets you let that off the leash.** Brakes exist to press the gas.

---

## 2. Both/and — the two tensions, resolved

**Control-plane AND initiative.** Not a governance tool *or* a proactive agent — the governance is what makes the proactivity safe to allow. Control-plane is the entry and the market category; unleashed initiative is what it delivers.

**Govern AND free — and adjustable.** The mechanism that gives both at once (`architecture.md §7.3` severity × reversibility; vision §3/§5):
> **Control the irreversible boundary hard. Run the reversible interior free.**

And **both zones are dials the human owns:**
- **Interior dial** — the autonomy envelope (how much the agent may do unattended in each category), earned through accepted work.
- **Exterior dial** — the user-owned allow-policy (what irreversible acts may cross without a hand) + auto-approve modes.

It **ships cage-shaped**: tight, safe defaults, command-and-control — because that is what a solo user adopts. But every bar is a dial the human owns, so it becomes a lab at the user's discretion.

> **Command-and-control you can loosen to a lab — you hold every dial, interior and exterior.**

---

## 3. The anchor claim

> **The control plane you own for your own agents — one gate, one record, one policy, tight by default and adjustable to a lab. Ships to you; grows into how your team runs together.**

Load-bearing words:
- **You / your own** — human-centric, solo entry, owned (files in git, exit = clone, per-principal encrypted).
- **Tight by default, adjustable** — the C&C→lab dials (§2).
- **Grows into your team** — the destination, not the pitch (§8).

**The promise line** (adopted from the vision doc's one falsifiable guarantee):
> **No irreversible action ever happens without either a rule you set or a confirmation you gave — and every one has a record before it acts.** A deployment where one slips through is a bug, not a tolerable residual. Everything else is best-effort; this is not.

---

## 4. How it reaches your agents — Plane A first

The architecture (`§7.5`) is explicit about priority, and v0.8 had it backwards:

- **Plane A (primary) — Team OS acts as *your* agent.** Team OS is itself an MCP *client*, holding its own connections to Slack/Gmail/Jira/Drive/GitHub under your grants, acting ambiently on your behalf. The gate fires locally on *its own* actions. **The proactive identity requires this plane** — a digest that only runs during an open chat is a chatbot, not a background agent. This is where full-trust governance lives.
- **Plane B (secondary) — a door for other clients.** Team OS also exposes an MCP *server* a Claude/ChatGPT session can query. Useful, but an *addition* to Plane A, never the mechanism for it.

So the harness-agnostic story leads with **Team OS originating as the client** (governed locally, full-trust), not with other harnesses reaching *through* Team OS's door. The door is how you *reach in*; Plane A is how it *acts out*.

**Inference is a routed portfolio** (primary sub + secondary subs + closed APIs + local), each model assigned a role — with one caveat v0.8 missed: routing is *mostly* orthogonal to trust, but a **routing×disclosure seam** binds them (`§14.4`) — a task touching your vendor-blind personal layer may not route to a non-attested endpoint just because it's cheaper. "Hooks fire locally, not who bills the tokens" — *unless* the data's residency tier constrains the endpoint.

---

## 5. The gate — what it actually does

Deterministic, model-free (SE-1), payload-inspecting, fail-closed. It classifies every action two ways — **by class** (read/write/send/execute/schedule) and **by reversibility** — and:
- **Irreversible boundary:** deny-by-default; crosses only on an allow-policy match or a confirmation, always with a pre-act record (the §3 guarantee).
- **Reversible interior:** runs and is recorded; friction only from taint, secrets, protected paths, or the earned-autonomy floor.
- **Earned autonomy:** a clean side-effectful action is auto-permitted only once the principal has earned the level in that category — the interior dial, now enforced at the gate (WO-1).

The one third-party attack chain — a forged or replayed reaction widening autonomy — is closed: acceptance signals are principal-authenticated over their full payload, single-use, and freshness-bound (WO-2, CN-1).

---

## 6. The market gap (the four-corner whitespace)

Does any product hold all four: **(a) action-level payload gating + (b) owned/self-hosted + (c) works across your harnesses + (d) solo-usable by a person**? Enterprise control planes miss (b)/(d); Conductor does approvals but no payload inspection; OSS gateways are MCP-only; raw Claude Code hooks are harness-locked. **No product occupies all four for a solo human on infrastructure they own.** And none of them is human-*centric* — they are admin consoles for governing agents top-down; Team OS is the person's own.

---

## 7. Why only this can be it (the moat)

- **Human-centric + owned (exit = clone).** Your git, per-principal encrypted; the person's own control point, not an admin's console. Admin-console vendors *want* the individual-comparison surface Team OS refuses (no individuation), so they can't follow to the human center.
- **Payload inspection across the full surface**, not approvals-only, not MCP-only, not PR-level.
- **The falsifiable guarantee** — deterministic, model-free, ownable; nobody else states a line strong enough to be wrong.
- **Adjustable both-zones autonomy** — the C&C→lab range, with the boundary always deny-by-default. The market is fleeing *ungoverned* autonomy; this is autonomy you can dial and always take back.
- **Cross-account skill transfer** — the team payoff labs ship only *inside one account*.

---

## 8. Where it goes — the team, human-first

Adoption law: **one person adopts for themselves; the team is the expansion, never the lead.** Nobody installs a control plane "to help their team." They install it to run *their own* agents — and because it's already the owned, on-the-record space where their agents run, the team joins. The same machinery turns:
- the payload gate → **co-approval** (any of N humans vetoes before an action fires),
- the ledger → **shared accountability**,
- the envelope/allow-policy → **team autonomy policy**,
- the promotion gate + git → **skills that compound across people**.

The destination — *"where your team runs its agents, together"* — is genuinely uncontested (agent *managers* and *admins* exist; joint *operation* is named only in research, [CHAP arXiv 2606.09751](https://arxiv.org/pdf/2606.09751)). It is the land-and-expand outcome, reached because the solo product was already indispensable. **A human-centric team product throughout — solo is the entry, not the identity.**

---

## 9. Proof — reconciled against the build (2026-07-12)

Direct code inspection + `make test` (230 tests). Full evidence: `positioning-v0.8-build-reconciliation.md`, `…-doc-alignment.md`, `review/2026-07-12-positioning-alignment-workorder.md`.

| Claim | Verdict | Evidence |
|---|---|---|
| Payload-inspecting gate, full surface | ✅ built & tested | `hooks/gate.py` |
| Owned / exit=clone / per-principal encrypted | ✅ | `crypto_store.py` |
| Tamper-evident ledger + provable deletion | ✅ | `hashchain.py`, `deletion.py` |
| **Earned autonomy enforced at the gate** (interior dial) | ✅ **now built (WO-1)** | `envelope_gate.py` + `gate.py`; `test_gate.EnvelopeEnforcement` |
| **Autonomy can't be forged/replayed** | ✅ **now built (WO-2)** | `principal_auth.verified_fresh`; `test_principal_auth` |
| Reversibility boundary + falsifiable guarantee (exterior dial) | ⏳ **next (WO-3/WO-4)** | frozen §7.3 + vision §8; work order queued |
| Plane A primary, door secondary | ⏳ verify (WO-5) | loops/connectors gated; door propose-only |
| Multi-model portfolio via a hooked conductor | 🟡 mechanism real | gate inspects a conductor's egress/API calls |
| Team / joint operation | ❌ unbuilt | single-user primitives only; the multiplayer wiring is the build |
| Cross-account transfer measurably works | 🟡 instrument built | `transfer.py`; needs A-P3 collaborators |

**Framing:** the solo anchor now stands on **tested code** — the two differentiators that were "display-only / forgeable" in v0.8 (earned autonomy, principal-authenticated autonomy) are built and green. WO-3/WO-4 make the reversibility boundary and the falsifiable guarantee real (the exterior dial); WO-5 aligns the harness story with Plane A. If cross-user transfer (§8) comes back flat, the human still has a real, differentiated, owned control plane for their own agents.

---

## 10. One-liner tests

- **What it is:** "How you run your agents — on the record, under gates you own, with autonomy you can dial from command-and-control up to a lab."
- **Human-centric:** "It's not a console for managing agents. It's *your* control point — and it makes your team better, not your agents busier."
- **Both/and:** "The control plane that lets you let a proactive agent off the leash."
- **The range:** "Ships tight. Every dial is yours — interior and exterior. Loosen it to a lab when you trust it."
- **The promise:** "Nothing irreversible happens without a rule you set or a hand you gave — with a record, every time."
- **Plane A:** "It acts *as* you, in the background — not just a thing you query from a chat window."
- **Growth (secondary):** "Good enough that you'll want your team on it — and the same gate becomes co-approval when they join."

---

## Appendix — inputs
- Reconciliation of framing (this version): in-conversation, 2026-07-12 (both/and; human-centric; adjustable C&C→lab).
- Docs read in full: `docs/team-os-architecture.md` (frozen), `docs/team-os-emergence-architecture.md` + `…-summary.md` (vision). Alignment: `positioning-v0.8-doc-alignment.md`.
- Build state: `positioning-v0.8-build-reconciliation.md`; work order `review/2026-07-12-positioning-alignment-workorder.md` (WO-1/WO-2 shipped this session).
- Category/landscape research: `research/` threads 11–14. Memory: [[positioning-anchor-control-plane]], [[adoption-single-user-first]].
- Supersedes: `positioning-v0.8.md` (→ v0.7 → … → v0.1).
