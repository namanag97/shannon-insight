/**
 * IssuesScreen v2 - Redesigned with proper information architecture
 *
 * Information Priority:
 * 1. Severity Overview Bar - Visual distribution (CRITICAL | HIGH | MEDIUM | LOW)
 * 2. Critical Findings - Always expanded, all critical issues visible
 * 3. High/Medium Findings - Collapsible sections
 * 4. Tools - Sort + filter below insights
 * 5. Category Tabs - Alternative view
 *
 * Design System:
 * - 12-column grid with proper gutters
 * - Mathematical spacing (8px baseline)
 * - Clear visual hierarchy
 * - Insights before tools
 */

import { useState } from "preact/hooks";
import useStore from "../../state/store.js";
import { FindingCard } from "../cards/FindingCard.jsx";
import { CATEGORY_ORDER, CATEGORY_LABELS, SEVERITY_LEVELS } from "../../utils/constants.js";
import { sevKey } from "../../utils/helpers.js";
import { hColor } from "../../utils/helpers.js";

export function IssuesScreenV2() {
  const data = useStore((s) => s.data);
  const issueTab = useStore((s) => s.issueTab);
  const issueSortKey = useStore((s) => s.issueSortKey);
  const issueSeverityFilter = useStore((s) => s.issueSeverityFilter);
  const setIssueTab = useStore((s) => s.setIssueTab);
  const setIssueSortKey = useStore((s) => s.setIssueSortKey);
  const toggleIssueSeverity = useStore((s) => s.toggleIssueSeverity);

  // Local state for collapsible sections
  const [highExpanded, setHighExpanded] = useState(false);
  const [mediumExpanded, setMediumExpanded] = useState(false);
  const [lowExpanded, setLowExpanded] = useState(false);

  if (!data) return null;

  const cats = data.categories || {};
  const activeTab = cats[issueTab] ? issueTab : CATEGORY_ORDER[0];

  // Chronic findings set
  const chronicSet =
    data.trends && data.trends.chronic
      ? new Set(data.trends.chronic.map((c) => c.finding_type || c.identity_key))
      : new Set();

  // Get all findings across all categories
  const allFindings = [];
  for (const catKey in cats) {
    const cat = cats[catKey];
    if (cat && cat.findings && cat.findings.length > 0) {
      cat.findings.forEach((f) => {
        allFindings.push({ ...f, category: catKey });
      });
    }
  }

  // Sort findings
  const sortedFindings = sortFindings(allFindings, issueSortKey, chronicSet);

  // Group by severity
  const critical = sortedFindings.filter((f) => f.severity >= 8);
  const high = sortedFindings.filter((f) => f.severity >= 6 && f.severity < 8);
  const medium = sortedFindings.filter((f) => f.severity >= 4 && f.severity < 6);
  const low = sortedFindings.filter((f) => f.severity < 4);

  // Calculate severity distribution for overview bar
  const severityCounts = {
    critical: critical.length,
    high: high.length,
    medium: medium.length,
    low: low.length,
  };

  return (
    <div className="stack stack--2xl">
      {/* ══════════════════════════════════════════════════════════
          PRIORITY 1: SEVERITY OVERVIEW BAR
          Answer: "What's the severity distribution?"
          ══════════════════════════════════════════════════════════ */}
      <section>
        <div className="grid">
          <div className="span-12">
            <SeverityOverviewBar counts={severityCounts} total={allFindings.length} />
          </div>
        </div>
      </section>

      {/* ══════════════════════════════════════════════════════════
          PRIORITY 2: CRITICAL FINDINGS (Always Expanded)
          Answer: "What are the critical issues?"
          ══════════════════════════════════════════════════════════ */}
      {critical.length > 0 && (
        <section>
          <div className="grid">
            <div className="span-12">
              <div className="ds-card">
                <div className="ds-card__header">
                  <div className="ds-card__title" style={{ color: 'var(--red)' }}>
                    🔥 CRITICAL FINDINGS ({critical.length})
                  </div>
                </div>
                <div className="ds-card__body">
                  <div className="stack stack--md">
                    {critical.map((f, i) => (
                      <FindingCard
                        key={i}
                        finding={f}
                        showFiles={true}
                        chronicSet={chronicSet}
                        maxEvidence={4}
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
          PRIORITY 3: HIGH/MEDIUM/LOW FINDINGS (Collapsible)
          Answer: "What are the other issues?"
          ══════════════════════════════════════════════════════════ */}
      {high.length > 0 && (
        <section>
          <CollapsibleFindingSection
            title={`⚠️ HIGH PRIORITY (${high.length})`}
            findings={high}
            chronicSet={chronicSet}
            isExpanded={highExpanded}
            onToggle={() => setHighExpanded(!highExpanded)}
            color="var(--orange)"
          />
        </section>
      )}

      {medium.length > 0 && (
        <section>
          <CollapsibleFindingSection
            title={`🟡 MEDIUM PRIORITY (${medium.length})`}
            findings={medium}
            chronicSet={chronicSet}
            isExpanded={mediumExpanded}
            onToggle={() => setMediumExpanded(!mediumExpanded)}
            color="var(--yellow)"
          />
        </section>
      )}

      {low.length > 0 && (
        <section>
          <CollapsibleFindingSection
            title={`🟢 LOW PRIORITY (${low.length})`}
            findings={low}
            chronicSet={chronicSet}
            isExpanded={lowExpanded}
            onToggle={() => setLowExpanded(!lowExpanded)}
            color="var(--green)"
          />
        </section>
      )}

      {/* ══════════════════════════════════════════════════════════
          PRIORITY 4: TOOLS (Sort + Filter)
          Below insights, not above
          ══════════════════════════════════════════════════════════ */}
      <section>
        <div className="grid">
          <div className="span-12">
            <div className="ds-card ds-card--compact">
              <div className="ds-card__body">
                <SortAndFilter
                  sortKey={issueSortKey}
                  setSortKey={setIssueSortKey}
                  severityFilter={issueSeverityFilter}
                  toggleSeverity={toggleIssueSeverity}
                />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ══════════════════════════════════════════════════════════
          PRIORITY 5: CATEGORY TABS (Alternative View)
          For users who want to tackle one category at a time
          ══════════════════════════════════════════════════════════ */}
      <section>
        <div className="grid">
          <div className="span-12">
            <CategoryTabView
              categories={cats}
              activeTab={activeTab}
              setActiveTab={setIssueTab}
              chronicSet={chronicSet}
              sortKey={issueSortKey}
              severityFilter={issueSeverityFilter}
            />
          </div>
        </div>
      </section>

      {/* Empty state */}
      {allFindings.length === 0 && (
        <section>
          <div className="grid">
            <div className="span-12">
              <div className="ds-card" style={{ padding: 'var(--space-12)', textAlign: 'center' }}>
                <div className="text-h3" style={{ color: 'var(--text-tertiary)', marginBottom: 'var(--space-2)' }}>
                  No issues found
                </div>
                <div className="text-body" style={{ color: 'var(--text-tertiary)' }}>
                  Your codebase is looking healthy!
                </div>
              </div>
            </div>
          </div>
        </section>
      )}
    </div>
  );
}


/* ═══════════════════════════════════════════════════════════════════════════
   SUB-COMPONENTS
   ═══════════════════════════════════════════════════════════════════════════ */

/**
 * Severity Overview Bar - Visual distribution of issues by severity
 */
function SeverityOverviewBar({ counts, total }) {
  if (total === 0) return null;

  const segments = [
    { key: 'critical', label: 'CRITICAL', color: 'var(--red)', count: counts.critical },
    { key: 'high', label: 'HIGH', color: 'var(--orange)', count: counts.high },
    { key: 'medium', label: 'MEDIUM', color: 'var(--yellow)', count: counts.medium },
    { key: 'low', label: 'LOW', color: 'var(--green)', count: counts.low },
  ];

  return (
    <div className="ds-card">
      <div className="ds-card__header">
        <div className="ds-card__title">Severity Overview</div>
      </div>
      <div className="ds-card__body">
        <div className="stack stack--md">
          {/* Visual bar */}
          <div style={{ display: 'flex', height: '48px', borderRadius: 'var(--radius-md)', overflow: 'hidden', border: '1px solid var(--border)' }}>
            {segments.map((seg) => {
              if (seg.count === 0) return null;
              const percent = (seg.count / total) * 100;
              return (
                <div
                  key={seg.key}
                  style={{
                    flex: `0 0 ${percent}%`,
                    background: seg.color,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    minWidth: percent < 15 ? '80px' : 'auto',
                  }}
                  title={`${seg.label}: ${seg.count} issues`}
                >
                  <div className="text-body-sm" style={{ color: 'var(--bg)', fontWeight: 600 }}>
                    {seg.count}
                  </div>
                </div>
              );
            })}
          </div>

          {/* Legend */}
          <div className="cluster cluster--md">
            {segments.map((seg) => (
              <div key={seg.key} className="cluster cluster--xs" style={{ alignItems: 'center' }}>
                <div style={{ width: '12px', height: '12px', borderRadius: '2px', background: seg.color }} />
                <div className="text-body-sm">
                  {seg.label} <span className="text-mono" style={{ color: 'var(--text-secondary)' }}>({seg.count})</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

/**
 * Collapsible Finding Section - For high/medium/low priority findings
 */
function CollapsibleFindingSection({ title, findings, chronicSet, isExpanded, onToggle, color }) {
  return (
    <div className="grid">
      <div className="span-12">
        <div className="ds-card">
          <div
            className="ds-card__header"
            style={{ cursor: 'pointer', userSelect: 'none' }}
            onClick={onToggle}
          >
            <div className="ds-card__title" style={{ color, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span>{title}</span>
              <span style={{ fontFamily: 'var(--font-mono)', fontSize: '14px', color: 'var(--text-tertiary)' }}>
                {isExpanded ? '−' : '+'}
              </span>
            </div>
          </div>
          {isExpanded && (
            <div className="ds-card__body">
              <div className="stack stack--md">
                {findings.map((f, i) => (
                  <FindingCard
                    key={i}
                    finding={f}
                    showFiles={true}
                    chronicSet={chronicSet}
                    maxEvidence={4}
                  />
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

/**
 * Sort and Filter Controls
 */
function SortAndFilter({ sortKey, setSortKey, severityFilter, toggleSeverity }) {
  return (
    <div className="cluster cluster--md" style={{ alignItems: 'center', flexWrap: 'wrap' }}>
      {/* Sort dropdown */}
      <div className="cluster cluster--sm" style={{ alignItems: 'center' }}>
        <div className="text-label">SORT BY:</div>
        <select
          className="sort-select"
          value={sortKey}
          onChange={(e) => setSortKey(e.target.value)}
          style={{
            padding: 'var(--space-2) var(--space-3)',
            background: 'var(--surface)',
            border: '1px solid var(--border)',
            borderRadius: 'var(--radius-sm)',
            color: 'var(--text)',
            fontSize: 'var(--text-sm)',
            fontFamily: 'var(--font-sans)',
          }}
        >
          <option value="severity_desc">Severity (high first)</option>
          <option value="severity_asc">Severity (low first)</option>
          <option value="effort_asc">Effort (low first)</option>
          <option value="file_count">File count</option>
        </select>
      </div>

      {/* Severity filter chips */}
      <div className="cluster cluster--sm" style={{ alignItems: 'center' }}>
        <div className="text-label">FILTER:</div>
        {SEVERITY_LEVELS.map((sl) => (
          <button
            key={sl}
            className={`sev-filter${severityFilter.has(sl) ? " active" : ""}`}
            onClick={() => toggleSeverity(sl)}
            style={{
              padding: 'var(--space-2) var(--space-3)',
              background: severityFilter.has(sl) ? getSeverityColor(sl) : 'transparent',
              border: `1px solid ${getSeverityColor(sl)}`,
              borderRadius: 'var(--radius-sm)',
              color: severityFilter.has(sl) ? 'var(--bg)' : getSeverityColor(sl),
              fontSize: 'var(--text-xs)',
              fontWeight: 600,
              textTransform: 'uppercase',
              cursor: 'pointer',
              transition: 'all var(--transition-base)',
            }}
          >
            {sl}
          </button>
        ))}
      </div>
    </div>
  );
}

/**
 * Category Tab View - Alternative view grouped by category
 */
function CategoryTabView({ categories, activeTab, setActiveTab, chronicSet, sortKey, severityFilter }) {
  return (
    <div className="ds-card">
      <div className="ds-card__header">
        <div className="ds-card__title">Browse by Category</div>
      </div>
      <div className="ds-card__body">
        <div className="stack stack--lg">
          {/* Tabs */}
          <div className="cluster cluster--sm" style={{ flexWrap: 'wrap' }}>
            {CATEGORY_ORDER.map((key) => {
              const cat = categories[key];
              if (!cat) return null;
              const isActive = activeTab === key;
              return (
                <button
                  key={key}
                  className={`issue-tab${isActive ? " active" : ""}`}
                  onClick={() => setActiveTab(key)}
                  style={{
                    padding: 'var(--space-3) var(--space-4)',
                    background: isActive ? 'var(--accent)' : 'transparent',
                    border: `1px solid ${isActive ? 'var(--accent)' : 'var(--border)'}`,
                    borderRadius: 'var(--radius-sm)',
                    color: isActive ? 'var(--bg)' : 'var(--text)',
                    fontSize: 'var(--text-sm)',
                    fontWeight: 600,
                    cursor: 'pointer',
                    transition: 'all var(--transition-base)',
                  }}
                >
                  {CATEGORY_LABELS[key] || key}
                  <span style={{ marginLeft: 'var(--space-2)', opacity: 0.8 }}>
                    ({cat.count})
                  </span>
                </button>
              );
            })}
          </div>

          {/* Tab content */}
          <CategoryTabContent
            category={categories[activeTab]}
            categoryKey={activeTab}
            chronicSet={chronicSet}
            sortKey={sortKey}
            severityFilter={severityFilter}
          />
        </div>
      </div>
    </div>
  );
}

/**
 * Category Tab Content - Shows findings for a single category
 */
function CategoryTabContent({ category, categoryKey, chronicSet, sortKey, severityFilter }) {
  if (!category || category.count === 0) {
    return (
      <div className="text-body-sm" style={{ color: 'var(--text-tertiary)', padding: 'var(--space-8) 0', textAlign: 'center' }}>
        No {CATEGORY_LABELS[categoryKey] || categoryKey} issues found
      </div>
    );
  }

  // Get and filter findings
  let findings = (category.findings || []).slice();

  // Filter by severity
  findings = findings.filter((f) => severityFilter.has(sevKey(f.severity)));

  // Sort
  findings = sortFindings(findings, sortKey, chronicSet);

  if (findings.length === 0) {
    return (
      <div className="text-body-sm" style={{ color: 'var(--text-tertiary)', padding: 'var(--space-8) 0', textAlign: 'center' }}>
        No issues match current filters
      </div>
    );
  }

  return (
    <div className="stack stack--md">
      {findings.map((f, i) => (
        <FindingCard
          key={i}
          finding={f}
          showFiles={true}
          chronicSet={chronicSet}
          maxEvidence={4}
        />
      ))}
    </div>
  );
}


/* ═══════════════════════════════════════════════════════════════════════════
   HELPERS
   ═══════════════════════════════════════════════════════════════════════════ */

/**
 * Sort findings based on sort key
 */
function sortFindings(findings, sortKey, chronicSet) {
  const sorted = findings.slice();

  if (sortKey === "severity_desc") {
    sorted.sort((a, b) => b.severity - a.severity);
  } else if (sortKey === "severity_asc") {
    sorted.sort((a, b) => a.severity - b.severity);
  } else if (sortKey === "effort_asc") {
    const effortOrder = { LOW: 0, MEDIUM: 1, HIGH: 2 };
    sorted.sort((a, b) => (effortOrder[a.effort] || 1) - (effortOrder[b.effort] || 1));
  } else if (sortKey === "file_count") {
    sorted.sort((a, b) => (b.files ? b.files.length : 0) - (a.files ? a.files.length : 0));
  }

  return sorted;
}

/**
 * Get color for severity level
 */
function getSeverityColor(severity) {
  const colors = {
    critical: 'var(--red)',
    high: 'var(--orange)',
    medium: 'var(--yellow)',
    low: 'var(--green)',
    info: 'var(--blue)',
  };
  return colors[severity] || 'var(--text-tertiary)';
}
