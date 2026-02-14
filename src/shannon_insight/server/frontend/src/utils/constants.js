/**
 * Signal display labels, categories, and polarity mappings.
 * Single source of truth for signal metadata across all components.
 *
 * Each signal has a clear human-readable label and a short description
 * explaining what it measures, so users never need tooltips.
 */

export const SIGNAL_LABELS = {
  lines: "Lines of Code",
  function_count: "Function Count",
  class_count: "Classes / Structs",
  max_nesting: "Deepest Nesting Level",
  cognitive_load: "Cognitive Complexity",
  pagerank: "Import Centrality (PageRank)",
  betweenness: "Bridge Score (Betweenness)",
  in_degree: "Imported By (in-degree)",
  out_degree: "Depends On (out-degree)",
  blast_radius_size: "Change Impact Size",
  depth: "Dependency Chain Depth",
  stub_ratio: "Stub / Empty Function Ratio",
  is_orphan: "Orphan (no imports or importers)",
  phantom_import_count: "Broken Imports",
  compression_ratio: "Code Uniqueness (compression)",
  semantic_coherence: "Code Focus (coherence)",
  total_changes: "Total Commits",
  churn_trajectory: "Change Trend (rising / falling)",
  churn_cv: "Change Volatility (CV)",
  bus_factor: "Team Knowledge Spread",
  author_entropy: "Author Diversity",
  fix_ratio: "Bug-Fix Commit Ratio",
  change_entropy: "Change Distribution",
  risk_score: "Overall Risk Score",
  wiring_quality: "Dependency Health",
  file_health_score: "File Health Score",
  raw_risk: "Raw Risk (pre-normalization)",
};

/**
 * Short descriptions shown inline under signal values
 * to explain what each metric actually measures.
 */
export const SIGNAL_DESCRIPTIONS = {
  lines: "Total lines in the file",
  function_count: "Number of functions / methods defined",
  class_count: "Number of classes or structs defined",
  max_nesting: "Deepest level of nested blocks (if/for/while)",
  cognitive_load: "How hard this file is to understand",
  pagerank: "How central this file is in the import graph",
  betweenness: "How often this file bridges between other files",
  in_degree: "Number of files that import this file",
  out_degree: "Number of files this file imports",
  blast_radius_size: "How many files could be affected by a change here",
  depth: "Longest chain of imports from this file to a leaf",
  stub_ratio: "Fraction of functions that are empty or trivial",
  is_orphan: "This file is not imported by any other file",
  phantom_import_count: "Imports that point to files that do not exist",
  compression_ratio: "Lower means more repetitive / duplicated code",
  semantic_coherence: "How focused this file is on a single concept",
  total_changes: "How many times this file has been committed",
  churn_trajectory: "Whether changes are increasing or decreasing over time",
  churn_cv: "How erratic the change pattern is (high = unstable)",
  bus_factor: "How many people understand this code (higher = safer)",
  author_entropy: "How evenly distributed authorship is",
  fix_ratio: "Fraction of commits that were bug fixes",
  change_entropy: "How evenly changes are spread across the file",
  risk_score: "Combined risk from complexity, churn, and coupling",
  wiring_quality: "How clean the file's import/export structure is",
  file_health_score: "Overall health combining all signals (1-10)",
  raw_risk: "Risk score before percentile normalization",
};

export const SIGNAL_CATEGORIES = [
  {
    key: "size",
    name: "Size & Complexity",
    signals: ["lines", "function_count", "class_count", "max_nesting", "cognitive_load"],
  },
  {
    key: "structure",
    name: "Graph Position",
    signals: ["pagerank", "betweenness", "in_degree", "out_degree", "blast_radius_size", "depth"],
  },
  {
    key: "health",
    name: "Code Health",
    signals: [
      "stub_ratio",
      "is_orphan",
      "phantom_import_count",
      "compression_ratio",
      "semantic_coherence",
    ],
  },
  {
    key: "temporal",
    name: "Change History",
    signals: ["total_changes", "churn_trajectory", "churn_cv", "fix_ratio", "change_entropy"],
  },
  {
    key: "team",
    name: "Team Context",
    signals: ["author_entropy", "bus_factor"],
  },
  {
    key: "risk",
    name: "Computed Risk",
    signals: ["risk_score", "wiring_quality", "file_health_score", "raw_risk"],
  },
];

/**
 * Signal polarity: true = higher is worse, false = higher is better, null = neutral.
 */
export const SIGNAL_POLARITY = {
  risk_score: true,
  raw_risk: true,
  churn_cv: true,
  cognitive_load: true,
  max_nesting: true,
  stub_ratio: true,
  phantom_import_count: true,
  fix_ratio: true,
  blast_radius_size: true,
  wiring_quality: false,
  file_health_score: false,
  semantic_coherence: false,
  bus_factor: false,
  compression_ratio: false,
  pagerank: null,
  betweenness: null,
  in_degree: null,
  out_degree: null,
  depth: null,
  lines: null,
  function_count: null,
  class_count: null,
  total_changes: null,
  author_entropy: null,
};

/** Category display order and labels. */
export const CATEGORY_ORDER = ["incomplete", "fragile", "tangled", "team"];
export const CATEGORY_LABELS = {
  incomplete: "Incomplete",
  fragile: "Fragile",
  tangled: "Tangled",
  team: "Team",
};

/** Screen identifiers for navigation. */
export const SCREENS = ["overview", "issues", "files", "modules", "health"];

/** Severity levels for filter chips. */
export const SEVERITY_LEVELS = ["critical", "high", "medium", "low", "info"];

/** Upper bounds for unbounded integer signals (used for color normalization). */
export const UNBOUNDED_SIGNAL_CAPS = {
  blast_radius_size: 50,
  phantom_import_count: 5,
  cognitive_load: 25,
  max_nesting: 10,
};
