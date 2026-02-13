-- layer_violation.sql
-- Detects modules with backward/skip edges in inferred layer ordering
--
-- Scope: MODULE_PAIR
-- Severity: 0.52 (base)
--
-- Criteria:
--   layer_violation_count > 0 for a module
--   (We detect the specific cross-module edges that violate layer ordering)
--
-- Since we don't have explicit layer assignments in the edge data,
-- we identify modules with violations and report them.
--
-- The $snapshot_id parameter filters to a specific snapshot.

SELECT
    module_path,
    layer_violation_count,
    instability,
    abstractness,
    file_count,
    coupling,
    health_score
FROM module_signals
WHERE snapshot_id = $snapshot_id
  AND layer_violation_count > 0
  AND file_count >= 2
ORDER BY layer_violation_count DESC
LIMIT 10
