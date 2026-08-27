"""Supra-adjacency matrix for multi-layer spectral analysis.

Constructs the block supra-adjacency matrix:

    M_supra = [
        G_0     ωI      ωI      ...
        ωI      G_1     ωI      ...
        ωI      ωI      G_2     ...
        ...     ...     ...     ...
    ]

Where G_r are per-layer adjacency matrices and ωI are inter-layer
coupling matrices (same node across layers connected with weight ω).

Multi-layer spectral analysis on M_supra reveals:
- Multi-layer modularity (communities spanning all relation types)
- Cross-layer Fiedler value (algebraic connectivity across layers)
- Layer interdependence structure
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

import numpy as np
from scipy import sparse
from scipy.sparse.linalg import eigsh

from .core import COMBINED, RELATION_NAMES, RelationTensor

logger = logging.getLogger(__name__)


@dataclass
class SupraSpectralResult:
    """Result of spectral analysis on the supra-adjacency matrix."""

    fiedler_value: float  # algebraic connectivity across all layers
    spectral_gap: float  # λ₃ - λ₂
    eigenvalues: list[float]  # smallest k eigenvalues
    supra_size: int  # R*N
    n_layers: int  # R (number of layers included)
    layer_participation: dict[str, float]  # how much each layer contributes to Fiedler vector


def build_supra_adjacency(
    tensor: RelationTensor,
    t: int = -1,
    omega: float = 0.1,
    exclude_combined: bool = True,
) -> sparse.csr_matrix:
    """Build the supra-adjacency matrix from the tensor.

    Args:
        tensor: RelationTensor with finalized slices.
        t: Time window (-1 for latest).
        omega: Inter-layer coupling weight.
        exclude_combined: Whether to exclude the COMBINED layer
            (since it's derived from other layers).

    Returns:
        Sparse CSR supra-adjacency matrix of shape (R*N, R*N).
    """
    if t == -1:
        t = tensor.n_windows - 1

    n = tensor.n_nodes
    if n < 2:
        return sparse.csr_matrix((0, 0))

    # Determine which layers to include
    layers = list(range(tensor.n_relations))
    if exclude_combined:
        layers = [r for r in layers if r != COMBINED]
    n_layers = len(layers)

    supra_n = n_layers * n
    blocks: list[list[sparse.csr_matrix | None]] = [[None] * n_layers for _ in range(n_layers)]

    identity = sparse.eye(n, dtype=np.float32, format="csr")
    omega_identity = omega * identity

    for i, r_i in enumerate(layers):
        for j, r_j in enumerate(layers):
            if i == j:
                # Diagonal block: the actual adjacency matrix for this layer
                blocks[i][j] = tensor.slice(t, r_i).astype(np.float32)
            else:
                # Off-diagonal: inter-layer coupling (same node across layers)
                blocks[i][j] = omega_identity

    return sparse.bmat(blocks, format="csr")


def supra_spectral_analysis(
    tensor: RelationTensor,
    t: int = -1,
    omega: float = 0.1,
    k: int = 10,
    exclude_combined: bool = True,
) -> SupraSpectralResult | None:
    """Spectral analysis on the supra-adjacency matrix.

    Computes Fiedler value and spectral gap across all layers simultaneously,
    revealing multi-layer connectivity structure.

    Args:
        tensor: RelationTensor.
        t: Time window.
        omega: Inter-layer coupling weight.
        k: Number of smallest eigenvalues to compute.
        exclude_combined: Exclude the derived COMBINED layer.

    Returns:
        SupraSpectralResult or None if computation fails.
    """
    n = tensor.n_nodes
    if n < 3:
        return None

    try:
        M = build_supra_adjacency(tensor, t, omega, exclude_combined)
        supra_n = M.shape[0]

        if supra_n < 3:
            return None

        # Build Laplacian: L = D - M
        degrees = np.array(M.sum(axis=1)).flatten()
        D = sparse.diags(degrees, format="csr")
        L = D - M

        # Compute smallest eigenvalues
        k_actual = min(k, supra_n - 2)
        if k_actual < 2:
            return None

        eigenvalues, eigenvectors = eigsh(L.astype(np.float64), k=k_actual, which="SM")
        eigenvalues = np.sort(np.real(eigenvalues))

        # Fiedler value = λ₂
        fiedler = float(eigenvalues[1]) if len(eigenvalues) > 1 else 0.0

        # Spectral gap = λ₃ - λ₂
        spectral_gap = float(eigenvalues[2] - eigenvalues[1]) if len(eigenvalues) > 2 else 0.0

        # Layer participation: how much of the Fiedler vector
        # is concentrated in each layer
        layers = list(range(tensor.n_relations))
        if exclude_combined:
            layers = [r for r in layers if r != COMBINED]

        fiedler_vec = eigenvectors[:, 1] if eigenvectors.shape[1] > 1 else np.zeros(supra_n)
        layer_participation = {}
        for i, r in enumerate(layers):
            segment = fiedler_vec[i * n : (i + 1) * n]
            energy = float(np.sum(segment**2))
            total_energy = float(np.sum(fiedler_vec**2)) or 1.0
            name = RELATION_NAMES[r] if r < len(RELATION_NAMES) else f"LAYER_{r}"
            layer_participation[name] = energy / total_energy

        return SupraSpectralResult(
            fiedler_value=fiedler,
            spectral_gap=spectral_gap,
            eigenvalues=[float(e) for e in eigenvalues],
            supra_size=supra_n,
            n_layers=len(layers),
            layer_participation=layer_participation,
        )

    except Exception as e:
        logger.warning(f"Supra spectral analysis failed: {e}")
        return None
