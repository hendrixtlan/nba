from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from nba.ml.evaluation import temporal_split
from nba.ml.features import ALL_FEATURES

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "sample" / "training.csv"
ARTIFACTS = ROOT / "artifacts"


def main() -> None:
    try:
        import shap
    except ImportError:
        print("SHAP is optional. Install with: pip install -e '.[ml]'")
        return

    calibrated = joblib.load(ARTIFACTS / "propensity.joblib")
    pipeline = calibrated.estimator
    pre = pipeline.named_steps["pre"]
    clf = pipeline.named_steps["clf"]

    split = temporal_split(pd.read_csv(DATA))
    sample = split.test[ALL_FEATURES].sample(min(500, len(split.test)), random_state=42)
    transformed = pre.transform(sample)
    names = list(pre.get_feature_names_out())

    class_name = clf.__class__.__name__.lower()
    if "xgb" in class_name:
        explainer = shap.TreeExplainer(clf)
        values = explainer.shap_values(transformed)
    elif "logistic" in class_name:
        explainer = shap.LinearExplainer(clf, transformed)
        values = explainer.shap_values(transformed)
    else:
        print(f"No SHAP adapter configured for {clf.__class__.__name__}; permutation importance remains available.")
        return

    arr = np.asarray(values)
    if arr.ndim == 3:
        arr = arr[:, :, -1]
    mean_abs = np.mean(np.abs(arr), axis=0)
    rows = sorted(
        [{"feature": name, "mean_abs_shap": round(float(value), 8)} for name, value in zip(names, mean_abs)],
        key=lambda row: row["mean_abs_shap"],
        reverse=True,
    )
    (ARTIFACTS / "shap_importance.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print(json.dumps(rows[:15], indent=2))


if __name__ == "__main__":
    main()
