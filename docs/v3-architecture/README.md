# v3 Architecture Documentation

This folder contains the complete architectural specification for Shannon Insight v3.

## Philosophy

v3 is built on an **ontologically correct fact-based architecture**:

1. **Everything is a fact** - immutable, timestamped observations
2. **Content-addressable storage** - files identified by hash, not path
3. **Stable identity** - files survive renames, authors survive email changes
4. **Layered computation** - each level depends only on levels below

## Document Structure

| File | Level | Description |
|------|-------|-------------|
| `00-CODEBASE-AUDIT.md` | - | Current implementation analysis |
| `01-FACT-EXTRACTION.md` | 0 | Primitive facts, identity, blobs |
| `02-TEMPORAL-SIGNALS.md` | 1 | Churn, authorship, co-change |
| `03-GRAPH-CONSTRUCTION.md` | 2 | Relationship graphs |
| `04-GRAPH-ALGORITHMS.md` | 3 | PageRank, Louvain, spectral |
| `05-CROSS-LAYER-TRAJECTORY.md` | 4 | MI between graphs, time derivatives |
| `06-COMPOSITES.md` | 5 | Risk, health, quality scores |
| `07-FINDERS.md` | 6 | Pattern detection |

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│ Level 6: FINDERS                                                    │
│   Pattern matching → Findings                                       │
└─────────────────────────────────────────────────────────────────────┘
                              ▲
┌─────────────────────────────────────────────────────────────────────┐
│ Level 5: COMPOSITES                                                 │
│   raw_risk → risk_score → health_score → delta_h                    │
└─────────────────────────────────────────────────────────────────────┘
                              ▲
┌─────────────────────────────────────────────────────────────────────┐
│ Level 4: CROSS-LAYER + TRAJECTORY                                   │
│   I(G₁; G₂), neighborhood overlap, d(signal)/dt                     │
└─────────────────────────────────────────────────────────────────────┘
                              ▲
┌─────────────────────────────────────────────────────────────────────┐
│ Level 3: GRAPH ALGORITHMS                                           │
│   PageRank, Louvain, Fiedler, betweenness, SCC                      │
└─────────────────────────────────────────────────────────────────────┘
                              ▲
┌─────────────────────────────────────────────────────────────────────┐
│ Level 2: GRAPH CONSTRUCTION                                         │
│   G_import, G_cochange, G_author, G_semantic, G_clone               │
└─────────────────────────────────────────────────────────────────────┘
                              ▲
┌─────────────────────────────────────────────────────────────────────┐
│ Level 1: TEMPORAL SIGNALS                                           │
│   churn_cv, bus_factor, lift, author_jaccard                        │
└─────────────────────────────────────────────────────────────────────┘
                              ▲
┌─────────────────────────────────────────────────────────────────────┐
│ Level 0: FACT EXTRACTION                                            │
│   BlobStore, FileIdentity, CommitFact, ParsedSyntax                 │
└─────────────────────────────────────────────────────────────────────┘
                              ▲
┌─────────────────────────────────────────────────────────────────────┐
│ RAW INPUTS                                                          │
│   Files on disk + Git repository                                    │
└─────────────────────────────────────────────────────────────────────┘
```

## Key Innovations

### 1. Stable File Identity
Files are identified by UUID, not path. Renames are tracked as events.
```python
file_id = "550e8400-e29b-41d4-a716-446655440000"  # survives rename
```

### 2. Content-Addressable Caching
Parse results cached by content hash. Unchanged files skip re-parsing.
```python
if hash in syntax_cache:
    return syntax_cache[hash]  # instant
```

### 3. Multi-Layer Graph Algebra
Graphs combined via set operations and weighted sums:
```
HIDDEN_COUPLING = G_cochange \ G_import
A_combined = 0.4×A_import + 0.3×A_cochange + 0.2×A_author + 0.1×A_semantic
```

### 4. Graph Mutual Information
Quantifies alignment between relationship types:
```
I(G_import; G_cochange) = H(G₁) + H(G₂) - H(G₁,G₂)
```

### 5. Health Laplacian
Measures file risk relative to neighbors:
```
Δh(v) = raw_risk(v) - mean(raw_risk(neighbors))
```

## Migration Path

1. **Phase 1**: Add identity layer alongside existing code
2. **Phase 2**: Unified FactStore replacing separate DBs
3. **Phase 3**: Content-addressable parsing
4. **Phase 4**: Author normalization
5. **Phase 5**: Full signal computation refactor

## Related Documentation

- `docs/v2/` - Previous v2 specifications
- `docs/v2/phases/` - Implementation phases
- `docs/v2/registry/` - Signal registry
