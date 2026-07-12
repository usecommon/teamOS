# Verification Report — residual remediations

- **Date:** 2026-07-12
- **Model:** Claude Fable 5 (`claude-fable-5`)
- **Under test:** the fixed tree after commits `52ade3f`, `47b7762`, `e6dcbac`, `3937971` (E1/E2/E3/E4/D3).
- **Environment:** a fresh sandbox copy of the repo (`…/scratchpad/verify-sandbox`), isolated ledgers/state, synthetic data only, no real-world side effects.
- **Method:** (1) full `make test`; (2) an independent verification harness (`sim-artifacts/verify_remediation.py`) that exercises each fixed item end-to-end **and** re-checks the security regression guards; (3) live re-run of `reconcile.py`.

---

## 1. TL;DR

Every residual now **degrades instead of dying**, and no security control was weakened. Full suite green (**210 tests**); the independent harness is **10/10 PASS**; the reconcile probe flips E1/E3/D3 from crash/double-send to graceful/at-most-once. E2 is closed at the audit layer (anchor detection), which is where a silent deletion becomes visible.

## 2. Results

### 2a. Full suite
`make test` → **210 tests, OK**; 16 schemas, 0 failures; `verify_chains` clean.

### 2b. Independent harness (`verify_remediation.py`) — 10/10 PASS

| Check | Result |
|---|---|
| E1 torn-tail heals append (verify=3 records) | PASS |
| E1 regression: interior tamper still detected (`verify` raises) | PASS |
| E4 corrupt checkpoint restarts clean; `.corrupt` preserved | PASS |
| E2 silent deletion detected by anchor (`detect_truncation` flags; `verify_chains` rc=1) | PASS |
| E3 breaker-open **pauses** loop (`ran=False`, no crash, slot unclaimed) | PASS |
| E3 resumes when breaker closes (`ran=True`) | PASS |
| D3 at-most-once per identical payload (`sends=1`, same ts) | PASS |
| REG fail-closed: corrupt breaker → deny | PASS |
| REG exfil: bash egress+secret → deny | PASS |
| REG concurrency guard intact (640/640, unit suite) | PASS |

### 2c. Live reconcile probe (before → after)

| Item | Before | After |
|---|---|---|
| E1 torn tail-line | `CRASH JSONDecodeError` | `GRACEFUL (append tolerated torn tail)` |
| E3 breaker-open scheduled send | `CRASH PermissionError` | `GRACEFUL (no crash)` |
| D3 double-send | `sends=3` | `sends=1 (at-most-once)` |
| E2 ledger deletion | `SILENT` (append layer) | `SILENT at append, DETECTED at verify` (see §3) |

## 3. E2 — where it's verified

`reconcile.py` reports E2 at the **append** layer (a fresh chain's `prev_hash is None`), and `append()` intentionally does not consult the off-box anchor on the hot write path. The fix lives at the **audit/verify** layer: `anchor.detect_truncation()` compares the last anchored head against the current chain and `verify_chains` fails non-zero when it's gone. The harness confirms both: `flagged=['l7.jsonl']`, `verify_chains rc=1`. A silent deletion is now caught at the next verify/loop, which is the layer that matters for tamper-evidence.

## 4. Regression posture

The fixes touched only durability/liveness paths (`hashchain`, `day_one_brief`, `checkpoint`, `anchor`, `verify_chains`). The security guards are unchanged and re-verified live: the gate still fails closed on a corrupt breaker, bash egress carrying a secret still denies, interior ledger tampering still raises, and the 640/640 concurrency guarantee holds. **No protected paths (`hooks/`, `adapter/`, `config/envelope-policy.json`, CLAUDE.md) were modified.**

## 5. Residual after this batch

- **A7 🔒** — WebFetch untainted-first-move exfil, `hooks/` (protected): flagged for human-approved design decision; not executed here.
- **T10 / F6** — non-code long pole (recruit real collaborators; A-P3 transfer at real n). Cannot be closed by remediation.

## 6. Artifacts

- Harness: `review/sim-artifacts/verify_remediation.py`
- Reconcile probe: `review/sim-artifacts/reconcile.py`
- Sandbox: `…/scratchpad/verify-sandbox` (left intact)
- Execution detail: `2026-07-12-remediation-execution-report.md`
- Status roll-up: `2026-07-12-master-report.md`
