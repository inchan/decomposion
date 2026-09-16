from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EvalPolicy:
    version: str = "planning-eval-v1-dev"
    composite_score_enabled: bool = False
    novel_findings_are_false_positive: bool = False
    silence_counts_as_abstention: bool = False
    human_required_for_ambiguous_granularity: bool = True


V1_POLICY = EvalPolicy()
