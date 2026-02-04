"""Semantic coherence via identifier token analysis."""

from pathlib import Path
from typing import Dict, List

from ..base import PrimitivePlugin
from ...models import FileMetrics
from ...math import IdentifierAnalyzer


class CoherencePrimitive(PrimitivePlugin):
    name = "semantic_coherence"
    display_name = "Identifier Coherence"
    short_name = "coherence"
    description = "Responsibility focus (identifier clustering)"
    direction = "both_extreme_bad"
    default_weight = 0.15

    def compute(self, files: List[FileMetrics], root_dir: Path) -> Dict[str, float]:
        result = {}
        for file in files:
            file_path = root_dir / file.path if not Path(file.path).is_absolute() else Path(file.path)
            try:
                with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
                tokens = IdentifierAnalyzer.extract_identifier_tokens(content)
                result[file.path] = IdentifierAnalyzer.compute_coherence(tokens)
            except Exception:
                result[file.path] = 1.0
        return result

    def interpret(self, v: float) -> str:
        if v < 0.30:
            return "mixed responsibilities"
        elif v < 0.70:
            return "somewhat focused"
        return "highly focused"
