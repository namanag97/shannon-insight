/**
 * Issues screen - tabbed category view with severity filtering and sorting.
 */

import useStore from "../../state/store.js";
import { FindingCard } from "../cards/FindingCard.jsx";
import { CATEGORY_ORDER, CATEGORY_LABELS, SEVERITY_LEVELS } from "../../utils/constants.js";
import { sevKey } from "../../utils/helpers.js";

export function IssuesScreen() {
  const data = useStore((s) => s.data);
  const issueTab = useStore((s) => s.issueTab);
  const issueSortKey = useStore((s) => s.issueSortKey);
  const issueSeverityFilter = useStore((s) => s.issueSeverityFilter);
  const setIssueTab = useStore((s) => s.setIssueTab);
  const setIssueSortKey = useStore((s) => s.setIssueSortKey);
  const toggleIssueSeverity = useStore((s) => s.toggleIssueSeverity);

  if (!data) return null;

  const cats = data.categories || {};
  const activeTab = cats[issueTab] ? issueTab : CATEGORY_ORDER[0];

  // Get and filter findings
  const cat = cats[activeTab];
  let findings = cat && cat.count > 0 ? (cat.findings || []).slice() : [];

  // Filter by severity
  findings = findings.filter((f) => issueSeverityFilter.has(sevKey(f.severity)));

  // Sort
  const chronicSet =
    data.trends && data.trends.chronic
      ? new Set(data.trends.chronic.map((c) => c.finding_type || c.identity_key))
      : new Set();

  if (issueSortKey === "severity_desc") {
    findings.sort((a, b) => b.severity - a.severity);
  } else if (issueSortKey === "severity_asc") {
    findings.sort((a, b) => a.severity - b.severity);
  } else if (issueSortKey === "effort_asc") {
    const eo = { LOW: 0, MEDIUM: 1, HIGH: 2 };
    findings.sort((a, b) => (eo[a.effort] || 1) - (eo[b.effort] || 1));
  } else if (issueSortKey === "file_count") {
    findings.sort((a, b) => (b.files ? b.files.length : 0) - (a.files ? a.files.length : 0));
  }

  return (
    <div>
      {/* Filter bar */}
      <div class="filter-bar">
        <select
          class="sort-select"
          value={issueSortKey}
          onChange={(e) => setIssueSortKey(e.target.value)}
        >
          <option value="severity_desc">Severity (high first)</option>
          <option value="severity_asc">Severity (low first)</option>
          <option value="effort_asc">Effort (low first)</option>
          <option value="file_count">File count</option>
        </select>

        {SEVERITY_LEVELS.map((sl) => (
          <button
            key={sl}
            class={`sev-filter${issueSeverityFilter.has(sl) ? " active" : ""}`}
            onClick={() => toggleIssueSeverity(sl)}
          >
            {sl.toUpperCase()}
          </button>
        ))}
      </div>

      {/* Tabs */}
      <div class="issue-tabs">
        {CATEGORY_ORDER.map((key) => {
          const c = cats[key];
          if (!c) return null;
          return (
            <button
              key={key}
              class={`issue-tab${activeTab === key ? " active" : ""}`}
              onClick={() => setIssueTab(key)}
            >
              {CATEGORY_LABELS[key] || key}
              <span class="issue-tab-count">{c.count}</span>
            </button>
          );
        })}
      </div>

      {/* Content */}
      {!cat || cat.count === 0 ? (
        <div class="empty-state">
          <div class="empty-state-title">
            No {CATEGORY_LABELS[activeTab] || activeTab} issues
          </div>
        </div>
      ) : findings.length === 0 ? (
        <div class="empty-state">
          <div class="empty-state-title">No issues match current filters</div>
        </div>
      ) : (
        <div>
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
      )}
    </div>
  );
}
