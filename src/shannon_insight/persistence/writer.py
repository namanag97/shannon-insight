"""Write a Snapshot into the history database in a single transaction."""

import json
import sqlite3

from .models import Snapshot


def save_snapshot(conn: sqlite3.Connection, snapshot: Snapshot) -> int:
    """Persist a snapshot to the database.

    All inserts happen inside a single transaction so the database stays
    consistent even if the process is interrupted.

    Parameters
    ----------
    conn:
        An open ``sqlite3.Connection`` (from ``HistoryDB.connect()``).
    snapshot:
        The ``Snapshot`` to persist.

    Returns
    -------
    int
        The ``snapshot_id`` (primary key) of the newly inserted row.
    """
    cur = conn.cursor()
    try:
        cur.execute("BEGIN")

        # ── snapshots row ────────────────────────────────────────
        cur.execute(
            """
            INSERT INTO snapshots (
                schema_version, tool_version, commit_sha, timestamp,
                analyzed_path, file_count, module_count, commits_analyzed,
                analyzers_ran, config_hash
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                snapshot.schema_version,
                snapshot.tool_version,
                snapshot.commit_sha,
                snapshot.timestamp,
                snapshot.analyzed_path,
                snapshot.file_count,
                snapshot.module_count,
                snapshot.commits_analyzed,
                json.dumps(snapshot.analyzers_ran),
                snapshot.config_hash,
            ),
        )
        snapshot_id = cur.lastrowid
        assert snapshot_id is not None

        # ── file_signals (batch) ─────────────────────────────────
        file_signal_rows = []
        for file_path, signals in snapshot.file_signals.items():
            for signal_name, value in signals.items():
                file_signal_rows.append((snapshot_id, file_path, signal_name, value))
        if file_signal_rows:
            cur.executemany(
                """
                INSERT INTO file_signals (snapshot_id, file_path, signal_name, value)
                VALUES (?, ?, ?, ?)
                """,
                file_signal_rows,
            )

        # ── codebase_signals (batch) ─────────────────────────────
        codebase_signal_rows = [
            (snapshot_id, signal_name, value)
            for signal_name, value in snapshot.codebase_signals.items()
        ]
        if codebase_signal_rows:
            cur.executemany(
                """
                INSERT INTO codebase_signals (snapshot_id, signal_name, value)
                VALUES (?, ?, ?)
                """,
                codebase_signal_rows,
            )

        # ── findings (batch) ─────────────────────────────────────
        finding_rows = []
        for f in snapshot.findings:
            evidence_json = json.dumps(
                [
                    {
                        "signal": e.signal,
                        "value": e.value,
                        "percentile": e.percentile,
                        "description": e.description,
                    }
                    for e in f.evidence
                ]
            )
            finding_rows.append(
                (
                    snapshot_id,
                    f.finding_type,
                    f.identity_key,
                    f.severity,
                    f.title,
                    json.dumps(f.files),
                    evidence_json,
                    f.suggestion,
                )
            )
        if finding_rows:
            cur.executemany(
                """
                INSERT INTO findings (
                    snapshot_id, finding_type, identity_key, severity,
                    title, files, evidence, suggestion
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                finding_rows,
            )

        # ── dependency_edges (batch) ─────────────────────────────
        edge_rows = [(snapshot_id, src, dst) for src, dst in snapshot.dependency_edges]
        if edge_rows:
            cur.executemany(
                """
                INSERT INTO dependency_edges (snapshot_id, src, dst)
                VALUES (?, ?, ?)
                """,
                edge_rows,
            )

        conn.commit()
        return snapshot_id

    except Exception:
        conn.rollback()
        raise
