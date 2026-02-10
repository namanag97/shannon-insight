-- unstable_file.sql
-- Detects files with churning/spiking trajectory above median changes
--
-- Scope: FILE
-- Severity: 0.7 (base)
-- Hotspot-filtered: requires total_changes > median
--
-- Criteria:
--   churn_trajectory IN ('CHURNING', 'SPIKING')
--   AND total_changes > median(total_changes)
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
    fs.churn_trajectory,
    fs.total_changes,
    fs.churn_slope,
    fs.churn_cv,
    fs.fix_ratio,
    m.median_val AS changes_median
FROM file_signals fs
CROSS JOIN median_changes m
WHERE fs.snapshot_id = $snapshot_id
  AND fs.churn_trajectory IN ('CHURNING', 'SPIKING')
  AND fs.total_changes > m.median_val
  -- Exclude test files
  AND COALESCE(fs.role, '') != 'TEST'
  AND fs.file_path NOT LIKE '%test_%'
  AND fs.file_path NOT LIKE '%_test.py'
ORDER BY fs.total_changes DESC, fs.churn_slope DESC
