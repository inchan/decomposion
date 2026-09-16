from __future__ import annotations

from dataclasses import dataclass

from .model import Kind, ReferencePlan, Scorecard, Severity


@dataclass(frozen=True)
class CoverageMetrics:
    critical_coverage: float
    major_coverage: float
    minor_coverage: float
    decision_recall: float
    risk_recall: float


def _ratio(matched: int, total: int) -> float:
    return 1.0 if total == 0 else matched / total


def coverage_metrics(reference: ReferencePlan, score: Scorecard) -> CoverageMetrics:
    required = [node for node in reference.nodes if node.required]

    def coverage(*, severity: Severity | None = None, kind: Kind | None = None) -> float:
        subset = [
            node for node in required
            if (severity is None or node.severity == severity) and (kind is None or node.kind == kind)
        ]
        return _ratio(sum(node.id in score.matched_reference_ids for node in subset), len(subset))

    return CoverageMetrics(
        critical_coverage=coverage(severity=Severity.CRITICAL),
        major_coverage=coverage(severity=Severity.MAJOR),
        minor_coverage=coverage(severity=Severity.MINOR),
        decision_recall=coverage(kind=Kind.DECISION),
        risk_recall=coverage(kind=Kind.RISK),
    )
