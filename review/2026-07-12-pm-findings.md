# Team OS — PM Review Findings (corrected, post-review)

- **Date:** 2026-07-12 · **Model:** Claude Fable 5 · **Code:** HEAD `0f069f4` (post-remediation T0–T13)
- **Source:** `review/2026-07-12-pm-product-review.md` (full report). Findings below are the **corrected** set after adversarial + council + fact-check review; all code claims verified in the sandbox worktree.
- **Nature:** §4 findings are observed behavior of the shipped code. §3 persona reads (in the full report) are demonstrations under authored personas, not measured adoption.

## Ranked findings

| # | Sev | Finding | Evidence (verified) |
|---|---|---|---|
| 1 | **CRITICAL** | **Autonomy envelope is inert at enforcement.** `gate.py` never reads the envelope; sole consumer is the dashboard renderer. Send verdict identical at level 0 vs ceiling. State moves; enforcement doesn't. Fix locus per FK6b is `settings.json`, not `gate.py`. | `grep -c envelope hooks/gate.py` → 0; probe: verdict same at high/zero level |
| 2 | **CRITICAL (flip side of #1)** | **Level-0 permissiveness.** Policy declares level 0 = "ask always," but an untainted, secret-clean send at level 0 returns `allow`. Inert envelope grants *un-earned* autonomy, not just withholds earned. | level-0 untainted send verdict = `allow` |
| 3 | **HIGH-security** | **Acceptance signature is replayable (CN-1 gap).** `signing_payload` binds only `signal_type\|path\|principal_id\|outcome`; `unprompted` and `edit_distance_normalized` — the fields the floor/envelope gate on — are unsigned, no nonce. A captured signed endorsement can be replayed with `unprompted:true`/doctored distance and pass `verified()`. | `principal_auth.py:46-54` |
| 4 | **HIGH** | **Initiative floor not computable as orchestrated (A-A4).** Slack-✓ path (`harvest_reactions`) is structurally floor-ineligible (no `unprompted`/distance). `capture_edit(unprompted=True)`+keydir is eligible but no shipped orchestration calls it. Formative posture reads zero. | run: 82 authenticated endorsements → 0 floor-eligible |
| 5 | **HIGH** | **Security posture vs low-interrupt promise unreconciled.** Session-keyed taint → interactive corpus-drafting session always `ask`s on send regardless of envelope. Corpus-as-taint is designed/divergence-logged; the *reconciliation* is not. Headless path has no confirm surface — `deliver()` raises on non-`allow`, so `ask`==hard fail. | `gate.py:188-193`, `day_one_brief.py:104`, `hooks/taint.py` |
| 6 | **HIGH residual** | **WebFetch first-move exfil.** Untainted session: `WebFetch(url=?d=<corpus>)` → `allow/send-scanned-clean`; scan matches only secret patterns. Gated only after a taint-read. | `allow/send-scanned-clean` |
| 7 | **MEDIUM** | **Cold-start silence — kit-install path only** (re-scoped). Repo ships a git-tracked closed `ledgers/breaker.json`; a real clone install delivers (4/4). Gap survives only for the collaborator kit install (no breaker provisioning). "Distinguish missing vs tampered" fix is unsound — strike it. | `git ls-files ledgers/` shows closed breaker; kit path unprovisioned |
| 8 | **MEDIUM** | **Autonomy gradient favors low-effort stamping** (partly epistemic). Heavy edits (`signal_type="edit"`) move the envelope not at all; only light/no-edit accepts widen it. A distance-0 rubber-stamp is observationally identical to a genuine clean accept — no acceptance-shaped metric separates them without external ground truth. | `envelope.py`, `measurement.py` |
| 9 | **PROCESS** | **FK6b divergence-log entry missing.** Envelope shipped state-machine-only vs the spec's settings.json actuation, with no §7 divergence entry. | no §7 entry references the envelope |

## Confirmed NOT broken (prior criticals closed)

- Untrusted → plan structure: **FIXED** — schedule/skill proposals go to `pending` (human approval); never auto-commit.
- Deletion: **WORKS** — 12/12 `test_deletion` pass; sim failure was an unmapped-node-id harness artifact.
- Bash egress (`ssh`, `git push`): **`ask`** (human-gated), not `allow`.
- Forgery with keydir: **BLOCKED** for unsigned forgeries (but see #3 — replay of *signed* records is open).
- Individuation: **clean** — no per-person leaderboard; audit passes on both dashboard modules.

## Residual / evidence gaps

- Deletion ledger enumerates *what* was deleted in git (org-rollout blocker; IETF tombstone pattern is a fix template).
- Per-principal encryption keys are plain files (no hardware keystore).
- Transfer (FK7/A-P3) inconclusive at n=2 synthetic receivers — needs real collaborators.

## Fix chain (dependency-ordered — not a menu)

1. Actuate the envelope at the settings.json locus + fix level-0 permissiveness.
2. Bind `unprompted`/distance + a nonce into the acceptance signature.
3. Make the floor computable end-to-end; validate `weekly_accepted()` ≥3 for two consecutive weeks on the builder's footprint.
4. Decide the taint ↔ interrupt reconciliation; give the headless path a real confirm surface.
5. Provision a closed breaker on the kit-install path + user-facing block message.

Then: 4 weeks on builder + 2–3 recruited collaborators → **GO** if floor ≥3/week and ask-rate falls; **PIVOT** to governed-drafting-for-compliance-ICs if taint keeps ask-rate flat; FK7 read = platform go/no-go. Blockers to the GO decision: n>1 validation and a unit-cost-per-principal-week number.
