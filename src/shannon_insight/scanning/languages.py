"""Language configurations — the single source of truth for all language patterns.

Adding a new language:
  1. Add a LanguageConfig entry to LANGUAGES below.
  2. That's it. The ConfigurableScanner picks it up automatically.
"""

import re as _re
from dataclasses import dataclass, field


@dataclass(frozen=True)
class LanguageConfig:
    """Everything the scanner needs to know about a language."""

    name: str
    extensions: list[str]

    # Comment syntax to strip before token counting.
    # Each tuple is (pattern, flags) passed to re.sub.
    comment_patterns: list[tuple[str, int]] = field(default_factory=list)

    # String literal patterns to strip before token counting.
    string_patterns: list[str] = field(default_factory=list)

    # Function detection regex(es). Matches are counted.
    function_patterns: list[str] = field(default_factory=list)

    # Import detection regex(es). Group 1 is captured as the import name.
    import_patterns: list[str] = field(default_factory=list)

    # Export detection regex(es). Group 1 is captured as the export name.
    export_patterns: list[str] = field(default_factory=list)

    # Complexity keywords. Each occurrence adds 1.
    complexity_keywords: list[str] = field(default_factory=list)

    # Complexity operators (not word-boundary). Each occurrence adds 1.
    complexity_operators: list[str] = field(default_factory=list)

    # Nesting mode: "brace" (count {}), "indent" (count indentation),
    # or "both" (take max of brace and indent depth).
    nesting_mode: str = "brace"

    # Struct/interface patterns (language-specific, empty = returns 0)
    struct_patterns: list[str] = field(default_factory=list)
    interface_patterns: list[str] = field(default_factory=list)

    # Extra AST node type patterns: list of (node_name, pattern).
    extra_ast_patterns: list[tuple[str, str]] = field(default_factory=list)

    # Skip patterns: directory names and file prefixes to ignore.
    skip_dirs: tuple[str, ...] = (
        "vendor",
        "node_modules",
        "venv",
        ".venv",
        "__pycache__",
        ".git",
        ".tox",
        ".mypy_cache",
        ".pytest_cache",
        "dist",
        "build",
        "target",
        ".eggs",
        "third_party",
    )
    skip_file_prefixes: tuple[str, ...] = ("test_",)
    skip_file_suffixes: tuple[str, ...] = ()
    skip_file_names: tuple[str, ...] = ()
    skip_path_fragments: tuple[str, ...] = ()


# ── Re-usable building blocks ──────────────────────────────────────

_C_LINE_COMMENT = (r"//.*", 0)
_C_BLOCK_COMMENT = (r"/\*.*?\*/", _re.DOTALL)
_HASH_COMMENT = (r"#.*", 0)
_TRIPLE_DQ_STR = (r'""".*?"""', _re.DOTALL)
_TRIPLE_SQ_STR = (r"'''.*?'''", _re.DOTALL)

_DOUBLE_QUOTE_STR = r'"[^"]*"'
_SINGLE_QUOTE_STR = r"'[^']*'"
_BACKTICK_STR = r"`[^`]*`"


# ── Language definitions ───────────────────────────────────────────

LANGUAGES = {
    "go": LanguageConfig(
        name="go",
        extensions=[".go"],
        comment_patterns=[_C_LINE_COMMENT, _C_BLOCK_COMMENT],
        string_patterns=[_BACKTICK_STR, _DOUBLE_QUOTE_STR],
        function_patterns=[r"\bfunc\s+\w+\s*\("],
        import_patterns=[
            r'import\s+"([^"]+)"',
        ],
        export_patterns=[
            r"^func\s+([A-Z]\w*)\s*\(",
            r"^type\s+([A-Z]\w*)\s+",
            r"^const\s+([A-Z]\w*)\s*[=\n]",
            r"^var\s+([A-Z]\w*)\s*[=\n]",
        ],
        complexity_keywords=["if", "else", "case", "for", "range", "select"],
        complexity_operators=["&&", r"\|\|"],
        nesting_mode="brace",
        struct_patterns=[r"\btype\s+\w+\s+struct\s*\{"],
        interface_patterns=[r"\btype\s+\w+\s+interface\s*\{"],
        skip_dirs=("vendor", "venv", ".venv", "__pycache__", ".git", ".tox", ".mypy_cache"),
        skip_file_prefixes=(),
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
        complexity_keywords=["if", "elif", "else", "for", "while", "except", "and", "or", "with"],
        complexity_operators=[],
        nesting_mode="indent",
        struct_patterns=[r"\bclass\s+\w+"],
        skip_dirs=(
            "venv",
            ".venv",
            "__pycache__",
            ".git",
            ".tox",
            ".mypy_cache",
            ".pytest_cache",
            "node_modules",
            "dist",
            "build",
            ".eggs",
        ),
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
            r"const\s+\w+\s*=\s*(?:\([^)]*\)|[a-zA-Z_]\w*)\s*=>",
            r"const\s+\w+\s*=\s*function",
        ],
        import_patterns=[
            r"""import\s+.*?\s+from\s+['"]([^'"]+)['"]""",
            r"""import\s+['"]([^'"]+)['"]""",
        ],
        export_patterns=[
            r"\bexport\s+(?:default\s+)?(?:function|class|const|let|var|type|interface)\s+(\w+)",
        ],
        complexity_keywords=["if", "else", "case", "while", "for", "catch"],
        complexity_operators=["&&", r"\|\|", r"\?"],
        nesting_mode="brace",
        interface_patterns=[r"\binterface\s+\w+"],
        struct_patterns=[r"const\s+[A-Z]\w+\s*:\s*React\.FC"],
        skip_dirs=(
            "node_modules",
            "dist",
            "build",
            "venv",
            ".venv",
            "__pycache__",
            ".git",
            ".tox",
            ".mypy_cache",
        ),
        skip_file_prefixes=(),
        extra_ast_patterns=[
            ("jsx", r"<[A-Z]\w+"),
            ("hook", r"\buse[A-Z]\w+\s*\("),
        ],
    ),
    "java": LanguageConfig(
        name="java",
        extensions=[".java"],
        comment_patterns=[_C_LINE_COMMENT, _C_BLOCK_COMMENT],
        string_patterns=[_DOUBLE_QUOTE_STR],
        function_patterns=[
            r"(?:public|private|protected|static|\s)+\s+\w+(?:<[^>]+>)?\s+\w+\s*\(",
        ],
        import_patterns=[r"^import\s+(?:static\s+)?([^;]+);"],
        export_patterns=[
            r"public\s+(?:static\s+)?(?:final\s+)?(?:class|interface|enum|record)\s+(\w+)",
            r"public\s+(?:static\s+)?(?:final\s+)?(?:synchronized\s+)?\w+(?:<[^>]+>)?\s+(\w+)\s*\(",
        ],
        complexity_keywords=["if", "else", "case", "for", "while", "catch"],
        complexity_operators=["&&", r"\|\|", r"\?"],
        nesting_mode="brace",
        struct_patterns=[r"\bclass\s+\w+"],
        interface_patterns=[r"\binterface\s+\w+"],
        skip_dirs=(
            "target",
            "build",
            ".gradle",
            ".mvn",
            ".git",
            "node_modules",
            "venv",
            ".venv",
            "__pycache__",
        ),
        skip_file_prefixes=(),
        skip_file_suffixes=("Test.java", "Tests.java", "IT.java"),
        skip_path_fragments=("/test/", "/tests/"),
        extra_ast_patterns=[
            ("throw", r"\bthrow\b"),
            ("try", r"\btry\s*\{"),
            ("annotation", r"^\s*@\w+"),
        ],
    ),
    "rust": LanguageConfig(
        name="rust",
        extensions=[".rs"],
        comment_patterns=[_C_LINE_COMMENT, _C_BLOCK_COMMENT],
        string_patterns=[_DOUBLE_QUOTE_STR],
        function_patterns=[r"\bfn\s+\w+"],
        import_patterns=[
            r"^use\s+([^;{]+)",
            r"^extern\s+crate\s+(\w+)",
        ],
        export_patterns=[r"\bpub\s+(?:fn|struct|enum|trait|type|const|mod|static)\s+(\w+)"],
        complexity_keywords=["if", "else", "match", "for", "while", "loop"],
        complexity_operators=["&&", r"\|\|", r"\?"],
        nesting_mode="brace",
        struct_patterns=[r"\bstruct\s+\w+", r"\benum\s+\w+"],
        interface_patterns=[r"\btrait\s+\w+"],
        skip_dirs=("target", ".git", "node_modules", "venv", ".venv", "__pycache__"),
        skip_file_prefixes=("test_",),
        skip_file_suffixes=("_test.rs",),
        skip_path_fragments=("/tests/",),
        extra_ast_patterns=[
            ("impl", r"\bimpl\s+"),
            ("macro", r"\w+!\s*[(\[{]"),
        ],
    ),
    "c": LanguageConfig(
        name="c",
        extensions=[".c", ".cpp", ".cc", ".cxx", ".h", ".hpp", ".hxx"],
        comment_patterns=[_C_LINE_COMMENT, _C_BLOCK_COMMENT],
        string_patterns=[_DOUBLE_QUOTE_STR],
        function_patterns=[
            r"^[a-zA-Z_][\w\s*&:<>]+\s+\w+\s*\([^)]*\)\s*(?:const\s*)?\{",
        ],
        import_patterns=[r'^\s*#include\s+[<"]([^>"]+)[>"]'],
        export_patterns=[
            r"^(?:extern\s+)?(?:static\s+)?(?:inline\s+)?\w+[\w\s*&]+\s+(\w+)\s*\([^)]*\)\s*\{",
            r"\bclass\s+(\w+)",
            r"\bstruct\s+(\w+)\s*\{",
        ],
        complexity_keywords=["if", "else", "case", "for", "while", "do", "switch"],
        complexity_operators=["&&", r"\|\|", r"\?"],
        nesting_mode="brace",
        struct_patterns=[r"\bstruct\s+\w+\s*\{", r"\btypedef\s+struct\b"],
        interface_patterns=[r"\bclass\s+\w+"],
        skip_dirs=(
            "build",
            "cmake-build",
            ".git",
            "node_modules",
            "venv",
            ".venv",
            "__pycache__",
            "third_party",
            "vendor",
            "deps",
            "external",
        ),
        skip_file_prefixes=("test_",),
        skip_file_suffixes=("_test.cpp", "_test.c"),
        skip_path_fragments=("/test/", "/tests/"),
        extra_ast_patterns=[
            ("macro", r"^\s*#define\b"),
            ("template", r"\btemplate\s*<"),
        ],
    ),
    "ruby": LanguageConfig(
        name="ruby",
        extensions=[".rb"],
        comment_patterns=[_HASH_COMMENT, (r"=begin.*?=end", _re.DOTALL)],
        string_patterns=[_DOUBLE_QUOTE_STR, _SINGLE_QUOTE_STR],
        function_patterns=[r"\bdef\s+\w+"],
        import_patterns=[
            r"require\s+['\"]([^'\"]+)['\"]",
            r"require_relative\s+['\"]([^'\"]+)['\"]",
        ],
        export_patterns=[
            r"^\s*def\s+(?:self\.)?(\w+)",
            r"^\s*class\s+(\w+)",
            r"^\s*module\s+(\w+)",
        ],
        complexity_keywords=[
            "if",
            "elsif",
            "else",
            "unless",
            "case",
            "when",
            "while",
            "until",
            "rescue",
        ],
        complexity_operators=["&&", r"\|\|"],
        nesting_mode="ruby",
        struct_patterns=[r"\bclass\s+\w+"],
        interface_patterns=[r"\bmodule\s+\w+"],
        skip_dirs=(
            "vendor",
            "bundle",
            ".git",
            "node_modules",
            "venv",
            ".venv",
            "__pycache__",
            "tmp",
            "log",
        ),
        skip_file_prefixes=("test_",),
        skip_file_suffixes=("_test.rb", "_spec.rb"),
        skip_path_fragments=("/test/", "/spec/"),
    ),
    "universal": LanguageConfig(
        name="universal",
        extensions=[],  # set dynamically by caller
        comment_patterns=[
            _C_LINE_COMMENT,
            _C_BLOCK_COMMENT,
            _HASH_COMMENT,
            _TRIPLE_DQ_STR,
            _TRIPLE_SQ_STR,
        ],
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
        complexity_keywords=[
            "if",
            "else",
            "elif",
            "elsif",
            "unless",
            "case",
            "switch",
            "for",
            "while",
            "match",
            "when",
        ],
        complexity_operators=["&&", r"\|\|", r"\band\b", r"\bor\b"],
        nesting_mode="both",
        skip_dirs=(
            "vendor",
            "node_modules",
            "venv",
            ".venv",
            "__pycache__",
            ".git",
            ".tox",
            ".mypy_cache",
            ".pytest_cache",
            "dist",
            "build",
            "target",
            ".eggs",
            "third_party",
            "cmake-build",
        ),
        skip_file_prefixes=("test_",),
    ),
}


# ── Default source-file extensions for universal scanner ───────────

DEFAULT_SOURCE_EXTENSIONS = [
    ".scala",
    ".kt",
    ".kts",
    ".swift",
    ".m",
    ".mm",
    ".ex",
    ".exs",
    ".erl",
    ".hrl",
    ".clj",
    ".cljs",
    ".cljc",
    ".edn",
    ".hs",
    ".lhs",
    ".ml",
    ".mli",
    ".fs",
    ".fsi",
    ".fsx",
    ".lua",
    ".pl",
    ".pm",
    ".r",
    ".R",
    ".jl",
    ".nim",
    ".zig",
    ".v",
    ".sv",
    ".groovy",
    ".gradle",
    ".dart",
    ".php",
    ".sh",
    ".bash",
    ".zsh",
    ".fish",
    ".ps1",
    ".psm1",
    ".coffee",
    ".elm",
    ".purs",
    ".d",
    ".ada",
    ".adb",
    ".ads",
    ".pas",
    ".pp",
    ".lpr",
    ".vb",
    ".vbs",
    ".cls",
    ".tcl",
    ".awk",
    ".sed",
    ".pro",
    ".P",
    ".lisp",
    ".cl",
    ".el",
    ".rkt",
    ".scm",
    ".ss",
    ".tf",
    ".hcl",
    ".yaml",
    ".yml",
    ".toml",
    ".json5",
    ".cmake",
]


def get_language_config(name: str) -> LanguageConfig:
    """Look up a language by name. Raises ShannonInsightError if unknown."""
    try:
        return LANGUAGES[name]
    except KeyError:
        supported = ", ".join(sorted(LANGUAGES.keys()))
        from ..exceptions import ShannonInsightError

        raise ShannonInsightError(f"Unsupported language: '{name}'. Supported: {supported}")


def get_all_known_extensions() -> set:
    """Return the set of all file extensions covered by specific (non-universal) languages."""
    exts = set()
    for name, cfg in LANGUAGES.items():
        if name != "universal":
            exts.update(cfg.extensions)
    return exts


# Extension to language mapping (built from LANGUAGES)
_EXTENSION_TO_LANGUAGE: dict[str, str] = {}
for _lang_name, _cfg in LANGUAGES.items():
    if _lang_name != "universal":
        for _ext in _cfg.extensions:
            _EXTENSION_TO_LANGUAGE[_ext] = _lang_name


def detect_language(filepath) -> str:
    """Detect language from file extension.

    Args:
        filepath: Path object or string

    Returns:
        Language name (e.g., "python", "go") or "unknown"
    """
    from pathlib import Path

    path = Path(filepath) if not hasattr(filepath, "suffix") else filepath
    ext = path.suffix.lower()
    return _EXTENSION_TO_LANGUAGE.get(ext, "unknown")
