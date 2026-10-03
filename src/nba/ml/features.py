from __future__ import annotations

import pandas as pd

from nba.domain.models import CandidateAction, CustomerContext

NUMERIC_FEATURES = [
    "avg_ticket",
    "purchase_frequency_30d",
    "days_since_last_purchase",
    "category_affinity",
    "historical_discount_response",
    "price_sensitivity",
    "contact_count_7d",
    "action_expected_margin",
    "action_discount_cost",
    "action_contact_cost",
    "action_price",
    "action_risk_penalty",
]

CATEGORICAL_FEATURES = ["channel", "region", "action_type", "action_id"]
ALL_FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES


def build_feature_row(customer: CustomerContext, action: CandidateAction) -> pd.DataFrame:
    row = {
        **customer.model_dump(exclude={"customer_id"}),
        "action_expected_margin": action.expected_margin,
        "action_discount_cost": action.discount_cost,
        "action_contact_cost": action.contact_cost,
        "action_price": action.price,
        "action_risk_penalty": action.risk_penalty,
        "action_type": action.action_type,
        "action_id": action.action_id,
    }
    return pd.DataFrame([row], columns=ALL_FEATURES)
