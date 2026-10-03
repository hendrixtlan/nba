from __future__ import annotations

from pathlib import Path

from nba.ml.model import HeuristicPropensityModel, JoblibPropensityModel
from nba.services.config import ROOT, load_actions, load_policy
from nba.services.decision_engine import DecisionEngine


def build_engine() -> DecisionEngine:
    model_path = Path(ROOT) / "artifacts" / "propensity.joblib"
    model = JoblibPropensityModel(model_path) if model_path.exists() else HeuristicPropensityModel()
    return DecisionEngine(model=model, actions=load_actions(), policy=load_policy())
