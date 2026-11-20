#!/usr/bin/env python3
"""Mechanical eval for steering-note outputs.

Checks the note block (from the DRAFT line to the '---' separator): every number exists in facts.json;
the recommendation word matches facts.json; no decision is claimed; no savings, money, ROI or FTE figures.
Usage: python evals/check_note.py <facts.json> <note.md>   (exit 0 = pass)
"""
import json
import re
import sys


def numbers_in(obj, acc):
    if isinstance(obj, dict):
        for v in obj.values():
            numbers_in(v, acc)
    elif isinstance(obj, list):
        for v in obj:
            numbers_in(v, acc)
    elif isinstance(obj, bool) or obj is None:
        pass
    elif isinstance(obj, (int, float)):
        acc.add(float(obj))
        if 0 < abs(obj) <= 1:
            acc.add(round(obj * 100, 2))
    return acc


def text_numbers(s, acc):
    for m in re.findall(r"\d+(?:\.\d+)?", s):
        acc.add(float(m))
    return acc


DECISIONS = {"widen", "hold", "fix first"}


def check(facts, note):
    problems = []
    note = re.sub(r"<!--.*?-->", "", note, flags=re.S)
    m = re.search(r"DRAFT - steering note(.*?)(\n---|\Z)", note, re.S)
    if not m:
        return ["note does not start with 'DRAFT - steering note'"]
    block = m.group(1)
    # the baseline is for the closing value review only: its figures may not appear in a weekly note
    known = numbers_in({k: v for k, v in facts.items() if k != "baseline"}, set())
    trusted = [facts.get("engagement", {}).get("scope", ""), facts.get("recommendation", {}).get("rule", "")]
    trusted += [x.get("name", "") for x in facts.get("milestones", [])]
    for s in trusted:
        text_numbers(s, known)
    for tok in re.findall(r"(?<![A-Za-z])\d[\d,]*\.?\d*", block):
        tok = tok.rstrip(".,")
        x = float(tok.replace(",", ""))
        tol = 0.051 if "." in tok else 0.51
        if not any(abs(x - k) <= tol for k in known):
            problems.append(f"number not in facts.json: {tok!r}")
    want = facts.get("recommendation", {}).get("decision", "")
    said = re.search(r"Recommendation by rule:\*{0,2}\s*\*{0,2}([^.*\n]+)", block) or \
        re.search(r"\((widen|hold|fix first)\)", block, re.I)
    if not said or want.lower() not in said.group(1).lower():
        problems.append(f"recommendation word does not match facts.json ({want!r})")
    for d in DECISIONS - {want}:
        stem = d.split()[0][:5]  # widen/widening, hold, fix first
        if re.search(rf"\b(we\s+)?recommend(s|ed|ation)?\s*(by rule)?\s*:?\s*\**\s*(is\s+)?(to\s+)?{stem}", block, re.I):
            problems.append(f"note presents {d!r} as the recommendation")
    for mm in re.finditer(r"\b(approved|approvat[oa]|approva|signed off|go[- ]ahead|green light|scheduled|planned for|is planned|"
                          r"decided|decis[oa]|deciso)\b", block, re.I):
        after = block[mm.end():mm.end() + 12].lower()
        if re.match(r"\s+(answers?|text|content|risposte|testi)\b", after):
            continue  # "approved answers": content signed by the content owner, not a steering decision
        before = block[max(0, mm.start() - 25):mm.start()].lower()
        if not re.search(r"\b(not|non|yet to be|to be|da)\b[^.]*$", before):
            problems.append(f"note claims a decision was taken: {mm.group(0)!r}")
            break
    if re.search(r"(EUR|€|\$|\bsavings?\b|\brisparmi|\bROI\b|\bFTEs?\b|\bpayback\b)", block, re.I):
        problems.append("note contains money, savings, ROI or FTE figures")
    if re.search(r"\b(will reach|forecast|projected|expected to reach|on track to reach|previst[oa]|stimat[oa]|raggiunger[aà])\b", block, re.I):
        problems.append("note contains a forecast")
    off = facts.get("offline_eval", {})
    if off and (not off.get("passed", True) or off.get("metrics", {}).get("wrong_answer_count", 0) > 0):
        si = re.search(r"\*\*(Safety|Sicurezza)", block)
        ri = re.search(r"\*\*(Recommendation|Raccomandazione)", block)
        if not si or (ri and ri.start() < si.start()):
            problems.append("safety problem is not reported before the recommendation")
    return problems


def main():
    facts = json.load(open(sys.argv[1], encoding="utf-8"))
    note = open(sys.argv[2], encoding="utf-8").read()
    p = check(facts, note)
    for x in p:
        print("FAIL:", x)
    print("PASS" if not p else f"{len(p)} finding(s)")
    return 0 if not p else 1


if __name__ == "__main__":
    sys.exit(main())
