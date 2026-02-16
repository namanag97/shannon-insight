"""Multi-level analysis engine — orchestrates graph construction, algorithms, and measurements."""

from collections import defaultdict
from pathlib import Path
from typing import Callable, Optional

from ..math.compression import Compression
from ..math.gini import Gini
from ..scanning.syntax import FileSyntax
from .algorithms import (
    compute_centrality_gini,
    compute_dag_depth,
    compute_orphans,
    run_graph_algorithms,
)
from .builder import build_dependency_graph
from .models import (
    BoundaryMismatch,
    CodebaseAnalysis,
    FileAnalysis,
    GraphAnalysis,
    ModuleAnalysis,
)


class AnalysisEngine:
    """Executes the full analysis DAG on a set of parsed files."""

    def __init__(
        self,
        file_syntax: list[FileSyntax],
        root_dir: str = "",
        content_getter: Optional[Callable[[str], Optional[str]]] = None,
    ):
        """Initialize the analysis engine.

        Args:
            file_syntax: List of FileSyntax from scanning
            root_dir: Root directory for file resolution
            content_getter: Optional function(rel_path) -> str|None for cached content
        """
        self.file_syntax = file_syntax
        self.root_dir = root_dir
        self._file_map: dict[str, FileSyntax] = {f.path: f for f in file_syntax}
        self._content_getter = content_getter

    def run(self) -> CodebaseAnalysis:
        """Run the full analysis DAG and return structured results."""
        result = CodebaseAnalysis()
        result.total_files = len(self.file_syntax)

        # Phase 2: Build dependency graph from imports
        graph = build_dependency_graph(self.file_syntax, self.root_dir)
        result.graph = graph
        result.total_edges = graph.edge_count

        # Phase 3: Graph algorithms
        graph_analysis = run_graph_algorithms(graph)
        result.graph_analysis = graph_analysis
        result.cycle_count = len(graph_analysis.cycles)
        result.modularity = graph_analysis.modularity_score

        # Phase 3 additions: centrality_gini
        graph_analysis.centrality_gini = compute_centrality_gini(graph_analysis.pagerank)

        # Phase 3: DAG depth computation
        # For now, use simple heuristic for entry points: in_degree=0 files
        # Full role-based entry points will come from Phase 2 semantics
        entry_points = {
            path
            for path, degree in graph_analysis.in_degree.items()
            if degree == 0 and graph_analysis.out_degree.get(path, 0) > 0
        }
        graph_analysis.depth = compute_dag_depth(graph.adjacency, entry_points)

        # Phase 3: Orphan detection (without roles, all in_degree=0 are candidates)
        # When roles are available (Phase 2), will filter ENTRY_POINT and TEST
        no_roles: dict[str, str] = {}  # Empty roles for now
        graph_analysis.is_orphan = compute_orphans(graph_analysis.in_degree, no_roles)

        # Phase 4a: Per-file measurements (construct-level + graph-level)
        result.files = self._measure_files(graph, graph_analysis)

        # Phase 4b: Per-module measurements
        result.modules = self._measure_modules(graph, graph_analysis)
        result.total_modules = len(result.modules)

        # Phase 4c: Boundary analysis (declared vs discovered)
        result.boundary_mismatches = self._analyze_boundaries(result.modules, graph_analysis)

        # Phase 5: Statistical outlier detection
        result.outliers = self._detect_outliers(result.files)

        return result

    # ── Phase 4a: Per-file Measurements ────────────────────────────

    def _measure_files(self, graph, ga: GraphAnalysis) -> dict[str, FileAnalysis]:
        results: dict[str, FileAnalysis] = {}

        for fm in self.file_metrics:
            fa = FileAnalysis(path=fm.path, lines=fm.lines)

            # Construct-level measurements
            fa.function_count = fm.functions
            fa.nesting_depth = fm.nesting_depth
            fa.max_function_size = max(fm.function_sizes) if fm.function_sizes else 0

            # Compression ratio (read file content)
            content = self._read_file_content(fm.path)
            if content:
                fa.compression_ratio = Compression.compression_ratio(content.encode("utf-8"))

            # Cognitive load with Gini
            fa.cognitive_load = self._compute_cognitive_load(fm)
            if fm.function_sizes and len(fm.function_sizes) > 1:
                fa.function_size_gini = Gini.gini_coefficient(fm.function_sizes)

            # Graph-level measurements
            fa.pagerank = ga.pagerank.get(fm.path, 0.0)
            fa.betweenness = ga.betweenness.get(fm.path, 0.0)
            fa.in_degree = ga.in_degree.get(fm.path, 0)
            fa.out_degree = ga.out_degree.get(fm.path, 0)
            fa.blast_radius_size = len(ga.blast_radius.get(fm.path, set()))
            fa.community_id = ga.node_community.get(fm.path, -1)

            # Cycle membership
            fa.cycle_member = any(fm.path in cycle.nodes for cycle in ga.cycles)

            # Direct dependencies
            fa.depends_on = graph.adjacency.get(fm.path, [])
            fa.depended_on_by = graph.reverse.get(fm.path, [])

            # Phase 3 additions
            fa.depth = ga.depth.get(fm.path, -1)
            fa.is_orphan = ga.is_orphan.get(fm.path, False)
            fa.phantom_import_count = len(graph.unresolved_imports.get(fm.path, []))

            results[fm.path] = fa

        return results

    def _compute_cognitive_load(self, fm: FileMetrics) -> float:
        """Cognitive load: weighted sum of complexity factors.

        Based on research on code comprehension difficulty:
        - Lines of code (log-scaled, diminishing returns)
        - Cyclomatic complexity (decision points to track)
        - Nesting depth (working memory load)
        - Function count (context switches)
        - Gini inequality (god functions harder to understand)

        Formula: log2(lines+1) * (1 + complexity/10) * (1 + nesting/5) * (1 + gini)

        Output is typically 0-50 for normal files, 50-100 for complex files.
        """
        import math

        # Log-scaled lines (1000 lines = ~10, 100 lines = ~7)
        lines_factor = math.log2(fm.lines + 1) if fm.lines > 0 else 0

        # Complexity factor: average cyclomatic complexity
        # complexity_score is now average per function
        complexity_factor = 1 + fm.complexity_score / 10

        # Nesting penalty: deep nesting is hard to follow
        nesting_factor = 1 + fm.nesting_depth / 5

        # Gini penalty: unequal function sizes suggest god functions
        gini = 0.0
        if fm.function_sizes and len(fm.function_sizes) > 1:
            gini = Gini.gini_coefficient(fm.function_sizes)
        gini_factor = 1 + gini

        return lines_factor * complexity_factor * nesting_factor * gini_factor

    def _read_file_content(self, rel_path: str) -> Optional[str]:
        """Read file content from cache or disk."""
        # Try cache first (avoids disk I/O)
        if self._content_getter is not None:
            content = self._content_getter(rel_path)
            if content is not None:
                return content

        # Fallback to disk read
        if self.root_dir:
            full_path = Path(self.root_dir) / rel_path
        else:
            full_path = Path(rel_path)

        try:
            return full_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return None

    # ── Phase 4b: Per-module Measurements ──────────────────────────

    def _measure_modules(self, graph, ga: GraphAnalysis) -> dict[str, ModuleAnalysis]:
        """Compute per-module (directory) metrics: cohesion, coupling."""
        # Group files by parent directory
        module_files: dict[str, list[str]] = defaultdict(list)
        for fm in self.file_metrics:
            module_path = str(Path(fm.path).parent)
            module_files[module_path].append(fm.path)

        results: dict[str, ModuleAnalysis] = {}

        for mod_path, files in module_files.items():
            file_set = set(files)
            ma = ModuleAnalysis(path=mod_path, files=files, file_count=len(files))

            # Count internal vs external edges
            for f in files:
                for dep in graph.adjacency.get(f, []):
                    if dep in file_set:
                        ma.internal_edges += 1
                    else:
                        ma.external_edges_out += 1
                for dep in graph.reverse.get(f, []):
                    if dep not in file_set:
                        ma.external_edges_in += 1

            # Cohesion: internal edges / possible internal edges
            n = len(files)
            possible = n * (n - 1) if n > 1 else 1
            ma.cohesion = ma.internal_edges / possible if possible > 0 else 0.0

            # Coupling: external edges / total edges
            total = ma.internal_edges + ma.external_edges_out + ma.external_edges_in
            ma.coupling = (
                (ma.external_edges_out + ma.external_edges_in) / total if total > 0 else 0.0
            )

            # Community alignment
            community_ids = set()
            comm_counts: dict[int, int] = defaultdict(int)
            for f in files:
                cid = ga.node_community.get(f, -1)
                community_ids.add(cid)
                comm_counts[cid] += 1

            ma.community_ids = community_ids
            if comm_counts:
                dominant_count = max(comm_counts.values())
                ma.boundary_alignment = dominant_count / len(files)
            else:
                ma.boundary_alignment = 1.0

            results[mod_path] = ma

        return results

    # ── Phase 4c: Boundary Analysis ────────────────────────────────

    def _analyze_boundaries(
        self,
        modules: dict[str, ModuleAnalysis],
        ga: GraphAnalysis,
    ) -> list[BoundaryMismatch]:
        """Find modules where declared boundaries don't match communities."""
        mismatches: list[BoundaryMismatch] = []

        for mod_path, ma in modules.items():
            if ma.boundary_alignment < 0.7 and ma.file_count > 2:
                # This module spans multiple communities
                comm_dist: dict[int, int] = defaultdict(int)
                for f in ma.files:
                    cid = ga.node_community.get(f, -1)
                    comm_dist[cid] += 1

                # Find the dominant community
                dominant_comm = max(comm_dist, key=lambda k: comm_dist[k])

                # Files not in the dominant community are "misplaced"
                misplaced = []
                for f in ma.files:
                    cid = ga.node_community.get(f, -1)
                    if cid != dominant_comm:
                        # Suggest the module where most of that community's files live
                        suggested = self._suggest_module(f, cid, modules, ga)
                        misplaced.append((f, suggested))

                mismatches.append(
                    BoundaryMismatch(
                        module_path=mod_path,
                        declared_files=set(ma.files),
                        community_distribution=dict(comm_dist),
                        misplaced_files=misplaced,
                    )
                )

        return mismatches

    def _suggest_module(
        self,
        file_path: str,
        community_id: int,
        modules: dict[str, ModuleAnalysis],
        ga: GraphAnalysis,
    ) -> str:
        """Suggest which module a misplaced file should belong to."""
        # Find the module that has the most files in this community
        best_module = ""
        best_count = 0

        for mod_path, ma in modules.items():
            count = sum(1 for f in ma.files if ga.node_community.get(f, -1) == community_id)
            if count > best_count:
                best_count = count
                best_module = mod_path

        return best_module or "unknown"

    # ── Phase 5: Statistical Outlier Detection ─────────────────────

    def _detect_outliers(self, files: dict[str, FileAnalysis]) -> dict[str, list[str]]:
        """Detect statistical outliers using MAD (robust to heavy-tailed distributions)."""
        outliers: dict[str, list[str]] = defaultdict(list)

        if len(files) < 5:
            return dict(outliers)

        # Metrics to check for outliers.
        # Only flag things that are likely problems, not just structural facts.
        # Hub/fan-in/fan-out are structural properties, not defects — excluded here.
        metrics = {
            "cognitive_load": ("high cognitive load", lambda f: f.cognitive_load),
            "compression_ratio": ("high compression complexity", lambda f: f.compression_ratio),
            "function_size_gini": (
                "unequal function sizes (possible God function)",
                lambda f: f.function_size_gini,
            ),
            "blast_radius_size": ("large blast radius", lambda f: float(f.blast_radius_size)),
        }

        for _metric_name, (description, extractor) in metrics.items():
            values = [(path, extractor(fa)) for path, fa in files.items()]
            vals_only = [v for _, v in values]

            # Use MAD (Median Absolute Deviation) for robust outlier detection
            median_val = self._median(vals_only)
            mad = self._mad(vals_only)

            if mad == 0:
                continue

            # Modified z-score threshold. Standard is 3.5 (Iglewicz & Hoaglin),
            # but we use 5.0 to only flag truly extreme outliers and reduce noise.
            threshold = 5.0
            for path, val in values:
                modified_z = 0.6745 * (val - median_val) / mad
                if modified_z > threshold:
                    outliers[path].append(
                        f"{description} (value={val:.3f}, "
                        f"median={median_val:.3f}, modified_z={modified_z:.1f})"
                    )

        # Also flag cycle membership
        for path, fa in files.items():
            if fa.cycle_member:
                outliers[path].append("member of circular dependency")

        return dict(outliers)

    @staticmethod
    def _median(values: list[float]) -> float:
        if not values:
            return 0.0
        sorted_v = sorted(values)
        n = len(sorted_v)
        if n % 2 == 0:
            return (sorted_v[n // 2 - 1] + sorted_v[n // 2]) / 2
        return sorted_v[n // 2]

    @staticmethod
    def _mad(values: list[float]) -> float:
        """Median Absolute Deviation."""
        if not values:
            return 0.0
        median = AnalysisEngine._median(values)
        deviations = [abs(v - median) for v in values]
        return AnalysisEngine._median(deviations)
