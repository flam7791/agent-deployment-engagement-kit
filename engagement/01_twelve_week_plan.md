# The 12-week engagement

One customer-facing agent, one process, one sponsor. Every phase ends with an artefact the client keeps.

| Weeks | Phase | What happens | Artefact | Exit criterion |
|---|---|---|---|---|
| 1-2 | Discovery | Read a sample of real contacts with the team that answers them; rank contact reasons by volume and effort; map every path to a person (who takes a handoff, how fast) | `02_discovery_canvas.md` filled in | Top contact reasons cover at least 60% of volume; handoff owners named |
| 3 | Scope and success criteria | Choose the intents the agent answers and the ones it must always hand off; fix targets and the widen rule with the sponsor, before anything is built | `config/engagement.json` signed | Sponsor signs scope, targets and widen rule |
| 4-5 | Build | Write approved answers in every customer language and get them signed by the content owner; configure escalation rules; build the evaluation set from real phrasing, split into a dev set (for tuning) and a held-out test set (for the gate) | `config/knowledge_base.json`, `data/*_messages.jsonl`, `03_agent_spec.md` | Content owner signs every answer |
| 6 | Offline gate | Run the held-out test set; every must-escalate message goes to a person; wrong answers investigated one by one | `deploykit evaluate` report | Offline gate passed |
| 7-9 | Pilot | 10% of traffic; weekly review of containment, CSAT, repeat contact and the wait after handoff; content fixes from real conversations | weekly steering pack | Targets met two weeks running |
| 10 | Widen decision | The sponsor decides on 50% of traffic from the steering pack; the rule recommends, the sponsor decides | decision recorded | Decision taken |
| 11 | Handover | The client team runs content updates, the weekly review and the evaluation set themselves | `04_go_live_checklist.md` complete | Client team runs one review unaided |
| 12 | Close | Value review against the week-3 baseline, using the client's own contact-centre figures | value review | Sponsor accepts the review |

Principles: the escalation policy and the evaluation set come before the model; the agent answers only from approved text; a person is always one step away; the sponsor decides, the delivery team recommends.
