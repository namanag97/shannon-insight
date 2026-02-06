"""Protocol classes for v2 Analyzer and Finder plugins.

Enhanced protocols with enterprise metadata for orchestration and graceful degradation.

Analyzer Protocol:
    - name: Unique identifier
    - api_version: "2.0" for v2 compatibility
    - requires: Slots that must be in store.available
    - provides: Slots this analyzer adds to store.available
    - run_last: If True, runs in Wave 2 (after all Wave 1 analyzers)
    - error_mode: "fail" | "skip" | "degrade"
    - deprecated/deprecation_note: For migration

Finder Protocol:
    - name: Unique identifier
    - api_version: "2.0" for v2 compatibility
    - requires: Signals/slots that must be available
    - error_mode: "fail" | "skip" | "degrade"
    - hotspot_filtered: If True, must also check total_changes > median
    - tier_minimum: "ABSOLUTE" | "BAYESIAN" | "FULL"
    - deprecated/deprecation_note: For migration
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from shannon_insight.insights.models import Finding
    from shannon_insight.insights.store_v2 import AnalysisStore


class Analyzer(Protocol):
    """Analyzer protocol with enterprise metadata for orchestration.

    Analyzers read from the store, compute, and write results back.
    They populate slots declared in `provides` and require slots in `requires`.

    Attributes:
        name: Unique identifier for this analyzer
        api_version: Semantic version for compatibility checks ("2.0" for v2)
        requires: Slots that must be in store.available before running
        provides: Slots this analyzer adds to store.available
        run_last: If True, runs in Wave 2 (after all Wave 1 analyzers)
        error_mode: How to handle errors
            - "fail": raise exception, halt pipeline
            - "skip": log warning, continue without this analyzer
            - "degrade": partial results OK, continue
        deprecated: Whether this analyzer is deprecated
        deprecation_note: Migration instructions if deprecated
    """

    name: str
    api_version: str
    requires: set[str]
    provides: set[str]
    run_last: bool
    error_mode: str
    deprecated: bool
    deprecation_note: str | None

    def analyze(self, store: AnalysisStore) -> None:
        """Mutate store by populating slots declared in `provides`.

        Args:
            store: The analysis store to read from and write to

        Raises:
            Exception if error_mode is "fail" and an error occurs
        """
        ...


class Finder(Protocol):
    """Finder protocol with enterprise metadata for graceful degradation.

    Finders read from the store (NEVER write) and return findings.
    They only run if all required signals/slots are available.

    Attributes:
        name: Unique identifier for this finder
        api_version: Semantic version for compatibility checks ("2.0" for v2)
        requires: Signals/slots that must be available before running
        error_mode: How to handle errors
            - "skip": if requirements missing, silently return []
            - "degrade": partial evaluation with reduced confidence
            - "fail": raise if requirements missing
        hotspot_filtered: If True, must also check total_changes > median
        tier_minimum: Minimum tier for this finder
            - "ABSOLUTE": Can run on any tier
            - "BAYESIAN": Requires 15+ files for percentiles
            - "FULL": Requires 50+ files for full analysis
        deprecated: Whether this finder is deprecated
        deprecation_note: Migration instructions if deprecated
    """

    name: str
    api_version: str
    requires: set[str]
    error_mode: str
    hotspot_filtered: bool
    tier_minimum: str
    deprecated: bool
    deprecation_note: str | None

    def find(self, store: AnalysisStore) -> list[Finding]:
        """Return findings based on store contents. Never mutate store.

        Args:
            store: The analysis store to read from

        Returns:
            List of Finding objects (may be empty if no issues found)

        Note:
            If error_mode is "skip" and requirements are missing,
            return [] instead of raising an exception.
        """
        ...
