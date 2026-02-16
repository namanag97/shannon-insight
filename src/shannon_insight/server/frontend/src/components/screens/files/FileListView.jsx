/**
 * FileListView - Redesigned with proper information architecture
 *
 * Information Priority:
 * 1. Summary Cards - Risk distribution at a glance (how many high/medium/low?)
 * 2. Top 10 Files - Actionable list of worst files (what should I fix?)
 * 3. Search + Filters - Tools for exploration (below insights, not above)
 * 4. Full File Table - Comprehensive grouped view (all data, organized by tier)
 *
 * Design System:
 * - 12-column grid with proper gutters
 * - Mathematical spacing (8px baseline)
 * - Clear visual hierarchy
 * - Every component intentionally placed
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
      <div className="empty-state">
        <div className="empty-state-title">No file data</div>
      </div>
    );
  }

  // Build entries array (preserving all existing logic)
  let entries = [];
  for (const p in data.files) entries.push({ path: p, ...data.files[p] });
  const totalCount = entries.length;
  const changedSet = data.recent_changes ? new Set(data.recent_changes) : new Set();

  // Compute risk tiers BEFORE filtering (for summary cards showing full picture)
  const allHighRisk = entries.filter((e) => (e.risk_score || 0) > 0.07);
  const allMediumRisk = entries.filter((e) => {
    const s = e.risk_score || 0;
    return s > 0.03 && s <= 0.07;
  });
  const allLowRisk = entries.filter((e) => {
    const s = e.risk_score || 0;
    return s > 0 && s <= 0.03;
  });
  const allNoRisk = entries.filter((e) => !e.risk_score || e.risk_score === 0);

  // Top 10 files by risk (before filtering, excluding zero-risk)
  const top10 = [...entries]
    .sort((a, b) => (b.risk_score || 0) - (a.risk_score || 0))
    .slice(0, 10)
    .filter((e) => (e.risk_score || 0) > 0);

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

  // Group filtered entries by risk tier for grouped table view
  const highRisk = entries.filter((e) => (e.risk_score || 0) > 0.07);
  const mediumRisk = entries.filter((e) => {
    const s = e.risk_score || 0;
    return s > 0.03 && s <= 0.07;
  });
  const lowRisk = entries.filter((e) => {
    const s = e.risk_score || 0;
    return s > 0 && s <= 0.03;
  });
  const noRisk = entries.filter((e) => !e.risk_score || e.risk_score === 0);

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
    <div className="stack stack--2xl">
      {/* ══════════════════════════════════════════════════════════
          PRIORITY 1: SUMMARY CARDS - Risk Distribution at a Glance
          Answer: "How are my files distributed by risk?"
          ══════════════════════════════════════════════════════════ */}
      <section>
        <div className="grid grid--compact">
          <div className="span-3">
            <RiskSummaryCard
              level="HIGH"
              count={allHighRisk.length}
              total={totalCount}
              color="var(--red)"
            />
          </div>
          <div className="span-3">
            <RiskSummaryCard
              level="MEDIUM"
              count={allMediumRisk.length}
              total={totalCount}
              color="var(--orange)"
            />
          </div>
          <div className="span-3">
            <RiskSummaryCard
              level="LOW"
              count={allLowRisk.length}
              total={totalCount}
              color="var(--yellow)"
            />
          </div>
          <div className="span-3">
            <RiskSummaryCard
              level="NO ISSUES"
              count={allNoRisk.length}
              total={totalCount}
              color="var(--text-tertiary)"
            />
          </div>
        </div>
      </section>

      {/* ══════════════════════════════════════════════════════════
          PRIORITY 2: TOP 10 FILES NEEDING ATTENTION
          Answer: "Which files should I fix first?"
          ══════════════════════════════════════════════════════════ */}
      {top10.length > 0 && (
        <section>
          <div className="ds-card">
            <div className="ds-card__header">
              <div className="ds-card__title">Files Needing Attention (Top 10)</div>
            </div>
            <div className="ds-card__body">
              <CompactFileTable files={top10} onFileClick={handleFileClick} />
            </div>
          </div>
        </section>
      )}

      {/* ══════════════════════════════════════════════════════════
          PRIORITY 3: SEARCH + FILTERS
          Tools below insights (insight-first UX)
          ══════════════════════════════════════════════════════════ */}
      <section>
        <div className="ds-card ds-card--compact">
          <div className="ds-card__body">
            <div className="stack stack--md">
              {/* Search input */}
              <input
                className="search-input"
                type="text"
                id="fileSearchInput"
                placeholder="Search files..."
                value={fileSearch}
                onInput={(e) => setFileSearch(e.target.value)}
                onKeyDown={(e) => { if (e.key === "Escape") e.target.blur(); }}
              />

              {/* Filter chips */}
              <div className="cluster cluster--sm">
                {FILE_FILTER_CHIPS.map(([key, label]) => (
                  <FilterChip
                    key={key}
                    label={label}
                    active={fileFilters.has(key)}
                    onClick={() => toggleFileFilter(key)}
                  />
                ))}
              </div>

              {/* File count + view mode toggle */}
              <div className="cluster cluster--sm" style={{ justifyContent: 'space-between' }}>
                <div className="text-body-sm" style={{ color: 'var(--text-secondary)' }}>
                  Showing {entries.length} of {totalCount} files
                </div>
                <div className="treemap-toggle">
                  <button
                    className={fileViewMode === "table" ? "active" : ""}
                    onClick={() => setFileViewMode("table")}
                  >
                    Table
                  </button>
                  <button
                    className={fileViewMode === "treemap" ? "active" : ""}
                    onClick={() => setFileViewMode("treemap")}
                  >
                    Treemap
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ══════════════════════════════════════════════════════════
          PRIORITY 4: FULL FILE TABLE (or Treemap)
          Comprehensive view grouped by risk tier
          ══════════════════════════════════════════════════════════ */}
      <section>
        {fileViewMode === "treemap" ? (
          <Treemap
            entries={entries.map((e) => [e.path, e])}
            onFileClick={(path) => {
              location.hash = "files/" + encodeURIComponent(path);
            }}
          />
        ) : (
          <GroupedFileTable
            highRisk={highRisk}
            mediumRisk={mediumRisk}
            lowRisk={lowRisk}
            noRisk={noRisk}
            columns={FILE_COLUMNS}
            sortKey={fileSortKey}
            sortAsc={fileSortAsc}
            onSort={setFileSortKey}
            onFileClick={handleFileClick}
            selectedIndex={sel}
            maxRows={200}
            totalFiltered={entries.length}
          />
        )}
      </section>
    </div>
  );
}


/* ═══════════════════════════════════════════════════════════════════════════
   SUB-COMPONENTS
   ═══════════════════════════════════════════════════════════════════════════ */

/**
 * Risk Summary Card - Displays count of files in a risk tier.
 * Uses design system card and typography patterns.
 */
function RiskSummaryCard({ level, count, total, color }) {
  const percent = total > 0 ? ((count / total) * 100).toFixed(0) : 0;

  return (
    <div className="ds-card ds-card--compact" style={{ textAlign: 'center' }}>
      <div
        className="text-label"
        style={{
          color,
          letterSpacing: 'var(--tracking-wider)',
          fontWeight: 'var(--font-semibold)',
        }}
      >
        {level}
      </div>
      <div
        className="text-mono"
        style={{
          color,
          marginTop: 'var(--space-1)',
          fontSize: 'var(--text-2xl)',
          fontWeight: 'var(--font-semibold)',
          lineHeight: 'var(--leading-tight)',
        }}
      >
        {count}
      </div>
      <div
        className="text-label"
        style={{
          marginTop: 'var(--space-1)',
          color: 'var(--text-tertiary)',
        }}
      >
        {percent}% of files
      </div>
    </div>
  );
}

/**
 * Compact File Table - Shows top N files in a dense, clickable table.
 * Used for the "Files Needing Attention" priority section.
 * Columns: Path | Risk | Issues | Complexity
 */
function CompactFileTable({ files, onFileClick }) {
  const columns = [
    {
      key: "path",
      label: "File",
      align: "left",
      format: (v) => <span className="text-mono">{v}</span>,
      cellClass: () => "td-path",
    },
    {
      key: "risk_score",
      label: "Risk",
      align: "right",
      format: (v) => fmtF(v, 3),
      cellClass: () => "td-risk",
      cellStyle: (v) => {
        const score = v || 0;
        return { color: hColor(10 - score * 10), fontWeight: 600 };
      },
    },
    {
      key: "finding_count",
      label: "Issues",
      align: "right",
      format: (v) => v || 0,
      cellClass: () => "td-issues",
    },
    {
      key: "cognitive_load",
      label: "Complexity",
      align: "right",
      format: (v) => fmtF(v, 1),
      cellClass: () => "td-num",
    },
  ];

  return (
    <Table
      columns={columns}
      data={files}
      rowKey={(row) => row.path}
      sortable={false}
      onRowClick={onFileClick}
      maxRows={10}
    />
  );
}

/**
 * Grouped File Table - Full file table with visual separators between risk tiers.
 * Shows HIGH, MEDIUM, LOW, and NO RISK groups with clear headers.
 */
function GroupedFileTable({
  highRisk,
  mediumRisk,
  lowRisk,
  noRisk,
  columns,
  sortKey,
  sortAsc,
  onSort,
  onFileClick,
  selectedIndex,
  maxRows,
  totalFiltered,
}) {
  // Track how many rows we have rendered for maxRows limit
  let rowsRendered = 0;
  const limit = maxRows || Infinity;

  const groups = [
    { key: "high", label: "HIGH RISK", data: highRisk, color: "var(--red)" },
    { key: "medium", label: "MEDIUM RISK", data: mediumRisk, color: "var(--orange)" },
    { key: "low", label: "LOW RISK", data: lowRisk, color: "var(--yellow)" },
    { key: "none", label: "NO RISK", data: noRisk, color: "var(--text-tertiary)" },
  ];

  return (
    <div className="stack stack--lg">
      {groups.map((group) => {
        if (group.data.length === 0) return null;

        const remaining = limit - rowsRendered;
        if (remaining <= 0) return null;

        const slicedData = group.data.slice(0, remaining);
        rowsRendered += slicedData.length;

        return (
          <div key={group.key}>
            {/* Tier header with colored underline */}
            <div
              className="text-h4"
              style={{
                color: group.color,
                marginBottom: 'var(--space-4)',
                paddingBottom: 'var(--space-2)',
                borderBottom: `2px solid ${group.color}`,
              }}
            >
              {group.label} ({group.data.length})
            </div>

            {/* Tier table */}
            <Table
              columns={columns}
              data={slicedData}
              rowKey={(row) => row.path}
              sortable={true}
              sortKey={sortKey}
              sortAsc={sortAsc}
              onSort={onSort}
              onRowClick={onFileClick}
              selectedIndex={-1}
              stickyHeader={false}
            />

            {group.data.length > remaining && (
              <div
                className="text-body-sm"
                style={{
                  color: 'var(--text-tertiary)',
                  marginTop: 'var(--space-2)',
                }}
              >
                Showing {slicedData.length} of {group.data.length} files in this tier
              </div>
            )}
          </div>
        );
      })}

      {totalFiltered > limit && (
        <div
          className="text-body-sm"
          style={{
            color: 'var(--text-tertiary)',
            textAlign: 'center',
            marginTop: 'var(--space-4)',
          }}
        >
          Showing first {Math.min(limit, totalFiltered)} of {totalFiltered} files (use search/filters to narrow)
        </div>
      )}
    </div>
  );
}
