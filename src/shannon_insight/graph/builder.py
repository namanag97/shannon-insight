"""Dependency graph construction from import declarations."""

from pathlib import Path
from typing import Optional

from ..persistence.fact_models import FileFact, ImportFact
from ..scanning.syntax import FileSyntax
from .models import CodeGraph, DependencyGraph

# Language-specific file extensions for import resolution
LANGUAGE_EXTENSIONS: dict[str, list[str]] = {
    "python": [".py", "/__init__.py"],
    "go": [".go"],
    "typescript": [".ts", ".tsx", "/index.ts", "/index.tsx", ".d.ts"],
    "javascript": [".js", ".jsx", ".mjs", ".cjs", "/index.js", "/index.jsx"],
    "java": [".java"],
    "rust": [".rs", "/mod.rs"],
    "ruby": [".rb"],
    "c": [".c", ".h"],
    "cpp": [".cpp", ".hpp", ".cc", ".hh"],
}

# Known stdlib/builtin modules per language (common ones to exclude from phantom tracking)
# These are root module names that should NOT be flagged as phantom imports
STDLIB_ROOTS: dict[str, set[str]] = {
    "python": {
        "abc",
        "aifc",
        "argparse",
        "array",
        "ast",
        "asynchat",
        "asyncio",
        "asyncore",
        "atexit",
        "audioop",
        "base64",
        "bdb",
        "binascii",
        "binhex",
        "bisect",
        "builtins",
        "bz2",
        "calendar",
        "cgi",
        "cgitb",
        "chunk",
        "cmath",
        "cmd",
        "code",
        "codecs",
        "codeop",
        "collections",
        "colorsys",
        "compileall",
        "concurrent",
        "configparser",
        "contextlib",
        "contextvars",
        "copy",
        "copyreg",
        "cProfile",
        "crypt",
        "csv",
        "ctypes",
        "curses",
        "dataclasses",
        "datetime",
        "dbm",
        "decimal",
        "difflib",
        "dis",
        "distutils",
        "doctest",
        "email",
        "encodings",
        "enum",
        "errno",
        "faulthandler",
        "fcntl",
        "filecmp",
        "fileinput",
        "fnmatch",
        "fractions",
        "ftplib",
        "functools",
        "gc",
        "getopt",
        "getpass",
        "gettext",
        "glob",
        "graphlib",
        "grp",
        "gzip",
        "hashlib",
        "heapq",
        "hmac",
        "html",
        "http",
        "idlelib",
        "imaplib",
        "imghdr",
        "imp",
        "importlib",
        "inspect",
        "io",
        "ipaddress",
        "itertools",
        "json",
        "keyword",
        "lib2to3",
        "linecache",
        "locale",
        "logging",
        "lzma",
        "mailbox",
        "mailcap",
        "marshal",
        "math",
        "mimetypes",
        "mmap",
        "modulefinder",
        "multiprocessing",
        "netrc",
        "nis",
        "nntplib",
        "numbers",
        "operator",
        "optparse",
        "os",
        "ossaudiodev",
        "parser",
        "pathlib",
        "pdb",
        "pickle",
        "pickletools",
        "pipes",
        "pkgutil",
        "platform",
        "plistlib",
        "poplib",
        "posix",
        "posixpath",
        "pprint",
        "profile",
        "pstats",
        "pty",
        "pwd",
        "py_compile",
        "pyclbr",
        "pydoc",
        "queue",
        "quopri",
        "random",
        "re",
        "readline",
        "reprlib",
        "resource",
        "rlcompleter",
        "runpy",
        "sched",
        "secrets",
        "select",
        "selectors",
        "shelve",
        "shlex",
        "shutil",
        "signal",
        "site",
        "smtpd",
        "smtplib",
        "sndhdr",
        "socket",
        "socketserver",
        "spwd",
        "sqlite3",
        "ssl",
        "stat",
        "statistics",
        "string",
        "stringprep",
        "struct",
        "subprocess",
        "sunau",
        "symbol",
        "symtable",
        "sys",
        "sysconfig",
        "syslog",
        "tabnanny",
        "tarfile",
        "telnetlib",
        "tempfile",
        "termios",
        "test",
        "textwrap",
        "threading",
        "time",
        "timeit",
        "tkinter",
        "token",
        "tokenize",
        "trace",
        "traceback",
        "tracemalloc",
        "tty",
        "turtle",
        "turtledemo",
        "types",
        "typing",
        "typing_extensions",
        "unicodedata",
        "unittest",
        "urllib",
        "uu",
        "uuid",
        "venv",
        "warnings",
        "wave",
        "weakref",
        "webbrowser",
        "winreg",
        "winsound",
        "wsgiref",
        "xdrlib",
        "xml",
        "xmlrpc",
        "zipapp",
        "zipfile",
        "zipimport",
        "zlib",
        # Common third-party that are almost universal
        "pytest",
        "numpy",
        "pandas",
        "scipy",
        "sklearn",
        "matplotlib",
    },
    "go": {
        "archive",
        "bufio",
        "builtin",
        "bytes",
        "compress",
        "container",
        "context",
        "crypto",
        "database",
        "debug",
        "embed",
        "encoding",
        "errors",
        "expvar",
        "flag",
        "fmt",
        "go",
        "hash",
        "html",
        "image",
        "index",
        "io",
        "log",
        "math",
        "mime",
        "net",
        "os",
        "path",
        "plugin",
        "reflect",
        "regexp",
        "runtime",
        "sort",
        "strconv",
        "strings",
        "sync",
        "syscall",
        "testing",
        "text",
        "time",
        "unicode",
        "unsafe",
    },
    "javascript": {
        # Node.js builtins
        "assert",
        "buffer",
        "child_process",
        "cluster",
        "console",
        "constants",
        "crypto",
        "dgram",
        "dns",
        "domain",
        "events",
        "fs",
        "http",
        "http2",
        "https",
        "inspector",
        "module",
        "net",
        "os",
        "path",
        "perf_hooks",
        "process",
        "punycode",
        "querystring",
        "readline",
        "repl",
        "stream",
        "string_decoder",
        "timers",
        "tls",
        "tty",
        "url",
        "util",
        "v8",
        "vm",
        "worker_threads",
        "zlib",
        # Common npm packages - not phantom
        "react",
        "react-dom",
        "preact",
        "vue",
        "angular",
        "express",
        "lodash",
        "axios",
        "moment",
        "jquery",
        "underscore",
        "webpack",
        "babel",
        "typescript",
        "eslint",
        "prettier",
        "next",
        "nuxt",
        "svelte",
        "solid-js",
        "htmx",
    },
    "typescript": {
        # Same as JavaScript plus TypeScript-specific
        "assert",
        "buffer",
        "child_process",
        "cluster",
        "console",
        "constants",
        "crypto",
        "dgram",
        "dns",
        "domain",
        "events",
        "fs",
        "http",
        "http2",
        "https",
        "inspector",
        "module",
        "net",
        "os",
        "path",
        "perf_hooks",
        "process",
        "punycode",
        "querystring",
        "readline",
        "repl",
        "stream",
        "string_decoder",
        "timers",
        "tls",
        "tty",
        "url",
        "util",
        "v8",
        "vm",
        "worker_threads",
        "zlib",
        "react",
        "react-dom",
        "preact",
        "vue",
        "angular",
        "express",
        "lodash",
        "axios",
        "moment",
        "jquery",
        "underscore",
        "webpack",
        "babel",
        "typescript",
        "eslint",
        "prettier",
        "next",
        "nuxt",
        "svelte",
        "solid-js",
        "htmx",
    },
    "java": {
        "java",
        "javax",
        "sun",
        "com.sun",
        "org.w3c",
        "org.xml",
    },
    "rust": {
        "std",
        "core",
        "alloc",
        "proc_macro",
    },
    "ruby": {
        "abbrev",
        "base64",
        "benchmark",
        "bigdecimal",
        "cgi",
        "csv",
        "date",
        "delegate",
        "digest",
        "drb",
        "English",
        "erb",
        "etc",
        "fcntl",
        "fiddle",
        "fileutils",
        "find",
        "forwardable",
        "getoptlong",
        "io",
        "ipaddr",
        "irb",
        "json",
        "logger",
        "matrix",
        "minitest",
        "monitor",
        "mutex_m",
        "net",
        "nkf",
        "observer",
        "open-uri",
        "open3",
        "openssl",
        "optparse",
        "ostruct",
        "pathname",
        "pp",
        "prettyprint",
        "prime",
        "pstore",
        "psych",
        "pty",
        "racc",
        "rake",
        "rdoc",
        "readline",
        "reline",
        "resolv",
        "rinda",
        "ripper",
        "rss",
        "ruby2_keywords",
        "rubygems",
        "securerandom",
        "set",
        "shellwords",
        "singleton",
        "socket",
        "stringio",
        "strscan",
        "syslog",
        "tempfile",
        "test",
        "time",
        "timeout",
        "tmpdir",
        "tracer",
        "tsort",
        "un",
        "uri",
        "weakref",
        "webrick",
        "yaml",
        "zlib",
    },
}


def build_dependency_graph(file_syntax: list[FileSyntax], root_dir: str = "") -> DependencyGraph:
    """Build dependency graph from import declarations in FileSyntax.

    Also tracks unresolved imports for phantom_import_count signal.
    Only imports that look like they should resolve internally are tracked
    as unresolved — stdlib and third-party imports are excluded.

    Now language-aware: uses source file's language to determine resolution rules.
    """
    file_map: dict[str, FileSyntax] = {f.path: f for f in file_syntax}
    all_paths = set(file_map.keys())
    adjacency: dict[str, list[str]] = {p: [] for p in all_paths}
    reverse: dict[str, list[str]] = {p: [] for p in all_paths}
    unresolved: dict[str, list[str]] = {}  # Phase 3: track unresolved imports
    edge_count = 0

    path_index = _build_path_index(all_paths)
    project_prefixes = _infer_project_prefixes(all_paths)

    for fs in file_syntax:
        language = fs.language  # Now we use the language!
        for imp in fs.import_sources:
            resolved = _resolve_import(imp, fs.path, language, path_index, all_paths)
            if resolved and resolved != fs.path:
                adjacency[fs.path].append(resolved)
                reverse[resolved].append(fs.path)
                edge_count += 1
            elif resolved is None and _looks_internal(imp, language, project_prefixes):
                # Only track as phantom if it looks like it should be internal
                if fs.path not in unresolved:
                    unresolved[fs.path] = []
                unresolved[fs.path].append(imp)

    return DependencyGraph(
        adjacency=adjacency,
        reverse=reverse,
        all_nodes=all_paths,
        edge_count=edge_count,
        unresolved_imports=unresolved,
    )


def _infer_project_prefixes(all_paths: set[str]) -> set[str]:
    """Infer project namespace prefixes from file paths.

    If files live under "src/myproject/", then "myproject" is a project prefix.
    Relative imports (starting with ".") are always considered internal.
    """
    prefixes: set[str] = set()
    for path in all_paths:
        parts = Path(path).parts
        # Top-level directory names are likely project prefixes
        if len(parts) >= 2:
            prefixes.add(parts[0])
            # Also add "src/X" patterns
            if parts[0] == "src" and len(parts) >= 3:
                prefixes.add(parts[1])
    return prefixes


def _looks_internal(imp: str, language: str, project_prefixes: set[str]) -> bool:
    """Check if an unresolved import looks like it should be internal.

    Now language-aware: uses stdlib registries per language.

    Returns True for:
    - Relative imports (.foo, ..bar, ./foo, ../bar) to code files — internal
    - Imports matching a project namespace prefix

    Returns False for:
    - Known stdlib/builtin modules for the language
    - Single-segment imports that look like stdlib
    - NPM-style scoped packages (@scope/pkg) — external
    - Third-party packages (don't match project prefixes)
    - Style imports (CSS, SCSS, LESS, etc.) — not code dependencies
    """
    imp = imp.strip()

    # Style imports are NOT code dependencies (CSS, SCSS, LESS, etc.)
    style_extensions = (".css", ".scss", ".sass", ".less", ".styl", ".stylus")
    if any(imp.endswith(ext) for ext in style_extensions):
        return False

    # Relative imports to code files are internal
    if imp.startswith("."):
        return True

    # Go-style quoted imports: strip quotes
    if imp.startswith('"') and imp.endswith('"'):
        imp = imp[1:-1]

    # NPM-style scoped packages (@scope/pkg) are external
    if imp.startswith("@"):
        return False

    # Check language-specific stdlib
    stdlib_roots = STDLIB_ROOTS.get(language, set())
    first_segment = imp.split(".")[0].split("/")[0]
    if first_segment in stdlib_roots:
        return False

    # Single-segment imports without dots/slashes are likely external
    # (stdlib or third-party packages: os, fmt, lodash, express)
    if "." not in imp and "/" not in imp:
        return False

    # Check if any segment matches a project prefix
    if first_segment in project_prefixes:
        return True

    return False


def _build_path_index(all_paths: set[str]) -> dict[str, str]:
    """Map dotted module paths to file paths for import resolution.

    Builds multiple lookup keys per file so resolution can work
    from different prefix levels. Handles multiple file extensions.
    """
    index: dict[str, str] = {}
    for path in all_paths:
        # Strip common extensions to get dotted form
        dotted = path.replace("/", ".").replace("\\", ".")

        # Remove known extensions
        for ext in (".py", ".ts", ".tsx", ".js", ".jsx", ".mjs", ".go", ".java", ".rs", ".rb"):
            if dotted.endswith(ext):
                dotted = dotted[: -len(ext)]
                break

        # Remove __init__, index, mod suffixes
        for suffix in (".__init__", ".index", ".mod"):
            if dotted.endswith(suffix):
                dotted = dotted[: -len(suffix)]
                break

        index[dotted] = path

        # Also without "src." prefix
        if dotted.startswith("src."):
            short = dotted[4:]
            index[short] = path

    return index


def _resolve_import(
    imp: str,
    source_path: str,
    language: str,
    path_index: dict[str, str],
    all_paths: set[str],
) -> Optional[str]:
    """Resolve an import string to a file path in the codebase.

    Now language-aware: uses appropriate resolution rules per language.

    Handles:
      - Relative imports: .base, ..models, ./utils, ../helpers
      - Absolute imports: shannon_insight.models, pathlib, os
    """
    imp = imp.strip()

    # ── Relative imports (leading dots or ./) ────────────────────────
    if imp.startswith("."):
        return _resolve_relative_import(imp, source_path, language, all_paths)

    # ── Absolute imports ───────────────────────────────────────────
    # Try exact match in index
    if imp in path_index:
        return path_index[imp]

    # Try with common project prefixes prepended
    for prefix in ("src.", "src.shannon_insight."):
        candidate = prefix + imp
        if candidate in path_index:
            return path_index[candidate]

    # Try stripping prefixes progressively
    # "shannon_insight.signals.composites" → "signals.composites" → "composites"
    parts = imp.split(".")
    for i in range(1, len(parts)):
        suffix = ".".join(parts[i:])
        if suffix in path_index:
            return path_index[suffix]

    # Not an internal import (stdlib or third-party)
    return None


def _resolve_relative_import(
    imp: str, source_path: str, language: str, all_paths: set[str]
) -> Optional[str]:
    """Resolve a relative import like ..models or ./utils.

    Now language-aware: uses appropriate file extensions per language.
    """
    # Handle JS/TS style "./" and "../" prefixes
    if imp.startswith("./") or imp.startswith("../"):
        return _resolve_path_relative_import(imp, source_path, language, all_paths)

    # Handle Python-style ".module" and "..module" imports
    return _resolve_dot_relative_import(imp, source_path, language, all_paths)


def _resolve_path_relative_import(
    imp: str, source_path: str, language: str, all_paths: set[str]
) -> Optional[str]:
    """Resolve JS/TS style relative imports like ./utils or ../helpers."""
    source_dir = Path(source_path).parent

    # Normalize the path
    target_path = (source_dir / imp).resolve()

    # Get the relative path from cwd (since all_paths are relative)
    try:
        # Try to make it relative to find in all_paths
        rel_path = str(target_path)
        # Strip leading "/" if present
        if rel_path.startswith("/"):
            # Find common prefix with any path in all_paths
            for p in all_paths:
                if rel_path.endswith(p) or p.endswith(rel_path.split("/")[-1]):
                    rel_path = p
                    break
    except ValueError:
        rel_path = str(target_path)

    # Get language-specific extensions
    extensions = LANGUAGE_EXTENSIONS.get(language, LANGUAGE_EXTENSIONS.get("python", [".py"]))

    # Build candidate paths
    candidates = []
    for ext in extensions:
        if ext.startswith("/"):
            # It's a directory index pattern like /index.js
            candidates.append(rel_path + ext)
        else:
            candidates.append(rel_path + ext)

    # Also try the exact path if it already has an extension
    candidates.append(rel_path)

    for candidate in candidates:
        # Normalize path separators
        normalized = candidate.replace("\\", "/")
        if normalized in all_paths:
            return normalized
        # Try without leading directory components
        for p in all_paths:
            if p.endswith(normalized.split("/")[-1]) or normalized.endswith(p):
                return p

    return None


def _resolve_dot_relative_import(
    imp: str, source_path: str, language: str, all_paths: set[str]
) -> Optional[str]:
    """Resolve Python-style relative import like ..models or .base."""
    # Count leading dots
    dot_count = 0
    while dot_count < len(imp) and imp[dot_count] == ".":
        dot_count += 1
    module_part = imp[dot_count:]  # e.g., "models", "math.graph", "base"

    # Navigate up from source file's directory
    source_dir = Path(source_path).parent
    for _ in range(dot_count - 1):  # -1 because . means current package
        source_dir = source_dir.parent

    # Get language-specific extensions
    extensions = LANGUAGE_EXTENSIONS.get(language, LANGUAGE_EXTENSIONS.get("python", [".py"]))

    # Build candidate paths
    candidates = []
    if module_part:
        module_as_path = module_part.replace(".", "/")
        for ext in extensions:
            if ext.startswith("/"):
                # Directory index pattern
                candidates.append(str(source_dir / module_as_path) + ext)
            else:
                candidates.append(str(source_dir / module_as_path) + ext)
    else:
        # Just dots, looking for package init
        for ext in extensions:
            if ext.startswith("/"):
                candidates.append(str(source_dir) + ext)

    for candidate in candidates:
        # Normalize path separators for comparison
        normalized = candidate.replace("\\", "/")
        if normalized in all_paths:
            return normalized
        # Also try matching by suffix (handles src/ prefix mismatches)
        for path in all_paths:
            if path.endswith(normalized) or normalized.endswith(path):
                return path

    return None


# ── Phase 2: Multi-type graph from facts ─────────────────────────────


def build_code_graph_from_facts(
    file_facts: list[FileFact],
    call_targets: dict[str, list[str]],
    class_bases: dict[str, list[str]],
    imports: list[ImportFact],
) -> CodeGraph:
    """Build multi-type graph from stored facts.

    This is the NEW way - uses pre-computed data from Phase 1 FactDatabase.

    Args:
        file_facts: List of FileFact from db.get_file_facts_for_session()
        call_targets: Dict from db.get_call_targets_for_session()
        class_bases: Dict from db.get_class_bases_for_session()
        imports: List from db.get_imports_for_session()

    Returns:
        CodeGraph with all node types and edge types populated
    """
    graph = CodeGraph()

    # Build indexes for resolution
    all_paths = {f.path for f in file_facts}
    function_index, function_nodes, file_to_functions = _build_function_index(file_facts)
    class_index, class_nodes, file_to_classes = _build_class_index(file_facts)
    import_index = _build_import_index(imports)

    # Build FILE nodes
    for fact in file_facts:
        graph.file_nodes.add(fact.path)

    # Build FUNCTION nodes and CONTAINS edges
    for file_fact in file_facts:
        for fn in file_fact.functions:
            node_id = f"{file_fact.path}:{fn.qualified_name}"
            graph.function_nodes.add(node_id)
            graph.contains_edges.setdefault(file_fact.path, []).append(node_id)
            graph.contained_in[node_id] = file_fact.path

    # Build CALL edges
    for file_fact in file_facts:
        for fn in file_fact.functions:
            caller_node = f"{file_fact.path}:{fn.qualified_name}"

            for target in fn.call_targets:
                # Resolve target to a function node
                target_node = _resolve_call_target(
                    target,
                    file_fact.path,
                    fn.class_name,
                    function_index,
                    function_nodes,
                    file_to_functions,
                    import_index,
                    all_paths,
                )
                if target_node and target_node in graph.function_nodes:
                    graph.call_edges.setdefault(caller_node, []).append(target_node)
                    graph.called_by.setdefault(target_node, []).append(caller_node)

    # Build CLASS nodes and INHERIT edges
    for class_key, bases in class_bases.items():
        # class_key is "file:ClassName"
        graph.class_nodes.add(class_key)
        file_path = class_key.split(":", 1)[0]
        graph.contains_edges.setdefault(file_path, []).append(class_key)
        graph.contained_in[class_key] = file_path

        for base in bases:
            # Try to resolve base class to a node
            base_node = _resolve_class(
                base,
                file_path,
                class_index,
                class_nodes,
                import_index,
                all_paths,
            )
            if base_node and base_node in graph.class_nodes:
                graph.inherit_edges.setdefault(class_key, []).append(base_node)
                graph.inherited_by.setdefault(base_node, []).append(class_key)

    # Build IMPORT edges (use resolved_path from facts)
    for imp in imports:
        if imp.resolved_path and imp.resolved_path in all_paths:
            if imp.file_path != imp.resolved_path:  # Skip self-imports
                graph.import_edges.setdefault(imp.file_path, []).append(imp.resolved_path)
                graph.imported_by.setdefault(imp.resolved_path, []).append(imp.file_path)

    # Build TYPE nodes and TYPE_FLOW edges
    for file_fact in file_facts:
        for fn in file_fact.functions:
            func_node = f"{file_fact.path}:{fn.qualified_name}"

            # Return type edge (FUNCTION -> TYPE)
            if fn.return_type:
                type_str = _normalize_type(fn.return_type)
                graph.type_nodes.add(type_str)
                graph.returns_edges[func_node] = type_str
                graph.used_by.setdefault(type_str, []).append(func_node)

            # Parameter type edges (FUNCTION -> {param: TYPE})
            if fn.param_types:
                param_types: dict[str, str] = {}
                for param, ptype in fn.param_types.items():
                    type_str = _normalize_type(ptype)
                    graph.type_nodes.add(type_str)
                    param_types[param] = type_str
                    graph.used_by.setdefault(type_str, []).append(func_node)
                if param_types:
                    graph.param_type_edges[func_node] = param_types

        # Field type edges (CLASS -> {field: TYPE})
        for cls in file_fact.classes:
            class_node = f"{file_fact.path}:{cls.name}"
            if cls.field_types:
                field_types: dict[str, str] = {}
                for field_name, ftype in cls.field_types.items():
                    type_str = _normalize_type(ftype)
                    graph.type_nodes.add(type_str)
                    field_types[field_name] = type_str
                    graph.used_by.setdefault(type_str, []).append(class_node)
                if field_types:
                    graph.field_type_edges[class_node] = field_types

    return graph


def _normalize_type(type_str: str) -> str:
    """Normalize a type annotation string.

    Removes whitespace, normalizes Optional[X] to X | None, etc.
    """
    # Strip whitespace
    type_str = type_str.strip()

    # Remove 'typing.' prefix
    type_str = type_str.replace("typing.", "")

    # Normalize common patterns
    if type_str.startswith("Optional[") and type_str.endswith("]"):
        inner = type_str[9:-1]
        type_str = f"{inner} | None"

    return type_str


def _build_function_index(
    file_facts: list[FileFact],
) -> tuple[dict[str, str], set[str], dict[str, list[str]]]:
    """Build indexes for fast function resolution.

    Returns:
        function_index: name → node_id (only unique mappings)
        function_nodes: set of ALL node_ids (for O(1) membership check)
        file_to_functions: file → [node_ids] (for fast same-file lookup)

    Maps in function_index:
    - "func_name" -> "file:func_name" (if unique)
    - "ClassName.method" -> "file:ClassName.method" (if unique)
    - "file:qualified_name" -> "file:qualified_name" (always)
    """
    # O(1) membership check for node IDs
    function_nodes: set[str] = set()
    # Fast lookup of functions by file
    file_to_functions: dict[str, list[str]] = {}

    # First pass: collect all occurrences and build fast indexes
    occurrences: dict[str, list[str]] = {}
    for file_fact in file_facts:
        file_funcs: list[str] = []
        for fn in file_fact.functions:
            node_id = f"{file_fact.path}:{fn.qualified_name}"

            # Add to O(1) lookup structures
            function_nodes.add(node_id)
            file_funcs.append(node_id)

            # Full path always maps
            occurrences.setdefault(node_id, []).append(node_id)

            # Short name (qualified_name only)
            occurrences.setdefault(fn.qualified_name, []).append(node_id)

            # Just the function name (without class)
            if fn.class_name:
                occurrences.setdefault(fn.name, []).append(node_id)

        file_to_functions[file_fact.path] = file_funcs

    # Second pass: create index (only unique mappings)
    index: dict[str, str] = {}
    for key, nodes in occurrences.items():
        if len(nodes) == 1:
            index[key] = nodes[0]
        # If multiple, don't add to index (ambiguous)

    return index, function_nodes, file_to_functions


def _build_class_index(
    file_facts: list[FileFact],
) -> tuple[dict[str, str], set[str], dict[str, list[str]]]:
    """Build indexes for fast class resolution.

    Returns:
        class_index: name → node_id (only unique mappings)
        class_nodes: set of ALL node_ids (for O(1) membership check)
        file_to_classes: file → [node_ids] (for fast same-file lookup)

    Maps in class_index:
    - "ClassName" -> "file:ClassName" (if unique)
    - "file:ClassName" -> "file:ClassName" (always)
    """
    # O(1) membership check for node IDs
    class_nodes: set[str] = set()
    # Fast lookup of classes by file
    file_to_classes: dict[str, list[str]] = {}

    occurrences: dict[str, list[str]] = {}
    for file_fact in file_facts:
        file_classes: list[str] = []
        for cls in file_fact.classes:
            node_id = f"{file_fact.path}:{cls.name}"

            # Add to O(1) lookup structures
            class_nodes.add(node_id)
            file_classes.append(node_id)

            # Full path always maps
            occurrences.setdefault(node_id, []).append(node_id)

            # Short name
            occurrences.setdefault(cls.name, []).append(node_id)

        file_to_classes[file_fact.path] = file_classes

    index: dict[str, str] = {}
    for key, nodes in occurrences.items():
        if len(nodes) == 1:
            index[key] = nodes[0]

    return index, class_nodes, file_to_classes


def _build_import_index(imports: list[ImportFact]) -> dict[str, dict[str, str]]:
    """Build index from imported names to their source files.

    For each file, maps:
    - imported name -> source file path

    Example: if foo.py has "from bar import Baz", then:
    - index["foo.py"]["Baz"] -> "bar.py"
    """
    index: dict[str, dict[str, str]] = {}
    for imp in imports:
        if imp.resolved_path:
            file_imports = index.setdefault(imp.file_path, {})
            for name in imp.names:
                file_imports[name] = imp.resolved_path

    return index


def _resolve_call_target(
    target: str,
    caller_file: str,
    caller_class: Optional[str],
    function_index: dict[str, str],
    function_nodes: set[str],
    file_to_functions: dict[str, list[str]],
    import_index: dict[str, dict[str, str]],
    all_paths: set[str],
) -> Optional[str]:
    """Resolve a call target string to a function node ID.

    Args:
        target: Call target name (e.g., "foo", "self.bar", "cls.baz")
        caller_file: Path of the file containing the call
        caller_class: Name of the class if call is in a method, else None
        function_index: name → node_id mapping (only unique names)
        function_nodes: O(1) set of all function node IDs
        file_to_functions: file → [node_ids] for O(1) same-file lookup
        import_index: file → {imported_name → source_file}
        all_paths: Set of all file paths

    Strategy:
    1. If target is "self.X" or "cls.X", look for method X in same class
    2. If target matches a function in same file, use that
    3. If target matches an imported name, follow the import
    4. If target matches in function_index, use that
    5. Otherwise, return None (external/stdlib call)
    """
    # Handle self.method and cls.method
    if target.startswith("self.") or target.startswith("cls."):
        method_name = target.split(".", 1)[1]
        if caller_class:
            # Look for ClassName.method in same file
            qualified = f"{caller_class}.{method_name}"
            node_id = f"{caller_file}:{qualified}"
            if node_id in function_nodes:  # O(1) lookup
                return node_id
            # Also check if it's in the index
            if qualified in function_index:
                return function_index[qualified]
        return None

    # Check same-file functions first (most common case)
    # Try exact match: "file:target"
    same_file_node = f"{caller_file}:{target}"
    if same_file_node in function_nodes:  # O(1) lookup
        return same_file_node

    # Try as method in same file using file_to_functions (O(m) where m = methods in file)
    same_file_funcs = file_to_functions.get(caller_file, [])
    suffix = f".{target}"
    for node_id in same_file_funcs:
        if node_id.endswith(suffix):
            return node_id

    # Check if it's an imported symbol
    file_imports = import_index.get(caller_file, {})
    if target in file_imports:
        source_file = file_imports[target]
        # Look for a function with this name in the source file
        source_node = f"{source_file}:{target}"
        if source_node in function_nodes:  # O(1) lookup
            return source_node
        # Check if the target is in the unique index
        if target in function_index:
            return function_index[target]

    # Check if the target contains a dot (method call on imported object)
    if "." in target:
        parts = target.split(".", 1)
        obj_name, method = parts[0], parts[1]
        # Check if obj_name is imported
        if obj_name in file_imports:
            source_file = file_imports[obj_name]
            # Look for obj_name.method in source file (if obj_name is a class)
            source_node = f"{source_file}:{obj_name}.{method}"
            if source_node in function_nodes:  # O(1) lookup
                return source_node

    # Try global lookup (unique names only)
    if target in function_index:
        return function_index[target]

    # Not an internal call (stdlib/third-party)
    return None


def _resolve_class(
    base_name: str,
    current_file: str,
    class_index: dict[str, str],
    class_nodes: set[str],
    import_index: dict[str, dict[str, str]],
    all_paths: set[str],
) -> Optional[str]:
    """Resolve a base class name to a class node ID.

    Args:
        base_name: Base class name (e.g., "BaseClass", "abc.ABC")
        current_file: Path of the file containing the class
        class_index: name → node_id mapping (only unique names)
        class_nodes: O(1) set of all class node IDs
        import_index: file → {imported_name → source_file}
        all_paths: Set of all file paths

    Strategy:
    1. If base is in same file, use that
    2. If base is imported, follow the import
    3. If base is in class_index (unique), use that
    4. Otherwise, return None (external/stdlib class)
    """
    # Check same-file classes first
    same_file_node = f"{current_file}:{base_name}"
    if same_file_node in class_nodes:  # O(1) lookup
        return same_file_node

    # Check if it's an imported symbol
    file_imports = import_index.get(current_file, {})
    if base_name in file_imports:
        source_file = file_imports[base_name]
        source_node = f"{source_file}:{base_name}"
        if source_node in class_nodes:  # O(1) lookup
            return source_node

    # Try global lookup (if unique)
    if base_name in class_index:
        return class_index[base_name]

    # Handle qualified names like "module.ClassName"
    if "." in base_name:
        parts = base_name.rsplit(".", 1)
        class_only = parts[-1]
        # Check if the module part is imported
        module_part = parts[0]
        if module_part in file_imports:
            source_file = file_imports[module_part]
            source_node = f"{source_file}:{class_only}"
            if source_node in class_nodes:  # O(1) lookup
                return source_node

    # Not an internal class (stdlib/third-party like ABC, Protocol)
    return None
