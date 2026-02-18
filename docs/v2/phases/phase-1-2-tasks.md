# Phase 1 & 2 Implementation Tasks

## Status: PLANNING
**Created:** 2026-02-18
**Priority:** CRITICAL - Current architecture loses data

---

## Phase 1: Fix Scanning & Storage

### P1.1 - Enhance FileSyntax Model
**File:** `src/shannon_insight/scanning/syntax.py`

- [ ] **P1.1.1** Add `content_hash: str` field (SHA-256 of content)
- [ ] **P1.1.2** Add `absolute_path: str` field
- [ ] **P1.1.3** Add `start_line`, `end_line` to ClassDef (currently missing)
- [ ] **P1.1.4** Add `qualified_name` to FunctionDef ("ClassName.method" format)
- [ ] **P1.1.5** Add `is_stdlib: bool` to ImportDecl
- [ ] **P1.1.6** Add `is_relative: bool` to ImportDecl (computed from source.startswith("."))

### P1.2 - Create Fact Storage Database
**File:** `src/shannon_insight/persistence/facts.py` (NEW)

- [ ] **P1.2.1** Create `FactDatabase` class with SQLite backend
- [ ] **P1.2.2** Create `analysis_sessions` table schema
- [ ] **P1.2.3** Create `file_facts` table schema
- [ ] **P1.2.4** Create `function_facts` table schema
- [ ] **P1.2.5** Create `class_facts` table schema
- [ ] **P1.2.6** Create `import_facts` table schema
- [ ] **P1.2.7** Create indexes for graph queries

### P1.3 - Create Fact Data Models
**File:** `src/shannon_insight/persistence/fact_models.py` (NEW)

- [ ] **P1.3.1** Create `FileFact` dataclass
- [ ] **P1.3.2** Create `FunctionFact` dataclass
- [ ] **P1.3.3** Create `ClassFact` dataclass
- [ ] **P1.3.4** Create `ImportFact` dataclass
- [ ] **P1.3.5** Create conversion: `FileSyntax` → `FileFact`

### P1.4 - Store Facts After Scanning
**File:** `src/shannon_insight/insights/kernel.py`

- [ ] **P1.4.1** Create session record at analysis start
- [ ] **P1.4.2** After scanning, convert FileSyntax → FileFact
- [ ] **P1.4.3** Store all FileFacts to FactDatabase
- [ ] **P1.4.4** Store all FunctionFacts
- [ ] **P1.4.5** Store all ClassFacts
- [ ] **P1.4.6** Store all ImportFacts
- [ ] **P1.4.7** Update session record on completion

### P1.5 - Test Phase 1
**File:** `tests/persistence/test_facts.py` (NEW)

- [ ] **P1.5.1** Test FileFact creation and storage
- [ ] **P1.5.2** Test FunctionFact with call_targets preserved
- [ ] **P1.5.3** Test ClassFact with bases preserved
- [ ] **P1.5.4** Test ImportFact with resolution preserved
- [ ] **P1.5.5** Test session tracking
- [ ] **P1.5.6** Verify: query call_targets from DB
- [ ] **P1.5.7** Verify: query bases from DB

---

## Phase 2: Fix Graph Building

### P2.1 - Create Multi-Type Graph Model
**File:** `src/shannon_insight/graph/models.py`

- [ ] **P2.1.1** Create `NodeType` enum (FILE, FUNCTION, CLASS)
- [ ] **P2.1.2** Create `EdgeType` enum (IMPORTS, CALLS, INHERITS, CONTAINS)
- [ ] **P2.1.3** Create `CodeGraph` dataclass with typed edges
- [ ] **P2.1.4** Add reverse index builders
- [ ] **P2.1.5** Keep `DependencyGraph` for backward compat (deprecated)

### P2.2 - Build Graph From Facts (not FileSyntax)
**File:** `src/shannon_insight/graph/builder.py`

- [ ] **P2.2.1** Create `build_code_graph(facts_db: FactDatabase) -> CodeGraph`
- [ ] **P2.2.2** Build FILE nodes from file_facts
- [ ] **P2.2.3** Build FUNCTION nodes from function_facts
- [ ] **P2.2.4** Build CLASS nodes from class_facts
- [ ] **P2.2.5** Build IMPORTS edges from import_facts.resolved_path
- [ ] **P2.2.6** Build CALLS edges from function_facts.call_targets
- [ ] **P2.2.7** Build INHERITS edges from class_facts.bases
- [ ] **P2.2.8** Build CONTAINS edges (file → functions, file → classes)
- [ ] **P2.2.9** Resolve call_targets to qualified function names

### P2.3 - Enhance Graph Algorithms
**File:** `src/shannon_insight/graph/algorithms.py`

- [ ] **P2.3.1** PageRank on function call graph (not just files)
- [ ] **P2.3.2** Betweenness on function call graph
- [ ] **P2.3.3** Detect dead functions (no incoming CALLS edges)
- [ ] **P2.3.4** Detect inheritance depth
- [ ] **P2.3.5** Detect diamond inheritance
- [ ] **P2.3.6** Detect circular calls (function-level cycles)

### P2.4 - Update GraphAnalysis Model
**File:** `src/shannon_insight/graph/models.py`

- [ ] **P2.4.1** Add `function_pagerank: dict[str, float]`
- [ ] **P2.4.2** Add `dead_functions: set[str]`
- [ ] **P2.4.3** Add `inheritance_depth: dict[str, int]`
- [ ] **P2.4.4** Add `function_cycles: list[set[str]]`
- [ ] **P2.4.5** Add `hotspot_functions: list[str]` (high centrality + high churn)

### P2.5 - Test Phase 2
**File:** `tests/graph/test_code_graph.py` (NEW)

- [ ] **P2.5.1** Test CALLS edges from call_targets
- [ ] **P2.5.2** Test INHERITS edges from bases
- [ ] **P2.5.3** Test function PageRank
- [ ] **P2.5.4** Test dead function detection
- [ ] **P2.5.5** Test inheritance depth calculation
- [ ] **P2.5.6** Verify: function-level cycles detected

---

## Verification Checklist

After completing Phase 1 + 2:

### Data Preserved
- [ ] `call_targets` stored in DB and queryable
- [ ] `bases` stored in DB and queryable
- [ ] `names` (import symbols) stored in DB
- [ ] `resolved_path` stored (no re-computation)
- [ ] Session metadata tracked

### Graph Complete
- [ ] FILE → FILE edges (imports) ✓ (already works)
- [ ] FUNCTION → FUNCTION edges (calls) ← NEW
- [ ] CLASS → CLASS edges (inheritance) ← NEW
- [ ] FILE → FUNCTION edges (contains) ← NEW
- [ ] FILE → CLASS edges (contains) ← NEW

### Signals Enabled
After this work, we can compute:
- [ ] Function-level PageRank (hotspot functions, not just files)
- [ ] Dead function detection
- [ ] Inheritance depth per class
- [ ] Diamond inheritance detection
- [ ] Method coupling (which methods call which)
- [ ] Decorator patterns

---

## Dependencies

```
P1.1 (FileSyntax) → P1.3 (Fact Models) → P1.2 (Fact DB) → P1.4 (Store)
                                                              ↓
P2.1 (Graph Model) → P2.2 (Build from Facts) → P2.3 (Algorithms)
```

## Estimated Effort

| Phase | Tasks | Est. Hours |
|-------|-------|------------|
| P1.1 | 6 | 2h |
| P1.2 | 7 | 4h |
| P1.3 | 5 | 2h |
| P1.4 | 7 | 3h |
| P1.5 | 7 | 3h |
| P2.1 | 5 | 2h |
| P2.2 | 9 | 6h |
| P2.3 | 6 | 4h |
| P2.4 | 5 | 2h |
| P2.5 | 6 | 3h |
| **Total** | **63** | **31h** |

---

## Migration Notes

1. **Backward Compatibility**: Keep `DependencyGraph` working, mark deprecated
2. **Database Location**: `.shannon/facts.db` (separate from `history.db`)
3. **Incremental**: Facts DB can be built incrementally (only re-parse changed files)
4. **Content Hash**: Use content_hash to skip re-parsing unchanged files
