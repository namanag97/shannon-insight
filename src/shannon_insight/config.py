"""Configuration loading and management for Shannon Insight.

This module provides configuration discovery and validation. Configuration
sources are merged in priority order:
    1. Defaults (defined in AnalysisConfig)
    2. Global config (~/.shannon-insight.toml)
    3. Project config (./shannon-insight.toml)
    4. CLI overrides (passed as kwargs)

Example:
    >>> config = load_config(verbose=True, max_findings=100)
    >>> config.verbosity
    'verbose'
    >>> config.max_findings
    100
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal, Optional, get_type_hints

from .exceptions import ShannonInsightError

# Type aliases for clarity
Verbosity = Literal["quiet", "normal", "verbose"]


@dataclass(frozen=True)
class AnalysisConfig:
    """Configuration for analysis execution.

    All fields have sensible defaults. Users typically override only a few
    fields via CLI flags or config file.

    Attributes:
        Analysis algorithm parameters:
            pagerank_damping: Damping factor for PageRank (0.0-1.0)
            pagerank_iterations: Maximum iterations for PageRank convergence
            pagerank_tolerance: Convergence tolerance for PageRank

        Performance tuning:
            workers: Number of parallel workers (None = auto-detect)
            timeout_seconds: Timeout for file operations

        Caching:
            cache_enabled: Enable disk caching for faster re-analysis
            cache_dir: Directory for cache storage
            cache_ttl_hours: Cache time-to-live in hours

        File filtering:
            exclude_patterns: Glob patterns to exclude from analysis
            max_file_size_mb: Maximum file size to analyze (MB)
            max_files: Maximum number of files to analyze

        Git integration:
            git_max_commits: Maximum commits to analyze (0 = unlimited)
            git_min_commits: Minimum commits required for temporal analysis

        Output control:
            max_findings: Maximum findings to return
            verbosity: Logging verbosity level

        Feature flags:
            enable_validation: Enable phase validation contracts
            enable_history: Auto-save snapshots to .shannon/ directory

        Provenance tracking:
            enable_provenance: Enable signal provenance tracking (off by default)
            provenance_retention_hours: Hours to retain stale provenance data

        Security:
            allow_hidden_files: Include hidden files (starting with .)
            follow_symlinks: Follow symbolic links during scanning
    """

    # Analysis algorithm parameters
    pagerank_damping: float = 0.85
    pagerank_iterations: int = 20
    pagerank_tolerance: float = 1e-6

    # Performance tuning
    workers: Optional[int] = None  # None = auto-detect from CPU cores
    timeout_seconds: int = 10

    # Caching
    cache_enabled: bool = True
    cache_dir: str = ".shannon-cache"
    cache_ttl_hours: int = 24

    # File filtering
    exclude_patterns: list[str] = field(
        default_factory=lambda: [
            "*_test.go",
            "*_test.ts",
            "*.test.ts",
            "*.spec.ts",
            "vendor/*",
            "node_modules/*",
            "dist/*",
            "build/*",
            ".git/*",
            "venv/*",
            ".venv/*",
            "__pycache__/*",
            ".tox/*",
            ".mypy_cache/*",
            "htmlcov/*",
            ".coverage",
            "coverage/*",
            "*.egg-info/*",
            ".eggs/*",
            ".pytest_cache/*",
            ".ruff_cache/*",
            "*.min.js",
            "*.bundle.js",
            "*.generated.*",
            "experiments/*",
        ]
    )
    max_file_size_mb: float = 10.0
    max_files: int = 10000

    # Git integration
    git_max_commits: int = 5000
    git_min_commits: int = 10

    # Output control
    max_findings: int = 50
    verbosity: Verbosity = "normal"

    # Feature flags
    enable_validation: bool = True
    enable_history: bool = True

    # Provenance tracking
    enable_provenance: bool = False
    provenance_retention_hours: int = 24

    # Security
    allow_hidden_files: bool = False
    follow_symlinks: bool = False

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        # Validate PageRank parameters
        if not 0.0 <= self.pagerank_damping <= 1.0:
            raise ValueError("pagerank_damping must be between 0.0 and 1.0")
        if self.pagerank_iterations < 1:
            raise ValueError("pagerank_iterations must be at least 1")
        if self.pagerank_tolerance <= 0:
            raise ValueError("pagerank_tolerance must be positive")

        # Validate performance parameters
        if self.workers is not None and self.workers < 1:
            raise ValueError("workers must be at least 1")
        if self.timeout_seconds < 1:
            raise ValueError("timeout_seconds must be at least 1")

        # Validate cache parameters
        if self.cache_ttl_hours < 0:
            raise ValueError("cache_ttl_hours must be non-negative")

        # Validate file filtering
        if self.max_file_size_mb <= 0:
            raise ValueError("max_file_size_mb must be positive")
        if self.max_files < 1:
            raise ValueError("max_files must be at least 1")

        # Validate git parameters
        if self.git_max_commits < 0:
            raise ValueError("git_max_commits must be non-negative")
        if self.git_min_commits < 0:
            raise ValueError("git_min_commits must be non-negative")

        # Validate output
        if self.max_findings < 1:
            raise ValueError("max_findings must be at least 1")

        # Validate provenance
        if self.provenance_retention_hours < 0:
            raise ValueError("provenance_retention_hours must be non-negative")

    @property
    def max_file_size_bytes(self) -> int:
        """Get max file size in bytes."""
        return int(self.max_file_size_mb * 1024 * 1024)

    @property
    def cache_ttl_seconds(self) -> int:
        """Get cache TTL in seconds."""
        return self.cache_ttl_hours * 3600


def load_config(config_file: Optional[Path] = None, **overrides) -> AnalysisConfig:
    """Load configuration with auto-discovery and merging.

    Configuration sources are merged in priority order (lowest to highest):
        1. Defaults (AnalysisConfig field defaults)
        2. Global config (~/.shannon-insight.toml)
        3. Project config (./shannon-insight.toml)
        4. Explicit config file (if config_file provided)
        5. Environment variables (SHANNON_* prefix)
        6. CLI overrides (kwargs)

    Args:
        config_file: Optional explicit config file path
        **overrides: Direct overrides (typically from CLI flags)

    Returns:
        Validated AnalysisConfig instance

    Raises:
        ShannonInsightError: If config file is invalid or missing

    Example:
        >>> config = load_config(verbose=True)
        >>> config.verbosity
        'verbose'

        >>> config = load_config(config_file=Path("custom.toml"))
    """
    # Start with empty dict - dataclass defaults will fill in
    merged: dict = {}

    # 1. Try global config
    global_config = Path.home() / ".shannon-insight.toml"
    if global_config.exists():
        try:
            merged.update(_load_toml_file(global_config))
        except Exception as e:
            raise ShannonInsightError(f"Invalid global config '{global_config}': {e}")

    # 2. Try project config
    project_config = Path.cwd() / "shannon-insight.toml"
    if project_config.exists():
        try:
            merged.update(_load_toml_file(project_config))
        except Exception as e:
            raise ShannonInsightError(f"Invalid project config '{project_config}': {e}")

    # 3. Explicit config file (highest priority from files)
    if config_file is not None:
        if not config_file.exists():
            raise ShannonInsightError(f"Config file not found: {config_file}")
        try:
            merged.update(_load_toml_file(config_file))
        except Exception as e:
            raise ShannonInsightError(f"Invalid config file '{config_file}': {e}")

    # 4. Environment variables (SHANNON_* prefix)
    env_overrides = _load_env_vars()
    merged.update(env_overrides)

    # 5. CLI overrides (highest priority)
    # Convert verbosity boolean flags to string
    if "verbose" in overrides:
        if overrides["verbose"]:
            overrides["verbosity"] = "verbose"
        del overrides["verbose"]
    if "quiet" in overrides:
        if overrides["quiet"]:
            overrides["verbosity"] = "quiet"
        del overrides["quiet"]

    merged.update(overrides)

    # Create and validate config
    try:
        return AnalysisConfig(**merged)
    except TypeError as e:
        # Unknown field in config
        raise ShannonInsightError(f"Invalid configuration: {e}")


def _load_env_vars() -> dict[str, Any]:
    """Load configuration from SHANNON_* environment variables.

    Supported environment variables:
        SHANNON_MAX_FINDINGS: int
        SHANNON_WORKERS: int
        SHANNON_CACHE_ENABLED: bool (true/false/1/0)
        SHANNON_CACHE_TTL_HOURS: int
        SHANNON_MAX_FILE_SIZE_MB: float
        SHANNON_MAX_FILES: int
        SHANNON_GIT_MAX_COMMITS: int
        SHANNON_GIT_MIN_COMMITS: int
        SHANNON_VERBOSITY: quiet/normal/verbose
        SHANNON_ENABLE_VALIDATION: bool
        SHANNON_ENABLE_HISTORY: bool
        SHANNON_ALLOW_HIDDEN_FILES: bool
        SHANNON_FOLLOW_SYMLINKS: bool
        SHANNON_TIMEOUT_SECONDS: int
        SHANNON_PAGERANK_DAMPING: float

    Returns:
        Dict of field_name -> parsed_value for any SHANNON_* vars found.
    """
    # Map of field name -> expected type
    type_hints = get_type_hints(AnalysisConfig)

    result: dict[str, Any] = {}

    for field_name in AnalysisConfig.__dataclass_fields__:
        env_key = f"SHANNON_{field_name.upper()}"
        env_value = os.environ.get(env_key)

        if env_value is None:
            continue

        # Get type hint (handle Optional)
        type_hint = type_hints.get(field_name)
        if type_hint is None:
            continue

        # Parse value based on type
        try:
            parsed = _parse_env_value(env_value, type_hint, field_name)
            if parsed is not None:
                result[field_name] = parsed
        except ValueError as e:
            raise ShannonInsightError(f"Invalid {env_key}: {e}")

    return result


def _parse_env_value(value: str, type_hint: Any, field_name: str) -> Any:
    """Parse environment variable string to the correct type.

    Args:
        value: Raw string from environment
        type_hint: Type annotation from dataclass
        field_name: Field name for error messages

    Returns:
        Parsed value or None if can't parse

    Raises:
        ValueError: If value can't be parsed to expected type
    """
    # Handle Optional types (e.g., Optional[int])
    origin = getattr(type_hint, "__origin__", None)
    if origin is type(None):
        return None

    # Handle Optional[X] which is Union[X, None]
    args = getattr(type_hint, "__args__", ())
    if type(None) in args:
        # It's Optional[X], extract X
        non_none_types = [t for t in args if t is not type(None)]
        if non_none_types:
            type_hint = non_none_types[0]

    # Skip list types (like exclude_patterns) - too complex for env vars
    if origin is list or type_hint is list:
        return None

    # Bool: accept true/false/1/0/yes/no
    if type_hint is bool:
        lower = value.lower()
        if lower in ("true", "1", "yes", "on"):
            return True
        elif lower in ("false", "0", "no", "off"):
            return False
        else:
            raise ValueError(f"expected true/false, got '{value}'")

    # Int
    if type_hint is int:
        return int(value)

    # Float
    if type_hint is float:
        return float(value)

    # String (including Literal types like Verbosity)
    if type_hint is str or origin is Literal:
        return value

    return None


def _load_toml_file(path: Path) -> dict:
    """Load TOML file and return parsed dict.

    Args:
        path: Path to TOML file

    Returns:
        Parsed TOML as dict

    Raises:
        ImportError: If tomllib/tomli not available
        Exception: If TOML parsing fails
    """
    try:
        # Python 3.11+ has tomllib in stdlib
        import tomllib
    except ModuleNotFoundError:
        try:
            # Fallback to tomli for Python 3.9-3.10
            import tomli as tomllib  # type: ignore
        except ImportError:
            raise ShannonInsightError(
                "TOML support requires Python 3.11+ or 'tomli' package. "
                "Install with: pip install tomli"
            )

    with open(path, "rb") as f:
        return tomllib.load(f)
