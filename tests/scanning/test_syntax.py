"""Tests for v2 FileSyntax data models."""

import pytest

from shannon_insight.scanning.syntax import (
    ClassDef,
    FileSyntax,
    FunctionDef,
    ImportDecl,
)


class TestFunctionDef:
    """Test FunctionDef dataclass."""

    def test_basic_attributes(self):
        """FunctionDef has all required attributes."""
        fn = FunctionDef(
            name="foo",
            params=["a", "b"],
            body_tokens=50,
            signature_tokens=10,
            nesting_depth=1,
            start_line=10,
            end_line=20,
        )
        assert fn.name == "foo"
        assert fn.params == ["a", "b"]
        assert fn.body_tokens == 50
        assert fn.signature_tokens == 10
        assert fn.nesting_depth == 1
        assert fn.start_line == 10
        assert fn.end_line == 20

    def test_call_targets_optional(self):
        """call_targets is None by default (regex fallback)."""
        fn = FunctionDef(
            name="foo",
            params=[],
            body_tokens=10,
            signature_tokens=5,
            nesting_depth=0,
            start_line=1,
            end_line=5,
        )
        assert fn.call_targets is None

    def test_call_targets_populated(self):
        """call_targets can be populated by tree-sitter."""
        fn = FunctionDef(
            name="foo",
            params=[],
            body_tokens=10,
            signature_tokens=5,
            nesting_depth=0,
            start_line=1,
            end_line=5,
            call_targets=["bar", "baz"],
        )
        assert fn.call_targets == ["bar", "baz"]

    def test_decorators_default_empty(self):
        """decorators defaults to empty list."""
        fn = FunctionDef(
            name="foo",
            params=[],
            body_tokens=10,
            signature_tokens=5,
            nesting_depth=0,
            start_line=1,
            end_line=5,
        )
        assert fn.decorators == []

    def test_decorators_populated(self):
        """decorators can capture @property, @abstractmethod, etc."""
        fn = FunctionDef(
            name="foo",
            params=[],
            body_tokens=10,
            signature_tokens=5,
            nesting_depth=0,
            start_line=1,
            end_line=5,
            decorators=["property", "abstractmethod"],
        )
        assert fn.decorators == ["property", "abstractmethod"]

    def test_is_stub_property(self):
        """is_stub property based on body_tokens threshold."""
        stub = FunctionDef(
            name="stub",
            params=[],
            body_tokens=2,  # < 3, definitely a stub
            signature_tokens=10,
            nesting_depth=0,
            start_line=1,
            end_line=2,
        )
        assert stub.is_stub is True

        real = FunctionDef(
            name="real",
            params=[],
            body_tokens=50,
            signature_tokens=10,
            nesting_depth=0,
            start_line=1,
            end_line=10,
        )
        assert real.is_stub is False

    def test_stub_score_property(self):
        """stub_score: empty=1.0, small=0.0, large scales by ratio."""
        # Empty body is pure stub
        empty = FunctionDef(
            name="empty",
            params=[],
            body_tokens=0,
            signature_tokens=10,
            nesting_depth=0,
            start_line=1,
            end_line=2,
        )
        assert empty.stub_score == pytest.approx(1.0)

        # Small but non-trivial body (< 10 tokens) is NOT a stub
        small = FunctionDef(
            name="small",
            params=[],
            body_tokens=8,
            signature_tokens=10,
            nesting_depth=0,
            start_line=1,
            end_line=3,
        )
        assert small.stub_score == pytest.approx(0.0)

        # Larger body with body >= signature is fully implemented
        full = FunctionDef(
            name="full",
            params=[],
            body_tokens=15,
            signature_tokens=10,
            nesting_depth=0,
            start_line=1,
            end_line=5,
        )
        assert full.stub_score == pytest.approx(0.0)


class TestClassDef:
    """Test ClassDef dataclass."""

    def test_basic_attributes(self):
        """ClassDef has all required attributes."""
        cls = ClassDef(
            name="Foo",
            bases=["Bar", "Baz"],
            methods=[],
            fields=["x", "y"],
        )
        assert cls.name == "Foo"
        assert cls.bases == ["Bar", "Baz"]
        assert cls.methods == []
        assert cls.fields == ["x", "y"]

    def test_is_abstract_default(self):
        """is_abstract defaults to False."""
        cls = ClassDef(name="Foo", bases=[], methods=[], fields=[])
        assert cls.is_abstract is False

    def test_is_abstract_true(self):
        """is_abstract can be set True."""
        cls = ClassDef(name="AbstractFoo", bases=["ABC"], methods=[], fields=[], is_abstract=True)
        assert cls.is_abstract is True


class TestImportDecl:
    """Test ImportDecl dataclass."""

    def test_basic_attributes(self):
        """ImportDecl has all required attributes."""
        imp = ImportDecl(source="os.path", names=["join", "dirname"])
        assert imp.source == "os.path"
        assert imp.names == ["join", "dirname"]

    def test_resolved_path_default(self):
        """resolved_path is None by default (phantom)."""
        imp = ImportDecl(source="some.module", names=["foo"])
        assert imp.resolved_path is None

    def test_resolved_path_populated(self):
        """resolved_path can be set."""
        imp = ImportDecl(source="mymodule", names=["thing"], resolved_path="/path/to/mymodule.py")
        assert imp.resolved_path == "/path/to/mymodule.py"

    def test_is_phantom_property(self):
        """is_phantom is True when resolved_path is None."""
        phantom = ImportDecl(source="missing", names=["foo"])
        assert phantom.is_phantom is True

        resolved = ImportDecl(source="found", names=["bar"], resolved_path="/path/to/found.py")
        assert resolved.is_phantom is False


class TestFileSyntax:
    """Test FileSyntax dataclass."""

    def test_basic_attributes(self):
        """FileSyntax has all required attributes."""
        fs = FileSyntax(
            path="/foo/bar.py",
            functions=[],
            classes=[],
            imports=[],
            language="python",
        )
        assert fs.path == "/foo/bar.py"
        assert fs.functions == []
        assert fs.classes == []
        assert fs.imports == []
        assert fs.language == "python"

    def test_has_main_guard_default(self):
        """has_main_guard defaults to False."""
        fs = FileSyntax(path="/foo.py", functions=[], classes=[], imports=[], language="python")
        assert fs.has_main_guard is False

    def test_has_main_guard_true(self):
        """has_main_guard can be set True."""
        fs = FileSyntax(
            path="/foo.py",
            functions=[],
            classes=[],
            imports=[],
            language="python",
            has_main_guard=True,
        )
        assert fs.has_main_guard is True

    def test_function_count_property(self):
        """function_count property returns len(functions)."""
        fs = FileSyntax(
            path="/foo.py",
            functions=[
                FunctionDef("a", [], 10, 5, 0, 1, 5),
                FunctionDef("b", [], 20, 5, 0, 6, 10),
            ],
            classes=[],
            imports=[],
            language="python",
        )
        assert fs.function_count == 2

    def test_class_count_property(self):
        """class_count property returns len(classes)."""
        fs = FileSyntax(
            path="/foo.py",
            functions=[],
            classes=[
                ClassDef("A", [], [], []),
                ClassDef("B", [], [], []),
                ClassDef("C", [], [], []),
            ],
            imports=[],
            language="python",
        )
        assert fs.class_count == 3

    def test_import_count_property(self):
        """import_count property returns len(imports)."""
        fs = FileSyntax(
            path="/foo.py",
            functions=[],
            classes=[],
            imports=[
                ImportDecl("os", ["path"]),
                ImportDecl("sys", []),
            ],
            language="python",
        )
        assert fs.import_count == 2

    def test_max_nesting_property(self):
        """max_nesting returns max nesting_depth across functions."""
        fs = FileSyntax(
            path="/foo.py",
            functions=[
                FunctionDef("a", [], 10, 5, 2, 1, 5),
                FunctionDef("b", [], 20, 5, 5, 6, 10),  # max nesting = 5
                FunctionDef("c", [], 15, 5, 3, 11, 15),
            ],
            classes=[],
            imports=[],
            language="python",
        )
        assert fs.max_nesting == 5

    def test_max_nesting_empty(self):
        """max_nesting returns 0 if no functions."""
        fs = FileSyntax(path="/foo.py", functions=[], classes=[], imports=[], language="python")
        assert fs.max_nesting == 0

    def test_stub_ratio_property(self):
        """stub_ratio returns mean stub_score."""
        fn1 = FunctionDef("a", [], 1, 10, 0, 1, 2)  # pure stub (body < 3, score=1.0)
        fn2 = FunctionDef("b", [], 60, 10, 0, 3, 10)  # not stub (score=0.0)
        fs = FileSyntax(
            path="/foo.py",
            functions=[fn1, fn2],
            classes=[],
            imports=[],
            language="python",
        )
        # stub_score(fn1) = 1.0 (body < 3)
        # stub_score(fn2) = 0.0 (body >= signature)
        # mean = (1.0 + 0) / 2 = 0.5
        assert fs.stub_ratio == pytest.approx(0.5)

    def test_stub_ratio_no_functions(self):
        """stub_ratio returns 0.0 if no functions."""
        fs = FileSyntax(path="/foo.py", functions=[], classes=[], imports=[], language="python")
        assert fs.stub_ratio == 0.0

    def test_impl_gini_property(self):
        """impl_gini returns Gini coefficient of body_tokens."""
        # Equal sizes: Gini should be ~0
        fs = FileSyntax(
            path="/foo.py",
            functions=[
                FunctionDef("a", [], 100, 10, 0, 1, 5),
                FunctionDef("b", [], 100, 10, 0, 6, 10),
                FunctionDef("c", [], 100, 10, 0, 11, 15),
            ],
            classes=[],
            imports=[],
            language="python",
        )
        assert fs.impl_gini == pytest.approx(0.0, abs=0.01)

    def test_impl_gini_unequal(self):
        """impl_gini is higher for unequal distributions."""
        fs = FileSyntax(
            path="/foo.py",
            functions=[
                FunctionDef("big", [], 1000, 10, 0, 1, 100),  # very large
                FunctionDef("tiny", [], 1, 10, 0, 101, 102),  # very small
            ],
            classes=[],
            imports=[],
            language="python",
        )
        assert fs.impl_gini > 0.4  # Should be significantly unequal
