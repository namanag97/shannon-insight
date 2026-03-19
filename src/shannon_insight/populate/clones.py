"""Populate CLONE layer (R=4) from NCD clone detection.

Feeds detected clone pairs into the tensor as symmetric edges with
weight = 1 - NCD (higher = more similar).
"""

from __future__ import annotations

from typing import Any

from ..graph.clone_detection import ClonePair
from ..tensor.core import CLONE


def populate_clones(
    tensor: Any,
    clone_pairs: list[ClonePair],
) -> None:
    """Fill T[:,:,t,CLONE] with clone similarity weights.

    Args:
        tensor: A ``RelationTensor`` instance.
        clone_pairs: Detected clone pairs from NCD analysis.
    """
    if not clone_pairs:
        return

    t = tensor.n_windows - 1  # latest time window

    for pair in clone_pairs:
        # Weight = 1 - NCD (higher = more similar)
        weight = 1.0 - pair.ncd

        # Only add if both files are registered nodes
        if tensor.has_node(pair.file_a) and tensor.has_node(pair.file_b):
            # Symmetric: add both directions
            tensor.add_edge(pair.file_a, pair.file_b, t, CLONE, weight=weight)
            tensor.add_edge(pair.file_b, pair.file_a, t, CLONE, weight=weight)
