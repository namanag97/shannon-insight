"""Data models for snapshot diffing — deltas at metric, finding, file, and snapshot level.

V2 adds:
- SignalDelta with trend detection (improving/stable/worsening)
- FindingDelta with lifecycle status (new/persisting/resolved/regression)
- TensorSnapshotDiff with debt_velocity and improving/worsening file lists
"""

from dataclasses import dataclass, field
from typing import Optional

from .models import FindingRecord


@dataclass
class MetricDelta:
    """Change in a single numeric metric between two snapshots."""

    old_value: float
    new_value: float
    delta: float  # new - old
    direction: str  # "better" | "worse" | "neutral"


@dataclass
class SignalDelta:
    """Change in a signal between two snapshots with trend detection.

    Trend is determined by signal polarity:
    - HIGH_IS_BAD (e.g., cognitive_load): decrease = improving
    - HIGH_IS_GOOD (e.g., cohesion): increase = improving
    """

    signal_name: str
    old_value: float
    new_value: float
    delta: float  # new - old
    trend: str  # "improving" | "stable" | "worsening"


@dataclass
class FindingDelta:
    """Change in status or severity of a finding between two snapshots.

    V2 adds lifecycle status:
    - new: first time seen
    - persisting: in both old and new snapshots
    - resolved: was in old, not in new
    - regression: was resolved, now back
    """

    status: str  # "new" | "resolved" | "worsened" | "improved" | "unchanged" | "persisting" | "regression"
    finding: FindingRecord
    old_severity: Optional[float]
    new_severity: Optional[float]
    severity_delta: Optional[float]
    persistence_count: int = 1  # How many snapshots this finding has persisted


@dataclass
class FileDelta:
    """Aggregated metric changes for a single file."""

    filepath: str
    status: str  # "new" | "removed" | "changed" | "unchanged"
    metric_deltas: dict[str, MetricDelta] = field(default_factory=dict)


@dataclass
class SnapshotDiff:
    """Complete diff between two V1 analysis snapshots.

    Organized into actionable categories so renderers can present
    the most important changes first.
    """

    old_commit: Optional[str]
    new_commit: Optional[str]
    old_timestamp: str
    new_timestamp: str

    # Finding-level deltas
    new_findings: list[FindingRecord] = field(default_factory=list)
    resolved_findings: list[FindingRecord] = field(default_factory=list)
    worsened_findings: list[FindingDelta] = field(default_factory=list)
    improved_findings: list[FindingDelta] = field(default_factory=list)

    # File-level deltas
    file_deltas: list[FileDelta] = field(default_factory=list)

    # Codebase-level signal deltas
    codebase_deltas: dict[str, MetricDelta] = field(default_factory=dict)

    # Detected file renames (old_path, new_path)
    renames: list[tuple[str, str]] = field(default_factory=list)


@dataclass
class TensorSnapshotDiff:
    """Structured diff between two V2 TensorSnapshots.

    Extends SnapshotDiff with:
    - Signal deltas per file/module/global with trend detection
    - Finding lifecycle (new/persisting/resolved/regression)
    - debt_velocity = |new| - |resolved|
    - Lists of improving/worsening files
    """

    old_commit: Optional[str]
    new_commit: Optional[str]
    old_timestamp: str
    new_timestamp: str

    # Files added/removed
    files_added: list[str] = field(default_factory=list)
    files_removed: list[str] = field(default_factory=list)

    # Signal deltas with trend detection
    signal_deltas: dict[str, list[SignalDelta]] = field(default_factory=dict)  # file -> signals
    module_deltas: dict[str, list[SignalDelta]] = field(default_factory=dict)  # module -> signals
    global_deltas: list[SignalDelta] = field(default_factory=list)

    # Finding lifecycle
    finding_deltas: list[FindingDelta] = field(default_factory=list)

    # Summary metrics
    debt_velocity: int = 0  # |new findings| - |resolved findings|
    improving_files: list[str] = field(default_factory=list)
    worsening_files: list[str] = field(default_factory=list)

    # V1-compatible fields
    new_findings: list[FindingRecord] = field(default_factory=list)
    resolved_findings: list[FindingRecord] = field(default_factory=list)
    file_deltas: list[FileDelta] = field(default_factory=list)
    codebase_deltas: dict[str, MetricDelta] = field(default_factory=dict)
    renames: list[tuple[str, str]] = field(default_factory=list)
