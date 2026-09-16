from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .model import ErrorCode, Severity


class AdjudicationSource(str, Enum):
    SEMANTIC_JUDGE = "semantic_judge"
    HUMAN = "human"


@dataclass(frozen=True)
class AdjudicatedFinding:
    code: ErrorCode
    severity: Severity
    detail: str
    source: AdjudicationSource
    reference_id: str | None = None
    evidence: tuple[str, ...] = ()


def validate_adjudicated_finding(finding: AdjudicatedFinding) -> None:
    if not finding.detail.strip():
        raise ValueError("adjudicated finding requires detail")
    if finding.code in {ErrorCode.UNDER_DECOMPOSITION, ErrorCode.OVER_DECOMPOSITION} and not finding.evidence:
        raise ValueError("granularity findings require evidence/rationale")
