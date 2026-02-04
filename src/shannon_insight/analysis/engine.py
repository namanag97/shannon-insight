"""Multi-level analysis engine implementing the computation DAG.

DAG:
  Parse → Constructs + Relationships
       → Build Graphs
       → Graph Algorithms (centrality, SCC, blast radius, communities)
       → Measure Constructs (compression, cognitive load)
       → Measure Modules (cohesion, coupling, boundary alignment)
       → Statistical Layer (outlier detection)
       → Result Store
"""

from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from ..models import FileMetrics
from ..math.graph import GraphMetrics
from ..math.compression import Compression
from ..math.gini import Gini
from .models import (
    CodebaseAnalysis,
    DependencyGraph,
    GraphAnalysis,
    CycleGroup,
    Community,
    FileAnalysis,
    ModuleAnalysis,
    BoundaryMismatch,
)


class AnalysisEngine:
    """Executes the full analysis DAG on a set of parsed files."""

    def __init__(self, file_metrics: List[FileMetrics], root_dir: str = ""):
        self.file_metrics = file_metrics
        self.root_dir = root_dir
        self._file_map: Dict[str, FileMetrics] = {f.path: f for f in file_metrics}

    def run(self) -> CodebaseAnalysis:
        """Run the full analysis DAG and return structured results."""
        result = CodebaseAnalysis()
        result.total_files = len(self.file_metrics)

        # Phase 2: Build dependency graph from imports
        graph = self._build_dependency_graph()
        result.graph = graph
        result.total_edges = graph.edge_count

        # Phase 3: Graph algorithms
        graph_analysis = self._run_graph_algorithms(graph)
        result.graph_analysis = graph_analysis
        result.cycle_count = len(graph_analysis.cycles)
        result.modularity = graph_analysis.modularity_score

        # Phase 4a: Per-file measurements (construct-level + graph-level)
        result.files = self._measure_files(graph, graph_analysis)

        # Phase 4b: Per-module measurements
        result.modules = self._measure_modules(graph, graph_analysis)
        result.total_modules = len(result.modules)

        # Phase 4c: Boundary analysis (declared vs discovered)
        result.boundary_mismatches = self._analyze_boundaries(
            result.modules, graph_analysis
        )

        # Phase 5: Statistical outlier detection
        result.outliers = self._detect_outliers(result.files)

        return result

    # ── Phase 2: Graph Construction ────────────────────────────────

    def _build_dependency_graph(self) -> DependencyGraph:
        """Build dependency graph from import declarations in FileMetrics."""
        all_paths = set(self._file_map.keys())
        adjacency: Dict[str, List[str]] = {p: [] for p in all_paths}
        reverse: Dict[str, List[str]] = {p: [] for p in all_paths}
        edge_count = 0

        path_index = self._build_path_index(all_paths)

        for fm in self.file_metrics:
            for imp in fm.imports:
                resolved = self._resolve_import(imp, fm.path, path_index, all_paths)
                if resolved and resolved != fm.path:
                    adjacency[fm.path].append(resolved)
                    reverse[resolved].append(fm.path)
                    edge_count += 1

        return DependencyGraph(
            adjacency=adjacency,
            reverse=reverse,
            all_nodes=all_paths,
            edge_count=edge_count,
        )

    def _build_path_index(self, all_paths: Set[str]) -> Dict[str, str]:
        """Map dotted module paths to file paths for import resolution.

        Builds multiple lookup keys per file so resolution can work
        from different prefix levels.
        """
        index: Dict[str, str] = {}
        for path in all_paths:
            # "src/shannon_insight/models.py" -> dotted form
            dotted = (
                path.replace("/", ".")
                .replace("\\", ".")
                .replace(".py", "")
            )
            # Remove __init__ suffix: "src.shannon_insight.math.__init__" -> "src.shannon_insight.math"
            if dotted.endswith(".__init__"):
                dotted = dotted[: -len(".__init__")]

            index[dotted] = path

            # Also without "src." prefix
            if dotted.startswith("src."):
                short = dotted[4:]
                index[short] = path

        return index

    def _resolve_import(
        self,
        imp: str,
        source_path: str,
        path_index: Dict[str, str],
        all_paths: Set[str],
    ) -> Optional[str]:
        """Resolve an import string to a file path in the codebase.

        Handles:
          - Relative imports: .base, ..models, ..math.graph
          - Absolute imports: shannon_insight.models, pathlib, os
        """
        imp = imp.strip()

        # ── Relative imports (leading dots) ────────────────────────
        if imp.startswith("."):
            return self._resolve_relative_import(imp, source_path, all_paths)

        # ── Absolute imports ───────────────────────────────────────
        # Try exact match in index
        if imp in path_index:
            return path_index[imp]

        # Try with common project prefixes stripped
        for prefix in ("src.", "src.shannon_insight."):
            candidate = prefix + imp
            if candidate in path_index:
                return path_index[candidate]

        # Not an internal import (stdlib or third-party)
        return None

    def _resolve_relative_import(
        self, imp: str, source_path: str, all_paths: Set[str]
    ) -> Optional[str]:
        """Resolve a Python relative import like ..models or .base."""
        # Count leading dots
        dot_count = 0
        while dot_count < len(imp) and imp[dot_count] == ".":
            dot_count += 1
        module_part = imp[dot_count:]  # e.g., "models", "math.graph", "base"

        # Navigate up from source file's directory
        source_dir = Path(source_path).parent
        for _ in range(dot_count - 1):  # -1 because . means current package
            source_dir = source_dir.parent

        # Build candidate paths
        if module_part:
            module_as_path = module_part.replace(".", "/")
            candidates = [
                str(source_dir / module_as_path) + ".py",
                str(source_dir / module_as_path / "__init__.py"),
            ]
        else:
            candidates = [str(source_dir / "__init__.py")]

        for candidate in candidates:
            if candidate in all_paths:
                return candidate

        return None

    # ── Phase 3: Graph Algorithms ──────────────────────────────────

    def _run_graph_algorithms(self, graph: DependencyGraph) -> GraphAnalysis:
        analysis = GraphAnalysis()

        # Centrality (reuse existing math)
        analysis.pagerank = GraphMetrics.pagerank(graph.adjacency)
        analysis.betweenness = GraphMetrics.betweenness_centrality(graph.adjacency)

        # Degree
        for node in graph.all_nodes:
            analysis.out_degree[node] = len(graph.adjacency.get(node, []))
            analysis.in_degree[node] = len(graph.reverse.get(node, []))

        # Strongly connected components (Tarjan's algorithm)
        sccs = self._tarjan_scc(graph.adjacency, graph.all_nodes)
        for scc in sccs:
            if len(scc) > 1:  # Only real cycles
                internal_edges = sum(
                    1
                    for n in scc
                    for neighbor in graph.adjacency.get(n, [])
                    if neighbor in scc
                )
                analysis.cycles.append(
                    CycleGroup(nodes=scc, internal_edge_count=internal_edges)
                )

        # Blast radius (transitive closure on reverse graph)
        analysis.blast_radius = self._compute_blast_radius(graph.reverse)

        # Community detection (Louvain)
        communities, node_community, modularity = self._louvain(
            graph.adjacency, graph.all_nodes
        )
        analysis.communities = communities
        analysis.node_community = node_community
        analysis.modularity_score = modularity

        return analysis

    def _tarjan_scc(
        self, adjacency: Dict[str, List[str]], all_nodes: Set[str]
    ) -> List[Set[str]]:
        """Tarjan's algorithm for strongly connected components."""
        index_counter = [0]
        stack: List[str] = []
        on_stack: Set[str] = set()
        index: Dict[str, int] = {}
        lowlink: Dict[str, int] = {}
        result: List[Set[str]] = []

        def strongconnect(v: str):
            index[v] = index_counter[0]
            lowlink[v] = index_counter[0]
            index_counter[0] += 1
            stack.append(v)
            on_stack.add(v)

            for w in adjacency.get(v, []):
                if w not in all_nodes:
                    continue
                if w not in index:
                    strongconnect(w)
                    lowlink[v] = min(lowlink[v], lowlink[w])
                elif w in on_stack:
                    lowlink[v] = min(lowlink[v], index[w])

            if lowlink[v] == index[v]:
                component: Set[str] = set()
                while True:
                    w = stack.pop()
                    on_stack.discard(w)
                    component.add(w)
                    if w == v:
                        break
                result.append(component)

        for v in all_nodes:
            if v not in index:
                strongconnect(v)

        return result

    def _compute_blast_radius(
        self, reverse_adj: Dict[str, List[str]]
    ) -> Dict[str, Set[str]]:
        """Compute blast radius: for each file, what files are transitively affected.

        Uses BFS on the reverse graph. If A imports B, then changing B
        affects A. So we follow reverse edges from each node.
        """
        blast: Dict[str, Set[str]] = {}

        for start_node in reverse_adj:
            visited: Set[str] = set()
            queue = list(reverse_adj.get(start_node, []))
            while queue:
                node = queue.pop(0)
                if node in visited:
                    continue
                visited.add(node)
                queue.extend(
                    n for n in reverse_adj.get(node, []) if n not in visited
                )
            blast[start_node] = visited

        return blast

    def _louvain(
        self,
        adjacency: Dict[str, List[str]],
        all_nodes: Set[str],
    ) -> Tuple[List[Community], Dict[str, int], float]:
        """Louvain community detection.

        Maximizes modularity Q = (1/2m) * sum[(A_ij - k_i*k_j/2m) * delta(c_i, c_j)]
        Uses the correct two-part gain: cost of removal + benefit of insertion.

        Returns (communities, node->community_id, modularity_score).
        """
        nodes = list(all_nodes)
        if not nodes:
            return [], {}, 0.0

        # Build undirected weighted adjacency for modularity computation
        edge_weights: Dict[Tuple[str, str], float] = {}
        degree: Dict[str, float] = defaultdict(float)

        for src, targets in adjacency.items():
            for tgt in targets:
                if tgt not in all_nodes:
                    continue
                key = (min(src, tgt), max(src, tgt))
                edge_weights[key] = edge_weights.get(key, 0) + 1
                degree[src] += 1
                degree[tgt] += 1

        m = sum(edge_weights.values())  # total edge weight
        if m == 0:
            communities = [
                Community(id=i, members={n}) for i, n in enumerate(nodes)
            ]
            node_community = {n: i for i, n in enumerate(nodes)}
            return communities, node_community, 0.0

        two_m = 2.0 * m

        # Initialize: each node in its own community
        node_comm: Dict[str, int] = {n: i for i, n in enumerate(nodes)}
        comm_members: Dict[int, Set[str]] = {i: {n} for i, n in enumerate(nodes)}

        # Precompute: sum of degrees per community
        sigma_tot: Dict[int, float] = {i: degree.get(n, 0) for i, n in enumerate(nodes)}

        # Neighbor edges per node
        neighbors: Dict[str, Dict[str, float]] = defaultdict(lambda: defaultdict(float))
        for (a, b), w in edge_weights.items():
            neighbors[a][b] += w
            neighbors[b][a] += w

        max_passes = 20  # Safety limit
        for _pass in range(max_passes):
            moved = False
            for node in nodes:
                current_comm = node_comm[node]
                ki = degree.get(node, 0)

                # Weights from node to each neighboring community
                comm_edge_weights: Dict[int, float] = defaultdict(float)
                for neighbor, w in neighbors[node].items():
                    comm_edge_weights[node_comm[neighbor]] += w

                # Weight from node to its own community (excluding self-loops)
                ki_in_current = comm_edge_weights.get(current_comm, 0.0)

                # Cost of removing node from current community
                # sigma_tot of current community MINUS node's own degree
                sigma_current = sigma_tot.get(current_comm, 0) - ki
                remove_cost = ki_in_current / two_m - (sigma_current * ki) / (two_m * two_m)

                best_comm = current_comm
                best_gain = 0.0

                for comm_id, ki_in_target in comm_edge_weights.items():
                    if comm_id == current_comm:
                        continue

                    sigma_target = sigma_tot.get(comm_id, 0)
                    # Gain of adding node to target community
                    add_gain = ki_in_target / two_m - (sigma_target * ki) / (two_m * two_m)

                    # Net gain = add_gain - remove_cost
                    net_gain = add_gain - remove_cost

                    if net_gain > best_gain:
                        best_gain = net_gain
                        best_comm = comm_id

                if best_comm != current_comm:
                    # Update sigma_tot
                    sigma_tot[current_comm] = sigma_tot.get(current_comm, 0) - ki
                    sigma_tot[best_comm] = sigma_tot.get(best_comm, 0) + ki

                    # Move node
                    comm_members[current_comm].discard(node)
                    if not comm_members[current_comm]:
                        del comm_members[current_comm]
                        if current_comm in sigma_tot:
                            del sigma_tot[current_comm]
                    comm_members.setdefault(best_comm, set()).add(node)
                    node_comm[node] = best_comm
                    moved = True

            if not moved:
                break

        # Build result
        communities = [
            Community(id=cid, members=members)
            for cid, members in comm_members.items()
        ]
        modularity = self._compute_modularity(
            edge_weights, degree, node_comm, m
        )

        return communities, node_comm, modularity

    @staticmethod
    def _compute_modularity(
        edge_weights: Dict[Tuple[str, str], float],
        degree: Dict[str, float],
        node_comm: Dict[str, int],
        m: float,
    ) -> float:
        """Compute modularity Q = (1/2m) * sum[(A_ij - ki*kj/2m) * delta(ci,cj)]."""
        if m == 0:
            return 0.0
        two_m = 2.0 * m
        q = 0.0
        for (a, b), w in edge_weights.items():
            if node_comm.get(a) == node_comm.get(b):
                q += w - (degree.get(a, 0) * degree.get(b, 0)) / two_m
        return q / two_m

    # ── Phase 4a: Per-file Measurements ────────────────────────────

    def _measure_files(
        self, graph: DependencyGraph, ga: GraphAnalysis
    ) -> Dict[str, FileAnalysis]:
        results: Dict[str, FileAnalysis] = {}

        for fm in self.file_metrics:
            fa = FileAnalysis(path=fm.path, lines=fm.lines)

            # Construct-level measurements
            fa.function_count = fm.functions
            fa.nesting_depth = fm.nesting_depth
            fa.max_function_size = max(fm.function_sizes) if fm.function_sizes else 0

            # Compression ratio (read file content)
            content = self._read_file_content(fm.path)
            if content:
                fa.compression_ratio = Compression.compression_ratio(
                    content.encode("utf-8")
                )

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
            fa.cycle_member = any(
                fm.path in cycle.nodes for cycle in ga.cycles
            )

            # Direct dependencies
            fa.depends_on = graph.adjacency.get(fm.path, [])
            fa.depended_on_by = graph.reverse.get(fm.path, [])

            results[fm.path] = fa

        return results

    def _compute_cognitive_load(self, fm: FileMetrics) -> float:
        """Cognitive load with Gini-based concentration penalty."""
        n_concepts = fm.functions + fm.structs + fm.interfaces

        gini = 0.0
        if fm.function_sizes and len(fm.function_sizes) > 1:
            gini = Gini.gini_coefficient(fm.function_sizes)

        base = n_concepts * fm.complexity_score * (1 + fm.nesting_depth / 10)
        concentration = 1 + gini
        return base * concentration

    def _read_file_content(self, rel_path: str) -> Optional[str]:
        """Read file content from disk."""
        if self.root_dir:
            full_path = Path(self.root_dir) / rel_path
        else:
            full_path = Path(rel_path)

        try:
            return full_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return None

    # ── Phase 4b: Per-module Measurements ──────────────────────────

    def _measure_modules(
        self, graph: DependencyGraph, ga: GraphAnalysis
    ) -> Dict[str, ModuleAnalysis]:
        """Compute per-module (directory) metrics: cohesion, coupling."""
        # Group files by parent directory
        module_files: Dict[str, List[str]] = defaultdict(list)
        for fm in self.file_metrics:
            module_path = str(Path(fm.path).parent)
            module_files[module_path].append(fm.path)

        results: Dict[str, ModuleAnalysis] = {}

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
                (ma.external_edges_out + ma.external_edges_in) / total
                if total > 0
                else 0.0
            )

            # Community alignment
            community_ids = set()
            comm_counts: Dict[int, int] = defaultdict(int)
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
        modules: Dict[str, ModuleAnalysis],
        ga: GraphAnalysis,
    ) -> List[BoundaryMismatch]:
        """Find modules where declared boundaries don't match communities."""
        mismatches: List[BoundaryMismatch] = []

        for mod_path, ma in modules.items():
            if ma.boundary_alignment < 0.7 and ma.file_count > 2:
                # This module spans multiple communities
                comm_dist: Dict[int, int] = defaultdict(int)
                for f in ma.files:
                    cid = ga.node_community.get(f, -1)
                    comm_dist[cid] += 1

                # Find the dominant community
                dominant_comm = max(comm_dist, key=comm_dist.get)

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
        modules: Dict[str, ModuleAnalysis],
        ga: GraphAnalysis,
    ) -> str:
        """Suggest which module a misplaced file should belong to."""
        # Find the module that has the most files in this community
        best_module = ""
        best_count = 0

        for mod_path, ma in modules.items():
            count = sum(
                1 for f in ma.files
                if ga.node_community.get(f, -1) == community_id
            )
            if count > best_count:
                best_count = count
                best_module = mod_path

        return best_module or "unknown"

    # ── Phase 5: Statistical Outlier Detection ─────────────────────

    def _detect_outliers(
        self, files: Dict[str, FileAnalysis]
    ) -> Dict[str, List[str]]:
        """Detect statistical outliers using MAD (robust to heavy-tailed distributions)."""
        outliers: Dict[str, List[str]] = defaultdict(list)

        if len(files) < 5:
            return dict(outliers)

        # Metrics to check for outliers.
        # Only flag things that are likely problems, not just structural facts.
        # Hub/fan-in/fan-out are structural properties, not defects — excluded here.
        metrics = {
            "cognitive_load": ("high cognitive load", lambda f: f.cognitive_load),
            "compression_ratio": ("high compression complexity", lambda f: f.compression_ratio),
            "function_size_gini": ("unequal function sizes (possible God function)", lambda f: f.function_size_gini),
            "blast_radius_size": ("large blast radius", lambda f: float(f.blast_radius_size)),
        }

        for metric_name, (description, extractor) in metrics.items():
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
    def _median(values: List[float]) -> float:
        if not values:
            return 0.0
        sorted_v = sorted(values)
        n = len(sorted_v)
        if n % 2 == 0:
            return (sorted_v[n // 2 - 1] + sorted_v[n // 2]) / 2
        return sorted_v[n // 2]

    @staticmethod
    def _mad(values: List[float]) -> float:
        """Median Absolute Deviation."""
        if not values:
            return 0.0
        median = AnalysisEngine._median(values)
        deviations = [abs(v - median) for v in values]
        return AnalysisEngine._median(deviations)
