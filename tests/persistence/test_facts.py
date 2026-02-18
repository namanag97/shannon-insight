"""Tests for Phase 1 fact storage.

Tests verify:
1. Fact models convert correctly from FileSyntax
2. FactDatabase stores and retrieves facts
3. Call targets are preserved (THE KEY TEST)
4. Class bases are preserved
5. Import details are preserved
6. Session tracking works
"""

import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path

import pytest

from shannon_insight.persistence.fact_models import (
    AnalysisSession,
    ClassFact,
    FileFact,
    FunctionFact,
    ImportFact,
)
from shannon_insight.persistence.facts import FactDatabase
from shannon_insight.scanning import SyntaxExtractor
from shannon_insight.scanning.syntax import ClassDef, FileSyntax, FunctionDef, ImportDecl


class TestFunctionFact:
    """Tests for FunctionFact model."""

    def test_from_function_def_basic(self):
        """Test basic conversion from FunctionDef."""
        fn = FunctionDef(
            name="test_func",
            params=["a", "b"],
            body_tokens=50,
            signature_tokens=10,
            nesting_depth=2,
            start_line=10,
            end_line=20,
            call_targets=["foo", "bar", "baz"],
            decorators=["staticmethod"],
            class_name=None,
        )
        fact = FunctionFact.from_function_def(fn, "test.py")

        assert fact.name == "test_func"
        assert fact.qualified_name == "test_func"
        assert fact.file_path == "test.py"
        assert fact.params == ["a", "b"]
        assert fact.call_targets == ["foo", "bar", "baz"]
        assert fact.decorators == ["staticmethod"]
        assert fact.is_stub is False

    def test_from_function_def_method(self):
        """Test conversion from method FunctionDef."""
        fn = FunctionDef(
            name="method",
            params=["self"],
            body_tokens=30,
            signature_tokens=5,
            nesting_depth=1,
            start_line=5,
            end_line=10,
            call_targets=["self.other", "helper"],
            decorators=["property"],
            class_name="MyClass",
        )
        fact = FunctionFact.from_function_def(fn, "test.py")

        assert fact.name == "method"
        assert fact.qualified_name == "MyClass.method"
        assert fact.class_name == "MyClass"

    def test_call_targets_preserved(self):
        """THE KEY TEST: call_targets are not lost."""
        fn = FunctionDef(
            name="func",
            params=[],
            body_tokens=100,
            signature_tokens=5,
            nesting_depth=3,
            start_line=1,
            end_line=50,
            call_targets=[
                "AnalysisStore",
                "logger",
                "capture_tensor_snapshot",
                "InsightResult",
                "validate_after_scanning",
            ],
            decorators=[],
        )
        fact = FunctionFact.from_function_def(fn, "kernel.py")

        assert fact.call_targets == [
            "AnalysisStore",
            "logger",
            "capture_tensor_snapshot",
            "InsightResult",
            "validate_after_scanning",
        ]


class TestClassFact:
    """Tests for ClassFact model."""

    def test_from_class_def(self):
        """Test conversion from ClassDef."""
        cd = ClassDef(
            name="MyClass",
            bases=["BaseClass", "Protocol"],
            methods=[],
            fields=["field1", "field2"],
            is_abstract=True,
            start_line=10,
            end_line=50,
        )
        fact = ClassFact.from_class_def(cd, "test.py")

        assert fact.name == "MyClass"
        assert fact.bases == ["BaseClass", "Protocol"]
        assert fact.is_abstract is True
        assert fact.start_line == 10
        assert fact.end_line == 50

    def test_bases_preserved(self):
        """THE KEY TEST: bases are not lost."""
        cd = ClassDef(
            name="ConcreteClass",
            bases=["ABC", "Mixin1", "Mixin2"],
            methods=[],
            fields=[],
            is_abstract=False,
            start_line=1,
            end_line=100,
        )
        fact = ClassFact.from_class_def(cd, "impl.py")

        assert fact.bases == ["ABC", "Mixin1", "Mixin2"]


class TestImportFact:
    """Tests for ImportFact model."""

    def test_from_import_decl(self):
        """Test conversion from ImportDecl."""
        imp = ImportDecl(
            source="..models",
            names=["FileFact", "FunctionFact"],
            resolved_path="persistence/fact_models.py",
            is_stdlib=False,
        )
        fact = ImportFact.from_import_decl(imp, "test.py")

        assert fact.source == "..models"
        assert fact.names == ["FileFact", "FunctionFact"]
        assert fact.resolved_path == "persistence/fact_models.py"
        assert fact.is_relative is True
        assert fact.is_phantom is False
        assert fact.is_stdlib is False


class TestFileFact:
    """Tests for FileFact model."""

    def test_from_file_syntax(self):
        """Test conversion from FileSyntax."""
        fs = FileSyntax(
            path="test.py",
            functions=[
                FunctionDef(
                    name="func1",
                    params=["x"],
                    body_tokens=20,
                    signature_tokens=5,
                    nesting_depth=1,
                    start_line=1,
                    end_line=10,
                    call_targets=["print", "len"],
                    decorators=[],
                ),
            ],
            classes=[
                ClassDef(
                    name="MyClass",
                    bases=["Base"],
                    methods=[],
                    fields=[],
                    is_abstract=False,
                    start_line=15,
                    end_line=30,
                ),
            ],
            imports=[
                ImportDecl(
                    source="os",
                    names=["path"],
                    resolved_path=None,
                    is_stdlib=True,
                ),
            ],
            language="python",
            has_main_guard=False,
            mtime=1234567890.0,
            content_hash="abc123",
            absolute_path="/full/path/test.py",
            _lines=50,
            _tokens=200,
            _complexity=2.5,
        )

        fact = FileFact.from_file_syntax(fs, "session-123", "0.8.0", "tree-sitter")

        assert fact.path == "test.py"
        assert fact.session_id == "session-123"
        assert fact.content_hash == "abc123"
        assert fact.language == "python"
        assert fact.lines == 50
        assert len(fact.functions) == 1
        assert len(fact.classes) == 1
        assert len(fact.imports) == 1
        assert fact.functions[0].call_targets == ["print", "len"]
        assert fact.classes[0].bases == ["Base"]


class TestFactDatabase:
    """Tests for FactDatabase."""

    @pytest.fixture
    def temp_db(self):
        """Create a temporary database."""
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "test_facts.db"
            yield FactDatabase(db_path)

    def test_create_session(self, temp_db):
        """Test session creation."""
        session = AnalysisSession(
            id="test-session",
            started_at=datetime.now(timezone.utc),
            completed_at=None,
            commit_sha="abc123",
            analyzed_path="/test",
            tool_version="0.8.0",
            config_hash="xyz",
            status="running",
        )
        temp_db.create_session(session)

        retrieved = temp_db.get_session("test-session")
        assert retrieved is not None
        assert retrieved.id == "test-session"
        assert retrieved.status == "running"

    def test_complete_session(self, temp_db):
        """Test session completion."""
        session = AnalysisSession(
            id="test-session",
            started_at=datetime.now(timezone.utc),
            completed_at=None,
            commit_sha=None,
            analyzed_path="/test",
            tool_version="0.8.0",
            config_hash="xyz",
            status="running",
        )
        temp_db.create_session(session)
        temp_db.complete_session("test-session", file_count=10)

        retrieved = temp_db.get_session("test-session")
        assert retrieved.status == "completed"
        assert retrieved.file_count == 10
        assert retrieved.completed_at is not None

    def test_store_file_fact(self, temp_db):
        """Test storing a file fact with all entities."""
        session_id = str(uuid.uuid4())
        session = AnalysisSession(
            id=session_id,
            started_at=datetime.now(timezone.utc),
            completed_at=None,
            commit_sha=None,
            analyzed_path="/test",
            tool_version="0.8.0",
            config_hash="xyz",
            status="running",
        )
        temp_db.create_session(session)

        fact = FileFact(
            path="test.py",
            absolute_path="/test/test.py",
            content_hash="hash123",
            session_id=session_id,
            parsed_at=datetime.now(timezone.utc),
            parser_type="tree-sitter",
            tool_version="0.8.0",
            language="python",
            lines=100,
            tokens=500,
            complexity=3.0,
            has_main_guard=False,
            mtime=1234567890.0,
            functions=[
                FunctionFact(
                    name="func1",
                    qualified_name="func1",
                    file_path="test.py",
                    start_line=1,
                    end_line=10,
                    params=["x", "y"],
                    signature_tokens=10,
                    decorators=[],
                    body_tokens=50,
                    nesting_depth=2,
                    call_targets=["print", "helper"],
                    class_name=None,
                    is_stub=False,
                    stub_score=0.0,
                ),
            ],
            classes=[
                ClassFact(
                    name="MyClass",
                    file_path="test.py",
                    start_line=15,
                    end_line=50,
                    bases=["Base"],
                    method_names=["method1"],
                    field_names=["field1"],
                    is_abstract=False,
                    method_count=1,
                ),
            ],
            imports=[
                ImportFact(
                    file_path="test.py",
                    source="os",
                    names=["path"],
                    resolved_path=None,
                    is_relative=False,
                    is_phantom=False,
                    is_stdlib=True,
                ),
            ],
            function_count=1,
            class_count=1,
            import_count=1,
            max_nesting=2,
            stub_ratio=0.0,
            impl_gini=0.0,
        )

        file_id = temp_db.store_file_fact(fact)
        assert file_id > 0

        # Retrieve and verify
        retrieved = temp_db.get_file_fact_by_path(session_id, "test.py")
        assert retrieved is not None
        assert retrieved.path == "test.py"
        assert len(retrieved.functions) == 1
        assert len(retrieved.classes) == 1
        assert len(retrieved.imports) == 1

    def test_call_targets_preserved_in_db(self, temp_db):
        """THE KEY TEST: call_targets survive round-trip to DB."""
        session_id = str(uuid.uuid4())
        session = AnalysisSession(
            id=session_id,
            started_at=datetime.now(timezone.utc),
            completed_at=None,
            commit_sha=None,
            analyzed_path="/test",
            tool_version="0.8.0",
            config_hash="xyz",
            status="running",
        )
        temp_db.create_session(session)

        # Store a function with call_targets
        fact = FileFact(
            path="kernel.py",
            absolute_path="/test/kernel.py",
            content_hash="hash456",
            session_id=session_id,
            parsed_at=datetime.now(timezone.utc),
            parser_type="tree-sitter",
            tool_version="0.8.0",
            language="python",
            lines=500,
            tokens=2000,
            complexity=5.0,
            has_main_guard=False,
            mtime=1234567890.0,
            functions=[
                FunctionFact(
                    name="run",
                    qualified_name="InsightKernel.run",
                    file_path="kernel.py",
                    start_line=86,
                    end_line=332,
                    params=["self", "max_findings", "on_progress"],
                    signature_tokens=15,
                    decorators=[],
                    body_tokens=727,
                    nesting_depth=4,
                    call_targets=[
                        "AnalysisStore",
                        "logger",
                        "capture_tensor_snapshot",
                        "InsightResult",
                        "StoreSummary",
                        "validate_after_scanning",
                    ],
                    class_name="InsightKernel",
                    is_stub=False,
                    stub_score=0.0,
                ),
            ],
            classes=[],
            imports=[],
            function_count=1,
            class_count=0,
            import_count=0,
            max_nesting=4,
            stub_ratio=0.0,
            impl_gini=0.0,
        )

        temp_db.store_file_fact(fact)

        # Retrieve call targets
        call_targets = temp_db.get_call_targets_for_session(session_id)

        assert "InsightKernel.run" in call_targets
        assert call_targets["InsightKernel.run"] == [
            "AnalysisStore",
            "logger",
            "capture_tensor_snapshot",
            "InsightResult",
            "StoreSummary",
            "validate_after_scanning",
        ]

    def test_class_bases_preserved_in_db(self, temp_db):
        """THE KEY TEST: class bases survive round-trip to DB."""
        session_id = str(uuid.uuid4())
        session = AnalysisSession(
            id=session_id,
            started_at=datetime.now(timezone.utc),
            completed_at=None,
            commit_sha=None,
            analyzed_path="/test",
            tool_version="0.8.0",
            config_hash="xyz",
            status="running",
        )
        temp_db.create_session(session)

        fact = FileFact(
            path="models.py",
            absolute_path="/test/models.py",
            content_hash="hash789",
            session_id=session_id,
            parsed_at=datetime.now(timezone.utc),
            parser_type="tree-sitter",
            tool_version="0.8.0",
            language="python",
            lines=200,
            tokens=800,
            complexity=2.0,
            has_main_guard=False,
            mtime=1234567890.0,
            functions=[],
            classes=[
                ClassFact(
                    name="Finding",
                    file_path="models.py",
                    start_line=10,
                    end_line=50,
                    bases=["BaseModel", "Serializable"],
                    method_names=["to_dict", "from_dict"],
                    field_names=["severity", "title"],
                    is_abstract=False,
                    method_count=2,
                ),
            ],
            imports=[],
            function_count=0,
            class_count=1,
            import_count=0,
            max_nesting=0,
            stub_ratio=0.0,
            impl_gini=0.0,
        )

        temp_db.store_file_fact(fact)

        # Retrieve class bases
        bases = temp_db.get_class_bases_for_session(session_id)

        assert "models.py:Finding" in bases
        assert bases["models.py:Finding"] == ["BaseModel", "Serializable"]

    def test_session_stats(self, temp_db):
        """Test session statistics."""
        session_id = str(uuid.uuid4())
        session = AnalysisSession(
            id=session_id,
            started_at=datetime.now(timezone.utc),
            completed_at=None,
            commit_sha=None,
            analyzed_path="/test",
            tool_version="0.8.0",
            config_hash="xyz",
            status="running",
        )
        temp_db.create_session(session)

        # Store multiple facts
        for i in range(3):
            fact = FileFact(
                path=f"file{i}.py",
                absolute_path=f"/test/file{i}.py",
                content_hash=f"hash{i}",
                session_id=session_id,
                parsed_at=datetime.now(timezone.utc),
                parser_type="tree-sitter",
                tool_version="0.8.0",
                language="python",
                lines=50,
                tokens=200,
                complexity=2.0,
                has_main_guard=False,
                mtime=1234567890.0,
                functions=[
                    FunctionFact(
                        name=f"func{i}",
                        qualified_name=f"func{i}",
                        file_path=f"file{i}.py",
                        start_line=1,
                        end_line=10,
                        params=[],
                        signature_tokens=5,
                        decorators=[],
                        body_tokens=20,
                        nesting_depth=1,
                        call_targets=[],
                        class_name=None,
                        is_stub=False,
                        stub_score=0.0,
                    ),
                ],
                classes=[],
                imports=[
                    ImportFact(
                        file_path=f"file{i}.py",
                        source="os",
                        names=[],
                        resolved_path=None,
                        is_relative=False,
                        is_phantom=False,
                        is_stdlib=True,
                    ),
                ],
                function_count=1,
                class_count=0,
                import_count=1,
                max_nesting=1,
                stub_ratio=0.0,
                impl_gini=0.0,
            )
            temp_db.store_file_fact(fact)

        stats = temp_db.get_session_stats(session_id)

        assert stats["file_count"] == 3
        assert stats["function_count"] == 3
        assert stats["import_count"] == 3


class TestIntegrationWithSyntaxExtractor:
    """Integration tests with real file parsing."""

    def test_real_file_parsing_preserves_call_targets(self):
        """Test that real file parsing + fact storage preserves call_targets."""
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "facts.db"
            db = FactDatabase(db_path)

            # Parse actual source files
            extractor = SyntaxExtractor()
            root = Path("src/shannon_insight")
            files = list(root.rglob("*.py"))[:5]
            syntax_map = extractor.extract_all(files, root)

            # Create session and store facts
            session_id = str(uuid.uuid4())
            session = AnalysisSession(
                id=session_id,
                started_at=datetime.now(timezone.utc),
                completed_at=None,
                commit_sha=None,
                analyzed_path=str(root),
                tool_version="0.8.0",
                config_hash="test",
                status="running",
            )
            db.create_session(session)

            # Store facts
            for fs in syntax_map.values():
                parser_type = "tree-sitter" if fs.functions and fs.functions[0].call_targets is not None else "regex"
                fact = FileFact.from_file_syntax(fs, session_id, "0.8.0", parser_type)
                db.store_file_fact(fact)

            db.complete_session(session_id, len(syntax_map))

            # Verify call_targets are preserved
            call_targets = db.get_call_targets_for_session(session_id)

            # Should have call targets from tree-sitter parsed functions
            assert len(call_targets) > 0

            # At least some functions should have non-empty call targets
            has_calls = any(len(targets) > 0 for targets in call_targets.values())
            assert has_calls, "Expected at least some functions to have call_targets"
