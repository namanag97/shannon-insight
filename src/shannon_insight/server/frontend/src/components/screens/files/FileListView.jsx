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
import { Table } from "../../ui/Table.jsx";

const FILE_FILTER_CHIPS = [
  ["has_issues", "Has Issues"],
  ["orphans", "Orphans (no importers)"],
  ["MODEL", "Model"],
  ["SERVICE", "Service"],
  ["ENTRY_POINT", "Entry Point"],
  ["TEST", "Test"],
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
  for (const p in data.files) entries.push({ path: p, ...data.files[p] });
  const totalCount = entries.length;
  const changedSet = data.recent_changes ? new Set(data.recent_changes) : new Set();

  // Apply search
  if (fileSearch) {
    const q = fileSearch.toLowerCase();
    entries = entries.filter((e) => e.path.toLowerCase().indexOf(q) !== -1);
  }

  // Apply filters
  if (fileFilters.has("has_issues")) {
    entries = entries.filter((e) => (e.finding_count || 0) > 0);
  }
  if (fileFilters.has("orphans")) {
    entries = entries.filter((e) => e.signals && e.signals.is_orphan);
  }
  const roleFilters = [];
  fileFilters.forEach((f) => {
    if (["MODEL", "SERVICE", "ENTRY_POINT", "TEST"].indexOf(f) !== -1) roleFilters.push(f);
  });
  if (roleFilters.length > 0) {
    const rs = new Set(roleFilters);
    entries = entries.filter((e) => rs.has(e.role));
  }

  // Sort
  entries.sort((a, b) => {
    if (fileSortKey === "path") {
      return fileSortAsc ? a.path.localeCompare(b.path) : b.path.localeCompare(a.path);
    }
    const va = a[fileSortKey] != null ? a[fileSortKey] : 0;
    const vb = b[fileSortKey] != null ? b[fileSortKey] : 0;
    return fileSortAsc ? va - vb : vb - va;
  });

  function handleFileClick(row) {
    location.hash = "files/" + encodeURIComponent(row.path);
  }

  const sel = selectedIndex.files || 0;

  const FILE_COLUMNS = [
    {
      key: "path",
      label: "File",
      align: "left",
      format: (v, row) => (
        <>
          <span>{v}</span>
          {changedSet.has(v) && <Badge variant="changed">changed</Badge>}
        </>
      ),
      cellClass: () => "td-path",
    },
    {
      key: "risk_score",
      label: "Risk Score",
      align: "right",
      format: (v) => fmtF(v, 3),
      cellClass: () => "td-risk",
      cellStyle: (v) => {
        const score = v || 0;
        if (score > 0.05) {
          return { color: hColor(10 - score * 10) };
        }
        return undefined;
      },
    },
    {
      key: "total_changes",
      label: "Commits",
      align: "right",
      format: (v) => v || 0,
      cellClass: () => "td-num",
    },
    {
      key: "cognitive_load",
      label: "Complexity",
      align: "right",
      format: (v) => fmtF(v, 1),
      cellClass: () => "td-num",
    },
    {
      key: "blast_radius",
      label: "Impact Size",
      align: "right",
      format: (v) => v || 0,
      cellClass: () => "td-num",
    },
    {
      key: "finding_count",
      label: "Issues",
      align: "right",
      format: (v) => v || 0,
      cellClass: () => "td-issues",
    },
  ];

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
        <Treemap entries={entries.map((e) => [e.path, e])} onFileClick={(path) => { location.hash = "files/" + encodeURIComponent(path); }} />
      ) : (
        <div>
          <Table
            columns={FILE_COLUMNS}
            data={entries}
            rowKey={(row) => row.path}
            sortable={true}
            sortKey={fileSortKey}
            sortAsc={fileSortAsc}
            onSort={setFileSortKey}
            onRowClick={handleFileClick}
            selectedIndex={sel}
            maxRows={200}
          />
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
