# Team OS — Positioning Statement

- **Version:** v0.2
- **Date:** 2026-07-12
- **Status:** Research-informed working draft. Supersedes v0.1. Four gating research threads (demand/WTP, substrate race, transfer evidence, buyer/ICP) are now folded in; §9 summarizes them with sources.
- **Changed since v0.1:**
  1. **Buyer corrected** — the paying buyer is the *org-side risk owner*, not the worker. Worker-sovereignty is a trust/retention/recruiting asset and an EU-works-council purchase criterion, not the lead reason anyone pays. (v0.1 over-weighted "moat on sovereignty" as a buy reason.)
  2. **Lead corrected** — lead with *initiative* (painkiller); the trust stack is a *vitamin* at small scale and a *painkiller* only at the regulated boundary, where it becomes the upsell.
  3. **Transfer claim scoped** — cross-user transfer works for *executable, task-general skill artifacts*, not personalized/"my-voice" work (flat-to-negative). Narrowed accordingly.
  4. **Moat relocated** — from "sovereignty" broadly to the *transfer + measurement + cross-account-federation layer* built atop whatever memory substrate the labs commoditize, plus ownership/no-surveillance for the buyers who actually pay for those.

---

## 0. The trap we are steering away from

Calling Team OS a **"proactive personal assistant"** files it next to Lindy, ChatGPT, Copilot, Superhuman — where the unit of value is *"it drafts my email,"* every incumbent ships it, and it's priced to zero. The repo's architecture doc warns against exactly this. We move **up the value stack** (from feature to infrastructure) and, over time, **toward the team** (from personal tool to compounding layer) — but staged by what the evidence supports *today*.

---

## 1. Positioning is staged, not single. Three altitudes, three buyers.

The single biggest v0.2 change: there is no one positioning line, because the near-term buyer, the expansion buyer, and the long-game bet are different people with different pain. Trying to say all three at once is what pushes it back into "assistant."

| Stage | Who buys | The pain (painkiller) | What we say |
|---|---|---|---|
| **A — Wedge (now)** | Technical IC / small dev team (bottom-up, capability-led) | "Recurring work I have to assemble by hand" | **"The proactive agent you own and can audit."** Sold on *initiative* — drafts arrive done, on the record, in your repo. Ownership/auditability is the reason to *trust and stay*, not the headline. |
| **B — Expansion (upsell)** | Org-side risk owner (security / platform-eng / CISO / compliance) at **regulated or IP-sensitive** orgs | "We're deploying agents on real data and can't prove what they did or delete it" | **"Autonomous work that's provable and erasable, in your own scope."** Here the trust stack *is* the painkiller (EU AI Act Art. 12 logging, GDPR erasure, air-gapped, keys-are-yours, exit=clone). |
| **C — The bet (long game)** | The team, via the risk owner | "Our know-how lives in one person's head / one engineer's session" | **"Every agent gets better from what the others learned — measured, and no one gets ranked for it."** The compounding skill loop. Gated on A-P3 evidence (§6). |

**Near-term headline (Stage A):** *The team agent layer you own — drafts arrive done, every action on the record, nothing leaves your repo.*

---

## 2. Category framing: not an assistant, not an admin console; a sovereign cooperative (long game)

Three shapes of "team AI tool." Two are taken/compromised; the third is open — but is the *destination*, reached through Stage A.

| Shape | Example | Why not us |
|---|---|---|
| **Shared bot** — one agent everyone queries | Dust org agents, shared Slackbot | Collapses into memory/RAG; no individual ownership |
| **Admin console** — one manager governs everyone's agents | MS Agent 365, OpenAI Frontier | *Control over* people; top-down; the surveillance shape |
| **Sovereign cooperative** — individually-owned agents sharing *skill improvements* through a governed, consent-based, non-surveilling channel | *(open)* | **This is Team OS's destination.** |

Mental model: **"git + CI + an audit log for autonomous work, with a shared skill library."** The assistant is the delivery vehicle; the product is governed initiative + the cross-agent improvement loop.

---

## 3. The strategic thesis in one move (revised)

**Sell the initiative. Moat the transfer layer and the ownership. Upsell the governance into regulated teams.**

- **Initiative is the painkiller** people adopt for (Stage A). Trust stack alone is a vitamin at small scale — do not lead with it there.
- **The durable moat is the transfer layer, not a memory store.** The labs will commoditize the *substrate* (team memory as shared context) within 6–18 months (Anthropic's Managed-Agent memory + open request #38536 point straight at it). What they are structurally disinclined to build — because it breaks "keep the data inside one account" — is **cross-account, measured, privacy-preserving skill transfer with a promotion gate.** Build to sit *on top of* whatever substrate they ship.
- **Governance is the expansion painkiller** (Stage B): the same trust stack that's a vitamin for a solo dev is a legal precondition for a regulated org. That's the upsell path, and it's where the real budget is.
- **Ownership + no-surveillance are the buyer-specific closers** for the two segments that actually pay for them: regulated/IP-sensitive orgs (own-your-keys, air-gapped, exit=clone) and EU works-council teams (no per-person individuation = a co-determination / AI-Act requirement).

---

## 4. What we sell, by buyer (value stack, corrected)

1. **Initiative that compounds (the through-line).** Drafts/loops/proposals that originate work. Stage A adopts on this alone.
2. **Provable, erasable autonomous work (the expansion painkiller).** Payload-gated, tamper-evident ledgers, lineage, provable deletion — a *legal precondition* for regulated agent deployment, priced accordingly (comps: air-gapped code assistants at ~$39/user/mo; Agent 365 governance $15/user/mo).
3. **Measured skill transfer across the team (the bet/moat).** Executable skills that improve from real use and propagate through a default-deny promotion gate — the one thing no lab ships and the labs won't (cross-account). Unproven; §6.
4. **Ownership + non-surveillance (buyer-specific closers).** Exit=clone and structural no-individuation — decisive for regulated orgs and EU works councils; a trust/retention tiebreaker (Obsidian/n8n/Bitwarden pattern) for technical prosumers.

---

## 5. Why now / why us

- Market bifurcated into **"act" (everyone)** and **"govern" (Microsoft Agent 365, OpenAI Frontier)** — nobody ships proactive + owned + auditable + leavable under user ownership.
- **Regulatory forcing function:** EU AI Act Art. 12 tamper-evident logging enforceable **Aug 2, 2026** (fines to €15M / 3%); GDPR erasure; Gartner projects a **billion-dollar AI-governance market**. This is what turns Stage B's trust stack from vitamin to painkiller.
- **The transfer layer is unoccupied and just proven in the lab:** `FederatedSkill` (arXiv 2606.03143) exchanges *semantic skill patches* across clients, privacy-preserving, personalized, **+44% success / −37% cost**. Mechanism emerging in research (12–24mo from product), shipped by no one.
- **Post-lock-in moment:** Limitless/Rewind's shutdown (users stranded) is the market's own cautionary tale for exit=clone.

---

## 6. The transfer claim, scoped honestly (this is the make-or-break)

The evidence says the compounding-team bet is real **only for a subclass**, and is otherwise flat-to-negative. Positioning must not overreach.

- **Works:** executable, task-general skill *artifacts* on a shared tool surface (Voyager: a skill library lifted a *different* agent 0/3→1–2/3). A "pull-the-deploy-metrics" or "PR-description" skill is this shape.
- **Fails (flat-to-negative):** personalized, tacit, "my-voice/my-context" improvements. "Skill is Not One-Size-Fits-All" (arXiv 2605.30723) — transfer is *negative by default* across even a model gap without active re-alignment. The heavy-editing PM persona is precisely the null case.
- **Strongest adjacent proof:** Brynjolfsson, Li & Raymond (QJE 2025, n=5,179) — AI trained on top performers' transcripts lifted others **+14% avg, +34% novices, ~0 for top performers** — but shared-task, via pooled retraining, not per-user skill promotion.
- **Design consequences:** gate promotion on **artifact-shaped skills first**; **instrument for negative transfer from day one**; treat any cross-*user* lift as unproven until a **two-different-users, non-shared-task** experiment reproduces it. That experiment is **the cheapest differentiated evidence in the market — nobody has published it.** It *is* the A-P3 gate.

---

## 7. Beachhead & sequencing

- **Beachhead: technical IC / small dev team.** CLI-first fits them; adoption is bottom-up on capability. Do **not** market to non-technical PMs until a GUI/hosted install exists — the CLI excludes them by construction (sim §3).
- **Cold-start on-ramp: the MCP door + cloud routines (path b)** for subscription-only users — value in minutes — then **graduate to the local runtime (path a)** for the full gated posture. Narrative: *easy on-ramp → owned runtime.* (Caveat: path b is reduced-trust/disclosed; only Team OS door actions are gated there.)
- **Expansion motion:** land bottom-up with a dev team inside a regulated/IP-sensitive org → the security/platform owner adopts it org-wide for the trust stack (Stage B) → the team-transfer loop (Stage C) becomes the expansion/retention engine.
- **EU works-council angle** is a distinct, high-conviction secondary: "no individuation surface" is a *purchase criterion*, not a sentiment, there.

---

## 8. Proof obligations (what must be true; updated)

| Claim | Status | Gate |
|---|---|---|
| Initiative compounds across people (A→B) — **for artifact-shaped skills** | ⚠️ plausible, unproven | FK7/A-P3: two-different-users, non-shared-task, measured lift — needs real collaborators |
| The core loop is felt by the user | ❌ broken today | Envelope inert at the gate (review §4 P0) |
| We can count accepted unprompted work | ❌ broken today | Initiative floor un-computable as orchestrated (review §4 P1) |
| Regulated buyers will pay for the trust stack | ✅ supported | Art. 12 / GDPR forcing function; air-gapped comps at $39/user |
| A paying ICP exists | ✅ supported | Org-side risk owner (regulated/IP-sensitive); EU works councils; technical prosumers |
| Worker-sovereignty is a *lead buy reason* | ❌ refuted | It's a trust/retention/recruiting asset + EU-works-council criterion, not a standalone driver |

**Honest framing:** today Team OS is a strong *owned, auditable personal* agent with two unwired core mechanisms (envelope, floor) that must be fixed before any of Stages B/C are real. Stage A is buildable now; Stage B is the budget; Stage C is the moat and the risk. If artifact-skill transfer (A-P3) comes back flat, the honest floor is Stage A alone — "the proactive agent you own and can audit" — real, defensible, smaller.

---

## 9. Research findings that shaped v0.2 (with sources)

- **Demand/WTP:** Trust stack is a **painkiller at the enterprise/regulated boundary, a vitamin at individual/small-team scale.** EU AI Act Art. 12 ([artificialintelligenceact.eu/article/12](https://artificialintelligenceact.eu/article/12/)); Gartner billion-dollar governance market ([gartner 2026-02-17](https://www.gartner.com/en/newsroom/press-releases/2026-02-17-gartner-global-ai-regulations-fuel-billion-dollar-market-for-ai-governance-platforms)); CIOs won't fund governance without ROI ([CIO](https://www.cio.com/article/3989224/ai-governance-platforms-wait-for-customers-to-catch-up.html)); consumer privacy WTP ~$1–2 ([Springer](https://link.springer.com/article/10.1007/s40812-022-00221-5)).
- **Substrate race:** Cross-human *learned* transfer shipped by no one; Anthropic Managed-Agent memory is workspace-scoped agent-to-agent ([claude.com/blog/claude-managed-agents-memory](https://claude.com/blog/claude-managed-agents-memory)); shared-team-memory request open ([#38536](https://github.com/anthropics/claude-code/issues/38536)); durable edge = the transfer/federation layer; `FederatedSkill` ([arXiv 2606.03143](https://arxiv.org/pdf/2606.03143)).
- **Does transfer work:** EMERGING, narrow. Voyager cross-agent reuse ([arXiv 2305.16291](https://arxiv.org/abs/2305.16291)); negative-by-default without re-alignment ([arXiv 2605.30723](https://arxiv.org/abs/2605.30723)); Brynjolfsson QJE 2025 human→human via AI ([arXiv 2304.11771](https://arxiv.org/abs/2304.11771)).
- **Buyer/ICP:** Real paying buyer is the **org-side risk owner** (regulated/IP-sensitive); air-gapped comps $39/user ([IntuitionLabs](https://intuitionlabs.ai/articles/enterprise-ai-code-assistants-air-gapped-environments)); EU works-council co-determination on monitoring ([compound.law](https://compound.law/en-DE/compliance/ai-employee-monitoring/)); prosumer ownership converts on top of capability (Obsidian ~$25M ARR / n8n $40M ARR).

---

## 10. Messaging tests (revised, by stage)

- **A:** "The proactive agent you own and can audit." / "Autonomous work, on the record, in your repo."
- **B:** "Provable, erasable AI actions — in your own scope, with your own keys." / "Agent deployment your auditors can read."
- **C:** "Every agent gets better from what the others learned — and no one gets ranked for it." / "Git for how your team's work gets done."

---

## Appendix — inputs

- PM review + findings: `review/2026-07-12-pm-product-review.md`, `review/2026-07-12-pm-findings.md`
- Sim + prior memos: `review/sim-2026-07-12-pm/qualitative-inputs.md`
- Four research memos (demand/WTP, substrate race, transfer evidence, buyer/ICP): in-conversation, 2026-07-12 (sources inline in §9)
- Supersedes: `positioning-v0.1.md`
