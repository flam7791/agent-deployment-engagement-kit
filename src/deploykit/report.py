"""Write facts.json (input for the steering-note agent) and steering.md (for people)."""
from __future__ import annotations

import json
import os


def pct(x):
    return "n/a" if x is None else f"{x * 100:.1f}%"


def tick(ok):
    return "met" if ok else "**missed**"


def to_markdown(f: dict) -> str:
    e, off, p, rec = f["engagement"], f["offline_eval"], f["pilot"], f["recommendation"]
    om, og = off["metrics"], off["gate"]
    out = [f"# Steering pack: {e['client']}, week {e['current_week']} of {e['engagement_weeks']}", "",
           f"Sponsor: {e['sponsor']} · Process owner: {e['process_owner']}", "", f"Scope: {e['scope']}", "",
           f"## Recommendation by rule: **{rec['decision']}**", "", f"Rule: {rec['rule']}", ""]
    out += [f"- {r}" for r in rec["reasons"]]
    out += ["", "## Plan", "", "| Week | Milestone | Status |", "|---|---|---|"]
    out += [f"| {m['week']} | {m['name']} | {m['status']} |" for m in f["milestones"]]
    out += ["", f"## Offline evaluation (held-out test set, {om['messages']} messages): {'passed' if off['passed'] else '**failed**'}", "",
            "| Measure | Result | Gate | |", "|---|---|---|---|",
            f"| Intent accuracy | {pct(om['intent_accuracy'])} | >= {pct(og['intent_accuracy_min'])} | {tick(off['checks']['intent_accuracy'])} |",
            f"| Must-escalate messages handed to a person | {pct(om['escalation_recall'])} | >= {pct(og['escalation_recall_min'])} | {tick(off['checks']['escalation_recall'])} |",
            f"| Answerable messages handed off anyway | {pct(om['false_handoff_rate'])} | <= {pct(og['false_handoff_rate_max'])} | {tick(off['checks']['false_handoff_rate'])} |",
            f"| Reply in the customer's language | {pct(om['language_match'])} | >= {pct(og['language_match_min'])} | {tick(off['checks']['language_match'])} |",
            f"| Wrong answers given | {om['wrong_answer_count']} | <= {og.get('wrong_answers_max', 0)} | {tick(off['checks'].get('wrong_answers', True))} |"]
    t = p["targets"]
    out += ["", "## Pilot (10% of chat traffic)", "",
            "| Week | Conversations | Contained | CSAT (responses) | Repeat contact in 7 days | Median wait after handoff (min) | All targets |",
            "|---|---|---|---|---|---|---|"]
    for w in p["weeks"]:
        out.append(f"| {w['week']} | {w['conversations']} | {pct(w['containment'])} | {w['csat']} ({w['csat_responses']}) | "
                   f"{pct(w['repeat_contact'])} | {w['handoff_wait_median_min']} | {'yes' if w['all_met'] else '**no**'} |")
    out += ["", f"Targets: contained >= {pct(t['containment_min'])}, CSAT >= {t['csat_min']}, repeat contact <= {pct(t['repeat_contact_max'])}, "
            f"median wait after handoff <= {t['handoff_wait_median_min_max']} min.", "",
            "## Risks", "", "| Risk | Owner | Status |", "|---|---|---|"]
    out += [f"| {r['risk']} | {r['owner']} | {r['status']} |" for r in f["risks"]]
    out += ["", "## Decisions needed from the sponsor", ""]
    out += [f"- {d}" for d in f["decisions_needed"]]
    out += ["", f"Status: **{f['approval']['status']}**. {f['approval']['rule']}", ""]
    return "\n".join(out)


def write(facts: dict, meta: dict, outdir: str):
    os.makedirs(outdir, exist_ok=True)
    fj, md = os.path.join(outdir, "facts.json"), os.path.join(outdir, "steering.md")
    with open(fj, "w", encoding="utf-8") as fh:
        json.dump({"meta": meta, **facts}, fh, indent=1, ensure_ascii=False)
    with open(md, "w", encoding="utf-8") as fh:
        fh.write(to_markdown(facts))
    return fj, md
