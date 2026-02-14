/**
 * Concern bar - renders a single health dimension as a progress bar.
 * Used as fallback when there are fewer than 3 concerns (radar chart needs 3+).
 */

import { hColor } from "../../utils/helpers.js";

export function ConcernBar({ concern }) {
  const pct = (concern.score / 10) * 100;
  const color = hColor(concern.score);

  return (
    <div class="concern-row">
      <span class="concern-name">{concern.name}</span>
      <div class="concern-track">
        <div class="concern-fill" style={{ width: pct + "%", background: color }} />
      </div>
      <span class="concern-score" style={{ color }}>{concern.score.toFixed(1)}</span>
    </div>
  );
}
