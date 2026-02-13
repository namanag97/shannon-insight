-- naming_drift.sql
-- Detects files where filename doesn't match content
--
-- Scope: FILE
-- Severity: 0.45 (base)
-- Structural-only: does not require change activity
--
-- Criteria:
--   naming_drift > 0.7
--
-- The $snapshot_id parameter filters to a specific snapshot.

SELECT
    file_path,
    naming_drift,
    concept_count,
    role
FROM file_signals
WHERE snapshot_id = $snapshot_id
  AND naming_drift > 0.7
  -- Exclude test files
  AND COALESCE(role, '') != 'TEST'
  AND file_path NOT LIKE '%test_%'
  AND file_path NOT LIKE '%_test.py'
  -- Exclude __init__.py (common to be unfocused)
  AND file_path NOT LIKE '%__init__.py'
ORDER BY naming_drift DESC
LIMIT 10
