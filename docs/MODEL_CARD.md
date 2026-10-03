# Model card — NBA propensity model

## Intended use
Estimate action-specific response probability for already eligible candidate commercial actions. Probabilities feed a deterministic expected-utility calculation; the model does not directly execute customer actions.

## Data
Synthetic, non-personal portfolio data spanning January 2025 through September 2026. The generator includes seasonality and mild temporal distribution shift to exercise production monitoring patterns.

## Evaluation design
Chronological 70/15/15 train/validation/test split. Candidate selection occurs on validation data. Calibration uses validation data. The final test window remains untouched until the selected calibrated artifact is evaluated.

## Metrics
See `artifacts/metrics.json` for ROC-AUC, PR-AUC, Brier score and log loss. Business acceptance requires online incremental-revenue and incremental-margin experiments; offline discrimination is insufficient.

## Limitations
Synthetic data does not represent real commercial heterogeneity, regional policy, inventory dynamics, causal confounding or fairness risk. Scores must not be interpreted as real customer behavior.

## Governance
Every API decision carries model and policy versions. The model artifact is accompanied by a registry-style manifest and SHA-256 hash. `no_action` remains a valid policy outcome.
