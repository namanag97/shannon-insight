"""SpectralAnalyzer — Laplacian eigenvalues and Fiedler value."""

from collections import defaultdict

from ...infrastructure.entities import EntityId, EntityType
from ...infrastructure.signals import Signal
from ...logging_config import get_logger
from ...temporal.models import SpectralSummary
from ..store_v2 import AnalysisStore

logger = get_logger(__name__)


class SpectralAnalyzer:
    name = "spectral"
    requires: set[str] = {"structural"}
    provides: set[str] = {"spectral"}

    def analyze(self, store: AnalysisStore) -> None:
        if not store.structural.available:
            return

        structural = store.structural.value
        graph = structural.graph
        if len(graph.all_nodes) < 3:
            return

        try:
            import numpy as np
        except ImportError:
            logger.info("numpy not available — spectral analysis skipped")
            return

        # Build undirected adjacency from directed graph
        nodes = sorted(graph.all_nodes)
        node_idx = {n: i for i, n in enumerate(nodes)}
        n = len(nodes)

        adj = np.zeros((n, n), dtype=float)  # type: ignore[var-annotated]
        for src, targets in graph.adjacency.items():
            i = node_idx.get(src)
            if i is None:
                continue
            for tgt in targets:
                j = node_idx.get(tgt)
                if j is not None:
                    adj[i][j] = 1.0
                    adj[j][i] = 1.0  # undirected

        # Laplacian: L = D - A
        degree_vec = adj.sum(axis=1)
        laplacian = np.diag(degree_vec) - adj

        # Eigendecomposition
        eigenvalues = np.linalg.eigvalsh(laplacian)
        eigenvalues = sorted(eigenvalues.tolist())

        # Number of connected components = number of zero eigenvalues
        tolerance = 1e-8
        num_components = sum(1 for ev in eigenvalues if abs(ev) < tolerance)

        # Fiedler value (2nd smallest eigenvalue)
        # For disconnected graphs, compute on largest connected component
        fiedler_value = 0.0
        if num_components <= 1 and len(eigenvalues) >= 2:
            fiedler_value = eigenvalues[1]
        elif num_components > 1:
            # Find largest connected component and compute Fiedler on it
            fiedler_value = self._fiedler_largest_component(graph.adjacency, graph.all_nodes, np)

        # Spectral gap: ratio of 2nd to 3rd eigenvalue
        spectral_gap = 0.0
        non_zero = [ev for ev in eigenvalues if ev > tolerance]
        if len(non_zero) >= 2:
            spectral_gap = non_zero[0] / non_zero[1] if non_zero[1] > 0 else 0.0

        result = SpectralSummary(
            fiedler_value=fiedler_value,
            num_components=num_components,
            eigenvalues=eigenvalues[: min(20, len(eigenvalues))],  # cap for storage
            spectral_gap=spectral_gap,
        )
        store.spectral.set(result, produced_by=self.name)

        # Sync spectral signals to FactStore
        if hasattr(store, "fact_store"):
            codebase_id = EntityId(EntityType.CODEBASE, store.root_dir)
            store.fact_store.set_signal(codebase_id, Signal.FIEDLER_VALUE, fiedler_value)
            store.fact_store.set_signal(codebase_id, Signal.SPECTRAL_GAP, spectral_gap)

        logger.debug(f"Spectral analysis: Fiedler={fiedler_value:.4f}, components={num_components}")

    def _fiedler_largest_component(self, adjacency, all_nodes, np):
        """Compute Fiedler value on the largest connected component."""
        # BFS to find connected components on the undirected version
        undirected = defaultdict(set)
        for src, targets in adjacency.items():
            for tgt in targets:
                if tgt in all_nodes:
                    undirected[src].add(tgt)
                    undirected[tgt].add(src)

        visited = set()
        components = []
        for node in all_nodes:
            if node in visited:
                continue
            component = set()
            queue = [node]
            while queue:
                curr = queue.pop()
                if curr in visited:
                    continue
                visited.add(curr)
                component.add(curr)
                queue.extend(undirected[curr] - visited)
            components.append(component)

        if not components:
            return 0.0

        largest = max(components, key=len)
        if len(largest) < 3:
            return 0.0

        nodes = sorted(largest)
        node_idx = {n: i for i, n in enumerate(nodes)}
        n = len(nodes)

        adj = np.zeros((n, n), dtype=float)
        for src in nodes:
            i = node_idx[src]
            for tgt in undirected[src]:
                j = node_idx.get(tgt)
                if j is not None:
                    adj[i][j] = 1.0

        degree_vec = adj.sum(axis=1)
        laplacian = np.diag(degree_vec) - adj
        eigenvalues = sorted(np.linalg.eigvalsh(laplacian).tolist())

        return eigenvalues[1] if len(eigenvalues) >= 2 else 0.0
