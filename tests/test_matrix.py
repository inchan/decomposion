from pathlib import Path

from eval_harness.baselines import FixtureStrategy
from eval_harness.matrix import evaluate_matrix
from eval_harness.report import markdown_report, summarize


def test_fixture_matrix_compares_strategies():
    strategies = [
        FixtureStrategy("plain", concepts={"authorization_policy_needed"}),
        FixtureStrategy(
            "structured",
            concepts={"authorization_policy_needed", "sharing_principal_scope_decision", "revoke_or_permission_change_semantics"},
        ),
        FixtureStrategy(
            "decomposion",
            concepts={"authorization_policy_needed", "sharing_principal_scope_decision", "revoke_or_permission_change_semantics"},
        ),
    ]
    results = evaluate_matrix(strategies, Path("golden"))
    assert results
    summary = summarize(results)
    assert set(summary) == {"plain", "structured", "decomposion"}
    report = markdown_report(results)
    assert "Decomposion Evaluation Matrix" in report
    assert "Abstention accuracy" in report
