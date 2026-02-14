/**
 * Finding card - renders a single finding with severity indicator,
 * collapsible evidence, interpretation, and actionable suggestion.
 *
 * v2: Added collapsible evidence sections, improved typography hierarchy,
 * cleaner severity indicators.
 */

import { useState } from "preact/hooks";
import { SeverityDot } from "../ui/SeverityDot.jsx";
import { Badge } from "../ui/Badge.jsx";
import { sevKey } from "../../utils/helpers.js";
import { SIGNAL_LABELS } from "../../utils/constants.js";

function Evidence({ evidence, maxItems = 4 }) {
  const [expanded, setExpanded] = useState(false);
  if (!evidence || !evidence.length) return null;

  const showToggle = evidence.length > maxItems;
  const displayed = expanded ? evidence : evidence.slice(0, maxItems);

  return (
    <div>
      <div class="finding-evidence">
        {displayed.map((ev, i) => {
          const sigName = SIGNAL_LABELS[ev.signal] || ev.signal.replace(/_/g, " ");
          const valStr =
            typeof ev.value === "number"
              ? Number.isInteger(ev.value)
                ? String(ev.value)
                : ev.value.toFixed(2)
              : String(ev.value);
          return (
            <span key={i}>
              {sigName}: <strong>{valStr}</strong>
              {ev.percentile ? (
                <span class="pctl"> ({Math.round(ev.percentile)}th pctl)</span>
              ) : null}
              {i < displayed.length - 1 ? "\u00a0\u00a0\u00b7\u00a0\u00a0" : null}
            </span>
          );
        })}
      </div>
      {showToggle && (
        <div class="finding-evidence-toggle" onClick={() => setExpanded(!expanded)}>
          {expanded ? "Show less" : `Show ${evidence.length - maxItems} more...`}
        </div>
      )}
    </div>
  );
}

export function FindingCard({ finding, showFiles = false, chronicSet, maxEvidence = 4 }) {
  const sk = sevKey(finding.severity);
  let classes = "finding-row sev-" + sk;
  if (finding.confidence != null && finding.confidence < 0.5) {
    classes += " finding-low-confidence";
  }

  return (
    <div class={classes}>
      <div class="finding-head">
        <SeverityDot severity={sk} />
        <span class="finding-type-label">{finding.label}</span>
        {finding.effort && <Badge variant="effort">{finding.effort}</Badge>}
        {chronicSet && chronicSet.has(finding.finding_type) && (
          <Badge variant="chronic">CHRONIC</Badge>
        )}
      </div>

      {showFiles && finding.files && finding.files.length > 0 && (
        <div class="finding-files">
          {finding.files.map((f, i) => (
            <span key={f}>
              {i > 0 ? ", " : null}
              <a href={"#files/" + encodeURIComponent(f)}>{f}</a>
            </span>
          ))}
        </div>
      )}

      <Evidence evidence={finding.evidence} maxItems={maxEvidence} />

      {finding.interpretation && (
        <div class="finding-interp">{finding.interpretation}</div>
      )}

      {finding.suggestion && (
        <div class="finding-suggestion">{finding.suggestion}</div>
      )}
    </div>
  );
}
