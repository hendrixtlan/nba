from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from nba.ml.drift import categorical_psi, drift_status, population_stability_index
from nba.ml.evaluation import temporal_split
from nba.ml.features import CATEGORICAL_FEATURES, NUMERIC_FEATURES

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "sample" / "training.csv"
ARTIFACTS = ROOT / "artifacts"


def main() -> None:
    df = pd.read_csv(DATA)
    split = temporal_split(df)
    report = []
    for feature in NUMERIC_FEATURES:
        psi = population_stability_index(split.train[feature], split.test[feature])
        report.append({"feature": feature, "type": "numeric", "psi": round(psi, 6), "status": drift_status(psi)})
    for feature in CATEGORICAL_FEATURES:
        psi = categorical_psi(split.train[feature], split.test[feature])
        report.append({"feature": feature, "type": "categorical", "psi": round(psi, 6), "status": drift_status(psi)})
    summary = {
        "thresholds": {"stable": "PSI < 0.10", "watch": "0.10 <= PSI < 0.25", "investigate": "PSI >= 0.25"},
        "features": sorted(report, key=lambda row: row["psi"], reverse=True),
    }
    ARTIFACTS.mkdir(exist_ok=True)
    (ARTIFACTS / "drift_report.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
