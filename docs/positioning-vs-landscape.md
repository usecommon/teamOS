**`v0.2 — 2026-07-12`** *(POSITIONING — market/competitive context for Team OS. Not governing. Snapshot of the 2026 "agent control plane" landscape and where Team OS sits. Sources are external and dated; re-check before quoting in a raise.)*

# Team OS vs. the landscape — the emerging agent control surface

## The category is real, and it's forming now

"Agent control plane / control surface" became a named category in 2026 — the layer that deploys, operates, monitors, and governs AI agents:

- **IBM** defines an [agent control plane](https://www.ibm.com/think/topics/agent-control-plane) as "the system that deploys, operates, monitors and governs AI agents."
- **Microsoft Agent 365** hit GA May 2026 — agents get Entra identities, governed via Defender / Purview / Intune.
- **Cloud Security Alliance** runs an [agentic control plane](https://cloudsecurityalliance.org/blog/2026/04/29/securing-the-agentic-control-plane-key-progress-at-the-csai-foundation) working group; **Google DeepMind** published an [AI Control Roadmap](https://deepmind.google/blog/securing-the-future-of-ai-agents/).
- **Gardener** ([gardener.run](https://gardener.run/)) — an "Agentic Development Environment," the control layer for AI-accelerated *coding*.

The 2026 enterprise mandate, stated plainly: **do not scale agents until you can name, scope, monitor, approve, audit, stop, and recover from them.**

Team OS was built independently and lands squarely inside this category — with a **different philosophy** (control surface as *enabler*, not *cage*) and a **broader domain** (a person's whole job, not just code).

## The mandate, mapped to Team OS

| Mandate | Team OS mechanism |
|---|---|
| **Name** | Named fleet (`agents.json`); per-agent lineage |
| **Scope** | CLAUDE.md cascade + deny-by-default **allow policy** |
| **Monitor** | Observability ("nothing silent") + the Observatory |
| **Approve** | Candidate stage; auto-approve modes; boundary confirmation |
| **Audit** | Ten hash-chained ledgers; pre-act records |
| **Stop** | Circuit breaker (fleet-wide, human-only reset) + user **stop-rules** |
| **Recover** | Unwind (limited) + key-destruction erasure |

All seven — independently.

---

## Gardener — closest in spirit, opposite in philosophy

Gardener is the nearest neighbor: a *control layer* that keeps a project coherent as AI generates code faster than humans can review. Its skeleton matches ours almost exactly.

**Same skeleton:**

| Gardener | Team OS analog |
|---|---|
| Knowledge Mesh — project reality → navigable system map | Corpus + lineage + emergent topology (Observatory) |
| Project Truth Substrate — connected view from files, decisions, changes | Files-as-truth corpus + job graph |
| Knowledge Write-Back — accepted outcomes update memory | Candidate → promote; inbox → gate processor |
| Execution Layer — agents into a controlled workflow | Fleet + gates |
| Context-bundling, acceptance gates, traceability, versioning | Gates, ledgers, git |

**Where Team OS diverges — and it's most of what matters:**

1. **Domain.** Gardener governs *coding agents you point at code* ("made by vibecoder for vibecoders"). Team OS *is the worker* — a person's whole job across sources (email, Slack, deliverables), proactive.
2. **Emergence stance — opposite.** Gardener is explicitly conservative: *"containment through context curation; humans as decision-makers, not observers."* Team OS lets emergence run in the reversible interior, humans as **observers who can take it back**, control only at the irreversible boundary. **Gardener contains; Team OS enables-and-observes.**
3. **Proactivity.** Gardener reacts to what you direct. Team OS works **unprompted** (Day One Brief, loops).
4. **The fabric.** Gardener = single-project coherence. Team OS's whitespace = **cross-person skill transfer** — the human-team "agent fabric." Gardener has no team-transfer thesis.

Net: same architectural skeleton, discovered independently; a dev tool with a containment philosophy vs. a proactive team OS with an emergence philosophy.

---

## Gartner — validates three core bets, challenges one (and we answer it)

**✅ Proportional, not uniform, governance.** Gartner, May 2026: *["Applying uniform governance across AI agents will lead to enterprise AI agent failure"](https://www.gartner.com/en/newsroom/press-releases/2026-05-26-gartner-says-applying-uniform-governance-across-ai-agents-will-lead-to-enterprise-ai-agent-failure)* — classify agents across **autonomy levels, each a different trust boundary.** That is exactly Team OS's **envelope** (earned autonomy levels) + **reversible/irreversible split** + **three auto-approve modes.** We built proportional governance; Gartner names uniform governance as the failure.

**✅ The control plane must be vendor-independent.** Gartner on [AI Agent Management Platforms](https://xpander.ai/resources/ai-agent-management-platforms-gartner): *"the control plane cannot be owned by the same vendor that sells the agents, or the governance layer becomes a sales channel rather than a risk-management system."* Team OS's **owned inference (Plane A, can exclude Claude) + policy-neutral + files-as-truth** puts governance in *user-owned code*, not vendor SaaS.

**✅ Close the gap before the incident, not after.** Gartner: by 2027, ~40% of enterprises will demote/decommission autonomous agents due to governance gaps found *only after production incidents*. Team OS's **one falsifiable guarantee + pre-act ledger records** is designed so the gap is structural and checkable *before* the act, not discovered after.

**⚠️ Guardian agents — and why we're not deviating from them.** Gartner's [guardian agents](https://www.opsinsecurity.com/blog/gartner-market-guide-guardian-agents) *"monitor actions, enforce policies, and intervene when behavior deviates from intended goals."* That is deviation-detection. Team OS **keeps it** — and adds a layer guardian-only systems lack, via one principle:

> **Be deterministic about permitting; be semantic about stopping.**

The user's policy has **two sides**:

- **Allow-rules (permit side).** Which irreversible acts may cross the boundary. **Deny-by-default**, deterministic, model-free — because a wrong permit is *irreversible*. This is the layer pure guardian agents don't have; it's what closes the novel-harm gap that deviation-detection alone leaves open.
- **Stop-rules (halt side).** Goals and tripwires — *"if the agent deviates from goal G, halt."* Enforced by the concern detector / safety agent tripping the circuit breaker. This *is* guardian behavior, and it's kept in full — because a wrong stop is *reversible* (just resume), so it can afford the model's semantic judgment.

So Team OS is **guardian-agents-plus**: it monitors-and-stops on trajectory (guardian) *and* permits-only-known-safe on irreversibles (deny-by-default). Strictly more than a guardian, not a rejection of one. If the user writes "stop when the agent leaves goal G," it stops; if an irreversible act isn't allow-listed, it's denied — both from one policy.

---

## The differentiated position (one paragraph)

Team OS is an **agent control surface that treats control as an enabler, not a cage.** It is **proportional** (autonomy is earned per trust boundary, not uniform), **vendor-independent** (governance is user-owned code + owned inference that can exclude the model vendor), and **gap-before-incident** (one falsifiable guarantee, pre-act records). It **subsumes the guardian-agent pattern** (semantic stop-on-deviation) and goes past it with a **deterministic deny-by-default permit boundary**. And uniquely, it points the control surface at a person's **whole job across a human team** — with **cross-person skill transfer** as the wedge — rather than at a single codebase.

## Rebuttal — "but it runs on the vendor's harness"

The sharpest investor objection: *Gartner says the control plane can't be owned by the agent vendor, and Team OS runs on Claude Code — isn't your governance captured?* The prepared answer:

**One line:** *Claude Code is our runtime, not our control plane. Gartner's rule is about who owns the governance — ours is user-owned code in the user's own git repo, owned by no vendor at all.*

The unpack, when they push:

1. **Runtime ≠ control plane.** Your firewall rules aren't "owned by Intel" because they run on an Intel CPU; a bank's controls aren't AWS's because they run on AWS. Gartner's rule is about who owns the *governance*, not who provides the *compute*.
2. **Our control plane is literally files.** The gate, the ten ledgers, the allow/stop policy — plain files in the user's git repo, running as user-owned code. Anthropic doesn't write, host, or see them. Nothing for the vendor to wave through, because the vendor doesn't operate the governor.
3. **Owned inference removes the model dependence.** Plane A runs on the user's API key or a local model and can **exclude the Claude account entirely**. The inference behind the agents need not be the vendor's.
4. **Portability is the proof.** Only a thin adapter touches harness internals; swap runtimes by fixing the adapter, not the governance. Exit = `git clone`. A control plane you can walk out with is, by definition, not vendor-owned.
5. **The inversion — we are *more* independent than the analyst's own examples.** Microsoft Agent 365 and peers are still *someone's SaaS*: independent of the agent vendor, but still *vendor-owned governance*. Team OS's governance is owned by **no vendor at all** — your code, your repo, your keys. Pushed hard, the objection flips into the purest form of Gartner's own recommendation.
6. **The honest boundary (say it first).** If you *choose* the Claude account for inference, you depend on Anthropic for the **model** — but that is *buying the agent*, which Gartner explicitly permits; it is the *governance* that must stay independent, and it does. Plane A removes even that. A purchasing choice, not governance capture.

## Honest tensions

- **Runs on the harness.** See the rebuttal above — a nuance to explain, not a weakness, but be ready with the one-liner.
- **Contrarian on emergence.** The market is *fleeing* autonomous agency; "emergence you can see, bound, and take back" is a bet that a different posture beats retreat. Unproven until a dense deployment.
- **Density-gated.** The emergence payoff needs scale (FK7+); the near-term, buildable piece is the deny-by-default boundary + allow/stop policy, which needs no density.
