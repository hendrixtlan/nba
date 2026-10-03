from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, brier_score_loss, log_loss, roc_auc_score


@dataclass(frozen=True)
class TemporalSplit:
    train: pd.DataFrame
    validation: pd.DataFrame
    test: pd.DataFrame


def temporal_split(
    df: pd.DataFrame,
    timestamp_col: str = "event_timestamp",
    train_fraction: float = 0.70,
    validation_fraction: float = 0.15,
) -> TemporalSplit:
    if train_fraction <= 0 or validation_fraction <= 0 or train_fraction + validation_fraction >= 1:
        raise ValueError("Fractions must be positive and leave a non-empty test window")
    ordered = df.copy()
    ordered[timestamp_col] = pd.to_datetime(ordered[timestamp_col], utc=True)
    ordered = ordered.sort_values(timestamp_col).reset_index(drop=True)
    n = len(ordered)
    train_end = int(n * train_fraction)
    validation_end = int(n * (train_fraction + validation_fraction))
    return TemporalSplit(
        train=ordered.iloc[:train_end].copy(),
        validation=ordered.iloc[train_end:validation_end].copy(),
        test=ordered.iloc[validation_end:].copy(),
    )


def binary_metrics(y_true: pd.Series | np.ndarray, probabilities: np.ndarray) -> dict[str, float]:
    p = np.clip(np.asarray(probabilities, dtype=float), 1e-6, 1 - 1e-6)
    y = np.asarray(y_true)
    return {
        "roc_auc": round(float(roc_auc_score(y, p)), 6),
        "pr_auc": round(float(average_precision_score(y, p)), 6),
        "brier": round(float(brier_score_loss(y, p)), 6),
        "log_loss": round(float(log_loss(y, p)), 6),
        "positive_rate": round(float(y.mean()), 6),
        "mean_prediction": round(float(p.mean()), 6),
    }


def split_window(df: pd.DataFrame, timestamp_col: str = "event_timestamp") -> dict[str, str | int]:
    ts = pd.to_datetime(df[timestamp_col], utc=True)
    return {
        "rows": int(len(df)),
        "start": ts.min().isoformat(),
        "end": ts.max().isoformat(),
    }
