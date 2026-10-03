-- Run against the Lakehouse SQL analytics endpoint after Gold publication.
-- A production pipeline should fail when any assertion returns a non-zero count.

SELECT COUNT(*) AS invalid_label_count
FROM gold.nba_training_features
WHERE response NOT IN (0, 1) OR response IS NULL;

SELECT COUNT(*) AS invalid_probability_feature_count
FROM gold.nba_training_features
WHERE category_affinity NOT BETWEEN 0 AND 1
   OR historical_discount_response NOT BETWEEN 0 AND 1
   OR price_sensitivity NOT BETWEEN 0 AND 1
   OR action_risk_penalty NOT BETWEEN 0 AND 1;

SELECT COUNT(*) AS missing_key_count
FROM gold.nba_training_features
WHERE customer_id IS NULL OR action_id IS NULL OR event_time IS NULL;

SELECT customer_id, action_id, event_time, COUNT(*) AS duplicate_count
FROM gold.nba_training_features
GROUP BY customer_id, action_id, event_time
HAVING COUNT(*) > 1;
