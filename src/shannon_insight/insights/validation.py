"""Phase validation contracts.

Run after each analyzer phase to catch data integrity issues before they propagate.
Inspired by Dagster's @asset_check pattern.

Validators are O(n) checks -- trivial compared to graph algorithms.
In production, can be disabled for speed (controlled by config flag).

Usage in kernel:
    from shannon_insight.insights.validation import (
        validate_after_scanning,
        validate_after_structural,
        validate_signal_field,
    )

    self._extract_syntax(store)  # Populates file_syntax
    validate_after_scanning(store)

    self._run_wave1_analyzers()
    validate_after_structural(store)

    self._run_wave2_analyzers()
    validate_signal_field(store)
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

from ..logging_config import get_logger

if TYPE_CHECKING:
    from shannon_insight.insights.store import AnalysisStore

logger = get_logger(__name__)

# Numeric fields on FileSignals that must never be NaN or Inf.
# These are the key computed signals that downstream composites and finders consume.
_NUMERIC_SIGNAL_FIELDS = (
    "lines",
    "function_count",
    "class_count",
    "max_nesting",
    "impl_gini",
    "stub_ratio",
    "import_count",
    "pagerank",
    "betweenness",
    "in_degree",
    "out_degree",
    "blast_radius_size",
    "depth",
    "compression_ratio",
    "semantic_coherence",
    "cognitive_load",
    "total_changes",
    "churn_slope",
    "churn_cv",
    "bus_factor",
    "author_entropy",
    "fix_ratio",
    "refactor_ratio",
    "raw_risk",
    "risk_score",
    "wiring_quality",
)


class PhaseValidationError(Exception):
    """Raised when phase contract is violated. Stops pipeline with clear message."""

    pass


def validate_after_scanning(store: AnalysisStore) -> None:
    """Validate store after scanner phase, before analyzers.

    Checks:
        - file_metrics has at least one file
        - No duplicate paths in file_metrics
        - file_syntax (if available) is subset of file_metrics paths

    Args:
        store: The analysis store after scanning

    Raises:
        PhaseValidationError: If validation fails
    """
    if not store.file_metrics:
        raise PhaseValidationError("Scanner produced 0 files")

    # Check for duplicate paths
    paths = [fm.path for fm in store.file_metrics]
    path_set = set(paths)
    if len(paths) != len(path_set):
        dupes = [p for p in path_set if paths.count(p) > 1]
        raise PhaseValidationError(
            f"Duplicate paths in file_metrics: {dupes[:5]}{'...' if len(dupes) > 5 else ''}"
        )

    if store.file_syntax.available:
        syntax_paths = set(store.file_syntax.value.keys())
        extra = syntax_paths - path_set
        if extra:
            raise PhaseValidationError(
                f"file_syntax has {len(extra)} paths not in file_metrics: "
                f"{list(extra)[:5]}{'...' if len(extra) > 5 else ''}"
            )
        # Missing is OK -- some files may fail to parse


def validate_after_structural(store: AnalysisStore) -> None:
    """Validate store after StructuralAnalyzer.

    Checks:
        - Graph nodes are subset of scanned files
        - Reverse adjacency is consistent with forward adjacency

    Args:
        store: The analysis store after structural analysis

    Raises:
        PhaseValidationError: If validation fails
    """
    if not store.structural.available:
        return  # Structural might have failed -- that's OK, finders will skip

    graph = store.structural.value.graph
    metric_paths = {fm.path for fm in store.file_metrics}

    # Every graph node must be a scanned file
    orphan_nodes = graph.all_nodes - metric_paths
    if orphan_nodes:
        raise PhaseValidationError(
            f"Graph has {len(orphan_nodes)} nodes not in scanned files: "
            f"{list(orphan_nodes)[:5]}{'...' if len(orphan_nodes) > 5 else ''}"
        )

    # Reverse adjacency must be consistent with forward
    for src, targets in graph.adjacency.items():
        for tgt in targets:
            if src not in graph.reverse.get(tgt, []):
                raise PhaseValidationError(
                    f"Adjacency has {src} -> {tgt} but reverse is inconsistent"
                )


def validate_signal_field(store: AnalysisStore) -> None:
    """Validate store after SignalFusion. The most critical validation.

    Checks:
        - SignalField covers exactly the same files as file_metrics
        - No NaN or Inf values in numeric signal fields
        - Tier is a valid value

    Args:
        store: The analysis store after signal fusion

    Raises:
        PhaseValidationError: If validation fails
    """
    if not store.signal_field.available:
        return

    field = store.signal_field.value
    metric_paths = {fm.path for fm in store.file_metrics}
    signal_paths = set(field.per_file.keys())

    missing = metric_paths - signal_paths
    if missing:
        raise PhaseValidationError(
            f"SignalField missing files: {len(missing)} files not covered. "
            f"Examples: {list(missing)[:5]}{'...' if len(missing) > 5 else ''}"
        )

    extra = signal_paths - metric_paths
    if extra:
        raise PhaseValidationError(
            f"SignalField has extra files: {len(extra)} files not in file_metrics. "
            f"Examples: {list(extra)[:5]}{'...' if len(extra) > 5 else ''}"
        )

    # Validate tier
    valid_tiers = {"ABSOLUTE", "BAYESIAN", "FULL"}
    if field.tier not in valid_tiers:
        raise PhaseValidationError(
            f"SignalField tier '{field.tier}' is not valid. Must be one of {valid_tiers}"
        )

    # Check for NaN/Inf in numeric signal fields
    for path, fs in field.per_file.items():
        for attr_name in _NUMERIC_SIGNAL_FIELDS:
            val = getattr(fs, attr_name, None)
            if val is None:
                continue
            if isinstance(val, (int, float)) and (math.isnan(val) or math.isinf(val)):
                raise PhaseValidationError(f"NaN/Inf detected: {path}.{attr_name} = {val}")

    # Check for NaN/Inf in percentile values
    for path, fs in field.per_file.items():
        for signal_name, pctl_val in fs.percentiles.items():
            if isinstance(pctl_val, float) and (math.isnan(pctl_val) or math.isinf(pctl_val)):
                raise PhaseValidationError(
                    f"NaN/Inf in percentile: {path}.percentiles[{signal_name}] = {pctl_val}"
                )


def run_all_validations(store: AnalysisStore) -> list[str]:
    """Run all validations and collect errors instead of raising.

    Useful for diagnostics mode -- collects all issues instead of stopping at the first.

    Args:
        store: The analysis store to validate

    Returns:
        List of validation error messages (empty if all passed)
    """
    errors: list[str] = []

    validators = [
        validate_after_scanning,
        validate_after_structural,
        validate_signal_field,
    ]

    for validator in validators:
        try:
            validator(store)
        except PhaseValidationError as e:
            errors.append(str(e))

    return errors
