/**
 * ModulesScreen v2 - Redesigned with proper information architecture
 *
 * Information Priority:
 * 1. Module Health Summary - avg health, best/worst, architectural metrics
 * 2. Top 5 Modules Needing Attention - compact list with key metrics
 * 3. All Modules Table - sortable, full data
 *
 * Design System:
 * - 12-column grid with proper gutters
 * - Mathematical spacing (8px baseline)
 * - Clear visual hierarchy
 * - Every component intentionally placed
 */

import { useState } from "preact/hooks";
import useStore from "../../state/store.js";
import { fmtF, fmtN, fmtSigVal } from "../../utils/formatters.js";
import { hColor, polarColor } from "../../utils/helpers.js";
import { Table } from "../ui/Table.jsx";
import {
  MODULE_SIGNAL_LABELS,
  MODULE_SIGNAL_DESCRIPTIONS,
  MODULE_SIGNAL_CATEGORIES,
} from "../../utils/constants.js";
import { interpretSignal } from "../../utils/interpretations.js";
import { Sparkline } from "../charts/Sparkline.jsx";

const MODULE_COLUMNS = [
  {
    key: "path",
    label: "Module",
    align: "left",
    format: (v) => <span class="td-path"><span>{v}</span></span>,
    cellClass: () => "td-path",
  },
  {
    key: "health_score",
    label: "Health Score",
    align: "right",
    format: (v, row) => fmtF(v, 1),
    cellClass: () => "td-risk",
    cellStyle: (v, row) => ({ color: hColor(row.health_score || 5) }),
  },
  {
    key: "instability",
    label: "Change Sensitivity",
    align: "right",
    format: (v) => fmtF(v, 2),
    cellClass: () => "td-num",
  },
  {
    key: "abstractness",
    label: "Abstraction Level",
    align: "right",
    format: (v) => fmtF(v, 2),
    cellClass: () => "td-num",
  },
  {
    key: "file_count",
    label: "File Count",
    align: "right",
    format: (v) => v || 0,
    cellClass: () => "td-num",
  },
  {
    key: "velocity",
    label: "Change Velocity",
    align: "right",
    format: (v) => fmtF(v, 1),
    cellClass: () => "td-num",
  },
];

function ModuleListViewV2() {
  const data = useStore((s) => s.data);
  const moduleSortKey = useStore((s) => s.moduleSortKey);
  const moduleSortAsc = useStore((s) => s.moduleSortAsc);
  const setModuleSortKey = useStore((s) => s.setModuleSortKey);

  if (!data || !data.modules) {
    return (
      <div class="empty-state">
        <div class="empty-state-title">No module data</div>
      </div>
    );
  }

  // Convert modules to array
  const entries = [];
  for (const p in data.modules) {
    entries.push({ path: p, ...data.modules[p] });
  }

  // Sort modules
  entries.sort((a, b) => {
    if (moduleSortKey === "path") {
      return moduleSortAsc ? a.path.localeCompare(b.path) : b.path.localeCompare(a.path);
    }
    const va = a[moduleSortKey] != null ? a[moduleSortKey] : 0;
    const vb = b[moduleSortKey] != null ? b[moduleSortKey] : 0;
    return moduleSortAsc ? va - vb : vb - va;
  });

  // Calculate summary metrics
  const validHealthScores = entries.filter(m => m.health_score != null).map(m => m.health_score);
  const avgHealth = validHealthScores.length > 0
    ? validHealthScores.reduce((sum, h) => sum + h, 0) / validHealthScores.length
    : null;

  const bestModule = validHealthScores.length > 0
    ? entries.reduce((best, m) => m.health_score > (best?.health_score || 0) ? m : best, entries[0])
    : null;

  const worstModule = validHealthScores.length > 0
    ? entries.reduce((worst, m) => m.health_score < (worst?.health_score || 10) ? m : worst, entries[0])
    : null;

  // Calculate architectural metrics
  const validInstabilities = entries.filter(m => m.instability != null).map(m => m.instability);
  const avgCoupling = validInstabilities.length > 0
    ? validInstabilities.reduce((sum, i) => sum + i, 0) / validInstabilities.length
    : null;

  const validAbstractness = entries.filter(m => m.abstractness != null).map(m => m.abstractness);
  const avgCohesion = validAbstractness.length > 0
    ? validAbstractness.reduce((sum, a) => sum + a, 0) / validAbstractness.length
    : null;

  const totalViolations = entries.reduce((sum, m) => sum + (m.violations?.length || 0), 0);

  // Get top 5 worst modules
  const problemModules = entries
    .filter(m => m.health_score != null)
    .sort((a, b) => a.health_score - b.health_score)
    .slice(0, 5);

  function handleRowClick(row) {
    location.hash = "modules/" + encodeURIComponent(row.path);
  }

  return (
    <div className="stack stack--2xl">
      {/* ══════════════════════════════════════════════════════════
          PRIORITY 1: MODULE HEALTH SUMMARY
          Answer: "How healthy are my modules overall?"
          ══════════════════════════════════════════════════════════ */}
      <section>
        <div className="grid">
          {/* Module Health */}
          <div className="span-6">
            <div className="ds-card">
              <div className="ds-card__header">
                <div className="ds-card__title">Module Health</div>
              </div>
              <div className="ds-card__body">
                <div className="stack stack--md">
                  {/* Average Health */}
                  <div className="text-center">
                    <div className="text-display text-mono" style={{ color: hColor(avgHealth || 5) }}>
                      {avgHealth != null ? avgHealth.toFixed(1) : '—'}
                    </div>
                    <div className="text-label" style={{ marginTop: 'var(--space-2)' }}>
                      AVERAGE HEALTH
                    </div>
                  </div>

                  {/* Best/Worst */}
                  <div className="grid grid--compact" style={{ marginTop: 'var(--space-6)' }}>
                    <div className="span-6">
                      <div className="text-center" style={{ padding: 'var(--space-3)' }}>
                        <div className="text-label" style={{ marginBottom: 'var(--space-2)', color: 'var(--green)' }}>
                          BEST
                        </div>
                        {bestModule ? (
                          <>
                            <div className="text-body-sm text-mono" style={{ color: 'var(--text-secondary)', marginBottom: 'var(--space-1)' }}>
                              {bestModule.path}
                            </div>
                            <div className="text-lg text-mono" style={{ color: hColor(bestModule.health_score) }}>
                              {bestModule.health_score.toFixed(1)}
                            </div>
                          </>
                        ) : (
                          <div className="text-body-sm" style={{ color: 'var(--text-tertiary)' }}>—</div>
                        )}
                      </div>
                    </div>

                    <div className="span-6">
                      <div className="text-center" style={{ padding: 'var(--space-3)' }}>
                        <div className="text-label" style={{ marginBottom: 'var(--space-2)', color: 'var(--red)' }}>
                          WORST
                        </div>
                        {worstModule ? (
                          <>
                            <div className="text-body-sm text-mono" style={{ color: 'var(--text-secondary)', marginBottom: 'var(--space-1)' }}>
                              {worstModule.path}
                            </div>
                            <div className="text-lg text-mono" style={{ color: hColor(worstModule.health_score) }}>
                              {worstModule.health_score.toFixed(1)}
                            </div>
                          </>
                        ) : (
                          <div className="text-body-sm" style={{ color: 'var(--text-tertiary)' }}>—</div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Architectural Metrics */}
          <div className="span-6">
            <div className="ds-card">
              <div className="ds-card__header">
                <div className="ds-card__title">Architectural Metrics</div>
              </div>
              <div className="ds-card__body">
                <div className="grid grid--compact">
                  <div className="span-6">
                    <MetricItem
                      value={avgCoupling != null ? avgCoupling.toFixed(2) : '—'}
                      label="Avg Change Sensitivity"
                      color={avgCoupling != null && avgCoupling > 0.7 ? 'var(--orange)' : undefined}
                    />
                  </div>
                  <div className="span-6">
                    <MetricItem
                      value={avgCohesion != null ? avgCohesion.toFixed(2) : '—'}
                      label="Avg Abstraction"
                      color={avgCohesion != null && avgCohesion < 0.3 ? 'var(--orange)' : undefined}
                    />
                  </div>
                  <div className="span-6">
                    <MetricItem
                      value={fmtN(entries.length)}
                      label="Total Modules"
                    />
                  </div>
                  <div className="span-6">
                    <MetricItem
                      value={fmtN(totalViolations)}
                      label="Violations"
                      color={totalViolations > 0 ? 'var(--red)' : undefined}
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ══════════════════════════════════════════════════════════
          PRIORITY 2: TOP 5 MODULES NEEDING ATTENTION
          Answer: "Which modules should I fix first?"
          ══════════════════════════════════════════════════════════ */}
      {problemModules.length > 0 && (
        <section>
          <div className="grid">
            <div className="span-12">
              <div className="ds-card">
                <div className="ds-card__header">
                  <div className="ds-card__title">🎯 Modules Needing Attention</div>
                </div>
                <div className="ds-card__body">
                  <div className="stack stack--sm">
                    {problemModules.map((module) => (
                      <ModuleProblemRow
                        key={module.path}
                        module={module}
                        onClick={() => handleRowClick(module)}
                      />
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>
      )}

      {/* ══════════════════════════════════════════════════════════
          PRIORITY 3: ALL MODULES TABLE
          Answer: "Show me all the data"
          ══════════════════════════════════════════════════════════ */}
      <section>
        <div className="grid">
          <div className="span-12">
            <div className="ds-card">
              <div className="ds-card__header">
                <div className="ds-card__title">All Modules ({entries.length})</div>
              </div>
              <div className="ds-card__body">
                <Table
                  columns={MODULE_COLUMNS}
                  data={entries}
                  rowKey={(row) => row.path}
                  sortable={true}
                  sortKey={moduleSortKey}
                  sortAsc={moduleSortAsc}
                  onSort={setModuleSortKey}
                  onRowClick={handleRowClick}
                />
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

/**
 * Module Problem Row - Compact display for problem modules
 */
function ModuleProblemRow({ module, onClick }) {
  const healthColor = hColor(module.health_score || 5);

  return (
    <div
      className="cluster cluster--md"
      style={{
        padding: 'var(--space-3)',
        borderLeft: `3px solid ${healthColor}`,
        background: 'rgba(255,255,255,0.02)',
        borderRadius: 'var(--radius-sm)',
        cursor: 'pointer',
        transition: 'background var(--transition-base)',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: 'var(--space-4)'
      }}
      onClick={onClick}
      onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(255,255,255,0.04)'}
      onMouseLeave={(e) => e.currentTarget.style.background = 'rgba(255,255,255,0.02)'}
    >
      {/* Module path */}
      <div style={{ flex: '1 1 200px', minWidth: '200px' }}>
        <div className="text-body text-mono" style={{ fontWeight: 500, color: 'var(--text)' }}>
          {module.path}
        </div>
      </div>

      {/* Key metrics */}
      <div className="cluster cluster--sm" style={{ gap: 'var(--space-4)' }}>
        <MetricBadge
          label="Health"
          value={module.health_score.toFixed(1)}
          color={healthColor}
        />
        {module.instability != null && (
          <MetricBadge
            label="Instability"
            value={module.instability.toFixed(2)}
            color={module.instability > 0.7 ? 'var(--orange)' : 'var(--text-secondary)'}
          />
        )}
        {module.file_count != null && (
          <MetricBadge
            label="Files"
            value={module.file_count}
            color="var(--text-secondary)"
          />
        )}
        {module.violations && module.violations.length > 0 && (
          <MetricBadge
            label="Violations"
            value={module.violations.length}
            color="var(--red)"
          />
        )}
      </div>
    </div>
  );
}

/**
 * Metric Item - Display for key metrics
 */
function MetricItem({ value, label, color }) {
  return (
    <div className="text-center" style={{ padding: 'var(--space-3)' }}>
      <div className="text-2xl text-mono" style={{ color: color || 'var(--text)' }}>
        {value}
      </div>
      <div className="text-label" style={{ marginTop: 'var(--space-1)' }}>
        {label}
      </div>
    </div>
  );
}

/**
 * Metric Badge - Small metric display with label
 */
function MetricBadge({ label, value, color }) {
  return (
    <div
      className="text-body-sm"
      style={{
        padding: 'var(--space-2) var(--space-3)',
        background: 'rgba(255,255,255,0.04)',
        border: '1px solid var(--border)',
        borderRadius: 'var(--radius-sm)',
        whiteSpace: 'nowrap'
      }}
    >
      <span style={{ color: 'var(--text-tertiary)', fontSize: 'var(--text-xs)' }}>{label}:</span>{' '}
      <span className="text-mono" style={{ color: color || 'var(--text)', fontWeight: 500 }}>{value}</span>
    </div>
  );
}

function ModuleDetailView({ path }) {
  const data = useStore((s) => s.data);
  const [openCats, setOpenCats] = useState(() => {
    // First 2 categories start open
    const initial = new Set();
    let count = 0;
    for (const cat of MODULE_SIGNAL_CATEGORIES) {
      if (count >= 2) break;
      initial.add(cat.key);
      count++;
    }
    return initial;
  });

  if (!data || !data.modules || !data.modules[path]) {
    return (
      <div>
        <a class="file-detail-back" href="#modules">&larr; Modules</a>
        <div class="empty-state">
          <div class="empty-state-title">Module not found</div>
          <div>{path}</div>
        </div>
      </div>
    );
  }

  const m = data.modules[path];
  const color = hColor(m.health_score || 5);

  // Key metrics shown at top
  const topMetrics = [
    { label: "File Count", value: m.file_count, interp: interpretSignal("file_count", m.file_count) },
    { label: "Health Score", value: fmtF(m.health_score, 1), interp: interpretSignal("health_score", m.health_score) },
    { label: "Change Sensitivity", value: fmtF(m.instability, 2), interp: interpretSignal("instability", m.instability) },
    { label: "Abstraction Level", value: fmtF(m.abstractness, 2), interp: interpretSignal("abstractness", m.abstractness) },
  ];

  // All module signals with trends
  const sigs = m.signals || {};
  const sigKeys = Object.keys(sigs);

  // Build categorized set for detecting uncategorized signals
  const categorized = new Set();
  MODULE_SIGNAL_CATEGORIES.forEach((c) => c.signals.forEach((s) => categorized.add(s)));
  const uncatSigs = sigKeys.filter((s) => !categorized.has(s) && sigs[s] != null).sort();

  function toggleCat(catKey) {
    setOpenCats((prev) => {
      const next = new Set(prev);
      if (next.has(catKey)) next.delete(catKey);
      else next.add(catKey);
      return next;
    });
  }

  return (
    <div>
      <a class="file-detail-back" href="#modules">&larr; Modules</a>

      <div class="file-detail-header">
        <span class="file-detail-path">{path}</span>
        <span class="file-detail-health" style={{ color }}>{fmtF(m.health_score, 1)}</span>
      </div>

      {/* Top metrics grid */}
      <div class="file-detail-metrics">
        {topMetrics.map((met) => (
          <div class="fdm-cell" key={met.label}>
            <div class="fdm-value">{met.value != null ? met.value : "--"}</div>
            <div class="fdm-label">{met.label}</div>
            {met.interp && <div class="fdm-interp">{met.interp}</div>}
          </div>
        ))}
      </div>

      {/* Module signals grouped by category */}
      {sigKeys.length > 0 && (
        <div class="file-detail-section">
          {MODULE_SIGNAL_CATEGORIES.map((cat) => {
            const catSigs = cat.signals.filter((s) => sigs[s] != null);
            if (!catSigs.length) return null;

            const isOpen = openCats.has(cat.key);
            return (
              <div key={cat.key}>
                <div
                  class={`file-detail-section-title signals-collapsible sig-cat-toggle${isOpen ? " sig-cat-open open" : ""}`}
                  onClick={() => toggleCat(cat.key)}
                >
                  {cat.name} ({catSigs.length})
                  {cat.description && isOpen && (
                    <span class="sig-cat-desc">{cat.description}</span>
                  )}
                </div>
                <div
                  class="signals-grid sig-cat-grid"
                  style={{ display: isOpen ? "grid" : "none" }}
                >
                  {catSigs.map((sk) => {
                    const sv = sigs[sk];
                    const label = MODULE_SIGNAL_LABELS[sk] || sk.replace(/_/g, " ");
                    const display = fmtSigVal(sk, sv);
                    const valColor = typeof sv === "number" ? polarColor(sk, sv) : "var(--text)";
                    const trendData = m.trends && m.trends[sk];
                    const interp = interpretSignal(sk, sv);

                    return (
                      <div class="sig-row" key={sk}>
                        <span class="sig-name">
                          {label}
                          {MODULE_SIGNAL_DESCRIPTIONS[sk] && (
                            <span class="sig-desc">{MODULE_SIGNAL_DESCRIPTIONS[sk]}</span>
                          )}
                        </span>
                        <span class="sig-val-group">
                          <span class="sig-val" style={{ color: valColor }}>
                            {display}
                            {trendData && (
                              <>
                                {" "}
                                <Sparkline values={trendData} width={48} height={14} color={valColor} />
                              </>
                            )}
                          </span>
                          {interp && <span class="sig-interp">{interp}</span>}
                        </span>
                      </div>
                    );
                  })}
                </div>
              </div>
            );
          })}

          {/* Uncategorized signals */}
          {uncatSigs.length > 0 && (
            <div>
              <div
                class={`file-detail-section-title signals-collapsible sig-cat-toggle${openCats.has("other") ? " sig-cat-open open" : ""}`}
                onClick={() => toggleCat("other")}
              >
                Other ({uncatSigs.length})
              </div>
              <div
                class="signals-grid sig-cat-grid"
                style={{ display: openCats.has("other") ? "grid" : "none" }}
              >
                {uncatSigs.map((sk) => {
                  const sv = sigs[sk];
                  const display =
                    typeof sv === "number"
                      ? Number.isInteger(sv)
                        ? String(sv)
                        : sv.toFixed(4)
                      : String(sv);
                  return (
                    <div class="sig-row" key={sk}>
                      <span class="sig-name">{sk.replace(/_/g, " ")}</span>
                      <span class="sig-val">{display}</span>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Violations */}
      {m.violations && m.violations.length > 0 && (
        <div class="file-detail-section">
          <div class="file-detail-section-title">Violations ({m.violations.length})</div>
          {m.violations.map((v, i) => (
            <div class="module-violation-item" key={i}>{typeof v === "string" ? v : JSON.stringify(v)}</div>
          ))}
        </div>
      )}
    </div>
  );
}

export function ModulesScreenV2() {
  const moduleDetail = useStore((s) => s.moduleDetail);

  if (moduleDetail) {
    return <ModuleDetailView path={moduleDetail} />;
  }

  return <ModuleListViewV2 />;
}
