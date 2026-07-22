# Realistic synthetic data — and what it exposes about cold-start

- **Date:** 2026-07-21 · **Built:** `synth.generate_realistic_footprint` + `teamos synth --realistic`
- **Why:** the 2026-07-20 realism audit rated the clean synthetic data ~2/10 and predicted that de-labeling it would reveal the deterministic compiler can't do cold-start. This built the realistic generator and **ran that experiment.** The prediction held.

## What "realistic" means here

The clean generator (`generate_footprint`) hands the compiler its answer: every file carries `deliverable_type: standup` frontmatter, the type is also in the filename stem, cadence is perfectly regular, and there's no junk. Real footprints have **none** of that. `generate_realistic_footprint` produces what real data looks like:

- **De-labeled** — no `deliverable_type` frontmatter anywhere; type must be inferred from content.
- **Opaque, varied filenames** — `msg-<hex>.md`, `2026-06-03-3f85.md`, `Re-cache.md`, `note-<date>.md` — type never in the stem.
- **Noised cadence** — ±2-day jitter, ~20% missed occurrences, occasional bursts.
- **Junk at 4× the deliverable volume** — replies ("thanks!", "+1"), notifications ("[CI] build passed"), off-topic ("lunch at 12?"), newsletters.

## The experiment: clean vs realistic through the real compiler

| Persona | Clean tasks | **Realistic tasks** | Realistic files | Cluster found | True types recovered |
|---|---|---|---|---|---|
| engineer | 3 | **1** | 320 | `note ×32` | **NONE** |
| pm | 3 | **1** | 110 | `note ×15` | **NONE** |
| ops | 3 | **1** | 305 | `note ×31` | **NONE** |
| researcher | 3 | **1** | 315 | `note ×34` | **NONE** |
| founder | 3 | **1** | 115 | `note ×15` | **NONE** |

## The finding

**On realistic data the deterministic compiler recovers ZERO of the true deliverable types.** The single "recurring task" it reports is a **filename artifact**: the ~1-in-6 files named `note-<date>.md` all collapse to the signature `note` (dates stripped), so it clusters 15–34 *unrelated* files — standups, PRs, incidents, **and junk** — into one meaningless "note" task. It found "you write notes," not "you do standups / PRs / incidents."

So the clean generator's tidy "3 recurring tasks" — and the A-C2 gate passing on it — was **entirely an artifact of pre-labeling.** `compile_footprint` clusters by `deliverable_type` frontmatter, falling back to the filename stem (`_signature`) and filename dates. Strip the labels (as reality does) and it has no true signal to cluster on.

## Implication for the thesis

**A-C2 / A-C4 (cold start: compiler finds ≥3 *real* recurring tasks; Day One Brief recognizable) does not hold on realistic data with the deterministic core alone.** Inferring "these 30 unlabeled, differently-named files are all standups" is a **semantic classification problem that requires the model-in-the-loop layer** — which the architecture defers as the "high-touch" part. The deterministic path handles labeled/structured input (Claude Code command imports, tagged exports); it cannot cold-start a raw human footprint.

This is not a bug in the compiler — it's the honest boundary of the deterministic approach, now demonstrated rather than assumed. It sharpens the R1 decision: the cold-start thesis (compiler distills a raw footprint) needs the model layer built and measured; the parts that are done and real (governed loops, ledgers, envelope, deletion, transfer rig) don't depend on it.

## What's now available

- `teamos synth --persona <id> --realistic [--weeks N] --out <dir>` — generate realistic footprints for honest testing.
- `synth.generate_realistic_footprint(...)` — reusable by the sim/tests.
- Tests assert the data is de-labeled + junk-laden, and that the compiler recovers 0 true types from it (the finding, locked in).

## Recommended next

1. **Treat A-C2's clean-data pass as "plumbing," not "cold-start works."** Re-run cold-start against realistic data once the model-inference layer exists — that's the real gate.
2. **Scope the model-in-the-loop type-inference layer** (deferred) if the cold-start thesis is being pursued; it's the pacing item for A-C4 on real footprints.
3. The behavior model is still unrealistic too (acceptance decoupled from quality — see the 07-20 audit); a quality-coupled, non-stationary behavior model is the parallel fix if A-A4 is pursued.
