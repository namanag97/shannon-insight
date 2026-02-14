/**
 * Health screen - trend chart, top movers, chronic findings,
 * radar/bar concern chart, and global signals table.
 */

import useStore from "../../state/store.js";
import { hColor } from "../../utils/helpers.js";
import { fmtDate, fmtDateFull } from "../../utils/formatters.js";
import { SIGNAL_LABELS } from "../../utils/constants.js";
import { interpretSignal } from "../../utils/interpretations.js";
import { TrendChart } from "../charts/TrendChart.jsx";
import { RadarChart } from "../charts/RadarChart.jsx";
import { ConcernBar } from "../cards/ConcernCard.jsx";
import { Table } from "../ui/Table.jsx";

/* ── Column definitions for reusable Table component ── */

const MOVERS_COLUMNS = [
  {
    key: "path",
    label: "File",
    align: "left",
    format: (v) => <a href={"#files/" + encodeURIComponent(v)}>{v}</a>,
    cellClass: () => "td-path",
  },
  {
    key: "old_value",
    label: "Previous Risk",
    align: "right",
    format: (v) => v != null ? v.toFixed(3) : "--",
    cellClass: () => "td-num",
  },
  {
    key: "new_value",
    label: "Current Risk",
    align: "right",
    format: (v) => v != null ? v.toFixed(3) : "--",
    cellClass: () => "td-num",
  },
  {
    key: "delta",
    label: "Change",
    align: "right",
    format: (v) => v > 0 ? "+" + v.toFixed(3) : v.toFixed(3),
    cellClass: () => "td-num",
    cellStyle: (v) => ({
      color: v > 0 ? "var(--red)" : "var(--green)",
      fontWeight: 600,
    }),
  },
];

export function HealthScreen() {
  const data = useStore((s) => s.data);
  if (!data) return null;

  const concerns = data.concerns || [];
  const gs = data.global_signals || {};
  const gsKeys = Object.keys(gs).sort();

  // Extract health trend data
  const hasTrends = data.trends && data.trends.health && data.trends.health.length > 0;
  let trendValues = [];
  let trendLabels = [];
  let trendTimestamps = [];

  if (hasTrends) {
    for (const h of data.trends.health) {
      if (typeof h === "object") {
        trendValues.push(h.health * 9 + 1);
        trendLabels.push(fmtDate(h.timestamp));
        trendTimestamps.push(h.timestamp);
      } else {
        trendValues.push(h * 9 + 1);
        trendLabels.push("");
        trendTimestamps.push(null);
      }
    }
  }

  // Build global signals data for the Table component
  const gsData = gsKeys
    .map((key) => {
      const v = gs[key];
      if (v == null) return null;
      const display =
        typeof v === "number"
          ? Number.isInteger(v)
            ? String(v)
            : v.toFixed(4)
          : String(v);
      const label = SIGNAL_LABELS[key] || key.replace(/_/g, " ");
      const interp = typeof v === "number" ? interpretSignal(key, v) : null;
      return { _key: key, name: label, value: display, interp: interp || "" };
    })
    .filter(Boolean);

  const GS_COLUMNS = [
    {
      key: "name",
      label: "Signal",
      align: "left",
      cellClass: () => "gs-name",
    },
    {
      key: "value",
      label: "Value",
      align: "right",
      cellClass: () => "gs-val",
    },
    {
      key: "interp",
      label: "",
      align: "left",
      cellClass: () => "gs-interp",
    },
  ];

  return (
    <div class="health-screen-layout">
      {/* Health Trend Section */}
      <div class="health-section">
        <div class="section-title">Health Score Over Time</div>
        {hasTrends ? (
          <div class="card trend-chart-card">
            <TrendChart
              values={trendValues}
              xLabels={trendLabels}
              width={640}
              height={220}
              color="var(--accent)"
              yMin={1}
              yMax={10}
              ySteps={9}
              yFormat={(v) => v.toFixed(0)}
              tooltipFormat={(v) => v.toFixed(1)}
              showDots={true}
              showGrid={true}
              showFill={true}
            />
            <div class="trend-chart-subtitle">
              {trendValues.length} snapshot{trendValues.length !== 1 ? "s" : ""} tracked
            </div>
          </div>
        ) : (
          <div class="card empty-state-card">
            <div class="empty-state-inline">
              <div class="empty-state-icon">
                <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
                  <path d="M4 24L11 17L17 21L28 8" stroke="var(--text-tertiary)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
                  <circle cx="11" cy="17" r="2" fill="var(--border)" />
                  <circle cx="17" cy="21" r="2" fill="var(--border)" />
                  <circle cx="28" cy="8" r="2" fill="var(--border)" />
                </svg>
              </div>
              <div class="empty-state-message">
                <div class="empty-state-title">No trend data yet</div>
                <div class="empty-state-hint">
                  Run analysis with <code>--save</code> to track health over time.
                  Each saved snapshot adds a data point.
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Top Movers Section */}
      {data.trends && data.trends.movers && data.trends.movers.length > 0 && (
        <div class="health-section">
          <div class="section-title">Biggest Risk Changes Since Last Snapshot</div>
          <div class="card">
            <Table
              columns={MOVERS_COLUMNS}
              data={data.trends.movers}
              rowKey={(row, i) => i}
              stickyHeader={false}
            />
          </div>
        </div>
      )}

      {/* Chronic Findings Section */}
      {data.trends && data.trends.chronic && data.trends.chronic.length > 0 && (
        <div class="health-section">
          <div class="section-title">Persistent Issues (Across Multiple Snapshots)</div>
          <div class="card">
            {data.trends.chronic.map((c, i) => (
              <div class="chronic-finding-row" key={i}>
                <span class="chronic-finding-type">{c.title || c.finding_type}</span>
                <span class="chronic-finding-count">{c.count || "?"} snapshots</span>
                {c.severity != null && (
                  <span
                    class="chronic-finding-severity"
                    style={{
                      color: c.severity >= 0.8 ? "var(--red)" : c.severity >= 0.6 ? "var(--orange)" : "var(--yellow)",
                    }}
                  >
                    {c.severity.toFixed(2)}
                  </span>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Health Dimensions (Concern Chart) */}
      <div class="health-section">
        <div class="section-title">Health Breakdown by Dimension</div>
        <div class="card">
          {concerns.length >= 3 ? (
            <div class="radar-chart-container">
              <RadarChart items={concerns} />
            </div>
          ) : concerns.length > 0 ? (
            <div>
              {concerns.map((c, i) => (
                <ConcernBar key={i} concern={c} />
              ))}
            </div>
          ) : (
            <div class="empty-state-inline">
              <div class="empty-state-message">
                <div class="empty-state-title">No dimension data</div>
                <div class="empty-state-hint">Health dimensions require findings to be present.</div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Global Signals */}
      {gsData.length > 0 && (
        <div class="health-section">
          <div class="section-title">Codebase-Wide Metrics</div>
          <div class="card">
            <Table
              columns={GS_COLUMNS}
              data={gsData}
              rowKey={(row) => row._key}
              stickyHeader={false}
            />
          </div>
        </div>
      )}
    </div>
  );
}
