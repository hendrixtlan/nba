# v0.3 — Fabric, OneLake and Azure ML

## Architectural decision

Fabric owns the governed feature data product. Azure ML owns model training, registration
and managed inference. The Python NBA service owns commercial eligibility and utility
ranking. This prevents the ML platform from becoming the owner of business policy.

## Data boundaries

- **Bronze:** replayable source-aligned events plus ingestion metadata.
- **Silver:** conformed types, deterministic event key, deduplication and quarantine.
- **Gold:** point-in-time-safe supervised training product.
- **Snapshot:** immutable Parquet materialization under Lakehouse `Files` for AML training.

## OneLake to Azure ML

The repository uses an Azure ML OneLake datastore. It points to the Lakehouse `Files`
surface and is authenticated by identity. The AML training job receives the curated
snapshot as a mounted `uri_folder` rather than copying credentials into code.

## Model lifecycle

```text
Gold quality gate
      -> publish snapshot
      -> Azure ML command job
      -> temporal validation/champion selection
      -> calibration + untouched test
      -> custom model output
      -> registered model asset
      -> managed online endpoint
      -> Entra-authenticated NBA service call
```

## Production promotion gates

A model is eligible for deployment only when:

- data contract and quality checks pass;
- temporal test metrics meet use-case thresholds;
- calibration remains within tolerance;
- model artifact manifest and hash are emitted;
- model/data lineage is retained;
- security review allows the endpoint identity and caller identity;
- rollback target remains registered.

This repository demonstrates the mechanics. Business thresholds are intentionally not
invented because they must be approved per real use case.
