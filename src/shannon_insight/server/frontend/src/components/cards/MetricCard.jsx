/**
 * Metric card for stat-strip display (files, modules, commits, issues).
 */

export function MetricCard({ value, label, style }) {
  return (
    <div class="stat-card">
      <div class="stat-value" style={style}>
        {value}
      </div>
      <div class="stat-label">{label}</div>
    </div>
  );
}
