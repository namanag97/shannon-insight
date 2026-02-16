"""Write Snapshot / TensorSnapshot into the history database in a single transaction."""

import json
import sqlite3
from typing import Any

from .models import Snapshot, TensorSnapshot


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
                # Handle nested percentiles dict - flatten to separate rows
                if signal_name == "percentiles" and isinstance(value, dict):
                    for metric, pctl_value in value.items():
                        file_signal_rows.append(
                            (
                                snapshot_id,
                                file_path,
                                f"percentile_{metric}",
                                float(pctl_value) if pctl_value is not None else 0.0,
                            )
                        )
                elif value is not None:
                    # Skip None values, save everything else
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


def save_tensor_snapshot(conn: sqlite3.Connection, snapshot: TensorSnapshot) -> int:
    """Persist a v2 TensorSnapshot to the database.

    Writes to all v1 tables (snapshots, file_signals, codebase_signals, findings,
    dependency_edges) PLUS v2 tables (signal_history, module_signal_history,
    global_signal_history, finding_lifecycle).

    Parameters
    ----------
    conn:
        An open ``sqlite3.Connection`` (from ``HistoryDB.connect()``).
    snapshot:
        The ``TensorSnapshot`` to persist.

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

        # ── file_signals (v1 compat) + signal_history (v2) ─────
        file_signal_rows: list[tuple[Any, ...]] = []
        signal_history_rows: list[tuple[Any, ...]] = []
        for file_path, signals in snapshot.file_signals.items():
            percentiles = signals.get("percentiles", {})
            for signal_name, value in signals.items():
                if signal_name == "percentiles":
                    continue
                if not isinstance(value, (int, float)):
                    continue
                file_signal_rows.append((snapshot_id, file_path, signal_name, float(value)))
                pctl = percentiles.get(signal_name) if isinstance(percentiles, dict) else None
                signal_history_rows.append(
                    (snapshot_id, file_path, signal_name, float(value), pctl)
                )

        if file_signal_rows:
            cur.executemany(
                "INSERT INTO file_signals (snapshot_id, file_path, signal_name, value) "
                "VALUES (?, ?, ?, ?)",
                file_signal_rows,
            )
        if signal_history_rows:
            cur.executemany(
                "INSERT OR IGNORE INTO signal_history "
                "(snapshot_id, file_path, signal_name, value, percentile) "
                "VALUES (?, ?, ?, ?, ?)",
                signal_history_rows,
            )

        # ── module_signal_history (v2) ─────────────────────────
        module_rows: list[tuple[Any, ...]] = []
        for module_path, signals in snapshot.module_signals.items():
            for signal_name, value in signals.items():
                if isinstance(value, (int, float)):
                    module_rows.append((snapshot_id, module_path, signal_name, float(value)))
        if module_rows:
            cur.executemany(
                "INSERT OR IGNORE INTO module_signal_history "
                "(snapshot_id, module_path, signal_name, value) "
                "VALUES (?, ?, ?, ?)",
                module_rows,
            )

        # ── global_signals → codebase_signals (v1) + global_signal_history (v2)
        global_rows_v1: list[tuple[Any, ...]] = []
        global_rows_v2: list[tuple[Any, ...]] = []
        for signal_name, value in snapshot.global_signals.items():
            if isinstance(value, (int, float)):
                global_rows_v1.append((snapshot_id, signal_name, float(value)))
                global_rows_v2.append((snapshot_id, signal_name, float(value)))
        if global_rows_v1:
            cur.executemany(
                "INSERT INTO codebase_signals (snapshot_id, signal_name, value) VALUES (?, ?, ?)",
                global_rows_v1,
            )
        if global_rows_v2:
            cur.executemany(
                "INSERT OR IGNORE INTO global_signal_history "
                "(snapshot_id, signal_name, value) VALUES (?, ?, ?)",
                global_rows_v2,
            )

        # ── findings + finding_lifecycle ───────────────────────
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
            cur.execute(
                "INSERT INTO findings "
                "(snapshot_id, finding_type, identity_key, severity, title, files, evidence, suggestion) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    snapshot_id,
                    f.finding_type,
                    f.identity_key,
                    f.severity,
                    f.title,
                    json.dumps(f.files),
                    evidence_json,
                    f.suggestion,
                ),
            )

            # Upsert finding_lifecycle
            cur.execute(
                """
                INSERT INTO finding_lifecycle
                    (identity_key, first_seen_snapshot, last_seen_snapshot,
                     persistence_count, current_status, finding_type, severity)
                VALUES (?, ?, ?, 1, 'active', ?, ?)
                ON CONFLICT(identity_key) DO UPDATE SET
                    last_seen_snapshot = excluded.last_seen_snapshot,
                    persistence_count = persistence_count + 1,
                    current_status = 'active',
                    severity = excluded.severity
                """,
                (f.identity_key, snapshot_id, snapshot_id, f.finding_type, f.severity),
            )

        # Mark findings NOT in this snapshot as resolved
        if snapshot.findings:
            current_keys = [f.identity_key for f in snapshot.findings]
            placeholders = ",".join("?" * len(current_keys))
            cur.execute(
                f"UPDATE finding_lifecycle SET current_status = 'resolved' "
                f"WHERE current_status = 'active' AND identity_key NOT IN ({placeholders})",
                current_keys,
            )
        else:
            cur.execute(
                "UPDATE finding_lifecycle SET current_status = 'resolved' "
                "WHERE current_status = 'active'"
            )

        # ── dependency_edges ───────────────────────────────────
        edge_rows = [(snapshot_id, src, dst) for src, dst in snapshot.dependency_edges]
        if edge_rows:
            cur.executemany(
                "INSERT INTO dependency_edges (snapshot_id, src, dst) VALUES (?, ?, ?)",
                edge_rows,
            )

        conn.commit()
        return snapshot_id

    except Exception:
        conn.rollback()
        raise
