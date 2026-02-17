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
class ThresholdConfig:
    """Algorithm thresholds and tuning parameters.

    All thresholds have mathematically-principled defaults:
    - Percentiles use IQR-based outlier detection (~93rd percentile = Q3 + 0.5×IQR)
    - NCD threshold from literature (0.3 is standard for clone detection)
    - Composite weights normalized to sum=1.0

    Users can tune these based on false positive/negative tradeoffs:
    - Lower thresholds → more findings (higher recall, lower precision)
    - Higher thresholds → fewer findings (higher precision, lower recall)

    Attributes:
        Clone Detection:
            clone_ncd_threshold: NCD below this = clone (0.0=identical, 1.0=different)
            clone_min_lines: Minimum lines to consider for clone detection
            clone_lsh_file_threshold: File count to switch to LSH pre-filtering

        Hub Detection (HIGH_RISK_HUB):
            hub_pagerank_pctl: PageRank percentile threshold
            hub_blast_radius_pctl: Blast radius percentile threshold
            hub_cognitive_load_pctl: Cognitive load percentile threshold

        God File Detection:
            god_file_cognitive_pctl: Cognitive load percentile
            god_file_coherence_pctl: Semantic coherence percentile (LOW is bad)
            god_file_min_functions: Minimum functions to avoid trivial files

        Churn/Temporal:
            churn_slope_threshold: Slope magnitude for STABILIZING/SPIKING
            churn_cv_threshold: CV threshold for erratic vs steady
            churn_window_weeks: Time window for churn analysis

        Hidden Coupling:
            coupling_lift_threshold: Lift threshold for co-change
            coupling_confidence_threshold: Confidence threshold

        Zone of Pain (Martin Metrics):
            zone_abstractness_threshold: Abstractness threshold
            zone_instability_threshold: Instability threshold

        Tier Boundaries:
            tier_absolute_limit: Files below this use ABSOLUTE tier
            tier_bayesian_limit: Files below this use BAYESIAN tier

        Severity/Risk Weights (must sum to 1.0):
            risk_pagerank_weight: PageRank weight in risk_score
            risk_blast_radius_weight: Blast radius weight
            risk_cognitive_load_weight: Cognitive load weight
            risk_instability_weight: Instability factor weight
            risk_bus_factor_weight: Bus factor weight
    """

    # === Clone Detection ===
    # NCD literature: 0.25-0.35 typical, 0.3 is standard
    clone_ncd_threshold: float = 0.30
    clone_min_lines: int = 20  # Skip trivial files (was 10 bytes)
    clone_lsh_file_threshold: int = 1000

    # === Hub Detection (HIGH_RISK_HUB) ===
    # IQR-based: Q3 + 0.5×IQR ≈ 87th percentile, using 0.90 for safety
    hub_pagerank_pctl: float = 0.90
    hub_blast_radius_pctl: float = 0.90
    hub_cognitive_load_pctl: float = 0.85  # Slightly lower for compound condition

    # === God File Detection ===
    god_file_cognitive_pctl: float = 0.90
    god_file_coherence_pctl: float = 0.20  # LOW coherence is bad
    god_file_min_functions: int = 3

    # === Churn/Temporal ===
    # CV: coefficient of variation. >1.0 means std > mean (very erratic)
    churn_slope_threshold: float = 0.10
    churn_cv_threshold: float = 0.50
    churn_window_weeks: int = 4

    # === Hidden Coupling ===
    # Lift: how much more likely to change together than by chance
    coupling_lift_threshold: float = 2.0
    coupling_confidence_threshold: float = 0.5

    # === Zone of Pain (Martin Metrics) ===
    zone_abstractness_threshold: float = 0.30
    zone_instability_threshold: float = 0.30

    # === Truck Factor ===
    truck_factor_threshold: float = 1.0  # Single author
    truck_factor_min_lines: int = 50
    truck_factor_pagerank_pctl: float = 0.70

    # === Weak Link ===
    weak_link_pagerank_pctl: float = 0.80
    weak_link_risk_threshold: float = 0.70

    # === Bug Attractor ===
    bug_attractor_fix_ratio: float = 0.50  # >50% changes are fixes

    # === Thrashing Code ===
    thrashing_cv_threshold: float = 1.50
    thrashing_min_changes: int = 3
    thrashing_min_lines: int = 30

    # === Hollow Code ===
    hollow_stub_ratio: float = 0.50
    hollow_impl_gini: float = 0.60

    # === Tier Boundaries ===
    # ABSOLUTE: no percentiles, raw values only
    # BAYESIAN: Beta posterior percentiles
    # FULL: standard percentiles
    tier_absolute_limit: int = 15
    tier_bayesian_limit: int = 50

    # === Risk Score Composite Weights (sum = 1.0) ===
    risk_pagerank_weight: float = 0.25
    risk_blast_radius_weight: float = 0.20
    risk_cognitive_load_weight: float = 0.20
    risk_instability_weight: float = 0.20
    risk_bus_factor_weight: float = 0.15

    # === Louvain Algorithm ===
    louvain_max_passes: int = 20
    louvain_max_coarsen: int = 10

    def __post_init__(self) -> None:
        """Validate threshold configuration."""
        # NCD must be in [0, 1]
        if not 0.0 <= self.clone_ncd_threshold <= 1.0:
            raise ValueError("clone_ncd_threshold must be between 0.0 and 1.0")

        # Percentiles must be in [0, 1]
        pctl_fields = [
            "hub_pagerank_pctl",
            "hub_blast_radius_pctl",
            "hub_cognitive_load_pctl",
            "god_file_cognitive_pctl",
            "god_file_coherence_pctl",
            "truck_factor_pagerank_pctl",
            "weak_link_pagerank_pctl",
        ]
        for field_name in pctl_fields:
            value = getattr(self, field_name)
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{field_name} must be between 0.0 and 1.0")

        # Risk weights must sum to 1.0 (within tolerance)
        weight_sum = (
            self.risk_pagerank_weight
            + self.risk_blast_radius_weight
            + self.risk_cognitive_load_weight
            + self.risk_instability_weight
            + self.risk_bus_factor_weight
        )
        if not 0.99 <= weight_sum <= 1.01:
            raise ValueError(
                f"Risk weights must sum to 1.0, got {weight_sum:.3f}"
            )

        # Positive integers
        if self.clone_min_lines < 1:
            raise ValueError("clone_min_lines must be at least 1")
        if self.tier_absolute_limit < 1:
            raise ValueError("tier_absolute_limit must be at least 1")


# Default threshold configuration (singleton)
DEFAULT_THRESHOLDS = ThresholdConfig()


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

    # Algorithm thresholds (nested config)
    thresholds: ThresholdConfig = field(default_factory=ThresholdConfig)

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

    # Handle [thresholds] section from TOML
    thresholds_dict = merged.pop("thresholds", None)
    if thresholds_dict is not None:
        if isinstance(thresholds_dict, dict):
            try:
                merged["thresholds"] = ThresholdConfig(**thresholds_dict)
            except TypeError as e:
                raise ShannonInsightError(f"Invalid [thresholds] config: {e}")
        elif isinstance(thresholds_dict, ThresholdConfig):
            merged["thresholds"] = thresholds_dict
        # else: ignore invalid type

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
