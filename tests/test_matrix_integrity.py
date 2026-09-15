from pathlib import Path

import pytest
import yaml

from eval_harness.baselines import EvalOutput, FixtureStrategy
from eval_harness.golden import GoldenCase, GoldenCaseError
from eval_harness.matrix import evaluate_matrix, evaluate_strategy
from eval_harness.report import markdown_report


def case():
    return GoldenCase(Path("synthetic.yaml"), {
        "id": "synthetic", "version": 1, "context": {"nested": {"value": "original"}},
        "change": "analyze", "expected": {
            "unknowns": {"should_abstain_on": ["cache_exists"]},
            "impacted_domains": {"must_not_invent": ["billing"]},
        },
    })


def test_matrix_uses_actual_abstentions_and_nested_forbidden():
    empty = evaluate_strategy(FixtureStrategy("empty"), case())
    assert empty.score.abstention_accuracy == 0
    good = evaluate_strategy(FixtureStrategy("good", abstentions={"cache_exists"}), case())
    assert good.score.abstention_accuracy == 1
    bad = evaluate_strategy(FixtureStrategy("bad", concepts={"billing"}), case())
    assert bad.score.forbidden_hit == 1
    assert "FIXTURE ONLY" in markdown_report([empty])


def test_context_cannot_be_modified_across_arms():
    class Mutator:
        name = "mutator"
        def run(self, item):
            assert not hasattr(item, "expected")
            item.context["nested"]["value"] = "changed"
            return EvalOutput(set(), set(), {})
    sample = case()
    evaluate_strategy(Mutator(), sample)
    assert sample.data["context"]["nested"]["value"] == "original"


def test_no_cases_is_failure(tmp_path):
    with pytest.raises(GoldenCaseError, match="No golden cases"):
        evaluate_matrix([FixtureStrategy("plain")], tmp_path)


def test_duplicate_cases_and_strategies_are_not_silent(tmp_path):
    for name in ("one.yaml", "two.yaml"):
        (tmp_path / name).write_text(yaml.safe_dump(case().data))
    with pytest.raises(GoldenCaseError, match="Duplicate"):
        evaluate_matrix([FixtureStrategy("plain")], tmp_path)
    with pytest.raises(ValueError, match="uniquely"):
        evaluate_matrix([FixtureStrategy("plain"), FixtureStrategy("plain")], tmp_path)
