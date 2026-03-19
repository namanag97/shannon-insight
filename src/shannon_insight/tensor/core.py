"""Core 4D relationship tensor: T ∈ ℝ^(N × N × K × R)."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from scipy import sparse

# Relationship type constants
IMPORT = 0
COCHANGE = 1
AUTHOR = 2
SEMANTIC = 3
CLONE = 4
COMBINED = 5
RELATION_NAMES = ["IMPORT", "COCHANGE", "AUTHOR", "SEMANTIC", "CLONE", "COMBINED"]


@dataclass
class RelationTensor:
    """
    T ∈ ℝ^(N × N × K × R) stored as dict of sparse CSR matrices.

    N = number of files
    K = number of time windows (default 12 months)
    R = 5 relationship types (IMPORT, COCHANGE, AUTHOR, SEMANTIC, COMBINED)

    Storage: Dict[(t, r), csr_matrix] for efficient slicing.
    """

    n_files: int
    n_windows: int = 12
    n_relations: int = 5

    # Node index: path ↔ int (bidirectional)
    _node_to_idx: dict[str, int] = field(default_factory=dict)
    _idx_to_node: dict[int, str] = field(default_factory=dict)

    # Sparse storage: (t, r) → csr_matrix
    _slices: dict[tuple[int, int], sparse.csr_matrix] = field(default_factory=dict)

    # COO accumulator for building phase
    _coords: dict[tuple[int, int], list] = field(default_factory=dict)
    _values: dict[tuple[int, int], list] = field(default_factory=dict)
    _finalized: bool = False

    def register_node(self, path: str) -> int:
        """Register a file path, return its index."""
        if path not in self._node_to_idx:
            idx = len(self._node_to_idx)
            self._node_to_idx[path] = idx
            self._idx_to_node[idx] = path
        return self._node_to_idx[path]

    def add_edge(self, src: str, dst: str, t: int, r: int, weight: float = 1.0):
        """Add weighted edge. Accumulates — call finalize() when done."""
        if self._finalized:
            raise RuntimeError("Tensor already finalized")
        i = self.register_node(src)
        j = self.register_node(dst)
        key = (t, r)
        if key not in self._coords:
            self._coords[key] = []
            self._values[key] = []
        self._coords[key].append((i, j))
        self._values[key].append(weight)

    def finalize(self):
        """Convert COO accumulators to CSR matrices. Sums duplicate edges."""
        n = len(self._node_to_idx)
        for (t, r), coords in self._coords.items():
            if not coords:
                continue
            rows, cols = zip(*coords)
            data = self._values[(t, r)]
            coo = sparse.coo_matrix((data, (rows, cols)), shape=(n, n), dtype=np.float32)
            self._slices[(t, r)] = coo.tocsr()
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
        n = len(self._node_to_idx)
        return sparse.csr_matrix((n, n), dtype=np.float32)

    def slice_all_time(self, r: int) -> list[sparse.csr_matrix]:
        """Get T[:,:,:,r] — all time windows for one relation type."""
        return [self.slice(t, r) for t in range(self.n_windows)]

    def slice_all_relations(self, t: int) -> list[sparse.csr_matrix]:
        """Get T[:,:,t,:] — all relation types at one time."""
        return [self.slice(t, r) for r in range(self.n_relations)]

    def node_path(self, idx: int) -> str:
        """Get path for node index."""
        return self._idx_to_node[idx]

    def node_index(self, path: str) -> int:
        """Get index for path."""
        return self._node_to_idx[path]

    def has_node(self, path: str) -> bool:
        return path in self._node_to_idx

    @property
    def n_nodes(self) -> int:
        return len(self._node_to_idx)

    @property
    def n_edges(self) -> int:
        return sum(m.nnz for m in self._slices.values())

    def edge_density(self, t: int, r: int) -> float:
        n = self.n_nodes
        if n < 2:
            return 0.0
        return self.slice(t, r).nnz / (n * (n - 1))

    @property
    def paths(self) -> list[str]:
        """All registered paths in index order."""
        return [self._idx_to_node[i] for i in range(len(self._idx_to_node))]

    def summary(self) -> dict:
        """Return summary statistics."""
        return {
            "n_nodes": self.n_nodes,
            "n_edges": self.n_edges,
            "n_windows": self.n_windows,
            "n_relations": self.n_relations,
            "slices": {
                f"{RELATION_NAMES[r]}_t{t}": self.slice(t, r).nnz
                for t in range(self.n_windows)
                for r in range(self.n_relations)
                if (t, r) in self._slices
            },
        }
