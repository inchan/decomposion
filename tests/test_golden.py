from pathlib import Path

import pytest

from eval_harness.golden import GoldenCaseError, load_case


GOLDEN_DIR = Path("golden")


def test_all_golden_cases_validate() -> None:
    paths = sorted(GOLDEN_DIR.rglob("*.yaml"))
    assert paths, "expected at least one golden case"
    for path in paths:
        load_case(path)


def test_invalid_case_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "invalid.yaml"
    path.write_text("id: broken\nversion: 1\n", encoding="utf-8")
    with pytest.raises(GoldenCaseError):
        load_case(path)
