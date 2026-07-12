# Claude Code Remediation Prompts — residual durability/liveness

- **Date:** 2026-07-12
- **Model:** Claude Fable 5 (`claude-fable-5`)
- **Use:** paste one prompt per task into Claude Code, in order. Each is self-contained, names its files, its test, and its done-criteria. All targets are in `scripts/` (non-protected). Run `make test` after each; one commit per task off `remediation/2026-07-11`.
- **Governing rules:** files are the system of record; test alongside code; fail-safe posture must not weaken; no protected paths (`hooks/`, `adapter/`, `config/envelope-policy.json`, CLAUDE.md) touched.

---

## Prompt R1 — E1: torn ledger tail-line must not brick the writer

```
In scripts/hashchain.py, a crash mid-append can leave a partial final line (no
newline / invalid JSON). Today last_hash() then crashes in json.loads on every
future append, permanently bricking the ledger.

Fix, without weakening tamper-evidence:
1. last_hash(): walk backward past TRAILING lines that don't parse to a record
   with a "hash" field; return the last VALID record's hash (None if none).
2. append(): before writing, detect and truncate a torn trailing fragment
   (a final line that is non-newline-terminated OR does not parse to a record);
   keep all complete records.
3. Do NOT change verify() — interior tampering/gaps must still raise.

Add tests/test_hashchain.py:
- append {"a":1}; corrupt by appending a partial '{"partial":' fragment;
  assert a subsequent append() SUCCEEDS and verify() returns the intact count.
- assert an interior tampered record still makes verify() raise.

Done: make test green; the torn-tail case no longer raises.
```

## Prompt R2 — E3: a tripped breaker must pause the loop, not crash it

```
In scripts/day_one_brief.py, when the circuit breaker is open the gate denies
the send and deliver() raises PermissionError; run_if_due() doesn't catch it, so
the scheduled autonomous run dies and retries-crash every tick.

Fix:
1. Define `class GateBlocked(PermissionError)`. In deliver(), raise GateBlocked
   (not bare PermissionError) when the gate decision != "allow". Keep the base
   class PermissionError so existing `assertRaises(PermissionError)` still pass.
   Leave the post-permit "send failed after permit" path as a plain
   PermissionError (a real failure, not a halt).
2. In run_if_due(), capture the prior state before claiming the slot. Wrap
   action(): on GateBlocked, roll back the claim (restore prior state so
   last_run is NOT advanced) and return (False, catch_up, None) WITHOUT raising
   — a graceful pause. Any other exception keeps today's behavior (mark failed,
   raise).

Add a test (tests/test_brief.py): breaker open -> run_if_due(..deliver..) returns
ran=False, does not raise, slot still due; breaker closed -> next call delivers.

Done: make test green; reconcile.py E3 row reports GRACEFUL.
```

## Prompt R3 — E2: whole-file ledger deletion must be detected

```
Deleting a ledger file and appending starts a fresh chain (prev_hash=None) and
verify() passes — silent history loss. T13 writes an off-box anchor witness
(scripts/anchor.py) but nothing consults it.

Fix:
1. In scripts/anchor.py add detect_truncation(ledger_dir, anchor_dir): for each
   ledger that has a recorded anchored head, check that head hash still appears
   in the current chain. Return the list of ledger names whose anchored head is
   missing (truncated/rewritten since the last anchor).
2. In scripts/verify_chains.py, run detect_truncation and exit NON-ZERO with a
   clear message if any ledger's anchored head is gone.

Add a test: anchor a chain head, delete the ledger, re-append a fresh record;
assert detect_truncation flags that ledger.

Done: make test green; a deleted ledger is caught at the chains step instead of
passing.
```

## Prompt R4 — E4: corrupt checkpoint must restart clean

```
In scripts/checkpoint.py, Checkpoint.__init__ does json.loads(read_text()); a
torn checkpoint crashes every resume so the loop can never restart.

Fix: wrap the load. On JSON error, move the bad file to <name>.corrupt (preserve
for audit) and initialize clean {"done":[],"results":{}}. A corrupt checkpoint
costs at most a redo of the current run.

Add tests/test_checkpoint.py: write garbage to the checkpoint path; Checkpoint(path)
initializes with empty done/results; the corrupt bytes are preserved at .corrupt.

Done: make test green.
```

## Prompt R5 — D3: deliver must be at-most-once against its receipt

```
In scripts/day_one_brief.py, run_if_due claims the slot before the effect, but
deliver() itself is not idempotent: an out-of-band re-invocation re-posts (probe
shows sends=3). T13's send-receipt makes this auditable, not prevented.

Fix: in deliver(), before slack.post_message, scan the L2 ledger for an existing
"send-receipt" record with the same payload_digest (sha256 of the text) and
outcome "send_succeeded". If found, return the prior ts WITHOUT re-posting
(idempotent). Scheduled-brief content varies per slot, so suppressing an
identical payload only ever drops a true duplicate.

Add a test (tests/test_brief.py): call deliver(brief,…) twice with the same
brief; assert slack.post_message ran once and the second call returns the first
ts; assert exactly one send-receipt with outcome send_succeeded.

Done: make test green; reconcile.py D3 row reports at-most-once.
```

---

## Not in this batch (flagged)

**A7 🔒 (protected path)** — WebFetch untainted-first-move exfil lives in `hooks/`.
Do not auto-apply. Open a PR with a design proposal (corpus-content fingerprint
on outbound URL/params vs. rely on the taint layer per BEHAVIOR.md) for human
review.
