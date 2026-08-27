# Correct Mathematical Computation DAG

## 1. DAG Construction Method

For each computation, I specify:
- **REQUIRES**: What inputs must exist before this can run
- **PRODUCES**: What outputs this computation creates
- **FORMULA**: The exact transformation

---

## Level 0: Raw Data Sources

### 0.1 Filesystem Read
```
REQUIRES: Nothing
PRODUCES: 
  - file_content(path) → bytes
  - file_list → Set[path]
METHOD: os.walk() + file read
```

### 0.2 Git Repository Read
```
REQUIRES: Nothing
PRODUCES:
  - git_log_output → str (raw git log)
  - git_diff_output → str (raw git diff)
METHOD: git log, git log --numstat
```

---

## Level 1: Lexical/Parsing Layer

### 1.1 AST Parser
```
REQUIRES: file_content(path) from 0.1
PRODUCES:
  - ast_tree(path) → AST
  - syntax_errors(path) → List[Error]
METHOD: tree-sitter parse or language-specific parser
```

### 1.2 Import Statement Extractor
```
REQUIRES: ast_tree(path) from 1.1
PRODUCES:
  - import_names(path) → List[str]
    Examples: ["os", "collections.abc", ".utils", "..parent.module"]
  - import_details(path) → List[ImportInfo]
    Where ImportInfo = {
      module: str,        # "collections"
      names: List[str],   # ["defaultdict", "Counter"]  
      level: int,         # 0=absolute, 1+=relative
      lineno: int
    }
METHOD: Traverse AST for Import/ImportFrom nodes

EXAMPLE (Python):
  Code: from collections import defaultdict, Counter
  Output: ImportInfo(module="collections", names=["defaultdict","Counter"], level=0)

  Code: from .utils import helper
  Output: ImportInfo(module="utils", names=["helper"], level=1)
```

### 1.3 Class/Function Extractor
```
REQUIRES: ast_tree(path) from 1.1
PRODUCES:
  - class_names(path) → List[str]
  - function_names(path) → List[str]
  - class_info(path) → List[ClassInfo]
  - function_info(path) → List[FunctionInfo]
    
    ClassInfo = {name, bases, methods, lineno}
    FunctionInfo = {name, params, return_type, body_size, lineno}
METHOD: Traverse AST for ClassDef/FunctionDef nodes
```

### 1.4 Identifier Extractor
```
REQUIRES: ast_tree(path) from 1.1
PRODUCES:
  - identifiers(path) → List[str]
    All variable names, function names, class names, attribute accesses
  - function_calls(path) → List[str]
    Names of functions being called
METHOD: Traverse AST for Name, Attribute, Call nodes

EXAMPLE:
  Code: result = process_data(get_user(id))
  Output: 
    identifiers = ["result", "process_data", "get_user", "id"]
    function_calls = ["process_data", "get_user"]
```

### 1.5 Comment/Docstring Extractor
```
REQUIRES: ast_tree(path) from 1.1, file_content(path) from 0.1
PRODUCES:
  - docstrings(path) → Dict[function_name → str]
  - comments(path) → List[str]
  - todo_comments(path) → List[str]
METHOD: 
  - Docstrings: First statement in function/class body
  - Comments: Tokenizer or regex for #, //, /* */
```

### 1.6 Nesting/Complexity Extractor
```
REQUIRES: ast_tree(path) from 1.1
PRODUCES:
  - max_nesting(path) → int
  - cyclomatic_complexity(path) → int
  - nesting_per_function(path) → Dict[str, int]
METHOD:
  - max_nesting: Max depth of control flow nesting (if/for/while/try)
  - complexity: Count decision points (if/for/while/and/or/try/except)
```

### 1.7 Line Counter
```
REQUIRES: file_content(path) from 0.1
PRODUCES:
  - line_count(path) → int
  - blank_lines(path) → int
  - code_lines(path) → int
  - comment_lines(path) → int
METHOD: Line-by-line analysis
```

### 1.8 Git Commit Parser
```
REQUIRES: git_log_output from 0.2
PRODUCES:
  - commits → List[Commit]
    Commit = {hash, timestamp, author_email, subject, body}
METHOD: Parse git log --format output
```

### 1.9 Git File Change Parser
```
REQUIRES: git_diff_output from 0.2
PRODUCES:
  - file_changes → List[FileChange]
    FileChange = {
      commit_hash: str,
      file_path: str,
      change_type: str,  # 'A', 'M', 'D', 'R'
      old_path: str,     # for renames
      additions: int,
      deletions: int
    }
METHOD: Parse git log --numstat --name-status
```

---

## Level 2: Resolution Layer

### 2.1 Import Resolver
```
REQUIRES: 
  - import_names(path) from 1.2
  - file_list from 0.1
  - project_root_path
PRODUCES:
  - resolved_imports(path) → List[str]
    File paths that each import resolves to
  - unresolved_imports(path) → List[str]
    Imports that couldn't be resolved (phantom)
  - import_map(path) → Dict[import_name → resolved_path | None]
METHOD:
  For each import in import_names(path):
    1. Handle relative imports: level > 0 means go up directories
    2. Try: import_name + ".py"
    3. Try: import_name + "/__init__.py"
    4. Try: import_name + ".ts" (for TypeScript)
    5. If not found → phantom

EXAMPLE:
  import_names("src/api/users.py") = ["models.user", "utils.auth", "flask"]
  resolved_imports = ["src/models/user.py", "src/utils/auth.py"]
  unresolved_imports = ["flask"]  # third-party
```

### 2.2 Identifier Tokenizer
```
REQUIRES: identifiers(path) from 1.4, function_names(path) from 1.3, class_names(path) from 1.3
PRODUCES:
  - tokens(path) → List[str]
    Split camelCase/snake_case into individual words
  - token_frequencies(path) → Dict[str, int]
METHOD:
  For each identifier:
    1. Split on underscores: "get_user_data" → ["get", "user", "data"]
    2. Split camelCase: "getUserData" → ["get", "user", "data"]
    3. Lowercase all
    4. Remove stopwords (a, an, the, of, etc.)
    5. Count frequencies

EXAMPLE:
  identifiers = ["getUserData", "validate_input", "HTTPClient"]
  tokens = ["get", "user", "data", "validate", "input", "http", "client"]
```

### 2.3 Docstring/Comment Tokenizer
```
REQUIRES: 
  - docstrings(path) from 1.5
  - comments(path) from 1.5
PRODUCES:
  - docstring_tokens(path) → List[str]
  - comment_tokens(path) → List[str]
METHOD:
  1. Split on whitespace and punctuation
  2. Lowercase
  3. Remove stopwords
  4. Count frequencies
```

### 2.4 Concept Vector Builder
```
REQUIRES:
  - token_frequencies(path) from 2.2
  - docstring_tokens(path) from 2.3
  - All files' tokens (for IDF)
PRODUCES:
  - tfidf_vector(path) → Dict[str, float]
  - concepts(path) → List[(concept, weight)]
    Top-k concepts by TF-IDF score
METHOD:
  1. TF(term, path) = count(term, path) / total_terms(path)
  2. IDF(term) = log(N / |{paths containing term}|)
  3. TF-IDF(term, path) = TF × IDF
  4. Keep top-k by TF-IDF score
```

### 2.5 Commit File Grouper
```
REQUIRES: file_changes from 1.9
PRODUCES:
  - files_per_commit(commit_hash) → Set[path]
  - commits_per_file(path) → List[commit_hash]
  - changes_per_file(path) → List[FileChange]
METHOD: Group by commit_hash, then invert
```

### 2.6 Cochange Counter
```
REQUIRES: files_per_commit from 2.5
PRODUCES:
  - cochange_counts → Dict[(path_a, path_b) → int]
    How many times each pair of files changed together
METHOD:
  For each commit c:
    files = files_per_commit(c)
    For each pair (a, b) in files where a < b:
      cochange_counts[(a, b)] += 1
```

### 2.7 Author Set Builder
```
REQUIRES: 
  - commits from 1.8
  - commits_per_file from 2.5
PRODUCES:
  - authors(path) → Set[email]
  - commits_per_author_per_file(path) → Dict[email → int]
METHOD:
  For each path:
    authors(path) = {c.author_email for c in commits_per_file(path)}
```

### 2.8 Time Window Partitioner
```
REQUIRES:
  - commits from 1.8
  - file_changes from 1.9
PRODUCES:
  - windows → List[Window]
    Window = {start_ts, end_ts, commits, files_changed}
  - window_for_commit(commit_hash) → Window
  - file_changes_in_window(window) → List[FileChange]
METHOD:
  1. window_size = 4 weeks (default)
  2. Partition commits by (timestamp // window_size)
  3. For each window, collect all file changes
```

### 2.9 Node Lifecycle Tracker
```
REQUIRES: 
  - file_changes from 1.9
  - commits from 1.8
PRODUCES:
  - birth_ts(path) → int (timestamp of first appearance)
  - death_ts(path) → int | None (timestamp of deletion, None if alive)
  - birth_commit(path) → str
  - death_commit(path) → str | None
METHOD:
  For each path:
    birth = min(commit.timestamp for commit where path first added)
    death = max(commit.timestamp for commit where path deleted) or None
```

---

## Level 3: Graph Construction Layer

### 3.1 Import Graph (G_import)
```
REQUIRES:
  - resolved_imports(path) from 2.1
  - file_list from 0.1
PRODUCES:
  - V_import → Set[path]
  - E_import → Set[(source, target)]
  - W_import(source, target) → float (always 1.0 for imports)
METHOD:
  V_import = file_list
  For each path, for each resolved in resolved_imports(path):
    E_import.add((path, resolved))
```

### 3.2 Phantom Import Counter
```
REQUIRES:
  - unresolved_imports(path) from 2.1
PRODUCES:
  - phantom_import_count(path) → int
  - phantom_imports(path) → List[str]
METHOD: Count and list unresolved imports
```

### 3.3 Cochange Graph (G_cochange)
```
REQUIRES:
  - cochange_counts from 2.6
  - files_per_commit from 2.5
  - commits from 1.8
PRODUCES:
  - V_cochange → Set[path]
  - E_cochange → Set[(path_a, path_b)]
  - W_cochange(path_a, path_b) → float (lift score)
METHOD:
  For each (a, b) in cochange_counts:
    count_ab = cochange_counts[(a, b)]
    count_a = |commits touching a|
    count_b = |commits touching b|
    total = |commits|
    
    P_ab = count_ab / total
    P_a = count_a / total
    P_b = count_b / total
    lift = P_ab / (P_a × P_b)
    
    if lift > 1.0:  # more than random co-occurrence
      E_cochange.add((a, b))
      W_cochange(a, b) = lift
```

### 3.4 Author Graph (G_author)
```
REQUIRES:
  - authors(path) from 2.7
PRODUCES:
  - V_author → Set[path]
  - E_author → Set[(path_a, path_b)]
  - W_author(path_a, path_b) → float (Jaccard similarity)
METHOD:
  For each pair (a, b):
    A = authors(a)
    B = authors(b)
    jaccard = |A ∩ B| / |A ∪ B|
    
    if jaccard > 0.1:  # non-trivial overlap
      E_author.add((a, b))
      W_author(a, b) = jaccard
```

### 3.5 Semantic Graph (G_semantic)
```
REQUIRES:
  - tfidf_vector(path) from 2.4
  - file_list from 0.1
PRODUCES:
  - V_semantic → Set[path]
  - E_semantic → Set[(path_a, path_b)]
  - W_semantic(path_a, path_b) → float (cosine similarity)
METHOD:
  For each pair (a, b):
    vec_a = tfidf_vector(a)
    vec_b = tfidf_vector(b)
    
    # Cosine similarity
    dot = sum(vec_a[t] * vec_b[t] for t in vec_a if t in vec_b)
    norm_a = sqrt(sum(v^2 for v in vec_a.values()))
    norm_b = sqrt(sum(v^2 for v in vec_b.values()))
    cosine = dot / (norm_a * norm_b)
    
    if cosine > 0.3:
      E_semantic.add((a, b))
      W_semantic(a, b) = cosine
```

### 3.6 Clone Graph (G_clone)
```
REQUIRES:
  - file_content(path) from 0.1
  - file_list from 0.1
PRODUCES:
  - V_clone → Set[path]
  - E_clone → Set[(path_a, path_b)]
  - W_clone(path_a, path_b) → float (1 - NCD)
METHOD:
  For each pair (a, b):
    C_a = compressed_size(file_content(a))
    C_b = compressed_size(file_content(b))
    C_ab = compressed_size(file_content(a) + file_content(b))
    
    NCD = (C_ab - min(C_a, C_b)) / max(C_a, C_b)
    
    if NCD < 0.3:  # high similarity
      E_clone.add((a, b))
      W_clone(a, b) = 1 - NCD
```

---

## Level 4: Graph Fusion Layer

### 4.1 Graph Weight Normalizer
```
REQUIRES:
  - W_import, W_cochange, W_author, W_semantic from Level 3
PRODUCES:
  - W_import_norm(a, b) → float in [0, 1]
  - W_cochange_norm(a, b) → float in [0, 1]
  - W_author_norm(a, b) → float in [0, 1]
  - W_semantic_norm(a, b) → float in [0, 1]
METHOD:
  For each graph type r:
    min_r = min(W_r values)
    max_r = max(W_r values)
    W_r_norm(a, b) = (W_r(a, b) - min_r) / (max_r - min_r)
```

### 4.2 Combined Graph (G_combined)
```
REQUIRES:
  - W_*_norm from 4.1
  - E_import, E_cochange, E_author, E_semantic from Level 3
PRODUCES:
  - V_combined → Set[path]
  - E_combined → Set[(a, b)]
  - W_combined(a, b) → float
METHOD:
  α = 0.4  # import weight
  β = 0.3  # cochange weight
  γ = 0.2  # author weight
  δ = 0.1  # semantic weight
  
  V_combined = V_import
  
  all_edges = E_import ∪ E_cochange ∪ E_author ∪ E_semantic
  
  For each (a, b) in all_edges:
    w = α * W_import_norm(a, b) if (a,b) in E_import else 0
      + β * W_cochange_norm(a, b) if (a,b) in E_cochange else 0
      + γ * W_author_norm(a, b) if (a,b) in E_author else 0
      + δ * W_semantic_norm(a, b) if (a,b) in E_semantic else 0
    
    if w > 0.1:
      E_combined.add((a, b))
      W_combined(a, b) = w
```

---

## Level 5: Graph Matrix Layer

### 5.1 Adjacency Matrix Builder
```
REQUIRES:
  - V, E from any graph (3.1, 3.3, 3.4, 3.5, 3.6, 4.2)
  - W for that graph
PRODUCES:
  - A → Matrix[N×N]  (N = |V|)
  - node_index → Dict[path → int]  (mapping from path to matrix index)
  - index_node → Dict[int → path]  (reverse mapping)
METHOD:
  1. Assign each node an index 0 to N-1
  2. A[i][j] = W(i, j) if (i, j) in E else 0
```

### 5.2 Degree Matrix Builder
```
REQUIRES:
  - A from 5.1
PRODUCES:
  - D → DiagonalMatrix[N×N]
  - in_degree(path) → int
  - out_degree(path) → int
  - degree(path) → int
METHOD:
  D[i][i] = sum(A[j][i] for all j)  # in-degree
  in_degree(path) = D[node_index[path]][node_index[path]]
  out_degree(path) = sum(A[node_index[path]][j] for all j)
  degree = in_degree + out_degree
```

### 5.3 Is Orphan
```
REQUIRES:
  - in_degree from 5.2
PRODUCES:
  - is_orphan(path) → bool
METHOD: is_orphan(path) = (in_degree(path) == 0)
```

### 5.4 Transition Matrix Builder
```
REQUIRES:
  - A from 5.1
  - D from 5.2
PRODUCES:
  - P → Matrix[N×N]
METHOD: P = D^{-1} × A  (row-normalized adjacency)
```

---

## Level 6: Graph Algorithm Layer - Centrality

### 6.1 PageRank
```
REQUIRES:
  - P from 5.4
  - N (number of nodes)
PRODUCES:
  - pagerank(path) → float
METHOD:
  α = 0.15  # damping factor
  v = [1/N, 1/N, ..., 1/N]  # personalization vector
  
  π = [1/N, 1/N, ..., 1/N]  # initial
  
  Repeat until convergence:
    π_new = (1 - α) × P × π + α × v
    if ||π_new - π||_1 < 0.0001:
      break
    π = π_new
  
  pagerank(path) = π[node_index[path]]
```

### 6.2 Betweenness Centrality
```
REQUIRES:
  - A from 5.1
  - node_index from 5.1
PRODUCES:
  - betweenness(path) → float
METHOD: Brandes algorithm
  C_B(v) = Σ_{s≠v≠t} σ_st(v) / σ_st
  where σ_st = number of shortest paths from s to t
        σ_st(v) = number of those passing through v
```

---

## Level 7: Graph Algorithm Layer - Structure

### 7.1 Laplacian Matrix
```
REQUIRES:
  - A from 5.1
  - D from 5.2
PRODUCES:
  - L → Matrix[N×N]
  - L_norm → Matrix[N×N]
METHOD:
  L = D - A
  L_norm = I - D^{-1/2} × A × D^{-1/2}
```

### 7.2 Spectral Decomposition
```
REQUIRES:
  - L_norm from 7.1
PRODUCES:
  - eigenvalues → List[float] (sorted)
  - eigenvectors → Matrix[N×N]
  - fiedler_value → float
  - spectral_gap → float
METHOD:
  eigendecomposition of L_norm
  eigenvalues = sorted ascending
  fiedler_value = eigenvalues[1]  # λ₂
  spectral_gap = eigenvalues[2] - eigenvalues[1]  # λ₃ - λ₂
```

### 7.3 Strongly Connected Components
```
REQUIRES:
  - A from 5.1
  - node_index from 5.1
PRODUCES:
  - sccs → List[Set[path]]
  - cycle_member(path) → bool
  - cycle_size(path) → int
  - cycle_count → int
METHOD: Tarjan's or Kosaraju's algorithm
  cycle_member(path) = |SCC containing path| > 1
  cycle_size(path) = |SCC containing path|
  cycle_count = |{SCC : |SCC| > 1}|
```

### 7.4 Entry Point Detection
```
REQUIRES:
  - is_orphan from 5.3
  - function_names from 1.3
  - file_list from 0.1
PRODUCES:
  - entry_points → Set[path]
  - is_entry_point(path) → bool
METHOD:
  is_entry_point(path) = 
    "main" in function_names(path) or
    "__main__" in function_names(path) or
    path ends with "__main__.py" or
    (is_orphan(path) and not is_test(path))
```

### 7.5 BFS Depth
```
REQUIRES:
  - A from 5.1
  - entry_points from 7.4
  - node_index from 5.1
PRODUCES:
  - depth(path) → int
METHOD:
  Run BFS from all entry_points
  depth(path) = min(BFS_distance from any entry_point to path)
  If unreachable from any entry_point: depth = ∞
```

### 7.6 Transitive Closure
```
REQUIRES:
  - A from 5.1
  - node_index from 5.1
PRODUCES:
  - reachable_from(path) → Set[path]
  - can_reach(path) → Set[path]
METHOD:
  TC = closure of A under Boolean matrix multiplication
  reachable_from(path) = {q : TC[node_index[path]][q] = 1}
```

### 7.7 Blast Radius
```
REQUIRES:
  - reachable_from from 7.6
PRODUCES:
  - blast_radius_size(path) → int
METHOD: blast_radius_size(path) = |reachable_from(path)|
```

---

## Level 8: Graph Algorithm Layer - Community

### 8.1 Louvain Community Detection
```
REQUIRES:
  - A from 5.1
  - D from 5.2
  - node_index from 5.1
PRODUCES:
  - community(path) → int
  - community_size(community_id) → int
  - modularity → float
METHOD:
  Q = (1/2m) Σ_{i,j} [A_{ij} - (k_i k_j / 2m)] δ(c_i, c_j)
  
  Phase 1 (Local Moving):
    For each node i:
      Move i to community C that maximizes ΔQ
  
  Phase 2 (Aggregation):
    Build supergraph from communities
  
  Repeat until Q stops improving
```

---

## Level 9: Distribution Statistics

### 9.1 Centrality Distribution
```
REQUIRES:
  - pagerank from 6.1
PRODUCES:
  - pagerank_values → List[float]
  - pagerank_mean → float
  - pagerank_std → float
METHOD: Collect all pagerank values
```

### 9.2 Gini Coefficient
```
REQUIRES:
  - pagerank_values from 9.1
PRODUCES:
  - centrality_gini → float
METHOD:
  x = sorted(pagerank_values)
  n = len(x)
  G = (2 × Σ(i × x_i)) / (n × Σ(x_i)) - (n+1)/n
```

---

## Level 10: Temporal Statistics - Basic

### 10.1 Total Changes
```
REQUIRES:
  - changes_per_file from 2.5
PRODUCES:
  - total_changes(path) → int
METHOD: total_changes(path) = |changes_per_file(path)|
```

### 10.2 Total Additions/Deletions
```
REQUIRES:
  - changes_per_file from 2.5
PRODUCES:
  - total_additions(path) → int
  - total_deletions(path) → int
METHOD:
  total_additions(path) = Σ(c.additions for c in changes_per_file(path))
  total_deletions(path) = Σ(c.deletions for c in changes_per_file(path))
```

### 10.3 Author Statistics
```
REQUIRES:
  - authors from 2.7
  - commits_per_author_per_file from 2.7
PRODUCES:
  - total_authors(path) → int
  - author_distribution(path) → Dict[email → float]
    (proportion of commits by each author)
METHOD:
  total_authors(path) = |authors(path)|
  total_commits = Σ counts
  author_distribution[a] = count[a] / total_commits
```

---

## Level 11: Temporal Statistics - Windowed

### 11.1 Windowed Churn
```
REQUIRES:
  - file_changes_in_window from 2.8
PRODUCES:
  - churn_w(path, window) → int
  - commits_w(path, window) → int
METHOD:
  churn_w(path, w) = Σ(c.additions + c.deletions for c in w if c.path == path)
  commits_w(path, w) = |{c in w : c.path == path}|
```

### 11.2 Churn Statistics
```
REQUIRES:
  - churn_w from 11.1
PRODUCES:
  - churn_mean(path) → float
  - churn_std(path) → float
  - churn_cv(path) → float
METHOD:
  values = [churn_w(path, w) for w in windows]
  churn_mean = mean(values)
  churn_std = std(values)
  churn_cv = churn_std / max(churn_mean, 1)
```

### 11.3 Churn Trend
```
REQUIRES:
  - churn_w from 11.1
  - windows from 2.8
PRODUCES:
  - churn_trend(path) → float
METHOD:
  # Linear regression slope
  x = [w.start_ts for w in windows]
  y = [churn_w(path, w) for w in windows]
  β = linear_regression_slope(x, y)
  churn_trend = β
```

### 11.4 Churn Trajectory
```
REQUIRES:
  - churn_cv from 11.2
  - churn_trend from 11.3
  - total_changes from 10.1
PRODUCES:
  - churn_trajectory(path) → enum
METHOD:
  if total_changes ≤ 1 or churn_cv == 0: DORMANT
  elif churn_trend < -θ and churn_cv < 0.5: STABILIZING
  elif churn_trend > θ and churn_cv > 0.5: SPIKING
  elif churn_cv > 0.5: CHURNING
  else: STABLE
```

### 11.5 Author Entropy
```
REQUIRES:
  - author_distribution from 10.3
PRODUCES:
  - author_entropy(path) → float
METHOD:
  H = -Σ_a p_a × log₂(p_a)
  where p_a = author_distribution[path][a]
```

### 11.6 Bus Factor
```
REQUIRES:
  - author_entropy from 11.5
PRODUCES:
  - bus_factor(path) → float
METHOD: bus_factor = 2^(author_entropy)
```

### 11.7 Commit Classification
```
REQUIRES:
  - commits from 1.8
  - commits_per_file from 2.5
PRODUCES:
  - fix_commits(path) → int
  - refactor_commits(path) → int
METHOD:
  fix_keywords = ["fix", "bug", "patch", "issue", "error"]
  refactor_keywords = ["refactor", "clean", "restructure", "rename"]
  
  For each commit c in commits_per_file(path):
    subject_lower = c.subject.lower()
    if any(kw in subject_lower for kw in fix_keywords):
      fix_commits += 1
    if any(kw in subject_lower for kw in refactor_keywords):
      refactor_commits += 1
```

### 11.8 Commit Ratios
```
REQUIRES:
  - fix_commits from 11.7
  - refactor_commits from 11.7
  - total_changes from 10.1
PRODUCES:
  - fix_ratio(path) → float
  - refactor_ratio(path) → float
METHOD:
  fix_ratio = fix_commits / max(total_changes, 1)
  refactor_ratio = refactor_commits / max(total_changes, 1)
```

### 11.9 Change Entropy
```
REQUIRES:
  - churn_w from 11.1
PRODUCES:
  - change_entropy(path) → float
METHOD:
  values = [churn_w(path, w) for w in windows]
  total = sum(values)
  if total == 0: return 0
  p_w = values[w] / total
  H = -Σ_w p_w × log₂(p_w)
```

---

## Level 12: Semantic Statistics

### 12.1 Role Classifier
```
REQUIRES:
  - function_names from 1.3
  - class_names from 1.3
  - import_names from 1.2
  - resolved_imports from 2.1
PRODUCES:
  - role(path) → enum {ENTRY, MODEL, SERVICE, TEST, CONFIG, DATASTORE, ROUTER, UTILITY}
METHOD:
  # Pattern matching on names and imports
  if has_main_function(function_names): ENTRY
  elif has_test_patterns(function_names, class_names): TEST
  elif has_db_imports(import_names): DATASTORE
  elif has_route_handlers(function_names): ROUTER
  elif has_class_defs_only(class_names, function_names): MODEL
  elif has_many_imports(import_names) and has_many_exports(function_names): SERVICE
  elif has_config_patterns(function_names): CONFIG
  else: UTILITY
```

### 12.2 Concept Count
```
REQUIRES:
  - concepts from 2.4
PRODUCES:
  - concept_count(path) → int
METHOD: concept_count = len(concepts(path))
```

### 12.3 Concept Entropy
```
REQUIRES:
  - concepts from 2.4
PRODUCES:
  - concept_entropy(path) → float
METHOD:
  weights = [w for _, w in concepts(path)]
  total = sum(weights)
  p_i = weights[i] / total
  H = -Σ_i p_i × log₂(p_i)
```

### 12.4 Semantic Coherence
```
REQUIRES:
  - concept_entropy from 12.3
PRODUCES:
  - semantic_coherence(path) → float
METHOD: semantic_coherence = 1 / (1 + concept_entropy)
```

### 12.5 TODO Density
```
REQUIRES:
  - todo_comments from 1.5
  - line_count from 1.7
PRODUCES:
  - todo_density(path) → float
METHOD: todo_density = len(todo_comments(path)) / max(line_count(path), 1)
```

### 12.6 Docstring Coverage
```
REQUIRES:
  - docstrings from 1.5
  - function_names from 1.3
PRODUCES:
  - docstring_coverage(path) → float
METHOD:
  documented = len([f for f in function_names(path) if f in docstrings(path)])
  docstring_coverage = documented / max(len(function_names(path)), 1)
```

---

## Level 13: Derived Syntax Statistics

### 13.1 Stub Ratio
```
REQUIRES:
  - function_info from 1.3
PRODUCES:
  - stub_count(path) → int
  - stub_ratio(path) → float
METHOD:
  is_stub(f) = body_size < 3 or body contains only "pass" or "..."
  stub_count = count(is_stub(f) for f in function_info(path))
  stub_ratio = stub_count / max(len(function_names(path)), 1)
```

### 13.2 Implementation Gini
```
REQUIRES:
  - function_info from 1.3
PRODUCES:
  - impl_gini(path) → float
METHOD:
  sizes = [f.body_size for f in function_info(path)]
  # Gini coefficient of function size distribution
```

---

## Level 14: Cognitive Load

### 14.1 Cognitive Load Score
```
REQUIRES:
  - line_count from 1.7
  - cyclomatic_complexity from 1.6
  - max_nesting from 1.6
  - impl_gini from 13.2
  - degree from 5.2
PRODUCES:
  - cognitive_load(path) → float
METHOD:
  CL = 0.25 × log(line_count)
     + 0.25 × log(complexity + 1)
     + 0.20 × max_nesting
     + 0.15 × impl_gini
     + 0.15 × log(degree + 1)
  
  cognitive_load = CL / (0.25 + 0.25 + 0.20 + 0.15 + 0.15)
```

### 14.2 Compression Ratio
```
REQUIRES:
  - file_content from 0.1
PRODUCES:
  - compression_ratio(path) → float
METHOD:
  raw = len(file_content(path))
  compressed = len(zlib.compress(file_content(path)))
  compression_ratio = compressed / raw
```

---

## Level 15: Historical Sampling

### 15.1 Historical Graph Reconstructor
```
REQUIRES:
  - file_changes from 1.9
  - birth_ts, death_ts from 2.9
  - import_changes (optional) from git diff parsing
PRODUCES:
  - G_import_at(t) → (V, E)
  - sample_times → List[int]
METHOD:
  sample_times = [now - 1mo, now - 3mo, now - 6mo, now - 12mo]
  
  For each t in sample_times:
    V(t) = {path : birth_ts(path) ≤ t < death_ts(path)}
    E(t) = {(a, b) : import added before t and not removed before t}
```

### 15.2 Historical Signal Computation
```
REQUIRES:
  - G_import_at from 15.1
PRODUCES:
  - pagerank_history(path) → List[(t, value)]
  - community_history(path) → List[(t, value)]
METHOD:
  For each t in sample_times:
    Compute PageRank on G_import_at(t)
    Compute Louvain on G_import_at(t)
    Store results with timestamp
```

---

## Level 16: Trajectory Signals

### 16.1 PageRank Velocity
```
REQUIRES:
  - pagerank_history from 15.2
PRODUCES:
  - pagerank_velocity(path) → float
METHOD:
  times = sorted(pagerank_history(path), key=lambda x: x[0])
  if len(times) < 2: return 0
  velocity = (times[-1][1] - times[-2][1]) / (times[-1][0] - times[-2][0])
```

### 16.2 Community Stability
```
REQUIRES:
  - community_history from 15.2
PRODUCES:
  - community_changes(path) → int
  - community_stability(path) → float
METHOD:
  history = sorted(community_history(path), key=lambda x: x[0])
  changes = sum(1 for i in range(1, len(history)) if history[i][1] != history[i-1][1])
  community_changes = changes
  community_stability = 1 - changes / max(len(history) - 1, 1)
```

### 16.3 Global Trajectory
```
REQUIRES:
  - G_import_at from 15.1
  - fiedler_value from 7.2 (for each t)
  - modularity from 8.1 (for each t)
PRODUCES:
  - graph_velocity → float
  - fiedler_trend → float
  - modularity_trend → float
  - topology_stability → float
METHOD:
  # Graph velocity: edge churn
  graph_velocity = mean(|E(t) △ E(t-1)| / |E(t) ∪ E(t-1)|)
  
  # Fiedler trend
  fiedler_trend = linear_regression_slope([fiedler(t) for t in times])
  
  # Modularity trend
  modularity_trend = linear_regression_slope([modularity(t) for t in times])
  
  # Topology stability
  topology_stability = 1 / (1 + graph_velocity)
```

---

## Level 17: Cross-Layer - Global

### 17.1 Mutual Information
```
REQUIRES:
  - E_import, E_cochange, E_author, E_semantic from Level 3
  - V from Level 3
PRODUCES:
  - behavioral_coherence → float
  - conway_alignment → float
  - semantic_alignment → float
METHOD:
  # Edge-based MI between two graphs
  I(G1; G2) = Σₐ Σᵦ (nₐᵦ/n) × log₂[(nₐᵦ × n) / (nₐ• × n•ᵦ)]
  
  where:
    n₁₁ = |{(i,j) : (i,j) in E1 and (i,j) in E2}|
    n₁₀ = |{(i,j) : (i,j) in E1 and (i,j) not in E2}|
    n₀₁ = |{(i,j) : (i,j) not in E1 and (i,j) in E2}|
    n₀₀ = |{(i,j) : (i,j) not in E1 and (i,j) not in E2}|
    n = n₁₁ + n₁₀ + n₀₁ + n₀₀
  
  behavioral_coherence = I(G_import; G_cochange)
  conway_alignment = I(G_import; G_author)
  semantic_alignment = I(G_import; G_semantic)
```

---

## Level 18: Cross-Layer - Per Node

### 18.1 Neighborhood Sets
```
REQUIRES:
  - E_import, E_cochange, E_author from Level 3
PRODUCES:
  - N_import(path) → Set[path]
  - N_cochange(path) → Set[path]
  - N_author(path) → Set[path]
METHOD:
  N_r(path) = {other : (path, other) in E_r or (other, path) in E_r}
```

### 18.2 Hidden Coupling Count
```
REQUIRES:
  - N_import, N_cochange from 18.1
PRODUCES:
  - hidden_coupling_count(path) → int
METHOD: hidden_coupling_count = |N_cochange(path) \ N_import(path)|
```

### 18.3 Neighborhood Coherence
```
REQUIRES:
  - N_import, N_cochange from 18.1
PRODUCES:
  - neighborhood_coherence(path) → float
METHOD:
  intersection = |N_import(path) ∩ N_cochange(path)|
  union = |N_import(path) ∪ N_cochange(path)|
  neighborhood_coherence = intersection / max(union, 1)
```

---

## Level 19: Cross-Layer - Per Pair

### 19.1 Pair Signals
```
REQUIRES:
  - E_import, E_cochange, E_author, E_semantic from Level 3
  - W_import, W_cochange, W_author, W_semantic from Level 3
PRODUCES:
  - has_import(a, b) → bool
  - cochange_strength(a, b) → float
  - author_overlap(a, b) → float
  - semantic_similarity(a, b) → float
  - hidden_coupling_pair(a, b) → float
  - conway_violation_pair(a, b) → float
METHOD:
  has_import(a, b) = (a, b) in E_import or (b, a) in E_import
  cochange_strength(a, b) = W_cochange(a, b) if (a, b) in E_cochange else 0
  author_overlap(a, b) = W_author(a, b) if (a, b) in E_author else 0
  semantic_similarity(a, b) = W_semantic(a, b) if (a, b) in E_semantic else 0
  
  hidden_coupling_pair = cochange_strength × (1 - int(has_import))
  conway_violation_pair = int(has_import) × (1 - author_overlap)
```

---

## Level 20: Module Aggregation

### 20.1 Module Membership
```
REQUIRES:
  - file_list from 0.1
  - project_root
PRODUCES:
  - module(path) → str
  - module_files(module) → Set[path]
METHOD: module = dirname(path) or explicit config
```

### 20.2 Module Edges
```
REQUIRES:
  - E_import from 3.1
  - module from 20.1
PRODUCES:
  - internal_edges(module) → Set[(path, path)]
  - external_edges(module) → Set[(path, path)]
  - incoming_edges(module) → Set[(path, path)]
METHOD:
  internal = {(a, b) in E_import : module(a) == module(b) == m}
  external = {(a, b) in E_import : module(a) == m and module(b) != m}
  incoming = {(a, b) in E_import : module(a) != m and module(b) == m}
```

### 20.3 Module Metrics
```
REQUIRES:
  - internal_edges, external_edges from 20.2
  - module_files from 20.1
PRODUCES:
  - cohesion(module) → float
  - coupling(module) → float
  - Ce(module) → int
  - Ca(module) → int
  - instability(module) → float
METHOD:
  n = |module_files(module)|
  possible_internal = n × (n - 1) / 2
  cohesion = |internal_edges| / max(possible_internal, 1)
  
  Ce = |external_edges|  # efferent
  Ca = |incoming_edges|  # afferent
  coupling = Ce / max(Ce + Ca, 1)
  instability = Ce / max(Ce + Ca, 1)
```

### 20.4 Abstractness
```
REQUIRES:
  - module_files from 20.1
  - role from 12.1
PRODUCES:
  - abstractness(module) → float
METHOD:
  abstract_count = |{p in module : role(p) in {MODEL, INTERFACE, ABSTRACT}}|
  abstractness = abstract_count / |module_files(module)|
```

### 20.5 Main Sequence Distance
```
REQUIRES:
  - instability from 20.3
  - abstractness from 20.4
PRODUCES:
  - main_seq_distance(module) → float
METHOD: main_seq_distance = |abstractness + instability - 1|
```

### 20.6 Boundary Alignment
```
REQUIRES:
  - module_files from 20.1
  - community from 8.1
PRODUCES:
  - boundary_alignment(module) → float
METHOD:
  communities = [community(p) for p in module_files(module)]
  dominant = most_common(communities)
  boundary_alignment = communities.count(dominant) / len(communities)
```

---

## Level 21: Percentile Normalization

### 21.1 Percentile Computer
```
REQUIRES:
  - All numeric signals from Level 6-20
PRODUCES:
  - pctl(signal_name, value) → float
METHOD:
  values = sorted([signal(path) for path in files])
  pctl(x) = index_of(x in values) / len(values)
  
  # Special: ABSOLUTE tier for n < 15 files
  if len(files) < 15:
    pctl(x) = x / max(values)  # linear normalization
```

### 21.2 Effective Percentile
```
REQUIRES:
  - pctl from 21.1
PRODUCES:
  - eff_pctl(signal_name, value) → float
METHOD:
  FLOORS = {
    'pagerank': 0.001,
    'blast_radius': 2,
    'cognitive_load': 3,
  }
  
  if signal in FLOORS and value < FLOORS[signal]:
    return 0.0
  return pctl(signal_name, value)
```

---

## Level 22: Composite Signals - File

### 22.1 Raw Risk
```
REQUIRES:
  - pagerank from 6.1
  - blast_radius_size from 7.7
  - cognitive_load from 14.1
  - churn_cv from 11.2
  - bus_factor from 11.6
  - pctl from 21.1
PRODUCES:
  - raw_risk(path) → float
METHOD:
  raw_risk = 0.25 × pctl('pagerank', pagerank(path))
           + 0.20 × pctl('blast_radius', blast_radius_size(path))
           + 0.20 × pctl('cognitive_load', cognitive_load(path))
           + 0.20 × min(churn_cv(path) / 2, 1)
           + 0.15 × max(0, 1 - bus_factor(path) / 5)
```

### 22.2 Risk Score
```
REQUIRES:
  - raw_risk from 22.1
  - pagerank_velocity from 16.1
  - hidden_coupling_count from 18.2
  - community_stability from 16.2
  - pctl from 21.1
PRODUCES:
  - risk_score(path) → float
METHOD:
  risk_score = 0.15 × pctl('pagerank', pagerank(path))
             + 0.10 × pctl('pagerank_velocity', abs(pagerank_velocity(path)))
             + 0.15 × pctl('blast_radius', blast_radius_size(path))
             + 0.15 × min(churn_cv(path) / 2, 1)
             + 0.15 × max(0, 1 - bus_factor(path) / 5)
             + 0.15 × pctl('hidden_coupling', hidden_coupling_count(path))
             + 0.15 × (1 - community_stability(path))
```

### 22.3 Wiring Quality
```
REQUIRES:
  - is_orphan from 5.3
  - stub_ratio from 13.1
  - phantom_import_count from 3.2
  - hidden_coupling_count from 18.2
  - degree from 5.2
PRODUCES:
  - wiring_quality(path) → float
METHOD:
  phantom_ratio = phantom_import_count(path) / max(import_count(path), 1)
  hidden_ratio = hidden_coupling_count(path) / max(degree(path), 1)
  
  wiring_quality = 1 - (
      0.25 × int(is_orphan(path))
    + 0.25 × stub_ratio(path)
    + 0.25 × phantom_ratio
    + 0.25 × hidden_ratio
  )
```

### 22.4 File Health Score
```
REQUIRES:
  - risk_score from 22.2
  - wiring_quality from 22.3
  - cognitive_load from 14.1
  - is_orphan from 5.3
  - neighborhood_coherence from 18.3
  - pctl from 21.1
PRODUCES:
  - file_health_score(path) → float
METHOD:
  file_health_score = 1 - (
      0.25 × risk_score(path)
    + 0.20 × (1 - wiring_quality(path))
    + 0.20 × pctl('cognitive_load', cognitive_load(path))
    + 0.15 × int(is_orphan(path))
    + 0.20 × (1 - neighborhood_coherence(path))
  )
```

### 22.5 Health Laplacian
```
REQUIRES:
  - file_health_score from 22.4
  - E_import from 3.1
PRODUCES:
  - delta_h(path) → float
METHOD:
  neighbors = {b : (path, b) in E_import} ∪ {a : (a, path) in E_import}
  if len(neighbors) == 0:
    delta_h = 0
  else:
    mean_neighbor = mean(file_health_score(n) for n in neighbors)
    delta_h = file_health_score(path) - mean_neighbor
```

---

## Level 23: Composite Signals - Global

### 23.1 Global Ratios
```
REQUIRES:
  - is_orphan from 5.3
  - phantom_import_count from 3.2
  - file_list from 0.1
PRODUCES:
  - orphan_ratio → float
  - phantom_ratio → float
METHOD:
  orphan_ratio = |{p : is_orphan(p)}| / |file_list|
  phantom_ratio = |{p : phantom_import_count(p) > 0}| / |file_list|
```

### 23.2 Codebase Health
```
REQUIRES:
  - architecture_health from (computed from modules)
  - wiring_score from (computed from ratios)
  - bus_factor from 11.6
  - modularity from 8.1
  - behavioral_coherence from 17.1
  - topology_stability from 16.3
PRODUCES:
  - codebase_health → float
METHOD:
  min_bus = min(bus_factor(p) for p in files if pagerank(p) > pctl_90)
  team_size = |{c.author for c in commits}|
  
  codebase_health = 0.20 × architecture_health
                   + 0.20 × wiring_score
                   + 0.15 × (min_bus / team_size)
                   + 0.15 × modularity
                   + 0.15 × behavioral_coherence
                   + 0.15 × topology_stability
```

---

## Level 24+: Finders

Each finder is a boolean condition on signals:

### GOD_FILE
```
REQUIRES: lines, cognitive_load, in_degree
CONDITION: lines > 500 AND (cognitive_load > pctl_90 OR in_degree > pctl_90)
```

### ORPHAN_CODE
```
REQUIRES: is_orphan, role
CONDITION: is_orphan == True AND role NOT IN {ENTRY, TEST, CONFIG}
```

### HIDDEN_COUPLING
```
REQUIRES: hidden_coupling_pair
CONDITION: hidden_coupling_pair(a, b) > threshold
```

### HIGH_RISK_HUB
```
REQUIRES: pagerank, churn_cv, bus_factor
CONDITION: pagerank > pctl_90 AND (churn_cv > 1.0 OR bus_factor < 2)
```

[... and 18 more finders with specific conditions]

---

## Summary: Level Dependencies

```
Level 0:  Raw data (filesystem, git)
   ↓
Level 1:  Parsing (AST, tokens, git parsing)
   ↓
Level 2:  Resolution (imports → paths, concepts, grouping)
   ↓
Level 3:  Graph construction (5 graphs)
   ↓
Level 4:  Graph fusion (combined graph)
   ↓
Level 5:  Matrices (adjacency, degree, transition)
   ↓
Level 6:  Centrality (PageRank, betweenness)
   ↓
Level 7:  Structure (spectral, SCC, depth, blast radius)
   ↓
Level 8:  Community (Louvain)
   ↓
Level 9:  Distributions (Gini)
   ↓
Level 10: Temporal basic (counts)
   ↓
Level 11: Temporal windowed (churn, trajectory)
   ↓
Level 12: Semantic (role, concepts)
   ↓
Level 13: Derived syntax (stub, impl_gini)
   ↓
Level 14: Cognitive load
   ↓
Level 15: Historical sampling
   ↓
Level 16: Trajectory signals
   ↓
Level 17: Cross-layer global (MI)
   ↓
Level 18: Cross-layer per-node
   ↓
Level 19: Cross-layer per-pair
   ↓
Level 20: Module aggregation
   ↓
Level 21: Percentile normalization
   ↓
Level 22: File composites
   ↓
Level 23: Global composites
   ↓
Level 24+: Finders (22 patterns)
```

---

## Critical Path

The longest dependency chain determines minimum runtime:

```
file_content → AST → import_names → resolved_imports → E_import 
  → A → D → P → pagerank → pagerank_history → pagerank_velocity 
  → pctl → risk_score → file_health_score → delta_h → codebase_health 
  → HIGH_RISK_HUB
```

**Depth: ~24 levels**

---

## Parallelization

**Fully parallel within level:**
- Level 1: All file parsing
- Level 2: All resolution (per file)
- Level 3: Graph construction (5 graphs)
- Level 6-9: Graph algorithms (per graph type)
- Level 10-14: Per-file computations
- Level 24+: All finders

**Sequential:**
- Level 4: Fusion needs all graphs
- Level 15: Historical needs prior graph states
- Level 21: Percentiles need all values
- Level 22-23: Composites need percentiles

---

*End of Corrected DAG*
