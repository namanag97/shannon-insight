/**
 * Overview screen - health score hero, stat strip, category summary,
 * risk histogram, and focus point.
 */

import useStore from "../../state/store.js";
import { fmtN } from "../../utils/formatters.js";
import { hColor } from "../../utils/helpers.js";
import { CATEGORY_ORDER, CATEGORY_LABELS } from "../../utils/constants.js";
import { interpretHealth } from "../../utils/interpretations.js";
import { MetricCard } from "../cards/MetricCard.jsx";
import { CategoryRow } from "../cards/CategoryRow.jsx";
import { FocusPoint } from "../cards/FocusPoint.jsx";
import { RiskHistogram } from "../charts/RiskHistogram.jsx";
import { TrendChart } from "../charts/TrendChart.jsx";

export function OverviewScreen() {
  const data = useStore((s) => s.data);
  if (!data) return null;

  const score = data.health;
  const color = hColor(score);
  const healthInfo = interpretHealth(score);
  const cats = data.categories || {};

  // Total issues
  let totalIssues = 0;
  for (const k in cats) totalIssues += cats[k].count;

  // Max count for proportional bars
  let maxCount = 1;
  for (const key of CATEGORY_ORDER) {
    const c = cats[key];
    if (c && c.count > maxCount) maxCount = c.count;
  }

  function handleCatClick(catKey) {
    location.hash = "issues";
    useStore.getState().setIssueTab(catKey);
  }

  return (
    <div>
      {/* Hero */}
      <div class="hero">
        <div class="hero-score-area">
          {data.verdict && (
            <div class="verdict-banner" style={{ color: data.verdict_color || color }}>
              {data.verdict}
            </div>
          )}
          <div class="health-big" style={{ color }}>{score.toFixed(1)}</div>
          <div class="health-label-primary" style={{ color }}>
            {healthInfo.label}
          </div>
          <div class="health-explanation">
            {healthInfo.description}
          </div>
        </div>
      </div>

      {/* Stat strip */}
      <div class="stat-strip">
        <MetricCard value={fmtN(data.file_count)} label="Files Analyzed" />
        <MetricCard value={fmtN(data.module_count)} label="Modules" />
        <MetricCard value={fmtN(data.commits_analyzed)} label="Commits Scanned" />
        <MetricCard
          value={fmtN(totalIssues)}
          label="Issues Found"
          style={totalIssues > 0 ? { color: "var(--orange)" } : undefined}
        />
      </div>

      {/* Evolution & Metadata */}
      {(data.evolution || data.metadata) && (
        <div class="overview-evolution-section">
          {data.evolution && (
            <div class="card">
              <div class="card-title">Codebase Evolution</div>
              <div class="evolution-charts">
                {data.evolution.file_count && data.evolution.file_count.length > 1 && (
                  <div class="evolution-chart-wrapper">
                    <TrendChart
                      values={data.evolution.file_count.map((d) => d.value)}
                      xLabels={data.evolution.file_count.map((d) =>
                        new Date(d.timestamp).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
                      )}
                      color="var(--blue)"
                      yFormat={(v) => Math.round(v).toString()}
                      width={280}
                      height={140}
                    />
                    <div class="evolution-chart-label">Files Over Time</div>
                  </div>
                )}

                {data.evolution.total_loc && data.evolution.total_loc.length > 1 && (
                  <div class="evolution-chart-wrapper">
                    <TrendChart
                      values={data.evolution.total_loc.map((d) => d.value)}
                      xLabels={data.evolution.total_loc.map((d) =>
                        new Date(d.timestamp).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
                      )}
                      color="var(--green)"
                      yFormat={(v) => (v / 1000).toFixed(1) + "k"}
                      width={280}
                      height={140}
                    />
                    <div class="evolution-chart-label">Lines of Code</div>
                  </div>
                )}

                {data.evolution.avg_complexity && data.evolution.avg_complexity.length > 1 && (
                  <div class="evolution-chart-wrapper">
                    <TrendChart
                      values={data.evolution.avg_complexity.map((d) => d.value)}
                      xLabels={data.evolution.avg_complexity.map((d) =>
                        new Date(d.timestamp).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
                      )}
                      color="var(--orange)"
                      yFormat={(v) => v.toFixed(1)}
                      width={280}
                      height={140}
                    />
                    <div class="evolution-chart-label">Avg Complexity</div>
                  </div>
                )}

                {data.evolution.avg_risk && data.evolution.avg_risk.length > 1 && (
                  <div class="evolution-chart-wrapper">
                    <TrendChart
                      values={data.evolution.avg_risk.map((d) => d.value)}
                      xLabels={data.evolution.avg_risk.map((d) =>
                        new Date(d.timestamp).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
                      )}
                      color="var(--red)"
                      yFormat={(v) => v.toFixed(3)}
                      width={280}
                      height={140}
                    />
                    <div class="evolution-chart-label">Avg Risk Score</div>
                  </div>
                )}
              </div>
            </div>
          )}

          {data.metadata && (
            <div class="card">
              <div class="card-title">Analysis Metadata</div>
              <div class="metadata-grid">
                <div class="metadata-item">
                  <div class="metadata-value">{fmtN(data.metadata.files_scanned)}</div>
                  <div class="metadata-label">Files Scanned</div>
                </div>
                <div class="metadata-item">
                  <div class="metadata-value">{fmtN(data.metadata.modules_detected)}</div>
                  <div class="metadata-label">Modules Detected</div>
                </div>
                <div class="metadata-item">
                  <div class="metadata-value">{fmtN(data.metadata.commits_processed)}</div>
                  <div class="metadata-label">Commits Processed</div>
                </div>
                <div class="metadata-item">
                  <div class="metadata-value">{data.metadata.snapshot_count}</div>
                  <div class="metadata-label">Snapshots</div>
                </div>
                <div class="metadata-item">
                  <div class="metadata-value">{data.metadata.db_size_mb.toFixed(1)} MB</div>
                  <div class="metadata-label">Database Size</div>
                </div>
                <div class="metadata-item">
                  <div class="metadata-value">{data.metadata.analyzers_ran?.length || 0}</div>
                  <div class="metadata-label">Analyzers Ran</div>
                </div>
              </div>
              {data.metadata.analyzers_ran && data.metadata.analyzers_ran.length > 0 && (
                <div class="metadata-analyzers">
                  {data.metadata.analyzers_ran.map((a) => (
                    <span key={a} class="analyzer-badge">{a}</span>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Two-column content */}
      <div class="overview-cols">
        <div class="card">
          <div class="card-title">Issues by Category</div>
          <div>
            {CATEGORY_ORDER.map((key) => {
              const cat = cats[key];
              if (!cat) return null;
              return (
                <CategoryRow
                  key={key}
                  catKey={key}
                  label={CATEGORY_LABELS[key] || key}
                  cat={cat}
                  maxCount={maxCount}
                  onClick={handleCatClick}
                />
              );
            })}

            {data.recent_changes && (
              <div class="cat-delta-info" style={{ marginTop: "8px", color: "var(--accent)" }}>
                {data.recent_changes.length} files changed
              </div>
            )}

            {data.changes && (data.changes.new_findings || data.changes.resolved_findings) && (
              <div class="cat-delta-info">
                {data.changes.new_findings > 0 && (
                  <span class="cat-delta-new">+{data.changes.new_findings} new </span>
                )}
                {data.changes.resolved_findings > 0 && (
                  <span class="cat-delta-resolved">{data.changes.resolved_findings} resolved</span>
                )}
              </div>
            )}
          </div>

          <RiskHistogram files={data.files} />
        </div>

        <div class="card">
          <div class="card-title">Recommended Starting Point</div>
          <FocusPoint focus={data.focus} />
        </div>
      </div>
    </div>
  );
}
