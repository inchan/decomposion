from planning_eval.status import CAPABILITIES


def test_step1_does_not_claim_unimplemented_quality_judging() -> None:
    assert CAPABILITIES["reference_constraint_model"]
    assert CAPABILITIES["deterministic_selftests"]
    assert not CAPABILITIES["real_semantic_matcher"]
    assert not CAPABILITIES["judge_calibrated"]
    assert not CAPABILITIES["deep_reference_cases"]
    assert not CAPABILITIES["visual_review_eval"]
