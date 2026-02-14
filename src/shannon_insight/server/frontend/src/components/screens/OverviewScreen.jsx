/**
 * Overview screen - health score hero, stat strip, category summary,
 * risk histogram, and focus point.
 */

import useStore from "../../state/store.js";
import { fmtN } from "../../utils/formatters.js";
import { hColor } from "../../utils/helpers.js";
import { CATEGORY_ORDER, CATEGORY_LABELS } from "../../utils/constants.js";
import { MetricCard } from "../cards/MetricCard.jsx";
import { CategoryRow } from "../cards/CategoryRow.jsx";
import { FocusPoint } from "../cards/FocusPoint.jsx";
import { RiskHistogram } from "../charts/RiskHistogram.jsx";

export function OverviewScreen() {
  const data = useStore((s) => s.data);
  if (!data) return null;

  const score = data.health;
  const color = hColor(score);
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
          <div class="health-label" style={{ color: "var(--text-secondary)" }}>
            {data.health_label || ""}
          </div>
        </div>
      </div>

      {/* Stat strip */}
      <div class="stat-strip">
        <MetricCard value={fmtN(data.file_count)} label="files" />
        <MetricCard value={fmtN(data.module_count)} label="modules" />
        <MetricCard value={fmtN(data.commits_analyzed)} label="commits" />
        <MetricCard
          value={fmtN(totalIssues)}
          label="issues"
          style={totalIssues > 0 ? { color: "var(--orange)" } : undefined}
        />
      </div>

      {/* Two-column content */}
      <div class="overview-cols">
        <div class="card">
          <div class="card-title">Issue Summary</div>
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
          <div class="card-title">Focus Point</div>
          <FocusPoint focus={data.focus} />
        </div>
      </div>
    </div>
  );
}
