from __future__ import annotations

from collections import defaultdict

from .model import CandidateEdge


HARD_RELATIONS = {"blocks", "requires_decision", "requires_data", "requires_contract", "requires_information"}


def has_hard_dependency_cycle(edges: tuple[CandidateEdge, ...]) -> bool:
    graph: dict[str, list[str]] = defaultdict(list)
    nodes: set[str] = set()
    for edge in edges:
        if edge.relation not in HARD_RELATIONS:
            continue
        graph[edge.source].append(edge.target)
        nodes.update((edge.source, edge.target))

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str) -> bool:
        if node in visiting:
            return True
        if node in visited:
            return False
        visiting.add(node)
        if any(visit(target) for target in graph.get(node, ())):
            return True
        visiting.remove(node)
        visited.add(node)
        return False

    return any(visit(node) for node in nodes if node not in visited)
