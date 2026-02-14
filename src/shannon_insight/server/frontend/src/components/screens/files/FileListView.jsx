/**
 * File list view - table or treemap mode with search, filters, and sorting.
 * Extracted from the 270-line showFileList() function.
 */

import useStore from "../../../state/store.js";
import { fmtF } from "../../../utils/formatters.js";
import { hColor } from "../../../utils/helpers.js";
import { FilterChip } from "../../ui/FilterChip.jsx";
import { Badge } from "../../ui/Badge.jsx";
import { Treemap } from "../../charts/Treemap.jsx";

const FILE_FILTER_CHIPS = [
  ["has_issues", "Has Issues"],
  ["orphans", "Orphans (no importers)"],
  ["MODEL", "Model"],
  ["SERVICE", "Service"],
  ["ENTRY_POINT", "Entry Point"],
  ["TEST", "Test"],
];

const FILE_COLUMNS = [
  { key: "path", label: "File", numeric: false },
  { key: "risk_score", label: "Risk Score", numeric: true },
  { key: "total_changes", label: "Commits", numeric: true },
  { key: "cognitive_load", label: "Complexity", numeric: true },
  { key: "blast_radius", label: "Impact Size", numeric: true },
  { key: "finding_count", label: "Issues", numeric: true },
];

export function FileListView() {
  const data = useStore((s) => s.data);
  const fileSortKey = useStore((s) => s.fileSortKey);
  const fileSortAsc = useStore((s) => s.fileSortAsc);
  const fileSearch = useStore((s) => s.fileSearch);
  const fileFilters = useStore((s) => s.fileFilters);
  const fileViewMode = useStore((s) => s.fileViewMode);
  const selectedIndex = useStore((s) => s.selectedIndex);
  const setFileSortKey = useStore((s) => s.setFileSortKey);
  const setFileSearch = useStore((s) => s.setFileSearch);
  const toggleFileFilter = useStore((s) => s.toggleFileFilter);
  const setFileViewMode = useStore((s) => s.setFileViewMode);

  if (!data || !data.files) {
    return (
      <div class="empty-state">
        <div class="empty-state-title">No file data</div>
      </div>
    );
  }

  // Build entries array
  let entries = [];
  for (const p in data.files) entries.push([p, data.files[p]]);
  const totalCount = entries.length;
  const changedSet = data.recent_changes ? new Set(data.recent_changes) : new Set();

  // Apply search
  if (fileSearch) {
    const q = fileSearch.toLowerCase();
    entries = entries.filter((e) => e[0].toLowerCase().indexOf(q) !== -1);
  }

  // Apply filters
  if (fileFilters.has("has_issues")) {
    entries = entries.filter((e) => (e[1].finding_count || 0) > 0);
  }
  if (fileFilters.has("orphans")) {
    entries = entries.filter((e) => e[1].signals && e[1].signals.is_orphan);
  }
  const roleFilters = [];
  fileFilters.forEach((f) => {
    if (["MODEL", "SERVICE", "ENTRY_POINT", "TEST"].indexOf(f) !== -1) roleFilters.push(f);
  });
  if (roleFilters.length > 0) {
    const rs = new Set(roleFilters);
    entries = entries.filter((e) => rs.has(e[1].role));
  }

  // Sort
  entries.sort((a, b) => {
    if (fileSortKey === "path") {
      return fileSortAsc ? a[0].localeCompare(b[0]) : b[0].localeCompare(a[0]);
    }
    const va = a[1][fileSortKey] != null ? a[1][fileSortKey] : 0;
    const vb = b[1][fileSortKey] != null ? b[1][fileSortKey] : 0;
    return fileSortAsc ? va - vb : vb - va;
  });

  function handleFileClick(path) {
    location.hash = "files/" + encodeURIComponent(path);
  }

  const sel = selectedIndex.files || 0;

  return (
    <div>
      {/* Filter bar */}
      <div class="filter-bar">
        <input
          class="search-input"
          type="text"
          id="fileSearchInput"
          placeholder="Search files..."
          value={fileSearch}
          onInput={(e) => setFileSearch(e.target.value)}
          onKeyDown={(e) => { if (e.key === "Escape") e.target.blur(); }}
        />
        {FILE_FILTER_CHIPS.map(([key, label]) => (
          <FilterChip
            key={key}
            label={label}
            active={fileFilters.has(key)}
            onClick={() => toggleFileFilter(key)}
          />
        ))}
        <div class="treemap-toggle">
          <button
            class={fileViewMode === "table" ? "active" : ""}
            onClick={() => setFileViewMode("table")}
          >
            Table
          </button>
          <button
            class={fileViewMode === "treemap" ? "active" : ""}
            onClick={() => setFileViewMode("treemap")}
          >
            Treemap
          </button>
        </div>
      </div>

      <div class="file-count-summary">
        Showing {entries.length} of {totalCount} files
      </div>

      {fileViewMode === "treemap" ? (
        <Treemap entries={entries} onFileClick={handleFileClick} />
      ) : (
        <div>
          <table class="file-table">
            <thead>
              <tr>
                {FILE_COLUMNS.map((col) => {
                  const arrow =
                    fileSortKey === col.key
                      ? fileSortAsc
                        ? <span class="sort-arrow">&#9650;</span>
                        : <span class="sort-arrow">&#9660;</span>
                      : null;
                  return (
                    <th
                      key={col.key}
                      class={col.numeric ? "num" : undefined}
                      data-sort={col.key}
                      onClick={() => setFileSortKey(col.key)}
                    >
                      {col.label}
                      {arrow}
                    </th>
                  );
                })}
              </tr>
            </thead>
            <tbody>
              {entries.slice(0, 200).map(([path, f], r) => {
                const riskColor = hColor(10 - (f.risk_score || 0) * 10);
                const riskStyle =
                  (f.risk_score || 0) > 0.05 ? { color: riskColor } : undefined;
                return (
                  <tr
                    key={path}
                    data-path={path}
                    class={r === sel ? "kbd-selected" : undefined}
                    onClick={() => handleFileClick(path)}
                  >
                    <td class="td-path" title={path}>
                      <span>{path}</span>
                      {changedSet.has(path) && <Badge variant="changed">changed</Badge>}
                    </td>
                    <td class="td-risk" style={riskStyle}>{fmtF(f.risk_score, 3)}</td>
                    <td class="td-num">{f.total_changes || 0}</td>
                    <td class="td-num">{fmtF(f.cognitive_load, 1)}</td>
                    <td class="td-num">{f.blast_radius || 0}</td>
                    <td class="td-issues">{f.finding_count || 0}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
          {entries.length > 200 && (
            <div class="file-count-note">
              Showing 200 of {entries.length} files (filtered)
            </div>
          )}
        </div>
      )}
    </div>
  );
}
