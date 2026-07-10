**`2026-07-10`** *(FK1 — proposed divergence-log entries; MERGED into fork spec §7 on 2026-07-10 by principal instruction — this file kept as audit trail)*

# Divergence-log proposals (FK1)

Per CLAUDE.md, divergence-log edits are append-only via PR, human-merged. These
entries were produced by the FR1 mapping gate (`make mapping` regenerates the
field-miss list mechanically). Classes per fork spec §6: field-miss entries are
**uncounted** toward R18's ≤5 architectural-deviation threshold.

## class: field-miss (4 — from the A-FK1 gate, 97.2% mapped, 0 load-bearing misses)

1. **field-miss** `corpus-entry#/owner` — harness artifacts carry no ownership
   metadata; single-principal pilot defaults every entry to the principal.
   Maps when FK4 compilation or multi-user scope assignment supplies it.
2. **field-miss** `ledger-l5#/delegation_chain[].token_ref` — no OIDC/W3C-VC
   token primitive in the harness or the fork pilot; delegation chains are
   recorded without cryptographic tokens until mainline's authenticated-
   delegation framework.
3. **field-miss** `scope#/disclosure_default` — the CLAUDE.md cascade carries no
   disclosure policy. Default-deny stands in structurally (promotion gate is
   the only exit); populates when FK3b/FK7 policy config exists.
4. **field-miss** `skill#/capability_manifest.capture_surface` — the harness
   command format declares no capture-surface tier; import defaults to
   cloud+synced+local-folders and the default is recorded as a default, not a
   mapping.

## class: experiment note (uncounted)

- The harness cascade exposes three levels (enterprise/project/user); the
  five-scope model's division/org levels have no harness counterpart at fork
  scale (n≤3). The schema carries all five; the adapter emits only
  company/team/individual. A scope-level gap, not a field gap — revisit at
  merge-back.

## class: experiment note (FK6c — PENDING, require a live cloud platform)

Both need a real Cowork/Routines surface + a remote-driven session; not runnable
in this build environment. Recorded here; results fill in when run on the pinned
surface.

- **FK6c experiment #1** — can an *ordinary* (non-privileged) cloud session
  *create* scheduled tasks via the platform's own tools, or only `update` them?
  Determines whether "one guided chat sets up schedules" is achievable or the
  reconciliation task must be seeded another way. STATUS: pending.
- **FK6c experiment #2** — do *remote-driven* Claude Code sessions (mobile app
  driving a local CLI) execute the local FK2 hooks? If yes, that posture is
  full-trust from the phone (upgrade ladder rung 2). STATUS: pending.

## class: path-(b) surface tests (FK6c — PENDING, require a live cloud run)

Deterministic fences are tested (loop-prompt linter, proposal-parser probes).
The three live-surface checks — one real cloud-scheduled run end-to-end through
the door; missed-run catch-up on the cloud tier; caps-exhaustion behavior — need
the actual platform and are pending, not closeable by CI.

## Counting-rule note for A-FK1 (human review requested)

The gate counts `fork-native` fields (values authored by fork writers — ledger
envelopes, scoring, deletion engine — where the harness was never the datum's
source) as *mapped*, on the reasoning that no translation occurs, so nothing
can be lost. If review rejects that rule and restricts the numerator to
`harness-mapped` only, the percentage over the harness-facing schemas (skill,
scope, corpus-entry, lineage-sidecar, L1) still clears 90%, but the report
should be re-cut that way deliberately, not silently.
