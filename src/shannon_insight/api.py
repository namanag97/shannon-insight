"""Public API for Shannon Insight.

This module provides the main entry point for analysis. Users should call
analyze() instead of manually constructing sessions and kernels.

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
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from .config import load_config
from .environment import discover_environment
from .logging_config import get_logger, setup_logging
from .session import AnalysisSession

logger = get_logger(__name__)


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

    # 1. Load configuration
    config = load_config(config_file=config_file, **overrides)
    logger.debug(f"Configuration loaded: {config.verbosity} mode")

    # 2. Discover environment
    env = discover_environment(Path(path))
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

    kernel = InsightKernel(session=session)
    result, snapshot = kernel.run(max_findings=config.max_findings)

    logger.info(
        f"Analysis complete: {len(result.findings)} findings, "
        f"{snapshot.metadata.total_files} files analyzed"
    )

    return result, snapshot
