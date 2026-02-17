"""Environment discovery for Shannon Insight.

This module discovers facts about the target codebase and system capabilities.
Discovery is fast (uses git index when available) and immutable once created.

Example:
    >>> env = discover_environment(Path("/path/to/code"))
    >>> env.file_count
    142
    >>> env.is_git_repo
    True
    >>> env.detected_languages
    {'python', 'typescript'}
"""

from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from .logging_config import get_logger
from .scanning.languages import SKIP_DIRS

logger = get_logger(__name__)


@dataclass(frozen=True)
class Environment:
    """Immutable snapshot of environment facts.

    All fields are discovered automatically. Users should never construct
    this directly - use discover_environment() instead.

    Attributes:
        root: Absolute path to codebase root
        file_count: Total source files found (excludes common ignore patterns)
        file_paths: List of discovered file paths (relative to root)
        detected_languages: Programming languages detected from file extensions
        is_git_repo: Whether target is inside a git repository
        git_branch: Current git branch name (None if not a git repo)
        has_tree_sitter: Whether tree-sitter parsing is available
        system_cores: Number of CPU cores available
    """

    root: Path
    file_count: int
    file_paths: tuple[Path, ...] = field(default_factory=tuple)
    detected_languages: frozenset[str] = field(default_factory=frozenset)
    is_git_repo: bool = False
    git_branch: Optional[str] = None
    has_tree_sitter: bool = False
    system_cores: int = 1


def discover_environment(
    root: Path | str,
    allow_hidden_files: bool = False,
    follow_symlinks: bool = False,
) -> Environment:
    """Discover environment facts about the target codebase.

    This function performs fast discovery using git when available:
    - File counting: uses `git ls-files` (fast, uses index)
    - Language detection: scans file extensions
    - Git info: checks if repo exists and current branch
    - Capabilities: checks for tree-sitter availability

    Args:
        root: Path to codebase root directory
        allow_hidden_files: Include hidden files (starting with .)
        follow_symlinks: Follow symbolic links during discovery

    Returns:
        Immutable Environment instance

    Raises:
        FileNotFoundError: If root directory doesn't exist
        PermissionError: If root directory isn't readable

    Example:
        >>> env = discover_environment("/path/to/code")
        >>> env.file_count
        142
        >>> env.is_git_repo
        True
    """
    root_path = Path(root).resolve()

    if not root_path.exists():
        raise FileNotFoundError(f"Directory not found: {root_path}")
    if not root_path.is_dir():
        raise NotADirectoryError(f"Not a directory: {root_path}")

    # Discover git info
    is_git = _is_git_repository(root_path)
    git_branch = _get_git_branch(root_path) if is_git else None

    # Discover files and languages
    if is_git:
        # Fast path: use git index
        files = _get_git_files(root_path, allow_hidden_files=allow_hidden_files)
    else:
        # Fallback: manual walk
        files = _walk_directory(
            root_path,
            allow_hidden_files=allow_hidden_files,
            follow_symlinks=follow_symlinks,
        )

    file_count = len(files)
    languages = _detect_languages(files)

    # Discover capabilities
    has_tree_sitter = _check_tree_sitter_available()
    system_cores = os.cpu_count() or 1

    logger.debug(
        f"Environment discovered: {file_count} files, "
        f"{len(languages)} languages, git={is_git}, cores={system_cores}"
    )

    return Environment(
        root=root_path,
        file_count=file_count,
        file_paths=tuple(files),
        detected_languages=frozenset(languages),
        is_git_repo=is_git,
        git_branch=git_branch,
        has_tree_sitter=has_tree_sitter,
        system_cores=system_cores,
    )


def _is_git_repository(root: Path) -> bool:
    """Check if directory is inside a git repository.

    Args:
        root: Directory to check

    Returns:
        True if inside a git repo, False otherwise
    """
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "--is-inside-work-tree"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def _get_git_branch(root: Path) -> Optional[str]:
    """Get current git branch name.

    Args:
        root: Git repository root

    Returns:
        Branch name or None if detached HEAD or error
    """
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            branch = result.stdout.strip()
            return None if branch == "HEAD" else branch
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return None


def _get_git_files(root: Path, allow_hidden_files: bool = False) -> list[Path]:
    """Get list of files from git index that exist on disk.

    Uses `git ls-files` to get tracked files. This is much faster than
    walking the directory tree manually.

    Important: Filters out files that are deleted in working tree but not
    yet committed (staged deletions). Only returns files that actually exist.

    Args:
        root: Git repository root
        allow_hidden_files: Include hidden files (starting with .)

    Returns:
        List of relative file paths (only those that exist on disk)
    """
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "ls-files"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            files = []
            for line in result.stdout.splitlines():
                line = line.strip()
                if not line or not _is_source_file(line, allow_hidden_files):
                    continue
                # Only include files that actually exist on disk
                file_path = root / line
                if file_path.exists():
                    files.append(Path(line))
            return files
    except (subprocess.TimeoutExpired, FileNotFoundError):
        logger.warning("git ls-files failed, falling back to directory walk")

    # Fallback to manual walk
    return _walk_directory(root, allow_hidden_files=allow_hidden_files)


def _walk_directory(
    root: Path,
    allow_hidden_files: bool = False,
    follow_symlinks: bool = False,
) -> list[Path]:
    """Manually walk directory tree to find source files.

    Fallback when git is not available. Applies basic exclude patterns
    to avoid walking into common ignore directories.

    Args:
        root: Directory root
        allow_hidden_files: Include hidden files (starting with .)
        follow_symlinks: Follow symbolic links

    Returns:
        List of relative file paths
    """
    files: list[Path] = []
    for item in root.rglob("*"):
        # Skip if any parent directory is in SKIP_DIRS (canonical constant from languages.py)
        if any(part in SKIP_DIRS for part in item.parts):
            continue

        # Skip symlinks if not following them
        if item.is_symlink() and not follow_symlinks:
            continue

        if item.is_file() and _is_source_file(str(item.relative_to(root)), allow_hidden_files):
            files.append(item.relative_to(root))

    return files


def _is_source_file(path: str, allow_hidden_files: bool = False) -> bool:
    """Check if file is a source code file.

    Args:
        path: File path (relative or absolute)
        allow_hidden_files: Include hidden files (starting with .)

    Returns:
        True if file appears to be source code
    """
    # Exclude hidden files unless allowed
    if not allow_hidden_files and Path(path).name.startswith("."):
        return False

    # Check for source code extensions
    source_extensions = {
        ".py",
        ".js",
        ".ts",
        ".tsx",
        ".jsx",
        ".go",
        ".java",
        ".rs",
        ".rb",
        ".cpp",
        ".cc",
        ".c",
        ".h",
        ".hpp",
        ".cs",
        ".php",
        ".swift",
        ".kt",
        ".scala",
    }

    return Path(path).suffix.lower() in source_extensions


def _detect_languages(files: list[Path]) -> set[str]:
    """Detect programming languages from file extensions.

    Args:
        files: List of file paths

    Returns:
        Set of language names (lowercase)
    """
    # Extension to language mapping
    ext_to_lang = {
        ".py": "python",
        ".js": "javascript",
        ".ts": "typescript",
        ".tsx": "typescript",
        ".jsx": "javascript",
        ".go": "go",
        ".java": "java",
        ".rs": "rust",
        ".rb": "ruby",
        ".cpp": "cpp",
        ".cc": "cpp",
        ".c": "c",
        ".h": "c",
        ".hpp": "cpp",
        ".cs": "csharp",
        ".php": "php",
        ".swift": "swift",
        ".kt": "kotlin",
        ".scala": "scala",
    }

    languages = set()
    for file in files:
        ext = file.suffix.lower()
        if ext in ext_to_lang:
            languages.add(ext_to_lang[ext])

    return languages


def _check_tree_sitter_available() -> bool:
    """Check if tree-sitter is available for parsing.

    Returns:
        True if tree-sitter can be imported, False otherwise
    """
    try:
        import tree_sitter  # noqa: F401

        return True
    except ImportError:
        return False
