"""Base scanner class for language-agnostic functionality"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List
from ..models import FileMetrics


class BaseScanner(ABC):
    """Abstract base class for language-specific scanners"""

    def __init__(self, root_dir: str, extensions: List[str]):
        self.root_dir = Path(root_dir)
        self.extensions = extensions

    def scan(self) -> List[FileMetrics]:
        """Scan all source files and extract metrics"""
        files = []

        for ext in self.extensions:
            for filepath in self.root_dir.rglob(f"*{ext}"):
                if self._should_skip(filepath):
                    continue

                try:
                    metrics = self._analyze_file(filepath)
                    files.append(metrics)
                except Exception as e:
                    print(f"Error analyzing {filepath}: {e}")

        return files

    @abstractmethod
    def _should_skip(self, filepath: Path) -> bool:
        """Determine if file should be skipped (e.g., tests, vendor)"""
        pass

    @abstractmethod
    def _analyze_file(self, filepath: Path) -> FileMetrics:
        """Extract all metrics from a single file"""
        pass

    @abstractmethod
    def _count_tokens(self, content: str) -> int:
        """Count tokens in source code"""
        pass

    @abstractmethod
    def _extract_imports(self, content: str) -> List[str]:
        """Extract import statements"""
        pass

    @abstractmethod
    def _extract_exports(self, content: str) -> List[str]:
        """Extract exported identifiers"""
        pass

    @abstractmethod
    def _count_functions(self, content: str) -> int:
        """Count function declarations"""
        pass

    @abstractmethod
    def _estimate_complexity(self, content: str) -> float:
        """Estimate cyclomatic complexity"""
        pass

    def _max_nesting_depth(self, content: str) -> int:
        """Calculate maximum nesting depth (language-agnostic)"""
        max_depth = 0
        current_depth = 0

        for char in content:
            if char == "{":
                current_depth += 1
                max_depth = max(max_depth, current_depth)
            elif char == "}":
                current_depth -= 1

        return max_depth
