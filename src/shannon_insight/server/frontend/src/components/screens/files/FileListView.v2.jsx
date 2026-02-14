/**
 * FileListView v2 - Redesigned with proper information architecture
 *
 * Information Priority:
 * 1. Summary Cards - Risk distribution (high/medium/low/none)
 * 2. Top 10 Files Needing Attention - Action items
 * 3. Tools - Search and filters BELOW insights
 * 4. Full File Table - Grouped by risk tier, sortable
 *
 * Design System:
 * - 12-column grid with proper gutters
 * - Mathematical spacing (8px baseline)
 * - Insights before tools
 * - Clear visual hierarchy
 */

import useStore from "../../../state/store.js";
import { fmtF, fmtN } from "../../../utils/formatters.js";
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

export function FileListViewV2() {
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

  // Calculate risk distribution BEFORE filtering
  const riskDistribution = calculateRiskDistribution(entries);

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

  // Get top 10 files needing attention (highest risk, has issues)
  const top10Files = getTop10Files(entries);

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
          PRIORITY 1: SUMMARY CARDS - Risk Distribution
          Answer: "How many files are at risk?"
          ══════════════════════════════════════════════════════════ */}
      <section>
        <div className="grid grid--compact">
          <div className="span-3">
            <RiskSummaryCard
              level="HIGH"
              count={riskDistribution.high}
              total={totalCount}
              color="var(--red)"
              icon="🔴"
            />
          </div>
          <div className="span-3">
            <RiskSummaryCard
              level="MEDIUM"
              count={riskDistribution.medium}
              total={totalCount}
              color="var(--orange)"
              icon="🟡"
            />
          </div>
          <div className="span-3">
            <RiskSummaryCard
              level="LOW"
              count={riskDistribution.low}
              total={totalCount}
              color="var(--yellow)"
              icon="🟢"
            />
          </div>
          <div className="span-3">
            <RiskSummaryCard
              level="NO ISSUES"
              count={riskDistribution.none}
              total={totalCount}
              color="var(--text-tertiary)"
              icon="⚪"
            />
          </div>
        </div>
      </section>

      {/* ══════════════════════════════════════════════════════════
          PRIORITY 2: TOP 10 FILES NEEDING ATTENTION
          Answer: "What should I fix first?"
          ══════════════════════════════════════════════════════════ */}
      {top10Files.length > 0 && (
        <section>
          <div className="grid">
            <div className="span-12">
              <div className="ds-card">
                <div className="ds-card__header">
                  <div className="ds-card__title">🎯 FILES NEEDING ATTENTION (Top 10)</div>
                </div>
                <div className="ds-card__body">
                  <Top10FilesTable files={top10Files} onFileClick={handleFileClick} />
                </div>
              </div>
            </div>
          </div>
        </section>
      )}

      {/* ══════════════════════════════════════════════════════════
          PRIORITY 3: TOOLS - Search and Filters
          Tools BELOW insights (insight-first UX)
          ══════════════════════════════════════════════════════════ */}
      <section>
        <div className="grid">
          <div className="span-12">
            <div className="ds-card ds-card--compact">
              <div className="ds-card__body">
                <div className="stack stack--md">
                  {/* Search */}
                  <input
                    className="search-input"
                    type="text"
                    id="fileSearchInput"
                    placeholder="Search files..."
                    value={fileSearch}
                    onInput={(e) => setFileSearch(e.target.value)}
                    onKeyDown={(e) => { if (e.key === "Escape") e.target.blur(); }}
                  />

                  {/* Filters */}
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

                  {/* View mode toggle */}
                  <div className="cluster cluster--sm" style={{ justifyContent: 'space-between', alignItems: 'center' }}>
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
          </div>
        </div>
      </section>

      {/* ══════════════════════════════════════════════════════════
          PRIORITY 4: FULL FILE TABLE
          Grouped by risk tier, sortable
          ══════════════════════════════════════════════════════════ */}
      <section>
        <div className="grid">
          <div className="span-12">
            {fileViewMode === "treemap" ? (
              <Treemap
                entries={entries.map((e) => [e.path, e])}
                onFileClick={(path) => { location.hash = "files/" + encodeURIComponent(path); }}
              />
            ) : (
              <div className="ds-card">
                <div className="ds-card__header">
                  <div className="ds-card__title">ALL FILES ({entries.length})</div>
                </div>
                <div className="ds-card__body">
                  <GroupedFileTable
                    entries={entries}
                    columns={FILE_COLUMNS}
                    sortKey={fileSortKey}
                    sortAsc={fileSortAsc}
                    onSort={setFileSortKey}
                    onRowClick={handleFileClick}
                    selectedIndex={sel}
                  />
                  {entries.length > 200 && (
                    <div className="text-body-sm" style={{ color: 'var(--text-tertiary)', marginTop: 'var(--space-4)', textAlign: 'center' }}>
                      Showing first 200 of {entries.length} files (use search/filters to narrow)
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </section>
    </div>
  );
}


/* ═══════════════════════════════════════════════════════════════════════════
   SUB-COMPONENTS
   ═══════════════════════════════════════════════════════════════════════════ */

/**
 * Risk Summary Card - Shows count and percentage for a risk tier
 */
function RiskSummaryCard({ level, count, total, color, icon }) {
  const percent = total > 0 ? ((count / total) * 100).toFixed(0) : 0;

  return (
    <div className="ds-card ds-card--compact text-center">
      <div className="text-label" style={{ marginBottom: 'var(--space-2)' }}>
        {icon} {level}
      </div>
      <div className="text-3xl text-mono" style={{ color, fontWeight: 600 }}>
        {count}
      </div>
      <div className="text-label" style={{ marginTop: 'var(--space-1)', color: 'var(--text-tertiary)' }}>
        {percent}% of files
      </div>
    </div>
  );
}

/**
 * Top 10 Files Table - Compact table showing files needing attention
 */
function Top10FilesTable({ files, onFileClick }) {
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
      format: (v) => fmtF(v, 2),
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
 * Grouped File Table - Table with risk tier groupings
 */
function GroupedFileTable({ entries, columns, sortKey, sortAsc, onSort, onRowClick, selectedIndex }) {
  // Group entries by risk tier
  const grouped = {
    high: entries.filter(e => getRiskTier(e.risk_score) === 'high'),
    medium: entries.filter(e => getRiskTier(e.risk_score) === 'medium'),
    low: entries.filter(e => getRiskTier(e.risk_score) === 'low'),
    none: entries.filter(e => getRiskTier(e.risk_score) === 'none'),
  };

  const tiers = [
    { key: 'high', label: '🔴 HIGH RISK', color: 'var(--red)', files: grouped.high },
    { key: 'medium', label: '🟡 MEDIUM RISK', color: 'var(--orange)', files: grouped.medium },
    { key: 'low', label: '🟢 LOW RISK', color: 'var(--yellow)', files: grouped.low },
    { key: 'none', label: '⚪ NO ISSUES', color: 'var(--text-tertiary)', files: grouped.none },
  ];

  return (
    <div className="stack stack--lg">
      {tiers.map(tier => {
        if (tier.files.length === 0) return null;

        return (
          <div key={tier.key}>
            {/* Tier header */}
            <div
              className="text-h4"
              style={{
                color: tier.color,
                marginBottom: 'var(--space-4)',
                paddingBottom: 'var(--space-2)',
                borderBottom: `2px solid ${tier.color}`,
              }}
            >
              {tier.label} ({tier.files.length})
            </div>

            {/* Tier table */}
            <Table
              columns={columns}
              data={tier.files}
              rowKey={(row) => row.path}
              sortable={true}
              sortKey={sortKey}
              sortAsc={sortAsc}
              onSort={onSort}
              onRowClick={onRowClick}
              selectedIndex={selectedIndex}
              maxRows={50}
            />

            {tier.files.length > 50 && (
              <div className="text-body-sm" style={{ color: 'var(--text-tertiary)', marginTop: 'var(--space-2)' }}>
                Showing first 50 of {tier.files.length} files in this tier
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}


/* ═══════════════════════════════════════════════════════════════════════════
   HELPERS
   ═══════════════════════════════════════════════════════════════════════════ */

/**
 * Calculate risk distribution across all files
 */
function calculateRiskDistribution(entries) {
  const distribution = {
    high: 0,
    medium: 0,
    low: 0,
    none: 0,
  };

  entries.forEach(e => {
    const tier = getRiskTier(e.risk_score);
    distribution[tier]++;
  });

  return distribution;
}

/**
 * Get risk tier for a given risk score
 */
function getRiskTier(riskScore) {
  const score = riskScore || 0;
  if (score >= 0.7) return 'high';
  if (score >= 0.4) return 'medium';
  if (score >= 0.1) return 'low';
  return 'none';
}

/**
 * Get top 10 files needing attention
 * Criteria: High risk score OR has issues, sorted by risk score descending
 */
function getTop10Files(entries) {
  // Filter to files with issues or high risk
  const needsAttention = entries.filter(e => {
    const hasIssues = (e.finding_count || 0) > 0;
    const highRisk = (e.risk_score || 0) > 0.3;
    return hasIssues || highRisk;
  });

  // Sort by risk score descending
  needsAttention.sort((a, b) => (b.risk_score || 0) - (a.risk_score || 0));

  return needsAttention.slice(0, 10);
}
