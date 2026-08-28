"""Tensor decomposition — CP/PARAFAC and Tucker for community/temporal discovery.

CP decomposition on the relation tensor discovers:
- Factor A (N x R): file community membership
- Factor B (N x R): file community membership (target)
- Factor C (K x R): temporal activity pattern per community
- Factor D (n_rel x R): which relation types define each community

Tucker decomposition captures cross-mode interactions via a core tensor.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

import numpy as np

from .core import RELATION_NAMES, RelationTensor

logger = logging.getLogger(__name__)


@dataclass
class CPResult:
    """Result of CP/PARAFAC decomposition."""

    rank: int
    weights: np.ndarray  # (R,) — component weights
    factors: list[np.ndarray]  # [A(N,R), B(N,R), C(K,R), D(n_rel,R)]
    reconstruction_error: float = 0.0

    @property
    def file_communities(self) -> np.ndarray:
        """File community membership (N x R). Average of source/target factors."""
        return np.asarray((self.factors[0] + self.factors[1]) / 2.0)

    @property
    def temporal_patterns(self) -> np.ndarray:
        """Temporal activity patterns (K x R)."""
        return self.factors[2]

    @property
    def relation_importance(self) -> np.ndarray:
        """Which relation types matter for each component (n_rel x R)."""
        return self.factors[3]

    def dominant_community(self) -> dict[int, int]:
        """Map each file index to its dominant community."""
        communities = self.file_communities
        return {i: int(np.argmax(communities[i])) for i in range(communities.shape[0])}

    def community_summary(self, tensor: RelationTensor) -> list[dict]:
        """Summarize each discovered community."""
        communities = self.file_communities
        temporal = self.temporal_patterns
        rel_imp = self.relation_importance

        summaries = []
        for r in range(self.rank):
            # Top files in this community
            scores = communities[:, r]
            top_indices = np.argsort(-scores)[:10]
            top_files = []
            for idx in top_indices:
                if scores[idx] > 0.01:
                    top_files.append(
                        {
                            "path": tensor.node_path(int(idx)),
                            "membership": float(scores[idx]),
                        }
                    )

            # Dominant relation type
            rel_scores = rel_imp[:, r]
            dominant_rel = (
                RELATION_NAMES[int(np.argmax(rel_scores))] if len(rel_scores) > 0 else "UNKNOWN"
            )

            # Temporal trend (slope of activity)
            t_vals = temporal[:, r]
            if len(t_vals) > 1:
                xs = np.arange(len(t_vals), dtype=float)
                trend = float(np.polyfit(xs, t_vals, 1)[0])
            else:
                trend = 0.0

            summaries.append(
                {
                    "component": r,
                    "weight": float(self.weights[r]),
                    "n_files": len(top_files),
                    "top_files": top_files,
                    "dominant_relation": dominant_rel,
                    "temporal_trend": trend,
                    "activity_pattern": t_vals.tolist(),
                }
            )

        return summaries


@dataclass
class TuckerResult:
    """Result of Tucker decomposition."""

    core: np.ndarray  # (R1, R2, R3, R4) core tensor
    factors: list[np.ndarray]  # [A(N,R1), B(N,R2), C(K,R3), D(n_rel,R4)]
    reconstruction_error: float = 0.0

    @property
    def cross_mode_interactions(self) -> np.ndarray:
        """Core tensor capturing cross-mode interactions."""
        return self.core


def _to_dense_4d(tensor: RelationTensor) -> np.ndarray:
    """Convert RelationTensor to dense 4D numpy array for decomposition.

    For tensors with many nodes, this can be memory-intensive.
    Only called when n_nodes is manageable (< 2000).
    """
    n = tensor.n_nodes
    k = tensor.n_windows
    r_count = tensor.n_relations
    T = np.zeros((n, n, k, r_count), dtype=np.float32)

    for (t, r), matrix in tensor._slices.items():
        T[:, :, t, r] = matrix.toarray()

    return T


def cp_decomposition(
    tensor: RelationTensor,
    rank: int = 5,
    max_iter: int = 100,
    tol: float = 1e-6,
) -> CPResult | None:
    """CP/PARAFAC decomposition of the relation tensor.

    Decomposes T ≈ Σᵣ wᵣ · aᵣ ⊗ bᵣ ⊗ cᵣ ⊗ dᵣ

    Uses Alternating Least Squares (ALS) with non-negativity constraint.

    Args:
        tensor: RelationTensor to decompose.
        rank: Number of components (communities to discover).
        max_iter: Maximum ALS iterations.
        tol: Convergence tolerance.

    Returns:
        CPResult or None if decomposition fails.
    """
    n = tensor.n_nodes
    k = tensor.n_windows
    n_rel = tensor.n_relations

    if n < 2 or tensor.n_edges == 0:
        logger.info("Tensor too small or empty for CP decomposition")
        return None

    if n > 2000:
        logger.warning(
            f"Tensor has {n} nodes — CP decomposition on dense 4D array "
            f"would require {n * n * k * n_rel * 4 / (1024**3):.1f} GB. Skipping."
        )
        return None

    try:
        T = _to_dense_4d(tensor)

        # ALS with non-negativity
        rng = np.random.default_rng(42)
        A = np.abs(rng.standard_normal((n, rank)).astype(np.float32))
        B = np.abs(rng.standard_normal((n, rank)).astype(np.float32))
        C = np.abs(rng.standard_normal((k, rank)).astype(np.float32))
        D = np.abs(rng.standard_normal((n_rel, rank)).astype(np.float32))

        prev_error = float("inf")

        for iteration in range(max_iter):
            # Update A: unfold mode-0, solve A * khatri_rao(D,C,B)^T = T_(0)
            A = _als_update_nonneg(T, [A, B, C, D], mode=0)
            B = _als_update_nonneg(T, [A, B, C, D], mode=1)
            C = _als_update_nonneg(T, [A, B, C, D], mode=2)
            D = _als_update_nonneg(T, [A, B, C, D], mode=3)

            # Check convergence
            T_approx = _reconstruct_cp([A, B, C, D])
            denominator = max(float(np.linalg.norm(T)), 1e-10)
            error = float(np.linalg.norm(T - T_approx)) / denominator

            if abs(prev_error - error) < tol:
                logger.debug(f"CP converged at iteration {iteration}, error={error:.6f}")
                break
            prev_error = error

        # Normalize: absorb magnitudes into weights
        weights = np.ones(rank, dtype=np.float32)
        for factor in [A, B, C, D]:
            norms = np.linalg.norm(factor, axis=0)
            norms = np.maximum(norms, 1e-10)
            weights *= norms
            factor /= norms

        return CPResult(
            rank=rank,
            weights=weights,
            factors=[A, B, C, D],
            reconstruction_error=prev_error,
        )

    except Exception as e:
        logger.warning(f"CP decomposition failed: {e}")
        return None


def tucker_decomposition(
    tensor: RelationTensor,
    ranks: tuple[int, int, int, int] = (5, 5, 5, 5),
    max_iter: int = 50,
    tol: float = 1e-6,
) -> TuckerResult | None:
    """Tucker decomposition of the relation tensor.

    Decomposes T ≈ G ×₁ A ×₂ B ×₃ C ×₄ D

    where G is the core tensor capturing cross-mode interactions.

    Args:
        tensor: RelationTensor to decompose.
        ranks: (R1, R2, R3, R4) ranks for each mode.
        max_iter: Maximum HOSVD iterations.
        tol: Convergence tolerance.

    Returns:
        TuckerResult or None if decomposition fails.
    """
    n = tensor.n_nodes
    k = tensor.n_windows
    n_rel = tensor.n_relations

    if n < 2 or tensor.n_edges == 0:
        return None

    # Clamp ranks to tensor dimensions
    ranks = (
        min(ranks[0], n),
        min(ranks[1], n),
        min(ranks[2], k),
        min(ranks[3], n_rel),
    )

    if n > 2000:
        logger.warning(f"Tensor has {n} nodes — too large for dense Tucker. Skipping.")
        return None

    try:
        T = _to_dense_4d(tensor)

        # Higher-Order SVD (HOSVD) — truncated SVD on each unfolding
        factors = []
        for mode in range(4):
            unfolded = _unfold(T, mode)
            U, _, _ = np.linalg.svd(unfolded, full_matrices=False)
            factors.append(U[:, : ranks[mode]].astype(np.float32))

        # Core tensor: G = T ×₁ A^T ×₂ B^T ×₃ C^T ×₄ D^T
        core = T.copy()
        for mode in range(4):
            core = _mode_dot(core, factors[mode].T, mode)

        # Reconstruction error
        T_approx = core.copy()
        for mode in range(4):
            T_approx = _mode_dot(T_approx, factors[mode], mode)
        denominator = max(float(np.linalg.norm(T)), 1e-10)
        error = float(np.linalg.norm(T - T_approx)) / denominator

        return TuckerResult(
            core=core.astype(np.float32),
            factors=factors,
            reconstruction_error=error,
        )

    except Exception as e:
        logger.warning(f"Tucker decomposition failed: {e}")
        return None


# ── Helper functions ──


def _unfold(T: np.ndarray, mode: int) -> np.ndarray:
    """Mode-n unfolding of a tensor."""
    return np.moveaxis(T, mode, 0).reshape(T.shape[mode], -1)


def _mode_dot(T: np.ndarray, M: np.ndarray, mode: int) -> np.ndarray:
    """Mode-n product: T ×ₙ M."""
    return np.moveaxis(
        np.tensordot(M, np.moveaxis(T, mode, 0), axes=([1], [0])),
        0,
        mode,
    )


def _khatri_rao(matrices: list[np.ndarray]) -> np.ndarray:
    """Column-wise Khatri-Rao product of a list of matrices."""
    result = matrices[0]
    for M in matrices[1:]:
        r = result.shape[1]
        result = np.einsum("ir,jr->ijr", result, M).reshape(-1, r)
    return result


def _reconstruct_cp(factors: list[np.ndarray]) -> np.ndarray:
    """Reconstruct tensor from CP factors."""
    rank = factors[0].shape[1]
    shape = tuple(f.shape[0] for f in factors)
    T = np.zeros(shape, dtype=np.float32)
    for r in range(rank):
        component = factors[0][:, r]
        for f in factors[1:]:
            component = np.multiply.outer(component, f[:, r])
        T += component
    return T


def _als_update_nonneg(
    T: np.ndarray,
    factors: list[np.ndarray],
    mode: int,
) -> np.ndarray:
    """ALS update for one mode with non-negativity projection."""
    n_modes = len(factors)
    rank = factors[0].shape[1]

    # Build Khatri-Rao product of all factors except current mode
    other_factors = [factors[i] for i in range(n_modes) if i != mode]
    kr = _khatri_rao(other_factors)

    # Unfold tensor along mode
    T_unf = _unfold(T, mode)

    # Solve: factor[mode] = T_(mode) @ kr @ inv(kr^T @ kr)
    gram = kr.T @ kr
    gram += 1e-8 * np.eye(rank)  # regularization
    rhs = T_unf @ kr
    new_factor = rhs @ np.linalg.inv(gram)

    # Non-negativity projection
    new_factor = np.asarray(np.maximum(new_factor, 0.0), dtype=np.float32)

    return new_factor
