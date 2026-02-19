"""Content-addressable blob storage backed by SQLite.

Stores raw file content keyed by SHA-256 hash.  Content is zlib-compressed
on write; the compressed size is recorded for NCD (Normalized Compression
Distance) clone detection.

Usage::

    store = BlobStore(conn)
    content_hash = store.store(b"def hello(): ...")
    assert store.has(content_hash)
    assert store.get(content_hash) == b"def hello(): ..."
    assert store.get_compressed_size(content_hash) > 0
"""

from __future__ import annotations

import hashlib
import logging
import sqlite3
import zlib

logger = logging.getLogger(__name__)

# zlib compression level: 6 is the default, good balance of speed and ratio.
_ZLIB_LEVEL = 6


class BlobStore:
    """Content-addressable blob storage using SQLite + zlib.

    Each blob is stored once (deduplication by SHA-256).  Compressed size
    is recorded at write time for downstream NCD computation.

    The caller owns the connection and is responsible for commits.
    """

    def __init__(self, conn: sqlite3.Connection) -> None:
        """Initialize the blob store.

        Args:
            conn: An open SQLite connection.  The ``blobs`` table must
                  already exist (call ``create_schema`` first).
        """
        self._conn = conn

    # ── Public API ────────────────────────────────────────────────────

    def store(self, content: bytes) -> str:
        """Store content and return its SHA-256 hash.

        If the content already exists (same hash), this is a no-op.

        Args:
            content: Raw file bytes to store.

        Returns:
            Hex-encoded SHA-256 hash of ``content``.
        """
        content_hash = hashlib.sha256(content).hexdigest()

        if self.has(content_hash):
            return content_hash

        compressed = zlib.compress(content, _ZLIB_LEVEL)

        self._conn.execute(
            "INSERT OR IGNORE INTO blobs "
            "(content_hash, data, original_size, compressed_size) "
            "VALUES (?, ?, ?, ?)",
            (content_hash, compressed, len(content), len(compressed)),
        )

        return content_hash

    def get(self, content_hash: str) -> bytes | None:
        """Retrieve content by its hash.

        Args:
            content_hash: SHA-256 hex digest.

        Returns:
            The original (decompressed) bytes, or ``None`` if not found.
        """
        cursor = self._conn.execute(
            "SELECT data FROM blobs WHERE content_hash = ?",
            (content_hash,),
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return zlib.decompress(row[0])

    def has(self, content_hash: str) -> bool:
        """Check whether a blob exists.

        Args:
            content_hash: SHA-256 hex digest.

        Returns:
            ``True`` if the blob is stored.
        """
        cursor = self._conn.execute(
            "SELECT 1 FROM blobs WHERE content_hash = ?",
            (content_hash,),
        )
        return cursor.fetchone() is not None

    def get_compressed_size(self, content_hash: str) -> int | None:
        """Get the compressed size of a stored blob.

        Used by NCD clone detection: NCD(x,y) uses C(x) and C(y).

        Args:
            content_hash: SHA-256 hex digest.

        Returns:
            Compressed size in bytes, or ``None`` if the blob is not found.
        """
        cursor = self._conn.execute(
            "SELECT compressed_size FROM blobs WHERE content_hash = ?",
            (content_hash,),
        )
        row = cursor.fetchone()
        if row is None:
            return None
        result: int = row[0]
        return result

    def get_original_size(self, content_hash: str) -> int | None:
        """Get the original (uncompressed) size of a stored blob.

        Args:
            content_hash: SHA-256 hex digest.

        Returns:
            Original size in bytes, or ``None`` if the blob is not found.
        """
        cursor = self._conn.execute(
            "SELECT original_size FROM blobs WHERE content_hash = ?",
            (content_hash,),
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return row[0]

    def store_batch(self, contents: list[bytes]) -> list[str]:
        """Store multiple blobs in a single transaction.

        More efficient than calling ``store()`` in a loop because it
        batches the INSERT statements.

        Args:
            contents: List of raw file bytes.

        Returns:
            List of SHA-256 hex digests, one per input.
        """
        hashes: list[str] = []
        rows: list[tuple[str, bytes, int, int]] = []

        for content in contents:
            content_hash = hashlib.sha256(content).hexdigest()
            hashes.append(content_hash)

            if not self.has(content_hash):
                compressed = zlib.compress(content, _ZLIB_LEVEL)
                rows.append((content_hash, compressed, len(content), len(compressed)))

        if rows:
            self._conn.executemany(
                "INSERT OR IGNORE INTO blobs "
                "(content_hash, data, original_size, compressed_size) "
                "VALUES (?, ?, ?, ?)",
                rows,
            )

        return hashes

    def count(self) -> int:
        """Return the total number of stored blobs.

        Returns:
            Number of distinct blobs in the store.
        """
        cursor = self._conn.execute("SELECT COUNT(*) FROM blobs")
        return cursor.fetchone()[0]

    def total_original_bytes(self) -> int:
        """Return the total original size of all stored blobs.

        Returns:
            Sum of original sizes in bytes.
        """
        cursor = self._conn.execute(
            "SELECT COALESCE(SUM(original_size), 0) FROM blobs"
        )
        return cursor.fetchone()[0]

    def total_compressed_bytes(self) -> int:
        """Return the total compressed size of all stored blobs.

        Returns:
            Sum of compressed sizes in bytes.
        """
        cursor = self._conn.execute(
            "SELECT COALESCE(SUM(compressed_size), 0) FROM blobs"
        )
        return cursor.fetchone()[0]
