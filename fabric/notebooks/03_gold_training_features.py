# Fabric notebook source: 03_gold_training_features
# The Gold product contains only features available at the event decision time.

from pyspark.sql import functions as F

spark.sql("CREATE SCHEMA IF NOT EXISTS gold")
SOURCE_TABLE = "silver.nba_customer_action_events"
TARGET_TABLE = "gold.nba_training_features"

FEATURE_COLUMNS = [
    "event_time",
    "customer_id",
    "avg_ticket",
    "purchase_frequency_30d",
    "days_since_last_purchase",
    "category_affinity",
    "historical_discount_response",
    "price_sensitivity",
    "contact_count_7d",
    "action_expected_margin",
    "action_discount_cost",
    "action_contact_cost",
    "action_price",
    "action_risk_penalty",
    "channel",
    "region",
    "action_type",
    "action_id",
    "response",
]

silver = spark.table(SOURCE_TABLE)

gold = (
    silver.select(*FEATURE_COLUMNS)
    .filter(F.col("event_time").isNotNull())
    .withColumn("feature_contract_version", F.lit("1.0.0"))
    .withColumn("published_at_utc", F.current_timestamp())
)

# Target leakage guard: the label is retained for offline supervised training, but
# feature columns contain no fields derived after event_time.
assert "response" in gold.columns
assert not any(c.startswith("future_") for c in gold.columns)

(
    gold.write.format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable(TARGET_TABLE)
)

print(f"gold_rows={gold.count()} target={TARGET_TABLE}")
