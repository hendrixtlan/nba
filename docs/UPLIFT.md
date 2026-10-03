# Uplift modeling and experimentation

Propensity answers: **who is likely to respond?**

Uplift answers: **whose outcome is likely to change because we intervene?**

v0.2 includes a synthetic randomized discount experiment and a T-learner baseline. Two outcome models estimate:

`P(response | treatment, x)` and `P(response | control, x)`

The individual uplift estimate is their difference.

The synthetic dataset includes `true_uplift` only to validate implementation quality. Real production data will not expose the counterfactual outcome. A real program should use randomized assignment where feasible and evaluate incremental conversion/margin by treatment policy, with guardrails for interference, repeated exposure and selection bias.

The uplift model is deliberately separate from the authoritative NBA decision path in v0.2. It becomes an input to expected incremental value after online experimental evidence is strong enough.
