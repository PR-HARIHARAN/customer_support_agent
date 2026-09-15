# Taxonomy Pilot Report — 300-Message Automated Annotation Pilot

Schema: v0.1 (17 trained labels + 1 OOD-eval). Model: local Ollama qwen2.5:7b, temperature 0.1, batched 10/call with single-call retry for 110 parse failures. Labels are `proposed_intent` — NOT ground truth. No kappa (single agent). Seed 42.

## 1. Dataset Verification

- Source: `data/processed/customer_messages_with_candidate_intents_v1.jsonl` — **44,199 rows**, 44,199 unique `message_uid` (zero dup IDs), 26,388 unique `conversation_id`, `full_conversation` present on 100% rows.
- Embeddings: `data/faiss_customer_message/index.faiss` — ntotal 44,199, dim 768 (`nomic-embed-text`), uid list length 44,199, aligned 1:1 to JSONL order via `metadata.json:message_uids`.
- Coarse clusters: 12 (0:4158, 1:4358, 2:5752, 3:4250, 4:1353, 5:4063, 6:2325, 7:2889, 8:2021, 9:4847, 10:2816, 11:5367).
- Exact-duplicate normalized texts: 622 (1.4%) — dedup applied at sampling (text-level skip within central picks).
- Full conversation retrievable per message: yes (`full_conversation` + `conversation_id`).
- Original dataset unmodified. Pilot outputs isolated under `data/processed/experiments/` (formerly `data/processed/taxonomy_pilot_v1/`).


## 2. Final 300-Message Sample Composition

Exact n=300, deduplicated by message_uid. Strata (actual): central 108, boundary 72, random 43, cross_cluster 24, known_error 20, non_actionable 16, spanish 12, hard_negative_topup 5. (Random 43 vs 48 target: 5 slots yielded to force-include all 15 priority known-error IDs.)
Coarse coverage: 0:37, 1:24, 2:27, 3:26, 4:17, 5:17, 6:24, 7:20, 8:27, 9:26, 10:23, 11:32 — all 12 present, min 17.
All 15 priority known IDs included: 1536525, 1068791, 722238, 302409, 335333, 333727, 255701, 630138, 2394043, 2618696, 1531567, 890846, 296510, 725608, 1028505.
Spanish (detector: accented chars / es keywords): 26 messages in sample (12 targeted + 14 incidental). Pure-noise regex hits (<15 chars after stripping mentions/URLs): 41.
Every trained label appears ≥1 in sample; all 11 hard-negative pairs represented (see §5).

## 3. Annotation Results

Method: primary-goal rule (next-step action), single label + competing_label + confidence + rationale + hard_negative_pair + language per message. 190 via batched calls, 110 via single-call retry (100% retry success). Checkpointed, reproducible (seed 42, config in `pilot_sampling_config.json`).
Confidence (single-model, overconfidence expected — NOT agreement): high 283, medium 10, low 7.
Model `needs_review` flag fired 300/300 (prompt misread: model treated it as "pilot-reviewed"). **Discarded as signal; recomputed analytically** (low OR competing+below-median margin): ambiguous 68/300, low-confidence 7, competing-label present 139, negative centroid margin 108.
Spot-checks on known errors (evidence the primary-goal rule works automatically): 1536525→missed_connection_rebooking ✓ (cross-cluster fix), 722238→seat_assignment_change ✓ (fee→seat fix), 302409→missed_connection_rebooking ✓ (fee→miss fix), 890846→missed (delay+miss → miss) ✓, 630138 es-delay→flight_delay ✓, 255701 umbrella→flight_status_inquiry ✓, 1531567→seat_assignment_change ✓.
Model failures (kept as ambiguity evidence, §7): 1068791→other_non_actionable (competing baggage_delayed_lost; should be forced_gate_check), 335333→positive_feedback_praise/low (should be cancellation/status).

## 4. Class Distribution

| proposed_intent | n | % | main coarse sources |
|---|---|---|---|
| other_non_actionable | 60 | 20.0 | C8:14, C0:9, C3:10, C11:8, C4:6, C5:5 |
| flight_delay | 44 | 14.7 | C2:19, C0:4, C1:4, C11:6, C3:4 |
| positive_feedback_praise | 26 | 8.7 | C0:9, C5:6, C9:4, C3:3 |
| flight_status_inquiry | 26 | 8.7 | C11:7, C8:3, C0/C2/C4/C5/C10:2 each |
| missed_connection_rebooking | 22 | 7.3 | C11:4, C7:3, C10:3, C0/C2/C4/C5:2 each |
| service_failure_complaint | 19 | 6.3 | C9:8, C6:4, C3:2 |
| seat_assignment_change | 13 | 4.3 | C6:8 |
| staff_conduct_complaint | 13 | 4.3 | C9:5, C1:4 |
| general_dissatisfaction_venting | 12 | 4.0 | C1:5, C0:3, C3:2 |
| baggage_delayed_lost | 12 | 4.0 | C10:6 |
| refund_request | 11 | 3.7 | C7:3, C10:2, C11:2 |
| change_fee_dispute | 11 | 3.7 | C7:5, C1:2, C9:2 |
| seat_upgrade_request | 7 | 2.3 | C6:2, C0/C5/C7/C8/C9:1 each |
| forced_gate_check_complaint | 7 | 2.3 | C10:5, C6:1, C11:1 |
| flight_cancellation | 6 | 2.0 | C7:2, C0/C1/C2/C8:1 each, C11:0 |
| other_out_of_domain | 6 | 2.0 | C0:3, C3:2, C11:1 |
| other_acknowledgement_thanks | 4 | 1.3 | C8:3, C3:1 |
| baggage_damaged | 1 | 0.3 | C4:1 |

Thin/unsupported: baggage_damaged 1 (~150 projected), acknowledgement 4, cancellation 6 (and zero from C11's 32 sampled — under-assignment, §8), upgrade 7, gate-check 7. Cross-cluster spread is healthy: delay appears in 5 coarse clusters, missed in 6, status in 7 — contamination is signal (intents cut across clusters as designed).

## 5. Hard-Negative Analysis

Competing-label top pairs (second-best counts): delay→status 12, non_actionable→status 11, failure→status 8, non_actionable→praise 7, missed→delay 7, delay→cancel 6, assignment→status 5, fee→status 4. `flight_status_inquiry` is the top competing magnet (56) — heterogeneous-bucket warning (§8).
Centroid cosine top similarities (pilot-space, n small — directional only): delay↔missed 0.968, status↔missed 0.968, non_actionable↔praise 0.968, delay↔status 0.964, status↔non_actionable 0.963. All pairs >0.95: expected in 768-d Twitter-embedding space; separability must come from the goal rule, not geometry.
Per-pair verdicts: delay/missed — rule works (890846, 302409 correct; 7 miss→delay competings are genuine conditionals). delay/status — 12 competings, the known hot spot (2394043-type); guideline holds but needs the disruption-cue sentence emphasized. cancel/rebook — cancellation under-assigned (6 total); boundary leans rebook correctly per priority, but bare-cancel reports are being absorbed. assignment/upgrade — clean (no cross-competing in top list). lost/damaged — 1 damaged sample, no signal; keep on principle + oversample. lost/gate-check — 1068791 failure shows short-text+URL breaks the automated annotator; human rule (protest-words vs trace-words) is sharp, model execution weak. refund/fee — 2618696 correctly split with competing flagged; boundary learnable. conduct/failure — no top competing pair (clean). praise/acknowledgement — 7 noise→praise competings + C8 collapse (14 noise vs 3 thanks): automated boundary weak, human content-rule (§4.10) untested. venting→specific — no venting-as-competing excess; last-resort rule held (12 venting, all content-free on spot check).

## 6. Cross-Cluster Contamination

Expected and useful: proposed intents span coarse clusters (table §4). Strong fixes: 1536525 (C11 content in C10 shell) → missed ✓; 722238 (C6 seat in C7 shell) → assignment ✓; 302409 (C11 miss in C7/C11 shells) → missed ✓; 1068791 (C10 bag in C6 shell) → MISSED by model (→noise), confirming seat↔baggage boarding-context confusion is the top cross-cluster risk for humans too.
Reverse direction (coarse → proposed): C2→delay 19/27 (good precision anchor); C10→lost 6 + gate-check 5 (good recall split); C6→assignment 8/24 with 4→failure bleed (seat-comfort vs process-failure edge); C7→fee 5 + refund 3 + missed 3 (fee cluster is the most contaminated — change/miss/refund co-occur linguistically); C11→status 7 + delay 6 + missed 4 + noise 8 + cancel 0 (cancel shell is a mix, not a class). C8→noise 14 vs thanks 3: acknowledgement definition fails the automated test (see §8).

## 7. Ambiguous Cases

Analytic ambiguous 68 (low 7 + competing/below-median-margin). Full list in `pilot_ambiguous_top30.csv` (sorted low-confidence, small-margin first). Patterns: (a) status-magnet cases (neutral-vs-aggrieved tone, e.g. 2394043 check-in failure → status/competing failure); (b) waiver/policy hybrids (335333 hurricane waivers → praise/low, competing status; correct home is cancellation/status — guideline needs a waiver sentence); (c) short-text + URL/photo (1068791 → noise/competing lost; correct gate-check — annotators must open conversation context, rule: never label URL-only short texts without context); (d) sarcasm (296510 → noise; venting-vs-noise boundary needs the sarcasm sentence); (e) loyalty overlays (333727 delay+plat → praise; acceptable per overlay rule, but delay-competitors should note it).
Taxonomy clarification needed for (b) and (d) only; (a),(c),(e) are annotation-execution issues (context opening, rule emphasis), not missing labels.

## 8. Weak-Class Analysis

- **flight_status_inquiry** (26 + 56 competings): heterogeneous by construction (schedule/gate/check-in/policy) but all share "answer, don't fix" routing. Verdict: KEEP through human pilot; add waiver sentence (335333-type → status-or-cancel by disruption state) and disruption-cue override. Split only if human confusion with failure/delay exceeds 25% (§9).
- **service_failure_complaint** (19, competing magnet 8 as second-best): not swallowing — venting stayed at 12, conduct at 13, specifics intact. Broad-by-design holds. KEEP + guardrails.
- **general_dissatisfaction_venting** (12, all content-free on check): used sparingly (4%), not a fallback dump. KEEP as triage class with last-resort rule.
- **positive_feedback_praise** (26) vs acknowledgement (4) vs noise→praise competings (7): praise itself is solid (301666/1623720 patterns consistent); the WEAKNESS is acknowledgement collapsing into noise (C8 14→noise). Verdict: KEEP praise; acknowledgement NEEDS_MORE_DATA-or-MERGE decision gated on human pilot (if human pair-κ thanks-vs-noise <0.5 → merge into non_actionable).
- **seat_upgrade_request** (7, dispersed across 6 coarse clusters): thin but correctly dispersed (upgrade language travels) and never confused in competing pairs. KEEP + targeted top-up in human pilot (empty-F/pay-upgrade retrieval).
- **baggage_damaged** (1): no learnability signal in pilot. KEEP ON PRINCIPLE (damage-claim action differs; photos) + mandatory oversampling in human pilot (torn/broken/photo retrieval, ≥30 candidates); DROP only if human pilot still <10 after targeted retrieval.

## 9. Taxonomy Problems Found

1. Cancellation under-assignment (6/300, 0/32 from C11): guideline too narrow (bare reports absorbed into miss/delay) and/or automated-annotator bias. Guideline problem, not necessarily missing intent.
2. Acknowledgement-vs-noise collapse (C8 14→noise, 3→thanks): content rule ("[MENTION]/URL + nothing else") needs a context-opening mandate + examples. Guideline problem.
3. Status-magnet (56 competings): expected for an answer-not-fix bucket; monitor, not a failure yet. Insufficient evidence for split.
4. 1068791-type short+URL failures: execution problem (context not weighted); add "open thread before labeling URL/photo shorts" rule.
5. Sarcasm (296510-type): needs one guideline sentence (sarcastic praise → failure/venting by content, never praise).
6. Waiver/policy hybrids (335333-type): needs disruption-state sentence in status vs cancellation.
7. Spanish: NO problem found (25/26 topical) — confirms language≠OOD policy.
8. No evidence for any 19th+ intent; no message required a label outside the 18 (0 invented labels; fallbacks were parse failures, all recovered).

## 10. Recommended Taxonomy Changes

`current_label | change | evidence | confidence`

- flight_cancellation | NEEDS_MORE_DATA (broaden: bare-cancel reports explicitly in-scope; re-test in human pilot) | 6/300, 0/32 from C11 | medium
- baggage_damaged | NEEDS_MORE_DATA (targeted photo/damage retrieval, ≥30 candidates in human pilot) | 1/300 | high (thinness) / medium (keep rationale)
- other_acknowledgement_thanks | NEEDS_MORE_DATA (keep separate through human pilot; merge into other_non_actionable only if human pair-κ <0.5) | 4/300; C8 14→noise collapse | medium
- seat_upgrade_request | NEEDS_MORE_DATA (targeted empty-F/EP retrieval) | 7/300, clean but thin | medium
- forced_gate_check_complaint | NEEDS_MORE_DATA ( boarding-context retrieval; 1068791 execution fix) | 7/300 + 1 model miss | medium
- flight_status_inquiry | KEEP (add waiver + disruption-cue sentences) | 26 + magnet 56, no systematic misroute | medium
- All other 12 trained labels | KEEP | per-class evidence §4–§6 | medium–high
- other_out_of_domain | KEEP (eval-only) | 6, heterogeneous as designed | high
- No MERGE / SPLIT / RENAME / DROP executed on automated evidence alone.

## 11. Pilot Conclusion

The schema survived first contact: 0 messages required a 19th label; primary-goal priority resolved the flagship multi-issue cases (delay+miss, cancel+rebook, fee+seat) automatically; Spanish and cross-cluster contamination behaved as designed. Automated confidence is uninformative (283 high including 2 clear errors), but analytic ambiguity (139 competings, 108 negative margins, status-magnet 56) maps exactly onto the predicted hard pairs — i.e. the taxonomy's stated boundaries are where the data is actually confusing, which is the desired property of a stress test.
Blockers for scale: (a) cancellation definition too narrow for real traffic, (b) acknowledgement/noise boundary unproven, (c) three tails (damaged, upgrade, gate-check) below learnability evidence. All three are guideline-plus-sampling fixes, not redesigns — but they must be fixed before paying for 2,500 human labels.

## 12. Exact Next Step

Patch schema v0.1 → v0.2 with four guideline sentences (bare-cancel in-scope; thanks-vs-noise content+context rule; sarcasm rule; waiver disruption-state rule), then run the **300-message double-human pilot** (same 300 UIDs in `taxonomy_pilot_300.csv`, blind to proposed_intent, full thread shown, 20% overlap adjudicated, κ gate ≥0.65 + pair-confusion gates per protocol). Only on human gates passing: lock v1.0 and label the remaining 2,200.

### TAXONOMY STATUS

`NEEDS_TAXONOMY_REVISION`

Reason: automated pilot found no missing intent but proved three minor guideline/sampling defects (cancellation scope, acknowledgement/noise boundary, tail support) that must be patched and re-tested with human agreement before scale. Single next action: apply the four-sentence v0.2 patch and launch the 300-message double-human annotation pilot on these same 300 UIDs.
