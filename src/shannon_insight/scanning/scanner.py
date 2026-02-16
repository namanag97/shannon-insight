"""Configurable scanner — a single class that handles any language.

Language-specific behavior is driven entirely by a LanguageConfig
instance (from languages.py). No subclassing needed.
"""

import re
from collections import Counter
from pathlib import Path
from typing import Optional

from ..config import AnalysisSettings
from ..exceptions import FileAccessError
from ..logging_config import get_logger
from .base import BaseScanner
from .languages import LanguageConfig
from .models import FileMetrics

logger = get_logger(__name__)

# Binary extensions — never try to read these as text.
BINARY_EXTENSIONS = frozenset(
    {
        ".exe",
        ".dll",
        ".so",
        ".dylib",
        ".o",
        ".a",
        ".lib",
        ".class",
        ".jar",
        ".war",
        ".ear",
        ".pyc",
        ".pyo",
        ".wasm",
        ".png",
        ".jpg",
        ".jpeg",
        ".gif",
        ".bmp",
        ".ico",
        ".svg",
        ".webp",
        ".mp3",
        ".mp4",
        ".avi",
        ".mov",
        ".wav",
        ".flac",
        ".zip",
        ".tar",
        ".gz",
        ".bz2",
        ".xz",
        ".7z",
        ".rar",
        ".pdf",
        ".doc",
        ".docx",
        ".xls",
        ".xlsx",
        ".ppt",
        ".pptx",
        ".ttf",
        ".otf",
        ".woff",
        ".woff2",
        ".eot",
        ".db",
        ".sqlite",
        ".sqlite3",
        ".bin",
        ".dat",
        ".img",
        ".iso",
    }
)


class ConfigurableScanner(BaseScanner):
    """A single scanner class driven by a LanguageConfig."""

    def __init__(
        self,
        root_dir: str,
        config: LanguageConfig,
        extensions: Optional[list[str]] = None,
        settings: Optional[AnalysisSettings] = None,
    ):
        super().__init__(
            root_dir,
            extensions=extensions or list(config.extensions),
            settings=settings,
        )
        self.config = config

    # ── Skip logic ─────────────────────────────────────────────

    def _should_skip(self, filepath: Path) -> bool:
        path_str = str(filepath)
        name = filepath.name
        suffix = filepath.suffix.lower()
        cfg = self.config

        if suffix in BINARY_EXTENSIONS:
            return True
        if any(d in path_str for d in cfg.skip_dirs):
            return True
        if cfg.skip_file_prefixes and any(name.startswith(p) for p in cfg.skip_file_prefixes):
            return True
        if cfg.skip_file_suffixes and any(name.endswith(s) for s in cfg.skip_file_suffixes):
            return True
        if cfg.skip_file_names and name in cfg.skip_file_names:
            return True
        if cfg.skip_path_fragments and any(frag in path_str for frag in cfg.skip_path_fragments):
            return True
        # Binary sniff for universal mode
        if cfg.name == "universal":
            try:
                with open(filepath, "rb") as f:
                    if b"\x00" in f.read(8192):
                        return True
            except OSError:
                return True
        return False

    # ── Main analysis ──────────────────────────────────────────

    def _analyze_file(self, filepath: Path) -> FileMetrics:
        try:
            with open(filepath, encoding="utf-8", errors="replace") as f:
                content = f.read()
        except OSError as e:
            raise FileAccessError(filepath, f"Cannot read file: {e}")

        if not content.strip():
            return FileMetrics(
                path=str(filepath.relative_to(self.root_dir)),
                lines=0,
                tokens=0,
                imports=[],
                exports=[],
                functions=0,
                interfaces=0,
                structs=0,
                complexity_score=1.0,
                nesting_depth=0,
                ast_node_types=Counter(),
                last_modified=filepath.stat().st_mtime,
                function_sizes=[],
            )

        lines = content.splitlines()
        return FileMetrics(
            path=str(filepath.relative_to(self.root_dir)),
            lines=len(lines),
            tokens=self._count_tokens(content),
            imports=self._extract_imports(content),
            exports=self._extract_exports(content),
            functions=self._count_functions(content),
            interfaces=self._count_patterns(content, self.config.interface_patterns),
            structs=self._count_patterns(content, self.config.struct_patterns),
            complexity_score=self._estimate_complexity(content),
            nesting_depth=self._compute_nesting(content),
            ast_node_types=self._extract_ast_node_types(content),
            last_modified=filepath.stat().st_mtime,
            function_sizes=self._extract_function_sizes(content),
        )

    # ── Token counting ─────────────────────────────────────────

    def _count_tokens(self, content: str) -> int:
        for pattern, flags in self.config.comment_patterns:
            content = re.sub(pattern, "", content, flags=flags)
        for pattern in self.config.string_patterns:
            content = re.sub(pattern, "", content)
        return len(re.findall(r"\w+|[{}()\[\];,.:@=<>!&|+\-*/%^~?]", content))

    # ── Imports ────────────────────────────────────────────────

    def _extract_imports(self, content: str) -> list[str]:
        imports: list[str] = []
        for pattern in self.config.import_patterns:
            imports.extend(m.group(1) for m in re.finditer(pattern, content, re.MULTILINE))
        # Handle Go-style grouped imports
        if self.config.name in ("go", "universal"):
            for m in re.finditer(r"import\s*\([^)]+\)", content, re.DOTALL):
                imports.extend(re.findall(r'"([^"]+)"', m.group(0)))
        # Strip whitespace from Rust-style imports
        imports = [i.strip() for i in imports]
        return imports

    # ── Exports ────────────────────────────────────────────────

    def _extract_exports(self, content: str) -> list[str]:
        exports = []
        for pattern in self.config.export_patterns:
            exports.extend(re.findall(pattern, content, re.MULTILINE))
        return exports

    # ── Function counting ──────────────────────────────────────

    def _count_functions(self, content: str) -> int:
        count = 0
        for pattern in self.config.function_patterns:
            count += len(re.findall(pattern, content, re.MULTILINE))
        return count

    # ── Generic pattern counter (structs, interfaces) ──────────

    @staticmethod
    def _count_patterns(content: str, patterns: list[str]) -> int:
        return sum(len(re.findall(p, content)) for p in patterns)

    # ── Complexity ─────────────────────────────────────────────

    def _estimate_complexity(self, content: str) -> float:
        """Estimate cyclomatic complexity.

        McCabe complexity = E - N + 2P where:
        - E = edges in control flow graph
        - N = nodes in control flow graph
        - P = connected components (functions)

        Approximation: 1 + decision_points per function.
        Each if/elif/for/while/case/catch/and/or adds 1.

        Returns sum across all functions, or file-level if no functions found.
        """
        # Count decision points (each adds a branch)
        decision_points = 0
        for kw in self.config.complexity_keywords:
            decision_points += len(re.findall(rf"\b{kw}\b", content))
        for op in self.config.complexity_operators:
            decision_points += len(re.findall(op, content))

        # Count functions - each function has base complexity 1
        func_count = self._count_functions(content)
        if func_count == 0:
            func_count = 1  # Treat file as single unit

        # McCabe approximation: base 1 per function + decision points
        # Return average complexity per function (more meaningful for comparison)
        return (func_count + decision_points) / func_count

    # ── Nesting ────────────────────────────────────────────────

    def _compute_nesting(self, content: str) -> int:
        mode = self.config.nesting_mode
        if mode == "brace":
            return self._max_nesting_depth(content)
        elif mode == "indent":
            return self._indent_nesting(content)
        elif mode == "ruby":
            return self._ruby_nesting(content)
        else:  # "both"
            return max(self._max_nesting_depth(content), self._indent_nesting(content))

    @staticmethod
    def _indent_nesting(content: str) -> int:
        max_depth = 0
        for line in content.split("\n"):
            stripped = line.lstrip()
            if not stripped or stripped.startswith("#") or stripped.startswith("//"):
                continue
            depth = (len(line) - len(stripped)) // 4
            max_depth = max(max_depth, depth)
        return max_depth

    @staticmethod
    def _ruby_nesting(content: str) -> int:
        max_depth = 0
        depth = 0
        for line in content.split("\n"):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            openers = len(
                re.findall(
                    r"\b(?:def|class|module|do|begin|if|unless|case|while|until|for)\b",
                    stripped,
                )
            )
            closers = len(re.findall(r"\bend\b", stripped))
            openers += stripped.count("{")
            closers += stripped.count("}")
            depth += openers - closers
            depth = max(depth, 0)
            max_depth = max(max_depth, depth)
        return max_depth

    # ── Function sizes ─────────────────────────────────────────

    def _extract_function_sizes(self, content: str) -> list[int]:
        if self.config.nesting_mode == "ruby":
            return self._ruby_function_sizes(content)

        lines = content.split("\n")
        sizes: list[int] = []
        all_fn_patterns = "|".join(self.config.function_patterns)
        if not all_fn_patterns:
            return sizes

        i = 0
        while i < len(lines):
            if re.search(all_fn_patterns, lines[i]):
                if self.config.nesting_mode in ("brace", "both") and "{" in content:
                    start, depth, found_open, j = i, 0, False, i
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
                        sizes.append(self._indent_fn_size(lines, i))
                        i += 1
                else:
                    sizes.append(self._indent_fn_size(lines, i))
                    i += 1
            else:
                i += 1
        return sizes

    def _ruby_function_sizes(self, content: str) -> list[int]:
        lines = content.split("\n")
        sizes = []
        i = 0
        while i < len(lines):
            if re.search(r"\bdef\s+\w+", lines[i]):
                start = i
                depth = 1
                j = i + 1
                while j < len(lines):
                    stripped = lines[j].strip()
                    if not stripped or stripped.startswith("#"):
                        j += 1
                        continue
                    depth += len(
                        re.findall(
                            r"\b(?:def|class|module|do|begin|if|unless|case|while|until|for)\b",
                            stripped,
                        )
                    )
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

    @staticmethod
    def _indent_fn_size(lines: list[str], start: int) -> int:
        if start >= len(lines):
            return 1
        base_indent = len(lines[start]) - len(lines[start].lstrip())
        count = 1
        for line in lines[start + 1 :]:
            stripped = line.strip()
            if not stripped:
                count += 1
                continue
            if (len(line) - len(line.lstrip())) <= base_indent:
                break
            count += 1
        return max(count, 1)

    # ── AST node types ─────────────────────────────────────────

    def _extract_ast_node_types(self, content: str) -> Counter:
        node_types: Counter[str] = Counter()
        node_types["function"] = self._count_functions(content)
        node_types["import"] = len(self._extract_imports(content))
        node_types["export"] = len(self._extract_exports(content))
        for kw in ("if", "for", "while", "return", "class", "try", "match", "switch"):
            node_types[kw] = len(re.findall(rf"\b{kw}\b", content))
        for name, pattern in self.config.extra_ast_patterns:
            node_types[name] = len(re.findall(pattern, content, re.MULTILINE))
        return node_types
