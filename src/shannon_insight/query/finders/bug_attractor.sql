-- bug_attractor.sql
-- Detects central files where most changes are bug fixes
--
-- Scope: FILE
-- Severity: 0.70 (base)
-- Hotspot-filtered: requires total_changes > median
--
-- Criteria:
--   fix_ratio > 0.4 AND pctl(pagerank) > 0.75
--   AND total_changes > median(total_changes)
--
-- The $snapshot_id parameter filters to a specific snapshot.

WITH median_changes AS (
    SELECT PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY total_changes) AS median_val
    FROM file_signals
    WHERE snapshot_id = $snapshot_id
      AND COALESCE(role, '') != 'TEST'
),
ranked AS (
    SELECT
        file_path,
        fix_ratio,
        pagerank,
        total_changes,
        blast_radius_size,
        role,
        PERCENT_RANK() OVER (ORDER BY pagerank) AS pagerank_pctl
    FROM file_signals
    WHERE snapshot_id = $snapshot_id
)
SELECT
    r.file_path,
    r.fix_ratio,
    r.pagerank,
    r.pagerank_pctl,
    r.total_changes,
    r.blast_radius_size,
    m.median_val AS changes_median
FROM ranked r
CROSS JOIN median_changes m
WHERE r.fix_ratio > 0.4
  AND r.pagerank_pctl > 0.75
  AND r.total_changes > m.median_val
  -- Exclude test files
  AND COALESCE(r.role, '') != 'TEST'
  AND r.file_path NOT LIKE '%test_%'
  AND r.file_path NOT LIKE '%_test.py'
ORDER BY r.fix_ratio DESC, r.pagerank_pctl DESC
