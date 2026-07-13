**`v0.1 — 2026-07-10`** *(X-1: one-page hook behavior spec — the code must match this page; reproducible review = diff gate.py against this spec)*

# Gate behavior spec (hooks/gate.py)

**What it is:** the PreToolUse hook. Every tool call the harness proposes passes
through it. It inspects the PAYLOAD (never just the tool name), returns
allow/deny/ask, and appends one hash-chained L2 record per call to
`ledgers/l2.jsonl`. No network. No language model. Reads only: stdin,
`hooks/policy.yaml`, the ledger file it appends to.

**Decision table (in order; first match wins):**

| # | Condition | Verdict | Rule id |
|---|---|---|---|
| 0 | Circuit breaker OPEN (`TEAMOS_BREAKER`) and action is side-effectful (write/edit/send/execute/schedule) | deny | circuit-open |
| 1 | Bash command has egress marker AND (sensitive path OR verbatim secret) | deny | bash-exfil |
| 2 | Bash command has egress marker | ask | bash-egress |
| 3 | Bash command touches sensitive read path (.ssh, .env, …) | ask | sensitive-read |
| 4 | Bash command touches a cloud-synced root → treated as SEND; secret found / clean | deny / ask | bash-synced-path |
| 5 | Write/Edit targets protected path (hooks/, adapter/, CLAUDE.md, workflows, divergence log) | ask | protected-path |
| 6 | Write targets cloud-synced dir → treated as SEND; content scanned; secret found | deny | synced-path-send |
| 7 | Write targets cloud-synced dir, content clean | ask | synced-path-send |
| 8 | Send-class tool (WebFetch/WebSearch/name matches send markers) with verbatim secret in any param (incl. one base64 layer decoded) | deny | outbound-secret |
| 9 | UNKNOWN tool (not in action_classes, no send marker) — defaults to send-class, params clean | ask | unknown-tool-send |
| 10 | Send-class tool, params clean, session TAINTED (has read corpus/inbox/external content) | ask | taint-confirm |
| 11 | Schedule-class action, session TAINTED | ask | taint-confirm |
| 12 | Send-class tool, params clean, session untainted (scan always runs — AT-6) | permit | send-scanned-clean |
| 13 | Any tool, secret pattern in any string param | ask | param-secret |
| 14 | Everything else | permit | default-permit |

**Taint (FR2 Layer A, session-granular — fork §7.7):** reading any
`taint_source_paths` root (stores/corpus, stores/skills, inbox/) or calling a
`taint_source_tools` tool (WebFetch, WebSearch) marks the session tainted
(state: `<ledger_dir>/taint/<session_id>.json`). From then on, every send or
schedule in that session escalates to the human. This is the layer that carries
paraphrase-exfil and attacker-chosen recipients; the verbatim scan never could.
Corrupt taint state reads as TAINTED (fail closed).

**Egress denylist is NOT defensible on its own:** the bash marker list is
substring matching over a normalized command (quotes/escapes stripped,
whitespace collapsed, casefolded). It defeats casual obfuscation (`cu"r"l`,
`CURL`), not a motivated attacker (aliases, ${!var}, self-decoding payloads,
binaries not on the list). It is defense-in-depth ONLY; the load-bearing
controls are taint-confirm on sends plus the harness permission prompt.

**Always-on:** the tool-parameter scan and (on sends) the outbound-content scan
run on every call regardless of posture. Posture (`TEAMOS_POSTURE` env,
declared before unattended runs — R-13) is recorded in the L2 record; it never
disables inspection.

**Outcome field is distinct from verdict** (S1): permit→gate_passed,
deny→gate_blocked, ask→escalated_to_human. A missed probe becomes a
posture-narrowing only by explicit logged decision, never silently.

**Honesty limits (X-2):** the content scan catches VERBATIM secrets/identifiers
(AWS keys, private-key headers, GitHub/Anthropic/Slack tokens, JWTs).
Paraphrase-exfiltration through a sanctioned send is invisible to any pattern
pass by construction; that risk is carried by the taint rule and the send gate,
not by this scan.

**Autonomy — two zones (WO-1/3/4, severity × reversibility).** After inspection,
a clean action passes through one post-gate (scripts/boundary.py); it only ever
ADDS friction, never turns a safety ask/deny into a permit:
- **Reversible interior** (drafts, corpus writes, local edits, local exec — git +
  lineage is the rewind): the **earned-autonomy envelope** (WO-1). A clean
  side-effectful action auto-permits only once the principal has earned the level
  in that category (envelope-state.json, a protected path the gate READS, never
  writes); below the floor it ASKS (the labeling period, §7.4). Enforced when
  `TEAMOS_ENVELOPE_STATE` points at the maintained state; unset ⇒ no envelope gating.
- **Irreversible boundary** (external send/mutation/disclosure/destruction/spend —
  can't be taken back): **deny-by-default**. Auto-permits ONLY on a match in the
  user-owned `config/allow-policy.md` (a protected path; ships with ONE rule —
  the agent's delivery to its own principal, so briefs/digests arrive done;
  everything else deny-by-default), otherwise ASKS. Reversibility is labeled in every L2
  record (`reversibility:{reversible|irreversible}` in checks_run).
- **The one falsifiable guarantee:** no irreversible action is auto-permitted
  without an allow-match or a hand, and every one is recorded before it acts. A
  deployment where one slips through is a falsifying bug.

**Env knobs:** `TEAMOS_POLICY` (policy file), `TEAMOS_LEDGER_DIR` (ledger dir),
`TEAMOS_POSTURE` (recorded posture), `TEAMOS_ENVELOPE_STATE` (earned-autonomy
state), `TEAMOS_ALLOW_POLICY` (irreversible allow policy). Defaults: repo policy,
repo ledgers/, "attended", envelope unconfigured, config/allow-policy.md.

**Line budget:** gate.py ≤ 300 lines including comments (CI-enforced; taint
helpers live in hooks/taint.py, same protected dir).
Registration: see hooks/settings-fragment.json. Failure mode: the gate FAILS
CLOSED — any crash (malformed stdin, broken policy, unwritable ledger) emits
`permissionDecision: deny` + exit 2 and appends a best-effort `gate-error` L2
record. A gate failure never becomes a permit.
