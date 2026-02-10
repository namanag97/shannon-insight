"""Write events to Parquet files in .shannon/parquet/.

Each event type gets its own Parquet file.  Snapshots are appended to
existing files (or new files are created).  This runs alongside the existing
SQLite writer during the strangler-fig migration.

Requires: pip install shannon-codebase-insight[tensordb]
"""

from __future__ import annotations

import json
import logging
from dataclasses import asdict
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def _import_pyarrow():
    """Lazy import pyarrow -- raises ImportError with a helpful message."""
    try:
        import pyarrow as pa
        import pyarrow.parquet as pq

        return pa, pq
    except ImportError:
        raise ImportError(
            "pyarrow is required for Parquet export. "
            "Install with: pip install shannon-codebase-insight[tensordb]"
        ) from None


# ── Table names → filenames ──────────────────────────────────────────

TABLE_FILES = {
    "snapshots": "snapshots.parquet",
    "file_signals": "file_signals.parquet",
    "module_signals": "module_signals.parquet",
    "global_signals": "global_signals.parquet",
    "edges": "edges.parquet",
    "findings": "findings.parquet",
}


# ── Public API ───────────────────────────────────────────────────────


class ParquetWriter:
    """Writes event data to Parquet files in a .shannon/parquet/ directory.

    Usage::

        writer = ParquetWriter("/path/to/project")
        writer.write_events(events_dict)  # from emitter.snapshot_to_events()
    """

    def __init__(self, project_root: str) -> None:
        self.parquet_dir = Path(project_root) / ".shannon" / "parquet"

    def _ensure_dir(self) -> None:
        """Create the parquet directory and .gitignore."""
        self.parquet_dir.mkdir(parents=True, exist_ok=True)
        gitignore = self.parquet_dir.parent / ".gitignore"
        if not gitignore.exists():
            gitignore.write_text("*\n")

    def write_events(self, events: dict[str, Any]) -> dict[str, Path]:
        """Write all events from an emitter output dict to Parquet files.

        Parameters
        ----------
        events:
            Dict from ``emitter.snapshot_to_events()``. Keys:
            "snapshot", "file_signals", "module_signals", "global_signals",
            "edges", "findings".

        Returns
        -------
        dict[str, Path]
            Map of table name -> Parquet file path written.
        """
        pa, pq = _import_pyarrow()
        self._ensure_dir()

        written: dict[str, Path] = {}

        # Snapshot metadata
        snap_event = events["snapshot"]
        snap_path = self._write_snapshot(pa, pq, snap_event)
        written["snapshots"] = snap_path

        # File signals
        if events["file_signals"]:
            fs_path = self._write_file_signals(pa, pq, events["file_signals"])
            written["file_signals"] = fs_path

        # Module signals
        if events["module_signals"]:
            ms_path = self._write_module_signals(pa, pq, events["module_signals"])
            written["module_signals"] = ms_path

        # Global signals
        gs_path = self._write_global_signals(pa, pq, events["global_signals"])
        written["global_signals"] = gs_path

        # Edges
        if events["edges"]:
            edges_path = self._write_edges(pa, pq, events["edges"])
            written["edges"] = edges_path

        # Findings
        if events["findings"]:
            findings_path = self._write_findings(pa, pq, events["findings"])
            written["findings"] = findings_path

        logger.info(
            "Parquet snapshot written: %d tables to %s",
            len(written),
            self.parquet_dir,
        )
        return written

    # ── Private writers ──────────────────────────────────────────────

    def _write_snapshot(self, pa, pq, snap_event) -> Path:
        """Write snapshot metadata row."""
        row = asdict(snap_event)
        row["analyzers_ran"] = json.dumps(row["analyzers_ran"])
        table = pa.Table.from_pylist([row])
        path = self.parquet_dir / TABLE_FILES["snapshots"]
        _append_parquet(pa, pq, table, path)
        return path

    def _write_file_signals(self, pa, pq, file_signal_events: list) -> Path:
        """Write file signal rows (wide table)."""
        rows = [e.to_dict() for e in file_signal_events]
        table = pa.Table.from_pylist(rows)
        path = self.parquet_dir / TABLE_FILES["file_signals"]
        _append_parquet(pa, pq, table, path)
        return path

    def _write_module_signals(self, pa, pq, module_signal_events: list) -> Path:
        """Write module signal rows."""
        rows = [e.to_dict() for e in module_signal_events]
        table = pa.Table.from_pylist(rows)
        path = self.parquet_dir / TABLE_FILES["module_signals"]
        _append_parquet(pa, pq, table, path)
        return path

    def _write_global_signals(self, pa, pq, global_signal_event) -> Path:
        """Write global signals row."""
        row = asdict(global_signal_event)
        table = pa.Table.from_pylist([row])
        path = self.parquet_dir / TABLE_FILES["global_signals"]
        _append_parquet(pa, pq, table, path)
        return path

    def _write_edges(self, pa, pq, edge_events: list) -> Path:
        """Write edge rows."""
        rows = [e.to_dict() for e in edge_events]
        table = pa.Table.from_pylist(rows)
        path = self.parquet_dir / TABLE_FILES["edges"]
        _append_parquet(pa, pq, table, path)
        return path

    def _write_findings(self, pa, pq, finding_events: list) -> Path:
        """Write finding rows."""
        rows = [e.to_dict() for e in finding_events]
        table = pa.Table.from_pylist(rows)
        path = self.parquet_dir / TABLE_FILES["findings"]
        _append_parquet(pa, pq, table, path)
        return path


# ── Helpers ──────────────────────────────────────────────────────────


def _append_parquet(pa, pq, new_table, path: Path) -> None:
    """Append rows to an existing Parquet file, or create a new one.

    Strategy: read existing file, concatenate tables, overwrite.
    This is fine for the small row counts we deal with (< 10k files).
    For larger codebases, we can switch to a partitioned dataset later.
    """
    if path.exists():
        try:
            existing = pq.read_table(str(path))
            # Align schemas before concatenation
            combined_schema = pa.unify_schemas([existing.schema, new_table.schema])
            existing_casted = existing.cast(combined_schema)
            new_casted = new_table.cast(combined_schema)
            merged = pa.concat_tables([existing_casted, new_casted])
            pq.write_table(merged, str(path))
        except Exception:
            logger.warning("Failed to append to %s, overwriting", path)
            pq.write_table(new_table, str(path))
    else:
        pq.write_table(new_table, str(path))
