from pathlib import Path


def test_checkpoint_explicitly_stops_before_step2() -> None:
    text = Path("docs/PLANNING_EVAL_V1_STEP.md").read_text(encoding="utf-8")
    assert "Do not begin Step 2" in text
