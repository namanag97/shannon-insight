"""Cognitive load using Gini-enhanced formula with compression fallback."""

from pathlib import Path
from typing import Dict, List

from ..base import PrimitivePlugin
from ...models import FileMetrics
from ...math import Compression, Gini


class CognitiveLoadPrimitive(PrimitivePlugin):
    name = "cognitive_load"
    display_name = "Cognitive Load"
    short_name = "cog.load"
    description = "Mental effort to understand (Gini-enhanced)"
    direction = "high_is_bad"
    default_weight = 0.20

    def compute(self, files: List[FileMetrics], root_dir: Path) -> Dict[str, float]:
        loads: Dict[str, float] = {}

        for file in files:
            concepts = file.functions + file.structs + file.interfaces
            nesting_factor = 1 + file.nesting_depth / 10

            if concepts > 0:
                base_load = concepts * file.complexity_score * nesting_factor
            else:
                file_path = root_dir / file.path if not Path(file.path).is_absolute() else Path(file.path)
                try:
                    with open(file_path, 'rb') as f:
                        raw = f.read()
                    ratio = Compression.compression_ratio(raw)
                except Exception:
                    ratio = 0.0
                base_load = ratio * (file.lines / 100.0) * file.complexity_score * nesting_factor

            if file.function_sizes and len(file.function_sizes) > 1:
                try:
                    gini = Gini.gini_coefficient(file.function_sizes)
                except ValueError:
                    gini = 0.0
                concentration = 1.0 + gini
            else:
                concentration = 1.0

            loads[file.path] = base_load * concentration

        if loads:
            mx = max(loads.values())
            if mx > 0:
                loads = {k: v / mx for k, v in loads.items()}

        return loads

    def interpret(self, v: float) -> str:
        if v > 0.6:
            return "high = hard to understand"
        return "within typical range"
