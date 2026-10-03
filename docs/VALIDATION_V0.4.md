# Validation — v0.4 Agentic AI

## Locally validated

- Core test suite: 17 tests passed.
- Deterministic agent evaluation: 6/6 cases passed.
- Intent accuracy: 1.00.
- Exact tool correctness: 1.00.
- Policy compliance: 1.00.
- Evidence coverage: 1.00.
- Approval boundary: 1.00.
- Budget compliance: 1.00.
- Python source compilation completed for `src`, `scripts`, and `foundry`.
- YAML configuration for agent policy and semantic catalog parsed successfully.
- Local `/v1/agent/run` contract exercised through FastAPI tests.

The first offline evaluation exposed an intent-routing regression: a request containing both "explain" and "runner-up" was routed as comparison. The routing precedence was corrected and the gate rerun successfully. The failed run was not suppressed; it demonstrates the purpose of the regression harness.

## Not claimed as validated

The following require a real Microsoft Foundry project, deployed model, Entra identity/RBAC, and network access and therefore are not represented as executed in this repository build:

- creation/invocation of the Foundry-managed prompt agent;
- actual LangGraph execution through `langchain-azure-ai`;
- cloud agent rubric generation;
- Foundry evaluation run and safety evaluators;
- Application Insights server-side tracing;
- actual token/cost telemetry from the deployed model.

`foundry/prompt_agent.py` and `foundry/evaluation/run_cloud_eval.py` follow the current Microsoft Foundry SDK patterns but should be validated in the target tenant before production promotion.

## Local tooling limitation

`ruff` was not installed in the isolated build runtime, so the local lint command was not executed. The repository's CI installs the `dev` extra, where `ruff` is declared, and runs linting as part of the normal GitHub Actions pipeline.
