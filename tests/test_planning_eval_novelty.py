from planning_eval.evaluator import evaluate
from planning_eval.model import CandidateNode, CandidatePlan, Kind, ReferencePlan


def test_novel_finding_is_neutral_before_adjudication() -> None:
    candidate = CandidatePlan((CandidateNode("novel", Kind.RISK, "new evidence-backed concern", evidence=("repo:file.py:10",)),))
    score = evaluate(ReferencePlan("novel", ()), candidate)
    assert score.unadjudicated_novel == ["novel"]
    assert score.findings == []
