"""Populate COMBINED layer as weighted sum of the other 5 layers.

Default weights: 0.35*IMPORT + 0.25*COCHANGE + 0.15*AUTHOR + 0.10*SEMANTIC + 0.15*CLONE.
Calls ``tensor.finalize()`` first to build CSR matrices, then writes the
combined result directly into ``tensor._slices``.
"""

from __future__ import annotations

from typing import Any

from ..tensor.core import AUTHOR, CLONE, COCHANGE, COMBINED, IMPORT, SEMANTIC


def populate_combined(
    tensor: Any,
    weights: tuple[float, float, float, float, float] = (0.35, 0.25, 0.15, 0.10, 0.15),
) -> None:
    """Fill T[:,:,t,COMBINED] as weighted sum of other layers.

    Args:
        tensor: A ``RelationTensor`` instance.  ``finalize()`` is called
            automatically if the tensor has not yet been finalized.
        weights: ``(w_import, w_cochange, w_author, w_semantic, w_clone)`` —
            must sum to 1.0 for a proper convex combination, but this is
            not enforced.
    """
    tensor.finalize()  # ensure CSR slices are built

    w_import, w_cochange, w_author, w_semantic, w_clone = weights

    for t in range(tensor.n_windows):
        # Fetch the five base-layer slices
        a_import = tensor.slice(t, IMPORT)
        a_cochange = tensor.slice(t, COCHANGE)
        a_author = tensor.slice(t, AUTHOR)
        a_semantic = tensor.slice(t, SEMANTIC)
        a_clone = tensor.slice(t, CLONE)

        # Weighted linear combination (sparse arithmetic)
        a_combined = (
            w_import * a_import
            + w_cochange * a_cochange
            + w_author * a_author
            + w_semantic * a_semantic
            + w_clone * a_clone
        )

        # Store directly — the tensor is finalized so add_edge() is blocked
        tensor._slices[(t, COMBINED)] = a_combined.tocsr()
