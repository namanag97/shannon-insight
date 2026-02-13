-- boundary_mismatch.sql
-- Detects modules where directory boundary doesn't match dependency structure
--
-- Scope: MODULE
-- Severity: 0.6 (base)
--
-- Criteria:
--   boundary_alignment < 0.7 AND file_count >= 3
--
-- The $snapshot_id parameter filters to a specific snapshot.

SELECT
    module_path,
    boundary_alignment,
    file_count,
    cohesion,
    coupling,
    health_score
FROM module_signals
WHERE snapshot_id = $snapshot_id
  AND boundary_alignment < 0.7
  AND file_count >= 3
ORDER BY boundary_alignment ASC
LIMIT 10
