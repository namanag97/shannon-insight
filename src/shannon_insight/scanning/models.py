"""Data models for the scanning layer."""

from collections import Counter
from dataclasses import dataclass, field


@dataclass
class FileMetrics:
    """Raw observations for a single file"""

    path: str
    lines: int
    tokens: int
    imports: list[str]
    exports: list[str]
    functions: int
    interfaces: int
    structs: int
    complexity_score: float
    nesting_depth: int
    ast_node_types: Counter
    last_modified: float
    function_sizes: list[int] = field(default_factory=list)
