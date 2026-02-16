"""SyntaxExtractor: produces FileSyntax for all scanned files.

This component sits alongside the existing scanner and produces v2 FileSyntax
objects. It tries tree-sitter first, falls back to regex.

Usage:
    extractor = SyntaxExtractor()
    results = extractor.extract_all(file_paths, root_dir)
    # results is dict[path, FileSyntax]

Fallback behavior:
    1. If tree-sitter is available and supports the language: use tree-sitter
    2. If tree-sitter fails (syntax error, encoding error): use regex fallback
    3. If tree-sitter not installed: use regex fallback

The fallback rate is tracked. If >20% of files use fallback, a warning is logged.
"""

from __future__ import annotations

import logging
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from threading import Lock
from typing import TYPE_CHECKING

from .fallback import RegexFallbackScanner
from .languages import detect_language
from .syntax import FileSyntax
from .normalizer import TreeSitterNormalizer
from .treesitter_parser import TREE_SITTER_AVAILABLE

if TYPE_CHECKING:
    pass

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

    def __init__(self, max_workers: int | None = None) -> None:
        """Initialize extractor with tree-sitter normalizer and regex fallback.

        Args:
            max_workers: Max parallel workers for extract_all(). Defaults to CPU count (max 8).
        """
        self._normalizer = TreeSitterNormalizer() if TREE_SITTER_AVAILABLE else None
        self._fallback = RegexFallbackScanner()
        self._max_workers = max_workers or _DEFAULT_WORKERS
        self._lock = Lock()  # Thread-safe counter updates
        self.fallback_count = 0
        self.treesitter_count = 0
        self.total_count = 0

    def extract(
        self, file_path: Path, root_dir: Path, content_cache: dict[str, str] | None = None
    ) -> FileSyntax | None:
        """Extract FileSyntax from a single file.

        Args:
            file_path: Path to the file
            root_dir: Root directory for relative path calculation
            content_cache: Optional dict to store file content for later reuse

        Returns:
            FileSyntax or None if file cannot be read
        """
        try:
            content = file_path.read_text(encoding="utf-8", errors="replace")
        except OSError as e:
            logger.debug(f"Cannot read {file_path}: {e}")
            return None

        rel_path = str(file_path.relative_to(root_dir))
        language = detect_language(file_path)

        # Cache content for later reuse (e.g., compression ratio)
        if content_cache is not None:
            content_cache[rel_path] = content

        # Thread-safe counter updates
        with self._lock:
            self.total_count += 1

        # Try tree-sitter first
        if self._normalizer is not None:
            syntax = self._normalizer.parse_file(content, rel_path, language)
            if syntax is not None:
                with self._lock:
                    self.treesitter_count += 1
                return syntax

        # Fall back to regex
        with self._lock:
            self.fallback_count += 1
        return self._fallback.parse(content, rel_path, language)

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
