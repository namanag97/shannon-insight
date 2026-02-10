-- hidden_coupling.sql
-- Detects file pairs that co-change without structural dependency
--
-- Scope: FILE_PAIR
-- Severity: 0.9 (base)
--
-- Criteria:
--   1. G4 (cochange) edge exists with lift >= 2.0 and confidence >= 0.5
--   2. No G1 (dependency) edge between the pair in either direction
--   3. Neither file is __init__.py
--   4. cochange_count >= 3
--
-- The $snapshot_id parameter filters to a specific snapshot.

WITH cochange AS (
    SELECT
        source AS file_a,
        target AS file_b,
        weight,
        CAST(json_extract(data, '$.lift') AS DOUBLE) AS lift,
        CAST(json_extract(data, '$.confidence_a_b') AS DOUBLE) AS confidence_a_b,
        CAST(json_extract(data, '$.confidence_b_a') AS DOUBLE) AS confidence_b_a,
        CAST(json_extract(data, '$.cochange_count') AS INTEGER) AS cochange_count
    FROM edges
    WHERE snapshot_id = $snapshot_id
      AND space = 'G4'
),
dependency AS (
    SELECT DISTINCT source, target
    FROM edges
    WHERE snapshot_id = $snapshot_id
      AND space = 'G1'
)
SELECT
    c.file_a,
    c.file_b,
    c.lift,
    c.confidence_a_b,
    c.confidence_b_a,
    c.cochange_count,
    GREATEST(c.confidence_a_b, c.confidence_b_a) AS max_confidence,
    -- Severity: base 0.9 * strength
    0.9 * LEAST(1.0, GREATEST(0.1, (c.lift / 10.0 + GREATEST(c.confidence_a_b, c.confidence_b_a)) / 2)) AS severity
FROM cochange c
-- Anti-join: exclude pairs that have a structural dependency in either direction
LEFT JOIN dependency d1 ON c.file_a = d1.source AND c.file_b = d1.target
LEFT JOIN dependency d2 ON c.file_b = d2.source AND c.file_a = d2.target
WHERE d1.source IS NULL
  AND d2.source IS NULL
  -- Minimum thresholds
  AND c.cochange_count >= 3
  AND c.lift >= 2.0
  AND GREATEST(c.confidence_a_b, c.confidence_b_a) >= 0.5
  -- Exclude __init__.py pairs
  AND c.file_a NOT LIKE '%__init__.py'
  AND c.file_b NOT LIKE '%__init__.py'
ORDER BY severity DESC
LIMIT 20
