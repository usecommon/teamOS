# Team OS — Positioning Statement

- **Version:** v0.3
- **Date:** 2026-07-12
- **Status:** Current working draft. Supersedes v0.2. Clarifies three things flagged in review: the buyer model, the initiative-vs-trust-stack distinction, and what "transfer" means.
- **Changed since v0.2:**
  1. **Buyer model corrected to two roles, not one.** The worker is the *champion/discoverer* (distribution engine); the org-side risk owner is the *economic buyer*. Bottom-up motion. v0.2 wrongly implied the worker is not a buyer at all.
  2. **No-surveillance reframed as load-bearing for both roles** — it's the precondition for the worker-champion motion (workers won't advocate a tool that can rank them) *and* the approval-enabler for the risk owner. Not a soft sentiment.
  3. **Initiative vs trust stack made crisp** (new §2): initiative = reason to want it; trust stack = reason you're allowed to run it. Engine vs brakes.
  4. **Transfer made crisp** (rewritten §7): *share the skill, keep the personalization local.* Portable skill artifacts transfer; personalization (voice/preferences) does not. Measure transfer on skill task-success, not edit-distance.

---

## 0. The trap we steer away from

"Proactive personal assistant" files Team OS next to Lindy/ChatGPT/Copilot — priced to zero. We move **up the value stack** (feature → infrastructure) and, over time, **toward the team** (personal tool → compounding layer), staged by what the evidence supports today.

---

## 1. Two roles buy this, in sequence (bottom-up motion)

The buyer is **not** one person. It's a champion and an approver, and they adopt in order — the classic dev-tool land-and-expand (Copilot, Cursor, Linear, Datadog).

| Role | Who | What convinces them | Their value |
|---|---|---|---|
| **Champion / discoverer** | The **worker** (technical IC first) | The tool does their recurring work unprompted and well | **Initiative** — drafts arrive done |
| **Economic buyer / approver** | The **org-side risk owner** (security / platform-eng / CISO / compliance; in the EU, the works council) | It can run on real data provably and be deleted/audited; it can't be turned against staff | **Trust stack** — provable, erasable, non-surveilling |

**The motion:** worker discovers (on initiative) → worker champions → risk owner approves & pays (on trust stack) → org-wide expansion (on transfer).

**No-surveillance is load-bearing for BOTH roles, not a soft value:**
- It's the **precondition for the champion motion** — a worker will not advocate a tool that can rank or monitor them; bottom-up adoption dies without it.
- It's the **approval-enabler for the risk owner** — "no per-person individuation" lets them say yes without a works-council fight (in the EU it's a co-determination / AI-Act requirement).

So worker-sovereignty rarely appears on the invoice, but it's what makes the invoice happen.

---

## 2. Initiative vs trust stack (the two halves, made crisp)

These get conflated constantly. They answer different questions and sell to different roles.

| | **Initiative** | **Trust stack** |
|---|---|---|
| What it is | What the product *does* — proactive action: drafts done, loops fire, proposals appear | What makes the action *safe to allow* — gate, ledgers, lineage, deletion, envelope, exit=clone |
| Question it answers | "Why would I want this?" | "Why am I allowed to run this on real data?" |
| Who it convinces | The worker/champion | The risk owner/approver |
| Failure if alone | *(Trust stack alone)* → a governance product with nothing to govern (crowded, vitamin) | *(Initiative alone)* → a reckless auto-sender no one can deploy on real data |

**One line: initiative is the reason to want it; the trust stack is the reason you're allowed to run it.**

**The analogy: initiative is the engine, the trust stack is the brakes + seatbelt + black-box recorder.** You buy the car for the engine — but a fast car with no brakes is uninsurable; nobody puts it on the road. This is *exactly why incumbents keep their proactive features timid and reactive* — engines without brakes can't be turned up. **The trust stack is what lets Team OS turn the initiative up — unattended, on real data, on real sends — instead of keeping it tame.** Sell the engine; the brakes are what make the sale deployable and what the risk owner signs for.

---

## 3. Staged positioning (three altitudes)

| Stage | Buyer | Pain (painkiller) | What we say |
|---|---|---|---|
| **A — Wedge (now)** | Worker/champion (technical IC / small dev team) | "Recurring work I assemble by hand" | **"The proactive agent you own and can audit."** Sold on *initiative*. |
| **B — Expansion (upsell)** | Org-side risk owner (regulated / IP-sensitive) | "We're running agents on real data and can't prove or delete what they did" | **"Autonomous work that's provable and erasable, in your own scope."** Trust stack *is* the painkiller here (EU AI Act Art. 12, GDPR, air-gapped, keys-yours, exit=clone). |
| **C — The bet (long game)** | The team, via the risk owner | "Our know-how lives in one person's session" | **"Every agent gets better from what the others learned — and no one gets ranked for it."** Gated on A-P3 (§7). |

**Near-term headline (A):** *The team agent layer you own — drafts arrive done, every action on the record, nothing leaves your repo.*

---

## 4. Category: not an assistant, not an admin console; a sovereign cooperative (destination)

| Shape | Example | Why not us |
|---|---|---|
| Shared bot (one agent everyone queries) | Dust org agents | Collapses into memory/RAG; no ownership |
| Admin console (one manager governs all agents) | MS Agent 365, OpenAI Frontier | *Control over* people; the surveillance shape |
| **Sovereign cooperative** (owned agents sharing *skill improvements* through a governed, non-surveilling channel) | *(open)* | **Team OS's destination**, reached via Stage A |

Mental model: **git + CI + audit log for autonomous work, with a shared skill library.**

---

## 5. Strategic thesis in one move

**Sell the initiative. Moat the transfer layer and the ownership. Upsell the governance into regulated teams.**

- Initiative is the painkiller people adopt for (A). Trust stack alone is a vitamin at small scale — don't lead with it there.
- The durable moat is the **cross-account, measured skill-transfer layer**, not a memory store — the labs will commoditize the substrate (Anthropic Managed-Agent memory + open request #38536) in 6–18mo; they *won't* build cross-account transfer (it breaks "keep data in one account"). Build atop their substrate.
- Governance is the expansion painkiller (B) — where the budget is.
- Ownership + no-surveillance are the buyer-specific closers for regulated orgs and EU works councils, and the champion-enabler for workers.

---

## 6. Why now

- Market bifurcated into **"act" (everyone)** and **"govern" (MS, OpenAI Frontier)** — nobody ships proactive + owned + auditable + leavable under user ownership.
- **Regulatory forcing function:** EU AI Act Art. 12 tamper-evident logging enforceable **Aug 2, 2026** (fines €15M/3%); Gartner projects a **billion-dollar governance market**. Turns Stage B's trust stack from vitamin to painkiller.
- **Transfer layer unoccupied and just proven in the lab:** `FederatedSkill` (arXiv 2606.03143) — cross-client skill-patch exchange, privacy-preserving, +44% success. Shipped by no one.
- **Post-lock-in moment:** Limitless/Rewind shutdown = the market's own exit=clone cautionary tale.

---

## 7. What "transfer" means (the make-or-break, made crisp)

An agent accumulates **two kinds of improvement**, and only one is shareable:

| | **Portable skill** | **Personalization** |
|---|---|---|
| What | A reusable procedure that does a task the same way for anyone: "pull deploy-freq from CI and format it," "draft a PR description from a diff" | How the agent adapts to *this person*: their voice, preferences, "I open with a customer anecdote" |
| Transfers between people? | **Yes** — A refines it, B's agent gets measurably better at that task | **No** — A's optimum is B's *wrong answer*; pushing it is negative transfer |
| Evidence | Voyager (skill lifted a *different* agent 0/3→1–2/3); Brynjolfsson QJE 2025 (+34% novices from best-practice codification); FederatedSkill | "Skill is Not One-Size-Fits-All" (arXiv 2605.30723): transfer negative-by-default without re-alignment; the "my-voice" problem |

**The rule: share the skill, keep the personalization local.** Two consequences:

1. **The promotion gate carries only *skill artifacts* across people; personalization stays in each person's private scope forever.** Maps onto the repo's existing boundary — *skills* promote, *corpus/profile* don't.
2. **Measure transfer on skill task-success, not edit-distance.** Edit-distance measures voice-fit (personalization) — the thing that *shouldn't* propagate. This is why a heavy-editing user correctly drives little team transfer: her edits are local personalization, not a portable skill — and that's fine, not a failure. The earlier metric tangle came from treating voice-edits as a transferable improvement; they never were.

**A-P3 gate (unchanged, now precisely scoped):** the two-different-users, non-shared-task, **skill-artifact** transfer experiment — measured on task-success. Nobody has published it; it's the cheapest differentiated evidence in the market.

---

## 8. Beachhead & sequencing

- **Beachhead: technical IC / small dev team** (the champion). CLI-first fits them; bottom-up on capability. Not non-technical PMs until a GUI exists (CLI excludes them; sim §3).
- **Cold-start on-ramp:** MCP door + cloud routines (path b) for subscription users — value in minutes — then graduate to local runtime (path a) for the full gated posture. *Easy on-ramp → owned runtime.*
- **Expansion:** land bottom-up with a dev team inside a regulated/IP-sensitive org → risk owner adopts org-wide for the trust stack (B) → team-transfer loop (C) is the expansion engine.
- **EU works-council angle:** distinct high-conviction secondary — "no individuation" is a purchase criterion there.

---

## 9. Proof obligations

| Claim | Status | Gate |
|---|---|---|
| Portable *skills* transfer A→B, measurably | ⚠️ plausible, unproven | A-P3: two-user, non-shared-task, skill-artifact, task-success |
| Personalization does *not* need to transfer | ✅ by design | keep it local; don't measure it as transfer |
| The core loop is felt by the user | ❌ broken today | Envelope inert at gate (review §4 P0) |
| We can count accepted unprompted work | ❌ broken today | Floor un-computable as orchestrated (review §4 P1) |
| Regulated buyers pay for the trust stack | ✅ supported | Art. 12 / GDPR; air-gapped comps ~$39/user |
| Worker-champion motion exists | ✅ supported (conditional) | requires no-surveillance to hold; capability-led adoption |
| A paying economic buyer exists | ✅ supported | org-side risk owner; EU works councils |

**Honest floor:** today Team OS is a strong owned/auditable personal agent with two unwired core mechanisms (envelope, floor) that must be fixed before Stages B/C are real. Stage A is buildable now; B is the budget; C is the moat and the risk. If skill-artifact transfer (A-P3) comes back flat, the honest floor is Stage A alone — real, defensible, smaller.

---

## 10. Messaging tests (by stage)

- **A (worker/champion):** "The proactive agent you own and can audit." / "Autonomous work, on the record, in your repo."
- **B (risk owner):** "Provable, erasable AI actions — your scope, your keys." / "Agent deployment your auditors can read."
- **C (team):** "Every agent gets better from what the others learned — and no one gets ranked for it." / "Git for how your team's work gets done."

---

## Appendix — inputs

- PM review + findings: `review/2026-07-12-pm-product-review.md`, `review/2026-07-12-pm-findings.md`
- Four research memos (demand/WTP, substrate race, transfer evidence, buyer/ICP): sources inline in v0.2 §9.
- Supersedes: `positioning-v0.2.md` (→ `v0.1.md`).
