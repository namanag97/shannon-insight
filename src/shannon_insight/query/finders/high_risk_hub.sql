-- high_risk_hub.sql
-- Detects central + complex + churning files
--
-- Criteria (v2 spec):
--   pctl(pagerank) >= 0.90 OR pctl(blast_radius_size) >= 0.90
--   AND (pctl(cognitive_load) >= 0.90 OR churn_trajectory IN ('CHURNING', 'SPIKING'))
--
-- Percentiles are computed on-the-fly via PERCENT_RANK().
-- The $snapshot_id parameter filters to a specific snapshot.

WITH ranked AS (
    SELECT
        file_path,
        pagerank,
        blast_radius_size,
        cognitive_load,
        in_degree,
        churn_trajectory,
        total_changes,
        PERCENT_RANK() OVER (ORDER BY pagerank) AS pagerank_pctl,
        PERCENT_RANK() OVER (ORDER BY blast_radius_size) AS blast_radius_pctl,
        PERCENT_RANK() OVER (ORDER BY cognitive_load) AS cognitive_load_pctl
    FROM file_signals
    WHERE snapshot_id = $snapshot_id
)
SELECT
    file_path,
    pagerank,
    pagerank_pctl,
    blast_radius_size,
    blast_radius_pctl,
    cognitive_load,
    cognitive_load_pctl,
    in_degree,
    churn_trajectory,
    total_changes,
    -- has_high_centrality: either percentile >= 0.90
    (pagerank_pctl >= 0.90 OR blast_radius_pctl >= 0.90) AS has_high_centrality,
    -- has_high_complexity: cognitive_load percentile >= 0.90
    (cognitive_load_pctl >= 0.90) AS has_high_complexity,
    -- has_high_churn: trajectory is CHURNING or SPIKING
    (churn_trajectory IN ('CHURNING', 'SPIKING')) AS has_high_churn
FROM ranked
WHERE
    -- Must have high centrality
    (pagerank_pctl >= 0.90 OR blast_radius_pctl >= 0.90)
    -- AND must have high complexity OR high churn
    AND (cognitive_load_pctl >= 0.90 OR churn_trajectory IN ('CHURNING', 'SPIKING'))
ORDER BY
    -- Sort by average of the qualifying percentiles descending
    (COALESCE(
        CASE WHEN pagerank_pctl >= 0.90 THEN pagerank_pctl ELSE NULL END,
        0
    ) + COALESCE(
        CASE WHEN blast_radius_pctl >= 0.90 THEN blast_radius_pctl ELSE NULL END,
        0
    )) DESC
