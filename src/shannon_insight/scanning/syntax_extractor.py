"""SyntaxExtractor: produces FileSyntax for all scanned files.

This component parses source files and produces FileSyntax objects.
It tries tree-sitter first, falls back to regex.

Usage:
    extractor = SyntaxExtractor()
    results = extractor.extract_all(file_paths, root_dir)
    # results is dict[path, FileSyntax]

Fallback behavior:
    1. If tree-sitter is available and supports the language: use tree-sitter
    2. If tree-sitter fails (syntax error, encoding error): use regex fallback
    3. If tree-sitter not installed: use regex fallback

The fallback rate is tracked. If >20% of files use fallback, a warning is logged.

Caching:
    When a FactStore is provided, parsed results are cached by content hash.
    Same content (regardless of path) produces the same parse result, so
    renames and duplicates are handled automatically.
"""

from __future__ import annotations

import logging
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from threading import Lock
from typing import TYPE_CHECKING, Any

# Import STDLIB_ROOTS for stdlib detection
from ..graph.builder import LANGUAGE_EXTENSIONS, STDLIB_ROOTS
from .fallback import RegexFallbackScanner
from .languages import detect_language
from .normalizer import TreeSitterNormalizer
from .syntax import ClassDef, FileSyntax, FunctionDef, ImportDecl
from .treesitter_parser import TREE_SITTER_AVAILABLE

if TYPE_CHECKING:
    from ..facts.store import FactStore

logger = logging.getLogger(__name__)

# Default worker count: use CPU count, capped at 8 to avoid overwhelming I/O
_DEFAULT_WORKERS = min(os.cpu_count() or 4, 8)


class SyntaxExtractor:
    """Extracts FileSyntax from source files.

    Attributes:
        fallback_count: Number of files that used regex fallback
        treesitter_count: Number of files parsed with tree-sitter
        total_count: Total files processed
    """

    def __init__(
        self,
        max_workers: int | None = None,
        fact_store: FactStore | None = None,
    ) -> None:
        """Initialize extractor with tree-sitter normalizer and regex fallback.

        Args:
            max_workers: Max parallel workers for extract_all(). Defaults to CPU count (max 8).
            fact_store: Optional FactStore for content-hash caching.
                        When provided, parsed results are cached by SHA-256 content
                        hash, so identical files are parsed only once.
        """
        self._normalizer = TreeSitterNormalizer() if TREE_SITTER_AVAILABLE else None
        self._fallback = RegexFallbackScanner()
        self._max_workers = max_workers or _DEFAULT_WORKERS
        self._lock = Lock()  # Thread-safe counter updates
        self.fallback_count = 0
        self.treesitter_count = 0
        self.total_count = 0
        self._fact_store = fact_store
        self._db_lock = Lock()  # Serialize FactStore (SQLite) access across threads
        self._cache_hits = 0
        self._cache_misses = 0

    def extract(
        self, file_path: Path, root_dir: Path, content_cache: dict[str, str] | None = None
    ) -> FileSyntax | None:
        """Extract FileSyntax from a single file.

        If a FactStore is configured, checks the cache by content hash first.
        On a cache miss, parses the file and stores the result for future use.

        Args:
            file_path: Path to the file
            root_dir: Root directory for relative path calculation
            content_cache: Optional dict to store file content for later reuse

        Returns:
            FileSyntax or None if file cannot be read
        """
        try:
            content = file_path.read_text(encoding="utf-8", errors="replace")
            mtime = file_path.stat().st_mtime
        except OSError as e:
            logger.debug(f"Cannot read {file_path}: {e}")
            return None

        rel_path = str(file_path.relative_to(root_dir))
        language = detect_language(file_path)

        # Cache content for later reuse (e.g., compression ratio)
        if content_cache is not None:
            content_cache[rel_path] = content

        content_hash = FileSyntax.compute_content_hash(content)

        # Try FactStore cache (serialize SQLite access across threads)
        if self._fact_store is not None:
            with self._db_lock:
                has_cached = self._fact_store.has_parsed_syntax(content_hash)
                cached_syntax = self._fact_store.get_parsed_syntax(content_hash) if has_cached else None
            if cached_syntax is not None:
                with self._lock:
                    self._cache_hits += 1
                    self.total_count += 1
                    # Count as treesitter or fallback based on cached parser_type
                    if cached_syntax.get("parser_type") == "tree-sitter":
                        self.treesitter_count += 1
                    else:
                        self.fallback_count += 1
                return self._rehydrate_syntax(
                    path=rel_path,
                    content_hash=content_hash,
                    mtime=mtime,
                    absolute_path=str(file_path.resolve()),
                    cached=cached_syntax,
                )

        # Cache miss -- parse normally
        with self._lock:
            self._cache_misses += 1

        # Thread-safe counter updates
        with self._lock:
            self.total_count += 1

        # Try tree-sitter first
        syntax: FileSyntax | None = None
        parser_type = "regex"
        if self._normalizer is not None:
            syntax = self._normalizer.parse_file(
                content, rel_path, language, mtime, absolute_path=str(file_path.resolve())
            )
            if syntax is not None:
                parser_type = "tree-sitter"
                with self._lock:
                    self.treesitter_count += 1

        if syntax is None:
            # Fall back to regex
            with self._lock:
                self.fallback_count += 1
            syntax = self._fallback.parse(
                content, rel_path, language, mtime, absolute_path=str(file_path.resolve())
            )
            parser_type = "regex"

        # Store in cache
        if self._fact_store is not None and syntax is not None:
            self._cache_syntax(content_hash, syntax, parser_type)

        return syntax

    def extract_all(
        self,
        file_paths: list[Path],
        root_dir: Path,
        parallel: bool = True,
        content_cache: dict[str, str] | None = None,
    ) -> dict[str, FileSyntax]:
        """Extract FileSyntax from all files.

        Args:
            file_paths: List of file paths to process
            root_dir: Root directory for relative path calculation
            parallel: Use parallel processing (default: True)
            content_cache: Optional dict to store file content for later reuse

        Returns:
            Dict mapping relative path to FileSyntax
        """
        results: dict[str, FileSyntax] = {}

        # Thread-safe wrapper for content cache
        cache_lock = Lock() if content_cache is not None else None

        def _extract_with_cache(fp: Path) -> FileSyntax | None:
            """Extract and optionally cache content (thread-safe)."""
            if content_cache is None:
                return self.extract(fp, root_dir)

            # Use local dict, merge under lock
            local_cache: dict[str, str] = {}
            result = self.extract(fp, root_dir, local_cache)
            if local_cache and cache_lock:
                with cache_lock:
                    content_cache.update(local_cache)
            return result

        if not parallel or len(file_paths) < 10:
            # Sequential for small batches (parallel overhead not worth it)
            for file_path in file_paths:
                syntax = _extract_with_cache(file_path)
                if syntax is not None:
                    results[syntax.path] = syntax
        else:
            # Parallel extraction for larger codebases
            with ThreadPoolExecutor(max_workers=self._max_workers) as executor:
                futures = {executor.submit(_extract_with_cache, fp): fp for fp in file_paths}
                for future in as_completed(futures):
                    try:
                        syntax = future.result()
                        if syntax is not None:
                            results[syntax.path] = syntax
                    except Exception as e:
                        fp = futures[future]
                        logger.debug(f"Error extracting {fp}: {e}")

        # Warn if fallback rate is high
        self._check_fallback_rate()

        return results

    def _check_fallback_rate(self) -> None:
        """Log fallback rate information.

        - If tree-sitter is not installed at all, use INFO (expected behavior).
        - If tree-sitter IS installed but many files fell back, use WARNING
          (something is actually wrong).
        """
        if self.total_count == 0:
            return

        fallback_rate = self.fallback_count / self.total_count
        if fallback_rate > 0.2:
            if TREE_SITTER_AVAILABLE:
                # tree-sitter is installed but failing on many files — real problem
                logger.warning(
                    f"tree-sitter installed but {self.fallback_count}/{self.total_count} "
                    f"({fallback_rate:.1%}) files fell back to regex. "
                    "Check for unsupported languages or syntax errors."
                )
            else:
                # tree-sitter not installed — expected, just inform once at INFO
                logger.info(
                    f"Using regex parsing ({self.total_count} files). "
                    "For richer analysis: pip install shannon-codebase-insight[parsing]"
                )
        elif self.fallback_count > 0:
            logger.debug(
                f"Fallback rate: {self.fallback_count}/{self.total_count} "
                f"({fallback_rate:.1%}) files used regex fallback"
            )

    @property
    def fallback_rate(self) -> float:
        """Get current fallback rate (0.0 to 1.0)."""
        if self.total_count == 0:
            return 0.0
        return self.fallback_count / self.total_count

    def reset_stats(self) -> None:
        """Reset extraction statistics."""
        self.fallback_count = 0
        self.treesitter_count = 0
        self.total_count = 0
        self._cache_hits = 0
        self._cache_misses = 0

    def cache_stats(self) -> dict[str, Any]:
        """Return cache hit/miss statistics.

        Returns:
            Dict with 'hits', 'misses', and 'hit_rate' keys.
        """
        total = self._cache_hits + self._cache_misses
        return {
            "hits": self._cache_hits,
            "misses": self._cache_misses,
            "hit_rate": self._cache_hits / total if total > 0 else 0.0,
        }

    # ── Caching helpers ─────────────────────────────────────────────────

    def _rehydrate_syntax(
        self,
        path: str,
        content_hash: str,
        mtime: float,
        absolute_path: str,
        cached: dict[str, Any],
    ) -> FileSyntax:
        """Reconstruct FileSyntax from cached data with current path.

        The cached data contains scalar metrics. Functions, classes, and
        imports are loaded from their respective tables.

        Args:
            path: Current relative path (may differ from original if renamed).
            content_hash: SHA-256 of the file content.
            mtime: Current mtime of the file.
            absolute_path: Current absolute path for debugging.
            cached: Dict from FactStore.get_parsed_syntax().

        Returns:
            Fully reconstructed FileSyntax.
        """
        assert self._fact_store is not None

        # Reconstruct functions
        cached_functions = self._fact_store.get_functions_for_content(content_hash)
        functions = [self._rehydrate_function(f) for f in cached_functions]

        # Reconstruct classes -- methods are reconstructed from the functions
        # that have a matching class_name
        cached_classes = self._fact_store.get_classes_for_content(content_hash)
        classes = [
            self._rehydrate_class(c, [f for f in functions if f.class_name == c["name"]])
            for c in cached_classes
        ]

        # Reconstruct imports
        cached_imports = self._fact_store.get_imports_for_content(content_hash)
        imports = [self._rehydrate_import(i) for i in cached_imports]

        return FileSyntax(
            path=path,
            functions=functions,
            classes=classes,
            imports=imports,
            language=cached["language"],
            has_main_guard=cached.get("has_main_guard", False),
            mtime=mtime,
            content_hash=content_hash,
            absolute_path=absolute_path,
            _lines=cached.get("lines", 0),
            _tokens=cached.get("tokens", 0),
            _complexity=cached.get("complexity", 1.0) or 1.0,
        )

    @staticmethod
    def _rehydrate_function(f: dict[str, Any]) -> FunctionDef:
        """Reconstruct a FunctionDef from cached dict."""
        return FunctionDef(
            name=f["name"],
            params=f.get("params", []),
            body_tokens=f.get("body_tokens", 0),
            signature_tokens=max(f.get("body_tokens", 0), 1),  # not stored; approximate
            nesting_depth=f.get("nesting_depth", 0),
            start_line=f["start_line"],
            end_line=f["end_line"],
            call_targets=None,  # not cached
            decorators=f.get("decorators", []),
            class_name=f.get("class_name"),
        )

    @staticmethod
    def _rehydrate_class(c: dict[str, Any], methods: list[FunctionDef]) -> ClassDef:
        """Reconstruct a ClassDef from cached dict."""
        return ClassDef(
            name=c["name"],
            bases=c.get("bases", []),
            methods=methods,
            fields=c.get("field_names", []),
            is_abstract=c.get("is_abstract", False),
            start_line=c.get("start_line", 0),
            end_line=c.get("end_line", 0),
        )

    @staticmethod
    def _rehydrate_import(i: dict[str, Any]) -> ImportDecl:
        """Reconstruct an ImportDecl from cached dict."""
        return ImportDecl(
            source=i["source_module"],
            names=i.get("names", []),
            resolved_path=None,  # resolution happens later
        )

    def _cache_syntax(self, content_hash: str, syntax: FileSyntax, parser_type: str) -> None:
        """Cache parsed syntax and its entities by content hash.

        Stores scalar metrics in parsed_syntax, and all functions, classes,
        and imports in their respective tables.

        Args:
            content_hash: SHA-256 of the file content.
            syntax: The parsed FileSyntax to cache.
            parser_type: ``"tree-sitter"`` or ``"regex"``.
        """
        assert self._fact_store is not None

        self._fact_store.store_parsed_syntax(
            content_hash=content_hash,
            language=syntax.language,
            lines=syntax.lines,
            tokens=syntax.tokens,
            complexity=int(syntax.complexity),
            max_nesting=syntax.max_nesting,
            has_main_guard=syntax.has_main_guard,
            stub_ratio=syntax.stub_ratio,
            parser_type=parser_type,
        )

        # Cache functions
        for fn in syntax.functions:
            self._fact_store.store_extracted_function(
                content_hash=content_hash,
                name=fn.name,
                qualified_name=fn.qualified_name,
                start_line=fn.start_line,
                end_line=fn.end_line,
                params=fn.params,
                decorators=fn.decorators,
                body_tokens=fn.body_tokens,
                nesting_depth=fn.nesting_depth,
                is_stub=fn.is_stub,
                class_name=fn.class_name,
            )

        # Cache classes
        for cls in syntax.classes:
            self._fact_store.store_extracted_class(
                content_hash=content_hash,
                name=cls.name,
                start_line=cls.start_line,
                end_line=cls.end_line,
                bases=cls.bases,
                method_names=[m.name for m in cls.methods],
                field_names=cls.fields,
                is_abstract=cls.is_abstract,
                method_count=cls.method_count,
            )

        # Cache imports
        for imp in syntax.imports:
            raw_statement = (
                f"from {imp.source} import {', '.join(imp.names)}"
                if imp.names
                else f"import {imp.source}"
            )
            self._fact_store.store_extracted_import(
                content_hash=content_hash,
                raw_statement=raw_statement,
                source_module=imp.source,
                names=imp.names,
                is_relative=imp.is_relative,
            )

        self._fact_store.commit()


# ══════════════════════════════════════════════════════════════════════════════
# Import Resolution
# ══════════════════════════════════════════════════════════════════════════════


def resolve_all_imports(file_syntaxes: dict[str, FileSyntax]) -> None:
    """Resolve imports across all parsed files.

    Updates ImportDecl.resolved_path and ImportDecl.is_stdlib in place.
    Must be called after all files are parsed, before storing to FactDatabase.

    Args:
        file_syntaxes: Dict mapping path -> FileSyntax (modified in place)
    """
    all_paths = set(file_syntaxes.keys())
    path_index = _build_path_index(all_paths)

    for fs in file_syntaxes.values():
        language = fs.language
        for imp in fs.imports:
            # Check if stdlib first
            if _is_stdlib_import(imp.source, language):
                imp.is_stdlib = True
                imp.resolved_path = None
                continue

            # Try to resolve internal import
            resolved = _resolve_import(imp.source, fs.path, language, path_index, all_paths)
            if resolved:
                imp.resolved_path = resolved
                imp.is_stdlib = False
            else:
                # Unresolved - could be phantom or external
                imp.resolved_path = None
                imp.is_stdlib = False


def _is_stdlib_import(source: str, language: str) -> bool:
    """Check if import is stdlib/third-party (not internal)."""
    stdlib_roots = STDLIB_ROOTS.get(language, set())
    first_segment = source.split(".")[0].split("/")[0]
    return first_segment in stdlib_roots


def _build_path_index(all_paths: set[str]) -> dict[str, str]:
    """Map dotted module paths to file paths for import resolution."""
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


def _infer_project_prefixes(all_paths: set[str]) -> set[str]:
    """Infer project namespace prefixes from file paths."""
    prefixes: set[str] = set()
    for path in all_paths:
        parts = Path(path).parts
        if len(parts) >= 2:
            prefixes.add(parts[0])
            if parts[0] == "src" and len(parts) >= 3:
                prefixes.add(parts[1])
    return prefixes


def _resolve_import(
    imp: str,
    source_path: str,
    language: str,
    path_index: dict[str, str],
    all_paths: set[str],
) -> str | None:
    """Resolve an import string to a file path in the codebase."""
    imp = imp.strip()

    # Relative imports
    if imp.startswith("."):
        return _resolve_relative_import(imp, source_path, language, all_paths)

    # Absolute imports - try exact match
    if imp in path_index:
        return path_index[imp]

    # Try with project prefixes
    for prefix in ("src.", "src.shannon_insight."):
        candidate = prefix + imp
        if candidate in path_index:
            return path_index[candidate]

    # Try stripping prefixes
    parts = imp.split(".")
    for i in range(1, len(parts)):
        suffix = ".".join(parts[i:])
        if suffix in path_index:
            return path_index[suffix]

    return None


def _resolve_relative_import(
    imp: str, source_path: str, language: str, all_paths: set[str]
) -> str | None:
    """Resolve a relative import like ..models or ./utils."""
    # Handle JS/TS style "./" and "../"
    if imp.startswith("./") or imp.startswith("../"):
        return _resolve_path_relative(imp, source_path, language, all_paths)

    # Handle Python-style ".module" and "..module"
    return _resolve_dot_relative(imp, source_path, language, all_paths)


def _resolve_path_relative(
    imp: str, source_path: str, language: str, all_paths: set[str]
) -> str | None:
    """Resolve JS/TS style relative imports like ./utils."""
    source_dir = Path(source_path).parent
    target_path = source_dir / imp

    # Normalize
    try:
        normalized = str(target_path).replace("\\", "/")
        # Remove any leading ./
        while normalized.startswith("./"):
            normalized = normalized[2:]
    except Exception:
        return None

    extensions = LANGUAGE_EXTENSIONS.get(language, [".py"])

    for ext in extensions:
        if ext.startswith("/"):
            candidate = normalized + ext
        else:
            candidate = normalized + ext
        candidate = candidate.replace("\\", "/")
        if candidate in all_paths:
            return candidate

    if normalized in all_paths:
        return normalized

    return None


def _resolve_dot_relative(
    imp: str, source_path: str, language: str, all_paths: set[str]
) -> str | None:
    """Resolve Python-style relative import like ..models."""
    dot_count = 0
    while dot_count < len(imp) and imp[dot_count] == ".":
        dot_count += 1
    module_part = imp[dot_count:]

    source_dir = Path(source_path).parent
    for _ in range(dot_count - 1):
        source_dir = source_dir.parent

    extensions = LANGUAGE_EXTENSIONS.get(language, [".py"])

    candidates = []
    if module_part:
        module_as_path = module_part.replace(".", "/")
        for ext in extensions:
            if ext.startswith("/"):
                candidates.append(str(source_dir / module_as_path) + ext)
            else:
                candidates.append(str(source_dir / module_as_path) + ext)
    else:
        for ext in extensions:
            if ext.startswith("/"):
                candidates.append(str(source_dir) + ext)

    for candidate in candidates:
        normalized = candidate.replace("\\", "/")
        if normalized in all_paths:
            return normalized
        for path in all_paths:
            if path.endswith(normalized) or normalized.endswith(path):
                return path

    return None
