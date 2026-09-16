from pathlib import Path


def test_step1_acceptance_artifacts_exist() -> None:
    required = [
        "docs/PLANNING_EVAL_V1.md",
        "docs/PLANNING_EVAL_V1_REVIEW.md",
        "docs/PLANNING_EVAL_V1_SCORECARD.md",
        "docs/PLANNING_EVAL_V1_BASELINES.md",
        "docs/PLANNING_EVAL_V1_TEST_MATRIX.md",
        "docs/PLANNING_EVAL_V1_SCHEMA.yaml",
    ]
    assert all(Path(path).is_file() for path in required)
