/**
 * Pure formatting functions. No side effects, no DOM access.
 * Each function transforms a value into a display string.
 */

/**
 * Format a number for compact display (e.g., 1200 -> "1.2k").
 * @param {number|null|undefined} n
 * @returns {string}
 */
export function fmtN(n) {
  if (n == null) return "--";
  if (n >= 1000) return (n / 1000).toFixed(1) + "k";
  return String(n);
}

/**
 * Format a float to a fixed number of decimal places.
 * @param {number|null|undefined} n
 * @param {number} [decimals=2]
 * @returns {string}
 */
export function fmtF(n, decimals) {
  if (n == null) return "--";
  return n.toFixed(decimals != null ? decimals : 2);
}

/**
 * Format a signal value for display, applying signal-specific rules.
 * @param {string} key - Signal name
 * @param {*} val - Signal value
 * @returns {string}
 */
export function fmtSigVal(key, val) {
  if (val == null) return "--";
  if (typeof val === "boolean") return val ? "Yes" : "No";
  if (typeof val !== "number") return String(val);

  const RATIO_SIGNALS = new Set(["stub_ratio", "fix_ratio", "compression_ratio", "semantic_coherence"]);
  if (RATIO_SIGNALS.has(key)) return (val * 100).toFixed(1) + "%";

  const SCORE_SIGNALS = new Set(["risk_score", "raw_risk", "wiring_quality", "file_health_score"]);
  if (SCORE_SIGNALS.has(key)) return val.toFixed(3);

  const PRECISION_SIGNALS = new Set([
    "pagerank", "betweenness", "churn_cv", "author_entropy", "change_entropy", "churn_trajectory",
  ]);
  if (PRECISION_SIGNALS.has(key)) return val.toFixed(4);

  if (Number.isInteger(val)) return String(val);
  return val.toFixed(2);
}
