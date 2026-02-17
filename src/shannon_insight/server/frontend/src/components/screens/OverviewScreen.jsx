/**
 * OverviewScreen — the home dashboard.
 *
 * Information Architecture
 * ────────────────────────
 * 1. HERO         Health score + verdict + trend. The single number that matters.
 * 2. STATS STRIP  Files · Issues · Modules · Commits in one horizontal sweep.
 * 3. FOCUS POINT  The one file to fix first, with full rationale.
 * 4. CONCERN GRID Health areas — structural, temporal, team, architecture.
 * 5. ISSUES SPLIT Category breakdown (incomplete/fragile/tangled/team) left
 *                 + risk histogram right.
 * 6. EVOLUTION    (when history available) Trend charts, collapsed by default.
 *
 * Design
 * ──────
 * Precision-technical aesthetic. Monospace accents for numeric values.
 * Color maps health: green ≥ 8, yellow ≥ 6, orange ≥ 4, red < 4.
 * All data access goes through getter functions — no scattered field names.
 */

import { useState } from "preact/hooks";
import useStore from "../../state/store.js";
import { fmtN, fmtF } from "../../utils/formatters.js";
import { hColor } from "../../utils/helpers.js";
import { CATEGORY_ORDER, CATEGORY_LABELS } from "../../utils/constants.js";
import { interpretHealth } from "../../utils/interpretations.js";
import { RiskHistogram } from "../charts/RiskHistogram.jsx";
import { TrendChart } from "../charts/TrendChart.jsx";

// ─────────────────────────────────────────────────────────────────────────────
// DATA ACCESSORS — single place for all field name contracts
// ─────────────────────────────────────────────────────────────────────────────

const getHealth = (data) => data?.health ?? 5;
const getFileCount = (data) => data?.file_count ?? 0;
const getModuleCount = (data) => data?.module_count ?? 0;
const getCommits = (data) => data?.commits_analyzed ?? 0;
const getAnalyzedPath = (data) => data?.analyzed_path ?? "";
const getFocus = (data) => data?.focus ?? null;
const getConcerns = (data) => data?.concerns ?? [];
const getCategories = (data) => data?.categories ?? {};
const getTrend = (data) => data?.trend ?? null;
const getVerdict = (data) => data?.verdict ?? "";
const getGlobalSignals = (data) => data?.global_signals ?? {};
const getFiles = (data) => data?.files ?? {};

function getTotalIssues(cats) {
  return Object.values(cats).reduce((sum, c) => sum + (c?.count ?? 0), 0);
}

function getTopFindings(cats, limit = 5) {
  const all = [];
  for (const catKey of CATEGORY_ORDER) {
    const cat = cats[catKey];
    if (cat?.findings) {
      for (const f of cat.findings) {
        all.push({ ...f, category: catKey });
      }
    }
  }
  return all.sort((a, b) => (b.severity ?? 0) - (a.severity ?? 0)).slice(0, limit);
}

// ─────────────────────────────────────────────────────────────────────────────
// MAIN COMPONENT
// ─────────────────────────────────────────────────────────────────────────────

export function OverviewScreen() {
  const data = useStore((s) => s.data);
  if (!data) return null;

  const score = getHealth(data);
  const cats = getCategories(data);
  const totalIssues = getTotalIssues(cats);
  const topFindings = getTopFindings(cats, 5);
  const concerns = getConcerns(data);
  const globalSignals = getGlobalSignals(data);
  const focus = getFocus(data);
  const trend = getTrend(data);
  const healthInfo = interpretHealth(score);
  const healthColor = hColor(score);

  function goToIssues(catKey) {
    location.hash = "issues";
    if (catKey) useStore.getState().setIssueTab(catKey);
  }

  function goToFile(path) {
    location.hash = "files/" + encodeURIComponent(path);
  }

  return (
    <div className="stack stack--2xl">

      {/* ─── 1. HERO ──────────────────────────────────────────────── */}
      <HealthHero
        score={score}
        color={healthColor}
        label={healthInfo?.label}
        description={healthInfo?.description}
        verdict={getVerdict(data)}
        trend={trend}
        analyzedPath={getAnalyzedPath(data)}
      />

      {/* ─── 2. STATS STRIP ───────────────────────────────────────── */}
      <StatsStrip
        fileCount={getFileCount(data)}
        moduleCount={getModuleCount(data)}
        commits={getCommits(data)}
        totalIssues={totalIssues}
      />

      {/* ─── 3. FOCUS POINT ───────────────────────────────────────── */}
      {focus && (
        <FocusSection focus={focus} onFileClick={goToFile} />
      )}

      {/* ─── 4. CONCERN GRID ──────────────────────────────────────── */}
      {concerns.length > 0 && (
        <ConcernGrid concerns={concerns} />
      )}

      {/* ─── 5. ISSUES + RISK ─────────────────────────────────────── */}
      <section>
        <div className="grid">
          <div className="span-7">
            <IssueCategoryCard categories={cats} onNavigate={goToIssues} />
          </div>
          <div className="span-5">
            <RiskCard files={getFiles(data)} globalSignals={globalSignals} />
          </div>
        </div>
      </section>

      {/* ─── 6. EVOLUTION (collapsed) ─────────────────────────────── */}
      {(data.evolution || data.metadata) && (
        <CollapsibleSection title="Evolution & Analysis Metadata">
          <div className="grid">
            {data.evolution && (
              <div className="span-7">
                <EvolutionPanel evolution={data.evolution} />
              </div>
            )}
            {data.metadata && (
              <div className="span-5">
                <MetadataPanel metadata={data.metadata} />
              </div>
            )}
          </div>
        </CollapsibleSection>
      )}

    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// HEALTH HERO
// ─────────────────────────────────────────────────────────────────────────────

function HealthHero({ score, color, label, description, verdict, trend, analyzedPath }) {
  // Arc gauge: score 1-10 maps to 0°–180° sweep (half-circle)
  const R = 54;
  const CX = 70;
  const CY = 70;
  const startAngle = Math.PI;            // left = 180°
  const sweepAngle = Math.PI;            // half circle
  const pct = Math.max(0, Math.min(1, (score - 1) / 9));
  const angle = startAngle + sweepAngle * pct;
  const nx = CX + R * Math.cos(angle);
  const ny = CY + R * Math.sin(angle);

  // Background arc path (grey track)
  const trackStart = { x: CX - R, y: CY };
  const trackEnd   = { x: CX + R, y: CY };
  // Filled arc path to the current value
  const sx = CX - R;
  const sy = CY;

  return (
    <div className="ds-card" style={{ position: "relative", overflow: "hidden" }}>
      {/* Subtle background gradient using health color */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          background: `radial-gradient(ellipse at 20% 50%, ${color}10 0%, transparent 70%)`,
          pointerEvents: "none",
        }}
      />

      <div className="ds-card__body" style={{ position: "relative" }}>
        <div className="grid" style={{ alignItems: "center" }}>
          {/* Left: gauge + score */}
          <div className="span-4" style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
            <svg
              width="140"
              height="90"
              viewBox="0 0 140 80"
              style={{ overflow: "visible" }}
            >
              {/* Track */}
              <path
                d={`M ${CX - R} ${CY} A ${R} ${R} 0 0 1 ${CX + R} ${CY}`}
                fill="none"
                stroke="var(--border)"
                strokeWidth="6"
                strokeLinecap="round"
              />
              {/* Filled arc */}
              {pct > 0 && (
                <path
                  d={`M ${sx} ${sy} A ${R} ${R} 0 ${pct > 0.5 ? 1 : 0} 1 ${nx} ${ny}`}
                  fill="none"
                  stroke={color}
                  strokeWidth="6"
                  strokeLinecap="round"
                  style={{ filter: `drop-shadow(0 0 4px ${color}60)` }}
                />
              )}
              {/* Needle dot */}
              <circle cx={nx} cy={ny} r="4" fill={color} />
              {/* Score text */}
              <text
                x={CX}
                y={CY - 4}
                textAnchor="middle"
                fill={color}
                fontSize="28"
                fontWeight="700"
                fontFamily="var(--font-mono)"
              >
                {score.toFixed(1)}
              </text>
              <text
                x={CX}
                y={CY + 12}
                textAnchor="middle"
                fill="var(--text-tertiary)"
                fontSize="8"
                fontFamily="var(--font-sans)"
                letterSpacing="0.08em"
              >
                / 10
              </text>
              {/* Min/max labels */}
              <text x={CX - R + 2} y={CY + 16} fill="var(--text-tertiary)" fontSize="7" fontFamily="var(--font-mono)">1</text>
              <text x={CX + R - 2} y={CY + 16} fill="var(--text-tertiary)" fontSize="7" fontFamily="var(--font-mono)" textAnchor="end">10</text>
            </svg>

            {trend != null && Math.abs(trend) >= 0.05 && (
              <div
                className="text-label"
                style={{
                  color: trend > 0 ? "var(--green)" : "var(--red)",
                  marginTop: "var(--space-1)",
                  fontSize: "var(--text-xs)",
                }}
              >
                {trend > 0 ? "↑" : "↓"} {Math.abs(trend).toFixed(1)} pts
              </div>
            )}
          </div>

          {/* Right: text details */}
          <div className="span-8">
            <div className="stack stack--sm">
              {verdict && (
                <div
                  className="text-label"
                  style={{ color, letterSpacing: "0.12em", fontSize: "var(--text-xs)" }}
                >
                  {verdict.toUpperCase()}
                </div>
              )}
              <div
                className="text-h2"
                style={{ color, lineHeight: 1.1 }}
              >
                {label ?? "Codebase Health"}
              </div>
              {description && (
                <div
                  className="text-body"
                  style={{ color: "var(--text-secondary)", maxWidth: "480px" }}
                >
                  {description}
                </div>
              )}
              {analyzedPath && (
                <div
                  className="text-mono"
                  style={{
                    fontSize: "var(--text-xs)",
                    color: "var(--text-tertiary)",
                    marginTop: "var(--space-2)",
                    padding: "var(--space-1) var(--space-2)",
                    background: "var(--surface-raised)",
                    borderRadius: "var(--radius-sm)",
                    display: "inline-flex",
                    alignItems: "center",
                    gap: "var(--space-1)",
                  }}
                >
                  <span style={{ opacity: 0.5 }}>analyzing</span>
                  {" "}{shortenPath(analyzedPath)}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// STATS STRIP
// ─────────────────────────────────────────────────────────────────────────────

function StatsStrip({ fileCount, moduleCount, commits, totalIssues }) {
  const stats = [
    { value: fmtN(fileCount),    label: "Files",   color: "var(--text)" },
    { value: fmtN(moduleCount),  label: "Modules", color: "var(--text)" },
    { value: fmtN(commits),      label: "Commits", color: "var(--text)" },
    {
      value: fmtN(totalIssues),
      label: "Issues",
      color: totalIssues > 0 ? "var(--orange)" : "var(--green)",
    },
  ];

  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "repeat(4, 1fr)",
        gap: "var(--space-3)",
      }}
    >
      {stats.map(({ value, label, color }) => (
        <div
          key={label}
          className="ds-card ds-card--compact"
          style={{ textAlign: "center", padding: "var(--space-4)" }}
        >
          <div
            className="text-mono"
            style={{ fontSize: "var(--text-2xl)", fontWeight: 700, color, lineHeight: 1.1 }}
          >
            {value}
          </div>
          <div
            className="text-label"
            style={{ marginTop: "var(--space-1)", color: "var(--text-tertiary)", fontSize: "var(--text-xs)" }}
          >
            {label.toUpperCase()}
          </div>
        </div>
      ))}
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// FOCUS SECTION
// ─────────────────────────────────────────────────────────────────────────────

function FocusSection({ focus, onFileClick }) {
  if (!focus?.path) return null;

  return (
    <div className="ds-card" style={{ borderLeft: "3px solid var(--accent)" }}>
      <div className="ds-card__header">
        <div className="ds-card__title" style={{ fontSize: "var(--text-xs)", letterSpacing: "0.1em" }}>
          RECOMMENDED STARTING POINT
        </div>
      </div>
      <div className="ds-card__body">
        <div className="grid" style={{ alignItems: "flex-start" }}>
          {/* File path + why */}
          <div className="span-8">
            <div className="stack stack--sm">
              <button
                onClick={() => onFileClick?.(focus.path)}
                style={{
                  background: "none",
                  border: "none",
                  cursor: "pointer",
                  padding: 0,
                  textAlign: "left",
                }}
              >
                <span
                  className="text-mono"
                  style={{
                    color: "var(--accent)",
                    fontSize: "var(--text-base)",
                    fontWeight: 500,
                    wordBreak: "break-all",
                  }}
                >
                  {focus.path}
                </span>
              </button>
              {focus.why && (
                <div className="text-body" style={{ color: "var(--text-secondary)" }}>
                  {focus.why}
                </div>
              )}
              {focus.findings?.length > 0 && (
                <div className="stack stack--xs" style={{ marginTop: "var(--space-2)" }}>
                  {focus.findings.slice(0, 3).map((f, i) => (
                    <div
                      key={i}
                      className="text-body-sm"
                      style={{
                        paddingLeft: "var(--space-3)",
                        borderLeft: "2px solid var(--border)",
                        color: "var(--text-secondary)",
                      }}
                    >
                      {f.label ?? f.finding_type}
                    </div>
                  ))}
                  {focus.findings.length > 3 && (
                    <div className="text-label" style={{ paddingLeft: "var(--space-3)", color: "var(--text-tertiary)" }}>
                      +{focus.findings.length - 3} more
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>

          {/* Score badges */}
          <div className="span-4">
            <div className="stack stack--sm" style={{ alignItems: "flex-end" }}>
              {[
                { label: "Risk",        value: focus.risk_score,         color: "var(--red)" },
                { label: "Impact",      value: focus.impact_score,       color: "var(--orange)" },
                { label: "Fixability",  value: focus.tractability_score, color: "var(--green)" },
                { label: "Confidence",  value: focus.confidence_score,   color: "var(--blue)" },
              ]
                .filter((s) => s.value != null)
                .map(({ label, value, color }) => (
                  <div
                    key={label}
                    className="cluster cluster--sm"
                    style={{ alignItems: "center", justifyContent: "flex-end" }}
                  >
                    <span
                      className="text-label"
                      style={{ color: "var(--text-tertiary)", fontSize: "var(--text-2xs)" }}
                    >
                      {label.toUpperCase()}
                    </span>
                    <span
                      className="text-mono"
                      style={{ color, fontWeight: 700, fontSize: "var(--text-base)" }}
                    >
                      {fmtF(value, 2)}
                    </span>
                  </div>
                ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// CONCERN GRID
// ─────────────────────────────────────────────────────────────────────────────

const CONCERN_STATUS_COLORS = {
  good:      "var(--green)",
  improving: "var(--blue)",
  warning:   "var(--yellow)",
  declining: "var(--orange)",
  critical:  "var(--red)",
};

function ConcernGrid({ concerns }) {
  return (
    <div>
      <div
        className="text-label"
        style={{ marginBottom: "var(--space-3)", color: "var(--text-tertiary)", letterSpacing: "0.1em", fontSize: "var(--text-xs)" }}
      >
        HEALTH AREAS
      </div>
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fill, minmax(180px, 1fr))",
          gap: "var(--space-3)",
        }}
      >
        {concerns.map((c) => {
          const scoreColor = hColor(c.score);
          const statusColor = CONCERN_STATUS_COLORS[c.status] ?? "var(--text-tertiary)";
          return (
            <div
              key={c.key}
              className="ds-card ds-card--compact"
              style={{
                borderTop: `2px solid ${scoreColor}`,
                padding: "var(--space-4)",
              }}
              title={c.description}
            >
              <div className="cluster cluster--md" style={{ justifyContent: "space-between", alignItems: "flex-start", marginBottom: "var(--space-2)" }}>
                <div
                  className="text-body-sm"
                  style={{ fontWeight: 600, color: "var(--text)", lineHeight: 1.2 }}
                >
                  {c.name}
                </div>
                <div
                  className="text-mono"
                  style={{ fontSize: "var(--text-xl)", fontWeight: 700, color: scoreColor, lineHeight: 1 }}
                >
                  {c.score.toFixed(1)}
                </div>
              </div>
              <div className="cluster cluster--xs" style={{ alignItems: "center" }}>
                <span
                  className="text-label"
                  style={{ color: statusColor, fontSize: "var(--text-2xs)", letterSpacing: "0.06em" }}
                >
                  {c.status?.toUpperCase() ?? "–"}
                </span>
                {c.finding_count > 0 && (
                  <span className="text-body-sm" style={{ color: "var(--text-tertiary)" }}>
                    · {c.finding_count}
                  </span>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// ISSUE CATEGORY CARD
// ─────────────────────────────────────────────────────────────────────────────

const CATEGORY_COLORS = {
  incomplete: "var(--blue)",
  fragile:    "var(--orange)",
  tangled:    "var(--yellow)",
  team:       "var(--red)",
};

function IssueCategoryCard({ categories, onNavigate }) {
  const maxCount = Math.max(...CATEGORY_ORDER.map((k) => categories[k]?.count ?? 0), 1);

  return (
    <div className="ds-card" style={{ height: "100%" }}>
      <div className="ds-card__header">
        <div className="ds-card__title">Issues by Category</div>
      </div>
      <div className="ds-card__body">
        <div className="stack stack--sm">
          {CATEGORY_ORDER.map((key) => {
            const cat = categories[key];
            const count = cat?.count ?? 0;
            const highCount = cat?.high_count ?? 0;
            const color = CATEGORY_COLORS[key] ?? "var(--accent)";
            const pct = (count / maxCount) * 100;

            return (
              <button
                key={key}
                onClick={() => onNavigate(key)}
                style={{
                  background: "none",
                  border: "none",
                  padding: "var(--space-2) 0",
                  cursor: "pointer",
                  width: "100%",
                  textAlign: "left",
                  display: "flex",
                  alignItems: "center",
                  gap: "var(--space-3)",
                  borderRadius: "var(--radius-sm)",
                  transition: "background var(--transition-base)",
                }}
                onMouseEnter={(e) => e.currentTarget.style.background = "var(--surface-raised)"}
                onMouseLeave={(e) => e.currentTarget.style.background = "none"}
              >
                <div
                  className="text-body-sm"
                  style={{ minWidth: "120px", color: "var(--text)", fontWeight: count > 0 ? 500 : 400 }}
                >
                  {CATEGORY_LABELS[key]}
                </div>
                <div
                  style={{
                    flex: 1,
                    height: "4px",
                    background: "var(--border)",
                    borderRadius: "2px",
                    overflow: "hidden",
                  }}
                >
                  <div
                    style={{
                      width: `${pct}%`,
                      height: "100%",
                      background: color,
                      borderRadius: "2px",
                      transition: "width 0.6s ease",
                    }}
                  />
                </div>
                <div
                  className="text-mono"
                  style={{
                    minWidth: "28px",
                    textAlign: "right",
                    color: count > 0 ? color : "var(--text-tertiary)",
                    fontWeight: 700,
                    fontSize: "var(--text-sm)",
                  }}
                >
                  {count}
                </div>
                {highCount > 0 && (
                  <span
                    className="text-label"
                    style={{
                      padding: "1px 5px",
                      background: "var(--red)",
                      color: "var(--bg)",
                      borderRadius: "8px",
                      fontSize: "var(--text-2xs)",
                      fontWeight: 700,
                      minWidth: "20px",
                      textAlign: "center",
                    }}
                  >
                    {highCount}↑
                  </span>
                )}
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// RISK CARD
// ─────────────────────────────────────────────────────────────────────────────

function RiskCard({ files, globalSignals }) {
  const gSigs = globalSignals;
  const keyMetrics = [
    { label: "Cycle count",    value: gSigs.cycle_count ?? 0,         color: gSigs.cycle_count > 0 ? "var(--orange)" : "var(--green)" },
    { label: "Orphan files",   value: `${((gSigs.orphan_ratio ?? 0) * 100).toFixed(1)}%`, color: "var(--text)" },
    { label: "Modularity",     value: fmtF(gSigs.modularity ?? 0, 2), color: "var(--text)" },
  ].filter((m) => m.value != null);

  return (
    <div className="ds-card" style={{ height: "100%" }}>
      <div className="ds-card__header">
        <div className="ds-card__title">Risk Distribution</div>
      </div>
      <div className="ds-card__body">
        <div className="stack stack--md">
          <RiskHistogram files={files} />
          {keyMetrics.length > 0 && (
            <div
              style={{
                paddingTop: "var(--space-3)",
                borderTop: "1px solid var(--border)",
                display: "grid",
                gridTemplateColumns: "1fr 1fr 1fr",
                gap: "var(--space-2)",
              }}
            >
              {keyMetrics.map(({ label, value, color }) => (
                <div key={label} style={{ textAlign: "center" }}>
                  <div
                    className="text-mono"
                    style={{ fontSize: "var(--text-base)", fontWeight: 700, color }}
                  >
                    {value}
                  </div>
                  <div
                    className="text-label"
                    style={{ fontSize: "var(--text-2xs)", color: "var(--text-tertiary)", marginTop: "2px" }}
                  >
                    {label}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// EVOLUTION PANEL
// ─────────────────────────────────────────────────────────────────────────────

function EvolutionPanel({ evolution }) {
  const charts = [
    { key: "file_count",     label: "Files",       color: "var(--blue)",   fmt: (v) => Math.round(v).toString() },
    { key: "total_loc",      label: "LOC",         color: "var(--green)",  fmt: (v) => (v / 1000).toFixed(1) + "k" },
    { key: "avg_complexity", label: "Complexity",  color: "var(--orange)", fmt: (v) => v.toFixed(1) },
    { key: "avg_risk",       label: "Avg Risk",    color: "var(--red)",    fmt: (v) => v.toFixed(3) },
  ];

  return (
    <div className="ds-card">
      <div className="ds-card__header">
        <div className="ds-card__title">Codebase Evolution</div>
      </div>
      <div className="ds-card__body">
        <div className="grid grid--compact">
          {charts.map(({ key, label, color, fmt }) => {
            const pts = evolution[key];
            if (!pts || pts.length < 2) return null;
            return (
              <div key={key} className="span-6">
                <div className="stack stack--xs">
                  <TrendChart
                    values={pts.map((d) => d.value)}
                    xLabels={pts.map((d) =>
                      new Date(d.timestamp).toLocaleDateString(undefined, { month: "short", day: "numeric" })
                    )}
                    color={color}
                    yFormat={fmt}
                    width={240}
                    height={80}
                  />
                  <div className="text-label text-center" style={{ fontSize: "var(--text-xs)" }}>
                    {label}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// METADATA PANEL
// ─────────────────────────────────────────────────────────────────────────────

function MetadataPanel({ metadata }) {
  const items = [
    { label: "Files Scanned", value: fmtN(metadata.files_scanned) },
    { label: "Modules",       value: fmtN(metadata.modules_detected) },
    { label: "Commits",       value: fmtN(metadata.commits_processed) },
    metadata.snapshot_count != null && { label: "Snapshots", value: metadata.snapshot_count },
    metadata.db_size_mb != null && { label: "DB Size", value: `${metadata.db_size_mb.toFixed(1)} MB` },
    { label: "Analyzers", value: metadata.analyzers_ran?.length ?? 0 },
  ].filter(Boolean);

  return (
    <div className="ds-card">
      <div className="ds-card__header">
        <div className="ds-card__title">Analysis Details</div>
      </div>
      <div className="ds-card__body">
        <div className="stack stack--sm">
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "var(--space-3)" }}>
            {items.map(({ label, value }) => (
              <div key={label} style={{ textAlign: "center", padding: "var(--space-2)" }}>
                <div className="text-mono" style={{ fontSize: "var(--text-lg)", fontWeight: 700, color: "var(--text)" }}>
                  {value}
                </div>
                <div className="text-label" style={{ color: "var(--text-tertiary)", fontSize: "var(--text-2xs)", marginTop: "2px" }}>
                  {label.toUpperCase()}
                </div>
              </div>
            ))}
          </div>
          {metadata.analyzers_ran?.length > 0 && (
            <div style={{ paddingTop: "var(--space-3)", borderTop: "1px solid var(--border)" }}>
              <div className="text-label" style={{ color: "var(--text-tertiary)", fontSize: "var(--text-2xs)", marginBottom: "var(--space-2)" }}>
                ANALYZERS
              </div>
              <div className="cluster cluster--xs">
                {metadata.analyzers_ran.map((a) => (
                  <span
                    key={a}
                    className="text-mono"
                    style={{
                      padding: "2px 6px",
                      background: "rgba(59, 130, 246, 0.08)",
                      color: "var(--accent)",
                      borderRadius: "var(--radius-sm)",
                      border: "1px solid rgba(59, 130, 246, 0.15)",
                      fontSize: "var(--text-xs)",
                    }}
                  >
                    {a}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// COLLAPSIBLE SECTION
// ─────────────────────────────────────────────────────────────────────────────

function CollapsibleSection({ title, children }) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <section>
      <button
        onClick={() => setIsOpen((v) => !v)}
        style={{
          width: "100%",
          background: "var(--surface)",
          border: "1px solid var(--border)",
          borderRadius: isOpen ? "var(--radius-md) var(--radius-md) 0 0" : "var(--radius-md)",
          padding: "var(--space-3) var(--space-4)",
          cursor: "pointer",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          color: "var(--text-secondary)",
          fontSize: "var(--text-sm)",
          fontWeight: 500,
          transition: "border-radius var(--transition-base)",
        }}
      >
        <span className="text-label" style={{ letterSpacing: "0.08em", fontSize: "var(--text-xs)" }}>
          {title.toUpperCase()}
        </span>
        <span style={{ fontFamily: "var(--font-mono)", fontSize: "var(--text-sm)", color: "var(--text-tertiary)" }}>
          {isOpen ? "−" : "+"}
        </span>
      </button>
      {isOpen && (
        <div
          style={{
            border: "1px solid var(--border)",
            borderTop: "none",
            borderRadius: "0 0 var(--radius-md) var(--radius-md)",
            padding: "var(--space-6)",
            background: "var(--bg)",
          }}
        >
          {children}
        </div>
      )}
    </section>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// HELPERS
// ─────────────────────────────────────────────────────────────────────────────

function shortenPath(p) {
  if (!p) return "";
  // Show last 2 path segments for long paths
  const parts = p.replace(/\\/g, "/").split("/").filter(Boolean);
  if (parts.length <= 2) return p;
  return "…/" + parts.slice(-2).join("/");
}
