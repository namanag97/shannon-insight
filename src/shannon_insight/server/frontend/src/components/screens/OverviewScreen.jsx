/**
 * OverviewScreen - Redesigned with proper information architecture
 *
 * Information Priority:
 * 1. Hero - Health score + verdict (how healthy is my code?)
 * 2. Focus Point - Recommended action (what should I fix first?)
 * 3. Risk + Issues - Context (where is the risk? what's broken?)
 * 4. Metrics + Categories - Supporting data
 * 5. Evolution - Historical context (collapsible)
 *
 * Design System:
 * - 12-column grid with proper gutters
 * - Mathematical spacing (8px baseline)
 * - Clear visual hierarchy
 * - Every component intentionally placed
 */

import useStore from "../../state/store.js";
import { fmtN, fmtF } from "../../utils/formatters.js";
import { hColor } from "../../utils/helpers.js";
import { CATEGORY_ORDER, CATEGORY_LABELS, SEVERITY_MAP } from "../../utils/constants.js";
import { interpretHealth } from "../../utils/interpretations.js";
import { RiskHistogram } from "../charts/RiskHistogram.jsx";
import { TrendChart } from "../charts/TrendChart.jsx";
import { SeverityDot } from "../ui/SeverityDot.jsx";

export function OverviewScreen() {
  const data = useStore((s) => s.data);
  if (!data) return null;

  const score = data.health;
  const color = hColor(score);
  const healthInfo = interpretHealth(score);
  const cats = data.categories || {};

  // Calculate total issues
  let totalIssues = 0;
  for (const k in cats) totalIssues += cats[k].count;

  // Get top 5 critical findings across all categories
  const topFindings = getTopFindings(cats, 5);

  // Navigation handlers
  function goToIssues(catKey) {
    location.hash = "issues";
    useStore.getState().setIssueTab(catKey);
  }

  function goToFile(path) {
    location.hash = "files/" + encodeURIComponent(path);
  }

  return (
    <div className="stack stack--2xl">
      {/* ══════════════════════════════════════════════════════════
          PRIORITY 1: HERO - Health Score + Verdict
          Answer: "How healthy is my codebase?"
          ══════════════════════════════════════════════════════════ */}
      <section>
        <div className="grid">
          <div className="span-12">
            <div className="priority-hero" style={{ background: 'var(--surface)', borderRadius: 'var(--radius-lg)' }}>
              {data.verdict && (
                <div className="text-label" style={{ color: color, marginBottom: 'var(--space-2)' }}>
                  {data.verdict.toUpperCase()}
                </div>
              )}
              <div className="text-display text-mono" style={{ color }}>
                {score.toFixed(1)}
              </div>
              <div className="text-h3 mt-2" style={{ color }}>
                {healthInfo.label}
              </div>
              <p className="text-body-sm" style={{ color: 'var(--text-secondary)', marginTop: 'var(--space-2)', maxWidth: '480px', marginLeft: 'auto', marginRight: 'auto' }}>
                {healthInfo.description}
              </p>
              {data.trend && (
                <div className="text-label" style={{ marginTop: 'var(--space-4)', color: data.trend > 0 ? 'var(--green)' : 'var(--red)' }}>
                  {data.trend > 0 ? '↑' : '↓'} {Math.abs(data.trend).toFixed(1)} points since last analysis
                </div>
              )}
            </div>
          </div>
        </div>
      </section>

      {/* ══════════════════════════════════════════════════════════
          PRIORITY 2: FOCUS POINT - Recommended Starting Point
          Answer: "What should I fix first?"
          ══════════════════════════════════════════════════════════ */}
      {data.focus && (
        <section>
          <div className="grid">
            <div className="span-12">
              <div className="priority-primary">
                <div className="text-h4" style={{ marginBottom: 'var(--space-4)' }}>
                  🎯 RECOMMENDED STARTING POINT
                </div>
                <FocusPoint focus={data.focus} onFileClick={goToFile} />
              </div>
            </div>
          </div>
        </section>
      )}

      {/* ══════════════════════════════════════════════════════════
          PRIORITY 3: RISK + CRITICAL ISSUES
          Answer: "Where is the risk? What are the worst problems?"
          ══════════════════════════════════════════════════════════ */}
      <section>
        <div className="grid">
          {/* 3a. Risk Distribution */}
          <div className="span-6">
            <div className="ds-card">
              <div className="ds-card__header">
                <div className="ds-card__title">Risk Distribution</div>
              </div>
              <div className="ds-card__body">
                <RiskHistogram files={data.files} />
              </div>
            </div>
          </div>

          {/* 3b. Top Critical Issues */}
          <div className="span-6">
            <div className="ds-card">
              <div className="ds-card__header">
                <div className="ds-card__title">Top Critical Issues</div>
              </div>
              <div className="ds-card__body">
                {topFindings.length === 0 ? (
                  <div className="text-body-sm" style={{ color: 'var(--text-tertiary)', padding: 'var(--space-4) 0' }}>
                    No critical issues found
                  </div>
                ) : (
                  <div className="stack stack--md">
                    {topFindings.map((finding, i) => (
                      <CriticalFindingRow key={i} finding={finding} onClick={() => goToIssues(finding.category)} />
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ══════════════════════════════════════════════════════════
          PRIORITY 4: KEY METRICS + CATEGORY BREAKDOWN
          Answer: "How big is the codebase? What types of issues exist?"
          ══════════════════════════════════════════════════════════ */}
      <section>
        <div className="grid">
          {/* 4a. Key Metrics */}
          <div className="span-6">
            <div className="ds-card">
              <div className="ds-card__header">
                <div className="ds-card__title">Key Metrics</div>
              </div>
              <div className="ds-card__body">
                <div className="grid grid--compact">
                  <div className="span-6">
                    <MetricItem value={fmtN(data.file_count)} label="Files Analyzed" />
                  </div>
                  <div className="span-6">
                    <MetricItem value={fmtN(data.module_count)} label="Modules" />
                  </div>
                  <div className="span-6">
                    <MetricItem value={fmtN(data.commits_analyzed)} label="Commits" />
                  </div>
                  <div className="span-6">
                    <MetricItem
                      value={fmtN(totalIssues)}
                      label="Issues Found"
                      color={totalIssues > 0 ? 'var(--orange)' : undefined}
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* 4b. Category Breakdown */}
          <div className="span-6">
            <div className="ds-card">
              <div className="ds-card__header">
                <div className="ds-card__title">Issues by Category</div>
              </div>
              <div className="ds-card__body">
                <CategoryBreakdown categories={cats} onClick={goToIssues} />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ══════════════════════════════════════════════════════════
          PRIORITY 5: SUPPORTING DATA (Evolution + Metadata)
          Collapsible section - low priority
          ══════════════════════════════════════════════════════════ */}
      {(data.evolution || data.metadata) && (
        <CollapsibleSection title="Evolution & Metadata" defaultOpen={false}>
          <div className="grid">
            {/* Evolution Charts */}
            {data.evolution && (
              <div className="span-6">
                <div className="ds-card">
                  <div className="ds-card__header">
                    <div className="ds-card__title">Codebase Evolution</div>
                  </div>
                  <div className="ds-card__body">
                    <EvolutionCharts evolution={data.evolution} />
                  </div>
                </div>
              </div>
            )}

            {/* Metadata */}
            {data.metadata && (
              <div className="span-6">
                <div className="ds-card">
                  <div className="ds-card__header">
                    <div className="ds-card__title">Analysis Metadata</div>
                  </div>
                  <div className="ds-card__body">
                    <MetadataGrid metadata={data.metadata} />
                  </div>
                </div>
              </div>
            )}
          </div>
        </CollapsibleSection>
      )}
    </div>
  );
}


/* ═══════════════════════════════════════════════════════════════════════════
   SUB-COMPONENTS
   ═══════════════════════════════════════════════════════════════════════════ */

/**
 * Focus Point v2 - Redesigned with clear hierarchy
 *
 * API sends: { path, why, risk_score, impact_score, tractability_score, confidence_score, findings, alternatives }
 */
function FocusPoint({ focus, onFileClick }) {
  if (!focus || !focus.path) {
    return (
      <div className="text-body-sm" style={{ color: 'var(--text-tertiary)' }}>
        No specific recommendations at this time.
      </div>
    );
  }

  return (
    <div className="stack stack--md">
      {/* File path - clickable */}
      <div>
        <a
          href={`#files/${encodeURIComponent(focus.path)}`}
          className="text-lg text-mono"
          style={{ color: 'var(--accent)', textDecoration: 'none', fontWeight: 500 }}
          onClick={(e) => {
            e.preventDefault();
            if (onFileClick) onFileClick(focus.path);
          }}
        >
          {focus.path}
        </a>
      </div>

      {/* Why this file? */}
      {focus.why && (
        <div className="text-body" style={{ color: 'var(--text-secondary)' }}>
          {focus.why}
        </div>
      )}

      {/* Key metrics - direct fields from API, not nested in signals */}
      <div className="cluster cluster--md">
        {focus.risk_score != null && (
          <MetricBadge label="Risk" value={fmtF(focus.risk_score, 2)} color="var(--red)" />
        )}
        {focus.impact_score != null && (
          <MetricBadge label="Impact" value={fmtF(focus.impact_score, 2)} color="var(--orange)" />
        )}
        {focus.tractability_score != null && (
          <MetricBadge label="Fixability" value={fmtF(focus.tractability_score, 2)} color="var(--green)" />
        )}
        {focus.findings && focus.findings.length > 0 && (
          <MetricBadge label="Issues" value={focus.findings.length} color="var(--accent)" />
        )}
      </div>

      {/* Findings in this file */}
      {focus.findings && focus.findings.length > 0 && (
        <div className="stack stack--sm" style={{ marginTop: 'var(--space-2)' }}>
          <div className="text-label">FINDINGS IN THIS FILE:</div>
          {focus.findings.slice(0, 3).map((f, i) => (
            <div key={i} className="text-body-sm" style={{ color: 'var(--text-secondary)', paddingLeft: 'var(--space-4)', borderLeft: `2px solid ${hColor(10 - f.severity * 10)}` }}>
              {f.label || f.finding_type || f.type}
            </div>
          ))}
          {focus.findings.length > 3 && (
            <div className="text-label" style={{ paddingLeft: 'var(--space-4)' }}>
              +{focus.findings.length - 3} more
            </div>
          )}
        </div>
      )}
    </div>
  );
}

/**
 * Critical Finding Row - Compact display for top issues
 */
function CriticalFindingRow({ finding, onClick }) {
  const severity = finding.severity || 5;
  const sevColor = hColor(10 - severity);

  return (
    <div
      className="stack stack--xs"
      style={{
        padding: 'var(--space-3)',
        borderLeft: `3px solid ${sevColor}`,
        background: 'rgba(255,255,255,0.02)',
        borderRadius: 'var(--radius-sm)',
        cursor: 'pointer',
        transition: 'background var(--transition-base)'
      }}
      onClick={onClick}
      onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(255,255,255,0.04)'}
      onMouseLeave={(e) => e.currentTarget.style.background = 'rgba(255,255,255,0.02)'}
    >
      <div className="text-body" style={{ fontWeight: 500, color: 'var(--text)' }}>
        {finding.finding_type || finding.type}
      </div>
      {finding.files && finding.files.length > 0 && (
        <div className="text-body-sm text-mono" style={{ color: 'var(--text-secondary)' }}>
          {finding.files.length === 1
            ? finding.files[0]
            : `${finding.files.length} files affected`}
        </div>
      )}
      {finding.evidence && (
        <div className="text-label" style={{ color: 'var(--text-tertiary)' }}>
          {truncateEvidence(finding.evidence)}
        </div>
      )}
    </div>
  );
}

/**
 * Metric Item - Display for key metrics
 */
function MetricItem({ value, label, color }) {
  return (
    <div className="text-center" style={{ padding: 'var(--space-3)' }}>
      <div className="text-2xl text-mono" style={{ color: color || 'var(--text)' }}>
        {value}
      </div>
      <div className="text-label" style={{ marginTop: 'var(--space-1)' }}>
        {label}
      </div>
    </div>
  );
}

/**
 * Metric Badge - Small metric display with label
 */
function MetricBadge({ label, value, color }) {
  return (
    <div
      className="text-body-sm"
      style={{
        padding: 'var(--space-2) var(--space-3)',
        background: 'rgba(255,255,255,0.04)',
        border: '1px solid var(--border)',
        borderRadius: 'var(--radius-sm)',
        whiteSpace: 'nowrap'
      }}
    >
      <span style={{ color: 'var(--text-tertiary)', fontSize: 'var(--text-xs)' }}>{label}:</span>{' '}
      <span className="text-mono" style={{ color: color || 'var(--text)', fontWeight: 500 }}>{value}</span>
    </div>
  );
}

/**
 * Category Breakdown v2 - Simplified bar chart
 */
function CategoryBreakdown({ categories, onClick }) {
  const maxCount = Math.max(...CATEGORY_ORDER.map(k => categories[k]?.count || 0), 1);

  return (
    <div className="stack stack--sm">
      {CATEGORY_ORDER.map((key) => {
        const cat = categories[key];
        if (!cat || cat.count === 0) return null;

        const percent = (cat.count / maxCount) * 100;
        const catColor = hColor(10 - (cat.severity_avg || 5));

        return (
          <div
            key={key}
            className="cluster cluster--sm"
            style={{
              padding: 'var(--space-2) 0',
              cursor: 'pointer',
              transition: 'padding-left var(--transition-base)'
            }}
            onClick={() => onClick(key)}
            onMouseEnter={(e) => e.currentTarget.style.paddingLeft = 'var(--space-2)'}
            onMouseLeave={(e) => e.currentTarget.style.paddingLeft = '0'}
          >
            <div className="text-body-sm" style={{ minWidth: '120px', color: 'var(--text)' }}>
              {CATEGORY_LABELS[key] || key}
            </div>
            <div style={{ flex: 1, height: '6px', background: 'var(--border)', borderRadius: '3px', overflow: 'hidden' }}>
              <div style={{ width: `${percent}%`, height: '100%', background: catColor, transition: 'width var(--transition-slow)' }} />
            </div>
            <div className="text-body-sm text-mono" style={{ minWidth: '32px', textAlign: 'right', color: 'var(--text)', fontWeight: 500 }}>
              {cat.count}
            </div>
          </div>
        );
      })}
    </div>
  );
}

/**
 * Evolution Charts - Compact grid of trend charts
 */
function EvolutionCharts({ evolution }) {
  const charts = [
    { key: 'file_count', label: 'Files', color: 'var(--blue)', format: (v) => Math.round(v).toString() },
    { key: 'total_loc', label: 'Lines of Code', color: 'var(--green)', format: (v) => (v / 1000).toFixed(1) + 'k' },
    { key: 'avg_complexity', label: 'Avg Complexity', color: 'var(--orange)', format: (v) => v.toFixed(1) },
    { key: 'avg_risk', label: 'Avg Risk', color: 'var(--red)', format: (v) => v.toFixed(3) },
  ];

  return (
    <div className="grid grid--compact">
      {charts.map(({ key, label, color, format }) => {
        const data = evolution[key];
        if (!data || data.length < 2) return null;

        return (
          <div key={key} className="span-6">
            <div className="stack stack--xs">
              <TrendChart
                values={data.map((d) => d.value)}
                xLabels={data.map((d) => new Date(d.timestamp).toLocaleDateString(undefined, { month: 'short', day: 'numeric' }))}
                color={color}
                yFormat={format}
                width={240}
                height={100}
              />
              <div className="text-label text-center">{label}</div>
            </div>
          </div>
        );
      })}
    </div>
  );
}

/**
 * Metadata Grid - Key metadata in grid
 */
function MetadataGrid({ metadata }) {
  const items = [
    { label: 'Files Scanned', value: fmtN(metadata.files_scanned) },
    { label: 'Modules', value: fmtN(metadata.modules_detected) },
    { label: 'Commits', value: fmtN(metadata.commits_processed) },
    { label: 'Snapshots', value: metadata.snapshot_count },
    { label: 'DB Size', value: `${metadata.db_size_mb.toFixed(1)} MB` },
    { label: 'Analyzers', value: metadata.analyzers_ran?.length || 0 },
  ];

  return (
    <div className="stack stack--md">
      <div className="grid grid--dense">
        {items.map(({ label, value }) => (
          <div key={label} className="span-6">
            <MetricItem value={value} label={label} />
          </div>
        ))}
      </div>
      {metadata.analyzers_ran && metadata.analyzers_ran.length > 0 && (
        <div className="stack stack--xs" style={{ paddingTop: 'var(--space-4)', borderTop: '1px solid var(--border)' }}>
          <div className="text-label">ANALYZERS RAN:</div>
          <div className="cluster cluster--xs">
            {metadata.analyzers_ran.map((a) => (
              <span
                key={a}
                className="text-xs text-mono"
                style={{
                  padding: 'var(--space-1) var(--space-2)',
                  background: 'rgba(59, 130, 246, 0.08)',
                  color: 'var(--accent)',
                  borderRadius: 'var(--radius-sm)',
                  border: '1px solid rgba(59, 130, 246, 0.15)'
                }}
              >
                {a}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

/**
 * Collapsible Section - For low-priority content
 */
function CollapsibleSection({ title, children, defaultOpen = false }) {
  const [isOpen, setIsOpen] = React.useState(defaultOpen);

  return (
    <section>
      <div
        className="text-h4"
        style={{
          cursor: 'pointer',
          padding: 'var(--space-4)',
          background: 'var(--surface)',
          borderRadius: 'var(--radius-md)',
          border: '1px solid var(--border)',
          userSelect: 'none',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between'
        }}
        onClick={() => setIsOpen(!isOpen)}
      >
        <span>{title}</span>
        <span style={{ color: 'var(--text-tertiary)', fontFamily: 'var(--font-mono)', fontSize: '14px' }}>
          {isOpen ? '−' : '+'}
        </span>
      </div>
      {isOpen && (
        <div style={{ marginTop: 'var(--space-6)' }}>
          {children}
        </div>
      )}
    </section>
  );
}


/* ═══════════════════════════════════════════════════════════════════════════
   HELPERS
   ═══════════════════════════════════════════════════════════════════════════ */

/**
 * Get top N findings across all categories, sorted by severity
 */
function getTopFindings(categories, limit = 5) {
  const allFindings = [];

  for (const catKey in categories) {
    const cat = categories[catKey];
    if (cat.findings && cat.findings.length > 0) {
      cat.findings.forEach(f => {
        allFindings.push({ ...f, category: catKey });
      });
    }
  }

  // Sort by severity (highest first)
  allFindings.sort((a, b) => (b.severity || 0) - (a.severity || 0));

  return allFindings.slice(0, limit);
}

/**
 * Truncate evidence string for compact display
 */
function truncateEvidence(evidence) {
  if (typeof evidence !== 'string') {
    return JSON.stringify(evidence).substring(0, 60) + '...';
  }
  return evidence.length > 60 ? evidence.substring(0, 60) + '...' : evidence;
}

// Import React for useState in CollapsibleSection
import React from 'preact/compat';
