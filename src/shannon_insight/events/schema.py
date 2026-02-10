"""Event dataclasses for the tensor DB migration.

Events are the canonical intermediate representation between extraction
(scanners, analyzers, finders) and storage (Parquet snapshots). Each event
type maps 1:1 to a Parquet table.

Design decisions:
- JSON blob for ``data`` fields (flexibility without schema churn)
- File signals are a 36-column wide row (one row per file per snapshot)
- Edges use a unified table with ``space`` column (G1, G4, G5, G6)
- Percentiles are computed on read (DuckDB window functions), not stored
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any

# ---------------------------------------------------------------------------
# Snapshot metadata
# ---------------------------------------------------------------------------


@dataclass
class SnapshotEvent:
    """One row per analysis run.  The ``snapshot_id`` is the primary key that
    ties all other tables together.

    Mirrors persistence.models.TensorSnapshot metadata fields.
    """

    snapshot_id: str  # UUID or monotonic integer, set by writer
    timestamp: str = ""  # ISO-8601 UTC
    commit_sha: str | None = None
    analyzed_path: str = ""
    tool_version: str = ""
    schema_version: int = 2
    file_count: int = 0
    module_count: int = 0
    commits_analyzed: int = 0
    analyzers_ran: list[str] = field(default_factory=list)
    config_hash: str = ""

    @staticmethod
    def now_iso() -> str:
        """Return the current UTC time in ISO-8601."""
        return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# Per-file signals (wide table: 1 row per file)
# ---------------------------------------------------------------------------


@dataclass
class FileSignalEvent:
    """One row per file per snapshot.

    Columns correspond to the 36 per-file signals from the signal registry,
    plus composites and raw_risk.  All float/int; missing values are None.
    Percentiles are NOT stored -- they are computed on read via DuckDB
    window functions.
    """

    snapshot_id: str
    file_path: str

    # IR1 (scanning) - signals #1-7
    lines: int | None = None
    function_count: int | None = None
    class_count: int | None = None
    max_nesting: int | None = None
    impl_gini: float | None = None
    stub_ratio: float | None = None
    import_count: int | None = None

    # IR2 (semantics) - signals #8-13
    role: str | None = None
    concept_count: int | None = None
    concept_entropy: float | None = None
    naming_drift: float | None = None
    todo_density: float | None = None
    docstring_coverage: float | None = None

    # IR3 (graph) - signals #14-26
    pagerank: float | None = None
    betweenness: float | None = None
    in_degree: int | None = None
    out_degree: int | None = None
    blast_radius_size: int | None = None
    depth: int | None = None
    is_orphan: bool | None = None
    phantom_import_count: int | None = None
    broken_call_count: int | None = None
    community: int | None = None
    compression_ratio: float | None = None
    semantic_coherence: float | None = None
    cognitive_load: float | None = None

    # IR5t (temporal) - signals #27-34
    total_changes: int | None = None
    churn_trajectory: str | None = None
    churn_slope: float | None = None
    churn_cv: float | None = None
    bus_factor: float | None = None
    author_entropy: float | None = None
    fix_ratio: float | None = None
    refactor_ratio: float | None = None

    # Pre-percentile risk
    raw_risk: float | None = None

    # Composites (post-percentile)
    risk_score: float | None = None
    wiring_quality: float | None = None
    file_health_score: float | None = None

    # Health Laplacian delta
    delta_h: float | None = None

    def to_dict(self) -> dict[str, Any]:
        """Flatten to a dict suitable for a Parquet row."""
        return asdict(self)

    @classmethod
    def from_file_signals(
        cls,
        snapshot_id: str,
        path: str,
        fs: Any,
        delta_h: float | None = None,
    ) -> FileSignalEvent:
        """Construct from a signals.models.FileSignals instance."""
        return cls(
            snapshot_id=snapshot_id,
            file_path=path,
            lines=fs.lines if fs.lines else None,
            function_count=fs.function_count if fs.function_count else None,
            class_count=fs.class_count if fs.class_count else None,
            max_nesting=fs.max_nesting if fs.max_nesting else None,
            impl_gini=fs.impl_gini if fs.impl_gini else None,
            stub_ratio=fs.stub_ratio if fs.stub_ratio else None,
            import_count=fs.import_count if fs.import_count else None,
            role=fs.role if fs.role != "UNKNOWN" else None,
            concept_count=fs.concept_count if fs.concept_count > 1 else None,
            concept_entropy=fs.concept_entropy if fs.concept_entropy else None,
            naming_drift=fs.naming_drift if fs.naming_drift else None,
            todo_density=fs.todo_density if fs.todo_density else None,
            docstring_coverage=fs.docstring_coverage,
            pagerank=fs.pagerank if fs.pagerank else None,
            betweenness=fs.betweenness if fs.betweenness else None,
            in_degree=fs.in_degree if fs.in_degree else None,
            out_degree=fs.out_degree if fs.out_degree else None,
            blast_radius_size=fs.blast_radius_size if fs.blast_radius_size else None,
            depth=fs.depth if fs.depth >= 0 else None,
            is_orphan=fs.is_orphan if fs.is_orphan else None,
            phantom_import_count=(fs.phantom_import_count if fs.phantom_import_count else None),
            broken_call_count=fs.broken_call_count if fs.broken_call_count else None,
            community=fs.community if fs.community >= 0 else None,
            compression_ratio=fs.compression_ratio if fs.compression_ratio else None,
            semantic_coherence=fs.semantic_coherence if fs.semantic_coherence else None,
            cognitive_load=fs.cognitive_load if fs.cognitive_load else None,
            total_changes=fs.total_changes if fs.total_changes else None,
            churn_trajectory=(fs.churn_trajectory if fs.churn_trajectory != "DORMANT" else None),
            churn_slope=fs.churn_slope if fs.churn_slope else None,
            churn_cv=fs.churn_cv if fs.churn_cv else None,
            bus_factor=fs.bus_factor if fs.bus_factor > 1.0 else None,
            author_entropy=fs.author_entropy if fs.author_entropy else None,
            fix_ratio=fs.fix_ratio if fs.fix_ratio else None,
            refactor_ratio=fs.refactor_ratio if fs.refactor_ratio else None,
            raw_risk=fs.raw_risk if fs.raw_risk else None,
            risk_score=fs.risk_score if fs.risk_score else None,
            wiring_quality=fs.wiring_quality if fs.wiring_quality != 1.0 else None,
            file_health_score=(fs.file_health_score if fs.file_health_score != 1.0 else None),
            delta_h=delta_h,
        )


# ---------------------------------------------------------------------------
# Per-module signals
# ---------------------------------------------------------------------------


@dataclass
class ModuleSignalEvent:
    """One row per module per snapshot."""

    snapshot_id: str
    module_path: str

    # Martin metrics - signals #37-41
    cohesion: float | None = None
    coupling: float | None = None
    instability: float | None = None
    abstractness: float | None = None
    main_seq_distance: float | None = None

    # Boundary analysis - signals #42-44
    boundary_alignment: float | None = None
    layer_violation_count: int | None = None
    role_consistency: float | None = None

    # Module temporal - signals #45-48
    velocity: float | None = None
    coordination_cost: float | None = None
    knowledge_gini: float | None = None
    module_bus_factor: float | None = None

    # Aggregated - signals #49-50
    mean_cognitive_load: float | None = None
    file_count: int | None = None

    # Composite - signal #51
    health_score: float | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_module_signals(
        cls,
        snapshot_id: str,
        path: str,
        ms: Any,
    ) -> ModuleSignalEvent:
        """Construct from a signals.models.ModuleSignals instance."""
        return cls(
            snapshot_id=snapshot_id,
            module_path=path,
            cohesion=ms.cohesion if ms.cohesion else None,
            coupling=ms.coupling if ms.coupling else None,
            instability=ms.instability,  # None is valid (isolated module)
            abstractness=ms.abstractness if ms.abstractness else None,
            main_seq_distance=ms.main_seq_distance if ms.main_seq_distance else None,
            boundary_alignment=(ms.boundary_alignment if ms.boundary_alignment else None),
            layer_violation_count=(ms.layer_violation_count if ms.layer_violation_count else None),
            role_consistency=ms.role_consistency if ms.role_consistency else None,
            velocity=ms.velocity if ms.velocity else None,
            coordination_cost=ms.coordination_cost if ms.coordination_cost else None,
            knowledge_gini=ms.knowledge_gini if ms.knowledge_gini else None,
            module_bus_factor=(ms.module_bus_factor if ms.module_bus_factor > 1.0 else None),
            mean_cognitive_load=(ms.mean_cognitive_load if ms.mean_cognitive_load else None),
            file_count=ms.file_count if ms.file_count else None,
            health_score=ms.health_score if ms.health_score else None,
        )


# ---------------------------------------------------------------------------
# Global signals
# ---------------------------------------------------------------------------


@dataclass
class GlobalSignalEvent:
    """One row per snapshot -- codebase-level aggregates."""

    snapshot_id: str

    # Graph structure - signals #52-56
    modularity: float | None = None
    fiedler_value: float | None = None
    spectral_gap: float | None = None
    cycle_count: int | None = None
    centrality_gini: float | None = None

    # Wiring quality - signals #57-59
    orphan_ratio: float | None = None
    phantom_ratio: float | None = None
    glue_deficit: float | None = None

    # Phase 3/4 derived
    clone_ratio: float | None = None
    violation_rate: float | None = None
    conway_alignment: float | None = None
    team_size: int | None = None

    # Composites - signals #60-62
    wiring_score: float | None = None
    architecture_health: float | None = None
    team_risk: float | None = None
    codebase_health: float | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_global_signals(
        cls,
        snapshot_id: str,
        gs: Any,
    ) -> GlobalSignalEvent:
        """Construct from a signals.models.GlobalSignals instance."""
        return cls(
            snapshot_id=snapshot_id,
            modularity=gs.modularity if gs.modularity else None,
            fiedler_value=gs.fiedler_value if gs.fiedler_value else None,
            spectral_gap=gs.spectral_gap if gs.spectral_gap else None,
            cycle_count=gs.cycle_count if gs.cycle_count else None,
            centrality_gini=gs.centrality_gini if gs.centrality_gini else None,
            orphan_ratio=gs.orphan_ratio if gs.orphan_ratio else None,
            phantom_ratio=gs.phantom_ratio if gs.phantom_ratio else None,
            glue_deficit=gs.glue_deficit if gs.glue_deficit else None,
            clone_ratio=gs.clone_ratio if gs.clone_ratio else None,
            violation_rate=gs.violation_rate if gs.violation_rate else None,
            conway_alignment=(gs.conway_alignment if gs.conway_alignment != 1.0 else None),
            team_size=gs.team_size if gs.team_size > 1 else None,
            wiring_score=gs.wiring_score if gs.wiring_score else None,
            architecture_health=(gs.architecture_health if gs.architecture_health else None),
            team_risk=gs.team_risk if gs.team_risk else None,
            codebase_health=gs.codebase_health if gs.codebase_health else None,
        )


# ---------------------------------------------------------------------------
# Edges (unified table with space column)
# ---------------------------------------------------------------------------


@dataclass
class EdgeEvent:
    """Unified edge table row.  The ``space`` column distinguishes:
    - G1: import / dependency edges
    - G4: co-change (temporal coupling) edges
    - G5: author distance edges
    - G6: clone / NCD similarity edges
    """

    snapshot_id: str
    source: str
    target: str
    space: str  # "G1" | "G4" | "G5" | "G6"
    weight: float = 1.0  # edge weight (co-change freq, NCD distance, etc.)
    data: str | None = None  # JSON blob for extra metadata

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# ---------------------------------------------------------------------------
# Findings
# ---------------------------------------------------------------------------


@dataclass
class FindingEvent:
    """One row per finding per snapshot."""

    snapshot_id: str
    finding_type: str
    identity_key: str  # SHA-256[:16] hex, stable across runs
    severity: float
    title: str
    files: list[str] = field(default_factory=list)
    evidence: str = "[]"  # JSON-encoded list of evidence dicts
    suggestion: str = ""
    confidence: float = 1.0
    effort: str = "MEDIUM"  # LOW | MEDIUM | HIGH
    scope: str = "FILE"  # FILE | FILE_PAIR | MODULE | MODULE_PAIR | CODEBASE

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["files"] = json.dumps(self.files)
        return d

    @classmethod
    def from_finding_record(
        cls,
        snapshot_id: str,
        fr: Any,
    ) -> FindingEvent:
        """Construct from a persistence.models.FindingRecord."""
        evidence_json = json.dumps(
            [
                {
                    "signal": e.signal,
                    "value": e.value,
                    "percentile": e.percentile,
                    "description": e.description,
                }
                for e in fr.evidence
            ]
        )
        return cls(
            snapshot_id=snapshot_id,
            finding_type=fr.finding_type,
            identity_key=fr.identity_key,
            severity=fr.severity,
            title=fr.title,
            files=list(fr.files),
            evidence=evidence_json,
            suggestion=fr.suggestion,
            confidence=getattr(fr, "confidence", 1.0),
            effort=getattr(fr, "effort", "MEDIUM"),
            scope=getattr(fr, "scope", "FILE"),
        )
