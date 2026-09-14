from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class EvalInput:
    case_id: str
    context: dict
    change: str


@dataclass(frozen=True)
class EvalOutput:
    concepts: set[str]
    abstentions: set[str]
    metadata: dict


class Strategy(Protocol):
    name: str

    def run(self, item: EvalInput) -> EvalOutput: ...


class FixtureStrategy:
    """Deterministic stand-in for a real provider-backed strategy.

    Keeps CI reproducible until provider/model/prompt configuration is versioned.
    """

    def __init__(self, name: str, concepts: set[str] | None = None, abstentions: set[str] | None = None):
        self.name = name
        self._concepts = concepts or set()
        self._abstentions = abstentions or set()

    def run(self, item: EvalInput) -> EvalOutput:
        return EvalOutput(
            concepts=set(self._concepts),
            abstentions=set(self._abstentions),
            metadata={"strategy": self.name, "provider": "fixture"},
        )
