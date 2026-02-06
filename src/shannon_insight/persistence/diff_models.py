"""Data models for snapshot diffing — deltas at metric, finding, file, and snapshot level."""

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
class FindingDelta:
    """Change in status or severity of a finding between two snapshots."""

    status: str  # "new" | "resolved" | "worsened" | "improved" | "unchanged"
    finding: FindingRecord
    old_severity: Optional[float]
    new_severity: Optional[float]
    severity_delta: Optional[float]


@dataclass
class FileDelta:
    """Aggregated metric changes for a single file."""

    filepath: str
    status: str  # "new" | "removed" | "changed" | "unchanged"
    metric_deltas: dict[str, MetricDelta] = field(default_factory=dict)


@dataclass
class SnapshotDiff:
    """Complete diff between two analysis snapshots.

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
