"""Runtime context and tier system for Shannon Insight v2.

The RuntimeContext captures everything the tool needs to know about its
environment: root path, git state, detected languages, codebase tier,
and configuration overrides.

The Tier enum drives adaptive behavior -- percentile computation,
composite signals, and finder availability all depend on codebase size.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Tier(Enum):
    """Codebase size tier. Determines normalization and finder behavior.

    ABSOLUTE  (<15 files):  Raw signals only, no percentiles/composites.
    BAYESIAN  (15-50 files): Bayesian posterior percentiles.
    FULL      (50+ files):  Standard percentile normalization.
    """

    ABSOLUTE = "absolute"
    BAYESIAN = "bayesian"
    FULL = "full"


def determine_tier(file_count: int) -> Tier:
    """Map file count to the appropriate analysis tier."""
    if file_count < 15:
        return Tier.ABSOLUTE
    elif file_count < 50:
        return Tier.BAYESIAN
    else:
        return Tier.FULL


@dataclass
class RuntimeContext:
    """Everything the tool needs to know about its environment."""

    root: str
    is_git_repo: bool = False
    languages: list[str] = field(default_factory=list)
    tier: Tier = Tier.FULL
    config: dict = field(default_factory=dict)
