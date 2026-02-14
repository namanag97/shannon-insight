/**
 * Colored dot indicating severity level (critical/high/medium/low/info).
 */

import { sevKey } from "../../utils/helpers.js";

export function SeverityDot({ severity }) {
  const key = typeof severity === "string" ? severity : sevKey(severity);
  return <div class={`sev-dot ${key}`} />;
}
