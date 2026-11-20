"""Offline evaluation of an agent on a labelled message set, checked against the engagement's offline gate."""
from __future__ import annotations

import json

from .agent import respond


def load_messages(path: str) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def evaluate(messages: list[dict], kb: dict, gate: dict, agent=respond) -> dict:
    rows, n = [], len(messages)
    for m in messages:
        out = agent(m["text"], kb)
        intent_ok = out["intent"] == m["expected_intent"] or (m["expected_intent"] == "unknown" and out["action"] == "handoff")
        rows.append({"id": m["id"], "expected_action": m["expected_action"], "expected_intent": m["expected_intent"],
                     "action": out["action"], "intent": out["intent"], "confidence": out["confidence"],
                     "language_ok": out["language"] == m["language"],
                     "correct": out["action"] == m["expected_action"] and intent_ok})
    must = [r for r in rows if r["expected_action"] == "handoff"]
    answerable = [r for r in rows if r["expected_action"] == "answer"]
    metrics = {
        "messages": n,
        "intent_accuracy": round(sum(r["correct"] for r in rows) / n, 3),
        "escalation_recall": round(sum(r["action"] == "handoff" for r in must) / len(must), 3) if must else None,
        "false_handoff_rate": round(sum(r["action"] == "handoff" for r in answerable) / len(answerable), 3) if answerable else None,
        "wrong_answer_count": sum(r["action"] == "answer" and not r["correct"] for r in rows),
        "language_match": round(sum(r["language_ok"] for r in rows) / n, 3),
    }
    if set(gate) <= {"escalation_recall_min", "wrong_answers_max"}:  # red-team gate: safety only
        checks = {"escalation_recall": metrics["escalation_recall"] is not None and metrics["escalation_recall"] >= gate["escalation_recall_min"],
                  "wrong_answers": metrics["wrong_answer_count"] <= gate["wrong_answers_max"]}
        return {"metrics": metrics, "gate": gate, "checks": checks, "passed": all(checks.values()),
                "failures": [r for r in rows if not r["correct"]]}
    checks = {
        "intent_accuracy": metrics["intent_accuracy"] >= gate["intent_accuracy_min"],
        "escalation_recall": metrics["escalation_recall"] is not None and metrics["escalation_recall"] >= gate["escalation_recall_min"],
        "false_handoff_rate": metrics["false_handoff_rate"] is not None and metrics["false_handoff_rate"] <= gate["false_handoff_rate_max"],
        "language_match": metrics["language_match"] >= gate["language_match_min"],
        "wrong_answers": metrics["wrong_answer_count"] <= gate.get("wrong_answers_max", 0),
    }
    return {"metrics": metrics, "gate": gate, "checks": checks, "passed": all(checks.values()),
            "failures": [r for r in rows if not r["correct"]]}
