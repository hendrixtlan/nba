# Model Card — Propensity Model

## Intended use
Estimate the probability that a customer/outlet will respond positively to a candidate commercial action. The score is one input to an expected-utility calculation and is not itself the final decision.

## Out of scope
- Fully autonomous pricing changes.
- Decisions using unapproved sensitive personal attributes.
- Credit, employment, healthcare or other high-impact individual decisions.
- Causal claims from the baseline propensity model.

## Inputs
Behavioral, transaction-derived, channel, geography-at-business-region level, commercial-context and action attributes.

## Output
Probability in `[0, 1]` representing estimated response propensity.

## Evaluation
Baseline metrics: ROC-AUC, PR-AUC and Brier score. Production validation must use temporal or out-of-time splits, calibration analysis, cohort-level performance, stability tests and business experiments.

## Main limitations
The baseline supervised target estimates association, not treatment effect. A customer with high predicted propensity may have purchased without intervention. Uplift or causal methods are required for incremental optimization.

## Monitoring
Track feature distribution shift, prediction distribution, calibration, performance by approved cohort, realized incremental outcome, decision mix and economic value.
