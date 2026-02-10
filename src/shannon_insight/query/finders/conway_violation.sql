-- conway_violation.sql
-- Detects module pairs with structural coupling but separate teams
--
-- Scope: MODULE_PAIR
-- Severity: 0.55 (base)
--
-- Criteria:
--   d_author(M1, M2) > 0.8 AND structural_coupling(M1, M2) > 0.3
--
-- Uses G5 (author distance) edges between modules if available,
-- otherwise falls back to module-level signals (knowledge_gini).
-- Structural coupling is derived from cross-module G1 edges.
--
-- The $snapshot_id parameter filters to a specific snapshot.

WITH cross_module_edges AS (
    -- Count G1 edges between different modules
    SELECT
        fs_s.community AS source_module,
        fs_t.community AS target_module,
        COUNT(*) AS edge_count
    FROM edges e
    JOIN file_signals fs_s ON e.source = fs_s.file_path AND fs_s.snapshot_id = $snapshot_id
    JOIN file_signals fs_t ON e.target = fs_t.file_path AND fs_t.snapshot_id = $snapshot_id
    WHERE e.snapshot_id = $snapshot_id
      AND e.space = 'G1'
      AND fs_s.community != fs_t.community
    GROUP BY fs_s.community, fs_t.community
),
module_pairs AS (
    -- Get pairs of modules with their coupling strength
    SELECT
        ms_a.module_path AS module_a,
        ms_b.module_path AS module_b,
        ms_a.knowledge_gini AS gini_a,
        ms_b.knowledge_gini AS gini_b,
        ms_a.module_bus_factor AS bus_factor_a,
        ms_b.module_bus_factor AS bus_factor_b,
        ms_a.coupling AS coupling_a,
        ms_b.coupling AS coupling_b
    FROM module_signals ms_a
    JOIN module_signals ms_b ON ms_a.snapshot_id = ms_b.snapshot_id
        AND ms_a.module_path < ms_b.module_path
    WHERE ms_a.snapshot_id = $snapshot_id
      AND ms_a.file_count >= 2
      AND ms_b.file_count >= 2
      -- Proxy for author distance: high knowledge_gini means concentrated ownership
      -- If both modules have high gini and different owners, likely different teams
      AND ms_a.knowledge_gini > 0.5
      AND ms_b.knowledge_gini > 0.5
      -- At least one must have structural coupling
      AND (ms_a.coupling > 0.3 OR ms_b.coupling > 0.3)
)
SELECT
    mp.module_a,
    mp.module_b,
    mp.gini_a,
    mp.gini_b,
    mp.bus_factor_a,
    mp.bus_factor_b,
    mp.coupling_a,
    mp.coupling_b
FROM module_pairs mp
ORDER BY GREATEST(mp.coupling_a, mp.coupling_b) DESC
LIMIT 20
