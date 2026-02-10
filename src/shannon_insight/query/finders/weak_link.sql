-- weak_link.sql
-- Detects files that are much worse than their structural neighbors
-- (health Laplacian delta_h)
--
-- Scope: FILE
-- Severity: 0.75 (base)
-- Hotspot-filtered: requires total_changes > median
--
-- Criteria:
--   delta_h > 0.4 (file much worse than neighbors)
--   AND total_changes > median(total_changes)
--
-- delta_h is pre-computed in file_signals (health Laplacian:
-- difference between file's raw_risk and mean of neighbors' raw_risk)
--
-- The $snapshot_id parameter filters to a specific snapshot.

WITH median_changes AS (
    SELECT PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY total_changes) AS median_val
    FROM file_signals
    WHERE snapshot_id = $snapshot_id
      AND COALESCE(role, '') != 'TEST'
)
SELECT
    fs.file_path,
    fs.delta_h,
    fs.raw_risk,
    fs.risk_score,
    fs.total_changes,
    fs.pagerank,
    fs.cognitive_load,
    m.median_val AS changes_median
FROM file_signals fs
CROSS JOIN median_changes m
WHERE fs.snapshot_id = $snapshot_id
  AND fs.delta_h > 0.4
  AND fs.total_changes > m.median_val
  -- Exclude test files
  AND COALESCE(fs.role, '') != 'TEST'
  AND fs.file_path NOT LIKE '%test_%'
  AND fs.file_path NOT LIKE '%_test.py'
ORDER BY fs.delta_h DESC
