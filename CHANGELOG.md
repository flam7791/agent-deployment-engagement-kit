# Changelog

## v0.1.0 - 2026-11-18
- First public version: 12-week engagement playbook (plan, discovery canvas, agent spec, go-live checklist); `deploykit` reference agent (Italian/English, approved answers only, escalation rules, safety-keyword net, personal-data guard), offline evaluation gate on a held-out test set, pilot metrics, widen rule and weekly steering pack.
- `steering-note` Claude skill v0.1.0: sponsor note from facts.json in English or Italian, recommendation exactly as the rule gives it, no savings figures.
- 19 unit tests; offline gate passed (96.7% intent accuracy, 100% escalation, 0 wrong answers); red-team safety gate passed (18 messages, 100% escalation, 0 wrong answers); 10 steering-note cases (9 must-pass, all passing, model-run); CI workflow.
