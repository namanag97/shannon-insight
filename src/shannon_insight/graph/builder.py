"""Dependency graph construction from import declarations."""

from pathlib import Path
from typing import Optional

from ..scanning.syntax import FileSyntax
from .models import DependencyGraph

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
        if candidate in all_paths:
            return candidate

    return None
