from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class MatchVerdict(str, Enum):
    MATCH = "match"
    NO_MATCH = "no_match"
    ABSTAIN = "abstain"


@dataclass(frozen=True)
class SemanticMatch:
    reference_id: str
    candidate_ids: tuple[str, ...]
    verdict: MatchVerdict
    rationale: str
    judge_id: str
    evidence: tuple[str, ...] = ()


def validate_semantic_match(match: SemanticMatch) -> None:
    if not match.reference_id.strip() or not match.judge_id.strip():
        raise ValueError("semantic match requires reference_id and judge_id")
    if not match.rationale.strip():
        raise ValueError("semantic match requires rationale")
    if match.verdict == MatchVerdict.MATCH and not match.candidate_ids:
        raise ValueError("MATCH requires at least one candidate id")
