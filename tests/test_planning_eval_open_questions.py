from pathlib import Path


def test_step1_open_questions_are_not_lost() -> None:
    text = Path("docs/PLANNING_EVAL_V1_OPEN_QUESTIONS.md").read_text(encoding="utf-8")
    for word in ("Explicitness", "Granularity", "Critical failures", "Novel findings", "Golden authorship"):
        assert word in text
