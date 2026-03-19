"""4D Relationship Tensor for codebase analysis."""

from .core import AUTHOR, CLONE, COCHANGE, COMBINED, IMPORT, RELATION_NAMES, SEMANTIC, RelationTensor
from .decomposition import CPResult, TuckerResult, cp_decomposition, tucker_decomposition
from .hypergraph import HypergraphResult, build_hypergraph, hypergraph_laplacian_spectrum
from .index import NodeIndex
from .persistence import load_tensor, save_tensor, tensor_exists
from .supra import SupraSpectralResult, build_supra_adjacency, supra_spectral_analysis

__all__ = [
    "RelationTensor",
    "NodeIndex",
    "IMPORT",
    "COCHANGE",
    "AUTHOR",
    "SEMANTIC",
    "CLONE",
    "COMBINED",
    "RELATION_NAMES",
    "save_tensor",
    "load_tensor",
    "tensor_exists",
    # Decomposition
    "cp_decomposition",
    "tucker_decomposition",
    "CPResult",
    "TuckerResult",
    # Supra-adjacency
    "build_supra_adjacency",
    "supra_spectral_analysis",
    "SupraSpectralResult",
    # Hypergraph
    "build_hypergraph",
    "hypergraph_laplacian_spectrum",
    "HypergraphResult",
]
