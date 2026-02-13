-- chronic_problem.sql
-- Detects findings that have persisted across 3+ snapshots
--
-- Scope: (wraps another finding)
-- Severity: base_severity * 1.25
--
-- Criteria:
--   Same finding (by identity_key) appears in 3+ snapshots
--
-- The $snapshot_id parameter filters to the CURRENT snapshot.
-- We look backward across all snapshots to count persistence.

WITH finding_history AS (
    SELECT
        identity_key,
        finding_type,
        COUNT(DISTINCT snapshot_id) AS snapshot_count,
        MIN(snapshot_id) AS first_seen_snapshot,
        MAX(severity) AS max_severity,
        -- Get latest data
        FIRST(title ORDER BY snapshot_id DESC) AS title,
        FIRST(files ORDER BY snapshot_id DESC) AS files,
        FIRST(suggestion ORDER BY snapshot_id DESC) AS suggestion,
        FIRST(confidence ORDER BY snapshot_id DESC) AS confidence,
        FIRST(effort ORDER BY snapshot_id DESC) AS effort,
        FIRST(scope ORDER BY snapshot_id DESC) AS scope
    FROM findings
    GROUP BY identity_key, finding_type
    HAVING COUNT(DISTINCT snapshot_id) >= 3
),
-- Ensure the finding still exists in the current snapshot
current_findings AS (
    SELECT identity_key
    FROM findings
    WHERE snapshot_id = $snapshot_id
)
SELECT
    fh.identity_key,
    fh.finding_type,
    fh.snapshot_count,
    fh.first_seen_snapshot,
    fh.max_severity,
    -- Severity scaled up by persistence
    LEAST(1.0, fh.max_severity * 1.25) AS chronic_severity,
    fh.title,
    fh.files,
    fh.suggestion,
    fh.confidence,
    fh.effort,
    fh.scope
FROM finding_history fh
JOIN current_findings cf ON fh.identity_key = cf.identity_key
ORDER BY fh.snapshot_count DESC, chronic_severity DESC
LIMIT 10
