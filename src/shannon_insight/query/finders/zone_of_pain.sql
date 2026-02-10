-- zone_of_pain.sql
-- Detects modules in the "zone of pain" (concrete + stable = hard to change)
--
-- Scope: MODULE
-- Severity: 0.60 (base)
--
-- Criteria:
--   instability IS NOT NULL AND abstractness < 0.3 AND instability < 0.3
--
-- The $snapshot_id parameter filters to a specific snapshot.

SELECT
    module_path,
    abstractness,
    instability,
    main_seq_distance,
    file_count,
    coupling,
    cohesion,
    health_score
FROM module_signals
WHERE snapshot_id = $snapshot_id
  AND instability IS NOT NULL
  AND abstractness < 0.3
  AND instability < 0.3
  -- Exclude trivial modules
  AND file_count >= 3
ORDER BY
    -- Worst modules first: deeper in the zone of pain
    (abstractness + instability) ASC
