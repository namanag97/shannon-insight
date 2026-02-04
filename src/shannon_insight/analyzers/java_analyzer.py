"""Java language analyzer"""

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


class JavaScanner(BaseScanner):
    """Scanner for Java codebases"""

    def __init__(self, root_dir: str, settings: Optional[AnalysisSettings] = None):
        super().__init__(root_dir, extensions=[".java"], settings=settings)

    def _should_skip(self, filepath: Path) -> bool:
        path_str = str(filepath)
        skip_dirs = ("target", "build", ".gradle", ".mvn", ".git",
                     "node_modules", "venv", ".venv", "__pycache__")
        name = filepath.name
        return (
            any(d in path_str for d in skip_dirs)
            or name.endswith("Test.java")
            or name.endswith("Tests.java")
            or name.endswith("IT.java")
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
            interfaces=self._count_interfaces(content),
            structs=self._count_classes(content),  # classes map to structs slot
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
        tokens = re.findall(r"\w+|[{}()\[\];,.<>@]", content)
        return len(tokens)

    def _extract_imports(self, content: str) -> List[str]:
        return re.findall(r"^import\s+(?:static\s+)?([^;]+);", content, re.MULTILINE)

    def _extract_exports(self, content: str) -> List[str]:
        exports = []
        exports.extend(re.findall(
            r"public\s+(?:static\s+)?(?:final\s+)?(?:class|interface|enum|record)\s+(\w+)",
            content,
        ))
        exports.extend(re.findall(
            r"public\s+(?:static\s+)?(?:final\s+)?(?:synchronized\s+)?\w+(?:<[^>]+>)?\s+(\w+)\s*\(",
            content,
        ))
        return exports

    def _count_functions(self, content: str) -> int:
        # Match method declarations (access modifier + return type + name + parens)
        return len(re.findall(
            r"(?:public|private|protected|static|\s)+\s+\w+(?:<[^>]+>)?\s+\w+\s*\(",
            content,
        ))

    def _count_interfaces(self, content: str) -> int:
        return len(re.findall(r"\binterface\s+\w+", content))

    def _count_classes(self, content: str) -> int:
        return len(re.findall(r"\bclass\s+\w+", content))

    def _estimate_complexity(self, content: str) -> float:
        complexity = 1
        complexity += len(re.findall(r"\bif\s*\(", content))
        complexity += len(re.findall(r"\belse\b", content))
        complexity += len(re.findall(r"\bcase\s+", content))
        complexity += len(re.findall(r"\bfor\s*\(", content))
        complexity += len(re.findall(r"\bwhile\s*\(", content))
        complexity += len(re.findall(r"\bcatch\s*\(", content))
        complexity += len(re.findall(r"&&", content))
        complexity += len(re.findall(r"\|\|", content))
        complexity += len(re.findall(r"\?", content))  # ternary
        return complexity

    def _extract_function_sizes(self, content: str) -> List[int]:
        """Extract line counts per method using brace matching."""
        lines = content.split("\n")
        sizes = []
        method_pattern = re.compile(
            r"(?:public|private|protected|static|\s)+\s+\w+(?:<[^>]+>)?\s+\w+\s*\("
        )

        i = 0
        while i < len(lines):
            if method_pattern.search(lines[i]):
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
        c["method"] = self._count_functions(content)
        c["class"] = self._count_classes(content)
        c["interface"] = self._count_interfaces(content)
        c["import"] = len(self._extract_imports(content))
        c["export"] = len(self._extract_exports(content))
        c["if"] = len(re.findall(r"\bif\s*\(", content))
        c["for"] = len(re.findall(r"\bfor\s*\(", content))
        c["while"] = len(re.findall(r"\bwhile\s*\(", content))
        c["return"] = len(re.findall(r"\breturn\b", content))
        c["throw"] = len(re.findall(r"\bthrow\b", content))
        c["try"] = len(re.findall(r"\btry\s*\{", content))
        c["annotation"] = len(re.findall(r"^\s*@\w+", content, re.MULTILINE))
        return c
