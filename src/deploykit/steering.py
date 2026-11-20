"""Weekly steering facts: plan status, offline gate, pilot metrics, the widen recommendation by rule, risks and decisions."""
from __future__ import annotations


def recommend(offline: dict, weeks: list[dict]) -> dict:
    last2 = weeks[-2:]
    reasons = []
    if not offline["passed"]:
        failed = [k for k, v in offline["checks"].items() if not v]
        return {"decision": "fix first", "reasons": [f"offline gate failed on: {', '.join(failed)}"]}
    if len(last2) < 2:
        return {"decision": "hold", "reasons": ["fewer than two pilot weeks of data"]}
    for w in last2:
        for k, ok in w["checks"].items():
            if not ok:
                reasons.append(f"week {w['week']}: {k} target missed")
    if reasons:
        return {"decision": "hold", "reasons": reasons}
    return {"decision": "widen", "reasons": ["offline gate passed and every pilot target met in the last two weeks"]}


def build(engagement: dict, offline: dict, weeks: list[dict]) -> dict:
    rec = recommend(offline, weeks)
    cur = engagement["current_week"]
    ms = engagement["milestones"]
    late = [m for m in ms if m["week"] < cur and m["status"] not in ("done",)]
    decisions = []
    nxt = next((m for m in ms if m["status"] == "pending"), None)
    if nxt:
        decisions.append(f"Week {nxt['week']}: {nxt['name']} (recommendation by rule: {rec['decision']})")
    for r in engagement["risks"]:
        if r["status"] == "open":
            decisions.append(f"Confirm the owner's action on the open risk: {r['risk']} (owner: {r['owner']})")
    latest = weeks[-1] if weeks else None
    b = engagement["baseline"]
    return {
        "engagement": {k: engagement[k] for k in ("client", "sponsor", "process_owner", "engagement_weeks", "current_week", "scope")},
        "milestones": ms, "late_milestones": late,
        "offline_eval": {"metrics": offline["metrics"], "gate": offline["gate"], "checks": offline["checks"], "passed": offline["passed"]},
        "pilot": {"targets": engagement["pilot_targets"], "weeks": weeks, "latest": latest},
        "recommendation": {**rec, "rule": engagement["widen_rule"]},
        "baseline": b,
        "risks": engagement["risks"],
        "decisions_needed": decisions,
        "approval": {"status": "draft for the sponsor's steering meeting",
                     "rule": "The sponsor decides on widening; the agent and the delivery team only recommend."},
    }
