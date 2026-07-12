# Remediation Work Order — from 2026-07-11 adversarial review

- **Date:** 2026-07-11
- **Model:** Claude Fable 5 (`claude-fable-5`)
- **Source:** `review/2026-07-11-adversarial-14-counsel-review.md`, adjusted per `review/2026-07-11-meta-review-of-14-counsel-review.md` (source-verified; endorses this ordering).
- **For:** Claude Code, building the Team OS fork. Read this fully, then work top-down.

## Rules of engagement

- **Do not ingest real colleague data until P0 closes.** FR2 fails today. This is the stop-and-flag condition in CLAUDE.md.
- **Severity is conditional, not live.** These are a mid-build, fixtures-only repo with honest docs — the envelope, breaker, and safety agent are all inert and no real data exists, so the *live* severity of most P0 items today is low. Severity flips to CRITICAL **at the moment real colleague data is ingested**. That is why P0 gates ingestion. Treat the CRITICAL labels as pre-emptive (fix-before-data), not as evidence of a live breach. Do not read "theater" into unfinished enforcement — the invariants are unbuilt, not deceptive.
- **Protected paths need human approval** — `hooks/`, `adapter/`, `config/envelope-policy.json`, CLAUDE.md. Tasks touching them are marked 🔒. Propose the diff; do not auto-merge. Open a PR.
- **Test alongside code.** No task is done until its named test is written and `make test` is green. Add the crash/concurrency tests that are missing — the current suite covers happy + adversarial-input paths, never crash/concurrent paths.
- **Log divergences** append-only via PR.
- One task per commit. Branch off `main`.

---

## P0 — blocking. Close before any real data or the next thesis clock.

### T0. Restore the pre-registered A-P3 / A-A4 interval rules
- **Why:** highest priority. Terminal gate success criterion was silently weakened. `validation-plan.md:58` says "pooled **interval excluding zero**"; code does bare `pooled > 0`. This corrupts the measurement the project exists to produce.
- **Files:** `scripts/transfer.py:73-81` (`passes_preregistered_rule`), `scripts/measurement.py` (A-A4 correlation path).
- **Do:** compute a pooled interval (bootstrap or t-interval over usable receiver deltas). Pass rule = `positive in ≥2 receivers AND interval_lower > 0`. Same for A-A4: report the correlation interval, don't just point-estimate. Fix the docstring back to the plan's wording.
- **Proof:** test that a set of small-positive deltas whose interval spans zero returns `inconclusive`, not `pass`.
- **Invariant:** pre-registration is fixed before data. Restore it.

### T1. Gate fail-closed 🔒
- **Why:** `gate.py:197-199` `main()` has no try/except. Any crash (malformed stdin, policy typo, missing pyyaml, unwritable ledger dir) → exit 1 → Claude Code treats non-2 as non-blocking → tool runs ungated AND unledgered.
- **File:** `hooks/gate.py`.
- **Do:** wrap `process()` in try/except in `main()`. On any exception: emit `permissionDecision: "deny"` (or `sys.exit(2)`) AND append a `gate-error` L2 record. Never let a gate crash become a permit.
- **Proof:** `tests/test_gate.py` — feed garbage stdin and a broken policy; assert decision is `deny`, not proceed; assert an error record was written.
- **Invariant:** every tool call is gated and ledgered — including on gate failure.

### T2. FR2: build the missing compensating control (taint), then harden egress 🔒
- **Why:** FR2 fails, but be precise about *why*, because it changes the fix. The outbound regex scan matching only credentials is the **documented design** (`policy.yaml:60` — "catches VERBATIM secrets only; paraphrase-exfil is carried by taint + send gate"), not a discovered flaw. The finding is: **the compensating layer (taint-tracking) isn't built**, so corpus/paraphrase exfil has nothing catching it. So the real fix is "build taint," not "add more regexes." Two layers, both needed:
  - **Layer A — taint (the actual gap, do this first).** Untrusted content (corpus, inbox, A2A, historical) must not be able to add a recipient, add a step, or trigger a send without confirmation. Session-granular taint is **in scope** (CLAUDE.md: datum-granular deferred, session-granular fine at n≤3). Track whether the current action's plan structure was influenced by untrusted content; if a send's recipient/target derives from tainted input, require confirmation. This is what stops `WebFetch(url=?d=<corpus>)` — the URL is attacker-chosen plan structure, not a value.
  - **Layer B — egress hardening (defense-in-depth, still required).** Classification: default unknown / non-read tools to **send-class** (scan + ask); explicit read-only allowlist, everything else egress-capable. Scan send params including **decoded base64**. Bash: prefer an allowlist of known-safe commands over the denylist; if the denylist stays as interim, add the missing markers (`ssh`, `git push`, `rsync`, `dig`, `nslookup`, `open`, `osascript`, `/dev/udp`), handle quoting/obfuscation, and **say in BEHAVIOR.md that substring-denylist is not defensible**. Synced paths: add `Library/CloudStorage`, `Box`, match modern `GoogleDrive-<email>` (no space); scan Bash commands (not only `file_path`) against synced roots.
- **Files:** `hooks/gate.py:74-148`, `hooks/policy.yaml`, new taint module + `hooks/BEHAVIOR.md`.
- **Proof:** taint test — a send whose recipient/url derives from tainted corpus content requires confirmation (not `permit`). Egress test — extend `fixtures/exfil-probes.json` with payloads **written the way an attacker writes them (quoted, base64, ssh, git push)**, not shaped to match the pattern; assert `deny`/`ask`. Delete or rewrite the rigged `python-socket-variant` probe.
- **Invariant:** untrusted content supplies values, never plan structure; no permitted tool is an exfil path. The scan is one layer; taint is the layer that was missing.

### T3. Resolve paths; protect the dials and the hook config 🔒
- **Why:** protected-path check is string-only (`gate.py:124`) → symlink `drafts/x.py → hooks/gate.py` overwrites the gate. Breaker/envelope **state** files and `~/.claude/settings.json` are unprotected → agent disarms breaker, widens its own envelope, or disables the hook at the source.
- **Files:** `hooks/gate.py`, `hooks/policy.yaml`.
- **Do:** `Path(...).resolve()` before the protected-path comparison (match `gate_processor._safe_target`). Add to `protected_paths`: breaker-state file, envelope-state file, and `~/.claude/settings.json` (absolute + repo-relative). Wire the breaker into the gate **unconditionally** — stop gating the breaker check on the `TEAMOS_BREAKER` env var being set; corrupt/missing breaker file must fail **closed** (treat as open/deny), not open.
- **Proof:** test that a Write through a symlink to a protected file is `ask`/`deny`; test that writing the breaker state or settings.json is `ask`/`deny`; test that a corrupt breaker file denies side-effectful actions.
- **Invariant:** the envelope script can never touch its own ceiling — extend to the dial and the stop, not just the ceiling.

### T4. Make deletion touch content
- **Why:** `deletion.py` appends L9 events but removes no content. Only the L8 diff is unlinked. Corpus files survive a `purge_completed`. `l3.jsonl` is git-committed with evidence locators and cannot be deleted from the chain. `dm_email` opt-in is never enforced.
- **Files:** `scripts/deletion.py`, `scripts/connectors.py`, `.gitignore` / ledger storage design.
- **Do:**
  - Generalize the L8 crypto-shred pattern to L3 and corpus: content lives encrypted / in a redactable side-store keyed by node id; erasure crypto-shreds the key or unlinks the content file, leaving the chain intact (chain hashes references, never content — extend the L8 design to L3).
  - Stop committing `ledgers/l3.jsonl` to git, OR design an explicit chain-redaction story. Remove it from tracking; `.gitignore` the ledger content.
  - Enforce `dm_email` at `connectors.eligibility()` — a source with `dm_email: false` must not ingest DM-class items; tag item source so `ingest()` can tell DM from channel.
- **Proof:** `tests/test_deletion.py` — assert the **content is absent** after erasure (grep the store, not just the ledger). `tests/test_connectors.py` — assert a DM item is refused when `dm_email` is false.
- **Invariant:** deletion works before others' data is ingested (FK3 precedes FK4); DMs/email are opt-in.

### T5. Serialize ledger appends
- **Why:** `hashchain.append` (`hashchain.py:62,71`) is read-last-hash → write with no lock. Parallel subagents (design-encouraged) fork the chain; `verify()` raises forever; tamper-evidence collapses under normal concurrency.
- **File:** `scripts/hashchain.py`.
- **Do:** `fcntl.flock(LOCK_EX)` on the ledger file spanning read-last-hash + write. One fix, since all writers share this module. While there, read the tail via `seek()` instead of full-file scan (O(n) per append on the hot path).
- **Proof:** new `tests/test_ledgers.py` case — spawn ≥4 processes appending to one ledger; assert `verify()` passes and record count is exact.
- **Invariant:** one chain implementation, tamper-evident under concurrency.

---

## P1 — integrity of the thesis instruments. Before the FK6 clock.

### T6. Decouple the acceptance signal; kill the engagement penalty
- **Why:** ✓ + edit≤0.2 does four jobs (floor, envelope widen, A-A4 proxy, A-P3 metric). It punishes real editing twice (fails the floor + narrows envelope → more interrupts) and rewards rubber-stamping. Missing edit distance counts as accepted.
- **Files:** `scripts/measurement.py` (`weekly_accepted`), `scripts/envelope.py`, `docs/schemas/ledger-l8-human-signal.schema.json`.
- **Do:**
  - Add an `unprompted` provenance field to the L8 schema; the initiative floor counts only `unprompted=true` records. Prompted work (user asked Tuesday) must not inflate the floor.
  - Remove narrowing-as-punishment-for-rejection, or make the floor independent of the envelope so honest ✗ doesn't cost the human more interrupts.
  - Treat **missing** edit distance as **not accepted** (fail safe), not accepted.
  - Add a dedupe / triviality filter so a recurring digest counts once and padding is excluded — implement the prose clause.
- **Proof:** tests — prompted records don't count toward the floor; a rejection doesn't reduce the floor count; missing-distance record is excluded; duplicate digests count once.
- **Invariant:** initiative floor measures unprompted accepted work, not compliance.

### T7. Authenticate the L8 endorsement path
- **Why:** CN-1 is nominal. `capture_edit(attribution="principal_authenticated")` is a default param (fails unsafe). The real forge is appending an `signal_type="endorsement"` L8 line directly — envelope widens on it, no crypto. (Note: `capture_edit` writes `"edit"`, which nothing consumes — local accepts are dead signal; fix that too.)
- **Files:** `scripts/l8_capture.py`, `scripts/envelope.py`, `scripts/day_one_brief.py`.
- **Do:** default `attribution="unattributed"`; require a verified principal identity to stamp `principal_authenticated`. The envelope and floor must only trust cryptographically-attributed endorsements. Reconcile `signal_type`: either `capture_edit` emits the consumed type or the consumers read `"edit"` — decide and wire it so local accepts are not silently dead.
- **Proof:** test — a forged endorsement record with no verified identity does not widen the envelope and does not count toward the floor.
- **Invariant:** acceptance signals are principal-authenticated; the envelope never widens on unattributed signals.

### T8. Replace the L7 quality metric
- **Why:** `measurement.py:33` score = fraction of `["#","cadence","source"]` present. Three magic strings → 1.0 → clears the promotion floor → distributed to colleagues.
- **File:** `scripts/measurement.py`.
- **Do:** replace with a real deterministic proxy (or mark it explicitly non-load-bearing and block promotion on it until a real metric exists). If kept as scaffolding, `log()` that promotion cannot rely on it.
- **Proof:** test — a stub deliverable containing the three markers does not score 1.0 / does not clear promotion.
- **Invariant:** production-as-eval — the eval must not be gameable by string presence.

### T9. Wire and window the safety agent; add human approval to the door
- **Why:** `safety_agent.check()` is never invoked; counters are lifetime, not windowed → once tripped, human reset re-trips forever (stuck-open deadlock); third-party ✗ reactions can trip a permanent halt. `process_inbox` auto-commits proposals with no approval step, despite the door docstring claiming one — untrusted content adds a scheduled step / loadable skill (taint violation).
- **Files:** `scripts/safety_agent.py`, `scripts/spawn.py`, `scripts/gate_processor.py`, `scripts/door.py`.
- **Do:** invoke `safety_agent.check()` on the runtime path (loop pre-flight). Filter counters by a sliding `ts` window. Attribute rejections (CN-1) so a stranger's ✗ can't halt. Add a real human-approval step before `process_inbox` commits schedules/skills; untrusted-sourced proposals require confirmation. Enforce spawn depth/rate at `spawn.record` (refuse depth>N), not self-report.
- **Proof:** tests — windowed counter recovers after reset; unattributed ✗ does not halt; a `propose_schedule`/`propose_skill` from an untrusted source is not auto-committed.
- **Invariant:** untrusted content supplies values, never plan structure; the kill switch recovers.

---

## P2 — process, scope, surfaces.

### T10. Freeze UI; start the clocks
- **Why:** last full day went to five HTML surfaces + launch site while all three thesis gates and both measurement clocks sit unstarted; collaborators (the stated long pole) at zero hours. "Initiative before interface" inverted.
- **Do:** stop new UI work. Today: send collaborator recruitment asks; run FK4 on the real footprint; declare unattended posture in L2; start the 14-day streak. Begin filling `ledgers/fr8-fork-overhead.md` (currently one empty row).
- **Proof:** a real (non-fixture) L3/L7/L8 record from the builder's own footprint; a named collaborator + signed FK4-pre notice.

### T11. Reconcile scope + divergence log
- **Why:** operator console (do-not-build list) shipped by name; subagent/spawn/safety machinery + Insights/console landed with no divergence entries, straight to `main`, including edits to protected `hooks/gate.py`.
- **Do:** for each Jul-11 out-of-scope addition, either append a divergence-log entry (PR) justifying it, or revert. Rename/reframe the "operator console" or move it behind the FK gate.

### T12. Real, reachable controls + fix the individuation audit
- **Why:** console buttons are inert `<span>`s; no reachable kill switch / reset / undo; fleet dashboard is a de-facto leaderboard; `audit_no_individuation` never runs against `render_dashboard.py`; cross-page facts contradict (API-key, test counts, gate size).
- **Files:** `docs/*.html`, `scripts/render_dashboard.py`, `scripts/dashboard.py`, `docs/INSTALL.md`.
- **Do:** make stop/reset/undo real and reachable, or remove the claim. Run the individuation audit against `render_dashboard.py` in CI. Reconcile the contradicting facts to one source of truth. Remove fabricated ✓/✗ reactions from the renderer or label the surface as demo.
- **Proof:** CI runs `audit_no_individuation` on the actual UI generator; a single canonical stats source; a doc-lint that fails on divergent test-count / API-key claims.

### T13. Housekeeping (from SWE review)
- `chmod 0600` on per-principal keys (`crypto_store.py:51-53`).
- Atomic writes (tmp+fsync+rename) for breaker/envelope/deletion/`run_if_due` state — corrupt breaker file must fail closed.
- Record **outcomes** not just decisions in L2 (send-receipt ledger) so permitted-but-failed / double-send is visible.
- Off-box anchor push (`anchor.py`) — currently anchors in-repo; SE-6 tamper-evidence has no external witness.
- Fix double-send: write `last_run`/checkpoint **before** the side effect is observable, or make the send idempotent; add the crash-after-effect test (`test_loop.py` only tests crash-before-effect).
- JWT regex (`policy.yaml:67`) false-positive-denies any base64 JSON — tighten.
- Delete or wire orphaned scripts (`l3_writer.py` prod-uncalled, `insights.py`, `l6_from_git.py`, `field_inventory.py`); split the 784-line HTML blob out of `render_dashboard.py`.

---

## Done criteria for the work order

- P0 fully closed and green in CI before any real colleague data.
- Each closed task: code + named test + `make test` green + divergence entry if it touched a protected path or deviated from the spec.
- FR2 re-tested with attacker-shaped probes (not fixtures shaped to the matcher) and passing — with the taint layer (T2 Layer A) built, not just egress regexes widened.
- **Evidence in-artifact:** when a task asserts an exfil verdict empirically, capture the actual gate stdout in the test/fixture, not just a pass/fail — an empirical claim carries its transcript.
- `review/2026-07-11-adversarial-14-counsel-review.md` findings each map to a closed task or a logged, justified deferral.
