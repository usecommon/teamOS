# Team OS — Harness-Native Fork

**You run your agents; then your team does.** Team OS is how *one person* runs
their own agents — on the record, under gates they own, with autonomy they can
dial from tight command-and-control up to a free-running lab — and then grows into
how their **team** runs together. Human-centric by design: the unit is a *person*,
and the agents are the **fabric** that carries what the person and the team know
(who knows what, skills that transfer between people, memory that outlives
turnover). Not an agent-orchestration framework — the payoff is people getting
better together. (Full positioning: `positioning/positioning-v0.9.md`.)

This repo is the harness-native fork: Team OS implemented using a
Claude-Code-class harness's own primitives (CLAUDE.md cascade = scope; skills =
registry; hooks = gates; scheduled tasks = loops; a plugin = the kit). Governing
docs in `docs/`; the fork spec is `docs/team-os-fork-harness-native.md`, the
gates are `docs/team-os-fork-validation-plan.md`. Onboarding:
`docs/INSTALL.md` and `docs/onboarding.html`.

**One test command:** `make test` (schemas + FR1 mapping gate + hook budget +
240 unit tests + chain verification). CI runs the same on every push.

## Build status — FK1..FK8 mechanisms complete

| Item | What | Key modules | Gate (functional) |
|---|---|---|---|
| FK1 | schemas + adapter + FR1 gate | `docs/schemas/`, `adapter/`, `scripts/mapping_report.py` | ✅ 97.2% mapped, 0 load-bearing misses |
| FK2 | gate hook + ledger substrate | `hooks/gate.py`, `scripts/hashchain.py`, `scripts/l3_writer.py`, `l8_capture.py`, `l1_compile.py` | ✅ probes blocked, lineage-required, tamper-detected |
| FK3 | deletion propagation | `scripts/deletion.py` | ✅ tombstone/flag/resume, L8 shred keeps chain |
| FK3b | connector config + credential domains | `config/connectors.json`, `scripts/connectors.py` | ✅ off-by-default, allowlist, Plane-A owned inference |
| FK4-pre | threat model + basis | `docs/fk4-pre-threat-and-basis.md` | ✅ 5 personas; source basis = null for own data |
| FK4 | compilation skill (C2) | `scripts/compile_footprint.py` | ✅ 5/5 found, injection quarantined, distill-then-discard |
| FK5 | Day One Brief | `scripts/day_one_brief.py`, `slack_client.py` | ✅ gated send, SE-1 harvest, catch-up |
| FK6 | Class A loops | `scripts/loop.py`, `checkpoint.py`, `measurement.py`, `anchor.py` | ✅ ≥3 deliverables, FR4 resume, L7, floor |
| FK6b | envelope-by-script | `scripts/envelope.py`, `config/envelope-policy.json` | ✅ slow-widen/fast-narrow, forged ✓ can't widen |
| FK6c | kit + door | `scripts/door.py`, `gate_processor.py`, `loop_linter.py`, `posture.py`, `reconcile.py`, `plugin/` | ✅ propose→inbox, SE-3 probes, fences |
| FK7-pre | multi-user trio | `scripts/crypto_store.py`, `dashboard.py` | ✅ per-principal crypto, self-ledger, no individuation |
| FK7 | transfer mechanism | `scripts/promotion_gate.py`, `transfer.py` | ✅ PII/eval-floor block, cohorts, byte-identical rollback |
| FK8 | discovery scout | `scripts/discovery.py` | ✅ texture guard, ≤2/run, A-D3-lite floor |

## What mechanisms CANNOT close (measured on real data / people / time)

- **A-C4** (cold start) — real footprint + a non-builder run.
- **A-A4** (production-as-eval) — 14-day unattended streak + 4-week clock + ≥25 pulses.
- **A-P3** (transfer) — 2–3 collaborators, within-receiver time series.
- **FK6c live experiments** (#1 create-schedules, #2 remote-driven hooks) + path-(b)
  surface tests — need a live cloud platform. Recorded pending in
  `docs/divergence-log-proposals.md`.

## Invariants held throughout

Files-as-truth; every tool call gated + hash-chained; memory writes carry lineage
(unlabelled write rejected by construction); default-deny sharing; deletion before
ingestion; DMs/email opt-in; no individuation surface; per-principal encryption
(exit = clone); untrusted content never becomes plan structure.
