from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from nba.ml.evaluation import temporal_split
from nba.ml.uplift import TLearnerUpliftModel

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "sample" / "uplift.csv"
ARTIFACTS = ROOT / "artifacts"
NUMERIC = ["avg_ticket", "purchase_frequency_30d", "category_affinity", "historical_discount_response", "price_sensitivity"]
CATEGORICAL = ["channel", "region"]
FEATURES = NUMERIC + CATEGORICAL


def _observed_uplift(frame: pd.DataFrame) -> float:
    treated = frame[frame["treatment"] == 1]["response"]
    control = frame[frame["treatment"] == 0]["response"]
    return float(treated.mean() - control.mean()) if len(treated) and len(control) else 0.0


def main() -> None:
    df = pd.read_csv(DATA)
    split = temporal_split(df)
    pre = ColumnTransformer(
        [("num", StandardScaler(), NUMERIC), ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL)]
    )
    base = Pipeline([("pre", pre), ("clf", LogisticRegression(max_iter=1500))])
    model = TLearnerUpliftModel(base).fit(split.train[FEATURES], split.train["treatment"], split.train["response"])

    scored = split.test.copy()
    scored["predicted_uplift"] = model.predict_uplift(scored[FEATURES])
    scored = scored.sort_values("predicted_uplift", ascending=False).reset_index(drop=True)
    top20 = scored.iloc[: max(1, int(len(scored) * 0.20))]
    metrics = {
        "randomized_experiment": True,
        "test_rows": int(len(scored)),
        "overall_observed_uplift": round(_observed_uplift(scored), 6),
        "top20_observed_uplift": round(_observed_uplift(top20), 6),
        "top20_mean_predicted_uplift": round(float(top20["predicted_uplift"].mean()), 6),
        "simulation_only_uplift_mae": round(float(np.mean(np.abs(scored["predicted_uplift"] - scored["true_uplift"]))), 6),
        "note": "true_uplift exists only because this is synthetic data; a real deployment would use randomized experiments or causal identification assumptions.",
    }
    ARTIFACTS.mkdir(exist_ok=True)
    joblib.dump(model, ARTIFACTS / "uplift.joblib")
    (ARTIFACTS / "uplift_metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
