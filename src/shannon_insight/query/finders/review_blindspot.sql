-- review_blindspot.sql
-- Detects high-centrality files with single owner and no tests
--
-- Scope: FILE
-- Severity: 0.80 (base)
-- Hotspot-filtered: requires total_changes > median
--
-- Criteria (tightened):
--   pctl(pagerank) > 0.80
--   AND bus_factor <= 1.5
--   AND no corresponding test file
--   AND total_changes > median(total_changes)
--
-- Test file detection: check if a file named test_<name>.py or <name>_test.py
-- exists in the same snapshot for the same base name.
--
-- The $snapshot_id parameter filters to a specific snapshot.

WITH median_changes AS (
    SELECT PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY total_changes) AS median_val
    FROM file_signals
    WHERE snapshot_id = $snapshot_id
      AND COALESCE(role, '') != 'TEST'
      AND total_changes > 0
),
ranked AS (
    SELECT
        file_path,
        bus_factor,
        author_entropy,
        pagerank,
        total_changes,
        role,
        in_degree,
        PERCENT_RANK() OVER (ORDER BY pagerank) AS pagerank_pctl
    FROM file_signals
    WHERE snapshot_id = $snapshot_id
),
test_files AS (
    SELECT file_path
    FROM file_signals
    WHERE snapshot_id = $snapshot_id
      AND (role = 'TEST' OR file_path LIKE '%test_%' OR file_path LIKE '%_test.py')
)
SELECT
    r.file_path,
    r.bus_factor,
    r.author_entropy,
    r.pagerank,
    r.pagerank_pctl,
    r.total_changes,
    r.in_degree,
    m.median_val AS changes_median
FROM ranked r
CROSS JOIN median_changes m
WHERE r.bus_factor <= 1.5
  AND r.pagerank_pctl > 0.80
  AND r.total_changes > m.median_val
  -- Must not be a test file itself
  AND COALESCE(r.role, '') != 'TEST'
  AND r.file_path NOT LIKE '%test_%'
  AND r.file_path NOT LIKE '%_test.py'
  -- Must not have a corresponding test file
  AND NOT EXISTS (
      SELECT 1 FROM test_files tf
      WHERE tf.file_path LIKE '%test_%'
        AND (
            -- test_<filename> pattern
            tf.file_path LIKE '%test_' || regexp_extract(r.file_path, '[^/]+$', 0)
            -- Or <filename_without_ext>_test.py pattern
            OR tf.file_path LIKE '%' || replace(regexp_extract(r.file_path, '[^/]+$', 0), '.py', '_test.py')
        )
  )
ORDER BY r.pagerank_pctl DESC, r.bus_factor ASC
LIMIT 10
