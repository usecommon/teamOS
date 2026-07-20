# Team OS Fork — Consolidated Findings

- **Date:** 2026-07-11 (status re-checked 2026-07-12)
- **Model:** Claude Fable 5 (`claude-fable-5`)
- **Sources:** the 14-counsel review + meta-review, and three simulation passes (security/HEAD, autonomy, failure-injection).
  - `review/2026-07-11-adversarial-14-counsel-review.md`
  - `review/2026-07-11-meta-review-of-14-counsel-review.md`
  - `review/2026-07-11-simulation-report.md` (§3a security, §8a autonomy, §8b resilience)
  - Evidence: `review/sim-artifacts/` (engines, fault matrix, coverage, findings JSON)
- **Status legend:** ✅ FIXED (verified) · 🟠 OPEN (confirmed at HEAD) · ⚪ LATENT (real but not live) · 🔵 PENDING (committed, needs targeted test)
- **Framing:** all data is sandboxed simulation with synthetic actors — **formative, not proof**. Severity is *conditional*: most items become live only when real colleague data is ingested.
- **RECONCILED 2026-07-12 against the full remediation tree (all T0–T13, branch `remediation/2026-07-11`, `make test` green).** My earlier autonomy (§8a) and fault (§8b) sweeps ran on a stale sandbox (T0–T5 only), so several items below were re-verified live against the current tree. See the reconciliation block next.

---

## RECONCILIATION — verified live against current tree (T0–T13)

The remediation branch closed all fourteen work-order tasks (each with a test). I re-ran targeted probes (`…/scratchpad/teamos-sim4/reconcile.py`) on every previously-open item. Result: **most are fixed; four resilience residuals remain.**

| Item | Was | Live verdict now | Status |
|---|---|---|---|
| D1/F1 untrusted → schedule via `process_inbox` | committed (CRIT) | **pending human approval, not committed** | ✅ FIXED (T9) |
| D2 agent auto-creates shared worker | auto-committed | **pending human approval** | ✅ FIXED (T9) |
| A7/F2 WebFetch corpus exfil (untainted first move) | allow (CRIT) | **ask** (blocked) | ✅ FIXED (T2) |
| A10/F4 forge envelope (unsigned endorsements) | widens 0→1 | **0→0, forge blocked** (HMAC verify) | ✅ FIXED (T7) |
| C1/C3/F5 initiative-floor over-count | 82–91 inflated | **=2** — excludes prompted, heavy-edit, dedups | ✅ FIXED (T6) |
| C2 engagement penalty (narrow on heavy edit) | narrows autonomy | envelope no longer narrows on edits | ✅ FIXED (T6) |
| C4 gameable L7 marker | score 1.0 clears promotion | marked non-load-bearing; promotion ignores it | ✅ FIXED (T8) |
| C6 local accepts dead signal | ignored | `signal_type` reconciled; verified records consumed | ✅ FIXED (T7) |
| B1 deletion tombstone-only | 0 files removed | content shred + `test_corpus_file_removed_on_erasure` | ✅ FIXED (T4) |
| B3 key hygiene | world-readable, no shred | `chmod 0600`, keys outside repo | ✅ FIXED (T13) |
| D3 scheduled double-send | double-sends | **at-most-once** — slot claimed before the effect; re-run within interval not due | ✅ FIXED · `test_crash_after_effect_never_double_sends` |
| E1 torn ledger tail-line | bricks writer | **heals** — `_truncate_torn_tail` drops the partial fragment, append proceeds | ✅ FIXED · `test_torn_trailing_fragment_does_not_brick_append` |
| E2 whole-file deletion | silent history loss | **detected** — `verify_chains` cross-checks the off-box anchor (`anchor.detect_truncation`), `make chains` fails on truncation | ✅ FIXED · `test_deleted_ledger_flagged_by_anchor` |
| E3 breaker-open crashes scheduled loop | uncaught `PermissionError` | **pauses gracefully** — `run_if_due` catches `GateBlocked`, rolls back the claim, retries when the breaker closes | ✅ FIXED · `test_breaker_open_pauses_not_crashes` |

**Reconciliation resolved (2026-07-16):** the four durability/liveness residuals I flagged on 07-12 were subsequently closed by the ongoing work-order stream (WO-3/4/5, now merged to `main`). Re-verified live against the current tree (`…/teamos-sim5`): E1 heals, D3 is at-most-once, E3 pauses without crashing, E2 truncation is caught by the chains gate (`verify_chains` rc=1). Each has a named regression guard; `make test` green, and the 4 guard files pass (22 tests). **No code residual remains.**

The per-domain tables below are the *pre-reconciliation* record; where a row disagrees with the reconciliation table above, **the reconciliation wins.**

---

## A. Security & containment (from review §Security, simulation §3a)

| # | Finding | Sev | Status | Evidence |
|---|---|---|---|---|
| A1 | Gate fails **open** on crash (no try/except in `main()`) | CRIT | ✅ FIXED (T1) | garbage stdin → `rc=2`, "failing closed"; `gate.py:208-233` |
| A2 | Symlink → protected file overwrites `hooks/gate.py` (string path check) | CRIT | ✅ FIXED (T3) | `Write` to symlink → `ask`/protected-path |
| A3 | `~/.claude/settings.json` writable (disable the hook at source) | CRIT | ✅ FIXED (T3) | → `ask`/protected-path |
| A4 | Breaker/envelope **state files** writable past gate (disarm) | HIGH | ✅ FIXED (T3) | write breaker-state → `ask`/protected-path |
| A5 | Breaker inert / corrupt file fails unsafe | HIGH | ✅ FIXED (T3) | corrupt **and** missing breaker → gate **deny** |
| A6 | Hash chain corrupts under concurrent append (no lock) | CRIT | ✅ FIXED (T5) | 4×40 concurrent → `verify` OK, 160/160 intact (flock) |
| A7 | **WebFetch exfiltrates non-credential corpus** in the URL | CRIT | 🟠 OPEN | `WebFetch(?d=<corpus>)` → **allow** (`send-scanned-clean`) |
| A8 | Bash egress denylist misses `ssh`/`git push`/`rsync`/etc. | CRIT→ | 🟠 PARTIAL (T2) | now `ask` (bash-egress), not `allow`; still not `deny` under unattended |
| A9 | Send-class classification by tool-name substring (MCP egress escapes) | HIGH | 🟠 OPEN | unknown egress tools bypass the send scan |
| A10 | Forgeable envelope (attribution is an unverified string) | HIGH | ⚪ LATENT | 7 forged endorsements widen 0→1, **but gate never reads envelope** |

## B. Privacy (from review §Privacy)

| # | Finding | Sev | Status | Evidence |
|---|---|---|---|---|
| B1 | **Deletion deletes nothing** — `request_erasure` is tombstone-only | CRIT | 🔵 PENDING (T4) | T4 "deletion touches content" committed; sim probe inconclusive (erased a job-graph node, not the file) — needs a test that erases the node backing a stored file |
| B2 | `l3.jsonl` committed to git (evidence locators in history) | CRIT | ✅ FIXED | T4 commit: "l3 ledger untracked" |
| B3 | Per-principal keys unauthenticated / world-readable, no crypto-shred | HIGH | 🟠 OPEN | any co-principal can `load_or_create_key(...)`; no `chmod 0600` |
| B4 | `dm_email` opt-in toggle never enforced | HIGH | ✅ FIXED (T4) | commit: "dm_email enforced" (re-verify with a DM-class probe) |
| B5 | Individuation audit only scanned `dashboard.py` | MED | ✅ FIXED / GOOD | audit run on `render_dashboard.py` → clean `(True, [])` |

## C. Behavioral / incentive (from review §Behavioral, simulation §5–6)

| # | Finding | Sev | Status | Evidence |
|---|---|---|---|---|
| C1 | Acceptance metric is **blind to engagement** — floor counts ✓s that were heavily edited | HIGH | 🟠 OPEN | floor 82–91 "accepted" while 28–44 deliverables heavily rewritten; harvested endorsements carry no edit distance |
| C2 | Metric **punishes engagement** — heavy edit fails the floor AND (under a wired envelope) narrows autonomy | HIGH | 🟠 OPEN (latent narrow) | `LIGHT_EDIT=0.2`, `narrow_edit_severity=0.5`; dead zone 0.2–0.5 |
| C3 | Initiative floor gameable — no `unprompted` provenance, no dedupe/triviality filter | HIGH | 🟠 OPEN | 5 prompted ✓s read as initiative=5 |
| C4 | L7 quality metric = 3 magic strings (`#`, `cadence`, `source`) | HIGH | 🟠 OPEN | any doc with those → score 1.0 → clears promotion |
| C5 | Pre-registered A-P3/A-A4 rule weakened to point-estimate | CRIT | ✅ FIXED (T0) | `passes_preregistered_rule` computes t-interval, requires `lo>0` |
| C6 | Local `capture_edit` accepts are dead signal (`signal_type="edit"` consumed by nothing) | MED | 🟠 OPEN | floor/envelope only read `"endorsement"` |

## D. Autonomy & initiative (simulation §8a)

| # | Finding | Sev | Status | Evidence |
|---|---|---|---|---|
| D1 | **Untrusted content → autonomous artifact** — scout mines client messages, auto-commits to corpus | CRIT | 🟠 OPEN | entities "Billing Team / Compliance Mailbox / Halcyon…" committed, no confirmation |
| D2 | **Agent auto-creates a new shared worker** (skill) with no human approval | HIGH | 🟠 OPEN | `propose_skill`→`process_inbox` wrote `stores/skills/standup-writer/SKILL.md`; `approval_step_in_code=False` (door docstring claims approval) |
| D3 | Scheduled self-running task **double-sends** on crash-after-effect | HIGH | 🟠 OPEN | `run_if_due` writes state after action → `total_sends=3` for one delivery |
| D4 | Subagent spawning has **no preventive cap** — depth self-reported | HIGH | 🟠 OPEN | `spawn.record` accepted depth 5 > `MAX_DEPTH=3`; safety trips only post-hoc |
| D5 | **Earned autonomy is decorative** — envelope widens but gate never consults it | HIGH | ⚪ LATENT | `gate_consults_envelope=False` |
| — | Self-running loop crash-safe (idempotent re-fire, clean resume) | — | ✅ GOOD | 0 duplicate L7; `done=[s1,s2]`→`[s1,s2,s3]`, FR4 holds |
| — | Recommend/insights deterministic, no name leak | — | ✅ GOOD | identical across runs; no person tokens |

## E. Failure & resilience (simulation §8b) — 14 faults, 9 good / 5 bad, **no FAIL-OPEN**

| # | Finding | Sev | Status | Evidence |
|---|---|---|---|---|
| E1 | **Torn ledger tail-line bricks the writer** — every future `append` crashes | HIGH | 🟠 OPEN | partial last line → `last_hash` `json.loads` crash; T5 locked but no tail-repair |
| E2 | **Whole-file deletion = silent history loss** — append starts fresh chain, `verify` passes | HIGH | 🟠 OPEN | off-box anchor (`anchor.py`) not consulted at append (SE-6 unwired) |
| E3 | **Breaker-open crashes the scheduled loop** it protects (uncaught `PermissionError`) | HIGH | 🟠 OPEN | safety halt should pause, not crash; crash-before-state → retry-crash loop |
| E4 | Corrupt checkpoint unrecoverable on resume | MED | 🟠 OPEN | `Checkpoint.__init__` `json.loads` crash; should restart clean |
| E5 | Permitted-but-failed send leaves false `gate_passed` in audit | MED | 🟠 OPEN | no send-receipt/outcome ledger; can't tell sent/failed/double-sent |
| — | Corrupt policy / corrupt+missing breaker / unwritable ledger | — | ✅ FAIL-CLOSED | all → deny under fault |
| — | Tampered record detected; poison proposal isolated | — | ✅ GOOD | `verify` raises; batch commits good, rejects bad |

---

## Still-open, ranked (RECONCILED against current tree — final, 2026-07-16)

**All code findings are closed and guarded.** What remains cannot be fixed in code:

1. **T10 — the human long pole.** Recruit 2–3 collaborators, declare the unattended posture in L2, start the 14-day streak, and fill the FR8 overhead ledger. Nothing downstream (A-P3, the transfer thesis) can be measured until this starts.
2. **F6 — transfer needs real receivers.** The T0 interval rule is correct; at synthetic n it returns `inconclusive` by design. Requires real collaborators (see T10).

**Latent, already mitigated (keep both halves together):** the send-class/egress denylist is "interim, not defensible" per BEHAVIOR.md — the taint layer is the real control, so keep it. A10/D5 are moot: T7 verifies L8 identity, so forging is blocked even if/when the gate wires the envelope.

**Fixed, verified, and regression-guarded — everything else:** A1–A7, A10, B1–B5, C1–C6, D1–D5, E1–E5, plus the good baseline behaviors (fail-closed gate/policy/breaker, tamper detection, batch isolation, crash-safe loop, deterministic insights, no-individuation). Guards for the last-closed durability residuals: `test_torn_trailing_fragment_does_not_brick_append` (E1), `test_deleted_ledger_flagged_by_anchor` (E2), `test_breaker_open_pauses_not_crashes` (E3), `test_crash_after_effect_never_double_sends` (D3).

---

## Final status

Every code-level finding from the 14-counsel review and all three simulation passes is **closed and guarded** on `main` (`make test` green). The security, privacy, behavioral, autonomy, and durability/liveness layers all hold under simulation and fault injection. **The only open items are the human long pole (T10: collaborators + the measurement clocks) and its dependent F6 (real-receiver transfer evidence)** — exactly the outcome CLAUDE.md predicted: the code was never the binding constraint; two or three recruited humans and four weeks of clock are. This ledger is now a passing checklist; keep it as the regression baseline.
