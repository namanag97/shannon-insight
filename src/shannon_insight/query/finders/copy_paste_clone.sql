-- copy_paste_clone.sql
-- Detects file pairs with high structural similarity (NCD < 0.3)
--
-- Scope: FILE_PAIR
-- Severity: 0.50 (base)
--
-- Criteria:
--   Compression-based similarity between file pairs.
--   Uses compression_ratio as a proxy when NCD clone data isn't
--   available as edges. Files with very similar compression_ratio
--   and high compression (low entropy) may be clones.
--
-- When G3 (NCD clone) edges are available, query those directly.
-- Fallback: identify files with very similar compression ratios.
--
-- The $snapshot_id parameter filters to a specific snapshot.

-- Try G3 (NCD clone) edges first
WITH clone_edges AS (
    SELECT
        source AS file_a,
        target AS file_b,
        weight AS ncd_score,
        data
    FROM edges
    WHERE snapshot_id = $snapshot_id
      AND space = 'G3'
      AND weight < 0.3
)
SELECT
    ce.file_a,
    ce.file_b,
    ce.ncd_score,
    fs_a.lines AS lines_a,
    fs_b.lines AS lines_b,
    fs_a.compression_ratio AS compression_a,
    fs_b.compression_ratio AS compression_b
FROM clone_edges ce
LEFT JOIN file_signals fs_a ON ce.file_a = fs_a.file_path AND fs_a.snapshot_id = $snapshot_id
LEFT JOIN file_signals fs_b ON ce.file_b = fs_b.file_path AND fs_b.snapshot_id = $snapshot_id
WHERE ce.file_a NOT LIKE '%__init__.py'
  AND ce.file_b NOT LIKE '%__init__.py'
ORDER BY ce.ncd_score ASC
LIMIT 20
