"""Read Parquet snapshot files from .shannon/parquet/.

Provides read access to Parquet tables written by writer.py.
Each public function returns Python-native data structures (dicts, lists).

Requires: pip install shannon-codebase-insight[tensordb]
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def _import_pyarrow():
    """Lazy import pyarrow -- raises ImportError with a helpful message."""
    try:
        import pyarrow.parquet as pq

        return pq
    except ImportError:
        raise ImportError(
            "pyarrow is required for Parquet export. "
            "Install with: pip install shannon-codebase-insight[tensordb]"
        ) from None


class ParquetReader:
    """Reads Parquet snapshot data from .shannon/parquet/.

    Usage::

        reader = ParquetReader("/path/to/project")
        snapshots = reader.list_snapshots()
        file_sigs = reader.read_file_signals("snapshot-id-123")
    """

    def __init__(self, project_root: str) -> None:
        self.parquet_dir = Path(project_root) / ".shannon" / "parquet"

    @property
    def available(self) -> bool:
        """Return True if the Parquet directory exists and has files."""
        if not self.parquet_dir.exists():
            return False
        return any(self.parquet_dir.glob("*.parquet"))

    def list_snapshots(self, limit: int = 20) -> list[dict[str, Any]]:
        """List recent snapshots, newest first.

        Parameters
        ----------
        limit:
            Maximum number of snapshots to return.

        Returns
        -------
        list[dict]
            Each dict has keys: snapshot_id, timestamp, commit_sha, file_count,
            module_count, tool_version, analyzers_ran.
        """
        pq = _import_pyarrow()
        path = self.parquet_dir / "snapshots.parquet"
        if not path.exists():
            return []

        table = pq.read_table(str(path))
        rows = table.to_pylist()

        # Sort by timestamp descending
        rows.sort(key=lambda r: r.get("timestamp", ""), reverse=True)

        results: list[dict[str, Any]] = []
        for row in rows[:limit]:
            analyzers = row.get("analyzers_ran", "[]")
            if isinstance(analyzers, str):
                analyzers = json.loads(analyzers)
            results.append(
                {
                    "snapshot_id": row["snapshot_id"],
                    "timestamp": row.get("timestamp", ""),
                    "commit_sha": row.get("commit_sha"),
                    "file_count": row.get("file_count", 0),
                    "module_count": row.get("module_count", 0),
                    "tool_version": row.get("tool_version", ""),
                    "analyzers_ran": analyzers,
                }
            )
        return results

    def read_file_signals(
        self,
        snapshot_id: str,
    ) -> dict[str, dict[str, Any]]:
        """Read all file signals for a given snapshot.

        Parameters
        ----------
        snapshot_id:
            The snapshot ID to query.

        Returns
        -------
        dict[str, dict[str, Any]]
            Map of file_path -> {signal_name: value}.
            Only non-None values are included.
        """
        pq = _import_pyarrow()
        path = self.parquet_dir / "file_signals.parquet"
        if not path.exists():
            return {}

        table = pq.read_table(str(path))
        rows = table.to_pylist()

        result: dict[str, dict[str, Any]] = {}
        for row in rows:
            if row.get("snapshot_id") != snapshot_id:
                continue
            file_path = row.get("file_path", "")
            signals: dict[str, Any] = {}
            for key, value in row.items():
                if key in ("snapshot_id", "file_path"):
                    continue
                if value is not None:
                    signals[key] = value
            result[file_path] = signals
        return result

    def read_module_signals(
        self,
        snapshot_id: str,
    ) -> dict[str, dict[str, Any]]:
        """Read all module signals for a given snapshot.

        Returns
        -------
        dict[str, dict[str, Any]]
            Map of module_path -> {signal_name: value}.
        """
        pq = _import_pyarrow()
        path = self.parquet_dir / "module_signals.parquet"
        if not path.exists():
            return {}

        table = pq.read_table(str(path))
        rows = table.to_pylist()

        result: dict[str, dict[str, Any]] = {}
        for row in rows:
            if row.get("snapshot_id") != snapshot_id:
                continue
            module_path = row.get("module_path", "")
            signals: dict[str, Any] = {}
            for key, value in row.items():
                if key in ("snapshot_id", "module_path"):
                    continue
                if value is not None:
                    signals[key] = value
            result[module_path] = signals
        return result

    def read_global_signals(
        self,
        snapshot_id: str,
    ) -> dict[str, Any]:
        """Read global signals for a given snapshot.

        Returns
        -------
        dict[str, Any]
            Signal name -> value.
        """
        pq = _import_pyarrow()
        path = self.parquet_dir / "global_signals.parquet"
        if not path.exists():
            return {}

        table = pq.read_table(str(path))
        rows = table.to_pylist()

        for row in rows:
            if row.get("snapshot_id") != snapshot_id:
                continue
            signals: dict[str, Any] = {}
            for key, value in row.items():
                if key == "snapshot_id":
                    continue
                if value is not None:
                    signals[key] = value
            return signals
        return {}

    def read_edges(
        self,
        snapshot_id: str,
        space: str | None = None,
    ) -> list[dict[str, Any]]:
        """Read edges for a given snapshot, optionally filtered by space.

        Parameters
        ----------
        snapshot_id:
            The snapshot ID to query.
        space:
            Optional filter: "G1", "G4", "G5", or "G6".

        Returns
        -------
        list[dict]
            Each dict has keys: source, target, space, weight, data.
        """
        pq = _import_pyarrow()
        path = self.parquet_dir / "edges.parquet"
        if not path.exists():
            return []

        table = pq.read_table(str(path))
        rows = table.to_pylist()

        result: list[dict[str, Any]] = []
        for row in rows:
            if row.get("snapshot_id") != snapshot_id:
                continue
            if space is not None and row.get("space") != space:
                continue
            result.append(
                {
                    "source": row["source"],
                    "target": row["target"],
                    "space": row["space"],
                    "weight": row.get("weight", 1.0),
                    "data": row.get("data"),
                }
            )
        return result

    def read_findings(
        self,
        snapshot_id: str,
    ) -> list[dict[str, Any]]:
        """Read findings for a given snapshot.

        Returns
        -------
        list[dict]
            Each dict has finding fields.
        """
        pq = _import_pyarrow()
        path = self.parquet_dir / "findings.parquet"
        if not path.exists():
            return []

        table = pq.read_table(str(path))
        rows = table.to_pylist()

        result: list[dict[str, Any]] = []
        for row in rows:
            if row.get("snapshot_id") != snapshot_id:
                continue
            # Deserialize JSON fields
            files = row.get("files", "[]")
            if isinstance(files, str):
                files = json.loads(files)
            evidence = row.get("evidence", "[]")
            if isinstance(evidence, str):
                evidence = json.loads(evidence)
            result.append(
                {
                    "finding_type": row["finding_type"],
                    "identity_key": row["identity_key"],
                    "severity": row["severity"],
                    "title": row["title"],
                    "files": files,
                    "evidence": evidence,
                    "suggestion": row.get("suggestion", ""),
                    "confidence": row.get("confidence", 1.0),
                    "effort": row.get("effort", "MEDIUM"),
                    "scope": row.get("scope", "FILE"),
                }
            )
        return result
