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
| 1 | Bash command has egress marker AND (sensitive path OR verbatim secret) | deny | bash-exfil |
| 2 | Bash command has egress marker | ask | bash-egress |
| 3 | Bash command touches sensitive read path (.ssh, .env, …) | ask | sensitive-read |
| 4 | Write/Edit targets protected path (hooks/, adapter/, CLAUDE.md, workflows, divergence log) | ask | protected-path |
| 5 | Write targets cloud-synced dir → treated as SEND; content scanned; secret found | deny | synced-path-send |
| 6 | Write targets cloud-synced dir, content clean | ask | synced-path-send |
| 7 | Send-class tool (WebFetch/WebSearch/name matches send markers) with verbatim secret in any param | deny | outbound-secret |
| 8 | Send-class tool, params clean (scan always runs — AT-6) | permit | send-scanned-clean |
| 9 | Any tool, secret pattern in any string param | ask | param-secret |
| 10 | Everything else | permit | default-permit |

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

**Env knobs:** `TEAMOS_POLICY` (policy file), `TEAMOS_LEDGER_DIR` (ledger dir),
`TEAMOS_POSTURE` (recorded posture). Defaults: repo policy, repo ledgers/,
"attended".

**Line budget:** gate.py ≤ 300 lines including comments (CI-enforced).
Registration: see hooks/settings-fragment.json. Failure mode: if the hook
crashes, the harness's own permission system still applies (fail-closed at the
harness layer); the crash leaves no L2 record — absence of a record for an
executed call is itself the tamper signal (L1↔L2 join, FK6 scoring).
