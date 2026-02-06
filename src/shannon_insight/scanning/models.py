"""Data models for the scanning layer."""

from collections import Counter
from dataclasses import dataclass, field
from typing import List


@dataclass
class FileMetrics:
    """Raw observations for a single file"""

    path: str
    lines: int
    tokens: int
    imports: List[str]
    exports: List[str]
    functions: int
    interfaces: int
    structs: int
    complexity_score: float
    nesting_depth: int
    ast_node_types: Counter
    last_modified: float
    function_sizes: List[int] = field(default_factory=list)
