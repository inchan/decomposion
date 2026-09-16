from __future__ import annotations

from .model import CandidatePlan


def untraceable_node_ids(plan: CandidatePlan) -> tuple[str, ...]:
    """Return nodes with neither evidence nor explicit trace links.

    This is structural only. Whether a trace/evidence citation is substantively
    valid remains a semantic/human judgment.
    """
    return tuple(node.id for node in plan.nodes if not node.evidence and not node.traces_to)
