from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass


@dataclass(frozen=True)
class EvalReleaseInputs:
    dataset_hash: str
    reference_hash: str
    scoring_version: str
    judge_config_hash: str
    baseline_protocol_hash: str

    def fingerprint(self) -> str:
        payload = json.dumps(self.__dict__, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(payload).hexdigest()
