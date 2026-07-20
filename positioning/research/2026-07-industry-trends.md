# Agentic AI — Industry Trends (synthesis)

- **As of:** 2026-07-12. **Method:** web research (model: Claude Fable 5) across 14 threads, consolidated here.
- **Scope:** the market/competitive/academic backdrop for autonomous agents, agent control planes, and multi-human agent operation — the industry context that motivates Team OS, independent of the product.
- **✅ Verification status (pass run 2026-07-12 via web):** the category framing and most headline figures **CONFIRMED** against primary/secondary sources; **two figures CORRECTED** (Cursor ARR was stale; dev-adoption %); a few remain **UNVERIFIED**. Details in the **Verification pass** table at the end — check it before quoting any single number externally (deck, pitch, fundraise).
- **Sources consolidated:** `2026-07-12-control-plane-market-sizing.md`, `-control-plane-landscape.md`, `-agent-hq-deep-dive.md`, `-solo-agent-use-cases.md`, `-hermes-agent.md`, and threads 1–9 (distilled in `../positioning-v0.2.md §9`, `../positioning-v0.4.md §2–4`). Index: `README.md`.

---

## TL;DR — the eight trends
1. **The "agent control plane" is a newly-named, actively-forming category** — analyst-named late 2025, no Magic Quadrant/Wave yet.
2. **Observability ≠ control, and the money is still on observability** — vendors talk control, funding flows to eval/monitoring.
3. **Trust is falling *as* agents gain the power to act** — adoption up, trust down; proactivity got humbled.
4. **Coding is the dominant solo-agent use case and the only durable retention** — everything else is shallower.
5. **Runtime-security / action-gating consolidated hard** — heavy M&A; the "look inside the action" tools are mostly OSS.
6. **Harnesses/runtimes are commoditizing; the labs will commoditize the substrate next** (6–18 mo).
7. **Cross-human learning transfer and joint multi-human agent operation are shipped by no one** — named only in research.
8. **A regulatory floor is arriving** — EU AI Act traceability (enforcement Aug 2, 2026) makes tamper-evident logging table stakes.

---

## 1. The agent control plane — a category being born
- **Analyst-named, multiply, un-consolidated.** ✅ Gartner: **"AI Agent Management Platform (AMP)"** — *"the centralized control layer for heterogeneous enterprise agent ecosystems"* — from the **Oct 2025** note **"AI Vendor Race: AI Agent Management Platform: The Most Valuable Real Estate in AI"** (Gartner doc 7048898). AMP capabilities per Gartner: governance, security, compliance, operational oversight, performance monitoring, cost/ROI tracking, lifecycle management, marketplace controls (the earlier "six pillars" shorthand was imprecise — this is the actual list). Profiled in Gartner's Hype Cycle for Agentic AI, at the **Peak of Inflated Expectations**. **The independence thesis (verbatim-adjacent):** *"the control plane cannot be owned by the same vendor that sells the agents, or the governance layer becomes a sales channel rather than a risk management system"* — direct external support for Team OS's owned/independent stance.
- ✅ **Forrester: "agent control plane"** (Dec 2025) — infra that *"inventories, governs, orchestrates, and assures heterogeneous agents across vendors."* Forrester has **announced an evaluation of the market** ("Announcing Our Evaluation Of The Agent Control Plane Market") but **no Wave/scores published yet**; 79% of surveyed vendors call it a distinct category.
- **Forrester three-plane model:** build → orchestration → **control** (out-of-band governance sitting outside both). Community framing: *"observability tells you what happened; a control plane governs what can happen."*
- **Sizing (dispersed = pre-consensus):** ✅ Gartner's bet — **AMP spend ~$15B by 2029 vs <$5M today** (near-vertical curve); and **by 2027, 75% of enterprises will treat their agent-monitoring methodology as their most important AI tool, up from 1% today.** Adjacent: AI orchestration $11B→$30B by 2030; "AgentOps infra" $1.8B→$58B by 2034. A discrete "governance/control" line barely exists yet.
- **The whitespace:** every analyst frame is the **enterprise/IT buyer.** **No analyst-recognized individual/solo control-plane category exists** — unclaimed.
- **So what:** you can enter *during* category formation (12–24 mo before the first MQ/Wave) and shape vocabulary — and own the solo segment nobody has named.

## 2. Observability ≠ control — money still on observability
- Vendors and VCs converge on the *control* need (permissions, spend caps, audit, approvals), but funded companies are still eval/observability: LangChain/LangSmith **$125M at $1.25B** (Oct 2025), Arize $70M, Braintrust $80M (Feb 2026); AgentOps.ai only $2.6M pre-seed.
- Canonical AgentOps tools **observe, don't gate** (Langfuse, LangSmith, Arize/Phoenix, Datadog LLM Obs). Exceptions that actually block on a tool call are new and SaaS-only (Datadog AI Guard).
- **So what:** the gap between "talking control" and "shipping control" is the opening — especially *action-level* control that inspects a call before it executes.

## 3. Trust is falling as agents act
- ✅ **Stack Overflow 2025 Developer Survey (49k respondents):** AI adoption rose to **84%** even as **trust in AI accuracy fell 40% → 29% YoY** — more devs now actively distrust accuracy (46%) than trust it (33%). **66%** say they spend more time fixing "almost-right" AI code; that "almost right, but not quite" failure is the #1 frustration (45%). People use agents they don't trust. *(The "~90% use / 51% daily" figures cited earlier were a different source and are superseded by SO 2025's 84%.)*
- **Proactivity got humbled:** consumer "always-on" bets retreated (Pulse sunset, Recall retreat). The safe-workflow consensus is defensive: never let an agent commit to main, feature-branch isolation, human review, read-only DB, pipe everything to a SIEM.
- Churn: agents produce more code *and* more rework (GitClear: churn 3.1%→5.7%). Agent HQ's headline features are governance, not capability.
- **So what:** the sharpest unmet pain is **trust/control as agents shift from suggesting to acting** — the pain a control plane addresses.

## 4. Coding is the dominant solo use case (and the only strong retention)
- **Revenue:** ✅ Claude Code **~$2.5B run-rate (Feb 2026)** — and, per later secondary blogs, climbing toward **~$8B by May 2026** (verify; secondary sources only). ⚠️ **Cursor (re-corrected — timeline matters): ~$1B ARR late 2025 → ~$2B (Feb 2026) → ~$4B (June 2026, ~$2.6B enterprise).** The doc's first "~$2B" ≈ Feb 2026; the second pass's "~$4B late 2025" was wrong on *timing* — $4B is June 2026. Current (mid-2026) figure to cite: **~$4B**. No non-coding agent is within an order of magnitude on willingness-to-pay.
- **Frontier = solo multi-agent orchestration, and it's coding:** Devin Desktop (up to 8 parallel agents in worktrees), GitHub Agent HQ mission control. Orchestration primitives (worktrees, PRs, CI) are *code* primitives.
- **Non-coding tail is wide but shallow/supervised:** >90% of Claude Cowork usage is non-software but young and session-based; ChatGPT agent mode — 73% of Plus users exhaust caps week one (project-runner, not retained).
- **Retention:** coding agents show the only durable retention (Copilot 81% same-day activation; Claude Code ~28% primary share).
- **So what:** the beachhead is the developer orchestrating coding agents — the mainstream user nervous about letting agents push to prod (trust at 29%), not a niche "privacy" persona.

## 5. Action-gating / runtime security — consolidated, mostly OSS
- **Near-total M&A in ~14 months:** Invariant→Snyk, Lakera→Check Point, Prompt Security→SentinelOne, Protect AI + Portkey→Palo Alto, Robust Intelligence→Cisco.
- **The genuine "look inside the action" tools are overwhelmingly OSS:** Invariant Guardrails/MCP-scan (arg-value + dataflow, **MCP-scoped**), Solo.io agentgateway, Docker MCP Gateway, **Claude Code PreToolUse hooks** (Claude-Code-locked).
- **The four-corner test** — (a) action-level payload gating + (b) owned/self-hosted + (c) harness-agnostic + (d) solo-usable: **no product holds all four.** Closest solo analogs each miss one: Conductor (approvals, **no payload inspection**), Invariant (**MCP-only**), raw CC hooks (**CC-locked**). Enterprise (Glean, AWS AgentCore, Google Gemini Ent.) miss owned and/or solo.
- **Identity is consolidating as a control layer** (Okta for AI Agents, Astrix→Cisco, Aembit, CyberArk) — governs *credentials*, not payloads.
- **So what:** the payload-inspecting, owned, harness-agnostic, solo quadrant is real whitespace; the risk is incumbents pushing down-market, not saturation.

## 6. Runtimes commoditizing; the substrate is next
- **Hermes Agent** (Nous Research, MIT, **~$50M Paradigm, Apr 2025**): a self-hosted, model-agnostic **harness** with a self-improving skill loop, cron proactivity, 40+ tools. Capability-ahead; **no trust stack** (no audit ledger, no payload gate, no proven deletion); explicitly **anti-restriction** ("aligned to you, not corporate policy").
- Harnesses (Claude Code, Cursor, Hermes) sit at the same layer; capability is racing and cheapening.
- **The substrate race:** labs are expected to **commoditize the memory/skill substrate in 6–18 mo.** A store is not a moat.
- **So what:** don't compete on capability — sit *on top of* the most capable runtime and add what none has (governance + team operation). The durable edge is the **transfer/federation + measurement layer**, not a store.

## 7. Joint multi-human operation & cross-human transfer — unshipped
- **Team spaces are "agent manager" (one human runs many agents) or "agent admin" (IT governs a fleet top-down)** — never *joint operation* (a team operating agents together). True across Claude (no "Ultra"; shared artifacts + admin console), OpenAI/Google/MS, and non-AI vendors (Slack/Notion/Linear/Rovo/Devin = shared visibility/admin only).
- **Joint multi-human agent control is named only in research** — CHAP (arXiv 2606.09751) — shipped by no product.
- **Cross-human *learned* transfer:** emerging and narrow — works for executable, task-general **skill artifacts**, flat-to-negative for personalization ("my-voice"). Labs ship shared memory **inside one account**, not cross-account.
- **So what:** joint operation and cross-account skill transfer are the genuine open frontier — and the hardest to fake (needs real second-person data; can't be simulated).

## 8. A regulatory/compliance floor is arriving
- ✅ **EU AI Act Art. 12 (high-risk obligations broadly enforceable Aug 2, 2026):** automatic recording of traceability-relevant events over the system's lifetime, enabling post-hoc reconstruction of individual AI-assisted decisions; **≥6-mo retention** (24 mo for biometric/law-enforcement). Penalty up to €15M or 3% of worldwide turnover. *(Note: the statute mandates automatic logging + traceability/integrity; it does not literally prescribe "cryptographic tamper-evidence" — that's the implementation best-practice, and no technical standard is finalized yet — prEN 18229-1 and ISO/IEC DIS 24970 are the drafts to watch.)* Practical gap: off-the-shelf APIs don't emit reconstruction-grade decision records by default, and logs held only by a vendor without your own copy leave the deployer exposed.
- Off-the-shelf AI APIs don't produce compliant decision records by default; the deployer owns the gap. SOC 2 / procurement increasingly demand the same records outside EU scope.
- Buyer signal: the trust stack is a **painkiller at the regulated boundary, a vitamin at small scale**; the economic buyer is the **org-side risk owner** (security/platform/CISO), plus EU works councils. Worker = champion, not payer.
- **So what:** tamper-evident, exportable, owned records move from "nice" to "required" at the regulated boundary — a structural tailwind for owned/self-hosted governance.

## 9. Academic corroboration + the three risks
- **Design agrees with the evidence** on the core product bets (proactivity, provenance, skill compilation). Grounding: PROBE (proactivity ceiling ~40% end-to-end → **discover-and-propose, not discover-and-execute**), MemLineage (crypto provenance → memory-poisoning ASR→0), Collaborative Memory (multi-user asymmetric access), τ-bench/CLEAR (measurement).
- **Three risks to design against:** (1) **self-threat of anticipatory help** (unrequested help can dent competence signaling), (2) **Goodhart floor** (if acceptance signals read as surveillance, humans game them and the training data rots — enforce "measure agents, not people" structurally), (3) **complacency/deskilling** (automate toil, preserve texture; propose, don't presume).
- **So what:** the trends validate the direction; the risks say the *governance and no-individuation* posture is load-bearing, not decoration.

---

## Verification pass — results (2026-07-12, web)

| Claim | Status | Finding / source |
|---|---|---|
| Gartner **"AI Agent Management Platform (AMP)"** term + definition | ✅ **Confirmed** | Gartner doc 7048898 ([gartner.com](https://www.gartner.com/en/documents/7048898)); corroborated by [xpander](https://xpander.ai/resources/ai-agent-management-platforms-gartner), [Parloa](https://www.parloa.com/guides-ebooks-and-reports/gartner-ai-agent-sprawl/) |
| Note title **"…The Most Valuable Real Estate in AI"** (Oct 2025) | ✅ **Confirmed** | Full title: *"AI Vendor Race: AI Agent Management Platform: The Most Valuable Real Estate in AI"* |
| **$15B by 2029 vs <$5M today** | ✅ **Confirmed** | Verbatim in Gartner note; +bonus stat *"by 2027, 75% … up from 1%"* |
| The **"six pillars"** list | ⚠️ **Corrected** | Gartner's actual capability list is broader (governance, security, compliance, oversight, monitoring, cost/ROI, lifecycle, marketplace) — "six pillars" was imprecise shorthand; fixed in §1 |
| **Forrester "agent control plane"** (Dec 2025) + three-plane model | ✅ **Confirmed** | [Forrester: "Announcing Our Evaluation Of The Agent Control Plane Market"](https://www.forrester.com/blogs/announcing-our-evaluation-of-the-agent-control-plane-market/) + ["…Robust Standards Stack"](https://www.forrester.com/blogs/agent-control-planes-still-need-a-robust-standards-stack/) |
| **LangChain $125M at $1.25B** (Oct 2025) | ✅ **Confirmed** | [Fortune](https://fortune.com/2025/10/20/exclusive-early-ai-darling-langchain-is-now-a-unicorn-with-a-fresh-125-million-in-funding/), [SiliconANGLE](https://siliconangle.com/2025/10/20/ai-agent-tooling-provider-langchain-raises-125m-1-25b-valuation/) |
| **Nous/Hermes — $50M Series A, Paradigm, Apr 2025** | ✅ **Confirmed** | [Fortune](https://fortune.com/crypto/2025/04/25/paradigm-nous-research-crypto-ai-venture-capital-deepseek-openai-blockchain/), [The Block](https://www.theblock.co/post/352000/paradigm-leads-50-million-usd-round-decentralized-ai-project-nous-research); $1B token valuation |
| **Claude Code $2.5B run-rate (Feb 2026)** | ✅ **Confirmed** | [MindStudio](https://www.mindstudio.ai/blog/claude-code-2-5-billion-annualized-revenue-saas-comparison); later ~$8B (May 2026) per secondary blogs — verify before quoting |
| **Cursor ARR** | ⚠️ **Corrected twice** | Accurate timeline: ~$1B late 2025 → ~$2B Feb 2026 → **~$4B June 2026** ([Forbes](https://www.forbes.com/sites/richardnieva/2026/06/08/cursor-4-billion-annualized-revenue/), [getlatka](https://getlatka.com/companies/cursor.com)); cite ~$4B now; fixed in §4 |
| **Dev trust 40% → 29% YoY** | ✅ **Confirmed** | [Stack Overflow 2025 Developer Survey](https://survey.stackoverflow.co/2025/ai/) (49k respondents); adoption 84%, not ~90% (fixed in §3) |
| **EU AI Act Art. 12, enforce Aug 2 2026, ≥6-mo retention** | ✅ **Confirmed** (one caveat) | [artificialintelligenceact.eu/article/12](https://artificialintelligenceact.eu/article/12/); statute mandates auto-logging + traceability, **not** literal "cryptographic tamper-evidence" (softened in §8) |
| **M&A pairings** — Snyk←Invariant, CheckPoint←Lakera ($300M), SentinelOne←Prompt Security ($250–300M), PaloAlto←Protect AI (>$500M) | ✅ **Confirmed** | [govinfosecurity](https://www.govinfosecurity.com/blogs/ai-security-goes-mainstream-as-vendors-spend-heavily-on-ma-p-3953), [CSO](https://www.csoonline.com/article/4058653/check-point-acquires-lakera-to-build-a-unified-ai-security-stack.html), [SiliconANGLE](https://siliconangle.com/2025/08/05/sentinelone-acquires-ai-security-startup-prompt-security/) — 5 vendors spent ~$1.31B in one Sept wave |
| **Arize $70M Series C; Braintrust $80M Series B** | ✅ **Confirmed** | Arize $70M (Feb 2025, Adams Street) [Arize](https://arize.com/blog/arize-ai-raises-70m-series-c-to-build-the-gold-standard-for-ai-evaluation-observability/); Braintrust $80M @ $800M val (Feb 2026, Iconiq) [Axios](https://www.axios.com/pro/enterprise-software-deals/2026/02/17/ai-observability-braintrust-80-million-800-million) |
| ChatGPT **"73% exhaust caps week one"** | ✅ **Confirmed** (soft sourcing) | The 40-msg Plus quota; stat recurs across secondary analyses (~5k sessions) — directional, secondary sources only |
| **Portkey←Palo Alto**; **Robust Intelligence←Cisco** | ◻️ **Unverified** | not confirmed this pass (Protect AI←Palo Alto *is* confirmed); check before citing these two pairings |
| Product GA dates (MS Agent 365, ServiceNow, Agent HQ) | ◻️ **Unverified** | "announced ≠ shipping" — confirm GA before relying |

**Bottom line (after two verification passes):** every load-bearing claim — the named category, the note title, the $15B TAM signal, the funding rounds, the M&A wave, the trust decline, the regulatory floor — **holds**. Corrections made: **Cursor ARR** (now correctly ~$1B late-2025 → ~$2B Feb-2026 → **~$4B Jun-2026**, after two wrong attributions), **dev adoption** (~90%→84%), the loose Gartner **"six pillars"** label, and the over-stated **Art. 12 "cryptography"** detail. Pass 2 cleared the M&A pairings, Arize/Braintrust rounds, and the ChatGPT-73% stat. Only two items remain ◻️: the **Portkey←Palo Alto / Robust Intelligence←Cisco** pairings and **product GA dates**. The **directional trends** are safe to state as trends.
