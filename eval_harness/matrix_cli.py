from __future__ import annotations

import argparse
from pathlib import Path

from .baselines import FixtureStrategy
from .matrix import evaluate_matrix
from .report import markdown_report


def main() -> None:
    parser = argparse.ArgumentParser(description="Run deterministic three-strategy evaluation matrix.")
    parser.add_argument("--golden-dir", default="golden")
    parser.add_argument("--output", default="eval-report.md")
    args = parser.parse_args()

    strategies = [
        FixtureStrategy("plain"),
        FixtureStrategy("structured"),
        FixtureStrategy("decomposion"),
    ]
    results = evaluate_matrix(strategies, Path(args.golden_dir))
    Path(args.output).write_text(markdown_report(results), encoding="utf-8")
    print(f"wrote {args.output} for {len(results)} strategy/case evaluations")


if __name__ == "__main__":
    main()
