# Shannon Insight v2 — Feature Brainstorm

## Domain Map

| Domain | What it answers | Math/Technique |
|--------|----------------|----------------|
| **AI Code Quality** | Is this AI-generated code actually wired together? | Graph connectivity, entropy, compression |
| **Root Cause** | Why did this get bad? | Git blame + threshold crossing |
| **Social/Team** | Who knows what? Who's a bus factor? | Author graph, knowledge distribution |
| **Refactoring** | What exactly should I move/split/extract? | Clustering, min-cut, community detection |
| **PR Risk** | How dangerous is this changeset? | Blast radius × centrality × instability |
| **Architecture** | Does reality match intent? | Layer graphs, dependency flow |
| **Temporal** | What patterns emerge over time? | Time series, co-evolution, regression |
| **Test Gap** | Where are we flying blind? | Test↔source mapping, coverage overlay |
| **Onboarding** | Where should a newcomer start? | Topological sort, entry point scoring |

---

## 1. AI Code Quality (NEW — high priority)

Detect patterns typical of AI-generated codebases that look complete but aren't.

### Disconnected Components
- **Orphan files**: Files with zero in-degree that aren't entry points — written but never imported
- **Dead exports**: Functions/classes defined but never called anywhere in the codebase
- **Island modules**: Directory-level components with no edges to the rest of the graph
- **Math**: Connected components on dependency graph; flag non-trivial components disconnected from main

### Stub / Hollow Code
- **Empty functions**: Functions with just `pass`, `...`, `return None`, or a single-line return
- **Shallow implementations**: Abnormally low compression ratio relative to function count (lots of signatures, little logic)
- **TODO graveyards**: High density of TODO/FIXME/HACK comments relative to actual logic
- **Math**: Ratio of function_count to compressed_size; entropy per function

### Hallucinated References
- **Phantom imports**: Import statements referencing modules/packages that don't exist in project or installed deps
- **Broken call chains**: Function A calls B, B calls C, but C doesn't exist or has wrong signature
- **Missing routes/endpoints**: URL patterns or API routes defined but handler functions don't exist (or vice versa)
- **Math**: Graph edge validation — every edge target must resolve

### Structural Incoherence
- **Naming drift**: File names suggest one domain, identifiers inside suggest another (e.g., `auth.py` full of payment logic)
- **Copy-paste modules**: Near-identical files with minor variations (high cross-file compression ratio)
- **Inconsistent patterns**: Some modules use class-based, others functional, others mixed — no architectural consistency
- **Math**: Cross-file cosine similarity on identifier vectors; compression ratio of concatenated file pairs

### Missing Glue
- **No orchestration layer**: Many leaf modules exist but nothing composes them
- **Flat call graph**: Call depth ≤ 1 everywhere (everything called directly from entry point, no composition)
- **Config without consumers**: Config/settings defined but never read
- **Math**: Call graph depth distribution; ratio of leaf nodes to internal nodes

### Premature Abstraction
- **Wrapper-only files**: Classes that just delegate to one other class (pass-through ratio)
- **Deep inheritance, no logic**: Inheritance depth > 2 but override count ≈ 0
- **Interface bloat**: Many small interfaces/protocols with single implementors
- **Math**: Delegation ratio = forwarded_calls / total_methods

### Composite AI Score
Fuse signals into a single "AI code smell" score:
- `orphan_ratio × 0.25 + hollow_ratio × 0.25 + phantom_imports × 0.20 + coherence_drift × 0.15 + glue_deficit × 0.15`

---

## 2. Root Cause / "Why"

- **Blame attribution**: Which commits introduced a finding
- **Decay timeline**: When did a file cross the threshold into "bad"
- **Regression detection**: Finding resolved then re-appeared
- **Commit tagging**: Auto-classify commits as refactor/feature/fix from message + diff shape

---

## 3. Social / Team

- **Bus factor**: Distinct authors on critical hubs (1 author = risk)
- **Knowledge silos**: Files only one person has ever modified
- **Team coupling**: Author pairs that always co-change same files
- **Review blindspots**: High centrality + low author diversity

---

## 4. Actionable Refactoring

- **Split plan**: Cluster identifiers to suggest which functions go where
- **Move targets**: For boundary mismatches, name the destination directory
- **Cycle breaking**: Identify weakest edge in SCC (fewest imports + lowest co-change)
- **Extract interface**: High in-degree files → suggest protocol/interface

---

## 5. PR / Change Risk

- **Risk score**: `Σ (blast_radius × centrality × instability)` for touched files
- **Complexity delta**: +/- cognitive load per file in the diff
- **"What breaks" preview**: Transitive dependents of changed files
- **Hotspot amplification**: PR touches an already-churning file → extra warning

---

## 6. Architecture

- **Layer violations**: Define layers, flag imports that skip levels
- **Dependency flow**: Detect utility→feature imports (wrong direction)
- **Module health**: Aggregate file signals to per-directory score
- **Architecture drift**: Actual graph vs. declared/intended architecture

---

## 7. Richer Temporal

- **Co-evolution clusters**: Groups of 3+ files (not just pairs) via frequent itemset mining
- **Fix-commit hotspots**: Files attracting most "fix"/"bug" commits
- **Time-to-stabilize**: How long after creation/refactor until churn drops
- **Seasonal patterns**: Release-cycle vs steady-state activity

---

## 8. Test Gap

- **Test↔source mapping**: Convention-based (test_foo.py → foo.py) + import-based
- **Uncovered hubs**: High centrality + no test file → red flag
- **Test-to-complexity ratio**: Test LOC / source cognitive load per module

---

## 9. Onboarding

- **Entry points**: Low complexity + high centrality = good starting files
- **Reading order**: Topological sort of dependency graph
- **Concept glossary**: Dominant identifier clusters per module as auto-generated docs

---

## Priority Matrix

| Feature | Impact | Effort | Uniqueness |
|---------|--------|--------|------------|
| AI Code Quality (orphans, stubs, phantoms) | ★★★★★ | Medium | Very high — nobody does this |
| PR Risk Scoring | ★★★★★ | Medium | High |
| Bus Factor / Knowledge Silos | ★★★★ | Low | Medium |
| Actionable Split/Move suggestions | ★★★★ | High | High |
| Root Cause / Decay Timeline | ★★★ | Medium | Medium |
| Architecture Drift | ★★★ | High | High |
| Test Gap Detection | ★★★★ | Medium | Medium |
| Co-evolution Clusters | ★★★ | Medium | High |
| Onboarding / Reading Order | ★★ | Low | Medium |
