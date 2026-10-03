from __future__ import annotations

from pathlib import Path
from typing import Protocol

import joblib
import numpy as np

from nba.domain.models import CandidateAction, CustomerContext
from nba.ml.features import build_feature_row


class PropensityModel(Protocol):
    version: str

    def predict(self, customer: CustomerContext, action: CandidateAction) -> float: ...


class HeuristicPropensityModel:
    """Deterministic local fallback for development before a trained artifact exists."""

    version = "heuristic-v1"

    def predict(self, customer: CustomerContext, action: CandidateAction) -> float:
        if action.action_type == "no_action":
            return 1.0
        score = (
            0.30
            + 0.24 * customer.category_affinity
            + 0.18 * customer.historical_discount_response
            + 0.08 * min(customer.purchase_frequency_30d / 10, 1)
            - 0.16 * customer.price_sensitivity * (action.price > customer.avg_ticket)
            - 0.03 * min(customer.days_since_last_purchase / 30, 1)
        )
        return float(np.clip(score, 0.02, 0.98))


class JoblibPropensityModel:
    def __init__(self, path: Path, version: str = "sklearn-v1") -> None:
        self.pipeline = joblib.load(path)
        self.version = version

    def predict(self, customer: CustomerContext, action: CandidateAction) -> float:
        row = build_feature_row(customer, action)
        return float(self.pipeline.predict_proba(row)[0, 1])
