"""Read snapshots back from the history database."""

import json
import sqlite3
from typing import Any, Optional

from .models import EvidenceRecord, FindingRecord, Snapshot, TensorSnapshot


def load_snapshot(conn: sqlite3.Connection, snapshot_id: int) -> Snapshot:
    """Load a complete snapshot by its primary key.

    Parameters
    ----------
    conn:
        An open ``sqlite3.Connection`` (from ``HistoryDB.connect()``).
    snapshot_id:
        The snapshot's ``id`` column.

    Returns
    -------
    Snapshot
        Fully hydrated snapshot.

    Raises
    ------
    ValueError
        If no snapshot with that ID exists.
    """
    row = conn.execute("SELECT * FROM snapshots WHERE id = ?", (snapshot_id,)).fetchone()

    if row is None:
        raise ValueError(f"No snapshot with id={snapshot_id}")

    return _hydrate(conn, row)


def load_snapshot_by_commit(conn: sqlite3.Connection, commit_sha: str) -> Optional[Snapshot]:
    """Load the most recent snapshot for a given commit SHA.

    Parameters
    ----------
    conn:
        An open ``sqlite3.Connection``.
    commit_sha:
        The full or partial commit SHA.

    Returns
    -------
    Optional[Snapshot]
        The snapshot, or ``None`` if no match.
    """
    row = conn.execute(
        "SELECT * FROM snapshots WHERE commit_sha = ? ORDER BY id DESC LIMIT 1",
        (commit_sha,),
    ).fetchone()

    if row is None:
        return None

    return _hydrate(conn, row)


def list_snapshots(conn: sqlite3.Connection, limit: int = 20) -> list[dict]:
    """List recent snapshots with finding counts.

    Parameters
    ----------
    conn:
        An open ``sqlite3.Connection``.
    limit:
        Maximum number of rows to return.

    Returns
    -------
    List[Dict]
        List of dicts with keys: id, commit_sha, timestamp, file_count,
        module_count, finding_count, tool_version, analyzers_ran.
    """
    rows = conn.execute(
        """
        SELECT
            s.id,
            s.commit_sha,
            s.timestamp,
            s.file_count,
            s.module_count,
            s.tool_version,
            s.analyzers_ran,
            COUNT(f.id) AS finding_count
        FROM snapshots s
        LEFT JOIN findings f ON f.snapshot_id = s.id
        GROUP BY s.id
        ORDER BY s.id DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()

    results: list[dict] = []
    for r in rows:
        results.append(
            {
                "id": r["id"],
                "commit_sha": r["commit_sha"],
                "timestamp": r["timestamp"],
                "file_count": r["file_count"],
                "module_count": r["module_count"],
                "finding_count": r["finding_count"],
                "tool_version": r["tool_version"],
                "analyzers_ran": json.loads(r["analyzers_ran"]),
            }
        )
    return results


def load_tensor_snapshot(conn: sqlite3.Connection, snapshot_id: int) -> TensorSnapshot:
    """Load a complete V2 TensorSnapshot by its primary key.

    Reads from all V2 tables (signal_history, module_signal_history,
    global_signal_history) to reconstruct the full SignalField data.

    Parameters
    ----------
    conn:
        An open ``sqlite3.Connection`` (from ``HistoryDB.connect()``).
    snapshot_id:
        The snapshot's ``id`` column.

    Returns
    -------
    TensorSnapshot
        Fully hydrated V2 snapshot.

    Raises
    ------
    ValueError
        If no snapshot with that ID exists.
    """
    row = conn.execute("SELECT * FROM snapshots WHERE id = ?", (snapshot_id,)).fetchone()

    if row is None:
        raise ValueError(f"No snapshot with id={snapshot_id}")

    return _hydrate_tensor(conn, row)


def load_tensor_snapshot_by_commit(
    conn: sqlite3.Connection, commit_sha: str
) -> Optional[TensorSnapshot]:
    """Load the most recent TensorSnapshot for a given commit SHA.

    Parameters
    ----------
    conn:
        An open ``sqlite3.Connection``.
    commit_sha:
        The full or partial commit SHA.

    Returns
    -------
    Optional[TensorSnapshot]
        The snapshot, or ``None`` if no match.
    """
    row = conn.execute(
        "SELECT * FROM snapshots WHERE commit_sha = ? ORDER BY id DESC LIMIT 1",
        (commit_sha,),
    ).fetchone()

    if row is None:
        return None

    return _hydrate_tensor(conn, row)


# ── Private helpers ──────────────────────────────────────────────────


def _hydrate_tensor(conn: sqlite3.Connection, row: sqlite3.Row) -> TensorSnapshot:
    """Build a full TensorSnapshot from a snapshots row + V2 tables."""
    snapshot_id = row["id"]

    # Per-file signals from signal_history (includes percentiles)
    file_signals: dict[str, dict[str, Any]] = {}
    for fs_row in conn.execute(
        "SELECT file_path, signal_name, value, percentile FROM signal_history WHERE snapshot_id = ?",
        (snapshot_id,),
    ):
        fp = fs_row["file_path"]
        if fp not in file_signals:
            file_signals[fp] = {"percentiles": {}}
        file_signals[fp][fs_row["signal_name"]] = fs_row["value"]
        if fs_row["percentile"] is not None:
            file_signals[fp]["percentiles"][fs_row["signal_name"]] = fs_row["percentile"]

    # Clean up empty percentiles dicts
    for fp in file_signals:
        if not file_signals[fp].get("percentiles"):
            file_signals[fp].pop("percentiles", None)

    # Module signals from module_signal_history
    module_signals: dict[str, dict[str, Any]] = {}
    for ms_row in conn.execute(
        "SELECT module_path, signal_name, value FROM module_signal_history WHERE snapshot_id = ?",
        (snapshot_id,),
    ):
        mp = ms_row["module_path"]
        if mp not in module_signals:
            module_signals[mp] = {}
        module_signals[mp][ms_row["signal_name"]] = ms_row["value"]

    # Global signals from global_signal_history
    global_signals: dict[str, Any] = {}
    for gs_row in conn.execute(
        "SELECT signal_name, value FROM global_signal_history WHERE snapshot_id = ?",
        (snapshot_id,),
    ):
        global_signals[gs_row["signal_name"]] = gs_row["value"]

    # Findings with V2 fields
    findings: list[FindingRecord] = []
    for f_row in conn.execute("SELECT * FROM findings WHERE snapshot_id = ?", (snapshot_id,)):
        evidence_raw = json.loads(f_row["evidence"])
        evidence = [
            EvidenceRecord(
                signal=e["signal"],
                value=e["value"],
                percentile=e["percentile"],
                description=e["description"],
            )
            for e in evidence_raw
        ]
        # V2 fields with defaults for v1 data
        findings.append(
            FindingRecord(
                finding_type=f_row["finding_type"],
                identity_key=f_row["identity_key"],
                severity=f_row["severity"],
                title=f_row["title"],
                files=json.loads(f_row["files"]),
                evidence=evidence,
                suggestion=f_row["suggestion"],
                confidence=1.0,  # v1 data defaults
                effort="MEDIUM",
                scope="FILE",
            )
        )

    # Dependency edges
    dependency_edges = [
        (e_row["src"], e_row["dst"])
        for e_row in conn.execute(
            "SELECT src, dst FROM dependency_edges WHERE snapshot_id = ?",
            (snapshot_id,),
        )
    ]

    # Cochange edges
    cochange_edges = []
    for ce_row in conn.execute(
        """SELECT file_a, file_b, weight, lift, confidence_a_b, confidence_b_a, cochange_count
           FROM cochange_edges WHERE snapshot_id = ?""",
        (snapshot_id,),
    ):
        cochange_edges.append(
            (
                ce_row["file_a"],
                ce_row["file_b"],
                ce_row["weight"],
                ce_row["lift"],
                ce_row["confidence_a_b"],
                ce_row["confidence_b_a"],
                ce_row["cochange_count"],
            )
        )

    # Architecture modules
    modules = [
        r["module_path"]
        for r in conn.execute(
            "SELECT module_path FROM architecture_modules WHERE snapshot_id = ?",
            (snapshot_id,),
        )
    ]

    # Architecture layers
    layers = []
    for layer_row in conn.execute(
        "SELECT depth, modules FROM architecture_layers WHERE snapshot_id = ? ORDER BY depth",
        (snapshot_id,),
    ):
        layers.append({"depth": layer_row["depth"], "modules": json.loads(layer_row["modules"])})

    # Architecture violations
    violations = []
    for v_row in conn.execute(
        "SELECT source_module, target_module, violation_type FROM architecture_violations WHERE snapshot_id = ?",
        (snapshot_id,),
    ):
        violations.append(
            {"src": v_row["source_module"], "tgt": v_row["target_module"], "type": v_row["violation_type"]}
        )

    # Delta h (health Laplacian)
    delta_h = {}
    for dh_row in conn.execute(
        "SELECT file_path, value FROM delta_h WHERE snapshot_id = ?",
        (snapshot_id,),
    ):
        delta_h[dh_row["file_path"]] = dh_row["value"]

    # Communities
    communities = []
    for c_row in conn.execute(
        "SELECT community_id, members FROM communities WHERE snapshot_id = ?",
        (snapshot_id,),
    ):
        communities.append(
            {"id": c_row["community_id"], "members": json.loads(c_row["members"]), "size": len(json.loads(c_row["members"]))}
        )

    # Node community mapping
    node_community = {}
    for nc_row in conn.execute(
        "SELECT file_path, community_id FROM node_community WHERE snapshot_id = ?",
        (snapshot_id,),
    ):
        node_community[nc_row["file_path"]] = nc_row["community_id"]

    # Modularity score
    modularity_score = 0.0
    ms_row = conn.execute(
        "SELECT score FROM modularity_score WHERE snapshot_id = ?",
        (snapshot_id,),
    ).fetchone()
    if ms_row:
        modularity_score = ms_row["score"]

    return TensorSnapshot(
        schema_version=row["schema_version"],
        tool_version=row["tool_version"],
        commit_sha=row["commit_sha"],
        timestamp=row["timestamp"],
        analyzed_path=row["analyzed_path"],
        file_count=row["file_count"],
        module_count=row["module_count"],
        commits_analyzed=row["commits_analyzed"],
        analyzers_ran=json.loads(row["analyzers_ran"]),
        config_hash=row["config_hash"],
        file_signals=file_signals,
        module_signals=module_signals,
        global_signals=global_signals,
        findings=findings,
        dependency_edges=dependency_edges,
        cochange_edges=cochange_edges,
        modules=modules,
        layers=layers,
        violations=violations,
        delta_h=delta_h,
        communities=communities,
        node_community=node_community,
        modularity_score=modularity_score,
    )


def _hydrate(conn: sqlite3.Connection, row: sqlite3.Row) -> Snapshot:
    """Build a full Snapshot from a snapshots row + child tables."""
    snapshot_id = row["id"]

    # File signals
    file_signals: dict[str, dict[str, float]] = {}
    for fs_row in conn.execute(
        "SELECT file_path, signal_name, value FROM file_signals WHERE snapshot_id = ?",
        (snapshot_id,),
    ):
        fp = fs_row["file_path"]
        if fp not in file_signals:
            file_signals[fp] = {}
        file_signals[fp][fs_row["signal_name"]] = fs_row["value"]

    # Codebase signals
    codebase_signals: dict[str, float] = {}
    for cs_row in conn.execute(
        "SELECT signal_name, value FROM codebase_signals WHERE snapshot_id = ?",
        (snapshot_id,),
    ):
        codebase_signals[cs_row["signal_name"]] = cs_row["value"]

    # Findings
    findings: list[FindingRecord] = []
    for f_row in conn.execute("SELECT * FROM findings WHERE snapshot_id = ?", (snapshot_id,)):
        evidence_raw = json.loads(f_row["evidence"])
        evidence = [
            EvidenceRecord(
                signal=e["signal"],
                value=e["value"],
                percentile=e["percentile"],
                description=e["description"],
            )
            for e in evidence_raw
        ]
        findings.append(
            FindingRecord(
                finding_type=f_row["finding_type"],
                identity_key=f_row["identity_key"],
                severity=f_row["severity"],
                title=f_row["title"],
                files=json.loads(f_row["files"]),
                evidence=evidence,
                suggestion=f_row["suggestion"],
            )
        )

    # Dependency edges
    dependency_edges = [
        (e_row["src"], e_row["dst"])
        for e_row in conn.execute(
            "SELECT src, dst FROM dependency_edges WHERE snapshot_id = ?",
            (snapshot_id,),
        )
    ]

    return Snapshot(
        schema_version=row["schema_version"],
        tool_version=row["tool_version"],
        commit_sha=row["commit_sha"],
        timestamp=row["timestamp"],
        analyzed_path=row["analyzed_path"],
        file_count=row["file_count"],
        module_count=row["module_count"],
        commits_analyzed=row["commits_analyzed"],
        analyzers_ran=json.loads(row["analyzers_ran"]),
        config_hash=row["config_hash"],
        file_signals=file_signals,
        codebase_signals=codebase_signals,
        findings=findings,
        dependency_edges=dependency_edges,
    )
