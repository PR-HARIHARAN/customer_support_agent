# Hiver SDE Intern Take-Home: Final Submission Report
**Autonomous Support Agent & Evaluation Harness for American Airlines (`@AmericanAir`)**

---

## 1. Problem Framing

### What "Good" Means for American Airlines on Twitter
On Twitter (X), customer support is public, high-velocity, and high-liability. For American Airlines (`@AmericanAir`), a support agent is evaluated on three non-negotiables:
1. **Safety & Security First**: The agent must **never** solicit or allow passengers to tweet 6-character PNR record locators, ticket numbers, or payment info in public tweets. All identification must be routed to private Direct Messages (DM).
2. **Defensive Auto-Handling vs. Responsible Escalation**: When passengers face cancellations, missed connections, lost baggage claims, or severe flight disruptions, the AI must **not** hallucinate flight re-bookings, cash vouchers, or legal guarantees. It must escalate with a clear operational reason to human tier-2 agents while acknowledging the disruption empathetically.
3. **True Grounding**: Answers must reflect how American Airlines historically resolves issues (#AATeam brand tone, guiding to the Baggage Service Office, checking flight status, and directing to DMs).

### What We Chose NOT to Build
- **No Generative Auto-Booking / Payment Modification**: We deliberately chose not to let an LLM execute ticket refunds or seat changes directly. Real-world airline systems require authenticated SABRE/Amadeus API integrations with credit card authorization; executing re-ticketing over Twitter without verification is unsafe and irresponsible.
- **No Unconstrained Open-Ended Generation**: We banned unconstrained LLM responses. Every draft is strictly grounded in retrieved historical human agent resolutions from our canonical dataset of 12,443 reconstructed conversations.

---

## 2. Results vs. Baselines

All models were evaluated on the **exact same 20% held-out test split (seed 42, 200 train / 50 test)** of our 100% human-annotated golden set (`data/processed/golden_set.csv`).

| Model / Architecture | Type | Accuracy | Macro-F1 | Weighted-F1 | Status |
|---|---|---|---|---|---|
| **Majority Class** | Trivial Baseline | 0.1600 | 0.0340 | 0.0440 | Always predicts majority (`Service complaint`) |
| **Nearest Centroid (Cosine)** | Simple Geometric Baseline | 0.5200 | 0.4510 | 0.4990 | Fast, parameter-free centroid matching |
| **Logistic Regression (C=1.0, balanced)** | Standard Linear ML | 0.5800 | 0.5590 | 0.5790 | Multinomial L-BFGS head on static embeddings |
| **SetFit + LinearSVC (RTX 4050 GPU)** | Contrastive Fine-Tuned | 0.6400 | 0.6048 | 0.6276 | Contrastive adaptation on RTX 4050 GPU |
| **Dual-Backbone Ensemble (Raw Margins)** | Dual Fusion | 0.7400 | 0.6829 | 0.7278 | Domain + foundation blending (+16.0%) |
| **Calibrated SOTA Ensemble (WINNER)** | **Our Winning Model** | **0.7600** | **0.7179** | **0.7527** | **+18.0% accuracy gain over baseline** |

### Why the Calibrated SOTA Ensemble Succeeded (+18.0% Accuracy Boost)
1. **Domain Contrastive + Generalist Foundation Representations**: Combines fine-tuned Twitter airline domain embeddings (SetFit-MiniLM, 384d) with 1024-dimensional generalist conversational embeddings (`BAAI/bge-large-en-v1.5`).
2. **Prior Odds Calibration**: Adjusts for small-sample class frequency distortion (where praise was 4x more frequent than greetings), doubling recall on `Social acknowledgement` from 25% to 50% while preserving 100% recall on `Baggage issues` and `Flight delay`.
3. **Artifacts**: Serialized metrics at [`reports/experiments/intent_classification/calibrated_ensemble_76_metrics.json`](file:///e:/01_Projects/02_Main/Hiver_2/customer_support_agent/reports/experiments/intent_classification/calibrated_ensemble_76_metrics.json) and confusion matrix at [`reports/experiments/intent_classification/calibrated_ensemble_76_confusion_matrix.csv`](file:///e:/01_Projects/02_Main/Hiver_2/customer_support_agent/reports/experiments/intent_classification/calibrated_ensemble_76_confusion_matrix.csv).

---

## 3. Evaluation Harness: LLM-as-a-Judge & Ragas Metrics

We built an automated evaluation harness ([`scripts/run_eval_harness.py`](file:///e:/01_Projects/02_Main/Hiver_2/customer_support_agent/scripts/run_eval_harness.py)) measuring reply quality and brand policy across 4 rubric dimensions (1–5 scale) and automated Ragas metrics.

### Automated Evaluation Summary
- **Average LLM-as-a-Judge Score:** **4.37 / 5.0**
  - **Grounding & Faithfulness:** **5.0 / 5.0** (Zero hallucinated cash/vouchers; strictly anchored in historical resolutions)
  - **Intent Relevance:** **4.40 / 5.0** (Direct operational resolution to the customer's core problem)
  - **Brand Voice & Empathy:** **4.13 / 5.0** (Empathetic, concise, professional `#AATeam` tone)
  - **Actionability & Privacy:** **3.93 / 5.0** (Directs sensitive PNR/bag tags to DM)
- **Ragas Faithfulness:** **0.7819**
- **Ragas Answer Relevancy:** **0.6369**
- **Ragas Semantic Agreement:** **0.7630**
- **Decision Policy Distribution:** **AUTO_HANDLE = 16.7% | ESCALATE = 83.3%**
  - High escalation rate reflects conservative corporate safety gating (escalating angry customers, legal threats, cancellations, and damaged bag claims to human specialists).

### Evidence of Human-Judge Agreement
We calibrated the LLM-as-a-judge against human quality ratings across the test slice:
- **Pearson Correlation:** **r = 0.403** (positive alignment with human audits).
- **Mean Absolute Difference (MAD):** **1.08 points** on a 5-point scale.
- Both human and automated judge penalize replies that fail to direct sensitive booking information to DM or confuse Flight Delay with Disruption Rebooking.

---

## 4. Failure Analysis: Top 5 Failure Modes

Through systematic error auditing ([`reports/experiments/intent_classification/setfit_linearsvc_confusion_matrix.csv`](file:///e:/01_Projects/02_Main/Hiver_2/customer_support_agent/reports/experiments/intent_classification/setfit_linearsvc_confusion_matrix.csv)), we identified the top 5 failure modes:

### Mode 1: Sarcastic Praises Conflated with Genuine Positive Feedback
- **Example (CID 2307149)**:  
  *Customer:* `"@AmericanAir thank you so much for allowing the passengers of flight 2295 to sit in the airport in St. Lucia for 8+ hours..."*  
  *Predicted:* `Positive experience` | *True:* `Flight delay`
- **Hypothesis**: The sentence opens with lexical praise tokens (*"thank you so much"*), causing sentence embeddings to cluster near polite appreciation despite the underlying complaint.
- **Fix**: Add a sarcasm / sentiment contradiction detection head that checks for contrastive markers (*"for 8+ hours"*, *"waiting"*).

### Mode 2: Multi-Turn Operational Shift (Delay → Cancellation/Reroute)
- **Example (CID 1126533)**:  
  *Customer:* `"@AmericanAir talking to your staff is like talking to a toad. Leaving people stranded with no room, no car and no way out"*  
  *Predicted:* `Disruption recovery` | *True:* `Service complaint`
- **Hypothesis**: Multi-intent customer venting mixes severe frustration with stranded conditions. The classifier picked the operational disruption rather than the staff behavior complaint.
- **Fix**: Implement a multi-label classification head that outputs both primary intent and secondary escalation flags.

### Mode 3: Lost Items Left in Cabin vs. Checked Baggage
- **Example (CID 175587 & 890712)**:  
  *Customer:* `"@AmericanAir A friend just flew ORD-LGA, Seat 5f... and left his LAPTOP in the seatback pocket. Who does he contact?"*  
  *Predicted:* `Flight information` / `Seats and fares` | *True:* `Baggage issues`
- **Hypothesis**: Left-on-board personal items (lost & found) share tokens with seating (*"seatback pocket"*, *"seat 5f"*) rather than standard checked luggage vocabulary (*"bag tag"*, *"carousel"*).
- **Fix**: Expand the Baggage taxonomy to explicitly define an `"In-Cabin Lost and Found"` sub-intent.

### Mode 4: Upgrade Inquiries Confused with General Ticket Fares
- **Example (CID 848782 & 2023541)**:  
  *Customer:* `"@AmericanAir pls explain why my $750 tkt isn't eligible for a paid standby. Gate agt doesn't know..."*  
  *Predicted:* `Service complaint` | *True:* `Seats and fares`
- **Hypothesis**: Customers expressing confusion about complex fare rules often mention gate agents (*"gate agt doesn't know"*), triggering service complaint embeddings.
- **Fix**: Introduce hierarchical coarse-to-fine gating (Fare Rule inquiry vs. Agent Incompetence).

### Mode 5: Low-Context Single-Word Social Mentions
- **Example (CID 1876039)**:  
  *Customer:* `"Finally made it to Platinum status with @AmericanAir after 3+ years of travel. It's the little things in life."*  
  *Predicted:* `Positive experience` | *True:* `Social acknowledgement`
- **Hypothesis**: Platinum status milestone celebrations sit directly on the semantic boundary between brand praise and personal social sharing.
- **Fix**: Both intents are safely handled with brand appreciation, resulting in zero operational liability.

---

## 5. "What is Misleading About My Headline Number?" (Mandatory Section)

### 1. The 76.0% Accuracy Reflects an 8-Class Test Split (50 Instances), Not Production Volume
Our headline accuracy of **76.0%** (and Macro-F1 of **0.7179**) was measured on a held-out test split of 50 conversations. While achieving a **+18.0% improvement over the 58.0% baseline**, certain tail classes (like `Social acknowledgement` n=4 in test) have very few test instances, meaning a single misclassification impacts macro-F1 by ~2.5%.

### 2. Evaluated on Twitter Conversations, Not Omnichannel Inquiries
Twitter interactions are uniquely condensed (under 280 characters) and disproportionately skewed toward public escalations. A headline number trained on Twitter data will not generalize out-of-the-box to long-form email support or live webchat without domain adaptation.

### 3. High Grounding Score is Boosted by Retrieval Constraints
Our LLM-as-a-judge gave a **5.0/5.0 Grounding Score**. This high number is because our system is architected as an extractive-grounded generator that strictly prevents hallucinating flight vouchers or payment adjustments. It reflects safety constraint enforcement, not free-form conversational fluency.

### 4. Conservative Escalation Bias
Our decision policy escalates **83.3%** of test cases. While this guarantees near-zero corporate liability on Twitter, a commercial deployment aiming for a 40% auto-resolution rate would need to relax thresholds for routine baggage tracking and flight status inquiries once backend SABRE APIs are connected.

---

## 6. What We Would Do Next With One More Week

1. **Active Learning Feedback Loop in `label_app.py`**:
   - Stream the agent's lowest-confidence production predictions back into `label_app.py` for continuous human review, growing the golden set from 250 to 1,000+ examples.
2. **Cross-Encoder Reranking for Historical Retrieval**:
   - Implement a cross-encoder (`ms-marco-MiniLM-L-6-v2`) on top of FAISS retrieval to rerank historical resolutions by conversational relevance before prompt synthesis.
3. **Multi-Label Intent Architecture**:
   - Transition from single-label to multi-label intent detection (e.g. allowing `Flight delay` + `Service complaint` simultaneously).
4. **Mocked SABRE / PNR Lookup Tool**:
   - Integrate LangGraph tools with a mocked airline reservation database to resolve real PNR status queries during automated handling.

---

## 7. Decision Log (15 Non-Obvious Decisions)

1. **D1 — Every headline number must be an executable artifact**: Persisted as JSON + markdown reports in `reports/` rather than hardcoded in documents.
2. **D2 — Reconstruction over raw tweets**: Grouped 12,443 Twitter interactions into complete multi-turn threads (`conversations.jsonl`) to preserve conversational context.
3. **D3 — Separation of Proxy Gold vs. Human Gold**: Maintained strict separation between model-adjudicated labels (`gold_300.csv`) and true human ground truth (`golden_set.csv`).
4. **D4 — Frozen 9-Class Taxonomy**: Froze taxonomy at v1.0 with explicit tie-breaking rules to ensure all model iterations are directly comparable.
5. **D5 — Complete Human Golden Set Annotation (250/250 rows)**: Fully reviewed all 250 conversations across Representative (150), Uncertainty (60), and Challenge (40) strata.
6. **D6 — Elimination of "General Dissatisfaction" Noise Cluster**: Confirmed via human review that 100% of candidate "General Dissatisfaction" rows were specific operational intents or service complaints, eliminating unsupervised noise.
7. **D7 — Cross-Field Validation Rules**: Enforced logical validation in `label_app.py` to prevent contradictory verdicts (e.g. `ACCEPT` with a differing intent).
8. **D8 — Rejection of Proxy-600 Top-Up**: Maintained empirical evidence rejecting the 600-row proxy top-up after verifying it yielded zero generalization gain (+0.0 F1).
9. **D9 — Hardware Acceleration on RTX 4050 Laptop GPU**: Upgraded PyTorch to CUDA 12.4 (`torch==2.6.0+cu124`), unlocking local GPU acceleration.
10. **D10 — Adoption of SetFit Contrastive Fine-Tuning**: Chose SetFit few-shot sentence-transformer adaptation over deep neural nets to prevent overfitting on 200 training examples.
11. **D11 — Balanced Linear Support Vector Classifier Head**: Selected `LinearSVC(C=0.5, class_weight='balanced')` over Logistic Regression to maximize geometric margins on embedding spheres.
12. **D12 — LangGraph Multi-Actor State Machine**: Implemented the support pipeline in LangGraph to enforce a clean separation of concerns (`classify` → `retrieve` → `draft` → `policy`).
13. **D13 — Historical Grounded Resolution Store**: Built an indexed repository from 12,443 brand conversations so generated replies are anchored in real brand practices.
14. **D14 — Defensive Escalation Policy**: Gated all legal, financial, medical, profanity, and cancellation inquiries to human escalation to eliminate public Twitter brand liability.
15. **D15 — Calibrated Multi-Dimensional LLM-as-a-Judge**: Designed an explicit 4-part rubric and validated judge calibration against human ratings ($r = 0.403$).
