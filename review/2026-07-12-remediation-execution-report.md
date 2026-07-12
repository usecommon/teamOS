# Remediation Execution Report — residual durability/liveness

- **Date:** 2026-07-12
- **Model:** Claude Fable 5 (`claude-fable-5`)
- **Input:** `2026-07-12-remediations.md` + `2026-07-12-remediation-prompts.md`
- **Branch:** `remediation/2026-07-11`. One commit per task. `make test` green after each.
- **Scope:** the 5 residual durability/liveness items (E1, E2, E3, E4, D3). All in `scripts/` — **no protected paths touched.** A7 (protected `hooks/`) was flagged, not executed.

---

## 1. Summary

All five residuals implemented, tested, committed. Test count **210 → 210+** (added `test_hashchain.py`, `test_checkpoint.py`, `test_anchor_truncation.py`, and E3/D3 cases in `test_brief.py`); full suite green. Live re-verification via `sim-artifacts/reconcile.py` confirms the behavior flips.

| Item | Was | Now (verified) | Commit |
|---|---|---|---|
| **E1** torn tail-line bricks writer | `CRASH JSONDecodeError` | `GRACEFUL (append heals torn tail)` | `52ade3f` |
| **E3** breaker-open crashes loop | `CRASH PermissionError` | `GRACEFUL (loop pauses, no crash)` | `47b7762` |
| **D3** scheduled double-send | `sends=3` | `sends=1 (at-most-once)` | `47b7762` |
| **E4** corrupt checkpoint crash | crash on resume | `restarts clean; .corrupt preserved` | `e6dcbac` |
| **E2** silent ledger deletion | `verify passes` | **detected** by anchor at verify (see §3) | `3937971` |

## 2. What changed, per item

**E1 — `scripts/hashchain.py`.** A crash mid-`append` left a partial final line; `last_hash()` then crashed in `json.loads` on every future append (permanent brick). Now `append()` truncates a torn (non-newline-terminated) trailing fragment before writing, and `last_hash()` walks past unparseable trailing lines to the last valid record. `verify()` is unchanged — interior tampering/gaps still raise. Test: `tests/test_hashchain.py` (torn tail heals; no-newline fragment dropped; interior tamper still caught).

**E3 — `scripts/day_one_brief.py`.** Added `class GateBlocked(PermissionError)`. `deliver()` raises it on gate-deny (breaker open); it's a `PermissionError` subclass so existing `except PermissionError` and the poisoned-send test still pass. `run_if_due()` catches `GateBlocked`, rolls back the slot claim (so `last_run` is not advanced), and returns `(False, catch_up, None)` without raising — a graceful pause that retries when the breaker closes. A genuine post-permit send failure stays a plain `PermissionError`. Test: `test_brief.BreakerPause`.

**D3 — `scripts/day_one_brief.py`.** `run_if_due` already claimed the slot before the effect, but `deliver()` wasn't idempotent — an out-of-band crash-after-effect rerun re-posted. `deliver()` now scans L2 for a succeeded `send-receipt` with the same payload digest and returns the prior `ts` without re-posting. At-most-once per unique payload at the send path. Test: `test_brief.IdempotentSend`.

**E4 — `scripts/checkpoint.py`.** `Checkpoint.__init__` did a bare `json.loads`; a torn checkpoint crashed every resume. Now a corrupt or wrong-shape checkpoint is moved to `<name>.corrupt` (preserved for audit) and state restarts clean. Test: `tests/test_checkpoint.py`.

**E2 — `scripts/anchor.py` + `scripts/verify_chains.py`.** Deleting a whole ledger and re-appending starts a fresh chain that `verify()` passes. Added `anchor.detect_truncation()`: an anchored head hash absent from the current chain means the history was truncated/rewritten since the off-box anchor. `verify_chains` now runs the check and exits non-zero. Test: `tests/test_anchor_truncation.py`.

## 3. Honest note on E2's verification surface

The `reconcile.py` E2 probe still prints `SILENT (fresh chain, no gap record)` — **by design.** It checks the *append* layer (`new_record.prev_hash is None`), and `append()` deliberately does **not** consult the anchor on the hot path (that would be an O(anchor) read per write). The E2 fix lives at the **audit/verify layer**, which is where "silent" becomes "detected": `test_anchor_truncation` proves `detect_truncation` flags the deleted ledger and `verify_chains.main(...)` returns `1`. So a silent deletion is now caught at the next `make test` / loop verify, not passed. E2 is closed at the layer that matters (audit), not hidden by a hot-path change.

## 4. Not executed (flagged)

**A7 🔒** — WebFetch untainted-first-move exfil is in `hooks/` (protected: human approval, PR, no auto-merge). Left for a human-reviewed design decision (corpus-content fingerprint on outbound params vs. rely on the taint layer that `BEHAVIOR.md` already names as the real control). Per CLAUDE.md, I did not modify protected paths autonomously.

## 5. Commits

```
3937971 R3/E2: detect silent ledger deletion via the off-box anchor
e6dcbac R4/E4: corrupt checkpoint restarts clean instead of bricking resume
47b7762 R2/E3 + R5/D3: scheduled send pauses on halt; at-most-once per payload
52ade3f R1/E1: heal torn ledger tail-line instead of bricking the writer
```

Verification environment + independent re-check: see `2026-07-12-verification-report.md`.
