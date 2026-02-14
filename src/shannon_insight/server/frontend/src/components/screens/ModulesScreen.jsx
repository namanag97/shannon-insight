/**
 * Modules screen - sortable table list and module detail view.
 */

import useStore from "../../state/store.js";
import { fmtF } from "../../utils/formatters.js";
import { hColor } from "../../utils/helpers.js";

const MODULE_COLUMNS = [
  { key: "path", label: "Module", numeric: false },
  { key: "health_score", label: "Health", numeric: true },
  { key: "instability", label: "Instability", numeric: true },
  { key: "abstractness", label: "Abstractness", numeric: true },
  { key: "file_count", label: "Files", numeric: true },
  { key: "velocity", label: "Velocity", numeric: true },
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
  for (const p in data.modules) entries.push([p, data.modules[p]]);

  entries.sort((a, b) => {
    if (moduleSortKey === "path") {
      return moduleSortAsc ? a[0].localeCompare(b[0]) : b[0].localeCompare(a[0]);
    }
    const va = a[1][moduleSortKey] != null ? a[1][moduleSortKey] : 0;
    const vb = b[1][moduleSortKey] != null ? b[1][moduleSortKey] : 0;
    return moduleSortAsc ? va - vb : vb - va;
  });

  function handleClick(path) {
    location.hash = "modules/" + encodeURIComponent(path);
  }

  return (
    <table class="module-table">
      <thead>
        <tr>
          {MODULE_COLUMNS.map((col) => {
            const arrow =
              moduleSortKey === col.key
                ? moduleSortAsc
                  ? <span class="sort-arrow">&#9650;</span>
                  : <span class="sort-arrow">&#9660;</span>
                : null;
            return (
              <th
                key={col.key}
                class={col.numeric ? "num" : undefined}
                data-sort={col.key}
                onClick={() => setModuleSortKey(col.key)}
              >
                {col.label}
                {arrow}
              </th>
            );
          })}
        </tr>
      </thead>
      <tbody>
        {entries.map(([p, m]) => {
          const hc = hColor(m.health_score || 5);
          return (
            <tr key={p} data-mod={p} onClick={() => handleClick(p)}>
              <td class="td-path"><span>{p}</span></td>
              <td class="td-risk" style={{ color: hc }}>{fmtF(m.health_score, 1)}</td>
              <td class="td-num">{fmtF(m.instability, 2)}</td>
              <td class="td-num">{fmtF(m.abstractness, 2)}</td>
              <td class="td-num">{m.file_count || 0}</td>
              <td class="td-num">{fmtF(m.velocity, 1)}</td>
            </tr>
          );
        })}
      </tbody>
    </table>
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
    ["Files", m.file_count],
    ["Instability", fmtF(m.instability, 2)],
    ["Abstractness", fmtF(m.abstractness, 2)],
    ["Velocity", fmtF(m.velocity, 1)],
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
