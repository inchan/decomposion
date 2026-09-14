from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .baselines import EvalInput, Strategy
from .golden import GoldenCase, load_case
from .scoring import score_case


@dataclass(frozen=True)
class StrategyResult:
    strategy: str
    case_id: str
    score: float
    details: dict


def evaluate_strategy(strategy: Strategy, case: GoldenCase) -> StrategyResult:
    item = EvalInput(
        case_id=case.case_id,
        context=case.data["context"],
        change=case.data["change"],
    )
    output = strategy.run(item)
    scored = score_case(
        case.data,
        concepts=output.concepts,
        abstentions=output.abstentions,
    )
    return StrategyResult(
        strategy=strategy.name,
        case_id=case.case_id,
        score=float(scored["score"]),
        details={**scored, "metadata": output.metadata},
    )


def evaluate_matrix(strategies: list[Strategy], golden_dir: str | Path) -> list[StrategyResult]:
    root = Path(golden_dir)
    cases = [load_case(path) for path in sorted(root.rglob("*.yaml"))]
    return [evaluate_strategy(strategy, case) for strategy in strategies for case in cases]
