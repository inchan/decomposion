from __future__ import annotations

from dataclasses import dataclass

from .model import CandidatePlan, ReferencePlan


@dataclass(frozen=True)
class DependencyMetrics:
    required_total: int
    satisfied: int

    @property
    def recall(self) -> float:
        return 1.0 if self.required_total == 0 else self.satisfied / self.required_total


def exact_dependency_metrics(reference: ReferencePlan, candidate: CandidatePlan, ref_to_candidate: dict[str, str]) -> DependencyMetrics:
    """Exact structural dependency metric after semantic node matching.

    `ref_to_candidate` must come from the semantic matching layer in production.
    Tests may supply it directly.
    """
    required = [edge for edge in reference.edges if edge.required]
    candidate_edges = {(edge.source, edge.target, edge.relation) for edge in candidate.edges}
    satisfied = 0
    for edge in required:
        source = ref_to_candidate.get(edge.source)
        target = ref_to_candidate.get(edge.target)
        if source and target and (source, target, edge.relation) in candidate_edges:
            satisfied += 1
    return DependencyMetrics(len(required), satisfied)
