"""Public API for Shannon Insight.

This module provides the main entry point for analysis. Users should call
analyze() instead of manually constructing sessions and kernels.

Two kernel implementations are available:
- RuntimeKernel (new): Full observability, circuit breakers, partial results
- InsightKernel (legacy): Original implementation, deprecated

Example:
    >>> from shannon_insight import analyze
    >>>
    >>> # Simple usage
    >>> result, snapshot = analyze("/path/to/code")
    >>>
    >>> # With customization
    >>> result, snapshot = analyze(
    ...     "/path/to/code",
    ...     verbose=True,
    ...     max_findings=100
    ... )
    >>>
    >>> # Use new RuntimeKernel (full observability)
    >>> result = analyze_v2("/path/to/code")
    >>> print(result.metrics.summary())
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Optional

from .config import load_config
from .environment import discover_environment
from .logging_config import get_logger, setup_logging
from .session import AnalysisSession

if TYPE_CHECKING:
    from .kernel import RuntimeResult

logger = get_logger(__name__)


def _has_historical_data(path: Path, min_snapshots: int = 3) -> bool:
    """Check if historical data is available for persistence finders.

    Returns True if .shannon/history.db exists and has at least min_snapshots.
    This auto-enables chronic_problem and architecture_erosion finders.
    """
    db_path = path / ".shannon" / "history.db"
    if not db_path.exists():
        return False

    try:
        import sqlite3

        with sqlite3.connect(str(db_path)) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM snapshots")
            count: int = cursor.fetchone()[0]
            return count >= min_snapshots
    except Exception:
        return False


def analyze(
    path: str = ".",
    config_file: Optional[Path] = None,
    **overrides,
):
    """Analyze a codebase and return findings.

    This is the main entry point for Shannon Insight. It orchestrates
    the full analysis pipeline:
    1. Load configuration (auto-discover TOML + apply overrides)
    2. Discover environment (git, languages, file count)
    3. Create analysis session (derive tier, workers, etc.)
    4. Run analysis kernel (scan, analyze, find issues)
    5. Return results and snapshot

    Args:
        path: Path to codebase root (default: current directory)
        config_file: Optional explicit config file path
        **overrides: Configuration overrides (e.g., verbose=True, max_findings=100)

    Returns:
        Tuple of (InsightResult, TensorSnapshot):
        - InsightResult: Findings, store summary, diagnostics
        - TensorSnapshot: Serializable snapshot for persistence

    Raises:
        ShannonInsightError: If configuration is invalid
        FileNotFoundError: If path doesn't exist
        Exception: If analysis fails

    Example:
        >>> # Basic usage
        >>> result, snapshot = analyze()
        >>> len(result.findings)
        12

        >>> # Custom path and verbosity
        >>> result, snapshot = analyze(
        ...     "/path/to/code",
        ...     verbose=True
        ... )

        >>> # Custom config file
        >>> result, snapshot = analyze(
        ...     config_file=Path("custom.toml"),
        ...     max_findings=50
        ... )
    """
    # Setup logging based on verbosity
    verbosity = "verbose" if overrides.get("verbose") else "normal"
    if overrides.get("quiet"):
        verbosity = "quiet"
    setup_logging(verbose=(verbosity == "verbose"), quiet=(verbosity == "quiet"))

    logger.info(f"Starting analysis of {path}")

    # Extract non-config overrides before passing to load_config
    enable_provenance = overrides.pop("enable_provenance", False)
    use_fact_store = overrides.pop("use_fact_store", False)

    # 1. Load configuration
    config = load_config(config_file=config_file, **overrides)
    logger.debug(f"Configuration loaded: {config.verbosity} mode")

    # Use config.enable_provenance if not explicitly overridden via API
    if not enable_provenance:
        enable_provenance = config.enable_provenance

    # Clean up stale provenance sessions at the start of every run
    if enable_provenance:
        from .infrastructure.provenance import cleanup_stale_sessions

        cleanup_stale_sessions(retention_hours=config.provenance_retention_hours)

    # 2. Discover environment
    env = discover_environment(
        Path(path),
        allow_hidden_files=config.allow_hidden_files,
        follow_symlinks=config.follow_symlinks,
    )
    logger.info(
        f"Environment discovered: {env.file_count} files, "
        f"{len(env.detected_languages)} languages, "
        f"git={'yes' if env.is_git_repo else 'no'}"
    )

    # 3. Create analysis session
    session = AnalysisSession(config=config, env=env)
    logger.info(f"Session created: tier={session.tier.value}, workers={session.effective_workers}")

    # 4. Run analysis kernel
    from .insights.kernel import InsightKernel

    # Auto-detect historical data: enable persistence finders if history.db has snapshots
    enable_persistence_finders = _has_historical_data(Path(path))
    if enable_persistence_finders:
        logger.debug("Historical data detected, enabling persistence finders")

    kernel = InsightKernel(
        session=session,
        enable_provenance=enable_provenance,
        enable_persistence_finders=enable_persistence_finders,
        use_fact_store=use_fact_store,
    )
    result, snapshot = kernel.run(max_findings=config.max_findings)

    logger.info(
        f"Analysis complete: {len(result.findings)} findings, {snapshot.file_count} files analyzed"
    )

    return result, snapshot


def analyze_v2(
    path: str = ".",
    config_file: Optional[Path] = None,
    use_runtime_kernel: bool = True,
    **overrides,
) -> RuntimeResult:
    """Analyze a codebase using RuntimeKernel with full observability.

    This is the new API that uses RuntimeKernel instead of InsightKernel.
    It provides full observability with metrics, error collection, and
    partial result support.

    Args:
        path: Path to codebase root (default: current directory)
        config_file: Optional explicit config file path
        use_runtime_kernel: Always True (for API consistency)
        **overrides: Configuration overrides

    Returns:
        RuntimeResult with:
        - findings: List of code issues
        - snapshot: TensorSnapshot for persistence
        - metrics: RuntimeMetrics with timing/memory data
        - errors: List of exceptions (not swallowed)
        - warnings: List of warning messages
        - success/partial/cancelled: Status flags

    Example:
        >>> result = analyze_v2("/path/to/code")
        >>> if result.success:
        ...     print(f"Found {len(result.findings)} issues")
        >>> print(result.metrics.summary())
    """
    from .kernel import RuntimeKernel

    # Setup logging based on verbosity
    verbosity = "verbose" if overrides.get("verbose") else "normal"
    if overrides.get("quiet"):
        verbosity = "quiet"
    setup_logging(verbose=(verbosity == "verbose"), quiet=(verbosity == "quiet"))

    logger.info(f"Starting analysis of {path} (RuntimeKernel)")

    # Extract non-config overrides
    enable_provenance = overrides.pop("enable_provenance", False)
    use_fact_store = overrides.pop("use_fact_store", False)
    memory_limit_mb = overrides.pop("memory_limit_mb", 2048)
    total_timeout_seconds = overrides.pop("total_timeout_seconds", 1800)
    on_progress = overrides.pop("on_progress", None)

    # Load configuration
    config = load_config(config_file=config_file, **overrides)

    # Use config.enable_provenance if not explicitly overridden
    if not enable_provenance:
        enable_provenance = config.enable_provenance

    # Clean up stale provenance sessions
    if enable_provenance:
        from .infrastructure.provenance import cleanup_stale_sessions

        cleanup_stale_sessions(retention_hours=config.provenance_retention_hours)

    # Discover environment
    env = discover_environment(
        Path(path),
        allow_hidden_files=config.allow_hidden_files,
        follow_symlinks=config.follow_symlinks,
    )
    logger.info(
        f"Environment discovered: {env.file_count} files, {len(env.detected_languages)} languages"
    )

    # Create session
    session = AnalysisSession(config=config, env=env)

    # Run RuntimeKernel
    kernel = RuntimeKernel(
        session=session,
        memory_limit_mb=memory_limit_mb,
        total_timeout_seconds=total_timeout_seconds,
        enable_provenance=enable_provenance,
        use_fact_store=use_fact_store,
    )

    result = kernel.run(
        max_findings=config.max_findings,
        on_progress=on_progress,
    )

    logger.info(f"Analysis complete: {len(result.findings)} findings, status={result.status}")

    return result
