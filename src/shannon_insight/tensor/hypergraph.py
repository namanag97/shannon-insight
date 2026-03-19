"""Hypergraph incidence matrix for commit-level co-change analysis.

A commit touching files {A, B, C} is a 3-way hyperedge. Modeling this
as pairwise edges (A,B), (A,C), (B,C) loses the "changed together as
a unit" semantics. The hypergraph preserves this.

The incidence matrix H ∈ {0,1}^(N × M) maps files (N) to commits (M):
    H[i, j] = 1 if file i was changed in commit j

From this we derive:
- Co-occurrence tensor: H @ H^T (weighted file-file adjacency)
- Commit similarity: H^T @ H (weighted commit-commit adjacency)
- Hypergraph Laplacian: D_v - H @ W @ D_e^{-1} @ H^T
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

import numpy as np
from scipy import sparse
from scipy.sparse.linalg import eigsh

logger = logging.getLogger(__name__)


@dataclass
class HypergraphResult:
    """Result of hypergraph analysis."""

    n_files: int
    n_commits: int  # hyperedges
    incidence: sparse.csr_matrix  # H: N × M
    file_paths: list[str]  # index → path
    commit_hashes: list[str]  # index → hash

    @property
    def co_occurrence(self) -> sparse.csr_matrix:
        """File-file co-occurrence matrix: H @ H^T.

        Entry (i,j) = number of commits where both files changed.
        Diagonal (i,i) = total commits touching file i.
        """
        return (self.incidence @ self.incidence.T).tocsr()

    @property
    def commit_similarity(self) -> sparse.csr_matrix:
        """Commit-commit similarity: H^T @ H.

        Entry (i,j) = number of files shared between commits i and j.
        """
        return (self.incidence.T @ self.incidence).tocsr()

    def hyperedge_sizes(self) -> np.ndarray:
        """Number of files changed per commit."""
        return np.array(self.incidence.sum(axis=0)).flatten()

    def file_degrees(self) -> np.ndarray:
        """Number of commits touching each file."""
        return np.array(self.incidence.sum(axis=1)).flatten()


def build_hypergraph(
    commits: list,
    file_set: set[str],
    max_files_per_commit: int = 50,
) -> HypergraphResult | None:
    """Build hypergraph incidence matrix from git commits.

    Args:
        commits: List of commit objects with .files and .hash attributes.
        file_set: Set of analyzed file paths (only include these).
        max_files_per_commit: Skip bulk commits touching more files.

    Returns:
        HypergraphResult or None if no valid commits.
    """
    if not commits or not file_set:
        return None

    # Build file index
    file_list = sorted(file_set)
    file_to_idx = {f: i for i, f in enumerate(file_list)}
    n_files = len(file_list)

    # Filter and index commits
    rows: list[int] = []
    cols: list[int] = []
    commit_hashes: list[str] = []
    commit_idx = 0

    for commit in commits:
        # Get files from commit (handle both list and tuple)
        files = list(commit.files) if hasattr(commit, "files") else []
        relevant = [f for f in files if f in file_to_idx]

        if not relevant or len(relevant) > max_files_per_commit:
            continue

        for f in relevant:
            rows.append(file_to_idx[f])
            cols.append(commit_idx)

        commit_hashes.append(commit.hash if hasattr(commit, "hash") else str(commit_idx))
        commit_idx += 1

    if commit_idx == 0:
        return None

    # Build sparse incidence matrix
    data = np.ones(len(rows), dtype=np.float32)
    H = sparse.csr_matrix(
        (data, (rows, cols)),
        shape=(n_files, commit_idx),
        dtype=np.float32,
    )

    return HypergraphResult(
        n_files=n_files,
        n_commits=commit_idx,
        incidence=H,
        file_paths=file_list,
        commit_hashes=commit_hashes,
    )


def hypergraph_laplacian_spectrum(
    result: HypergraphResult,
    k: int = 10,
) -> dict | None:
    """Compute spectrum of the hypergraph Laplacian.

    The normalized hypergraph Laplacian:
        L = I - D_v^{-1/2} @ H @ W @ D_e^{-1} @ H^T @ D_v^{-1/2}

    Where:
        D_v = diagonal vertex degree matrix
        D_e = diagonal hyperedge degree matrix
        W = hyperedge weight matrix (identity for unweighted)

    Returns:
        Dict with eigenvalues, fiedler_value, spectral_gap, or None.
    """
    H = result.incidence
    n = result.n_files

    if n < 3:
        return None

    try:
        # Vertex degrees
        d_v = np.array(H.sum(axis=1)).flatten()
        d_v = np.maximum(d_v, 1e-10)  # avoid division by zero

        # Hyperedge degrees
        d_e = np.array(H.sum(axis=0)).flatten()
        d_e = np.maximum(d_e, 1e-10)

        # D_v^{-1/2}
        d_v_inv_sqrt = sparse.diags(1.0 / np.sqrt(d_v))

        # D_e^{-1}
        d_e_inv = sparse.diags(1.0 / d_e)

        # Normalized Laplacian: L = I - D_v^{-1/2} H D_e^{-1} H^T D_v^{-1/2}
        theta = d_v_inv_sqrt @ H @ d_e_inv @ H.T @ d_v_inv_sqrt
        L = sparse.eye(n) - theta

        k_actual = min(k, n - 2)
        if k_actual < 2:
            return None

        eigenvalues = eigsh(L.astype(np.float64), k=k_actual, which="SM", return_eigenvectors=False)
        eigenvalues = np.sort(np.real(eigenvalues))

        return {
            "eigenvalues": [float(e) for e in eigenvalues],
            "fiedler_value": float(eigenvalues[1]) if len(eigenvalues) > 1 else 0.0,
            "spectral_gap": float(eigenvalues[2] - eigenvalues[1]) if len(eigenvalues) > 2 else 0.0,
            "n_files": n,
            "n_commits": result.n_commits,
        }

    except Exception as e:
        logger.warning(f"Hypergraph Laplacian computation failed: {e}")
        return None
