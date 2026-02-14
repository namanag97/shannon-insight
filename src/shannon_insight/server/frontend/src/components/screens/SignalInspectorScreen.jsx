/**
 * Signal Inspector screen - deep dive into any signal across all files.
 * Shows distribution, statistics, and per-file breakdown with inline bars.
 */

import useStore from "../../state/store.js";
import { fmtF, fmtSigVal } from "../../utils/formatters.js";
import { polarColor } from "../../utils/helpers.js";
import { SIGNAL_LABELS, SIGNAL_CATEGORIES, SIGNAL_DESCRIPTIONS } from "../../utils/constants.js";
import { interpretSignal } from "../../utils/interpretations.js";

// Collect all inspectable signals (numeric ones that appear in file signals)
function getInspectableSignals() {
  const signals = [];
  for (const cat of SIGNAL_CATEGORIES) {
    for (const sig of cat.signals) {
      signals.push({ key: sig, label: SIGNAL_LABELS[sig] || sig, category: cat.name });
    }
  }
  return signals;
}

function computeStats(values) {
  if (!values.length) return { min: 0, max: 0, mean: 0, median: 0, p90: 0 };
  const sorted = [...values].sort((a, b) => a - b);
  const sum = sorted.reduce((s, v) => s + v, 0);
  const mean = sum / sorted.length;
  const median = sorted.length % 2 === 0
    ? (sorted[sorted.length / 2 - 1] + sorted[sorted.length / 2]) / 2
    : sorted[Math.floor(sorted.length / 2)];
  const p90Idx = Math.min(Math.floor(sorted.length * 0.9), sorted.length - 1);
  return {
    min: sorted[0],
    max: sorted[sorted.length - 1],
    mean,
    median,
    p90: sorted[p90Idx],
  };
}

export function SignalInspectorScreen() {
  const data = useStore((s) => s.data);
  const inspectedSignal = useStore((s) => s.inspectedSignal);
  const setInspectedSignal = useStore((s) => s.setInspectedSignal);

  if (!data || !data.files) {
    return (
      <div class="empty-state">
        <div class="empty-state-title">No file data available</div>
        <div class="empty-state-hint">
          Run analysis to inspect signal distributions.
        </div>
      </div>
    );
  }

  const inspectable = getInspectableSignals();

  // Extract values for the selected signal
  const entries = [];
  for (const path in data.files) {
    const f = data.files[path];
    const sigs = f.signals || {};
    let val = sigs[inspectedSignal];
    // Also check top-level file data
    if (val == null) val = f[inspectedSignal];
    if (val != null && typeof val === "number") {
      entries.push({ path, value: val });
    } else if (val != null && typeof val === "boolean") {
      entries.push({ path, value: val ? 1 : 0 });
    }
  }

  // Sort by value descending
  entries.sort((a, b) => b.value - a.value);

  const values = entries.map((e) => e.value);
  const stats = computeStats(values);
  const maxVal = stats.max || 1;

  const label = SIGNAL_LABELS[inspectedSignal] || inspectedSignal;
  const description = SIGNAL_DESCRIPTIONS[inspectedSignal] || "";

  // Build histogram (10 bins)
  const bins = new Array(10).fill(0);
  if (values.length > 0 && maxVal > 0) {
    for (const v of values) {
      const bin = Math.min(Math.floor((v / maxVal) * 10), 9);
      bins[bin]++;
    }
  }
  const maxBin = Math.max(...bins) || 1;

  const displayed = entries.slice(0, 100);

  return (
    <div class="signal-inspector">
      <div class="section-title">Signal Inspector</div>

      {/* Signal selector */}
      <div class="signal-selector">
        <select
          class="signal-select"
          value={inspectedSignal}
          onChange={(e) => setInspectedSignal(e.target.value)}
        >
          {SIGNAL_CATEGORIES.map((cat) => (
            <optgroup key={cat.key} label={cat.name}>
              {cat.signals.map((sig) => (
                <option key={sig} value={sig}>
                  {SIGNAL_LABELS[sig] || sig}
                </option>
              ))}
            </optgroup>
          ))}
        </select>
        {description && (
          <span style={{ fontSize: "12px", color: "var(--text-secondary)" }}>
            {description}
          </span>
        )}
      </div>

      {entries.length === 0 ? (
        <div class="empty-state">
          <div class="empty-state-title">No data for this signal</div>
          <div class="empty-state-hint">
            This signal may not be available in the current analysis.
          </div>
        </div>
      ) : (
        <>
          {/* Statistics summary */}
          <div class="signal-summary-strip">
            <div class="signal-summary-item">
              <div class="signal-summary-val">{entries.length}</div>
              <div class="signal-summary-label">Files</div>
            </div>
            <div class="signal-summary-item">
              <div class="signal-summary-val">{fmtF(stats.min, 3)}</div>
              <div class="signal-summary-label">Min</div>
            </div>
            <div class="signal-summary-item">
              <div class="signal-summary-val">{fmtF(stats.median, 3)}</div>
              <div class="signal-summary-label">Median</div>
            </div>
            <div class="signal-summary-item">
              <div class="signal-summary-val">{fmtF(stats.mean, 3)}</div>
              <div class="signal-summary-label">Mean</div>
            </div>
            <div class="signal-summary-item">
              <div class="signal-summary-val">{fmtF(stats.max, 3)}</div>
              <div class="signal-summary-label">Max</div>
            </div>
          </div>

          {/* Distribution histogram */}
          <div class="signal-distribution">
            <div class="card-title">Distribution</div>
            <svg width="100%" height="80" viewBox="0 0 400 80" preserveAspectRatio="none">
              {bins.map((count, i) => {
                const bw = 36;
                const bx = i * 40 + 2;
                const bh = (count / maxBin) * 60;
                const by = 70 - bh;
                return (
                  <g key={i}>
                    <rect
                      x={bx} y={by} width={bw} height={bh}
                      fill="var(--accent)" opacity="0.5" rx="2"
                    />
                    <text
                      x={bx + bw / 2} y={78}
                      fill="var(--text-tertiary)" font-size="7" font-family="var(--mono)"
                      text-anchor="middle"
                    >
                      {count}
                    </text>
                  </g>
                );
              })}
            </svg>
            <div style={{
              display: "flex", justifyContent: "space-between",
              fontSize: "9px", fontFamily: "var(--mono)", color: "var(--text-tertiary)",
              marginTop: "2px"
            }}>
              <span>{fmtF(0, 2)}</span>
              <span>{fmtF(maxVal, 3)}</span>
            </div>
          </div>

          {/* Per-file breakdown */}
          <div class="signal-distribution">
            <div class="card-title">
              Top Files by {label} ({displayed.length} of {entries.length})
            </div>
            <div class="signal-file-list">
              {displayed.map((entry) => {
                const pct = maxVal > 0 ? (entry.value / maxVal) * 100 : 0;
                const color = polarColor(inspectedSignal, entry.value);
                const display = fmtSigVal(inspectedSignal, entry.value);
                const interp = interpretSignal(inspectedSignal, entry.value);

                return (
                  <div
                    key={entry.path}
                    class="signal-file-item"
                    onClick={() => { location.hash = "files/" + encodeURIComponent(entry.path); }}
                  >
                    <span class="signal-file-item-path">{entry.path}</span>
                    <span class="signal-file-item-val" style={{ color }}>{display}</span>
                    <div class="signal-file-item-bar">
                      <div
                        class="signal-file-item-bar-fill"
                        style={{ width: pct + "%", background: color }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
