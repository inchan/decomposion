from planning_eval.evaluator import evaluate
from planning_eval.model import CandidatePlan, ErrorCode, Kind, ReferenceNode, ReferencePlan, Severity


def test_missing_decision_and_risk_have_specific_error_codes() -> None:
    ref = ReferencePlan(
        "kinds",
        (
            ReferenceNode("d", Kind.DECISION, "retention policy", Severity.CRITICAL),
            ReferenceNode("r", Kind.RISK, "data loss", Severity.MAJOR),
        ),
    )
    score = evaluate(ref, CandidatePlan(()))
    assert score.count(ErrorCode.MISSING_DECISION) == 1
    assert score.count(ErrorCode.MISSING_RISK) == 1
