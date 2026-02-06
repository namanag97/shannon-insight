# Shannon Insight v2 — Solutions to Known Weaknesses

Research-backed solutions for every identified weakness in the spec. To be integrated into `spec-v2.md`.

---

## W1: IR1 Multi-Language Deep Parsing

### Problem
IR1 needs per-function bodies, call targets, params, nesting depth across 8 languages. Current scanner uses regex — insufficient for deep extraction.

### Solution: tree-sitter + tree-sitter-languages

```bash
pip install tree-sitter==0.25.2
pip install tree-sitter-languages  # 165+ languages, pre-built wheels, no compilation
```

**Why tree-sitter:**
- Production-grade: used by GitHub (Semantic), Sourcegraph, Neovim, Helix
- Fast: ~166K lines/sec, 120ms for 20K lines
- Pre-built grammars for all 8 targets (Python, Go, TS, JS, Java, Rust, Ruby, C/C++)
- Error-tolerant parsing (handles incomplete/broken code)
- S-expression query language for structured extraction

**Per-language query files** (~50 lines each):

```python
# Python query
PYTHON_QUERY = """
(function_definition
  name: (identifier) @fn.name
  parameters: (parameters) @fn.params
  body: (block) @fn.body)

(call
  function: (identifier) @call.direct)

(call
  function: (attribute
    object: (identifier) @call.object
    attribute: (identifier) @call.method))
"""

# Go query
GO_QUERY = """
(function_declaration
  name: (identifier) @fn.name
  parameters: (parameter_list) @fn.params
  body: (block) @fn.body)

(method_declaration
  name: (field_identifier) @fn.name
  parameters: (parameter_list) @fn.params
  body: (block) @fn.body)

(call_expression
  function: (identifier) @call.direct)

(call_expression
  function: (selector_expression
    operand: (identifier) @call.object
    field: (field_identifier) @call.method))
"""
```

**Architecture:**

```
tree-sitter-languages (pre-built)
         │
    ┌────▼────┐
    │ Parser  │  one per language
    └────┬────┘
         │  AST
    ┌────▼────┐
    │ Query   │  language-specific .scm file
    │ Engine  │  extracts functions, calls, classes
    └────┬────┘
         │  raw captures
    ┌────▼────────┐
    │ Normalizer  │  language-agnostic FileSyntax output
    │             │  shared data model for all languages
    └─────────────┘
```

**What tree-sitter gives us:**
- Function names, params, body source text, start/end lines ✓
- Call site identification (syntactic) ✓
- Class definitions, inheritance, fields ✓
- Import statements with full paths ✓
- Nesting depth (tree depth from function root) ✓
- Decorator/annotation extraction ✓

**What tree-sitter does NOT give us:**
- Type inference (what type is `self.db`?)
- Cross-file symbol resolution (where does `db.query` point to?)
- Virtual dispatch resolution (which override gets called?)

These limitations are handled by W4 (call resolution) below.

**Alternatives considered and rejected:**
- srcML: Missing Go, Rust, Ruby, TypeScript
- LSIF: Too complex (requires full build environments)
- Joern: JVM dependency, overkill for syntax extraction
- Universal ctags: Regex-based, no body/call extraction
- Semgrep: OCaml, not Python-friendly as a library

**Effort estimate:** 2-3 weeks for all 8 languages (query files + normalizer + tests).

**Sources:**
- [py-tree-sitter docs](https://tree-sitter.github.io/py-tree-sitter/)
- [tree-sitter-languages PyPI](https://pypi.org/project/tree-sitter-languages/)
- [tree-sitter query syntax](https://tree-sitter.github.io/tree-sitter/using-parsers/queries/1-syntax.html)
- [Building call graphs with tree-sitter (DZone)](https://dzone.com/articles/call-graphs-code-exploration-tree-sitter)

---

## W2: Small Codebase Degradation

### Problem
Percentiles, Gini, PCA, clustering break down with < 30 files. First users will try small projects.

### Solution: Tiered analysis with absolute thresholds as foundation

**Tier system:**

| Codebase size | Strategy | Techniques enabled |
|---|---|---|
| **< 15 files** | Absolute thresholds only | Per-function complexity, nesting, stubs, orphans, phantoms. No percentiles, no Gini, no clustering. Show raw values with universal bounds. |
| **15–50 files** | Absolute + Bayesian percentiles | Add percentile-based signals using Bayesian priors from larger codebases. Show confidence intervals. Enable basic graph analysis. |
| **50+ files** | Full analysis | Everything: percentiles, Gini, PCA, clustering, tensor analysis, all finders. |

**Universal absolute thresholds** (work at any codebase size):

| Signal | Threshold | Source |
|---|---|---|
| Cyclomatic complexity per function | > 10 | McCabe 1976, NIST-endorsed |
| Max nesting depth per function | > 4 | Widely agreed |
| Function body lines | > 50 | Most style guides |
| File lines | > 500 | Rough consensus |
| Function params | > 5 | Clean Code |
| Stub: body_tokens | < 5 | Observable (pass, ..., return None) |
| Orphan: in_degree | = 0 AND not entry point | Structural fact |
| Phantom: unresolved import | any | Structural fact |

**Bayesian priors for medium codebases (15-50 files):**

```
Instead of: percentile(x) = |{v ≤ x}| / |values|    (noisy with n=20)

Use: posterior_percentile(x) = Beta(α + rank, β + n - rank)
     where α, β are prior parameters from industry data

Prior: fit Beta distribution to signal values from PROMISE/TechDebt datasets
       (33 Apache projects, 1000s of files → stable priors)
```

This regularizes percentiles toward industry norms when the sample is small.

**Focus on trends** — works at any size:

```
For any signal S:
  trend = S(now) - S(previous_snapshot)
  direction = IMPROVING | STABLE | WORSENING

Even with 5 files, "complexity is increasing" is meaningful.
```

**UI behavior for small codebases:**
- Don't show percentile-based findings (hide, don't disable — explain why)
- Show absolute threshold violations prominently
- Show orphan/phantom/stub detection (these are structural facts, not statistical)
- Emphasize trends over snapshots
- Show message: "Full analysis available for codebases with 50+ files"

**Sources:**
- [SonarQube quality gates (absolute thresholds)](https://docs.sonarsource.com/sonarqube-server/quality-standards-administration/managing-quality-gates/introduction-to-quality-gates)
- [Bayesian analysis for SE data](https://dl.acm.org/doi/10.1145/3490953)
- [Small sample analysis in SE (Kitchenham & Madeyski 2024)](https://link.springer.com/article/10.1007/s10664-024-10504-1)
- [NIST on cyclomatic complexity](https://learn.microsoft.com/en-us/visualstudio/code-quality/code-metrics-cyclomatic-complexity)

---

## W3: Composite Score Calibration

### Problem
All composite scores (risk, health, wiring) use hand-tuned weights. No validation that they predict anything real.

### Solution: Calibrate against labeled defect datasets using logistic regression

**Available ground truth:**

| Dataset | Size | What it has |
|---|---|---|
| **PROMISE/Tera-PROMISE** | 200+ projects | 20 OO metrics per class + defect labels |
| **Technical Debt Dataset** | 33 Apache projects, 78K commits | 95K SonarQube issues, fault data from Jira |
| **Defects4J** | 357 real Java bugs | Bug-triggering tests, file-level bug locations |
| **GitHub Bug Database** | 15 Java projects | Known bugs matched to source files |

**Calibration procedure:**

```
1. Run Shannon Insight on Technical Debt Dataset projects (33 Apache Java projects)

2. Extract per-file signal vectors:
   x(f) = [pagerank, blast_radius, cognitive_load, churn, bus_factor, ...]

3. Label files from ground truth:
   y(f) = 1 if file has known bug in Jira, 0 otherwise

4. Fit logistic regression:
   P(bug | x) = σ(w · x)
   where w = learned weights, σ = sigmoid

5. Learned weights w replace hand-tuned weights in all composite scores

6. Cross-validate: train on 25 projects, test on 8. Report AUC, precision, recall.

7. Report per-signal predictive power:
   Rank signals by |coefficient| in the logistic model.
   Drop signals with near-zero coefficients.
```

**Key finding from literature — most predictive signals:**

| Rank | Signal | Source |
|---|---|---|
| 1 | **Relative code churn** | Nagappan & Ball 2005, 89% accuracy |
| 2 | **Number of distinct committers** | Rahman & Devanbu 2013 |
| 3 | **File age / recency** | Multiple studies |
| 4 | **Coupling (PageRank proxy)** | Basili CK metrics validation |
| 5 | **Lack of cohesion** | CK metrics suite |
| 6 | **Cyclomatic complexity** | McCabe — correlated but weaker than process metrics |

**Critical insight:** Process metrics (churn, authors, age) outperform code metrics (complexity, coupling) for defect prediction. Our temporal signals (D6, D7, D8) are likely MORE predictive than our structural signals (D1, D2, D4). This validates the multi-dimensional approach — we need both, but temporal should be weighted higher.

**Fallback for v2.0 (before calibration):**
- Use **rank ordering** instead of absolute scores
- Display: "This file is the #1 riskiest in your codebase" rather than "risk = 0.87"
- Rank ordering is robust to weight misspecification

**Sources:**
- [PROMISE repository](http://promise.site.uottawa.ca/SERepository/)
- [Technical Debt Dataset (ACM 2019)](https://dl.acm.org/doi/10.1145/3345629.3345630)
- [Defects4J](https://dl.acm.org/doi/10.1145/2610384.2628055)
- [GitHub Bug Database](https://www.inf.u-szeged.hu/~ferenc/papers/GitHubBugDataSet/)
- [Process vs code metrics (Rahman & Devanbu 2013)](https://dl.acm.org/doi/10.1145/2568225.2568269)
- [Code churn predicts defects (Nagappan & Ball 2005)](https://www.st.cs.uni-saarland.de/edu/recommendation-systems/papers/ICSE05Churn.pdf)
- [SonarQube fault prediction study (ESE 2022)](https://link.springer.com/article/10.1007/s10664-022-10164-z)

---

## W4: Call Graph Resolution Without Type Inference

### Problem
Resolving `self.db.query()` requires type inference. Without it, CALL edges are unreliable.

### Solution: Language-specific tools for Python. Syntactic heuristics for others. Confidence tags on edges.

**Python (primary target): PyCG or JARVIS**

| Tool | Precision | Recall | Speed | Year |
|---|---|---|---|---|
| PyCG | ~99% | ~70% | 0.38s / 1K LOC | 2021 (ICSE) |
| **JARVIS** | ~99% | **~84%** | 67% faster than PyCG | **2024 (SOTA)** |

JARVIS uses flow-sensitive intra-procedural analysis with strong updates. It resolves:
- Direct function calls ✓
- Method calls on known types ✓
- Class instantiation ✓
- Module-qualified calls ✓
- Import aliases ✓

It does NOT resolve:
- `eval()` / `getattr()` / metaprogramming
- Complex closures
- Runtime-only dispatch

**Other languages: tree-sitter syntactic extraction + import tracking**

```
For each call site (from tree-sitter):
  1. Direct call: foo()
     → search imports for "foo" → resolve to file
     → confidence: HIGH

  2. Qualified call: module.foo()
     → search imports for "module" → resolve to file, find "foo" in it
     → confidence: HIGH

  3. Method call: obj.method()
     → search imports for obj's declared type (if type-hinted)
     → if no type hint, search all imported files for "method" definition
     → confidence: LOW (ambiguous)

  4. Chained call: a.b.c()
     → confidence: VERY LOW (skip or flag)
```

**Confidence tagging on edges:**

```
Edge:
  source: str
  target: str
  type: CALL
  confidence: HIGH | MEDIUM | LOW
  resolution: EXACT | HEURISTIC | AMBIGUOUS
```

Finders that depend on CALL edges can filter by confidence:
- Dead import detection: only use HIGH confidence edges
- Call depth analysis: only use HIGH + MEDIUM
- Disagreement analysis: flag LOW confidence results separately

**Estimated per-language accuracy:**

| Language | Approach | Precision | Recall |
|---|---|---|---|
| Python | JARVIS | ~99% | ~84% |
| JavaScript | ACG (approximate call graph) | ~98% | ~80% |
| Java | RTA via tree-sitter + heuristics | ~90% | ~70% |
| Go | tree-sitter + import tracking | ~85% | ~65% |
| TypeScript | Same as JS + type annotations | ~90% | ~75% |
| Rust/Ruby/C | tree-sitter syntactic only | ~70% | ~50% |

**For v2.0:** Ship Python CALL edges as first-class (JARVIS integration). Ship other languages with syntactic heuristics + confidence tags. Don't build finders that require CALL edges from low-confidence languages.

**Sources:**
- [PyCG (ICSE 2021)](https://arxiv.org/pdf/2103.00587)
- [JARVIS (2024 SOTA)](https://arxiv.org/abs/2305.05949)
- [Static JS call graphs comparative study (2024)](https://arxiv.org/html/2405.07206v1)
- [Call graph recall in practice (ICSE 2020)](https://ieeexplore.ieee.org/document/9283958)
- [CHA/RTA explained](https://ben-holland.com/call-graph-construction-algorithms-explained/)

---

## W5: Dimension Correlation

### Problem
The 8 dimensions may be correlated in practice, making the "8D space" actually 3-4D.

### Solution: Empirical validation via PCA + signal correlation analysis

**Procedure:**

```
1. Select 5-10 well-known open-source projects (Django, Flask, FastAPI, requests, pandas)
2. Run full analysis → extract ~40 signal vectors per file
3. Compute correlation matrix (40×40)
4. Flag pairs with |r| > 0.8 as redundant
5. Run PCA, report eigenvalue spectrum
6. Report effective dimensionality = k where Σᵢ₌₁ᵏ λᵢ / Σ λᵢ > 0.90
```

**If effective dimensionality is low (3-4):**
- Use PC scores as composite signals (replacing arbitrary weight fusion)
- The PCs themselves become interpretable: "PC1 = structural risk, PC2 = social risk, PC3 = information quality"
- Radar chart shows PC scores, not raw dimensions

**If effective dimensionality is high (8+):**
- Dimensions are genuinely independent — current approach is correct
- Each dimension contributes unique information

**Integration:**
- Report effective dimensionality in the web UI ("Your codebase has 5 independent quality factors")
- Use PCA-decorrelated signals for composite scores (eliminates double-counting correlated signals)
- Drop redundant signals from the tensor (keep the more interpretable one from each correlated pair)

**This is a validation step, not a design change.** Run it before finalizing composite score weights.

---

## W6: Concept Extraction for Small Files

### Problem
TF-IDF + Louvain needs minimum ~50 tokens. Most files are smaller. Concept extraction produces noise.

### Solution: Two-tier approach — heuristic roles (always) + concept extraction (when data suffices)

**Tier 1: Role classification (always, any file size)**

Pattern-based, zero minimum size. Works like ArchUnit/NDepend:

```python
def classify_role(file: FileSyntax) -> Role:
    # Structural patterns (from tree-sitter parse)
    if matches_test_patterns(file.path):           return TEST
    if has_main_guard(file):                        return ENTRY_POINT
    if has_abc_or_protocol(file):                   return INTERFACE
    if all_caps_ratio(file) > 0.8:                  return CONSTANT
    if mostly_exception_classes(file):              return EXCEPTION
    if field_heavy_classes(file):                   return MODEL
    if has_cli_decorators(file):                    return CLI
    if has_state_and_methods(file):                 return SERVICE
    if all_functions_no_classes(file):              return UTILITY
    return UNKNOWN
```

This is robust, deterministic, and fast. No ML, no minimum data.

**Tier 2: Concept extraction (files with 20+ unique identifiers)**

```
if unique_identifier_count(file) >= 20:
    concepts = tfidf_louvain(file)      # current approach
    concept_entropy = H(concept_weights)
    naming_drift = cosine(filename, concepts)
else:
    concepts = [Concept(topic=role.name, weight=1.0)]
    concept_entropy = 0.0               # not enough data
    naming_drift = None                 # not computable
```

**For future improvement: BERTopic**

BERTopic (BERT embeddings → UMAP → HDBSCAN → c-TF-IDF) works on 20-50 tokens and handles short documents much better than LDA. It's the modern replacement for LDA in topic modeling.

```bash
pip install bertopic
```

However, BERTopic adds a transformer model dependency (~500MB). Keep TF-IDF + Louvain for v2.0, add BERTopic as optional enhancement.

**code2vec / CodeBERT for later:**
- code2vec learns distributed representations from AST paths — excellent for function-level embeddings
- CodeBERT achieves 95% accuracy on code classification when combined with code2vec + FastText
- These are heavy dependencies but could replace our concept extraction entirely

**Sources:**
- [BERTopic GitHub](https://github.com/MaartenGr/BERTopic)
- [code2vec (POPL 2019)](https://dl.acm.org/doi/10.1145/3290353)
- [Topic modeling in SE research (Springer 2021)](https://link.springer.com/article/10.1007/s10664-021-10026-0)
- [Short text topic modeling survey (Springer 2022)](https://link.springer.com/article/10.1007/s10462-022-10254-w)
- [IdBench for identifier embeddings](https://github.com/sola-st/IdBench)

---

## W7: Module Boundary Detection

### Problem
"Module = parent directory" fails for flat projects, deep nesting, and monorepos.

### Solution: Layered approach — directory first, Louvain fallback, config override

**Algorithm:**

```
1. DETECT PROJECT ROOTS
   Scan for package markers: pyproject.toml, package.json, go.mod, Cargo.toml, pom.xml
   Each marker = a project root in a monorepo

2. DETERMINE MODULE GRANULARITY
   For each project root:
     depth_histogram = count files at each directory depth
     module_depth = shallowest depth where most directories have 3+ files
     modules = directories at module_depth

   If flat (all files in one directory):
     modules = Louvain communities from dependency graph

3. COMPUTE BOUNDARY ALIGNMENT
   For each module:
     louvain_community = dominant community of its files
     alignment = |files in dominant community| / |files in module|

   If alignment < 0.5:
     warn("Directory boundary doesn't match dependency structure")
     suggest Louvain communities as alternative boundaries

4. USER OVERRIDE (shannon-insight.toml)
   [modules]
   custom = [
     {name = "auth", paths = ["src/auth/", "src/middleware/auth*"]},
     {name = "payments", paths = ["src/payments/", "src/billing/"]},
   ]
```

**Research backing:**
- Louvain achieves 60-80% MoJoFM (similarity to ground truth) on real codebases
- Bunch tool uses genetic algorithm + MQ fitness — we can use Louvain as equivalent
- ACDC uses pattern-based heuristics — our role classification (W6) supplements this

**For monorepos:**
- Detect workspace definitions (npm workspaces, Nx project.json, Python namespace packages)
- Each workspace = a top-level module
- Within each workspace, apply normal module detection

**Sources:**
- [Louvain MoJoFM evaluation](https://link.springer.com/chapter/10.1007/978-3-030-29983-5_5)
- [Bunch tool](https://www.semanticscholar.org/paper/Bunch:-a-clustering-tool-for-the-recovery-and-of-Mancoridis-Mitchell/0c809e82f84154d55471e16e2e567d86f4b56e2b)
- [ACDC algorithm](https://www.researchgate.net/publication/221200422_ACDC_An_Algorithm_for_Comprehension-Driven_Clustering)
- [Nx module boundaries](https://nx.dev/docs/concepts/decisions/why-monorepos)

---

## W8: Martin's Abstractness for Python

### Problem
Python rarely uses ABC/Protocol. Abstractness = 0 for most modules, making D = |0 + I - 1| useless.

### Solution: Expanded abstractness definition for dynamic languages

**Python abstractness formula:**

```python
def abstractness(module: Module) -> float:
    abstract_count = 0
    total_count = 0

    for file in module.files:
        for cls in file.classes:
            total_count += 1
            if is_abstract(cls):
                abstract_count += 1
        for fn in file.functions:
            total_count += 1

    if total_count == 0:
        return 0.0
    return abstract_count / total_count

def is_abstract(cls: ClassDef) -> bool:
    return (
        inherits_abc(cls)                           # class Foo(ABC):
        or inherits_protocol(cls)                   # class Foo(Protocol):
        or has_abstractmethod_decorator(cls)         # @abstractmethod
        or all_methods_raise_not_implemented(cls)    # raise NotImplementedError
        or has_only_method_signatures(cls)           # class with pass-only methods
        or is_never_instantiated(cls)                # no MyClass() anywhere in codebase
    )
```

**"Never instantiated" check** (from IR3 CALL edges):
```
For each class C:
  instantiated = any file calls C() in the codebase
  if not instantiated AND C has subclasses:
    C is abstract-like
```

**Coupling-based proxy** (fallback if A is still near-zero):

```
A_proxy = Ca / (Ca + Ce)
```

Modules with high afferent coupling (many dependents) are functionally abstract even without formal interfaces. They BEHAVE like abstract modules — changing them breaks things.

**Updated main sequence:**

```
D = |A + I - 1|      where A = expanded abstractness
D_proxy = |A_proxy + I - 1|    if A is near-zero for all modules
```

Report both if they differ significantly. Let the user choose which model fits their codebase.

**TypeScript/JavaScript:**
- Count `interface` and `abstract class` keywords (TS)
- Count classes with only method signatures (JS)
- Apply same "never instantiated" heuristic

**Go:**
- Count `interface` types (Go has explicit interfaces)
- Abstractness works naturally in Go

**Sources:**
- [PEP 544 – Protocols](https://peps.python.org/pep-0544/)
- [Martin's package metrics](https://en.wikipedia.org/wiki/Software_package_metrics)
- [OO metrics for dynamic languages](https://kariera.future-processing.pl/blog/object-oriented-metrics-by-robert-martin/)

---

## W9: Validation Methodology

### Problem
No way to know if any of this is correct without validation against real outcomes.

### Solution: Three-phase validation pipeline

**Phase 1: Retrospective validation (pre-launch)**

```
1. Select benchmark projects:
   - Technical Debt Dataset: 33 Apache Java projects, 95K labeled issues
   - Defects4J: 357 real bugs in 5 Java programs
   - PROMISE: 200+ projects with defect labels

2. Run Shannon Insight on each project

3. For each finding type, compute:
   precision = |files flagged AND actually buggy| / |files flagged|
   recall = |files flagged AND actually buggy| / |actually buggy files|
   F1 = 2 × precision × recall / (precision + recall)

4. For composite scores, compute:
   AUC = area under ROC curve (risk_score vs. has_bug)
   Spearman ρ = rank correlation (risk_rank vs. bug_count)

5. Acceptance criteria:
   - AUC > 0.70 for risk score (better than random)
   - Precision > 0.50 for each finder (at least half the flags are real)
   - Recall > 0.30 for each finder (catches at least 30% of real issues)
```

**Phase 2: Prospective validation (post-launch)**

```
Web UI additions:
  - Thumbs up/down on each finding ("Was this useful?")
  - "Dismiss" button with reason (false positive, won't fix, already known)
  - Track: which findings lead to code changes within 30 days

Metrics:
  - Actionability rate = |findings acted on| / |findings shown|
  - False positive rate = |dismissed as FP| / |total findings|
  - User satisfaction = thumbs up / (thumbs up + thumbs down)

Target: actionability > 30%, FP rate < 40%
```

**Phase 3: Predictive validation (6+ months)**

```
For projects with issue trackers (Jira, GitHub Issues):

  1. Compute risk_score(file) at time T
  2. Count bugs_filed(file) between T and T+90 days
  3. Compute: Spearman ρ(risk_score, future_bugs)

  If ρ > 0.3: risk score is predictive (usable)
  If ρ > 0.5: risk score is strongly predictive (valuable)
  If ρ < 0.1: risk score is noise (needs recalibration)
```

**NCD clone detection — use as pre-filter only:**

Research shows token-based + AST hybrid methods outperform NCD for code clone detection. JPlag and difflib outperform NCD variants on the SOCO benchmark.

```
Clone detection pipeline:
  1. NCD pre-filter (fast, catches ~70% of clones)
  2. Token-based verification (slower, high precision)

Don't rely on NCD alone for CopyPasteClone findings.
```

**Gold standard benchmark codebases:**
- Juliet Test Suite: 64K test cases in 100K files (SAST benchmarking)
- Qualitas Corpus: curated collection of Java systems for empirical studies
- Technical Debt Dataset: 33 projects, multi-tool analysis

**Sources:**
- [PROMISE repository](http://promise.site.uottawa.ca/SERepository/)
- [Technical Debt Dataset](https://arxiv.org/pdf/1908.00827)
- [Defects4J](https://dl.acm.org/doi/10.1145/2610384.2628055)
- [GitHub Bug Database](https://www.inf.u-szeged.hu/~ferenc/papers/GitHubBugDataSet/)
- [Bad smell detection tool comparison (EASE 2016)](https://dl.acm.org/doi/10.1145/2915970.2915984)
- [SonarQube issues and faults (ESE 2022)](https://link.springer.com/article/10.1007/s10664-022-10164-z)
- [Clone detection comparison (ICSE 2023)](https://wu-yueming.github.io/Files/ICSE2023_TACC.pdf)
- [NCD limitations study](https://link.springer.com/article/10.1007/s11416-015-0260-0)
- [Juliet Test Suite](https://www.softwaretestinghelp.com/code-quality-tools/)

---

## Summary: Confidence After Research

| # | Weakness | Before | After | Key solution |
|---|----------|--------|-------|-------------|
| W1 | IR1 multi-language parsing | Low | **High** | tree-sitter-languages (pre-built, 165+ langs, 166K lines/sec) |
| W2 | Small codebases | Low | **High** | Tiered: absolute thresholds < 15 files, Bayesian 15-50, full 50+ |
| W3 | Score calibration | Low | **High** | PROMISE + TechDebt datasets + logistic regression for weights |
| W4 | Call resolution | Low | **Med-High** | JARVIS for Python (99%/84%), heuristics + confidence tags for others |
| W5 | Dimension correlation | Unknown | **Testable** | PCA on real data before launch, report effective dimensionality |
| W6 | Concept extraction noise | Low | **Medium** | Heuristic roles (always) + TF-IDF concepts (20+ tokens) + BERTopic later |
| W7 | Module boundaries | Low | **Med-High** | Directory → Louvain fallback → config override. 60-80% MoJoFM. |
| W8 | Martin's A for Python | Low | **Medium** | Expanded: ABC + Protocol + NotImplementedError + never-instantiated + coupling proxy |
| W9 | No validation | None | **Feasible** | 3-phase: retrospective (datasets) → prospective (UI feedback) → predictive (bug correlation) |

**No showstoppers remain.** Every weakness has a researched, practical solution with concrete tools, datasets, and accuracy numbers.
