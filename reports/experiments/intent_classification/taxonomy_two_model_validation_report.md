# Two-Model Validation Report — 300-Message Pilot (v0.2 schema)

Models: Annotator A `qwen2.5:7b` temp 0.1; Annotator B `llama3.2:latest` temp 0.2; adjudicator `qwen3:8b` temp 0.1.
Same 300 UIDs as `taxonomy_pilot_300.csv`. Neither annotator saw clusters, strata, or each other's outputs.
**Two-model agreement is a proxy stress test, not human ground truth.**

## 1. Executive Summary

- **Model agreement (measured):** raw 0.457, Cohen's κ **0.410** (137/300 agree, 163 disagree) → **Poor band** (<0.50): taxonomy needs substantial revision *or* the disagreement is model-behavioral. Evidence below shows it is substantially both: real boundary weaknesses (status-magnet, venting-fallback, cancellation scope, thanks/noise) **plus** large annotator-model biases (B never emits `missed_connection_rebooking` (0 vs A's 18), B routes 48 to venting vs A's 16, B claims high confidence on all 300).
- **Human agreement (not measured):** unknown. Nothing here transfers numerically to human κ.
- **Taxonomy quality:** no message required a 19th label (adjudicator's 5 BOTH_WRONG all resolved into existing labels, 4→venting, 1→assignment). The label *set* covers the data; the *boundaries* (status, venting, cancellation-vs-rebooking, thanks-vs-noise) need redefinition, not redesign.
- **Uncertainty:** single-model confidence is uninformative (A 284 high, B 300 high); adjudicator is investigational only (same-model-family overlap: adjudicator shares no family with either annotator — qwen3 vs qwen2.5/llama — but remains a model). Tails (damaged n≈1–2, OOD n≈1–3) have no statistical signal either way.

## 2. Annotator A Results (qwen2.5:7b)

Distribution (300): non_actionable 53, delay 43, praise 23, thanks 23, status 19, missed 18, venting 16, failure 15, conduct 14, fee 13, cancel 12, refund 12, lost 11, assignment 11, gate-check 10, OOD 3, damaged 2, upgrade 2. Confidence: high 284 / medium 7 / low 9; needs_review 1.
Profile: balanced across all 18 labels; uses missed (18), gate-check (10), fee (13); heaviest noise-bucket user (53). Closest to the pilot single-annotator distribution, as expected (same family, refined prompt).

## 3. Annotator B Results (llama3.2)

Distribution: delay 61, status 53, venting 48, praise 29, thanks 20, assignment 18, noise 14, refund 13, conduct 12, lost 11, failure 7, cancel 4, fee 4, upgrade 3, damaged 1, gate-check 1, OOD 1, **missed 0**. Confidence: high 300/300. needs_review 0.
Profile biases (systematic, not message-specific): (a) never emits missed_connection_rebooking — rebooking cases leak to delay/status/venting; (b) venting as fallback (48 vs 16); (c) status as magnet (53 vs 19); (d) near-zero tail usage (gate-check 1, fee 4, cancel 4); (e) total confidence compression (all-high). B reads as a coarser annotator operating at ~12 effective labels.

## 4. Two-Model Agreement

- Agree 137/300 (45.7%), disagree 163/300 (54.3%). Files: `taxonomy_pilot_annotator_A.csv`, `taxonomy_pilot_annotator_B.csv`, `taxonomy_pilot_two_model_agreement.csv`, `two_model_confusion_matrix.csv`, `two_model_per_class.csv`.
- Disagreement pre-tags: hard-negative-pair  (pair-listed), venting-fallback-suspect, model-reasoning (cross-competing), unclassified; all refined by adjudication (§8).

## 5. Cohen's Kappa

κ = **0.410** (sklearn, 18 labels, n=300) → **Poor** (<0.50) gate band. Diagnostic only: with B using 17 effective labels and all-high confidence, κ measures a mix of taxonomy ambiguity and B's fallback behavior. Do NOT read as "humans would score 0.41". The actionable decomposition is per-class (§6) and per-pair (§7), not the single number.

## 6. Per-Class Agreement

(highest → lowest agreed counts; P = agreed/B_n, R = agreed/A_n)
- delay 35 (B61/A43, P .574 R .814) — most stable actionable class.
- venting 15 (B48/A16, P .312 R .938) — A rarely vents; B vents constantly: fallback asymmetry, not boundary merit.
- praise 14 (B29/A23), thanks 13 (B20/A23) — moderate; cross-pair 8 (see §7).
- status 12 (B53/A19, P .226 R .632) — B over-assigns; A under-assigns: magnet confirmed both directions.
- noise 9 (B14/A53, P .643 R .170) — mirror of status: A dumps ambiguous into noise, B into status/venting.
- conduct 8, lost 7, refund 7, assignment 6 (B18/A11: B splits seat mentions finer), failure 3 (B7/A15), fee 2 (B4/A13), cancel 2 (B4/A12), upgrade 1, damaged 1, gate-check 1 (B1/A10), OOD 1, **missed 0 (B0/A18)** — complete single-model dropout, the strongest model-bias artifact in the pilot.

## 7. Hard-Negative Confusion

Disagreements (bidirectional) / involved / rate:
- praise↔thanks 8/60 .133 — worst rate; short-thanks boundary unresolved (§9).
- delay↔missed 10/77 .130 — driven by B's missed-dropout (B side contributes ~all); A-side rule validated by adjudication (A wins most).
- refund↔fee 3/30 .100 — genuine (2618696-type); low count, rule holds.
- lost↔gate-check 2/23 .087 — includes 1068791 (A noise vs B lost; adjudicator needed); short+URL fragility confirmed.
- lost↔damaged 1/16 .062 — no signal; principle-keep stands.
- delay↔cancel 4/79 .051; delay↔status 5/124 .040; assignment↔upgrade 1/26 .038; cancel↔missed 1/31 .032; conduct↔failure 1/36 .028 — all below the 25% gate. No pair breaches the bidirectional-confusion threshold on model evidence; the status/venting *magnet* problem shows in marginals (§6), not pair rates.

## 8. Adjudicated Disagreements (163, qwen3:8b, investigational)

Winners: A 114 / B 43 / BOTH_WRONG 5 / tie 1. A wins ~70%: the v0.2-detailed prompt (qwen2.5) beats the coarser reader; B's wins cluster where A over-filed noise (A-noise 53) and B chose status/praise correctly.
BOTH_WRONG (5, all resolved inside taxonomy): 1349666 seat-size/upgrade-refusal → assignment (neither caught the seat thrust); 1841796 hashtags/frustration → venting; 2445440 grief/close-accounts → venting; 2763820 first-class amenities (no TV/ports) → venting (notes: no cabin-comfort label — supports keeping comfort inside venting/failure, §10); 687147 amenities/lighting → venting (B said status — confirms status-magnet overreach).
Top adjudicator-noted issues: venting-vs-failure ambiguity (3), fee-vs-status, seat-vs-status, delay-vs-cancel wording ("delaying until crew can't fly"), thanks-vs-praise with no content, delay-vs-rebooking. No adjudication proposed a new label.

## 9. Taxonomy Weaknesses

1. **Status-magnet** — B files 53 here; 56 pilot competings pointed here. Heterogeneous (schedule/gate/check-in/policy/facility) but single-desk ("answer, don't fix") holds. REDEFINE (tighten disruption-cue override + waiver sentence), not split.
2. **Venting-fallback asymmetry** — B 48 vs A 16. Last-resort rule works for a careful reader, fails for a coarse one. REDEFINE (require naming the rejected specific in rationale; adjudicators overturned most B-vents).
3. **Cancellation scope** — A 12 / B 4 / pilot 6, zero from C11's 32 in pilot. Bare-cancel reports absorbed into miss/delay. REDEFINE (bare reports explicitly in-scope, per v0.2 patch — patch partially worked for A only).
4. **Thanks-vs-noise** — pair rate .133, worst; C8 collapse persists across all three model runs. REDEFINE with context-opening mandate; merge gated on human pair-κ.
5. **Missed-dropout (B)** — model artifact, not taxonomy: A's 18 missed + adjudication wins validate the class. No taxonomy action; human pilot must confirm.
6. **Tails** — damaged (A2/B1), upgrade (A2/B3), gate-check (A10/B1), OOD (A3/B1): directionally present, statistically unproven. NEEDS_MORE_DATA stands.

## 10. Recommended Taxonomy Changes

`label | decision | evidence | confidence` — full table in `taxonomy_v0_3_recommendation.md`. Summary: 11 KEEP, 4 REDEFINE (status, venting, cancellation, thanks/noise boundary), 0 MERGE, 0 SPLIT, 0 demoted, 3 NEEDS_MORE_DATA (damaged, upgrade, gate-check), OOD KEEP eval-only. No change executed on model evidence alone beyond guideline wording.

## 11. Final Decision

Taxonomy set covers the data (0/463 annotations across three models required a new label); boundaries need word-level patches, not restructuring. Model κ 0.410 reflects coarse-reader fallback behavior + four known soft boundaries, with adjudication favoring the detailed reader 114–43. Proceed to humans, do not relabel at scale, do not train.

## 12. Next Step

Freeze **schema v0.3** (v0.2 + four patched sentences + rationale-must-name-rejected-specific rule), then run the **300-message double-human pilot on these same UIDs**, blind, full-thread, κ ≥ 0.65 + pair gates (thanks-vs-noise pair-κ reported separately; tails oversampled ≥30 candidates each via targeted retrieval). Only on human gates: lock v1.0 → label remaining 2,200 → train/val/test.
