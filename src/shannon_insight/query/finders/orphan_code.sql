-- orphan_code.sql
-- Detects orphan files: is_orphan=true AND not __init__.py
--
-- Scope: FILE
-- Severity: 0.55 (constant)
-- Structural-only: does not require change activity
--
-- The $snapshot_id parameter filters to a specific snapshot.

SELECT
    file_path,
    in_degree,
    role,
    depth,
    is_orphan
FROM file_signals
WHERE snapshot_id = $snapshot_id
  AND is_orphan = true
  AND file_path NOT LIKE '%__init__.py'
  -- Exclude test files (role-based or path-based)
  AND COALESCE(role, '') != 'TEST'
  AND file_path NOT LIKE '%test_%'
  AND file_path NOT LIKE '%_test.py'
ORDER BY file_path
