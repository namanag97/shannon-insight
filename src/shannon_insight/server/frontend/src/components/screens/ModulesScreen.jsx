/**
 * ModulesScreen v2 - Redesigned with proper information architecture
 *
 * Information Priority:
 * 1. Summary Cards - Module health + architectural metrics (2-column grid)
 * 2. Modules Needing Attention - Top 5 worst modules (action items)
 * 3. All Modules Table - Full sortable table
 *
 * Design System:
 * - 12-column grid with proper gutters
 * - Mathematical spacing (8px baseline)
 * - Clear visual hierarchy
 * - Insights before tools
 */

import { useState } from "preact/hooks";
import useStore from "../../state/store.js";
import { fmtF, fmtSigVal } from "../../utils/formatters.js";
import { hColor, polarColor } from "../../utils/helpers.js";
import { Table } from "../ui/Table.jsx";
import {
  MODULE_SIGNAL_LABELS,
  MODULE_SIGNAL_DESCRIPTIONS,
  MODULE_SIGNAL_CATEGORIES,
} from "../../utils/constants.js";
import { interpretSignal } from "../../utils/interpretations.js";
import { Sparkline } from "../charts/Sparkline.jsx";


/* =====================================================================
   TABLE COLUMNS
   ===================================================================== */

const MODULE_COLUMNS = [
  {
    key: "path",
    label: "Module",
    align: "left",
    format: (v) => <span className="td-path"><span>{v}</span></span>,
    cellClass: () => "td-path",
  },
  {
    key: "health_score",
    label: "Health",
    align: "right",
    format: (v) => fmtF(v, 1),
    cellClass: () => "td-risk",
    cellStyle: (v, row) => ({ color: hColor(row.health_score || 5) }),
  },
  {
    key: "file_count",
    label: "Files",
    align: "right",
    format: (v) => v || 0,
    cellClass: () => "td-num",
  },
  {
    key: "instability",
    label: "Instability",
    align: "right",
    format: (v) => (v != null ? fmtF(v, 2) : "--"),
    cellClass: () => "td-num",
  },
  {
    key: "abstractness",
    label: "Abstractness",
    align: "right",
    format: (v) => (v != null ? fmtF(v, 2) : "--"),
    cellClass: () => "td-num",
  },
  {
    key: "coupling",
    label: "Coupling",
    align: "right",
    format: (v) => (v != null ? fmtF(v, 2) : "--"),
    cellClass: () => "td-num",
  },
  {
    key: "velocity",
    label: "Velocity",
    align: "right",
    format: (v) => (v != null ? fmtF(v, 1) : "--"),
    cellClass: () => "td-num",
  },
];


/* =====================================================================
   MAIN COMPONENT
   ===================================================================== */

export function ModulesScreenV2() {
  const data = useStore((s) => s.data);
  const moduleDetail = useStore((s) => s.moduleDetail);
  const moduleSortKey = useStore((s) => s.moduleSortKey);
  const moduleSortAsc = useStore((s) => s.moduleSortAsc);
  const setModuleSortKey = useStore((s) => s.setModuleSortKey);

  // If showing module detail, delegate to detail view (preserve existing behavior)
  if (moduleDetail) {
    return <ModuleDetailView path={moduleDetail} />;
  }

  if (!data || !data.modules) {
    return (
      <div className="grid">
        <div className="span-12">
          <div className="ds-card" style={{ padding: 'var(--space-12)', textAlign: 'center' }}>
            <div className="text-h3" style={{ color: 'var(--text-tertiary)', marginBottom: 'var(--space-2)' }}>
              No module data
            </div>
            <div className="text-body" style={{ color: 'var(--text-tertiary)' }}>
              Run analysis with module detection to see architectural insights.
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Build module entries
  const modules = Object.entries(data.modules).map(([path, mod]) => ({
    path,
    ...mod,
  }));

  if (modules.length === 0) {
    return (
      <div className="grid">
        <div className="span-12">
          <div className="ds-card" style={{ padding: 'var(--space-12)', textAlign: 'center' }}>
            <div className="text-h3" style={{ color: 'var(--text-tertiary)' }}>
              No modules detected
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Calculate summary statistics
  const healthScores = modules.filter((m) => m.health_score != null);
  const avgHealth = healthScores.length > 0
    ? healthScores.reduce((sum, m) => sum + m.health_score, 0) / healthScores.length
    : 0;

  const bestModule = healthScores.length > 0
    ? healthScores.reduce((best, m) => (m.health_score > best.health_score ? m : best))
    : null;
  const worstModule = healthScores.length > 0
    ? healthScores.reduce((worst, m) => (m.health_score < worst.health_score ? m : worst))
    : null;

  // Calculate architectural metrics - check both top-level and signals
  const avgCoupling = computeAvg(modules, "coupling");
  const avgCohesion = computeAvg(modules, "cohesion");

  const totalViolations = modules.reduce((sum, m) => {
    const fromViolations = m.violations ? m.violations.length : 0;
    const fromSignal = getSignalValue(m, "layer_violation_count") || 0;
    return sum + Math.max(fromViolations, fromSignal);
  }, 0);

  // Top 5 worst modules (lowest health scores)
  const top5Worst = [...healthScores]
    .sort((a, b) => (a.health_score || 0) - (b.health_score || 0))
    .slice(0, 5);

  // Sort modules for full table
  const sortedModules = sortModules(modules, moduleSortKey, moduleSortAsc);

  function handleModuleClick(module) {
    location.hash = "modules/" + encodeURIComponent(module.path);
  }

  return (
    <div className="stack stack--2xl">
      {/* ================================================================
          PRIORITY 1: SUMMARY CARDS (2-column grid)
          Answer: "How healthy is my architecture?"
          ================================================================ */}
      <section>
        <div className="grid">
          {/* Module Health Summary */}
          <div className="span-6">
            <div className="ds-card">
              <div className="ds-card__header">
                <div className="ds-card__title">Module Health</div>
              </div>
              <div className="ds-card__body">
                <div className="stack stack--md">
                  <SummaryMetric
                    label="Average Health"
                    value={fmtF(avgHealth, 1)}
                    color={hColor(avgHealth)}
                  />
                  {bestModule && (
                    <SummaryMetric
                      label="Best Module"
                      value={bestModule.path}
                      subValue={"Health: " + fmtF(bestModule.health_score, 1)}
                      color="var(--green)"
                    />
                  )}
                  {worstModule && (
                    <SummaryMetric
                      label="Worst Module"
                      value={worstModule.path}
                      subValue={"Health: " + fmtF(worstModule.health_score, 1)}
                      color="var(--red)"
                    />
                  )}
                  <SummaryMetric
                    label="Total Modules"
                    value={String(modules.length)}
                    color="var(--text)"
                  />
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
                <div className="stack stack--md">
                  <SummaryMetric
                    label="Average Coupling"
                    value={avgCoupling != null ? fmtF(avgCoupling, 2) : "--"}
                    color={
                      avgCoupling == null
                        ? "var(--text-tertiary)"
                        : avgCoupling > 0.6
                          ? "var(--red)"
                          : avgCoupling > 0.4
                            ? "var(--orange)"
                            : "var(--green)"
                    }
                  />
                  <SummaryMetric
                    label="Average Cohesion"
                    value={avgCohesion != null ? fmtF(avgCohesion, 2) : "--"}
                    color={
                      avgCohesion == null
                        ? "var(--text-tertiary)"
                        : avgCohesion < 0.4
                          ? "var(--red)"
                          : avgCohesion < 0.6
                            ? "var(--orange)"
                            : "var(--green)"
                    }
                  />
                  <SummaryMetric
                    label="Architecture Violations"
                    value={String(totalViolations)}
                    color={totalViolations > 0 ? "var(--red)" : "var(--green)"}
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ================================================================
          PRIORITY 2: MODULES NEEDING ATTENTION (Top 5)
          Answer: "Which modules should I focus on?"
          ================================================================ */}
      {top5Worst.length > 0 && (
        <section>
          <div className="grid">
            <div className="span-12">
              <div className="ds-card">
                <div className="ds-card__header">
                  <div className="ds-card__title">Modules Needing Attention (Top 5)</div>
                </div>
                <div className="ds-card__body">
                  <div className="stack stack--sm">
                    {top5Worst.map((module) => (
                      <ProblemModuleRow
                        key={module.path}
                        module={module}
                        onClick={() => handleModuleClick(module)}
                      />
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>
      )}

      {/* ================================================================
          PRIORITY 3: ALL MODULES TABLE
          Answer: "Show me every module"
          ================================================================ */}
      <section>
        <div className="grid">
          <div className="span-12">
            <div className="ds-card">
              <div className="ds-card__header">
                <div className="ds-card__title">All Modules ({modules.length})</div>
              </div>
              <div className="ds-card__body">
                <Table
                  columns={MODULE_COLUMNS}
                  data={sortedModules}
                  rowKey={(row) => row.path}
                  sortable={true}
                  sortKey={moduleSortKey}
                  sortAsc={moduleSortAsc}
                  onSort={setModuleSortKey}
                  onRowClick={handleModuleClick}
                />
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}


/* =====================================================================
   SUB-COMPONENTS: MODULE LIST
   ===================================================================== */

/**
 * Summary Metric - Key-value display for summary cards.
 * Shows label on the left and value on the right.
 */
function SummaryMetric({ label, value, subValue, color }) {
  return (
    <div
      style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        padding: "var(--space-2) 0",
      }}
    >
      <div className="text-body-sm" style={{ color: "var(--text-secondary)" }}>
        {label}
      </div>
      <div style={{ textAlign: "right" }}>
        <div
          className="text-mono"
          style={{
            color: color || "var(--text)",
            fontWeight: "var(--font-semibold)",
            fontSize: "var(--text-md)",
          }}
        >
          {value}
        </div>
        {subValue && (
          <div className="text-label" style={{ marginTop: "var(--space-1)" }}>
            {subValue}
          </div>
        )}
      </div>
    </div>
  );
}

/**
 * Problem Module Row - Compact actionable display for a module
 * needing attention. Clickable to navigate to module detail.
 */
function ProblemModuleRow({ module, onClick }) {
  const healthColor = hColor(module.health_score || 0);

  return (
    <div
      className="stack stack--xs"
      style={{
        padding: "var(--space-3)",
        borderLeft: `3px solid ${healthColor}`,
        background: "rgba(255,255,255,0.02)",
        borderRadius: "var(--radius-sm)",
        cursor: "pointer",
        transition: "background var(--transition-base)",
      }}
      onClick={onClick}
      onMouseEnter={(e) =>
        (e.currentTarget.style.background = "rgba(255,255,255,0.04)")
      }
      onMouseLeave={(e) =>
        (e.currentTarget.style.background = "rgba(255,255,255,0.02)")
      }
    >
      <div className="text-body text-mono" style={{ fontWeight: "var(--font-medium)" }}>
        {module.path}
      </div>
      <div className="cluster cluster--md">
        <span className="text-body-sm" style={{ color: "var(--text-secondary)" }}>
          Health:{" "}
          <span style={{ color: healthColor, fontWeight: "var(--font-medium)" }}>
            {fmtF(module.health_score, 1)}
          </span>
        </span>
        {module.instability != null && (
          <span className="text-body-sm" style={{ color: "var(--text-secondary)" }}>
            Instability: <span className="text-mono">{fmtF(module.instability, 2)}</span>
          </span>
        )}
        {module.coupling != null && (
          <span className="text-body-sm" style={{ color: "var(--text-secondary)" }}>
            Coupling: <span className="text-mono">{fmtF(module.coupling, 2)}</span>
          </span>
        )}
        <span className="text-body-sm" style={{ color: "var(--text-secondary)" }}>
          {module.file_count || 0} files
        </span>
      </div>
    </div>
  );
}

/**
 * Metric Badge - Small metric display with label (used in problem rows)
 */
function MetricBadge({ label, value, color }) {
  return (
    <div
      className="text-body-sm"
      style={{
        padding: "var(--space-2) var(--space-3)",
        background: "rgba(255,255,255,0.04)",
        border: "1px solid var(--border)",
        borderRadius: "var(--radius-sm)",
        whiteSpace: "nowrap",
      }}
    >
      <span style={{ color: "var(--text-tertiary)", fontSize: "var(--text-xs)" }}>
        {label}:
      </span>{" "}
      <span
        className="text-mono"
        style={{ color: color || "var(--text)", fontWeight: "var(--font-medium)" }}
      >
        {value}
      </span>
    </div>
  );
}


/* =====================================================================
   MODULE DETAIL VIEW (Migrated to design system)
   ===================================================================== */

/**
 * Module Detail View - Shows in-depth module signals, metrics, and violations.
 * Fully migrated to design system classes (ds-card, grid, stack, cluster).
 */
function ModuleDetailView({ path }) {
  const data = useStore((s) => s.data);
  const [openCats, setOpenCats] = useState(() => {
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
      <div className="stack stack--lg">
        <a className="file-detail-back" href="#modules">&larr; Modules</a>
        <div className="grid">
          <div className="span-12">
            <div className="ds-card" style={{ padding: "var(--space-12)", textAlign: "center" }}>
              <div className="text-h3" style={{ color: "var(--text-tertiary)", marginBottom: "var(--space-2)" }}>
                Module not found
              </div>
              <div className="text-body" style={{ color: "var(--text-tertiary)" }}>
                {path}
              </div>
            </div>
          </div>
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
    <div className="stack stack--2xl">
      {/* Back navigation */}
      <a className="file-detail-back" href="#modules">&larr; Modules</a>

      {/* Module header with path and health score */}
      <section>
        <div className="grid">
          <div className="span-12">
            <div className="ds-card">
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                }}
              >
                <div
                  className="text-mono"
                  style={{
                    fontSize: "var(--text-xl)",
                    fontWeight: "var(--font-semibold)",
                    color: "var(--text)",
                  }}
                >
                  {path}
                </div>
                <div
                  className="text-mono"
                  style={{
                    fontSize: "var(--text-3xl)",
                    fontWeight: "var(--font-semibold)",
                    color,
                  }}
                >
                  {fmtF(m.health_score, 1)}
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Top metrics grid */}
      <section>
        <div className="grid grid--compact">
          {topMetrics.map((met) => (
            <div className="span-3" key={met.label}>
              <div className="ds-card ds-card--compact" style={{ textAlign: "center" }}>
                <div
                  className="text-mono"
                  style={{
                    fontSize: "var(--text-2xl)",
                    fontWeight: "var(--font-semibold)",
                    color: "var(--text)",
                  }}
                >
                  {met.value != null ? met.value : "--"}
                </div>
                <div className="text-label" style={{ marginTop: "var(--space-1)" }}>
                  {met.label}
                </div>
                {met.interp && (
                  <div
                    className="text-label"
                    style={{ marginTop: "var(--space-1)", color: "var(--text-tertiary)" }}
                  >
                    {met.interp}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Module signals grouped by category */}
      {sigKeys.length > 0 && (
        <section>
          <div className="stack stack--md">
            {MODULE_SIGNAL_CATEGORIES.map((cat) => {
              const catSigs = cat.signals.filter((s) => sigs[s] != null);
              if (!catSigs.length) return null;

              const isOpen = openCats.has(cat.key);
              return (
                <div key={cat.key} className="grid">
                  <div className="span-12">
                    <div className="ds-card">
                      <div
                        className="ds-card__header"
                        style={{
                          cursor: "pointer",
                          userSelect: "none",
                          marginBottom: isOpen ? undefined : 0,
                          paddingBottom: isOpen ? undefined : 0,
                          borderBottom: isOpen ? undefined : "none",
                        }}
                        onClick={() => toggleCat(cat.key)}
                      >
                        <div
                          className="ds-card__title"
                          style={{
                            display: "flex",
                            justifyContent: "space-between",
                            alignItems: "center",
                          }}
                        >
                          <span>
                            {cat.name} ({catSigs.length})
                            {cat.description && isOpen && (
                              <span
                                style={{
                                  fontWeight: "var(--font-normal)",
                                  textTransform: "none",
                                  letterSpacing: "normal",
                                  color: "var(--text-tertiary)",
                                  marginLeft: "var(--space-3)",
                                  fontSize: "var(--text-xs)",
                                }}
                              >
                                {cat.description}
                              </span>
                            )}
                          </span>
                          <span
                            style={{
                              fontFamily: "var(--font-mono)",
                              fontSize: "var(--text-md)",
                              color: "var(--text-tertiary)",
                            }}
                          >
                            {isOpen ? "\u2212" : "+"}
                          </span>
                        </div>
                      </div>
                      {isOpen && (
                        <div className="ds-card__body">
                          <div className="stack stack--sm">
                            {catSigs.map((sk) => {
                              const sv = sigs[sk];
                              const label = MODULE_SIGNAL_LABELS[sk] || sk.replace(/_/g, " ");
                              const display = fmtSigVal(sk, sv);
                              const valColor =
                                typeof sv === "number" ? polarColor(sk, sv) : "var(--text)";
                              const trendData = m.trends && m.trends[sk];
                              const interp = interpretSignal(sk, sv);

                              return (
                                <SignalRow
                                  key={sk}
                                  label={label}
                                  description={MODULE_SIGNAL_DESCRIPTIONS[sk]}
                                  display={display}
                                  valColor={valColor}
                                  trendData={trendData}
                                  interp={interp}
                                />
                              );
                            })}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}

            {/* Uncategorized signals */}
            {uncatSigs.length > 0 && (
              <div className="grid">
                <div className="span-12">
                  <div className="ds-card">
                    <div
                      className="ds-card__header"
                      style={{
                        cursor: "pointer",
                        userSelect: "none",
                        marginBottom: openCats.has("other") ? undefined : 0,
                        paddingBottom: openCats.has("other") ? undefined : 0,
                        borderBottom: openCats.has("other") ? undefined : "none",
                      }}
                      onClick={() => toggleCat("other")}
                    >
                      <div
                        className="ds-card__title"
                        style={{
                          display: "flex",
                          justifyContent: "space-between",
                          alignItems: "center",
                        }}
                      >
                        <span>Other ({uncatSigs.length})</span>
                        <span
                          style={{
                            fontFamily: "var(--font-mono)",
                            fontSize: "var(--text-md)",
                            color: "var(--text-tertiary)",
                          }}
                        >
                          {openCats.has("other") ? "\u2212" : "+"}
                        </span>
                      </div>
                    </div>
                    {openCats.has("other") && (
                      <div className="ds-card__body">
                        <div className="stack stack--sm">
                          {uncatSigs.map((sk) => {
                            const sv = sigs[sk];
                            const display =
                              typeof sv === "number"
                                ? Number.isInteger(sv)
                                  ? String(sv)
                                  : sv.toFixed(4)
                                : String(sv);
                            return (
                              <SignalRow
                                key={sk}
                                label={sk.replace(/_/g, " ")}
                                display={display}
                                valColor="var(--text)"
                              />
                            );
                          })}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>
        </section>
      )}

      {/* Violations */}
      {m.violations && m.violations.length > 0 && (
        <section>
          <div className="grid">
            <div className="span-12">
              <div className="ds-card">
                <div className="ds-card__header">
                  <div className="ds-card__title" style={{ color: "var(--red)" }}>
                    Violations ({m.violations.length})
                  </div>
                </div>
                <div className="ds-card__body">
                  <div className="stack stack--sm">
                    {m.violations.map((v, i) => (
                      <div
                        key={i}
                        className="text-body-sm"
                        style={{
                          padding: "var(--space-3)",
                          borderLeft: "3px solid var(--red)",
                          background: "rgba(239, 68, 68, 0.05)",
                          borderRadius: "var(--radius-sm)",
                        }}
                      >
                        {typeof v === "string" ? v : JSON.stringify(v)}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>
      )}
    </div>
  );
}


/* =====================================================================
   SUB-COMPONENTS: DETAIL VIEW
   ===================================================================== */

/**
 * Signal Row - Displays a single signal with label, value, sparkline,
 * and interpretation. Used in the module detail collapsible sections.
 */
function SignalRow({ label, description, display, valColor, trendData, interp }) {
  return (
    <div
      style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "flex-start",
        padding: "var(--space-2) 0",
        borderBottom: "1px solid var(--border-subtle)",
      }}
    >
      <div className="stack stack--xs" style={{ flex: 1 }}>
        <div className="text-body-sm" style={{ color: "var(--text)" }}>
          {label}
        </div>
        {description && (
          <div className="text-label">{description}</div>
        )}
      </div>
      <div style={{ textAlign: "right", marginLeft: "var(--space-4)" }}>
        <div className="cluster cluster--sm" style={{ justifyContent: "flex-end" }}>
          <span
            className="text-mono"
            style={{
              color: valColor,
              fontWeight: "var(--font-medium)",
              fontSize: "var(--text-base)",
            }}
          >
            {display}
          </span>
          {trendData && (
            <Sparkline values={trendData} width={48} height={14} color={valColor} />
          )}
        </div>
        {interp && (
          <div className="text-label" style={{ marginTop: "var(--space-1)" }}>
            {interp}
          </div>
        )}
      </div>
    </div>
  );
}


/* =====================================================================
   HELPERS
   ===================================================================== */

/**
 * Sort modules by the given key and direction.
 * Returns a new array (does not mutate input).
 */
function sortModules(modules, sortKey, sortAsc) {
  return [...modules].sort((a, b) => {
    if (sortKey === "path") {
      return sortAsc ? a.path.localeCompare(b.path) : b.path.localeCompare(a.path);
    }
    const va = a[sortKey] != null ? a[sortKey] : 0;
    const vb = b[sortKey] != null ? b[sortKey] : 0;
    return sortAsc ? va - vb : vb - va;
  });
}

/**
 * Get a signal value from a module, checking both top-level
 * properties and the signals sub-object.
 */
function getSignalValue(mod, key) {
  if (mod[key] != null) return mod[key];
  if (mod.signals && mod.signals[key] != null) return mod.signals[key];
  return null;
}

/**
 * Compute average for a metric across modules, checking both
 * top-level and signals sub-object.
 */
function computeAvg(modules, key) {
  const values = modules
    .map((m) => getSignalValue(m, key))
    .filter((v) => v != null);
  if (values.length === 0) return null;
  return values.reduce((sum, v) => sum + v, 0) / values.length;
}
