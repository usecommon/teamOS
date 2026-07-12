# Review of the Review — 14-Counsel Adversarial Review

- **Date:** 2026-07-11
- **Reviewer:** Claude Fable 5 (`claude-fable-5`)
- **Subject:** `review/2026-07-11-adversarial-14-counsel-review.md`
- **Method:** Independent source verification of ~14 load-bearing claims spanning every severity tier (scientific integrity, all 5 security CRITICALs, behavioral). Each claim checked against the cited `file:line` in the working tree.

---

## Verdict

**High-quality, source-accurate. Trust it, with two calibration caveats.**

Every claim I checked held, with precise line references. Zero factual errors found. The line-level precision is real, not decorative. The meta-review also honestly corrects its own panel twice — a review that audits its own reviewers and downgrades their overreaches is doing the thing correctly.

The single most important finding is correctly ranked: fix #0 (the silently-relaxed A-P3 pre-registration) sits above every exfil hole. That is the one defect that changes a *conclusion* rather than a *risk posture*, and it is the right thing to lead with.

---

## Verification table

| Review claim | Source check | Result |
|---|---|---|
| A-P3 pass rule weakened: plan requires "pooled interval excluding zero," code does `pooled > 0` | plan:58 vs `transfer.py:79` | **Exact.** No interval computed anywhere. Function docstring rewritten to the weaker rule; module docstring still states the strong one. |
| `write_with_lineage` has zero production callers | grep | **Exact.** Only `tests/test_ledgers.py`. |
| Envelope steers nothing — `gate.py` never imports it | grep | **Exact.** Zero references. |
| Breaker unwired — only reads `TEAMOS_BREAKER`, config never sets it | `gate.py:43`, `settings-fragment.json` | **Exact.** |
| Gate fails open — `main()` has no try/except | `gate.py` tail | **Exact.** Unguarded `json.load` + `process()`. |
| Deletion deletes nothing — `request_erasure` appends events, never unlinks | `deletion.py:75,148` | **Exact.** Only `unlink()` is L8-specific (`:179`). |
| `l3.jsonl` committed to git | `git ls-files` | **Exact.** |
| `hashchain.append` has no locking | `hashchain.py` | **Exact.** read-last-hash-then-append, no flock. |
| FR2 exfil: scan is 6 credential regexes; corpus passes | `policy.yaml:60-67` | **Exact.** Non-credential data exfiltrates via `url` param. |
| Egress denylist misses ssh/git push/rsync/dig/open/osascript | `policy.yaml:46-57` | **Exact.** All absent. |
| Synced-paths misses `CloudStorage/`, `Box` | `policy.yaml:39-43` | **Exact.** "Google Drive" with a space won't match `CloudStorage/GoogleDrive-…`. |
| CN-1: `capture_edit(attribution="principal_authenticated")` default, no check | `l8_capture.py:18-19,57` | **Exact.** |

The meta-review honestly corrects its own panel twice — the behaviorist's "call `capture_edit` to self-widen" mechanism (wrong; `edit` records are ignored by the envelope) and the WebFetch verdict class.

---

## Where I'd push back on the review

### 1. "CRITICAL" and "theater" are over-dramatized for a fixtures-only, pre-production repo — and the review itself supplies the rebuttal.

The headline says "theater," then the meta-review admits these are "unenforced invariants, not live exploits… the system currently depends on nothing going wrong." Both can't be the honest framing. "Theater" implies intent to deceive; "unfinished enforcement in a mid-build repo with honest docs" is what the evidence actually shows — and the review praises that same honesty two sections later.

The *correct* severity of most items today is low (no production, no real data, envelope/breaker/safety-agent all inert); the severity becomes CRITICAL **at the moment real colleague data is ingested**. The review handles this correctly by gating its whole fix list on "before any real colleague data" — but a skimmer reads eight CRITICALs and misses that they're pre-emptive, not live. Calibration, not accuracy.

### 2. The FR2 finding tests one layer of a defense-in-depth design and reports it as total failure.

CLAUDE.md's own invariant says the outbound scan "catches VERBATIM secrets only; paraphrase-exfil is carried by taint + send gate." So "the regex only matches credentials" is the *documented* design, not a discovered flaw — the intended catch for corpus-exfil is taint-tracking (untrusted content can't add a recipient). The review's conclusion still stands, but for a reason it under-states: taint isn't implemented either (session-granular, deferred). The finding is "FR2 fails **because the compensating layer isn't built yet**," which is materially different from "the scan is naive." Worth the precision because it points at the real fix (build taint) rather than just "add more regexes."

### 3. Empirical claims are asserted, not shown.

The doc says two reviewers "ran exploits empirically" and "confirmed by execution," but includes no transcript or output. I re-derived the verdicts from source logic and they're correct — so the conclusion is sound — but a review invoking an empirical standard should carry the evidence in-artifact. Minor double-counting too: envelope-steers-nothing appears in three sections, which inflates the apparent finding count.

---

## Bottom line

This is a better review than most. The engineering claims are verifiable and verified; the prioritization is correct; it polices its own reviewers. Two adjustments when acting on it:

- Discount the rhetoric ("theater," the CRITICAL density) by remembering everything is gated on future data ingestion.
- Read the FR2 item as "the compensating control is unbuilt" rather than "the scan is broken."

Act on the fix list in the order given — **#0 (restore the pre-registered A-P3/A-A4 interval rules) first.**
