from planning_eval.release import EvalReleaseInputs


def test_eval_release_fingerprint_changes_when_frozen_input_changes() -> None:
    base = EvalReleaseInputs("dataset", "reference", "score-v1", "judge-none", "baselines-v1")
    changed = EvalReleaseInputs("dataset", "reference-2", "score-v1", "judge-none", "baselines-v1")
    assert base.fingerprint() != changed.fingerprint()
    assert base.fingerprint() == base.fingerprint()
