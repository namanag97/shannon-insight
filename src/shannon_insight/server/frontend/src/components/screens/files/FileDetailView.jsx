/**
 * FileDetailView - Redesigned with proper information architecture
 *
 * Information Priority:
 * 1. Header - File identity (path, role, health score)
 * 2. Metrics Grid - Key numbers in 4-column grid
 * 3. Findings - Issues found in this file
 * 4. Signals - All signals grouped by category (collapsible)
 *
 * Design System:
 * - 12-column grid with proper gutters
 * - Mathematical spacing (8px baseline)
 * - Clear visual hierarchy
 * - Collapsible sections for progressive disclosure
 */

import { useState } from "preact/hooks";
import useStore from "../../../state/store.js";
import { fmtF, fmtSigVal } from "../../../utils/formatters.js";
import { hColor, polarColor } from "../../../utils/helpers.js";
import { SIGNAL_LABELS, SIGNAL_DESCRIPTIONS, SIGNAL_CATEGORIES } from "../../../utils/constants.js";
import { interpretSignal, interpretHealth } from "../../../utils/interpretations.js";
import { FindingCard } from "../../cards/FindingCard.jsx";
import { Badge } from "../../ui/Badge.jsx";
import { Sparkline } from "../../charts/Sparkline.jsx";

export function FileDetailView({ path }) {
  const data = useStore((s) => s.data);
  const [openCats, setOpenCats] = useState(() => new Set());
  const [signalsOpen, setSignalsOpen] = useState(false);

  if (!data || !data.files || !data.files[path]) {
    return (
      <div className="stack stack--lg">
        <a className="file-detail-back" href="#files">&larr; Back to Files</a>
        <div className="empty-state">
          <div className="empty-state-title">File not found</div>
          <div className="text-body-sm" style={{ color: 'var(--text-tertiary)' }}>{path}</div>
        </div>
      </div>
    );
  }

  const f = data.files[path];
  const color = hColor(f.health);
  const healthInfo = interpretHealth(f.health);

  // Collect findings for this file
  const fileFindings = [];
  const cats = data.categories || {};
  for (const ck in cats) {
    for (const finding of cats[ck].findings || []) {
      if (finding.files && finding.files.indexOf(path) !== -1) {
        fileFindings.push(finding);
      }
    }
  }

  // Signal categories
  const sigs = f.signals || {};
  const sigKeys = Object.keys(sigs);

  // Build categorized set for detecting uncategorized signals
  const categorized = new Set();
  SIGNAL_CATEGORIES.forEach((c) => c.signals.forEach((s) => categorized.add(s)));
  const uncatSigs = sigKeys.filter((s) => !categorized.has(s) && sigs[s] != null).sort();

  function toggleCat(catKey) {
    setOpenCats((prev) => {
      const next = new Set(prev);
      if (next.has(catKey)) next.delete(catKey);
      else next.add(catKey);
      return next;
    });
  }

  return (
    <div className="stack stack--2xl">
      {/* ══════════════════════════════════════════════════════════
          HEADER - File identity, role, and health
          ══════════════════════════════════════════════════════════ */}
      <section>
        <div className="stack stack--md">
          <a
            className="text-body-sm"
            href="#files"
            style={{ color: 'var(--accent)', textDecoration: 'none' }}
          >
            &larr; Back to Files
          </a>
          <div className="ds-card ds-card--compact">
            <div className="stack stack--sm">
              <div
                className="text-mono"
                style={{
                  fontSize: 'var(--text-lg)',
                  fontWeight: 'var(--font-medium)',
                  color: 'var(--text)',
                  wordBreak: 'break-all',
                }}
              >
                {path}
              </div>
              <div className="cluster cluster--sm">
                {f.role && f.role !== "UNKNOWN" && (
                  <Badge variant="role">{f.role}</Badge>
                )}
                {f.health != null && (
                  <span
                    className="text-mono"
                    style={{
                      fontSize: 'var(--text-md)',
                      fontWeight: 'var(--font-semibold)',
                      color,
                    }}
                  >
                    Health: {fmtF(f.health, 1)}
                    <span
                      style={{
                        marginLeft: 'var(--space-2)',
                        fontSize: 'var(--text-sm)',
                        fontWeight: 'var(--font-normal)',
                        color: 'var(--text-secondary)',
                      }}
                    >
                      {healthInfo.label}
                    </span>
                  </span>
                )}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ══════════════════════════════════════════════════════════
          PRIORITY 2: METRICS GRID - Key numbers at a glance
          4-column grid with the most important file metrics
          ══════════════════════════════════════════════════════════ */}
      <section>
        <div className="grid grid--compact">
          <div className="span-3">
            <MetricCard
              value={fmtF(f.risk_score, 3)}
              label="Risk Score"
              color={(f.risk_score || 0) > 0.05 ? hColor(10 - (f.risk_score || 0) * 10) : undefined}
            />
          </div>
          <div className="span-3">
            <MetricCard
              value={f.total_changes || 0}
              label="Total Changes"
            />
          </div>
          <div className="span-3">
            <MetricCard
              value={fmtF(f.cognitive_load, 1)}
              label="Complexity"
              color={f.cognitive_load >= 15 ? 'var(--red)' : f.cognitive_load >= 10 ? 'var(--orange)' : undefined}
            />
          </div>
          <div className="span-3">
            <MetricCard
              value={f.blast_radius || 0}
              label="Impact Size"
              color={f.blast_radius >= 30 ? 'var(--red)' : f.blast_radius >= 15 ? 'var(--orange)' : undefined}
            />
          </div>
        </div>
      </section>

      {/* ══════════════════════════════════════════════════════════
          SECONDARY METRICS - Additional context
          ══════════════════════════════════════════════════════════ */}
      <section>
        <div className="grid grid--compact">
          <div className="span-3">
            <MetricCard
              value={f.lines != null ? f.lines : "--"}
              label="Lines of Code"
            />
          </div>
          <div className="span-3">
            <MetricCard
              value={f.signals ? (f.signals.function_count != null ? f.signals.function_count : "--") : "--"}
              label="Functions"
            />
          </div>
          <div className="span-3">
            <MetricCard
              value={fmtF(f.pagerank, 4)}
              label="Import Centrality"
            />
          </div>
          <div className="span-3">
            <MetricCard
              value={fmtF(f.bus_factor, 1)}
              label="Team Knowledge"
              color={f.bus_factor < 1.5 ? 'var(--red)' : undefined}
            />
          </div>
        </div>
      </section>

      {/* ══════════════════════════════════════════════════════════
          PRIORITY 3: FINDINGS IN THIS FILE
          Issues that apply to this specific file
          ══════════════════════════════════════════════════════════ */}
      {fileFindings.length > 0 && (
        <section>
          <div className="ds-card">
            <div className="ds-card__header">
              <div className="ds-card__title">
                Findings in this File ({fileFindings.length})
              </div>
            </div>
            <div className="ds-card__body">
              <div className="stack stack--md">
                {fileFindings.map((finding, j) => (
                  <FindingCard key={j} finding={finding} showFiles={false} maxEvidence={3} />
                ))}
              </div>
            </div>
          </div>
        </section>
      )}

      {/* ══════════════════════════════════════════════════════════
          PRIORITY 4: ALL SIGNALS (Collapsible)
          Full signal detail grouped by category
          ══════════════════════════════════════════════════════════ */}
      {sigKeys.length > 0 && (
        <section>
          <CollapsibleSection
            title={`All Signals (${sigKeys.filter((k) => sigs[k] != null).length})`}
            isOpen={signalsOpen}
            onToggle={() => setSignalsOpen(!signalsOpen)}
          >
            <div className="stack stack--lg">
              {SIGNAL_CATEGORIES.map((cat) => {
                const catSigs = cat.signals.filter((s) => sigs[s] != null);
                if (!catSigs.length) return null;

                const isOpen = openCats.has(cat.key);
                return (
                  <div key={cat.key}>
                    <div
                      className="text-h4"
                      style={{
                        cursor: 'pointer',
                        padding: 'var(--space-3) 0',
                        borderBottom: '1px solid var(--border-subtle)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        userSelect: 'none',
                      }}
                      onClick={() => toggleCat(cat.key)}
                    >
                      <span>
                        {cat.name} ({catSigs.length})
                        {cat.description && isOpen && (
                          <span
                            className="text-label"
                            style={{
                              marginLeft: 'var(--space-4)',
                              fontWeight: 'var(--font-normal)',
                              textTransform: 'none',
                              letterSpacing: 'normal',
                            }}
                          >
                            {cat.description}
                          </span>
                        )}
                      </span>
                      <span
                        className="text-mono"
                        style={{
                          color: 'var(--text-tertiary)',
                          fontSize: 'var(--text-md)',
                        }}
                      >
                        {isOpen ? '\u2212' : '+'}
                      </span>
                    </div>

                    {isOpen && (
                      <div className="signals-grid sig-cat-grid" style={{ marginTop: 'var(--space-4)' }}>
                        {catSigs.map((sk) => {
                          const sv = sigs[sk];
                          const label = SIGNAL_LABELS[sk] || sk.replace(/_/g, " ");
                          const display = fmtSigVal(sk, sv);
                          const valColor = typeof sv === "number" ? polarColor(sk, sv) : "var(--text)";
                          const trendData = f.trends && f.trends[sk];
                          const interp = interpretSignal(sk, sv);

                          return (
                            <div className="sig-row" key={sk}>
                              <span className="sig-name">
                                {label}
                                {SIGNAL_DESCRIPTIONS[sk] && (
                                  <span className="sig-desc">{SIGNAL_DESCRIPTIONS[sk]}</span>
                                )}
                              </span>
                              <span className="sig-val-group">
                                <span className="sig-val" style={{ color: valColor }}>
                                  {display}
                                  {trendData && (
                                    <>
                                      {" "}
                                      <Sparkline values={trendData} width={48} height={14} color={valColor} />
                                    </>
                                  )}
                                </span>
                                {interp && <span className="sig-interp">{interp}</span>}
                              </span>
                            </div>
                          );
                        })}
                      </div>
                    )}
                  </div>
                );
              })}

              {/* Uncategorized signals */}
              {uncatSigs.length > 0 && (
                <div>
                  <div
                    className="text-h4"
                    style={{
                      cursor: 'pointer',
                      padding: 'var(--space-3) 0',
                      borderBottom: '1px solid var(--border-subtle)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      userSelect: 'none',
                    }}
                    onClick={() => toggleCat("other")}
                  >
                    <span>Other ({uncatSigs.length})</span>
                    <span
                      className="text-mono"
                      style={{
                        color: 'var(--text-tertiary)',
                        fontSize: 'var(--text-md)',
                      }}
                    >
                      {openCats.has("other") ? '\u2212' : '+'}
                    </span>
                  </div>

                  {openCats.has("other") && (
                    <div className="signals-grid sig-cat-grid" style={{ marginTop: 'var(--space-4)' }}>
                      {uncatSigs.map((sk) => {
                        const sv = sigs[sk];
                        const display =
                          typeof sv === "number"
                            ? Number.isInteger(sv)
                              ? String(sv)
                              : sv.toFixed(4)
                            : String(sv);
                        return (
                          <div className="sig-row" key={sk}>
                            <span className="sig-name">{sk.replace(/_/g, " ")}</span>
                            <span className="sig-val">{display}</span>
                          </div>
                        );
                      })}
                    </div>
                  )}
                </div>
              )}
            </div>
          </CollapsibleSection>
        </section>
      )}
    </div>
  );
}


/* ═══════════════════════════════════════════════════════════════════════════
   SUB-COMPONENTS
   ═══════════════════════════════════════════════════════════════════════════ */

/**
 * MetricCard - Compact metric display for the 4-column grid.
 * Uses design system card pattern.
 */
function MetricCard({ value, label, color }) {
  return (
    <div className="ds-card ds-card--compact" style={{ textAlign: 'center' }}>
      <div
        className="text-mono"
        style={{
          color: color || 'var(--text)',
          fontSize: 'var(--text-xl)',
          fontWeight: 'var(--font-semibold)',
          lineHeight: 'var(--leading-tight)',
        }}
      >
        {value != null ? value : "--"}
      </div>
      <div
        className="text-label"
        style={{ marginTop: 'var(--space-1)' }}
      >
        {label}
      </div>
    </div>
  );
}

/**
 * CollapsibleSection - For low-priority content with progressive disclosure.
 * Consistent with the pattern used in OverviewScreen.v2.jsx.
 */
function CollapsibleSection({ title, children, isOpen, onToggle }) {
  return (
    <div>
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
          justifyContent: 'space-between',
        }}
        onClick={onToggle}
      >
        <span>{title}</span>
        <span
          className="text-mono"
          style={{
            color: 'var(--text-tertiary)',
            fontSize: 'var(--text-md)',
          }}
        >
          {isOpen ? '\u2212' : '+'}
        </span>
      </div>
      {isOpen && (
        <div style={{ marginTop: 'var(--space-6)' }}>
          {children}
        </div>
      )}
    </div>
  );
}
