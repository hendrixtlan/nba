# LATAM Next Best Action + Agentic AI

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
infra/        Azure/Fabric deployment placeholders
```

## Local quick start

Requirements: Python 3.11+

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\\Scripts\\activate
pip install -e '.[dev]'
python scripts/generate_synthetic_data.py
python scripts/train_propensity_model.py
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
- [x] Baseline propensity model training
- [x] FastAPI decision endpoint
- [x] Agent-facing decision explanation tool
- [x] Unit tests and CI
- [ ] Fabric/OneLake production adapter
- [ ] Azure ML managed training + model registry
- [ ] Microsoft Foundry hosted agent integration
- [ ] Uplift model / treatment-effect estimator
- [ ] Experiment assignment and A/B measurement service
- [ ] Model, data and agent observability dashboards
- [ ] Infrastructure-as-code deployment

## Design principles

- LLMs explain and orchestrate; governed services make authoritative commercial decisions.
- Policy constraints are explicit, versioned and testable.
- Every decision carries model and policy versions for auditability.
- `no_action` is a valid outcome.
- Business impact is measured incrementally, not just through offline prediction accuracy.
- Cloud dependencies sit behind adapters so the business logic remains portable and testable.

See `docs/ARCHITECTURE.md` for the full design.
