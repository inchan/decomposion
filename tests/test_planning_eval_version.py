from importlib.resources import files


def test_planning_eval_version_artifact_is_present() -> None:
    value = files("planning_eval").joinpath("VERSION").read_text(encoding="utf-8").strip()
    assert value == "planning-eval-v1-dev"
