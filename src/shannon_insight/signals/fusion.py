"""FusionPipeline — typestate pattern for signal fusion ordering.

The typestate pattern enforces the correct 6-step ordering:
    1. collect: Gather raw signals from all store slots
    2. raw_risk: Compute raw_risk per file (pre-percentile)
    3. normalize: Compute percentiles (ABSOLUTE tier skips this)
    4. module_temporal: Fill module temporal signals
    5. composites: Compute all composite scores
    6. laplacian: Health Laplacian (uses raw_risk, not composites)

Each step returns the next stage type. You literally cannot call
step5_composites() on a _Collected object — the method doesn't exist.
Mypy catches reordering at type-check time.

Example usage:
    field = build(store)  # Chains all 6 steps
    # or manually:
    field = (FusionPipeline(store)
        .step1_collect()
        .step2_raw_risk()
        .step3_normalize()
        .step4_module_temporal()
        .step5_composites()
        .step6_laplacian())
"""

from __future__ import annotations

from collections import Counter
from typing import TYPE_CHECKING

from shannon_insight.signals.composites import compute_composites
from shannon_insight.signals.health_laplacian import compute_all_raw_risks, compute_health_laplacian
from shannon_insight.signals.models import FileSignals, ModuleSignals, SignalField
from shannon_insight.signals.normalization import normalize

if TYPE_CHECKING:
    from shannon_insight.insights.store_v2 import AnalysisStore


def _gini(values: list[float]) -> float:
    """Compute Gini coefficient.

    G = (2 * sum(i * x_i)) / (n * sum(x_i)) - (n + 1) / n

    Values must be non-negative. Returns 0 for empty/all-zero values.
    """
    if not values or sum(values) == 0:
        return 0.0

    sorted_values = sorted(values)
    n = len(sorted_values)

    # i is 1-indexed in formula
    numerator = sum((i + 1) * v for i, v in enumerate(sorted_values))
    denominator = n * sum(sorted_values)

    return (2 * numerator / denominator) - (n + 1) / n


class FusionPipeline:
    """Entry point for signal fusion. Each step returns the next stage type."""

    def __init__(self, store: AnalysisStore) -> None:
        self.store = store
        self.field = SignalField()
        self._determine_tier()

    def _determine_tier(self) -> None:
        """Set tier based on file count."""
        n = len(self.store.file_metrics)
        if n < 15:
            self.field.tier = "ABSOLUTE"
        elif n < 50:
            self.field.tier = "BAYESIAN"
        else:
            self.field.tier = "FULL"

    def step1_collect(self) -> _Collected:
        """Gather raw signals from all store slots into SignalField.

        Reads from:
        - store.file_metrics (IR1 scanning)
        - store.structural (IR3 graph)
        - store.roles (IR2 role classification)
        - store.semantics (IR2 semantics)
        - store.churn (IR5t temporal)
        - store.architecture (IR4 modules)
        """
        # Per-file signals
        for fm in self.store.file_metrics:
            fs = FileSignals(path=fm.path)
            self._fill_from_scanning(fs, fm)
            self._fill_from_graph(fs)
            self._fill_from_semantics(fs)
            self._fill_from_temporal(fs)
            self.field.per_file[fm.path] = fs

        # Per-module signals
        self._collect_modules()

        # Global signals
        self._collect_global()

        return _Collected(self.field, self.store)

    def _fill_from_scanning(self, fs: FileSignals, fm) -> None:
        """Fill IR1 scanning signals from FileMetrics."""
        fs.lines = fm.lines
        fs.function_count = fm.functions
        fs.class_count = fm.structs  # structs in FileMetrics
        fs.max_nesting = fm.nesting_depth
        fs.import_count = len(fm.imports) if fm.imports else 0

        # impl_gini from function_sizes
        if fm.function_sizes:
            fs.impl_gini = _gini([float(s) for s in fm.function_sizes])

        # stub_ratio needs function body analysis (placeholder)
        # Will be filled from file_syntax if available
        if self.store.file_syntax.available:
            syntax = self.store.file_syntax.value.get(fm.path)
            if syntax and hasattr(syntax, "stub_ratio"):
                fs.stub_ratio = syntax.stub_ratio

    def _fill_from_graph(self, fs: FileSignals) -> None:
        """Fill IR3 graph signals from structural analysis."""
        if not self.store.structural.available:
            return

        structural = self.store.structural.value
        path = fs.path

        # Get FileAnalysis if available
        fa = structural.files.get(path)
        if fa:
            fs.pagerank = fa.pagerank
            fs.betweenness = fa.betweenness
            fs.in_degree = fa.in_degree
            fs.out_degree = fa.out_degree
            fs.blast_radius_size = fa.blast_radius_size
            fs.depth = fa.depth
            fs.is_orphan = fa.is_orphan
            fs.phantom_import_count = fa.phantom_import_count
            fs.community = fa.community_id
            fs.compression_ratio = fa.compression_ratio
            fs.cognitive_load = fa.cognitive_load

        # Semantic coherence from graph-based calculation
        # (import-based, not function-level TF-IDF)
        if hasattr(structural, "graph_analysis"):
            ga = structural.graph_analysis
            # Semantic coherence approximated from community structure
            # Files in same community have higher coherence
            if path in ga.node_community:
                comm_id = ga.node_community[path]
                comm = next((c for c in ga.communities if c.id == comm_id), None)
                if comm and len(comm.members) > 1:
                    # Coherence = how central this file is within its community
                    fs.semantic_coherence = min(1.0, fa.pagerank * 10) if fa else 0.0

    def _fill_from_semantics(self, fs: FileSignals) -> None:
        """Fill IR2 semantic signals from semantics slot."""
        if self.store.roles.available:
            role = self.store.roles.value.get(fs.path)
            if role:
                fs.role = role

        if not self.store.semantics.available:
            return

        sem = self.store.semantics.value.get(fs.path)
        if not sem:
            return

        fs.concept_count = sem.concept_count
        fs.concept_entropy = sem.concept_entropy
        fs.naming_drift = sem.naming_drift
        fs.todo_density = sem.todo_density

        if sem.docstring_coverage is not None:
            fs.docstring_coverage = sem.docstring_coverage

        # Role from semantics if not already set from roles slot
        if fs.role == "UNKNOWN" and hasattr(sem, "role"):
            fs.role = sem.role.value if hasattr(sem.role, "value") else str(sem.role)

    def _fill_from_temporal(self, fs: FileSignals) -> None:
        """Fill IR5t temporal signals from churn slot."""
        if not self.store.churn.available:
            return

        churn = self.store.churn.value.get(fs.path)
        if not churn:
            return

        fs.total_changes = churn.total_changes
        fs.churn_trajectory = churn.trajectory.upper() if churn.trajectory else "DORMANT"
        fs.churn_slope = churn.slope
        fs.churn_cv = churn.cv
        fs.bus_factor = churn.bus_factor
        fs.author_entropy = churn.author_entropy
        fs.fix_ratio = churn.fix_ratio
        fs.refactor_ratio = churn.refactor_ratio

    def _collect_modules(self) -> None:
        """Collect per-module signals from architecture."""
        if not self.store.architecture.available:
            return

        arch = self.store.architecture.value
        for path, mod in arch.modules.items():
            ms = ModuleSignals(path=path)

            # Martin metrics
            ms.cohesion = mod.cohesion
            ms.coupling = mod.coupling
            ms.instability = mod.instability  # Can be None
            ms.abstractness = mod.abstractness
            ms.main_seq_distance = mod.main_seq_distance

            # Boundary analysis
            ms.boundary_alignment = mod.boundary_alignment
            ms.role_consistency = mod.role_consistency

            # File count
            ms.file_count = mod.file_count

            # Layer violation count (sum violations where this module is source)
            ms.layer_violation_count = sum(1 for v in arch.violations if v.source_module == path)

            # Mean cognitive load for files in this module
            cog_loads = []
            for fpath in mod.files:
                fs = self.field.per_file.get(fpath)
                if fs:
                    cog_loads.append(fs.cognitive_load)
            ms.mean_cognitive_load = sum(cog_loads) / len(cog_loads) if cog_loads else 0.0

            self.field.per_module[path] = ms

    def _collect_global(self) -> None:
        """Collect global signals from store."""
        g = self.field.global_signals

        if self.store.structural.available:
            structural = self.store.structural.value
            g.modularity = structural.modularity
            g.cycle_count = structural.cycle_count

            if hasattr(structural, "graph_analysis"):
                ga = structural.graph_analysis
                g.centrality_gini = ga.centrality_gini
                g.spectral_gap = ga.spectral_gap

        if self.store.spectral.available:
            spectral = self.store.spectral.value
            g.fiedler_value = spectral.fiedler_value
            if hasattr(spectral, "spectral_gap"):
                g.spectral_gap = spectral.spectral_gap

        # Compute orphan_ratio and phantom_ratio
        if self.field.per_file:
            orphan_count = sum(1 for fs in self.field.per_file.values() if fs.is_orphan)
            phantom_count = sum(
                1 for fs in self.field.per_file.values() if fs.phantom_import_count > 0
            )
            total = len(self.field.per_file)
            g.orphan_ratio = orphan_count / total
            g.phantom_ratio = phantom_count / total

        # Glue deficit placeholder (requires more complex analysis)
        g.glue_deficit = 0.0

        # Clone ratio from Phase 3 clone detection
        if self.store.clone_pairs.available:
            files_in_clones = set()
            for pair in self.store.clone_pairs.value:
                files_in_clones.add(pair.file_a)
                files_in_clones.add(pair.file_b)
            total_files = len(self.field.per_file)
            g.clone_ratio = len(files_in_clones) / total_files if total_files > 0 else 0.0

        # Violation rate from Phase 4 architecture
        if self.store.architecture.available:
            arch = self.store.architecture.value
            g.violation_rate = arch.violation_rate

        # Conway alignment from Phase 3 author distances
        if self.store.author_distances.available and self.store.architecture.available:
            author_dists = self.store.author_distances.value
            arch = self.store.architecture.value

            # Get structurally-coupled module pairs (modules with imports between them)
            module_graph = arch.module_graph if hasattr(arch, "module_graph") else {}

            if author_dists and module_graph:
                # Map files to modules
                file_to_module = {}
                for mod_path, mod in arch.modules.items():
                    for fpath in mod.files:
                        file_to_module[fpath] = mod_path

                # Find module pairs with structural coupling AND author distances
                module_pair_distances = []
                for ad in author_dists:
                    mod_a = file_to_module.get(ad.file_a)
                    mod_b = file_to_module.get(ad.file_b)
                    if mod_a and mod_b and mod_a != mod_b:
                        # Check if these modules have structural coupling
                        if mod_b in module_graph.get(mod_a, {}) or mod_a in module_graph.get(
                            mod_b, {}
                        ):
                            module_pair_distances.append(ad.distance)

                # Conway alignment = 1 - mean(author_distance)
                if module_pair_distances:
                    mean_distance = sum(module_pair_distances) / len(module_pair_distances)
                    g.conway_alignment = max(0.0, 1.0 - mean_distance)
                else:
                    # No structurally-coupled pairs with different teams
                    g.conway_alignment = 1.0
            else:
                # Solo project or no data
                g.conway_alignment = 1.0

        # Team size from Phase 3 git history
        if self.store.git_history.available:
            git_hist = self.store.git_history.value
            distinct_authors = {commit.author for commit in git_hist.commits}
            g.team_size = len(distinct_authors) if distinct_authors else 1


class _Collected:
    """State after step1_collect. Can only proceed to step2_raw_risk."""

    def __init__(self, field: SignalField, store: AnalysisStore) -> None:
        self.field = field
        self.store = store

    def step2_raw_risk(self) -> _RawRisked:
        """Compute raw_risk per file (pre-percentile). Used by health Laplacian.

        MUST be before percentiles (FM-3).
        """
        compute_all_raw_risks(self.field)
        return _RawRisked(self.field, self.store)


class _RawRisked:
    """State after step2_raw_risk. Can only proceed to step3_normalize."""

    def __init__(self, field: SignalField, store: AnalysisStore) -> None:
        self.field = field
        self.store = store

    def step3_normalize(self) -> _Normalized:
        """Compute percentiles. ABSOLUTE tier skips this."""
        normalize(self.field)
        return _Normalized(self.field, self.store)


class _Normalized:
    """State after step3_normalize. Can only proceed to step4_module_temporal."""

    def __init__(self, field: SignalField, store: AnalysisStore) -> None:
        self.field = field
        self.store = store

    def step4_module_temporal(self) -> _ModuleTemporal:
        """Fill module temporal signals. Safe to read percentiles now."""
        self._fill_module_temporal()
        return _ModuleTemporal(self.field, self.store)

    def _fill_module_temporal(self) -> None:
        """Aggregate temporal signals to module level.

        IMPORTANT: Runs AFTER normalization because module_bus_factor
        needs percentile(pagerank) > 0.75 to identify critical files.
        """
        if not self.store.git_history.available:
            return
        if not self.store.architecture.available:
            return

        git = self.store.git_history.value
        arch = self.store.architecture.value

        for path, ms in self.field.per_module.items():
            mod = arch.modules.get(path)
            if not mod:
                continue

            # velocity: commits per week touching module
            module_files = set(mod.files)
            module_commits = [c for c in git.commits if any(f in module_files for f in c.files)]

            weeks = max(git.span_days / 7, 1)
            ms.velocity = len(module_commits) / weeks

            # coordination_cost: mean distinct authors per commit
            if module_commits:
                costs = []
                for commit in module_commits:
                    # Count files from this module in the commit
                    commit_module_files = [f for f in commit.files if f in module_files]
                    if commit_module_files:
                        costs.append(1)  # Each commit = 1 author touching module
                ms.coordination_cost = len({c.author for c in module_commits}) / max(
                    len(module_commits), 1
                )

            # knowledge_gini: Gini of per-author commit counts
            author_counts = Counter(c.author for c in module_commits)
            if len(author_counts) > 1:
                ms.knowledge_gini = _gini(list(author_counts.values()))

            # module_bus_factor: min(bus_factor) across high-centrality files
            high_centrality = []
            for fpath in mod.files:
                fs = self.field.file(fpath)
                if fs and fs.percentiles.get("pagerank", 0) > 0.75:
                    high_centrality.append(fs)

            if high_centrality:
                ms.module_bus_factor = min(fs.bus_factor for fs in high_centrality)
            else:
                # No high-centrality files, use module average
                all_bf = []
                for f in mod.files:
                    file_signals = self.field.file(f)
                    if file_signals:
                        all_bf.append(file_signals.bus_factor)
                ms.module_bus_factor = sum(all_bf) / len(all_bf) if all_bf else 1.0


class _ModuleTemporal:
    """State after step4_module_temporal. Can only proceed to step5_composites."""

    def __init__(self, field: SignalField, store: AnalysisStore) -> None:
        self.field = field
        self.store = store

    def step5_composites(self) -> _Composited:
        """Compute all composite scores. Requires percentiles + module temporal."""
        compute_composites(self.field)
        return _Composited(self.field, self.store)


class _Composited:
    """State after step5_composites. Can only proceed to step6_laplacian."""

    def __init__(self, field: SignalField, store: AnalysisStore) -> None:
        self.field = field
        self.store = store

    def step6_laplacian(self) -> SignalField:
        """Health Laplacian. Uses raw_risk, not composites. Final step."""
        if self.store.structural.available:
            graph = self.store.structural.value.graph
            self.field.delta_h = compute_health_laplacian(self.field, graph)
        return self.field


def build(store: AnalysisStore) -> SignalField:
    """Convenience function: run all 6 fusion steps.

    This is the ONLY valid call order for the pipeline.
    """
    return (
        FusionPipeline(store)
        .step1_collect()
        .step2_raw_risk()
        .step3_normalize()
        .step4_module_temporal()
        .step5_composites()
        .step6_laplacian()
    )
