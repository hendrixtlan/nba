# Fabric notebook source: 02_silver_conform
# Attach the Silver lakehouse as the default lakehouse and make Bronze available
# through a OneLake shortcut or an attached lakehouse.

from pyspark.sql import functions as F
from pyspark.sql.window import Window

spark.sql("CREATE SCHEMA IF NOT EXISTS silver")
SOURCE_TABLE = "bronze.nba_customer_action_events"
TARGET_TABLE = "silver.nba_customer_action_events"
QUARANTINE_TABLE = "silver.nba_customer_action_quarantine"

source = spark.table(SOURCE_TABLE)

conformed = (
    source.select(
        F.to_timestamp("event_time").alias("event_time"),
        F.trim("customer_id").alias("customer_id"),
        F.trim("channel").alias("channel"),
        F.trim("region").alias("region"),
        F.col("avg_ticket").cast("double").alias("avg_ticket"),
        F.col("purchase_frequency_30d").cast("int").alias("purchase_frequency_30d"),
        F.col("days_since_last_purchase").cast("int").alias("days_since_last_purchase"),
        F.col("category_affinity").cast("double").alias("category_affinity"),
        F.col("historical_discount_response").cast("double").alias("historical_discount_response"),
        F.col("price_sensitivity").cast("double").alias("price_sensitivity"),
        F.col("contact_count_7d").cast("int").alias("contact_count_7d"),
        F.col("action_expected_margin").cast("double").alias("action_expected_margin"),
        F.col("action_discount_cost").cast("double").alias("action_discount_cost"),
        F.col("action_contact_cost").cast("double").alias("action_contact_cost"),
        F.col("action_price").cast("double").alias("action_price"),
        F.col("action_risk_penalty").cast("double").alias("action_risk_penalty"),
        F.trim("action_type").alias("action_type"),
        F.trim("action_id").alias("action_id"),
        F.col("response").cast("int").alias("response"),
        "_ingested_at_utc",
        "_source_file",
    )
    .withColumn(
        "event_key",
        F.sha2(
            F.concat_ws(
                "|",
                F.col("customer_id"),
                F.col("action_id"),
                F.date_format("event_time", "yyyy-MM-dd'T'HH:mm:ss.SSSXXX"),
            ),
            256,
        ),
    )
)

required_value_missing = (
    F.col("avg_ticket").isNull()
    | F.col("purchase_frequency_30d").isNull()
    | F.col("days_since_last_purchase").isNull()
    | F.col("category_affinity").isNull()
    | F.col("historical_discount_response").isNull()
    | F.col("price_sensitivity").isNull()
    | F.col("contact_count_7d").isNull()
    | F.col("action_id").isNull()
    | F.col("action_type").isNull()
    | F.col("response").isNull()
)

quality_error = (
    F.when(F.col("event_time").isNull(), F.lit("invalid_event_time"))
    .when(F.col("customer_id").isNull() | (F.length("customer_id") == 0), F.lit("missing_customer_id"))
    .when(required_value_missing, F.lit("missing_required_value"))
    .when(F.col("avg_ticket") < 0, F.lit("negative_avg_ticket"))
    .when(~F.col("category_affinity").between(0, 1), F.lit("invalid_category_affinity"))
    .when(~F.col("historical_discount_response").between(0, 1), F.lit("invalid_discount_response"))
    .when(~F.col("price_sensitivity").between(0, 1), F.lit("invalid_price_sensitivity"))
    .when(~F.col("action_risk_penalty").between(0, 1), F.lit("invalid_risk_penalty"))
    .when(~F.col("response").isin(0, 1), F.lit("invalid_response"))
)

checked = conformed.withColumn("_quality_error", quality_error)
quarantine = checked.filter(F.col("_quality_error").isNotNull())
valid = checked.filter(F.col("_quality_error").isNull()).drop("_quality_error")

window = Window.partitionBy("event_key").orderBy(F.col("_ingested_at_utc").desc())
deduped = valid.withColumn("_row_number", F.row_number().over(window)).filter("_row_number = 1").drop("_row_number")

(
    deduped.write.format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable(TARGET_TABLE)
)

if quarantine.limit(1).count() > 0:
    quarantine.write.format("delta").mode("append").saveAsTable(QUARANTINE_TABLE)

print(
    f"silver_rows={deduped.count()} quarantined={quarantine.count()} "
    f"target={TARGET_TABLE}"
)
