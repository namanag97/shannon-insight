"""
Safe file operations for Shannon Insight.

Provides timeout-protected and size-limited file operations.
"""

import signal
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path
from typing import Optional

from .exceptions import FileAccessError, SecurityError
from .security import PathValidator, ResourceLimiter


class TimeoutError(Exception):
    """Raised when an operation times out."""

    pass


def _timeout_handler(signum, frame):
    """Signal handler for timeout."""
    raise TimeoutError("Operation timed out")


@contextmanager
def timeout(seconds: int):
    """
    Context manager for timeout protection.

    Args:
        seconds: Timeout in seconds

    Raises:
        TimeoutError: If operation exceeds timeout
    """
    # Set up signal handler
    old_handler = signal.signal(signal.SIGALRM, _timeout_handler)
    signal.alarm(seconds)

    try:
        yield
    finally:
        # Restore old handler and cancel alarm
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old_handler)


def safe_read_file(
    filepath: Path,
    validator: Optional[PathValidator] = None,
    limiter: Optional[ResourceLimiter] = None,
    timeout_seconds: int = 10,
    encoding: str = "utf-8",
    errors: str = "replace",
) -> str:
    """
    Safely read a file with security checks and timeout protection.

    Args:
        filepath: File to read
        validator: Path validator (if None, skips path validation)
        limiter: Resource limiter (if None, skips size check)
        timeout_seconds: Timeout in seconds
        encoding: Text encoding
        errors: How to handle encoding errors

    Returns:
        File contents as string

    Raises:
        FileAccessError: If file cannot be read
        SecurityError: If security checks fail
        TimeoutError: If read operation times out
    """
    # Validate path
    if validator:
        filepath = validator.validate_path(filepath)

    # Check file size
    if limiter:
        limiter.check_file_size(filepath)

    # Read with timeout protection
    try:
        with timeout(timeout_seconds):
            with open(filepath, encoding=encoding, errors=errors) as f:
                return f.read()
    except TimeoutError:
        raise FileAccessError(filepath, f"Read operation timed out after {timeout_seconds}s")
    except UnicodeDecodeError as e:
        raise FileAccessError(filepath, f"Encoding error: {e}")
    except OSError as e:
        raise FileAccessError(filepath, f"OS error: {e}")
    except Exception as e:
        raise FileAccessError(filepath, f"Unexpected error: {e}")


def safe_scan_directory(
    root_dir: Path,
    pattern: str = "**/*",
    validator: Optional[PathValidator] = None,
    limiter: Optional[ResourceLimiter] = None,
    follow_symlinks: bool = False,
) -> Generator[Path, None, None]:
    """
    Safely scan a directory with security checks.

    Args:
        root_dir: Directory to scan
        pattern: Glob pattern
        validator: Path validator
        limiter: Resource limiter
        follow_symlinks: Whether to follow symbolic links

    Yields:
        Safe file paths

    Raises:
        SecurityError: If resource limits are exceeded
    """
    # Validate root directory
    if validator:
        root_dir = validator.validate_path(root_dir)

    try:
        for path in root_dir.glob(pattern):
            # Skip symlinks if not following them
            if path.is_symlink() and not follow_symlinks:
                continue

            # Skip directories
            if path.is_dir():
                continue

            # Check file count limit
            if limiter:
                limiter.increment_file_count()

            # Validate path
            if validator:
                try:
                    path = validator.validate_path(path)
                except (SecurityError, Exception):
                    # Skip files that fail validation
                    continue

            # Check file size
            if limiter:
                try:
                    limiter.check_file_size(path)
                except SecurityError:
                    # Skip files that exceed size limit
                    continue

            yield path

    except OSError as e:
        raise FileAccessError(root_dir, f"Directory scan failed: {e}")


def safe_write_file(
    filepath: Path, content: str, validator: Optional[PathValidator] = None, encoding: str = "utf-8"
) -> None:
    """
    Safely write to a file with validation.

    Args:
        filepath: File to write
        content: Content to write
        validator: Path validator
        encoding: Text encoding

    Raises:
        FileAccessError: If file cannot be written
        SecurityError: If security checks fail
    """
    # Validate path (parent directory)
    if validator:
        parent = filepath.parent
        if parent.exists():
            validator.validate_path(parent)

    try:
        # Create parent directory if it doesn't exist
        filepath.parent.mkdir(parents=True, exist_ok=True)

        # Write file
        with open(filepath, "w", encoding=encoding) as f:
            f.write(content)

    except OSError as e:
        raise FileAccessError(filepath, f"Write failed: {e}")
    except Exception as e:
        raise FileAccessError(filepath, f"Unexpected error: {e}")


def should_skip_file(filepath: Path, exclude_patterns: list[str]) -> bool:
    """
    Check if a file should be skipped based on exclusion patterns.

    Args:
        filepath: File to check
        exclude_patterns: List of glob patterns to exclude

    Returns:
        True if file should be skipped
    """
    for pattern in exclude_patterns:
        if filepath.match(pattern):
            return True
    return False
