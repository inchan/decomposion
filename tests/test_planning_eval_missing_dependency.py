from planning_eval.evaluator import evaluate
from planning_eval.model import CandidateNode, CandidatePlan, ErrorCode, Kind, ReferenceEdge, ReferenceNode, ReferencePlan, Severity


def test_missing_required_dependency_is_detected() -> None:
    ref = ReferencePlan(
        "dep-miss",
        (ReferenceNode("a", Kind.TASK, "a", Severity.MAJOR), ReferenceNode("b", Kind.TASK, "b", Severity.MAJOR)),
        (ReferenceEdge("a", "b", "blocks", Severity.MAJOR),),
    )
    candidate = CandidatePlan((CandidateNode("x", Kind.TASK, "a"), CandidateNode("y", Kind.TASK, "b")))
    score = evaluate(ref, candidate)
    assert score.count(ErrorCode.MISSING_DEPENDENCY) == 1
