"""Tensor persistence — save/load RelationTensor to disk."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

from scipy import sparse

if TYPE_CHECKING:
    from .core import RelationTensor

TENSOR_DIR = ".shannon/tensor"


def save_tensor(tensor: RelationTensor, root: Path) -> Path:
    """
    Save tensor to disk under root/.shannon/tensor/.

    Layout:
        .shannon/tensor/
        ├── metadata.json      # n_files, n_windows, n_relations, node_index
        ├── slice_0_0.npz      # CSR matrix for (t=0, r=0)
        ├── slice_0_1.npz      # CSR matrix for (t=0, r=1)
        └── ...

    Returns path to tensor directory.
    """
    tensor_dir = root / TENSOR_DIR
    tensor_dir.mkdir(parents=True, exist_ok=True)

    # Save metadata + node index
    metadata = {
        "n_files": tensor.n_files,
        "n_windows": tensor.n_windows,
        "n_relations": tensor.n_relations,
        "n_nodes": tensor.n_nodes,
        "n_edges": tensor.n_edges,
        "node_index": tensor._node_to_idx,  # {path: int}
    }
    (tensor_dir / "metadata.json").write_text(json.dumps(metadata, indent=2))

    # Save each non-empty slice as npz
    # First clean up old slices
    for old in tensor_dir.glob("slice_*.npz"):
        old.unlink()

    for (t, r), matrix in tensor._slices.items():
        if matrix.nnz > 0:
            sparse.save_npz(tensor_dir / f"slice_{t}_{r}.npz", matrix)

    return tensor_dir


def load_tensor(root: Path) -> RelationTensor:
    """
    Load tensor from disk.

    Returns a finalized RelationTensor.
    """
    from .core import RelationTensor

    tensor_dir = root / TENSOR_DIR
    if not tensor_dir.exists():
        raise FileNotFoundError(f"No tensor data at {tensor_dir}")

    # Load metadata
    metadata = json.loads((tensor_dir / "metadata.json").read_text())

    tensor = RelationTensor(
        n_files=metadata["n_files"],
        n_windows=metadata["n_windows"],
        n_relations=metadata["n_relations"],
    )

    # Restore node index
    for path, idx in metadata["node_index"].items():
        tensor._node_to_idx[path] = idx
        tensor._idx_to_node[idx] = path

    # Load slices
    for npz_file in sorted(tensor_dir.glob("slice_*.npz")):
        # Parse t, r from filename: slice_0_1.npz -> (0, 1)
        parts = npz_file.stem.split("_")
        t, r = int(parts[1]), int(parts[2])
        tensor._slices[(t, r)] = sparse.load_npz(npz_file)

    tensor._finalized = True
    return tensor


def tensor_exists(root: Path) -> bool:
    """Check if saved tensor data exists."""
    return (root / TENSOR_DIR / "metadata.json").exists()
