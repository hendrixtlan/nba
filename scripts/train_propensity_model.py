from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "sample" / "training.csv"
ARTIFACTS = ROOT / "artifacts"

NUMERIC = [
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
CATEGORICAL = ["channel", "region", "action_type", "action_id"]


def main() -> None:
    df = pd.read_csv(DATA)
    X = df[NUMERIC + CATEGORICAL]
    y = df["response"]

    pre = ColumnTransformer(
        [
            ("num", StandardScaler(), NUMERIC),
            ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL),
        ]
    )
    model = Pipeline([("pre", pre), ("clf", LogisticRegression(max_iter=1500))])
    model.fit(X, y)
    p = model.predict_proba(X)[:, 1]

    ARTIFACTS.mkdir(exist_ok=True)
    joblib.dump(model, ARTIFACTS / "propensity.joblib")
    metrics = {
        "roc_auc_train": round(float(roc_auc_score(y, p)), 4),
        "pr_auc_train": round(float(average_precision_score(y, p)), 4),
        "brier_train": round(float(brier_score_loss(y, p)), 4),
        "warning": "Training-set metrics only; replace with temporal/out-of-time validation in production.",
    }
    (ARTIFACTS / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
