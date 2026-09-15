# Taxonomy v1.0 (frozen; gold = 300 adjudicated model annotations standing in for human labels)
Set: 18 labels unchanged. Binding tie-breaks added from adjudication majorities:
- T1 noise vs venting: affect words (frustration/anger/profanity/displeasure at AA) -> venting (5/6 adjudicated); affect-free observation -> noise.
- T2 delay vs status: R1 + passenger-late->status / flight-late->delay / hold-plane->delay (adjudicated 3 status / 2 delay on the 5).
- T3 thanks vs noise: gratitude verb present ("thank/thanks/appreciate" + you/AA) -> thanks (3/5 adjudicated); else noise.
- T4 tails kept: baggage_damaged (damage-claim action; C10 evidence), seat_upgrade_request, forced_gate_check_complaint (adjudication-validated).
Gold file: gold_300.csv (137 agree + 163 adjudicated: A114/B43/BOTH_WRONG5+tie1). Limitation: gold inherits model biases; treat metrics as taxonomy-consistency estimates, not human-ground-truth performance.
