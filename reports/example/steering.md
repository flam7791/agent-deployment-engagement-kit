# Steering pack: Northwind Energia (fictional), week 9 of 12

Sponsor: Director of Customer Operations · Process owner: Head of Customer Service

Scope: Customer chat on the website, Italian and English; five approved intents answered, four escalation intents always handed to a person.

## Recommendation by rule: **hold**

Rule: Widen only if the offline gate passed and every pilot target was met in each of the last two pilot weeks.

- week 8: csat target missed
- week 9: handoff_wait target missed

## Plan

| Week | Milestone | Status |
|---|---|---|
| 2 | Discovery: top contact reasons, handoff paths and approved content owners mapped | done |
| 3 | Scope and success criteria signed by the sponsor | done |
| 5 | Approved answers (IT/EN) signed off by the content owner | done |
| 6 | Offline evaluation gate passed on the held-out test set | done |
| 7 | Pilot live on 10% of chat traffic | done |
| 10 | Decision: widen to 50% of chat traffic | pending |
| 11 | Handover: client team runs content updates and the weekly review | planned |
| 12 | Close: value review against the week-3 baseline | planned |

## Offline evaluation (held-out test set, 30 messages): passed

| Measure | Result | Gate | |
|---|---|---|---|
| Intent accuracy | 96.7% | >= 85.0% | met |
| Must-escalate messages handed to a person | 100.0% | >= 100.0% | met |
| Answerable messages handed off anyway | 6.2% | <= 15.0% | met |
| Reply in the customer's language | 100.0% | >= 95.0% | met |
| Wrong answers given | 0 | <= 0 | met |

## Pilot (10% of chat traffic)

| Week | Conversations | Contained | CSAT (responses) | Repeat contact in 7 days | Median wait after handoff (min) | All targets |
|---|---|---|---|---|---|---|
| 7 | 480 | 54.8% | 3.86 (153) | 15.0% | 7 | **no** |
| 8 | 520 | 57.1% | 3.97 (204) | 11.7% | 9 | **no** |
| 9 | 560 | 61.6% | 4.16 (206) | 10.2% | 14.0 | **no** |

Targets: contained >= 55.0%, CSAT >= 4.0, repeat contact <= 12.0%, median wait after handoff <= 10 min.

## Risks

| Risk | Owner | Status |
|---|---|---|
| Handoff queue not staffed for the pilot volume; customers wait after the agent hands over | Head of Customer Service | open |
| New tariff letters in week 11 may spike bill questions beyond the approved answers | Content owner | open |
| Content updates still depend on the delivery team | Deployment strategist | mitigating |

## Decisions needed from the sponsor

- Week 10: Decision: widen to 50% of chat traffic (recommendation by rule: hold)
- Confirm the owner's action on the open risk: Handoff queue not staffed for the pilot volume; customers wait after the agent hands over (owner: Head of Customer Service)
- Confirm the owner's action on the open risk: New tariff letters in week 11 may spike bill questions beyond the approved answers (owner: Content owner)

Status: **draft for the sponsor's steering meeting**. The sponsor decides on widening; the agent and the delivery team only recommend.
