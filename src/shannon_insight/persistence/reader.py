"""Read snapshots back from the history database."""

import json
import sqlite3
from typing import Dict, List, Optional

from .models import EvidenceRecord, FindingRecord, Snapshot


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


def list_snapshots(conn: sqlite3.Connection, limit: int = 20) -> List[Dict]:
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

    results: List[Dict] = []
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


# ── Private helpers ──────────────────────────────────────────────────


def _hydrate(conn: sqlite3.Connection, row: sqlite3.Row) -> Snapshot:
    """Build a full Snapshot from a snapshots row + child tables."""
    snapshot_id = row["id"]

    # File signals
    file_signals: Dict[str, Dict[str, float]] = {}
    for fs_row in conn.execute(
        "SELECT file_path, signal_name, value FROM file_signals WHERE snapshot_id = ?",
        (snapshot_id,),
    ):
        fp = fs_row["file_path"]
        if fp not in file_signals:
            file_signals[fp] = {}
        file_signals[fp][fs_row["signal_name"]] = fs_row["value"]

    # Codebase signals
    codebase_signals: Dict[str, float] = {}
    for cs_row in conn.execute(
        "SELECT signal_name, value FROM codebase_signals WHERE snapshot_id = ?",
        (snapshot_id,),
    ):
        codebase_signals[cs_row["signal_name"]] = cs_row["value"]

    # Findings
    findings: List[FindingRecord] = []
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
