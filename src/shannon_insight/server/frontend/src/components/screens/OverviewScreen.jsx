/**
 * Overview screen - health score hero, stat strip, category summary,
 * risk histogram, and focus point.
 *
 * v2: Improved visual hierarchy, added health ring visualization,
 * enhanced stat cards with hover states, cleaner category layout.
 */

import useStore from "../../state/store.js";
import { fmtN } from "../../utils/formatters.js";
import { hColor } from "../../utils/helpers.js";
import { CATEGORY_ORDER, CATEGORY_LABELS, CATEGORY_DESCRIPTIONS } from "../../utils/constants.js";
import { interpretHealth } from "../../utils/interpretations.js";
import { MetricCard } from "../cards/MetricCard.jsx";
import { CategoryRow } from "../cards/CategoryRow.jsx";
import { FocusPoint } from "../cards/FocusPoint.jsx";
import { RiskHistogram } from "../charts/RiskHistogram.jsx";

/**
 * SVG ring visualization for the health score.
 * Shows a circular progress indicator around the numeric score.
 */
function HealthRing({ score, color, size = 120 }) {
  const r = (size - 8) / 2;
  const circumference = 2 * Math.PI * r;
  const progress = Math.max(0, Math.min(score / 10, 1));
  const dashOffset = circumference * (1 - progress);

  return (
    <svg width={size} height={size} style={{ position: "absolute", top: "50%", left: "50%", transform: "translate(-50%, -50%)" }}>
      {/* Background ring */}
      <circle
        cx={size / 2} cy={size / 2} r={r}
        fill="none" stroke="var(--border)" stroke-width="2"
      />
      {/* Progress ring */}
      <circle
        cx={size / 2} cy={size / 2} r={r}
        fill="none" stroke={color} stroke-width="2"
        stroke-dasharray={circumference}
        stroke-dashoffset={dashOffset}
        stroke-linecap="round"
        transform={`rotate(-90 ${size / 2} ${size / 2})`}
        style={{ transition: "stroke-dashoffset 0.8s ease-out" }}
        opacity="0.6"
      />
    </svg>
  );
}

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
          <div style={{ position: "relative", display: "inline-block" }}>
            <HealthRing score={score} color={color} />
            <div class="health-big" style={{ color }}>{score.toFixed(1)}</div>
          </div>
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

      {/* Two-column content */}
      <div class="overview-cols">
        <div>
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

        <div>
          <div class="card-title">Recommended Starting Point</div>
          <FocusPoint focus={data.focus} />
        </div>
      </div>
    </div>
  );
}
