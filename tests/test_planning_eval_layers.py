from planning_eval.layers import DETERMINISTIC_RESPONSIBILITIES, HUMAN_RESPONSIBILITIES, SEMANTIC_RESPONSIBILITIES


def test_evaluation_layers_do_not_overlap() -> None:
    deterministic = set(DETERMINISTIC_RESPONSIBILITIES)
    semantic = set(SEMANTIC_RESPONSIBILITIES)
    human = set(HUMAN_RESPONSIBILITIES)
    assert deterministic.isdisjoint(semantic)
    assert deterministic.isdisjoint(human)
    assert semantic.isdisjoint(human)
