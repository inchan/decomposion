from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class Score:
    required_total: int
    required_hit: int
    forbidden_total: int
    forbidden_hit: int
    abstain_total: int
    abstain_hit: int

    @property
    def recall(self) -> float:
        return 1.0 if self.required_total == 0 else self.required_hit / self.required_total

    @property
    def forbidden_rate(self) -> float:
        return 0.0 if self.forbidden_total == 0 else self.forbidden_hit / self.forbidden_total

    @property
    def abstention_accuracy(self) -> float:
        return 1.0 if self.abstain_total == 0 else self.abstain_hit / self.abstain_total


def normalize_concepts(values: Iterable[str]) -> set[str]:
    return {str(v).strip().lower() for v in values if str(v).strip()}


def score_concepts(*, produced: Iterable[str], required: Iterable[str] = (),
                   forbidden: Iterable[str] = (), abstained: Iterable[str] = (),
                   expected_abstentions: Iterable[str] = ()) -> Score:
    """Score explicit concept IDs, not semantic correctness of arbitrary prose.

    `abstained` is the actual model output; `expected_abstentions` is the rubric.
    Silence is not a correct abstention, and asserting AND abstaining on the same
    concept cannot earn abstention credit. Undefined metrics retain their legacy
    neutral values; inspect totals before interpreting percentages.
    """
    produced_set = normalize_concepts(produced)
    required_set = normalize_concepts(required)
    forbidden_set = normalize_concepts(forbidden)
    abstained_set = normalize_concepts(abstained)
    expected_set = normalize_concepts(expected_abstentions)
    return Score(
        required_total=len(required_set), required_hit=len(required_set & produced_set),
        forbidden_total=len(forbidden_set), forbidden_hit=len(forbidden_set & produced_set),
        abstain_total=len(expected_set),
        abstain_hit=len((expected_set & abstained_set) - produced_set),
    )


def passes_smoke_gate(score: Score, *, min_recall: float = 0.8, max_forbidden_rate: float = 0.0,
                      min_abstention_accuracy: float = 1.0) -> bool:
    return (score.recall >= min_recall and score.forbidden_rate <= max_forbidden_rate
            and score.abstention_accuracy >= min_abstention_accuracy)
