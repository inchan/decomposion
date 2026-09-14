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
    if expected is None:
        raise GoldenCaseError(f"{path}: case must define expected assertions")

    exp = _require_mapping(expected, "expected", path)

    # Standard structured cases.
    for section in ("outcomes", "impacted_domains", "hidden_concerns", "decisions", "risks"):
        if section in exp:
            sec = _require_mapping(exp[section], f"expected.{section}", path)
            for list_name in ("must_detect", "nice_to_detect"):
                if list_name in sec:
                    _require_list(sec[list_name], f"expected.{section}.{list_name}", path)

    # Adversarial/sparse cases may intentionally use a flatter assertion shape.
    for name in ("must_detect", "should_investigate", "must_not_claim_as_fact"):
        if name in exp:
            _require_list(exp[name], f"expected.{name}", path)

    if "unknowns" in exp:
        unknowns = _require_mapping(exp["unknowns"], "expected.unknowns", path)
        if "should_abstain_on" in unknowns:
            _require_list(unknowns["should_abstain_on"], "expected.unknowns.should_abstain_on", path)

    if "noise" in exp:
        noise = _require_mapping(exp["noise"], "expected.noise", path)
        if "forbidden_or_irrelevant" in noise:
            _require_list(noise["forbidden_or_irrelevant"], "expected.noise.forbidden_or_irrelevant", path)

    if "dependencies" in exp:
        deps = _require_mapping(exp["dependencies"], "expected.dependencies", path)
        for name in ("must_include", "must_not_include"):
            if name in deps:
                values = _require_list(deps[name], f"expected.dependencies.{name}", path)
                for index, item in enumerate(values):
                    if not isinstance(item, dict):
                        raise GoldenCaseError(f"{path}: expected.dependencies.{name}[{index}] must be a mapping")
                    for field in ("from", "to", "type"):
                        if field not in item:
                            raise GoldenCaseError(f"{path}: expected.dependencies.{name}[{index}] missing '{field}'")
