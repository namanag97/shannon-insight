"""Go language analyzer"""

import re
from pathlib import Path
from collections import Counter
from typing import List
from .base import BaseScanner
from ..models import FileMetrics


class GoScanner(BaseScanner):
    """Scanner optimized for Go codebases"""

    def __init__(self, root_dir: str):
        super().__init__(root_dir, extensions=[".go"])

    def _should_skip(self, filepath: Path) -> bool:
        """Skip test files and vendor directories"""
        path_str = str(filepath)
        return "_test.go" in path_str or "vendor" in path_str

    def _analyze_file(self, filepath: Path) -> FileMetrics:
        """Extract all metrics from a Go file"""
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        lines = content.split("\n")

        return FileMetrics(
            path=str(filepath.relative_to(self.root_dir)),
            lines=len(lines),
            tokens=self._count_tokens(content),
            imports=self._extract_imports(content),
            exports=self._extract_exports(content),
            functions=self._count_functions(content),
            interfaces=self._count_interfaces(content),
            structs=self._count_structs(content),
            complexity_score=self._estimate_complexity(content),
            nesting_depth=self._max_nesting_depth(content),
            ast_node_types=self._extract_ast_node_types(content),
            last_modified=filepath.stat().st_mtime,
        )

    def _count_tokens(self, content: str) -> int:
        """Approximate token count for Go"""
        # Remove comments and strings
        content = re.sub(r"//.*", "", content)
        content = re.sub(r"/\*.*?\*/", "", content, flags=re.DOTALL)
        content = re.sub(r"`[^`]*`", "", content)
        content = re.sub(r'"[^"]*"', "", content)

        # Split on whitespace and common operators
        tokens = re.findall(r"\w+|[{}()\[\];,.]", content)
        return len(tokens)

    def _extract_imports(self, content: str) -> List[str]:
        """Extract Go import statements"""
        imports = []

        # Match: import "github.com/..."
        for match in re.finditer(r'import\s+"([^"]+)"', content):
            imports.append(match.group(1))

        # Match grouped imports: import (\n  "foo"\n  "bar"\n)
        for match in re.finditer(r"import\s*\([^)]+\)", content, re.DOTALL):
            group = match.group(0)
            for imp in re.findall(r'"([^"]+)"', group):
                imports.append(imp)

        return imports

    def _extract_exports(self, content: str) -> List[str]:
        """Extract exported identifiers (capitalized names in Go)"""
        exports = []

        # Exported functions: func ExportedName(...)
        exports.extend(re.findall(r"^func\s+([A-Z]\w*)\s*\(", content, re.MULTILINE))

        # Exported types: type ExportedName ...
        exports.extend(re.findall(r"^type\s+([A-Z]\w*)\s+", content, re.MULTILINE))

        # Exported constants: const ExportedName
        exports.extend(
            re.findall(r"^const\s+([A-Z]\w*)\s*[=\n]", content, re.MULTILINE)
        )

        # Exported variables: var ExportedName
        exports.extend(re.findall(r"^var\s+([A-Z]\w*)\s*[=\n]", content, re.MULTILINE))

        return exports

    def _count_functions(self, content: str) -> int:
        """Count function declarations (including methods with receivers)"""
        return len(re.findall(r"\bfunc\s+\w+\s*\(", content))

    def _count_interfaces(self, content: str) -> int:
        """Count interface declarations"""
        return len(re.findall(r"\btype\s+\w+\s+interface\s*\{", content))

    def _count_structs(self, content: str) -> int:
        """Count struct declarations"""
        return len(re.findall(r"\btype\s+\w+\s+struct\s*\{", content))

    def _estimate_complexity(self, content: str) -> float:
        """Estimate cyclomatic complexity for Go"""
        # Count decision points: if, else, case, for, range, select, &&, ||
        complexity = 1  # Base complexity

        complexity += len(re.findall(r"\bif\s*\(", content))
        complexity += len(re.findall(r"\belse\b", content))
        complexity += len(re.findall(r"\bcase\s+", content))
        complexity += len(re.findall(r"\bfor\s+", content))
        complexity += len(re.findall(r"\brange\s+", content))
        complexity += len(re.findall(r"\bselect\s*\{", content))
        complexity += len(re.findall(r"&&", content))
        complexity += len(re.findall(r"\|\|", content))

        return complexity

    def _extract_ast_node_types(self, content: str) -> Counter:
        """Extract distribution of AST node types for Go"""
        node_types = Counter()

        # Go-specific node types
        node_types["function"] = self._count_functions(content)
        node_types["struct"] = self._count_structs(content)
        node_types["interface"] = self._count_interfaces(content)
        node_types["import"] = len(self._extract_imports(content))
        node_types["export"] = len(self._extract_exports(content))
        node_types["if"] = len(re.findall(r"\bif\s*\(", content))
        node_types["for"] = len(re.findall(r"\bfor\s+", content))
        node_types["range"] = len(re.findall(r"\brange\s+", content))
        node_types["return"] = len(re.findall(r"\breturn\b", content))
        node_types["defer"] = len(re.findall(r"\bdefer\b", content))
        node_types["go"] = len(re.findall(r"\bgo\s+\w+\s*\(", content))
        node_types["chan"] = len(re.findall(r"\bchan\s+\w+", content))

        return node_types
