"""Core 4D relationship tensor."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterator
import numpy as np
from scipy import sparse

# Relationship type constants
IMPORT = 0
COCHANGE = 1
AUTHOR = 2
SEMANTIC = 3
COMBINED = 4

RELATION_NAMES = ["IMPORT", "COCHANGE", "AUTHOR", "SEMANTIC", "COMBINED"]


@dataclass
class RelationTensor:
    """
    T ∈ ℝ^(N × N × K × R) stored as dict of sparse matrices.

    Storage: Dict[(t, r), csr_matrix] for efficient slicing.

    Usage:
        tensor = RelationTensor(n_files=100, n_windows=12)
        tensor.add_edge("a.py", "b.py", t=0, r=IMPORT, weight=1.0)

        # Get adjacency matrix for IMPORT at time 0
        A = tensor.slice(t=0, r=IMPORT)

        # Run PageRank
        pr = pagerank(A)
    """
    n_files: int
    n_windows: int = 12
    n_relations: int = 5

    # Node index: path ↔ int
    node_index: dict[str, int] = field(default_factory=dict)
    index_node: dict[int, str] = field(default_factory=dict)

    # Sparse storage: (t, r) → csr_matrix
    _slices: dict[tuple[int, int], sparse.csr_matrix] = field(default_factory=dict)

    # COO accumulator for building
    _coords: dict[tuple[int, int], list] = field(default_factory=dict)
    _values: dict[tuple[int, int], list] = field(default_factory=dict)
    _finalized: bool = False

    def register_node(self, path: str) -> int:
        """Register a file path and return its index."""
        if path not in self.node_index:
            idx = len(self.node_index)
            if idx >= self.n_files:
                raise ValueError(f"Exceeded n_files={self.n_files}")
            self.node_index[path] = idx
            self.index_node[idx] = path
        return self.node_index[path]

    def add_edge(self, src: str, dst: str, t: int, r: int, weight: float = 1.0):
        """Add weighted edge to tensor (accumulates, call finalize() when done)."""
        if self._finalized:
            raise RuntimeError("Tensor already finalized. Create new instance.")

        i = self.register_node(src)
        j = self.register_node(dst)

        key = (t, r)
        if key not in self._coords:
            self._coords[key] = []
            self._values[key] = []

        self._coords[key].append((i, j))
        self._values[key].append(weight)

    def finalize(self):
        """Convert COO accumulators to CSR matrices."""
        n = len(self.node_index)

        for (t, r), coords in self._coords.items():
            if not coords:
                continue
            rows, cols = zip(*coords)
            data = self._values[(t, r)]

            coo = sparse.coo_matrix(
                (data, (rows, cols)),
                shape=(n, n),
                dtype=np.float32
            )
            # Sum duplicates and convert to CSR
            self._slices[(t, r)] = coo.tocsr()

        # Clear accumulators
        self._coords.clear()
        self._values.clear()
        self._finalized = True

    def slice(self, t: int, r: int) -> sparse.csr_matrix:
        """Get adjacency matrix T[:,:,t,r]."""
        if not self._finalized:
            self.finalize()

        key = (t, r)
        if key in self._slices:
            return self._slices[key]

        # Return empty matrix
        n = len(self.node_index)
        return sparse.csr_matrix((n, n), dtype=np.float32)

    def slice_all_time(self, r: int) -> list[sparse.csr_matrix]:
        """Get T[:,:,:,r] as list of matrices for temporal analysis."""
        return [self.slice(t, r) for t in range(self.n_windows)]

    def slice_all_relations(self, t: int) -> list[sparse.csr_matrix]:
        """Get T[:,:,t,:] as list of matrices for cross-layer analysis."""
        return [self.slice(t, r) for r in range(self.n_relations)]

    @property
    def n_nodes(self) -> int:
        return len(self.node_index)

    @property
    def n_edges(self) -> int:
        return sum(m.nnz for m in self._slices.values())

    def edge_density(self, t: int, r: int) -> float:
        """Fraction of possible edges that exist."""
        n = self.n_nodes
        if n < 2:
            return 0.0
        return self.slice(t, r).nnz / (n * (n - 1))
