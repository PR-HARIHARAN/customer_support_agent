# Taxonomy v0.4 Report — Evidence-Mined Rules + Controlled Re-evaluation

18 labels, same set throughout. v0.3 baseline: raw 45.7%, κ 0.410, 163 disagreements. v0.4: raw 50.7%, κ 0.447, 148 disagreements. NOT human-validated.

## 1. Current v0.3 diagnosis
v0.3's label set covered the data (0/463 annotations needed a new label) but four boundaries were soft (status-magnet, venting-fallback, cancellation scope, thanks/noise) and three tails unproven (damaged, upgrade, gate-check). Disagreement was 70% fallback-asymmetry (one model specific, other in status/venting/noise), adjudication favoring the detailed reader 114–43.

## 2. Evidence from existing 300 annotations
`taxonomy_error_matrix.csv` (59 pairs; top: noise↔status 13, delay↔missed 10, thanks↔praise 8, noise↔praise 8, noise↔assignment 7) and `label_stability.csv` (1 STABLE: flight_delay .507; 3 FALLBACK_BUCKET: noise .155, status .200, venting .306; 10 BOUNDARY_PROBLEM incl. missed .000 — B-dropout artifact; 3 UNDERREPRESENTED: upgrade, damaged, OOD). Asymmetries ≥6:0 in 8 of top 10 pairs, all B-toward-magnet. Adjudication: delay↔missed 10/10 missed; status↔missed 6/6 missed; noise↔status 9/13 noise; thanks↔praise 4/4 split (genuine boundary).

## 3. Top disagreement boundaries
(1) noise↔status — B reads travel nouns as inquiries; fix = R4 ask-requirement. (2) delay↔missed — B anchors delay words; fix = R2 rebook-priority (10/10). (3) thanks↔praise — even adjudication split; fix = R5 content test. (4) noise↔praise — joke/ritual/rant frames; fix = R5 experience test. (5) noise↔assignment — B infers seats from loyalty talk; fix = R7 seat-noun rule. Full mined examples: `boundary_cases.md`.

## 4. Label stability analysis
STABLE: flight_delay only. FALLBACK_BUCKET: noise (A-overuse, 18 overturns), status (B-overuse, 32 overturns), venting (B-overuse, 22 overturns) — all three legitimate buckets with unenforced entry rules, not structural duplicates. BOUNDARY_PROBLEM: 10 labels whose disagreements concentrate in the above magnets (all <0.5 rate but adjudication-validated when applied). UNDERREPRESENTED: upgrade (4 involved), damaged (2), OOD-eval (3) — no verdict possible; OOD stays eval-only by design.

## 5. Prototype/counterexample analysis
`intent_prototypes_and_counterexamples.md`: 15/18 labels have agreed high-confidence prototypes. Gaps found and flagged honestly: baggage_damaged's only agreed case is URL-only garbage (agreement-on-garbage); staff_conduct's agreed cases are content-free (URL-only, "Boycott") — conduct definition rests on clustering + adjudicated manner-vs-outcome reasoning, not on clean 300-prototypes. Praise/thanks/noise triplets now have quote-the-noun counterexamples.

## 6. New decision rules (R1–R10, each justified by ≥3-case repeated patterns; see `taxonomy_v0.4.md`)
R1 disruption override; R2 rebooking priority; R3 complaint-specificity; R4 status-requires-ask; R5 praise content/experience tests + sarcasm bar; R6 money-direction verb quote; R7 seat-noun rule; R8 bag chain + thread-opening mandate; R9 venting justification mandate; R10 narrow OOD + language rule. No single-example rules; no splits/merges (top pairs are asymmetry, adjudication validates the specific side).

## 7. v0.3 vs v0.4 agreement (`v03_vs_v04.csv`)
Overall: 45.7%→50.7%, κ 0.410→0.447 (+0.037), 163→148 (−15). Improved: delay↔missed 10→2, status↔missed 6→1, noise↔status 13→8, noise↔assignment 7→2, thanks↔praise 8→4, noise↔praise 8→~4, failure↔venting stable. Regressed: venting↔noise 6→15, delay↔status 5→9, missed↔noise 0→5, gate-check↔noise 0→4, thanks↔noise 5→7, damaged-scatter (0→1 ×4 pairs; A damaged 2→8 over-filing). Unchanged: failure↔venting 6→6, cancel↔missed 1→1, conduct↔failure 1→1.
Reading: R1/R2/R4/R5/R7 fixed the targeted directional fallbacks (status-magnet drained: B status 53→46, A-missed→? no—) but both models grew more conservative on disruption claims (delay involved 69→36; A missed 18→3; B delay 61→20) and diverged on *which* fallback bucket to use (A→noise 73, B→venting 70). Rules sharpened the specific classes but did not harmonize the no-ask zone.

## 8. Labels changed
Set: none (18→18). Wording: 4 REDEFINEs encoded as R1/R4 (status), R9 (venting), R5 (thanks/praise/noise), cancellation scope. NEEDS_MORE_DATA stands for damaged/upgrade/gate-check (damaged now has an over-filing warning: A 8 vs agreed 1).

## 9. Labels unchanged
11 KEEP (delay, missed, assignment, lost, refund, fee, conduct, failure, praise, noise, OOD-eval) with new tie-breaks only.

## 10. Remaining unresolved boundaries
(a) noise↔venting (15, the new top pair): R4 and R9 pull opposite ways on mood-without-incident travel talk — needs a human tie-break (incident-adjacent grumble: venting; pure observation: noise). (b) delay↔status (9): passenger-late vs flight-late vs hold-requests still split models. (c) thanks↔noise (7): bare-thanks-with-mentions/URL. (d) tails: damaged over-filing vs under-evidence; upgrade/gate-check still <10 agreed. (e) B-model coarseness persists (failure 7→1: B nearly abandoned the class under v0.4).

## 11. Recommended next step
Freeze v0.4 + run the **double-human 300-UID pilot** with explicit orders: (i) report pair-κ for noise↔venting, delay↔status, thanks↔noise; (ii) targeted retrieval top-ups (damaged photos, upgrade lists, gate-check protests, bare cancels, Spanish) ≥30 candidates each before the support verdict; (iii) apply §9 change gates (merge only on >25% human confusion + shared routing; split only on ≥15% + distinct action + ≥300 projected). Do not train, do not label 43,899, do not split/merge on model evidence.
