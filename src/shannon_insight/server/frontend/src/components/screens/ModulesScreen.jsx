/**
 * Modules screen - sortable table list and module detail view.
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

function ModuleListView() {
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

  const entries = [];
  for (const p in data.modules) {
    entries.push({ path: p, ...data.modules[p] });
  }

  entries.sort((a, b) => {
    if (moduleSortKey === "path") {
      return moduleSortAsc ? a.path.localeCompare(b.path) : b.path.localeCompare(a.path);
    }
    const va = a[moduleSortKey] != null ? a[moduleSortKey] : 0;
    const vb = b[moduleSortKey] != null ? b[moduleSortKey] : 0;
    return moduleSortAsc ? va - vb : vb - va;
  });

  function handleRowClick(row) {
    location.hash = "modules/" + encodeURIComponent(row.path);
  }

  return (
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

export function ModulesScreen() {
  const moduleDetail = useStore((s) => s.moduleDetail);

  if (moduleDetail) {
    return <ModuleDetailView path={moduleDetail} />;
  }

  return <ModuleListView />;
}
