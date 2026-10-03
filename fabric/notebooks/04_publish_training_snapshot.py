# Fabric notebook source: 04_publish_training_snapshot
# Publishes an immutable Parquet snapshot under Lakehouse Files for Azure ML.

from datetime import datetime, timezone

from pyspark.sql import functions as F

spark.sql("CREATE SCHEMA IF NOT EXISTS gold")
SOURCE_TABLE = "gold.nba_training_features"
SNAPSHOT_ROOT = "Files/ml/training"

snapshot_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
snapshot_path = f"{SNAPSHOT_ROOT}/snapshots/{snapshot_id}"
latest_path = f"{SNAPSHOT_ROOT}/latest"

df = spark.table(SOURCE_TABLE).drop("published_at_utc", "feature_contract_version")

# Immutable dated snapshot for lineage/reproducibility.
df.write.mode("errorifexists").parquet(snapshot_path)

# Convenience pointer represented by a replaceable materialization. Production
# orchestration should update this only after all quality gates have passed.
df.write.mode("overwrite").parquet(latest_path)

manifest = spark.createDataFrame(
    [
        (
            snapshot_id,
            snapshot_path,
            df.count(),
            "1.0.0",
            datetime.now(timezone.utc),
        )
    ],
    "snapshot_id string, path string, row_count long, contract_version string, published_at_utc timestamp",
)
manifest.write.format("delta").mode("append").saveAsTable("gold.nba_training_snapshot_manifest")

print(f"snapshot_id={snapshot_id} rows={df.count()} path={snapshot_path}")
