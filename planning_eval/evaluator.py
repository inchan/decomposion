from __future__ import annotations

from .model import (
    CandidatePlan,
    ErrorCode,
    Finding,
    Kind,
    ReferenceNode,
    ReferencePlan,
    Scorecard,
    Severity,
)


def _norm(text: str) -> str:
    return " ".join(text.lower().replace("_", " ").replace("-", " ").split())


def _exact_or_alias_match(reference: ReferenceNode, concept: str) -> bool:
    """Deterministic matcher for evaluator self-tests only.

    Real semantic equivalence belongs to the semantic/human layers. Keeping this
    deliberately narrow prevents the deterministic layer from pretending to be
    a semantic judge.
    """
    candidate = _norm(concept)
    return candidate in {_norm(reference.concept), *(_norm(v) for v in reference.acceptable_aliases)}


def _miss_code(severity: Severity, kind: Kind) -> ErrorCode:
    if kind == Kind.DECISION:
        return ErrorCode.MISSING_DECISION
    if kind == Kind.RISK:
        return ErrorCode.MISSING_RISK
    return {
        Severity.CRITICAL: ErrorCode.MISS_CRITICAL,
        Severity.MAJOR: ErrorCode.MISS_MAJOR,
        Severity.MINOR: ErrorCode.MISS_MINOR,
    }[severity]


def evaluate(reference: ReferencePlan, candidate: CandidatePlan) -> Scorecard:
    score = Scorecard()
    candidate_by_id = {node.id: node for node in candidate.nodes}
    if len(candidate_by_id) != len(candidate.nodes):
        score.findings.append(Finding(ErrorCode.DUPLICATE_PLAN_ITEM, Severity.MAJOR, None, "duplicate candidate node id"))

    matched_candidate_ids: set[str] = set()
    ref_to_candidate: dict[str, str] = {}
    for ref in reference.nodes:
        match = next((node for node in candidate.nodes if _exact_or_alias_match(ref, node.concept)), None)
        if match:
            score.matched_reference_ids.add(ref.id)
            matched_candidate_ids.add(match.id)
            ref_to_candidate[ref.id] = match.id
        elif ref.required:
            score.findings.append(Finding(_miss_code(ref.severity, ref.kind), ref.severity, ref.id, f"missing required concept: {ref.concept}"))

    edge_keys = {(edge.source, edge.target, edge.relation) for edge in candidate.edges}
    for edge in reference.edges:
        if not edge.required:
            continue
        source = ref_to_candidate.get(edge.source)
        target = ref_to_candidate.get(edge.target)
        if source and target and (source, target, edge.relation) not in edge_keys:
            reverse = (target, source, edge.relation) in edge_keys
            code = ErrorCode.BAD_DEPENDENCY if reverse else ErrorCode.MISSING_DEPENDENCY
            score.findings.append(Finding(code, edge.severity, None, f"dependency {edge.source} -> {edge.target} ({edge.relation}) not satisfied"))

    unknown_norm = {_norm(value) for value in candidate.explicit_unknowns}
    facts_norm = {_norm(value) for value in candidate.asserted_facts}
    for constraint in reference.unknowns:
        concept = _norm(constraint.concept)
        if concept in facts_norm:
            score.findings.append(Finding(ErrorCode.FALSE_CERTAINTY, constraint.severity, None, f"unknown asserted as fact: {constraint.concept}"))
        elif concept not in unknown_norm:
            score.findings.append(Finding(ErrorCode.FALSE_CERTAINTY, constraint.severity, None, f"required uncertainty not explicit: {constraint.concept}"))

    for node in candidate.nodes:
        if node.id not in matched_candidate_ids:
            score.unadjudicated_novel.append(node.id)

    return score
