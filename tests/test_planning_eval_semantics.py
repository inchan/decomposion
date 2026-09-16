import pytest

from planning_eval.semantics import MatchVerdict, SemanticMatch, validate_semantic_match


def test_semantic_match_requires_candidate() -> None:
    match = SemanticMatch("ref", (), MatchVerdict.MATCH, "equivalent planning obligation", "judge-v1")
    with pytest.raises(ValueError, match="candidate"):
        validate_semantic_match(match)


def test_semantic_abstention_is_first_class() -> None:
    match = SemanticMatch("ref", (), MatchVerdict.ABSTAIN, "insufficient evidence to decide equivalence", "judge-v1")
    validate_semantic_match(match)
