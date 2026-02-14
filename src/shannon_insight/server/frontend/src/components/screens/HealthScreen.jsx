/**
 * Health screen - trend chart, top movers, chronic findings,
 * radar/bar concern chart, and global signals table.
 */

import useStore from "../../state/store.js";
import { hColor } from "../../utils/helpers.js";
import { fmtDate, fmtDateFull } from "../../utils/formatters.js";
import { TrendChart } from "../charts/TrendChart.jsx";
import { RadarChart } from "../charts/RadarChart.jsx";
import { ConcernBar } from "../cards/ConcernCard.jsx";

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
        trendValues.push(h.health);
        trendLabels.push(fmtDate(h.timestamp));
        trendTimestamps.push(h.timestamp);
      } else {
        trendValues.push(h);
        trendLabels.push("");
        trendTimestamps.push(null);
      }
    }
  }

  return (
    <div class="health-screen-layout">
      {/* Health Trend Section */}
      <div class="health-section">
        <div class="section-title">Health Trend</div>
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
          <div class="section-title">Top Movers</div>
          <div class="card">
            <table class="movers-table">
              <thead>
                <tr>
                  <th>File</th>
                  <th class="num">Previous</th>
                  <th class="num">Current</th>
                  <th class="num">Delta</th>
                </tr>
              </thead>
              <tbody>
                {data.trends.movers.map((m, i) => {
                  const dc = m.delta > 0 ? "var(--red)" : "var(--green)";
                  const ds = m.delta > 0 ? "+" + m.delta.toFixed(3) : m.delta.toFixed(3);
                  return (
                    <tr key={i}>
                      <td class="td-path">
                        <a href={"#files/" + encodeURIComponent(m.path)}>{m.path}</a>
                      </td>
                      <td class="td-num">{m.old_value != null ? m.old_value.toFixed(3) : "--"}</td>
                      <td class="td-num">{m.new_value != null ? m.new_value.toFixed(3) : "--"}</td>
                      <td class="td-num" style={{ color: dc, fontWeight: 600 }}>{ds}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Chronic Findings Section */}
      {data.trends && data.trends.chronic && data.trends.chronic.length > 0 && (
        <div class="health-section">
          <div class="section-title">Chronic Findings</div>
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
        <div class="section-title">Health Dimensions</div>
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
      {gsKeys.length > 0 && (
        <div class="health-section">
          <div class="section-title">Global Signals</div>
          <div class="card">
            <table class="global-signals-table">
              <tbody>
                {gsKeys.map((key) => {
                  const v = gs[key];
                  if (v == null) return null;
                  const display =
                    typeof v === "number"
                      ? Number.isInteger(v)
                        ? String(v)
                        : v.toFixed(4)
                      : String(v);
                  return (
                    <tr key={key}>
                      <td class="gs-name">{key.replace(/_/g, " ")}</td>
                      <td class="gs-val">{display}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
