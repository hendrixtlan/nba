from __future__ import annotations

import hashlib
import json
import logging
import math
import os
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger("nba.agent")


@dataclass(frozen=True)
class CostProfile:
    input_usd_per_1m_tokens: float = 0.0
    output_usd_per_1m_tokens: float = 0.0


def stable_id(prefix: str, value: str, length: int = 16) -> str:
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()[:length]
    return f"{prefix}_{digest}"


def estimate_tokens(text: str) -> int:
    # Deterministic local approximation for budget tests only; cloud telemetry is authoritative.
    return max(1, math.ceil(len(text) / 4))


def cost_profile_from_env() -> CostProfile | None:
    input_price = os.getenv("NBA_INPUT_USD_PER_1M_TOKENS")
    output_price = os.getenv("NBA_OUTPUT_USD_PER_1M_TOKENS")
    if input_price is None or output_price is None:
        return None
    return CostProfile(float(input_price), float(output_price))


def estimate_cost(
    input_tokens: int, output_tokens: int, profile: CostProfile | None = None
) -> float | None:
    if profile is None:
        return None
    amount = (
        input_tokens * profile.input_usd_per_1m_tokens
        + output_tokens * profile.output_usd_per_1m_tokens
    ) / 1_000_000
    return round(amount, 8)


def log_agent_event(event: str, payload: dict[str, Any]) -> None:
    logger.info(json.dumps({"event": event, **payload}, sort_keys=True, default=str))
