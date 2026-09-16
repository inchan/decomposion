from __future__ import annotations

from dataclasses import dataclass

from .evaluator import evaluate
from .model import CandidateEdge, CandidateNode, CandidatePlan, ErrorCode, Kind, ReferenceEdge, ReferenceNode, ReferencePlan, Severity, UnknownConstraint


@dataclass(frozen=True)
class SelfTestResult:
    name: str
    expected: ErrorCode | None
    observed: tuple[ErrorCode, ...]

    @property
    def passed(self) -> bool:
        return (self.expected is None and not self.observed) or (self.expected in self.observed)


def run_selftests() -> tuple[SelfTestResult, ...]:
    ref = ReferencePlan(
        "eval-selftest",
        (
            ReferenceNode("decision", Kind.DECISION, "permission policy", Severity.CRITICAL),
            ReferenceNode("task", Kind.TASK, "retrieval authorization", Severity.CRITICAL, acceptable_aliases=("authorize retrieval against document permissions",)),
        ),
        (ReferenceEdge("decision", "task", "requires_decision", Severity.CRITICAL),),
        (UnknownConstraint("cache existence", Severity.MAJOR),),
    )
    good = CandidatePlan(
        (
            CandidateNode("d", Kind.DECISION, "permission policy"),
            CandidateNode("t", Kind.TASK, "authorize retrieval against document permissions"),
        ),
        (CandidateEdge("d", "t", "requires_decision"),),
        ("cache existence",),
    )
    scenarios = (
        ("equivalent_alias", None, good),
        ("critical_omission", ErrorCode.MISS_CRITICAL, CandidatePlan((good.nodes[0],), explicit_unknowns=good.explicit_unknowns)),
        ("false_certainty", ErrorCode.FALSE_CERTAINTY, CandidatePlan(good.nodes, good.edges, asserted_facts=("cache existence",))),
        ("reversed_dependency", ErrorCode.BAD_DEPENDENCY, CandidatePlan(good.nodes, (CandidateEdge("t", "d", "requires_decision"),), good.explicit_unknowns)),
    )
    return tuple(
        SelfTestResult(name, expected, tuple(f.code for f in evaluate(ref, candidate).findings))
        for name, expected, candidate in scenarios
    )
