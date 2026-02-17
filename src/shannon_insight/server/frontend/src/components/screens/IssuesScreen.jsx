/**
 * IssuesScreen — Code quality findings with three views.
 *
 * Information Architecture
 * ────────────────────────
 * TOP    Severity summary bar — always visible, tells the full story at a glance
 * MID    Concern health cards — higher-level health areas (from data.concerns)
 * MAIN   Three view modes (toggle):
 *          • By Category  — incomplete / fragile / tangled / team
 *          • By Severity  — critical → info, collapsible groups
 *          • By Concern   — grouped under each codebase health area
 * BOTTOM Sort + filter controls (tools come after insights)
 *
 * Data Access
 * ───────────
 * All findings come from `data.categories` (canonical source).
 * Concern groupings come from `data.concerns` (each concern now includes its findings).
 * The `useIssuesData()` hook encapsulates all derivations so components stay dumb.
 *
 * Severity scale (0–1 float):
 *   >= 0.9 → critical  | >= 0.8 → high | >= 0.6 → medium | >= 0.4 → low | < 0.4 → info
 */

import { useState, useMemo } from "preact/hooks";
import useStore from "../../state/store.js";
import { FindingCard } from "../cards/FindingCard.jsx";
import {
  CATEGORY_ORDER,
  CATEGORY_LABELS,
  CATEGORY_DESCRIPTIONS,
  SEVERITY_LEVELS,
} from "../../utils/constants.js";
import { sevKey } from "../../utils/helpers.js";

// ─────────────────────────────────────────────────────────────────────────────
// SELECTORS — single place where field names are defined
// (Prevents scattered field-name bugs across components)
// ─────────────────────────────────────────────────────────────────────────────

/** Canonical field accessor for finding type. */
const getFindingType = (f) => f.finding_type ?? f.type ?? "unknown";

/** Severity level string from 0–1 float. */
const getSeverityLevel = (severity) => sevKey(severity);

/** Severity color from level string. */
const SEVERITY_COLORS = {
  critical: "var(--red)",
  high:     "var(--orange)",
  medium:   "var(--yellow)",
  low:      "var(--green)",
  info:     "var(--blue)",
};
const getSeverityColor = (level) => SEVERITY_COLORS[level] ?? "var(--text-tertiary)";

/** Concern status color. */
const CONCERN_STATUS_COLORS = {
  good:      "var(--green)",
  warning:   "var(--yellow)",
  critical:  "var(--red)",
  improving: "var(--blue)",
  declining: "var(--orange)",
};
const getConcernStatusColor = (status) =>
  CONCERN_STATUS_COLORS[status] ?? "var(--text-tertiary)";

/** Health score (1–10) to color. */
const getHealthColor = (score) => {
  if (score >= 8) return "var(--green)";
  if (score >= 6) return "var(--yellow)";
  if (score >= 4) return "var(--orange)";
  return "var(--red)";
};

// ─────────────────────────────────────────────────────────────────────────────
// HOOK — useIssuesData
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Derives all IssuesScreen state from the store in one place.
 * Components subscribe only to the shape they need.
 */
function useIssuesData() {
  const data = useStore((s) => s.data);
  const issueSortKey = useStore((s) => s.issueSortKey);
  const issueSeverityFilter = useStore((s) => s.issueSeverityFilter);

  const allFindings = useMemo(() => {
    if (!data?.categories) return [];
    return CATEGORY_ORDER.flatMap((cat) =>
      (data.categories[cat]?.findings ?? []).map((f) => ({
        ...f,
        category: cat,
        finding_type: getFindingType(f),
        severityLevel: getSeverityLevel(f.severity),
      }))
    );
  }, [data?.categories]);

  const filteredFindings = useMemo(
    () => allFindings.filter((f) => issueSeverityFilter.has(f.severityLevel)),
    [allFindings, issueSeverityFilter]
  );

  const sortedFindings = useMemo(
    () => sortFindings(filteredFindings, issueSortKey),
    [filteredFindings, issueSortKey]
  );

  const severityCounts = useMemo(
    () => ({
      critical: allFindings.filter((f) => f.severityLevel === "critical").length,
      high:     allFindings.filter((f) => f.severityLevel === "high").length,
      medium:   allFindings.filter((f) => f.severityLevel === "medium").length,
      low:      allFindings.filter((f) => f.severityLevel === "low").length,
      info:     allFindings.filter((f) => f.severityLevel === "info").length,
    }),
    [allFindings]
  );

  const chronicSet = useMemo(
    () =>
      new Set(
        (data?.trends?.chronic ?? []).map(
          (c) => c.finding_type ?? c.identity_key
        )
      ),
    [data?.trends?.chronic]
  );

  const concerns = useMemo(() => data?.concerns ?? [], [data?.concerns]);
  const categories = useMemo(() => data?.categories ?? {}, [data?.categories]);

  return {
    allFindings,
    sortedFindings,
    filteredFindings,
    severityCounts,
    chronicSet,
    concerns,
    categories,
    total: allFindings.length,
  };
}

// ─────────────────────────────────────────────────────────────────────────────
// MAIN COMPONENT
// ─────────────────────────────────────────────────────────────────────────────

const VIEWS = ["category", "severity", "concern"];
const VIEW_LABELS = { category: "By Category", severity: "By Severity", concern: "By Concern" };

export function IssuesScreen() {
  const data = useStore((s) => s.data);
  const issueSortKey = useStore((s) => s.issueSortKey);
  const issueSeverityFilter = useStore((s) => s.issueSeverityFilter);
  const setIssueSortKey = useStore((s) => s.setIssueSortKey);
  const toggleIssueSeverity = useStore((s) => s.toggleIssueSeverity);
  const [activeView, setActiveView] = useState("category");

  const issues = useIssuesData();

  if (!data) return null;

  if (issues.total === 0) {
    return (
      <div style={{ padding: "var(--space-16)", textAlign: "center" }}>
        <div className="text-h3" style={{ color: "var(--green)", marginBottom: "var(--space-2)" }}>
          No issues found
        </div>
        <div className="text-body" style={{ color: "var(--text-tertiary)" }}>
          Your codebase looks healthy. Run with <code>--save</code> to track trends over time.
        </div>
      </div>
    );
  }

  return (
    <div className="stack stack--2xl">

      {/* ── 1. SEVERITY SUMMARY — always visible, full picture ─── */}
      <SeveritySummaryBar counts={issues.severityCounts} total={issues.total} />

      {/* ── 2. CONCERN HEALTH CARDS — higher-level areas ───────── */}
      {issues.concerns.length > 0 && (
        <ConcernHealthCards concerns={issues.concerns} />
      )}

      {/* ── 3. VIEW SWITCHER + FINDINGS ────────────────────────── */}
      <div className="stack stack--lg">
        <ViewSwitcher active={activeView} onChange={setActiveView} />

        {activeView === "category" && (
          <CategoryView
            categories={issues.categories}
            chronicSet={issues.chronicSet}
            sortKey={issueSortKey}
            severityFilter={issueSeverityFilter}
          />
        )}

        {activeView === "severity" && (
          <SeverityView
            findings={issues.sortedFindings}
            chronicSet={issues.chronicSet}
          />
        )}

        {activeView === "concern" && (
          <ConcernView
            concerns={issues.concerns}
            chronicSet={issues.chronicSet}
            sortKey={issueSortKey}
          />
        )}
      </div>

      {/* ── 4. FILTER + SORT CONTROLS — tools below insights ───── */}
      <SortFilterBar
        sortKey={issueSortKey}
        setSortKey={setIssueSortKey}
        severityFilter={issueSeverityFilter}
        toggleSeverity={toggleIssueSeverity}
      />

    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// SEVERITY SUMMARY BAR
// ─────────────────────────────────────────────────────────────────────────────

function SeveritySummaryBar({ counts, total }) {
  if (total === 0) return null;

  const segments = SEVERITY_LEVELS.map((level) => ({
    level,
    label: level.toUpperCase(),
    color: getSeverityColor(level),
    count: counts[level] ?? 0,
  })).filter((s) => s.count > 0);

  return (
    <div className="ds-card ds-card--compact">
      <div className="ds-card__body">
        <div className="cluster cluster--md" style={{ alignItems: "center", flexWrap: "wrap" }}>
          {/* Proportional bar */}
          <div
            style={{
              flex: "1 1 200px",
              display: "flex",
              height: "8px",
              borderRadius: "4px",
              overflow: "hidden",
              gap: "2px",
              minWidth: "100px",
            }}
          >
            {segments.map((seg) => (
              <div
                key={seg.level}
                title={`${seg.label}: ${seg.count}`}
                style={{
                  flex: `0 0 ${(seg.count / total) * 100}%`,
                  background: seg.color,
                  borderRadius: "2px",
                  minWidth: "4px",
                }}
              />
            ))}
          </div>

          {/* Counts */}
          <div className="cluster cluster--md" style={{ flexWrap: "wrap" }}>
            {segments.map((seg) => (
              <span key={seg.level} className="text-body-sm" style={{ display: "flex", alignItems: "center", gap: "var(--space-1)" }}>
                <span
                  style={{
                    display: "inline-block",
                    width: "8px",
                    height: "8px",
                    borderRadius: "2px",
                    background: seg.color,
                    flexShrink: 0,
                  }}
                />
                <span style={{ color: seg.color, fontWeight: 700, fontFamily: "var(--font-mono)" }}>
                  {seg.count}
                </span>
                <span style={{ color: "var(--text-tertiary)" }}>{seg.label}</span>
              </span>
            ))}
            <span className="text-body-sm" style={{ color: "var(--text-tertiary)" }}>
              · {total} total
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// CONCERN HEALTH CARDS
// ─────────────────────────────────────────────────────────────────────────────

function ConcernHealthCards({ concerns }) {
  return (
    <div>
      <div className="text-label" style={{ marginBottom: "var(--space-3)", color: "var(--text-tertiary)" }}>
        HEALTH AREAS
      </div>
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))",
          gap: "var(--space-3)",
        }}
      >
        {concerns.map((concern) => (
          <ConcernHealthCard key={concern.key} concern={concern} />
        ))}
      </div>
    </div>
  );
}

function ConcernHealthCard({ concern }) {
  const scoreColor = getHealthColor(concern.score);
  const statusColor = getConcernStatusColor(concern.status);

  return (
    <div
      className="ds-card ds-card--compact"
      style={{ borderLeft: `3px solid ${scoreColor}` }}
      title={concern.description}
    >
      <div className="ds-card__body">
        <div className="stack stack--xs">
          <div className="cluster cluster--md" style={{ justifyContent: "space-between", alignItems: "flex-start" }}>
            <div className="text-body-sm" style={{ fontWeight: 600, color: "var(--text)" }}>
              {concern.name}
            </div>
            <div
              className="text-mono"
              style={{ fontSize: "var(--text-lg)", fontWeight: 700, color: scoreColor, lineHeight: 1 }}
            >
              {concern.score.toFixed(1)}
            </div>
          </div>
          <div className="cluster cluster--sm" style={{ alignItems: "center" }}>
            <span
              className="text-label"
              style={{ color: statusColor, fontSize: "var(--text-2xs)" }}
            >
              {concern.status?.toUpperCase() ?? "—"}
            </span>
            {concern.finding_count > 0 && (
              <span className="text-body-sm" style={{ color: "var(--text-tertiary)" }}>
                · {concern.finding_count} {concern.finding_count === 1 ? "issue" : "issues"}
              </span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// VIEW SWITCHER
// ─────────────────────────────────────────────────────────────────────────────

function ViewSwitcher({ active, onChange }) {
  return (
    <div
      style={{
        display: "inline-flex",
        background: "var(--surface)",
        border: "1px solid var(--border)",
        borderRadius: "var(--radius-md)",
        padding: "2px",
        gap: "2px",
      }}
    >
      {VIEWS.map((v) => (
        <button
          key={v}
          onClick={() => onChange(v)}
          style={{
            padding: "var(--space-2) var(--space-4)",
            background: active === v ? "var(--accent)" : "transparent",
            border: "none",
            borderRadius: "var(--radius-sm)",
            color: active === v ? "var(--bg)" : "var(--text-secondary)",
            fontSize: "var(--text-sm)",
            fontWeight: active === v ? 700 : 500,
            cursor: "pointer",
            transition: "all var(--transition-base)",
            whiteSpace: "nowrap",
          }}
        >
          {VIEW_LABELS[v]}
        </button>
      ))}
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// VIEW: BY CATEGORY
// ─────────────────────────────────────────────────────────────────────────────

function CategoryView({ categories, chronicSet, sortKey, severityFilter }) {
  const [activeTab, setActiveTab] = useState(CATEGORY_ORDER[0]);
  const cat = categories[activeTab];

  const findings = useMemo(() => {
    const raw = cat?.findings ?? [];
    const filtered = raw.filter((f) => severityFilter.has(sevKey(f.severity)));
    return sortFindings(filtered, sortKey);
  }, [cat, sortKey, severityFilter]);

  return (
    <div className="stack stack--md">
      {/* Category tabs with counts */}
      <div style={{ display: "flex", gap: "var(--space-2)", flexWrap: "wrap" }}>
        {CATEGORY_ORDER.map((key) => {
          const c = categories[key];
          const count = c?.count ?? 0;
          const highCount = c?.high_count ?? 0;
          const isActive = activeTab === key;

          return (
            <button
              key={key}
              onClick={() => setActiveTab(key)}
              style={{
                padding: "var(--space-3) var(--space-4)",
                background: isActive ? "var(--surface)" : "transparent",
                border: isActive ? "1px solid var(--border)" : "1px solid transparent",
                borderBottom: isActive ? "2px solid var(--accent)" : "2px solid transparent",
                borderRadius: "var(--radius-sm) var(--radius-sm) 0 0",
                color: isActive ? "var(--text)" : "var(--text-secondary)",
                fontSize: "var(--text-sm)",
                fontWeight: isActive ? 600 : 400,
                cursor: "pointer",
                transition: "all var(--transition-base)",
                display: "flex",
                alignItems: "center",
                gap: "var(--space-2)",
              }}
            >
              <span>{CATEGORY_LABELS[key]}</span>
              {count > 0 && (
                <span
                  className="text-mono"
                  style={{
                    padding: "1px 6px",
                    background: highCount > 0 ? "var(--orange)" : "var(--surface-raised)",
                    color: highCount > 0 ? "var(--bg)" : "var(--text-secondary)",
                    borderRadius: "10px",
                    fontSize: "var(--text-xs)",
                    fontWeight: 700,
                  }}
                >
                  {count}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* Tab panel */}
      <div className="ds-card" style={{ borderTopLeftRadius: 0 }}>
        <div className="ds-card__body">
          {findings.length === 0 ? (
            <EmptyFindings
              message={
                (cat?.count ?? 0) === 0
                  ? `No ${CATEGORY_LABELS[activeTab]} issues found`
                  : "No issues match current filters"
              }
            />
          ) : (
            <div className="stack stack--md">
              <CategoryDescription category={activeTab} />
              {findings.map((f, i) => (
                <FindingCard
                  key={i}
                  finding={f}
                  showFiles
                  chronicSet={chronicSet}
                  maxEvidence={4}
                />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function CategoryDescription({ category }) {
  const desc = CATEGORY_DESCRIPTIONS[category];
  if (!desc) return null;
  return (
    <div
      className="text-body-sm"
      style={{ color: "var(--text-tertiary)", paddingBottom: "var(--space-3)", borderBottom: "1px solid var(--border)" }}
    >
      {desc}
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// VIEW: BY SEVERITY
// ─────────────────────────────────────────────────────────────────────────────

function SeverityView({ findings, chronicSet }) {
  const groups = useMemo(() => {
    const grouped = {};
    for (const level of SEVERITY_LEVELS) {
      grouped[level] = findings.filter((f) => f.severityLevel === level);
    }
    return grouped;
  }, [findings]);

  const [expanded, setExpanded] = useState({ critical: true, high: true, medium: false, low: false, info: false });
  const toggle = (level) => setExpanded((prev) => ({ ...prev, [level]: !prev[level] }));

  const GROUP_LABELS = {
    critical: "Critical",
    high:     "High Priority",
    medium:   "Medium Priority",
    low:      "Low Priority",
    info:     "Informational",
  };

  return (
    <div className="stack stack--md">
      {SEVERITY_LEVELS.map((level) => {
        const group = groups[level];
        if (group.length === 0) return null;
        return (
          <SeverityGroup
            key={level}
            level={level}
            label={GROUP_LABELS[level]}
            findings={group}
            chronicSet={chronicSet}
            isExpanded={expanded[level]}
            onToggle={() => toggle(level)}
          />
        );
      })}
    </div>
  );
}

function SeverityGroup({ level, label, findings, chronicSet, isExpanded, onToggle }) {
  const color = getSeverityColor(level);

  return (
    <div className="ds-card" style={{ borderLeft: `3px solid ${color}` }}>
      <button
        className="ds-card__header"
        onClick={onToggle}
        style={{
          width: "100%",
          background: "none",
          border: "none",
          cursor: "pointer",
          padding: "var(--space-4) var(--space-5)",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          borderBottom: isExpanded ? "1px solid var(--border)" : "none",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "var(--space-3)" }}>
          <span className="text-label" style={{ color, fontSize: "var(--text-xs)" }}>
            {label.toUpperCase()}
          </span>
          <span
            className="text-mono"
            style={{
              padding: "1px 7px",
              background: color,
              color: "var(--bg)",
              borderRadius: "10px",
              fontSize: "var(--text-xs)",
              fontWeight: 700,
            }}
          >
            {findings.length}
          </span>
        </div>
        <span style={{ color: "var(--text-tertiary)", fontSize: "var(--text-md)", lineHeight: 1 }}>
          {isExpanded ? "−" : "+"}
        </span>
      </button>

      {isExpanded && (
        <div className="ds-card__body">
          <div className="stack stack--md">
            {findings.map((f, i) => (
              <FindingCard
                key={i}
                finding={f}
                showFiles
                chronicSet={chronicSet}
                maxEvidence={4}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// VIEW: BY CONCERN
// ─────────────────────────────────────────────────────────────────────────────

function ConcernView({ concerns, chronicSet, sortKey }) {
  if (concerns.length === 0) {
    return (
      <EmptyFindings message="No concern data available. This requires git history analysis." />
    );
  }

  const [expandedKey, setExpandedKey] = useState(concerns[0]?.key ?? null);
  const toggle = (key) => setExpandedKey((prev) => (prev === key ? null : key));

  return (
    <div className="stack stack--md">
      {concerns.map((concern) => {
        const findings = sortFindings(concern.findings ?? [], sortKey);
        const isExpanded = expandedKey === concern.key;
        const scoreColor = getHealthColor(concern.score);

        return (
          <div
            key={concern.key}
            className="ds-card"
            style={{ borderLeft: `3px solid ${scoreColor}` }}
          >
            <button
              className="ds-card__header"
              onClick={() => toggle(concern.key)}
              style={{
                width: "100%",
                background: "none",
                border: "none",
                cursor: "pointer",
                padding: "var(--space-4) var(--space-5)",
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                borderBottom: isExpanded ? "1px solid var(--border)" : "none",
              }}
            >
              <div style={{ display: "flex", alignItems: "center", gap: "var(--space-4)", flex: 1 }}>
                {/* Health score badge */}
                <span
                  className="text-mono"
                  style={{
                    fontSize: "var(--text-xl)",
                    fontWeight: 700,
                    color: scoreColor,
                    minWidth: "2.5ch",
                    textAlign: "right",
                  }}
                >
                  {concern.score.toFixed(1)}
                </span>
                <div style={{ textAlign: "left" }}>
                  <div className="text-body" style={{ fontWeight: 600, color: "var(--text)" }}>
                    {concern.name}
                  </div>
                  <div className="text-body-sm" style={{ color: "var(--text-tertiary)" }}>
                    {concern.description}
                  </div>
                </div>
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: "var(--space-4)" }}>
                <div style={{ textAlign: "right" }}>
                  {concern.finding_count > 0 && (
                    <span
                      className="text-label"
                      style={{
                        padding: "1px 7px",
                        background: "var(--surface-raised)",
                        borderRadius: "10px",
                        fontSize: "var(--text-xs)",
                        color: "var(--text-secondary)",
                        fontWeight: 600,
                      }}
                    >
                      {concern.finding_count} {concern.finding_count === 1 ? "issue" : "issues"}
                    </span>
                  )}
                  {concern.file_count > 0 && (
                    <div className="text-body-sm" style={{ color: "var(--text-tertiary)", marginTop: "2px" }}>
                      {concern.file_count} files affected
                    </div>
                  )}
                </div>
                <span style={{ color: "var(--text-tertiary)", fontSize: "var(--text-md)" }}>
                  {isExpanded ? "−" : "+"}
                </span>
              </div>
            </button>

            {isExpanded && (
              <div className="ds-card__body">
                {findings.length === 0 ? (
                  <EmptyFindings message="No findings for this concern." />
                ) : (
                  <div className="stack stack--md">
                    {findings.map((f, i) => (
                      <FindingCard
                        key={i}
                        finding={f}
                        showFiles
                        chronicSet={chronicSet}
                        maxEvidence={4}
                      />
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// SORT + FILTER BAR
// ─────────────────────────────────────────────────────────────────────────────

function SortFilterBar({ sortKey, setSortKey, severityFilter, toggleSeverity }) {
  return (
    <div className="ds-card ds-card--compact">
      <div className="ds-card__body">
        <div className="cluster cluster--md" style={{ alignItems: "center", flexWrap: "wrap" }}>
          <div className="text-label" style={{ color: "var(--text-tertiary)", flexShrink: 0 }}>
            FILTER & SORT
          </div>

          {/* Sort */}
          <div className="cluster cluster--sm" style={{ alignItems: "center" }}>
            <span className="text-body-sm" style={{ color: "var(--text-secondary)" }}>Sort:</span>
            <select
              value={sortKey}
              onChange={(e) => setSortKey(e.target.value)}
              style={{
                padding: "var(--space-1) var(--space-3)",
                background: "var(--surface)",
                border: "1px solid var(--border)",
                borderRadius: "var(--radius-sm)",
                color: "var(--text)",
                fontSize: "var(--text-sm)",
                fontFamily: "var(--font-sans)",
              }}
            >
              <option value="severity_desc">Severity ↓</option>
              <option value="severity_asc">Severity ↑</option>
              <option value="effort_asc">Effort (low first)</option>
              <option value="file_count">Files affected</option>
            </select>
          </div>

          {/* Severity filter chips */}
          <div className="cluster cluster--xs">
            {SEVERITY_LEVELS.map((sl) => {
              const color = getSeverityColor(sl);
              const active = severityFilter.has(sl);
              return (
                <button
                  key={sl}
                  onClick={() => toggleSeverity(sl)}
                  style={{
                    padding: "2px var(--space-3)",
                    background: active ? color : "transparent",
                    border: `1px solid ${color}`,
                    borderRadius: "var(--radius-sm)",
                    color: active ? "var(--bg)" : color,
                    fontSize: "var(--text-xs)",
                    fontWeight: 700,
                    textTransform: "uppercase",
                    cursor: "pointer",
                    transition: "all var(--transition-base)",
                    letterSpacing: "0.04em",
                  }}
                >
                  {sl}
                </button>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// SHARED COMPONENTS
// ─────────────────────────────────────────────────────────────────────────────

function EmptyFindings({ message }) {
  return (
    <div
      style={{
        padding: "var(--space-10) var(--space-4)",
        textAlign: "center",
        color: "var(--text-tertiary)",
      }}
    >
      <div className="text-body-sm">{message}</div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// PURE HELPERS (no side effects, easily testable)
// ─────────────────────────────────────────────────────────────────────────────

function sortFindings(findings, sortKey) {
  const sorted = findings.slice();
  if (sortKey === "severity_desc") {
    sorted.sort((a, b) => b.severity - a.severity);
  } else if (sortKey === "severity_asc") {
    sorted.sort((a, b) => a.severity - b.severity);
  } else if (sortKey === "effort_asc") {
    const effortOrder = { LOW: 0, MEDIUM: 1, HIGH: 2 };
    sorted.sort((a, b) => (effortOrder[a.effort] ?? 1) - (effortOrder[b.effort] ?? 1));
  } else if (sortKey === "file_count") {
    sorted.sort((a, b) => (b.files?.length ?? 0) - (a.files?.length ?? 0));
  }
  return sorted;
}
