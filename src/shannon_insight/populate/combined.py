"""Populate COMBINED layer (R=4)."""
from __future__ import annotations

from ..tensor.core import RelationTensor, IMPORT, COCHANGE, AUTHOR, SEMANTIC, COMBINED


def populate_combined(
    tensor: RelationTensor,
    weights: tuple[float, float, float, float] = (0.4, 0.3, 0.2, 0.1),
):
    """Fill T[:,:,t,COMBINED] as weighted sum of other layers.

    NOTE: Directly writes to tensor._slices (internal API) because the tensor
    is already finalized at this point and add_edge() is blocked. This is a
    known design issue — see FRESH-BUILD.md externalities.
    """
    tensor.finalize()  # Ensure slices are built

    w_import, w_cochange, w_author, w_semantic = weights

    for t in range(tensor.n_windows):
        # Get all slices
        A_import = tensor.slice(t, IMPORT)
        A_cochange = tensor.slice(t, COCHANGE)
        A_author = tensor.slice(t, AUTHOR)
        A_semantic = tensor.slice(t, SEMANTIC)

        # Weighted sum (sparse)
        A_combined = (
            w_import * A_import
            + w_cochange * A_cochange
            + w_author * A_author
            + w_semantic * A_semantic
        )

        # Store directly (bypasses add_edge since tensor is finalized)
        tensor._slices[(t, COMBINED)] = A_combined.tocsr()
