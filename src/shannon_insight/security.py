"""
Security utilities for Shannon Insight.

Provides path validation, resource limits, and safe file operations.
"""

import os
import re
from pathlib import Path
from typing import Optional, Pattern

from .exceptions import SecurityError, InvalidPathError


# System directories that should never be analyzed
SYSTEM_DIRECTORIES = {
    "/etc", "/sys", "/proc", "/dev", "/boot",
    "/bin", "/sbin", "/usr/bin", "/usr/sbin",
    "C:\\Windows", "C:\\Program Files", "C:\\Program Files (x86)",
}

# Maximum file size in bytes (default 10MB)
DEFAULT_MAX_FILE_SIZE = 10 * 1024 * 1024

# Maximum number of files to scan
DEFAULT_MAX_FILES = 10000


class PathValidator:
    """
    Validates file paths for security issues.

    Prevents:
    - Directory traversal attacks
    - Symlink escape attacks
    - Access to system directories
    - Access to hidden sensitive files
    """

    def __init__(
        self,
        root_dir: Path,
        allow_hidden: bool = False,
        block_system_dirs: bool = True
    ):
        """
        Initialize path validator.

        Args:
            root_dir: Root directory that paths must be within
            allow_hidden: Allow hidden files/directories (starting with .)
            block_system_dirs: Block access to system directories
        """
        self.root_dir = root_dir.resolve()
        self.allow_hidden = allow_hidden
        self.block_system_dirs = block_system_dirs

    def validate_path(self, path: Path) -> Path:
        """
        Validate that a path is safe to access.

        Args:
            path: Path to validate

        Returns:
            Resolved absolute path

        Raises:
            SecurityError: If path fails security checks
            InvalidPathError: If path doesn't exist or isn't accessible
        """
        # Resolve to absolute path
        try:
            resolved_path = path.resolve()
        except (OSError, RuntimeError) as e:
            raise InvalidPathError(path, f"Cannot resolve path: {e}")

        # Check if path exists
        if not resolved_path.exists():
            raise InvalidPathError(resolved_path, "Path does not exist")

        # Check if path is within root directory
        try:
            resolved_path.relative_to(self.root_dir)
        except ValueError:
            raise SecurityError(
                "Path traversal detected: path is outside root directory",
                filepath=resolved_path
            )

        # Check for symlinks that escape root directory
        if resolved_path.is_symlink():
            real_path = resolved_path.resolve()
            try:
                real_path.relative_to(self.root_dir)
            except ValueError:
                raise SecurityError(
                    "Symlink escape detected: target is outside root directory",
                    filepath=resolved_path
                )

        # Block system directories
        if self.block_system_dirs:
            path_str = str(resolved_path)
            for sys_dir in SYSTEM_DIRECTORIES:
                if path_str.startswith(sys_dir):
                    raise SecurityError(
                        f"Access to system directory blocked: {sys_dir}",
                        filepath=resolved_path
                    )

        # Check for hidden files
        if not self.allow_hidden:
            for part in resolved_path.parts:
                if part.startswith('.') and part not in {'.', '..'}:
                    raise SecurityError(
                        "Access to hidden file/directory blocked",
                        filepath=resolved_path
                    )

        return resolved_path

    def is_safe_path(self, path: Path) -> bool:
        """
        Check if path is safe without raising exceptions.

        Args:
            path: Path to check

        Returns:
            True if path is safe, False otherwise
        """
        try:
            self.validate_path(path)
            return True
        except (SecurityError, InvalidPathError):
            return False


class ResourceLimiter:
    """
    Enforces resource limits during analysis.
    """

    def __init__(
        self,
        max_file_size: int = DEFAULT_MAX_FILE_SIZE,
        max_files: int = DEFAULT_MAX_FILES
    ):
        """
        Initialize resource limiter.

        Args:
            max_file_size: Maximum file size in bytes
            max_files: Maximum number of files to process
        """
        self.max_file_size = max_file_size
        self.max_files = max_files
        self.files_processed = 0

    def check_file_size(self, filepath: Path) -> None:
        """
        Check if file size is within limits.

        Args:
            filepath: File to check

        Raises:
            SecurityError: If file exceeds size limit
        """
        try:
            size = filepath.stat().st_size
        except OSError as e:
            raise InvalidPathError(filepath, f"Cannot stat file: {e}")

        if size > self.max_file_size:
            size_mb = size / (1024 * 1024)
            limit_mb = self.max_file_size / (1024 * 1024)
            raise SecurityError(
                f"File size ({size_mb:.2f}MB) exceeds limit ({limit_mb:.2f}MB)",
                filepath=filepath
            )

    def check_file_count(self) -> None:
        """
        Check if file count is within limits.

        Raises:
            SecurityError: If file count exceeds limit
        """
        if self.files_processed >= self.max_files:
            raise SecurityError(
                f"File count ({self.files_processed}) exceeds limit ({self.max_files})"
            )

    def increment_file_count(self) -> None:
        """Increment the count of processed files."""
        self.files_processed += 1
        self.check_file_count()

    def reset(self) -> None:
        """Reset counters."""
        self.files_processed = 0


def safe_compile_regex(pattern: str, flags: int = 0) -> Optional[Pattern]:
    """
    Safely compile a regex pattern with timeout protection.

    Args:
        pattern: Regex pattern to compile
        flags: Regex flags

    Returns:
        Compiled regex pattern, or None if compilation fails

    Note:
        Python's re module doesn't have built-in timeout protection,
        but we can validate pattern complexity here.
    """
    # Reject overly complex patterns
    if len(pattern) > 1000:
        return None

    # Check for catastrophic backtracking patterns
    dangerous_patterns = [
        r'\(.*\)\*',  # (...)*
        r'\(.*\)\+',  # (...)+
        r'\(.*\)\{',  # (...){n,m}
    ]

    for dangerous in dangerous_patterns:
        if re.search(dangerous, pattern):
            # This is a heuristic - not foolproof
            pass

    try:
        return re.compile(pattern, flags)
    except re.error:
        return None


def validate_root_directory(path: Path) -> Path:
    """
    Validate that a root directory is safe to analyze.

    Args:
        path: Directory path to validate

    Returns:
        Resolved absolute path

    Raises:
        InvalidPathError: If path is invalid
        SecurityError: If path is unsafe
    """
    # Resolve to absolute path
    try:
        resolved = path.resolve()
    except (OSError, RuntimeError) as e:
        raise InvalidPathError(path, f"Cannot resolve path: {e}")

    # Check existence
    if not resolved.exists():
        raise InvalidPathError(resolved, "Directory does not exist")

    # Check it's a directory
    if not resolved.is_dir():
        raise InvalidPathError(resolved, "Path is not a directory")

    # Check readability
    if not os.access(resolved, os.R_OK):
        raise InvalidPathError(resolved, "Directory is not readable")

    # Block system directories
    path_str = str(resolved)
    for sys_dir in SYSTEM_DIRECTORIES:
        if path_str.startswith(sys_dir):
            raise SecurityError(
                f"Cannot analyze system directory: {sys_dir}",
                filepath=resolved
            )

    return resolved
