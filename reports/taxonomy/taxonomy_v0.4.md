# Taxonomy v0.4 — Guidelines (evidence-mined from 300-pilot, 163 adjudications)

18 labels, unchanged set (no merge/split justified: top disagreement pairs are fallback-asymmetry with 70% adjudication for the specific side, not mutual confusion). What changed vs v0.3: ten explicit decision rules (R1–R10) + per-label tie-breaks. Each rule below cites the repeated pattern (n) that justifies it — no single-example rules.

## Decision rules

**R1 Disruption override.** If the tweeter asserts delay/cancellation/miss (late, waiting, cancelled, missed, rebook, voucher-after-disruption), never file as `flight_status_inquiry`, even if phrased as a question. Status is for undisturbed trips only. (Patterns: noise→status 13, missed→status 6, fee/failure/conduct/cancel→status 3 each; ADJ overturned B-status 32×.)
**R2 Rebooking priority.** Miss facts or rebook verbs ("miss/missed/will miss", "get me on another flight", "rebook", "stuck + new flight", change-cost-after-miss) beat delay/cancellation/status wording. 10/10 adjudicated. Consequence beats cause.
**R3 Complaint-specificity.** A named incident, denied help, or cost consequence beats `general_dissatisfaction_venting`. Mood without incident → venting. (venting↔failure 6, venting↔delay 6; ADJ split by incident presence.)
**R4 Status requires an ask.** Question word, explicit status/where/when/can-I, or check-in/schedule/policy request about own trip. Fragments, anecdotes, amenity observations → `other_non_actionable`. (noise↔status 13, ADJ 9 noise.)
**R5 Praise content + experience tests.** Praise = own flight/service experience + positive adjective (quote the noun). Policies/features, jokes, rituals, rants with pleasantries fail → thanks/noise. Sarcastic "praise" never praise. (thanks↔praise 4/4 split; noise↔praise 8.)
**R6 Money direction.** Quote the verb: "refund/give back" + paid ticket → `refund_request`; "charge/fee to change/use-half" → `change_fee_dispute`. Partial-flight repricing defaults fee. (fee↔refund 3, ADJ 3/3 verb-consistent.)
**R7 Seat-noun rule.** seat/seat#/row + assign/change/move/bump/gave-away about own booking → assignment; better-cabin/first/business/EP-list → upgrade; status talk/entertainment/one-word replies → noise. (noise→assignment 7, ADJ 5 noise.)
**R8 Bag rule.** Trace ("where is") → lost; arrived-broken → damaged; protest-of-process → gate-check. URL/photo shorts: open the thread before labeling; never infer from "[MENTION] [URL]" alone. (lost↔gate-check 2; 1068791 miss.)
**R9 Venting last resort with justification.** Choosing venting requires naming the rejected specific in rationale ("no delay/cancel/bag/seat/fee/staff words present"). 
**R10 OOD narrow + language.** OOD only for genuinely unrelated topics. Spanish/Portuguese → topical intent + lang note. Amenity observation without request → noise; with asserted failure + incident → failure.

## Per-label tie-breaks (condensed; full definitions carry over from v0.3 schema)

- flight_delay: tie vs venting → delay if any delay word + operating frame (even jokes); vs status → R1; vs missed → R2.
- flight_cancellation: tie vs delay → final-state rule (cancel asserted, incl. customer reclassification "it's not a delay its cancellation", wins); turnaround/return without deplanement → delay.
- missed_connection_rebooking: tie vs status → R2 (rebook-questions are never status).
- flight_status_inquiry: tie vs anything → loses to any R1 trigger; passenger-late-to-airport → status (check-in help), flight-late → delay.
- seat_assignment_change / seat_upgrade_request: cabin test (same = assign, better = upgrade); no seat noun → noise.
- baggage_delayed_lost / baggage_damaged / forced_gate_check_complaint: R8 chain.
- refund_request / change_fee_dispute: R6 verb quote.
- staff_conduct_complaint / service_failure_complaint: person+behavior-verb vs system-noun; terse denied-help without behavior words → failure (1611995).
- general_dissatisfaction_venting: R9 justification mandatory.
- positive_feedback_praise / other_acknowledgement_thanks / other_non_actionable: R5 content + experience tests.
- other_out_of_domain: R10 only.

## Labels unchanged in set; status per v0.3
KEEP 11, REDEFINE 4 (cancellation scope, status R1+R4, venting R9, thanks R5 — all wording, now encoded above), NEEDS_MORE_DATA 3 (damaged, upgrade, gate-check: definitions unchanged, retrieval-gated).

## Per-label prototypes / counterexamples (UIDs; full texts in `intent_prototypes_and_counterexamples.md`)

- flight_delay: proto 1068787, 274649 | counter 1149123 (→missed), 1524483 (→status)
- flight_cancellation: proto 1049522, 1077591 | counter 1084574 (→delay)
- missed_connection_rebooking: proto 1536525, 302409 | counter 2568639-type (→delay)
- flight_status_inquiry: proto 1028505, 230681 | counter 2589772 (→noise), 1271353 (→missed)
- seat_assignment_change: proto 1531567, 1388241-thread | counter 824204 (→upgrade), 1080625 (→noise)
- seat_upgrade_request: proto 2421023 | counter 1531567 (→assignment). Second slot: retrieval required.
- baggage_delayed_lost: proto 1280841, 1056893 | counter 2070647 (→gate-check)
- baggage_damaged: no clean agreed prototype in 300 (1236921 agreement-on-garbage noted) | counter 1906554-type (→lost). Retrieval mandatory.
- forced_gate_check_complaint: proto 2070647 | counter 2371549-type (→lost)
- refund_request: proto 1063345, 1600794 | counter 1533972 (→fee)
- change_fee_dispute: proto 2618696, 1544463 | counter 2959650 (→refund)
- staff_conduct_complaint: agreed 300-prototypes weak (1174919 URL-only); rests on C1/C9 + 1611995 counterexample (→failure)
- service_failure_complaint: proto 1856590, 2123351 | counter 1478500 (→venting)
- general_dissatisfaction_venting: proto 1076533, 1280839 | counter: any incident-naming message (→specific)
- positive_feedback_praise: proto 1013269, 1032851 | counter 2572581 (→noise), 1013272 (→thanks)
- other_acknowledgement_thanks: proto 1013272 | counter 2148629 (→praise)
- other_non_actionable: proto 1174481, 2139159 | counter 1289187 (still noise — context rule usually confirms noise)
- other_out_of_domain: proto 2586568 | counter: Spanish delays (→topical)
