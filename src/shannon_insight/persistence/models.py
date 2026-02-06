"""Data models for analysis snapshots — immutable records of a single analysis run."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class EvidenceRecord:
    """Serialisable evidence attached to a finding."""

    signal: str
    value: float
    percentile: float
    description: str


@dataclass
class FindingRecord:
    """Serialisable finding with a stable identity key."""

    finding_type: str
    identity_key: str  # SHA-256[:16] hex, stable across runs
    severity: float
    title: str
    files: list[str]
    evidence: list[EvidenceRecord]
    suggestion: str


@dataclass
class Snapshot:
    """Complete, immutable record of one analysis run.

    Every field is a plain value or collection of plain values so the
    snapshot can be serialised to JSON or persisted to SQLite without
    any ORM machinery.
    """

    # ── Metadata ──────────────────────────────────────────────────
    schema_version: int = 1
    tool_version: str = ""
    commit_sha: Optional[str] = None
    timestamp: str = ""  # ISO-8601
    analyzed_path: str = ""
    file_count: int = 0
    module_count: int = 0
    commits_analyzed: int = 0
    analyzers_ran: list[str] = field(default_factory=list)
    config_hash: str = ""

    # ── Per-file signals ──────────────────────────────────────────
    file_signals: dict[str, dict[str, float]] = field(default_factory=dict)

    # ── Codebase-level signals ────────────────────────────────────
    codebase_signals: dict[str, float] = field(default_factory=dict)

    # ── Findings ──────────────────────────────────────────────────
    findings: list[FindingRecord] = field(default_factory=list)

    # ── Dependency edges ──────────────────────────────────────────
    dependency_edges: list[tuple[str, str]] = field(default_factory=list)
