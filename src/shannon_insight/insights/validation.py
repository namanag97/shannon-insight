"""Phase validation contracts.

Run after each analyzer phase to catch data integrity issues before they propagate.
Inspired by Dagster's @asset_check pattern.

Validators are O(n) checks — trivial compared to graph algorithms.
In production, can be disabled for speed (controlled by config flag).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from shannon_insight.insights.store_v2 import AnalysisStore


class PhaseValidationError(Exception):
    """Raised when phase contract is violated. Stops pipeline with clear message."""

    pass


def validate_after_scanning(store: AnalysisStore) -> None:
    """Validate store after scanner phase, before analyzers.

    Checks:
        - file_metrics has at least one file
        - file_syntax (if available) is subset of file_metrics paths

    Args:
        store: The analysis store after scanning

    Raises:
        PhaseValidationError: If validation fails
    """
    if not store.file_metrics:
        raise PhaseValidationError("Scanner produced 0 files")

    paths = {fm.path for fm in store.file_metrics}

    if store.file_syntax.available:
        syntax_paths = set(store.file_syntax.value.keys())
        extra = syntax_paths - paths
        if extra:
            raise PhaseValidationError(
                f"file_syntax has {len(extra)} paths not in file_metrics: "
                f"{list(extra)[:5]}{'...' if len(extra) > 5 else ''}"
            )
        # Missing is OK — some files may fail to parse


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
        return  # Structural might have failed — that's OK, finders will skip

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
                raise PhaseValidationError(f"Adjacency has {src}→{tgt} but reverse is inconsistent")


def validate_signal_field(store: AnalysisStore) -> None:
    """Validate store after SignalFusion. The most critical validation.

    Checks:
        - SignalField covers exactly the same files as file_metrics

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
