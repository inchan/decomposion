import pytest

from planning_eval.model import Kind, ReferenceEdge, ReferenceNode, ReferencePlan, Severity
from planning_eval.schema import ReferencePlanError, validate_reference


def node(node_id: str) -> ReferenceNode:
    return ReferenceNode(node_id, Kind.TASK, node_id, Severity.MAJOR)


def test_valid_reference_graph() -> None:
    validate_reference(ReferencePlan("case", (node("a"), node("b")), (ReferenceEdge("a", "b", "blocks", Severity.MAJOR),)))


def test_duplicate_reference_ids_fail() -> None:
    with pytest.raises(ReferencePlanError, match="unique"):
        validate_reference(ReferencePlan("case", (node("a"), node("a"))))


def test_dangling_reference_edge_fails() -> None:
    with pytest.raises(ReferencePlanError, match="dangling"):
        validate_reference(ReferencePlan("case", (node("a"),), (ReferenceEdge("a", "missing", "blocks", Severity.MAJOR),)))
