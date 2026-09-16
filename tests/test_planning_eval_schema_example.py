from pathlib import Path

import yaml


def test_planning_eval_schema_example_is_parseable() -> None:
    data = yaml.safe_load(Path("docs/PLANNING_EVAL_V1_SCHEMA.yaml").read_text(encoding="utf-8"))
    assert data["eval_version"] == "planning-eval-v1-dev"
    assert data["reference"]["nodes"]
    assert data["reference"]["edges"]
