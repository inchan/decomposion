from planning_eval.non_goals import NON_GOALS


def test_visual_review_is_not_scored_by_planning_eval_v1() -> None:
    assert "visual_aesthetics" in NON_GOALS
    assert "human_review_time" in NON_GOALS
