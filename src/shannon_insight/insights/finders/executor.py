"""Pattern Executor — Runs patterns against FactStore to produce findings.

The executor handles:
- Pattern matching across different scopes (FILE, FILE_PAIR, MODULE, etc.)
- Hotspot filtering for temporal patterns
- Tier-aware pattern execution (ABSOLUTE/BAYESIAN/FULL)
- Finding construction with evidence and confidence

Canonical spec: docs/v2/architecture/01-pipeline/05-detect.md
"""

from __future__ import annotations

import itertools
from typing import TYPE_CHECKING

from shannon_insight.infrastructure.entities import EntityId, EntityType
from shannon_insight.infrastructure.patterns import Finding, Pattern, PatternScope
from shannon_insight.infrastructure.signals import Signal
from shannon_insight.session import Tier

from .helpers import compute_median
from .registry import ALL_PATTERNS

if TYPE_CHECKING:
    from shannon_insight.infrastructure.store import FactStore


def execute_patterns(
    store: FactStore,
    patterns: list[Pattern] | None = None,
    tier: Tier = Tier.FULL,
    max_findings: int = 100,
) -> list[Finding]:
    """Execute patterns against FactStore to produce findings.

    Args:
        store: FactStore with entities, signals, and relations
        patterns: List of patterns to run (default: ALL_PATTERNS)
        tier: Runtime tier (ABSOLUTE/BAYESIAN/FULL) for graceful degradation
        max_findings: Maximum findings to return

    Returns:
        List of Finding objects sorted by severity descending
    """
    if patterns is None:
        patterns = ALL_PATTERNS

    findings: list[Finding] = []

    # Compute hotspot median once for all patterns
    hotspot_median = _compute_hotspot_median(store)

    for pattern in patterns:
        # Check if pattern requirements are satisfied
        if not _check_requirements(store, pattern):
            continue

        # Tier-aware filtering (some patterns require percentiles)
        if not _pattern_available_in_tier(pattern, tier):
            continue

        # Execute pattern based on scope
        pattern_findings = _execute_pattern(store, pattern, hotspot_median)
        findings.extend(pattern_findings)

    # Sort by severity descending and cap
    findings.sort(key=lambda f: f.severity, reverse=True)
    return findings[:max_findings]


def _check_requirements(store: FactStore, pattern: Pattern) -> bool:
    """Check if all pattern requirements are available in the store.

    Args:
        store: FactStore to check
        pattern: Pattern with requirements

    Returns:
        True if all requirements satisfied, False otherwise
    """
    for req in pattern.requires:
        # Check if it's a signal
        try:
            Signal[req]  # Just check if signal exists
            # Check if at least one entity has this signal
            # For now, assume available if signal enum exists
            # Full implementation would check store.signals
        except KeyError:
            # Not a signal, might be a slot name like "architecture"
            # For now, assume available
            pass

    return True


def _pattern_available_in_tier(pattern: Pattern, tier: Tier) -> bool:
    """Check if pattern can fire in the given tier.

    Some patterns require percentiles, which are only available in
    BAYESIAN and FULL tiers (not ABSOLUTE).

    Args:
        pattern: Pattern to check
        tier: Current tier

    Returns:
        True if pattern available in this tier, False otherwise
    """
    # Patterns that require percentiles skip in ABSOLUTE tier
    # These patterns check "pctl(X) > threshold"
    requires_percentiles = "pctl(" in pattern.condition or "percentile" in pattern.condition

    if tier == Tier.ABSOLUTE and requires_percentiles:
        return False

    return True


def _compute_hotspot_median(store: FactStore) -> float:
    """Compute median of total_changes across non-test files.

    This is used for hotspot filtering - only flag files above the median.

    Args:
        store: FactStore

    Returns:
        Median total_changes value
    """
    return compute_median(store, Signal.TOTAL_CHANGES)


def _execute_pattern(
    store: FactStore,
    pattern: Pattern,
    hotspot_median: float,
) -> list[Finding]:
    """Execute a single pattern against the store.

    Args:
        store: FactStore
        pattern: Pattern to execute
        hotspot_median: Median total_changes for hotspot filter

    Returns:
        List of findings from this pattern
    """
    findings: list[Finding] = []

    if pattern.scope == PatternScope.FILE:
        findings = _execute_file_pattern(store, pattern, hotspot_median)
    elif pattern.scope == PatternScope.FILE_PAIR:
        findings = _execute_file_pair_pattern(store, pattern)
    elif pattern.scope == PatternScope.MODULE:
        findings = _execute_module_pattern(store, pattern)
    elif pattern.scope == PatternScope.MODULE_PAIR:
        findings = _execute_module_pair_pattern(store, pattern)
    elif pattern.scope == PatternScope.CODEBASE:
        findings = _execute_codebase_pattern(store, pattern)

    return findings


def _execute_file_pattern(
    store: FactStore,
    pattern: Pattern,
    hotspot_median: float,
) -> list[Finding]:
    """Execute FILE scope pattern."""
    findings: list[Finding] = []

    for file_id in store.files():
        # Hotspot filter: skip files below median total_changes
        if pattern.hotspot_filtered:
            total_changes = store.get_signal(file_id, Signal.TOTAL_CHANGES, 0)
            if total_changes <= hotspot_median:
                continue

        # Run predicate
        if not pattern.predicate(store, file_id):
            continue

        # Build finding
        severity = pattern.severity_fn(store, file_id)
        evidence = pattern.evidence_fn(store, file_id)

        finding = Finding(
            pattern=pattern.name,
            scope=pattern.scope,
            target=file_id,
            severity=severity,
            confidence=0.85,  # Default confidence
            evidence=evidence,
            description=pattern.description,
            remediation=pattern.remediation,
        )

        findings.append(finding)

    return findings


def _execute_file_pair_pattern(
    store: FactStore,
    pattern: Pattern,
) -> list[Finding]:
    """Execute FILE_PAIR scope pattern."""
    findings: list[Finding] = []

    files = store.files()

    # Generate all unique pairs
    for file_a, file_b in itertools.combinations(files, 2):
        pair = (file_a, file_b)

        # Run predicate
        if not pattern.predicate(store, pair):
            continue

        # Build finding
        severity = pattern.severity_fn(store, pair)
        evidence = pattern.evidence_fn(store, pair)

        finding = Finding(
            pattern=pattern.name,
            scope=pattern.scope,
            target=pair,
            severity=severity,
            confidence=0.85,
            evidence=evidence,
            description=pattern.description,
            remediation=pattern.remediation,
        )

        findings.append(finding)

    return findings


def _execute_module_pattern(
    store: FactStore,
    pattern: Pattern,
) -> list[Finding]:
    """Execute MODULE scope pattern."""
    findings: list[Finding] = []

    for module_id in store.modules():
        # Run predicate
        if not pattern.predicate(store, module_id):
            continue

        # Build finding
        severity = pattern.severity_fn(store, module_id)
        evidence = pattern.evidence_fn(store, module_id)

        finding = Finding(
            pattern=pattern.name,
            scope=pattern.scope,
            target=module_id,
            severity=severity,
            confidence=0.85,
            evidence=evidence,
            description=pattern.description,
            remediation=pattern.remediation,
        )

        findings.append(finding)

    return findings


def _execute_module_pair_pattern(
    store: FactStore,
    pattern: Pattern,
) -> list[Finding]:
    """Execute MODULE_PAIR scope pattern."""
    findings: list[Finding] = []

    modules = store.modules()

    # Generate all unique pairs
    for mod_a, mod_b in itertools.combinations(modules, 2):
        pair = (mod_a, mod_b)

        # Run predicate
        if not pattern.predicate(store, pair):
            continue

        # Build finding
        severity = pattern.severity_fn(store, pair)
        evidence = pattern.evidence_fn(store, pair)

        finding = Finding(
            pattern=pattern.name,
            scope=pattern.scope,
            target=pair,
            severity=severity,
            confidence=0.85,
            evidence=evidence,
            description=pattern.description,
            remediation=pattern.remediation,
        )

        findings.append(finding)

    return findings


def _execute_codebase_pattern(
    store: FactStore,
    pattern: Pattern,
) -> list[Finding]:
    """Execute CODEBASE scope pattern.

    CODEBASE patterns produce at most 1 finding per pattern.
    The target is a synthetic CODEBASE entity.
    """
    findings: list[Finding] = []

    # Create synthetic CODEBASE entity
    codebase_id = EntityId(EntityType.CODEBASE, store.root)

    # Run predicate
    if not pattern.predicate(store, codebase_id):
        return findings

    # Build finding
    severity = pattern.severity_fn(store, codebase_id)
    evidence = pattern.evidence_fn(store, codebase_id)

    finding = Finding(
        pattern=pattern.name,
        scope=pattern.scope,
        target=codebase_id,
        severity=severity,
        confidence=0.85,
        evidence=evidence,
        description=pattern.description,
        remediation=pattern.remediation,
    )

    findings.append(finding)

    return findings
