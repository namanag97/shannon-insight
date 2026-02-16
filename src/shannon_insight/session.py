"""Analysis session management for Shannon Insight.

This module provides the AnalysisSession - the single source of truth for
an analysis run. It combines user configuration and discovered environment
into a unified execution context with derived strategy (tier, workers, etc).

Example:
    >>> from shannon_insight.config import load_config
    >>> from shannon_insight.environment import discover_environment
    >>> from shannon_insight.session import AnalysisSession
    >>>
    >>> config = load_config(verbose=True)
    >>> env = discover_environment("/path/to/code")
    >>> session = AnalysisSession(config, env)
    >>>
    >>> session.tier
    <Tier.FULL: 'full'>
    >>> session.effective_workers
    8
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from functools import cached_property
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .config import AnalysisConfig
    from .environment import Environment


class Tier(Enum):
    """Codebase size tier determining normalization strategy.

    The tier is computed from file count and affects how signals are
    normalized and which finders are available:

    - ABSOLUTE (<15 files): No percentile normalization, absolute thresholds only.
      Small codebases lack statistical significance for percentiles.

    - BAYESIAN (15-49 files): Bayesian percentile normalization with flat priors.
      Medium codebases have some statistical power but benefit from smoothing.

    - FULL (50+ files): Standard percentile normalization.
      Large codebases have sufficient data for robust percentiles.

    The tier directly impacts:
    1. Signal normalization (percentiles vs absolute)
    2. Composite signal availability (some require percentiles)
    3. Finder availability (some require percentiles or specific signals)
    """

    ABSOLUTE = "absolute"
    BAYESIAN = "bayesian"
    FULL = "full"


@dataclass(frozen=True)
class AnalysisSession:
    """Immutable analysis session capturing execution strategy.

    This is the single source of truth for an analysis run. It combines
    user configuration (intent) and discovered environment (facts) into
    derived execution strategy.

    All derived properties are cached on first access and remain stable
    for the session lifetime.

    Attributes:
        config: User configuration (preferences, parameters)
        env: Discovered environment (git, languages, file count)

    Derived Properties (cached):
        tier: Codebase size tier (ABSOLUTE/BAYESIAN/FULL)
        effective_workers: Actual worker count (config or auto-detected)

    Example:
        >>> session = AnalysisSession(config, env)
        >>> session.tier  # Computed from env.file_count
        <Tier.FULL: 'full'>
        >>> session.effective_workers  # Computed from config + env
        8
    """

    config: AnalysisConfig
    env: Environment

    @cached_property
    def tier(self) -> Tier:
        """Compute analysis tier from file count.

        The tier is determined solely by file count:
        - <15 files: ABSOLUTE (no percentiles)
        - 15-49 files: BAYESIAN (smoothed percentiles)
        - 50+ files: FULL (standard percentiles)

        Returns:
            Tier enum value
        """
        if self.env.file_count < 15:
            return Tier.ABSOLUTE
        elif self.env.file_count < 50:
            return Tier.BAYESIAN
        else:
            return Tier.FULL

    @cached_property
    def effective_workers(self) -> int:
        """Compute effective worker count for parallelism.

        Strategy:
        1. If config.workers is set: use that value
        2. If small codebase (<100 files): use 1 (no parallelism overhead)
        3. Otherwise: use system cores (capped at 8 to avoid overload)

        Returns:
            Number of workers (1 = sequential, >1 = parallel)
        """
        # Explicit config override
        if self.config.workers is not None:
            return self.config.workers

        # Small codebases: sequential is faster (avoid overhead)
        if self.env.file_count < 100:
            return 1

        # Large codebases: parallel, but cap at 8 to avoid context switching
        return min(self.env.system_cores, 8)

    @cached_property
    def requires_git(self) -> bool:
        """Check if temporal analysis is possible.

        Temporal finders (co-change, churn, etc.) require git history.
        This property gates temporal analysis features.

        Returns:
            True if git is available and has sufficient commits
        """
        return self.env.is_git_repo

    @cached_property
    def requires_percentiles(self) -> bool:
        """Check if percentile normalization is available.

        ABSOLUTE tier doesn't support percentiles (too few files).
        BAYESIAN and FULL tiers do.

        Returns:
            True if percentiles will be computed
        """
        return self.tier in (Tier.BAYESIAN, Tier.FULL)

    def __repr__(self) -> str:
        """Human-readable session summary."""
        return (
            f"AnalysisSession("
            f"tier={self.tier.value}, "
            f"files={self.env.file_count}, "
            f"workers={self.effective_workers}, "
            f"languages={sorted(self.env.detected_languages)}"
            f")"
        )
