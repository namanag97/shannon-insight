-- god_file.sql
-- Detects complex files with low coherence (doing too many things)
--
-- Scope: FILE
-- Severity: 0.8 (base)
--
-- Criteria (tightened):
--   pctl(cognitive_load) >= 0.95 AND pctl(semantic_coherence) < 0.20
--   AND function_count >= 3 (minimum size)
--   AND total_changes > 0 (hotspot gate)
--
-- Percentiles are computed on-the-fly via PERCENT_RANK().
-- The $snapshot_id parameter filters to a specific snapshot.

WITH ranked AS (
    SELECT
        file_path,
        cognitive_load,
        semantic_coherence,
        function_count,
        concept_count,
        concept_entropy,
        lines,
        total_changes,
        PERCENT_RANK() OVER (ORDER BY cognitive_load) AS cognitive_load_pctl,
        PERCENT_RANK() OVER (ORDER BY semantic_coherence) AS coherence_pctl
    FROM file_signals
    WHERE snapshot_id = $snapshot_id
)
SELECT
    file_path,
    cognitive_load,
    cognitive_load_pctl,
    semantic_coherence,
    coherence_pctl,
    function_count,
    concept_count,
    concept_entropy,
    lines,
    total_changes
FROM ranked
WHERE
    -- Hotspot gate: must have change activity
    total_changes > 0
    -- Minimum function count
    AND function_count >= 3
    -- Top 5% cognitive load AND bottom 20% coherence
    AND cognitive_load_pctl >= 0.95
    AND coherence_pctl < 0.20
ORDER BY
    -- Sort by the worst combination
    (cognitive_load_pctl - coherence_pctl) DESC
