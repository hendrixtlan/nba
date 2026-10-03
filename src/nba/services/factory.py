from __future__ import annotations

import os
from pathlib import Path

from nba.adapters.azureml_model import AzureMLPropensityModel
from nba.ml.model import HeuristicPropensityModel, JoblibPropensityModel
from nba.services.config import ROOT, load_actions, load_policy
from nba.services.decision_engine import DecisionEngine


def build_engine() -> DecisionEngine:
    scoring_uri = os.getenv("NBA_AZUREML_SCORING_URI")
    if scoring_uri:
        version = os.getenv("NBA_AZUREML_MODEL_VERSION", "azureml-managed-endpoint")
        model = AzureMLPropensityModel(scoring_uri=scoring_uri, version=version)
    else:
        model_path = Path(ROOT) / "artifacts" / "propensity.joblib"
        model = JoblibPropensityModel(model_path) if model_path.exists() else HeuristicPropensityModel()
    return DecisionEngine(model=model, actions=load_actions(), policy=load_policy())
