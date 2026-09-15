# Boundary Cases — mined from 163 adjudicated disagreements (300-pilot)

Notation: A = qwen2.5:7b, B = llama3.2, ADJ = qwen3:8b adjudicator (investigational, not truth).

## noise vs status (13, 8.0% — largest pair; direction 13:0 A-noise/B-status; ADJ 9 A / 2 B / 2 wrong)

### Example 1 — 1289187 "No. DFW to MSP."
A noise / B status / ADJ noise(A). Bare route fragment, no verb, no request.
### Example 2 — 1701232 (es) "Ya les escribí por privado…" (sent flight data via DM)
A noise / B status / ADJ noise(A). Status update on the *support process*, not a flight-info request.
### Example 3 — 2442163 guitar/FAA anecdote + Thanks + URL
A noise / B status-policy / ADJ noise(A). Social storytelling with policy flavor, no ask.
### Example 4 — 2589772 "PHL to LAX flight without charger/entertainment… wow"
A noise-low / B status / ADJ noise(A). Amenity observation, no request, no failure asserted.

### Pattern discovered
B treats any travel noun (route, seat, guitar, charger) as a status inquiry. Adjudication sides with A 9/13: without a question word + actionable topic, there is no inquiry.
### Correct boundary rule
**Status requires an ask.** A question mark, explicit "status/where/when/can I", or a check-in/schedule/policy request about the tweeter's own trip. Fragments, anecdotes, amenity observations → noise. (v0.4 Rule R4+R1.)

## delay vs missed (10, 6.1% — direction 10:0 A-missed/B-delay; ADJ 10/10 A)

### Example 1 — 1126899 "seems like I'll miss my flight LAX→DFW… pay another $75?"
A missed / B delay / ADJ missed(A). Future-miss + cost cue.
### Example 2 — 1149123 "can you get me on another flight since this one isnt taking off"
A missed / B delay / ADJ missed(A). Explicit rebook verb; B anchored on "not taking off".
### Example 3 — 1521435 "30 min delay… caused me to miss my connecting flight"
A missed / B delay / ADJ missed(A). Cause (delay) vs consequence (miss): consequence wins.
### Example 4 — 1277359 "now we're changing planes!! Everyone deserves a voucher"
A missed / B delay / ADJ missed(A). Weakest of the four (no explicit miss); voucher-as-rebook inference held.

### Pattern discovered
Perfect 10/10 adjudication for the rebooking-priority rule: any miss (actual, imminent, or explicit rebook verb) outranks delay-reporting, even when delay wording dominates.
### Correct boundary rule
**Rebook verbs and miss facts beat delay words.** "miss/missed/will miss", "get me on another flight", "rebook", "stuck + new flight", "pay again/change fee after miss" → missed. Waiting on original aircraft with no miss → delay. (v0.4 Rule R2.)

## thanks vs praise (8, 4.9% — 7:1; ADJ 4 A / 4 B — genuinely balanced)

### Example 1 — 1103764 miles-donation thanks
A thanks / B praise / ADJ thanks(A). Gratitude for a *policy/feature*, no service/flight content.
### Example 2 — 2148629 "Nina… rockstar!! Super helpful, knowledgeable, great attitude"
A thanks(!) / B praise / ADJ praise(B). A under-called obvious praise — execution error.
### Example 3 — 2174393 boarding-groups praise + URL
A thanks / B praise / ADJ praise(B). Specific operational praise beats generic thanks frame.
### Example 4 — 2273750 ice-cream-sundae praise
A thanks / B praise / ADJ praise(B). "Wow… #toogoodforwords" + named service element = praise.

### Pattern discovered
Only pair where adjudication splits evenly: the boundary is real, not fallback. Decisive feature: **named service/flight noun + positive adjective** (Nina+rockstar/helpful; sundae+wow; boarding+working) → praise. Gratitude for policies/features/attention without service content → thanks.
### Correct boundary rule
**Content test.** Quote the praised noun: flight/crew/staff/desk/service/food + positive adjective → praise; else thanks. Sarcasm ("great way to lose water weight") never praise. (v0.4 Rule R5.)

## noise vs praise (8, 4.9% — 5:3; ADJ 4/4)

### Example 1 — 2123361 SkyHarbor joke ("Don't let [MENTION] know I'm flying with you… break up")
A noise / B praise ("great job today") / ADJ noise(A). Joke frame defeats embedded praise phrase.
### Example 2 — 2139159 "#WindowSeatWednesday!"
A praise(!) / B noise / ADJ noise(B). Hashtag ritual, no service content — A over-read.
### Example 3 — 2572581 elephant-trophy rant ending "thank you! I will fly your airline!"
A praise / B noise / ADJ noise(B). Political rant; closing pleasantry is not flight praise.
### Example 4 — 261892 fleet review ("mainline pretty great… regionals awful… CRJs solid")
A noise / B praise / ADJ praise(B). Mixed sentiment with specific praise → praise wins.

### Pattern discovered
Praise needs *service-experience* content, not any positive word: jokes, rituals, rants with pleasantries fail; mixed-sentiment reviews with specific praise pass.
### Correct boundary rule
**Experience test.** Praise = the tweeter's own flight/service experience described positively. Jokes, hashtags, politics, fleet punditry → noise unless tied to own experience. (v0.4 Rule R5.)

## noise vs assignment (7, 4.3% — 7:0 A-noise/B-assignment; ADJ 5 A / 2 B)

### Example 1 — 1080625 status/numbers loyalty talk ("buy up 116 miles for $50… Vegas")
A noise / B assignment / ADJ noise(A). Loyalty-program musing; B inferred seat intent from "status".
### Example 2 — 1388241 "best airline… real people…" (seat context in thread)
A noise→(ADJ praise! BOTH_WRONG-ish) / B assignment. Praise-with-context beats inferred seat ask.
### Example 3 — 1630672 "Ok"
A noise / B assignment (hallucinated Advantage-program question) / ADJ noise(A). B confabulated context — single-word messages must stay noise.
### Example 4 — 1644143 wireless-entertainment update request
A noise / B assignment / ADJ noise(A). "Update the entertainment" ≠ seat change; no seat noun at all.

### Pattern discovered
B infers seat intent from loyalty/status/travel vocabulary. Adjudication: a seat noun + change verb about the tweeter's seat is required.
### Correct boundary rule
**Seat-noun rule.** seat/seat#/row/upgrade-class + assign/change/move/bump/gave-away about own booking → assignment (or upgrade if better-cabin). Status talk, entertainment, one-word replies → noise. (v0.4 Rule R7.)

## venting vs failure (6, 3.7% — 5:1 A-failure/B-vent; ADJ 4 failure / 2 vent)

### Example 1 — 1072410 hotel horror (hairs in sheets, airline-provided hotel)
A failure / B vent / ADJ failure(A). Named outsourced-service failure with specifics.
### Example 2 — 1478500 terminal "worse and worse… crowded… when is it over?"
A failure / B vent / ADJ vent(B). Diffuse facility grumble, no incident.
### Example 3 — 1611995 "No one was accommodating. #disappointing"
A failure / B vent / ADJ failure(A). Denied assistance = process failure, even if terse.
### Example 4 — 1664944 "Rebooking is not the issue. Compensating for hotel… lack of communication is."
A vent(!) / B failure / ADJ failure(B). Communication-failure cause + cost consequence = failure.

### Pattern discovered
Specificity decides: named incident/denied-help/cost-consequence → failure (even terse); diffuse mood ("worse", "awful experience", no incident) → venting.
### Correct boundary rule
**Incident test.** Quote the incident: a thing that happened or was denied (hotel filth, no accommodation, no communication + cost) → failure. Mood without incident → venting. Rationale must quote it. (v0.4 Rules R3+R9.)

## status vs missed (6, 3.7% — 6:0 A-missed/B-status; ADJ 6/6 A)

### Examples — 1271353 codeshare rebook w/ miles; 1536525 auto-rebook if miss by 30 min; 2105174 "missed that connection"; 302409 LGA missed-flight + dead phone.
All A-missed/B-status, all adjudicated missed. B reads rebook questions as neutral info-seeking.
### Correct boundary rule
**Rebook-question rule.** Any question whose answer changes the tweeter's booking (auto-rebook? who rebooks codeshare? where is the agent after a miss?) → missed, never status. Status is for undisturbed trips only. (v0.4 Rules R1+R2.)

## delay vs venting (6, 3.7% — 6:0 A-delay/B-vent; ADJ 4 delay / 2 vent)

### Examples — 1354819 #stuckindallas maintenance (→delay); 1469656 5-hr-delay lemons joke (→delay); 1481607 silent gate, "Wonderful job AA…NOT" (→delay); 1029067 "not a pleasant experience… lost sense of time", no disruption named (→vent, B correct).
### Correct boundary rule
**Disruption-word rule.** A delay word with an operating-flight frame (late/waiting/tarmac/maintenance/hours + flight) → delay even if joking/sarcastic. Pure mood with no disruption noun → venting. (v0.4 Rules R1+R3.)

## delay vs status (5, 3.1% — 4:1; ADJ 4 status-side/A-labels… mixed)

### Examples — 1524483 "running late to airport for check-in" (A status wins: passenger-late ≠ flight-late); 230681 Hawaii system-down "Any updates?" (A status wins: no disruption asserted by tweeter); 274649 maintenance-delay report, sarcastic thanks (A delay wins); 2210178 "hold that plane" URL-only (B delay wins: hold-request = delay concern).
### Correct boundary rule
**Whose-lateness + assertion tests.** Passenger late to airport → status (check-in help), not delay. "Any updates?" with no tweeter-asserted disruption → status. Reported delay of own flight → delay even if phrased as question or sarcasm. Hold-the-plane → delay (miss only if rebook asked). (v0.4 Rule R1.)

## cancel vs delay (4, 2.5% — 3:1; ADJ 3 cancel-side… 2 cancel 1 delay + 1 delay)

### Examples — 1077591 13.5hr delay + cancellation while sleeping (→cancel: final state); 1084574 "delaying until crew can't fly" (→delay: no cancel asserted, B inferred); 1438719 turnaround for wrong luggage (→delay: returned flight = delay); 2653940 "12 hours delay it's not a delay its cancellation" (→cancel: customer reclassification wins).
### Correct boundary rule
**Final-state + assertion rules.** Cancel asserted ( cancelled/no pilots/won't operate/customer reclassifies) → cancel. "Delaying until X" without cancel assertion → delay. Turnaround/return → delay unless deplaned-cancelled. (v0.4 Rule R1.)

## fee vs refund (3, 1.8% — 2:1; ADJ 3/3 A: 2 fee, 1 refund)

### Examples — 1533972 pay-MORE-for-half-flight (A fee wins: policy/fee-structure dispute, no "refund me" verb); 2704435 $400 fees for half round-trip (A fee wins); 2959650 no-pilots "won't give customers back their money" (A refund wins: explicit money-back ask).
### Correct boundary rule
**Money-direction rule.** Quote the verb: "refund/give back" + paid ticket → refund; "charge/fee to change/use half" → fee. Partial-flight repricing grievances default fee unless "refund" is explicit. (v0.4 Rule R6.)
