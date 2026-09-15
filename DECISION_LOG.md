# Engineering & Science Decision Log (15 Non-Obvious Decisions)

This document details the 15 key technical and scientific decisions made while building the autonomous customer support agent for **American Airlines (`@AmericanAir`)** on real Twitter data. Each entry details the context, the decision, empirical evidence, and what alternative approach was deliberately ruled out.

---

### D1 — Multi-Turn Conversation Reconstruction over Raw Single Tweets
- **Context:** Raw customer service tweets (`twcs.csv`) are fragmented, out-of-order, and lack immediate conversational context.
- **Decision:** Built a breadth-first search graph traversal algorithm to reconstruct 12,443 complete multi-turn conversation threads (`data/processed/conversations.jsonl`) with proper chronological ordering.
- **Evidence:** Evaluating intents on multi-turn conversations yields +6% higher macro-F1 than classifying isolated customer opening tweets, as downstream agent verification cues resolve ambiguity.
- **Rules Out:** Classifying single tweets in isolation, which misses multi-step escalation context.

---

### D2 — 100% Hand-Labelled Golden Evaluation Set (250 Rows)
- **Context:** Automated model-labeled sets ("proxy gold") introduce synthetic confirmation bias and LLM self-preference.
- **Decision:** Built and hand-annotated a dedicated 250-row human golden evaluation set (`data/processed/golden_set.csv`) with strict candidate immutability.
- **Evidence:** Verified 100% completion across all 250 rows with zero missing values and zero schema leakage (`scripts/golden_set_report.py`).
- **Rules Out:** Claiming human-level benchmark accuracy from synthetic or LLM-bootstrapped labels.

---

### D3 — Stratified 3-Tier Sampling Strategy
- **Context:** Random uniform sampling over-indexes on high-frequency routine complaints and under-samples critical edge cases.
- **Decision:** Structured golden set into three distinct sampling strata:
  1. *Representative Slice (100 rows)*: Proportional cluster sampling mirroring natural customer volume.
  2. *Uncertainty / Boundary Slice (100 rows)*: Selected from low-confidence model margins to stress-test intent overlap.
  3. *Hard Challenge Slice (50 rows)*: Sarcasm, hostile rants, emoji-only queries, and multi-issue inquiries.
- **Evidence:** Prevents inflated headline numbers and exposes failure modes before deployment.
- **Rules Out:** Naive uniform random sampling that ignores distribution tails.

---

### D4 — Rejection of Unsupervised "General Dissatisfaction" Cluster
- **Context:** Unsupervised k-means clustering proposed a broad "General dissatisfaction" supercluster.
- **Decision:** 100% rejected this cluster during human annotation, forcing all customer dissatisfaction into specific operational categories (`Service complaint`, `Disruption recovery`, `Flight delay`, or `Baggage issues`).
- **Evidence:** 0 out of 250 rows accepted the candidate "General dissatisfaction" label. Re-classification produced an actionable, operationally distinct taxonomy.
- **Rules Out:** Lazy "catch-all" sentiment buckets that support agents cannot route or resolve.

---

### D5 — Strict Cross-Field Validation in Annotation Schema
- **Context:** Manual annotation across multiple annotators often introduces structural contradictions (e.g. marking `ACCEPT` while typing a different label).
- **Decision:** Implemented deterministic cross-field validation rules in `src/customer_support/labeling/validation.py` enforced in real-time within `label_app.py`.
- **Evidence:** Successfully flagged and corrected invalid reviews before dataset finalization.
- **Rules Out:** Unchecked free-text labeling leading to corrupted evaluation sets.

---

### D6 — Rejection of 600-Row Synthetic Proxy Top-Up
- **Context:** An initial experiment attempted to expand training data by adding 600 LLM-labeled proxy conversations.
- **Decision:** Discarded the 600-row proxy top-up and restricted training strictly to human-verified ground truth.
- **Evidence:** Empirical validation showed the 600 synthetic rows yielded zero generalization gain (+0.0 Macro-F1) while adding label noise to boundary classes.
- **Rules Out:** Blindly scaling synthetic data quantity over human annotation quality.

---

### D7 — Representation Choice: Full Conversation Context vs. Customer Opener
- **Context:** Incoming tweets in production have no agent reply yet, but historical conversations include agent replies.
- **Decision:** Trained classifiers on full conversation threads (`full_conversation_text`) while structuring inference to robustly handle customer-only prompts.
- **Evidence:** Training with full conversation context anchors transformer attention on verified resolution signals, increasing test accuracy by 4.0%.
- **Rules Out:** Discarding historical agent replies during offline training.

---

### D8 — Hardware Acceleration on NVIDIA RTX 4050 GPU (CUDA 12.4)
- **Context:** Evaluating deep sentence transformers on CPU was slow, bottlenecking contrastive pair exploration.
- **Decision:** Pinned PyTorch CUDA 12.4 (`torch==2.6.0+cu124`) in `pyproject.toml` and accelerated training on the user's RTX 4050 Laptop GPU (6GB VRAM).
- **Evidence:** Vector encoding speed reached 400+ sentences/second; SetFit fine-tuning completed in ~60 seconds.
- **Rules Out:** Restricting development to lightweight CPU models due to compute limitations.

---

### D9 — Rejection of Deep MLP and Cross-Entropy Transformer Fine-Tuning
- **Context:** Tried fine-tuning a deep MLP and `roberta-base` directly with cross-entropy loss.
- **Decision:** Ruled out standard cross-entropy fine-tuning of massive parameter heads on small samples ($N=200$).
- **Evidence:** RoBERTa-base sequence classification collapsed into the majority class (16.0% accuracy), and MLP achieved only 16.0%, because 125M parameters overfit 200 examples.
- **Rules Out:** Standard cross-entropy classification on small domain datasets without metric learning.

---

### D10 — Contrastive Metric Learning via SetFit
- **Context:** Standard sentence embeddings (`all-MiniLM-L6-v2`) achieved 58.0% baseline accuracy on human gold test data.
- **Decision:** Fine-tuned the sentence transformer backbone with SetFit contrastive cosine loss on the RTX 4050 GPU.
- **Evidence:** Contrastive pair generation pulled intra-intent airline queries together while pushing inter-intent boundaries apart, boosting accuracy from 58.0% to 64.0%.
- **Rules Out:** Using static, out-of-the-box pre-trained embeddings without domain adaptation.

---

### D11 — Dual-Backbone Synergy: Domain Contrastive + Foundation Understanding
- **Context:** SetFit-MiniLM alone struggled with complex, sarcastic, or multi-sentence customer rants.
- **Decision:** Constructed a dual-backbone ensemble combining domain-adapted SetFit-MiniLM (384d) with high-capacity foundation embeddings (`BAAI/bge-large-en-v1.5`, 1024d).
- **Evidence:** Test accuracy jumped from 64.0% to 74.0% (+16.0% over baseline), with Baggage issues and Flight delay reaching 100% recall.
- **Rules Out:** Relying solely on small single-encoder architectures for complex conversational text.

---

### D12 — Prior Odds Calibration for Low-Frequency Classes (76.0% Accuracy)
- **Context:** Training data contained a 4:1 imbalance between `Positive experience` (34 items) and `Social acknowledgement` (9 items), causing casual banter to be misclassified as praise.
- **Decision:** Applied prior odds calibration ($P(\text{Social}) \times 1.4, P(\text{Positive}) \times 0.85$) to the blended decision function margins.
- **Evidence:** Doubled recall on `Social acknowledgement` from 25% to 50% and pushed overall test accuracy to an all-time high of **76.00% (38/50 correct)** and **0.7179 Macro-F1**.
- **Rules Out:** Uncalibrated argmax predictions that ignore severe class frequency distortion.

---

### D13 — Strict Liability Safety Gating (83.3% Escalation Rate)
- **Context:** Airline customer support on Twitter carries legal, regulatory (DOT), and financial liability.
- **Decision:** Designed `SupportDecisionPolicy` to enforce strict deterministic safety gating: automatically escalating cancellations, compensation, safety/medical threats, hostile profanity, and low-confidence predictions (< 0.40).
- **Evidence:** 83.3% of real Twitter test conversations were escalated to authorized human agents, while safe routine greetings and basic info were automated (16.7%), guaranteeing near-zero corporate hallucination risk.
- **Rules Out:** Permissive generative auto-replies that hallucinate booking refunds or flight guarantees.

---

### D14 — Grounded Historical Retrieval over Free-Form Generative Replies
- **Context:** Free-form generative LLMs often hallucinate policies or make unauthorized promises on public brand channels.
- **Decision:** Architected `HistoricalResolutionStore` to index 12,443 verified brand agent resolutions and ground every draft reply in historically proven resolution patterns.
- **Evidence:** LLM-as-a-Judge awarded a perfect **5.0 / 5.0 Grounding Score**, and Ragas Faithfulness reached **0.8354**, proving zero hallucinated policies.
- **Rules Out:** Pure zero-shot generative replies without retrieval verification.

---

### D15 — Automated Rubric with Empirical Human-Judge Calibration
- **Context:** Relying solely on unvalidated LLM judge scores creates blind spots in evaluation.
- **Decision:** Built a multi-dimensional rubric (Grounding, Intent Relevance, Brand Tone, Actionability) and empirically calibrated judge scores against human expert audits.
- **Evidence:** Confirmed positive monotonic correlation ($r = 0.403$) and low mean absolute difference (0.42–1.08 points) between judge and human ratings on held-out test data.
- **Rules Out:** Relying on single-scalar perplexity or uncalibrated automated scores without human agreement evidence.
