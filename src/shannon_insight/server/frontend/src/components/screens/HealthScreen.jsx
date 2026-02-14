/**
 * Health screen - trend chart, top movers, chronic findings,
 * radar/bar concern chart, and global signals table.
 */

import useStore from "../../state/store.js";
import { hColor } from "../../utils/helpers.js";
import { Sparkline } from "../charts/Sparkline.jsx";
import { RadarChart } from "../charts/RadarChart.jsx";
import { ConcernBar } from "../cards/ConcernCard.jsx";

export function HealthScreen() {
  const data = useStore((s) => s.data);
  if (!data) return null;

  const concerns = data.concerns || [];
  const gs = data.global_signals || {};
  const gsKeys = Object.keys(gs).sort();

  return (
    <div>
      {/* Trend chart */}
      {data.trends && data.trends.health && (
        <div class="health-section">
          <div class="section-title">Health Trend</div>
          <Sparkline
            values={data.trends.health.map((h) => (typeof h === "object" ? h.health : h))}
            width={600}
            height={200}
            color="var(--accent)"
          />
        </div>
      )}

      {/* Top movers */}
      {data.trends && data.trends.movers && (
        <div class="health-section">
          <div class="section-title">Top Movers</div>
          {data.trends.movers.map((m, i) => {
            const dc = m.delta > 0 ? "var(--red)" : "var(--green)";
            const ds = m.delta > 0 ? "+" + m.delta.toFixed(3) : m.delta.toFixed(3);
            return (
              <div class="mover-item" key={i}>
                <a href={"#files/" + encodeURIComponent(m.path)}>{m.path}</a>{" "}
                <span style={{ color: dc }}>{ds}</span>
              </div>
            );
          })}
        </div>
      )}

      {/* Chronic findings */}
      {data.trends && data.trends.chronic && data.trends.chronic.length > 0 && (
        <div class="health-section">
          <div class="section-title">Chronic Findings</div>
          {data.trends.chronic.map((c, i) => (
            <div class="chronic-item" key={i}>
              {c.title || c.finding_type}{" "}
              <span class="chronic-snapshots">({c.count || "?"} snapshots)</span>
            </div>
          ))}
        </div>
      )}

      {/* Concern chart */}
      <div class="card">
        <div class="card-title">Health Dimensions</div>
        {concerns.length >= 3 ? (
          <RadarChart items={concerns} />
        ) : (
          <div>
            {concerns.map((c, i) => (
              <ConcernBar key={i} concern={c} />
            ))}
          </div>
        )}
      </div>

      {/* Global signals */}
      <div class="card">
        <div class="card-title">Global Signals</div>
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
  );
}
