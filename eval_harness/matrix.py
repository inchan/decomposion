from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from .baselines import EvalInput, Strategy
from .golden import GoldenCase, GoldenCaseError, load_case
from .scoring import Score, score_concepts


@dataclass(frozen=True)
class StrategyResult:
    strategy: str
    case_id: str
    score: Score
    metadata: dict


def _strings(values: object) -> list[str]:
    if not isinstance(values, list):
        return []
    return [str(v) for v in values if isinstance(v, (str, int, float))]


def _collect_expected(case: GoldenCase) -> tuple[set[str], set[str], set[str]]:
    data = case.data
    expected = data.get("expected") if isinstance(data.get("expected"), dict) else {}
    required: set[str] = set()
    forbidden: set[str] = set()
    abstain: set[str] = set()
    for section_name in ("outcomes", "impacted_domains", "hidden_concerns", "decisions", "risks"):
        section = expected.get(section_name)
        if isinstance(section, dict):
            required.update(_strings(section.get("must_detect")))
            forbidden.update(_strings(section.get("must_not_invent")))
    required.update(_strings(expected.get("must_detect")))
    noise = expected.get("noise")
    if isinstance(noise, dict):
        forbidden.update(_strings(noise.get("forbidden_or_irrelevant")))
    unknowns = expected.get("unknowns")
    if isinstance(unknowns, dict):
        abstain.update(_strings(unknowns.get("should_abstain_on")))
    forbidden.update(_strings(expected.get("must_not_claim_as_fact")))
    adversarial = data.get("adversarial")
    if isinstance(adversarial, dict):
        abstain.update(_strings(adversarial.get("must_abstain_on")))
        forbidden.update(_strings(adversarial.get("must_not_invent")))
    return required, forbidden, abstain


def evaluate_strategy(strategy: Strategy, case: GoldenCase) -> StrategyResult:
    # A strategy receives no gold labels, and cannot mutate context for later arms.
    item = EvalInput(case_id=case.case_id, context=deepcopy(case.data["context"]), change=case.data["change"])
    output = strategy.run(item)
    required, forbidden, abstain = _collect_expected(case)
    score = score_concepts(produced=output.concepts, required=required, forbidden=forbidden,
                           abstained=output.abstentions, expected_abstentions=abstain)
    return StrategyResult(strategy=strategy.name, case_id=case.case_id, score=score, metadata=output.metadata)


def evaluate_matrix(strategies: Iterable[Strategy], golden_dir: str | Path) -> list[StrategyResult]:
    strategies = list(strategies)
    if not strategies or len({s.name for s in strategies}) != len(strategies):
        raise ValueError("Provide a non-empty list of uniquely named strategies")
    root = Path(golden_dir)
    cases = [load_case(path) for path in sorted(root.rglob("*.yaml"))]
    if not cases:
        raise GoldenCaseError(f"No golden cases found under {root}")
    if len({c.case_id for c in cases}) != len(cases):
        raise GoldenCaseError("Duplicate golden case identifiers")
    return [evaluate_strategy(strategy, case) for strategy in strategies for case in cases]
