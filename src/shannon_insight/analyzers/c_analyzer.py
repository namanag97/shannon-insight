"""C / C++ language analyzer"""

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


class CScanner(BaseScanner):
    """Scanner for C and C++ codebases"""

    def __init__(self, root_dir: str, settings: Optional[AnalysisSettings] = None):
        super().__init__(
            root_dir,
            extensions=[".c", ".cpp", ".cc", ".cxx", ".h", ".hpp", ".hxx"],
            settings=settings,
        )

    def _should_skip(self, filepath: Path) -> bool:
        path_str = str(filepath)
        skip_dirs = ("build", "cmake-build", ".git", "node_modules",
                     "venv", ".venv", "__pycache__", "third_party",
                     "vendor", "deps", "external")
        name = filepath.name
        return (
            any(d in path_str for d in skip_dirs)
            or name.startswith("test_")
            or name.endswith("_test.cpp")
            or name.endswith("_test.c")
            or "/test/" in path_str
            or "/tests/" in path_str
        )

    def _analyze_file(self, filepath: Path) -> FileMetrics:
        try:
            with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
        except OSError as e:
            raise FileAccessError(filepath, f"Cannot read file: {e}")

        lines = content.split("\n")

        return FileMetrics(
            path=str(filepath.relative_to(self.root_dir)),
            lines=len(lines),
            tokens=self._count_tokens(content),
            imports=self._extract_imports(content),
            exports=self._extract_exports(content),
            functions=self._count_functions(content),
            interfaces=self._count_classes(content),   # C++ classes → interfaces slot
            structs=self._count_structs(content),
            complexity_score=self._estimate_complexity(content),
            nesting_depth=self._max_nesting_depth(content),
            ast_node_types=self._extract_ast_node_types(content),
            last_modified=filepath.stat().st_mtime,
            function_sizes=self._extract_function_sizes(content),
        )

    def _count_tokens(self, content: str) -> int:
        content = re.sub(r"//.*", "", content)
        content = re.sub(r"/\*.*?\*/", "", content, flags=re.DOTALL)
        content = re.sub(r'"[^"]*"', "", content)
        tokens = re.findall(r"\w+|[{}()\[\];,.<>*&#:!?]", content)
        return len(tokens)

    def _extract_imports(self, content: str) -> List[str]:
        # #include <...> and #include "..."
        return re.findall(r'^\s*#include\s+[<"]([^>"]+)[>"]', content, re.MULTILINE)

    def _extract_exports(self, content: str) -> List[str]:
        exports = []
        # Function declarations at file scope (simplified heuristic)
        exports.extend(re.findall(
            r"^(?:extern\s+)?(?:static\s+)?(?:inline\s+)?\w+[\w\s*&]+\s+(\w+)\s*\([^)]*\)\s*\{",
            content, re.MULTILINE,
        ))
        # Class / struct names
        exports.extend(re.findall(r"\bclass\s+(\w+)", content))
        exports.extend(re.findall(r"\bstruct\s+(\w+)\s*\{", content))
        return exports

    def _count_functions(self, content: str) -> int:
        # Function definitions: type name(...) {
        return len(re.findall(
            r"^[a-zA-Z_][\w\s*&:<>]+\s+\w+\s*\([^)]*\)\s*(?:const\s*)?\{",
            content, re.MULTILINE,
        ))

    def _count_classes(self, content: str) -> int:
        return len(re.findall(r"\bclass\s+\w+", content))

    def _count_structs(self, content: str) -> int:
        return (
            len(re.findall(r"\bstruct\s+\w+\s*\{", content))
            + len(re.findall(r"\btypedef\s+struct\b", content))
        )

    def _estimate_complexity(self, content: str) -> float:
        complexity = 1
        complexity += len(re.findall(r"\bif\s*\(", content))
        complexity += len(re.findall(r"\belse\b", content))
        complexity += len(re.findall(r"\bcase\s+", content))
        complexity += len(re.findall(r"\bfor\s*\(", content))
        complexity += len(re.findall(r"\bwhile\s*\(", content))
        complexity += len(re.findall(r"\bdo\s*\{", content))
        complexity += len(re.findall(r"\bswitch\s*\(", content))
        complexity += len(re.findall(r"&&", content))
        complexity += len(re.findall(r"\|\|", content))
        complexity += len(re.findall(r"\?", content))  # ternary
        return complexity

    def _extract_function_sizes(self, content: str) -> List[int]:
        """Extract line counts per function using brace matching."""
        lines = content.split("\n")
        sizes = []
        func_pattern = re.compile(
            r"^[a-zA-Z_][\w\s*&:<>]+\s+\w+\s*\([^)]*\)\s*(?:const\s*)?\{",
            re.MULTILINE,
        )

        i = 0
        while i < len(lines):
            # Check if this line starts a function definition
            if func_pattern.match(lines[i]):
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
                    i += 1
            else:
                i += 1

        return sizes

    def _extract_ast_node_types(self, content: str) -> Counter:
        c = Counter()
        c["function"] = self._count_functions(content)
        c["class"] = self._count_classes(content)
        c["struct"] = self._count_structs(content)
        c["include"] = len(self._extract_imports(content))
        c["export"] = len(self._extract_exports(content))
        c["if"] = len(re.findall(r"\bif\s*\(", content))
        c["for"] = len(re.findall(r"\bfor\s*\(", content))
        c["while"] = len(re.findall(r"\bwhile\s*\(", content))
        c["switch"] = len(re.findall(r"\bswitch\s*\(", content))
        c["return"] = len(re.findall(r"\breturn\b", content))
        c["macro"] = len(re.findall(r"^\s*#define\b", content, re.MULTILINE))
        c["template"] = len(re.findall(r"\btemplate\s*<", content))
        return c
