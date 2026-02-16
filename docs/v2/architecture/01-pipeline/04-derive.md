# Stage 4: Derive

Compute derived signals from raw measurements. Derivers are topo-sorted by requires/provides.

---

## Deriver Protocol

```python
class SignalDeriver(Protocol):
    name: str
    requires: set[Signal | RelationType]
    provides: set[Signal]

    def derive(self, store: FactStore) -> None:
        """
        Compute derived signals and add to store.
        May skip if required signals unavailable.
        """
        ...
```

---

## Derivers (Execution Order)

Derivers are topologically sorted by their `requires` → `provides` dependencies.

| Order | Deriver | Requires | Provides |
|-------|---------|----------|----------|
| 1 | GraphMetricsDeriver | IMPORTS | pagerank, betweenness, in_degree, out_degree, blast_radius_size |
| 2 | OrphanDeriver | in_degree, role | is_orphan, depth |
| 3 | CloneDeriver | file content | CLONED_FROM relations |
| 4 | AuthorDistanceDeriver | AUTHORED_BY | G5 author distance |
| 5 | ModuleDeriver | IMPORTS, IN_MODULE | cohesion, coupling, instability, abstractness, main_seq_distance |
| 6 | LayerDeriver | DEPENDS_ON, instability | layer assignments, layer_violation_count |
| 7 | GlobalMetricsDeriver | various | modularity, centrality_gini, orphan_ratio, etc. |
| 8 | PercentileDeriver | all raw signals | *_pctl versions |
| 9 | CompositeDeriver | percentiles | risk_score, health_score, wiring_quality, etc. |
| 10 | LaplacianDeriver | composites, IMPORTS | raw_risk, delta_h |

---

## 1. GraphMetricsDeriver

### PageRank

```python
def compute_pagerank(
    edges: dict[str, set[str]],
    damping: float = 0.85,
    max_iterations: int = 50,
    tolerance: float = 1e-6,
) -> dict[str, float]:
    """
    Signal #14: pagerank

    PR(v) = (1-d)/N + d × Σ PR(u)/out_degree(u) for u→v
    """
    nodes = set(edges.keys()) | {t for targets in edges.values() for t in targets}
    N = len(nodes)
    if N == 0:
        return {}

    # Initialize
    pr = {n: 1.0 / N for n in nodes}
    out_degree = {n: len(edges.get(n, set())) for n in nodes}

    for _ in range(max_iterations):
        new_pr = {}
        for node in nodes:
            incoming = [src for src, targets in edges.items() if node in targets]
            rank = (1 - damping) / N
            for src in incoming:
                if out_degree[src] > 0:
                    rank += damping * pr[src] / out_degree[src]
            new_pr[node] = rank

        # Check convergence
        diff = max(abs(new_pr[n] - pr[n]) for n in nodes)
        pr = new_pr
        if diff < tolerance:
            break

    return pr
```

### Betweenness (Brandes' Algorithm)

```python
def compute_betweenness(edges: dict[str, set[str]]) -> dict[str, float]:
    """
    Signal #15: betweenness

    B(v) = Σ_{s≠v≠t} σ(s,t|v) / σ(s,t)
    """
    # Brandes' algorithm O(|V| × |E|)
    nodes = set(edges.keys()) | {t for targets in edges.values() for t in targets}
    betweenness = {n: 0.0 for n in nodes}

    for s in nodes:
        # BFS from s
        S = []  # Stack
        P = {n: [] for n in nodes}  # Predecessors
        sigma = {n: 0 for n in nodes}
        sigma[s] = 1
        d = {n: -1 for n in nodes}
        d[s] = 0
        Q = [s]  # Queue

        while Q:
            v = Q.pop(0)
            S.append(v)
            for w in edges.get(v, set()):
                if d[w] < 0:
                    Q.append(w)
                    d[w] = d[v] + 1
                if d[w] == d[v] + 1:
                    sigma[w] += sigma[v]
                    P[w].append(v)

        # Accumulation
        delta = {n: 0.0 for n in nodes}
        while S:
            w = S.pop()
            for v in P[w]:
                delta[v] += (sigma[v] / sigma[w]) * (1 + delta[w])
            if w != s:
                betweenness[w] += delta[w]

    # Normalize
    n = len(nodes)
    if n > 2:
        norm = 2.0 / ((n - 1) * (n - 2))
        betweenness = {k: v * norm for k, v in betweenness.items()}

    return betweenness
```

### Blast Radius

```python
def compute_blast_radius(
    path: str,
    reverse_edges: dict[str, set[str]],
) -> int:
    """
    Signal #18: blast_radius_size

    BFS on reverse graph, count reachable nodes.
    """
    visited = {path}
    queue = [path]

    while queue:
        current = queue.pop(0)
        for dependent in reverse_edges.get(current, set()):
            if dependent not in visited:
                visited.add(dependent)
                queue.append(dependent)

    return len(visited) - 1  # Exclude self
```

---

## 2. OrphanDeriver

```python
def derive_orphan_signals(store: FactStore) -> None:
    """
    Signal #19: depth (shortest path from entry point)
    Signal #20: is_orphan (in_degree=0 AND not entry point)
    """
    # Find entry points
    entry_points = set()
    for entity in store.files():
        role = store.signals.get(entity, Signal.ROLE)
        if role in (Role.ENTRY_POINT, Role.TEST):
            entry_points.add(entity.key)

    # BFS from entry points to compute depth
    depth = {ep: 0 for ep in entry_points}
    queue = list(entry_points)

    while queue:
        current = queue.pop(0)
        current_depth = depth[current]
        # Find files that import current (outgoing edges from current)
        for rel in store.relations.outgoing(
            EntityId(EntityType.FILE, current),
            RelationType.IMPORTS
        ):
            target = rel.target.key
            if target not in depth:
                depth[target] = current_depth + 1
                queue.append(target)

    # Set signals
    for entity in store.files():
        path = entity.key

        # depth
        if path in depth:
            store.signals.set(entity, Signal.DEPTH, depth[path])
        else:
            store.signals.set(entity, Signal.DEPTH, -1)  # Unreachable

        # is_orphan
        in_degree = store.signals.get(entity, Signal.IN_DEGREE, 0)
        role = store.signals.get(entity, Signal.ROLE, Role.UNKNOWN)
        is_orphan = in_degree == 0 and role not in (Role.ENTRY_POINT, Role.TEST)
        store.signals.set(entity, Signal.IS_ORPHAN, is_orphan)
```

---

## 3. ModuleDeriver

### Martin Metrics

```python
def derive_module_signals(store: FactStore) -> None:
    """
    Signals #37-44: Module-level metrics.
    """
    for module in store.modules():
        files = [r.target for r in store.relations.incoming(module, RelationType.IN_MODULE)]

        if not files:
            continue

        # #37 cohesion: internal_edges / (n × (n-1))
        internal_edges = 0
        for f in files:
            for rel in store.relations.outgoing(f, RelationType.IMPORTS):
                if rel.target in files:
                    internal_edges += 1

        n = len(files)
        cohesion = internal_edges / (n * (n - 1)) if n > 1 else 0.0
        store.signals.set(module, Signal.COHESION, cohesion)

        # #38 coupling: external_edges / (internal + external)
        external_edges = 0
        for f in files:
            for rel in store.relations.outgoing(f, RelationType.IMPORTS):
                if rel.target not in files:
                    external_edges += 1

        total = internal_edges + external_edges
        coupling = external_edges / total if total > 0 else 0.0
        store.signals.set(module, Signal.COUPLING, coupling)

        # #39 instability: Ce / (Ca + Ce)
        # Ca = afferent (incoming from other modules)
        # Ce = efferent (outgoing to other modules)
        Ca = sum(1 for f in files for r in store.relations.incoming(f, RelationType.IMPORTS)
                 if r.source not in files)
        Ce = external_edges

        if Ca + Ce > 0:
            instability = Ce / (Ca + Ce)
            store.signals.set(module, Signal.INSTABILITY, instability)
        else:
            store.signals.set(module, Signal.INSTABILITY, None)  # Isolated module

        # #40 abstractness: abstract_symbols / total_symbols
        abstract_count = 0
        total_symbols = 0
        for f in files:
            syntax = store.get_syntax(f.key)
            if syntax:
                for cls in syntax.classes:
                    total_symbols += 1
                    if cls.is_abstract:
                        abstract_count += 1

        abstractness = abstract_count / total_symbols if total_symbols > 0 else 0.0
        store.signals.set(module, Signal.ABSTRACTNESS, abstractness)

        # #41 main_seq_distance: |A + I - 1|
        instability_val = store.signals.get(module, Signal.INSTABILITY)
        if instability_val is not None:
            D = abs(abstractness + instability_val - 1)
            store.signals.set(module, Signal.MAIN_SEQ_DISTANCE, D)
        # else: skip (instability=None for isolated modules)

        # #42 boundary_alignment (requires Louvain communities)
        # ... (see ArchitectureAnalyzer)

        # #44 role_consistency
        roles = [store.signals.get(f, Signal.ROLE, Role.UNKNOWN) for f in files]
        role_counts = Counter(roles)
        most_common_count = role_counts.most_common(1)[0][1] if role_counts else 0
        role_consistency = most_common_count / len(files) if files else 0.0
        store.signals.set(module, Signal.ROLE_CONSISTENCY, role_consistency)

        # #50 file_count
        store.signals.set(module, Signal.FILE_COUNT, len(files))
```

---

## 4. PercentileDeriver

```python
def derive_percentiles(store: FactStore) -> None:
    """
    For each percentileable signal, compute percentile for each file.

    pctl(signal, f) = |{v : signal(v) ≤ signal(f)}| / |all_files|
    """
    if store.tier == Tier.ABSOLUTE:
        return  # No percentiles for tiny codebases

    files = list(store.files())

    for signal in PERCENTILEABLE_SIGNALS:
        # Gather values
        values = []
        for f in files:
            val = store.signals.get(f, signal)
            if val is not None:
                values.append((f, val))

        if not values:
            continue

        # Sort by value
        values.sort(key=lambda x: x[1])
        n = len(values)

        # Compute percentiles
        for i, (entity, val) in enumerate(values):
            # Count of values ≤ this value
            count_le = i + 1  # Since sorted, position gives count
            pctl = count_le / n
            store.signals.set(entity, f"{signal.value}_pctl", pctl)
```

---

## 5. CompositeDeriver

```python
def derive_composites(store: FactStore) -> None:
    """
    Signals #35-36, #51, #60-62: Composite scores.
    Must run AFTER PercentileDeriver.
    """
    if store.tier == Tier.ABSOLUTE:
        return  # No composites for tiny codebases

    # Per-file composites
    for f in store.files():
        # #35 risk_score
        risk = derive_risk_score(store, f)
        store.signals.set(f, Signal.RISK_SCORE, risk)

        # #36 wiring_quality
        wiring = derive_wiring_quality(store, f)
        store.signals.set(f, Signal.WIRING_QUALITY, wiring)

    # Per-module composites
    for m in store.modules():
        # #51 health_score
        health = derive_health_score(store, m)
        store.signals.set(m, Signal.HEALTH_SCORE, health)

    # Global composites
    codebase = store.codebase()

    # #60 wiring_score
    wiring_score = derive_wiring_score(store)
    store.signals.set(codebase, Signal.WIRING_SCORE, wiring_score)

    # #61 architecture_health
    arch_health = derive_architecture_health(store)
    store.signals.set(codebase, Signal.ARCHITECTURE_HEALTH, arch_health)

    # #62 codebase_health
    codebase_health = derive_codebase_health(store)
    store.signals.set(codebase, Signal.CODEBASE_HEALTH, codebase_health)
```

See [07-composites/README.md](../07-composites/README.md) for exact formulas.

---

## 6. LaplacianDeriver

```python
def derive_laplacian_signals(store: FactStore) -> None:
    """
    Compute health Laplacian: Δh(f) = raw_risk(f) - mean(raw_risk(neighbors))

    raw_risk uses absolute values (not percentiles) to preserve variation.
    """
    files = list(store.files())

    # Step 1: Compute raw_risk for each file
    raw_risks = {}
    max_pagerank = max(store.signals.get(f, Signal.PAGERANK, 0) for f in files) or 1
    max_blast = max(store.signals.get(f, Signal.BLAST_RADIUS_SIZE, 0) for f in files) or 1
    max_cognitive = max(store.signals.get(f, Signal.COGNITIVE_LOAD, 0) for f in files) or 1
    max_bus = max(store.signals.get(f, Signal.BUS_FACTOR, 1) for f in files)

    for f in files:
        pr = store.signals.get(f, Signal.PAGERANK, 0)
        blast = store.signals.get(f, Signal.BLAST_RADIUS_SIZE, 0)
        cognitive = store.signals.get(f, Signal.COGNITIVE_LOAD, 0)
        trajectory = store.signals.get(f, Signal.CHURN_TRAJECTORY, Trajectory.STABLE)
        bus = store.signals.get(f, Signal.BUS_FACTOR, 1)

        instability_factor = 1.0 if trajectory in (Trajectory.CHURNING, Trajectory.SPIKING) else 0.3

        raw_risk = (
            0.25 * (pr / max_pagerank if max_pagerank > 0 else 0) +
            0.20 * (blast / max_blast if max_blast > 0 else 0) +
            0.20 * (cognitive / max_cognitive if max_cognitive > 0 else 0) +
            0.20 * instability_factor +
            0.15 * (1 - bus / max_bus if max_bus > 0 else 0)
        )
        raw_risks[f.key] = raw_risk
        store.signals.set(f, Signal.RAW_RISK, raw_risk)

    # Step 2: Compute Δh (Laplacian)
    for f in files:
        # Neighbors = files that import f OR that f imports
        neighbors = set()
        for rel in store.relations.outgoing(f, RelationType.IMPORTS):
            neighbors.add(rel.target.key)
        for rel in store.relations.incoming(f, RelationType.IMPORTS):
            neighbors.add(rel.source.key)

        if not neighbors:
            # Orphan: no neighborhood comparison
            store.signals.set(f, Signal.DELTA_H, 0.0)
        else:
            neighbor_risks = [raw_risks.get(n, 0) for n in neighbors]
            mean_neighbor_risk = sum(neighbor_risks) / len(neighbor_risks)
            delta_h = raw_risks[f.key] - mean_neighbor_risk
            store.signals.set(f, Signal.DELTA_H, delta_h)
```

---

## Execution

```python
def run_derivers(store: FactStore) -> None:
    """
    Run all derivers in topologically sorted order.
    """
    derivers = [
        GraphMetricsDeriver(),
        OrphanDeriver(),
        CloneDeriver(),
        AuthorDistanceDeriver(),
        ModuleDeriver(),
        LayerDeriver(),
        GlobalMetricsDeriver(),
        PercentileDeriver(),
        CompositeDeriver(),
        LaplacianDeriver(),
    ]

    # Topo-sort by requires/provides
    sorted_derivers = topological_sort(derivers)

    for deriver in sorted_derivers:
        # Check if requirements are met
        if all(store.has_signal(s) for s in deriver.requires if isinstance(s, Signal)):
            deriver.derive(store)
        else:
            logger.info(f"Skipping {deriver.name}: missing requirements")
```
