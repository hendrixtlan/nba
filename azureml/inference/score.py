from __future__ import annotations

import json
import os
import sys
from pathlib import Path

# Azure ML uploads the repository as the endpoint code asset. Add the src-layout
# package before unpickling custom model classes.
REPO_ROOT = Path(__file__).resolve().parents[2]
SRC = REPO_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import joblib
import pandas as pd

MODEL = None
MODEL_VERSION = "unknown"


def _find_file(root: Path, name: str) -> Path:
    matches = list(root.rglob(name))
    if len(matches) != 1:
        raise RuntimeError(f"Expected exactly one {name} under {root}; found {len(matches)}")
    return matches[0]


def init() -> None:
    global MODEL, MODEL_VERSION
    model_root = Path(os.environ["AZUREML_MODEL_DIR"])
    model_path = _find_file(model_root, "propensity.joblib")
    MODEL = joblib.load(model_path)

    manifest_path = _find_file(model_root, "model_manifest.json")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    MODEL_VERSION = manifest.get("model_version", "unknown")


def run(raw_data: str) -> dict:
    if MODEL is None:
        raise RuntimeError("Model is not initialized")
    payload = json.loads(raw_data)
    rows = payload.get("input_data")
    if not isinstance(rows, list) or not rows:
        raise ValueError("Request must contain a non-empty 'input_data' list")

    frame = pd.DataFrame(rows)
    probabilities = MODEL.predict_proba(frame)[:, 1]
    return {
        "probabilities": [round(float(p), 8) for p in probabilities],
        "model_version": MODEL_VERSION,
    }
