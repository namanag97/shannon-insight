-- architecture_erosion.sql
-- Detects increasing violation rate over multiple snapshots
--
-- Scope: CODEBASE
-- Severity: 0.65 (base)
--
-- Criteria:
--   violation_rate increasing over 3+ snapshots
--
-- The $snapshot_id parameter filters to the CURRENT snapshot.
-- We look at historical snapshots to detect the trend.

WITH violation_history AS (
    SELECT
        gs.snapshot_id,
        s.timestamp,
        gs.violation_rate,
        gs.architecture_health,
        ROW_NUMBER() OVER (ORDER BY s.timestamp) AS snapshot_order,
        COUNT(*) OVER () AS total_snapshots
    FROM global_signals gs
    JOIN snapshots s ON gs.snapshot_id = s.snapshot_id
    -- Only consider snapshots up to and including the current one
    WHERE s.timestamp <= (SELECT timestamp FROM snapshots WHERE snapshot_id = $snapshot_id)
),
halved AS (
    SELECT
        total_snapshots,
        violation_rate,
        architecture_health,
        snapshot_order,
        CASE WHEN snapshot_order <= total_snapshots / 2 THEN violation_rate END AS first_half_vr,
        CASE WHEN snapshot_order > total_snapshots / 2 THEN violation_rate END AS second_half_vr,
        CASE WHEN snapshot_order = total_snapshots THEN violation_rate END AS latest_vr,
        CASE WHEN snapshot_order = total_snapshots THEN architecture_health END AS latest_ah,
        CASE WHEN snapshot_order = 1 THEN violation_rate END AS first_vr
    FROM violation_history
),
trend AS (
    SELECT
        MAX(total_snapshots) AS snapshot_count,
        AVG(first_half_vr) AS first_half_avg,
        AVG(second_half_vr) AS second_half_avg,
        MAX(latest_vr) AS latest_violation_rate,
        MAX(latest_ah) AS latest_arch_health,
        MAX(first_vr) AS first_violation_rate
    FROM halved
)
SELECT
    snapshot_count,
    latest_violation_rate,
    first_violation_rate,
    latest_arch_health,
    first_half_avg,
    second_half_avg,
    (second_half_avg - first_half_avg) AS violation_rate_delta
FROM trend
WHERE snapshot_count >= 3
  AND second_half_avg > first_half_avg
  -- Must have meaningful violations
  AND latest_violation_rate > 0.1
