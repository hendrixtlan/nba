# Validation strategy

## Offline predictive validation

- chronological 70/15/15 split;
- baseline and challenger comparison on validation PR-AUC/Brier;
- Platt/sigmoid calibration using validation only;
- one final evaluation on the untouched newest test window;
- ROC-AUC, PR-AUC, Brier and log loss;
- permutation feature importance on test data.

## Causal/business validation

Offline propensity performance does not prove business impact. Production acceptance requires randomized or otherwise causally defensible experiments that measure incremental conversion, incremental margin and policy-level value.

## Monitoring

PSI screening compares reference and current feature distributions. Production monitoring should additionally include calibration drift, realized-vs-predicted response, policy distribution, action mix, latency, errors and commercial KPIs.
