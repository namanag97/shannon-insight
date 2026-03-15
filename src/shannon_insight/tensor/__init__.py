"""4D Relationship Tensor for codebase analysis."""
from .core import RelationTensor, IMPORT, COCHANGE, AUTHOR, SEMANTIC, COMBINED, RELATION_NAMES
from .index import NodeIndex
from .persistence import save_tensor, load_tensor, tensor_exists

__all__ = [
    "RelationTensor", "NodeIndex",
    "IMPORT", "COCHANGE", "AUTHOR", "SEMANTIC", "COMBINED", "RELATION_NAMES",
    "save_tensor", "load_tensor", "tensor_exists",
]
