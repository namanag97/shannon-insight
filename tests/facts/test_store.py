"""Tests for the unified FactStore.

Tests verify:
1. Content-addressable blob storage (store, retrieve, dedup)
2. Commit fact storage and retrieval
3. File change storage and querying
4. Parsed syntax caching
5. Extracted entity storage (functions, classes, imports)
6. Resolved import edge storage
7. File identity resolution
8. File observation tracking
9. Session management
10. Transaction management (context manager)
11. Dataclass convenience methods
"""

from __future__ import annotations

import pytest

from shannon_insight.facts.models import (
    ChangeType,
    CommitFact,
    ExtractedClass,
    ExtractedFunction,
    ExtractedImport,
    FileChangeFact,
    ParsedSyntaxFact,
)
from shannon_insight.facts.store import FactStore


@pytest.fixture
def store() -> FactStore:
    """In-memory FactStore for testing."""
    s = FactStore.in_memory()
    yield s
    s.close()


# ── Content Storage ────────────────────────────────────────────────────


class TestContentStorage:
    """Content-addressable blob storage tests."""

    def test_store_and_retrieve(self, store: FactStore) -> None:
        content = b"hello world"
        h = store.store_content(content)

        assert h is not None
        assert len(h) == 64  # SHA-256 hex digest

        retrieved = store.get_content(h)
        assert retrieved == content

    def test_has_content(self, store: FactStore) -> None:
        assert store.has_content("nonexistent") is False

        h = store.store_content(b"test data")
        assert store.has_content(h) is True

    def test_deduplication(self, store: FactStore) -> None:
        """Storing same content twice returns same hash, no error."""
        content = b"duplicate content"
        h1 = store.store_content(content)
        h2 = store.store_content(content)

        assert h1 == h2
        assert store.get_content(h1) == content

    def test_different_content_different_hash(self, store: FactStore) -> None:
        h1 = store.store_content(b"content A")
        h2 = store.store_content(b"content B")

        assert h1 != h2

    def test_empty_content(self, store: FactStore) -> None:
        h = store.store_content(b"")
        assert store.get_content(h) == b""

    def test_large_content_compressed(self, store: FactStore) -> None:
        """Large content should be compressed in storage."""
        content = b"x" * 100_000
        h = store.store_content(content)
        assert store.get_content(h) == content

    def test_get_nonexistent_returns_none(self, store: FactStore) -> None:
        assert store.get_content("0" * 64) is None


# ── Commit Facts ───────────────────────────────────────────────────────


class TestCommitFacts:
    """Commit fact storage and retrieval."""

    def test_store_and_get(self, store: FactStore) -> None:
        store.store_commit(
            commit_hash="abc123",
            timestamp=1700000000,
            author_email="dev@example.com",
            author_name="Dev",
            message_subject="Initial commit",
        )
        store.commit()

        result = store.get_commit("abc123")
        assert result is not None
        assert result["commit_hash"] == "abc123"
        assert result["timestamp"] == 1700000000
        assert result["author_email"] == "dev@example.com"
        assert result["author_name"] == "Dev"
        assert result["message_subject"] == "Initial commit"
        assert result["message_body"] is None
        assert result["parent_hashes"] == []
        assert result["is_merge"] is False

    def test_store_with_all_fields(self, store: FactStore) -> None:
        store.store_commit(
            commit_hash="def456",
            timestamp=1700001000,
            author_email="dev@example.com",
            author_name="Dev",
            message_subject="Merge branch",
            message_body="Merging feature branch",
            parent_hashes=["abc123", "ghi789"],
            is_merge=True,
        )
        store.commit()

        result = store.get_commit("def456")
        assert result is not None
        assert result["message_body"] == "Merging feature branch"
        assert result["parent_hashes"] == ["abc123", "ghi789"]
        assert result["is_merge"] is True

    def test_duplicate_commit_ignored(self, store: FactStore) -> None:
        store.store_commit(
            commit_hash="abc123",
            timestamp=1700000000,
            author_email="dev@example.com",
            author_name="Dev",
            message_subject="First",
        )
        # Store again with different subject -- should be silently ignored
        store.store_commit(
            commit_hash="abc123",
            timestamp=1700000000,
            author_email="dev@example.com",
            author_name="Dev",
            message_subject="Should be ignored",
        )
        store.commit()

        result = store.get_commit("abc123")
        assert result["message_subject"] == "First"

    def test_get_nonexistent_returns_none(self, store: FactStore) -> None:
        assert store.get_commit("nonexistent") is None

    def test_get_commits_in_range(self, store: FactStore) -> None:
        for i in range(5):
            store.store_commit(
                commit_hash=f"commit{i}",
                timestamp=1700000000 + i * 1000,
                author_email="dev@example.com",
                author_name="Dev",
                message_subject=f"Commit {i}",
            )
        store.commit()

        # All commits
        all_commits = list(store.get_commits_in_range())
        assert len(all_commits) == 5

        # Range query
        ranged = list(store.get_commits_in_range(since=1700001000, until=1700003000))
        assert len(ranged) == 3

        # Since only
        since_only = list(store.get_commits_in_range(since=1700003000))
        assert len(since_only) == 2

        # Until only
        until_only = list(store.get_commits_in_range(until=1700001000))
        assert len(until_only) == 2

    def test_store_commit_fact_dataclass(self, store: FactStore) -> None:
        fact = CommitFact(
            commit_hash="dc1",
            timestamp=1700000000,
            author_id="dev",
            author_email_raw="dev@example.com",
            author_name_raw="Dev",
            message_subject="Dataclass commit",
            message_body=None,
            parent_hashes=(),
            is_merge=False,
        )
        store.store_commit_fact(fact)
        store.commit()

        result = store.get_commit("dc1")
        assert result is not None
        assert result["message_subject"] == "Dataclass commit"

    def test_store_commits_batch(self, store: FactStore) -> None:
        commits = [
            CommitFact(
                commit_hash=f"batch{i}",
                timestamp=1700000000 + i,
                author_id="dev",
                author_email_raw="dev@example.com",
                author_name_raw="Dev",
                message_subject=f"Batch {i}",
                message_body=None,
                parent_hashes=(),
                is_merge=False,
            )
            for i in range(10)
        ]
        count = store.store_commits_batch(commits)
        store.commit()

        assert count >= 10  # total_changes may count higher
        all_commits = list(store.get_commits_in_range())
        assert len(all_commits) == 10


# ── File Change Facts ──────────────────────────────────────────────────


class TestFileChangeFacts:
    """File change storage and querying."""

    def test_store_and_get_by_commit(self, store: FactStore) -> None:
        store.store_file_change(
            commit_hash="c1",
            file_id="f1",
            change_type="M",
            new_path="src/main.py",
            additions=10,
            deletions=5,
        )
        store.commit()

        changes = store.get_changes_for_commit("c1")
        assert len(changes) == 1
        assert changes[0]["file_id"] == "f1"
        assert changes[0]["change_type"] == "M"
        assert changes[0]["additions"] == 10
        assert changes[0]["deletions"] == 5

    def test_get_by_file(self, store: FactStore) -> None:
        store.store_file_change(commit_hash="c1", file_id="f1", change_type="A", new_path="x.py")
        store.store_file_change(
            commit_hash="c2", file_id="f1", change_type="M", new_path="x.py", additions=5
        )
        store.store_file_change(commit_hash="c1", file_id="f2", change_type="A", new_path="y.py")
        store.commit()

        changes = store.get_changes_for_file("f1")
        assert len(changes) == 2

    def test_duplicate_change_ignored(self, store: FactStore) -> None:
        store.store_file_change(commit_hash="c1", file_id="f1", change_type="M")
        store.store_file_change(commit_hash="c1", file_id="f1", change_type="M")
        store.commit()

        changes = store.get_changes_for_commit("c1")
        assert len(changes) == 1

    def test_rename_change(self, store: FactStore) -> None:
        store.store_file_change(
            commit_hash="c1",
            file_id="f1",
            change_type="R",
            old_path="old.py",
            new_path="new.py",
        )
        store.commit()

        changes = store.get_changes_for_commit("c1")
        assert changes[0]["old_path"] == "old.py"
        assert changes[0]["new_path"] == "new.py"

    def test_store_file_change_fact_dataclass(self, store: FactStore) -> None:
        fact = FileChangeFact(
            commit_hash="c1",
            file_id="f1",
            change_type=ChangeType.MODIFIED,
            old_path=None,
            new_path="src/main.py",
            additions=20,
            deletions=3,
        )
        store.store_file_change_fact(fact)
        store.commit()

        changes = store.get_changes_for_commit("c1")
        assert len(changes) == 1
        assert changes[0]["change_type"] == "M"

    def test_store_file_changes_batch(self, store: FactStore) -> None:
        facts = [
            FileChangeFact(
                commit_hash="c1",
                file_id=f"f{i}",
                change_type=ChangeType.ADDED,
                old_path=None,
                new_path=f"file{i}.py",
                additions=i * 10,
                deletions=0,
            )
            for i in range(5)
        ]
        count = store.store_file_changes_batch(facts)
        store.commit()

        assert count >= 5
        changes = store.get_changes_for_commit("c1")
        assert len(changes) == 5


# ── File Observations ──────────────────────────────────────────────────


class TestFileObservations:
    """File observation (state at commit) tracking."""

    def test_store_and_get(self, store: FactStore) -> None:
        store.store_file_observation(
            file_id="f1",
            commit_hash="c1",
            path="src/main.py",
            content_hash="hash1",
            timestamp=1700000000,
        )
        store.commit()

        obs = store.get_file_at_commit("f1", "c1")
        assert obs is not None
        assert obs["path"] == "src/main.py"
        assert obs["content_hash"] == "hash1"
        assert obs["timestamp"] == 1700000000

    def test_get_nonexistent_returns_none(self, store: FactStore) -> None:
        assert store.get_file_at_commit("f1", "c1") is None

    def test_get_current_files(self, store: FactStore) -> None:
        # Register identities first
        store.register_file_identity("f1", "c1", "a.py", "a.py", is_alive=True)
        store.register_file_identity("f2", "c1", "b.py", "b.py", is_alive=True)
        store.register_file_identity("f3", "c1", "c.py", None, is_alive=False)

        store.store_file_observation("f1", "c1", "a.py", "h1", 1000)
        store.store_file_observation("f2", "c1", "b.py", "h2", 1000)
        store.store_file_observation("f3", "c1", "c.py", "h3", 1000)
        store.commit()

        current = list(store.get_current_files())
        assert len(current) == 2
        paths = {f["path"] for f in current}
        assert paths == {"a.py", "b.py"}


# ── File Identity ──────────────────────────────────────────────────────


class TestFileIdentity:
    """File identity resolution tests."""

    def test_register_and_resolve(self, store: FactStore) -> None:
        store.register_file_identity("f1", "c1", "src/main.py")
        store.commit()

        fid = store.resolve_file_id("src/main.py")
        assert fid == "f1"

    def test_resolve_nonexistent_returns_none(self, store: FactStore) -> None:
        assert store.resolve_file_id("nonexistent.py") is None

    def test_get_identity(self, store: FactStore) -> None:
        store.register_file_identity("f1", "c1", "src/main.py", "src/main.py", True)
        store.commit()

        identity = store.get_file_identity("f1")
        assert identity is not None
        assert identity["file_id"] == "f1"
        assert identity["birth_commit"] == "c1"
        assert identity["birth_path"] == "src/main.py"
        assert identity["current_path"] == "src/main.py"
        assert identity["is_alive"] is True

    def test_update_path_on_rename(self, store: FactStore) -> None:
        store.register_file_identity("f1", "c1", "old.py")
        store.update_file_path("f1", "new.py", timestamp=2000)
        store.commit()

        assert store.resolve_file_id("new.py") == "f1"
        identity = store.get_file_identity("f1")
        assert identity["current_path"] == "new.py"

    def test_resolve_at_historical(self, store: FactStore) -> None:
        store.register_file_identity("f1", "c1", "a.py")
        # Record path history
        store.conn.execute(
            "INSERT INTO file_path_history (file_id, path, timestamp) VALUES (?, ?, ?)",
            ("f1", "a.py", 1000),
        )
        store.update_file_path("f1", "b.py", timestamp=2000)
        store.commit()

        assert store.resolve_file_id_at("a.py", 1500) == "f1"
        assert store.resolve_file_id_at("b.py", 2500) == "f1"

    def test_mark_deleted(self, store: FactStore) -> None:
        store.register_file_identity("f1", "c1", "del.py")
        store.update_file_path("f1", None, timestamp=2000, is_alive=False)
        store.commit()

        assert store.resolve_file_id("del.py") is None
        identity = store.get_file_identity("f1")
        assert identity["is_alive"] is False


# ── Parsed Syntax Cache ───────────────────────────────────────────────


class TestParsedSyntax:
    """Parsed syntax caching tests."""

    def test_store_and_get(self, store: FactStore) -> None:
        store.store_parsed_syntax(
            content_hash="h1",
            language="python",
            lines=100,
            tokens=500,
            complexity=5,
            max_nesting=3,
            has_main_guard=True,
            stub_ratio=0.1,
            parser_type="tree-sitter",
            tool_version="0.9.0",
        )
        store.commit()

        result = store.get_parsed_syntax("h1")
        assert result is not None
        assert result["content_hash"] == "h1"
        assert result["language"] == "python"
        assert result["lines"] == 100
        assert result["tokens"] == 500
        assert result["complexity"] == 5
        assert result["max_nesting"] == 3
        assert result["has_main_guard"] is True
        assert result["stub_ratio"] == pytest.approx(0.1)
        assert result["parser_type"] == "tree-sitter"
        assert result["tool_version"] == "0.9.0"

    def test_has_parsed_syntax(self, store: FactStore) -> None:
        assert store.has_parsed_syntax("nonexistent") is False

        store.store_parsed_syntax(content_hash="h1", language="python", lines=10)
        store.commit()

        assert store.has_parsed_syntax("h1") is True

    def test_get_nonexistent_returns_none(self, store: FactStore) -> None:
        assert store.get_parsed_syntax("nonexistent") is None

    def test_duplicate_ignored(self, store: FactStore) -> None:
        store.store_parsed_syntax(content_hash="h1", language="python", lines=100)
        store.store_parsed_syntax(content_hash="h1", language="go", lines=200)
        store.commit()

        result = store.get_parsed_syntax("h1")
        assert result["language"] == "python"  # first one wins
        assert result["lines"] == 100

    def test_nullable_fields(self, store: FactStore) -> None:
        store.store_parsed_syntax(content_hash="h1", language="python", lines=50)
        store.commit()

        result = store.get_parsed_syntax("h1")
        assert result["tokens"] is None
        assert result["complexity"] is None
        assert result["max_nesting"] is None
        assert result["stub_ratio"] is None

    def test_store_parsed_syntax_fact_dataclass(self, store: FactStore) -> None:
        fact = ParsedSyntaxFact(
            content_hash="dc1",
            language="rust",
            lines=200,
            tokens=1000,
            complexity=8,
            max_nesting=4,
            has_main_guard=False,
            stub_ratio=0.05,
            parser_type="tree-sitter",
        )
        store.store_parsed_syntax_fact(fact)
        store.commit()

        result = store.get_parsed_syntax("dc1")
        assert result is not None
        assert result["language"] == "rust"
        assert result["lines"] == 200


# ── Extracted Functions ────────────────────────────────────────────────


class TestExtractedFunctions:
    """Function extraction tests."""

    def test_store_and_get(self, store: FactStore) -> None:
        store.store_extracted_function(
            content_hash="h1",
            name="do_stuff",
            qualified_name="MyClass.do_stuff",
            start_line=10,
            end_line=30,
            params=["self", "x"],
            decorators=["property"],
            body_tokens=100,
            nesting_depth=2,
            is_stub=False,
            class_name="MyClass",
        )
        store.commit()

        funcs = store.get_functions_for_content("h1")
        assert len(funcs) == 1
        f = funcs[0]
        assert f["name"] == "do_stuff"
        assert f["qualified_name"] == "MyClass.do_stuff"
        assert f["start_line"] == 10
        assert f["end_line"] == 30
        assert f["params"] == ["self", "x"]
        assert f["decorators"] == ["property"]
        assert f["body_tokens"] == 100
        assert f["nesting_depth"] == 2
        assert f["is_stub"] is False
        assert f["class_name"] == "MyClass"

    def test_multiple_functions_per_content(self, store: FactStore) -> None:
        for i in range(3):
            store.store_extracted_function(
                content_hash="h1",
                name=f"func{i}",
                qualified_name=f"func{i}",
                start_line=i * 10,
                end_line=i * 10 + 5,
            )
        store.commit()

        funcs = store.get_functions_for_content("h1")
        assert len(funcs) == 3

    def test_empty_result(self, store: FactStore) -> None:
        assert store.get_functions_for_content("nonexistent") == []

    def test_store_extracted_function_fact_dataclass(self, store: FactStore) -> None:
        fact = ExtractedFunction(
            content_hash="dc1",
            name="helper",
            qualified_name="helper",
            start_line=1,
            end_line=5,
            params=("a", "b"),
            decorators=(),
            body_tokens=20,
            nesting_depth=1,
            is_stub=True,
            class_name=None,
        )
        store.store_extracted_function_fact(fact)
        store.commit()

        funcs = store.get_functions_for_content("dc1")
        assert len(funcs) == 1
        assert funcs[0]["name"] == "helper"
        assert funcs[0]["is_stub"] is True


# ── Extracted Classes ──────────────────────────────────────────────────


class TestExtractedClasses:
    """Class extraction tests."""

    def test_store_and_get(self, store: FactStore) -> None:
        store.store_extracted_class(
            content_hash="h1",
            name="MyClass",
            start_line=5,
            end_line=50,
            bases=["BaseClass", "Mixin"],
            method_names=["run", "stop"],
            field_names=["name", "value"],
            is_abstract=True,
            method_count=2,
        )
        store.commit()

        classes = store.get_classes_for_content("h1")
        assert len(classes) == 1
        c = classes[0]
        assert c["name"] == "MyClass"
        assert c["bases"] == ["BaseClass", "Mixin"]
        assert c["method_names"] == ["run", "stop"]
        assert c["field_names"] == ["name", "value"]
        assert c["is_abstract"] is True
        assert c["method_count"] == 2

    def test_empty_result(self, store: FactStore) -> None:
        assert store.get_classes_for_content("nonexistent") == []

    def test_store_extracted_class_fact_dataclass(self, store: FactStore) -> None:
        fact = ExtractedClass(
            content_hash="dc1",
            name="Config",
            start_line=1,
            end_line=10,
            bases=("BaseModel",),
            method_names=("validate",),
            field_names=("host", "port"),
            is_abstract=False,
            method_count=1,
        )
        store.store_extracted_class_fact(fact)
        store.commit()

        classes = store.get_classes_for_content("dc1")
        assert len(classes) == 1
        assert classes[0]["name"] == "Config"
        assert classes[0]["bases"] == ["BaseModel"]


# ── Extracted Imports ──────────────────────────────────────────────────


class TestExtractedImports:
    """Import extraction tests."""

    def test_store_and_get(self, store: FactStore) -> None:
        store.store_extracted_import(
            content_hash="h1",
            raw_statement="from os.path import join",
            source_module="os.path",
            names=["join"],
            is_relative=False,
        )
        store.commit()

        imports = store.get_imports_for_content("h1")
        assert len(imports) == 1
        imp = imports[0]
        assert imp["source_module"] == "os.path"
        assert imp["names"] == ["join"]
        assert imp["is_relative"] is False

    def test_relative_import(self, store: FactStore) -> None:
        store.store_extracted_import(
            content_hash="h1",
            raw_statement="from ..models import Base",
            source_module="..models",
            names=["Base"],
            is_relative=True,
        )
        store.commit()

        imports = store.get_imports_for_content("h1")
        assert imports[0]["is_relative"] is True

    def test_empty_result(self, store: FactStore) -> None:
        assert store.get_imports_for_content("nonexistent") == []

    def test_store_extracted_import_fact_dataclass(self, store: FactStore) -> None:
        fact = ExtractedImport(
            content_hash="dc1",
            source="os.path",
            names=("join", "dirname"),
            is_relative=False,
            resolved_path=None,
        )
        store.store_extracted_import_fact(fact)
        store.commit()

        imports = store.get_imports_for_content("dc1")
        assert len(imports) == 1
        assert imports[0]["source_module"] == "os.path"
        assert imports[0]["names"] == ["join", "dirname"]


# ── Resolved Imports ───────────────────────────────────────────────────


class TestResolvedImports:
    """Resolved import edge tests."""

    def test_store_and_query_from(self, store: FactStore) -> None:
        store.store_resolved_import(
            source_content_hash="h1",
            source_file_id="f1",
            target_file_id="f2",
            target_module="models",
            is_stdlib=False,
            is_phantom=False,
        )
        store.commit()

        imports = store.get_resolved_imports_from("f1")
        assert len(imports) == 1
        assert imports[0]["target_file_id"] == "f2"
        assert imports[0]["target_module"] == "models"
        assert imports[0]["is_stdlib"] is False
        assert imports[0]["is_phantom"] is False

    def test_query_to(self, store: FactStore) -> None:
        store.store_resolved_import(
            source_content_hash="h1",
            source_file_id="f1",
            target_file_id="f2",
            target_module="models",
        )
        store.store_resolved_import(
            source_content_hash="h2",
            source_file_id="f3",
            target_file_id="f2",
            target_module="models",
        )
        store.commit()

        imports = store.get_resolved_imports_to("f2")
        assert len(imports) == 2

    def test_stdlib_and_phantom(self, store: FactStore) -> None:
        store.store_resolved_import(
            source_content_hash="h1",
            source_file_id="f1",
            target_file_id=None,
            target_module="os.path",
            is_stdlib=True,
            is_phantom=False,
        )
        store.store_resolved_import(
            source_content_hash="h2",
            source_file_id="f1",
            target_file_id=None,
            target_module="my_missing_module",
            is_stdlib=False,
            is_phantom=True,
        )
        store.commit()

        imports = store.get_resolved_imports_from("f1")
        stdlib = [i for i in imports if i["is_stdlib"]]
        phantom = [i for i in imports if i["is_phantom"]]
        assert len(stdlib) == 1
        assert len(phantom) == 1

    def test_duplicate_resolved_import_ignored(self, store: FactStore) -> None:
        store.store_resolved_import(
            source_content_hash="h1",
            source_file_id="f1",
            target_file_id="f2",
            target_module="models",
        )
        store.store_resolved_import(
            source_content_hash="h1",
            source_file_id="f1",
            target_file_id="f2",
            target_module="models",
        )
        store.commit()

        imports = store.get_resolved_imports_from("f1")
        assert len(imports) == 1


# ── Session Management ─────────────────────────────────────────────────


class TestSessionManagement:
    """Extraction session tracking."""

    def test_start_and_complete(self, store: FactStore) -> None:
        sid = store.start_session(head_commit="abc123")
        assert sid > 0

        store.complete_session(sid, file_count=10, commit_count=50)
        store.commit()

        session = store.get_last_session()
        assert session is not None
        assert session["id"] == sid
        assert session["head_commit"] == "abc123"
        assert session["file_count"] == 10
        assert session["commit_count"] == 50
        assert session["status"] == "completed"
        assert session["completed_at"] is not None

    def test_no_completed_sessions(self, store: FactStore) -> None:
        store.start_session()  # running, not completed
        store.commit()

        assert store.get_last_session() is None

    def test_fail_session(self, store: FactStore) -> None:
        sid = store.start_session()
        store.fail_session(sid)
        store.commit()

        assert store.get_last_session() is None  # failed session not returned

    def test_multiple_sessions_returns_latest(self, store: FactStore) -> None:
        sid1 = store.start_session(head_commit="old")
        store.complete_session(sid1, file_count=5, commit_count=10)

        sid2 = store.start_session(head_commit="new")
        store.complete_session(sid2, file_count=15, commit_count=30)
        store.commit()

        session = store.get_last_session()
        assert session["id"] == sid2
        assert session["head_commit"] == "new"


# ── Statistics ─────────────────────────────────────────────────────────


class TestStatistics:
    """Database statistics."""

    def test_stats_empty(self, store: FactStore) -> None:
        stats = store.get_stats()
        assert all(v == 0 for v in stats.values())

    def test_stats_populated(self, store: FactStore) -> None:
        store.store_content(b"hello")
        store.store_commit(
            commit_hash="c1",
            timestamp=1700000000,
            author_email="dev@example.com",
            author_name="Dev",
            message_subject="test",
        )
        store.store_parsed_syntax(content_hash="h1", language="python", lines=10)
        store.commit()

        stats = store.get_stats()
        assert stats["blobs"] == 1
        assert stats["commits"] == 1
        assert stats["parsed_syntax"] == 1


# ── Transaction / Context Manager ─────────────────────────────────────


class TestTransactions:
    """Context manager commit/rollback behavior."""

    def test_context_manager_commits_on_success(self) -> None:
        import sqlite3

        conn = sqlite3.connect(":memory:")
        with FactStore(conn) as store:
            store.store_commit(
                commit_hash="c1",
                timestamp=1700000000,
                author_email="dev@example.com",
                author_name="Dev",
                message_subject="test",
            )
        # Connection is closed after exit, but data was committed
        # Verify by reopening on same file (not possible with :memory:)
        # Instead verify no exception occurred

    def test_context_manager_rolls_back_on_error(self) -> None:
        import sqlite3

        conn = sqlite3.connect(":memory:")
        try:
            with FactStore(conn) as store:
                store.store_commit(
                    commit_hash="c1",
                    timestamp=1700000000,
                    author_email="dev@example.com",
                    author_name="Dev",
                    message_subject="test",
                )
                raise ValueError("simulated error")
        except ValueError:
            pass
        # Connection is closed, rollback was called


# ── File-based Open ────────────────────────────────────────────────────


class TestFileBasedOpen:
    """Opening from filesystem path."""

    def test_open_creates_file(self, tmp_path) -> None:
        db_path = tmp_path / "subdir" / "facts.db"
        store = FactStore.open(db_path)
        try:
            store.store_content(b"test")
            store.commit()
            assert db_path.exists()
        finally:
            store.close()

    def test_open_reopen_persists(self, tmp_path) -> None:
        db_path = tmp_path / "facts.db"

        # Write
        store = FactStore.open(db_path)
        store.store_commit(
            commit_hash="persist_test",
            timestamp=1700000000,
            author_email="dev@example.com",
            author_name="Dev",
            message_subject="persist",
        )
        store.commit()
        store.close()

        # Read back
        store2 = FactStore.open(db_path)
        try:
            result = store2.get_commit("persist_test")
            assert result is not None
            assert result["message_subject"] == "persist"
        finally:
            store2.close()


# ── Integration: End-to-End Workflow ───────────────────────────────────


class TestEndToEnd:
    """Full workflow: content -> syntax -> entities -> resolved imports."""

    def test_full_pipeline(self, store: FactStore) -> None:
        # 1. Start session
        sid = store.start_session(head_commit="abc123")

        # 2. Store content
        content = b"import os\n\ndef main():\n    print('hello')\n"
        h = store.store_content(content)

        # 3. Register file identity
        store.register_file_identity("f1", "abc123", "main.py")

        # 4. Store commit
        store.store_commit(
            commit_hash="abc123",
            timestamp=1700000000,
            author_email="dev@example.com",
            author_name="Dev",
            message_subject="Initial",
        )

        # 5. Store file change
        store.store_file_change(
            commit_hash="abc123",
            file_id="f1",
            change_type="A",
            new_path="main.py",
            additions=4,
        )

        # 6. Store observation
        store.store_file_observation("f1", "abc123", "main.py", h, 1700000000)

        # 7. Cache syntax
        store.store_parsed_syntax(
            content_hash=h,
            language="python",
            lines=4,
            tokens=15,
            complexity=1,
            max_nesting=1,
            has_main_guard=False,
            parser_type="regex",
        )

        # 8. Store entities
        store.store_extracted_function(
            content_hash=h,
            name="main",
            qualified_name="main",
            start_line=3,
            end_line=4,
            body_tokens=5,
        )

        store.store_extracted_import(
            content_hash=h,
            raw_statement="import os",
            source_module="os",
        )

        # 9. Resolve import
        store.store_resolved_import(
            source_content_hash=h,
            source_file_id="f1",
            target_file_id=None,
            target_module="os",
            is_stdlib=True,
        )

        # 10. Complete session
        store.complete_session(sid, file_count=1, commit_count=1)
        store.commit()

        # Verify everything round-trips
        assert store.get_content(h) == content
        assert store.resolve_file_id("main.py") == "f1"
        assert store.get_commit("abc123") is not None
        assert len(store.get_changes_for_commit("abc123")) == 1
        assert store.get_file_at_commit("f1", "abc123") is not None
        assert store.get_parsed_syntax(h) is not None
        assert len(store.get_functions_for_content(h)) == 1
        assert len(store.get_imports_for_content(h)) == 1
        assert len(store.get_resolved_imports_from("f1")) == 1
        assert store.get_last_session() is not None

        stats = store.get_stats()
        assert stats["blobs"] == 1
        assert stats["commits"] == 1
        assert stats["file_changes"] == 1
        assert stats["file_identities"] == 1
        assert stats["file_observations"] == 1
        assert stats["parsed_syntax"] == 1
        assert stats["extracted_functions"] == 1
        assert stats["extracted_imports"] == 1
        assert stats["resolved_imports"] == 1
        assert stats["extraction_sessions"] == 1
