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

  const stats = [
    ["File Count", m.file_count],
    ["Change Sensitivity", fmtF(m.instability, 2)],
    ["Abstraction Level", fmtF(m.abstractness, 2)],
    ["Change Velocity", fmtF(m.velocity, 1)],
  ];

  return (
    <div>
      <a class="file-detail-back" href="#modules">&larr; Modules</a>

      <div class="file-detail-header">
        <span class="file-detail-path">{path}</span>
        <span class="file-detail-health" style={{ color }}>{fmtF(m.health_score, 1)}</span>
      </div>

      <div class="file-detail-metrics">
        {stats.map(([label, value]) => (
          <div class="fdm-cell" key={label}>
            <div class="fdm-value">{value != null ? value : "--"}</div>
            <div class="fdm-label">{label}</div>
          </div>
        ))}
      </div>

      {m.files && m.files.length > 0 && (
        <div class="file-detail-section">
          <div class="file-detail-section-title">Files ({m.files.length})</div>
          {m.files.map((f) => (
            <div class="module-file-item" key={f}>
              <a href={"#files/" + encodeURIComponent(f)}>{f}</a>
            </div>
          ))}
        </div>
      )}

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
