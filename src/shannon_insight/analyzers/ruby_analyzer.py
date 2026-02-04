"""Ruby language analyzer"""

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


class RubyScanner(BaseScanner):
    """Scanner for Ruby codebases"""

    def __init__(self, root_dir: str, settings: Optional[AnalysisSettings] = None):
        super().__init__(root_dir, extensions=[".rb"], settings=settings)

    def _should_skip(self, filepath: Path) -> bool:
        path_str = str(filepath)
        skip_dirs = ("vendor", "bundle", ".git", "node_modules",
                     "venv", ".venv", "__pycache__", "tmp", "log")
        name = filepath.name
        return (
            any(d in path_str for d in skip_dirs)
            or name.startswith("test_")
            or name.endswith("_test.rb")
            or name.endswith("_spec.rb")
            or "/test/" in path_str
            or "/spec/" in path_str
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
            interfaces=self._count_modules(content),   # modules → interfaces slot
            structs=self._count_classes(content),       # classes → structs slot
            complexity_score=self._estimate_complexity(content),
            nesting_depth=self._max_nesting_depth_ruby(content),
            ast_node_types=self._extract_ast_node_types(content),
            last_modified=filepath.stat().st_mtime,
            function_sizes=self._extract_function_sizes(content),
        )

    def _count_tokens(self, content: str) -> int:
        content = re.sub(r"#.*", "", content)
        content = re.sub(r'=begin.*?=end', "", content, flags=re.DOTALL)
        content = re.sub(r'"[^"]*"', "", content)
        content = re.sub(r"'[^']*'", "", content)
        tokens = re.findall(r"\w+|[{}()\[\];,.:@|&!?]", content)
        return len(tokens)

    def _extract_imports(self, content: str) -> List[str]:
        imports = []
        # require 'x' / require "x"
        imports.extend(re.findall(r"require\s+['\"]([^'\"]+)['\"]", content))
        # require_relative 'x'
        imports.extend(re.findall(r"require_relative\s+['\"]([^'\"]+)['\"]", content))
        # include X, extend X
        imports.extend(re.findall(r"\b(?:include|extend)\s+(\w+(?:::\w+)*)", content))
        return imports

    def _extract_exports(self, content: str) -> List[str]:
        exports = []
        # Public methods (def without private/protected prefix in scope)
        exports.extend(re.findall(r"^\s*def\s+(?:self\.)?(\w+)", content, re.MULTILINE))
        # Classes and modules
        exports.extend(re.findall(r"^\s*class\s+(\w+)", content, re.MULTILINE))
        exports.extend(re.findall(r"^\s*module\s+(\w+)", content, re.MULTILINE))
        return exports

    def _count_functions(self, content: str) -> int:
        return len(re.findall(r"\bdef\s+\w+", content))

    def _count_classes(self, content: str) -> int:
        return len(re.findall(r"\bclass\s+\w+", content))

    def _count_modules(self, content: str) -> int:
        return len(re.findall(r"\bmodule\s+\w+", content))

    def _estimate_complexity(self, content: str) -> float:
        complexity = 1
        complexity += len(re.findall(r"\bif\s+", content))
        complexity += len(re.findall(r"\belsif\s+", content))
        complexity += len(re.findall(r"\belse\b", content))
        complexity += len(re.findall(r"\bunless\s+", content))
        complexity += len(re.findall(r"\bcase\s+", content))
        complexity += len(re.findall(r"\bwhen\s+", content))
        complexity += len(re.findall(r"\bwhile\s+", content))
        complexity += len(re.findall(r"\buntil\s+", content))
        complexity += len(re.findall(r"\.each\b", content))
        complexity += len(re.findall(r"\.map\b", content))
        complexity += len(re.findall(r"\brescue\b", content))
        complexity += len(re.findall(r"&&", content))
        complexity += len(re.findall(r"\|\|", content))
        return complexity

    def _max_nesting_depth_ruby(self, content: str) -> int:
        """Ruby uses do/end and def/end blocks, not just braces."""
        max_depth = 0
        depth = 0
        for line in content.split("\n"):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            # Opening keywords
            openers = len(re.findall(
                r"\b(?:def|class|module|do|begin|if|unless|case|while|until|for)\b",
                stripped,
            ))
            # Closing keyword
            closers = len(re.findall(r"\bend\b", stripped))
            # Also count brace blocks
            openers += stripped.count("{")
            closers += stripped.count("}")
            depth += openers - closers
            depth = max(depth, 0)
            max_depth = max(max_depth, depth)
        return max_depth

    def _extract_function_sizes(self, content: str) -> List[int]:
        """Extract line counts per method using def/end matching."""
        lines = content.split("\n")
        sizes = []

        i = 0
        while i < len(lines):
            if re.search(r"\bdef\s+\w+", lines[i]):
                start = i
                depth = 1  # The def opens a block
                j = i + 1
                while j < len(lines):
                    stripped = lines[j].strip()
                    if not stripped or stripped.startswith("#"):
                        j += 1
                        continue
                    # Count block openers and closers
                    depth += len(re.findall(
                        r"\b(?:def|class|module|do|begin|if|unless|case|while|until|for)\b",
                        stripped,
                    ))
                    depth -= len(re.findall(r"\bend\b", stripped))
                    if depth <= 0:
                        sizes.append(max(j - start + 1, 1))
                        i = j + 1
                        break
                    j += 1
                else:
                    sizes.append(max(len(lines) - start, 1))
                    i = len(lines)
            else:
                i += 1

        return sizes

    def _extract_ast_node_types(self, content: str) -> Counter:
        c = Counter()
        c["method"] = self._count_functions(content)
        c["class"] = self._count_classes(content)
        c["module"] = self._count_modules(content)
        c["import"] = len(self._extract_imports(content))
        c["export"] = len(self._extract_exports(content))
        c["if"] = len(re.findall(r"\bif\s+", content))
        c["case"] = len(re.findall(r"\bcase\s+", content))
        c["each"] = len(re.findall(r"\.each\b", content))
        c["block"] = len(re.findall(r"\bdo\b", content))
        c["return"] = len(re.findall(r"\breturn\b", content))
        c["rescue"] = len(re.findall(r"\brescue\b", content))
        c["symbol"] = len(re.findall(r":\w+", content))
        return c
