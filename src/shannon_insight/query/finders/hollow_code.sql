-- hollow_code.sql
-- Detects files with mostly stub/empty function implementations
--
-- Scope: FILE
-- Severity: 0.71 (base)
-- Structural-only: does not require change activity
--
-- Criteria (tightened):
--   stub_ratio > 0.6 AND impl_gini > 0.6
--   AND function_count >= 3 (minimum meaningful functions)
--
-- The $snapshot_id parameter filters to a specific snapshot.

SELECT
    file_path,
    stub_ratio,
    impl_gini,
    function_count,
    lines,
    role
FROM file_signals
WHERE snapshot_id = $snapshot_id
  AND stub_ratio > 0.6
  AND impl_gini > 0.6
  -- Must have enough functions to be meaningfully hollow
  AND function_count >= 3
  -- Exclude test files
  AND COALESCE(role, '') != 'TEST'
  AND file_path NOT LIKE '%test_%'
  AND file_path NOT LIKE '%_test.py'
ORDER BY stub_ratio DESC, impl_gini DESC
