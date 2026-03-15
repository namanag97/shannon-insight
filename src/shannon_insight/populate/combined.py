"""Populate COMBINED layer (R=4) as weighted sum of the other 4 layers.

Default weights: 0.4*IMPORT + 0.3*COCHANGE + 0.2*AUTHOR + 0.1*SEMANTIC.
Calls ``tensor.finalize()`` first to build CSR matrices, then writes the
combined result directly into ``tensor._slices``.
"""
from __future__ import annotations

from typing import Any

from ..tensor.core import IMPORT, COCHANGE, AUTHOR, SEMANTIC, COMBINED


def populate_combined(
    tensor: Any,
    weights: tuple[float, float, float, float] = (0.4, 0.3, 0.2, 0.1),
) -> None:
    """Fill T[:,:,t,COMBINED] as weighted sum of other layers.

    Args:
        tensor: A ``RelationTensor`` instance.  ``finalize()`` is called
            automatically if the tensor has not yet been finalized.
        weights: ``(w_import, w_cochange, w_author, w_semantic)`` — must
            sum to 1.0 for a proper convex combination, but this is not
            enforced.
    """
    tensor.finalize()  # ensure CSR slices are built

    w_import, w_cochange, w_author, w_semantic = weights

    for t in range(tensor.n_windows):
        # Fetch the four base-layer slices
        a_import = tensor.slice(t, IMPORT)
        a_cochange = tensor.slice(t, COCHANGE)
        a_author = tensor.slice(t, AUTHOR)
        a_semantic = tensor.slice(t, SEMANTIC)

        # Weighted linear combination (sparse arithmetic)
        a_combined = (
            w_import * a_import
            + w_cochange * a_cochange
            + w_author * a_author
            + w_semantic * a_semantic
        )

        # Store directly — the tensor is finalized so add_edge() is blocked
        tensor._slices[(t, COMBINED)] = a_combined.tocsr()
