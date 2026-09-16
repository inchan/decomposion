from __future__ import annotations

from collections import defaultdict
from statistics import mean

from .matrix import StrategyResult


def summarize(results: list[StrategyResult]) -> dict[str, dict[str, float]]:
    grouped: dict[str, list[StrategyResult]] = defaultdict(list)
    for result in results:
        grouped[result.strategy].append(result)

    summary: dict[str, dict[str, float]] = {}
    for strategy, items in grouped.items():
        summary[strategy] = {
            "recall": mean(item.score.recall for item in items),
            "forbidden_rate": mean(item.score.forbidden_rate for item in items),
            "abstention_accuracy": mean(item.score.abstention_accuracy for item in items),
        }
    return summary


def markdown_report(results: list[StrategyResult]) -> str:
    summary = summarize(results)
    lines = [
        "# Decomposion Evaluation Matrix",
        "",
        "FIXTURE ONLY — wiring/scorer verification, not model quality."
        if results and all(r.metadata.get("provider") == "fixture" for r in results)
        else "Concept-ID scores require independent semantic/evidence review; they are not proof of correctness.",
        "",
        "| Strategy | Recall | Forbidden rate | Abstention accuracy |",
        "|---|---:|---:|---:|",
    ]
    for strategy in sorted(summary):
        row = summary[strategy]
        lines.append(
            f"| {strategy} | {row['recall']:.1%} | {row['forbidden_rate']:.1%} | {row['abstention_accuracy']:.1%} |"
        )
    lines.extend(["", "## Per case", ""])
    for item in sorted(results, key=lambda r: (r.case_id, r.strategy)):
        lines.append(
            f"- `{item.case_id}` / **{item.strategy}**: recall {item.score.recall:.1%}, "
            f"forbidden {item.score.forbidden_rate:.1%}, abstention {item.score.abstention_accuracy:.1%}"
        )
    return "\n".join(lines) + "\n"
