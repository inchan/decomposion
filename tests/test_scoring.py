from eval_harness.scoring import passes_smoke_gate, score_concepts


def test_required_and_forbidden_scoring() -> None:
    score = score_concepts(produced=["retrieval_authorization", "payment_gateway"],
                           required=["retrieval_authorization", "tenant_boundary"],
                           forbidden=["payment_gateway"])
    assert score.recall == 0.5
    assert score.forbidden_rate == 1.0
    assert not passes_smoke_gate(score)


def test_explicit_abstention_is_required() -> None:
    expected = ["redis_cache_exists", "vector_database_exists"]
    score = score_concepts(produced=["authorization_policy_needed"],
                           required=["authorization_policy_needed"],
                           abstained=expected, expected_abstentions=expected)
    assert score.abstention_accuracy == 1.0
    assert passes_smoke_gate(score)


def test_silence_is_not_abstention() -> None:
    score = score_concepts(produced=[], expected_abstentions=["cache_exists"])
    assert score.abstention_accuracy == 0.0
    assert not passes_smoke_gate(score)


def test_contradictory_assertion_cannot_earn_abstention_credit() -> None:
    score = score_concepts(produced=["CACHE_EXISTS"], abstained=["cache_exists"],
                           expected_abstentions=["cache_exists"])
    assert score.abstention_accuracy == 0.0


def test_abstentions_do_not_define_their_own_denominator() -> None:
    score = score_concepts(produced=[], abstained=["easy", "irrelevant"],
                           expected_abstentions=["easy", "hard"])
    assert score.abstain_total == 2
    assert score.abstention_accuracy == 0.5
