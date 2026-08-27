"""File Identity Resolution.

Establishes stable file identity across renames using an in-memory cache
backed by SQLite persistence.

Processing order matters: commits MUST be fed oldest-first so that rename
chains are built correctly (A created -> A renamed to B -> B renamed to C
produces one FileID for A, B, and C).

Edge cases:
  - Partial history (MODIFIED without prior ADD): treated as implicit ADD.
  - Re-add after delete: new identity (not resurrected old).
  - Copy: new identity (not shared with source).
"""

from __future__ import annotations

import logging
import sqlite3
import uuid
from collections.abc import Iterator

from .models import ChangeType, FileIdentity

logger = logging.getLogger(__name__)

# ── SQL Schema ──────────────────────────────────────────────────────────

_CREATE_TABLES = """
CREATE TABLE IF NOT EXISTS file_identities (
    file_id       TEXT PRIMARY KEY,
    birth_commit  TEXT NOT NULL,
    birth_path    TEXT NOT NULL,
    current_path  TEXT,
    is_alive      INTEGER NOT NULL DEFAULT 1,
    created_at    INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS file_renames (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    file_id     TEXT NOT NULL,
    commit_hash TEXT NOT NULL,
    timestamp   INTEGER NOT NULL,
    old_path    TEXT NOT NULL,
    new_path    TEXT NOT NULL,
    UNIQUE(file_id, commit_hash)
);

CREATE INDEX IF NOT EXISTS idx_renames_file
    ON file_renames(file_id);

CREATE INDEX IF NOT EXISTS idx_identities_path
    ON file_identities(current_path)
    WHERE is_alive = 1;
"""


# ── FileChange (local to this module) ───────────────────────────────────


class FileChange:
    """A file change observed in a commit.

    Lightweight carrier used by ``FileIdentityResolver.process_change``.
    Not persisted directly -- the resolver extracts what it needs.
    """

    __slots__ = ("commit_hash", "path", "change_type", "old_path", "additions", "deletions")

    def __init__(
        self,
        commit_hash: str,
        path: str,
        change_type: ChangeType,
        old_path: str | None = None,
        additions: int | None = None,
        deletions: int | None = None,
    ) -> None:
        self.commit_hash = commit_hash
        self.path = path
        self.change_type = change_type
        self.old_path = old_path
        self.additions = additions
        self.deletions = deletions


# ── Resolver ────────────────────────────────────────────────────────────


class FileIdentityResolver:
    """Resolves file identity across renames.

    Key invariants:
      - Each unique file has exactly one FileID (UUID).
      - FileID survives renames (A->B means A and B share the same FileID).
      - Deleted files retain their FileID (is_alive=False).

    Usage::

        resolver = FileIdentityResolver(conn)

        # Process git history chronologically (oldest first!)
        for commit in git_log(oldest_first=True):
            for change in commit.changes:
                resolver.process_change(commit.hash, commit.timestamp, change)

        resolver.commit()

        # Query
        file_id = resolver.resolve("src/foo.py")
    """

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn
        self._ensure_tables()
        # In-memory caches for hot-path lookups.
        self._path_to_id: dict[str, str] = {}  # current_path -> file_id (alive only)
        self._id_to_path: dict[str, str | None] = {}  # file_id -> current_path (None if dead)
        self._load_cache()

    # ── Schema bootstrap ────────────────────────────────────────────

    def _ensure_tables(self) -> None:
        """Create tables/indexes if they don't exist."""
        self.conn.executescript(_CREATE_TABLES)

    # ── Cache loading ───────────────────────────────────────────────

    def _load_cache(self) -> None:
        """Populate in-memory caches from persisted data."""
        cursor = self.conn.execute("SELECT file_id, current_path, is_alive FROM file_identities")
        for row in cursor:
            file_id = row[0]
            current_path = row[1]
            is_alive = bool(row[2])
            if is_alive and current_path is not None:
                self._path_to_id[current_path] = file_id
                self._id_to_path[file_id] = current_path
            else:
                self._id_to_path[file_id] = None

    # ── Change processing ───────────────────────────────────────────

    def process_change(
        self,
        commit_hash: str,
        timestamp: int,
        change: FileChange,
    ) -> str:
        """Process a single file change and return the file_id.

        Dispatches to the appropriate handler based on ``change.change_type``.
        Returns the stable file_id for the affected file.
        """
        ct = change.change_type

        handler = {
            ChangeType.ADDED: self._handle_add,
            ChangeType.RENAMED: self._handle_rename,
            ChangeType.DELETED: self._handle_delete,
            ChangeType.MODIFIED: self._handle_modify,
            # Copy creates a NEW identity rather than sharing the source identity.
            ChangeType.COPIED: self._handle_add,
        }.get(ct)
        if handler is None:
            logger.warning(
                "Unknown change type %s for %s in %s, treating as ADD",
                ct,
                change.path,
                commit_hash,
            )
            handler = self._handle_add
        return handler(commit_hash, timestamp, change)

    def _handle_add(self, commit_hash: str, timestamp: int, change: FileChange) -> str:
        """Handle ADD (or COPY) -- create a fresh identity.

        If the path already has a *living* identity this is a logic error in
        input data but we handle it gracefully by returning the existing id.
        """
        existing = self._path_to_id.get(change.path)
        if existing is not None:
            # Path already tracked and alive. This could happen if git history
            # has duplicate ADDs. Return the existing identity.
            logger.debug(
                "ADD for already-alive path %s (commit %s), reusing %s",
                change.path,
                commit_hash,
                existing,
            )
            return existing

        file_id = str(uuid.uuid4())
        self._persist_identity(file_id, commit_hash, change.path, timestamp)
        self._path_to_id[change.path] = file_id
        self._id_to_path[file_id] = change.path
        return file_id

    def _handle_rename(self, commit_hash: str, timestamp: int, change: FileChange) -> str:
        """Handle RENAME -- transfer identity from old_path to new_path.

        If old_path has no known identity (partial history / shallow clone)
        we create a retroactive identity rooted at the rename commit.
        """
        old_path = change.old_path
        new_path = change.path

        if old_path is None:
            # Malformed rename without old_path: treat as add.
            logger.warning(
                "RENAME without old_path for %s in %s, treating as ADD",
                new_path,
                commit_hash,
            )
            return self._handle_add(commit_hash, timestamp, change)

        # Find existing identity for old_path.
        file_id = self._path_to_id.get(old_path)

        if file_id is None:
            # Partial history: old_path was never seen. Create a retroactive
            # identity anchored at this commit with old_path as birth_path.
            file_id = str(uuid.uuid4())
            self._persist_identity(file_id, commit_hash, old_path, timestamp)

        # Record the rename event.
        self.conn.execute(
            """
            INSERT OR IGNORE INTO file_renames
                (file_id, commit_hash, timestamp, old_path, new_path)
            VALUES (?, ?, ?, ?, ?)
            """,
            (file_id, commit_hash, timestamp, old_path, new_path),
        )

        # Update current_path in DB.
        self.conn.execute(
            "UPDATE file_identities SET current_path = ? WHERE file_id = ?",
            (new_path, file_id),
        )

        # Update caches: remove old mapping, add new.
        self._path_to_id.pop(old_path, None)
        self._path_to_id[new_path] = file_id
        self._id_to_path[file_id] = new_path

        return file_id

    def _handle_delete(self, commit_hash: str, timestamp: int, change: FileChange) -> str:
        """Handle DELETE -- mark identity as dead.

        If the path has no known identity (partial history), create one
        retroactively so we still have a record.
        """
        file_id = self._path_to_id.get(change.path)

        if file_id is None:
            # Partial history: never saw ADD for this file.
            file_id = str(uuid.uuid4())
            self._persist_identity(file_id, commit_hash, change.path, timestamp)

        # Mark dead in DB.
        self.conn.execute(
            "UPDATE file_identities SET is_alive = 0, current_path = NULL WHERE file_id = ?",
            (file_id,),
        )

        # Update caches.
        self._path_to_id.pop(change.path, None)
        self._id_to_path[file_id] = None

        return file_id

    def _handle_modify(self, commit_hash: str, timestamp: int, change: FileChange) -> str:
        """Handle MODIFY -- just return existing identity.

        If the path has no identity yet (partial history / shallow clone),
        treat as an implicit ADD.
        """
        file_id = self._path_to_id.get(change.path)
        if file_id is not None:
            return file_id

        # Implicit ADD for partial history.
        logger.debug(
            "MODIFY for unknown path %s (commit %s), treating as implicit ADD",
            change.path,
            commit_hash,
        )
        return self._handle_add(commit_hash, timestamp, change)

    # ── Persistence helpers ─────────────────────────────────────────

    def _persist_identity(
        self,
        file_id: str,
        birth_commit: str,
        birth_path: str,
        timestamp: int,
    ) -> None:
        """Insert a new identity row into the database."""
        self.conn.execute(
            """
            INSERT INTO file_identities
                (file_id, birth_commit, birth_path, current_path, is_alive, created_at)
            VALUES (?, ?, ?, ?, 1, ?)
            """,
            (file_id, birth_commit, birth_path, birth_path, timestamp),
        )

    # ── Query API ───────────────────────────────────────────────────

    def resolve(self, path: str) -> str | None:
        """Get the FileID for a currently-alive path.

        This is the hot-path query -- served from the in-memory cache.

        Returns None if the path is unknown or the file has been deleted.
        """
        return self._path_to_id.get(path)

    def resolve_at(self, path: str, timestamp: int) -> str | None:
        """Get the FileID that owned *path* at a given point in time.

        Searches rename history to find which identity held the path
        at (or just before) *timestamp*.

        Falls back to birth_path matching if no rename covers the path.
        """
        # 1. Check if a rename *into* this path happened at or before timestamp.
        row = self.conn.execute(
            """
            SELECT file_id FROM file_renames
            WHERE new_path = ? AND timestamp <= ?
            ORDER BY timestamp DESC
            LIMIT 1
            """,
            (path, timestamp),
        ).fetchone()
        if row is not None:
            # Confirm the file wasn't renamed *away* before our timestamp.
            later_rename = self.conn.execute(
                """
                SELECT id FROM file_renames
                WHERE file_id = ? AND old_path = ? AND timestamp <= ? AND timestamp > (
                    SELECT MAX(timestamp) FROM file_renames
                    WHERE file_id = ? AND new_path = ? AND timestamp <= ?
                )
                """,
                (row[0], path, timestamp, row[0], path, timestamp),
            ).fetchone()
            if later_rename is None:
                return str(row[0])

        # 2. Check birth_path (file may have never been renamed).
        row = self.conn.execute(
            """
            SELECT file_id FROM file_identities
            WHERE birth_path = ? AND created_at <= ?
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (path, timestamp),
        ).fetchone()
        if row is not None:
            # Make sure it wasn't renamed away from birth_path before timestamp.
            later_rename = self.conn.execute(
                """
                SELECT id FROM file_renames
                WHERE file_id = ? AND old_path = ? AND timestamp <= ?
                """,
                (row[0], path, timestamp),
            ).fetchone()
            if later_rename is None:
                return str(row[0])

        return None

    def get_identity(self, file_id: str) -> FileIdentity | None:
        """Look up a FileIdentity by its UUID."""
        row = self.conn.execute(
            "SELECT file_id, birth_commit, birth_path, current_path, is_alive "
            "FROM file_identities WHERE file_id = ?",
            (file_id,),
        ).fetchone()
        if row is None:
            return None
        return FileIdentity(
            file_id=row[0],
            birth_commit=row[1],
            birth_path=row[2],
            current_path=row[3],
            is_alive=bool(row[4]),
        )

    def get_path_history(self, file_id: str) -> list[tuple[str, int, int | None]]:
        """Return the rename history for a file_id.

        Returns a list of ``(path, valid_from, valid_until)`` tuples
        sorted chronologically.  ``valid_until`` is None for the final
        (current) path segment.
        """
        identity = self.get_identity(file_id)
        if identity is None:
            return []

        renames = self.conn.execute(
            "SELECT old_path, new_path, timestamp FROM file_renames "
            "WHERE file_id = ? ORDER BY timestamp",
            (file_id,),
        ).fetchall()

        history: list[tuple[str, int, int | None]] = []

        # Birth timestamp.
        birth_row = self.conn.execute(
            "SELECT created_at FROM file_identities WHERE file_id = ?",
            (file_id,),
        ).fetchone()
        birth_ts = birth_row[0] if birth_row else 0

        if not renames:
            # Never renamed.
            history.append((identity.birth_path, birth_ts, None))
        else:
            # First segment: birth_path -> first rename.
            history.append((identity.birth_path, birth_ts, renames[0][2]))
            # Middle segments: between renames.
            for i, rename in enumerate(renames):
                valid_until = renames[i + 1][2] if i + 1 < len(renames) else None
                history.append((rename[1], rename[2], valid_until))

        return history

    def get_current_path(self, file_id: str) -> str | None:
        """Return the current path for a file_id, or None if dead."""
        return self._id_to_path.get(file_id)

    def get_all_paths(self, file_id: str) -> set[str]:
        """Return every path this file has ever held."""
        paths: set[str] = set()

        identity = self.get_identity(file_id)
        if identity is None:
            return paths

        paths.add(identity.birth_path)
        if identity.current_path is not None:
            paths.add(identity.current_path)

        cursor = self.conn.execute(
            "SELECT old_path, new_path FROM file_renames WHERE file_id = ?",
            (file_id,),
        )
        for row in cursor:
            paths.add(row[0])
            paths.add(row[1])

        return paths

    def iterate_alive(self) -> Iterator[FileIdentity]:
        """Iterate over all alive file identities."""
        cursor = self.conn.execute(
            "SELECT file_id, birth_commit, birth_path, current_path, is_alive "
            "FROM file_identities WHERE is_alive = 1"
        )
        for row in cursor:
            yield FileIdentity(
                file_id=row[0],
                birth_commit=row[1],
                birth_path=row[2],
                current_path=row[3],
                is_alive=bool(row[4]),
            )

    def commit(self) -> None:
        """Commit the current transaction."""
        self.conn.commit()

    def stats(self) -> dict[str, int]:
        """Return summary statistics about tracked identities."""
        total = self.conn.execute("SELECT COUNT(*) FROM file_identities").fetchone()[0]
        alive = self.conn.execute(
            "SELECT COUNT(*) FROM file_identities WHERE is_alive = 1"
        ).fetchone()[0]
        dead = total - alive
        renames = self.conn.execute("SELECT COUNT(*) FROM file_renames").fetchone()[0]
        return {
            "total_identities": total,
            "alive": alive,
            "dead": dead,
            "renames": renames,
        }


__all__ = [
    "ChangeType",
    "FileChange",
    "FileIdentity",
    "FileIdentityResolver",
]
