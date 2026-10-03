# Microsoft Fabric / OneLake data plane

This folder contains the v0.3 production data-plane reference for the NBA capability.
It intentionally keeps Fabric-specific assets outside the Python decisioning domain.

## Logical flow

```text
Operational sources
      |
      v
Fabric Data Factory / shortcuts
      |
      v
Bronze  - source aligned, replayable
      |
      v
Silver  - typed, deduplicated, quality checked
      |
      v
Gold    - point-in-time ML feature product
      |
      +--> Delta table for analytics / lineage
      |
      +--> immutable Parquet training snapshot under Lakehouse Files
                |
                v
        Azure ML OneLake datastore
```

The snapshot under `Files/ml/training/...` is an immutable ML training product derived
from the governed Gold Delta table. It is not an independent system of record.

## Fabric assets

- `notebooks/01_bronze_ingest.py` — source-aligned ingestion with technical metadata.
- `notebooks/02_silver_conform.py` — schema, range, null and duplicate handling.
- `notebooks/03_gold_training_features.py` — point-in-time-safe ML feature dataset.
- `notebooks/04_publish_training_snapshot.py` — immutable Parquet snapshot for AML.
- `data-contracts/` — machine-readable contracts.
- `pipelines/nba_feature_pipeline.yaml` — source-controlled orchestration specification.
- `sql/gold_quality_checks.sql` — SQL endpoint quality assertions.

The Python notebook sources are designed to be pasted/imported into Fabric notebooks
or synchronized by the team's preferred deployment tooling. Environment-specific
workspace IDs and Lakehouse IDs are never committed.
