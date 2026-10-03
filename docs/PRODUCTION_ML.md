# Production ML design — v0.2

## Objective

Move the propensity component from an in-sample demonstration to a reproducible model-selection process that respects time, calibration and auditability.

## Training protocol

1. Sort observations by `event_timestamp`.
2. Use the oldest 70% for training, the next 15% for validation and the newest 15% as an untouched test window.
3. Train a transparent logistic-regression baseline and a nonlinear challenger.
4. Select on validation PR-AUC, with Brier score as a tie-breaker.
5. Fit Platt/sigmoid calibration on the validation window only.
6. Evaluate the selected calibrated model once on the untouched test window.
7. Persist the model, metrics, feature importance and a registry-style manifest with SHA-256 artifact integrity.

This protocol avoids random splitting across time, a common source of optimistic estimates when commercial behavior, channel mix or prices drift.

## Model contract

The inference artifact implements `predict_proba` and is loaded behind the `PropensityModel` protocol. The decision engine therefore does not depend on XGBoost, scikit-learn or a future Azure ML endpoint directly.

`artifacts/model_manifest.json` records model ID/version, features, temporal windows, test metrics, calibration method, intended use and artifact hash. In Azure ML this maps naturally to registered-model metadata and deployment provenance.

## Calibration

The utility engine multiplies probability by economic value. Consequently, calibration matters: a ranking model with good discrimination but systematically overstated probabilities can produce bad economic decisions. v0.2 therefore reports Brier score and log loss in addition to ROC-AUC and PR-AUC.

## Feature importance

Permutation importance is generated against the untouched test window. It is model-agnostic and available without an optional explainability dependency. The optional `ml` extra contains SHAP and XGBoost for deeper local/global explanations.
