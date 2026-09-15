# Gold-300 Classifier Baselines — Final Report (proxy-human gold)

Gold: `gold_300.csv` (137 agreed + 163 adjudicated: A114/B43/wrong5+tie1). Taxonomy: v1.0 frozen (18 labels, 4 adjudication-majority tie-breaks T1–T4). Splits: `gold_train.csv` 210 / `gold_test.csv` 90, stratified (seed 42); `baggage_damaged` (n=1) train-only, unevaluated. Models: TF-IDF+logreg, embedding+logreg (balanced, C=1), nearest-centroid (train centroids). Artifacts: `gold_test_confusion_matrix.csv`, `baseline_metrics.json`, `gold_centroids.json` (18×768, reuse for confidence-filtered propagation).

## Metrics (test n=90, 17 classes)
| model | acc | macro-F1 |
|---|---|---|
| tfidf_logreg | 0.222 | 0.157 |
| embed_logreg | 0.333 | 0.276 |
| centroid | **0.400** | **0.326** |

Centroid wins: with ~12 ex/class, parametric heads overfit; geometry already encodes coarse structure. Zero-F1: cancellation, refund, upgrade, OOD (≤3 test ex each). Strongest: assignment (F1 .727, recall 1.0), lost (.667), praise (.615), thanks (.556), status (.533). Note gate-check over-predicted as fallback (5+ false assignments into it) — its centroid is too broad (boarding + baggage vocabulary).

## Hard-negative slices (centroid, test)
- assignment↔upgrade 5 acc .80 (best — cabin test works)
- praise↔thanks 14 acc .64
- lost↔gate-check 7 acc .57; lost↔damaged 4 acc .50
- delay↔status 21 acc .43; delay↔missed 18 acc .39; delay↔cancel 15 acc .33; cancel↔missed 7 acc .29
- venting↔failure 14 acc .29; conduct↔failure 10 acc .20; refund↔fee 6 acc .17 (worst — money-direction needs more examples)

## Error analysis
Errors concentrate exactly on the v0.4-unresolved boundaries (noise↔venting, delay↔status, money-direction) plus gate-check centroid spread. No error suggests a missing 19th label; all confusions fall inside documented pairs. TF-IDF logreg far worse → wording alone insufficient at this sample size; embedding geometry carries the signal.

## Verdict
300 proxy-gold labels validate taxonomy *consistency* (annotation pipeline works end-to-end) but are **insufficient to train production intent classification** (macro-F1 0.33 ceiling, 4 classes unevaluable). This is a sample-size verdict, not a taxonomy verdict.

## Next step (single)
Scale labeling per the 2,500-message plan (§7 of v0.4 track): stratified central/boundary/random + tail retrieval (damaged photos, upgrade lists, gate-check protests, bare cancels, Spanish) to ≥50 train examples per actionable class, then re-run these exact baselines → fine-tune MiniLM/E5 with class weights → hard-negative gates → confusion audit. Reuse `gold_centroids.json` for confidence-filtered pre-labeling with human/model review (never auto-accept below margin threshold; tails always reviewed).
