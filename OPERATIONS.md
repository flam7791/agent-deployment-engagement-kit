# Operating model (sample)

Designed for production; operated as a prototype with synthetic data. Thresholds come from `config/engagement.json`.

## 1. Release gate (before the pilot and before every change to answers or rules)
- [ ] `deploykit evaluate` passes on the held-out test set, with 100% of must-escalate messages handed to a person and 0 wrong answers
- [ ] Every approved answer signed by the content owner, in every language
- [ ] Handoff queue staffed and the target wait agreed with the process owner
- [ ] Data protection: personal financial data never processed in chat; logs hold conversation IDs only
- [ ] Kill switch tested: the chat falls back to "talk to a person" in one change
- [ ] Previous knowledge-base version kept for rollback

## 2. Rollout
10% of chat traffic for at least three weeks; widen to 50% only under the widen rule (every pilot target met in each of the last two weeks, offline gate passed), and only on the sponsor's decision.

## 3. Monitoring
| Signal | Source | Frequency | Alert |
|---|---|---|---|
| Containment, CSAT, repeat contact | pilot log | weekly | any target missed two weeks running |
| Wait after handoff | handoff queue | weekly | median above target |
| Safety | offline gate re-run on every change; sample of 50 conversations reviewed weekly | weekly | any wrong answer or missed escalation |
| Content drift | questions handed off as "low confidence" | weekly | a new contact reason above 5% of volume |
| Steering note grounding | `check_note.py` | every note | any failure |

Format: `ops/sample-monitoring-log.csv` (invented data).

## 4. Feedback into evals
Every real conversation that was answered wrongly or should have been escalated is added to the test set, labelled, before the fix ships.

## 5. Change and drift
Re-run the offline gate on any change to answers, examples, rules or the agent; re-run the steering-note cases on any change to the skill or the model.

## 6. Incident runbook
| Incident | Detected by | Contain | Follow-up |
|---|---|---|---|
| Wrong answer given to a customer | weekly review, complaint | switch the intent to handoff; correct the answer with the content owner | new test case |
| Must-escalate message answered | weekly review | kill switch to "talk to a person"; re-run the gate | new test case; rule fix |
| Personal data stored in a log | data protection review | purge the log | tighten the guard; new test |
| Handoff queue overloaded | wait after handoff | reduce traffic share | staffing decision for the sponsor |

## 7. Ownership and retirement
During the engagement: the deployment strategist. After handover (week 11): the client's head of customer service, with a named content owner. Review every three months.
