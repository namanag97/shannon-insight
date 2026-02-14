/**
 * HealthScreen v2 - Redesigned with proper information architecture
 *
 * Information Priority:
 * 1. Hero - Health trend chart (is the codebase improving?)
 * 2. Movers + Chronic Issues - What changed? What's persistent?
 * 3. Evolution Charts - Historical trends (4 charts in 2x2 grid)
 * 4. Snapshot History - Table of past snapshots
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
import { fmtDate, fmtDateFull, fmtN } from "../../utils/formatters.js";
import { SIGNAL_LABELS } from "../../utils/constants.js";
import { interpretSignal } from "../../utils/interpretations.js";
import { TrendChart } from "../charts/TrendChart.jsx";
import { RadarChart } from "../charts/RadarChart.jsx";
import { ConcernBar } from "../cards/ConcernCard.jsx";
import { Table } from "../ui/Table.jsx";

export function HealthScreenV2() {
  const data = useStore((s) => s.data);
  if (!data) return null;

  const concerns = data.concerns || [];
  const gs = data.global_signals || {};

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

  // Calculate trend direction
  const trendDirection = hasTrends && trendValues.length >= 2
    ? trendValues[trendValues.length - 1] - trendValues[trendValues.length - 2]
    : 0;

  const currentHealth = hasTrends ? trendValues[trendValues.length - 1] : data.health;
  const healthColor = hColor(currentHealth);

  return (
    <div className="stack stack--2xl">
      {/* ══════════════════════════════════════════════════════════
          PRIORITY 1: HEALTH TREND CHART
          Answer: "Is my codebase improving or degrading?"
          ══════════════════════════════════════════════════════════ */}
      <section>
        <div className="grid">
          <div className="span-12">
            <div className="ds-card">
              <div className="ds-card__header">
                <div className="ds-card__title">Health Score Over Time</div>
              </div>
              <div className="ds-card__body">
                {hasTrends ? (
                  <div className="stack stack--md">
                    {/* Trend summary */}
                    <div className="grid grid--compact">
                      <div className="span-4">
                        <div className="text-center">
                          <div className="text-2xl text-mono" style={{ color: healthColor }}>
                            {currentHealth.toFixed(1)}
                          </div>
                          <div className="text-label mt-2">Current Health</div>
                        </div>
                      </div>
                      <div className="span-4">
                        <div className="text-center">
                          <div
                            className="text-2xl text-mono"
                            style={{ color: trendDirection > 0 ? 'var(--green)' : trendDirection < 0 ? 'var(--red)' : 'var(--text-tertiary)' }}
                          >
                            {trendDirection > 0 ? '↑' : trendDirection < 0 ? '↓' : '–'} {Math.abs(trendDirection).toFixed(1)}
                          </div>
                          <div className="text-label mt-2">Since Last Snapshot</div>
                        </div>
                      </div>
                      <div className="span-4">
                        <div className="text-center">
                          <div className="text-2xl text-mono" style={{ color: 'var(--text)' }}>
                            {trendValues.length}
                          </div>
                          <div className="text-label mt-2">Snapshots Tracked</div>
                        </div>
                      </div>
                    </div>

                    {/* Chart */}
                    <div style={{ paddingTop: 'var(--space-4)' }}>
                      <TrendChart
                        values={trendValues}
                        xLabels={trendLabels}
                        width={800}
                        height={280}
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
                    </div>
                  </div>
                ) : (
                  <EmptyStateInline
                    icon={<TrendIcon />}
                    title="No trend data yet"
                    message="Run analysis with --save to track health over time. Each saved snapshot adds a data point."
                  />
                )}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ══════════════════════════════════════════════════════════
          PRIORITY 2: TOP MOVERS + CHRONIC ISSUES
          Answer: "What changed? What's persistently broken?"
          ══════════════════════════════════════════════════════════ */}
      {(data.trends?.movers?.length > 0 || data.trends?.chronic?.length > 0) && (
        <section>
          <div className="grid">
            {/* 2a. Top Movers */}
            <div className="span-6">
              <div className="ds-card">
                <div className="ds-card__header">
                  <div className="ds-card__title">Top Movers</div>
                </div>
                <div className="ds-card__body">
                  {data.trends?.movers?.length > 0 ? (
                    <MoversTable movers={data.trends.movers} />
                  ) : (
                    <EmptyStateCompact message="No changes since last snapshot" />
                  )}
                </div>
              </div>
            </div>

            {/* 2b. Chronic Issues */}
            <div className="span-6">
              <div className="ds-card">
                <div className="ds-card__header">
                  <div className="ds-card__title">Chronic Issues</div>
                </div>
                <div className="ds-card__body">
                  {data.trends?.chronic?.length > 0 ? (
                    <ChronicIssuesList chronic={data.trends.chronic} />
                  ) : (
                    <EmptyStateCompact message="No persistent issues detected" />
                  )}
                </div>
              </div>
            </div>
          </div>
        </section>
      )}

      {/* ══════════════════════════════════════════════════════════
          PRIORITY 3: EVOLUTION CHARTS
          Answer: "How have key metrics changed over time?"
          ══════════════════════════════════════════════════════════ */}
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

      {/* ══════════════════════════════════════════════════════════
          PRIORITY 4: SNAPSHOT HISTORY
          Answer: "What's the full history of snapshots?"
          ══════════════════════════════════════════════════════════ */}
      {hasTrends && (
        <section>
          <div className="grid">
            <div className="span-12">
              <div className="ds-card">
                <div className="ds-card__header">
                  <div className="ds-card__title">Snapshot History</div>
                </div>
                <div className="ds-card__body">
                  <SnapshotHistoryTable snapshots={data.trends.health} timestamps={trendTimestamps} />
                </div>
              </div>
            </div>
          </div>
        </section>
      )}

      {/* ══════════════════════════════════════════════════════════
          SUPPORTING DATA: HEALTH DIMENSIONS + GLOBAL SIGNALS
          Lower priority - useful for power users
          ══════════════════════════════════════════════════════════ */}
      {(concerns.length > 0 || Object.keys(gs).length > 0) && (
        <CollapsibleSection title="Health Dimensions & Global Metrics" defaultOpen={false}>
          <div className="grid">
            {/* Health Dimensions */}
            {concerns.length > 0 && (
              <div className="span-6">
                <div className="ds-card">
                  <div className="ds-card__header">
                    <div className="ds-card__title">Health Breakdown by Dimension</div>
                  </div>
                  <div className="ds-card__body">
                    {concerns.length >= 3 ? (
                      <div style={{ minHeight: '240px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
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
            )}

            {/* Global Signals */}
            {Object.keys(gs).length > 0 && (
              <div className="span-6">
                <div className="ds-card">
                  <div className="ds-card__header">
                    <div className="ds-card__title">Codebase-Wide Metrics</div>
                  </div>
                  <div className="ds-card__body">
                    <GlobalSignalsTable signals={gs} />
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
 * Movers Table - Shows files with biggest risk changes
 */
function MoversTable({ movers }) {
  const MOVERS_COLUMNS = [
    {
      key: "path",
      label: "File",
      align: "left",
      format: (v) => <a href={"#files/" + encodeURIComponent(v)} className="text-mono">{v}</a>,
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

  return (
    <Table
      columns={MOVERS_COLUMNS}
      data={movers}
      rowKey={(row, i) => i}
      stickyHeader={false}
    />
  );
}

/**
 * Chronic Issues List - Shows persistent findings across snapshots
 */
function ChronicIssuesList({ chronic }) {
  return (
    <div className="stack stack--sm">
      {chronic.map((c, i) => (
        <div
          key={i}
          className="cluster cluster--sm"
          style={{
            padding: 'var(--space-3)',
            background: 'rgba(255,255,255,0.02)',
            borderRadius: 'var(--radius-sm)',
            borderLeft: `3px solid ${c.severity >= 0.8 ? 'var(--red)' : c.severity >= 0.6 ? 'var(--orange)' : 'var(--yellow)'}`
          }}
        >
          <div className="text-body" style={{ flex: 1, fontWeight: 500 }}>
            {c.title || c.finding_type}
          </div>
          <div className="text-body-sm text-mono" style={{ color: 'var(--text-tertiary)' }}>
            {c.count || "?"} snapshots
          </div>
          {c.severity != null && (
            <div
              className="text-body-sm text-mono"
              style={{
                color: c.severity >= 0.8 ? "var(--red)" : c.severity >= 0.6 ? "var(--orange)" : "var(--yellow)",
                fontWeight: 600
              }}
            >
              {c.severity.toFixed(2)}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

/**
 * Evolution Charts Grid - 2x2 grid of small trend charts
 */
function EvolutionChartsGrid({ evolution }) {
  const charts = [
    { key: 'file_count', label: 'Files', color: 'var(--blue)', format: (v) => Math.round(v).toString() },
    { key: 'total_loc', label: 'Lines of Code', color: 'var(--green)', format: (v) => (v / 1000).toFixed(1) + 'k' },
    { key: 'avg_complexity', label: 'Avg Complexity', color: 'var(--orange)', format: (v) => v.toFixed(1) },
    { key: 'avg_risk', label: 'Avg Risk', color: 'var(--red)', format: (v) => v.toFixed(3) },
  ];

  return (
    <div className="grid grid--compact">
      {charts.map(({ key, label, color, format }) => {
        const data = evolution[key];
        if (!data || data.length < 2) return null;

        return (
          <div key={key} className="span-6">
            <div className="stack stack--sm">
              <div className="text-label text-center" style={{ color: 'var(--text-secondary)' }}>
                {label}
              </div>
              <TrendChart
                values={data.map((d) => d.value)}
                xLabels={data.map((d) => new Date(d.timestamp).toLocaleDateString(undefined, { month: 'short', day: 'numeric' }))}
                color={color}
                yFormat={format}
                tooltipFormat={format}
                width={360}
                height={160}
                showDots={true}
                showGrid={true}
                showFill={true}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
}

/**
 * Snapshot History Table - Shows all snapshots with key metrics
 */
function SnapshotHistoryTable({ snapshots, timestamps }) {
  const tableData = snapshots.map((h, i) => {
    const healthValue = typeof h === "object" ? h.health : h;
    const timestamp = timestamps[i];
    return {
      date: timestamp ? fmtDateFull(timestamp) : `Snapshot ${i + 1}`,
      health: (healthValue * 9 + 1).toFixed(1),
      healthColor: hColor(healthValue * 9 + 1),
    };
  }).reverse(); // Most recent first

  const SNAPSHOT_COLUMNS = [
    {
      key: "date",
      label: "Date",
      align: "left",
      cellClass: () => "text-body-sm",
    },
    {
      key: "health",
      label: "Health Score",
      align: "right",
      format: (v, row) => (
        <span className="text-mono" style={{ color: row.healthColor, fontWeight: 600 }}>
          {v}
        </span>
      ),
      cellClass: () => "td-num",
    },
  ];

  return (
    <Table
      columns={SNAPSHOT_COLUMNS}
      data={tableData}
      rowKey={(row, i) => i}
      stickyHeader={false}
    />
  );
}

/**
 * Global Signals Table - Shows codebase-wide metrics
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
      cellClass: () => "gs-val text-mono",
    },
    {
      key: "interp",
      label: "",
      align: "left",
      cellClass: () => "gs-interp text-body-sm",
      cellStyle: () => ({ color: 'var(--text-tertiary)' }),
    },
  ];

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
 * Collapsible Section - For low-priority content
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
          transition: 'background var(--transition-base)'
        }}
        onClick={() => setIsOpen(!isOpen)}
        onMouseEnter={(e) => e.currentTarget.style.background = 'var(--surface-elevated)'}
        onMouseLeave={(e) => e.currentTarget.style.background = 'var(--surface)'}
      >
        <span>{title}</span>
        <span style={{ color: 'var(--text-tertiary)', fontFamily: 'var(--font-mono)', fontSize: '14px' }}>
          {isOpen ? '−' : '+'}
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

/**
 * Empty State - Inline with icon
 */
function EmptyStateInline({ icon, title, message }) {
  return (
    <div style={{ display: 'flex', alignItems: 'flex-start', gap: 'var(--space-4)', padding: 'var(--space-6)' }}>
      <div style={{ flexShrink: 0 }}>
        {icon}
      </div>
      <div className="stack stack--xs">
        <div className="text-body" style={{ fontWeight: 500 }}>
          {title}
        </div>
        <div className="text-body-sm" style={{ color: 'var(--text-tertiary)' }}>
          {message}
        </div>
      </div>
    </div>
  );
}

/**
 * Empty State - Compact for cards
 */
function EmptyStateCompact({ message }) {
  return (
    <div className="text-body-sm" style={{ color: 'var(--text-tertiary)', padding: 'var(--space-4)', textAlign: 'center' }}>
      {message}
    </div>
  );
}

/**
 * Trend Icon - SVG for empty state
 */
function TrendIcon() {
  return (
    <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
      <path d="M4 24L11 17L17 21L28 8" stroke="var(--text-tertiary)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
      <circle cx="11" cy="17" r="2" fill="var(--border)" />
      <circle cx="17" cy="21" r="2" fill="var(--border)" />
      <circle cx="28" cy="8" r="2" fill="var(--border)" />
    </svg>
  );
}
