from planning_eval.scorecard import CoverageMetrics


def test_v1_coverage_metrics_have_no_composite_score() -> None:
    metrics = CoverageMetrics(1.0, 1.0, 1.0, 1.0, 1.0)
    assert not hasattr(metrics, "total_score")
    assert not hasattr(metrics, "overall")
