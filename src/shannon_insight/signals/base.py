"""Base class for primitive plugins."""

from abc import ABC, abstractmethod
from pathlib import Path

from ..scanning.models import FileMetrics


class PrimitivePlugin(ABC):
    name: str
    display_name: str
    short_name: str
    description: str
    direction: str  # "high_is_bad" | "low_is_bad" | "both_extreme_bad"
    default_weight: float

    @abstractmethod
    def compute(self, files: list[FileMetrics], root_dir: Path) -> dict[str, float]: ...

    @abstractmethod
    def interpret(self, value: float) -> str: ...
