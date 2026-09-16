from planning_eval.evaluator import evaluate
from planning_eval.model import CandidateNode, CandidatePlan, Kind, ReferenceNode, ReferencePlan, Severity
from planning_eval.scorecard import coverage_metrics


def test_coverage_is_reported_by_severity_and_kind() -> None:
    ref = ReferencePlan(
        "score",
        (
            ReferenceNode("critical", Kind.TASK, "critical work", Severity.CRITICAL),
            ReferenceNode("major", Kind.TASK, "major work", Severity.MAJOR),
            ReferenceNode("decision", Kind.DECISION, "policy choice", Severity.CRITICAL),
            ReferenceNode("risk", Kind.RISK, "data loss", Severity.MAJOR),
        ),
    )
    candidate = CandidatePlan(
        nodes=(
            CandidateNode("c1", Kind.TASK, "critical work"),
            CandidateNode("c2", Kind.DECISION, "policy choice"),
        )
    )
    metrics = coverage_metrics(ref, evaluate(ref, candidate))
    assert metrics.critical_coverage == 1.0
    assert metrics.major_coverage == 0.0
    assert metrics.decision_recall == 1.0
    assert metrics.risk_recall == 0.0
