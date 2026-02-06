"""Structural entropy via compression ratio."""

from pathlib import Path
from typing import Dict, List

from ...math import Compression
from ...scanning.models import FileMetrics
from ..base import PrimitivePlugin


class CompressionPrimitive(PrimitivePlugin):
    name = "structural_entropy"
    display_name = "Compression Complexity"
    short_name = "compress"
    description = "Compression-based complexity (Kolmogorov approximation)"
    direction = "both_extreme_bad"
    default_weight = 0.20

    def compute(self, files: List[FileMetrics], root_dir: Path) -> Dict[str, float]:
        result = {}
        for file in files:
            file_path = (
                root_dir / file.path if not Path(file.path).is_absolute() else Path(file.path)
            )
            try:
                with open(file_path, "rb") as f:
                    content = f.read()
                result[file.path] = Compression.compression_ratio(content)
            except Exception:
                result[file.path] = 0.0
        return result

    def interpret(self, v: float) -> str:
        if v < 0.20:
            return "highly repetitive (duplication?)"
        elif v < 0.45:
            return "normal complexity"
        elif v < 0.65:
            return "dense/complex"
        return "very dense"
