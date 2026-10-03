from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import yaml

from nba.domain.models import CandidateAction

ROOT = Path(__file__).resolve().parents[3]


@lru_cache
def load_policy() -> dict:
    with (ROOT / "configs" / "policy.yaml").open(encoding="utf-8") as f:
        return yaml.safe_load(f)


@lru_cache
def load_actions() -> list[CandidateAction]:
    with (ROOT / "configs" / "actions.yaml").open(encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    return [CandidateAction(**item) for item in raw["actions"]]
