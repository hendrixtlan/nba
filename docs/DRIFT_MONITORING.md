# Data and model drift monitoring

`python scripts/monitor_drift.py` compares the original training window with the latest test window using Population Stability Index (PSI).

Operational thresholds used in this reference implementation:

- PSI < 0.10: stable
- 0.10 <= PSI < 0.25: watch
- PSI >= 0.25: investigate

PSI is a screening signal, not an automatic retraining command. Production retraining should combine data drift, performance decay, calibration decay, business KPI movement and operational context.

The synthetic generator intentionally introduces modest temporal movement in digital-channel mix, average ticket and selected behavioral variables so the monitoring path can be exercised.
