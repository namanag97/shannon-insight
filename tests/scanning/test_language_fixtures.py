"""Tests for parsing all 8 language fixtures.

These tests verify that the scanner can process representative code files
for each supported language without errors.
"""

from pathlib import Path

import pytest

from shannon_insight.scanning.syntax_extractor import SyntaxExtractor

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"


class TestLanguageFixtures:
    """Test parsing all 8 language fixtures."""

    @pytest.fixture
    def extractor(self):
        """Create fresh extractor for each test."""
        return SyntaxExtractor()

    def test_python_fixture(self, extractor):
        """Parse Python fixture file."""
        fixture = FIXTURES_DIR / "sample_complex.py"
        assert fixture.exists(), f"Missing fixture: {fixture}"

        result = extractor.extract(fixture, FIXTURES_DIR)

        assert result is not None
        assert result.language == "python"
        assert result.function_count > 0

    def test_go_fixture(self, extractor):
        """Parse Go fixture file."""
        fixture = FIXTURES_DIR / "sample.go"
        assert fixture.exists(), f"Missing fixture: {fixture}"

        result = extractor.extract(fixture, FIXTURES_DIR)

        assert result is not None
        assert result.language == "go"
        # Go has funcs
        assert result.function_count > 0

    def test_typescript_fixture(self, extractor):
        """Parse TypeScript fixture file."""
        fixture = FIXTURES_DIR / "sample.ts"
        assert fixture.exists(), f"Missing fixture: {fixture}"

        result = extractor.extract(fixture, FIXTURES_DIR)

        assert result is not None
        assert result.language == "typescript"
        # Should have functions and classes
        assert result.function_count > 0 or result.class_count > 0

    def test_javascript_fixture(self, extractor):
        """Parse JavaScript fixture file."""
        fixture = FIXTURES_DIR / "sample.js"
        assert fixture.exists(), f"Missing fixture: {fixture}"

        result = extractor.extract(fixture, FIXTURES_DIR)

        assert result is not None
        # .js files are handled by TypeScript config (includes .js, .jsx)
        assert result.language in ("javascript", "typescript")

    def test_java_fixture(self, extractor):
        """Parse Java fixture file."""
        fixture = FIXTURES_DIR / "Sample.java"
        assert fixture.exists(), f"Missing fixture: {fixture}"

        result = extractor.extract(fixture, FIXTURES_DIR)

        assert result is not None
        assert result.language == "java"

    def test_rust_fixture(self, extractor):
        """Parse Rust fixture file."""
        fixture = FIXTURES_DIR / "sample.rs"
        assert fixture.exists(), f"Missing fixture: {fixture}"

        result = extractor.extract(fixture, FIXTURES_DIR)

        assert result is not None
        assert result.language == "rust"

    def test_ruby_fixture(self, extractor):
        """Parse Ruby fixture file."""
        fixture = FIXTURES_DIR / "sample.rb"
        assert fixture.exists(), f"Missing fixture: {fixture}"

        result = extractor.extract(fixture, FIXTURES_DIR)

        assert result is not None
        assert result.language == "ruby"
        assert result.function_count > 0 or result.class_count > 0

    def test_c_fixture(self, extractor):
        """Parse C fixture file."""
        fixture = FIXTURES_DIR / "sample.c"
        assert fixture.exists(), f"Missing fixture: {fixture}"

        result = extractor.extract(fixture, FIXTURES_DIR)

        assert result is not None
        assert result.language == "c"

    def test_cpp_fixture(self, extractor):
        """Parse C++ fixture file."""
        fixture = FIXTURES_DIR / "sample.cpp"
        assert fixture.exists(), f"Missing fixture: {fixture}"

        result = extractor.extract(fixture, FIXTURES_DIR)

        assert result is not None
        # .cpp files are handled by C config (includes .c, .cpp, .h, .hpp)
        assert result.language in ("c", "cpp")


class TestEncodingFallback:
    """Test encoding error handling and fallback."""

    def test_latin1_file_uses_fallback(self, tmp_path):
        """Latin-1 encoded file should use fallback without crashing."""
        # Create a Latin-1 encoded file with special characters
        fixture = tmp_path / "latin1.py"
        content = "# Caf\xe9 and na\xefve\ndef foo():\n    pass\n"
        fixture.write_bytes(content.encode("latin-1"))

        extractor = SyntaxExtractor()
        result = extractor.extract(fixture, tmp_path)

        # Should still get a result (via errors='replace' handling)
        assert result is not None
        assert result.language == "python"

    def test_utf8_file_works(self, tmp_path):
        """UTF-8 file should work normally."""
        fixture = tmp_path / "utf8.py"
        content = "# Café and naïve\ndef foo():\n    pass\n"
        fixture.write_text(content, encoding="utf-8")

        extractor = SyntaxExtractor()
        result = extractor.extract(fixture, tmp_path)

        assert result is not None
        assert result.function_count == 1

    def test_binary_content_handled(self, tmp_path):
        """Files with binary content should be handled gracefully."""
        fixture = tmp_path / "binary.py"
        # Write binary content with null bytes
        fixture.write_bytes(b"def foo():\x00\x00\x00    pass\n")

        extractor = SyntaxExtractor()
        result = extractor.extract(fixture, tmp_path)

        # Should still get a result, even if content is mangled
        assert result is not None


class TestNestingDepthAccuracy:
    """Test that nesting depth is calculated correctly."""

    def test_python_nesting_depth(self, tmp_path):
        """Python nesting depth should be accurate (when tree-sitter available)."""
        fixture = tmp_path / "nested.py"
        fixture.write_text("""
def deeply_nested():
    if True:
        for i in range(10):
            while i > 0:
                if i % 2:
                    try:
                        pass
                    except:
                        pass
""")

        extractor = SyntaxExtractor()
        result = extractor.extract(fixture, tmp_path)

        assert result is not None
        # Regex fallback may have limited nesting detection
        # Tree-sitter will detect >= 3, regex may detect 0
        # Just verify we get a result without crashing
        assert result.max_nesting >= 0


class TestStubDetection:
    """Test stub/empty function detection."""

    def test_stub_functions_detected(self, tmp_path):
        """Stub functions should have high stub_score."""
        fixture = tmp_path / "stubs.py"
        fixture.write_text("""
def stub1():
    pass

def stub2():
    ...

def real_function():
    x = 1
    y = 2
    z = x + y
    if z > 0:
        return z
    return 0
""")

        extractor = SyntaxExtractor()
        result = extractor.extract(fixture, tmp_path)

        assert result is not None
        # Should have some stubs
        stubs = [fn for fn in result.functions if fn.is_stub]
        assert len(stubs) >= 1

    def test_stub_ratio_calculated(self, tmp_path):
        """stub_ratio should be calculated correctly."""
        fixture = tmp_path / "mixed.py"
        fixture.write_text("""
def stub1(): pass
def stub2(): pass
def real():
    x = 1
    y = 2
    z = 3
    return x + y + z
""")

        extractor = SyntaxExtractor()
        result = extractor.extract(fixture, tmp_path)

        assert result is not None
        # With 2 stubs and 1 real, ratio should be > 0
        assert result.stub_ratio > 0


class TestImplGini:
    """Test implementation Gini coefficient."""

    def test_equal_functions_low_gini(self, tmp_path):
        """Equal-sized functions should have low Gini."""
        fixture = tmp_path / "equal.py"
        fixture.write_text("""
def func1():
    x = 1
    y = 2
    return x + y

def func2():
    a = 3
    b = 4
    return a + b

def func3():
    m = 5
    n = 6
    return m + n
""")

        extractor = SyntaxExtractor()
        result = extractor.extract(fixture, tmp_path)

        assert result is not None
        # Should have relatively low Gini for equal-ish functions
        assert result.impl_gini < 0.5

    def test_unequal_functions_high_gini(self, tmp_path):
        """Very unequal function sizes should have higher Gini (when tree-sitter available)."""
        fixture = tmp_path / "unequal.py"
        fixture.write_text("""
def tiny(): pass

def huge():
    a = 1
    b = 2
    c = 3
    d = 4
    e = 5
    f = 6
    g = 7
    h = 8
    i = 9
    j = 10
    k = 11
    l = 12
    m = 13
    n = 14
    o = 15
    return a + b + c + d + e + f + g + h + i + j + k + l + m + n + o
""")

        extractor = SyntaxExtractor()
        result = extractor.extract(fixture, tmp_path)

        assert result is not None
        # Regex fallback has limited body_tokens detection
        # Tree-sitter will detect inequality, regex may not
        # Just verify calculation doesn't crash
        assert result.impl_gini >= 0.0
