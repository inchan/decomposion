from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Severity(str, Enum):
    CRITICAL = "critical"
    MAJOR = "major"
    MINOR = "minor"


class Kind(str, Enum):
    OUTCOME = "outcome"
    TASK = "task"
    DECISION = "decision"
    RISK = "risk"
    UNKNOWN = "unknown"
    DELIVERABLE = "deliverable"


class ErrorCode(str, Enum):
    MISS_CRITICAL = "MISS_CRITICAL"
    MISS_MAJOR = "MISS_MAJOR"
    MISS_MINOR = "MISS_MINOR"
    FALSE_IMPACT = "FALSE_IMPACT"
    UNSUPPORTED_CLAIM = "UNSUPPORTED_CLAIM"
    FALSE_CERTAINTY = "FALSE_CERTAINTY"
    BAD_DEPENDENCY = "BAD_DEPENDENCY"
    MISSING_DEPENDENCY = "MISSING_DEPENDENCY"
    UNDER_DECOMPOSITION = "UNDER_DECOMPOSITION"
    OVER_DECOMPOSITION = "OVER_DECOMPOSITION"
    MISSING_DECISION = "MISSING_DECISION"
    MISSING_RISK = "MISSING_RISK"
    DUPLICATE_PLAN_ITEM = "DUPLICATE_PLAN_ITEM"
    UNTRACEABLE_PLAN_ITEM = "UNTRACEABLE_PLAN_ITEM"


@dataclass(frozen=True)
class ReferenceNode:
    id: str
    kind: Kind
    concept: str
    severity: Severity
    required: bool = True
    acceptable_aliases: tuple[str, ...] = ()
    granularity_group: str | None = None


@dataclass(frozen=True)
class ReferenceEdge:
    source: str
    target: str
    relation: str
    severity: Severity
    required: bool = True


@dataclass(frozen=True)
class UnknownConstraint:
    concept: str
    severity: Severity


@dataclass(frozen=True)
class ReferencePlan:
    case_id: str
    nodes: tuple[ReferenceNode, ...]
    edges: tuple[ReferenceEdge, ...] = ()
    unknowns: tuple[UnknownConstraint, ...] = ()


@dataclass(frozen=True)
class CandidateNode:
    id: str
    kind: Kind
    concept: str
    evidence: tuple[str, ...] = ()
    traces_to: tuple[str, ...] = ()
    epistemic_state: str = "proposed"


@dataclass(frozen=True)
class CandidateEdge:
    source: str
    target: str
    relation: str


@dataclass(frozen=True)
class CandidatePlan:
    nodes: tuple[CandidateNode, ...]
    edges: tuple[CandidateEdge, ...] = ()
    explicit_unknowns: tuple[str, ...] = ()
    asserted_facts: tuple[str, ...] = ()


@dataclass(frozen=True)
class Finding:
    code: ErrorCode
    severity: Severity
    reference_id: str | None
    detail: str


@dataclass
class Scorecard:
    matched_reference_ids: set[str] = field(default_factory=set)
    findings: list[Finding] = field(default_factory=list)
    unadjudicated_novel: list[str] = field(default_factory=list)

    def count(self, code: ErrorCode) -> int:
        return sum(1 for finding in self.findings if finding.code == code)
