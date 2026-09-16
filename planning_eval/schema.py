from __future__ import annotations

from .model import ReferencePlan


class ReferencePlanError(ValueError):
    pass


def validate_reference(plan: ReferencePlan) -> None:
    if not plan.case_id.strip():
        raise ReferencePlanError("case_id must be non-empty")
    ids = [node.id for node in plan.nodes]
    if len(ids) != len(set(ids)):
        raise ReferencePlanError("reference node ids must be unique")
    known = set(ids)
    for node in plan.nodes:
        if not node.id.strip() or not node.concept.strip():
            raise ReferencePlanError("reference nodes require non-empty id and concept")
    for edge in plan.edges:
        if edge.source not in known or edge.target not in known:
            raise ReferencePlanError(f"dangling reference edge: {edge.source} -> {edge.target}")
        if edge.source == edge.target:
            raise ReferencePlanError("self dependency is not allowed")
        if not edge.relation.strip():
            raise ReferencePlanError("edge relation must be non-empty")
