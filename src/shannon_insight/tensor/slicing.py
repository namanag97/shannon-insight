"""Tensor slice utilities."""
from __future__ import annotations

from scipy import sparse
from .core import RelationTensor


def sum_over_time(tensor: RelationTensor, r: int) -> sparse.csr_matrix:
    """Sum all time windows for a given relation type."""
    slices = tensor.slice_all_time(r)
    if not slices:
        return sparse.csr_matrix((tensor.n_nodes, tensor.n_nodes))
    result = slices[0].copy()
    for s in slices[1:]:
        result = result + s
    return result.tocsr()


def sum_over_relations(tensor: RelationTensor, t: int) -> sparse.csr_matrix:
    """Sum all relation types for a given time window."""
    slices = tensor.slice_all_relations(t)
    if not slices:
        return sparse.csr_matrix((tensor.n_nodes, tensor.n_nodes))
    result = slices[0].copy()
    for s in slices[1:]:
        result = result + s
    return result.tocsr()
