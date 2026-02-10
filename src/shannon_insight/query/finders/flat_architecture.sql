-- flat_architecture.sql
-- Detects flat dependency structure (no composition layer)
--
-- Scope: CODEBASE
-- Severity: 0.60 (base)
-- Structural-only: does not require change activity
--
-- Criteria:
--   max(depth) <= 1 AND glue_deficit > 0.5
--
-- The $snapshot_id parameter filters to a specific snapshot.

SELECT
    MAX(fs.depth) AS max_depth,
    gs.glue_deficit,
    COUNT(DISTINCT fs.file_path) AS file_count,
    gs.orphan_ratio
FROM file_signals fs
JOIN global_signals gs ON fs.snapshot_id = gs.snapshot_id
WHERE fs.snapshot_id = $snapshot_id
  AND fs.depth IS NOT NULL
GROUP BY gs.glue_deficit, gs.orphan_ratio
HAVING MAX(fs.depth) <= 1
   AND gs.glue_deficit > 0.5
