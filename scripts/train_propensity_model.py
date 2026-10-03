from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from nba.ml.calibration import PlattCalibratedClassifier
from nba.ml.evaluation import binary_metrics, split_window, temporal_split
from nba.ml.features import CATEGORICAL_FEATURES, NUMERIC_FEATURES

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "sample" / "training.csv"
ARTIFACTS = ROOT / "artifacts"
TARGET = "response"
FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES


def _preprocessor(scale_numeric: bool = True) -> ColumnTransformer:
    numeric = StandardScaler() if scale_numeric else "passthrough"
    return ColumnTransformer(
        [
            ("num", numeric, NUMERIC_FEATURES),
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), CATEGORICAL_FEATURES),
        ]
    )


def _candidate_models() -> dict[str, Pipeline]:
    models: dict[str, Pipeline] = {
        "logistic_regression": Pipeline(
            [("pre", _preprocessor()), ("clf", LogisticRegression(max_iter=2000, C=1.0))]
        )
    }
    try:
        from xgboost import XGBClassifier

        models["xgboost"] = Pipeline(
            [
                ("pre", _preprocessor(scale_numeric=False)),
                (
                    "clf",
                    XGBClassifier(
                        n_estimators=350,
                        max_depth=4,
                        learning_rate=0.045,
                        subsample=0.85,
                        colsample_bytree=0.85,
                        min_child_weight=5,
                        reg_lambda=1.5,
                        objective="binary:logistic",
                        eval_metric="logloss",
                        random_state=42,
                        n_jobs=2,
                    ),
                ),
            ]
        )
    except ImportError:
        from sklearn.ensemble import HistGradientBoostingClassifier

        models["hist_gradient_boosting"] = Pipeline(
            [
                ("pre", _preprocessor(scale_numeric=False)),
                ("clf", HistGradientBoostingClassifier(max_iter=250, learning_rate=0.06, max_leaf_nodes=31)),
            ]
        )
    return models


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    df = pd.read_csv(DATA)
    split = temporal_split(df)
    x_train, y_train = split.train[FEATURES], split.train[TARGET]
    x_val, y_val = split.validation[FEATURES], split.validation[TARGET]
    x_test, y_test = split.test[FEATURES], split.test[TARGET]

    comparison: dict[str, dict] = {}
    fitted: dict[str, Pipeline] = {}
    for name, model in _candidate_models().items():
        model.fit(x_train, y_train)
        fitted[name] = model
        comparison[name] = {
            "validation": binary_metrics(y_val, model.predict_proba(x_val)[:, 1]),
        }

    winner_name = max(
        comparison,
        key=lambda name: (
            comparison[name]["validation"]["pr_auc"],
            -comparison[name]["validation"]["brier"],
        ),
    )
    winner = fitted[winner_name]
    calibrated = PlattCalibratedClassifier.fit_from_validation(winner, x_val, y_val)
    test_metrics = binary_metrics(y_test, calibrated.predict_proba(x_test)[:, 1])

    permutation = permutation_importance(
        winner,
        x_test,
        y_test,
        n_repeats=5,
        random_state=42,
        scoring="average_precision",
    )
    importance = sorted(
        [
            {"feature": feature, "importance_mean": round(float(mean), 6), "importance_std": round(float(std), 6)}
            for feature, mean, std in zip(FEATURES, permutation.importances_mean, permutation.importances_std)
        ],
        key=lambda row: row["importance_mean"],
        reverse=True,
    )

    ARTIFACTS.mkdir(exist_ok=True)
    model_path = ARTIFACTS / "propensity.joblib"
    joblib.dump(calibrated, model_path)

    metrics = {
        "selection_metric": "validation_pr_auc_then_brier",
        "winner": winner_name,
        "candidate_comparison": comparison,
        "test_calibrated": test_metrics,
        "temporal_windows": {
            "train": split_window(split.train),
            "validation": split_window(split.validation),
            "test": split_window(split.test),
        },
        "calibration": "platt_sigmoid_on_validation_window",
        "warning": "Synthetic portfolio data; test window was untouched during model selection and calibration.",
    }
    (ARTIFACTS / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    (ARTIFACTS / "feature_importance.json").write_text(json.dumps(importance, indent=2), encoding="utf-8")

    version = f"{winner_name}-platt-v2"
    manifest = {
        "model_id": "latam-nba-propensity",
        "model_version": version,
        "trained_at_utc": datetime.now(timezone.utc).isoformat(),
        "artifact": model_path.name,
        "artifact_sha256": _sha256(model_path),
        "features": FEATURES,
        "target": TARGET,
        "selection": {"winner": winner_name, "metric": "validation_pr_auc_then_brier"},
        "calibration": "platt_sigmoid",
        "test_metrics": test_metrics,
        "temporal_windows": metrics["temporal_windows"],
        "data_classification": "synthetic_non_personal",
        "intended_use": "rank eligible commercial actions by expected utility",
    }
    (ARTIFACTS / "model_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
