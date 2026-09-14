from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


class GoldenCaseError(ValueError):
    pass


@dataclass(frozen=True)
class GoldenCase:
    path: Path
    data: dict[str, Any]

    @property
    def case_id(self) -> str:
        return str(self.data["id"])


def load_case(path: str | Path) -> GoldenCase:
    p = Path(path)
    data = yaml.safe_load(p.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise GoldenCaseError(f"{p}: root must be a mapping")
    validate_case(data, p)
    return GoldenCase(path=p, data=data)


def _require_mapping(obj: Any, name: str, path: Path) -> dict[str, Any]:
    if not isinstance(obj, dict):
        raise GoldenCaseError(f"{path}: {name} must be a mapping")
    return obj


def _require_list(obj: Any, name: str, path: Path) -> list[Any]:
    if not isinstance(obj, list):
        raise GoldenCaseError(f"{path}: {name} must be a list")
    return obj


def validate_case(data: dict[str, Any], path: Path) -> None:
    for key in ("id", "version", "context", "change"):
        if key not in data:
            raise GoldenCaseError(f"{path}: missing required key '{key}'")

    if not isinstance(data["id"], str) or not data["id"].strip():
        raise GoldenCaseError(f"{path}: id must be a non-empty string")
    if not isinstance(data["version"], int) or data["version"] < 1:
        raise GoldenCaseError(f"{path}: version must be a positive integer")
    _require_mapping(data["context"], "context", path)
    if not isinstance(data["change"], str) or not data["change"].strip():
        raise GoldenCaseError(f"{path}: change must be a non-empty string")

    expected = data.get("expected")
    adversarial = data.get("adversarial")
    if expected is None and adversarial is None:
        raise GoldenCaseError(f"{path}: case must define expected and/or adversarial assertions")

    if expected is not None:
        exp = _require_mapping(expected, "expected", path)
        for section in ("outcomes", "impacted_domains", "hidden_concerns", "decisions", "risks"):
            if section in exp:
                sec = _require_mapping(exp[section], f"expected.{section}", path)
                for list_name in ("must_detect", "nice_to_detect"):
                    if list_name in sec:
                        _require_list(sec[list_name], f"expected.{section}.{list_name}", path)
        if "noise" in exp:
            noise = _require_mapping(exp["noise"], "expected.noise", path)
            if "forbidden_or_irrelevant" in noise:
                _require_list(noise["forbidden_or_irrelevant"], "expected.noise.forbidden_or_irrelevant", path)

    if adversarial is not None:
        adv = _require_mapping(adversarial, "adversarial", path)
        for name in ("must_abstain_on", "must_not_invent"):
            if name in adv:
                _require_list(adv[name], f"adversarial.{name}", path)
