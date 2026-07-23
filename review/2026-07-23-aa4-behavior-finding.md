# Realistic behavior model — and what it exposes about A-A4

- **Date:** 2026-07-23 · **Built:** `synth.draft_quality` / `downstream_use` / `realistic_decision` / `update_trust`
- **Why:** the 07-20 audit rated the behavior model ~2/10 — acceptance was a coin flip *decoupled from draft quality*, so A-A4 (does the acceptance proxy correlate with real downstream use?) was structurally untestable. This built the realistic version and ran the honest test. Parallels the cold-start finding.

## What "realistic behavior" means here

- **Draft quality** — a latent [0,1] score per turn, with variance and a trust-ramp (the agent improves over ~40 turns). The thing that was missing entirely before.
- **Downstream use** (ME-1) — was the deliverable actually forwarded / clicked / referenced? Quality-coupled + independent noise. This is the **second series** A-A4 correlates against — it did not exist in the old model.
- **Quality-coupled acceptance** — `p(accept) = f(quality, trust)`, not a coin flip. Edit distance is content-tied (worse draft → bigger edit).
- **Non-stationary trust** — earned slowly on acceptance, dropped fast on rejection (OB-1), so the envelope tracks a *moving* level instead of a flat line.

## The experiment: proxy↔use correlation, realistic vs null, swept over n

`measurement.proxy_behavior_correlation` (Pearson r + Fisher-z 95% interval, "correlated" only if the interval excludes zero):

| n | Realistic (quality-coupled) | Coin-flip null (current) |
|---|---|---|
| 100 | r=0.10 [−0.10, 0.29] inconclusive | r=0.10 inconclusive |
| 250 | r=0.15 [0.02, 0.27] **correlated** | r=0.10 inconclusive |
| 500 | r=0.08 [−0.00, 0.17] inconclusive | r=0.08 inconclusive |
| 1000 | r=0.08 [0.01, 0.14] **correlated** | r=0.03 inconclusive |
| 2000 | r=0.06 [0.01, 0.10] **correlated** | r=0.01 inconclusive |
| 4000 | r=0.045 [0.014, 0.076] **correlated** | r=0.005 inconclusive |

(At n=120 across all 5 personas, the null even produced a **false positive** — founder r=0.19 "correlated" — a small-n fluke.)

## Two findings

**1. The A-A4 instrument is sound.** With real coupling it detects the proxy↔use correlation (interval excludes zero) once n is large enough; the coin-flip null shrinks to r→0 and stays inconclusive at every n. So the measurement design — Pearson r with a pre-registered interval — works: it neither misses real signal (at n) nor is fooled by the null (at n). This validates the *instrument*, which is what a synthetic test legitimately can.

**2. The effect is small (r ≈ 0.05–0.15), so A-A4 needs a LOT of real data.** Because acceptance and downstream-use are both noisy signals of the same latent quality, their correlation is inherently modest, and the interval only reliably excludes zero around **n ≈ 1000+ rated deliverables**. The fork's planned instrument — a ~25-point micro-pulse over a 4-week clock — is **underpowered by an order of magnitude** to detect an effect this size. And small-n runs can false-positive (the founder n=120 case), which is exactly why the interval + pre-registration + "decision point, not pass/fail" framing matter.

## Implication for the thesis

**A-A4 is measurable in principle, but not at the planned scale.** The old coin-flip model correctly yields no A-A4 signal — so any A-A4 number from the earlier clean campaign would have been noise, confirmed. To get a real A-A4 read you need either (a) far more rated deliverables than a 4-week solo run produces (densify hard, or run much longer), or (b) a stronger, cleaner downstream-use signal than "forwarded/clicked." This mirrors the cold-start finding: the realistic test reveals a boundary the clean data hid.

Combined with the 07-21 cold-start finding, the two production-as-eval gates now have honest boundaries:
- **A-C4 (cold start):** does not work on real footprints without the deferred model-inference layer.
- **A-A4 (production-as-eval):** the instrument is sound but needs ~1000+ points; the planned ~25 is underpowered.

Both sharpen the R1 decision. Neither touches the parts that are done and real (governed loops, ledgers, envelope dynamics, deletion, transfer rig, observability) — but both say the *cold-start / production-as-eval thesis* needs materially more (a model layer, and far more data) than currently scoped.

## What's now available

- `synth.realistic_decision / draft_quality / downstream_use / update_trust` — a quality-coupled, non-stationary behavior model for honest A-A4 / envelope testing.
- `review/2026-07-23-aa4-behavior-experiment.py` — the reproducible power sweep.
- Tests lock in: acceptance is quality-coupled, and the instrument separates coupled (correlated at n) from null (inconclusive).
