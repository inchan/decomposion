from __future__ import annotations

import argparse
import json
from pathlib import Path

from . import __version__
from .core import evaluate, load_json
from .experiment import cases, dump_new, judge, prepare, report, run
from .selftest import selftest


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Evidence-backed planning evaluation; no model calls without --execute.")
    parser.add_argument("--version", action="version", version=__version__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("check", help="validate the three packaged development references")
    sub.add_parser("selftest", help="controlled evaluator checks, not model-quality scores")
    prep = sub.add_parser("prepare", help="verify pinned Git source and freeze identical evidence for all strategies")
    prep.add_argument("--repo", required=True, type=Path)
    prep.add_argument("--out", required=True, type=Path)
    execute = sub.add_parser("run", help="preview or explicitly execute bounded local/cloud model calls")
    execute.add_argument("--packet", required=True, type=Path)
    execute.add_argument("--config", required=True, type=Path)
    execute.add_argument("--out", required=True, type=Path)
    execute.add_argument("--repeats", type=int, default=1)
    execute.add_argument("--seed", type=int, default=17)
    execute.add_argument("--strategies", nargs="+")
    execute.add_argument("--max-calls", type=int, default=21)
    execute.add_argument("--execute", action="store_true")
    assessment = sub.add_parser("judge", help="optional uncalibrated LLM review; never a certified quality verdict")
    assessment.add_argument("--run", required=True, type=Path)
    assessment.add_argument("--config", required=True, type=Path)
    assessment.add_argument("--max-calls", type=int, default=12)
    assessment.add_argument("--execute", action="store_true")
    score = sub.add_parser("score", help="check a plan and count provenance-bound review labels")
    score.add_argument("--case", required=True, type=Path)
    score.add_argument("--plan", required=True, type=Path)
    score.add_argument("--review", type=Path)
    score.add_argument("--out", required=True, type=Path)
    summary = sub.add_parser("report", help="show per-trial results, including pending and failed trials")
    summary.add_argument("--run", required=True, type=Path)
    summary.add_argument("--out", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "check":
            suite = cases()
            value = {"cases": len(suite), "obligations": sum(len(c["obligations"]) for c in suite),
                     "dependencies": sum(len(c["dependencies"]) for c in suite), "reference_validated": False}
        elif args.command == "selftest":
            value = selftest()
            print(json.dumps(value, indent=2))
            return 0 if all(row["passed"] for row in value) else 1
        elif args.command == "prepare":
            value = prepare(args.repo, args.out)
        elif args.command == "run":
            value = run(args.packet, load_json(args.config), args.out, args.repeats, args.seed,
                        args.strategies, args.max_calls, args.execute)
        elif args.command == "judge":
            value = judge(args.run, load_json(args.config), args.max_calls, args.execute)
        elif args.command == "score":
            value = evaluate(load_json(args.case), load_json(args.plan), load_json(args.review) if args.review else None)
            dump_new(args.out, value)
        else:
            value = report(args.run)
            if args.out:
                with args.out.open("x", encoding="utf-8") as stream:
                    stream.write(value)
            print(value)
            return 0
        print(json.dumps(value, ensure_ascii=False, indent=2))
        return 1 if isinstance(value, dict) and value.get("failed_plans", 0) else 0
    except (ValueError, OSError, TimeoutError) as exc:
        # Remote exception strings may include keys, body content or credentials.
        if args.command in {"run", "judge"} and args.execute:
            print(f"ERROR: {type(exc).__name__}; inspect saved artifacts/config; no automatic retry.")
        else:
            print(f"ERROR: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
