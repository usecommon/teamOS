<!-- VERSION: v3.3 | 2026-07-10 | governing — fork SPEC | History: … → v3.2 → v3.3 round-3 (SE-4 path-b mitigations, X-1 first-install review feasibility) -->
**`v3.3 — 2026-07-10`** *(governing — fork SPEC)*

# Team OS — FORK: Harness-Native Implementation
*Forked from: team-os-architecture.md (16 sections, post-remediation), team-os-build-validation-plan.md (~70 items), team-os-council-findings.md (remediated). Those three documents are the frozen mainline base; this fork diverges without modifying them.*

**Fork thesis:** Mainline positions Team OS as the layer *above* the harness (§"is this a harness?" — no; the OS schedules and governs many harness instances). This fork inverts the build strategy while preserving the architecture's invariants: **implement Team OS *as* a single agent-with-harness**, using a Claude-Code-class harness's native primitives as the runtime, and Team OS becomes a *kit* — files, hooks, conventions, and scheduled invocations — installed into it. The OS-above-harness remains the destination; the harness-native agent is the vehicle that gets the kernel validated with weeks less plumbing.

**Identity claim (inherited from mainline §1, binding on the fork):** this is a **proactive, action-driven system, not a memory or corpus product**. The stores are organs; the initiative is the organism. Concretely for the fork: the scheduled headless loops (FK5–FK6) are the product; the MCP door and the stores exist to make unprompted action trustworthy and compounding. If the fork ever ships recall without initiative, it has drifted into the crowded category (Mem0/Supermemory-class) and lost the whitespace — the loops are not optional scope.

---

## 1. Why fork here

- The harness already ships 70% of Phase 0: session runtime, tool dispatch, MCP client, context assembly, permission prompts, transcripts, sub-agent spawning.
- The kernel's thesis gates (A-C4 cold start, A-A4 production-as-eval, A-P3 transfer) test *the idea*, not the infrastructure — mainline's own two-stage methodology says pilot-scale results are formative anyway. Validate formative on borrowed runtime; build owned runtime only for confirmatory.
- Claude Code's disk layout (~/.claude/commands, CLAUDE.md cascade, settings, session history) is near-isomorphic to the mainline store model — the fork exploits that isomorphism instead of re-implementing it.
- Risk being managed: mainline is a two-quarter solo platform build before the first thesis gate; the fork targets the same gates in weeks.

## 2. The mapping (mainline concept → harness primitive)

| Mainline (§ref) | Harness-native realization | Fidelity |
|---|---|---|
| Scope cascade (§3) | CLAUDE.md cascade: user-level → project-level → local; team scope = shared repo's CLAUDE.md | High — native |
| Skill registry (§10.2) | Skills / slash-commands as versioned folders in a git repo; personal namespace = user dir, team = shared repo | High — native |
| Corpus (§3.3) | Markdown repo, typed frontmatter, derived indexes via agentic search (grep/glob); no vector DB at kernel scale | High |
| Connectors (C1, mainline plan item) | MCP servers in config; boundary defaults = which servers/scopes are configured | High — native |
| Gates / action manifest (§7.3) | **Hooks** (pre-tool-use) enforcing allow/deny/ask + writing gate records; permission rules in settings | Medium — hooks exist; taint-conditioning is custom |
| Ledger 1 (traces) | Session transcripts (JSONL) post-processed into L1 schema | Medium — needs a transcript→ledger compiler |
| Ledgers 2,6,7,8 | Hook outputs (L2); git history (L6); a scoring script over transcripts (L7); edit-diff capture (L8) | Medium — thin custom scripts |
| Class A loops (§2) | Headless harness invocations on cron/launchd/Actions; each loop = a command + schedule | High |
| Job compilation (§11.2) | The harness runs C2 as its own first task — a compilation *skill* pointed at history + Claude Code's own footprint (commands→skills, CLAUDE.md→profile, transcripts→trajectories) | High — the fork's killer feature |
| Discovery miner / scout (§9) | Sub-agents on idle-time scheduled runs; proposals = files in an inbox dir | Medium |
| Work objects (§7.6) | GitHub issues (external) + an `inbox/` dir of markdown state-machine files (internal) | Medium — SLA/aging by script |
| Durable workflows (§7.6) | **Gap** — no suspend-for-days primitive; shim: checkpoint files + resume-on-next-invocation convention | Low — the biggest shim |
| Single-writer (§14.5) | One machine, one lockfile, serialized cron; no concurrent surfaces at kernel scale | Adequate for n=1–3 |
| Promotion gate (§10.5) | PR into the shared skills repo; CI = Gates 2/3/3.5 scripts | High — native git |
| Autonomy envelope (§7.4) | Permission rules edited *by script* as confidence accumulates (settings.json as the envelope's state) | Medium — novel but simple |
| Taint (§7.7) | Hook-level: source-tier lookup on tool inputs; write/send tools require confirm when session touched untrusted sources | Medium — coarser than mainline (session-granular, not datum-granular) |
| Mission control (§14.7) | The repo itself + a static dashboard generated from ledgers; chat = the universal remote (native) | Adequate |

## 3. Invariants preserved (non-negotiable in the fork)
Files-as-truth; every tool call gated + recorded; memory writes carry lineage; default-deny sharing (PR gate); L9 deletion before real colleague data (C6 survives the fork untouched); DMs/email opt-in; no individuation surface built; exit = clone (**scoped once multi-user encryption lands: a clone delivers your own decryptable scope + shared artifacts you're keyed for — never another principal's encrypted personal store**). **The fork changes the runtime, never the trust posture.**

### 3a. Responsibility model (policy-neutral by design)
Team OS does **not** adjudicate what data a user may ingest — no more than git, Dropbox, or Obsidian do. Source eligibility is the responsibility of whoever holds the deployment:
- **Individual install** (the fork's pilot case): the user's machine, the user's OAuth grants, the user's responsibility. No admin, no pretense of one.
- **Org-sanctioned deployment** (mainline §16): admin-provisioned; the organization sets source policy through the operator console.

In org deployments the **company's own control planes are the enforcement layer** — Workspace/Slack admin app-approval, MDM, SSO already gate which apps reach corp data and what installs on managed machines. Team OS *integrates with* the company privilege system; it does not replicate or replace it. A user without admin privilege who tries to connect an unapproved workspace is blocked at the workspace side, not by Team OS. (This is also the answer to the enterprise buyer's "how do you prevent shadow deployment": your existing app-approval controls do.)

**The product ships policy *surfaces*, never policy:** opt-in source defaults (nothing read until toggled — the toggle is the responsible party exercising their policy); provenance on everything (Ledger 3 lineage makes "which workspace did this come from" always answerable, so any policy is auditable after the fact); a configurable source allowlist (FK3b — the neutral configuration point where the user's or org's rule lives, empty of opinion, capable of holding one). Options to integrate; policy manages them.

**Thin-history acknowledgment (H-2/X10):** the fork's pilot footprints (builder + co-builders) are the most-compilable footprints available; A-C2 says nothing about thin-history users (new grads, career changers) — that failure mode and its fallback (observe-and-propose bootstrap) remain mainline-open and are not claimed here.

## 4. Deferred to mainline (explicitly out of fork scope)
Multi-surface projections + phone Door 2 (fork: Slack-DM loop outputs only; §9's app+CLI remote-drive ladder is a *posture*, not a new surface); Tier-3 pooled learning; A2A/Class C beyond two hand-configured peers; managed tier; DP machinery (n too small to pool anyway); datum-granular taint; detection/IR at fleet scale. Each remains specified in mainline; the fork's ledgers are written in mainline schemas so nothing collected is thrown away at merge.

## 5. Fork risks (honest)
1. **Harness API drift** — hooks/settings/transcript formats are product surfaces, not contracts; pin versions, wrap access in one adapter module.
2. **Session-granular taint is weaker** than §7.7's datum-granular design — acceptable at n=1–3 with human-in-loop, insufficient beyond; marked as a merge-back trigger.
3. **Durable-execution shim** (checkpoint files) will leak edge cases — bound it by keeping multi-day workflows out of kernel scope (approvals resolve in-session or via inbox files).
4. **Harness self-attestation residual (accepted, chosen):** every gate/hook/ledger runs inside the harness; a compromised harness defeats them by construction. Undefended at pilot scale by explicit decision (mitigations: version+surface pin, human review of harness updates); mandatory revisit before managed tier or merge-back.
5. **Isomorphism seduction** — the harness's shapes may quietly redefine the architecture (e.g., "skills are whatever slash-commands are"); the mainline doc is the spec, the harness is an implementation, and divergences get logged in §7 below.

## 6. Fork build order (kernel items only, re-sequenced)
1. **FK1** Repo skeleton + adapter module (harness paths → mainline store schemas)
2. **FK2** Hooks: gate with **always-on payload inspection** + L2 writer; **L3 lineage writer (every memory/corpus write carries source/evidence/transformation/confidence — consumed by FK3's deletion DAG, FK3b's provenance, FK1's must-map set)**; transcript→L1 compiler; L8 edit-diff capture — *the ledger substrate on borrowed runtime*
3. **FK3** C6 deletion propagation (unchanged from mainline — still gates ingestion)
4. **FK3b** Connector config + policy surfaces (neutral source allowlist, opt-in defaults, provenance)
5. **FK4-pre** Threat-model lite + lawful-basis note + pilot-source decision (user's choice, §3a)
6. **FK4** Compilation skill (C2): ingest eligible footprint (incl. Claude Code artifacts) → job graph, profile, first skills — **with the imperative-content quarantine**
7. **FK5** Day One Brief as a scheduled headless run → Slack DM (A-C4 measured here)
8. **FK6** Class A loops + scoring script, **path (a) runtime of record** (A-A4's four-week clock starts)
9. **FK6b** Envelope-by-script (autonomy earned on evidence)
10. **FK6c** Kit + minimal door — plugin packaging + MCP server (read + `propose_*` to the inbox, never the corpus); posture detection; the two experiments. **After the loops — loops-before-doors preserved by sequence, not by omission.** Required for FK7 and for path (b).
11. **FK7-pre** Multi-user prerequisites (per-principal encryption, access self-ledgering, no individuation surface) — before any collaborator's data
12. **FK7** Shared skills repo + PR gate + staggered adoption across 2–3 collaborators (A-P3)
13. **FK8** Discovery sub-agent + scout — only after the gates.

Same thesis gates, same thresholds, same register (R1–R18 apply; **R18: the harness's primitives can carry the kernel without distorting it** — validated by FK1–FK7 shipping with **divergence log ≤5 entries of class *architectural deviation*, none touching an invariant — R18's green is builder-classified and therefore formative like every builder-as-subject result (AT-8)** (entry classes: field-miss [FK1, uncounted here] / architectural deviation [counted] / experiment note [FK6c, uncounted]; threshold arbitrary-pending-baseline); **FR1–FR7** are the fork-specific rows in the validation plan).

**Loops-before-doors, stated once so it isn't mis-read:** the door (FK6c) is built *after* the loops (FK5–FK6) deliberately. The identity claim forbids shipping the interface *before* the initiative — not building the door at all. FK7 and path (b) both need the door; omitting it would make the thesis gate unrunnable. Sequence resolves the tension; exclusion would have broken it.

## 7. Divergence log (append-only, reviewed at merge-back)
- 2026-07-10 · **field-miss** (uncounted) · `skill.capability_manifest.capture_surface` — harness command format declares no capture-surface tier; import defaults to cloud+synced+local-folders; default recorded as default, not mapping. [FK1 gate]
- 2026-07-10 · **field-miss** (uncounted) · `corpus-entry.owner` — harness artifacts carry no ownership metadata; single-principal pilot defaults to principal; maps at FK4/multi-user. [FK1 gate]
- 2026-07-10 · **field-miss** (uncounted) · `ledger-l5.delegation_chain[].token_ref` — no OIDC/W3C-VC token primitive in harness or pilot; chains recorded without crypto tokens until mainline. [FK1 gate]
- 2026-07-10 · **field-miss** (uncounted) · `scope.disclosure_default` — CLAUDE.md cascade carries no disclosure policy; default-deny stands in structurally; populates at FK3b/FK7. [FK1 gate]
- 2026-07-10 · **experiment note** (uncounted) · harness cascade exposes 3 levels (enterprise/project/user); division/org have no harness counterpart at n≤3. Schema carries all five; adapter emits company/team/individual. Scope-level gap, revisit at merge-back. [FK1]
- 2026-07-10 · **method note** (uncounted) · A-FK1 counting rule: fork-native fields (fork writers author the datum; harness never its source) count as mapped — no translation, no loss possible. Human-reviewed at merge. [FK1 gate]
- 2026-07-12 · **architectural deviation** (counted) · RETROACTIVE for 2026-07-11: subagent spawn ledger + safety agent + circuit breaker shipped ahead of spec order and landed on main without entries. Machinery kept (autonomy-bounding, not mainline console scope); T9 remediation added enforcement (computed spawn depth/rate refusal, windowed safety counters, loop pre-flight wiring). [T9/T11 work order]
- 2026-07-12 · **architectural deviation** (counted) · RETROACTIVE for 2026-07-11: demo console/insights HTML surfaces shipped by name against the §16 do-not-build list. Reclassified: read-only fixture-fed DEMO renderings; no live controls claimed; per-person comparative rendering barred by the CI individuation audit (T12). Removal-or-FK-gate decision belongs to the human reviewer. [T11/T12 work order]
- 2026-07-12 · **experiment note** (uncounted) · FR2 Layer A implemented as SESSION-granular taint (hook-level session files; sends/schedules in a tainted session escalate). Matches the declared fork shape (§7.7 fork mapping, "coarser than mainline"); datum-granular remains the merge-back trigger. [T2]
- 2026-07-12 · **method note** (uncounted) · L8 principal authentication (CN-1) implemented as fork-local HMAC signing (principal_auth.py, keys outside repo, enforcement keyed on TEAMOS_PRINCIPAL_KEYDIR). Stands in for mainline identity/delegation infra; replaced at merge-back. [T7]
- 2026-07-12 · **method note** (uncounted) · ledgers/l3.jsonl removed from git tracking: a git-committed ledger holding evidence locators cannot honor erasure (FK3). Ledgers are runtime state; anchoring (SE-6) carries tamper-evidence, git carries code/config only. Prior git history still holds pre-removal records — history purge is a human decision. [T4]
- 2026-07-12 · **architectural deviation** (counted) · Irreversible boundary added to the gate (severity × reversibility, arch §7.3): external send/mutation/destruction/spend are deny-by-default, auto-permitting only on a match in the user-owned `config/allow-policy.md` (arch §8 deny-by-default allowlist + the one falsifiable guarantee — no irreversible act permits without an allow-match or a hand, each recorded pre-act). Reversible interior stays envelope-gated (WO-1). **CONSEQUENCE:** FK5/FK6 delivery (`slack_post_message`) is irreversible → now gated; the allow-policy SHIPS one rule authorizing the agent's delivery to its own principal (DP-1=A) so briefs/digests still arrive done, everything else deny-by-default. No invariant touched (this implements mainline §7.3/§8; it does not diverge from them). The shipped delivery-authorization default and whether to scope it to the principal's DM id is a **human product decision** (PR #2). [WO-3/WO-4 positioning-alignment work order]

## 8. Merge-back criteria
Fork graduates to mainline when any of: A-P3 passes and a second team wants in (fleet services now real); taint needs datum granularity (multi-user untrusted volume); durable workflows exceed the shim; or a tier promise (§14.7) must be demonstrated rather than described. At merge, the ledgers, corpus, skills, and register results transfer as-is — the fork's whole design goal is that **nothing validated needs revalidating**.

## 9. Kit packaging, scheduling & postures (B1-remediated)

**Two runtimes, two trust postures — declared, never blurred:**
- **Path (a) — runtime of record (full trust):** loops run as headless Claude Code sessions on the user's machine (local scheduled tasks / cron). **Inference requirement: owned — an API key or a local model (a subscription-authenticated local Claude Code session also qualifies if it runs the loops headless on this machine; the defining property is that hooks fire locally, not who bills the tokens). Connector eligibility: Team OS's own Plane-A connectors and locally-configured MCPs — all traversing the FK2 gate.** FK2 hooks fire, transcripts are on disk, L1/L2/L8 complete. **All FK6 validation and the A-A4 clock run here.** Validated surface of record: Claude Code Desktop + local scheduled tasks (pin version *and* surface).
- **Path (b) — cloud-scheduled (reduced trust, disclosed):** loops run as Cowork Scheduled Tasks / Routines on Anthropic's cloud. Our hooks do not demonstrably run there; session transcripts are not on our disk. **Fence:** path-(b) loop prompts may use *only* the Team OS door — read tools + `propose_*` — and **no direct third-party MCPs in scheduled prompts**. The door's server-side tool log is the partial-but-honest L1 for this posture. **Disclosure sentence:** "Loops run on Anthropic's cloud; only their Team OS actions are gated and recorded by Team OS; the session itself is governed by Anthropic, not by your hooks — and other connectors enabled on your Claude account **may be reachable to the session and are ungoverned by Team OS** — the linter checks the prompt, but the platform makes account connectors available to the session regardless." **Cheap mitigations, offered in setup (SE-4 — disclosure is not mitigation when mitigation costs a paragraph): run path (b) on a dedicated Claude account with no other connectors enabled (or disable them explicitly), and the door serves summary-tier views to path-(b) sessions (extending m2's brief posture) — so the injection chain door-read → corpus content → account-connector send has neither connectors to invoke nor full-content payloads to carry.**

**Write topology — inbox, never corpus (single-writer preserved everywhere):** the door's `propose_*` tools append to a **proposals inbox**, not the corpus. The gate processor at the runtime of record pulls the inbox, applies gates, commits, pushes — **it invokes the identical FK2 hook rule set (one implementation, two entry points) and its commits emit standard L2 records**; two drifting gate implementations is exactly the failure FR2 exists to prevent. Cloud sessions get read + propose only. CLI-holder posture: local runtime is the writer; the remote store is its pushed mirror + inbox. App-only posture: the door's server *is* the runtime of record and commits only after in-app human approval. "Local mirrors app activity" = `git pull`; the store the door serves is remote-reachable (private git remote / relay); local corpora are clones.

**Posture is detected, not assigned (upgrade ladder):** onboarding probes for a CLI footprint (`~/.claude`). Ladder: **app-only** (door + cloud loops, reduced trust) → **app + CLI-at-home** (the mobile app can remote-drive a local Claude Code session — if remote-driven sessions execute local hooks, this is full trust from the phone; FK6c experiment #2) → **CLI-native** (full kit). A CLI appearing later upgrades the posture; the upgrade is itself ledgered.

**Scheduler setup — three tiers, honestly stated:**
1. **CLI install = automatic:** the plugin drops `~/.claude/scheduled-tasks/<name>/SKILL.md` files directly. Here the install *is* the schedule.
2. **Cloud surfaces = conversational setup:** account-level schedules cannot be registered by a local install. The door ships `list_desired_schedules` (templates served as data); the user's first conversation — "set up my Team OS schedules" — has Claude read the desired set and create the tasks via the platform's own scheduling tools. One guided chat, not N manual steps. (Confirmed: tasks are MCP-manipulable from within runs via `update_scheduled_task`; whether ordinary sessions can *create* them is FK6c experiment #1.)
3. **Reconciliation loop:** one bootstrap task runs daily, compares desired-vs-actual schedules via the door, repairs drift. Self-healing on both tiers.

**Credential domains (three, never interchangeable — enforced in FK3b):**
| Domain | Who holds the grant | Reachable by | Inference requirement | Trust posture |
|---|---|---|---|---|
| Claude-account connectors | Anthropic (user's Claude account) | Claude sessions only | Subscription only | Reduced-trust fence (path b) |
| Team OS's own connectors (Plane A) | Team OS runtime | Team OS loops/daemon | **Own inference: API key or local model + always-on runtime** | Full (gated + ledgered) |
| The door's OAuth | User authorizes client→Team OS | Any MCP client | The client's own model | Semi-trusted (§7.7) |

Connecting Slack to Claude does **not** connect Slack to Team OS, and vice versa — different owners, different revocation surfaces.

**The Team OS plugin (one installable unit):** MCP connector (the door: read tools + `propose_*`, readOnlyHint set), gate/ledger hooks, schedule templates (`daily-digest`, `nightly-corpus-compile`, `weekly-gap-fill`, `morning-brief`), adapter config. Marketplace = GitHub repo + `marketplace.json`. Existence proof: Mem0's plugin. On CLI install the compile task fires once → Day One Brief. **Gate-3.5 signing/sandbox discipline applies to the Team OS plugin itself — concretely at fork scale: signing-lite = signed commits + reproducible plugin build + each collaborator reviews the hook code before install — made feasible on FIRST install, not just updates (X-1): a hook line-count budget (readable in ~15 minutes), a one-page hook behavior spec the code must match, and the reproducible build verifying spec↔artifact (CN-3; the builder ships code that runs with hook privilege on collaborator machines, so the diff review is the collaborator's control over their own TCB).**

**Self-tuning cadences (governed):** the discovery loop may *propose* new scheduled tasks as it learns rhythms (via the same scheduler tools). An agent writing its own schedules is unattended-action-expansion — proposals only, human-approved (§7.7/§16 leash).

**Caveats:** routines are research-preview (daily caps separate from usage limits); plugins execute arbitrary code with no Anthropic review; **ToS check before distributing the subscription-scheduled kit beyond the pilot**; verify plugin-manifest + scheduled-task schema + per-surface scheduling-tool availability against live docs at build (all move monthly).
