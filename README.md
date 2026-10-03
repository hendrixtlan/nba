# LATAM Next Best Action + Agentic AI

**Version 0.3 — Governed Data + Managed ML**

Production-shaped reference implementation for a governed **Next Best Action (NBA)** decisioning system with an **agentic explanation and orchestration layer**.

The project demonstrates how predictive modeling, prescriptive ranking, governed enterprise data, agentic AI, evaluation, observability, and MLOps can be combined for commercial decision support.

> Portfolio project. Uses synthetic data only and is not affiliated with any beverage company.

## Business objective

For each customer or outlet, select the action that maximizes expected business utility while respecting commercial, inventory, contact-frequency, and governance constraints.

The decision engine separates **prediction** from **decisioning**:

1. Generate eligible candidate actions.
2. Estimate response propensity for each customer-action pair.
3. Calculate expected economic value.
4. Apply deterministic business and policy constraints.
5. Rank remaining actions by expected utility.
6. Expose the decision through an API.
7. Let an AI agent explain or orchestrate the governed decision through approved tools.

A language model does **not** calculate the authoritative NBA score. It consumes the output of deterministic services and approved ML models.

## Core decision function

```text
Expected utility = P(response | customer, action, context) × expected_margin
                   - discount_cost
                   - contact_cost
                   - risk_penalty
```

```text
NBA(customer) = argmax eligible_action ExpectedUtility(action)
```

## Target architecture

```text
Business User / Channel
          |
          v
+-------------------------+
| Commercial AI Assistant |
| Microsoft Foundry       |
+------------+------------+
             |
       approved tools
             |
  +----------+-----------+
  |                      |
  v                      v
NBA Decision API     Semantic / KPI Layer
  |                      |
  |               Microsoft Fabric
  |                      |
  +----------+-----------+
             |
             v
   Governed feature datasets
             |
          OneLake
             |
 +-----------+-----------+
 | CRM | POS | ERP | Pricing |
 +---------------------------+
```

## Repository map

```text
src/nba/
  api/        FastAPI endpoints
  domain/     Typed contracts and business entities
  services/   Candidate generation, constraints and ranking
  ml/         Training and inference code
  agent/      Agent-facing governed tools
  adapters/   Local and cloud data/model adapters
configs/      Policy and use-case configuration
docs/         Architecture, model card, governance and runbooks
scripts/      Data generation and training entry points
tests/        Unit and integration tests
fabric/       Fabric/OneLake notebooks, contracts and orchestration spec
azureml/      Azure ML OneLake datastore, training, registry and endpoint assets
infra/        Infrastructure-as-code evolution
```

## Local quick start

Requirements: Python 3.11+

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\\Scripts\\activate
pip install -e '.[dev]'
make pipeline
uvicorn nba.api.app:app --reload
```

Then call:

```bash
curl -X POST http://127.0.0.1:8000/v1/next-best-action \
  -H 'Content-Type: application/json' \
  -d '{
        "customer_id":"C0001",
        "channel":"traditional_trade",
        "region":"MX-CENTRAL",
        "avg_ticket":350.0,
        "purchase_frequency_30d":6,
        "days_since_last_purchase":4,
        "category_affinity":0.82,
        "historical_discount_response":0.55,
        "price_sensitivity":0.42,
        "contact_count_7d":1
      }'
```

## Production evolution

The local reference implementation uses synthetic data and a lightweight scikit-learn model. The production target replaces the adapters without changing the decision contract:

- **Data**: Microsoft Fabric + OneLake / governed Delta tables.
- **Training/registry**: Azure ML or approved enterprise ML platform.
- **Agent**: Microsoft Foundry Agent Service / approved orchestration runtime.
- **Identity**: Microsoft Entra ID + managed identity.
- **Secrets**: Azure Key Vault; no application secrets in source control.
- **Monitoring**: Azure Monitor / Application Insights plus model and decision metrics.
- **Governance**: lineage, model cards, eval sets, audit log, policy version, dataset readiness score.

## Evaluation layers

This project intentionally separates five forms of evaluation:

| Layer | Examples |
|---|---|
| Predictive model | ROC-AUC, PR-AUC, calibration |
| Ranking | Precision@K, NDCG@K |
| Causal/business | conversion uplift, incremental margin |
| Agent | groundedness, tool correctness, policy compliance |
| Operations | latency, error rate, token cost, model drift |

## Roadmap

- [x] Domain model and deterministic decision pipeline
- [x] Synthetic commercial dataset generator
- [x] Temporal train/validation/test split
- [x] Baseline + nonlinear challenger model selection
- [x] Held-out probability calibration and untouched test evaluation
- [x] Model manifest, artifact hash and permutation importance
- [x] Data drift monitoring with PSI
- [x] Randomized synthetic experiment + T-learner uplift baseline
- [x] FastAPI decision endpoint
- [x] Agent-facing decision explanation tool
- [x] Unit tests and CI
- [x] Fabric/OneLake governed medallion feature product
- [x] Azure ML OneLake datastore + managed training contract
- [x] Azure ML model registry + managed online endpoint assets
- [ ] Microsoft Foundry hosted agent integration
- [x] Uplift model / treatment-effect estimator baseline
- [ ] Online experiment assignment and A/B measurement service
- [ ] Model, data and agent observability dashboards
- [ ] Full infrastructure-as-code deployment

## Design principles

- LLMs explain and orchestrate; governed services make authoritative commercial decisions.
- Policy constraints are explicit, versioned and testable.
- Every decision carries model and policy versions for auditability.
- `no_action` is a valid outcome.
- Business impact is measured incrementally, not just through offline prediction accuracy.
- Cloud dependencies sit behind adapters so the business logic remains portable and testable.

See `docs/ARCHITECTURE.md` for the full design.


## v0.2 production-ML outputs

Running `make pipeline` produces:

- `artifacts/propensity.joblib` — calibrated selected model.
- `artifacts/model_manifest.json` — registry-style provenance and artifact hash.
- `artifacts/metrics.json` — candidate comparison plus untouched-test metrics.
- `artifacts/feature_importance.json` — permutation importance.
- `artifacts/drift_report.json` — PSI-based feature drift report.
- `artifacts/uplift.joblib` and `uplift_metrics.json` — causal/uplift baseline.
- `artifacts/shap_importance.json` — optional global SHAP explanation summary (`make install-ml && make explain`).

See `docs/PRODUCTION_ML.md`, `docs/DRIFT_MONITORING.md`, and `docs/UPLIFT.md`.


## Experiment assignment

`nba.experimentation.assign_variant` uses a salted SHA-256 bucket to provide deterministic, sticky treatment/control assignment. Assignment is separated from outcome modeling so experimentation can be audited and reproduced independently of the recommender.

## CI/CD surfaces

- `ci.yml` validates code quality and API/unit contracts.
- `model-pipeline.yml` regenerates deterministic data, trains candidate models, evaluates uplift/drift/SHAP, runs tests, and publishes validation artifacts for review.
- `Dockerfile` packages only the API source, configuration and selected model artifacts for inference.


## v0.3 governed data and managed ML

The v0.3 increment keeps the same decision contract while replacing local-only data/model
surfaces with production-shaped Microsoft platform adapters:

```text
Sources
  -> Fabric Bronze
  -> Fabric Silver + quarantine
  -> Fabric Gold ML feature product
  -> immutable OneLake training snapshot
  -> Azure ML OneLake datastore
  -> managed training job
  -> registered model
  -> Entra-authenticated managed online endpoint
  -> NBA decision service
```

The cloud artifacts are deliberately environment-neutral: tenant IDs, workspace IDs,
Lakehouse IDs, subscriptions and secrets are not committed. See `fabric/README.md`,
`azureml/README.md`, `docs/FABRIC_AZUREML.md` and `docs/AI_READY_DATASET.md`.

Run `make validate-cloud` to validate the source-controlled JSON/YAML cloud contracts.
