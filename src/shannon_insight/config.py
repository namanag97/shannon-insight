"""
Configuration management for Shannon Insight.

Uses pydantic-settings for type-safe configuration with automatic validation.
"""

from pathlib import Path
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AnalysisSettings(BaseSettings):
    """
    Type-safe configuration with automatic validation.

    Configuration hierarchy (highest to lowest priority):
    1. CLI arguments (merged manually in CLI)
    2. Environment variables (SHANNON_*)
    3. TOML file (./shannon-insight.toml or ~/.shannon-insight.toml)
    4. Defaults defined in Field()
    """

    model_config = SettingsConfigDict(
        env_prefix="SHANNON_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ==================== Anomaly Detection ====================
    # Legacy — unused by InsightKernel, kept for config file compatibility

    z_score_threshold: float = Field(
        default=1.5,
        gt=0.0,
        lt=10.0,
        description="Z-score threshold for anomaly detection",
    )

    # ==================== PageRank ====================

    pagerank_damping: float = Field(
        default=0.85, ge=0.0, le=1.0, description="PageRank damping factor"
    )

    pagerank_iterations: int = Field(
        default=20, ge=1, le=100, description="Maximum PageRank iterations"
    )

    pagerank_tolerance: float = Field(
        default=1e-6, gt=0.0, description="PageRank convergence tolerance"
    )

    # ==================== Signal Fusion ====================
    # Legacy — unused by InsightKernel, kept for config file compatibility

    fusion_weights: list[float] = Field(
        default=[0.2, 0.25, 0.2, 0.15, 0.2],
        description="Signal fusion weights [entropy, centrality, churn, coherence, cognitive]",
    )

    fusion_normalize: bool = Field(default=True, description="Normalize weights to sum to 1.0")

    # ==================== File Filtering ====================

    exclude_patterns: list[str] = Field(
        default=[
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
        ],
        description="File patterns to exclude from analysis",
    )

    max_file_size_mb: float = Field(
        default=10.0, gt=0.0, le=100.0, description="Maximum file size in MB"
    )

    max_files: int = Field(
        default=10000, gt=0, le=100000, description="Maximum number of files to analyze"
    )

    # ==================== Performance ====================

    parallel_workers: Optional[int] = Field(
        default=None,
        ge=1,
        le=32,
        description="Number of parallel workers (None = auto-detect)",
    )

    timeout_seconds: int = Field(
        default=10, ge=1, le=300, description="Timeout for file operations in seconds"
    )

    # ==================== Cache ====================

    enable_cache: bool = Field(
        default=True, description="Enable caching for faster repeated analysis"
    )

    cache_dir: str = Field(default=".shannon-cache", description="Cache directory path")

    cache_ttl_hours: int = Field(
        default=24,
        ge=0,
        le=720,  # 30 days max
        description="Cache time-to-live in hours",
    )

    # ==================== Logging ====================

    verbose: bool = Field(default=False, description="Enable verbose (DEBUG) logging")

    quiet: bool = Field(default=False, description="Suppress all but ERROR logging")

    log_file: Optional[str] = Field(default=None, description="Log file path (optional)")

    # ==================== Insights ====================

    git_max_commits: int = Field(
        default=5000,
        ge=0,
        le=100000,
        description="Max git commits to analyze (0 = no limit)",
    )

    git_min_commits: int = Field(
        default=10,
        ge=0,
        description="Min commits required for temporal analysis",
    )

    insights_max_findings: int = Field(
        default=50,
        ge=1,
        le=500,
        description="Max findings to show in insights command",
    )

    enable_validation: bool = Field(
        default=True,
        description="Enable phase validation contracts between pipeline stages",
    )

    # ==================== History ====================

    enable_history: bool = Field(default=True, description="Auto-save snapshots to .shannon/")

    history_max_snapshots: int = Field(
        default=100,
        ge=1,
        le=10000,
        description="Maximum snapshots to retain (oldest pruned)",
    )

    # ==================== Security ====================

    allow_hidden_files: bool = Field(
        default=False, description="Allow analysis of hidden files (starting with .)"
    )

    block_system_dirs: bool = Field(default=True, description="Block access to system directories")

    follow_symlinks: bool = Field(
        default=False, description="Follow symbolic links during scanning"
    )

    # ==================== Validators ====================

    @field_validator("fusion_weights")
    @classmethod
    def validate_fusion_weights(cls, v: list[float]) -> list[float]:
        """Validate fusion weights."""
        if len(v) != 5:
            raise ValueError("fusion_weights must have exactly 5 values")

        if any(w < 0 for w in v):
            raise ValueError("fusion_weights must be non-negative")

        weight_sum = sum(v)
        if weight_sum == 0:
            raise ValueError("fusion_weights cannot all be zero")

        # Normalize to sum to 1.0
        return [w / weight_sum for w in v]

    @field_validator("cache_dir")
    @classmethod
    def validate_cache_dir(cls, v: str) -> str:
        """Validate cache directory."""
        # Convert to absolute path
        cache_path = Path(v)
        if not cache_path.is_absolute():
            try:
                cache_path = Path.cwd() / cache_path
            except (FileNotFoundError, OSError):
                # Fallback to home directory if cwd doesn't exist
                cache_path = Path.home() / v
        return str(cache_path)

    @field_validator("parallel_workers")
    @classmethod
    def validate_parallel_workers(cls, v: Optional[int]) -> Optional[int]:
        """Validate parallel workers count."""
        if v is not None and v < 1:
            raise ValueError("parallel_workers must be at least 1")
        return v

    # ==================== Computed Properties ====================

    @property
    def max_file_size_bytes(self) -> int:
        """Get max file size in bytes."""
        return int(self.max_file_size_mb * 1024 * 1024)

    @property
    def cache_ttl_seconds(self) -> int:
        """Get cache TTL in seconds."""
        return self.cache_ttl_hours * 3600


def load_settings(config_file: Optional[Path] = None, **overrides) -> AnalysisSettings:
    """
    Load settings from config file and environment variables.

    Args:
        config_file: Optional TOML config file path
        **overrides: Manual overrides (typically from CLI args)

    Returns:
        Loaded settings with all overrides applied
    """
    # Try to load from TOML file
    if config_file and config_file.exists():
        # pydantic-settings doesn't natively support TOML
        # We'll load it manually and pass as overrides
        try:
            import tomllib
        except ModuleNotFoundError:
            try:
                tomllib = __import__("tomli")
            except ImportError:
                tomllib = None

        if tomllib is not None:
            try:
                with open(config_file, "rb") as f:
                    toml_data = tomllib.load(f)
                # Merge TOML data with overrides (overrides take precedence)
                merged = {**toml_data, **overrides}
                return AnalysisSettings(**merged)
            except Exception as e:
                from .exceptions import ShannonInsightError

                raise ShannonInsightError(f"Invalid configuration file '{config_file}': {e}")

    # Load from environment variables + overrides
    return AnalysisSettings(**overrides)


# Default settings instance
default_settings = AnalysisSettings()
