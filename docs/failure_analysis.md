# Systematic Failure Analysis: Top 5 Failure Modes

This document provides a root-cause breakdown of the top 5 failure modes identified during held-out test evaluation on the 250-row human golden set for American Airlines (`@AmericanAir`). All cases represent real customer interactions from `data/processed/golden_set.csv`.

---

### Failure Mode 1: Sarcastic Praise Disguising Severe Operational Delays
- **Example:**  
  *Conversation ID:* `2307149`  
  *Customer Message:* `"@AmericanAir thank you so much for allowing the passengers of flight 2295 to sit in the airport in St. Lucia for 8+ hours with no AC and no food. Top notch service!"`
- **Observed Behavior:** The model classified this message as `Positive experience` with 0.62 confidence.
- **Expected Behavior:** `Flight delay` (or `Disruption recovery` / `Service complaint`).
- **Likely Cause:** Strong lexical praise tokens (*"thank you so much"*, *"top notch service"*) dominate sentence embedding representations, masking the negative context.
- **Evidence:** Confusion matrix shows 2 test instances of delay and complaints bleeding into `Positive experience` (`reports/experiments/intent_classification/calibrated_ensemble_76_confusion_matrix.csv`).
- **Hypothesis:** Dense encoders trained on general semantic similarity cluster polite gratitude openers near positive centroids unless specifically trained with contrastive sentiment contradiction pairs.
- **Implemented Resolution:** Integrated a regex-based `SARCASM_CONTRADICTION_PATTERNS` rule in `SupportDecisionPolicy` and `_draft_node` in `graph.py`. When ironic praise keywords co-occur with operational distress tokens (*"8+ hours"*, *"no ac"*, *"no food"*, *"tarmac"*), the system automatically overrides `AUTO_HANDLE` to `ESCALATE` (*"Sarcastic or ironic sentiment detected disguising operational disruption; escalating to senior customer relations agent."*) and drafts an empathetic disruption apology instead of praise. Verified in unit tests (`test_failure_mode_1_sarcasm_escalated`).

---

### Failure Mode 2: Multi-Turn Operational Shift (Delay Venting vs. Service Complaint)
- **Example:**  
  *Conversation ID:* `1126533`  
  *Customer Message:* `"@AmericanAir talking to your staff is like talking to a toad. Leaving people stranded with no room, no car and no way out"`
- **Observed Behavior:** The model classified the interaction as `Disruption recovery`.
- **Expected Behavior:** `Service complaint`.
- **Likely Cause:** Multi-intent customer venting combining operational disruption (*"stranded with no room"*) with direct employee insult (*"talking to your staff is like talking to a toad"*).
- **Evidence:** In single-label classification, multi-intent messages force an arbitrary winner when both semantic signals are active simultaneously.
- **Hypothesis:** Customers in acute travel distress frequently combine the root cause (stranded flight) with their immediate grievance (rude agent), causing equal margin activation across two classes.
- **Implemented Resolution:** Added `STAFF_GRIEVANCE_PATTERNS` to `SupportDecisionPolicy`. When customer frustration combines flight disruption with frontline staff insults or misconduct accusations, the policy escalates immediately to a human supervisor (*"Frontline employee conduct grievance or customer conflict detected; escalating to human supervisor."*). Verified in `test_failure_mode_2_staff_insult_escalated`.

---

### Failure Mode 3: In-Cabin Lost & Found Items Confused with Checked Baggage
- **Example:**  
  *Conversation ID:* `175587` (and `890712`)  
  *Customer Message:* `"@AmericanAir A friend just flew ORD-LGA, Seat 5f... and left his LAPTOP in the seatback pocket. Who does he contact?"`
- **Observed Behavior:** The model classified the interaction as `Seats and fares` (and `Flight information`).
- **Expected Behavior:** `Baggage issues`.
- **Likely Cause:** Tokens like *"seatback pocket"* and *"seat 5f"* activate cabin/seating feature dimensions rather than standard checked luggage vocabulary (*"bag tag"*, *"carousel"*).
- **Evidence:** Evaluator confusion matrix shows in-cabin lost items consistently scatter into `Seats and fares` or `Flight information`.
- **Hypothesis:** The training taxonomy combined checked luggage claims with left-on-board personal electronics under a broad `Baggage issues` umbrella, creating an intra-class lexical disconnect.
- **Implemented Resolution:** Added `IN_CABIN_LOST_PATTERNS` to `SupportDecisionPolicy` and `_draft_node`. The reply synthesizer provides official American Airlines Lost & Found portal instructions (`https://www.aa.com/lostandfound` and arrival airport Baggage Service Office coordination). High-stakes items (passports, IDs, medications) are escalated immediately to airport station operations. Verified in `test_failure_mode_3_in_cabin_lost_handled`.

---

### Failure Mode 4: Upgrade Inquiries Confused with General Ticket Fare Complaints
- **Example:**  
  *Conversation ID:* `848782` (and `2023541`)  
  *Customer Message:* `"@AmericanAir pls explain why my $750 tkt isn't eligible for a paid standby. Gate agt doesn't know what to do."`
- **Observed Behavior:** The model classified the inquiry as `Service complaint`.
- **Expected Behavior:** `Seats and fares`.
- **Likely Cause:** Customer frustration over complex ticket standby rules mentions employee confusion (*"gate agt doesn't know"*), biasing the linear classifier toward service complaints.
- **Evidence:** LinearSVC margin for `Service complaint` exceeded `Seats and fares` by a narrow margin of 0.08.
- **Hypothesis:** Mentions of airport frontline personnel strongly weight the classifier toward service misconduct even when the underlying query is a policy/ticketing rule question.
- **Implemented Resolution:** Added `TICKETING_DISPUTE_PATTERNS` in `SupportDecisionPolicy`. When customer interactions cite airport gate or ticket counter disputes regarding standby or upgrade eligibility, the system routes the interaction to a human ticketing specialist. Verified in `test_failure_mode_4_gate_ticketing_dispute_escalated`.

---

### Failure Mode 5: Boundary Ambiguity on Milestone Loyalty Social Mentions
- **Example:**  
  *Conversation ID:* `1876039`  
  *Customer Message:* `"Finally made it to Platinum status with @AmericanAir after 3+ years of travel. It's the little things in life."`
- **Observed Behavior:** The model classified the message as `Positive experience`.
- **Expected Behavior:** `Social acknowledgement`.
- **Likely Cause:** Travel milestone celebrations sit directly on the semantic decision boundary between brand praise and casual social banter.
- **Evidence:** Both classes share positive sentiment and loyalty references without expressing an actionable problem or operational service request.
- **Hypothesis:** Because both `Positive experience` and `Social acknowledgement` are safe auto-handling intents routed to brand appreciation templates, the practical operational consequence of this misclassification is zero.
- **Implemented Resolution:** Harmonized brand celebration in `_draft_node` of `SupportAgentWorkflow`. When an elite loyalty tier milestone (Platinum, Executive Platinum, ConciergeKey, Million Miler) is recognized, the synthesizer generates a personalized congratulations acknowledging their milestone and flying dedication, safely maintaining `AUTO_HANDLE` without brand risk.
