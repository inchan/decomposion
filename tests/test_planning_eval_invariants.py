from planning_eval.invariants import has_hard_dependency_cycle
from planning_eval.model import CandidateEdge


def test_hard_cycle_is_detected() -> None:
    edges = (
        CandidateEdge("a", "b", "blocks"),
        CandidateEdge("b", "c", "requires_decision"),
        CandidateEdge("c", "a", "requires_information"),
    )
    assert has_hard_dependency_cycle(edges)


def test_nonblocking_impact_relation_does_not_create_execution_cycle() -> None:
    edges = (
        CandidateEdge("a", "b", "impacts"),
        CandidateEdge("b", "a", "impacts"),
    )
    assert not has_hard_dependency_cycle(edges)
