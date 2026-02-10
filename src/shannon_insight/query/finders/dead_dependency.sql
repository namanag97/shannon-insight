-- dead_dependency.sql
-- Detects structural dependencies with zero co-change
--
-- Scope: FILE_PAIR
-- Severity: 0.4 (base)
--
-- Criteria:
--   1. G1 (dependency) edge exists between source and target
--   2. No G4 (cochange) edge between the pair in either direction
--   3. Both files have total_changes >= 50
--
-- The $snapshot_id parameter filters to a specific snapshot.

WITH dependency AS (
    SELECT source, target
    FROM edges
    WHERE snapshot_id = $snapshot_id
      AND space = 'G1'
),
cochange AS (
    SELECT DISTINCT source, target
    FROM edges
    WHERE snapshot_id = $snapshot_id
      AND space = 'G4'
)
SELECT
    d.source AS file_a,
    d.target AS file_b,
    fs_a.total_changes AS source_changes,
    fs_b.total_changes AS target_changes,
    fs_a.pagerank AS source_pagerank,
    fs_b.pagerank AS target_pagerank
FROM dependency d
-- Ensure both files exist in file_signals
JOIN file_signals fs_a ON d.source = fs_a.file_path AND fs_a.snapshot_id = $snapshot_id
JOIN file_signals fs_b ON d.target = fs_b.file_path AND fs_b.snapshot_id = $snapshot_id
-- Anti-join: no cochange edge in either direction
LEFT JOIN cochange c1 ON d.source = c1.source AND d.target = c1.target
LEFT JOIN cochange c2 ON d.target = c2.source AND d.source = c2.target
WHERE c1.source IS NULL
  AND c2.source IS NULL
  -- Both files must have significant history
  AND fs_a.total_changes >= 50
  AND fs_b.total_changes >= 50
  -- Exclude __init__.py pairs
  AND d.source NOT LIKE '%__init__.py'
  AND d.target NOT LIKE '%__init__.py'
ORDER BY (fs_a.total_changes + fs_b.total_changes) DESC
LIMIT 30
