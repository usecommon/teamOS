# Remediations — residual durability/liveness cluster

- **Date:** 2026-07-12
- **Model:** Claude Fable 5 (`claude-fable-5`)
- **Source:** `2026-07-11-consolidated-findings.md` "Still-open, ranked", re-verified live by `sim-artifacts/reconcile.py`.
- **Scope:** the 5 residual **durability/liveness** items — all in `scripts/` (non-protected). **A7** (WebFetch untainted-first-move exfil) is `hooks/` (protected) and is **flagged, not auto-remediated** here.
- **Principle:** an unattended agent must **degrade, not die**. Every fix below turns a crash / silent-loss into a graceful, auditable outcome. No fix weakens a security control; failure stays deny/halt-by-default.

---

## R1 — E1: torn ledger tail-line bricks the writer  `[HIGH]`

- **Defect:** a crash mid-`append` leaves a partial last line (no newline / invalid JSON). Every future `hashchain.append` then crashes in `last_hash()` → `json.loads(torn)`. The ledger is permanently un-writable.
- **File:** `scripts/hashchain.py` (`_tail_line`, `last_hash`, `append`).
- **Fix:**
  1. `last_hash()` walks backward past **trailing** lines that don't parse to a record with a `"hash"` field, returning the last *valid* record's hash. A torn tail no longer crashes the reader.
  2. `append()` truncates a torn (non-newline-terminated or non-parseable) trailing fragment **before** writing, so the file stays clean and `verify()` still passes over completed records.
  3. Mid-chain corruption is untouched — `verify()` still raises on any tampered/excised interior record.
- **Proof:** append `{"a":1}` then a partial `{"partial":` fragment; a subsequent `append` succeeds; `verify()` returns the count of intact records. (New `tests/test_hashchain.py`.)
- **Invariant:** tamper-evidence preserved (interior breaks still caught); availability restored (a crash artifact self-heals).

## R2 — E3: tripping the breaker crashes the scheduled loop  `[HIGH]`

- **Defect:** breaker-open → `deliver()` raises `PermissionError` → `run_if_due()` doesn't distinguish it from a real failure → the autonomous run dies and retries-crash each tick.
- **File:** `scripts/day_one_brief.py` (`deliver`, `run_if_due`).
- **Fix:**
  1. Add `class GateBlocked(PermissionError)`. `deliver()` raises `GateBlocked` when the gate denies the send (keeps `PermissionError` as the base so existing `assertRaises(PermissionError)` stays green). A genuine post-permit send failure stays a plain `PermissionError`.
  2. `run_if_due()` catches `GateBlocked`: it **rolls back the slot claim** (does not advance `last_run`) and returns `(ran=False, catch_up, None)` without raising — a graceful pause. The run retries on the next tick once the breaker closes.
- **Proof:** breaker open + `run_if_due(..deliver..)` returns `ran=False`, does not raise, leaves the slot due; breaker closed → next call delivers. (New `tests/test_hashchain.py`/`test_brief.py` case.)
- **Invariant:** the safety halt still halts the side effect (deny holds); it now pauses the loop instead of killing it.

## R3 — E2: whole-file ledger deletion is silent  `[HIGH]`

- **Defect:** delete a ledger and `append` again → a fresh chain (prev_hash=None); `verify()` passes; the truncation is invisible. T13 added an off-box **anchor witness** but it's not consulted.
- **Files:** `scripts/anchor.py` (add `detect_truncation`), `scripts/verify_chains.py` (wire it).
- **Fix:**
  1. `anchor.detect_truncation(ledger_dir, anchor_dir)` — for each ledger with a recorded anchored head, confirm that head hash still appears in the current chain. If absent → the history was truncated/rewritten since the last anchor. Return the list of truncated ledgers.
  2. `verify_chains.py` runs the check and **fails loudly** (non-zero) when an anchored head is missing — so `make test`'s `chains` step surfaces a silent deletion instead of passing.
- **Proof:** anchor a chain's head, delete the ledger, re-append; `detect_truncation` flags it; `verify_chains` exits non-zero. (New test.)
- **Invariant:** deletion is now **detected** at the next verify/loop; the off-box witness is the trust root, as SE-6 intends.

## R4 — E4: corrupt checkpoint unrecoverable on resume  `[MED]`

- **Defect:** `Checkpoint.__init__` does `json.loads(read_text())` — a torn checkpoint crashes every resume; the loop can't restart.
- **File:** `scripts/checkpoint.py`.
- **Fix:** wrap the load; on corruption, move the bad file aside to `<name>.corrupt` and start clean (`{"done":[],"results":{}}`). A corrupt checkpoint costs a redo of the current run, never a permanent crash.
- **Proof:** write garbage to the checkpoint path; `Checkpoint(path)` initializes clean; the corrupt bytes are preserved at `.corrupt`. (New `tests/test_checkpoint.py`.)
- **Invariant:** resume is always possible; no silent loss (corrupt file retained for audit).

## R5 — D3: scheduled double-send on crash-after-effect  `[HIGH]`

- **Defect:** `run_if_due` already claims the slot before the effect (at-most-once for its own path), but `deliver()` itself is **not idempotent**: an out-of-band re-invocation (crash-after-effect that rewinds state) re-posts. Probe: `sends=3`.
- **File:** `scripts/day_one_brief.py` (`deliver`).
- **Fix:** before `slack.post_message`, scan L2 for an existing `send-receipt` with the same `payload_digest` and `outcome=send_succeeded`. If found, **return the prior `ts` without re-posting** (idempotent). Scheduled-brief content varies per slot (date/digest), so suppressing an *identical* payload only ever suppresses a true duplicate.
- **Proof:** call `deliver(brief,…)` twice with the same brief → one `post_message`, second returns the first `ts`; `slack.messages` has one entry. (New test.)
- **Invariant:** at-most-once per unique payload, enforced at the send path — not just auditable via the receipt.

---

## A7 — IMPLEMENTED (Option B), pending human merge-approval

### A7 🔒 — WebFetch untainted-first-move exfil  `[HIGH, protected path]`
- **Was:** `WebFetch(?d=<corpus>)` on a fresh session → `allow`. Taint closed it only after a corpus read; the untainted first move permitted.
- **Decision:** Option B — fingerprint outbound content against the stored corpus.
- **Implemented (`13924ed`):** `taint.matches_corpus(policy, texts, repo_root)` computes word-shingle overlap between outbound content and `stores/corpus` (URL-encoding/underscores collapse to the same tokens), cached by corpus mtime. Folded into gate.py's existing `tainted` check — **net-zero lines**, gate.py stays at the 300-line X-1 budget — so a matching send returns `ask/taint-confirm`. Config: `policy.yaml` `corpus_fingerprint` (k=6, min_shingles=1, enabled). Tests: `tests/test_corpus_egress.py` (4 cases; full suite 214 green). Heuristic defense-in-depth; the taint layer remains the primary control.
- **Status:** committed on `remediation/2026-07-11` tagged `[protected: hooks/]`. **Touches `hooks/` — needs human approval before merge to main** (CLAUDE.md protected-path rule). Do not ingest real colleague data until merged.

## Sequencing
R1 → R2 → R4 (hashchain/loop/checkpoint core), then R3 (anchor wiring), then R5 (send idempotency). One task per commit, test alongside, `make test` green before each. Branch: current `remediation/2026-07-11`. None touch protected paths.
