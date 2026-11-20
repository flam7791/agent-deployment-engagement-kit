"""Command line: python -m deploykit {ask,evaluate,pilot-generate,steer} ..."""
from __future__ import annotations

import argparse
import json
import sys

from . import __version__
from .agent import respond
from .evaluate import evaluate, load_messages
from .pilot import generate, load, weekly
from .report import write
from .steering import build


def _j(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="deploykit")
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("ask", help="send one customer message to the reference agent")
    a.add_argument("message")
    a.add_argument("--kb", default="config/knowledge_base.json")
    e = sub.add_parser("evaluate", help="run the offline evaluation on a labelled message set")
    e.add_argument("--messages", default="data/test_messages.jsonl")
    e.add_argument("--kb", default="config/knowledge_base.json")
    e.add_argument("--engagement", default="config/engagement.json")
    e.add_argument("--gate", choices=["offline", "redteam"], default="offline")
    g = sub.add_parser("pilot-generate", help="write the synthetic pilot log")
    g.add_argument("--out", default="data/pilot_log.csv")
    g.add_argument("--seed", type=int, default=9)
    s = sub.add_parser("steer", help="build the weekly steering pack (facts.json + steering.md)")
    s.add_argument("--messages", default="data/test_messages.jsonl")
    s.add_argument("--pilot", default="data/pilot_log.csv")
    s.add_argument("--kb", default="config/knowledge_base.json")
    s.add_argument("--engagement", default="config/engagement.json")
    s.add_argument("--out", default="reports/latest")
    args = ap.parse_args(argv)

    if args.cmd == "ask":
        print(json.dumps(respond(args.message, _j(args.kb)), ensure_ascii=False, indent=1))
        return 0
    if args.cmd == "pilot-generate":
        generate(args.out, args.seed)
        print(f"wrote {args.out}")
        return 0
    eng = _j(args.engagement)
    gate = eng["redteam_gate"] if getattr(args, "gate", "offline") == "redteam" else eng["offline_gate"]
    off = evaluate(load_messages(args.messages), _j(args.kb), gate)
    if args.cmd == "evaluate":
        print(json.dumps({k: off[k] for k in ("metrics", "checks", "passed")}, indent=1))
        for r in off["failures"]:
            print(f"  miss {r['id']}: expected {r['expected_action']}/{r['expected_intent']}, got {r['action']}/{r['intent']}")
        return 0 if off["passed"] else 1
    weeks = weekly(load(args.pilot), eng["pilot_targets"])
    fj, md = write(build(eng, off, weeks), {"tool": "deploykit", "version": __version__}, args.out)
    print(f"wrote {fj} and {md}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
