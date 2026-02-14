/**
 * Progress bar and reconnect banner. Shows analysis progress
 * and reconnection state.
 */

import useStore from "../../state/store.js";

export function ProgressBar() {
  const progressActive = useStore((s) => s.progressActive);
  const progressPercent = useStore((s) => s.progressPercent);
  const reconnectActive = useStore((s) => s.reconnectActive);

  const percentText =
    progressPercent != null ? Math.round(progressPercent * 100) + "%" : "";
  const fillStyle = {};
  if (progressPercent != null) {
    fillStyle.animation = "none";
    fillStyle.width = progressPercent * 100 + "%";
  }

  return (
    <>
      <div id="progressBar" class={progressActive ? "active" : ""}>
        <div id="progressFill" style={fillStyle} />
      </div>
      <div
        class={`progress-text${progressPercent != null && progressActive ? " active" : ""}`}
      >
        {percentText}
      </div>
      <div id="reconnectBanner" class={reconnectActive ? "active" : ""}>
        <span class="reconnect-dot" />
        Reconnecting<span class="analyzing-dots" />
      </div>
    </>
  );
}
