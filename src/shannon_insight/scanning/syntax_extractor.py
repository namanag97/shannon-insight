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
from pathlib import Path
from typing import TYPE_CHECKING

from .fallback import RegexFallbackScanner
from .languages import detect_language
from .models_v2 import FileSyntax
from .normalizer import TreeSitterNormalizer
from .treesitter_parser import TREE_SITTER_AVAILABLE

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class SyntaxExtractor:
    """Extracts FileSyntax from source files.

    Attributes:
        fallback_count: Number of files that used regex fallback
        treesitter_count: Number of files parsed with tree-sitter
        total_count: Total files processed
    """

    def __init__(self) -> None:
        """Initialize extractor with tree-sitter normalizer and regex fallback."""
        self._normalizer = TreeSitterNormalizer() if TREE_SITTER_AVAILABLE else None
        self._fallback = RegexFallbackScanner()
        self.fallback_count = 0
        self.treesitter_count = 0
        self.total_count = 0

    def extract(self, file_path: Path, root_dir: Path) -> FileSyntax | None:
        """Extract FileSyntax from a single file.

        Args:
            file_path: Path to the file
            root_dir: Root directory for relative path calculation

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

        self.total_count += 1

        # Try tree-sitter first
        if self._normalizer is not None:
            syntax = self._normalizer.parse_file(content, rel_path, language)
            if syntax is not None:
                self.treesitter_count += 1
                return syntax

        # Fall back to regex
        self.fallback_count += 1
        return self._fallback.parse(content, rel_path, language)

    def extract_all(self, file_paths: list[Path], root_dir: Path) -> dict[str, FileSyntax]:
        """Extract FileSyntax from all files.

        Args:
            file_paths: List of file paths to process
            root_dir: Root directory for relative path calculation

        Returns:
            Dict mapping relative path to FileSyntax
        """
        results: dict[str, FileSyntax] = {}

        for file_path in file_paths:
            syntax = self.extract(file_path, root_dir)
            if syntax is not None:
                results[syntax.path] = syntax

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
