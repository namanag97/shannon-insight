# Shannon Insight — Full Rearchitecture Plan

## Guiding Principle

The codebase should read like a **production line**: raw material (source files) enters one end, passes through clearly labeled stations (scan → extract → detect → fuse → recommend), and a finished product (report) comes out the other end. Each station does one thing, is independently testable, and can be swapped out without rewiring the whole factory.

---

## Current Architecture (Before)

```
cli.py (427 lines — monolith function)
  └─► core.py (352 lines — orchestration + detection + progress display)
        ├─► analyzers/go_analyzer.py       (181 lines)  ─┐
        ├─► analyzers/python_analyzer.py   (198 lines)   │
        ├─► analyzers/typescript_analyzer  (197 lines)   │  85% identical
        ├─► analyzers/java_analyzer.py     (155 lines)   │  ~1,400 duplicated lines
        ├─► analyzers/rust_analyzer.py     (150 lines)   │
        ├─► analyzers/c_analyzer.py        (167 lines)   │
        ├─► analyzers/ruby_analyzer.py     (187 lines)   │
        └─► analyzers/universal_analyzer   (391 lines)  ─┘
        │
        └─► primitives/
              ├─► extractor.py      (300 lines — compute methods hardwired)
              ├─► detector.py       (226 lines)
              ├─► fusion.py         (220 lines)
              ├─► recommendations.py(357 lines)
              └─► registry.py       (127 lines)
```

Problems:
1. 8 scanner files that are 85% copy-paste of each other
2. `core.py` mixes orchestration, language detection, and Rich progress bars
3. `cli.py` main() is 180 lines handling 6 different concerns
4. Pipeline stages are hardwired — can't skip, reorder, or extend
5. Adding a new primitive requires editing 2 core files

---

## Target Architecture (After)

```
cli/
  ├─► main.py          — entry point, argument parsing only
  ├─► commands/
  │     ├─► analyze.py  — the main analysis command
  │     ├─► diff.py     — diff against baseline
  │     ├─► explain.py  — deep-dive on a single file
  │     ├─► baseline.py — save/show baseline
  │     └─► cache.py    — cache info/clear

core/
  ├─► pipeline.py       — composable stage runner
  ├─► scanner_factory.py— language detection + scanner construction
  └─► progress.py       — Rich progress reporter (or no-op)

analyzers/
  ├─► base.py           — BaseScanner (unchanged)
  ├─► scanner.py        — single ConfigurableScanner (~200 lines)
  └─► languages.py      — registry of LanguageConfig dicts (~250 lines)

primitives/
  ├─► base.py           — PrimitivePlugin ABC
  ├─► registry.py       — discovers and registers primitives
  ├─► plugins/
  │     ├─► compression.py    — structural_entropy
  │     ├─► centrality.py     — network_centrality
  │     ├─► volatility.py     — churn_volatility
  │     ├─► coherence.py      — semantic_coherence
  │     └─► cognitive_load.py — cognitive_load
  ├─► detector.py       — anomaly detection (mostly unchanged)
  ├─► fusion.py         — signal fusion (mostly unchanged)
  └─► recommendations.py— (mostly unchanged)
```

---

## Phase 1: Eliminate Scanner Duplication

### Goal
Replace 8 scanner classes (~1,626 lines) with 1 `ConfigurableScanner` class (~200 lines) + 1 `languages.py` config registry (~250 lines). Adding a new language = adding a ~20 line dict.

### Key Insight
Every scanner does the same thing in `_analyze_file`:
```python
content = read_file(filepath)
return FileMetrics(
    path=..., lines=...,
    tokens=self._count_tokens(content),
    imports=self._extract_imports(content),
    exports=self._extract_exports(content),
    functions=self._count_functions(content),
    interfaces=self._count_interfaces(content),      # 0 for most languages
    structs=self._count_structs(content),             # 0 for most languages
    complexity_score=self._estimate_complexity(content),
    nesting_depth=self._nesting(content),
    ast_node_types=self._ast_nodes(content),
    function_sizes=self._function_sizes(content),
)
```

The ONLY differences are: which regex patterns are used, which comment syntax to strip, and whether nesting is brace-based or indent-based.

### Files to Create

#### `src/shannon_insight/analyzers/languages.py` (~250 lines)

This file holds ALL language-specific knowledge as data, not code.

```python
"""Language configurations — the single source of truth for all language patterns.

Adding a new language:
  1. Add a LanguageConfig entry to LANGUAGES below.
  2. That's it. The ConfigurableScanner picks it up automatically.
"""

from dataclasses import dataclass, field
from typing import List, Tuple


@dataclass(frozen=True)
class LanguageConfig:
    """Everything the scanner needs to know about a language."""

    name: str
    extensions: List[str]

    # Comment syntax to strip before token counting.
    # Each tuple is (pattern, flags) passed to re.sub.
    comment_patterns: List[Tuple[str, int]] = field(default_factory=list)

    # String literal patterns to strip before token counting.
    string_patterns: List[str] = field(default_factory=list)

    # Function detection regex(es). Matches are counted.
    function_patterns: List[str] = field(default_factory=list)

    # Import detection regex(es). Group 1 is captured as the import name.
    import_patterns: List[str] = field(default_factory=list)

    # Export detection regex(es). Group 1 is captured as the export name.
    export_patterns: List[str] = field(default_factory=list)

    # Complexity keywords. Each occurrence adds 1.
    complexity_keywords: List[str] = field(default_factory=list)

    # Complexity operators (not word-boundary). Each occurrence adds 1.
    complexity_operators: List[str] = field(default_factory=list)

    # Nesting mode: "brace" (count {}), "indent" (count indentation),
    # or "both" (take max of brace and indent depth).
    nesting_mode: str = "brace"

    # Struct/interface patterns (language-specific, empty = returns 0)
    struct_patterns: List[str] = field(default_factory=list)
    interface_patterns: List[str] = field(default_factory=list)

    # Extra AST node type patterns: list of (node_name, pattern).
    extra_ast_patterns: List[Tuple[str, str]] = field(default_factory=list)

    # Skip patterns: directory names and file prefixes to ignore.
    skip_dirs: Tuple[str, ...] = (
        "vendor", "node_modules", "venv", ".venv", "__pycache__",
        ".git", ".tox", ".mypy_cache", ".pytest_cache",
        "dist", "build", "target", ".eggs", "third_party",
    )
    skip_file_prefixes: Tuple[str, ...] = ("test_",)
    skip_file_suffixes: Tuple[str, ...] = ()  # e.g., ("_test.go",)
    skip_file_names: Tuple[str, ...] = ()     # e.g., ("conftest.py",)


# ── Re-usable building blocks ──────────────────────────────────────

import re as _re  # noqa: E402  — used only for flag constants

_C_LINE_COMMENT   = (r"//.*", 0)
_C_BLOCK_COMMENT  = (r"/\*.*?\*/", _re.DOTALL)
_HASH_COMMENT     = (r"#.*", 0)

_DOUBLE_QUOTE_STR = r'"[^"]*"'
_SINGLE_QUOTE_STR = r"'[^']*'"
_BACKTICK_STR     = r"`[^`]*`"
_TRIPLE_DQ_STR    = (r'""".*?"""', _re.DOTALL)
_TRIPLE_SQ_STR    = (r"'''.*?'''", _re.DOTALL)

_UNIVERSAL_COMPLEXITY_KW = [
    "if", "else", "elif", "elsif", "unless",
    "case", "switch", "for", "while",
    "match", "when",
]
_UNIVERSAL_COMPLEXITY_OP = ["&&", r"\|\|"]

_PYTHON_COMPLEXITY_KW = ["if", "elif", "else", "for", "while", "except", "and", "or", "with"]


# ── Language definitions ───────────────────────────────────────────

LANGUAGES = {

    "go": LanguageConfig(
        name="go",
        extensions=[".go"],
        comment_patterns=[_C_LINE_COMMENT, _C_BLOCK_COMMENT],
        string_patterns=[_BACKTICK_STR, _DOUBLE_QUOTE_STR],
        function_patterns=[r"\bfunc\s+\w+\s*\("],
        import_patterns=[
            r'import\s+"([^"]+)"',              # single import
            # grouped imports handled specially in scanner
        ],
        export_patterns=[
            r"^func\s+([A-Z]\w*)\s*\(",         # exported function
            r"^type\s+([A-Z]\w*)\s+",            # exported type
        ],
        complexity_keywords=["if", "else", "case", "for", "range", "select"],
        complexity_operators=["&&", r"\|\|"],
        nesting_mode="brace",
        struct_patterns=[r"\btype\s+\w+\s+struct\s*\{"],
        interface_patterns=[r"\btype\s+\w+\s+interface\s*\{"],
        skip_file_suffixes=("_test.go",),
        extra_ast_patterns=[
            ("range", r"\brange\s+"),
            ("defer", r"\bdefer\b"),
            ("go", r"\bgo\s+\w+\s*\("),
            ("chan", r"\bchan\s+\w+"),
        ],
    ),

    "python": LanguageConfig(
        name="python",
        extensions=[".py"],
        comment_patterns=[_HASH_COMMENT, _TRIPLE_DQ_STR, _TRIPLE_SQ_STR],
        string_patterns=[_DOUBLE_QUOTE_STR, _SINGLE_QUOTE_STR],
        function_patterns=[r"^\s*def\s+\w+\s*\("],
        import_patterns=[
            r"^import\s+(\S+)",
            r"^from\s+(\S+)\s+import",
        ],
        export_patterns=[
            r"^def\s+([a-zA-Z]\w*)\s*\(",
            r"^class\s+([a-zA-Z]\w*)",
        ],
        complexity_keywords=_PYTHON_COMPLEXITY_KW,
        complexity_operators=[],
        nesting_mode="indent",
        struct_patterns=[r"^class\s+\w+"],
        skip_file_prefixes=("test_",),
        skip_file_suffixes=("_test.py",),
        skip_file_names=("setup.py", "conftest.py"),
        extra_ast_patterns=[
            ("yield", r"\byield\b"),
            ("with", r"\bwith\s+"),
            ("try", r"\btry\s*:"),
            ("decorator", r"^\s*@\w+"),
        ],
    ),

    "typescript": LanguageConfig(
        name="typescript",
        extensions=[".ts", ".tsx", ".js", ".jsx"],
        comment_patterns=[_C_LINE_COMMENT, _C_BLOCK_COMMENT],
        string_patterns=[_BACKTICK_STR, _DOUBLE_QUOTE_STR, _SINGLE_QUOTE_STR],
        function_patterns=[
            r"\bfunction\s+\w+\s*\(",
            r"(?:\)\s*=>|\w+\s*=>)\s*\{",       # arrow functions
        ],
        import_patterns=[
            r"""from\s+['"]([^'"]+)['"]""",
            r"""require\s*\(\s*['"]([^'"]+)['"]\s*\)""",
        ],
        export_patterns=[
            r"\bexport\s+(?:default\s+)?(?:function|class|const|let|var|type|interface)\s+(\w+)",
        ],
        complexity_keywords=["if", "else", "case", "for", "while", "catch"],
        complexity_operators=["&&", r"\|\|", r"\?"],
        nesting_mode="brace",
        interface_patterns=[r"\binterface\s+\w+"],
    ),

    "java": LanguageConfig(
        name="java",
        extensions=[".java"],
        comment_patterns=[_C_LINE_COMMENT, _C_BLOCK_COMMENT],
        string_patterns=[_DOUBLE_QUOTE_STR],
        function_patterns=[
            r"(?:public|private|protected|static|\s)+\s+\w+(?:<[^>]+>)?\s+\w+\s*\(",
        ],
        import_patterns=[r"^import\s+([\w.]+);"],
        export_patterns=[
            r"\bpublic\s+(?:class|interface|enum)\s+(\w+)",
        ],
        complexity_keywords=["if", "else", "case", "for", "while", "catch"],
        complexity_operators=["&&", r"\|\|", r"\?"],
        nesting_mode="brace",
        struct_patterns=[r"\bclass\s+\w+"],
        interface_patterns=[r"\binterface\s+\w+"],
    ),

    "rust": LanguageConfig(
        name="rust",
        extensions=[".rs"],
        comment_patterns=[_C_LINE_COMMENT, _C_BLOCK_COMMENT],
        string_patterns=[_DOUBLE_QUOTE_STR],
        function_patterns=[r"\bfn\s+\w+"],
        import_patterns=[r"^\s*use\s+([\w:]+)"],
        export_patterns=[r"\bpub\s+(?:fn|struct|enum|trait|type|mod)\s+(\w+)"],
        complexity_keywords=["if", "else", "for", "while", "match", "loop"],
        complexity_operators=["&&", r"\|\|"],
        nesting_mode="brace",
        struct_patterns=[r"\bstruct\s+\w+"],
        interface_patterns=[r"\btrait\s+\w+"],
    ),

    "c": LanguageConfig(
        name="c",
        extensions=[".c", ".cpp", ".cc", ".cxx", ".h", ".hpp", ".hxx"],
        comment_patterns=[_C_LINE_COMMENT, _C_BLOCK_COMMENT],
        string_patterns=[_DOUBLE_QUOTE_STR],
        function_patterns=[
            r"(?:^|\n)\s*(?:static|inline|virtual)?\s*\w+\s+\w+\s*\([^)]*\)\s*\{",
        ],
        import_patterns=[r'#include\s*[<"]([^>"]+)[>"]'],
        export_patterns=[],
        complexity_keywords=["if", "else", "case", "for", "while", "do"],
        complexity_operators=["&&", r"\|\|", r"\?"],
        nesting_mode="brace",
        struct_patterns=[r"\bstruct\s+\w+\s*\{"],
        skip_dirs=("build", "cmake-build", ".git", "node_modules",
                   "venv", ".venv", "__pycache__", "third_party"),
    ),

    "ruby": LanguageConfig(
        name="ruby",
        extensions=[".rb"],
        comment_patterns=[_HASH_COMMENT],
        string_patterns=[_DOUBLE_QUOTE_STR, _SINGLE_QUOTE_STR],
        function_patterns=[r"\bdef\s+\w+"],
        import_patterns=[r"^require\s+['\"]([^'\"]+)['\"]"],
        export_patterns=[r"^def\s+([a-zA-Z]\w*)"],
        complexity_keywords=["if", "else", "elsif", "unless", "case", "for", "while", "until", "rescue"],
        complexity_operators=["&&", r"\|\|"],
        nesting_mode="brace",   # Ruby uses end but braces work for nesting estimate
        struct_patterns=[r"\bclass\s+\w+"],
    ),

    "universal": LanguageConfig(
        name="universal",
        extensions=[],  # set dynamically by scanner_factory
        comment_patterns=[_C_LINE_COMMENT, _C_BLOCK_COMMENT, _HASH_COMMENT,
                          _TRIPLE_DQ_STR, _TRIPLE_SQ_STR],
        string_patterns=[_BACKTICK_STR, _DOUBLE_QUOTE_STR, _SINGLE_QUOTE_STR],
        function_patterns=[
            r"\b(?:def|fn|func|function|sub)\s+\w+",
            r"(?:\)\s*=>|\w+\s*=>)\s*\{",
        ],
        import_patterns=[
            r"^import\s+(\S+)",
            r"^from\s+(\S+)\s+import",
            r'#include\s*[<"]([^>"]+)[>"]',
            r"^\s*use\s+([\w:]+)",
            r"""from\s+['"]([^'"]+)['"]""",
            r"""require\s*\(\s*['"]([^'"]+)['"]\s*\)""",
        ],
        export_patterns=[
            r"\bexport\s+(?:default\s+)?(?:function|class|const|let|var|type|interface)\s+(\w+)",
            r"\bpub\s+(?:fn|struct|enum|trait|type|mod)\s+(\w+)",
            r"\bpublic\s+(?:class|interface|enum)\s+(\w+)",
            r"^def\s+([a-zA-Z]\w*)\s*\(",
            r"^class\s+([a-zA-Z]\w*)",
        ],
        complexity_keywords=_UNIVERSAL_COMPLEXITY_KW,
        complexity_operators=_UNIVERSAL_COMPLEXITY_OP + [r"\band\b", r"\bor\b"],
        nesting_mode="both",
    ),
}


def get_language_config(name: str) -> LanguageConfig:
    """Look up a language by name. Raises KeyError if not found."""
    return LANGUAGES[name]


def get_all_known_extensions() -> set:
    """Return the set of all file extensions covered by specific (non-universal) languages."""
    exts = set()
    for name, cfg in LANGUAGES.items():
        if name != "universal":
            exts.update(cfg.extensions)
    return exts
```

#### `src/shannon_insight/analyzers/scanner.py` (~200 lines)

One class that replaces all 8 scanner files.

```python
"""Configurable scanner — a single class that handles any language.

Language-specific behavior is driven entirely by a LanguageConfig
instance (from languages.py). No subclassing needed.
"""

import re
from pathlib import Path
from collections import Counter
from typing import List, Optional

from .base import BaseScanner
from .languages import LanguageConfig
from ..models import FileMetrics
from ..config import AnalysisSettings
from ..exceptions import FileAccessError
from ..logging_config import get_logger

logger = get_logger(__name__)

# Binary extensions — never try to read these as text.
BINARY_EXTENSIONS = frozenset({ ... })  # move from universal_analyzer.py


class ConfigurableScanner(BaseScanner):
    """A single scanner class driven by a LanguageConfig."""

    def __init__(
        self,
        root_dir: str,
        config: LanguageConfig,
        extensions: Optional[List[str]] = None,
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
        if any(name.startswith(p) for p in cfg.skip_file_prefixes):
            return True
        if any(name.endswith(s) for s in cfg.skip_file_suffixes):
            return True
        if name in cfg.skip_file_names:
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
                ast_node_types=Counter(),
                last_modified=filepath.stat().st_mtime,
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

    def _extract_imports(self, content: str) -> List[str]:
        imports = []
        for pattern in self.config.import_patterns:
            imports.extend(m.group(1) for m in re.finditer(pattern, content, re.MULTILINE))
        # Handle Go-style grouped imports
        if self.config.name in ("go", "universal"):
            for m in re.finditer(r'import\s*\([^)]+\)', content, re.DOTALL):
                imports.extend(re.findall(r'"([^"]+)"', m.group(0)))
        return imports

    # ── Exports ────────────────────────────────────────────────

    def _extract_exports(self, content: str) -> List[str]:
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
    def _count_patterns(content: str, patterns: List[str]) -> int:
        return sum(len(re.findall(p, content)) for p in patterns)

    # ── Complexity ─────────────────────────────────────────────

    def _estimate_complexity(self, content: str) -> float:
        complexity = 1.0
        for kw in self.config.complexity_keywords:
            complexity += len(re.findall(rf"\b{kw}\b", content))
        for op in self.config.complexity_operators:
            complexity += len(re.findall(op, content))
        return complexity

    # ── Nesting ────────────────────────────────────────────────

    def _compute_nesting(self, content: str) -> int:
        mode = self.config.nesting_mode
        if mode == "brace":
            return self._max_nesting_depth(content)       # inherited from BaseScanner
        elif mode == "indent":
            return self._indent_nesting(content)
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

    # ── Function sizes ─────────────────────────────────────────
    # (brace-matching with indent fallback — same logic as universal_analyzer.py)

    def _extract_function_sizes(self, content: str) -> List[int]:
        lines = content.split("\n")
        sizes = []
        all_fn_patterns = "|".join(self.config.function_patterns)
        i = 0
        while i < len(lines):
            if re.match(all_fn_patterns, lines[i]):
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

    @staticmethod
    def _indent_fn_size(lines: List[str], start: int) -> int:
        if start >= len(lines):
            return 1
        base_indent = len(lines[start]) - len(lines[start].lstrip())
        count = 1
        for line in lines[start + 1:]:
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
        node_types = Counter()
        node_types["function"] = self._count_functions(content)
        node_types["import"] = len(self._extract_imports(content))
        node_types["export"] = len(self._extract_exports(content))
        # Standard keywords
        for kw in ("if", "for", "while", "return", "class", "try", "match", "switch"):
            node_types[kw] = len(re.findall(rf"\b{kw}\b", content))
        # Extra language-specific
        for name, pattern in self.config.extra_ast_patterns:
            node_types[name] = len(re.findall(pattern, content, re.MULTILINE))
        return node_types
```

### Files to Modify

#### `src/shannon_insight/analyzers/__init__.py`
```python
"""Language analyzers"""

from .base import BaseScanner
from .scanner import ConfigurableScanner
from .languages import LanguageConfig, LANGUAGES, get_language_config, get_all_known_extensions

__all__ = [
    "BaseScanner",
    "ConfigurableScanner",
    "LanguageConfig",
    "LANGUAGES",
    "get_language_config",
    "get_all_known_extensions",
]
```

#### `src/shannon_insight/core.py` — update `_get_scanners()`

Replace all direct scanner class imports with:
```python
from .analyzers import ConfigurableScanner, get_language_config, get_all_known_extensions, LANGUAGES
```

The `explicit_map` becomes:
```python
explicit_map = {
    lang_name: lambda ln=lang_name: [mk_cfg(ln)]
    for lang_name in LANGUAGES if lang_name != "universal"
}
# Aliases
explicit_map["react"] = explicit_map["typescript"]
explicit_map["javascript"] = explicit_map["typescript"]
explicit_map["cpp"] = explicit_map["c"]
explicit_map["universal"] = lambda: [mk_cfg("universal")]
```

Where `mk_cfg` is:
```python
def mk_cfg(lang_name):
    cfg = get_language_config(lang_name)
    scanner = ConfigurableScanner(str(self.root_dir), config=cfg, settings=self.settings)
    return (scanner, lang_name)
```

### Files to Delete

After all tests pass with the new scanner:
- `src/shannon_insight/analyzers/go_analyzer.py`
- `src/shannon_insight/analyzers/python_analyzer.py`
- `src/shannon_insight/analyzers/typescript_analyzer.py`
- `src/shannon_insight/analyzers/java_analyzer.py`
- `src/shannon_insight/analyzers/rust_analyzer.py`
- `src/shannon_insight/analyzers/c_analyzer.py`
- `src/shannon_insight/analyzers/ruby_analyzer.py`
- `src/shannon_insight/analyzers/universal_analyzer.py`

### Testing Strategy

1. Run ALL existing tests first — they must keep passing with the new ConfigurableScanner
2. The existing tests (test_integration.py, test_multilang_primitives.py, test_universal_scanner.py) are the regression suite
3. Add one new test: `test_language_config.py` that verifies each language config produces the same results as the old dedicated scanner on sample files

### TODO Checklist — Phase 1

- [ ] Create `src/shannon_insight/analyzers/languages.py` with all 8 LanguageConfig entries
- [ ] Create `src/shannon_insight/analyzers/scanner.py` with ConfigurableScanner
- [ ] Update `src/shannon_insight/analyzers/__init__.py` to export new classes
- [ ] Update `src/shannon_insight/core.py` to use ConfigurableScanner + language configs
- [ ] Run `python3 -m pytest tests/ -v` — all existing tests must pass
- [ ] Create `tests/test_language_config.py` — verify parity with old scanners
- [ ] Delete the 8 old scanner files
- [ ] Run `python3 -m pytest tests/ -v` — still all pass
- [ ] Verify: `shannon-insight --language go test_codebase` works
- [ ] Verify: `shannon-insight --language auto test_codebase` works
- [ ] Verify: `shannon-insight --language universal .` works

---

## Phase 2: Split `core.py`

### Goal
`core.py` (352 lines) currently does 3 things: language detection, pipeline orchestration, and progress display. Split into 3 focused files.

### Files to Create

#### `src/shannon_insight/core/scanner_factory.py` (~80 lines)

Handles language detection and scanner construction.

```python
"""Scanner factory — resolves language setting to scanner instances."""

from pathlib import Path
from typing import List, Tuple

from ..analyzers import ConfigurableScanner, get_language_config, get_all_known_extensions, LANGUAGES
from ..analyzers.scanner import BINARY_EXTENSIONS
from ..config import AnalysisSettings
from ..logging_config import get_logger

logger = get_logger(__name__)

# Directories to skip during auto-detection
_SKIP_DIRS = {"venv", ".venv", "node_modules", "__pycache__", ".git", "dist", "build", "target"}


class ScannerFactory:
    """Resolves a language setting into a list of (scanner, lang_name) tuples."""

    def __init__(self, root_dir: Path, settings: AnalysisSettings):
        self.root_dir = root_dir
        self.settings = settings

    def create(self, language: str) -> Tuple[List[Tuple], List[str]]:
        """Return (scanners, detected_languages)."""
        if language != "auto":
            cfg = get_language_config(language)
            scanner = ConfigurableScanner(str(self.root_dir), config=cfg, settings=self.settings)
            return [(scanner, language)], [language]

        return self._auto_detect()

    def _auto_detect(self) -> Tuple[List[Tuple], List[str]]:
        ...  # same logic as current _get_scanners auto-detect block
```

#### `src/shannon_insight/core/progress.py` (~40 lines)

Thin wrapper around Rich progress bar — or a no-op for tests.

```python
"""Progress reporting — wraps Rich or runs silently."""

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn, TextColumn


class ProgressReporter:
    """Rich progress bar wrapper."""

    def __init__(self, console: Console):
        self.console = console

    def run(self, callback):
        """Execute callback(progress) inside a Rich progress context."""
        with Progress(
            SpinnerColumn(), TextColumn("[progress.description]{task.description}"),
            BarColumn(), TaskProgressColumn(), TimeElapsedColumn(),
            console=self.console, transient=False,
        ) as progress:
            return callback(progress)


class SilentReporter:
    """No-op reporter for tests and --quiet mode."""

    def run(self, callback):
        return callback(None)
```

#### `src/shannon_insight/core/pipeline.py` (~80 lines)

The pipeline orchestrator — thin, just wires stages together.

```python
"""Analysis pipeline — runs the 5-layer analysis."""

from typing import List, Tuple, Dict

from ..models import FileMetrics, AnomalyReport
from ..primitives import PrimitiveExtractor, AnomalyDetector, SignalFusion, RecommendationEngine
from ..cache import AnalysisCache
from ..config import AnalysisSettings


class AnalysisPipeline:
    """Runs layers 2-5 on a group of files."""

    def __init__(self, settings: AnalysisSettings, cache=None, config_hash="", root_dir=""):
        self.settings = settings
        self.cache = cache
        self.config_hash = config_hash
        self.root_dir = root_dir

    def run(self, files: List[FileMetrics]) -> List[AnomalyReport]:
        """Run extract → detect → fuse → recommend."""
        extractor = PrimitiveExtractor(files, cache=self.cache, config_hash=self.config_hash, root_dir=self.root_dir)
        primitives = extractor.extract_all()

        detector = AnomalyDetector(primitives, threshold=self.settings.z_score_threshold)
        normalized = detector.normalize()
        anomalies = detector.detect_anomalies(normalized)

        fusion = SignalFusion(primitives, normalized, weights=self.settings.fusion_weights)
        fused_scores = fusion.fuse()

        engine = RecommendationEngine(files, primitives, normalized, anomalies, fused_scores, root_dir=self.root_dir)
        return engine.generate()
```

#### `src/shannon_insight/core/__init__.py`
```python
from .analyzer import CodebaseAnalyzer

__all__ = ["CodebaseAnalyzer"]
```

#### `src/shannon_insight/core/analyzer.py` (~120 lines)

The slim orchestrator that composes the above.

```python
"""Main entry point — composes scanner_factory + pipeline + progress."""

from .scanner_factory import ScannerFactory
from .pipeline import AnalysisPipeline
from .progress import ProgressReporter

class CodebaseAnalyzer:
    SUPPORTED_LANGUAGES = set(LANGUAGES.keys()) | {"auto", "react", "javascript", "cpp"}

    def __init__(self, root_dir, language="auto", settings=None):
        ...

    def analyze(self):
        factory = ScannerFactory(self.root_dir, self.settings)
        scanners, detected = factory.create(self.language)
        # ... scan files ...
        pipeline = AnalysisPipeline(self.settings, ...)
        # ... run per language group ...
```

### Files to Delete
- `src/shannon_insight/core.py` (replaced by `core/` package)

### TODO Checklist — Phase 2

- [ ] Create `src/shannon_insight/core/` directory
- [ ] Create `src/shannon_insight/core/__init__.py`
- [ ] Create `src/shannon_insight/core/scanner_factory.py`
- [ ] Create `src/shannon_insight/core/progress.py`
- [ ] Create `src/shannon_insight/core/pipeline.py`
- [ ] Create `src/shannon_insight/core/analyzer.py` (move logic from old core.py)
- [ ] Update `src/shannon_insight/__init__.py` import (from .core import CodebaseAnalyzer)
- [ ] Run `python3 -m pytest tests/ -v` — all pass
- [ ] Delete `src/shannon_insight/core.py`
- [ ] Run `python3 -m pytest tests/ -v` — still all pass

---

## Phase 3: Composable Pipeline Stages

### Goal
Make the pipeline stages independent and composable. Enable partial runs, custom stages, and caching between stages.

### Key Design

Each stage is a callable with a standard signature:

```python
class Stage:
    name: str
    def run(self, context: PipelineContext) -> PipelineContext:
        """Receives context, adds results, returns updated context."""
```

`PipelineContext` is a dict-like object that flows through stages:

```python
@dataclass
class PipelineContext:
    files: List[FileMetrics]
    settings: AnalysisSettings
    root_dir: str
    cache: Optional[AnalysisCache] = None
    config_hash: str = ""

    # Filled by stages as they run
    primitives: Optional[Dict[str, Primitives]] = None
    normalized: Optional[Dict[str, Primitives]] = None
    anomalies: Optional[Dict[str, List[str]]] = None
    fused_scores: Optional[Dict[str, Tuple[float, float]]] = None
    reports: Optional[List[AnomalyReport]] = None
```

### Files to Create

#### `src/shannon_insight/primitives/stages.py` (~120 lines)

```python
"""Pipeline stages — each is an independent, composable unit."""

from ..models import PipelineContext


class ExtractStage:
    name = "extract"

    def run(self, ctx: PipelineContext) -> PipelineContext:
        from .extractor import PrimitiveExtractor
        extractor = PrimitiveExtractor(ctx.files, cache=ctx.cache,
                                       config_hash=ctx.config_hash,
                                       root_dir=ctx.root_dir)
        ctx.primitives = extractor.extract_all()
        return ctx


class DetectStage:
    name = "detect"

    def run(self, ctx: PipelineContext) -> PipelineContext:
        from .detector import AnomalyDetector
        detector = AnomalyDetector(ctx.primitives, threshold=ctx.settings.z_score_threshold)
        ctx.normalized = detector.normalize()
        ctx.anomalies = detector.detect_anomalies(ctx.normalized)
        return ctx


class FuseStage:
    name = "fuse"

    def run(self, ctx: PipelineContext) -> PipelineContext:
        from .fusion import SignalFusion
        fusion = SignalFusion(ctx.primitives, ctx.normalized, weights=ctx.settings.fusion_weights)
        ctx.fused_scores = fusion.fuse()
        return ctx


class RecommendStage:
    name = "recommend"

    def run(self, ctx: PipelineContext) -> PipelineContext:
        from .recommendations import RecommendationEngine
        engine = RecommendationEngine(
            ctx.files, ctx.primitives, ctx.normalized,
            ctx.anomalies, ctx.fused_scores, root_dir=ctx.root_dir,
        )
        ctx.reports = engine.generate()
        return ctx
```

#### Update `src/shannon_insight/core/pipeline.py`

```python
"""Composable pipeline runner."""

from typing import List, Optional
from ..models import PipelineContext
from ..primitives.stages import ExtractStage, DetectStage, FuseStage, RecommendStage

# Default stage order
DEFAULT_STAGES = [ExtractStage(), DetectStage(), FuseStage(), RecommendStage()]


class AnalysisPipeline:
    def __init__(self, stages: Optional[List] = None):
        self.stages = stages or list(DEFAULT_STAGES)

    def add_stage(self, stage, after: Optional[str] = None):
        """Insert a custom stage after a named stage (or at the end)."""
        if after is None:
            self.stages.append(stage)
            return
        for i, s in enumerate(self.stages):
            if s.name == after:
                self.stages.insert(i + 1, stage)
                return
        self.stages.append(stage)

    def run(self, ctx: PipelineContext) -> PipelineContext:
        for stage in self.stages:
            ctx = stage.run(ctx)
        return ctx
```

### Usage Example

```python
# Default: run all stages
pipeline = AnalysisPipeline()
ctx = pipeline.run(PipelineContext(files=files, settings=settings, ...))

# Partial: extract only (for benchmarking)
pipeline = AnalysisPipeline(stages=[ExtractStage()])
ctx = pipeline.run(PipelineContext(files=files, settings=settings, ...))

# Custom: add a security stage
pipeline = AnalysisPipeline()
pipeline.add_stage(SecurityStage(), after="extract")
ctx = pipeline.run(...)
```

### TODO Checklist — Phase 3

- [ ] Add `PipelineContext` to `src/shannon_insight/models.py`
- [ ] Create `src/shannon_insight/primitives/stages.py`
- [ ] Update `src/shannon_insight/core/pipeline.py` to use composable stages
- [ ] Update `src/shannon_insight/core/analyzer.py` to construct PipelineContext
- [ ] Run `python3 -m pytest tests/ -v` — all pass
- [ ] Add test: partial pipeline (extract-only) produces primitives without reports
- [ ] Add test: custom stage can be inserted and receives context

---

## Phase 4: Plugin System for Primitives

### Goal
Each primitive becomes a self-contained plugin class. Adding a new primitive = creating one file. No modifications to extractor.py needed.

### Key Design

```python
class PrimitivePlugin(ABC):
    """Base class for all primitive plugins."""

    name: str            # "structural_entropy"
    display_name: str    # "Compression Complexity"
    short_name: str      # "compress"
    description: str
    direction: str       # "high_is_bad" | "low_is_bad" | "both_extreme_bad"
    default_weight: float

    @abstractmethod
    def compute(self, files: List[FileMetrics], root_dir: Path) -> Dict[str, float]:
        """Compute this primitive for all files. Returns {path: value}."""

    @abstractmethod
    def interpret(self, value: float) -> str:
        """Human-readable interpretation of a raw value."""
```

### Files to Create

#### `src/shannon_insight/primitives/base.py` (~30 lines)

```python
"""Base class for primitive plugins."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List
from ..models import FileMetrics


class PrimitivePlugin(ABC):
    name: str
    display_name: str
    short_name: str
    description: str
    direction: str
    default_weight: float

    @abstractmethod
    def compute(self, files: List[FileMetrics], root_dir: Path) -> Dict[str, float]:
        ...

    @abstractmethod
    def interpret(self, value: float) -> str:
        ...
```

#### `src/shannon_insight/primitives/plugins/compression.py` (~50 lines)

```python
"""Structural entropy via compression ratio."""

from pathlib import Path
from typing import Dict, List

from ..base import PrimitivePlugin
from ...models import FileMetrics
from ...math import Compression


class CompressionPrimitive(PrimitivePlugin):
    name = "structural_entropy"
    display_name = "Compression Complexity"
    short_name = "compress"
    description = "Compression-based complexity (Kolmogorov approximation)"
    direction = "both_extreme_bad"
    default_weight = 0.20

    def compute(self, files: List[FileMetrics], root_dir: Path) -> Dict[str, float]:
        result = {}
        for file in files:
            file_path = root_dir / file.path if not Path(file.path).is_absolute() else Path(file.path)
            try:
                with open(file_path, 'rb') as f:
                    content = f.read()
                result[file.path] = Compression.compression_ratio(content)
            except Exception:
                result[file.path] = 0.0
        return result

    def interpret(self, v: float) -> str:
        if v < 0.20: return "highly repetitive (duplication?)"
        elif v < 0.45: return "normal complexity"
        elif v < 0.65: return "dense/complex"
        return "very dense"
```

#### `src/shannon_insight/primitives/plugins/centrality.py` (~60 lines)

```python
"""Network centrality via PageRank on dependency graph."""

from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set

from ..base import PrimitivePlugin
from ...models import FileMetrics


class CentralityPrimitive(PrimitivePlugin):
    name = "network_centrality"
    display_name = "Network Centrality"
    short_name = "centrality"
    description = "Importance in dependency graph (PageRank)"
    direction = "high_is_bad"
    default_weight = 0.25

    # Skip stdlib / well-known third-party names when building the graph.
    _SKIP_NAMES = frozenset({
        "abc", "ast", "asyncio", "base64", "bisect", "builtins", "calendar",
        "cmath", "codecs", "collections", "concurrent", "contextlib", "copy",
        "csv", "ctypes", "dataclasses", "datetime", "decimal", "difflib",
        "email", "enum", "errno", "fcntl", "fileinput", "fnmatch", "fractions",
        "ftplib", "functools", "gc", "getpass", "glob", "gzip", "hashlib",
        "heapq", "hmac", "html", "http", "importlib", "inspect", "io",
        "itertools", "json", "logging", "lzma", "math", "mimetypes",
        "multiprocessing", "operator", "os", "pathlib", "pickle", "platform",
        "pprint", "queue", "random", "re", "secrets", "select", "shelve",
        "shlex", "shutil", "signal", "socket", "sqlite3", "ssl",
        "statistics", "string", "struct", "subprocess", "sys", "tempfile",
        "textwrap", "threading", "time", "timeit", "tkinter", "token",
        "tomllib", "traceback", "types", "typing", "unicodedata", "unittest",
        "urllib", "uuid", "venv", "warnings", "weakref", "xml", "zipfile",
        "zlib",
        # Third-party
        "numpy", "np", "pandas", "pd", "scipy", "sklearn", "matplotlib",
        "plt", "seaborn", "requests", "flask", "django", "fastapi",
        "pydantic", "typer", "click", "rich", "diskcache", "pytest",
        "setuptools", "wheel", "pip", "pkg_resources",
    })

    def compute(self, files: List[FileMetrics], root_dir: Path) -> Dict[str, float]:
        graph = self._build_graph(files)
        return self._pagerank(files, graph)

    def _build_graph(self, files: List[FileMetrics]) -> Dict[str, Set[str]]:
        graph: Dict[str, Set[str]] = defaultdict(set)
        file_by_name = {Path(f.path).stem: f.path for f in files}

        for file in files:
            for imp in file.imports:
                pkg = imp.split("/")[-1].split(".")[-1]
                if pkg in self._SKIP_NAMES or pkg.startswith(".") or pkg == "":
                    continue
                if pkg in file_by_name and file_by_name[pkg] != file.path:
                    graph[file.path].add(file_by_name[pkg])
        return dict(graph)

    @staticmethod
    def _pagerank(files: List[FileMetrics], graph: Dict[str, Set[str]]) -> Dict[str, float]:
        scores = {f.path: 1.0 for f in files}
        damping, iterations = 0.85, 20

        incoming: Dict[str, Set[str]] = defaultdict(set)
        for src, targets in graph.items():
            for tgt in targets:
                incoming[tgt].add(src)

        for _ in range(iterations):
            new = {}
            for f in files:
                rank = 1 - damping
                for src in incoming.get(f.path, []):
                    out = len(graph.get(src, []))
                    if out > 0:
                        rank += damping * (scores[src] / out)
                new[f.path] = rank
            scores = new

        mx = max(scores.values()) if scores else 1.0
        if mx > 0:
            scores = {k: v / mx for k, v in scores.items()}
        return scores

    def interpret(self, v: float) -> str:
        if v > 0.5:
            return "high = heavily depended on"
        return "within typical range"
```

#### `src/shannon_insight/primitives/plugins/volatility.py` (~35 lines)

```python
"""Churn volatility via filesystem modification timestamps."""

from datetime import datetime
from pathlib import Path
from typing import Dict, List

from ..base import PrimitivePlugin
from ...models import FileMetrics


class VolatilityPrimitive(PrimitivePlugin):
    name = "churn_volatility"
    display_name = "Churn Volatility"
    short_name = "churn"
    description = "Instability of change patterns"
    direction = "high_is_bad"
    default_weight = 0.20

    def compute(self, files: List[FileMetrics], root_dir: Path) -> Dict[str, float]:
        now = datetime.now().timestamp()
        ages = [now - f.last_modified for f in files]
        if not ages:
            return {}
        max_age = max(ages)
        return {
            f.path: (1 - (now - f.last_modified) / max_age) if max_age > 0 else 0
            for f in files
        }

    def interpret(self, v: float) -> str:
        if v > 0.5:
            return "high = frequently changed"
        return "within typical range"
```

#### `src/shannon_insight/primitives/plugins/coherence.py` (~40 lines)

```python
"""Semantic coherence via identifier token analysis."""

from pathlib import Path
from typing import Dict, List

from ..base import PrimitivePlugin
from ...models import FileMetrics
from ...math import IdentifierAnalyzer


class CoherencePrimitive(PrimitivePlugin):
    name = "semantic_coherence"
    display_name = "Identifier Coherence"
    short_name = "coherence"
    description = "Responsibility focus (identifier clustering)"
    direction = "both_extreme_bad"
    default_weight = 0.15

    def compute(self, files: List[FileMetrics], root_dir: Path) -> Dict[str, float]:
        result = {}
        for file in files:
            file_path = root_dir / file.path if not Path(file.path).is_absolute() else Path(file.path)
            try:
                with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
                tokens = IdentifierAnalyzer.extract_identifier_tokens(content)
                result[file.path] = IdentifierAnalyzer.compute_coherence(tokens)
            except Exception:
                result[file.path] = 1.0  # default to coherent on failure
        return result

    def interpret(self, v: float) -> str:
        if v < 0.30:
            return "mixed responsibilities"
        elif v < 0.70:
            return "somewhat focused"
        return "highly focused"
```

#### `src/shannon_insight/primitives/plugins/cognitive_load.py` (~65 lines)

```python
"""Cognitive load using Gini-enhanced formula with compression fallback."""

from pathlib import Path
from typing import Dict, List

from ..base import PrimitivePlugin
from ...models import FileMetrics
from ...math import Compression, Gini


class CognitiveLoadPrimitive(PrimitivePlugin):
    name = "cognitive_load"
    display_name = "Cognitive Load"
    short_name = "cog.load"
    description = "Mental effort to understand (Gini-enhanced)"
    direction = "high_is_bad"
    default_weight = 0.20

    def compute(self, files: List[FileMetrics], root_dir: Path) -> Dict[str, float]:
        loads: Dict[str, float] = {}

        for file in files:
            concepts = file.functions + file.structs + file.interfaces
            nesting_factor = 1 + file.nesting_depth / 10

            if concepts > 0:
                base_load = concepts * file.complexity_score * nesting_factor
            else:
                file_path = root_dir / file.path if not Path(file.path).is_absolute() else Path(file.path)
                try:
                    with open(file_path, 'rb') as f:
                        raw = f.read()
                    ratio = Compression.compression_ratio(raw)
                except Exception:
                    ratio = 0.0
                base_load = ratio * (file.lines / 100.0) * file.complexity_score * nesting_factor

            if file.function_sizes and len(file.function_sizes) > 1:
                try:
                    gini = Gini.gini_coefficient(file.function_sizes)
                except ValueError:
                    gini = 0.0
                concentration = 1.0 + gini
            else:
                concentration = 1.0

            loads[file.path] = base_load * concentration

        # Normalize to [0, 1]
        if loads:
            mx = max(loads.values())
            if mx > 0:
                loads = {k: v / mx for k, v in loads.items()}

        return loads

    def interpret(self, v: float) -> str:
        if v > 0.6:
            return "high = hard to understand"
        return "within typical range"
```

#### Update `src/shannon_insight/primitives/registry.py`

Auto-discover plugins:

```python
"""Registry — auto-discovers all PrimitivePlugin subclasses."""

from .base import PrimitivePlugin
from .plugins import compression, centrality, volatility, coherence, cognitive_load

_ALL_PLUGINS = [
    compression.CompressionPrimitive(),
    centrality.CentralityPrimitive(),
    volatility.VolatilityPrimitive(),
    coherence.CoherencePrimitive(),
    cognitive_load.CognitiveLoadPrimitive(),
]

def get_plugins() -> list[PrimitivePlugin]:
    return list(_ALL_PLUGINS)

def get_plugin(name: str) -> PrimitivePlugin:
    for p in _ALL_PLUGINS:
        if p.name == name:
            return p
    raise KeyError(f"Unknown primitive: {name!r}")
```

#### Update `src/shannon_insight/primitives/extractor.py`

Replace hardcoded `_compute_<name>` methods:

```python
class PrimitiveExtractor:
    def extract_all_dict(self) -> Dict[str, PrimitiveValues]:
        plugins = get_plugins()
        per_primitive = {}
        for plugin in plugins:
            per_primitive[plugin.name] = plugin.compute(self.files, self.root_dir)
        # Pivot: file -> {prim_name: value}
        ...
```

### TODO Checklist — Phase 4

- [ ] Create `src/shannon_insight/primitives/base.py` with PrimitivePlugin ABC
- [ ] Create `src/shannon_insight/primitives/plugins/` directory
- [ ] Create `src/shannon_insight/primitives/plugins/__init__.py`
- [ ] Create `src/shannon_insight/primitives/plugins/compression.py`
- [ ] Create `src/shannon_insight/primitives/plugins/centrality.py`
- [ ] Create `src/shannon_insight/primitives/plugins/volatility.py`
- [ ] Create `src/shannon_insight/primitives/plugins/coherence.py`
- [ ] Create `src/shannon_insight/primitives/plugins/cognitive_load.py`
- [ ] Update `src/shannon_insight/primitives/registry.py` to use plugins
- [ ] Update `src/shannon_insight/primitives/extractor.py` to use plugin.compute()
- [ ] Run `python3 -m pytest tests/ -v` — all pass
- [ ] Add test: creating a custom PrimitivePlugin and registering it works
- [ ] Delete old `_compute_*` methods from extractor.py

---

## Phase 5: Refactor CLI into Subcommands

### Goal
Break the 180-line `main()` function into focused subcommands. Each command handles one concern.

### Target Structure

```
shannon-insight analyze .                    # main analysis (default)
shannon-insight analyze . --language go      # explicit language
shannon-insight analyze . --format json      # output format
shannon-insight diff . --base-ref main       # diff mode
shannon-insight explain . --file complex.go  # deep-dive
shannon-insight baseline .                   # save baseline (existing)
shannon-insight cache-info                   # cache info (existing)
shannon-insight cache-clear                  # cache clear (existing)
```

### Files to Create

#### `src/shannon_insight/cli/` directory

```
cli/
├── __init__.py      — app = typer.Typer(), register subcommands
├── analyze.py       — @app.command() for main analysis (~80 lines)
├── diff.py          — @app.command() for diff mode (~40 lines)
├── explain.py       — @app.command() for explain mode (~30 lines)
├── baseline.py      — @app.command() for baseline (move existing)
├── cache.py         — @app.command() for cache-info/clear (move existing)
└── _common.py       — shared helpers (settings loading, error handling)
```

#### `src/shannon_insight/cli/__init__.py`

```python
"""CLI entry point — registers all subcommands."""

import typer

app = typer.Typer(
    name="shannon-insight",
    help="Shannon Insight - Multi-Signal Codebase Quality Analyzer",
    add_completion=False,
    invoke_without_command=True,
)

from .analyze import analyze    # noqa
from .diff import diff          # noqa
from .explain import explain    # noqa
from .baseline import baseline  # noqa
from .cache import cache_info, cache_clear  # noqa
```

#### `src/shannon_insight/cli/_common.py` (~40 lines)

```python
"""Shared CLI helpers."""

from pathlib import Path
from typing import Optional
from rich.console import Console

from ..config import load_settings, AnalysisSettings
from ..logging_config import setup_logging

console = Console()


def resolve_settings(
    config: Optional[Path] = None,
    threshold: Optional[float] = None,
    no_cache: bool = False,
    workers: Optional[int] = None,
    verbose: bool = False,
    quiet: bool = False,
) -> AnalysisSettings:
    """Build settings from CLI options."""
    overrides = {}
    if threshold is not None:
        overrides["z_score_threshold"] = threshold
    if no_cache:
        overrides["enable_cache"] = False
    if workers is not None:
        overrides["parallel_workers"] = workers
    if verbose:
        overrides["verbose"] = True
    if quiet:
        overrides["quiet"] = True
    return load_settings(config_file=config, **overrides)
```

#### `src/shannon_insight/cli/analyze.py` (~80 lines)

```python
"""Main analysis command."""

import typer
from pathlib import Path
from typing import Optional
from datetime import datetime

from . import app
from ._common import console, resolve_settings
from ..core import CodebaseAnalyzer
from ..formatters import get_formatter, JsonFormatter
from ..exceptions import ShannonInsightError
from ..logging_config import setup_logging


@app.callback(invoke_without_command=True)
def analyze(
    path: Path = typer.Argument(Path("."), ...),
    language: str = typer.Option("auto", "--language", "-l", ...),
    top: int = typer.Option(15, "--top", "-t", ...),
    output: Optional[Path] = typer.Option(None, "--output", "-o", ...),
    fmt: str = typer.Option("rich", "--format", "-f", ...),
    fail_above: Optional[float] = typer.Option(None, "--fail-above", ...),
    # ... other options ...
):
    """Analyze codebase quality."""
    settings = resolve_settings(...)
    analyzer = CodebaseAnalyzer(root_dir=path, language=language, settings=settings)
    reports, context = analyzer.analyze()
    context.top_n = top

    formatter = get_formatter(fmt)
    formatter.render(reports, context)

    # JSON export
    if output or fmt == "rich":
        ...

    # CI gating
    if fail_above is not None:
        ...
```

### Backward Compatibility

The default command (no subcommand) runs `analyze`, so `shannon-insight .` still works.

### TODO Checklist — Phase 5

- [ ] Create `src/shannon_insight/cli/` directory
- [ ] Create `src/shannon_insight/cli/__init__.py` with app and subcommand registration
- [ ] Create `src/shannon_insight/cli/_common.py` with shared helpers
- [ ] Create `src/shannon_insight/cli/analyze.py` — extract from main()
- [ ] Create `src/shannon_insight/cli/diff.py` — extract diff mode
- [ ] Create `src/shannon_insight/cli/explain.py` — extract explain mode
- [ ] Create `src/shannon_insight/cli/baseline.py` — move existing command
- [ ] Create `src/shannon_insight/cli/cache.py` — move existing commands
- [ ] Update `pyproject.toml` entry point if needed
- [ ] Run `python3 -m pytest tests/ -v` — all pass
- [ ] Test: `shannon-insight .` still works (default = analyze)
- [ ] Test: `shannon-insight --version` still works
- [ ] Test: `shannon-insight --help` shows subcommands
- [ ] Delete `src/shannon_insight/cli.py`

---

## Execution Order & Dependencies

```
Phase 1 (scanners)  ──►  Phase 2 (core.py split)  ──►  Phase 3 (pipeline)
                                                              │
                                                              ▼
                                                     Phase 4 (plugins)

Phase 5 (CLI) can run independently at any time.
```

- Phase 1 is standalone — no dependencies
- Phase 2 depends on Phase 1 (imports change)
- Phase 3 depends on Phase 2 (pipeline.py already exists)
- Phase 4 depends on Phase 3 (uses PipelineContext)
- Phase 5 is independent — can be done any time

---

## Agent Prompt

When implementing any phase, use this prompt:

```
You are implementing Phase N of the Shannon Insight rearchitecture.

RULES:
- Do NOT use agents or subagents. Do all work directly.
- Do NOT read files you don't need. The plan doc contains all necessary
  code snippets and file contents.
- Read ONLY: the plan doc, the specific file being modified (to find the
  exact edit point), and test files if a test fails.
- Write code that reads like a production line: clear inputs, clear
  outputs, one responsibility per function/class.
- After EACH file change, run: python3 -m pytest tests/ -v
- If tests fail, fix immediately before moving to the next file.
- Do not add docstrings, type annotations, or comments beyond what the
  plan specifies. Keep it minimal.
- Commit after each phase is complete and all tests pass.

PHASE N STEPS:
(copy the TODO checklist for that phase here)
```

---

## Success Metrics

After all 5 phases:

| Metric | Before | After |
|--------|--------|-------|
| Scanner files | 8 files, ~1,626 lines | 2 files, ~450 lines |
| core.py | 1 file, 352 lines | 4 files, ~320 lines total |
| Lines to add a new language | ~160 (new file + class) | ~20 (dict entry) |
| Lines to add a new primitive | ~50 (edit 2 files) | ~50 (1 new file, no edits) |
| Lines to add a CLI command | edit main() | 1 new file |
| cli.py main() | 180 lines, 6 concerns | ~80 lines, 1 concern |
| Pipeline extensibility | Hardwired 4 stages | Composable, pluggable stages |
