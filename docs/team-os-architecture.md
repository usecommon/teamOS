<!-- VERSION: v3.0 | 2026-07-10 | constitution — frozen mainline, 16 sections | History: v1.0 §1-13 → v1.5 §14 → v2.0 four-council remediation (§15, §7.7, §5.3, Gate fixes) + §16, §3.4/3.5, identity claim → v2.5 X-findings ports (§14.0, routing×disclosure, two-person integrity) → v3.0 round-2 ports (§15.10 residual, §14.3 scope) -->
**`v3.0 — 2026-07-10`** *(constitution — frozen mainline, 16 sections)*

# Team OS — Working Architecture Document
*Consolidated from research sessions, July 2026. Living document.*

---

## 1. Concept & Thesis

**Identity claim (read this before filing the product in a category):** Team OS is a **proactive, action-driven system — it works on its principal's behalf without being asked.** Memory, corpus, and measurement are how it knows and learns; they are the organs, not the organism. The product is the initiative: drafts that arrive done, loops that fire on the world's schedule, proposals nobody requested, commitments fulfilled while the principal sleeps — under gates, on the record, improving across the fleet. This is a structural distinction, not an emphasis: request-response systems (including every memory/RAG MCP) can only answer; Team OS has a runtime that *originates*. Its KPIs were always action metrics — acceptance rate, edit distance, unmodified-send rate, commitment integrity, interrupts-per-week; recall/retrieval metrics are internal diagnostics only, never headline KPIs. *Others remember so you can ask better questions; this works so you don't have to ask.*

**Team OS** is an organizational operating system in which:

1. **Every user has a personal agent that acts as their representative** — to them, and to other users' agents.
2. **The OS syncs communications and knowledge across all teams** — individual productivity compounds into organizational intelligence.
3. **Performance of skills, MCPs, and agents (never of users) is measured, compiled, and redistributed** across the fleet so every agent improves from every agent's experience.

### Positioning against the landscape

| Pillar | Research maturity | Market maturity | Verdict |
|---|---|---|---|
| 1. Representative agents | Active subfield (AI delegates, LLM-X, delegation tokens) | Early products (Read AI Digital Twin); assistants ≠ representatives | Validated, trust problems unsolved |
| 2. Cross-team knowledge sync | Formal blueprint exists (Collaborative Memory) | Well-funded competitor thesis (Dust "multiplayer AI") | Crowded; differentiate on *personal agents, collective learning* |
| 3. Compiled performance sharing | Fragments exist (skill libraries, failure taxonomies, observability) | **Nobody assembles the loop** | **White space — the defensible core** |

Key structural distinction vs. Dust et al.: they solved compounding by **collectivizing agents** (shared functional agents per team). Team OS keeps **agents personal** and **collectivizes the learning**.

The industry validation for pillar 3: surveyed agent builders report evals under-deliver because keeping them current is impossible — offline suites are snapshots of past traffic. Team OS inverts this: **production is the eval**, failures auto-generate the regression set, fixes redistribute across the fleet.

---

## 2. Task Model

Four delegation classes; the class determines measurement, oversight, and interaction design.

### Class A — Looped / scheduled (autonomous, recurring)
Daily digest · weekly update generation · meeting prep & debrief packets · status sync to stakeholders · inbox/Slack triage · tracker hygiene · decision/knowledge capture · metric & experiment anomaly watch · calendar defense.
**Property:** same task, repeated daily, across every agent → production *is* the pass^k harness. **Measurement beachhead.**

### Class B — Delegated one-shot (human-initiated, human-consumed)
Research/scouting · document & spec drafting · spec review vs. templates · data pulls & experiment readouts · "who owns X" resolution · artifact scaffolding · option analysis.
**Key metric:** edit distance between draft and shipped version — free to collect, doubles as training signal.

### Class C — Representative (agent-to-agent; the novel class)
Answering peer-agent queries on the principal's behalf · meeting-time negotiation · knowledge brokering under disclosure policy · commitment tracking & status reporting · pre-meeting consensus mapping · escalation routing.
**Property:** measurement must be invented (see §4.4). The heart of the concept and its research-grade contribution.

### Class D — Fleet / system (the OS itself)
Skill performance compilation · cross-agent skill redistribution · context freshness maintenance · permission/policy enforcement · exploration-budget management.

---

## 3. Knowledge Architecture: Corpus & Hierarchy

### 3.1 Scoped corpus with cascade semantics

Five nested scopes: **company → division → org → team → individual**. Each scope holds three object types:

- **Context** — what exists and matters at this level. At team scope this is the *team corpus proper*: decisions, specs, operating norms, glossary, active workstreams.
- **Profile** — at individual scope: role, relationships, priorities, voice. At team scope: roster, ownership map, rituals. Upward: org charters, division strategy, company principles.
- **Experience** — output conventions per scope (division spec template, team update format, company tone).

An agent's working context = composition of its full path down the tree, narrower scope overriding broader (CLAUDE.md-style cascade: enterprise → project → user).

### 3.2 Corpus design rules

1. **Lineage-bearing store, not a wiki.** Every entry carries memory-write metadata (author, source type, evidence, transformation, confidence, update history — see §5, Ledger 3). Team knowledge is queryable *and* auditable.
2. **Promotion gates govern upward flow.** Individual learnings are *proposed* to team scope, not auto-written. Promotion by curator role or endorsement threshold (N principals' agents independently confirm). Asymmetric access-control semantics (per Collaborative Memory) given an org-chart shape.
3. **Scope sets disclosure defaults.** Same-team agents share corpus knowledge freely; cross-org requests hit explicit disclosure policy. Cross-scope brokering is a designed path, not an accident (see §8.3).
4. **Directory-first indexing.** The primary index is *who knows what* (transactive memory), with content hanging off it. "Who owns X / who solved Y" resolution is the corpus's killer query, not full-text search.

### 3.3 Corpus mechanics (design rules from the PKM / hypertext / PKG lineage)

1. **Links computed, never stored** (Obsidian pattern): the corpus repo stays plain markdown; backlink/graph indexes are derived and rebuildable — portability costs nothing.
2. **Block-level atomicity** (Roam pattern): lineage, confidence, and citations attach to atoms, not pages; a promoted rule cites the exact block of evidence.
3. **Unlinked-reference detection** as the scout's cheapest trick: string/entity matching proposing links nobody drew — nearly free, decades-proven.
4. **Typed entries** (Tana supertag pattern): `decision / definition / owner / norm` as schema-on-write, making the corpus queryable rather than merely searchable; aligns with bottom-up schema induction in the LLM-KG literature.
5. **Navigation-first retrieval** (PIM's core empirical finding: people prefer navigation over search in personal collections): the corpus needs a browsable shape humans can walk, not only an embedding index agents can query — trust is built by seeing the structure.
6. **Entity resolution as a first-class compiler stage** (KG-construction surveys: LLM-built graphs suffer duplicate entities, ungrammatical names, wrong relation semantics): dedup and canonical naming decide whether the corpus is a knowledge graph or a hairball.

Lineage grounding: Memex → hypertext → MyLifeBits (capture-everything without structure failed to become the memex → **compile, don't pile**); the PIM field (keeping / finding / meta-level activities; six senses of personal information); Zettelkasten (independently converged upon by agentic-memory research, e.g. A-MEM); Personal Knowledge Graphs as the formal discipline (Balog & Kenter research agenda; ecosystem survey & roadmap); GraphRAG/agentic-traversal retrieval (hybrid full-text + embeddings + multi-hop graph search, agent-driven).

### 3.4 Sub-teams, mixed roles & scope topology

**Two orthogonal axes:** *scope* is where you sit (which corpus cascade composes into your agent); *role template* is what you do (§10.3). A cross-functional team is one team scope + N different templates — one shared truth, rendered per role via absorptive-capacity translation (§8.2): the same decision entry surfaces as API implications to the engineer's agent and stakeholder-narrative implications to the PM's. Mixed-role teams are the architecture's native habitat, not an edge case: cross-role Class C exchange (PM's agent ↔ engineer's agent on build status) is the highest-value A2A traffic, and role-pair calibration / cross-role protocol efficacy are Tier-3 patterns a homogeneous team cannot generate. **Pillar 3 at full value requires role heterogeneity.**

**Sub-teams: the cascade nests.** Squads/pods are additional scope nodes (`… → team → squad → individual`); Gate 5 subsidiarity already routes knowledge to the narrowest applicable node; squad-specific conventions live at squad scope and promote upward through the same gates when both squads need them.

**The scope-vs-project rule (anti-proliferation discipline).** Every scope costs context weight (open Q7 compounds with tree depth), curator overhead, and disclosure-policy surface — so: **scopes are for stable social units; projects are for ephemeral ones.** Standing identity + own rhythms + outlives current work (squad, platform pod) → scope node. Workstream, launch team, incident response, hiring loop → **project context**: a shared-context bundle attached to work objects (§7.6) with its own disclosure policy and a TTL; on dissolution its knowledge either promotes through the gates into team corpus or archives under retention rules. Shallow, stable tree; temporary collaborations get boundary + context without minting governance that outlives its purpose.

**Edge cases:** *Confidential sub-groups* (comp, reorg, hiring) = restrictive-disclosure project contexts, with the deeper protection already structural — capture inherits source boundaries, so private-channel content never enters broader scope regardless of tree shape (§15 permission-mirroring baseline). *Cross-cutting guilds/chapters* (all PMs across squads; the frontend guild) are role communities orthogonal to the reporting tree; a person composes multiple scopes simultaneously (squad + guild). **Guild-as-template-curator resolves open question 10:** the guild owns its role's template, evidenced by fleet data — the PM guild decides what enters the PM template.

**Deployment sequence by role (go-to-market note):** engineer-validated (only builders can self-serve the fork; richest artifact trail incl. the Claude Code footprint), **PM-proven** (the PM job — synthesis loops, status representation, commitment tracking — is the Class A/C sweet spot: Team OS automates an engineer's annoying 20% and a PM's recurring 60%), mixed-at-scale (the fleet thesis requires it). Largest single beneficiary: **combined-role individuals** (EM-who-codes, TPM, founding PM) — one agent holding all contexts attacks exactly the switching tax those roles pay.

### 3.5 Agent members (a member need not be human)

Membership = a scope position + a role template + an accountable owner. None of the three requires the member to be human. Three kinds:

- **Representative agent** (core, pillar 1): every human is represented by an agent; the system was always agent-mediated, never human-to-human.
- **Ownerless service agent** (new): a member with no human *principal* that owns a recurring function — the release-notes agent, the on-call triage agent, the competitive-intel agent. Principal-agnostic primitives accommodate it (scope, template, skills, ledgers, Class C participation). Three rules make it safe:
  - **Named human owner-of-record** — no ownerless agent without a human who answers for its actions, receives its escalations, and is the accountable party (Ledger 5's token chain still needs a human root; "the agent did it" must never be an accountability vacuum). The service-account precedent.
  - **No personal layer** — a service agent has no self to protect; everything it knows is team-scoped by construction, so the privacy apparatus (E2E personal store, individuation protection) simply doesn't apply. Simpler and safer, not more complex — and it makes ownerless agents the *cleanest* pillar-3 contributors (no principal-privacy boundary around their observations).
  - **Tighter security, not looser** — an ownerless agent in Class C is a worm/impersonation surface with *no human to notice something's off*, so it needs stricter taint and rate limits (§7.7) and its owner-of-record receives the anomaly alerts (§16 detection) a principal would otherwise catch. Membership without a human in the loop makes the detection layer load-bearing where it was a backstop.
- **Sub-agent** (core, distinct): the miner, compiler, scout are *faculties* of a member's agent, not members themselves — not participants in team scope.

Strategic upside: an org can staff *functions*, not just people, with governed, measured, improving agents — a cleaner version of what service accounts and RPA do badly today.

---

## 4. Measurement Schema

### 4.1 The layered stack (established)

| Layer | Metrics | Source concepts |
|---|---|---|
| **Outcome** | Task success (rule-based / LLM-judge / environment-state comparison vs. goal state); correctness, helpfulness | τ-bench state comparison |
| **Reliability** | pass^k (all k attempts succeed; decays as p^k — 90% pass@1 → 57% at k=8); shape of pass^1→pass^k curve | τ-bench |
| **Trajectory** | Tool selection precision/recall, argument correctness, step in-order/any-order match, path efficiency, plan quality/adherence; Trajectory Exact-Match / Inclusion / Tool-Usage schema checks / LLM-judge Trajectory-Satisfy | TRAJECT-Bench |
| **Component** | Per-tool / per-MCP / per-retriever / per-sub-agent evals | diagnostic stack: outcome → path → component |
| **Failure** | 14 failure modes in 3 categories: system design, inter-agent misalignment, task verification; step/agent-level failure attribution (full traces improve attribution up to 76% vs. partial) | MAST; Who&When; TraceElephant |
| **Control decisions** | Autonomy-choice quality separated from outcome correctness (act vs. ask vs. escalate) | AgentAtlas |
| **Safety/security** | Attack Success Rate under injection; Task Success Rate under attack; Broad Refusal Rate; Harmful Compliance / Valid Refusal / SafeScore. Distributional verdicts, not single-sample | AgentDojo; AgentHarm |
| **Economic** | Cost-of-pass (expected $ per correct solution); tokens, tool-call turns, planning attempts; Cost Gap vs. optimal trajectory; invalid tool calls as tooling inefficiency | Efficient Agents; TPS-Bench; CostBench |
| **Enterprise composite** | **CLEAR: Cost, Latency, Efficacy, Assurance, Reliability.** Motivating evidence: 50× cost variation at similar precision; 60% single-run → 25% 8-run consistency | CLEAR framework |
| **Human/operational** | Engagement, acceptance rate, edit distance, override/correction rate, escalation rate | product practice |

### 4.2 Alignment: task class × measurement

| Task class | Outcome | pass^k | Trajectory | Failure attrib. | Control decisions | Representation fidelity |
|---|---|---|---|---|---|---|
| A: Looped | ◐ soft ground truth → human-signal proxies | ● **native fit** | ● | ◐ | ◐ | — |
| B: One-shot | ● via acceptance/edit distance | ◐ | ● (cost attribution) | ◐ | ◐ | ◐ |
| C: Representative | ◐ | ◐ | ◐ | ◐ (inter-agent misalignment) | ● needed, immature | ○ **gap — invent** |
| D: Fleet | ○ | ○ | ○ | ○ | ○ | ○ **gap — invent** |

### 4.3 Class A proxies (soft ground truth)
Read-through rate · click-through on cited sources · correction frequency · missed-item rate (things the human later acted on that the digest omitted).

### 4.4 Class C metrics to invent (the research contribution)
- **Principal-endorsement rate** — periodic sampling of agent-said-on-your-behalf, thumbs up/down.
- **Disclosure-policy violation rate** — shares outside policy, caught by ledger audit.
- **Commitment integrity** — promises made agent-to-agent vs. reality.
- **Grounding-failure rate** in negotiations (agents losing the principal's position when converting private goals to joint action).

### 4.5 Class D metric: redistribution efficacy
Natural-experiment design: staggered skill rollouts give a free control group. Compare pass^k / edit-distance trends between adopting and not-yet-adopting agents per update.

### 4.6 Judging economics
Frontier-LLM-as-judge per trace does not pencil at fleet scale. Use distilled small evaluation models (3B–8B class, per Galileo/Luna-2 pattern) for continuous production scoring; reserve frontier judges for promotion gates and disputes.

---

## 5. Records & Lineage: The Ten Ledgers

Each ledger answers one question. Standards noted per ledger.

| # | Ledger | Question | Contents / standards |
|---|---|---|---|
| 1 | **Execution trace** | What did the agent do? | OTel GenAI + MCP semantic-convention spans (gen_ai.* attributes; invoke_agent / execute_tool; v1.37+ aggregated message attributes). Content stored externally with span references — the only pattern that scales across privacy, retention, cost. |
| 2 | **Decision/gate** | Why was this permitted? | Every proposed action + permit/deny verdict + policy version in force at execution. Same artifact as the interaction layer's action manifest (§7.3). |
| 3 | **Memory write** | Can this memory be trusted? | Per write: source type, timestamp, authoring agent, supporting evidence, transformation operation, confidence, update history. Cryptographic trust labels surviving LLM-mediated derivation and cross-session persistence (MemLineage pattern; drove memory-poisoning ASR to 0 at sub-ms overhead). |
| 4 | **Knowledge exchange** | Who told whom; were they allowed? | Every inter-agent transfer: content, source→recipient principals, disclosure policy applied, lineage to origin. **No academic benchmark, no commercial product ships this. Team OS's novel record type.** |
| 5 | **Delegation/identity** | On whose authority? | User-ID / agent-ID / delegation-token chains with scopes (OIDC / W3C VC adaptation per authenticated-delegation framework). |
| 6 | **Version history** | Which config produced this? | Git-backed skills, context files, profiles, prompts; model versions; dataset lineage (ISO/IEC 42001 mapping). |
| 7 | **Evaluation scores** | Is this skill improving? | Per-invocation scores, pass^k aggregates, cost-of-pass, ASR samples — keyed to Ledger 6 so performance attributes to versions. |
| 8 | **Human signal** | Did the principal agree? | Edits, overrides, endorsements/rejections, escalation outcomes. Access-controlled (see §8.6). |
| 9 | **Retention/deletion** | Did forgetting happen? | GDPR deletion propagation over the lineage DAG (see §5.3). Ledger 3 locates every derived memory across every agent for purge. **On the critical path — must exist before real colleague data is ingested (before C2).** |
| 10 | **Environment state** | What world did it run in? | Per invocation: model+version, connector versions & schema hashes, dependency health, index freshness. Join to Ledger 7 for causal attribution. **Also unshipped by any vendor.** |

**Ledger minimization schema (what is deliberately NOT logged):** the ledgers are a surveillance record with legal armor against their own deletion, so each specifies excluded fields. L1: raw span *content* stored externally with references, never inline; L4: exchange *payloads* referenced not copied where sensitive; L8: signal *outcomes* (edited/rejected) without reproducing the edited content. Field-level exclusions are defined per ledger before build (work item V3), not discovered after a breach.

### 5.1 Provenance standards to build on
- **W3C PROV** (Entity / Activity / Agent core classes) + **PROV-AGENT** extension: integrates MCP concepts; captures agent, prompt, and downstream decision lineage; motivation is exactly pillar-2 risk — errors propagate when one agent's output becomes another's input. Open-source capture system: Flowcept.
- **OpenLineage** (+ Marquez) for data-pipeline lineage; **OpenMetadata** notable for treating conversations, memories, and agent workflows as governed, lineage-tracked asset classes in one graph (unifies PROV-O, OpenLineage, DCAT).
- Catalog-side convergence: lineage graphs exposed to agents via MCP (origin, transformations, quality, policy, ownership in one call).

### 5.2 Compliance floor (EU AI Act, enforcement Aug 2, 2026)
- **Art. 12:** automatic logging of traceability-relevant events; ≥6-month retention (24 for biometric/LE); inputs, reference data, period of use, output-verification records.
- Practitioner bar: no developer toggle-off; structured records (timestamp, agent identity, action, input, output, context); **tamper-evident via cryptography**, independently verifiable; exportable.
- **Art. 18:** 10-year horizon for technical docs incl. model versions and dataset lineage. **Art. 19:** logs held only by a vendor without your independent replicated copy = compliance gap.
- The requirement is **traceability, not logging**: prove why an action was taken, on what data, under which policy at the moment of execution → gate architecture (Ledger 2).
- Off-the-shelf AI APIs do not produce compliant decision records by default; the deployer owns the gap. SOC 2 / enterprise procurement increasingly demand the same records outside EU scope.

---

### 5.3 Deletion propagation (Ledger 9 mechanism)
*(Canonical labels: "Ledger 9" = the deletion ledger; "C6" = its build item in the validation plan. One mechanism, two names, used consistently.)*
Erasure is a garbage-collection problem over the lineage DAG, deadline-bound (GDPR: one month). Design:
- **Tombstones:** a deletion request writes a tombstone at the origin node; propagation walks Ledger-3 derivation edges marking every descendant.
- **Derivation severing:** when a to-be-deleted memory is an *ancestor of a promoted skill*, the skill is not silently killed — it is flagged for re-derivation from remaining sources or curator review; content-traceable deletion vs. statistical-influence deletion are distinguished (a distilled pattern that no longer contains the datum may survive; a memory quoting it does not).
- **Third-party erasure:** a colleague's DSAR-erasure enters at their content's nodes and propagates identically — the non-user rights surface (§15) routes here.
- **Single-writer ordering** (§14.5) gives deletion a consistent frontier; tombstones are durable so a machine offline during a purge completes it on reconnect.


## 6. Environment Health (Platform Telemetry)

**Why it's load-bearing:** every environment failure mode masquerades as skill/agent regression. Without Ledger 10, the pillar-3 loop learns wrong lessons (demoting healthy skills during connector flakiness; propagating "fixes" that were provider incidents resolving).

### 6.1 Serving layer — two SLO classes
- **Interactive surface (human waiting):** TTFT, inter-token latency at P99, error budgets. TTFT dominated by queuing, KV-cache misses, prompt processing — not generation.
- **Background fleet (Class A/D volume):** agent traffic is stateful, tool-consumed, near-zero inter-arrival — behaviorally batch, not chat. Human-perception SLOs are wrong here; measure **total task completion time / throughput**. Metric groups: operational (request rate, error rate, TTFT, latency, tokens/sec), economic (token counts, cost per request/session), quality proxies (feedback rate, retry rate, refusal rate) as leading indicators.

### 6.2 Tool/connector environment (MCP health)
- **Blind spot:** reachable ≠ working; tool degradation is invisible to infra monitoring.
- **Protocol-native probing:** list_tools handshake (green = actually ready), JSON-RPC ping ~30s cadence, ~3 consecutive failures before restart; 60s heartbeat + auto-recovery in production references.
- **Schema drift detection:** compare tool schemas across checks; agents calling outdated schemas get malformed responses they can't surface.
- **Tool-budget saturation:** tool-count-vs-accuracy is a health curve (production reference: 80-tool cap per agent to avoid degradation).
- Pre-built MCP dashboards exist (tool performance, protocol health, context-window usage, error tracking) with OTel cross-language context propagation. Silent failures (partial data, quiet timeouts) are the target class.

### 6.3 Environment security
Supply-chain patterns: tool **rug pulls** (benign at install, malicious on later update) and **cross-server tool shadowing** (malicious server intercepts calls to a trusted same-named tool). Scale: ~40k open-source MCP repos fuzzed → 106 zero-days, 67 CVEs. Platform health therefore includes connector vetting, version pinning, schema-hash verification: **an unticketed schema-hash change is a health incident, not an update.**

### 6.4 Knowledge environment
Embedding drift, retrieval quality (context relevance traced embedding→search→assembly), index freshness. New-style SLIs: e.g., RAG faithfulness ≥0.85 on 98% of answers, alert on vector-DB drift. Team-OS-specific: **sync lag** (source systems → knowledge layer) and **staleness age on scoped context/profile files** — a stale team context silently degrades every downstream skill and reads as fleet-wide regression.

### 6.5 Model environment
Provider incidents, quota pressure, **silent model updates behind pinned names**. Defense: scheduled canary eval suite per provider/model so upstream drift becomes a labeled environment event. Per-model cost/latency feeds routing.

### 6.6 Sustainability (optional column)
Tokens → energy → carbon attribution per agent; power-efficient agentic serving is an active research area. Cheap to add early if ESG reporting ever applies.

---

## 7. Interaction Layer

**Framing:** not a new subsystem — a projection of the record layer for principals, plus instrumentation flowing back. Every surface is simultaneously sensor, actuator, and rendezvous point.

### 7.1 Three planes

**Plane 1 — Embedded work surfaces (third-party).** Slack/Teams @-mention & DM · CC-the-agent email · doc comments · tracker updates · calendar · meetings · IDE/CLI. Design rule: **channel symmetry** — reply in the surface invoked from, at its native formality.

**Plane 2 — Native console.** Direct dialogue with the representative: briefings, delegation, thought-partnership, Class-B checkpoints and artifacts.

**Plane 3 — Mission control (management plane).** Reference pattern set: overview panel · oversight flow · activity log · work reports · event-stream config · capacity/logic config · human-oversight config. Team-OS additions (each a ledger rendered):
- **Memory/profile editor** — view/edit/delete inferred personal details (Ledger 3 UI; consent mechanism).
- **Disclosure policy editor** — what my agent may share, with whose agents (Ledger 4 UI).
- **Skill manager** with per-skill report cards (Ledgers 6+7).
- **"On my behalf" review feed** — samples of agent-to-agent statements with endorse/correct (populates Ledger 8; operationalizes representation fidelity, §4.4).

### 7.2 Initiative spectrum & HITL
Chat → ambient shift: agents listen to event streams, act, and demand attention only at important opportunities. Three ambient HITL patterns: **notify / question / review**. Governance modes: human-**in**-the-loop (approve each action) vs. human-**on**-the-loop (autonomous with interrupt/override/rollback as primary actions, not edge cases). Async accumulation → **agent inbox** (approve / edit / respond / reject), deliverable into Slack/email.

### 7.3 Action manifest
Classify every possible action by **severity × reversibility**; assign approval requirements and escalation paths *before* orchestration. Same object as Ledger 2's gate policy — one artifact serves UX, safety, and Art. 12.

**The gate looks inside the action (payload-layer inspection, always-on):** classification by tool *name* is insufficient — a permitted tool must not become an exfil path via its payload. Bash commands are scanned for egress + sensitive-file reads; writes to declared cloud-synced paths are classified as *sends*, not local writes; tool parameters that can carry data out are scanned. **Unattended-run hardening is the user's choice, offered not mandated** (policy-neutral, §14.1): pre-declared allow rules for headless runs (default), an OS-level egress allowlist (recommended), or looser postures the user accepts knowingly — safe option easy, risk legible, choice respected.

### 7.4 Bidirectional signal model
- **Explicit inputs:** commands, approvals, rejections, edits (+distance), endorsements, policy changes.
- **Implicit inputs:** opened vs. ignored digests, source click-throughs, response latency, unmodified-send rate, acted-on recommendations.
Both stream to Ledger 8 → pillar-3 training data. **Approval friction is the labeling budget:** auto-approve everything and the fleet learns nothing; ask constantly and humans rubber-stamp (approval fatigue). Therefore **adaptive autonomy envelope**: high-touch early (max labeling, min autonomy), relaxing per action-category as calibrated confidence accumulates — the envelope expands as a function of Ledger 8. *(No product ships this; the measurement pillar becomes the UX.)*
- **Provenance in every output:** each digest bullet / on-behalf statement carries its lineage citation (Ledger 3 as a link).
- **Observation/surveillance boundary:** visible "what I'm listening to" config + memory editor = consent mechanism (and Ledger 9 alignment).
- **Inbound-exchange transparency:** when another agent queries yours (Class C) and the exchange enters your review feed, the *querying* principal is told their queries are principal-reviewable — symmetric disclosure, so no one is human-surfaced without knowing (contextual-integrity fix, §15).

### 7.5 Surface matrix

| Surface | Input (sensor) | Output (actuator) | Mgmt hook |
|---|---|---|---|
| Slack/Teams | messages, @-mentions, reactions | replies, digests, status posts | inbox items as DMs |
| Email | threads, CC-the-agent | drafts, sent-on-behalf, briefs | approval requests |
| Docs/wiki | edits, comments | drafted sections, reviews | provenance links |
| Trackers/calendar | task & schedule events | updates, negotiated holds | manifest gates |
| Console | commands, dialogue | briefings, artifacts, checkpoints | everything on demand |
| Mission control | policy/memory edits, endorsements | report cards, activity feed, A2A review | *is* the hook |
| Agent-to-agent | peer queries, commitments | responses, brokered knowledge | review-feed samples |

**Unifying requirement:** a persistence layer saving agent state between actions — pause mid-task, resume on any surface. One agent state, many projections; otherwise each surface becomes a half-consistent agent and the representative premise breaks. (The durable-execution substrate in §7.6 is this requirement, productized.)

**Two CONNECTION planes (distinct from §7.1's interaction planes — connection = who holds the pipe; interaction = where the human meets the agent):**
- **Plane A — Team OS → services (primary).** Team OS is itself an MCP *client* holding its own connections to Slack/Gmail/Jira/Drive/GitHub under the user's OAuth grants. This is the ambient half: every Class A loop, the discovery miner, the representative answering colleagues run here, Team OS acting *as* the user, with no Claude client in the loop. The proactive identity claim *requires* this plane — a digest that only runs during an open chat session is a chatbot, not a background agent.
- **Plane B — Claude (and ChatGPT) → Team OS (secondary).** Team OS exposes an MCP *server*; a client toggles it on to query the corpus or check what the loops produced. The client holds nothing; Team OS is the server. Human-to-agent interaction from a surface you already have.
- **Distinction:** on Plane A, Team OS holds the credential and acts as you (gated, ledgered, taint per source); on Plane B, queries arrive from a session Team OS cannot observe (semi-trusted tier, §7.7 — writes need confirmation). The same service can appear on both — reading Slack directly (A) vs. asking a Claude session "what did my agent post" (B, which queries Team OS's *record*, not Slack). "Claude as the door" (B) is an addition to direct connection (A), never the mechanism for it.

### 7.6 Work objects (ticketing) & the workflow substrate

**Boundary rule — two ticketing domains, never conflated:**
- Work *about the org's product* lives in the org's existing trackers (Jira/Asana/Linear), which agents read/write via connectors (Class A hygiene). Team OS never replaces these.
- Work *about the agent system itself* lives in an internal **Work Object system**: approval requests, automation proposals (§9), promotion requests (§10.5), A2A commitments, shadow-trial reviews, structural-insight proposals (§10.4), escalations.

**Work Object schema (one type for every ticket-shaped thing):** id · type · state machine (open → in-review → approved/rejected/expired → executed → verified) · assignee (human **or** agent) · principal · SLA/aging · priority · provenance links into the ledgers · payload.
- The **agent inbox is the human view** of the work-object queue; **mission control is the management view** (queues, aging, reassignment, SLA breaches).
- Every state transition writes to Ledger 2 — ticketing and audit trail are the same object.
- **Class C commitments are work objects** with a made → in-progress → fulfilled/breached lifecycle, making the commitment-integrity metric (§4.4) mechanically computable.

**Workflow substrate — durable execution:** long-running, multi-step processes spanning agents and humans run on a durable-execution engine. Grounding: durable execution crossed into the early majority in late 2025 (AWS Durable Functions, Cloudflare Workflows GA, Vercel Workflow DevKit) with AI agents as the driver; **HITL maps directly to suspend/resume primitives** — workflows pause hours or days awaiting approval without losing state. Production pattern: **outer durable orchestration (Temporal-class) + inner agent logic (LangGraph-class) per activity**; state held indefinitely, automatic retries until a probabilistic LLM returns valid output. For irreversible external effects (send/pay/publish), gate settlement transactional-outbox-style on workflow progress (Atomix pattern). Result: a system that can be **operated, not just observed** — pause, veto, rollback, replay as primary operations.

**Management model:** workflow definitions are versioned artifacts (Ledger 6) → measured like skills (workflow-level pass^k, cost-of-pass, completion time) → degrading templates roll back via the same pillar-3 machinery → proven workflows federate through the promotion gate into role templates. Human steps inside workflows materialize as work objects; escalation chains and timers are workflow-native.

### 7.7 Taint tracking & provenance-conditioned capability (injection defense)

The system is the **lethal trifecta** by design — private-data access, untrusted-content exposure, and external communication are all permanently present. A static injection-test suite (T5) is necessary and insufficient; the structural defense is to make capability a function of context provenance.

**The core rule (CaMeL-style separation):** *untrusted sources may contribute **content** to outputs, never **structure** to plans.* An email can be summarized in a digest; it cannot add a step to the task list, change a recipient, or trigger a tool. Enforced at the planner boundary.

**Taint tracking:** every datum entering context carries an origin mark from L3 lineage (external sender / unreviewed doc / another agent / historical-ingest / principal). Side-effectful tools degrade under tainted context: external sends, disclosure-relevant A2A replies, and — highest friction of all — **memory/corpus writes** require elevated gating when untrusted content is present. *The memory/corpus write is the most consequential tool call in the system* (a poisoned write re-enters every future context as trusted; a promoted poisoned entry is privilege escalation from personal-lie to team-fact) — so write-under-taint outranks even external send in the action manifest.

**Per-source trust-tier table** (config, maintained like the flow map; the security twin of §15's CI flow map):

| Tier | Sources | Default posture |
|---|---|---|
| Trusted | principal's own chat (protect the channel) | command authority |
| Semi-trusted | internal docs/wiki, first-party tracker fields | content yes, instructions extracted+flagged |
| Untrusted | email, calendar invite bodies, external PR/issue text, web, MCP tool outputs | content only; no plan structure; no write without confirm |
| Transitively untrusted | A2A inbound (= the peer's weakest source) | untrusted-by-default; cross-agent taint propagates via L4 |

**Capability minimization as schema:** every scheduled loop declares its tool set, **read-only by default** (the §10.2 capability manifest, repurposed for security). The digest loop mechanically lacks send/write tools — so even a fully successful injection of an ambient loop degrades to *misinformation* (recoverable), never *action* (sometimes not). This matters because ambient loops read sources with no competing human intent in context, making the injection the only instruction present.

**Cross-agent taint:** an A2A message derived from tainted context carries the mark, so a receiving agent's gates see "traces to an external email the peer read," not "trusted peer said so" — the difference between per-agent defense and fleet immunology, and the containment for the Class C worm vector.

**Compilation-time injection (critical-path):** job compilation (§11.2) ingests years of unreviewed history as *exemplars* — permanent, trusted-by-construction, voice-laundered. Treated as fully tainted: exemplars contribute style and structure of *outputs*, never standing instructions; anything imperative-shaped in historical content is extracted, flagged, and quarantined, not compiled. Scanned inside C2, before T5's defenses exist downstream.

---

## 8. Organizational Design Principles
*(From organizational behavior, psychology, and economics — the layer that determines whether the system helps or harms the org.)*

### 8.1 Transactive memory → directory-first knowledge
Effective teams share a **directory of who knows what**, not all knowledge; directory quality predicts performance (Wegner; Moreland & Lewis). Build the corpus index as the directory (§3.2.4). **Atrophy risk:** if agents always synthesize, humans stop knowing who knows things — design the agent to sometimes *route to the person* ("Priya solved this in March — intro or writeup?"), preserving the human network.

### 8.2 Knowledge stickiness → recipient-adaptive transfer
Transfer fails on **causal ambiguity, absorptive capacity, and arduous relationships** — not unwillingness (Szulanski; Cohen & Levinthal). Pillar-2 sync must move *packaged* knowledge — decision + rationale + evidence (the lineage layer doing double duty) — and the receiving agent translates into the recipient's frame via their profile. Same learning lands differently for a new hire vs. a principal engineer. **Genuine differentiator: no knowledge tool does recipient-adaptive transfer.**

### 8.3 Weak ties & structural holes → designed brokerage
Novel information flows through weak ties (Granovetter); brokers across disconnected groups capture outsized value and are scarce (Burt). The fleet can **democratize brokerage**: detect Team A's agents solved what Team B's agents struggle with — across a hole no human spans — and propose the bridge. Highest-value sync behavior, and precisely what hierarchy-scoped defaults would block → explicit cross-scope brokering path (§3.2.3), not accidental.

### 8.4 Job design → toil, not texture
Motivating work = skill variety, task identity, significance, autonomy, feedback (Hackman & Oldham). "Mundane" tasks often carry identity and feedback (writing your own update is how you notice what you did). **Ironies of automation** (Bainbridge): automate the easy parts and humans keep only the hardest, with less practice to stay sharp — the deskilling loop. Discipline: remove **toil** (manual, repetitive, automatable, no enduring value — SRE definition); preserve **texture** (agent drafts, human owns the judgment layer). Self-Determination Theory (Deci & Ryan): **propose, don't presume** for identity-adjacent work — fait-accompli automation erodes autonomy even when output is good.

### 8.5 Attention science → interruption budgets
Interrupted work takes ~23 min to fully resume (Mark); even anticipated switches leave attention residue (Leroy). Converts notify/question/review thresholds into arithmetic: per-principal **interruption budget**; batch non-urgent into digest rhythm; synchronous interrupts only where expected value exceeds ~25 min of principal time. A computable gate.

### 8.6 Psychological safety & Goodhart → structurally enforce "measure agents, not people"
**Scale honesty:** this is a fleet-scale guarantee. At pilot scale (n≤3) an agent and its principal are the same entity — per-agent metrics ARE per-person metrics — so the guarantee degrades to: measured data is consented, visible to its subject, and time-boxed (the research-exception posture). Do not claim the structural guarantee at a scale where it cannot hold.
Teams learn only when errors surface without penalty (Edmondson); otherwise organizational silence (Morrison & Milliken). If principals believe Ledger 8 is performance surveillance, they manage edits/approvals for optics (Goodhart) and pillar-3 training data is poisoned. Enforcement must be **structural** — aggregation, access control on Ledger 8, explicit policy — not promised.

### 8.7 Exploration/exploitation → variance as an asset
Organizations systematically over-exploit (March). Pillar 3 is an exploitation engine: propagating the best variant **homogenizes the fleet** and kills the variance learning feeds on. Reserve an explicit exploration budget (fraction of fleet/invocations on variant skills); staggered rollouts already provide the shape (§4.5). Farm variance; don't eliminate it.

### 8.8 Sensemaking → beware the single narrative
Organizations act coherently through shared interpretation of ambiguity (Weick). Identical model + corpus generating every principal's brief **industrializes sensemaking**: interpretation errors correlate perfectly across the team. Mitigations: digests surface disagreement and anomaly rather than smoothing to consensus; deliberate perspective variation across briefs; preserve human debate rituals as where interpretations collide.

### 8.9 Choice architecture & diffusion → defaults and observability drive adoption
Defaults dominate behavior (Thaler & Sunstein); habits form on cue-routine-reward. Adoption spreads on relative advantage, compatibility, **trialability**, **observability** (Rogers). Ship opinionated defaults (starter skills, digest time, disclosure policy); anchor the morning brief to an existing cue; make peer usage visible. Setup cost is the trialability killer — dedicated onboarding time/events beat organic rollout.

---

## 9. The Efficiency Discovery Loop (Self-Learning)

Personal agents learn from the principal **broadly** — not only from assigned tasks — and proactively propose automations and efficiencies. This merges two traditions that haven't been combined: enterprise task mining (detection) and proactive-agent research (initiative).

### 9.1 Research grounding
- **Proactivity defined:** anticipation of user needs, initiation without explicit commands, targeting the user's current/future goals.
- **State of the art:** most "always-on" assistants still depend on user-specified schedules and explicit automation instructions; the frontier (ProAct) adds long-term user grounding, **value-aware evaluation balancing utility against interruption cost**, and **idle-time compute** for anticipation.
- **The capability ceiling:** PROBE decomposes proactivity into (1) searching for unspecified issues, (2) identifying bottlenecks, (3) executing resolutions — best frontier models reach only ~40% end-to-end. **Design consequence: discovery-and-proposal, not discovery-and-execution.** Timing-aware RL (ProActor) and joint Productivity/Proactivity/Personalization training (PPP) are improving the timing and personalization dimensions.
- **Task mining lineage:** desktop-activity capture → recurring-pattern detection → automation scoring (frequency, handle time, ease, savings); proven at eliminating ~25% of non-value-added activity. **Trust-model inversion required:** enterprise task mining is an instrument deployed *on* employees by transformation teams; Team OS runs it as a service *to* the individual — principal-owned, never aggregated upward.

### 9.2 The six-stage loop
1. **Observe (free).** The behavioral stream already exists: every surface is a sensor (§7.4); Ledgers 1 & 8 capture what the principal does, delegates, edits, repeats. Bounded by the "what I'm listening to" consent config.
2. **Mine (idle-time compute).** Three detectors: **recurrence** (same sequence weekly), **variance** (same job done three inconsistent ways → standardization candidate), **bottleneck** (throughput stalls on something automatable).
3. **Score.** frequency × time cost × automatability × reversibility, then two filters enterprise tools lack: the **texture guard** (§8.4 — toil yes, identity-bearing work no) and the **interruption budget** (§8.5 — a proposal is itself an interruption and must clear the expected-value bar). **Precision over recall:** every weak proposal spends trust.
4. **Propose.** Candidates land in the agent inbox with a **shadow-trial offer**: "I ran this silently this week — here's my version vs. yours, diff attached. Take it over with your review for a month?" Shadow runs convert proposals into evidence; graduated review plugs into the adaptive autonomy envelope (§7.4).
5. **Synthesize & measure.** Accepted candidates become generated skills (Trace2Skill pattern: distill trajectory-local lessons into transferable skills) in the personal skill namespace, instrumented by pillar 3 from invocation one.
6. **Federate.** A locally verified pattern is checked against the fleet: if N other principals show the same recurrence signature, the skill is proposed to them through the promotion gate with the discoverer's performance data attached. Individual self-learning becomes organizational learning; §8.7's exploration budget keeps variant approaches alive.

### 9.3 Guardrails
- **Discovery corpus is architecturally principal-private** (Ledger 8 access class). Only accepted *skills* — never the behavioral observations behind them — are eligible for federation. This is the §8.6 Goodhart boundary under maximum pressure.
- **KPI: proposal acceptance rate**, at low volume (a couple per week, batched into the digest). The discovery capability is itself a skill measured by pillar 3 and improves like any other.

### 9.4 The knowledge scout ("sniffer")

A sibling loop to task discovery: agents proactively prospect for **content and knowledge worth acquiring**, not just tasks worth automating. Research grounding spans three traditions:

- **Curiosity-triggered acquisition.** The RL curiosity lineage (Schmidhuber 1991; Pathak's prediction-error intrinsic reward) now extends to LLM agents: curiosity as a lightweight trigger — when the agent is uncertain in unfamiliar territory, it initiates external retrieval and constructs a knowledge card to reduce future uncertainty (the AppCard pattern). Team OS translation: **corpus entries born from need** — an agent hitting uncertainty mid-task retrieves, distills, and proposes the entry, so acquisition is demand-paged rather than speculative.
- **Foraging economics.** Information Foraging Theory (Pirolli & Card) supplies the stopping rules: information scent, patch-leaving decisions, cost-benefit per source. The LLM-era extension finds that in chat/agent environments **trust supersedes scent** as the navigation driver — so scouted knowledge must carry provenance (Ledger 3) to be worth anything.
- **Anticipatory prospecting.** The proactive-agent line (§9.1, ProAct's idle-time compute) applied to knowledge: scan connected sources during idle cycles for high-value uncompiled knowledge — decision threads never captured, heavily-linked docs missing from the corpus, questions multiple agents keep failing to answer (Tier-3 gap signals as the demand map).

**Design constraints:** (1) The literature's warning — low propensity for proactive exploration is a dominant bottleneck in current agents — means the scout needs explicit budgets and triggers, not hoped-for emergence. (2) The noisy-TV guard: novelty ≠ value; scout candidates are scored by expected corpus utility (query-miss frequency, breadth of principals affected), not by newness. (3) Scope discipline: the scout sniffs only what connectors already permit, and everything scouted enters as a *proposal* through the §10.5 gates — the sniffer feeds the promotion pipeline, never bypasses it.

---

## 10. Learning Storage & Portability Architecture

### 10.1 The compression gradient: learnings are routed, not pooled

"Learnings" are heterogeneous. Following the memory → skill → rule compression spectrum, each learning type routes to a different store:

| Learning type | Example | Destination |
|---|---|---|
| **Episodic** (raw experience) | conversation history, task trajectories, observations | Personal memory store |
| **Procedural** (distilled how-to) | a generated skill from the discovery loop | Skill registry (personal namespace) |
| **Semantic** (facts, decisions) | "we chose vendor X because Y" | Scoped corpus — via promotion gate only |
| **Calibration** (behavioral state) | autonomy-envelope levels, voice, preferences, interruption tolerance | Personal profile |
| **Performance** (scores) | pass^k, edit distance, cost-of-pass | Telemetry ledgers — **never the corpus** |
| **Interactional** (emergent from agent-to-agent exchange) | which negotiation moves settle fastest; what disclosure level gets useful answers from Team B; recurring cross-team exchange patterns | Fleet learning layer (§10.4) — a process over Ledger 4 + Class C traces, whose outputs route back into existing stores |

Provenance survives compression: a promoted corpus rule traces back through the skills and episodes that produced it (Ledgers 3 + 6). Answer to "corpus or separate?": **both, by type** — semantic knowledge earns its way into the corpus through the promotion gate; everything else lives in purpose-built stores that reference each other by lineage.

### 10.2 The five stores

| # | Store | Contents | Owner | Format | Portability property |
|---|---|---|---|---|---|
| 1 | **Scoped corpus repos** (one per scope) | context / profile / experience files + promoted knowledge entries | Org (team-scope curated) | Git: markdown + PROV/JSON-LD lineage sidecars | Portable as a repo; fork/audit/migrate; **survives turnover** |
| 2 | **Skill registry** | skills at all scopes incl. personal namespaces | Org; personal namespace co-owned | Git: versioned skill folders (SKILL.md pattern) **+ capability manifest per skill** (declared capture-surface requirements: cloud-only / +synced / +local-folders; checked at load; graceful degradation on lesser tiers — tier portability, §14.7) | Portable; version history = Ledger 6 |
| 3 | **Personal memory store** | episodic memory, discovery observation corpus, calibration state | **Principal** | Encrypted DB, lineage metadata per write (Ledger 3), principal-keyed | Moves with the person per policy |
| 4 | **Telemetry/ledger store** | Ledgers 1–10 | Org (Ledger 8 access-restricted) | Append-only, OTel/OTLP-native | Exportable (Art. 12/19 compliance) |
| 5 | **Role template registry** | predetermined skill sets + knowledge pointers per role | Org | Git | **The provisioning unit** |

Everything file-based and open-standard (git, markdown, PROV, OTLP) — no store is locked to a harness or vendor; the corpus-as-repo pattern makes the knowledge base as portable as a codebase.

### 10.3 Agent portability & provisioning

**An agent is a composition, not an artifact:**
`agent = base runtime (fungible) + scope cascade (stores 1) + role template (store 5) + personal layer (stores 2-personal + 3)`

No learning lives in the runtime → models and harnesses are swappable at will, validated by the Ledger-10 canary suite.

- **New-hire provisioning:** instantiate from role template + team/org/division/company scopes. Day one, the agent already knows the team's decisions, glossary, norms, and conventions — the predetermined skills and knowledge come from stores 5 and 1, not from ramp time. Absorptive-capacity translation (§8.2) renders team knowledge in a novice frame. The autonomy envelope starts conservative — **onboarding doubles as the labeling period** — and the discovery loop starts in observe-only warmup.
- **Internal transfer:** a ledger event — swap team/org scopes; personal layer travels intact; old-team semantic knowledge access reverts to cross-scope disclosure policy.
- **Departure:** personal layer export governed by policy (personal preferences and calibration vs. org-derived knowledge separated at export by lineage metadata — this is what Ledger 3's source-typing is for). Team corpus, promoted skills, and templates persist: **organizational memory survives turnover**, directly countering the knowledge-loss problem that motivates the OB literature.
- **Role template lifecycle:** templates are themselves improved by pillar 3 — when a promoted skill proves out across a role's population, it joins that role's template, so each new hire starts from the fleet's accumulated learning, not from zero.

### 10.4 Segregation and pooling: the three-tier learning topology

Learning operates at three tiers with different privacy and value properties:

**Tier 1 — Segregated (per-agent).** Each agent's episodic memory, calibration, and discovery observations are principal-private (§9.3). This is the default; nothing leaves without crossing a gate.

**Tier 2 — Federated (individual → fleet).** Distilled artifacts — skills, promoted semantic knowledge — cross the promotion gate carrying performance evidence but not the raw observations behind them. Federated-learning discipline: **share the distillation, never the data.** (§9.2 stage 6; SkillClaw pattern: cross-user traces collectively refining a shared repository.)

**Tier 3 — Pooled (emergent from interaction).** Some learnings exist *only between* agents — no individual agent could have produced them. The fleet learning layer mines Ledger 4 (knowledge exchange) and Class C traces for:

- **Protocol efficacy** — which negotiation/query patterns settle fastest, which framing gets substantive answers vs. deflection. Output: interaction-protocol rules written to **company-scope Experience** (all agents inherit better A2A conduct).
- **Pairwise calibration** — what works specifically between agent *i* and agent *j* (formality, detail level, trusted topics). Output: calibration entries in each agent's **personal profile**, symmetric and lineage-tagged.
- **Structural insight** — recurring cross-team exchange patterns that reveal organizational facts: Teams A and B exchange the same artifact weekly (→ propose a standing sync or shared corpus entry); three teams independently ask about X (→ a corpus gap); a structural-hole bridge is carrying heavy traffic (§8.3 brokerage made visible). Output: **proposals to humans**, not silent restructuring — the org chart belongs to the organization.

Design decisions that keep Tier 3 safe and cheap: it is a **process, not a sixth store** — its outputs route into existing stores (corpus Experience, profiles, proposal inbox), keeping the architecture closed. It learns from **patterns, not content** — aggregate thresholds (a pattern must recur across ≥N distinct principal pairs before it's mined) prevent any pooled learning from being traceable to one person's behavior, which is the §8.6 Goodhart boundary applied to interaction data. And its products are versioned and measured like everything else: a Tier-3 protocol rule that degrades settlement rates gets rolled back by the same pillar-3 machinery that promoted it. Research grounding: shared-memory-pool work shows dialogue-like memory sharing among agents produces collective self-enhancement (INMS); Tier 3 is that mechanism made governable.

### 10.5 The sharing decision function: private vs. federated vs. pooled

**Default-deny.** Every learning is born private (Tier 1). Sharing must be *earned* (evidence), *safe* (generalization), and *permitted* (provenance + consent). Five sequential gates:

| Gate | Test | Mechanism |
|---|---|---|
| **0 — Type eligibility** | Is this type ever shareable? | Episodic: never. Calibration: never (except Tier-3 symmetric pairwise entries). Performance: ledgers only. Procedural + semantic: Tier-2 eligible. Interactional: Tier-3 aggregation only. |
| **1 — Provenance sensitivity** | What did it come from? | Learning inherits the **max sensitivity of its source lineage** (taint propagation via Ledger-3 trust labels, MemLineage-style). Public/team-artifact sources → eligible; discovery-corpus/personal-comms sources → private unless distilled. **Distillation = logged declassification event**, valid only if Gate 2 passes. **Classifier is probabilistic → quarantine tier:** uncertain items are held, not shared; declassification requires explicit human confirmation; classifier accuracy is a measured, first-class metric (A-K5). |
| **2 — Generalization** | Statable without reference to any individual's content/behavior? | PII/secret scans on artifacts; Tier-3 k-threshold — **replaced by differential privacy with a declared epsilon budget** (k-anonymity fails to intersection/longitudinal attacks, §15). "Invoice reconciliation macro" passes; "short sentences for Bob" fails → routes to pairwise calibration. |
| **3 — Evidence** | Has it proven out locally? | pass^k floor over N invocations, or acceptance-rate floor for discovery-generated skills. Promotion gate consumes Ledger 7. Sharing junk pollutes the fleet. |
| **3.5 — Integrity** | Is the skill itself safe to distribute? | **Signing + behavioral sandbox before federation; updates re-enter review** (supply-chain gate; §15). Blocks the promotion-pipeline-as-malware-channel and the rug-pull vector. |
| **4 — Lawful basis & objection** | On what basis, and can the subject object? | **Basis is per-context:** consent where genuinely free (pilot volunteers); at deployment scale **legitimate interest + documented balancing (LIA), with objection rights** (consent is invalid under employment power-asymmetry); and **special-category data appearing incidentally (health etc.) always needs an explicit condition — detect-and-exclude by default** regardless of tier. Standing disclosure policies set defaults; corpus writes need curator/endorsement threshold (§3.2.2). Third-party-derived content additionally faces the non-user rights surface (§15). **Revocable** — lineage makes downstream copies findable (Ledger 9 propagation, §5). |
| **5 — Scope assignment** | Where does it apply? | **Subsidiarity:** narrowest applicable scope — role template if role-specific, team corpus if team-specific, company Experience only for universal protocols. Controls context bloat and over-broadcast. |

**Design properties:**
- **Deliberate asymmetry:** private costs nothing; sharing costs evidence + safety + a tap — the inverse of enterprise KM defaults, and the reason this design avoids the §8.6 psychological-safety failure.
- **One gate object system-wide:** Gates 0–5 are the action manifest (§7.3) and decision-gate ledger (Ledger 2) applied to knowledge movement instead of tool calls — every sharing decision yields the same tamper-evident, auditable record as every action decision.
- **Write-time discipline is load-bearing:** Gate 1 only works if source-typing is correct when memories are written (open question #8) — classification cannot be retrofitted.


---

## 11. Cold Start: Ingestion, Job Compilation & Onboarding

### 11.1 Principle
**Cold start is the agent's first task, not the user's.** Users point at inputs and outputs (a one-time, IT-authorized connector grant) and expect the system to work. Value precedes configuration; every correction is training signal; there is no training mode, setup wizard, or interview.

### 11.2 Ingestion as job compilation
One-time historical ingest whose product is not a memory pile but **three compiled artifacts**:
1. **The job graph** — recurring *transformations* mined from artifact history (these sources → that Thursday doc; those threads → these release notes). Each becomes a **pre-built skill with the user's own historical outputs as few-shot exemplars**. The training already happened; the user did it over the last three years without knowing.
2. **The corpus** — decisions with rationale, definitions, ownership, norms — each entry carrying evidence links to source.
3. **The voice/Experience layer** — structure, register, and format compiled from the user's own outputs, so day-one drafts read as "mine, roughly," not AI slop.

**Distill-then-discard at full scale:** raw ingest is transient working data; what persists are compiled artifacts plus lineage *references* — colleagues' words become pointers in evidence chains, not standing records. **Gate-1 blast radius bounded:** everything compiled lands at personal/team scope by default; nothing federates until it earns evidence (§10.5), so bootstrap misclassification cannot leak beyond the audience that already had source access.

### 11.3 The Day One experience
- **Minute 0:** user signs in. Connectors pre-provisioned by IT; one-sentence boundary default ("shared team spaces, calendar, and docs you've authored; DMs and email off unless you turn them on").
- **Background:** the agent runs self-onboarding as a Class B research task on its own principal — org position, calendar rhythm, authored artifacts, owned tickets, team channels → drafts profile, collaborator map, and the inferred recurring-task list.
- **The Day One Brief** — a deliverable, not a wizard: (1) a working digest, immediately; (2) the draft understanding of the job as ✓/✗ bullets (the first Ledger-8 labeling pass, experienced as "a sharp new hire summarizing what they've learned"); (3) **first drafts delivered as work** — the Thursday doc, done, with one line: "built from your last 40 — edit anything and I'll learn." The first cycle *is* the shadow trial.

### 11.4 Corpus bootstrap: inferred canon
Do not scrape the wiki; do not convene a curation workshop. Rank candidates by **link centrality, access patterns, maintenance recency, and author centrality**; top ~30 go to one lead as a 15-minute ✓/✗ (optional — canon can ship inferred, marked as such, and harden through use: retrieved-and-uncorrected entries gain confidence, contradicted ones surface for resolution). Tier-3 gap detection (§10.4) and the knowledge scout (§9.4) grow the corpus toward actual demand.

### 11.5 What starts fresh, on principle
Calibration, the autonomy envelope, and discovery-loop warmup — behavioral state of *this* principal-agent relationship, which has no history to import. Backfilling behavior would be maximum surveillance for minimum inference reliability. Conservative start = the labeling period (§10.3).

### 11.6 Evidence base
- **Second-brain products:** import-as-onboarding (Notion importers), never-a-blank-page (templates), grant-once passive capture (Rewind/Limitless), the daily artifact as habit anchor (Roam/Logseq daily note), tutorial-as-real-content (Obsidian sandbox vault). **Refuse** Obsidian's effort-gated value model — it builds devoted niches by filtering for tool-gardeners; enterprise users reject it.
- **Organizational socialization science:** on-the-job training beats orientation programs (systematic review); role clarity, self-efficacy, and social acceptance are the adjustment variables that predict performance and retention (Bauer & Erdogan meta-analytic line); newcomer proactivity/information-seeking predicts adjustment — **the agent is a proactivity prosthetic** (does the asking without the social cost); greater socialization knowledge reduces newcomer stress.
- **Legitimate Peripheral Participation** (Lave & Wenger; Wikipedia/CSCW empirics): membership is earned through simple, low-risk, *productive* tasks; the majority of newcomers to knowledge communities disengage after the very first interaction; there is no quick technological fix to becoming a member.

### 11.7 Apprentice-inverted mode (human newcomers)
The LPP collision: **peripheral productive tasks are how humans become insiders — and they are exactly what Team OS automates** (the Class A sweet spot *is* the traditional periphery). Bainbridge's irony at the socialization layer. Resolution: for `tenure < X months`, the agent **scaffolds the human doing the peripheral tasks instead of doing them** — "here are the four sources this doc draws from, here's how the last author structured it, here's who reviews it" — an accelerated LPP experience with the agent as the observable old-timer. Handover proceeds gradually on the newcomer's own signal. The role-template ramp metric gains a second criterion: **socially integrated, not just serviced.**

---

## 12. Research & Market Reference Index

### Academic — agents & delegation
- Multi-Agent Collaboration Mechanisms survey (Tran et al., arXiv:2501.06322) — actors/types/structures/strategies framework
- AI Delegates: privacy & strategic self-disclosure (arXiv:2409.17642)
- Choose Your Agent: advisor/coach/delegate tradeoffs — preference-performance misalignment; delegates as market makers (Harvard/DeepMind)
- LLM-X: negotiation-oriented exchange for personal-agent populations (message bus, schema validity, policy enforcement)
- Intelligent AI Delegation (arXiv:2602.11865) — authority/responsibility/accountability transfer
- Authenticated Delegation & Authorized AI Agents (arXiv:2501.09674) — user/agent/delegation token framework
- Grounding failures in agent-agent negotiation (arXiv:2605.01750); delegation & psychological distance / ethics (Gratch & Fast)

### Academic — memory, skills, collective learning
- Collaborative Memory: multi-user sharing with dynamic asymmetric access control (arXiv:2505.18279) — pillar-2 blueprint
- A-MEM (Zettelkasten-style agentic memory); INMS shared memory pool; MemGPT/GraphRAG/HippoRAG lineage
- SkillGraph (graph-structured skill libraries, trajectory-updated); Trace2Skill; AutoSkill; SAGE (RL + skill library)
- **SkillClaw — cross-user trace aggregation refining a shared skill repo (closest to pillar 3)**
- Evidence Tracing & Execution Provenance survey (arXiv:2606.04990) — memory-write lineage metadata
- MemLineage (arXiv:2605.14421) — cryptographic memory provenance; ASR→0
- Generative Agents (Park et al.) + 1,000-people simulations; caution: simulations look right, causal effects go wrong → **represent preferences/context, don't predict principals' decisions**

### Academic — proactivity & discovery
- Proactive Agent: reactive → active assistance (arXiv:2410.12361)
- PROBE: proactive bottleneck resolution benchmark — search/identify/execute, ~40% frontier ceiling (arXiv:2510.19771)
- ProAct: idle-time compute, long-term grounding, value-aware utility-vs-interruption evaluation (arXiv:2605.25971)
- ProActor: timing-aware RL for proactive scheduling (arXiv:2605.24900); PPP: joint Productivity/Proactivity/Personalization training (arXiv:2511.02208); PRIME: training-free proactive reasoning via memory evolution (arXiv:2604.07645)
- Experience Compression Spectrum: unifying memory, skills, and rules (arXiv:2604.15877) — basis of §10.1 routing
- Task mining (industry): desktop-activity pattern detection, automation-potential scoring (UiPath, Mimica, Skan, ABBYY category)

### Academic — measurement
- τ-bench (pass^k, environment-state grading); TRAJECT-Bench; MAST (arXiv:2503.13657); Who&When; TraceElephant; AgentAtlas (control decisions); CLEAR (arXiv:2511.14136); cost-of-pass (Efficient Agents, arXiv:2508.02694); CostBench; AgentDojo; AgentHarm; principled agent-safety measurement (distributional verdicts)
- PROV-AGENT (arXiv:2508.02866) + W3C PROV; reasoning-provenance (AER)

### Standards & open source
- OTel GenAI + MCP semantic conventions (SIG since 4/2024; v1.37 message-attribute overhaul; still Development status) · OpenLLMetry · OpenInference · OpenLineage/Marquez · OpenMetadata (memories & agent workflows as governed assets)
- Durable execution / workflow: Temporal (state for years; HITL suspend/resume; retry-until-valid-LLM-output) · Inngest · Restate · Cloudflare Workflows · AWS Durable Functions · LangGraph persistence/interrupts (inner layer of the two-layer pattern) · Atomix (transactional-outbox gating for irreversible agent effects, arXiv:2602.14849)
- Eval harnesses: DeepEval (pytest-native) · Inspect AI (UK AISI; Task/Solver/Scorer/Sandbox) · agentevals/openevals · Strands Evals. Note: promptfoo acquired by OpenAI (3/2026); OpenAI hosted Evals sunsets 11/2026
- Observability: Langfuse (ClickHouse-acquired 1/2026) · Arize Phoenix · MLflow Tracing · AgentOps · Laminar · Helicone

### Market
- Assistant-per-employee: Glean (enterprise + personal graph; editable personal graph; agent sandboxes; 100+ MCP actions) · M365 Copilot · Gemini Enterprise · Moveworks · Rovo
- Shared-context compounding: **Dust** (multiplayer thesis; shared surface; memory loops; dual-layer permissions; 300k agents, 240% NRR) — differentiate via personal-agents/collective-learning
- Representative products: Read AI Digital Twin ("represents you"; approval gates; consent UX worth studying)
- Eval/observability commercial: LangSmith · Braintrust · Galileo (distilled 3B/8B judges — fleet-scale scoring economics) · Latitude (trace→issue→eval closed loop) · Confident AI · Datadog (native OTel GenAI)
- Internal exemplars of the category: Ramp Glass, Stripe Minions (organizational sponsorship as moat)

---

### Academic — onboarding, socialization & knowledge scouting
- Organizational socialization: Bauer & Erdogan meta-analytic line (incl. 2025 update: 123 studies, ~198k respondents); formal-onboarding systematic review (on-the-job > orientation, PLOS ONE 2023); bibliometric map of the field (452 articles, 2024); future-of-work extension (informal knowledge transmission lost in digital settings — augment, don't replace)
- Legitimate Peripheral Participation: Lave & Wenger 1991; Wikipedia/CSCW empirics (Halfaker et al. reader-engagement experiments CSCW'13; newcomer homepage, CSCW'23; Kraut & Resnick, *Building Successful Online Communities*); majority-disengage-after-first-interaction finding
- Information Foraging Theory: Pirolli & Card; LLM/chat extension (Ragavan et al. 2024 — trust supersedes scent; prey-specification cost)
- Curiosity-driven acquisition: Schmidhuber 1991; Pathak ICM 2017; Curiosity-Driven Knowledge Retrieval for Mobile Agents (WWW'26 — uncertainty-triggered retrieval, AppCard pattern); GUI-Explorer (autonomous knowledge mining, ACL'25); knowledge-acquisition taxonomy for GUI agents (internal/historical/external exploration)
- Known bottleneck: low propensity for proactive exploration dominates agent failure on latent-knowledge tasks (Task2Quiz, arXiv:2601.09503)

### Academic — PKM, hypertext & personal knowledge graphs
- Lineage: Bush's Memex (1945) → Nelson/Engelbart hypertext → MyLifeBits ("fulfilling the Memex vision"; passive capture at scale) and MIT Haystack — lesson: capture without structure fails; structure + links make retrieval work
- PIM field: Jones & Teevan (*Keeping Found Things Found*; NSF PIM workshops); six senses of personal information; keeping/finding/meta-level activities; **navigation preferred over search in personal collections** (Bergman et al.)
- Zettelkasten (Luhmann): atomic notes + dense links → emergence; independently converged upon by agentic memory (A-MEM)
- Personal Knowledge Graphs: Balog & Kenter research agenda (SIGIR-ICTIR 2019); PKG ecosystem survey & roadmap (arXiv:2304.09572)
- Retrieval: GraphRAG survey (arXiv:2501.13958); KG-RAG survey (construction flaws: duplicate entities, wrong relation semantics → entity resolution first-class); LLM-empowered KG construction survey (KG as dynamic grounding infrastructure; bottom-up schema induction); PersonalAI 2.0 (adaptive iterative graph traversal with planning, arXiv:2605.13481)
- Sensemaking/HCI: low-cost collection & triage (Wigglite), mixed-initiative synthesis (Synergi), curation metrics (Kerne)
- Product mechanics (market): Obsidian (derived backlink/graph indexes over plain files), Roam/Logseq (block atomicity; unlinked references; Datalog-queryable graph), Tana (supertags = schema-on-note), Mem/Notion AI (embeddings + RAG layer)

## 13. Open Questions & Build Order

### Open questions
1. Harness: Claude Code-class agent runtime per user vs. custom orchestrator? Auth model per connector (per-user OAuth vs. service accounts)?
2. Profile generation: templated at setup, hand-authored, or inferred-with-review (editable-graph pattern)?
3. Corpus promotion mechanics: curator role vs. endorsement threshold vs. hybrid; who arbitrates conflicts between scopes?
4. Disclosure policy language: expressive enough for real norms, simple enough for the policy editor?
5. Class C fidelity sampling rate: how much "on my behalf" review is enough labeling without becoming toil?
6. Exploration budget size and assignment (per-agent vs. per-invocation lottery)?
7. Token/cost economics of always-loaded scoped context (five-scope cascade compounds context weight).
8. Departure-export policy: exactly which lineage source-types in the personal layer count as "personal" vs. "org-derived" at export time (§10.3)?
9. Discovery-loop cold start: how many weeks of observation before first proposals, and what floor on candidate confidence?
10. Role-template governance: who owns a role's template, and what evidence threshold adds a skill to it? **[Resolved in §3.4: the cross-cutting guild/chapter curates its role's template, evidenced by fleet data; threshold remains open.]**

### Build order (maturity-gradient sequencing)
*(Authoritative sequencing lives in the validation plans — the fork plan for current work, the mainline plan for platform phases. This list is the shape, not the schedule.)*
0. **Safety prerequisites (before any real data touches the system):** threat model + data-subject map (§15.1–15.4, F6); DPIA + LIA + Gate-4 lawful basis (F7); taint mechanism (§7.7, S1); **Ledger 9 deletion propagation (§5.3, C6) — before colleague data is ingested.**
0b. **Job compilation on the pilot users** (§11.2–11.3) — one-time ingest (with compilation-injection scan), compiled job graph + Day One Brief; time-to-first-value under one hour is the gate for everything after.
1. **Instrument Class A** — looped tasks on 2–3 users; Ledgers 1, 6, 7, 8, 10; pass^k + edit-distance + cost-of-pass dashboards. Production-as-eval proven here.
1b. **Multi-user prerequisites (Phase 2.5) — before recruitment widens:** E2E personal layer + attestation-gated key unwrap (T1/S8); access self-ledgering (T2); aggregate-only query layer with structural absence (T6). Trust machinery ships ahead of the population it protects.
2. **Prove the pillar-3 loop** — one skill improvement, staggered rollout, measured redistribution efficacy (§4.5).
3. **Add the corpus** — team scope only; directory-first index; promotion gate; Ledger 3 lineage; corpus-as-repo portability from day one (§10.2).
4. **Extend to Class B** — drafting skills; edit-distance as primary KPI.
5. **Open Class C carefully** — two agents, one task type (status queries); "on my behalf" review feed from day one; Ledgers 4, 5; fidelity metrics (§4.4) as the research contribution.
6. **Mission control** — render the ledgers; adaptive autonomy envelope; interruption budget.
7. **Turn on the discovery loop** (§9) — observe-only warmup, then low-volume proposals with shadow trials; acceptance rate as KPI.
8. **Role templates** (§10.3) — extract the first template from the pilot users' proven skill sets; provision the next new team member from it; measure ramp-time delta as the headline outcome.
9. **Scale scopes** — org/division/company cascade; brokerage detection (§8.3); sensemaking mitigations (§8.8).

---

## 14. Deployment Topology & Packaging

### 14.0 Responsibility model (policy-neutral by design)
Team OS does not adjudicate what data a user may ingest — no more than git or Dropbox do. Source eligibility belongs to whoever holds the deployment: the individual on a personal install; the organization (via §16) on a sanctioned one, where the company's own control planes (workspace app-approval, MDM, SSO) are the outer enforcement layer — Team OS integrates with the privilege system, never replicates it. The product ships policy *surfaces*, not policy: opt-in source defaults, provenance on everything (Ledger 3), a configurable source allowlist that holds the deployer's rule and ships with none.

### 14.1 The framing rule
**Files are the system of record; the database is operational machinery.** Corpus, skills, templates, and profiles live in git as plain files (§10.2). Ledgers, derived indexes, work objects, and workflow state are machinery — rebuildable and exportable. Consequence: **who hosts the database is a packaging decision, not an architecture decision.** Standing up a team database is organizationally hard (permissions, access, IT process) — so the product absorbs that, and the customer never faces it.

### 14.2 Three packages (same architecture, different custody)
1. **Self-managed / local-first.** Per-user harness on customer machines; repos wherever the customer controls; ledgers as JSONL/SQLite; cron/launchd scheduling; PRs as promotion gates with CI as Gates 2–3. Note: "local" means *customer-controlled*, not cloud-free — self-managed teams may still quietly use managed primitives (hosted git, managed SQLite/Postgres). Deployable in a weekend; the air-gapped variant (fully local models + files) lives here.
2. **Managed cloud — the product.** Team OS hosts the runtime, ledgers, indexes, work-object service, and durable execution. The team's total obligations: **connect inputs (SSO/OAuth connector grants — the same grants the §11 cold start requires anyway) and receive outputs (their existing surfaces).** No platform team, no database provisioning, no permissions project. This is what makes the sub-one-hour cold start real for teams without infrastructure engineers — "point at inputs and outputs" extended from the agent to the entire system.
3. **BYOC / hybrid.** Team OS control plane, customer-VPC data plane, for compliance-bound enterprises. Note: **ledger replication to customer-controlled storage is a mandatory feature of the managed tier regardless** — Art. 19's "logs under their control" means a hosted-only ledger is a compliance gap for the customer (§5.2).

### 14.3 Portability as the trust architecture
**Scope note (multi-user encryption):** "exit = clone" means a leaver's clone delivers *their own decryptable scope plus shared artifacts they hold keys for* — never another principal's encrypted personal store. The promise is completeness of *your* knowledge, not omniscience over the repo.
**Exit = `git clone`.** Portable by construction: corpus, skills, templates, profiles (plain files); ledgers (OTLP/JSONL export — required for compliance anyway); personal memory (principal-keyed, exported per §10.3 lineage policy). Derived indexes never need porting — they rebuild from files. This is the Obsidian open-files promise at team scale, inverting the enterprise-KM lock-in default — and it is the *adoption argument* for the managed tier: teams accept hosted convenience because exit is guaranteed cheap. Commercial posture: **sell operations, never custody of knowledge.**

### 14.4 Model routing (orthogonal axis — with one non-orthogonal seam)
**Routing×disclosure invariant:** every endpoint in the route table carries a residency/attestation label; a task may only route to an endpoint whose label satisfies the active tier's disclosure sentence (§14.7). A T2 "we cannot read your personal layer" promise must not silently break because a hard task fell back to a non-attested endpoint — the router enforces the tier, not just the capability match.
Local models (Apple Silicon/MLX, Ollama) for high-volume batch work — job compilation (one-time, overnight-able), Class A digests/triage, embeddings, idle-time discovery mining. Cloud frontier models for Class B drafting and fidelity-critical Class C. Router in front of the harness (LiteLLM-class); Ledger-10 canary suite validates every swap. Fully-local posture viable in package 1.

### 14.5 Multi-device rule
**One runtime; never two agents.** The agent needs an always-on home (home server in package 1; the product's containers in package 2). Single-writer event log: all state mutations flow through the one runtime; devices are projections. Phone = Plane-1 surfaces (agent inbox as Slack/iMessage DMs; approvals, digests, queries in chat) plus remote session attach; laptop = console plus synced files. Mission control is desktop; a chat thread with your own agent is 90% of mobile.

### 14.6 Grounding
Local-first software ideals (Kleppmann et al., Ink & Switch): data ownership, offline operation, **sync as a service, not a silo**. Packaging precedents: Obsidian + Obsidian Sync (local files, optional managed E2E sync); GitHub (managed hosting of a portable-by-protocol artifact wins *because* the artifact is portable).

### 14.7 Tier transparency table

**Two laws:** (1) *The runtime must live on something that stays on* — a machine you keep powered, or a cloud; every deployment is that choice per component. (2) *The capture boundary is the residency boundary* — ambient observation of local state requires local residence; the cloud runtime sees only granted cloud sources. **Two independent axes:** observation breadth (what the system can view) and custody (who else touches it) — the daemon tier maximizes both sight and privacy simultaneously; the managed tier trades vendor-touched machinery for zero operations, mitigated by E2E + attestation.

| | **T0 On-Demand** | **T1 Serverless (self-custody)** | **T2 Managed (product)** | **T3 Daemon (local)** |
|---|---|---|---|---|
| Runtime | none (summoned) | your cloud accounts | vendor cloud (attested) | your always-on machine |
| **LLM lives** | provider API, per call | provider APIs (or TEE-attested endpoints); no local option | vendor-routed: frontier APIs + vendor-hosted models in TEEs; org sets routing policy | **hybrid**: local models on the box (batch/high-volume) + frontier API (hard tasks); air-gapped = local only |
| Can view | pasted/pointed only | granted cloud connectors + synced folders | T1 + fleet aggregates | T1 + designated local folders |
| Cannot view | everything else | local disk, unsynced files, DMs/email unless enabled | T1 + personal layer (E2E, vendor-blind) | excluded folders; DMs/email still opt-in |
| Others touching data | model API, transient | your git host/storage + model API (or TEE) | + vendor infra (E2E + attestation mitigated) | fewest; zero if air-gapped |
| Automation | none (assistant, not representative) | full: loops, ambient, Class C, discovery (cloud sources) | T1 + fleet learning, templates | max: + local-file capture, sub-second, offline, local inference |
| Stops when | you stop | never | never (SLA) | box down → queue + catch-up (lateness, never loss) |
| Footprint | CLI | **zero resident software** | zero on user devices | signed, open-source, TCC-prompted daemon |
| **What's installed** | optional CLI binary (invoked, never resident) | **nothing** — browser + existing apps (Slack etc.); optional CLI | **nothing on user devices**; IT grants OAuth centrally; optional mobile/desktop thin clients | daemon installer on the always-on box (supervisor binary + launchd/systemd registration + repo skeleton + keychain entries); optional local models (GB-scale weights); menu-bar app; other devices: nothing (clients only) |
| **Control surface** | CLI flags + config file | web mission control (self-hosted, reads your accounts) + CLI + chat commands + repo files | vendor web mission control + chat commands | local web UI served by daemon + menu-bar app + repo files + chat |
| You operate | nothing | accounts | nothing | the box |
| Best for | trial/skeptics | **default** | teams/orgs | privacy maximalists, local inference, local files |

**Boundaries invariant at every tier:** DMs/email opt-in per source; discovery corpus principal-private; no individual-telemetry query surface exists (aggregates with compiled floors only); personal layer principal-keyed; all access to a principal's data self-ledgered to their feed; exit = clone.

**Per-tier disclosure sentences** (the "what I'm listening to" screen, verbatim): T0 "I see only what you show me." T1 "I can see your shared team spaces, calendar, and synced folders; not your local disk, DMs, or email unless you turn them on; everything rests in your cloud account — which is your trust boundary (your personal layer is encrypted, but the compute plane can decrypt it to work, so whoever holds your cloud account effectively holds the keys)." T2 "Same sight as T1; we run the machinery in attested enclaves, we cannot read your personal layer — here's the attestation." T3 "I can also see the local folders you've designated — and almost no one else sees anything at all; keys never leave your box."

**Who detects/responds** (honesty row): T0/T1 self-custody — **nobody watches in real time** unless you wire detection to your own alerting; the ledgers are forensic, not a SOC. T2 — vendor security operations monitor fleet anomalies (never individual content). T3 — you, plus the daemon's self-audit. This row is a selling point for T2 and a disclosed limitation for T1.

**Design disciplines:** intrusiveness buys automation — every increase in observation surface must purchase a named capability (no ambient capture for its own sake; compile-don't-pile). Local disk as off-the-record is a *feature*: contextual integrity enforced by geography ("I cannot see your local files" is architecturally true at T1/T2). Local-file coverage at T1/T2 rides existing sync clients (borrowed daemon) or deliberate share-in (capture as an act, not an observation).

**Control surfaces (where the user manages the system).** Four layers, ordered by immediacy, with **control parity across tiers** — every tier exposes the same controls, housed differently:

1. **Chat — the universal remote.** The agent is a control surface for itself, from any Plane-1 surface including the phone: "pause", "stop reading #general", "what can you see right now?", "show me what you told Maria's agent this week", "undo that". Conversational control commands are gated actions like any other — executed through Ledger 2, confirmable, reversible. The kill switch is reachable from every surface, always.
2. **Mission control — the standing dashboard** (web at T1/T2; served locally by the daemon at T3; menu-bar quick controls at T3). Houses the §7.1 Plane-3 set: activity feed, agent inbox, "what I'm listening to" (the §14.7 disclosure rendered live, per-source toggles), memory/profile editor, disclosure-policy editor, skill manager + report cards, "on my behalf" review feed, autonomy-envelope view, access-transparency feed (who touched my data), tier switcher, and export ("take everything").
3. **Files — deep config as code.** Profiles, policies, schedules, routing tables are repo files; any editor is a control surface, every change is a commit (Ledger 6), reviewable and revertible. The Obsidian property: the app is optional, the format is the interface.
4. **Admin/curator consoles** (team+ scale, separate from personal mission control by construction): curator's promotion queue and canon manager; IT's connector grants, tier policy, ledger-replication settings. **Structural absence preserved:** the admin console contains no individual-telemetry views — not hidden, not permissioned: absent (§8.6).

Rule: *every control action is itself a ledgered event* — managing the system produces the same tamper-evident records as the system's own actions, so "who changed the disclosure policy and when" is always answerable.

**Where the LLM lives.** The model is the one component that is *stateless by design everywhere* — no learning lives in the weights (§10.3); the LLM is a rented reasoning engine that your data visits, transiently, per call. So "where does the LLM live" really means **where does your data go during inference, and under what terms**:
- **T0/T1:** frontier provider APIs — prompts transit the provider's cloud under its retention terms (ZDR/enterprise agreements where available), or **TEE-attested inference endpoints** where the provider proves cryptographically which code touched the plaintext (§15.5 mechanism 3; the answer to "E2E data must still be decrypted to be computed on").
- **T2:** vendor-routed per org policy — frontier APIs and/or vendor-hosted open models inside attested enclaves; the routing table is an admin-console control, and mutual attestation (provider verifies enclave before releasing weights; user verifies enclave before releasing data) is the target posture.
- **T3:** the hybrid that justifies the tier — local models on the always-on box (Apple Silicon/MLX-class) for the batch-heavy volume: job compilation, digests, embeddings, discovery mining; frontier API only for tasks that need it (Class B drafting, fidelity-critical Class C). The **air-gapped variant** routes nothing out: local models only, at a capability cost.
- **Every tier:** the router (§14.4) assigns model-to-task by class; **inference location is disclosed per interaction** (a provenance detail on outputs: which model, where, attested or not); the Ledger-10 canary suite validates any endpoint or model swap. Prompts are transient at the inference location; nothing persistent of the principal's lives there.

**What's installed (complete inventory per tier).** The install footprint is itself a trust property — the less resident software, the smaller the malware-shaped surface and the shorter the security review:
- **T0:** an optional CLI binary — invoked per use, never resident, no persistence registration, no background permissions. Uninstall = delete the binary.
- **T1:** **nothing.** The system is your browser (mission control), your existing apps (Slack/email — already installed), and cloud jobs in your accounts. Optional CLI for power users. This is the tier's headline: full representative-grade automation with zero installed software.
- **T2:** **nothing on user devices.** IT grants OAuth centrally (a configuration act, not an installation); employees' laptops run only what they already ran. Optional thin clients (desktop wrapper for mission control, mobile app for session attach) are conveniences, never requirements — Plane-1 chat covers their functions.
- **T3:** the full self-custody kit, all on the **always-on box only**: the daemon (one supervisor binary; signed + notarized + open-source), OS service registration (launchd/systemd, `KeepAlive`), the repo skeleton and encrypted personal-memory directory, keychain entries for tokens, TCC permission grants (prompted in context, per capability), optionally local model weights (GB-scale) and the menu-bar app. **Every other device — laptop, phone — installs nothing**: they are clients of the box (Door 1 chat; Door 2 mesh attach). Uninstall is enumerable and complete: deregister the service, delete binary + repos + keychain entries; nothing else was touched.
- **Invariant:** the phone never installs a runtime at any tier; connectors are grants, not installs; and anything installed is signed, listed, and removable with a published uninstall that leaves zero residue — the install inventory *is* the first page of the security review packet.

---

## 15. Threat Model, Data Subjects & Separation of Powers

*This section opens with adversaries and data subjects, then derives mechanisms — reversing the reactive order that four review councils flagged. It absorbs the red-team amendments, the five-mechanism trust stack, abuse resistance, and the third-party data-subject architecture.*

### 15.1 Why this section leads with a model
Every prior control in this document was derived reactively, review by review. That pattern is itself the finding: features without an adversary model leave whole categories unprotected (the councils independently discovered the unprotected third party and the malicious principal). A STRIDE-style pass over the composition diagram — harness, runtime/daemon, stores, gates, A2A, fleet services, with trust boundaries drawn — is a Phase-0 work item (F6), revisited at every phase gate.

### 15.2 Adversaries (personas)
1. **The employer** — most probable abuser; standing bossware demand for the individual telemetry this system exhausts. Defended by structural absence (§15.6).
2. **The malicious principal** — weaponizes their own agent: machine-speed scraping of colleagues via Class C, plausible-deniability harassment ("the agent misunderstood"), insider threat with a tireless proxy. Defended by rate limits, Class C reciprocity, and **non-repudiable principal accountability** (the principal owns their agent's actions via Ledger 2 — stated policy, not implied).
3. **The intimate/coercing abuser** — installs on a partner's account; or an abusive manager "requests" a report enable ingestion (every gate passes, consent recorded, surveillance achieved). Defended by coercion resistance (§15.7).
4. **The insider / compromised admin / compromised curator** — a phished curator federates malware through a fully-compliant Gate 3.5; an admin who can freeze agents can silence them. Defended by access self-ledgering, signing + sandbox (Gate 3.5), and the freeze/kill separation (§15.8 tension 1).
5. **The external attacker** — prompt injection through every input source (§15.3); webhook/perimeter; supply-chain (dependencies, update channel, GitHub-org root of trust).
6. **The vendor (us) and its future owner** — concentration risk at T2; monetization/acquisition/compulsion pressure. Defended by can't-read cryptography and incentive durability (§15.6, §15.9).
7. **The compute-account compromise** — at T1 the crown jewel: key access + connector tokens + ledgers in one account. Defended by attestation-gated key unwrap (S8) and named honestly in the T1 disclosure.

### 15.3 Injection through input sources
Injection risk = (who can write the source) × (agent capability while reading) × (persistence afterward). The per-source trust-tier table and the taint mechanism live in §7.7; the model-level commitments:
- **Trust gradient is inverted from intuition:** quasi-trusted machine-formatted sources (calendar invite bodies, external PR/issue text, transcripts) are the dangerous middle band — anyone can write them, the loops read them as data.
- **Ambient loops are more injectable than chat** (no competing human intent in context) → capability minimization per loop; digest loops are read-only.
- **Compilation is injection with a time machine** → historical exemplars treated as fully tainted; imperative content extracted and quarantined inside C2, before downstream defenses exist.
- **Memory/corpus write is the highest-consequence action** (persistence + privilege escalation) → highest friction under taint, above external send.
- **A2A is transitive and wormable** → inbound untrusted-by-default; cross-agent taint via Ledger 4; hop counts and per-pair rate limits.
- **Structural rule:** untrusted content supplies *values*, never *plan structure* (CaMeL). Static injection suites (T5) are necessary and insufficient.

### 15.4 Data subjects — the non-user majority (deepest finding)
The system protects its *users* and observes its users' *worlds*. Most people in the data never consented: colleagues whose messages are compiled, counterparties modeled by pairwise calibration, org-chart neighbors in the directory, meeting attendees in debriefs. **Non-user data subjects get a rights surface:**
- **Notice** — a discoverable statement that agents compile shared-space content; team-level disclosure at deployment.
- **Access** — a colleague's DSAR is answerable: lineage (Ledger 3) locates their content across the corpus.
- **Erasure** — routes through Ledger 9 deletion propagation (§5.3) identically to first-party erasure.
- **Modeling limits** — **pairwise calibration of a non-user is impermissible by default** (modeling "what works with Maria" when Maria isn't a user and has no visibility). This may be the feature sacrificed for third-party legitimacy; decided here, not deferred.
- **Contextual-integrity flow map** (work item V2): every ingestion path annotated sender-context → new-recipient → new-purpose; borrowed-daemon norm-laundering acknowledged; the tier table's "can view" re-expressed as flows, not sources.

### 15.5 The five-mechanism trust stack (each answers a different adversary)
1. **Aggregation guarantees → the employer.** Differential privacy with a declared epsilon budget (not bare k-anonymity, which falls to intersection and longitudinal attacks). Precedent: Viva Insights' aggregate-only manager surface and the Productivity Score backlash — individual workplace telemetry is radioactive even for Microsoft.
2. **Can't-read cryptography → the vendor's will.** E2E on the personal layer with principal-held keys + key transparency (auditable key logs). Precedent: Signal's subpoena responses; 1Password Secret Key; Obsidian Sync.
3. **Hardware attestation → the vendor's infrastructure and admins.** TEE-attested inference and processing; mutual attestation (provider verifies enclave before releasing weights; user verifies enclave before releasing data). Precedent: Apple PCC; Anthropic's confidential-inference whitepaper direction. Closes the gap that E2E can't: data must be decrypted to be computed on.
4. **Secure aggregation → the fleet-learning layer.** Federated-learning discipline: the aggregator learns only the aggregate, never a per-agent contribution. Tier-3 pooling becomes a secure-aggregation computation.
5. **Contextual integrity + accountable access → insiders.** Nissenbaum's appropriate-flow as the governing theory of the gates; Weitzner's information accountability as the charter for access self-ledgering — every access to a principal's data by any party (admin, curator, vendor operator, support) posts to that principal's own feed. Where prevention fails, misuse is visible and attributable.

The market pattern: each surviving product picked *one* mechanism as its identity (Signal→2, Apple→3, Viva→1, Glean→5-lite). Team OS's threat model requires all five composed — which is the strongest section of the enterprise pitch and the honest reason a privacy-credible incumbent is the natural home.

### 15.6 Architecture over policy: structural absences
Policies are one reorg from revision; architecture is not. Three commitments are made structural, not procedural:
- **No individual-telemetry query surface exists** — not permissioned-off, *absent* from the query layer; no person-keyed performance join is buildable (verified by code audit, A-T6). A bad VP can flip a setting; they cannot summon a surface that was never built.
- **Personal layer is principal-keyed** with attestation-gated unwrap (S8) — "can't read" over "won't read."
- **Metrics designed least-harmful-when-leaked** — aggregate outcomes (cycle time, ramp delta) are the sanctioned value language (§8.6); assume leakage, minimize its harm.

### 15.7 Coercion resistance (vulnerable users)
The IPV/tech-abuse playbook as tested controls (work item V5): installation binds to the principal's authenticated session; presence is **non-suppressible** (menu-bar + periodic "I'm active" notices that cannot be hidden); new device attach / connector grant / policy change notifies the principal on every surface; **duress affordances** in mission control. Scenario in the register: abusive-manager-compliant-gates (every gate passes, surveillance achieved) — the defense is that the *surveilled* principal is always notified and can object, and that certain manager-initiated ingestions of a report's data are simply not offered.

### 15.8 The never-build list (the ceiling on "intrusiveness buys automation")
"Every increase in observation must purchase a named capability" needs a ceiling, or it normalizes a ratchet. Refused at any observation price: keystroke/screen capture; sentiment scoring of individuals; covert (non-disclosed) observation; individual productivity ranking; retention of raw personal-comms beyond compilation; pairwise modeling of non-consenting non-users; any surface that re-identifies aggregates. This list existing is what separates a principled architecture from an efficient one.

### 15.9 Incentive durability (surviving our own Series B)
The E2E-default, structural-absence, and never-custody commitments are exactly what an acquirer pays to remove, and at T2 the *payer* (employer) diverges from the *surveilled* (employee) — the business model's original sin. Mitigations with teeth, not aspirations: change-of-control privacy covenants; publish the ledger-minimization schema so degradation is *detectable*; open-source the gate/query layer so structural absence is *verifiable*; foundation/trust structure for the commitments. Obsidian's lesson — *who pays is a privacy mechanism* — applied where the money actually is.

### 15.10 Detection, response & resource limits
**Self-attestation residual (accepted until mechanism 3 ships):** the trust substrate — gates, hooks, ledgers — executes inside the runtime it polices; a compromised runtime/harness defeats them by construction, since a component cannot attest to its own integrity. The mainline answer is hardware attestation (§15.5 mech 3) plus supply-chain hardening (S7) and tamper-evidence (T4); **until those exist, the residual is accepted and disclosed at pilot/self-custody tiers, and closing it is a T2 launch prerequisite** — not an oversight, a sequenced choice.
Ledgers are forensic, not a SOC; ten unread logs detect nothing in real time. Required (work items S4–S6): near-real-time rules over L1/L4/L10 (baseline deviation, corpus canary tokens, A2A anomalies); an IR runbook with a **tested fleet-freeze** (halt skill distribution mid-propagation); per-agent compute budgets with hard stops (cost-DoS defense); A2A hop counts / TTL / back-pressure (amplification defense). The freeze/kill separation (tension 1): a security freeze halts *distribution*, never kills a *principal's agent*, and the principal is notified — so the containment power cannot become a silencing power.

### 15.11 Open tensions (decisions, not defects)
1. Admin fleet-freeze vs. abuse resistance → freeze = distribution-halt only, principal-agent kill never, principal notified.
2. Payer ≠ surveilled at T2 → covenants + open-sourcing mitigate, never dissolve.
3. Pairwise calibration of non-users → impermissible by default (§15.4); revisit only with a genuine non-user consent path.
4. Detection at T1 self-custody → "nobody watches in real time" is honest and disclosed (§14.7 row); acceptable for self-custody, a reason to choose T2 otherwise.
5. Estimation vs. gate framing at pilot scale → slower certainty accepted over false precision (build plan methodology).

---

## 16. System Administration & Operator Console

*User control surfaces (§14.7 layers 1–3) are for governing your own agent. This is the surface for operating the **system** — a separate trust domain, and the most dangerous one, because it's where an insider or compromised admin does maximum damage. It inherits every constraint from §15.*

### 16.1 The five responsibility areas
1. **Fleet operations** — loop health, scheduler status, queue depths, per-agent compute budgets and spend (§15.10/S6), model-router policy, canary-suite results (Ledger 10).
2. **Member lifecycle** — provisioning humans *and* ownerless agents (§3.5); assigning scopes and templates; **offboarding** — the operator console is where the kill-chain (S3b) is triggered and where "this member is fully dead" is *verified*.
3. **Security operations** — detection alerts (S4); the IR runbook and the **fleet-freeze** control (S5). Someone must hold the button; §15.11 tension 1 is an *admin permission boundary* built here: freeze halts distribution, never kills a principal's agent, principal notified.
4. **Compliance operations** — DPIA/LIA artifacts; retention-window settings; DSAR intake incl. third-party (V1); ledger export/replication (Art. 19).
5. **Trust configuration** — connector allowlists; skill-signing policy (Gate 3.5); disclosure-policy defaults per scope; lawful-basis settings.

### 16.2 The console is the highest-scrutiny surface
- **Every admin action is itself ledgered** and pushed to affected principals' feeds — the watch-the-watchers rule (§15.5 mech 5) applies *hardest* here.
- **No individuation surface, by construction** — the admin console contains no person-keyed performance join (§8.6); absent, not permissioned-off. This is the single most important structural absence, because admin is exactly where the temptation and the power coincide.
- **Admin access is itself gated and time-boxed** — elevation is an event with a reason, a duration, and a record; standing god-mode does not exist.
- **Separation from curator and user surfaces** — knowledge governance (curator: promotion queue, canon) is distinct from system operation (admin: fleet, security, compliance) is distinct from self-governance (user: own agent). Three domains, three consoles, deliberately not merged.

### 16.3 Ownerless-agent administration
**Creation requires two-person integrity:** a compromised admin must not be able to mint an ownerless agent and name themselves owner-of-record (an accountable-to-the-attacker Class-C participant). Creation takes a second approver (another admin or a standing owner outside the console), and the creation event posts to a fleet-level audit surface — not only to the (creator-chosen) owner's feed, which the attacker controls.
Agent members (§3.5) are provisioned, owned, and offboarded here: the owner-of-record binding, the anomaly-alert routing to that owner, the tighter taint/rate policy. An ownerless agent's entire lifecycle is an admin-console concern because there's no principal to self-manage it.

### 16.4 Deployment placement
Admin console is a **multi-user-operations concern (fleet phase)** — needed only when multi-user operations are real; single-user (M0–M3) has no fleet to operate. At T1/T3 self-custody the operator *is* the user (the console degrades to the CLI + repo + the "who detects" honesty of §14.7); at T2 managed it's the surface the customer's IT/security/compliance functions use, with the vendor operating the layer beneath and — by the structural-absence rule — unable to see individual telemetry even as operator.
