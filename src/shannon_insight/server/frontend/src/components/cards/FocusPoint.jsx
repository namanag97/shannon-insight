/**
 * Focus point card - shows the most actionable file to work on.
 * Displays scores, findings, and alternatives.
 */

import { SeverityDot } from "../ui/SeverityDot.jsx";
import { fmtF } from "../../utils/formatters.js";
import { sevKey } from "../../utils/helpers.js";

export function FocusPoint({ focus }) {
  if (!focus) {
    return <div class="focus-empty">No actionable focus point identified.</div>;
  }

  return (
    <div>
      <div class="focus-path">
        <a href={"#files/" + encodeURIComponent(focus.path)}>{focus.path}</a>
      </div>

      {(focus.risk_score != null || focus.impact_score != null) && (
        <div class="focus-scores">
          {focus.risk_score != null && (
            <div class="focus-score-item">
              <div class="focus-score-val">{fmtF(focus.risk_score, 2)}</div>
              <div class="focus-score-label">risk</div>
            </div>
          )}
          {focus.impact_score != null && (
            <div class="focus-score-item">
              <div class="focus-score-val">{fmtF(focus.impact_score, 2)}</div>
              <div class="focus-score-label">impact</div>
            </div>
          )}
          {focus.tractability_score != null && (
            <div class="focus-score-item">
              <div class="focus-score-val">{fmtF(focus.tractability_score, 2)}</div>
              <div class="focus-score-label">tractability</div>
            </div>
          )}
          {focus.confidence_score != null && (
            <div class="focus-score-item">
              <div class="focus-score-val">{fmtF(focus.confidence_score, 2)}</div>
              <div class="focus-score-label">confidence</div>
            </div>
          )}
        </div>
      )}

      <div class="focus-why">{focus.why}</div>

      {(focus.findings || []).slice(0, 3).map((fi, j) => (
        <div class="focus-finding" key={j}>
          <SeverityDot severity={fi.severity} />
          <div class="focus-finding-text">{fi.label}</div>
        </div>
      ))}

      {focus.alternatives && focus.alternatives.length > 0 && (
        <div>
          <div class="also-consider-label">Also consider:</div>
          {focus.alternatives.slice(0, 3).map((alt, a) => (
            <div class="alt-item" key={a}>
              <a href={"#files/" + encodeURIComponent(alt.path)}>{alt.path}</a>
              {alt.why && <span class="alt-why">{alt.why}</span>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
