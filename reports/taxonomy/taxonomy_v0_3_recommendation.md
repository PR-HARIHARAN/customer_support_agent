# Taxonomy v0.3 Recommendation (post two-model pilot)

Basis: 300-message pilot, Annotator A (qwen2.5:7b) vs B (llama3.2), κ=0.410, 163 adjudicated (A114/B43/wrong5). All decisions model-evidenced only — human pilot still required. No label added (0/463 annotations needed one).

| label | decision | evidence | confidence |
|---|---|---|---|
| flight_delay | KEEP | 35 agreed, R .814, rule wins adjudications | high |
| flight_cancellation | REDEFINE (broaden: bare-cancel reports explicitly in-scope) | 6 pilot / A12 vs B4, 0/32 from C11 | medium |
| missed_connection_rebooking | KEEP | A18 + adjudication wins; B-dropout is model artifact | high |
| flight_status_inquiry | REDEFINE (disruption-cue override + waiver sentence) | magnet: B53, 56 competings; pair rates <25% | medium |
| seat_assignment_change | KEEP | 6 agreed; B finer-splits seat mentions (18) without harm | medium |
| seat_upgrade_request | NEEDS_MORE_DATA (targeted empty-F/EP retrieval, ≥30 cands) | A2/B3, clean but thin | medium |
| baggage_delayed_lost | KEEP | 7 agreed, P/R .636 | medium-high |
| baggage_damaged | NEEDS_MORE_DATA (photo/damage retrieval, ≥30 cands; drop if <10 after retrieval) | A2/B1/pilot1 | high (thinness) |
| forced_gate_check_complaint | NEEDS_MORE_DATA (boarding-context retrieval; add URL/context-opening rule) | A10 vs B1 + 1068791 miss | medium |
| refund_request | KEEP | 7 agreed, P .538 R .583 | medium |
| change_fee_dispute | KEEP | thin (B4/A13) but rule holds (2618696-type) | medium |
| staff_conduct_complaint | KEEP | 8 agreed, pair rate .028 | medium-high |
| service_failure_complaint | KEEP | 3 agreed is low but misses are status-ward (guideline, not structure) | medium |
| general_dissatisfaction_venting | REDEFINE (rationale must name rejected specific; adjudicators overturn loose vents) | B48 vs A16 fallback asymmetry | medium |
| positive_feedback_praise | KEEP | 14 agreed | medium-high |
| other_acknowledgement_thanks | REDEFINE (content+context rule; merge into non_actionable only if human pair-κ <0.5) | pair rate .133, C8 collapse persists | medium |
| other_non_actionable | KEEP | largest bucket, high-recall anchor for abstention | high |
| other_out_of_domain | KEEP (eval-only) | 1–6, heterogeneous as designed | high |

- **Labels kept:** 11 (delay, missed, assignment, lost, refund, fee, conduct, failure, praise, noise, OOD-eval).
- **Labels redefined (wording only):** 4 (cancellation, status, venting, thanks boundary).
- **Labels merged:** 0. **Labels split:** 0. **Labels demoted:** 0.
- **Unresolved boundaries (human pilot must decide):** thanks-vs-noise (merge gate: human pair-κ <0.5), cancellation scope (does broadening recover C11 bare reports?), status heterogeneity (split gate: human confusion >25% with failure/delay), tails (damaged/upgrade/gate-check support counts).
