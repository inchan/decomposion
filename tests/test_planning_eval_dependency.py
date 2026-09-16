from planning_eval.dependency import exact_dependency_metrics
from planning_eval.model import CandidateEdge, CandidateNode, CandidatePlan, Kind, ReferenceEdge, ReferenceNode, ReferencePlan, Severity


def test_dependency_recall_uses_matched_node_mapping() -> None:
    ref = ReferencePlan(
        "dep",
        (ReferenceNode("a", Kind.DECISION, "a", Severity.CRITICAL), ReferenceNode("b", Kind.TASK, "b", Severity.CRITICAL)),
        (ReferenceEdge("a", "b", "requires_decision", Severity.CRITICAL),),
    )
    candidate = CandidatePlan(
        (CandidateNode("x", Kind.DECISION, "a"), CandidateNode("y", Kind.TASK, "b")),
        (CandidateEdge("x", "y", "requires_decision"),),
    )
    metrics = exact_dependency_metrics(ref, candidate, {"a": "x", "b": "y"})
    assert metrics.recall == 1.0
