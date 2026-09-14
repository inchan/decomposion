from eval_harness.scoring import passes_smoke_gate, score_concepts


def test_required_and_forbidden_scoring() -> None:
    score = score_concepts(
        produced=["retrieval_authorization", "payment_gateway"],
        required=["retrieval_authorization", "tenant_boundary"],
        forbidden=["payment_gateway"],
    )
    assert score.recall == 0.5
    assert score.forbidden_rate == 1.0
    assert not passes_smoke_gate(score)


def test_abstention_rewards_not_inventing_unknowns() -> None:
    score = score_concepts(
        produced=["authorization_policy_needed"],
        required=["authorization_policy_needed"],
        abstained=["redis_cache_exists", "vector_database_exists"],
    )
    assert score.recall == 1.0
    assert score.abstention_accuracy == 1.0
    assert passes_smoke_gate(score)
