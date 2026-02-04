"""Universal language-agnostic analyzer.

Fallback scanner for any text-based source file not covered by the
language-specific scanners.  Uses universal regex heuristics for
function detection, complexity estimation, and nesting analysis.
"""

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

# Extensions that are almost certainly binary — never try to parse.
_BINARY_EXTENSIONS = frozenset({
    ".exe", ".dll", ".so", ".dylib", ".o", ".a", ".lib",
    ".class", ".jar", ".war", ".ear",
    ".pyc", ".pyo", ".wasm",
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".ico", ".svg", ".webp",
    ".mp3", ".mp4", ".avi", ".mov", ".wav", ".flac",
    ".zip", ".tar", ".gz", ".bz2", ".xz", ".7z", ".rar",
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
    ".ttf", ".otf", ".woff", ".woff2", ".eot",
    ".db", ".sqlite", ".sqlite3",
    ".bin", ".dat", ".img", ".iso",
})

# Default set of common source-file extensions when none are provided.
_DEFAULT_SOURCE_EXTENSIONS = [
    ".scala", ".kt", ".kts", ".swift", ".m", ".mm",
    ".ex", ".exs", ".erl", ".hrl",
    ".clj", ".cljs", ".cljc", ".edn",
    ".hs", ".lhs", ".ml", ".mli", ".fs", ".fsi", ".fsx",
    ".lua", ".pl", ".pm", ".r", ".R",
    ".jl", ".nim", ".zig", ".v", ".sv",
    ".groovy", ".gradle", ".dart", ".php",
    ".sh", ".bash", ".zsh", ".fish",
    ".ps1", ".psm1",
    ".coffee", ".elm", ".purs",
    ".d", ".ada", ".adb", ".ads",
    ".pas", ".pp", ".lpr",
    ".vb", ".vbs", ".cls",
    ".tcl", ".awk", ".sed",
    ".pro", ".P",  # Prolog
    ".lisp", ".cl", ".el",
    ".rkt", ".scm", ".ss",
    ".tf", ".hcl",  # Terraform / HCL
    ".yaml", ".yml", ".toml", ".json5",
    ".cmake",
]


class UniversalScanner(BaseScanner):
    """Language-agnostic fallback scanner.

    Uses universal regex patterns that work across most programming
    languages to extract approximate metrics for cognitive-load,
    complexity, and structural analysis.
    """

    def __init__(
        self,
        root_dir: str,
        extensions: Optional[List[str]] = None,
        settings: Optional[AnalysisSettings] = None,
    ):
        super().__init__(
            root_dir,
            extensions=extensions or list(_DEFAULT_SOURCE_EXTENSIONS),
            settings=settings,
        )

    # ------------------------------------------------------------------
    # Skip logic
    # ------------------------------------------------------------------

    def _should_skip(self, filepath: Path) -> bool:
        path_str = str(filepath)
        skip_dirs = (
            "vendor", "node_modules", "venv", ".venv", "__pycache__",
            ".git", ".tox", ".mypy_cache", ".pytest_cache",
            "dist", "build", "target", ".eggs",
            "third_party", "cmake-build",
        )
        name = filepath.name
        suffix = filepath.suffix.lower()

        if suffix in _BINARY_EXTENSIONS:
            return True
        if any(d in path_str for d in skip_dirs):
            return True
        if name.startswith("test_") or name.endswith("_test" + suffix):
            return True
        # Binary sniff: null byte in first 8 KB
        try:
            with open(filepath, "rb") as f:
                chunk = f.read(8192)
            if b"\x00" in chunk:
                return True
        except OSError:
            return True
        return False

    # ------------------------------------------------------------------
    # File analysis
    # ------------------------------------------------------------------

    def _analyze_file(self, filepath: Path) -> FileMetrics:
        try:
            with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
        except OSError as e:
            raise FileAccessError(filepath, f"Cannot read file: {e}")

        if not content.strip():
            return FileMetrics(
                path=str(filepath.relative_to(self.root_dir)),
                lines=0, tokens=0, imports=[], exports=[],
                functions=0, interfaces=0, structs=0,
                complexity_score=1.0, nesting_depth=0,
                ast_node_types=Counter(), last_modified=filepath.stat().st_mtime,
                function_sizes=[],
            )

        lines = content.split("\n")
        return FileMetrics(
            path=str(filepath.relative_to(self.root_dir)),
            lines=len(lines),
            tokens=self._count_tokens(content),
            imports=self._extract_imports(content),
            exports=self._extract_exports(content),
            functions=self._count_functions(content),
            interfaces=0,
            structs=0,
            complexity_score=self._estimate_complexity(content),
            nesting_depth=self._max_nesting_depth_universal(content),
            ast_node_types=self._extract_ast_node_types(content),
            last_modified=filepath.stat().st_mtime,
            function_sizes=self._extract_function_sizes(content),
        )

    # ------------------------------------------------------------------
    # Token counting
    # ------------------------------------------------------------------

    def _count_tokens(self, content: str) -> int:
        # Strip C-style line comments
        content = re.sub(r"//.*", "", content)
        # Strip C-style block comments
        content = re.sub(r"/\*.*?\*/", "", content, flags=re.DOTALL)
        # Strip hash comments
        content = re.sub(r"#.*", "", content)
        # Strip triple-quoted strings
        content = re.sub(r'""".*?"""', "", content, flags=re.DOTALL)
        content = re.sub(r"'''.*?'''", "", content, flags=re.DOTALL)
        # Strip backtick strings
        content = re.sub(r"`[^`]*`", "", content)
        # Strip regular strings
        content = re.sub(r'"[^"]*"', "", content)
        content = re.sub(r"'[^']*'", "", content)

        tokens = re.findall(r"\w+|[{}()\[\];,.:@=<>!&|+\-*/%^~?]", content)
        return len(tokens)

    # ------------------------------------------------------------------
    # Import extraction — union of all language patterns
    # ------------------------------------------------------------------

    def _extract_imports(self, content: str) -> List[str]:
        imports: List[str] = []

        # Python-style: import X / from X import Y
        imports.extend(
            m.group(1) for m in re.finditer(r"^import\s+(\S+)", content, re.MULTILINE)
        )
        imports.extend(
            m.group(1)
            for m in re.finditer(r"^from\s+(\S+)\s+import", content, re.MULTILINE)
        )

        # C/C++ #include
        imports.extend(
            m.group(1) for m in re.finditer(r'#include\s*[<"]([^>"]+)[>"]', content)
        )

        # Rust / Ruby: use X
        imports.extend(
            m.group(1)
            for m in re.finditer(r"^\s*use\s+([\w:]+)", content, re.MULTILINE)
        )

        # JS/TS: import ... from '...' / require('...')
        imports.extend(
            m.group(1)
            for m in re.finditer(r"""(?:from|require)\s*\(\s*['"]([^'"]+)['"]\s*\)""", content)
        )
        imports.extend(
            m.group(1)
            for m in re.finditer(r"""from\s+['"]([^'"]+)['"]""", content)
        )

        # Go grouped imports
        for m in re.finditer(r'import\s*\([^)]+\)', content, re.DOTALL):
            imports.extend(re.findall(r'"([^"]+)"', m.group(0)))

        return imports

    # ------------------------------------------------------------------
    # Export extraction
    # ------------------------------------------------------------------

    def _extract_exports(self, content: str) -> List[str]:
        exports: List[str] = []

        # JS/TS export
        exports.extend(
            re.findall(r"\bexport\s+(?:default\s+)?(?:function|class|const|let|var|type|interface)\s+(\w+)", content)
        )

        # Rust: pub fn/struct/enum
        exports.extend(
            re.findall(r"\bpub\s+(?:fn|struct|enum|trait|type|mod)\s+(\w+)", content)
        )

        # Java-style: public class/interface
        exports.extend(
            re.findall(r"\bpublic\s+(?:class|interface|enum)\s+(\w+)", content)
        )

        # Top-level def / class (Python-like)
        exports.extend(
            re.findall(r"^def\s+([a-zA-Z]\w*)\s*\(", content, re.MULTILINE)
        )
        exports.extend(
            re.findall(r"^class\s+([a-zA-Z]\w*)", content, re.MULTILINE)
        )

        return exports

    # ------------------------------------------------------------------
    # Function counting
    # ------------------------------------------------------------------

    def _count_functions(self, content: str) -> int:
        # Keyword-based: def, fn, func, function, sub
        keyword_fns = len(
            re.findall(r"\b(?:def|fn|func|function|sub)\s+\w+", content)
        )
        # Arrow functions:  (args) => or ident => {
        arrow_fns = len(
            re.findall(r"(?:\)\s*=>|\w+\s*=>)\s*\{", content)
        )
        # Java/C-style: visibility? type name(
        c_style = len(
            re.findall(
                r"(?:^|\n)\s*(?:public|private|protected|static|inline|virtual|override|async)?"
                r"\s*\w+(?:<[^>]+>)?\s+(\w+)\s*\(",
                content,
            )
        )
        return keyword_fns + arrow_fns + c_style

    # ------------------------------------------------------------------
    # Complexity estimation
    # ------------------------------------------------------------------

    def _estimate_complexity(self, content: str) -> float:
        complexity = 1  # base

        complexity += len(re.findall(r"\bif\b", content))
        complexity += len(re.findall(r"\belse\b", content))
        complexity += len(re.findall(r"\belif\b", content))
        complexity += len(re.findall(r"\belsif\b", content))
        complexity += len(re.findall(r"\bunless\b", content))
        complexity += len(re.findall(r"\bcase\b", content))
        complexity += len(re.findall(r"\bswitch\b", content))
        complexity += len(re.findall(r"\bfor\b", content))
        complexity += len(re.findall(r"\bwhile\b", content))
        complexity += len(re.findall(r"\bmatch\b", content))
        complexity += len(re.findall(r"\bwhen\b", content))
        complexity += len(re.findall(r"&&", content))
        complexity += len(re.findall(r"\|\|", content))
        complexity += len(re.findall(r"\band\b", content))
        complexity += len(re.findall(r"\bor\b", content))

        return float(complexity)

    # ------------------------------------------------------------------
    # Nesting depth — max of brace-based and indent-based
    # ------------------------------------------------------------------

    def _max_nesting_depth_universal(self, content: str) -> int:
        # Brace depth (C-family)
        brace_depth = self._max_nesting_depth(content)

        # Indentation depth (Python / Ruby / Haskell / etc.)
        indent_depth = 0
        for line in content.split("\n"):
            stripped = line.lstrip()
            if not stripped or stripped.startswith("#") or stripped.startswith("//"):
                continue
            indent = len(line) - len(stripped)
            depth = indent // 4
            indent_depth = max(indent_depth, depth)

        return max(brace_depth, indent_depth)

    # ------------------------------------------------------------------
    # Function sizes — brace matching with indent fallback
    # ------------------------------------------------------------------

    def _extract_function_sizes(self, content: str) -> List[int]:
        lines = content.split("\n")
        sizes: List[int] = []

        i = 0
        while i < len(lines):
            if re.match(r".*\b(?:def|fn|func|function|sub)\s+\w+", lines[i]):
                # Try brace-matching first
                if "{" in content:
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
                        # Brace matching failed — fall back to indent
                        sizes.append(self._indent_function_size(lines, i))
                        i += 1
                else:
                    # No braces at all — indent-based (Python-like)
                    sizes.append(self._indent_function_size(lines, i))
                    i += 1
            else:
                i += 1

        return sizes

    @staticmethod
    def _indent_function_size(lines: List[str], start: int) -> int:
        """Measure function size by indentation (for def-style languages)."""
        if start >= len(lines):
            return 1
        base_indent = len(lines[start]) - len(lines[start].lstrip())
        count = 1
        for line in lines[start + 1:]:
            stripped = line.strip()
            if not stripped:
                count += 1
                continue
            indent = len(line) - len(line.lstrip())
            if indent <= base_indent:
                break
            count += 1
        return max(count, 1)

    # ------------------------------------------------------------------
    # AST node types — universal keyword counting
    # ------------------------------------------------------------------

    def _extract_ast_node_types(self, content: str) -> Counter:
        node_types = Counter()

        node_types["function"] = self._count_functions(content)
        node_types["import"] = len(self._extract_imports(content))
        node_types["export"] = len(self._extract_exports(content))
        node_types["if"] = len(re.findall(r"\bif\b", content))
        node_types["for"] = len(re.findall(r"\bfor\b", content))
        node_types["while"] = len(re.findall(r"\bwhile\b", content))
        node_types["return"] = len(re.findall(r"\breturn\b", content))
        node_types["class"] = len(re.findall(r"\bclass\s+\w+", content))
        node_types["try"] = len(re.findall(r"\btry\b", content))
        node_types["match"] = len(re.findall(r"\bmatch\b", content))
        node_types["switch"] = len(re.findall(r"\bswitch\b", content))

        return node_types
