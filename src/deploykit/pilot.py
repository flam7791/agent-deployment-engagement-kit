"""Pilot log: one row per conversation. Generator for the synthetic pilot, and weekly metrics against targets."""
from __future__ import annotations

import csv
import random
from statistics import median

INTENTS = ["bill_explanation", "meter_reading", "moving_house", "payment_methods", "outage"]
ESCALATIONS = ["complaint", "payment_hardship", "vulnerability", "account_change", "personal_data", "unknown"]
FIELDS = ["week", "conversation_id", "language", "intent", "action", "resolved", "csat", "repeat_contact_7d", "handoff_wait_min"]

# per pilot week (engagement weeks 7, 8, 9): invented behaviour. Containment and CSAT improve as content
# is refined; the handoff queue is under-staffed, so waits grow with volume.
PROFILE = {
    7: {"n": 480, "answer_share": 0.60, "resolve_if_answered": 0.82, "csat_mean": 3.9, "repeat": 0.14, "wait": 7},
    8: {"n": 520, "answer_share": 0.66, "resolve_if_answered": 0.86, "csat_mean": 4.1, "repeat": 0.11, "wait": 9},
    9: {"n": 560, "answer_share": 0.68, "resolve_if_answered": 0.87, "csat_mean": 4.2, "repeat": 0.10, "wait": 14},
}


def generate(path: str, seed: int = 9) -> None:
    rng = random.Random(seed)
    rows, cid = [], 0
    for wk, p in PROFILE.items():
        for _ in range(p["n"]):
            cid += 1
            answered = rng.random() < p["answer_share"]
            resolved = answered and rng.random() < p["resolve_if_answered"]
            csat = ""
            if rng.random() < 0.35:  # about a third of customers rate the chat
                csat = max(1, min(5, round(rng.gauss(p["csat_mean"] + (0.3 if resolved else -0.5), 0.8))))
            rows.append({"week": wk, "conversation_id": f"C{cid:06d}", "language": "it" if rng.random() < 0.82 else "en",
                         "intent": rng.choice(INTENTS) if answered else rng.choice(ESCALATIONS),
                         "action": "answer" if answered else "handoff", "resolved": int(resolved), "csat": csat,
                         "repeat_contact_7d": int(rng.random() < p["repeat"]),
                         "handoff_wait_min": "" if answered else max(0, round(rng.gauss(p["wait"], 3)))})
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)


def load(path: str) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def weekly(rows: list[dict], targets: dict) -> list[dict]:
    out = []
    for wk in sorted({int(r["week"]) for r in rows}):
        w = [r for r in rows if int(r["week"]) == wk]
        n = len(w)
        rated = [int(r["csat"]) for r in w if r["csat"]]
        waits = [int(r["handoff_wait_min"]) for r in w if r["handoff_wait_min"] != ""]
        m = {"week": wk, "conversations": n,
             "containment": round(sum(int(r["resolved"]) for r in w) / n, 3),
             "handoff_rate": round(sum(r["action"] == "handoff" for r in w) / n, 3),
             "csat": round(sum(rated) / len(rated), 2) if rated else None, "csat_responses": len(rated),
             "repeat_contact": round(sum(int(r["repeat_contact_7d"]) for r in w) / n, 3),
             "handoff_wait_median_min": round(median(waits), 1) if waits else None,
             "italian_share": round(sum(r["language"] == "it" for r in w) / n, 3)}
        m["checks"] = {
            "containment": m["containment"] >= targets["containment_min"],
            "csat": m["csat"] is not None and m["csat"] >= targets["csat_min"],
            "repeat_contact": m["repeat_contact"] <= targets["repeat_contact_max"],
            "handoff_wait": m["handoff_wait_median_min"] is not None and m["handoff_wait_median_min"] <= targets["handoff_wait_median_min_max"],
        }
        m["all_met"] = all(m["checks"].values())
        out.append(m)
    return out
