# Review Top-Up Report — gold 300 → 600 (single-model, proxy review)

Sample: 300 (tails: damaged 60, upgrade 60, OOD 40, cancel 40 + reject-queue 100), annotated once by qwen2.5:7b under v1.0. No adjudication (limitation). Files: `review_topup_300.json`, `topup_review_300.json`, `gold_600.csv`, `gold_centroids_600.json`.

## Agreement signal
Model-vs-centroid agreement on top-up: **0.217** (vs ~0.70 on easy cases). Expected: sample is adversarial by design (tails + rejects). Consequence check: of 60 damaged-silver candidates the model kept only 4 as damaged (centroid over-files damaged — confirms v0.4 over-filing warning); OOD kept 13/40; cancel 16/40; upgrade kept 23/60. Model under-assigns missed (6), assignment (4), gate-check (3) on hard cases — same conservative pattern as v0.4 rescore.

## Valid eval (fresh 450/150 stratified split, disjoint)
| model | acc | macro-F1 |
|---|---|---|
| centroid (600-gold) | 0.327 | 0.328 |
| logreg (600-gold) | 0.280 | 0.272 |

No gain vs gold-300 baselines (0.40/0.33 on n=90; 0.33/0.28 embed-logreg). The earlier 0.622 was leakage (test UIDs inside train) — discarded. Synchronized verdict: **adding 300 unadjudicated single-model labels on hard cases does not improve generalization.** Quality (adjudication) beats quantity.

## Decision
Top-up stays as silver-v2 (useful for retrieval/top-up pools and centroid priors), NOT merged into trusted gold for training claims. Trusted set remains adjudicated gold_300. Next: adjudicate top-up centroid-vs-model conflicts (~235) with the A/B+adjudicator protocol (or human spot-review of tails), then re-fit; only then scale to 2,500. Transformer fine-tuning still blocked on torch/GPU env + reviewed volume.
