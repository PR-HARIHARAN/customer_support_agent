# Fine-grained intent discovery (per coarse cluster)

Clusters: 12 | samples/cluster: 15 representative + 10 boundary | Granularity target: PolyAI/Banking77.

## Cluster 0 — General Query
*Coarse sub-intent:* General chat / social engagement | *Size:* 4158 | *Keywords:* url, great, mention mention, home, club, today, happy, thanks, love, thank mention

### Proposed sub-intents
- `thank_you` — Expressing gratitude or appreciation to the airline.
  - e.g. _thank you_
  - e.g. _thanks for_
  - e.g. _thank you for the upgrade_
- `flight_confirmation` — Confirming or checking the details of a flight.
  - e.g. _flight tonight_
  - e.g. _flight next week_
  - e.g. _flight home_
- `upgrade_confirmation` — Acknowledging or confirming an upgrade received or expected.
  - e.g. _upgrade message_
  - e.g. _upgrade for my trip_
  - e.g. _upgrade to first class_
- `travel_satisfaction` — Expressing satisfaction or happiness about a recent or upcoming travel experience.
  - e.g. _looking forward to_
  - e.g. _smooth travel day_
  - e.g. _wishing you a great descent_
- `social_engagement` — Engaging in social media interactions, such as following or liking the airline’s posts.
  - e.g. _following you_
  - e.g. _reading your tweets_
  - e.g. _good luck with_
- `loyalty_program` — Inquiring or expressing appreciation for loyalty program benefits or status.
  - e.g. _AA club_
  - e.g. _loyalty program_
  - e.g. _executive platinum_

### Query mapping (25)
- **R1** `987894` → `thank_you` (high) — 
- **R2** `341074` → `upgrade_confirmation` (high) — 
- **R3** `404231` → `flight_confirmation` (high) — 
- **R4** `1644163` → `flight_confirmation` (high) — 
- **R5** `2487507` → `social_engagement` (high) — 
- **R6** `2114307` → `flight_confirmation` (high) — 
- **R7** `485725` → `thank_you` (high) — 
- **R8** `699775` → `thank_you` (high) — 
- **R9** `818342` → `thank_you` (high) — 
- **R10** `368419` → `social_engagement` (high) — 
- **R11** `1238364` → `upgrade_confirmation` (high) — 
- **R12** `335333` → `social_engagement` (high) — 
- **R13** `388618` → `social_engagement` (high) — 
- **R14** `609879` → `travel_satisfaction` (high) — 
- **R15** `2606787` → `flight_confirmation` (high) — 
- **B1** `720344` → `out_of_distribution_noise` (low) 🚩 — Spanish language, not related to American Airlines support
- **B2** `1460833` → `out_of_distribution_noise` (low) 🚩 — Spanish language, not related to American Airlines support
- **B3** `2786842` → `out_of_distribution_noise` (low) 🚩 — Spanish language, not related to American Airlines support
- **B4** `2595685` → `out_of_distribution_noise` (low) 🚩 — Spanish language, not related to American Airlines support
- **B5** `1582345` → `out_of_distribution_noise` (low) 🚩 — Spanish language, not related to American Airlines support
- **B6** `906726` → `out_of_distribution_noise` (low) 🚩 — Complaint about food, not related to American Airlines support
- **B7** `2692175` → `out_of_distribution_noise` (low) 🚩 — Spanish language, not related to American Airlines support
- **B8** `1287152` → `out_of_distribution_noise` (low) 🚩 — Complaint about food, not related to American Airlines support
- **B9** `178304` → `out_of_distribution_noise` (low) 🚩 — Information about visa, not related to American Airlines support
- **B10** `1440819` → `out_of_distribution_noise` (low) 🚩 — Complaint about service, not related to American Airlines support

### Recommendation: **KEEP**
The proposed sub-intents are mutually exclusive and cover the representative queries effectively. The boundary queries are clearly out of distribution or not related to support queries.

### Edge cases
- flight_confirmation vs upgrade_confirmation
- thank_you vs social_engagement
- travel_satisfaction vs flight_confirmation

---

## Cluster 1 — Negative Feedback
*Coarse sub-intent:* Complaint / Dissatisfaction | *Size:* 4358 | *Keywords:* worst, airline, service, flight, customer, fly, customer service, airlines, rude, experience

### Proposed sub-intents
- `rude_flight_attendants` — Complaints about the behavior or attitude of flight attendants.
  - e.g. _rude flight crew_
  - e.g. _rude attendants_
  - e.g. _poor customer service_
- `long_delays` — Complaints about delays that significantly impact the customer’s travel plans.
  - e.g. _5 hours after scheduled arrival_
  - e.g. _missed connection_
  - e.g. _3.5 more hours wait_
- `poor_customer_service` — General dissatisfaction with the overall customer service provided by the airline.
  - e.g. _horrible customer service_
  - e.g. _appalling customer service_
  - e.g. _non-existent customer service_
- `flight_experience` — Complaints about the overall flight experience, including issues with the plane, food, or service.
  - e.g. _worst flight experience_
  - e.g. _horrible flight experience_
  - e.g. _wasted more than enough of my time and money_

### Query mapping (25)
- **R1** `2633492` → `rude_flight_attendants` (high) — 
- **R2** `2873860` → `poor_customer_service` (high) — 
- **R3** `707019` → `poor_customer_service` (high) — 
- **R4** `223198` → `poor_customer_service` (high) — 
- **R5** `2394043` → `rude_flight_attendants` (high) — 
- **R6** `1141245` → `poor_customer_service` (high) — 
- **R7** `2268182` → `poor_customer_service` (high) — 
- **R8** `303689` → `rude_flight_attendants` (high) — 
- **R9** `306332` → `rude_flight_attendants` (high) — 
- **R10** `1827558` → `rude_flight_attendants` (high) — 
- **R11** `321469` → `poor_customer_service` (high) — 
- **R12** `1186657` → `poor_customer_service` (high) — 
- **R13** `1178223` → `poor_customer_service` (high) — 
- **R14** `2846668` → `poor_customer_service` (high) — 
- **R15** `2364986` → `poor_customer_service` (high) — 
- **B1** `725608` → `out_of_distribution_noise` (low) 🚩 — 
- **B2** `677783` → `out_of_distribution_noise` (low) 🚩 — 
- **B3** `1393608` → `out_of_distribution_noise` (low) 🚩 — 
- **B4** `1036878` → `out_of_distribution_noise` (low) 🚩 — 
- **B5** `368013` → `out_of_distribution_noise` (low) 🚩 — 
- **B6** `1102489` → `out_of_distribution_noise` (low) 🚩 — 
- **B7** `2901312` → `out_of_distribution_noise` (low) 🚩 — 
- **B8** `1571202` → `out_of_distribution_noise` (low) 🚩 — 
- **B9** `1180798` → `out_of_distribution_noise` (low) 🚩 — 
- **B10** `548816` → `out_of_distribution_noise` (low) 🚩 — 

### Recommendation: **KEEP**
The proposed sub-intents cover the representative queries effectively and are mutually exclusive. The queries map clearly to these intents without overlap.

### Edge cases
- rude_flight_attendants vs poor_customer_service
- long_delays vs flight_experience

---

## Cluster 2 — Flight Delay
*Coarse sub-intent:* Delayed flight | *Size:* 5752 | *Keywords:* delayed, delay, flight, hours, hour, minutes, plane, waiting, late, flight delayed

### Proposed sub-intents
- `flight_delay_announcement` — Notification of a flight delay.
  - e.g. _my flight is delayed_
  - e.g. _flight delayed_
- `flight_delay_duration` — Complaint or inquiry about the duration of a flight delay.
  - e.g. _delayed for more than two hours_
  - e.g. _waiting for another hour_
- `flight_delay_impact` — Concern about the impact of a flight delay, such as missing a connecting flight.
  - e.g. _missed my connecting flight_
  - e.g. _have to wait 6 hours_
- `flight_delay_reason` — Request for the reason behind a flight delay.
  - e.g. _why is my flight getting delayed_
  - e.g. _delayed because of maintenance_

### Query mapping (25)
- **R1** `2568639` → `flight_delay_duration` (high) — 
- **R2** `333727` → `out_of_distribution_noise` (low) 🚩 — 
- **R3** `2279125` → `flight_delay_impact` (high) — 
- **R4** `638090` → `flight_delay_reason` (high) — 
- **R5** `1468073` → `flight_delay_reason` (high) — 
- **R6** `1185986` → `flight_delay_impact` (high) — 
- **R7** `890846` → `flight_delay_impact` (high) — 
- **R8** `597457` → `flight_delay_duration` (high) — 
- **R9** `299179` → `flight_delay_reason` (high) — 
- **R10** `877945` → `flight_delay_duration` (high) — 
- **R11** `2644447` → `flight_delay_reason` (high) — 
- **R12** `1292286` → `flight_delay_duration` (high) — 
- **R13** `773759` → `flight_delay_reason` (high) — 
- **R14** `893612` → `flight_delay_reason` (high) — 
- **R15** `2708056` → `flight_delay_reason` (high) — 
- **B1** `1028505` → `out_of_distribution_noise` (low) 🚩 — 
- **B2** `866805` → `out_of_distribution_noise` (low) 🚩 — 
- **B3** `892701` → `out_of_distribution_noise` (low) 🚩 — 
- **B4** `305972` → `out_of_distribution_noise` (low) 🚩 — 
- **B5** `892396` → `out_of_distribution_noise` (low) 🚩 — 
- **B6** `1493871` → `out_of_distribution_noise` (low) 🚩 — 
- **B7** `2681927` → `out_of_distribution_noise` (low) 🚩 — 
- **B8** `1772044` → `out_of_distribution_noise` (low) 🚩 — 
- **B9** `2443447` → `out_of_distribution_noise` (low) 🚩 — 
- **B10** `2983876` → `out_of_distribution_noise` (low) 🚩 — 

### Recommendation: **SPLIT**
The proposed sub-intents are mutually exclusive and cover the various aspects of flight delays, ensuring that each intent is specific and actionable.

### Edge cases
- flight_delay_reason vs flight_delay_announcement
- flight_delay_duration vs flight_delay_impact
- flight_delay_reason vs out_of_distribution_noise

---

## Cluster 3 — No Feedback
*Coarse sub-intent:*  | *Size:* 4250 | *Keywords:* mention, mention mention, mention lol, lol, mention don, mention did, mention dm, locator, mention ok, mention yes

### Proposed sub-intents
- `mention_confirmation` — Customer mentions a service or product without seeking specific assistance.
  - e.g. _mention_
  - e.g. _mention mention_
  - e.g. _mention lol_
- `mention_request` — Customer mentions a service or product and requests further information or assistance.
  - e.g. _mention did_
  - e.g. _mention dm_
  - e.g. _mention ok_

### Query mapping (25)
- **R1** `1237731` → `mention_confirmation` (high) — 
- **R2** `1391935` → `mention_confirmation` (high) — 
- **R3** `499432` → `mention_confirmation` (high) — 
- **R4** `716679` → `mention_confirmation` (high) — 
- **R5** `1090026` → `mention_confirmation` (high) — 
- **R6** `2292981` → `mention_confirmation` (high) — 
- **R7** `50243` → `mention_confirmation` (high) — 
- **R8** `1880900` → `mention_confirmation` (medium) — 
- **R9** `1425841` → `mention_confirmation` (high) — 
- **R10** `2773615` → `mention_confirmation` (high) — 
- **R11** `1841796` → `mention_confirmation` (medium) — 
- **R12** `1655274` → `mention_confirmation` (medium) — 
- **R13** `2551485` → `mention_confirmation` (medium) — 
- **R14** `475765` → `mention_confirmation` (medium) — 
- **R15** `2560644` → `mention_confirmation` (medium) — 
- **B1** `1290563` → `out_of_distribution_noise` (low) 🚩 — Spanish mention, not English
- **B2** `1664119` → `out_of_distribution_noise` (low) 🚩 — Salad joke, not a support query
- **B3** `1089018` → `out_of_distribution_noise` (low) 🚩 — Celebrity speculation, not a support query
- **B4** `809534` → `out_of_distribution_noise` (low) 🚩 — Fashion complaint, not a support query
- **B5** `1321794` → `out_of_distribution_noise` (low) 🚩 — Racial discrimination question, not a support query
- **B6** `1753652` → `out_of_distribution_noise` (low) 🚩 — Food complaint, not a support query
- **B7** `391847` → `out_of_distribution_noise` (low) 🚩 — Geography joke, not a support query
- **B8** `638059` → `out_of_distribution_noise` (low) 🚩 — Account name change request, but not a common support issue
- **B9** `1244019` → `out_of_distribution_noise` (low) 🚩 — Food complaint, not a support query
- **B10** `2301669` → `out_of_distribution_noise` (low) 🚩 — Food complaint, not a support query

### Recommendation: **MERGE**
The proposed sub-intents cover the representative queries effectively and are mutually exclusive. The boundary queries are clearly out of distribution or not related to customer support, so they can be handled separately.

### Edge cases
- mention_confirmation vs mention_request
- confirmation of a service vs general mention
- customer confusion vs genuine support request

---

## Cluster 4 — No Feedback
*Coarse sub-intent:* Photo / media share | *Size:* 1353 | *Keywords:* url, mention url, mention mention, mention, url mention, view, thank mention, website, right url, like url

### Proposed sub-intents
- `mention_share` — The customer mentions or shares a URL or mention without providing specific feedback or seeking assistance.
  - e.g. _[MENTION] [MENTION] [URL]_
  - e.g. _[MENTION] [URL]_
- `thank_share` — The customer thanks someone or something without providing specific feedback or seeking assistance.
  - e.g. _thank [MENTION] [URL]_
  - e.g. _thank [MENTION]_
- `website_share` — The customer shares a website or URL without providing specific feedback or seeking assistance.
  - e.g. _[URL]_
  - e.g. _view [URL]_

### Query mapping (25)
- **R1** `104342::cust3::2954868` → `mention_share` (high) — 
- **R2** `1109666::cust1::1109665` → `mention_share` (high) — 
- **R3** `1130782::cust1::1130781` → `mention_share` (high) — 
- **R4** `1174919::cust2::1174917` → `mention_share` (high) — 
- **R5** `1236907::cust1::1236906` → `mention_share` (high) — 
- **R6** `1236910::cust1::1236909` → `mention_share` (high) — 
- **R7** `1236917::cust3::1236915` → `mention_share` (high) — 
- **R8** `1236921::cust1::1236919` → `mention_share` (high) — 
- **R9** `1239157::cust3::1239161` → `mention_share` (high) — 
- **R10** `1264844::cust0::1264844` → `mention_share` (high) — 
- **R11** `1349666::cust3::1349668` → `mention_share` (high) — 
- **R12** `1498329::cust0::1498329` → `mention_share` (high) — 
- **R13** `160676::cust7::160690` → `mention_share` (high) — 
- **R14** `169855::cust0::169855` → `mention_share` (high) — 
- **R15** `173758::cust0::173758` → `mention_share` (high) — 
- **B1** `868626::cust0::868626` → `out_of_distribution_noise` (low) 🚩 — Mentions and URL, but no clear intent
- **B2** `1464888::cust0::1464888` → `out_of_distribution_noise` (low) 🚩 — Mentions and URL, but no clear intent
- **B3** `1353896::cust0::1353896` → `out_of_distribution_noise` (low) 🚩 — Mentions and URL, but no clear intent
- **B4** `2595731::cust0::2595731` → `out_of_distribution_noise` (low) 🚩 — Mentions and URL, but no clear intent
- **B5** `521884::cust0::521884` → `out_of_distribution_noise` (low) 🚩 — Mentions and URL, but no clear intent
- **B6** `2621440::cust0::2621440` → `out_of_distribution_noise` (low) 🚩 — Mentions and URL, but no clear intent
- **B7** `1038616::cust0::1038616` → `out_of_distribution_noise` (low) 🚩 — Mentions and URL, but no clear intent
- **B8** `954671::cust0::954671` → `out_of_distribution_noise` (low) 🚩 — Mentions and URL, but no clear intent
- **B9** `1203882::cust0::1203882` → `out_of_distribution_noise` (low) 🚩 — Mentions and URL, but no clear intent
- **B10** `1347003::cust0::1347003` → `out_of_distribution_noise` (low) 🚩 — Mentions and URL, but no clear intent

### Recommendation: **KEEP**
The proposed sub-intents cover the representative queries effectively and are mutually exclusive. The boundary queries are clearly noise or out of distribution, so no further splitting is necessary.

### Edge cases
- [MENTION] [MENTION] [URL] vs [MENTION] [URL]
- thank [MENTION] [URL] vs [URL]
- [URL] vs [MENTION] [URL]

---

## Cluster 5 — Positive Feedback
*Coarse sub-intent:* Appreciation / Praise | *Size:* 4063 | *Keywords:* flight, great, url, mention flight, flying, crew, thanks, best, thank, great flight

### Proposed sub-intents
- `great_flight_experience` — Expressing satisfaction with the overall flight experience.
  - e.g. _great flight_
  - e.g. _great flying experience_
  - e.g. _smooth flight_
- `crew_praise` — Acknowledging the quality of the flight crew.
  - e.g. _flight crew was awesome_
  - e.g. _attentive and polite crew_
  - e.g. _wonderful airline_
- `service_recognition` — Acknowledging the service provided during the flight.
  - e.g. _service rocks_
  - e.g. _attentive and polite_
  - e.g. _best service as always_
- `thank_you_message` — Sending a simple thank you message without specific details.
  - e.g. _thank you_
  - e.g. _thanks for the smooth flight_
  - e.g. _thank you for being the best_

### Query mapping (25)
- **R1** `301666` → `great_flight_experience` (high) — 
- **R2** `1847014` → `thank_you_message` (high) — 
- **R3** `2803836` → `great_flight_experience` (high) — 
- **R4** `15775` → `great_flight_experience` (high) — 
- **R5** `2572581` → `service_recognition` (high) — 
- **R6** `2572581` → `service_recognition` (high) — 
- **R7** `2127749` → `great_flight_experience` (high) — 
- **R8** `251714` → `service_recognition` (high) — 
- **R9** `1623720` → `crew_praise` (high) — 
- **R10** `1826407` → `service_recognition` (high) — 
- **R11** `1328822` → `service_recognition` (high) — 
- **R12** `2745130` → `great_flight_experience` (high) — 
- **R13** `1124069` → `service_recognition` (high) — 
- **R14** `2299786` → `crew_praise` (high) — 
- **R15** `2856073` → `great_flight_experience` (high) — 
- **B1** `296510` → `out_of_distribution_noise` (low) 🚩 — 
- **B2** `1644138` → `out_of_distribution_noise` (low) 🚩 — 
- **B3** `2362058` → `out_of_distribution_noise` (low) 🚩 — 
- **B4** `653229` → `out_of_distribution_noise` (low) 🚩 — 
- **B5** `1295957` → `out_of_distribution_noise` (low) 🚩 — 
- **B6** `1343135` → `out_of_distribution_noise` (low) 🚩 — 
- **B7** `2133719` → `out_of_distribution_noise` (low) 🚩 — 
- **B8** `1079331` → `out_of_distribution_noise` (low) 🚩 — 
- **B9** `1038622` → `out_of_distribution_noise` (low) 🚩 — 
- **B10** `2589772` → `out_of_distribution_noise` (low) 🚩 — 

### Recommendation: **KEEP**
The proposed sub-intents are mutually exclusive and cover the typical queries well. The boundary queries are clearly out of distribution and do not fit into the positive feedback category.

### Edge cases
- great flight vs. great flight experience
- service recognition vs. crew praise
- simple thank you vs. detailed thank you

---

## Cluster 6 — Seating
*Coarse sub-intent:* Seat assignment / change | *Size:* 2325 | *Keywords:* seat, seats, class, row, window, middle, extra, paid, sit, room

### Proposed sub-intents
- `seat_assignment_request` — Request for a specific seat assignment or reassignment.
  - e.g. _can you help with my seat assignment?_
  - e.g. _put me back in my seat_
- `seat_upgrade_request` — Request to upgrade to a better seat, often due to empty seats being available.
  - e.g. _not sure why I'm not allowed to PAY to upgrade my seat_
  - e.g. _I was able to change my seat for my first flight, but not for my connecting flight?_
- `seat_reassignment_request` — Request for a seat reassignment, often due to seat issues or personal preferences.
  - e.g. _The flight is later this evening. Any chance you can put me back in my seat_
  - e.g. _I didn’t like was that they all kept telling me “you can’t change seats”_
- `seat_complaint` — Complaint about the seat, including issues like seat class, seat location, or seat availability.
  - e.g. _Barely made it. You guys cancelled our flight and we had to run from concourse E all the way to concourse B_
  - e.g. _There are none and in facg we just opened the door again to let another person on an already delayed flight_

### Query mapping (25)
- **R1** `1068791` → `seat_complaint` (high) — 
- **R2** `2300836` → `seat_reassignment_request` (high) — 
- **R3** `1273746` → `seat_complaint` (high) — 
- **R4** `824204` → `seat_upgrade_request` (high) — 
- **R5** `1309478` → `seat_reassignment_request` (high) — 
- **R6** `766421` → `seat_reassignment_request` (high) — 
- **R7** `1531567` → `seat_assignment_request` (high) — 
- **R8** `257343` → `seat_reassignment_request` (high) — 
- **R9** `1839507` → `seat_complaint` (high) — 
- **R10** `1305328` → `seat_reassignment_request` (high) — 
- **R11** `1949121` → `seat_complaint` (high) — 
- **R12** `2768598` → `seat_complaint` (high) — 
- **R13** `1440822` → `seat_complaint` (high) — 
- **R14** `2911107` → `seat_reassignment_request` (high) — 
- **R15** `2922065` → `seat_reassignment_request` (high) — 
- **B1** `2233756` → `out_of_distribution_noise` (low) 🚩 — 
- **B2** `2513508` → `out_of_distribution_noise` (low) 🚩 — 
- **B3** `1374768` → `out_of_distribution_noise` (low) 🚩 — 
- **B4** `2678601` → `out_of_distribution_noise` (low) 🚩 — 
- **B5** `368009` → `out_of_distribution_noise` (low) 🚩 — 
- **B6** `1126269` → `out_of_distribution_noise` (low) 🚩 — 
- **B7** `2968550` → `out_of_distribution_noise` (low) 🚩 — 
- **B8** `2494020` → `out_of_distribution_noise` (low) 🚩 — 
- **B9** `2312342` → `out_of_distribution_noise` (low) 🚩 — 
- **B10** `2128820` → `out_of_distribution_noise` (low) 🚩 — 

### Recommendation: **KEEP**
The proposed sub-intents cover the representative queries effectively and are mutually exclusive. The cluster is coherent and does not require further splitting or merging.

### Edge cases
- seat_reassignment_request vs seat_complaint
- seat_upgrade_request vs seat_reassignment_request
- seat_complaint vs seat_reassignment_request

---

## Cluster 7 — Refunds and Charges
*Coarse sub-intent:* Refund / fee dispute | *Size:* 2889 | *Keywords:* ticket, pay, fee, change, miles, charge, 200, economy, paid, fees

### Proposed sub-intents
- `refund_dispute` — Customer disputes a refund or additional charge.
  - e.g. _I should not be charged_
  - e.g. _Why am I being charged_
  - e.g. _Refund issue_
- `fee_dispute` — Customer disputes a specific fee or charge applied to their ticket.
  - e.g. _Why is there a fee_
  - e.g. _Charge dispute_
  - e.g. _Extra fee_
- `flight_change_fee` — Customer questions or disputes the fee for changing their flight.
  - e.g. _Change fee_
  - e.g. _Flight change cost_
  - e.g. _Rebooking fee_

### Query mapping (25)
- **R1** `1533972` → `refund_dispute` (high) — 
- **R2** `2618696` → `fee_dispute` (high) — 
- **R3** `238229` → `refund_dispute` (high) — 
- **R4** `1638403` → `fee_dispute` (high) — 
- **R5** `2311233` → `refund_dispute` (high) — 
- **R6** `302409` → `flight_change_fee` (high) — 
- **R7** `1287145` → `flight_change_fee` (high) — 
- **R8** `1600794` → `refund_dispute` (high) — 
- **R9** `1851577` → `refund_dispute` (high) — 
- **R10** `722236` → `flight_change_fee` (high) — 
- **R11** `875399` → `refund_dispute` (medium) — 
- **R12** `1138113` → `refund_dispute` (medium) — 
- **R13** `1943648` → `fee_dispute` (high) — 
- **R14** `2946476` → `flight_change_fee` (high) — 
- **R15** `1845398` → `fee_dispute` (high) — 
- **B1** `341084` → `out_of_distribution_noise` (low) 🚩 — 
- **B2** `2518507` → `fee_dispute` (medium) — 
- **B3** `904814` → `out_of_distribution_noise` (low) 🚩 — 
- **B4** `1093530` → `out_of_distribution_noise` (low) 🚩 — 
- **B5** `1102928` → `out_of_distribution_noise` (low) 🚩 — 
- **B6** `1688843` → `out_of_distribution_noise` (low) 🚩 — 
- **B7** `2522626` → `out_of_distribution_noise` (low) 🚩 — 
- **B8** `2922072` → `out_of_distribution_noise` (low) 🚩 — 
- **B9** `1403105` → `out_of_distribution_noise` (low) 🚩 — 
- **B10** `2653778` → `out_of_distribution_noise` (low) 🚩 — 

### Recommendation: **SPLIT**
The queries are distinctly focused on different aspects of fee and refund disputes, making it necessary to split the cluster into more specific intents for better classification accuracy.

### Edge cases
- refund_dispute vs fee_dispute
- flight_change_fee vs refund_dispute
- fee_dispute vs seat_upgrade_request

---

## Cluster 8 — No Feedback
*Coarse sub-intent:* Acknowledgement / thanks | *Size:* 2021 | *Keywords:* thank, mention thank, thanks, mention thanks, sent, mention, dm, mention sent, sent dm, mention dm

### Proposed sub-intents
- `thank_you` — Expressing gratitude to the customer service team.
  - e.g. _Thank you!_
  - e.g. _Thanks!_
- `acknowledgment` — Acknowledging a previous interaction or request without providing further details.
  - e.g. _Mention thank_
  - e.g. _mention thanks_
- `dm_request` — Requesting a direct message for further communication.
  - e.g. _DM me_
  - e.g. _send DM_

### Query mapping (25)
- **R1** `1092474::cust4::1117434` → `thank_you` (high) — 
- **R2** `1134396::cust2::1134398` → `thank_you` (high) — 
- **R3** `1269737::cust2::1269739` → `thank_you` (high) — 
- **R4** `128889::cust2::128885` → `thank_you` (high) — 
- **R5** `1410006::cust1::1410007` → `thank_you` (high) — 
- **R6** `1455839::cust1::1455838` → `thank_you` (high) — 
- **R7** `1535887::cust1::1535886` → `thank_you` (high) — 
- **R8** `1558299::cust2::1558301` → `thank_you` (high) — 
- **R9** `1572526::cust3::1572521` → `thank_you` (high) — 
- **R10** `1592206::cust1::1592205` → `thank_you` (high) — 
- **R11** `1605212::cust1::1605210` → `thank_you` (high) — 
- **R12** `1629644::cust1::1629643` → `thank_you` (high) — 
- **R13** `1707356::cust3::1707353` → `thank_you` (high) — 
- **R14** `1732778::cust1::1732777` → `thank_you` (high) — 
- **R15** `1848502::cust3::1848507` → `thank_you` (high) — 
- **B1** `2810867::cust1::2810871` → `acknowledgment` (medium) — Acknowledges response but adds additional context
- **B2** `2313596::cust0::2313596` → `out_of_distribution_noise` (low) 🚩 — Request for account update with thanks, not a simple thank you
- **B3** `335806::cust0::335806` → `out_of_distribution_noise` (low) 🚩 — Request for DM with multiple mentions and urgency
- **B4** `607619::cust0::607619` → `thank_you` (medium) — Thanks for a specific action
- **B5** `2277909::cust0::2277909` → `out_of_distribution_noise` (low) 🚩 — Expresses regret for a past event
- **B6** `1102129::cust0::1102129` → `out_of_distribution_noise` (low) 🚩 — Request for further action in a DM
- **B7** `2279736::cust0::2279736` → `thank_you` (medium) — Thank you with additional context
- **B8** `1515549::cust1::1515547` → `thank_you` (medium) — Thank you with additional context
- **B9** `2544131::cust0::2544131` → `out_of_distribution_noise` (low) 🚩 — Request for someone to DM in another language
- **B10** `1410059::cust0::1410059` → `thank_you` (medium) — Thank you with additional context

### Recommendation: **KEEP**
The proposed sub-intents cover the representative queries effectively and are mutually exclusive. The boundary queries are either noise or belong to other clusters, so no further splitting is necessary.

### Edge cases
- Thank you for the help vs. Thank you for the help with additional context
- DM me vs. DM me for further communication
- Simple thank you vs. Thank you with additional context

---

## Cluster 9 — Customer Service
*Coarse sub-intent:* Agent responsiveness / support quality | *Size:* 4847 | *Keywords:* customer, service, customer service, phone, customers, help, email, mention customer, number, response

### Proposed sub-intents
- `poor_customer_service_complaint` — Complaints about the quality of customer service provided by the airline.
  - e.g. _poor customer service_
  - e.g. _terrible customer service_
  - e.g. _customer service bites_
- `lack_of_response_complaint` — Complaints about the lack of timely response to customer inquiries or issues.
  - e.g. _no response_
  - e.g. _haven't received a response_
  - e.g. _response time is too long_
- `customer_service_comparison` — Comparisons of the airline's customer service with that of other airlines or companies.
  - e.g. _better than_
  - e.g. _worse than_
  - e.g. _comparing customer service_

### Query mapping (25)
- **R1** `579540` → `poor_customer_service_complaint` (high) — 
- **R2** `955768` → `poor_customer_service_complaint` (high) — 
- **R3** `2135881` → `lack_of_response_complaint` (high) — 
- **R4** `2164831` → `poor_customer_service_complaint` (high) — 
- **R5** `1955135` → `customer_service_comparison` (high) — 
- **R6** `2977910` → `poor_customer_service_complaint` (high) — 
- **R7** `2245013` → `poor_customer_service_complaint` (high) — 
- **R8** `219731` → `poor_customer_service_complaint` (high) — 
- **R9** `2632894` → `poor_customer_service_complaint` (high) — 
- **R10** `2057548` → `poor_customer_service_complaint` (high) — 
- **R11** `2470282` → `poor_customer_service_complaint` (high) — 
- **R12** `594171` → `poor_customer_service_complaint` (high) — 
- **R13** `2373110` → `poor_customer_service_complaint` (high) — 
- **R14** `306332` → `lack_of_response_complaint` (high) — 
- **R15** `392344` → `poor_customer_service_complaint` (high) — 
- **B1** `390520` → `out_of_distribution_noise` (low) 🚩 — 
- **B2** `2472648` → `out_of_distribution_noise` (low) 🚩 — 
- **B3** `1858365` → `out_of_distribution_noise` (low) 🚩 — 
- **B4** `2520498` → `out_of_distribution_noise` (low) 🚩 — 
- **B5** `2714932` → `out_of_distribution_noise` (low) 🚩 — 
- **B6** `1804586` → `out_of_distribution_noise` (low) 🚩 — 
- **B7** `541746` → `out_of_distribution_noise` (low) 🚩 — 
- **B8** `1214644` → `out_of_distribution_noise` (low) 🚩 — 
- **B9** `1692783` → `out_of_distribution_noise` (low) 🚩 — 
- **B10** `1520578` → `out_of_distribution_noise` (low) 🚩 — 

### Recommendation: **KEEP**
The proposed sub-intents are mutually exclusive and cover the representative queries effectively. The queries are clearly related to customer service issues and do not overlap significantly.

### Edge cases
- poor_customer_service_complaint vs lack_of_response_complaint
- poor_customer_service_complaint vs customer_service_comparison

---

## Cluster 10 — Baggage
*Coarse sub-intent:* Lost, delayed or forced-checked baggage | *Size:* 2816 | *Keywords:* bag, bags, luggage, check, baggage, carry, checked, check bag, lost, claim

### Proposed sub-intents
- `lost_baggage_claim` — Customer reports that their baggage is missing or has not been found.
  - e.g. _my bag is missing_
  - e.g. _haven't received my baggage_
- `carry_on_gate_check_complaint` — Customer complains about being forced to check their carry-on bag despite available overhead space.
  - e.g. _forced to check my carry-on_
  - e.g. _no overhead space for my bag_
- `damaged_baggage_report` — Customer reports damage to their checked baggage.
  - e.g. _my bag was damaged_
  - e.g. _baggage was torn_
- `baggage_claim_dispute` — Customer disputes the handling of their baggage, including issues with baggage claim or lost baggage.
  - e.g. _dispute baggage claim_
  - e.g. _baggage claim issue_
- `baggage_policy_question` — Customer asks about baggage policies, such as weight limits or allowed items.
  - e.g. _baggage policy_
  - e.g. _weight limit for baggage_

### Query mapping (25)
- **R1** `2287172` → `carry_on_gate_check_complaint` (high) — 
- **R2** `902659` → `carry_on_gate_check_complaint` (high) — 
- **R3** `2395047` → `carry_on_gate_check_complaint` (high) — 
- **R4** `886087` → `lost_baggage_claim` (high) — 
- **R5** `1296923` → `carry_on_gate_check_complaint` (high) — 
- **R6** `390884` → `lost_baggage_claim` (high) — 
- **R7** `223223` → `lost_baggage_claim` (high) — 
- **R8** `2741079` → `out_of_distribution_noise` (low) 🚩 — No clear baggage issue
- **R9** `1906554` → `lost_baggage_claim` (high) — 
- **R10** `1244031` → `lost_baggage_claim` (high) — 
- **R11** `2371549` → `lost_baggage_claim` (high) — 
- **R12** `1536525` → `damaged_baggage_report` (high) — 
- **R13** `1109651` → `lost_baggage_claim` (high) — 
- **R14** `2837940` → `carry_on_gate_check_complaint` (high) — 
- **R15** `2044248` → `lost_baggage_claim` (high) — 
- **B1** `2306158` → `out_of_distribution_noise` (low) 🚩 — Personal item issue
- **B2** `255701` → `out_of_distribution_noise` (low) 🚩 — Carry-on policy inquiry
- **B3** `977455` → `out_of_distribution_noise` (low) 🚩 — Casual complaint
- **B4** `251703` → `out_of_distribution_noise` (low) 🚩 — Gender equality complaint
- **B5** `1848502` → `out_of_distribution_noise` (low) 🚩 — Customer service inquiry
- **B6** `795944` → `out_of_distribution_noise` (low) 🚩 — Breast pump policy inquiry
- **B7** `309631` → `out_of_distribution_noise` (low) 🚩 — Product complaint
- **B8** `1582329` → `out_of_distribution_noise` (low) 🚩 — Facility complaint
- **B9** `1499077` → `out_of_distribution_noise` (low) 🚩 — Food quality complaint
- **B10** `1816753` → `out_of_distribution_noise` (low) 🚩 — Security policy complaint

### Recommendation: **KEEP**
The proposed sub-intents are mutually exclusive and cover the representative queries effectively. The cluster remains coherent and does not require further splitting or merging.

### Edge cases
- lost_baggage_claim vs damaged_baggage_report
- carry_on_gate_check_complaint vs lost_baggage_claim
- baggage_policy_question vs lost_baggage_claim

---

## Cluster 11 — Flight Cancellation
*Coarse sub-intent:* Cancelled / missed flight & rebooking | *Size:* 5367 | *Keywords:* flight, flights, fly, flying, plane, mention flight, cancelled, planes, need, know

### Proposed sub-intents
- `flight_cancellation_announcement` — Customer is seeking information about a flight cancellation.
  - e.g. _flight cancelled_
  - e.g. _my flight was cancelled_
- `flight_cancellation_rebooking` — Customer requests rebooking or rescheduling after a flight cancellation.
  - e.g. _need to rebook my flight_
  - e.g. _reschedule my flight_
- `flight_cancellation_updates` — Customer is asking for updates on the status of a cancelled flight.
  - e.g. _when will my flight be confirmed_
  - e.g. _status of my flight_

### Query mapping (25)
- **R1** `2774883` → `flight_cancellation_announcement` (high) — 
- **R2** `2258775` → `flight_cancellation_announcement` (high) — 
- **R3** `33535` → `flight_cancellation_rebooking` (high) — 
- **R4** `2960856` → `flight_cancellation_rebooking` (high) — 
- **R5** `482590` → `flight_cancellation_announcement` (high) — 
- **R6** `2333700` → `flight_cancellation_announcement` (high) — 
- **R7** `1753607` → `flight_cancellation_announcement` (high) — 
- **R8** `2622942` → `flight_cancellation_announcement` (high) — 
- **R9** `293023` → `flight_cancellation_announcement` (high) — 
- **R10** `2086428` → `flight_cancellation_announcement` (high) — 
- **R11** `2455529` → `flight_cancellation_announcement` (high) — 
- **R12** `1102707` → `flight_cancellation_rebooking` (high) — 
- **R13** `2250304` → `flight_cancellation_rebooking` (high) — 
- **R14** `1458403` → `flight_cancellation_announcement` (high) — 
- **R15** `1004132` → `flight_cancellation_rebooking` (high) — 
- **B1** `630138` → `out_of_distribution_noise` (low) 🚩 — 
- **B2** `1817853` → `out_of_distribution_noise` (low) 🚩 — 
- **B3** `2194741` → `out_of_distribution_noise` (low) 🚩 — 
- **B4** `1209981` → `out_of_distribution_noise` (low) 🚩 — 
- **B5** `1098025` → `out_of_distribution_noise` (low) 🚩 — 
- **B6** `891859` → `out_of_distribution_noise` (low) 🚩 — 
- **B7** `601990` → `out_of_distribution_noise` (low) 🚩 — 
- **B8** `1425826` → `out_of_distribution_noise` (low) 🚩 — 
- **B9** `1297597` → `out_of_distribution_noise` (low) 🚩 — 
- **B10** `2499523` → `out_of_distribution_noise` (low) 🚩 — 

### Recommendation: **KEEP**
The proposed sub-intents are mutually exclusive and cover the representative queries effectively. The boundary queries do not fit into the cluster and are marked as noise.

### Edge cases
- flight_cancellation_announcement vs flight_cancellation_rebooking
- flight_cancellation_rebooking vs flight_cancellation_updates

---
