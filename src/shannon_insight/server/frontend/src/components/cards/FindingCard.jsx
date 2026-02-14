/**
 * Finding card - renders a single finding with severity indicator,
 * evidence, interpretation, and suggestion.
 *
 * Extracted from renderFindingRow() and renderEvidence() in old app.js.
 */

import { SeverityDot } from "../ui/SeverityDot.jsx";
import { Badge } from "../ui/Badge.jsx";
import { sevKey } from "../../utils/helpers.js";
import { SIGNAL_LABELS } from "../../utils/constants.js";

function Evidence({ evidence, maxItems = 4 }) {
  if (!evidence || !evidence.length) return null;

  const limit = Math.min(evidence.length, maxItems);
  return (
    <div class="finding-evidence">
      {evidence.slice(0, limit).map((ev, i) => {
        const sigName = ev.signal.replace(/_/g, " ");
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
            {i < limit - 1 ? "\u00a0\u00a0\u00a0" : null}
          </span>
        );
      })}
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
