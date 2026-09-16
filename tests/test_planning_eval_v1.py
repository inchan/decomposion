from planning_eval.evaluator import evaluate
from planning_eval.model import (
    CandidateEdge,
    CandidateNode,
    CandidatePlan,
    ErrorCode,
    Kind,
    ReferenceEdge,
    ReferenceNode,
    ReferencePlan,
    Severity,
    UnknownConstraint,
)


def reference() -> ReferencePlan:
    return ReferencePlan(
        case_id="self-test",
        nodes=(
            ReferenceNode("policy", Kind.DECISION, "permission policy", Severity.CRITICAL),
            ReferenceNode("auth", Kind.TASK, "retrieval authorization", Severity.CRITICAL, acceptable_aliases=("authorize retrieval against document permissions",)),
            ReferenceNode("risk", Kind.RISK, "revocation leakage", Severity.MAJOR),
        ),
        edges=(ReferenceEdge("policy", "auth", "requires_decision", Severity.CRITICAL),),
        unknowns=(UnknownConstraint("cache existence", Severity.MAJOR),),
    )


def good() -> CandidatePlan:
    return CandidatePlan(
        nodes=(
            CandidateNode("c-policy", Kind.DECISION, "permission policy"),
            CandidateNode("c-auth", Kind.TASK, "authorize retrieval against document permissions"),
            CandidateNode("c-risk", Kind.RISK, "revocation leakage"),
        ),
        edges=(CandidateEdge("c-policy", "c-auth", "requires_decision"),),
        explicit_unknowns=("cache existence",),
    )


def test_equivalent_alias_is_not_a_miss() -> None:
    score = evaluate(reference(), good())
    assert not score.findings


def test_remove_critical_obligation_is_detected() -> None:
    plan = good()
    broken = CandidatePlan(nodes=tuple(n for n in plan.nodes if n.id != "c-auth"), edges=(), explicit_unknowns=plan.explicit_unknowns)
    score = evaluate(reference(), broken)
    assert score.count(ErrorCode.MISS_CRITICAL) == 1


def test_unknown_promoted_to_fact_is_false_certainty() -> None:
    plan = good()
    broken = CandidatePlan(nodes=plan.nodes, edges=plan.edges, asserted_facts=("cache existence",))
    score = evaluate(reference(), broken)
    assert score.count(ErrorCode.FALSE_CERTAINTY) == 1


def test_silence_is_not_abstention() -> None:
    plan = good()
    broken = CandidatePlan(nodes=plan.nodes, edges=plan.edges)
    score = evaluate(reference(), broken)
    assert score.count(ErrorCode.FALSE_CERTAINTY) == 1


def test_reverse_required_dependency_is_bad_dependency() -> None:
    plan = good()
    broken = CandidatePlan(
        nodes=plan.nodes,
        edges=(CandidateEdge("c-auth", "c-policy", "requires_decision"),),
        explicit_unknowns=plan.explicit_unknowns,
    )
    score = evaluate(reference(), broken)
    assert score.count(ErrorCode.BAD_DEPENDENCY) == 1


def test_novel_item_is_not_automatically_false_positive() -> None:
    plan = good()
    candidate = CandidatePlan(
        nodes=plan.nodes + (CandidateNode("novel", Kind.RISK, "unexpected but plausible risk"),),
        edges=plan.edges,
        explicit_unknowns=plan.explicit_unknowns,
    )
    score = evaluate(reference(), candidate)
    assert score.unadjudicated_novel == ["novel"]
    assert not score.findings
