"""TypeScript/React analyzer"""

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


class TypeScriptScanner(BaseScanner):
    """Scanner optimized for TypeScript and React codebases"""

    def __init__(self, root_dir: str, settings: Optional[AnalysisSettings] = None):
        super().__init__(root_dir, extensions=[".ts", ".tsx", ".js", ".jsx"], settings=settings)

    def _should_skip(self, filepath: Path) -> bool:
        """Skip node_modules, dist, venv, and other non-project directories"""
        path_str = str(filepath)
        skip_dirs = ("node_modules", "dist", "build", "venv", ".venv", "__pycache__", ".git", ".tox", ".mypy_cache")
        return any(d in path_str for d in skip_dirs)

    def _analyze_file(self, filepath: Path) -> FileMetrics:
        """Extract all metrics from a TypeScript/React file"""
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
            interfaces=self._count_classes(content),  # Use classes for TypeScript
            structs=self._count_react_components(content),  # Repurpose for components
            complexity_score=self._estimate_complexity(content),
            nesting_depth=self._max_nesting_depth(content),
            ast_node_types=self._extract_ast_node_types(content),
            last_modified=filepath.stat().st_mtime,
            function_sizes=self._extract_function_sizes(content),
        )

    def _count_tokens(self, content: str) -> int:
        """Approximate token count for TypeScript"""
        # Remove comments and strings
        content = re.sub(r"//.*", "", content)
        content = re.sub(r"/\*.*?\*/", "", content, flags=re.DOTALL)
        content = re.sub(r'["\'].*?["\']', "", content)

        # Split on whitespace and common operators
        tokens = re.findall(r"\w+|[{}()\[\];,.]", content)
        return len(tokens)

    def _extract_imports(self, content: str) -> List[str]:
        """Extract import statements"""
        imports = []

        # Match: import X from 'Y'
        for match in re.finditer(
            r'import\s+.*?\s+from\s+["\']([^"\']+)["\']', content
        ):
            imports.append(match.group(1))

        # Match: import 'Y'
        for match in re.finditer(r'import\s+["\']([^"\']+)["\']', content):
            imports.append(match.group(1))

        return imports

    def _extract_exports(self, content: str) -> List[str]:
        """Extract exported identifiers"""
        exports = []

        # export const/function/class X
        exports.extend(
            re.findall(r"export\s+(?:const|function|class)\s+(\w+)", content)
        )

        # export { X, Y }
        for match in re.finditer(r"export\s+\{([^}]+)\}", content):
            items = match.group(1).split(",")
            exports.extend([item.strip().split()[0] for item in items])

        return exports

    def _count_functions(self, content: str) -> int:
        """Count function declarations"""
        # function X(), const X = () =>, const X = function()
        count = len(re.findall(r"\bfunction\s+\w+", content))
        count += len(
            re.findall(
                r"const\s+\w+\s*=\s*(?:\([^)]*\)|[a-zA-Z_]\w*)\s*=>", content
            )
        )
        count += len(re.findall(r"const\s+\w+\s*=\s*function", content))
        return count

    def _count_classes(self, content: str) -> int:
        """Count class declarations"""
        return len(re.findall(r"\bclass\s+\w+", content))

    def _count_react_components(self, content: str) -> int:
        """Count React component definitions"""
        # Function components: const X: React.FC, function X() { return <
        count = len(re.findall(r"const\s+[A-Z]\w+\s*:\s*React\.FC", content))
        count += len(
            re.findall(r"function\s+[A-Z]\w+.*?return\s*\(?\s*<", content, re.DOTALL)
        )
        return count

    def _count_react_hooks(self, content: str) -> int:
        """Count React hook usages"""
        # useState, useEffect, useCallback, etc.
        return len(re.findall(r"\buse[A-Z]\w+\s*\(", content))

    def _estimate_complexity(self, content: str) -> float:
        """Estimate cyclomatic complexity for TypeScript"""
        # Count decision points: if, else, case, while, for, &&, ||, ?
        complexity = 1  # Base complexity

        complexity += len(re.findall(r"\bif\s*\(", content))
        complexity += len(re.findall(r"\belse\b", content))
        complexity += len(re.findall(r"\bcase\s+", content))
        complexity += len(re.findall(r"\bwhile\s*\(", content))
        complexity += len(re.findall(r"\bfor\s*\(", content))
        complexity += len(re.findall(r"&&", content))
        complexity += len(re.findall(r"\|\|", content))
        complexity += len(re.findall(r"\?", content))

        return complexity

    def _extract_function_sizes(self, content: str) -> List[int]:
        """Extract line counts per function using brace matching."""
        lines = content.split("\n")
        sizes = []
        func_pattern = re.compile(
            r'(?:\bfunction\s+\w+|const\s+\w+\s*=\s*(?:\([^)]*\)|[a-zA-Z_]\w*)\s*=>|const\s+\w+\s*=\s*function)'
        )

        i = 0
        while i < len(lines):
            if func_pattern.search(lines[i]):
                start = i
                depth = 0
                found_open = False
                j = i
                while j < len(lines):
                    depth += lines[j].count("{") - lines[j].count("}")
                    if "{" in lines[j]:
                        found_open = True
                    if found_open and depth <= 0:
                        sizes.append(max(j - start + 1, 1))
                        i = j + 1
                        break
                    j += 1
                else:
                    # Arrow functions without braces (single expression)
                    if "=>" in lines[start]:
                        sizes.append(1)
                    i += 1
            else:
                i += 1

        return sizes

    def _extract_ast_node_types(self, content: str) -> Counter:
        """Extract distribution of AST node types for TypeScript"""
        node_types = Counter()

        # TypeScript/React-specific node types
        node_types["function"] = self._count_functions(content)
        node_types["class"] = self._count_classes(content)
        node_types["component"] = self._count_react_components(content)
        node_types["hook"] = self._count_react_hooks(content)
        node_types["import"] = len(self._extract_imports(content))
        node_types["export"] = len(self._extract_exports(content))
        node_types["if"] = len(re.findall(r"\bif\s*\(", content))
        node_types["for"] = len(re.findall(r"\bfor\s*\(", content))
        node_types["while"] = len(re.findall(r"\bwhile\s*\(", content))
        node_types["return"] = len(re.findall(r"\breturn\b", content))
        node_types["jsx"] = len(re.findall(r"<[A-Z]\w+", content))

        return node_types
