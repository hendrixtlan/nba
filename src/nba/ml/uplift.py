from __future__ import annotations

import numpy as np
from sklearn.base import clone


class TLearnerUpliftModel:
    """Simple T-learner: one outcome model for treatment and one for control."""

    def __init__(self, base_estimator) -> None:
        self.treatment_model = clone(base_estimator)
        self.control_model = clone(base_estimator)

    def fit(self, x, treatment, y):
        t = np.asarray(treatment).astype(bool)
        self.treatment_model.fit(x.loc[t], np.asarray(y)[t])
        self.control_model.fit(x.loc[~t], np.asarray(y)[~t])
        return self

    def predict_uplift(self, x) -> np.ndarray:
        p1 = self.treatment_model.predict_proba(x)[:, 1]
        p0 = self.control_model.predict_proba(x)[:, 1]
        return p1 - p0
