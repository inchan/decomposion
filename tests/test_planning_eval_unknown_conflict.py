from planning_eval.evaluator import evaluate
from planning_eval.model import CandidatePlan, ErrorCode, ReferencePlan, Severity, UnknownConstraint


def test_asserting_and_abstaining_same_unknown_still_fails() -> None:
    ref = ReferencePlan("unknown", (), unknowns=(UnknownConstraint("cache existence", Severity.CRITICAL),))
    candidate = CandidatePlan((), explicit_unknowns=("cache existence",), asserted_facts=("cache existence",))
    score = evaluate(ref, candidate)
    assert score.count(ErrorCode.FALSE_CERTAINTY) == 1
