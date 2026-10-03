# v0.3 validation report

Validated locally on 2026-10-03.

## Passed

- Python source compilation for application, Fabric notebook sources and Azure ML helper code.
- JSON parsing for Fabric data contracts.
- YAML parsing for Fabric orchestration and Azure ML compute/environment/job/endpoint assets.
- 12 unit/integration tests.
- Deterministic synthetic data generation.
- Full local propensity training with chronological train/validation/test windows.
- Calibrated model artifact generation and manifest hashing.
- Local NBA decision-engine smoke test using the newly trained v3 artifact.
- Azure ML scoring entry point initialization and inference against the packaged custom model.
- Entra-token remote adapter contract using a mocked credential and HTTP response.

## Not claimed as validated

This repository was not deployed into a live Microsoft Fabric tenant or Azure subscription
as part of this portfolio build. Therefore the following remain environment integration
checks, not completed deployment evidence:

- Fabric workspace/Lakehouse item provisioning and notebook execution.
- Fabric pipeline item deployment/scheduling.
- Azure ML OneLake datastore creation against a real Lakehouse.
- Azure ML compute/environment/job submission.
- Azure ML model registration and managed online endpoint provisioning.
- RBAC assignment and live `aad_token` endpoint invocation.
- Network isolation, private endpoints, capacity sizing and production cost validation.

These checks require tenant/subscription identities, resource IDs and governance controls
that are intentionally not stored in the public repository.
