/**
 * Signal display labels, categories, and polarity mappings.
 * Single source of truth for signal metadata across all components.
 *
 * Each signal has a clear human-readable label and a short description
 * explaining what it measures, so users never need tooltips.
 */

export const SIGNAL_LABELS = {
  // Size & Complexity
  lines: "Lines of Code",
  function_count: "Function Count",
  class_count: "Classes / Structs",
  max_nesting: "Deepest Nesting Level",
  nesting_depth: "Average Nesting Depth",
  cognitive_load: "Cognitive Complexity",
  todo_density: "TODO / FIXME Density",

  // Structural / Graph
  pagerank: "Import Centrality (PageRank)",
  betweenness: "Bridge Score (Betweenness)",
  in_degree: "Imported By (in-degree)",
  out_degree: "Depends On (out-degree)",
  import_count: "Total Import Statements",
  blast_radius_size: "Change Impact Size",
  depth: "Dependency Chain Depth",
  community: "Graph Community ID",
  network_centrality: "Network Centrality Score",
  structural_entropy: "Dependency Entropy",

  // Code Health / Quality
  stub_ratio: "Stub / Empty Function Ratio",
  is_orphan: "Orphan (no imports or importers)",
  phantom_import_count: "Broken Imports",
  broken_call_count: "Broken Function Calls",
  compression_ratio: "Code Uniqueness (compression)",
  semantic_coherence: "Code Focus (coherence)",
  docstring_coverage: "Documentation Coverage",
  naming_drift: "Naming Inconsistency",
  impl_gini: "Implementation Distribution",
  role: "File Role (Entry/Model/Test/etc)",
  percentiles: "Signal Percentile Rankings",

  // Temporal / Churn
  total_changes: "Total Commits",
  churn_trajectory: "Change Trend (rising / falling)",
  trajectory: "Change Trajectory Classification",
  churn_cv: "Change Volatility (CV)",
  churn_slope: "Change Rate Slope",
  churn_volatility: "Churn Volatility",
  fix_ratio: "Bug-Fix Commit Ratio",
  refactor_ratio: "Refactor Commit Ratio",
  change_entropy: "Change Distribution",

  // Team / Ownership
  bus_factor: "Team Knowledge Spread",
  author_entropy: "Author Diversity",

  // Composite / Scores
  risk_score: "Overall Risk Score",
  wiring_quality: "Dependency Health",
  file_health_score: "File Health Score",
  raw_risk: "Raw Risk (pre-normalization)",
  concept_count: "Semantic Concept Count",
  concept_entropy: "Concept Diversity",

  // API-level fields (top-level, not in signals dict)
  health: "File Health (1-10 scale)",
  blast_radius: "Change Impact Size",
  finding_count: "Number of Findings",
};

/**
 * Short descriptions shown inline under signal values
 * to explain what each metric actually measures.
 */
export const SIGNAL_DESCRIPTIONS = {
  // Size & Complexity
  lines: "Total lines in the file",
  function_count: "Number of functions / methods defined",
  class_count: "Number of classes or structs defined",
  max_nesting: "Deepest level of nested blocks (if/for/while)",
  nesting_depth: "Average nesting depth across all blocks",
  cognitive_load: "How hard this file is to understand (cyclomatic complexity)",
  todo_density: "Number of TODO/FIXME comments per 100 LOC",

  // Structural / Graph
  pagerank: "How central this file is in the import graph",
  betweenness: "How often this file bridges between other files",
  in_degree: "Number of files that import this file",
  out_degree: "Number of files this file imports",
  import_count: "Total number of import statements",
  blast_radius_size: "How many files could be affected by a change here",
  depth: "Longest chain of imports from this file to a leaf",
  community: "Louvain modularity community this file belongs to",
  network_centrality: "Combined centrality score in dependency network",
  structural_entropy: "Dependency pattern complexity (information-theoretic)",

  // Code Health / Quality
  stub_ratio: "Fraction of functions that are empty or trivial",
  is_orphan: "This file is not imported by any other file",
  phantom_import_count: "Imports that point to files that do not exist",
  broken_call_count: "Function calls that cannot be resolved",
  compression_ratio: "Lower means more repetitive / duplicated code",
  semantic_coherence: "How focused this file is on a single concept",
  docstring_coverage: "Fraction of functions with documentation",
  naming_drift: "Naming pattern inconsistency across identifiers",
  impl_gini: "How evenly code is distributed across functions (Gini coefficient)",
  role: "Semantic role: ENTRY_POINT, MODEL, CONTROLLER, UTILITY, TEST, etc",
  percentiles: "Percentile rankings (0-100) for all numeric signals",

  // Temporal / Churn
  total_changes: "How many times this file has been committed",
  churn_trajectory: "Whether changes are increasing or decreasing over time",
  trajectory: "Change pattern classification (STABILIZING, SURGING, etc.)",
  churn_cv: "How erratic the change pattern is (coefficient of variation)",
  churn_slope: "Rate of change increase/decrease over time",
  churn_volatility: "Standard deviation of changes over time",
  fix_ratio: "Fraction of commits that were bug fixes",
  refactor_ratio: "Fraction of commits that were refactors",
  change_entropy: "How evenly changes are spread across the file",

  // Team / Ownership
  bus_factor: "How many people understand this code (higher = safer)",
  author_entropy: "How evenly distributed authorship is",

  // Composite / Scores
  risk_score: "Combined risk from complexity, churn, and coupling",
  wiring_quality: "How clean the file's import/export structure is",
  file_health_score: "Overall health combining all signals (1-10)",
  raw_risk: "Risk score before percentile normalization",
  concept_count: "Number of distinct semantic concepts identified",
  concept_entropy: "Diversity of semantic concepts in the file",

  // API-level fields
  health: "Display health score (1-10 scale, transformed from file_health_score)",
  blast_radius: "How many files would be affected by changes to this file",
  finding_count: "Total number of code quality findings for this file",
};

export const SIGNAL_CATEGORIES = [
  {
    key: "size",
    name: "Size and Complexity",
    description: "How large and complex the file is",
    signals: ["lines", "function_count", "class_count", "max_nesting", "nesting_depth", "cognitive_load", "todo_density"],
  },
  {
    key: "structure",
    name: "Position in Dependency Graph",
    description: "How this file relates to other files through imports",
    signals: ["pagerank", "betweenness", "network_centrality", "in_degree", "out_degree", "import_count", "blast_radius_size", "depth", "community", "structural_entropy"],
  },
  {
    key: "health",
    name: "Code Quality Indicators",
    description: "Signs of code health or decay",
    signals: [
      "stub_ratio",
      "is_orphan",
      "phantom_import_count",
      "broken_call_count",
      "compression_ratio",
      "semantic_coherence",
      "docstring_coverage",
      "naming_drift",
      "impl_gini",
      "role",
    ],
  },
  {
    key: "semantics",
    name: "Semantic Structure",
    description: "Conceptual organization and meaning",
    signals: ["concept_count", "concept_entropy"],
  },
  {
    key: "temporal",
    name: "Change History and Patterns",
    description: "How this file has been changing over time",
    signals: ["total_changes", "churn_trajectory", "trajectory", "churn_cv", "churn_slope", "churn_volatility", "fix_ratio", "refactor_ratio", "change_entropy"],
  },
  {
    key: "team",
    name: "Team and Ownership",
    description: "Who works on this file and how spread out the knowledge is",
    signals: ["author_entropy", "bus_factor"],
  },
  {
    key: "risk",
    name: "Computed Risk Scores",
    description: "Combined risk metrics from all signals above",
    signals: ["risk_score", "wiring_quality", "file_health_score", "raw_risk"],
  },
];

/**
 * Signal polarity: true = higher is worse, false = higher is better, null = neutral.
 */
export const SIGNAL_POLARITY = {
  // Higher is WORSE
  risk_score: true,
  raw_risk: true,
  churn_cv: true,
  churn_volatility: true,
  cognitive_load: true,
  max_nesting: true,
  nesting_depth: true,
  stub_ratio: true,
  phantom_import_count: true,
  broken_call_count: true,
  fix_ratio: true,
  blast_radius_size: true,
  todo_density: true,
  naming_drift: true,
  impl_gini: true,
  structural_entropy: true,

  // Higher is BETTER
  wiring_quality: false,
  file_health_score: false,
  semantic_coherence: false,
  bus_factor: false,
  compression_ratio: false,
  docstring_coverage: false,
  network_centrality: false,

  // NEUTRAL (context-dependent)
  pagerank: null,
  betweenness: null,
  in_degree: null,
  out_degree: null,
  import_count: null,
  depth: null,
  lines: null,
  function_count: null,
  class_count: null,
  total_changes: null,
  author_entropy: null,
  churn_trajectory: null,
  trajectory: null,
  churn_slope: null,
  refactor_ratio: null,
  change_entropy: null,
  community: null,
  concept_count: null,
  concept_entropy: null,
};

/** Category display order and labels. */
export const CATEGORY_ORDER = ["incomplete", "fragile", "tangled", "team"];
export const CATEGORY_LABELS = {
  incomplete: "Incomplete Code",
  fragile: "Fragile / Risky Code",
  tangled: "Tangled Dependencies",
  team: "Team / Ownership Risks",
};
export const CATEGORY_DESCRIPTIONS = {
  incomplete: "Stubs, dead code, and missing implementations",
  fragile: "Code that breaks easily due to complexity or tight coupling",
  tangled: "Circular dependencies, hidden coupling, and messy imports",
  team: "Single-author files, knowledge silos, and bus factor risks",
};

/** Module signal labels and descriptions */
export const MODULE_SIGNAL_LABELS = {
  abstractness: "Abstraction Level",
  boundary_alignment: "Boundary Alignment",
  cohesion: "Internal Cohesion",
  coordination_cost: "Team Coordination Cost",
  coupling: "External Coupling",
  file_count: "File Count",
  health_score: "Module Health Score",
  instability: "Change Sensitivity",
  knowledge_gini: "Knowledge Concentration",
  layer_violation_count: "Layer Violations",
  main_seq_distance: "Distance from Main Sequence",
  mean_cognitive_load: "Average Complexity",
  module_bus_factor: "Module Bus Factor",
  role_consistency: "Role Consistency",
  velocity: "Change Velocity",
};

export const MODULE_SIGNAL_DESCRIPTIONS = {
  abstractness: "Ratio of abstract types to total types (0=concrete, 1=abstract)",
  boundary_alignment: "How well module boundaries align with coupling patterns",
  cohesion: "How tightly related the files within the module are",
  coordination_cost: "Team coordination overhead for this module",
  coupling: "Average coupling to other modules",
  file_count: "Number of files in this module",
  health_score: "Overall module health score (1-10)",
  instability: "Change sensitivity (0=stable, 1=unstable)",
  knowledge_gini: "Knowledge distribution inequality (higher = more concentrated)",
  layer_violation_count: "Number of architectural layer violations",
  main_seq_distance: "Distance from ideal abstraction/stability balance",
  mean_cognitive_load: "Average cognitive complexity across module files",
  module_bus_factor: "How many people understand this module",
  role_consistency: "How consistent file roles are within the module",
  velocity: "Rate of change over time",
};

export const MODULE_SIGNAL_CATEGORIES = [
  {
    key: "architecture",
    name: "Architecture Metrics",
    description: "Martin metrics and architectural properties",
    signals: ["abstractness", "instability", "coupling", "cohesion", "main_seq_distance", "layer_violation_count"],
  },
  {
    key: "quality",
    name: "Quality Indicators",
    description: "Code quality and organizational health",
    signals: ["health_score", "boundary_alignment", "role_consistency", "mean_cognitive_load"],
  },
  {
    key: "team",
    name: "Team Dynamics",
    description: "Ownership and coordination patterns",
    signals: ["module_bus_factor", "knowledge_gini", "coordination_cost"],
  },
  {
    key: "temporal",
    name: "Change Patterns",
    description: "How the module evolves over time",
    signals: ["velocity", "file_count"],
  },
];

export const MODULE_SIGNAL_POLARITY = {
  // Higher is WORSE
  coupling: true,
  coordination_cost: true,
  knowledge_gini: true,
  layer_violation_count: true,
  main_seq_distance: true,
  mean_cognitive_load: true,

  // Higher is BETTER
  abstractness: false,
  boundary_alignment: false,
  cohesion: false,
  health_score: false,
  module_bus_factor: false,
  role_consistency: false,

  // NEUTRAL
  instability: null,
  velocity: null,
  file_count: null,
};

/** Screen identifiers for navigation. */
export const SCREENS = ["overview", "issues", "files", "modules", "health", "graph", "churn", "signals"];

/** Severity levels for filter chips. */
export const SEVERITY_LEVELS = ["critical", "high", "medium", "low", "info"];

/** Upper bounds for unbounded integer signals (used for color normalization). */
export const UNBOUNDED_SIGNAL_CAPS = {
  blast_radius_size: 50,
  phantom_import_count: 5,
  cognitive_load: 25,
  max_nesting: 10,
};
