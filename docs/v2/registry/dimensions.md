# Registry: Dimensions

The eight irreducible dimensions of code. None can be derived from the others. Every signal in `signals.md` belongs to exactly one dimension. Every finding in `finders.md` is a condition on signals from one or more dimensions.

## D1: SIZE — "How much?"

Positive integers at every scale. Lines, tokens, parameters, functions, files, modules.

**Mathematical object**: Counting, distributions (Gini), growth models.

**Active at scales**: S0 (chars), S1 (tokens), S2 (params, body_tokens), S3 (methods, fields), S4 (functions, LOC, classes), S5 (file count, total LOC), S6 (module count, total files).

**Computed by IRs**: IR0 (byte size), IR1 (function/class counts, token counts).

**Key insight**: Size underpins almost every derived metric. Complexity without size is just shape. Risk without size has no blast radius.

---

## D2: SHAPE — "What structure?"

How code is organized internally. Depth, branching, distribution of sizes, symmetry.

**Mathematical object**: Trees (AST, class hierarchy), distributions of structural properties (Gini, entropy).

**Active at scales**: S2 (nesting, cyclomatic complexity, branches), S3 (inheritance depth, method distribution), S4 (function-size Gini, class hierarchy), S5 (internal dependency structure, layer depth), S6 (architectural pattern: layered, hub-spoke, flat, monolith).

**Computed by IRs**: IR1 (per-function nesting, cyclomatic approx), IR4 (module-level patterns).

**Key insight**: Shape captures geometry independent of content. Same SIZE, different SHAPE = different comprehension cost.

---

## D3: NAMING — "What concepts?"

Semantic content carried by identifiers. What code is *about*, as revealed by programmer word choice.

**Mathematical object**: Token vectors in TF-IDF space, cosine similarity, Louvain clustering on co-occurrence graphs.

**Active at scales**: S0 (keyword/identifier/literal distinction), S2 (function name, parameter names), S3 (class name, method names), S4 (filename, concept vocabulary), S5 (directory name, shared vocabulary), S6 (global conventions).

**Computed by IRs**: IR2 (role classification, concept extraction, naming drift).

**Key insight**: Only dimension capturing human intent at the token level. Identifiers are compressed natural language embedded in code.

---

## D4: REFERENCE — "What points to what?"

Every relationship where one entity depends on, uses, calls, inherits from, or refers to another.

**Mathematical object**: Directed multi-graphs G = (V, E, w, τ). Centrality (eigenvector, betweenness), spectral decomposition, reachability.

**Sub-types** (each a distinct graph):
- IMPORT: file A imports file B
- CALL: function in A calls function in B
- TYPE_FLOW: A uses a type defined in B
- INHERITANCE: class in A extends class in B

**Active at scales**: S2 (calls, reads, writes), S3 (bases, composed types), S4 (imports, exports), S5 (inter-module edges, cohesion, coupling), S6 (external dependency graph).

**Computed by IRs**: IR1 (import declarations), IR3 (resolved graph + all algorithms), IR4 (module-level contraction).

**Key insight**: Creates structure *between* entities (vs D2 which is structure *within*). Makes a codebase a graph, not a bag of files.

---

## D5: INFORMATION — "How dense? How ordered?"

Information-theoretic properties. Novelty, redundancy, compressibility.

**Mathematical object**: Shannon entropy H, Kolmogorov complexity approximation (compression ratio), Normalized Compression Distance (NCD), mutual information.

**Active at scales**: S0 (byte-level surprise/context), S2 (function body entropy, compression), S3 (method entropy distribution), S4 (file compression ratio, token entropy, semantic coherence), S5 (internal redundancy via mean NCD), S6 (global information density, modularity).

**Computed by IRs**: IR1 (token counts for entropy), IR3 (compression ratio, NCD pairs, coherence).

**Key insight**: Language-agnostic. Compression ratio doesn't care about syntax. Measures pure information content independent of expression. Shannon Insight is named after this dimension.

---

## D6: CHANGE — "How does it evolve?"

Temporal behavior of any entity. Frequency, direction, rate, acceleration.

**Mathematical object**: Time series, linear regression (slope), coefficient of variation (CV), trajectory classification.

**Active at scales**: S2 (function edit count, last modified), S4 (file churn trajectory, velocity), S5 (module velocity, growth rate), S6 (codebase growth rate, commit frequency).

**Computed by IRs**: IR5t (git log parsing, churn analysis, trajectory classification).

**Key insight**: Orthogonal to all spatial dimensions. A file can be any size, any shape, any information density, and independently change at any rate. Turns a snapshot into a movie.

---

## D7: AUTHORSHIP — "Who touches it?"

Human/social properties. Who creates, modifies, reviews, and owns code.

**Mathematical object**: Discrete distributions, Shannon entropy of author contributions, Gini coefficient, Jaccard overlap.

**Active at scales**: S4 (file bus factor, author entropy, ownership concentration), S5 (team size, knowledge Gini, coordination cost), S6 (org contributor count, turnover rate).

**Computed by IRs**: IR5t (git author extraction, entropy computation).

**Key insight**: Irreducible because no amount of static or temporal analysis reveals that only one person understands a critical system. Requires a separate data source (git authors).

---

## D8: INTENT — "Why was it changed?"

Purpose behind changes. Feature, bug fix, refactoring, test, docs, dependency update.

**Mathematical object**: Commit classification (keyword + diff shape), proportional analysis, intent entropy.

**Active at scales**: S4 (file fix_ratio, refactor_ratio), S5 (module purpose mix, refactor-to-fix ratio), S6 (project phase classification).

**Computed by IRs**: IR5t (commit message mining, diff shape analysis).

**Key insight**: Irreducible because the same SIZE change with the same SHAPE can be a feature or a bug fix, with completely different implications.

---

## Dimension × Scale Applicability Matrix

`-` = not meaningfully measurable at this scale.

```
              S0:Token  S1:Stmt  S2:Func  S3:Class  S4:File  S5:Module  S6:Codebase
D1:SIZE         x         x        x        x         x         x          x
D2:SHAPE        -         -        x        x         x         x          x
D3:NAMING       x         -        x        x         x         x          x
D4:REFERENCE    -         -        x        x         x         x          x
D5:INFORMATION  x         -        x        x         x         x          x
D6:CHANGE       -         -        x        -         x         x          x
D7:AUTHORSHIP   -         -        -        -         x         x          x
D8:INTENT       -         -        -        -         x         x          x

Active cells: ~40
```

Each active cell is one or more signals defined in `signals.md`. Each signal belongs to exactly one cell.
