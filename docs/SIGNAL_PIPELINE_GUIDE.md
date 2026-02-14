# Shannon Insight: Complete Signal Pipeline Guide

This guide explains how Shannon Insight transforms source code into actionable insights through a multi-stage signal processing pipeline.

---

## Table of Contents

1. [Pipeline Overview](#pipeline-overview)
2. [Stage 1: Source Scanning](#stage-1-source-scanning)
3. [Stage 2: Signal Analysis](#stage-2-signal-analysis)
4. [Stage 3: Signal Fusion](#stage-3-signal-fusion)
5. [Stage 4: Finding Generation](#stage-4-finding-generation)
6. [Complete Signal Reference](#complete-signal-reference)
7. [How Finders Work](#how-finders-work)

---

## Pipeline Overview

```
┌──────────────┐      ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│              │      │              │      │              │      │              │
│    Source    │ ───> │   Scanners   │ ───> │   Analyzers  │ ───> │   Finders    │
│    Files     │      │ (FileMetrics)│      │  (Signals)   │      │  (Findings)  │
│              │      │              │      │              │      │              │
└──────────────┘      └──────────────┘      └──────────────┘      └──────────────┘
                             │                     │                     │
                             │                     │                     │
                             v                     v                     v
                      Language-specific     Graph, Git, Temporal    Risk patterns
                      syntax analysis       semantic analysis       and anti-patterns
```

**Key principle:** Signals are **derived measurements** from code. Finders are **pattern detectors** that combine signals to identify issues.

---

## Stage 1: Source Scanning

### What happens here?
Language-specific scanners parse source files to extract basic **structural metrics**.

### Code location
- `src/shannon_insight/scanning/`
- `ScannerFactory` creates language-specific scanners
- 8 languages supported: Python, Go, TypeScript, JavaScript, Java, Rust, Ruby, C/C++

### Output: `FileMetrics`
Each scanned file produces a `FileMetrics` object with:

```python
@dataclass
class FileMetrics:
    path: str                    # File path
    lines: int                   # Total lines of code
    functions: int               # Number of functions
    structs: int                 # Number of classes/structs
    max_nesting: int             # Deepest nesting level
    imports: list[str]           # List of imported modules
    # ... + more structural data
```

### Example: Python Scanner
```python
# Input file: app.py
def process_data(items):
    if items:
        for item in items:
            if item.valid:
                return item.value
    return None

# Scanner output:
FileMetrics(
    path="app.py",
    lines=6,
    functions=1,
    max_nesting=3,  # if → for → if
    imports=[],
)
```

---

## Stage 2: Signal Analysis

### What happens here?
4 analyzers run in **topologically sorted order** to compute signals from `FileMetrics` and external data (git history, dependencies).

### Analyzers (in order)

#### 1. **StructuralAnalyzer** (`src/shannon_insight/graph/`)
**What it does:** Builds dependency graph and computes graph centrality metrics

**Input:** `FileMetrics` (imports data)
**Output:** Graph signals per file

**Signals produced:**
- `pagerank` - Import centrality (how central is this file in the dependency graph?)
- `betweenness` - Bridge score (how often does this file connect other files?)
- `in_degree` - Number of files that import this file
- `out_degree` - Number of files this file imports
- `depth` - Longest dependency chain from this file
- `community` - Louvain modularity community ID
- `blast_radius_size` - How many files are affected by changes here

**Example:**
```
File: auth.py
├─ Imported by: ["app.py", "api.py", "middleware.py"]  → in_degree = 3
├─ Imports: ["db.py", "utils.py"]                       → out_degree = 2
└─ PageRank: 0.042 (high centrality)
```

**Key algorithms:**
- PageRank (via NetworkX)
- Betweenness centrality
- Louvain community detection
- BFS for depth calculation

---

#### 2. **TemporalAnalyzer** (`src/shannon_insight/temporal/`)
**What it does:** Analyzes git history to compute churn and team metrics

**Input:** Git log (via `git_extractor.py`)
**Output:** Temporal signals per file

**Signals produced:**
- `total_changes` - Number of commits touching this file
- `churn_cv` - Coefficient of variation of changes (volatility)
- `churn_slope` - Rate of change increase/decrease
- `trajectory` - Change pattern (STABILIZING, SURGING, etc.)
- `bus_factor` - Number of people who understand this code (2^H where H is author entropy)
- `author_entropy` - Shannon entropy of author distribution
- `fix_ratio` - Fraction of commits that are bug fixes
- `refactor_ratio` - Fraction of commits that are refactors

**Example:**
```
File: legacy_payment.py
Git history: [commit 1, commit 5, commit 8, commit 15, ...]
├─ total_changes: 47
├─ churn_cv: 1.8 (high volatility - unpredictable change pattern)
├─ bus_factor: 1.2 (low - only 1 person really knows this)
├─ fix_ratio: 0.68 (68% of commits are bug fixes!)
└─ trajectory: THRASHING (frequent fixes, no stabilization)
```

**Key algorithms:**
- Shannon entropy: `H = -Σ p(author) × log₂(p(author))`
- CV (coefficient of variation): `σ / μ`
- Linear regression for slope

---

#### 3. **SemanticAnalyzer** (`src/shannon_insight/semantics/`)
**What it does:** Extracts semantic concepts and code quality signals

**Input:** File content (AST + text analysis)
**Output:** Semantic signals per file

**Signals produced:**
- `semantic_coherence` - How focused is this file on a single concept? (Jaccard similarity of imports)
- `concept_count` - Number of distinct semantic concepts (via TF-IDF)
- `concept_entropy` - Diversity of concepts
- `docstring_coverage` - Fraction of functions with documentation
- `stub_ratio` - Fraction of empty/trivial functions
- `todo_density` - Number of TODO/FIXME comments per 100 LOC
- `naming_drift` - Naming inconsistency score
- `compression_ratio` - Code uniqueness (lower = more duplication)
- `impl_gini` - How evenly distributed is code across functions (Gini coefficient)

**Example:**
```
File: utils.py
Content analysis:
├─ Functions: 42
├─ Stubs (pass/...): 18                    → stub_ratio = 0.43 (hollow!)
├─ With docstrings: 8                      → docstring_coverage = 0.19 (poor)
├─ TODO comments: 7                        → todo_density = 3.5 per 100 LOC
├─ Concepts: ["validation", "formatting",
│             "parsing", "serialization"]  → concept_count = 4
└─ Concept entropy: 1.8 (diverse - lacks focus)
```

**Key algorithms:**
- TF-IDF for concept extraction
- Jaccard similarity for coherence
- Gini coefficient: `G = (2×Σi×xᵢ)/(n×Σxᵢ) - (n+1)/n`

---

#### 4. **SignalFusionAnalyzer** (`src/shannon_insight/signals/fusion.py`)
**What it does:** Combines all raw signals into **composite risk scores**

**Input:** All raw signals from analyzers 1-3
**Output:** Composite scores (risk_score, health_score, etc.)

**Signals produced:**
- `raw_risk` - Pre-normalized risk score
- `risk_score` - Final risk percentile (0-0.1 scale, 90th percentile = 0.9)
- `file_health_score` - Overall health (1-10 scale, higher = better)
- `wiring_quality` - Dependency structure health
- `structural_entropy` - Dependency complexity
- `network_centrality` - Combined centrality score
- `cognitive_load` - How hard is this file to understand (cyclomatic complexity)

**Composite formulas:**

```python
# Risk score (weighted combination)
raw_risk = (
    0.30 × churn_percentile +         # High churn = risky
    0.25 × complexity_percentile +    # High complexity = risky
    0.20 × coupling_percentile +      # High coupling = risky
    0.15 × coherence_deficit +        # Low coherence = risky
    0.10 × stub_ratio                 # Incomplete code = risky
)

# Health score (inverse of risk, scaled to 1-10)
file_health_score = 10 × (1 - risk_score)

# Wiring quality (dependency health)
wiring_quality = (
    0.40 × (1 - orphan_penalty) +     # Not orphaned = good
    0.30 × (1 - phantom_ratio) +      # No broken imports = good
    0.30 × coherence                  # Focused imports = good
)
```

**Example:**
```
File: payment_handler.py
Raw signals → Fusion → Composite:
├─ churn_cv=1.2, total_changes=45    → churn_percentile=0.85
├─ cognitive_load=38, max_nesting=5  → complexity_percentile=0.78
├─ pagerank=0.08, in_degree=12       → coupling_percentile=0.92
└─ stub_ratio=0.15, coherence=0.65   → coherence_deficit=0.35

Combined:
raw_risk = 0.30×0.85 + 0.25×0.78 + 0.20×0.92 + 0.15×0.35 + 0.10×0.15
         = 0.255 + 0.195 + 0.184 + 0.053 + 0.015
         = 0.702

risk_score = 0.702 (70th percentile - high risk!)
file_health_score = 10 × (1 - 0.702) = 2.98 (unhealthy)
```

---

## Stage 3: Signal Fusion

After all analyzers run, we have **35 signals per file**:

| Category | Signal Count | Examples |
|----------|-------------|----------|
| Size & Complexity | 7 | lines, function_count, cognitive_load |
| Structural (Graph) | 10 | pagerank, betweenness, blast_radius_size |
| Code Health | 9 | stub_ratio, docstring_coverage, naming_drift |
| Temporal (Churn) | 9 | total_changes, churn_cv, fix_ratio |
| Team | 2 | bus_factor, author_entropy |
| Composite | 4 | risk_score, health_score, wiring_quality |

**All 35 signals are:**
1. lines
2. function_count
3. class_count
4. max_nesting
5. nesting_depth
6. cognitive_load
7. todo_density
8. pagerank
9. betweenness
10. in_degree
11. out_degree
12. import_count
13. blast_radius_size
14. depth
15. community
16. network_centrality
17. structural_entropy
18. stub_ratio
19. is_orphan
20. phantom_import_count
21. broken_call_count
22. compression_ratio
23. semantic_coherence
24. docstring_coverage
25. naming_drift
26. impl_gini
27. total_changes
28. churn_trajectory
29. trajectory
30. churn_cv
31. churn_slope
32. churn_volatility
33. fix_ratio
34. refactor_ratio
35. change_entropy
36. bus_factor
37. author_entropy
38. risk_score
39. wiring_quality
40. file_health_score
41. raw_risk
42. concept_count
43. concept_entropy

*(Actually 40+ signals if you count all computed values)*

---

## Stage 4: Finding Generation

### What are Finders?

**Finders** are pattern detectors that **read signals** and **emit findings** when they detect anti-patterns.

### Code location
- `src/shannon_insight/insights/finders/`

### Current Finders (7 total)

#### 1. **HighRiskHub** (`high_risk_hub.py`)
**Pattern:** Files with high risk and high coupling

**Signals read:**
- `risk_score` (must be > 0.7)
- `pagerank` (must be > 0.05)
- `total_changes` (must be above median)

**Logic:**
```python
if (risk_score > 0.7 and
    pagerank > 0.05 and
    total_changes > median_changes):
    emit_finding(
        severity=risk_score,
        title="High-Risk Hub: Risky code + high coupling + frequent changes"
    )
```

**Example finding:**
```
Finding: HIGH_RISK_HUB
Title: auth/session_manager.py is a high-risk central hub
Severity: 0.85 (high)
Evidence:
  - risk_score: 0.85 (85th percentile)
  - pagerank: 0.08 (highly coupled)
  - total_changes: 67 (frequent changes)
Suggestion: Refactor to reduce coupling and complexity
```

---

#### 2. **HiddenCoupling** (`hidden_coupling.py`)
**Pattern:** Files that co-change together but aren't directly connected

**Signals read:**
- `cochange_correlation` (from temporal co-change matrix)
- Dependency graph (to verify no direct edge)

**Logic:**
```python
for (file_a, file_b) in all_pairs:
    if (cochange_correlation(file_a, file_b) > 0.6 and
        not has_dependency_edge(file_a, file_b)):
        emit_finding(
            severity=correlation,
            title="Hidden coupling: Files change together without imports"
        )
```

---

#### 3. **GodFile** (`god_file.py`)
**Pattern:** Files with high complexity, size, and centrality

**Signals read:**
- `cognitive_load` (must be > 75th percentile)
- `lines` (must be > 500)
- `pagerank` (must be > 0.05)

**Logic:**
```python
if (cognitive_load_percentile > 0.75 and
    lines > 500 and
    pagerank > 0.05):
    severity = (cognitive_load_percentile + (lines / 2000) + pagerank) / 3
    emit_finding(severity=severity)
```

---

#### 4. **UnstableFile** (`unstable_file.py`)
**Pattern:** Files with volatile change patterns

**Signals read:**
- `churn_cv` (must be > 1.0)
- `trajectory` (must be THRASHING or SURGING)
- `fix_ratio` (must be > 0.5)

---

#### 5. **BoundaryMismatch** (`boundary_mismatch.py`)
**Pattern:** Module boundaries don't match coupling patterns

**Signals read:**
- Module-level `cohesion` (how related are files within a module?)
- Module-level `coupling` (how connected to other modules?)
- Louvain `community` assignments

---

#### 6. **DeadDependency** (`dead_dependency.py`)
**Pattern:** Imported modules that are never used

**Signals read:**
- `phantom_import_count` (imports to non-existent files)
- AST analysis to detect unused imports

---

#### 7. **OrphanCode** (`orphan_code.py`)
**Pattern:** Files not imported by anything

**Signals read:**
- `is_orphan` (boolean flag)
- `in_degree` (must be 0)

---

## How Finders Work: Complete Example

Let's trace a single file through the entire pipeline:

### Input File: `legacy_payment.py`

```python
# legacy_payment.py (200 LOC, last modified 3 months ago)
import stripe
import requests
from db import users, transactions

def process_payment(user_id, amount):
    # TODO: refactor this mess
    user = users.get(user_id)
    if user:
        if user.verified:
            if amount > 0:
                if amount < 10000:
                    # ... 50 lines of nested logic ...
                    pass
    return None

def refund_payment(txn_id):
    pass  # stub

# ... 20 more functions, half are stubs ...
```

### Stage 1: Scanning
```python
FileMetrics(
    path="legacy_payment.py",
    lines=200,
    functions=22,
    structs=0,
    max_nesting=5,
    imports=["stripe", "requests", "db.users", "db.transactions"],
)
```

### Stage 2: Signals

**StructuralAnalyzer:**
```python
pagerank=0.078          # High - many files import this
in_degree=15            # 15 files depend on this
out_degree=4            # Imports 4 modules
blast_radius_size=28    # Changes affect 28 files!
```

**TemporalAnalyzer:**
```python
total_changes=89        # Committed 89 times
churn_cv=1.6            # Highly volatile
fix_ratio=0.72          # 72% of commits are fixes (!)
bus_factor=1.3          # Only 1-2 people know this
trajectory=THRASHING    # Unstable pattern
```

**SemanticAnalyzer:**
```python
stub_ratio=0.45         # 45% of functions are empty
docstring_coverage=0.1  # Only 10% have docs
todo_density=5.0        # 10 TODOs in 200 LOC
concept_count=5         # Unfocused (payments, refunds, validation, ...)
```

**SignalFusion:**
```python
raw_risk = 0.30×0.89 + 0.25×0.68 + 0.20×0.85 + 0.15×0.72 + 0.10×0.45
         = 0.267 + 0.170 + 0.170 + 0.108 + 0.045
         = 0.760

risk_score=0.76         # 76th percentile - HIGH RISK
file_health_score=2.4   # Out of 10 - CRITICAL
```

### Stage 3: Findings

**Finders that fire:**

1. **HighRiskHub**
   - ✅ risk_score (0.76) > 0.7
   - ✅ pagerank (0.078) > 0.05
   - ✅ total_changes (89) > median (23)
   - **Severity: 0.85**

2. **GodFile**
   - ✅ cognitive_load (45) > 75th percentile
   - ✅ lines (200) > 500? NO (skip)
   - ❌ Does not fire

3. **UnstableFile**
   - ✅ churn_cv (1.6) > 1.0
   - ✅ trajectory == THRASHING
   - ✅ fix_ratio (0.72) > 0.5
   - **Severity: 0.78**

4. **HollowCode** (not in current codebase, but planned)
   - ✅ stub_ratio (0.45) > 0.4
   - **Severity: 0.45**

### Final Output

```json
{
  "findings": [
    {
      "finding_type": "high_risk_hub",
      "severity": 0.85,
      "title": "legacy_payment.py is a high-risk central hub",
      "files": ["legacy_payment.py"],
      "evidence": [
        {"signal": "risk_score", "value": 0.76, "percentile": 0.76},
        {"signal": "pagerank", "value": 0.078, "percentile": 0.88},
        {"signal": "total_changes", "value": 89, "percentile": 0.92}
      ],
      "suggestion": "This file is critical (many dependencies), risky (high complexity + churn), and frequently broken. Prioritize refactoring to split responsibilities."
    },
    {
      "finding_type": "unstable_file",
      "severity": 0.78,
      "title": "legacy_payment.py has a volatile change pattern",
      "evidence": [
        {"signal": "churn_cv", "value": 1.6},
        {"signal": "fix_ratio", "value": 0.72},
        {"signal": "trajectory", "value": "THRASHING"}
      ],
      "suggestion": "72% of commits are bug fixes. This suggests underlying design issues. Consider adding tests and refactoring."
    }
  ]
}
```

---

## Module Signals (15 total)

Shannon also computes **15 signals per module** (package/directory):

1. `abstractness` - Ratio of abstract types (interfaces) to concrete types
2. `instability` - Change sensitivity (Ce / (Ca + Ce))
3. `coupling` - Average coupling to other modules
4. `cohesion` - How related are files within this module
5. `main_seq_distance` - Distance from ideal abstraction/stability balance
6. `file_count` - Number of files in module
7. `health_score` - Module health (1-10)
8. `layer_violation_count` - Architectural violations
9. `boundary_alignment` - How well module boundaries match coupling patterns
10. `role_consistency` - How consistent are file roles within module
11. `mean_cognitive_load` - Average complexity
12. `module_bus_factor` - Team knowledge spread
13. `knowledge_gini` - Knowledge concentration (0=equal, 1=concentrated)
14. `coordination_cost` - Team coordination overhead
15. `velocity` - Rate of change

---

## Summary: The Complete Flow

1. **Source Code** → Language scanners extract structure
2. **FileMetrics** → Analyzers compute 35+ signals per file
3. **Signals** → Finders detect patterns and emit findings
4. **Findings** → Dashboard displays actionable insights

**Key insight:** Signals are **measurements**. Finders are **detectors**. The combination transforms "this file has 500 LOC and 45 commits" into "**this file is a high-risk hub that should be refactored**."

---

## Next Steps

1. **Explore signals:** Look at `.shannon/history.db` or the dashboard to see signal values
2. **Read finder code:** Start with `src/shannon_insight/insights/finders/high_risk_hub.py`
3. **Add a custom finder:** Implement the `Finder` protocol and register it in `InsightKernel`
4. **Experiment with thresholds:** Adjust finder logic (e.g., `risk_score > 0.7` → `> 0.6`) to see different results

---

**Questions? Check:**
- `docs/SIGNALS.md` - Full signal definitions
- `docs/FINDERS.md` - Finder catalog
- `CLAUDE.md` - Architecture overview
