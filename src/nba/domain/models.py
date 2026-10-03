from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class CustomerContext(BaseModel):
    customer_id: str
    channel: str
    region: str
    avg_ticket: float = Field(ge=0)
    purchase_frequency_30d: int = Field(ge=0)
    days_since_last_purchase: int = Field(ge=0)
    category_affinity: float = Field(ge=0, le=1)
    historical_discount_response: float = Field(ge=0, le=1)
    price_sensitivity: float = Field(ge=0, le=1)
    contact_count_7d: int = Field(ge=0)


class CandidateAction(BaseModel):
    action_id: str
    action_type: str
    expected_margin: float
    discount_cost: float
    contact_cost: float
    price: float
    inventory_units: int
    risk_penalty: float = Field(ge=0, le=1)


class ScoredAction(BaseModel):
    action_id: str
    action_type: str
    propensity: float | None = Field(default=None, ge=0, le=1)
    gross_expected_value: float
    expected_utility: float
    eligible: bool
    exclusion_reasons: list[str] = []


class DecisionResponse(BaseModel):
    customer_id: str
    selected_action: str
    expected_utility: float
    propensity: float | None
    policy_version: str
    model_version: str
    rationale_codes: list[str]
    alternatives: list[ScoredAction]


class ExplainRequest(BaseModel):
    decision: DecisionResponse
    style: Literal["concise", "business", "technical"] = "business"
