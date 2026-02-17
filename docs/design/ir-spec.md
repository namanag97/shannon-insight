# Shannon Insight — Intermediate Representation Specification

## The Two-Dimensional Model

Analysis is not a pipeline — it's a **matrix**. The vertical axis is abstraction level (IR0→IR7). The horizontal axis is time (git commits/snapshots).

```
              t₀         t₁         t₂         t₃         now
           ┌──────────┬──────────┬──────────┬──────────┬──────────┐
IR0 Files  │ files₀   │ files₁   │ files₂   │ files₃   │ files₄   │
           ├──────────┼──────────┼──────────┼──────────┼──────────┤
IR1 Syntax │ syntax₀  │ syntax₁  │ syntax₂  │ syntax₃  │ syntax₄  │
           ├──────────┼──────────┼──────────┼──────────┼──────────┤
IR2 Semant │ sem₀     │ sem₁     │ sem₂     │ sem₃     │ sem₄     │
           ├──────────┼──────────┼──────────┼──────────┼──────────┤
IR3 Graph  │ graph₀   │ graph₁   │ graph₂   │ graph₃   │ graph₄   │
           ├──────────┼──────────┼──────────┼──────────┼──────────┤
IR4 Arch   │ arch₀    │ arch₁    │ arch₂    │ arch₃    │ arch₄    │
           ├──────────┼──────────┼──────────┼──────────┼──────────┤
IR5 Signal │ sigs₀    │ sigs₁    │ sigs₂    │ sigs₃    │ sigs₄    │
           ├──────────┼──────────┼──────────┼──────────┼──────────┤
IR6 Insigh │ ins₀     │ ins₁     │ ins₂     │ ins₃     │ ins₄     │
           └──────────┴──────────┴──────────┴──────────┴──────────┘

Vertical (↓) = abstraction transforms: parsing, classifying, graph-building, pattern-matching
Horizontal (→) = temporal transforms: deltas, trends, trajectories, regressions
Diagonal (↘) = evolution questions: "how did this file's ROLE change as the GRAPH grew?"
```

Every cell is a snapshot. Every row is a time series. Every column is a full analysis at one point in time.

**The temporal model is not a separate IR** — it's the analysis of how each IR changes along the time axis.

---

## IR0: FileSystem

**What it captures**: What exists on disk. The raw material.

### Snapshot Data Model

```
FileEntry:
  path:      str              # relative to project root
  content:   bytes            # raw file content
  size:      int              # byte count
  hash:      str              # content SHA-256 (change detection)
  language:  Language          # detected: python, go, typescript, ...
  mtime:     datetime          # last modified timestamp
```

### What We Collect

| Field | Source | Cost |
|-------|--------|------|
| path, size, mtime | filesystem stat | O(n), trivial |
| content | file read | O(n), I/O bound |
| hash | SHA-256 of content | O(n), CPU cheap |
| language | extension + header heuristic | O(n), trivial |

### Math: None

This is raw data. No computation. But the **hash** is critical — it's how we detect changes between time points without diffing content.

### Temporal (IR0 over time)

**Delta(t₁, t₂):**

```
FileSystemDelta:
  added:    [FileEntry]          # hash not in t₁
  removed:  [FileEntry]          # hash not in t₂
  modified: [(path, hash₁, hash₂)]  # same path, different hash
  renamed:  [(old_path, new_path, similarity: float)]
```

Rename detection: files where `old` was removed and `new` was added with high content similarity.

```
similarity(a, b) = 1 - NCD(a, b)
rename if: similarity > 0.7 AND no file at old_path in t₂ AND no file at new_path in t₁
```

**Time series (IR0 across all t):**

| Metric | Formula | What it reveals |
|--------|---------|-----------------|
| file_count(t) | \|files at t\| | Growth curve — linear (healthy) vs exponential (bloat) |
| churn_rate(t) | \|modified\| / \|total\| per commit | How much changes per commit |
| language_entropy(t) | H({lang: count/total}) | Polyglot drift — are new languages creeping in? |
| growth_acceleration | d²(file_count)/dt² | Is growth speeding up or slowing down? |

---

## IR1: SyntacticForm

**What it captures**: The structural content of each file — functions, classes, imports — with enough detail for per-function analysis.

### Snapshot Data Model

```
FileSyntax:
  path:       str
  functions:  [FunctionDef]
  classes:    [ClassDef]
  imports:    [ImportDecl]
  top_level:  int              # non-function, non-class statements

FunctionDef:
  name:             str
  params:           [str]          # parameter names (+ types if available)
  return_type:      Optional[str]
  body_source:      str            # raw source of function body
  body_tokens:      int            # token count in body
  signature_tokens: int            # token count in signature line
  start_line:       int
  end_line:         int
  calls:            [str]          # identifiers called: ["db.query", "Token.create"]
  nesting_depth:    int            # max nesting within this function
  decorators:       [str]          # @staticmethod, @app.route("/login"), etc.

ClassDef:
  name:       str
  bases:      [str]              # parent classes
  methods:    [FunctionDef]      # references to function defs
  fields:     [str]              # instance attributes (from __init__ or annotations)
  is_abstract: bool              # has ABC base or all methods abstract

ImportDecl:
  source:        str             # "..models" or "bcrypt"
  names:         [str]           # ["User", "Token"] or ["*"]
  is_relative:   bool
  resolved_path: Optional[str]   # None = unresolved (phantom candidate)
  is_external:   bool            # not in project tree
```

### What We Collect

| Field | Source | Technique | Cost |
|-------|--------|-----------|------|
| functions, classes | AST parse | `ast.parse()` (Python), regex (others) | O(n) per file |
| body_tokens | tokenize body source | split + count | trivial |
| calls | AST walk for Call nodes | `ast.walk()` or regex `\w+\(` | O(n) per function |
| resolved_path | import resolution | path lookup + package resolution | O(imports) |
| fields | `__init__` body scan or class annotations | AST | O(methods) |

### Math at IR1

**Per-function stub score:**

```
stub_score(f) = 1 - min(1, body_tokens(f) / (signature_tokens(f) × k))
```

Where `k` is a scaling factor (~3). A function with 8 signature tokens should have at least 24 body tokens to not be a stub. `stub_score` ∈ [0, 1], 1 = definitely a stub.

Simpler hard classification:
```
is_stub(f) = body_tokens(f) < 5
          OR body_source(f) matches /^\s*(pass|\.\.\.|\breturn\s+None\b)\s*$/
```

**Implementation Gini (per file):**

```
sizes = [body_tokens(f) for f in file.functions]
gini = gini_coefficient(sizes)
```

- Gini ≈ 0: all functions similar size (uniform implementation)
- Gini > 0.6: huge variance (some functions complete, others stubs = AI signature)

**Function size entropy:**

```
p_i = body_tokens(f_i) / Σ body_tokens
H = -Σ p_i × log₂(p_i)
H_max = log₂(|functions|)
evenness = H / H_max
```

Low evenness = one or two functions contain all the logic, rest are shells.

### Temporal (IR1 over time)

**Delta(t₁, t₂) per file:**

```
SyntaxDelta:
  functions_added:    [FunctionDef]
  functions_removed:  [FunctionDef]
  functions_modified: [(FunctionDef_old, FunctionDef_new)]
  imports_added:      [ImportDecl]
  imports_removed:    [ImportDecl]
```

Function matching across versions: match by name (exact), then by signature similarity for renames.

```
match(f₁, f₂) = (f₁.name == f₂.name) OR
                 (jaccard(f₁.params, f₂.params) > 0.8 AND levenshtein(f₁.name, f₂.name) < 3)
```

**Time series per file:**

| Metric | Formula | What it reveals |
|--------|---------|-----------------|
| function_count(t) | \|functions\| | Is file growing (scope creep) or shrinking (refactoring)? |
| mean_body_tokens(t) | avg(body_tokens) | Are functions getting bigger (complexity) or smaller (decomposition)? |
| stub_ratio(t) | \|stubs\| / \|functions\| | Are stubs being filled in over time? (AI code completion tracking) |
| import_count(t) | \|imports\| | Dependency growth |
| impl_gini(t) | gini(body_tokens) | Is implementation becoming more even? |

**Stub fill-in velocity** (unique to AI code tracking):
```
fill_rate = Δ(stub_count) / Δt
```
Positive = stubs being filled. Negative = new stubs appearing faster than old ones are filled.

---

## IR2: SemanticForm

**What it captures**: What each file *means* — its role in the system, the concepts it deals with, its API surface and completeness. This is the first layer of "understanding."

### Snapshot Data Model

```
FileSemantics:
  path:          str
  role:          Role
  concepts:      [Concept]
  public_api:    [Symbol]
  consumed_api:  [ConsumedSymbol]
  completeness:  Completeness

Role: enum
  MODEL        # data structures, schemas, DTOs
  SERVICE      # business logic with state/deps
  UTILITY      # stateless helper functions
  CONFIG       # settings, constants, env vars
  TEST         # test code
  CLI          # command-line interface
  INTERFACE    # abstract classes, protocols, ABCs
  EXCEPTION    # custom exception definitions
  CONSTANT     # module-level constants
  ENTRY_POINT  # main, __main__, wsgi, asgi
  MIGRATION    # DB migrations
  UNKNOWN

Concept:
  topic:    str          # dominant token: "auth", "payment", "cache"
  tokens:   [str]        # all tokens in this cluster
  weight:   float        # fraction of identifiers belonging to this concept

Symbol:
  name:     str          # "AuthService", "authenticate"
  kind:     FUNCTION | CLASS | CONSTANT | TYPE
  params:   Optional[int]  # parameter count for functions

ConsumedSymbol:
  source_file:   str     # where it's imported from
  symbols_used:  [str]   # what's actually referenced in the code (not just imported)

Completeness:
  stub_ratio:          float   # from IR1
  implementation_gini: float   # from IR1
  docstring_coverage:  float   # documented public symbols / total public symbols
  todo_density:        float   # TODO/FIXME count / lines
```

### How Each Field Is Computed

**Role classification** — decision tree on IR1 structural signals:

```
classify_role(file: FileSyntax) -> Role:
  if file.path matches test patterns:         return TEST
  if file.path matches migration patterns:    return MIGRATION
  if has_main_guard(file) or is_entry_point:  return ENTRY_POINT

  # Structural signals
  class_count    = |file.classes|
  fn_count       = |file.functions|
  has_abc        = any(c.is_abstract for c in file.classes)
  field_heavy    = any(|c.fields| > |c.methods| for c in file.classes)
  all_caps_ratio = top_level_ALL_CAPS / top_level_assignments
  has_state      = any(c.fields for c in file.classes)

  if has_abc:                                 return INTERFACE
  if all_caps_ratio > 0.8:                    return CONSTANT
  if field_heavy and class_count > 0:         return MODEL
  if has_state and fn_count > 2:              return SERVICE
  if class_count == 0 and fn_count > 0:       return UTILITY
  if imports_click_or_typer(file):            return CLI
  if all_exception_classes(file):             return EXCEPTION
  return UNKNOWN
```

No ML. Pattern matching on structural signals. ~80% accuracy which is sufficient — the value is in catching the 20% that are misclassified (role confusion = smell).

**Concept extraction** — TF-IDF + clustering:

```
1. Extract all identifiers from file (variable names, function names, etc.)
2. Split into sub-tokens: "getUserProfile" → ["get", "user", "profile"]
3. Build token frequency vector for this file
4. Weight by IDF across all project files: rare tokens = more distinctive
5. Build co-occurrence graph: edge between tokens that appear in same function
6. Community detection (Louvain) on co-occurrence graph → clusters
7. Each cluster = a Concept, topic = highest-TF-IDF token in cluster
```

**concept_weight** = |tokens in cluster| / |all tokens in file|

A well-focused file: 1 concept with weight > 0.7
A god file: 3+ concepts with weights 0.3, 0.3, 0.2, 0.2

**Consumed API** (what's actually used, not just imported):

```
for each import in file.imports:
  imported_names = import.names
  actually_used = [name for name in imported_names
                   if name appears in any function body or class body]
  consumed_api.append(ConsumedSymbol(import.resolved_path, actually_used))
```

Difference between imported and consumed = dead imports (more precise than current co-change heuristic).

### Math at IR2

**Naming drift** — cosine similarity between filename tokens and content concept tokens:

```
filename_tokens = split_identifier(stem(file.path))  # "auth_service" → {"auth", "service"}
content_tokens  = union(concept.tokens for concept in file.concepts, weighted by concept.weight)

drift = 1 - cosine_similarity(
  tfidf_vector(filename_tokens),
  tfidf_vector(content_tokens)
)
```

- drift ≈ 0: filename matches content perfectly ("auth_service.py" contains auth + service code)
- drift > 0.7: filename misleading ("auth_service.py" is actually about payment processing)

**Role consistency score** (per directory):

```
files_in_dir = [f for f in files if dirname(f.path) == dir]
roles = [f.role for f in files_in_dir]
consistency = max(Counter(roles).values()) / |roles|
```

- 1.0: all files have same role (focused module)
- 0.3: roles scattered (confused module)

**Concept entropy** (per file):

```
H_concepts = -Σ concept.weight × log₂(concept.weight)
```

- H = 0: single concept (perfectly focused)
- H > 1.5: many competing concepts (unfocused)

### Temporal (IR2 over time)

**Delta(t₁, t₂) per file:**

```
SemanticDelta:
  role_changed:        Optional[(Role_old, Role_new)]
  concepts_added:      [Concept]
  concepts_removed:    [Concept]
  concept_drift:       float        # cosine distance between concept vectors
  api_surface_delta:   int          # change in public symbol count
  completeness_delta:  float        # change in stub_ratio
```

**Concept drift** — the key temporal metric at this level:

```
v₁ = tfidf_vector(concepts at t₁)
v₂ = tfidf_vector(concepts at t₂)
drift(t₁, t₂) = 1 - cosine_similarity(v₁, v₂)
```

Cumulative drift from origin: `Σ drift(tᵢ, tᵢ₊₁)` over all time steps. High cumulative drift = file has wandered far from its original purpose.

**Time series per file:**

| Metric | Formula | What it reveals |
|--------|---------|-----------------|
| concept_count(t) | \|concepts\| | Scope creep (growing) or focusing (shrinking) |
| concept_drift(t) | cumulative cosine distance | Has the file wandered from its original purpose? |
| stub_ratio(t) | from IR1 | AI stubs being filled in? |
| api_surface(t) | \|public_api\| | Over-exposure growth |
| naming_drift(t) | filename vs content distance | Did someone repurpose this file without renaming? |

**Role transition matrix** (codebase-wide):

```
Count how many files transition from role A to role B across all time steps.

          MODEL  SERVICE  UTILITY  ...
MODEL       45      3       1
SERVICE      1     38       2
UTILITY      0      5      29
...

Off-diagonal = role confusion events. High count = architectural instability.
```

---

## IR3: RelationshipGraph

**What it captures**: How files connect to each other — not just "A imports B" but the full multi-dimensional relationship: imports, calls, type flow, data sharing.

### Snapshot Data Model

```
CodeGraph:
  nodes:       {path: FileNode}
  edges:       [Edge]
  unresolved:  [UnresolvedEdge]       # phantom imports / broken calls

FileNode:
  path:        str
  ir1:         FileSyntax             # back-reference
  ir2:         FileSemantics          # back-reference

Edge:
  source:      str                    # file path
  target:      str                    # file path
  type:        EdgeType               # IMPORT | CALL | TYPE_FLOW
  symbols:     [str]                  # what crosses the boundary
  weight:      int                    # |symbols|

EdgeType: enum
  IMPORT       # A has import statement referencing B
  CALL         # function in A calls function in B
  TYPE_FLOW    # A uses a type defined in B as param/return

UnresolvedEdge:
  source:      str
  target_ref:  str                    # the unresolvable reference
  type:        PHANTOM_IMPORT | BROKEN_CALL
  context:     str                    # line of code containing the reference

# ---- Derived (computed from graph) ----

GraphMetrics:
  # Centrality
  pagerank:        {path: float}      # importance via random walk
  betweenness:     {path: float}      # bridge score
  in_degree:       {path: int}        # how many files depend on this
  out_degree:      {path: int}        # how many files this depends on

  # Topology
  sccs:            [set[str]]         # strongly connected components (cycles)
  communities:     {path: int}        # Louvain community assignment
  modularity:      float              # Q score of community structure
  connected_comps: [set[str]]         # weakly connected components

  # Reachability
  blast_radius:    {path: set[str]}   # transitive reverse closure

  # Depth (NEW)
  depth:           {path: int}        # longest path from nearest entry point
  max_depth:       int

  # Spectral (NEW - detailed)
  fiedler_value:   float              # algebraic connectivity (2nd eigenvalue of L)
  spectral_gap:    float              # λ₂/λ₃ ratio
  eigenvalues:     [float]            # first k eigenvalues of Laplacian

  # Connectivity quality (NEW)
  orphans:         [str]              # in_degree=0, not entry point
  orphan_ratio:    float
  phantom_count:   int                # |unresolved edges|
  phantom_ratio:   float              # phantom / total edges
  internal_ratio:  float              # nodes with in>0 AND out>0 / total
  glue_deficit:    float              # 1 - internal_ratio
```

### How Multi-Edge Types Are Built

**IMPORT edges** (have today):
```
for file in files:
  for imp in file.ir1.imports:
    if imp.resolved_path:
      add_edge(file.path, imp.resolved_path, IMPORT, imp.names)
    else:
      add_unresolved(file.path, imp.source, PHANTOM_IMPORT)
```

**CALL edges** (NEW):
```
for file in files:
  for func in file.ir1.functions:
    for call in func.calls:
      target_file, target_func = resolve_call(call, file.ir1.imports, all_files)
      if target_file and target_file != file.path:
        add_edge(file.path, target_file, CALL, [call])
      elif target_file is None and not is_builtin(call):
        add_unresolved(file.path, call, BROKEN_CALL)
```

**TYPE_FLOW edges** (NEW):
```
for file in files:
  for func in file.ir1.functions:
    for param_type in func.params:
      defining_file = resolve_type(param_type, file.ir1.imports, all_files)
      if defining_file and defining_file != file.path:
        add_edge(file.path, defining_file, TYPE_FLOW, [param_type])
```

### Math at IR3

**PageRank** (existing — damped random walk):
```
PR(v) = (1-d)/N + d × Σ PR(u)/out_degree(u)   for all u → v
d = 0.85, iterate 20 times
```

**Betweenness** (shortest path bridge score):
```
B(v) = Σ σ(s,t|v) / σ(s,t)   for all pairs s,t ≠ v
where σ(s,t) = number of shortest paths from s to t
      σ(s,t|v) = number passing through v
```

**Blast radius** (BFS on reverse graph):
```
blast(v) = BFS_reachable(v, reverse(G))
```

**DAG depth** (NEW — longest path from entry points):
```
depth(v) = 0                              if v is entry point
         = max(depth(u) + 1 for u → v)   otherwise
         = -1                             if unreachable (orphan)
```

Computed via BFS from entry points on the forward graph. Unreachable nodes are orphans.

**Centrality Gini** (NEW — how concentrated is importance):
```
gini(pagerank values across all files)
```
- Gini > 0.7: a few files dominate (hub-and-spoke, fragile)
- Gini < 0.3: importance well-distributed (resilient)

**Edge type ratio** (NEW — relationship character):
```
import_only_ratio = |edges with only IMPORT| / |all edges|
```
High import_only_ratio = files import each other but don't actually call each other = possibly dead dependencies at scale.

**NCD for clone detection** (NEW — pairwise):
```
NCD(a, b) = (C(a⋅b) - min(C(a), C(b))) / max(C(a), C(b))

where C(x) = len(zlib.compress(x))
      a⋅b = concatenation of file contents
```

Pruning to make O(n²) feasible:
```
candidates = [(a,b) for a,b in all_pairs
              if a.language == b.language                    # same language
              and |a.size - b.size| / max(a.size, b.size) < 0.3  # similar size
              and minhash_jaccard(a, b) > 0.3]              # minhash pre-filter

clones = [(a,b,ncd) for a,b in candidates if NCD(a,b) < 0.3]
```

MinHash for pre-filtering:
```
for each file:
  tokens = trigrams(file.content)        # sliding window of 3 tokens
  signature = [min(hash(t, seed_i) for t in tokens) for seed_i in seeds[:64]]

jaccard_estimate(a, b) = |{i : sig_a[i] == sig_b[i]}| / 64
```

### Temporal (IR3 over time)

**Delta(t₁, t₂):**

```
GraphDelta:
  edges_added:          [Edge]
  edges_removed:        [Edge]
  edges_retyped:        [(Edge, old_types, new_types)]
  new_phantoms:         [UnresolvedEdge]
  resolved_phantoms:    [UnresolvedEdge]
  new_cycles:           [set[str]]       # SCCs that appeared
  broken_cycles:        [set[str]]       # SCCs that disappeared
  community_migration:  [(path, old_community, new_community)]
  pagerank_delta:       {path: float}
  modularity_delta:     float
  fiedler_delta:        float
```

**Graph edit distance** (normalized):
```
GED(G₁, G₂) = (|edges_added| + |edges_removed|) / (|E₁| + |E₂|) / 2
```
- GED ≈ 0: graph barely changed
- GED > 0.1 in one commit: major structural change (refactor or something broke)

**Time series:**

| Metric | Formula | What it reveals |
|--------|---------|-----------------|
| edge_count(t) | \|E\| | Coupling growth |
| density(t) | \|E\| / (\|V\| × (\|V\|-1)) | Is graph getting denser (more coupled)? |
| modularity(t) | Q from Louvain | Architecture quality trend |
| fiedler(t) | λ₂ of Laplacian | Connectivity robustness trend |
| cycle_count(t) | \|SCCs with size>1\| | Circular dependency accumulation |
| orphan_ratio(t) | \|orphans\| / \|V\| | Disconnection trend |
| centrality_gini(t) | gini(pagerank) | Is importance concentrating or distributing? |
| phantom_ratio(t) | phantoms / total edges | Are broken references accumulating? |

**Co-change enrichment** (git data joins graph edges):

For each edge (A → B) in the graph:
```
temporal_coupling(A, B) = cochange_lift(A, B) × cochange_confidence(A, B)
```

Edges with high structural weight BUT low temporal coupling = potentially dead.
Edges with zero structural weight BUT high temporal coupling = hidden coupling.

---

## IR4: ArchitecturalModel

**What it captures**: The system-level view — modules, layers, boundaries, architectural patterns. This is where files become a *system*.

### Snapshot Data Model

```
Architecture:
  modules:        [Module]
  layers:         [Layer]
  violations:     [Violation]
  patterns:       ArchPatterns
  health:         ArchHealth

Module:
  path:            str              # directory path
  files:           [str]
  role:            ModuleRole        # aggregated from file roles
  role_consistency: float            # what fraction of files agree on role
  cohesion:        float             # [0,1] internal edge density
  coupling:        float             # [0,1] external edge fraction
  instability:     float             # Ce / (Ca + Ce)  — Martin's metric
  abstractness:    float             # abstract symbols / total symbols
  main_seq_dist:   float             # |A + I - 1|

Layer:
  depth:          int               # 0 = foundation, higher = closer to user
  modules:        [str]             # module paths at this depth

Violation:
  source_module:  str
  target_module:  str
  source_layer:   int
  target_layer:   int
  type:           BACKWARD | SKIP    # importing lower→higher, or skipping layers
  edge_count:     int                # how many edges constitute this violation
  symbols:        [str]              # what's crossing the boundary

ArchPatterns:
  is_layered:      bool             # clear topological ordering exists
  is_modular:      bool             # high cohesion, low coupling
  has_god_module:  bool             # one module owns >40% of edges
  hub_and_spoke:   bool             # single orchestration module
  layer_count:     int
  max_module_size: int              # files in largest module

ArchHealth:
  violation_rate:     float         # violating edges / total cross-module edges
  mean_cohesion:      float
  mean_coupling:      float
  mean_main_seq_dist: float
  boundary_alignment: float         # how well directories match communities
```

### How Layers Are Inferred (no user config needed)

```
1. Collapse file graph to MODULE graph:
   module_graph[dir_a → dir_b] if any file in dir_a imports any file in dir_b

2. Topological sort of module graph (ignore back-edges = violations):
   Remove back-edges via DFS, topo-sort the resulting DAG

3. Assign layer depth:
   layer(m) = 0                                   if in_degree(m) == 0 in the DAG
            = max(layer(dep) + 1 for dep in m.deps) otherwise

4. Detect violations:
   for each original edge (A → B) including back-edges:
     if layer(A) > layer(B):                      # lower layer importing higher
       violation(A, B, type=BACKWARD)
     if |layer(A) - layer(B)| > 1:                # skipping intermediate layers
       violation(A, B, type=SKIP)
```

### Math at IR4

**Module cohesion:**
```
internal_edges = |{(a,b) ∈ E : a ∈ module AND b ∈ module}|
possible_edges = |module| × (|module| - 1)
cohesion = internal_edges / possible_edges    (0 if |module| ≤ 1)
```

**Module coupling:**
```
external_edges = |{(a,b) ∈ E : (a ∈ module) XOR (b ∈ module)}|
total_edges = internal_edges + external_edges
coupling = external_edges / total_edges       (0 if total_edges == 0)
```

**Instability** (Robert Martin):
```
Ca = afferent coupling = edges coming INTO module from outside
Ce = efferent coupling = edges going OUT of module to outside
I = Ce / (Ca + Ce)
```
- I = 0: completely stable (everyone depends on you, you depend on nobody) — hard to change
- I = 1: completely unstable (you depend on everyone, nobody depends on you) — easy to change

**Abstractness** (Robert Martin):
```
A = abstract_symbols / total_symbols
where abstract = ABC methods, Protocol methods, abstract classes, type-only definitions
```

**Distance from Main Sequence:**
```
D = |A + I - 1|
```
- D = 0: on the "main sequence" — ideal balance of abstractness and stability
- D → 1: in the "zone of pain" (concrete + stable = rigid) or "zone of uselessness" (abstract + unstable = unused abstractions)

This is one of the most powerful architectural metrics — it tells you which modules are architected well vs. which are in trouble.

**Boundary alignment:**
```
For each module, find dominant Louvain community among its files.
alignment = |files in dominant community| / |files in module|

codebase_alignment = mean(alignment for all modules)
```
- 1.0: directory boundaries perfectly match actual dependency communities
- < 0.5: directories don't reflect how code actually clusters

**Architecture entropy:**
```
p_i = |module_i.files| / |total_files|
H_arch = -Σ p_i × log₂(p_i)
H_max = log₂(|modules|)
evenness = H_arch / H_max
```
- High evenness: modules are similarly sized (healthy)
- Low evenness: one module dominates (god module)

### Temporal (IR4 over time)

**Delta(t₁, t₂):**

```
ArchDelta:
  modules_added:       [Module]
  modules_removed:     [Module]
  modules_split:       [(old_module, [new_modules])]
  modules_merged:      [([old_modules], new_module)]
  layer_changes:       [(module, old_depth, new_depth)]
  new_violations:      [Violation]
  resolved_violations: [Violation]
  pattern_changes:     [(pattern, old_val, new_val)]
  cohesion_deltas:     {module: float}
  coupling_deltas:     {module: float}
```

**Time series:**

| Metric | Formula | What it reveals |
|--------|---------|-----------------|
| violation_count(t) | \|violations\| | Architecture erosion rate |
| violation_rate(t) | violations / cross-module edges | Normalized erosion |
| mean_cohesion(t) | avg(cohesion) across modules | Are modules becoming more/less focused? |
| mean_coupling(t) | avg(coupling) across modules | Are modules becoming more/less entangled? |
| mean_D(t) | avg(main_seq_distance) | Architecture quality trend |
| layer_count(t) | max(layer depth) | Is architecture getting deeper (more abstract) or flatter? |
| god_module_size(t) | max(module.files) / total_files | Is the biggest module growing? |
| boundary_alignment(t) | from Louvain vs directories | Are boundaries drifting from reality? |

**Architecture drift velocity:**
```
drift(t) = GED(module_graph(t-1), module_graph(t))
         = (|module_edges_added| + |module_edges_removed|) / |total_module_edges|
```
Accelerating drift = architecture is being actively eroded.

---

## IR5: TemporalModel

**What it captures**: The time dimension itself — not just "what changed" (that's deltas on IR0-IR4) but the **patterns** in how things change: trajectories, rhythms, social dynamics.

### Snapshot Data Model (computed from git history)

```
TemporalModel:
  file_histories:     {path: FileHistory}
  coevolution:        {(path, path): PairDynamics}
  module_dynamics:    {module: ModuleDynamics}
  codebase_dynamics:  CodebaseDynamics

FileHistory:
  commits:            [CommitRef]         # all commits touching this file
  total_changes:      int
  first_seen:         datetime
  last_modified:      datetime
  age:                timedelta

  # Author dimension
  authors:            {email: int}        # author → commit count
  author_count:       int
  author_entropy:     float               # H of author distribution
  bus_factor:         int                  # effective authors: 2^H
  primary_author:     str                 # mode of author distribution
  primary_author_pct: float               # % of commits by primary author

  # Churn dimension
  churn_trajectory:   Trajectory          # dormant | stabilizing | churning | spiking
  churn_series:       [int]               # changes per time window
  churn_slope:        float               # linear regression slope
  churn_cv:           float               # coefficient of variation

  # Quality dimension
  fix_ratio:          float               # fraction of commits with "fix"/"bug" in message
  refactor_ratio:     float               # fraction with "refactor"/"clean" in message

CommitRef:
  sha:       str
  timestamp: datetime
  author:    str
  message:   str
  files:     [str]             # other files in same commit

PairDynamics:
  cochange_count:     int
  lift:               float     # observed / expected co-change frequency
  confidence:         float     # P(B changes | A changes)
  has_structural_edge: bool     # does an import edge exist?
  temporal_coupling:   float    # lift × confidence

ModuleDynamics:
  velocity:           float     # commits per week touching this module
  coordination_cost:  float     # mean(distinct authors per commit touching module)
  knowledge_gini:     float     # gini of author contributions within module
  stability:          float     # fraction of files with stabilizing trajectory
  growth_rate:        float     # new files per month
  fix_hotspot_ratio:  float     # fraction of commits that are fixes

CodebaseDynamics:
  commit_frequency:    [float]  # commits per week over time
  active_contributors: [int]    # distinct authors per month
  growth_rate:         float    # files per month
  entropy_rate:        float    # H of commit distribution across modules
  bus_factor_global:   int      # min bus factor across critical modules
  debt_velocity:       float    # rate of finding accumulation from IR6
```

### Math at IR5

**Author entropy** (per file):
```
p(a) = commits_by(a) / total_commits for file
H = -Σ p(a) × log₂(p(a))
```
H = 0 → single author. H = log₂(n) → perfectly distributed.

**Effective authors (bus factor):**
```
bus_factor = 2^H
```
This is the "equivalent number of equally-contributing authors." A file with H=1.58 has bus_factor≈3.

**Churn trajectory classification:**
```
windows = [commit_count in each 4-week window]
slope = linear_regression(windows).slope
cv = std(windows) / mean(windows)

if total_changes ≤ 1:                    DORMANT
elif slope < -threshold:                  STABILIZING
elif slope > threshold AND cv > 0.5:      SPIKING
elif cv > 0.5:                            CHURNING
else:                                     STABLE
```

**Fix ratio** (commit message mining):
```
fix_keywords = {"fix", "bug", "patch", "hotfix", "repair", "resolve"}
fix_commits = |{c : any(kw in c.message.lower() for kw in fix_keywords)}|
fix_ratio = fix_commits / total_commits
```
High fix_ratio = file attracts bugs. Especially damning when combined with high centrality.

**Co-evolution lift:**
```
P(A) = commits_touching(A) / total_commits
P(B) = commits_touching(B) / total_commits
P(A∩B) = commits_touching_both(A,B) / total_commits
lift(A,B) = P(A∩B) / (P(A) × P(B))
```
- lift = 1: independent
- lift > 2: change together much more than chance
- lift < 0.5: actively avoid changing together

**Coordination cost** (Conway's Law metric):
```
for each commit touching module M:
  authors_in_commit = |distinct authors in that commit|
coordination_cost(M) = mean(authors_in_commit)
```
High = multiple people must coordinate to change this module = possible design issue.

**Knowledge Gini:**
```
contributions = [commit_count for each author who touched module]
gini(contributions)
```
- High Gini (>0.7): one author dominates = knowledge silo
- Low Gini (<0.3): knowledge well-distributed

**Entropy rate** (codebase-level):
```
p(m) = commits_touching_module(m) / total_commits
H = -Σ p(m) × log₂(p(m))
H_max = log₂(|modules|)
normalized = H / H_max
```
- Low normalized entropy: all activity concentrated in one module (bottleneck)
- High: activity well-distributed (healthy)

### Temporal (IR5 itself IS temporal, so "time series of IR5" = second-order dynamics)

The interesting second-order questions:

| Metric | Formula | What it reveals |
|--------|---------|-----------------|
| bus_factor(t) per file | 2^H over expanding windows | Is knowledge spreading or concentrating? |
| velocity(t) per module | commits/week in rolling window | Is this module heating up or cooling down? |
| coordination_cost(t) | rolling mean | Is the team structure becoming more or less coupled? |
| fix_ratio(t) | rolling fraction | Are bugs increasing in this area? |
| contributor_count(t) | active authors per month | Team growing or shrinking? |

---

## IR5 (Signals) — Renamed from original IR6

**What it captures**: Quantitative quality measurements at every level — per-file, per-module, codebase-wide. This is the fusion layer that combines all previous IRs into actionable numbers.

### Snapshot Data Model

```
SignalField:
  per_file:   {path: FileSignals}
  per_module: {module: ModuleSignals}
  global:     GlobalSignals

FileSignals:
  # --- From IR1 (syntactic) ---
  lines:                int
  function_count:       int
  class_count:          int
  max_nesting:          int
  import_count:         int

  # --- From IR2 (semantic) ---
  role:                 Role
  concept_count:        int
  concept_entropy:      float         # H of concept weights
  stub_ratio:           float
  implementation_gini:  float
  naming_drift:         float         # filename vs content similarity
  todo_density:         float
  docstring_coverage:   float

  # --- From IR3 (structural) ---
  pagerank:             float
  betweenness:          float
  in_degree:            int
  out_degree:           int
  blast_radius_size:    int
  is_orphan:            bool
  phantom_import_count: int
  broken_call_count:    int
  depth:                int           # DAG depth from entry point
  community:            int           # Louvain community ID

  # --- From IR3 (information-theoretic) ---
  compression_ratio:    float         # Kolmogorov approx
  semantic_coherence:   float         # identifier clustering quality
  cognitive_load:       float         # Gini-weighted complexity

  # --- From IR5-temporal ---
  total_changes:        int
  bus_factor:           int
  author_entropy:       float
  churn_trajectory:     str
  fix_ratio:            float

  # --- Composites ---
  risk_score:           float         # fused multi-signal risk
  wiring_quality:       float         # connectivity health (for AI detection)

ModuleSignals:
  # Structural (from IR4)
  cohesion:                  float
  coupling:                  float
  instability:               float      # Martin's I
  abstractness:              float      # Martin's A
  distance_main_sequence:    float      # Martin's D
  boundary_alignment:        float
  layer_violation_count:     int
  role_consistency:          float

  # Temporal (from IR5-temporal)
  velocity:                  float
  coordination_cost:         float
  knowledge_gini:            float
  bus_factor:                int
  fix_hotspot_ratio:         float

  # Aggregated file signals
  mean_cognitive_load:       float
  max_cognitive_load:        float
  mean_coherence:            float
  file_count:                int

  # Composite
  health_score:              float      # fused module health

GlobalSignals:
  # Graph topology
  modularity:                float
  fiedler_value:             float
  cycle_count:               int
  connected_component_count: int
  centrality_gini:           float

  # Wiring quality (AI detection)
  orphan_ratio:              float
  phantom_ratio:             float
  glue_deficit:              float
  mean_depth:                float
  wiring_score:              float     # composite

  # Architecture
  violation_rate:            float
  mean_main_seq_dist:        float
  boundary_alignment:        float
  architecture_health:       float     # composite

  # Social
  global_bus_factor:         int       # min across critical modules
  knowledge_entropy:         float     # author distribution

  # Overall
  codebase_health:           float     # grand composite
```

### Math at IR5-Signals: Signal Fusion

**Per-file risk score:**
```
risk(f) = w₁ × percentile(pagerank, f)
        + w₂ × percentile(blast_radius_size, f)
        + w₃ × percentile(cognitive_load, f)
        + w₄ × instability_factor(f)
        + w₅ × (1 - bus_factor(f) / max_bus_factor)

where instability_factor = 1.0 if trajectory ∈ {churning, spiking}, else 0.3
      w = [0.25, 0.20, 0.20, 0.20, 0.15]
```

**Per-file wiring quality:**
```
wiring(f) = 1 - (
    0.30 × is_orphan(f)
  + 0.25 × stub_ratio(f)
  + 0.25 × (phantom_import_count(f) / max(import_count(f), 1))
  + 0.20 × (broken_call_count(f) / max(total_calls(f), 1))
)
```

**Module health score:**
```
health(m) = w₁ × cohesion(m)
          + w₂ × (1 - coupling(m))
          + w₃ × (1 - distance_main_sequence(m))
          + w₄ × boundary_alignment(m)
          + w₅ × role_consistency(m)
          + w₆ × (1 - mean_stub_ratio(m))

where w = [0.20, 0.15, 0.20, 0.15, 0.15, 0.15]
```

**Global wiring score:**
```
wiring = 1 - (
    0.25 × orphan_ratio
  + 0.25 × phantom_ratio
  + 0.20 × glue_deficit
  + 0.15 × mean(stub_ratio across files)
  + 0.15 × max(clone_cluster_ratio, 0)
)
```

**Global codebase health** (the one number):
```
health = 0.25 × architecture_health
       + 0.25 × wiring_score
       + 0.20 × (1 - finding_density)
       + 0.15 × (global_bus_factor / team_size)
       + 0.15 × modularity
```

### Temporal (Signals over time)

This is where sparklines live. Every signal becomes a time series:

```
For signal S and file f:
  S(f, t₀), S(f, t₁), S(f, t₂), ..., S(f, now)

Trend classification:
  slope = linear_regression(S values over time).slope
  if slope > threshold:     WORSENING (for "high is bad" signals)
  elif slope < -threshold:  IMPROVING
  else:                     STABLE
```

**Module health trajectory** — the key architectural trend:
```
health(module, t) over time
→ IMPROVING / STABLE / DEGRADING
```

**Codebase health trajectory** — the executive summary:
```
health(codebase, t) over time
→ single sparkline: ▁▂▃▅▇ or ▇▅▃▂▁
```

---

## IR6 (Insights) — Renamed from original IR7

**What it captures**: Actionable findings with evidence chains reaching back through all IRs. This is what the user sees.

### Snapshot Data Model

```
InsightResult:
  findings:      [Finding]
  composites:    CompositeScores
  suggestions:   [Suggestion]

Finding:
  id:            str                 # stable hash for tracking across snapshots
  type:          str                 # "HIGH_RISK_HUB", "DISCONNECTED_CODE", etc.
  severity:      float               # [0, 1]
  confidence:    float               # [0, 1] — NEW: how sure are we?
  scope:         FILE | MODULE | CODEBASE
  targets:       [str]               # affected file/module paths

  evidence:      [Evidence]          # ordered chain from multiple IRs
  suggestion:    str                 # actionable recommendation
  effort:        LOW | MEDIUM | HIGH # estimated fix effort

  # Temporal context
  first_seen:         Optional[datetime]
  persistence_count:  int            # snapshots this has existed
  trend:              WORSENING | STABLE | IMPROVING
  regression:         bool           # was resolved, came back

Evidence:
  ir_source:     str                 # "IR1", "IR2", "IR3", "IR4", "IR5-temporal"
  signal:        str                 # signal name
  value:         Any                 # the actual value
  percentile:    Optional[float]     # where it ranks
  description:   str                 # human-readable explanation

CompositeScores:
  ai_quality:          float         # wiring score
  architecture_health: float
  team_risk:           float
  codebase_health:     float

Suggestion:
  action:        str                 # "Split auth_service.py into auth.py and cache.py"
  priority:      int                 # 1 = do first
  effort:        LOW | MEDIUM | HIGH
  impact:        float               # estimated health improvement
  targets:       [str]               # files/modules to change
  evidence_refs: [Finding]           # which findings this addresses
```

### Evidence Chain Example

A finding with evidence from 5 different IRs:

```
Finding:
  type: "HIGH_RISK_HUB"
  severity: 0.92
  confidence: 0.88
  targets: ["src/auth/service.py"]

  evidence:
    - ir: IR2,  signal: role,              value: SERVICE,     desc: "Classified as service"
    - ir: IR2,  signal: concept_count,     value: 3,           desc: "3 distinct concepts (auth, caching, validation) — unfocused"
    - ir: IR2,  signal: stub_ratio,        value: 0.25,        desc: "25% functions are stubs"
    - ir: IR3,  signal: pagerank,          value: 0.087,       percentile: 95, desc: "Top 5% most central file"
    - ir: IR3,  signal: blast_radius_size, value: 23,          percentile: 98, desc: "Changes affect 23 files"
    - ir: IR4,  signal: layer_violation,   value: true,        desc: "In utils/ but imports from services/"
    - ir: IR5t, signal: bus_factor,        value: 1,           desc: "Single author — knowledge silo"
    - ir: IR5t, signal: churn_trajectory,  value: "churning",  desc: "No stabilization trend over 3 months"
    - ir: IR5t, signal: fix_ratio,         value: 0.40,        desc: "40% of commits are bug fixes"

  suggestion: "Split into auth_core.py (auth concept) and auth_cache.py (caching concept).
               Move validation logic to validators/. Pair-program to spread knowledge."
  effort: HIGH
```

Compare to current output: "This file has high cognitive load (92nd percentile)" — the evidence chain is vastly richer.

### Temporal (Insights over time)

```
InsightDelta:
  new_findings:       [Finding]
  resolved_findings:  [Finding]
  persisting:         [Finding]        # with updated persistence_count
  regressions:        [Finding]        # was resolved, came back
  worsening:          [Finding]        # severity or evidence increased
  improving:          [Finding]        # severity or evidence decreased

# Tracked via stable finding IDs (hash of type + targets)
finding_id = hash(type + sorted(targets))
```

**Debt velocity:**
```
debt_velocity(t) = |new_findings(t)| - |resolved_findings(t)|
```
Positive = accumulating debt. Negative = paying it down.

**Mean time to resolve:**
```
MTTR = mean(resolution_time for all resolved findings)
where resolution_time = last_seen - first_seen
```

---

## Pipeline: How IRs Chain

```
                  ┌──────────────────────────────────────────┐
    SOURCE        │                   GIT                     │
    FILES         │                 HISTORY                   │
      │           │                    │                      │
      ▼           │                    ▼                      │
  ┌───────┐       │  ┌──────────────────────────────────┐    │
  │ IR0   │       │  │        IR5-temporal               │    │
  │ files │       │  │  file histories, cochange,        │    │
  └───┬───┘       │  │  author dist, churn, bus factor   │    │
      │           │  └────────────────┬─────────────────┘    │
      ▼           │                   │                      │
  ┌───────┐       │                   │                      │
  │ IR1   │       │   (these two      │                      │
  │syntax │       │    spines run     │                      │
  └───┬───┘       │    in parallel)   │                      │
      │           │                   │                      │
      ▼           │                   │                      │
  ┌───────┐       │                   │                      │
  │ IR2   │       │                   │                      │
  │semant │       │                   │                      │
  └───┬───┘       │                   │                      │
      │           │                   │                      │
      ▼           │                   │                      │
  ┌───────┐       │                   │                      │
  │ IR3   │◄──────┼───────────────────┘  (temporal data      │
  │graph  │       │                       enriches edges)    │
  └───┬───┘       │                                          │
      │           │                                          │
      ▼           │                                          │
  ┌───────┐       │                                          │
  │ IR4   │       │                                          │
  │ arch  │       │                                          │
  └───┬───┘       │                                          │
      │           │                                          │
      ▼           │                                          │
  ┌───────────┐   │                                          │
  │ IR5-sigs  │◄──┼──── reads ALL previous IRs               │
  │ (signals) │   │                                          │
  └─────┬─────┘   │                                          │
        │         │                                          │
        ▼         │                                          │
  ┌───────────┐   │                                          │
  │ IR6       │   │                                          │
  │ insights  │   │                                          │
  └───────────┘   │                                          │
                  └──────────────────────────────────────────┘

At every IR level, the temporal dimension provides:
  • Delta(tₙ, tₙ₊₁) — what changed between snapshots
  • TimeSeries — trend of metrics at that level
  • Trajectory — classification of the trend
```

### Persistence / What Gets Stored

Not every IR needs to be fully persisted. The storage strategy:

| IR | Store full snapshot? | Store delta? | Store time series? |
|----|---------------------|-------------|-------------------|
| IR0 | No (git has it) | Yes (file list + hashes) | Yes (file_count, growth) |
| IR1 | No (recompute from source) | Partial (function count, stub_ratio) | Yes (key metrics) |
| IR2 | Partial (roles, concepts summary) | Yes (role changes, drift) | Yes (concept_count, drift) |
| IR3 | Partial (edges, centrality, cycles) | Yes (graph delta) | Yes (modularity, fiedler, etc) |
| IR4 | Yes (it's small — module-level) | Yes (violations, layers) | Yes (all arch metrics) |
| IR5-temporal | Yes (it's the git-derived model) | N/A (it IS temporal) | N/A |
| IR5-signals | Partial (per-file key signals) | Yes (signal deltas) | Yes (sparklines) |
| IR6 | Yes (findings are the product) | Yes (new/resolved/persisting) | Yes (debt velocity) |

### Demand-Driven Evaluation

Each IR level declares what it needs from below:

```
IR1 requires: IR0
IR2 requires: IR1
IR3 requires: IR1 (imports), IR2 (for annotated nodes), IR5-temporal (optional, for edge enrichment)
IR4 requires: IR3
IR5-temporal requires: git history (independent of IR0-IR4)
IR5-signals requires: IR1, IR2, IR3, IR4, IR5-temporal (all of them)
IR6 requires: IR5-signals
```

If a specific finder only needs IR3-level data, the kernel only computes IR0 → IR1 → IR2 → IR3. No IR4, no temporal, no heavy signal fusion. Fast.

---

## Summary: What Each IR Adds

| IR | Abstraction | Key question it answers | Key math |
|----|-------------|------------------------|----------|
| IR0 | Files | What exists? | SHA-256 (change detection) |
| IR1 | Syntax | What's inside each file? | Per-function token ratios, Gini of function sizes |
| IR2 | Semantics | What does each file mean? | TF-IDF + Louvain clustering, cosine similarity |
| IR3 | Relationships | How do files connect? | PageRank, Tarjan, BFS blast radius, NCD, spectral |
| IR4 | Architecture | What's the system design? | Topo sort for layers, Martin's I/A/D, modularity |
| IR5-temporal | Evolution | How does it change? | Shannon entropy of authors, regression, lift |
| IR5-signals | Quality | How healthy is everything? | Weighted signal fusion, percentile ranking |
| IR6 | Insights | What should you fix? | Multi-IR evidence chains, severity scoring |
