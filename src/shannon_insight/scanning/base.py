"""Base scanner class for language-agnostic functionality"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from ..config import AnalysisSettings, default_settings
from ..exceptions import FileAccessError, ParsingError
from ..file_ops import should_skip_file
from ..logging_config import get_logger
from .models import FileMetrics

logger = get_logger(__name__)


class BaseScanner(ABC):
    """Abstract base class for language-specific scanners"""

    def __init__(
        self, root_dir: str, extensions: list[str], settings: Optional[AnalysisSettings] = None
    ):
        """
        Initialize scanner.

        Args:
            root_dir: Root directory to scan
            extensions: File extensions to include (e.g., ['.go', '.py'])
            settings: Analysis settings
        """
        self.root_dir = Path(root_dir)
        self.extensions = extensions
        self.settings = settings or default_settings
        logger.debug(f"Initialized {self.__class__.__name__} for {self.root_dir}")

    def scan(self) -> list[FileMetrics]:
        """
        Scan all source files and extract metrics.

        Returns:
            List of file metrics for analyzed files
        """
        files = []
        files_scanned = 0
        files_skipped = 0
        files_errored = 0

        # Pre-compute extension set for O(1) lookups
        ext_set = set(self.extensions)

        # Track visited inodes to detect symlink loops
        visited_inodes: set[tuple[int, int]] = set()

        # Single tree walk - much faster than multiple rglob() calls
        # Wrap in try to catch RecursionError from symlink loops
        try:
            file_iterator = self.root_dir.rglob("*")
        except RecursionError:
            logger.error("Symlink loop detected during directory traversal")
            return files

        for filepath in file_iterator:
            # Skip directories
            if not filepath.is_file():
                continue

            # Check extension match (O(1) set lookup)
            if filepath.suffix not in ext_set:
                continue

            # Check file count limit
            if files_scanned >= self.settings.max_files:
                logger.warning(f"Reached max files limit ({self.settings.max_files})")
                break

            # Skip based on custom logic
            if self._should_skip(filepath):
                files_skipped += 1
                logger.debug(f"Skipped (custom): {filepath}")
                continue

            # Skip based on exclusion patterns
            if should_skip_file(filepath, self.settings.exclude_patterns):
                files_skipped += 1
                logger.debug(f"Skipped (pattern): {filepath}")
                continue

            # Check file size
            try:
                size = filepath.stat().st_size
                if size > self.settings.max_file_size_bytes:
                    files_skipped += 1
                    logger.debug(f"Skipped (size): {filepath} ({size} bytes)")
                    continue
            except OSError as e:
                files_errored += 1
                logger.warning(f"Cannot stat {filepath}: {e}")
                continue

            # Analyze file
            try:
                metrics = self._analyze_file(filepath)
                files.append(metrics)
                files_scanned += 1
                logger.debug(f"Analyzed: {filepath}")
            except FileAccessError as e:
                files_errored += 1
                logger.warning(f"Access error for {filepath}: {e.reason}")
            except ParsingError as e:
                files_errored += 1
                logger.warning(f"Parse error for {filepath}: {e.reason}")
            except Exception as e:
                files_errored += 1
                logger.error(f"Unexpected error analyzing {filepath}: {e}")

        logger.info(
            f"Scan complete: {files_scanned} analyzed, {files_skipped} skipped, {files_errored} errors"
        )
        return files

    @abstractmethod
    def _should_skip(self, filepath: Path) -> bool:
        """
        Determine if file should be skipped (e.g., tests, vendor).

        Args:
            filepath: File to check

        Returns:
            True if file should be skipped
        """
        pass

    @abstractmethod
    def _analyze_file(self, filepath: Path) -> FileMetrics:
        """
        Extract all metrics from a single file.

        Args:
            filepath: File to analyze

        Returns:
            File metrics

        Raises:
            FileAccessError: If file cannot be read
            ParsingError: If file cannot be parsed
        """
        pass

    @abstractmethod
    def _count_tokens(self, content: str) -> int:
        """
        Count tokens in source code.

        Args:
            content: File content

        Returns:
            Token count
        """
        pass

    @abstractmethod
    def _extract_imports(self, content: str) -> list[str]:
        """
        Extract import statements.

        Args:
            content: File content

        Returns:
            List of import paths/names
        """
        pass

    @abstractmethod
    def _extract_exports(self, content: str) -> list[str]:
        """
        Extract exported identifiers.

        Args:
            content: File content

        Returns:
            List of exported names
        """
        pass

    @abstractmethod
    def _count_functions(self, content: str) -> int:
        """
        Count function declarations.

        Args:
            content: File content

        Returns:
            Function count
        """
        pass

    @abstractmethod
    def _estimate_complexity(self, content: str) -> float:
        """
        Estimate cyclomatic complexity.

        Args:
            content: File content

        Returns:
            Complexity score
        """
        pass

    def _max_nesting_depth(self, content: str) -> int:
        """
        Calculate maximum nesting depth (language-agnostic).

        Args:
            content: File content

        Returns:
            Maximum nesting depth
        """
        max_depth = 0
        current_depth = 0

        for char in content:
            if char == "{":
                current_depth += 1
                max_depth = max(max_depth, current_depth)
            elif char == "}":
                current_depth -= 1

        return max_depth
