from __future__ import annotations

import numpy as np
from sklearn.linear_model import LogisticRegression


class PlattCalibratedClassifier:
    """Post-hoc sigmoid calibration fit on a held-out validation window."""

    def __init__(self, estimator, calibrator: LogisticRegression) -> None:
        self.estimator = estimator
        self.calibrator = calibrator

    @staticmethod
    def _logit(probabilities: np.ndarray) -> np.ndarray:
        p = np.clip(np.asarray(probabilities, dtype=float), 1e-6, 1 - 1e-6)
        return np.log(p / (1 - p)).reshape(-1, 1)

    @classmethod
    def fit_from_validation(cls, estimator, x_validation, y_validation):
        raw = estimator.predict_proba(x_validation)[:, 1]
        calibrator = LogisticRegression(C=1e6, max_iter=1000)
        calibrator.fit(cls._logit(raw), y_validation)
        return cls(estimator=estimator, calibrator=calibrator)

    def predict_proba(self, x):
        raw = self.estimator.predict_proba(x)[:, 1]
        calibrated = self.calibrator.predict_proba(self._logit(raw))[:, 1]
        return np.column_stack([1.0 - calibrated, calibrated])
