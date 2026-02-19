"""Tests for FileIdentityResolver -- stable file identity across renames."""

from __future__ import annotations

import sqlite3

import pytest

from shannon_insight.facts.identity import FileChange, FileIdentityResolver
from shannon_insight.facts.models import ChangeType


@pytest.fixture
def conn() -> sqlite3.Connection:
    """In-memory SQLite connection for testing."""
    c = sqlite3.connect(":memory:")
    yield c
    c.close()


@pytest.fixture
def resolver(conn: sqlite3.Connection) -> FileIdentityResolver:
    """Fresh resolver backed by in-memory DB."""
    return FileIdentityResolver(conn)


# ── Basic lifecycle ─────────────────────────────────────────────────────


class TestAddFile:
    """Adding a file creates a new identity."""

    def test_add_creates_identity(self, resolver: FileIdentityResolver) -> None:
        change = FileChange("aaa", "src/foo.py", ChangeType.ADDED)
        fid = resolver.process_change("aaa", 1000, change)

        assert fid is not None
        assert resolver.resolve("src/foo.py") == fid

    def test_add_identity_fields(self, resolver: FileIdentityResolver) -> None:
        change = FileChange("aaa", "src/foo.py", ChangeType.ADDED)
        fid = resolver.process_change("aaa", 1000, change)

        identity = resolver.get_identity(fid)
        assert identity is not None
        assert identity.file_id == fid
        assert identity.birth_commit == "aaa"
        assert identity.birth_path == "src/foo.py"
        assert identity.current_path == "src/foo.py"
        assert identity.is_alive is True

    def test_two_files_get_different_ids(self, resolver: FileIdentityResolver) -> None:
        fid1 = resolver.process_change("aaa", 1000, FileChange("aaa", "a.py", ChangeType.ADDED))
        fid2 = resolver.process_change("aaa", 1000, FileChange("aaa", "b.py", ChangeType.ADDED))

        assert fid1 != fid2


class TestRenameFile:
    """Renaming preserves file identity."""

    def test_rename_preserves_identity(self, resolver: FileIdentityResolver) -> None:
        # Add file at old path.
        change_add = FileChange("aaa", "old.py", ChangeType.ADDED)
        fid = resolver.process_change("aaa", 1000, change_add)

        # Rename old.py -> new.py.
        change_rename = FileChange("bbb", "new.py", ChangeType.RENAMED, old_path="old.py")
        fid2 = resolver.process_change("bbb", 2000, change_rename)

        assert fid == fid2
        assert resolver.resolve("new.py") == fid
        assert resolver.resolve("old.py") is None  # old path no longer alive

    def test_rename_chain(self, resolver: FileIdentityResolver) -> None:
        """A -> B -> C should all share the same identity."""
        fid_a = resolver.process_change(
            "c1", 1000, FileChange("c1", "a.py", ChangeType.ADDED)
        )
        fid_b = resolver.process_change(
            "c2", 2000, FileChange("c2", "b.py", ChangeType.RENAMED, old_path="a.py")
        )
        fid_c = resolver.process_change(
            "c3", 3000, FileChange("c3", "c.py", ChangeType.RENAMED, old_path="b.py")
        )

        assert fid_a == fid_b == fid_c
        assert resolver.resolve("c.py") == fid_a
        assert resolver.resolve("a.py") is None
        assert resolver.resolve("b.py") is None

    def test_rename_updates_current_path(self, resolver: FileIdentityResolver) -> None:
        fid = resolver.process_change(
            "c1", 1000, FileChange("c1", "old.py", ChangeType.ADDED)
        )
        resolver.process_change(
            "c2", 2000, FileChange("c2", "new.py", ChangeType.RENAMED, old_path="old.py")
        )

        identity = resolver.get_identity(fid)
        assert identity is not None
        assert identity.current_path == "new.py"
        assert identity.birth_path == "old.py"

    def test_rename_without_prior_add(self, resolver: FileIdentityResolver) -> None:
        """Partial history: rename with no prior ADD creates retroactive identity."""
        change = FileChange("c1", "new.py", ChangeType.RENAMED, old_path="old.py")
        fid = resolver.process_change("c1", 1000, change)

        assert fid is not None
        assert resolver.resolve("new.py") == fid
        identity = resolver.get_identity(fid)
        assert identity is not None
        assert identity.birth_path == "old.py"


class TestDeleteFile:
    """Deleting marks identity as dead."""

    def test_delete_marks_dead(self, resolver: FileIdentityResolver) -> None:
        fid = resolver.process_change(
            "c1", 1000, FileChange("c1", "x.py", ChangeType.ADDED)
        )
        fid_del = resolver.process_change(
            "c2", 2000, FileChange("c2", "x.py", ChangeType.DELETED)
        )

        assert fid == fid_del
        assert resolver.resolve("x.py") is None  # no longer alive

        identity = resolver.get_identity(fid)
        assert identity is not None
        assert identity.is_alive is False
        assert identity.current_path is None

    def test_re_add_after_delete_creates_new_identity(
        self, resolver: FileIdentityResolver
    ) -> None:
        """Re-adding a path after deletion creates a NEW identity."""
        fid1 = resolver.process_change(
            "c1", 1000, FileChange("c1", "x.py", ChangeType.ADDED)
        )
        resolver.process_change("c2", 2000, FileChange("c2", "x.py", ChangeType.DELETED))

        fid2 = resolver.process_change(
            "c3", 3000, FileChange("c3", "x.py", ChangeType.ADDED)
        )

        assert fid1 != fid2
        assert resolver.resolve("x.py") == fid2


class TestModifyFile:
    """Modifying an existing file returns its identity."""

    def test_modify_returns_existing_id(self, resolver: FileIdentityResolver) -> None:
        fid = resolver.process_change(
            "c1", 1000, FileChange("c1", "m.py", ChangeType.ADDED)
        )
        fid2 = resolver.process_change(
            "c2", 2000, FileChange("c2", "m.py", ChangeType.MODIFIED)
        )

        assert fid == fid2

    def test_modify_without_add_creates_implicit(self, resolver: FileIdentityResolver) -> None:
        """Partial history: MODIFY without prior ADD -> implicit ADD."""
        fid = resolver.process_change(
            "c1", 1000, FileChange("c1", "m.py", ChangeType.MODIFIED)
        )

        assert fid is not None
        assert resolver.resolve("m.py") == fid
        identity = resolver.get_identity(fid)
        assert identity is not None
        assert identity.birth_path == "m.py"


class TestCopyFile:
    """Copying creates a new (independent) identity."""

    def test_copy_creates_new_identity(self, resolver: FileIdentityResolver) -> None:
        fid_orig = resolver.process_change(
            "c1", 1000, FileChange("c1", "orig.py", ChangeType.ADDED)
        )
        fid_copy = resolver.process_change(
            "c2", 2000, FileChange("c2", "copy.py", ChangeType.COPIED, old_path="orig.py")
        )

        assert fid_orig != fid_copy
        assert resolver.resolve("orig.py") == fid_orig
        assert resolver.resolve("copy.py") == fid_copy


# ── Query API ───────────────────────────────────────────────────────────


class TestPathHistory:
    """get_path_history returns chronological rename segments."""

    def test_no_renames(self, resolver: FileIdentityResolver) -> None:
        fid = resolver.process_change(
            "c1", 1000, FileChange("c1", "stable.py", ChangeType.ADDED)
        )

        history = resolver.get_path_history(fid)
        assert len(history) == 1
        path, valid_from, valid_until = history[0]
        assert path == "stable.py"
        assert valid_from == 1000
        assert valid_until is None

    def test_single_rename(self, resolver: FileIdentityResolver) -> None:
        fid = resolver.process_change(
            "c1", 1000, FileChange("c1", "a.py", ChangeType.ADDED)
        )
        resolver.process_change(
            "c2", 2000, FileChange("c2", "b.py", ChangeType.RENAMED, old_path="a.py")
        )

        history = resolver.get_path_history(fid)
        assert len(history) == 2

        assert history[0][0] == "a.py"
        assert history[0][1] == 1000
        assert history[0][2] == 2000  # valid_until = rename timestamp

        assert history[1][0] == "b.py"
        assert history[1][1] == 2000
        assert history[1][2] is None  # current segment

    def test_double_rename(self, resolver: FileIdentityResolver) -> None:
        fid = resolver.process_change(
            "c1", 1000, FileChange("c1", "a.py", ChangeType.ADDED)
        )
        resolver.process_change(
            "c2", 2000, FileChange("c2", "b.py", ChangeType.RENAMED, old_path="a.py")
        )
        resolver.process_change(
            "c3", 3000, FileChange("c3", "c.py", ChangeType.RENAMED, old_path="b.py")
        )

        history = resolver.get_path_history(fid)
        assert len(history) == 3
        assert [h[0] for h in history] == ["a.py", "b.py", "c.py"]

    def test_nonexistent_id(self, resolver: FileIdentityResolver) -> None:
        assert resolver.get_path_history("nonexistent-uuid") == []


class TestGetAllPaths:
    """get_all_paths returns the union of all historical paths."""

    def test_with_renames(self, resolver: FileIdentityResolver) -> None:
        fid = resolver.process_change(
            "c1", 1000, FileChange("c1", "a.py", ChangeType.ADDED)
        )
        resolver.process_change(
            "c2", 2000, FileChange("c2", "b.py", ChangeType.RENAMED, old_path="a.py")
        )

        all_paths = resolver.get_all_paths(fid)
        assert all_paths == {"a.py", "b.py"}


class TestGetCurrentPath:
    """get_current_path returns current live path or None."""

    def test_alive_file(self, resolver: FileIdentityResolver) -> None:
        fid = resolver.process_change(
            "c1", 1000, FileChange("c1", "alive.py", ChangeType.ADDED)
        )
        assert resolver.get_current_path(fid) == "alive.py"

    def test_dead_file(self, resolver: FileIdentityResolver) -> None:
        fid = resolver.process_change(
            "c1", 1000, FileChange("c1", "dead.py", ChangeType.ADDED)
        )
        resolver.process_change("c2", 2000, FileChange("c2", "dead.py", ChangeType.DELETED))
        assert resolver.get_current_path(fid) is None


class TestIterateAlive:
    """iterate_alive yields only living files."""

    def test_filters_dead(self, resolver: FileIdentityResolver) -> None:
        resolver.process_change("c1", 1000, FileChange("c1", "alive.py", ChangeType.ADDED))
        resolver.process_change("c1", 1000, FileChange("c1", "dead.py", ChangeType.ADDED))
        resolver.process_change("c2", 2000, FileChange("c2", "dead.py", ChangeType.DELETED))

        alive = list(resolver.iterate_alive())
        assert len(alive) == 1
        assert alive[0].current_path == "alive.py"
        assert alive[0].is_alive is True


class TestStats:
    """stats() returns correct counts."""

    def test_stats(self, resolver: FileIdentityResolver) -> None:
        resolver.process_change("c1", 1000, FileChange("c1", "a.py", ChangeType.ADDED))
        resolver.process_change("c1", 1000, FileChange("c1", "b.py", ChangeType.ADDED))
        resolver.process_change(
            "c2", 2000, FileChange("c2", "b2.py", ChangeType.RENAMED, old_path="b.py")
        )
        resolver.process_change("c3", 3000, FileChange("c3", "a.py", ChangeType.DELETED))

        s = resolver.stats()
        assert s["total_identities"] == 2
        assert s["alive"] == 1
        assert s["dead"] == 1
        assert s["renames"] == 1


class TestResolveAt:
    """resolve_at does historical path lookup."""

    def test_resolve_at_birth_path(self, resolver: FileIdentityResolver) -> None:
        fid = resolver.process_change(
            "c1", 1000, FileChange("c1", "a.py", ChangeType.ADDED)
        )
        resolver.commit()

        assert resolver.resolve_at("a.py", 1500) == fid

    def test_resolve_at_after_rename(self, resolver: FileIdentityResolver) -> None:
        fid = resolver.process_change(
            "c1", 1000, FileChange("c1", "a.py", ChangeType.ADDED)
        )
        resolver.process_change(
            "c2", 2000, FileChange("c2", "b.py", ChangeType.RENAMED, old_path="a.py")
        )
        resolver.commit()

        # Before rename, a.py was valid.
        assert resolver.resolve_at("a.py", 1500) == fid

        # After rename, b.py is valid.
        assert resolver.resolve_at("b.py", 2500) == fid

        # After rename, a.py should NOT resolve (it was renamed away).
        assert resolver.resolve_at("a.py", 2500) is None


class TestPersistenceReload:
    """Resolver reloads state correctly from DB."""

    def test_reload_from_db(self, conn: sqlite3.Connection) -> None:
        # Create resolver, add data, commit.
        r1 = FileIdentityResolver(conn)
        fid = r1.process_change("c1", 1000, FileChange("c1", "x.py", ChangeType.ADDED))
        r1.process_change(
            "c2", 2000, FileChange("c2", "y.py", ChangeType.RENAMED, old_path="x.py")
        )
        r1.commit()

        # Create a NEW resolver on the same connection -- should reload cache.
        r2 = FileIdentityResolver(conn)
        assert r2.resolve("y.py") == fid
        assert r2.resolve("x.py") is None

        identity = r2.get_identity(fid)
        assert identity is not None
        assert identity.current_path == "y.py"
        assert identity.birth_path == "x.py"


class TestCommit:
    """commit() persists data to the connection."""

    def test_commit_persists(self, conn: sqlite3.Connection) -> None:
        resolver = FileIdentityResolver(conn)
        resolver.process_change("c1", 1000, FileChange("c1", "f.py", ChangeType.ADDED))
        resolver.commit()

        # Verify directly via SQL.
        row = conn.execute(
            "SELECT * FROM file_identities WHERE birth_path = 'f.py'"
        ).fetchone()
        assert row is not None


class TestRenameWithoutOldPath:
    """Edge case: rename event with no old_path falls back to ADD."""

    def test_rename_no_old_path(self, resolver: FileIdentityResolver) -> None:
        change = FileChange("c1", "new.py", ChangeType.RENAMED, old_path=None)
        fid = resolver.process_change("c1", 1000, change)

        assert fid is not None
        assert resolver.resolve("new.py") == fid
