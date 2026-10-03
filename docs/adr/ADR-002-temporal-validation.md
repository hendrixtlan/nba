# ADR-002 — Temporal validation over random splitting

## Status
Accepted.

## Context
Commercial behavior, price sensitivity, channel mix and campaigns change over time. A random train/test split can allow future distribution information to leak into model development and can overstate expected production performance.

## Decision
All propensity model comparison uses chronological train/validation/test windows. The newest test window is excluded from model selection and calibration.

## Consequences
Reported metrics are typically more conservative, but better represent forward deployment. Drift can also be measured between reference and recent windows using the same event-time contract.
