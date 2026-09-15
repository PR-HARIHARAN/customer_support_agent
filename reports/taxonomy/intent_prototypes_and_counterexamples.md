# Prototypes & Counterexamples (from the 300-pilot; agreed cases only unless noted)

## flight_delay
Prototype: "seriously a two hour delay because you don't have a flight attendant?" (1068787, agreed).
Prototype: "Maintenance delay Orlando-Dallas, and maintenance delay Dallas-Austin" (274649, ADJ-confirmed).
Counterexample: "can you get me on another flight since this one isnt taking off" (1149123) — looks like delay ("not taking off") but is **missed_connection_rebooking** (explicit rebook verb wins).
Counterexample: "I'm running late to the airport for check-in… What can I do?" (1524483) — passenger-lateness, belongs to **flight_status_inquiry**.

## flight_cancellation
Prototype: "Sold me tix twice for flights they knew were canceled" (1049522, agreed).
Prototype: "After a 13.5hr delay, a cancellation while sleeping…" (1077591, ADJ-confirmed).
Counterexample: "delaying until the crew can't fly" (1084574) — apocalyptic delay language with no cancel assertion → **flight_delay**.

## missed_connection_rebooking
Prototype: "If I'm in flight to CLT and going to miss my connection by 30 minutes, will I be automatically rebooked?" (1536525, ADJ-confirmed).
Prototype: "Missed flight, my phone has died and I need to talk to an agent" (302409, ADJ-confirmed).
Counterexample: "my flight delayed 2+ hours, prob won't leave" (2568639-type) — still on original aircraft, no miss → **flight_delay**.

## flight_status_inquiry
Prototype: "At O'Hare and the line spans the entire terminal. Only one security gate open. How does this happen?" (1028505, agreed).
Prototype: "Touché. Seems to be major issues out of Hawaii and your online system has been down… Any updates?" (230681, ADJ-confirmed — no tweeter-asserted disruption).
Counterexample: "PHL to LAX flight without charger/entertainment… wow" (2589772) — looks like an amenity question but asserts no request → **other_non_actionable**.
Counterexample: "Why can't AA assist in rebooking codeshare…?" (1271353) — question form, but answer changes booking → **missed_connection_rebooking**.

## seat_assignment_change
Prototype: "AA just bumped seat for flight tonight from 5A to 20A… What gives?" (1531567, agreed).
Prototype: "Seat 6B was open… I am in 6C… $35 to move my friend" (1388241-thread, agreed).
Counterexample: "not allowed to PAY to upgrade… empty first class seat" (824204) — seat words but better-cabin goal → **seat_upgrade_request**.
Counterexample: loyalty/status talk ("buy up 116 miles… Vegas", 1080625) — status vocabulary, no seat ask → **other_non_actionable**.

## seat_upgrade_request
Prototype: "2:50 flight PBI… 5 people ahead of me on the upgrade list… Plat Exec…" (2421023, agreed).
Counterexample: same-cabin bump grievance (1531567) → **seat_assignment_change**. *Thin class: only 1 agreed prototype in 300; second slot requires targeted retrieval.*

## baggage_delayed_lost
Prototype: "I'd LOVE to know where my mom's GATE CHECKED WHEELCHAIR went. Didn't show up at LAX" (1280841, agreed).
Prototype: "I had never had baggage issues… like yesterday" + tracing thread (1056893, agreed).
Counterexample: "Super disappointed that you had me check luggage despite tons of space" (2070647) — bag words but protest-of-process → **forced_gate_check_complaint**.

## baggage_damaged
*No clean agreed prototype in the 300.* The single agreed case (1236921) is "[MENTION] [MENTION] [URL]" — agreement on garbage, not evidence. Prototype definition rests on C10 clustering evidence (torn/broken-bag reports) + adjudicator's lost-vs-damaged reasoning. Counterexample: any "where is my bag / 48h no clue" (1906554-type) → **baggage_delayed_lost**. *Targeted photo/damage retrieval mandatory before human pilot.*

## forced_gate_check_complaint
Prototype: "Super disappointed that you had me check luggage despite tons of space on plane" (2070647, agreed).
Counterexample: "my bag just got taken… please DM me, same bag I always fly with" (2371549-type, tracing goal) → **baggage_delayed_lost**.
Counterexample: "forced to check… overhead open" with only a joke and no protest (weak) → **other_non_actionable**.

## refund_request
Prototype: "I paid for upgraded seats, tray tables broken. Y can't you refund what I paid?" (1063345, agreed).
Prototype: "out $600 unless I'd like to spend $400 more" (1600794, agreed).
Counterexample: "pay MORE for half a flight… policy is flawed" without "refund me" (1533972) → **change_fee_dispute**.

## change_fee_dispute
Prototype: "missed my flight and you are going to charge me more than the flight costs to change it?" (2618696, agreed).
Prototype: "$200 change fee+fare diff" (1544463, agreed).
Counterexample: "won't give customers back their money" (2959650) — explicit money-back verb → **refund_request**.

## staff_conduct_complaint
*Weak agreed prototypes in the 300* (1174919 URL-only agreement; 1242383 "Boycott" — both content-free agreements, flagged as agreement-on-garbage). Operational definition rests on C1/C9 clustering + adjudicated manner-vs-outcome reasoning (1611995 "No one was accommodating" → failure, not conduct, is the informative counterexample: terse denied-help without behavior words stays failure).
Counterexample: "No one was accommodating" → **service_failure_complaint** (no behavior verb).

## service_failure_complaint
Prototype: "American Airlines app… froze twice" (1856590, agreed).
Prototype: "getting rid of group check-in… incredibly inconvenient for team travel" (2123351, agreed).
Counterexample: terminal "worse and worse… crowded… when is it over?" (1478500, ADJ venting) — diffuse mood, no incident → **general_dissatisfaction_venting**.
Counterexample: hotel filth with hairs in sheets via airline booking (1072410, ADJ failure) — named incident → failure, not venting.

## general_dissatisfaction_venting
Prototype: "I'll be going out of my way to never book with #AmericanAir again" (1076533, agreed).
Prototype: "y'all really fucked up… absolute worssst customer service" without incident (1280839, agreed).
Counterexample: any message naming an incident (delay hours, hotel filth, denied help) → the specific class, even if profane.

## positive_feedback_praise
Prototype: "Shoutout for great customer svc on the phone and at kiosk" (1013269, agreed).
Prototype: "Thank you Nannette & Laura. Outstanding service… re-qualify for EP" (1032851, agreed).
Counterexample: "thank you! I will fly your airline!" after political rant (2572581, ADJ noise) — pleasantry without experience content → **other_non_actionable**.
Counterexample: "thanks" bare (1013272) → **other_acknowledgement_thanks**.

## other_acknowledgement_thanks
Prototype: "[MENTION] thanks" (1013272, agreed).
Counterexample: "Nina… rockstar!! Super helpful, knowledgeable" (2148629, ADJ praise) — named person + adjectives → praise.

## other_non_actionable
Prototype: "Totally! On a side note, when are we having a chat?" (1174481, agreed).
Prototype: "[MENTION] Hey, just realized it's #WindowSeatWednesday!" (2139159, ADJ-confirmed).
Counterexample: "No. DFW to MSP." (1289187) — looks equally empty but thread shows reservation fragment; still noise (ADJ-confirmed), demonstrating the context-opening rule usually *confirms* noise rather than rescuing content.

## other_out_of_domain
Prototype: elephant-trophy/Trump-admin rant (2586568, agreed).
Counterexample: Spanish delay complaints → topical intents (language never OOD).
