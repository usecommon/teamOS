# Team OS Fork — Master Report

- **Date:** 2026-07-12
- **Model:** Claude Fable 5 (`claude-fable-5`)
- **Scope:** consolidates every review + simulation + remediation record in `review/` into one status document.
- **Tree state:** clean at `030acff`; remediation series **T0–T13** landed; findings reconciled live against the current tree.
- **Nature:** all evidence is sandboxed simulation with synthetic actors — **formative, not proof.** Severity is conditional: most security items become *live* only when real colleague data is ingested (the CLAUDE.md stop-and-flag gate).

---

## 1. TL;DR

A four-council adversarial review (`2026-07-11-adversarial-14-counsel-review.md`) plus four simulation passes (security, autonomy, failure-injection, and a 4-team × 120-turn sweep) found **~30 findings**. A remediation series **T0–T13** closed the security and privacy criticals; a live reconciliation (`030acff`) re-verified every item against the current tree. **The gate now fails closed, exfil via bash/known-send tools is gated, deletion erases content, the ledger survives concurrency, untrusted content can't auto-commit plan structure, acceptance signals are authenticated, and the initiative floor no longer over-counts.** What remained was **not security** — a cluster of **durability / liveness** bugs in the unattended-run machinery (E1–E4, D3). **That cluster has since been remediated and verified this session** (§3). What is still open: one security **residual** (A7 untainted-first-move exfil, protected path) and the standing **non-code long pole** (recruit real collaborators for the A-P3 transfer gate).

**Bottom line:** the system is safe-by-construction under fault (no fail-open observed), but not yet *robust* — several faults make it fail **closed-but-dead** (crash/brick) rather than degrade gracefully, which for a system that runs while its principal is away is the next thing to fix.

## 2. What was fixed (T0–T13, verified)

| Fix | What it closed | Verified |
|---|---|---|
| **T0** | Restored the pre-registered A-P3/A-A4 interval rule (was weakened to a point-estimate) | `passes_preregistered_rule` computes a t-interval, requires `lo>0` |
| **T1** 🔒 | Gate fails **closed** — a crash denies, never permits | garbage stdin → `rc=2`, "failing closed" |
| **T2** 🔒 | FR2: session-granular **taint** layer + egress hardening | bash egress (quoted/ssh/rsync/git-push/dig) → deny/ask; synced paths; unknown tool → send-class |
| **T3** 🔒 | Resolved-path protection for the dials, the stop, and the hook config | symlink→`hooks/gate.py`, breaker-state write → `ask`/protected-path |
| **T4** | Deletion touches **content** (not just tombstones); `dm_email` enforced; `l3` untracked | 12/12 deletion tests; wired probe removes content |
| **T5** | Serialized ledger appends (flock spans read-last-hash + write) | 16×40 concurrent → chain intact (640/640) |
| **T6** | Decoupled the acceptance signal; killed the engagement penalty | heavy edit no longer narrows autonomy |
| **T7** | Authenticated the L8 endorsement path (CN-1, HMAC) | forged endorsements no longer widen the envelope (0→0) |
| **T8** | The gameable L7 marker score is scaffolding — promotion won't count it | — |
| **T9** | Safety agent wired + windowed; **door proposals need human approval**; spawn bounds enforced | untrusted→schedule/skill now **PENDING-APPROVAL**, not committed |
| **T11/T12** 🔒 | Divergence log reconciled; individuation audit in CI | — |
| **T13** | Atomic state, send **receipts**, anchor witness, key perms, JWT regex, orphan removal | send outcome is now auditable |

**Regression-guard (fixed & re-verified live):** A1–A6, A10, B1–B5, C1–C6, D1, D2, D4. See `2026-07-11-consolidated-findings.md` for the full table.

## 3. What remains open (reconciled live)

> **Status update (this session): the durability/liveness cluster below is now FIXED.**
> Commits `52ade3f` (E1), `47b7762` (E3+D3), `e6dcbac` (E4), `3937971` (E2). Verified
> 10/10 in a clean sandbox — see `2026-07-12-remediation-execution-report.md` and
> `2026-07-12-verification-report.md`. The table is kept for the record with live
> before→after verdicts. **Only A7 (protected) and the non-code long pole remain open.**

### Durability / liveness — REMEDIATED (was the real residual, P1)
An unattended agent must degrade, not die. These made it die or lose data; each now degrades gracefully:

| # | Finding | Before | After (verified) |
|---|---|---|---|
| **E1** | Torn ledger tail-line **bricked the writer** | `CRASH JSONDecodeError` | ✅ `GRACEFUL` — append heals the torn tail; interior tamper still caught |
| **E3** | Tripping the breaker **crashed the scheduled loop** | `CRASH PermissionError` | ✅ `GRACEFUL` — `GateBlocked` → loop pauses, retries when breaker closes |
| **E2** | Whole-file ledger deletion was **silent** | `verify passes` | ✅ `DETECTED` — `anchor.detect_truncation` + `verify_chains` exit non-zero |
| **D3** | Scheduled **double-send** (sends 3×) | `sends=3` | ✅ `sends=1` — `deliver` at-most-once against its send-receipt |
| **E4** | Corrupt checkpoint **crashed resume** | crash on load | ✅ restarts clean; `.corrupt` preserved for audit |

### Security residual (P1 — protected path 🔒) — STILL OPEN
| # | Finding | Live verdict | Note |
|---|---|---|---|
| **A7** | WebFetch exfiltrates non-credential corpus data in the URL on an **untainted first move** | `ALLOW (still open)` | Taint closes it *after* a corpus read; the untainted-first-move case permits. `hooks/policy.yaml` documents the substring denylist as interim; the taint layer is the intended control. **Touches `hooks/` — needs human review; do not auto-merge.** |

### Non-code / human (cannot be closed by remediation)
- **T10** — recruit 2–3 collaborators, declare unattended posture in L2, start the 14-day streak, fill the FR8 overhead ledger. The standing long pole.
- **F6 / A-P3** — transfer is `inconclusive` at synthetic n; needs real receivers (the T0 interval rule is correct).

## 4. Metrics vs the thesis (synthetic — formative)

- **A-C4 cold-start:** compile + brief assembly succeed; delivery is gated by the fail-closed breaker on a fresh install (a facet of E3/A5 — correct posture, needs a first-run bootstrap).
- **A-A4 initiative:** the floor instrument was fixed (T6–T8) to count unprompted, unedited, deduped acceptances — `weekly_accepted=2` on the reconcile fixture (was inflated to 82–91). Real floor now measurable but needs real data.
- **A-P3 transfer:** inconclusive at synthetic n; the long pole.

## 5. Recommendation

The durability/liveness cluster (**E1, E3, E2, D3, E4**) is **done and verified** this session (`scripts/` only, no protected paths). What's left: handle **A7** as a separate, human-approved change on `hooks/` (still `allow` on a fresh session — verified), and the non-code long pole (**T10/F6**). Everything security/privacy-critical is closed except A7; per the CLAUDE.md gate, do not ingest real colleague data until A7 is closed.

## 6. Source index

- Reviews: `2026-07-11-adversarial-14-counsel-review.md`, `2026-07-11-meta-review-of-14-counsel-review.md`
- Plan: `2026-07-11-remediation-workorder.md`
- Findings (authoritative, reconciled): `2026-07-11-consolidated-findings.md`
- Simulations: `2026-07-11-simulation-report.md` (§3a security, §8a autonomy, §8b resilience), `2026-07-12-remediation-simulation-report.md` (100-turn, 0 violations), `sim-2026-07-12/`
- Evidence/probes: `sim-artifacts/` (`engine.py`, `engine_autonomy.py`, `engine_faults.py`, `reconcile.py`)
