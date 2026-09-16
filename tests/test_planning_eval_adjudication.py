import pytest

from planning_eval.adjudication import AdjudicatedFinding, AdjudicationSource, validate_adjudicated_finding
from planning_eval.model import ErrorCode, Severity


def test_under_decomposition_requires_adjudication_evidence() -> None:
    finding = AdjudicatedFinding(
        code=ErrorCode.UNDER_DECOMPOSITION,
        severity=Severity.MAJOR,
        detail="RAG integration hides independently reviewable authorization and citation work",
        source=AdjudicationSource.HUMAN,
    )
    with pytest.raises(ValueError, match="evidence"):
        validate_adjudicated_finding(finding)


def test_over_decomposition_can_be_recorded_with_rationale() -> None:
    finding = AdjudicatedFinding(
        code=ErrorCode.OVER_DECOMPOSITION,
        severity=Severity.MINOR,
        detail="three identical formatting subtasks add no planning information",
        source=AdjudicationSource.HUMAN,
        evidence=("reviewer: redundant units have identical dependency/evidence boundaries",),
    )
    validate_adjudicated_finding(finding)
