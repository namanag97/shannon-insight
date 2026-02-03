"""Python language analyzer"""

import re
from pathlib import Path
from collections import Counter
from typing import List, Optional

from .base import BaseScanner
from ..models import FileMetrics
from ..config import AnalysisSettings
from ..exceptions import FileAccessError
from ..logging_config import get_logger

logger = get_logger(__name__)


class PythonScanner(BaseScanner):
    """Scanner optimized for Python codebases"""

    def __init__(self, root_dir: str, settings: Optional[AnalysisSettings] = None):
        super().__init__(root_dir, extensions=[".py"], settings=settings)

    def _should_skip(self, filepath: Path) -> bool:
        """Skip test files, venv, and other non-project directories"""
        path_str = str(filepath)
        skip_dirs = (
            "venv", ".venv", "__pycache__", ".git", ".tox",
            ".mypy_cache", ".pytest_cache", "node_modules",
            "dist", "build", ".eggs", "*.egg-info",
        )
        skip_files = ("setup.py", "conftest.py")
        name = filepath.name
        return (
            any(d in path_str for d in skip_dirs)
            or name in skip_files
            or name.startswith("test_")
            or name.endswith("_test.py")
        )

    def _analyze_file(self, filepath: Path) -> FileMetrics:
        """Extract all metrics from a Python file"""
        try:
            with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
        except OSError as e:
            raise FileAccessError(filepath, f"Cannot read file: {e}")
        except Exception as e:
            raise FileAccessError(filepath, f"Unexpected error: {e}")

        lines = content.split("\n")

        return FileMetrics(
            path=str(filepath.relative_to(self.root_dir)),
            lines=len(lines),
            tokens=self._count_tokens(content),
            imports=self._extract_imports(content),
            exports=self._extract_exports(content),
            functions=self._count_functions(content),
            interfaces=0,  # Python doesn't have interfaces
            structs=self._count_classes(content),
            complexity_score=self._estimate_complexity(content),
            nesting_depth=self._max_nesting_depth_python(content),
            ast_node_types=self._extract_ast_node_types(content),
            last_modified=filepath.stat().st_mtime,
        )

    def _count_tokens(self, content: str) -> int:
        """Approximate token count for Python"""
        # Remove comments and strings
        content = re.sub(r"#.*", "", content)
        content = re.sub(r'""".*?"""', "", content, flags=re.DOTALL)
        content = re.sub(r"'''.*?'''", "", content, flags=re.DOTALL)
        content = re.sub(r'"[^"]*"', "", content)
        content = re.sub(r"'[^']*'", "", content)

        tokens = re.findall(r"\w+|[{}()\[\];,.:@]", content)
        return len(tokens)

    def _extract_imports(self, content: str) -> List[str]:
        """Extract Python import statements"""
        imports = []

        # import X
        for match in re.finditer(r"^import\s+(\S+)", content, re.MULTILINE):
            imports.append(match.group(1))

        # from X import Y
        for match in re.finditer(r"^from\s+(\S+)\s+import", content, re.MULTILINE):
            imports.append(match.group(1))

        return imports

    def _extract_exports(self, content: str) -> List[str]:
        """Extract public identifiers (no leading underscore)"""
        exports = []

        # Public functions: def name(
        exports.extend(
            re.findall(r"^def\s+([a-zA-Z]\w*)\s*\(", content, re.MULTILINE)
        )

        # Public classes: class Name
        exports.extend(
            re.findall(r"^class\s+([a-zA-Z]\w*)", content, re.MULTILINE)
        )

        # __all__ list
        match = re.search(r"__all__\s*=\s*\[([^\]]+)\]", content, re.DOTALL)
        if match:
            items = re.findall(r'["\'](\w+)["\']', match.group(1))
            exports.extend(items)

        return exports

    def _count_functions(self, content: str) -> int:
        """Count function and method definitions"""
        return len(re.findall(r"^\s*def\s+\w+\s*\(", content, re.MULTILINE))

    def _count_classes(self, content: str) -> int:
        """Count class definitions"""
        return len(re.findall(r"^class\s+\w+", content, re.MULTILINE))

    def _estimate_complexity(self, content: str) -> float:
        """Estimate cyclomatic complexity for Python"""
        complexity = 1

        complexity += len(re.findall(r"\bif\s+", content))
        complexity += len(re.findall(r"\belif\s+", content))
        complexity += len(re.findall(r"\belse\s*:", content))
        complexity += len(re.findall(r"\bfor\s+", content))
        complexity += len(re.findall(r"\bwhile\s+", content))
        complexity += len(re.findall(r"\bexcept\s*", content))
        complexity += len(re.findall(r"\band\b", content))
        complexity += len(re.findall(r"\bor\b", content))
        complexity += len(re.findall(r"\bwith\s+", content))

        return complexity

    def _max_nesting_depth_python(self, content: str) -> int:
        """Calculate max indentation depth for Python (indent-based)"""
        max_depth = 0
        for line in content.split("\n"):
            stripped = line.lstrip()
            if not stripped or stripped.startswith("#"):
                continue
            indent = len(line) - len(stripped)
            # Python standard is 4 spaces per level
            depth = indent // 4
            max_depth = max(max_depth, depth)
        return max_depth

    def _extract_ast_node_types(self, content: str) -> Counter:
        """Extract distribution of AST node types for Python"""
        node_types = Counter()

        node_types["function"] = self._count_functions(content)
        node_types["class"] = self._count_classes(content)
        node_types["import"] = len(self._extract_imports(content))
        node_types["export"] = len(self._extract_exports(content))
        node_types["if"] = len(re.findall(r"\bif\s+", content))
        node_types["for"] = len(re.findall(r"\bfor\s+", content))
        node_types["while"] = len(re.findall(r"\bwhile\s+", content))
        node_types["return"] = len(re.findall(r"\breturn\b", content))
        node_types["yield"] = len(re.findall(r"\byield\b", content))
        node_types["with"] = len(re.findall(r"\bwith\s+", content))
        node_types["try"] = len(re.findall(r"\btry\s*:", content))
        node_types["decorator"] = len(re.findall(r"^\s*@\w+", content, re.MULTILINE))

        return node_types
