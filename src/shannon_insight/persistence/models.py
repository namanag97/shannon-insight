"""Data models for analysis snapshots — immutable records of a single analysis run.

V2 adds TensorSnapshot with full SignalField serialization, module signals,
architecture data, and finding lifecycle tracking.
"""

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class EvidenceRecord:
    """Serialisable evidence attached to a finding."""

    signal: str
    value: float
    percentile: float
    description: str


@dataclass
class FindingRecord:
    """Serialisable finding with a stable identity key.

    V2 adds confidence, effort, scope fields for finding lifecycle tracking.
    """

    finding_type: str
    identity_key: str  # SHA-256[:16] hex, stable across runs
    severity: float
    title: str
    files: list[str]
    evidence: list[EvidenceRecord]
    suggestion: str
    confidence: float = 1.0  # 0.0-1.0, margin-based
    effort: str = "MEDIUM"  # LOW | MEDIUM | HIGH
    scope: str = "FILE"  # FILE | FILE_PAIR | MODULE | MODULE_PAIR | CODEBASE


@dataclass
class Snapshot:
    """V1 snapshot: original schema with file_signals and codebase_signals.

    Kept for backward compatibility. New code should use TensorSnapshot.
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


@dataclass
class TensorSnapshot:
    """V2 snapshot: stores full SignalField plus architecture and temporal summary.

    Extends V1 with:
    - module_signals: per-module signals (Martin metrics, etc.)
    - modules, layers, violations: architecture data
    - Enhanced FindingRecord with confidence/effort/scope

    All fields are plain values or collections of plain values for JSON/SQLite
    serialization without ORM machinery.
    """

    # ── Metadata (same as v1) ─────────────────────────────────────
    schema_version: int = 2
    tool_version: str = ""
    commit_sha: Optional[str] = None
    timestamp: str = ""  # ISO-8601
    analyzed_path: str = ""
    file_count: int = 0
    module_count: int = 0
    commits_analyzed: int = 0
    analyzers_ran: list[str] = field(default_factory=list)
    config_hash: str = ""

    # ── Per-file signals (replaces v1 file_signals) ───────────────
    # Dict[file_path, Dict[signal_name, value]]
    # Serialized from SignalField.per_file (FileSignals)
    file_signals: dict[str, dict[str, Any]] = field(default_factory=dict)

    # ── Per-module signals (NEW) ──────────────────────────────────
    # Dict[module_path, Dict[signal_name, value]]
    # Serialized from SignalField.per_module (ModuleSignals)
    module_signals: dict[str, dict[str, Any]] = field(default_factory=dict)

    # ── Global signals (replaces v1 codebase_signals) ─────────────
    # Dict[signal_name, value]
    # Serialized from SignalField.global_signals (GlobalSignals)
    global_signals: dict[str, Any] = field(default_factory=dict)

    # ── Findings (enhanced with confidence/effort/scope) ──────────
    findings: list[FindingRecord] = field(default_factory=list)

    # ── Graph structure (same as v1) ──────────────────────────────
    dependency_edges: list[tuple[str, str]] = field(default_factory=list)

    # ── Architecture summary (NEW) ────────────────────────────────
    modules: list[str] = field(default_factory=list)  # module paths
    layers: list[dict[str, Any]] = field(default_factory=list)  # [{depth, modules}]
    violations: list[dict[str, Any]] = field(default_factory=list)  # [{src, tgt, type}]

    # ── Cochange edges (G4 space) ─────────────────────────────────
    # List of (file_a, file_b, weight, lift, confidence_ab, confidence_ba, cochange_count)
    cochange_edges: list[tuple] = field(default_factory=list)

    # ── Health Laplacian delta_h (NEW) ────────────────────────────
    delta_h: dict[str, float] = field(default_factory=dict)  # file -> delta_h value

    # ── Community detection (graph visualization) ──────────────────
    communities: list[dict[str, Any]] = field(default_factory=list)  # [{id, members, size}]
    node_community: dict[str, int] = field(default_factory=dict)  # file -> community_id
    modularity_score: float = 0.0


def snapshot_to_tensor(v1: Snapshot) -> TensorSnapshot:
    """Convert a V1 Snapshot to TensorSnapshot.

    Maps v1 fields to v2 equivalents:
    - file_signals -> file_signals (unchanged)
    - codebase_signals -> global_signals
    - New fields get empty defaults

    Parameters
    ----------
    v1:
        The V1 Snapshot to convert.

    Returns
    -------
    TensorSnapshot
        Equivalent V2 snapshot with missing fields defaulted.
    """
    return TensorSnapshot(
        schema_version=2,
        tool_version=v1.tool_version,
        commit_sha=v1.commit_sha,
        timestamp=v1.timestamp,
        analyzed_path=v1.analyzed_path,
        file_count=v1.file_count,
        module_count=v1.module_count,
        commits_analyzed=v1.commits_analyzed,
        analyzers_ran=list(v1.analyzers_ran),
        config_hash=v1.config_hash,
        file_signals={k: dict(v) for k, v in v1.file_signals.items()},
        module_signals={},  # V1 didn't have module signals
        global_signals=dict(v1.codebase_signals),
        findings=list(v1.findings),
        dependency_edges=list(v1.dependency_edges),
        cochange_edges=[],  # V1 didn't have cochange edges
        modules=[],  # V1 didn't have architecture
        layers=[],
        violations=[],
        delta_h={},
        communities=[],
        node_community={},
        modularity_score=0.0,
    )
