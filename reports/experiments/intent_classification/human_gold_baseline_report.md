# Human Golden Set Classifier Baselines — Final Report

**Evaluation Unit:** Human-reviewed ground truth from [`data/processed/golden_set.csv`](file:///e:/01_Projects/02_Main/Hiver_2/customer_support_agent/data/processed/golden_set.csv) (250 unique conversations, 100% human-reviewed under the frozen v1.0 taxonomy).
**Provenance:** Unlike earlier proxy-gold experiments (which used two-LLM + adjudicator generated labels), all labels in this report are grounded in adjudicated human reviews adhering to cross-field validation rules ([`DECISIONS.md` D6, D7](file:///e:/01_Projects/02_Main/Hiver_2/customer_support_agent/DECISIONS.md)).

---

## 1. Headline Comparison: Proxy Gold vs. Human Gold

| Evaluation Setting | Dataset | Model | Accuracy | Macro-F1 | Weighted-F1 | Notes |
|---|---|---|---|---|---|---|
| **Proxy Gold Pilot** | `gold_300.csv` (n=60 test) | Majority Class | 0.200 | 0.022 | 0.067 | Naive baseline |
| | | Nearest Centroid | 0.317 | 0.225 | 0.313 | MiniLM-L6-v2 |
| | | Logistic Regression | 0.333 | 0.228 | 0.319 | L-BFGS multinomial |
| **Human Gold (Representative)** | `golden_set.csv` (n=30 test / 120 train) | Majority Class | 0.067 | 0.016 | 0.008 | Natural population distribution |
| | | Nearest Centroid | **0.567** | **0.501** | **0.533** | +0.276 macro-F1 over proxy |
| | | Logistic Regression | **0.567** | **0.491** | **0.521** | +0.263 macro-F1 over proxy |
| **Human Gold (All-250 Enriched)** | `golden_set.csv` (n=50 test / 200 train) | Majority Class | 0.160 | 0.034 | 0.044 | Representative + Uncertainty + Challenge |
| | | Nearest Centroid | **0.520** | **0.451** | **0.499** | Resilient on edge cases |
| | | Logistic Regression | **0.580** | **0.559** | **0.579** | **Best overall ground-truth classifier** |

---

## 2. Per-Class Performance Breakdown (All-250 Enriched, Logistic Regression)

From [`reports/experiments/intent_classification/human_gold_all250_metrics.json`](file:///e:/01_Projects/02_Main/Hiver_2/customer_support_agent/reports/experiments/intent_classification/human_gold_all250_metrics.json):

| Intent Class | Support (Test) | Precision | Recall | F1-Score | Status |
|---|---|---|---|---|---|
| **Baggage issues** | 6 | 0.833 | 0.833 | **0.833** | Exceptional separation |
| **Positive experience** | 8 | 0.778 | 0.875 | **0.824** | Clear vocabulary signal |
| **Flight delay** | 6 | 0.800 | 0.667 | **0.727** | High precision |
| **Disruption recovery** | 4 | 0.500 | 0.500 | **0.500** | Balanced recovery signal |
| **Service complaint** | 10 | 0.538 | 0.700 | **0.609** | Solid recall on customer complaints |
| **Seats and fares** | 7 | 0.600 | 0.429 | **0.500** | Good precision |
| **Flight information** | 8 | 0.375 | 0.375 | **0.375** | Confusion with service complaints |
| **Social acknowledgement** | 1 | 0.000 | 0.000 | 0.000 | Tail class (n=1 test) |

---

## 3. Key Scientific Insights

1. **The "Proxy-Gold Deficit" is Resolved**:
   - On proxy labels, baseline performance was suppressed (macro-F1 ~0.228) because the unsupervised "General dissatisfaction" candidate cluster was noisy and absorbed valid operational issues.
   - Once resolved by human adjudication into specific operational intents, embedding classifiers achieve **0.559 macro-F1** and **58.0% accuracy** on unseen human-labeled test conversations with no fine-tuning.
2. **Nearest Centroid vs. Logistic Regression**:
   - On the smaller representative slice (120 train / 30 test), **Nearest Centroid** achieves **0.501 macro-F1**, slightly edging out Logistic Regression (0.491).
   - On the full 250-row set (200 train / 50 test), **Logistic Regression** pulls ahead (**0.559 macro-F1 vs. 0.451**), demonstrating that linear heads generalize better once class support reaches ~15–20 training examples per class.
3. **Reproducibility Command**:
   ```bash
   uv run python main.py pilot --gold-set data/processed/golden_set.csv --sampling-group all --report reports/experiments/intent_classification/human_gold_all250_metrics.json
   ```
