from planning_eval.selftest import run_selftests


def test_all_planning_eval_selftests_pass() -> None:
    results = run_selftests()
    assert results
    assert all(result.passed for result in results), results
