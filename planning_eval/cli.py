from __future__ import annotations

import argparse
import json

from .selftest import run_selftests


def main() -> int:
    parser = argparse.ArgumentParser(description="Planning Eval v1 utilities")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("selftest", help="run controlled evaluator mutation checks")
    args = parser.parse_args()
    if args.command == "selftest":
        results = run_selftests()
        print(json.dumps([
            {"name": r.name, "expected": r.expected.value if r.expected else None, "observed": [v.value for v in r.observed], "passed": r.passed}
            for r in results
        ], indent=2))
        return 0 if all(r.passed for r in results) else 1
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
