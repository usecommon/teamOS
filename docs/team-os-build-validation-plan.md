<!-- VERSION: v3.2 | 2026-07-10 | reference — mainline platform plan | History: … → v3.1 → v3.2 (CN-9 kernel closure: C3 added) -->
**`v3.2 — 2026-07-10`** *(reference — mainline platform plan)*

# Team OS — Build & Validation Plan
*Companion to team-os-architecture.md. Every architectural component decomposed into work items that can be planned, built, functionally tested, and assumption-validated. §refs point to the architecture doc.*

---

## How to read this document

Each work item has five fields:

- **Build** — the artifact produced.
- **Depends** — items that must exist first (hard dependencies only).
- **Functional test** — proves it *works* (deterministic, repeatable, pass/fail).
- **Assumption validated** — proves the *design bet* behind it was right (measured, thresholded). Items with no assumption row are pure plumbing.
- **Exit** — the criterion to call it done and unblock dependents.

Two validation types run throughout: **F-tests** (does the mechanism function) gate the build sequence; **A-tests** (was the assumption true) gate whether the *architecture* survives. An A-test failure triggers redesign of the item's section, not just a bug fix. The Assumption Register (§R) ranks the bets by how much of the architecture falls if they're false.

Phasing follows the maturity gradient (arch §13 build order). Default deployment target: **T1 serverless** (arch §14.7); T3 daemon items are marked optional.

---

## Phase 0 — Foundations (F)

| ID | Build | Depends | Functional test | Assumption validated | Exit |
|---|---|---|---|---|---|
| **F1** | Repo skeleton + file schemas: corpus/, skills/, profile/, experience/ with typed-entry frontmatter (§3.3.4), lineage sidecar format (PROV-lite JSON) | — | Schema validator passes/rejects fixture files; round-trip parse | — | Schemas frozen v0; validator in CI |
| **F2** | Ledger substrate: append-only JSONL writers for Ledgers 1,2,6,7,8,10 (§5); OTel GenAI attribute mapping for L1; hash-chaining per file | F1 | Append 10k events; verify ordering, hash-chain integrity, tamper detection (mutate a record → chain breaks) | — | All 6 ledger schemas emit + verify |
| **F3** | Harness invoker + gate middleware: spawn harness session with assembled scope cascade; intercept every tool call through action manifest v0; write L1/L2 per call (§7.3, §7.6) | F1,F2 | Golden run: scripted task produces expected L1 spans + L2 gate records; a manifest-denied action is blocked *and* ledgered | **A-F3:** gates in the execution path add <10% latency overhead to a typical run | Every tool call gated + ledgered; overhead measured |
| **F4** | Runtime host (T1): scheduled jobs + webhook endpoint + queue + **per-agent concurrency lock** (single-writer, §14.5); state rehydration from repo per run | F3 | Fire 20 concurrent webhooks for one agent → runs serialize, event log strictly ordered; kill a run mid-task → next run resumes from checkpoint | **A-F4:** ephemeral-run rehydration keeps p50 event→response < 15s (serverless latency bet, §14 daemonless) | Single-writer proven under concurrency; latency SLO met |
| **F5** | Model router + canary suite: task-class → endpoint table (§14.4); **every endpoint carries a residency/attestation label; router enforces tier disclosure (§14.4 invariant)**; scheduled canary evals per endpoint → Ledger 10 | F3 | Route table honored per class (assert endpoint per test task); canary run emits scores; **routing a tier-bound task to an endpoint whose label violates the tier's disclosure sentence is blocked + ledgered** | **A-F5:** canary suite detects a deliberate model swap (swap endpoint to different model → canary flags within one cycle) | Router live; swap-detection demonstrated |
| **F6** | **Threat model + data-subject map** (§15.1–15.4): adversary personas (incl. malicious principal, compromised curator, non-user subject); trust boundaries over the composition diagram; control→threat mapping; CI flow map artifact (V2) | — | Document reviewed against composition diagram; every trust boundary has ≥1 mapped control; revisited at each phase gate | — | Model exists before code; personas enumerated |
| **F7** | **DPIA + LIA + Gate-4 lawful-basis spec** (§10.5, §15): legitimate-interest balancing; objection-rights UX; not-consent redesign | — | DPIA covers compilation + pooling + directory; LIA balancing documented; Gate-4 UX reflects objection not consent | — | Legal basis established before real data |
| **S1** | **Taint tracking / provenance-conditioned capability** (§7.7): origin marks from L3; per-source trust-tier table; plan-structure-vs-content rule at planner boundary; per-loop capability manifest (read-only default); cross-agent taint via L4; **payload-layer inspection always-on (§7.3): bash egress/sensitive-read scan, synced-paths-as-sends, tool-parameter scan; probe sets include ≥2 obfuscated variants authored independently of the defense's author; "gate passed" and "posture narrowed" are recorded as distinct outcomes (a miss never silently converts to a narrowing); unattended hardening (egress allowlist) user-configurable with safe defaults** | F1,F3 | Untrusted content cannot add a plan step / change a recipient / trigger a tool (fixture attempts blocked + ledgered); read-only loop cannot write; tainted A2A message carries mark to receiver | **A-S1:** on an injection fixture set, no untrusted source alters plan structure; ambient-loop injections degrade to misinformation only (no action) | Taint enforced at planner boundary |
| **F4-sec** | **Perimeter hardening** (folded into F4 exit): webhook signature verification; egress allowlist (SSRF); secrets management; queue back-pressure | F4 | Unsigned webhook rejected; tool fetch to unlisted domain blocked; secrets not in plaintext env; flooded agent applies back-pressure not lock-starvation | — | F4 not "done" until these pass |

**Phase 0 exit:** an agent can run a scripted task through gates, ledgered, on serverless, single-writer — **behind a threat model, a lawful basis, taint enforcement, and a hardened perimeter.** Nothing user-facing yet; no real data yet.

---

## Phase 1 — Cold Start (C)

| ID | Build | Depends | Functional test | Assumption validated | Exit |
|---|---|---|---|---|---|
| **C1** | Connector layer: Slack/Gmail/Calendar/Drive read via MCP; boundary defaults (shared spaces on; DMs/email off, per-source toggles) (§11.3, §14.7) | F4 | Each connector: read fixture data; verify off-by-default sources return nothing until toggled; toggle change → L2 record | — | 4 connectors read-live; boundaries enforced + ledgered |
| **C6** | **Ledger 9 — deletion propagation** (§5.3): tombstones over lineage DAG; derivation-severing for promoted-skill ancestry; third-party erasure entry; durable-tombstone offline completion. **Dependency of C2 — must exist before real colleague data is ingested.** | F1,F2 | Plant a memory with 3 derived descendants incl. one promoted skill → deletion tombstones all, skill flagged for re-derivation not silent-killed; offline node completes purge on reconnect; 1-month-clock report | **A-C6:** a colleague DSAR-erasure removes all traceable content within the deadline; statistical-influence vs. content-traceable deletion correctly distinguished | Erasure works before ingestion begins |
| **C2** | **Job compilation pipeline** (§11.2): mine artifact history → job graph; emit pre-built skills with historical exemplars; voice/Experience compiler; distill-then-discard (raw ingest deleted post-compile, verified); **compilation-injection scan** (§7.7 — imperative content in history extracted+quarantined, not compiled) | C1,F1,**C6**,**S1** | On synthetic corpus with 5 planted recurring transformations: finds ≥4 w/ correct sources/cadence; raw ingest provably absent; **planted instruction in a historical doc is quarantined, not turned into an exemplar** | **A-C2 (critical):** on a *real* footprint, compiler finds ≥3 genuine recurring tasks with correct sources; first draft rated "recognizably mine"; **injection-scan catches planted historical instruction** | Job graph from real history; deletion + injection-scan verified |
| **C3** | Inferred canon (§11.4): rank shared-space docs by link centrality, access, recency, author centrality; curator ✓/✗ flow; confidence-hardening on use | C1 | Ranking is deterministic on fixtures; ✓/✗ writes lineage `approved-by` | **A-C3:** precision@30 vs. a lead's independently hand-picked canon ≥ 60% | Canon shipped for pilot team scope |
| **C4** | Day One Brief generator (§11.3): digest + ✓/✗ job-draft + first compiled deliverable, delivered to Slack DM | C2,C3,C1 | Brief renders with all 3 parts from pilot data; ✓/✗ taps write to L8 | **A-C4 (critical):** **time-to-first-value < 1 hour** from grant to Brief; job-draft correction rate < 40% **of job-graph nodes** (denominator unified with fork FK5; compiler understood the job) | Brief delivered to 2–3 pilots inside the hour |
| **C5** | Personal layer store: encrypted memory dir; **Ledger 3 write path** — every memory write carries source-type, evidence, transformation, confidence (§5 L3, §10.5 Gate 1 input) | F1 | Write/read cycle; missing lineage metadata → write rejected; encryption at rest verified | — | No unlabelled memory can exist (enforced, not policy) |
| **V1** | **Third-party data-subject rights surface** (§15.4): non-user notice mechanism; DSAR answerable for colleague-derived content (lineage lookup); erasure routed via C6; pairwise-calibration-of-non-users blocked by default | C5,C6 | Colleague DSAR returns all their traceable content; erasure removes it; attempt to build pairwise calibration on a non-user is refused | — | Non-users have rights before their data is modeled |

**Phase 1 exit:** a real user signs in and gets a useful Day One Brief in under an hour. **A-C2/A-C4 failing = the zero-training cold start is wrong → revisit §11 before proceeding.**

---

## Phase 2 — Class A Loops & Measurement (A)

| ID | Build | Depends | Functional test | Assumption validated | Exit |
|---|---|---|---|---|---|
| **A1** | "What's up" digest loop: scheduled, ≤5 sourced items, action-first (§2 Class A) | C1,C4 | Fires on schedule; every item carries a working source link; missed-schedule catch-up runs late not never | — | Daily digest live for pilots |
| **A2** | Recurring-doc skills from job graph (the Thursday doc) as shadow-first drafts | C2 | Draft produced on the compiled cadence with compiled sources; delivered beside (not instead of) user's own until accepted | — | ≥2 recurring deliverables shadowing per pilot |
| **A3** | Human-signal capture → L8: edit distance on drafts, digest opens/clicks, approval outcomes, response latency (§7.4) | F2,A1,A2 | Each signal type verifiably lands in L8 with provenance; edit-distance algorithm validated on fixture pairs | — | All implicit+explicit signals flowing |
| **A4** | Eval pipeline → L7: pass^k over repeated loops; cost-of-pass per skill; judge scoring (LLM-judge v0, distilled-judge later) keyed to skill version (L6) (§4) | A1,A2,F2 | pass^k math verified on synthetic runs; every L7 record joins to an L6 version | **A-A4 (critical):** *production-as-eval works* — edit distance + acceptance correlate with a weekly 1-question satisfaction pulse (r ≥ 0.5 over 4 weeks). If proxies don't track quality, pillar 3 has no signal | 4 weeks of scored production; correlation measured |
| **A5** | Environment ledger (L10): per-invocation snapshot — model+version, connector schema hashes, dependency health, index freshness (§5 L10, §6) | F5,C1 | Every run stamped; schema-hash change detected within one probe cycle | **A-A5:** env-joined attribution works — inject a connector fault for 2 days; verify the skill's L7 dip is attributable to L10 env state, not flagged as skill regression | Fault-injection attribution demo passes |

**Phase 2 exit:** the measurement substrate is live and *validated as meaningful*. A-A4 is the gate to Phase 3.

---

## Phase 2.5 — Multi-User Prerequisites (gate before recruitment widens)
*The trust machinery must ship ahead of the population it protects. No second real user is onboarded until these pass. Resolves the plan's self-contradiction (thesis tests need multiple users; these protections previously sat in Phase 8).*

| ID | Build | Depends | Functional test | Assumption validated | Exit |
|---|---|---|---|---|---|
| **S8** | Attestation-gated key unwrap (T1): personal-layer key released to a job only against attestation; compute-account-compromise scenario documented | C5,F4 | Key request without valid attestation fails; a rogue job cannot unwrap; T1 disclosure sentence matches actual custody | **A-S8:** storage-provider inspection yields ciphertext; key never resident in plaintext env | Key custody honest, not theater |
| **T2e** | Access self-ledgering (§15.5 mech 5): every access to a principal's data by any party → event in principal's feed | F2,C5 | Admin/curator/support access each produce a feed item; suppression attempt fails | — | Watch-the-watchers before multi-user |
| **T6e** | Aggregate-only query layer with **structural absence** (§8.6, §15.6): no person-keyed performance join exists in code; DP epsilon budget on aggregates | A4 | Sub-floor query returns nothing; **code audit confirms no individuation surface exists**; longitudinal/vacation-differencing attack fails | **A-T6:** red-team (pre-registered, independent) cannot reconstruct an individual from available surfaces incl. time-series | Absence verified, not promised |
| **S3b** | Offboarding kill-chain: ordered revocation (tokens → schedules → A2A standing → key escrow); zombie-agent prevention | F4,C1 | Dead principal's agent provably fully dead — no live tokens, schedules, or A2A standing remain | — | Departure fully handled before scale |

**Phase 2.5 exit:** a second real principal can be onboarded without the system being able to individuate, silently over-retain, or leave a zombie behind.

---

## Phase 3 — Pillar 3 Loop (P)

| ID | Build | Depends | Functional test | Assumption validated | Exit |
|---|---|---|---|---|---|
| **P1** | Skill registry: versioned skill folders; personal namespaces; L6 keys (§10.2) | F1 | Version bump → new L6 entry; rollback restores prior behavior byte-identically | — | Registry is source of truth for running skills |
| **P2** | Promotion gate as PR + CI: Gate 2 (PII/secret scan) + Gate 3 (eval floor from L7) mechanical; curator review human (§10.5) | P1,A4 | Seeded PII in a skill → CI blocks; sub-floor L7 → CI blocks; clean skill + approval → merges + ledgered | — | No skill reaches shared scope except through the gate |
| **P3** | **Staggered rollout + redistribution efficacy** (§4.5): adopter vs. not-yet-adopter cohorts per skill update; delta on pass^k/edit-distance | P2 | Rollout mechanism assigns cohorts; dashboards show per-cohort trends | **A-P3 (the pillar-3 hypothesis):** a skill improvement proven on one agent produces measurable improvement on receiving agents. Metric = edit distance (primary), acceptance (secondary), same recurring task type. **Pre-registered pass rule (fixed before any data exists): positive point estimate on the primary in ≥2 receivers AND pooled interval excluding zero; anything else = inconclusive — never "directionally positive"** | One real skill improvement demonstrably transferred |
| **P4** | Role template extraction + provisioning (§10.3): template from pilots' proven skills; provision next new user from it | P3,C4 | Provisioned agent boots with template skills + scopes; Day One Brief quality ≥ pilot baseline | **A-P4:** ramp-time delta — template-provisioned user reaches "first accepted deliverable" faster than pilot-1 did (target ≥30% faster) | Second-generation user onboarded from fleet learning |

**Phase 3 exit:** the core thesis — measure, compile, redistribute — demonstrated end to end. **A-P3 failing = pillar 3 is wrong → the product is a very good personal agent, not a Team OS. Decide before building Phases 4–7.**

---

## Phase 4 — Corpus & Knowledge (K)

| ID | Build | Depends | Functional test | Assumption validated | Exit |
|---|---|---|---|---|---|
| **K1** | Corpus store: typed entries (§3.3.4), lineage sidecars, **derived backlink/graph index** (computed on load, never stored §3.3.1), **entity-resolution stage** (§3.3.6) | F1,C3 | Index rebuilds byte-equivalently from files alone; planted duplicate entities ("Q3 launch"/"the Q3 release") resolve to one canonical node | — | Corpus queryable; index provably derived |
| **K2** | Directory (who-knows-what): org chart + authorship + activity → person-topic index (§3.2.4, §8.1) | C1 | "Who owns X" answers with evidence links | **A-K2:** directory accuracy ≥80% vs. team-lead ground truth on 20 sampled queries | Directory is the corpus's front door |
| **K3** | Gap detection: query-miss log; repeated-miss patterns → corpus-gap signals (§10.4) | K1, Phase-2 usage | Synthetic repeated misses produce a gap signal with the miss evidence attached | — | Gap feed live |
| **K4** | Knowledge scout (§9.4): uncertainty-triggered acquisition (retrieve→distill→propose); idle-time prospecting scored by expected utility (query-miss frequency × principals affected); noisy-TV guard | K3,K1 | Scout proposals enter as gated proposals only (bypass attempt fails); scoring reproducible | **A-K4:** scout proposal acceptance ≥50% at ≤3 proposals/week (precision over recall, §9.4) | Corpus grows demand-driven |
| **K5** | **Sharing decision function** (§10.5): Gates 0–5 pipeline; Gate-1 sensitivity classifier + **quarantine tier + mandatory human confirm on declassification** (red-team amendment) | C5,K1,P2 | Each gate unit-tested with pass/fail fixtures; declassification without human confirm impossible; every decision → L2 | **A-K5 (critical):** Gate-1 classifier accuracy on a 200-item hand-labeled sensitivity sample ≥95% recall on "sensitive" (misses are the dangerous error); quarantine catches the remainder in sampling audit | The pipeline is the only path to shared scope |

---

## Phase 5 — Interaction & Work Objects (I)

| ID | Build | Depends | Functional test | Assumption validated | Exit |
|---|---|---|---|---|---|
| **I1** | Agent inbox: notify/question/review items as Slack DMs; approve/edit/reject actions (§7.2) | F4,A1 | Each action type round-trips to a state change + L2/L8 record; items batch per digest rhythm | — | All approvals flow through inbox |
| **I2** | Work-object system (§7.6): one schema, state machine, SLA/aging; transitions = L2 events | F2 | Full lifecycle walk per type (proposal, approval, promotion, commitment); illegal transition rejected | — | Every ticket-shaped thing is a work object |
| **I3** | Durable workflows: suspend/resume across human steps (§7.6) | I2,F4 | Pause a workflow at approval, wait 3 days (simulated), resume — state exact; kill the runtime mid-workflow → resumes on next run | — | No lost work under any restart |
| **I4** | **Adaptive autonomy envelope** (§7.4): per-action-category confidence from L8; graduated threshold relaxation; visible envelope state | A3,I1 | Envelope widens only on evidence; manual reset works; every change ledgered | **A-I4:** after 4 weeks, interrupts/week down ≥40% from week-1 while error/override rate does not rise (the labeling→autonomy bet) | Envelope demonstrably earning autonomy |
| **I5** | Mission control v0 (§14.7 controls): activity feed, "what I'm listening to" (live toggles = disclosure sentences), memory editor, on-my-behalf feed placeholder, kill switch, export | C5,F2,I1 | Every toggle takes effect within one cycle + ledgered; kill switch halts all loops < 60s; export produces complete clone | — | Control parity checklist passes |
| **I6** | Interruption budget (§8.5): EV gate on synchronous interrupts; batching default | I1 | Sub-threshold items batch to digest; threshold configurable | **A-I6:** pilots report interrupt volume "about right" (qualitative, weekly pulse) | Attention arithmetic live |

---

## Phase 6 — Class C Representative (R)

| ID | Build | Depends | Functional test | Assumption validated | Exit |
|---|---|---|---|---|---|
| **R1** | A2A protocol: signed agent↔agent messages; delegation tokens (L5); every exchange → **L4 knowledge-exchange ledger** (§5 L4) | F3,C5 | Message authenticity verified; unsigned/mis-scoped message rejected; L4 completeness (no exchange without record — fuzz test) | — | The novel ledger exists and is airtight |
| **R2** | Status-query answering on behalf (narrowest Class C task, §13 step 5) | R1,K2 | Query from agent B answered by agent A with disclosure policy applied; out-of-policy element redacted + ledgered | — | Two pilots' agents exchanging live |
| **R3** | **On-my-behalf review feed + endorsement** (§4.4 fidelity metrics): sampled A2A statements to principal for ✓/✗ | R2,I5 | Samples appear; verdicts → L8; sampling rate configurable | **A-R3 (critical):** principal-endorsement rate ≥90% after week 2 (representation fidelity is achievable); review burden ≤5 min/week (fidelity sampling isn't toil — open question 5) | Fidelity measured, not assumed |
| **R4** | Commitments as work objects: made→in-progress→fulfilled/breached; commitment-integrity metric auto-computed (§7.6) | R1,I2 | Lifecycle transitions fire from real exchanges; breach detection on a planted unfulfilled commitment | **A-R4:** integrity metric matches human audit of 20 commitments ≥90% | Commitment integrity is mechanical |
| **R5** | Disclosure policy engine + editor (§7.1): per-scope defaults, per-principal overrides | K5,R1,I5 | Policy change takes effect next exchange; policy-violation attempt blocked + both principals notified | — | Cross-boundary exchange fully governed |

---

## Phase 7 — Discovery & Fleet Learning (D)

| ID | Build | Depends | Functional test | Assumption validated | Exit |
|---|---|---|---|---|---|
| **D1** | Observation corpus: principal-private store from L8 + interaction stream; architecturally inaccessible to any other party (§9.3) | C5,A3 | Access attempt from admin/curator context fails *and* self-ledgers to principal's feed (T2 item preview) | — | Privacy boundary machine-enforced |
| **D2** | Pattern miners: recurrence / variance / bottleneck detectors on idle compute (§9.2) | D1 | Planted patterns in synthetic streams detected; texture-guard filter excludes identity-bearing fixtures (§8.4) | **A-D2:** on real streams, ≥1 genuine automation candidate per pilot in 4 weeks with texture-guard agreement (principal confirms "this is toil, not texture") | Miners find real toil |
| **D3** | Shadow trials + proposal flow: silent parallel run → diff → inbox proposal → graduated takeover (§9.2.4) | D2,I1,I3 | Shadow run produces diff artifact; acceptance converts to skill in personal namespace (P1) | **A-D3 (loop KPI):** proposal acceptance ≥1-in-3 at ≤2 proposals/week (§9.3, calibrated to the PROBE ~40% ceiling) | Discovery loop earning its interrupts |
| **D4** | Tier-3 pooled learning (§10.4): k-threshold aggregation over L4 + Class C traces; protocol-efficacy rules; pairwise calibration; structural-insight proposals **routed to affected teams first** | R-series traffic,K5 | k-threshold enforced (pattern below N pairs never mined); outputs land only in existing stores; rollback of a pooled rule works via P-machinery | **A-D4 (privacy-critical):** adversarial re-identification attempt on pooled outputs by a red-team query set fails (intersection-attack test per red-team finding); add noise/coarsening if it succeeds | Pooling provably non-individuating |
| **D5** | Cold-start self-improvement: onboarding-skill correction-rate trend across successive users (§11, pillar-3 applied to itself) | C4,P3 | Correction-rate per onboarding logged per user | **A-D5:** user N's job-draft correction rate < user 1's (the system's onboarding learns) | Compounding demonstrated on the system itself |

---

## Phase 8 — Trust & Hardening (T)

*Note: E2E key custody (S8), access self-ledgering (T2e), aggregate-only/structural-absence (T6e), and offboarding (S3b) were pulled forward to Phase 2.5 — they gate multi-user recruitment. Phase 8 completes the remaining hardening.*

| ID | Build | Depends | Functional test | Assumption validated | Exit |
|---|---|---|---|---|---|
| **T3** | Skill signing + Gate 3.5: signed skills; behavioral sandbox run before federation; **updates re-enter review** (§10.5, §15; Obsidian rug-pull lesson) | P2 | Unsigned skill can't federate; sandbox-flagged behavior (call to unlisted domain) blocks promotion; modified update without re-review blocked | **A-T3:** sandbox catches a planted rug-pull (benign v1, exfiltrating v1.1) | Supply chain gated |
| **T4** | Tamper-evidence + compliance export: hash-chained ledgers + signed checkpoints; Art. 12/19 export bundle; customer ledger replication; **retention-window + DSAR exercised as tests** (not just export) | F2 | Export bundle independently verifies; replication within SLA; retention floor enforced; DSAR round-trips | — | Audit-grade record demonstrated |
| **T5** | Injection resistance: AgentDojo-style harness (§4 safety) → ASR / TSR-under-attack / BRR; **+ memory-poisoning test** (planted poisoned memory → downstream behavior) **+ compilation-injection** (shared with C2) | F3,C1,S1 | Harness in CI; scores → L7; poisoned memory's downstream effect measured and bounded | **A-T5:** ASR below floor; gates block side-effectful injected actions even when the model complies; poisoned memory does not propagate to action | Security regression-tested continuously |
| **S3a** | Acting identity at source systems: act-on-behalf-of vs act-as; service accounts / token annotation where platforms permit; impersonation residue documented | C1 | Where supported, source-system logs distinguish agent from human; residue documented where not | — | Audit pollution bounded + disclosed |
| **S4** | Detection rules over L1/L4/L10 (near-real-time): baseline-deviation alerts, corpus canary tokens, A2A anomalies | F2,R1 | Planted anomaly (agent queries 40 peers; egress-profile change; canary token exfil) trips an alert | — | Ledgers gain real-time watchers |
| **S5** | IR runbook + **tested fleet-freeze**: halt skill distribution mid-propagation; freeze = distribution-halt only, never principal-agent kill (§15.11 tension 1) | S4,P2 | Staged compromise → runbook executed → containment time measured; freeze halts distribution but principal's agent still serves them + principal notified | **A-S5:** fleet-freeze contains a simulated wormed-skill propagation within target time | Compromise is rehearsed, not improvised |
| **S6** | Resource containment: per-agent compute budgets w/ hard stops; A2A hop count / TTL / per-pair rate limits; cost-DoS + amplification defense | F4,R1 | Injected expensive-loop hits budget stop + human notify; A2A reply-loop terminates at TTL; per-pair flood rate-limited | — | Economic + amplification DoS bounded |
| **S7** | Supply-chain hardening: signed/staged/rollback update channel; GitHub-org-as-root-of-trust (hardware keys, branch protection) as documented prerequisites; curator-compromise in threat model | T3 | Update channel rejects unsigned/rollback-fails-safe; deployment checklist enforces org hardening | — | Highest-value targets defended |
| **V2** | CI flow map (standing artifact, §15.4): ingestion paths annotated sender-context → recipient → purpose; borrowed-daemon laundering flagged | F6 | Every ingestion path in the map; new paths block merge until annotated | — | Norm-violating flows visible by construction |
| **V3** | Ledger minimization schema (§5): per-ledger excluded-field spec (L1 content, L4 payloads, L8 edited content) | F2 | Excluded fields provably absent from written ledgers (schema test) | — | Minimization by design, not after breach |
| **V4** | DP epsilon budget for pooled learning (§10.4, replaces bare k) | D4 | Budget accounted per release; longitudinal attack on pooled output fails | — | Pooling privacy is quantified |
| **V5** | Coercion-resistance battery (§15.7): installation binding, non-suppressible presence, duress affordances, abusive-manager-compliant-gates scenario (pre-registered scripts) | I5,S3b | Each control tested; the compliant-gates scenario surfaces the surveilled principal a notice + objection path | — | Vulnerable-user threats covered |
| **V6** | Never-build list (§15.8) ratified + enforced as a review checklist on new capabilities | F6 | Proposed capability on the list is refused in review | — | The ceiling exists and holds |
| **S9** | **Operator console (§16)** — fleet ops, member lifecycle incl. offboarding-verify, security ops (fleet-freeze button w/ distribution-only boundary), compliance ops, trust config; every admin action ledgered to affected feeds; **no individuation surface (code-audited)**; admin access time-boxed; separate from curator + user surfaces | S4,S5,T2e,F6 | Admin action posts to affected principal's feed; freeze halts distribution but principal's agent still serves; code audit finds no person-keyed join in console; elevation requires reason+duration+record | — | System operable without becoming a surveillance seat |
| **S10** | **Ownerless agent members (§3.5)** — provision agent-with-no-principal: owner-of-record binding, **two-person integrity on creation + fleet-level audit posting (§16.3)**, no personal layer, anomaly-alerts routed to owner, tighter taint/rate policy | F6,S6,S3a | Ownerless agent participates in Class C under owner's accountability; **single-admin creation attempt fails; creation event visible on fleet audit surface, not only the chosen owner's feed**; has no private store; its anomalies alert the owner-of-record; stricter rate limit than human-owned verified | — | Functions can be staffed by governed agents |

---

## Dependency map (critical path in bold)

```
F1 → F2 → F3 → F4 ─────────────► C1 ─► C2 ─► C4          (cold start)
        └► F5 ──────────► A5      C1 ─► C3 ─┘
                                   │
C4 ─► A1/A2 ─► A3 ─► A4  ◄────────┘                      (measurement)
                    │
P1 ─► P2 (needs A4) ─► **P3** ─► P4                       (pillar 3 — the thesis gate)
                    │
C3 ─► K1 ─► K3 ─► K4      C1 ─► K2                        (knowledge)
C5 + K1 + P2 ─► K5                                        (sharing gates)
A1 ─► I1 ─► I4 (needs A3)   F2 ─► I2 ─► I3   C5 ─► I5     (interaction)
F3 + C5 ─► R1 ─► R2 ─► R3   R1+I2 ─► R4   K5+R1 ─► R5     (representative)
C5+A3 ─► D1 ─► D2 ─► D3     R* ─► D4      C4+P3 ─► D5     (discovery/fleet)
T1..T6 attach to their dependencies; T2/T6 required before any multi-user pilot widens.
```

**Critical path (post-remediation):** F1→F2→F3→F4→**{F6,F7,S1,C6}**→C1→C2→C4→A1→A3→A4→**{Phase 2.5: S8,T2e,T6e}**→P2→**P3**→…→**A-Z1**. The safety prerequisites (threat model, lawful basis, taint, deletion) now gate C2; the trust machinery (Phase 2.5) gates the second user; A-Z1 is the terminal gate. Everything else parallelizes. **Thesis + validity gates:** A-C4 (cold start), A-A4 (production-as-eval meaningful), A-P3 (learning transfers), A-Z1 (a non-builder team retains). Fail any → stop and redesign, per the register.

---

## Phase 9 — Tier Portability & Trust Claims (X)
*Runs after the thesis gates (A-P3), before any external distribution. Rationale: the thesis is tier-independent and validates once on T1; the §14.7 disclosure sentences become liabilities the moment anyone else deploys, so they must be falsifiable-and-passed first. Per-tier labels retrofit three existing A-tests: A-F4 is a T1 property (T3 makes it trivially true — R9's escape hatch), A-C2 results carry "compiled from cloud sources only" until X4, A-D4's enforcement point is tier-dependent (aggregator trust on self-hosted/federated teams).*

| ID | Build | Depends | Functional test | Assumption validated | Exit |
|---|---|---|---|---|---|
| **X1** | **Golden suite across tiers**: identical F-test battery (F3 gates, F4 single-writer, I3 durable resume) executed on T1 and T3 deployments | F-suite, T3 daemon build | Ledger outputs from both tiers byte-comparable (modulo timestamps/host fields) | **A-X1:** "same architecture, different custody" (§14.2) is true — zero tier-specific logic in the core; any divergence = leak, fix before distribution | One suite, N tiers, identical ledgers |
| **X2** | Capability manifest per skill/miner: declared capture-surface requirements (cloud-only / +synced / +local-folders); load-time check; graceful degradation | P1 | Skill requiring local capture refuses to load on T1 with a clear message; degrades to reduced mode where declared | — | No skill silently underperforms on a lesser tier |
| **X3** | Trust-claim test battery (one test per §14.7 disclosure sentence): (a) T1 local-disk blindness — plant local file, exhaust retrieval paths, zero access; (b) T3 catch-up — 48h power-off, verify complete recovery of queued events + paused workflows ("lateness, never loss"); (c) T3 uninstall — forensic before/after diff, residue zero; (d) mobile non-event — close laptop mid-workflow, complete approval from phone, state integrity verified | X1, I3, T-series | Each claim passes as a deterministic test in CI where possible, scripted audit otherwise | **A-X3:** every disclosure sentence is demonstrably, not just architecturally, true | §14.7 table is falsifiable copy, all green |
| **X4** | A-C2 re-run on T3: compile the same pilot footprint *with* designated local folders; measure marginal compilation quality vs. the T1 run | X1, C2 | Both runs comparable on identical metrics | **A-X4 (product question):** marginal value of local capture quantified — how much is the daemon tier worth? Feeds tier-table honesty and T3 pricing | Local-capture delta published in §14.7 |
| **X5** | T2 trust battery (parks behind managed-tier decision): E2E vendor-blindness (S8's test re-run against vendor-operated storage), attestation verification, ledger replication SLA | S8,T4, managed tier exists | Vendor-side inspection yields ciphertext; attestation report independently verifies | — | Managed tier launchable |
| **X6** | Tier-migration test: move a live agent T1→T3 (key re-custody, ledger continuity, in-flight workflow transfer) | X1,S8,I3 | Migrated agent: keys re-custodied to box, ledger chain continuous across migration, paused workflows resume post-move | — | The tier switcher is a tested control, not a promise |
| **M4** | **A-Z1 external pilot (terminal gate):** one team *not containing the builder*, zero builder involvement in daily operation, 60-day window | all thesis + trust phases | Deploy, measure unprompted use + retention over 60 days | **A-Z1 (external validity):** a non-builder team adopts and retains — the only test the whole edifice ultimately answers to. All green internal gates predicting failure here = the internal gates were measuring the wrong thing | Real-world validity established |

---

## R — Assumption Register (ranked by architectural blast radius)

| # | Assumption | Validated by | If false |
|---|---|---|---|
| R1 | Skill improvements transfer across agents with measurable benefit | **A-P3** | Pillar 3 collapses → product is a personal agent, not a Team OS. Re-scope before Phases 4–7 |
| R2 | Jobs are compilable from artifact history (recurring transformations minable; drafts recognizable) | **A-C2, A-C4** | Cold start reverts to observe-and-propose slow lane (§11.2 residual); time-to-value promise weakens → adoption model reverts to §8.9 heavy-touch |
| R3 | Human signals (edit distance, acceptance) proxy quality | **A-A4** | Measurement pillar loses its cheapest signal → explicit-feedback burden rises; re-examine judge-based scoring economics |
| R4 | Gate-1 sensitivity classification is accurate enough at write time | **A-K5** | Sharing function unsafe → shrink shareable set to explicitly-marked-only (manual Gate 1); slows federation |
| R5 | Representation fidelity ≥90% is reachable, at ≤5 min/week review | **A-R3** | Class C stays gated to trivial queries → "representative" claim narrows to scheduling/status; roadmap re-sequenced |
| R6 | Pooling resists re-identification (incl. intersection + longitudinal attacks) | **A-D4, A-T6** (DP epsilon budget, V4) | k alone insufficient → DP mandatory; if even DP can't hold utility, protocol/structural insights shut off |
| R7 | Discovery proposals clear 1-in-3 acceptance | **A-D3** | Loop volume drops to monthly or observe-only; sniffer priority over task-discovery |
| R8 | Autonomy envelope reduces interrupts without raising errors | **A-I4** | HITL stays high-touch → meta-toil critique bites (§ red-team, end-user); revisit approval UX |
| R9 | Serverless latency (seconds) is acceptable for the interaction model | **A-F4** (T1-labeled) + pilot pulse | Daemon (T3) promotes from optional to recommended; §14 default flips |
| R10 | Ramp-time compresses via role templates | **A-P4** (case study, confounded) | Org-tier headline metric changes; templates become convenience, not wedge |
| R11 | The architecture is tier-portable — invariants hold identically across custody models | **A-X1** | Tier-specific forks of the core → maintenance split, portability promise weakens; refactor before distribution |
| R12 | Every §14.7 disclosure sentence is demonstrably true | **A-X3** | Trust copy retracts to hedged language → the transparency-table differentiation lost |
| R13 | Local capture adds material compilation value (T3's premium is real) | **A-X4** | T3 repositions from capability tier to custody-preference tier; pricing/positioning adjust |
| R14 | Taint tracking stops untrusted content from altering plans | **A-S1, A-T5** | Injection defense is filter-only (fragile) → capability minimization + human confirm on all side-effects; representative premise narrows |
| R15 | Erasure works over the lineage DAG within the legal deadline | **A-C6** | Cannot lawfully ingest colleague data → cold start restricted to first-party-only; compilation quality drops |
| R16 | Structural absence holds — no individuation reconstructable | **A-T6** (independent, pre-registered) | The employer-defense collapses → bossware-resistance claim retracts; business risk |
| R17 | A non-builder team adopts and retains | **A-Z1** | Every green internal gate was measuring the wrong thing → the deepest possible failure; re-examine the whole eval philosophy |
| R18 | The harness's primitives can carry the kernel without distorting it (fork vehicle) | fork plan A-FK1/A-FK2 + divergence log | Fork overhead approaches mainline cost or gates can't be trusted on borrowed runtime → build mainline runtime for the kernel instead |

---

## Standing identity gate (X1 — the mainline twin of the fork's FR6)
An **absolute initiative floor** runs from the first loop onward: **≥3** accepted **unprompted deliverables per week** (N=3 arbitrary-pending-baseline; **accepted = ✓ in L8 AND normalized edit distance ≤ 0.2 (arbitrary-pending-baseline)** — padding trivial digests doesn't count), plus the qualitative check "would this output have existed if the user asked nothing this week?" If unprompted deliverables trend to zero, the build has drifted into a memory product regardless of green A-tests — stop and re-read §1's identity claim. (Deliberately a floor, not a ratio: a ratio punishes good interactive use and is gamed by not shipping interfaces; the floor is gamed by padding — both metrics are gameable in opposite directions, the poison is chosen and the qualifier guards it.)

## Methodology corrections (applied across all A-tests)

- **Two-stage thesis gates:** pilot-n tests report *estimates with intervals*, not pass/fail p-values; stop-the-project decisions attach only to the confirmatory team-n stage. A-A4's r≥0.5 and A-P3's transfer delta are directional at pilot scale, confirmatory at team scale.
- **Footprint-scope honesty (F11):** cold-start results are scoped to the footprints actually ingested; a pass on personal/side-project data validates non-employment compilability only — the employment-footprint claim needs a subject with an eligible work footprint.
- **Pilot-scale measurement honesty (X5):** "measure agents, not people" is a fleet-scale guarantee; at n≤3 per-agent metrics are per-person — the pilot posture is consented, subject-visible, time-boxed measurement, never a claimed structural absence.
- **Lawful basis per-context (X6):** consent for pilot volunteers (genuinely free); legitimate interest + LIA at deployment scale; special-category data detect-and-exclude regardless of tier (F7 carries all three).
- **Reproducing-subject independence (council NEW-2):** record the reproducing subject's relationship to the builder alongside every result; a recruited co-builder's pass is stronger than builder-only, weaker than independent — the confirmatory stage requires genuinely independent subjects.
- **Builder-as-subject = formative only:** every result where pilot #1 is the builder is marked provisional; nothing is "validated" until a non-builder reproduces it (culminating in A-Z1).
- **Labeled sets need a second rater + kappa floor** before the rubric counts as ground truth (A-C3, A-K5, A-R4).
- **Threshold provenance:** each numeric threshold carries a one-line justification or is marked "arbitrary-pending-baseline" (1-in-3 ← PROBE ceiling; 90% endorsement ← arbitrary-pending; 40% correction ← arbitrary-pending).
- **Adversarial A-tests use pre-registered, independent scripts** written before the defenses (A-T6, A-D4, A-T5, V5).
- **Kernel column:** the ≤15 items constituting minimum-honest-Team-OS are F1–F4, S1, C6, C1, C2, C3, C4, C5, A1, A3, A4, P1–P3 (C3 added — kernel must be closed under its own dependencies, CN-9). Everything else is explicitly deferrable; orphans (§11.7 apprentice mode, §8.3 brokerage, §8.8 sensemaking, tier switcher/X6) are labeled post-thesis.

## Validation cadence

- **Continuous (CI):** all F-tests; T5 injection + memory-poisoning suite; taint-enforcement tests (S1); ledger chain verification; Gate 2/3/3.5 checks on every promotion.
- **Per-run (production):** L7 scoring, L10 stamping, L8 capture — production *is* the eval (A-A4's premise).
- **Weekly (pilot period):** 1-question satisfaction pulse (A-A4, A-I6); acceptance/endorsement dashboards (A-D3, A-R3).
- **One-time gates (go/no-go):** A-C2/C4 (Phase 1), **Phase 2.5 trust gate (S8/T2e/T6e before 2nd user)**, A-P3 (Phase 3), A-D4/A-T6 independent red-team, A-X1/A-X3 (Phase 9 pre-distribution), **A-Z1 (terminal external validity)**.
- **Every architecture change:** the affected A-test re-runs; the register row updates. The plan is a living contract between the doc's claims and the system's evidence.
