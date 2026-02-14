/**
 * File detail view - shows metrics, findings, and signal categories
 * for a single file.
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
  const [openCats, setOpenCats] = useState(() => {
    // First 2 categories start open
    const initial = new Set();
    let count = 0;
    for (const cat of SIGNAL_CATEGORIES) {
      if (count >= 2) break;
      initial.add(cat.key);
      count++;
    }
    return initial;
  });

  if (!data || !data.files || !data.files[path]) {
    return (
      <div>
        <a class="file-detail-back" href="#files">&larr; Files</a>
        <div class="empty-state">
          <div class="empty-state-title">File not found</div>
          <div>{path}</div>
        </div>
      </div>
    );
  }

  const f = data.files[path];
  const color = hColor(f.health);

  // Key metrics with clear names and interpretation
  const healthInfo = interpretHealth(f.health);
  const metrics = [
    { label: "Lines of Code", value: f.lines, interp: interpretSignal("lines", f.lines) },
    { label: "Functions", value: f.signals ? f.signals.function_count : null, interp: interpretSignal("function_count", f.signals ? f.signals.function_count : null) },
    { label: "Risk Score", value: fmtF(f.risk_score, 3), interp: interpretSignal("risk_score", f.risk_score) },
    { label: "Import Centrality", value: fmtF(f.pagerank, 4), interp: interpretSignal("pagerank", f.pagerank) },
    { label: "Total Commits", value: f.total_changes, interp: interpretSignal("total_changes", f.total_changes) },
    { label: "Team Knowledge Spread", value: fmtF(f.bus_factor, 1), interp: interpretSignal("bus_factor", f.bus_factor) },
    { label: "Change Impact Size", value: f.blast_radius, interp: interpretSignal("blast_radius_size", f.blast_radius) },
    { label: "Cognitive Complexity", value: fmtF(f.cognitive_load, 1), interp: interpretSignal("cognitive_load", f.cognitive_load) },
  ];

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
    <div>
      <a class="file-detail-back" href="#files">&larr; Files</a>

      <div class="file-detail-header">
        <span class="file-detail-path">{path}</span>
        {f.role && f.role !== "UNKNOWN" && <Badge variant="role">{f.role}</Badge>}
        <span class="file-detail-health" style={{ color }}>
          {fmtF(f.health, 1)}
          <span class="file-detail-health-label"> {healthInfo.label}</span>
        </span>
      </div>

      {/* Key metrics grid */}
      <div class="file-detail-metrics">
        {metrics.map((m) => (
          <div class="fdm-cell" key={m.label}>
            <div class="fdm-value">{m.value != null ? m.value : "--"}</div>
            <div class="fdm-label">{m.label}</div>
            {m.interp && <div class="fdm-interp">{m.interp}</div>}
          </div>
        ))}
      </div>

      {/* File findings */}
      {fileFindings.length > 0 && (
        <div class="file-detail-section">
          <div class="file-detail-section-title">Issues ({fileFindings.length})</div>
          {fileFindings.map((finding, j) => (
            <FindingCard key={j} finding={finding} showFiles={false} maxEvidence={3} />
          ))}
        </div>
      )}

      {/* Signals grouped by category */}
      {sigKeys.length > 0 && (
        <div class="file-detail-section">
          {SIGNAL_CATEGORIES.map((cat) => {
            const catSigs = cat.signals.filter((s) => sigs[s] != null);
            if (!catSigs.length) return null;

            const isOpen = openCats.has(cat.key);
            return (
              <div key={cat.key}>
                <div
                  class={`file-detail-section-title signals-collapsible sig-cat-toggle${isOpen ? " sig-cat-open open" : ""}`}
                  onClick={() => toggleCat(cat.key)}
                >
                  {cat.name} ({catSigs.length})
                </div>
                <div
                  class="signals-grid sig-cat-grid"
                  style={{ display: isOpen ? "grid" : "none" }}
                >
                  {catSigs.map((sk) => {
                    const sv = sigs[sk];
                    const label = SIGNAL_LABELS[sk] || sk.replace(/_/g, " ");
                    const display = fmtSigVal(sk, sv);
                    const valColor = typeof sv === "number" ? polarColor(sk, sv) : "var(--text)";
                    const trendData = f.trends && f.trends[sk];
                    const interp = interpretSignal(sk, sv);

                    return (
                      <div class="sig-row" key={sk}>
                        <span class="sig-name">
                          {label}
                          {SIGNAL_DESCRIPTIONS[sk] && (
                            <span class="sig-desc">{SIGNAL_DESCRIPTIONS[sk]}</span>
                          )}
                        </span>
                        <span class="sig-val-group">
                          <span class="sig-val" style={{ color: valColor }}>
                            {display}
                            {trendData && (
                              <>
                                {" "}
                                <Sparkline values={trendData} width={48} height={14} color={valColor} />
                              </>
                            )}
                          </span>
                          {interp && <span class="sig-interp">{interp}</span>}
                        </span>
                      </div>
                    );
                  })}
                </div>
              </div>
            );
          })}

          {/* Uncategorized signals */}
          {uncatSigs.length > 0 && (
            <div>
              <div
                class={`file-detail-section-title signals-collapsible sig-cat-toggle${openCats.has("other") ? " sig-cat-open open" : ""}`}
                onClick={() => toggleCat("other")}
              >
                Other ({uncatSigs.length})
              </div>
              <div
                class="signals-grid sig-cat-grid"
                style={{ display: openCats.has("other") ? "grid" : "none" }}
              >
                {uncatSigs.map((sk) => {
                  const sv = sigs[sk];
                  const display =
                    typeof sv === "number"
                      ? Number.isInteger(sv)
                        ? String(sv)
                        : sv.toFixed(4)
                      : String(sv);
                  return (
                    <div class="sig-row" key={sk}>
                      <span class="sig-name">{sk.replace(/_/g, " ")}</span>
                      <span class="sig-val">{display}</span>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
