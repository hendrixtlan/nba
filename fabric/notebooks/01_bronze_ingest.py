# Fabric notebook source: 01_bronze_ingest
# Attach the Bronze lakehouse as the default lakehouse before execution.

from pyspark.sql import functions as F

spark.sql("CREATE SCHEMA IF NOT EXISTS bronze")
SOURCE_PATH = "Files/landing/nba/customer_action_events"
TARGET_TABLE = "bronze.nba_customer_action_events"

raw = spark.read.option("header", True).option("inferSchema", True).csv(SOURCE_PATH)

bronze = (
    raw.withColumn("_ingested_at_utc", F.current_timestamp())
    .withColumn("_source_file", F.input_file_name())
    .withColumn("_source_system", F.lit("portfolio_synthetic_commercial"))
)

(
    bronze.write.format("delta")
    .mode("append")
    .option("mergeSchema", "false")
    .saveAsTable(TARGET_TABLE)
)

print(f"bronze_rows={bronze.count()} target={TARGET_TABLE}")
