from planning_eval.policy import V1_POLICY


def test_v1_policy_is_conservative() -> None:
    assert not V1_POLICY.composite_score_enabled
    assert not V1_POLICY.novel_findings_are_false_positive
    assert not V1_POLICY.silence_counts_as_abstention
    assert V1_POLICY.human_required_for_ambiguous_granularity
