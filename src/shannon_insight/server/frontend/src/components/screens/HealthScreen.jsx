/**
 * HealthScreen - Redesigned with proper information architecture
 *
 * Information Priority:
 * 1. Health Trend - Large prominent chart (is it getting better or worse?)
 * 2. Top Movers + Chronic Issues - What changed? What's stuck?
 * 3. Health Dimensions - Radar/bar breakdown by dimension
 * 4. Evolution Charts - Detailed metric trends (2x2 grid)
 * 5. Codebase-Wide Metrics - Supporting data (collapsible)
 *
 * Design System:
 * - 12-column grid with proper gutters
 * - Mathematical spacing (8px baseline)
 * - Clear visual hierarchy
 * - Every component intentionally placed
 */

import React from "preact/compat";
import useStore from "../../state/store.js";
import { hColor } from "../../utils/helpers.js";
import { fmtDate, fmtDateFull } from "../../utils/formatters.js";
import { SIGNAL_LABELS } from "../../utils/constants.js";
import { interpretSignal } from "../../utils/interpretations.js";
import { TrendChart } from "../charts/TrendChart.jsx";
import { RadarChart } from "../charts/RadarChart.jsx";
import { ConcernBar } from "../cards/ConcernCard.jsx";
import { Table } from "../ui/Table.jsx";


export function HealthScreen() {
  const data = useStore((s) => s.data);

  if (!data) return null;

  // ── Extract health trend data ────────────────────────────────────
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

  // Current, previous, and delta for the summary strip
  const currentHealth = trendValues.length > 0
    ? trendValues[trendValues.length - 1]
    : null;
  const previousHealth = trendValues.length > 1
    ? trendValues[trendValues.length - 2]
    : null;
  const healthDelta = currentHealth != null && previousHealth != null
    ? currentHealth - previousHealth
    : null;

  // ── Health dimensions (concern breakdown) ────────────────────────
  const concerns = data.concerns || [];

  // ── Global signals ──────────────────────────────────────────────
  const gs = data.global_signals || {};

  return (
    <div className="stack stack--2xl">
      {/* ================================================================
          PRIORITY 1: HEALTH TREND (Large, Prominent)
          Answer: "Is my codebase getting better or worse?"
          ================================================================ */}
      <section>
        <div className="grid">
          <div className="span-12">
            <div className="ds-card ds-card--spacious">
              <div className="ds-card__header">
                <div className="ds-card__title">Health Score Over Time</div>
              </div>
              <div className="ds-card__body">
                {hasTrends ? (
                  <div className="stack stack--lg">
                    {/* Large trend chart */}
                    <TrendChart
                      values={trendValues}
                      xLabels={trendLabels}
                      width={1200}
                      height={300}
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

                    {/* Summary stats below chart */}
                    {currentHealth != null && (
                      <div className="cluster cluster--lg" style={{ justifyContent: 'center' }}>
                        <div style={{ textAlign: 'center' }}>
                          <div className="text-label">CURRENT</div>
                          <div
                            className="text-mono"
                            style={{
                              fontSize: 'var(--text-2xl)',
                              fontWeight: 'var(--font-semibold)',
                              color: hColor(currentHealth),
                              marginTop: 'var(--space-1)',
                            }}
                          >
                            {currentHealth.toFixed(1)}
                          </div>
                        </div>

                        {previousHealth != null && (
                          <>
                            <div style={{ color: 'var(--border)', fontSize: 'var(--text-2xl)' }}>|</div>
                            <div style={{ textAlign: 'center' }}>
                              <div className="text-label">PREVIOUS</div>
                              <div
                                className="text-mono"
                                style={{
                                  fontSize: 'var(--text-xl)',
                                  fontWeight: 'var(--font-medium)',
                                  color: 'var(--text-secondary)',
                                  marginTop: 'var(--space-1)',
                                }}
                              >
                                {previousHealth.toFixed(1)}
                              </div>
                            </div>
                          </>
                        )}

                        {healthDelta != null && (
                          <>
                            <div style={{ color: 'var(--border)', fontSize: 'var(--text-2xl)' }}>|</div>
                            <div style={{ textAlign: 'center' }}>
                              <div className="text-label">CHANGE</div>
                              <div
                                className="text-mono"
                                style={{
                                  fontSize: 'var(--text-xl)',
                                  fontWeight: 'var(--font-medium)',
                                  color: healthDelta > 0
                                    ? 'var(--green)'
                                    : healthDelta < 0
                                      ? 'var(--red)'
                                      : 'var(--text-tertiary)',
                                  marginTop: 'var(--space-1)',
                                }}
                              >
                                {healthDelta > 0 ? '\u2191' : healthDelta < 0 ? '\u2193' : '='}{' '}
                                {Math.abs(healthDelta).toFixed(1)}
                              </div>
                            </div>
                          </>
                        )}
                      </div>
                    )}

                    <div className="text-label" style={{ textAlign: 'center' }}>
                      {trendValues.length} snapshot{trendValues.length !== 1 ? 's' : ''} tracked
                    </div>
                  </div>
                ) : (
                  <EmptyTrendState />
                )}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ================================================================
          PRIORITY 2: TOP MOVERS + CHRONIC ISSUES (2-column)
          Answer: "What changed? What's stuck?"
          ================================================================ */}
      {(hasMovers(data) || hasChronic(data)) && (
        <section>
          <div className="grid">
            {/* Top Movers */}
            <div className="span-6">
              <div className="ds-card">
                <div className="ds-card__header">
                  <div className="ds-card__title">Biggest Risk Changes</div>
                </div>
                <div className="ds-card__body">
                  {hasMovers(data) ? (
                    <Table
                      columns={MOVERS_COLUMNS}
                      data={data.trends.movers}
                      rowKey={(row, i) => i}
                      stickyHeader={false}
                    />
                  ) : (
                    <div className="text-body-sm" style={{ color: 'var(--text-tertiary)', padding: 'var(--space-4)', textAlign: 'center' }}>
                      No significant risk changes detected
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Chronic Issues */}
            <div className="span-6">
              <div className="ds-card">
                <div className="ds-card__header">
                  <div className="ds-card__title">Persistent Issues</div>
                </div>
                <div className="ds-card__body">
                  {hasChronic(data) ? (
                    <div className="stack stack--sm">
                      {data.trends.chronic.map((c, i) => (
                        <ChronicRow key={i} item={c} />
                      ))}
                    </div>
                  ) : (
                    <div className="text-body-sm" style={{ color: 'var(--text-tertiary)', padding: 'var(--space-4)', textAlign: 'center' }}>
                      No chronic issues detected
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </section>
      )}

      {/* ================================================================
          PRIORITY 3: HEALTH DIMENSIONS (Radar / Bar Chart)
          Answer: "Which dimensions are healthy vs struggling?"
          ================================================================ */}
      {concerns.length > 0 && (
        <section>
          <div className="grid">
            <div className="span-12">
              <div className="ds-card">
                <div className="ds-card__header">
                  <div className="ds-card__title">Health Breakdown by Dimension</div>
                </div>
                <div className="ds-card__body">
                  {concerns.length >= 3 ? (
                    <div style={{ display: 'flex', justifyContent: 'center' }}>
                      <RadarChart items={concerns} />
                    </div>
                  ) : (
                    <div className="stack stack--sm">
                      {concerns.map((c, i) => (
                        <ConcernBar key={i} concern={c} />
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </section>
      )}

      {/* ================================================================
          PRIORITY 4: EVOLUTION CHARTS (2x2 grid)
          Answer: "How are key metrics trending?"
          ================================================================ */}
      {data.evolution && (
        <section>
          <div className="grid">
            <div className="span-12">
              <div className="ds-card">
                <div className="ds-card__header">
                  <div className="ds-card__title">Codebase Evolution</div>
                </div>
                <div className="ds-card__body">
                  <EvolutionChartsGrid evolution={data.evolution} />
                </div>
              </div>
            </div>
          </div>
        </section>
      )}

      {/* ================================================================
          PRIORITY 5: SNAPSHOT HISTORY + GLOBAL SIGNALS (Collapsible)
          Supporting data for power users
          ================================================================ */}
      {(hasTrends || Object.keys(gs).length > 0) && (
        <CollapsibleSection title="Snapshot History & Global Metrics" defaultOpen={false}>
          <div className="stack stack--lg">
            {/* Snapshot History Table */}
            {hasTrends && (
              <div className="grid">
                <div className="span-12">
                  <div className="ds-card">
                    <div className="ds-card__header">
                      <div className="ds-card__title">
                        Snapshot History ({trendValues.length})
                      </div>
                    </div>
                    <div className="ds-card__body">
                      <SnapshotHistoryTable
                        snapshots={data.trends.health}
                        timestamps={trendTimestamps}
                      />
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Global Signals Table */}
            {Object.keys(gs).length > 0 && (
              <div className="grid">
                <div className="span-12">
                  <div className="ds-card">
                    <div className="ds-card__header">
                      <div className="ds-card__title">Codebase-Wide Metrics</div>
                    </div>
                    <div className="ds-card__body">
                      <GlobalSignalsTable signals={gs} />
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </CollapsibleSection>
      )}
    </div>
  );
}


/* ═══════════════════════════════════════════════════════════════════════════
   SUB-COMPONENTS
   ═══════════════════════════════════════════════════════════════════════════ */

/**
 * Empty state shown when no trend data is available.
 * Encourages user to run analysis with --save flag.
 */
function EmptyTrendState() {
  return (
    <div style={{ padding: 'var(--space-12)', textAlign: 'center' }}>
      <div style={{ marginBottom: 'var(--space-4)' }}>
        <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
          <path
            d="M4 24L11 17L17 21L28 8"
            stroke="var(--text-tertiary)"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          />
          <circle cx="11" cy="17" r="2" fill="var(--border)" />
          <circle cx="17" cy="21" r="2" fill="var(--border)" />
          <circle cx="28" cy="8" r="2" fill="var(--border)" />
        </svg>
      </div>
      <div className="text-body" style={{ color: 'var(--text-secondary)', fontWeight: 'var(--font-medium)' }}>
        No trend data yet
      </div>
      <div className="text-body-sm" style={{ color: 'var(--text-tertiary)', marginTop: 'var(--space-2)' }}>
        Run analysis with <code>--save</code> to track health over time.
        Each saved snapshot adds a data point.
      </div>
    </div>
  );
}

/**
 * Chronic Row - Displays a persistent finding that recurs across snapshots.
 * Shows finding type, snapshot count, and severity indicator.
 */
function ChronicRow({ item }) {
  const sevColor =
    item.severity != null
      ? item.severity >= 0.8
        ? 'var(--red)'
        : item.severity >= 0.6
          ? 'var(--orange)'
          : 'var(--yellow)'
      : 'var(--text-tertiary)';

  return (
    <div
      style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: 'var(--space-3)',
        background: 'rgba(255,255,255,0.02)',
        borderRadius: 'var(--radius-sm)',
        borderLeft: `3px solid ${sevColor}`,
      }}
    >
      <div className="stack stack--xs" style={{ flex: 1 }}>
        <div className="text-body-sm" style={{ color: 'var(--text)', fontWeight: 'var(--font-medium)' }}>
          {item.title || item.finding_type}
        </div>
        <div className="text-label">
          {item.count || '?'} snapshots - Never resolved
        </div>
      </div>
      {item.severity != null && (
        <div
          className="text-body-sm text-mono"
          style={{ color: sevColor, fontWeight: 'var(--font-semibold)' }}
        >
          {item.severity.toFixed(2)}
        </div>
      )}
    </div>
  );
}

/**
 * Evolution Charts Grid - 2x2 grid of trend charts showing
 * file count, LOC, complexity, and risk over time.
 */
function EvolutionChartsGrid({ evolution }) {
  const charts = [
    { key: 'file_count', label: 'Files', color: 'var(--blue)', format: (v) => Math.round(v).toString() },
    { key: 'total_loc', label: 'Lines of Code', color: 'var(--green)', format: (v) => (v / 1000).toFixed(1) + 'k' },
    { key: 'avg_complexity', label: 'Avg Complexity', color: 'var(--orange)', format: (v) => v.toFixed(1) },
    { key: 'avg_risk', label: 'Avg Risk', color: 'var(--red)', format: (v) => v.toFixed(3) },
  ];

  const renderable = charts.filter(({ key }) => {
    const d = evolution[key];
    return d && d.length >= 2;
  });

  if (renderable.length === 0) {
    return (
      <div className="text-body-sm" style={{ color: 'var(--text-tertiary)', padding: 'var(--space-8)', textAlign: 'center' }}>
        Not enough data points for evolution charts (need at least 2 snapshots)
      </div>
    );
  }

  return (
    <div className="grid grid--compact">
      {renderable.map(({ key, label, color, format }) => {
        const chartData = evolution[key];
        return (
          <div key={key} className="span-6">
            <div className="stack stack--xs" style={{ padding: 'var(--space-2)' }}>
              <TrendChart
                values={chartData.map((d) => d.value)}
                xLabels={chartData.map((d) =>
                  new Date(d.timestamp).toLocaleDateString(undefined, {
                    month: 'short',
                    day: 'numeric',
                  })
                )}
                color={color}
                yFormat={format}
                tooltipFormat={format}
                width={500}
                height={180}
                showDots={true}
                showGrid={true}
                showFill={true}
              />
              <div className="text-label" style={{ textAlign: 'center' }}>{label}</div>
            </div>
          </div>
        );
      })}
    </div>
  );
}

/**
 * Snapshot History Table - Lists all snapshots with health scores,
 * sorted most-recent-first.
 */
function SnapshotHistoryTable({ snapshots, timestamps }) {
  const tableData = snapshots.map((h, i) => {
    const healthValue = typeof h === "object" ? h.health : h;
    const ts = timestamps[i];
    return {
      date: ts ? fmtDateFull(ts) : `Snapshot ${i + 1}`,
      health: (healthValue * 9 + 1).toFixed(1),
      _healthNum: healthValue * 9 + 1,
    };
  }).reverse(); // Most recent first

  const SNAPSHOT_COLUMNS = [
    {
      key: "date",
      label: "Date",
      align: "left",
    },
    {
      key: "health",
      label: "Health Score",
      align: "right",
      cellClass: () => "td-num",
      cellStyle: (v, row) => ({
        color: hColor(row._healthNum),
        fontWeight: 600,
        fontFamily: 'var(--font-mono)',
      }),
    },
  ];

  return (
    <Table
      columns={SNAPSHOT_COLUMNS}
      data={tableData}
      rowKey={(row, i) => i}
      stickyHeader={false}
      striped={true}
    />
  );
}

/**
 * Global Signals Table - Shows codebase-wide metrics with
 * human-readable labels and interpretations.
 */
function GlobalSignalsTable({ signals }) {
  const gsKeys = Object.keys(signals).sort();
  const gsData = gsKeys
    .map((key) => {
      const v = signals[key];
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

  return (
    <Table
      columns={GS_COLUMNS}
      data={gsData}
      rowKey={(row) => row._key}
      stickyHeader={false}
    />
  );
}

/**
 * Collapsible Section - For low-priority content that can be
 * expanded by interested users.
 */
function CollapsibleSection({ title, children, defaultOpen = false }) {
  const [isOpen, setIsOpen] = React.useState(defaultOpen);

  return (
    <section>
      <div
        className="text-h4"
        style={{
          cursor: 'pointer',
          padding: 'var(--space-4)',
          background: 'var(--surface)',
          borderRadius: 'var(--radius-md)',
          border: '1px solid var(--border)',
          userSelect: 'none',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          transition: 'background var(--transition-base)',
        }}
        onClick={() => setIsOpen(!isOpen)}
        onMouseEnter={(e) => { e.currentTarget.style.background = 'var(--surface-elevated)'; }}
        onMouseLeave={(e) => { e.currentTarget.style.background = 'var(--surface)'; }}
      >
        <span>{title}</span>
        <span style={{ color: 'var(--text-tertiary)', fontFamily: 'var(--font-mono)', fontSize: '14px' }}>
          {isOpen ? '\u2212' : '+'}
        </span>
      </div>
      {isOpen && (
        <div style={{ marginTop: 'var(--space-6)' }}>
          {children}
        </div>
      )}
    </section>
  );
}


/* ═══════════════════════════════════════════════════════════════════════════
   COLUMN DEFINITIONS
   ═══════════════════════════════════════════════════════════════════════════ */

/**
 * Column definitions for the Top Movers table.
 * Shows file path, old risk, new risk, and delta.
 */
const MOVERS_COLUMNS = [
  {
    key: "path",
    label: "File",
    align: "left",
    format: (v) => (
      <a href={"#files/" + encodeURIComponent(v)} className="text-mono" style={{ color: 'var(--accent)', textDecoration: 'none' }}>
        {v}
      </a>
    ),
    cellClass: () => "td-path",
  },
  {
    key: "old_value",
    label: "Previous",
    align: "right",
    format: (v) => v != null ? v.toFixed(3) : "--",
    cellClass: () => "td-num",
  },
  {
    key: "new_value",
    label: "Current",
    align: "right",
    format: (v) => v != null ? v.toFixed(3) : "--",
    cellClass: () => "td-num",
  },
  {
    key: "delta",
    label: "Change",
    align: "right",
    format: (v) => (v > 0 ? "+" : "") + v.toFixed(3),
    cellClass: () => "td-num",
    cellStyle: (v) => ({
      color: v > 0 ? "var(--red)" : "var(--green)",
      fontWeight: 600,
    }),
  },
];

/**
 * Column definitions for the Global Signals table.
 */
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


/* ═══════════════════════════════════════════════════════════════════════════
   HELPERS
   ═══════════════════════════════════════════════════════════════════════════ */

/** Check if data has movers data */
function hasMovers(data) {
  return data.trends && data.trends.movers && data.trends.movers.length > 0;
}

/** Check if data has chronic findings */
function hasChronic(data) {
  return data.trends && data.trends.chronic && data.trends.chronic.length > 0;
}
