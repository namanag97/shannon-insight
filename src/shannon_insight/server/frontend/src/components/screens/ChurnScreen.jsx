/**
 * Churn Explorer screen - timeline view of file stability,
 * filtered by trajectory (rising/stable/declining).
 * Shows temporal patterns across the codebase.
 */

import useStore from "../../state/store.js";
import { fmtF, fmtN } from "../../utils/formatters.js";
import { Sparkline } from "../charts/Sparkline.jsx";

const TRAJECTORY_FILTERS = [
  { key: "all", label: "All Files" },
  { key: "rising", label: "Rising" },
  { key: "stable", label: "Stable" },
  { key: "declining", label: "Declining" },
  { key: "hotspot", label: "Hotspots" },
];

function classifyTrajectory(trajectory) {
  if (trajectory == null) return "unknown";
  if (trajectory > 0.3) return "rising";
  if (trajectory < -0.3) return "declining";
  return "stable";
}

function trajectoryBadgeClass(traj) {
  if (traj === "rising") return "churn-trajectory-badge rising";
  if (traj === "declining") return "churn-trajectory-badge declining";
  if (traj === "stable") return "churn-trajectory-badge stable";
  return "churn-trajectory-badge new";
}

export function ChurnScreen() {
  const data = useStore((s) => s.data);
  const trajectoryFilter = useStore((s) => s.churnTrajectoryFilter);
  const sortKey = useStore((s) => s.churnSortKey);
  const sortAsc = useStore((s) => s.churnSortAsc);
  const setFilter = useStore((s) => s.setChurnTrajectoryFilter);
  const setSortKey = useStore((s) => s.setChurnSortKey);

  if (!data || !data.files) {
    return (
      <div class="empty-state">
        <div class="empty-state-title">No file data available</div>
        <div class="empty-state-hint">
          Run analysis with git history to see churn patterns.
        </div>
      </div>
    );
  }

  // Build file entries with churn data
  let entries = [];
  for (const path in data.files) {
    const f = data.files[path];
    const trajectory = classifyTrajectory(f.signals?.churn_trajectory);
    entries.push({
      path,
      total_changes: f.total_changes || 0,
      churn_cv: f.churn_cv || 0,
      bus_factor: f.bus_factor || 1,
      risk_score: f.risk_score || 0,
      trajectory,
      churn_trajectory: f.signals?.churn_trajectory,
      fix_ratio: f.signals?.fix_ratio || 0,
      finding_count: f.finding_count || 0,
      trends: f.trends,
    });
  }

  // Count per trajectory for pills
  const counts = { all: entries.length, rising: 0, stable: 0, declining: 0, hotspot: 0 };
  for (const e of entries) {
    if (e.trajectory === "rising") counts.rising++;
    if (e.trajectory === "stable") counts.stable++;
    if (e.trajectory === "declining") counts.declining++;
    if (e.total_changes > 20 && e.finding_count > 0) counts.hotspot++;
  }

  // Filter
  if (trajectoryFilter === "rising") {
    entries = entries.filter((e) => e.trajectory === "rising");
  } else if (trajectoryFilter === "stable") {
    entries = entries.filter((e) => e.trajectory === "stable");
  } else if (trajectoryFilter === "declining") {
    entries = entries.filter((e) => e.trajectory === "declining");
  } else if (trajectoryFilter === "hotspot") {
    entries = entries.filter((e) => e.total_changes > 20 && e.finding_count > 0);
  }

  // Sort
  entries.sort((a, b) => {
    if (sortKey === "path") {
      return sortAsc ? a.path.localeCompare(b.path) : b.path.localeCompare(a.path);
    }
    const va = a[sortKey] != null ? a[sortKey] : 0;
    const vb = b[sortKey] != null ? b[sortKey] : 0;
    return sortAsc ? va - vb : vb - va;
  });

  // Summary stats
  const totalChanges = entries.reduce((s, e) => s + e.total_changes, 0);
  const avgCv = entries.length > 0
    ? entries.reduce((s, e) => s + e.churn_cv, 0) / entries.length
    : 0;
  const avgBusFactor = entries.length > 0
    ? entries.reduce((s, e) => s + e.bus_factor, 0) / entries.length
    : 0;

  const displayed = entries.slice(0, 200);

  return (
    <div class="churn-explorer">
      <div class="section-title">Churn Explorer</div>

      {/* Summary strip */}
      <div class="signal-summary-strip">
        <div class="signal-summary-item">
          <div class="signal-summary-val">{fmtN(entries.length)}</div>
          <div class="signal-summary-label">Files</div>
        </div>
        <div class="signal-summary-item">
          <div class="signal-summary-val">{fmtN(totalChanges)}</div>
          <div class="signal-summary-label">Total Commits</div>
        </div>
        <div class="signal-summary-item">
          <div class="signal-summary-val">{fmtF(avgCv, 2)}</div>
          <div class="signal-summary-label">Avg Volatility</div>
        </div>
        <div class="signal-summary-item">
          <div class="signal-summary-val">{fmtF(avgBusFactor, 1)}</div>
          <div class="signal-summary-label">Avg Bus Factor</div>
        </div>
        <div class="signal-summary-item">
          <div class="signal-summary-val" style={{ color: counts.rising > 0 ? "var(--orange)" : "var(--text)" }}>
            {counts.rising}
          </div>
          <div class="signal-summary-label">Rising</div>
        </div>
      </div>

      {/* Trajectory filter pills */}
      <div class="trajectory-pills">
        {TRAJECTORY_FILTERS.map((tf) => (
          <button
            key={tf.key}
            class={`trajectory-pill${trajectoryFilter === tf.key ? " active" : ""}`}
            onClick={() => setFilter(tf.key)}
          >
            {tf.label}
            <span class="pill-count">{counts[tf.key]}</span>
          </button>
        ))}

        {/* Sort controls */}
        <select
          class="sort-select"
          value={sortKey}
          style={{ marginLeft: "auto" }}
          onChange={(e) => setSortKey(e.target.value)}
        >
          <option value="total_changes">Commits</option>
          <option value="churn_cv">Volatility</option>
          <option value="bus_factor">Bus Factor</option>
          <option value="risk_score">Risk</option>
          <option value="path">Path</option>
        </select>
      </div>

      {/* File list */}
      <div class="churn-timeline-container">
        {displayed.length === 0 ? (
          <div class="empty-state">
            <div class="empty-state-title">No files match this filter</div>
          </div>
        ) : (
          <div>
            {displayed.map((entry) => (
              <div
                key={entry.path}
                class="churn-file-row"
                onClick={() => { location.hash = "files/" + encodeURIComponent(entry.path); }}
              >
                <span class={trajectoryBadgeClass(entry.trajectory)}>
                  {entry.trajectory}
                </span>
                <span class="churn-file-path">{entry.path}</span>
                <div class="churn-file-stats">
                  <div class="churn-file-stat">
                    <span class="churn-file-stat-val">{entry.total_changes}</span>
                    <span class="churn-file-stat-label">commits</span>
                  </div>
                  <div class="churn-file-stat">
                    <span class="churn-file-stat-val">{fmtF(entry.churn_cv, 2)}</span>
                    <span class="churn-file-stat-label">cv</span>
                  </div>
                  <div class="churn-file-stat">
                    <span class="churn-file-stat-val">{fmtF(entry.bus_factor, 1)}</span>
                    <span class="churn-file-stat-label">bus</span>
                  </div>
                  {entry.trends && entry.trends.total_changes && (
                    <Sparkline
                      values={entry.trends.total_changes}
                      width={64}
                      height={18}
                      color={entry.trajectory === "rising" ? "var(--orange)" : "var(--accent)"}
                    />
                  )}
                </div>
              </div>
            ))}
            {entries.length > 200 && (
              <div class="file-count-note">
                Showing 200 of {entries.length} files
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
