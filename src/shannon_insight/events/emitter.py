"""Emit events from existing TensorSnapshot or analysis store data.

The emitter bridges the old world (TensorSnapshot with nested dicts) to the
new world (flat event dataclasses suitable for Parquet tables). During the
strangler-fig migration, both paths coexist:

    Old: store -> capture -> TensorSnapshot -> SQLite writer
    New: store -> capture -> TensorSnapshot -> emitter -> events -> Parquet writer
"""

from __future__ import annotations

import json
import uuid
from typing import Any

from .schema import (
    EdgeEvent,
    FileSignalEvent,
    FindingEvent,
    GlobalSignalEvent,
    ModuleSignalEvent,
    SnapshotEvent,
)


def snapshot_to_events(
    snapshot: Any,
    snapshot_id: str | None = None,
) -> dict[str, Any]:
    """Convert a TensorSnapshot to a dict of event lists.

    Parameters
    ----------
    snapshot:
        A ``persistence.models.TensorSnapshot`` instance.
    snapshot_id:
        Optional snapshot ID.  If ``None``, a UUID4 is generated.

    Returns
    -------
    dict
        Keys: "snapshot", "file_signals", "module_signals", "global_signals",
              "edges", "findings".
        Values: single event or list of events.
    """
    sid = snapshot_id or uuid.uuid4().hex[:16]

    # ── Snapshot metadata ─────────────────────────────────────────
    snapshot_event = SnapshotEvent(
        snapshot_id=sid,
        timestamp=snapshot.timestamp,
        commit_sha=snapshot.commit_sha,
        analyzed_path=snapshot.analyzed_path,
        tool_version=snapshot.tool_version,
        schema_version=snapshot.schema_version,
        file_count=snapshot.file_count,
        module_count=snapshot.module_count,
        commits_analyzed=snapshot.commits_analyzed,
        analyzers_ran=list(snapshot.analyzers_ran),
        config_hash=snapshot.config_hash,
    )

    # ── File signals (wide rows) ──────────────────────────────────
    file_signal_events: list[FileSignalEvent] = []
    for file_path, signals in snapshot.file_signals.items():
        event = _dict_to_file_signal_event(sid, file_path, signals)
        # Add delta_h if available
        if file_path in snapshot.delta_h:
            event.delta_h = snapshot.delta_h[file_path]
        file_signal_events.append(event)

    # ── Module signals ────────────────────────────────────────────
    module_signal_events: list[ModuleSignalEvent] = []
    for module_path, signals in snapshot.module_signals.items():
        mod_event = _dict_to_module_signal_event(sid, module_path, signals)
        module_signal_events.append(mod_event)

    # ── Global signals ────────────────────────────────────────────
    global_signal_event = _dict_to_global_signal_event(sid, snapshot.global_signals)

    # ── Edges (G1 = dependency, G4 = cochange) ────────────────────
    edge_events: list[EdgeEvent] = []
    for src, dst in snapshot.dependency_edges:
        edge_events.append(EdgeEvent(snapshot_id=sid, source=src, target=dst, space="G1"))

    # G4 = cochange edges (from temporal analysis)
    for cochange_tuple in getattr(snapshot, "cochange_edges", []):
        file_a, file_b, weight, lift, conf_ab, conf_ba, count = cochange_tuple
        data = json.dumps(
            {
                "lift": lift,
                "confidence_a_b": conf_ab,
                "confidence_b_a": conf_ba,
                "cochange_count": count,
            }
        )
        edge_events.append(
            EdgeEvent(
                snapshot_id=sid,
                source=file_a,
                target=file_b,
                space="G4",
                weight=weight,
                data=data,
            )
        )

    # ── Findings ──────────────────────────────────────────────────
    finding_events: list[FindingEvent] = []
    for fr in snapshot.findings:
        finding_events.append(
            FindingEvent.from_finding_record(sid, fr),
        )

    return {
        "snapshot": snapshot_event,
        "file_signals": file_signal_events,
        "module_signals": module_signal_events,
        "global_signals": global_signal_event,
        "edges": edge_events,
        "findings": finding_events,
    }


# ---------------------------------------------------------------------------
# Private: dict-based construction (from TensorSnapshot's nested dicts)
# ---------------------------------------------------------------------------


def _dict_to_file_signal_event(
    snapshot_id: str,
    file_path: str,
    signals: dict[str, Any],
) -> FileSignalEvent:
    """Build a FileSignalEvent from a snapshot's file_signals dict.

    The dict may contain string or numeric values and a nested ``percentiles``
    dict (which we skip -- percentiles are computed on read).
    """

    def _get_float(key: str) -> float | None:
        v = signals.get(key)
        if v is None:
            return None
        try:
            return float(v)
        except (TypeError, ValueError):
            return None

    def _get_int(key: str) -> int | None:
        v = signals.get(key)
        if v is None:
            return None
        try:
            return int(v)
        except (TypeError, ValueError):
            return None

    def _get_str(key: str) -> str | None:
        v = signals.get(key)
        if v is None:
            return None
        return str(v)

    return FileSignalEvent(
        snapshot_id=snapshot_id,
        file_path=file_path,
        lines=_get_int("lines"),
        function_count=_get_int("function_count"),
        class_count=_get_int("class_count"),
        max_nesting=_get_int("max_nesting"),
        impl_gini=_get_float("impl_gini"),
        stub_ratio=_get_float("stub_ratio"),
        import_count=_get_int("import_count"),
        role=_get_str("role"),
        concept_count=_get_int("concept_count"),
        concept_entropy=_get_float("concept_entropy"),
        naming_drift=_get_float("naming_drift"),
        todo_density=_get_float("todo_density"),
        docstring_coverage=_get_float("docstring_coverage"),
        pagerank=_get_float("pagerank"),
        betweenness=_get_float("betweenness"),
        in_degree=_get_int("in_degree"),
        out_degree=_get_int("out_degree"),
        blast_radius_size=_get_int("blast_radius_size"),
        depth=_get_int("depth"),
        is_orphan=bool(signals.get("is_orphan")) if "is_orphan" in signals else None,
        phantom_import_count=_get_int("phantom_import_count"),
        broken_call_count=_get_int("broken_call_count"),
        community=_get_int("community"),
        compression_ratio=_get_float("compression_ratio"),
        semantic_coherence=_get_float("semantic_coherence"),
        cognitive_load=_get_float("cognitive_load"),
        total_changes=_get_int("total_changes"),
        churn_trajectory=_get_str("churn_trajectory"),
        churn_slope=_get_float("churn_slope"),
        churn_cv=_get_float("churn_cv"),
        bus_factor=_get_float("bus_factor"),
        author_entropy=_get_float("author_entropy"),
        fix_ratio=_get_float("fix_ratio"),
        refactor_ratio=_get_float("refactor_ratio"),
        change_entropy=_get_float("change_entropy"),
        raw_risk=_get_float("raw_risk"),
        risk_score=_get_float("risk_score"),
        wiring_quality=_get_float("wiring_quality"),
        file_health_score=_get_float("file_health_score"),
    )


def _dict_to_module_signal_event(
    snapshot_id: str,
    module_path: str,
    signals: dict[str, Any],
) -> ModuleSignalEvent:
    """Build a ModuleSignalEvent from a snapshot's module_signals dict."""

    def _get_float(key: str) -> float | None:
        v = signals.get(key)
        if v is None:
            return None
        try:
            return float(v)
        except (TypeError, ValueError):
            return None

    def _get_int(key: str) -> int | None:
        v = signals.get(key)
        if v is None:
            return None
        try:
            return int(v)
        except (TypeError, ValueError):
            return None

    return ModuleSignalEvent(
        snapshot_id=snapshot_id,
        module_path=module_path,
        cohesion=_get_float("cohesion"),
        coupling=_get_float("coupling"),
        instability=_get_float("instability"),
        abstractness=_get_float("abstractness"),
        main_seq_distance=_get_float("main_seq_distance"),
        boundary_alignment=_get_float("boundary_alignment"),
        layer_violation_count=_get_int("layer_violation_count"),
        role_consistency=_get_float("role_consistency"),
        velocity=_get_float("velocity"),
        coordination_cost=_get_float("coordination_cost"),
        knowledge_gini=_get_float("knowledge_gini"),
        module_bus_factor=_get_float("module_bus_factor"),
        mean_cognitive_load=_get_float("mean_cognitive_load"),
        file_count=_get_int("file_count"),
        health_score=_get_float("health_score"),
    )


def _dict_to_global_signal_event(
    snapshot_id: str,
    signals: dict[str, Any],
) -> GlobalSignalEvent:
    """Build a GlobalSignalEvent from a snapshot's global_signals dict."""

    def _get_float(key: str) -> float | None:
        v = signals.get(key)
        if v is None:
            return None
        try:
            return float(v)
        except (TypeError, ValueError):
            return None

    def _get_int(key: str) -> int | None:
        v = signals.get(key)
        if v is None:
            return None
        try:
            return int(v)
        except (TypeError, ValueError):
            return None

    return GlobalSignalEvent(
        snapshot_id=snapshot_id,
        modularity=_get_float("modularity"),
        fiedler_value=_get_float("fiedler_value"),
        spectral_gap=_get_float("spectral_gap"),
        cycle_count=_get_int("cycle_count"),
        centrality_gini=_get_float("centrality_gini"),
        orphan_ratio=_get_float("orphan_ratio"),
        phantom_ratio=_get_float("phantom_ratio"),
        glue_deficit=_get_float("glue_deficit"),
        clone_ratio=_get_float("clone_ratio"),
        violation_rate=_get_float("violation_rate"),
        conway_alignment=_get_float("conway_alignment"),
        team_size=_get_int("team_size"),
        wiring_score=_get_float("wiring_score"),
        architecture_health=_get_float("architecture_health"),
        team_risk=_get_float("team_risk"),
        codebase_health=_get_float("codebase_health"),
    )
