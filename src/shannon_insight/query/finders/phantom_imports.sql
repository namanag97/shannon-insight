-- phantom_imports.sql
-- Detects files with unresolved (phantom) imports
--
-- Scope: FILE
-- Severity: 0.65 (base)
-- Structural-only: does not require change activity
--
-- Criteria:
--   phantom_import_count > 0
--
-- The $snapshot_id parameter filters to a specific snapshot.

SELECT
    file_path,
    phantom_import_count,
    import_count,
    role,
    -- phantom_ratio: fraction of imports that are phantoms
    CASE WHEN import_count > 0
        THEN CAST(phantom_import_count AS DOUBLE) / CAST(import_count AS DOUBLE)
        ELSE 1.0
    END AS phantom_ratio
FROM file_signals
WHERE snapshot_id = $snapshot_id
  AND phantom_import_count > 0
  -- Exclude test files
  AND COALESCE(role, '') != 'TEST'
  AND file_path NOT LIKE '%test_%'
  AND file_path NOT LIKE '%_test.py'
ORDER BY phantom_import_count DESC, file_path
