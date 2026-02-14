/**
 * Signal interpretation functions.
 * Given a signal key and its numeric value, returns a short human-readable
 * interpretation string (e.g., "High - many files depend on this").
 *
 * These are displayed inline next to metric values so users understand
 * what numbers mean without needing tooltips or external documentation.
 */

/**
 * Interpret a signal value and return a short context string.
 * @param {string} key - Signal key name
 * @param {*} val - Signal value
 * @returns {string|null} Interpretation text, or null if no interpretation applies
 */
export function interpretSignal(key, val) {
  if (val == null) return null;
  if (typeof val === "boolean") {
    if (key === "is_orphan") return val ? "Not imported by any file" : "Connected in the graph";
    return null;
  }
  if (typeof val !== "number") return null;

  const fn = INTERPRETERS[key];
  return fn ? fn(val) : null;
}

/**
 * Get a health score label from a 1-10 score.
 * @param {number} score
 * @returns {{ label: string, description: string }}
 */
export function interpretHealth(score) {
  if (score >= 9) return { label: "Excellent", description: "Very clean codebase with minimal technical debt." };
  if (score >= 8) return { label: "Healthy", description: "Well-maintained code. Minor improvements possible." };
  if (score >= 7) return { label: "Good", description: "Generally solid. A few areas need attention." };
  if (score >= 6) return { label: "Moderate", description: "Some technical debt present. Focus on high-risk areas." };
  if (score >= 5) return { label: "Fair", description: "Notable issues found. Prioritize the riskiest files." };
  if (score >= 4) return { label: "Below Average", description: "Significant technical debt. Several areas need refactoring." };
  if (score >= 3) return { label: "Poor", description: "Many quality issues. Consider a focused cleanup effort." };
  return { label: "Critical", description: "Severe structural problems. Immediate attention recommended." };
}

/**
 * Interpret a risk score (0-1 scale, higher = worse).
 * @param {number} val
 * @returns {string}
 */
function interpretRisk(val) {
  if (val >= 0.7) return "Very high risk - prioritize for review";
  if (val >= 0.4) return "Elevated risk - warrants attention";
  if (val >= 0.15) return "Moderate risk";
  if (val >= 0.05) return "Low risk";
  return "Minimal risk";
}

const INTERPRETERS = {
  // -- Size & Complexity --
  lines(v) {
    if (v > 1000) return "Very large file - consider splitting";
    if (v > 500) return "Large file";
    if (v > 200) return "Medium-sized file";
    return "Small file";
  },
  function_count(v) {
    if (v > 30) return "Many functions - may do too much";
    if (v > 15) return "Moderate number of functions";
    return null;
  },
  class_count(v) {
    if (v > 5) return "Many classes - consider splitting";
    return null;
  },
  max_nesting(v) {
    if (v >= 6) return "Deeply nested - hard to follow";
    if (v >= 4) return "Moderately nested";
    if (v >= 2) return "Shallow nesting - easy to read";
    return "Flat structure";
  },
  cognitive_load(v) {
    if (v >= 15) return "Very complex - difficult to understand";
    if (v >= 10) return "Complex - requires careful reading";
    if (v >= 5) return "Moderate complexity";
    return "Simple and easy to understand";
  },

  // -- Graph Position --
  pagerank(v) {
    if (v >= 0.3) return "Core hub - many files depend on this";
    if (v >= 0.1) return "Important file in the dependency graph";
    if (v >= 0.01) return "Moderate centrality";
    return "Peripheral file - few dependencies";
  },
  betweenness(v) {
    if (v >= 0.3) return "Key bridge - sits between many file groups";
    if (v >= 0.1) return "Connects several parts of the codebase";
    if (v >= 0.01) return "Minor bridging role";
    return "Not a bridge between modules";
  },
  in_degree(v) {
    if (v >= 20) return "Heavily imported - changes here ripple widely";
    if (v >= 10) return "Widely imported";
    if (v >= 3) return "Moderately imported";
    if (v >= 1) return "Imported by a few files";
    return "Not imported by other files";
  },
  out_degree(v) {
    if (v >= 15) return "Many dependencies - tightly coupled";
    if (v >= 8) return "Moderate number of dependencies";
    if (v >= 1) return "Few dependencies";
    return "No external dependencies";
  },
  blast_radius_size(v) {
    if (v >= 30) return "Huge impact - changes affect many files";
    if (v >= 15) return "Large impact area";
    if (v >= 5) return "Moderate impact area";
    return "Small impact - changes are contained";
  },
  depth(v) {
    if (v >= 8) return "Very deep in dependency chain";
    if (v >= 4) return "Moderately deep";
    return "Near the surface of the graph";
  },

  // -- Code Health --
  stub_ratio(v) {
    if (v >= 0.5) return "Mostly stubs - largely unimplemented";
    if (v >= 0.2) return "Some empty functions present";
    if (v > 0) return "A few stubs";
    return "No empty functions";
  },
  phantom_import_count(v) {
    if (v >= 3) return "Several broken imports - will cause errors";
    if (v >= 1) return "Has broken import(s)";
    return "All imports resolve correctly";
  },
  compression_ratio(v) {
    if (v >= 0.8) return "Highly unique code";
    if (v >= 0.5) return "Some repetition present";
    if (v >= 0.3) return "Notable code duplication";
    return "Very repetitive - likely copy-pasted";
  },
  semantic_coherence(v) {
    if (v >= 0.7) return "Tightly focused on one concept";
    if (v >= 0.4) return "Reasonably focused";
    if (v >= 0.2) return "Mixes several concerns";
    return "Unfocused - does many unrelated things";
  },

  // -- Change History --
  total_changes(v) {
    if (v >= 100) return "Very frequently changed (hotspot)";
    if (v >= 50) return "Frequently changed";
    if (v >= 20) return "Moderately active";
    if (v >= 5) return "Occasionally changed";
    return "Rarely changed";
  },
  churn_trajectory(v) {
    if (v > 0.5) return "Changes are increasing over time";
    if (v > 0.1) return "Slightly increasing activity";
    if (v > -0.1) return "Stable change rate";
    if (v > -0.5) return "Activity is decreasing";
    return "Changes are declining sharply";
  },
  churn_cv(v) {
    if (v >= 2.0) return "Very erratic - unpredictable changes";
    if (v >= 1.0) return "Unstable - irregular change pattern";
    if (v >= 0.5) return "Moderately variable";
    return "Stable - steady, predictable changes";
  },
  bus_factor(v) {
    if (v >= 4) return "Widely understood by the team";
    if (v >= 2.5) return "Good knowledge spread";
    if (v >= 1.5) return "A few people know this code";
    return "Single-author risk - only 1 person knows this";
  },
  author_entropy(v) {
    if (v >= 2.0) return "Many contributors";
    if (v >= 1.0) return "A few contributors";
    return "Dominated by one author";
  },
  fix_ratio(v) {
    if (v >= 0.5) return "Most changes are bug fixes - error-prone code";
    if (v >= 0.3) return "Many bug-fix commits";
    if (v >= 0.1) return "Some bug-fix commits";
    return "Few or no bug fixes needed";
  },
  change_entropy(v) {
    if (v >= 2.0) return "Changes spread across many areas";
    if (v >= 1.0) return "Changes in several areas";
    return "Changes concentrated in one area";
  },

  // -- Computed Risk --
  risk_score: interpretRisk,
  raw_risk: interpretRisk,
  wiring_quality(v) {
    if (v >= 0.8) return "Clean dependency structure";
    if (v >= 0.5) return "Acceptable wiring";
    if (v >= 0.3) return "Messy dependencies - needs cleanup";
    return "Poor dependency structure";
  },
  file_health_score(v) {
    if (v >= 8) return "Healthy file";
    if (v >= 6) return "Some concerns";
    if (v >= 4) return "Needs attention";
    return "Significant problems";
  },
};
