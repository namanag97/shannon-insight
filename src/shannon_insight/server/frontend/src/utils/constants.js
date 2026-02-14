/**
 * Signal display labels, categories, and polarity mappings.
 * Single source of truth for signal metadata across all components.
 */

export const SIGNAL_LABELS = {
  lines: "Lines of code",
  function_count: "Functions",
  class_count: "Classes/Structs",
  max_nesting: "Max nesting depth",
  cognitive_load: "Cognitive load",
  pagerank: "PageRank centrality",
  betweenness: "Betweenness centrality",
  in_degree: "Files that import this",
  out_degree: "Files this imports",
  blast_radius_size: "Blast radius",
  depth: "DAG depth",
  stub_ratio: "Stub/empty functions",
  is_orphan: "Is orphan",
  phantom_import_count: "Missing imports",
  compression_ratio: "Compression ratio",
  semantic_coherence: "Semantic coherence",
  total_changes: "Total commits",
  churn_trajectory: "Churn trend",
  churn_cv: "Churn volatility",
  bus_factor: "Bus factor",
  author_entropy: "Author diversity",
  fix_ratio: "Bugfix ratio",
  change_entropy: "Change distribution",
  risk_score: "Risk score",
  wiring_quality: "Wiring quality",
  file_health_score: "File health",
  raw_risk: "Raw risk",
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
