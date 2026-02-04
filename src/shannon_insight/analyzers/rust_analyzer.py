"""Rust language analyzer"""

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


class RustScanner(BaseScanner):
    """Scanner for Rust codebases"""

    def __init__(self, root_dir: str, settings: Optional[AnalysisSettings] = None):
        super().__init__(root_dir, extensions=[".rs"], settings=settings)

    def _should_skip(self, filepath: Path) -> bool:
        path_str = str(filepath)
        skip_dirs = ("target", ".git", "node_modules", "venv", ".venv", "__pycache__")
        name = filepath.name
        return (
            any(d in path_str for d in skip_dirs)
            or name.startswith("test_")
            or name.endswith("_test.rs")
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
            interfaces=self._count_traits(content),  # traits → interfaces slot
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
        tokens = re.findall(r"\w+|[{}()\[\];,.<>!&|:?]", content)
        return len(tokens)

    def _extract_imports(self, content: str) -> List[str]:
        imports = []
        # use std::collections::HashMap;
        imports.extend(re.findall(r"^use\s+([^;{]+)", content, re.MULTILINE))
        # extern crate X;
        imports.extend(re.findall(r"^extern\s+crate\s+(\w+)", content, re.MULTILINE))
        return [i.strip() for i in imports]

    def _extract_exports(self, content: str) -> List[str]:
        exports = []
        # pub fn, pub struct, pub enum, pub trait, pub type, pub const, pub mod
        exports.extend(re.findall(
            r"\bpub\s+(?:fn|struct|enum|trait|type|const|mod|static)\s+(\w+)",
            content,
        ))
        return exports

    def _count_functions(self, content: str) -> int:
        return len(re.findall(r"\bfn\s+\w+", content))

    def _count_traits(self, content: str) -> int:
        return len(re.findall(r"\btrait\s+\w+", content))

    def _count_structs(self, content: str) -> int:
        return (
            len(re.findall(r"\bstruct\s+\w+", content))
            + len(re.findall(r"\benum\s+\w+", content))
        )

    def _estimate_complexity(self, content: str) -> float:
        complexity = 1
        complexity += len(re.findall(r"\bif\s+", content))
        complexity += len(re.findall(r"\belse\b", content))
        complexity += len(re.findall(r"\bmatch\s+", content))
        complexity += len(re.findall(r"\bfor\s+", content))
        complexity += len(re.findall(r"\bwhile\s+", content))
        complexity += len(re.findall(r"\bloop\s*\{", content))
        complexity += len(re.findall(r"&&", content))
        complexity += len(re.findall(r"\|\|", content))
        complexity += len(re.findall(r"\?", content))  # ? error propagation
        return complexity

    def _extract_function_sizes(self, content: str) -> List[int]:
        """Extract line counts per function using brace matching."""
        lines = content.split("\n")
        sizes = []

        i = 0
        while i < len(lines):
            if re.search(r"\bfn\s+\w+", lines[i]):
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
        c["struct"] = len(re.findall(r"\bstruct\s+\w+", content))
        c["enum"] = len(re.findall(r"\benum\s+\w+", content))
        c["trait"] = self._count_traits(content)
        c["impl"] = len(re.findall(r"\bimpl\s+", content))
        c["import"] = len(self._extract_imports(content))
        c["export"] = len(self._extract_exports(content))
        c["if"] = len(re.findall(r"\bif\s+", content))
        c["match"] = len(re.findall(r"\bmatch\s+", content))
        c["for"] = len(re.findall(r"\bfor\s+", content))
        c["return"] = len(re.findall(r"\breturn\b", content))
        c["macro"] = len(re.findall(r"\w+!\s*[(\[{]", content))
        return c
