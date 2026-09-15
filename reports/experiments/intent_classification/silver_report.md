# Silver-Training Report — 44k weak labels → classifier baseline

Method: nearest gold-centroid labeling of all 44,199 messages (768-d, L2-normalized); margin = d2−d1; threshold 0.0055 calibrated on gold-train for ~70% precision. Train: embedding logreg (balanced, C=0.5) on 35,253 silver labels EXCLUDING all 300 gold UIDs (no leakage into gold-test). Files: `weak_labels_44k.csv`, `weak_label_config.json`, `silver_test_preds.csv`, `silver_metrics.json`, `gold_centroids.json`.

## Coverage
Silver accepted 35,526/44,199 (80.4%); rejected 8,673 (19.6%) = review queue (low-margin/ambiguous — the natural target for the next annotation round, mirroring the 2,500-plan's uncertainty stratum). Silver distribution is healthy across all 18 labels (min: OOD 141, upgrade 262, damaged 593; max praise 4,139). Tails that were n≤3 in gold now have hundreds of silver candidates for review-top-up.

## Metrics (gold test n=90, 17 classes)
| model | acc | macro-F1 |
|---|---|---|
| gold-only embed logreg (210) | 0.333 | 0.276 |
| **silver embed logreg (35,253)** | **0.589** | **0.583** |

Perfect-F1 classes: refund, assignment, upgrade, conduct (1.0). Strong: lost (.750), praise (.714), cancel (.667), status/failure (.615). Zero-F1: damaged (0 test ex — train-only), OOD (1 test ex). Weakest: fee (.286), missed (.308) — the known money-direction and rebooking boundaries.

## Caveats
Silver labels inherit gold-centroid bias, so test metrics are optimistic (train and test share embedding geometry and centroid origin). True performance needs the scaled human/model-reviewed set. The 8,673 rejects + tail silver (damaged/upgrade/OOD) must be reviewed before any production claim.

## Next step (single)
Review-top-up loop: (1) review all 8,673 rejects + tail silver samples with the v1.0 guideline (prioritize damaged/upgrade/OOD/cancel), (2) correct-and-merge into gold, (3) re-fit centroids + logreg, (4) fine-tune a MiniLM/E5 encoder with class weights + hard-negative pair gates, (5) final confusion audit. Transformer fine-tuning needs GPU/torch — not run here.
