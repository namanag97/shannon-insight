/**
 * Pure helper functions for color mapping, severity classification,
 * and HTML escaping.
 */

import { SIGNAL_POLARITY, MODULE_SIGNAL_POLARITY, UNBOUNDED_SIGNAL_CAPS } from "./constants.js";

/**
 * Escape a string for safe HTML insertion.
 * @param {string} s
 * @returns {string}
 */
export function esc(s) {
  if (!s) return "";
  const d = document.createElement("div");
  d.textContent = s;
  return d.innerHTML;
}

/**
 * Map a 1-10 health score to a CSS color variable.
 * @param {number} score
 * @returns {string} CSS variable reference
 */
export function hColor(score) {
  if (score >= 8) return "var(--green)";
  if (score >= 6) return "var(--yellow)";
  if (score >= 4) return "var(--orange)";
  return "var(--red)";
}

/**
 * Map a 0-1 severity float to a severity keyword.
 * @param {number} sev
 * @returns {"critical"|"high"|"medium"|"low"|"info"}
 */
export function sevKey(sev) {
  if (sev >= 0.9) return "critical";
  if (sev >= 0.8) return "high";
  if (sev >= 0.6) return "medium";
  if (sev >= 0.4) return "low";
  return "info";
}

/**
 * Choose a CSS color variable based on signal polarity and value.
 * @param {string} key - Signal name
 * @param {number} val - Signal value
 * @returns {string} CSS variable reference
 */
export function polarColor(key, val) {
  const p = SIGNAL_POLARITY[key];
  if (p == null) return "var(--accent)";

  let v = val;
  if (UNBOUNDED_SIGNAL_CAPS[key]) {
    v = Math.min(val / UNBOUNDED_SIGNAL_CAPS[key], 1.0);
  }

  if (p === true) {
    return v > 0.5 ? "var(--red)" : v > 0.2 ? "var(--orange)" : "var(--text)";
  }
  if (p === false) {
    return v > 0.7 ? "var(--green)" : v < 0.3 ? "var(--orange)" : "var(--text)";
  }
  return "var(--accent)";
}
