"""Tests for Phase 3 NCD-based clone detection."""

import pytest

from shannon_insight.graph.clone_detection import (
    compute_ncd,
    detect_clones,
)


class TestComputeNCD:
    """Test Normalized Compression Distance computation."""

    def test_identical_strings_low_ncd(self):
        content = b"def foo(): pass\n" * 10
        ncd = compute_ncd(content, content)
        assert ncd < 0.1  # Identical content should have very low NCD

    def test_completely_different_high_ncd(self):
        a = b"def foo(): pass\n" * 10
        b = b"class Bar: x = 1\n" * 10
        ncd = compute_ncd(a, b)
        assert ncd > 0.3  # Different content should have higher NCD

    def test_similar_content_moderate_ncd(self):
        a = b"def process_data(x): return x + 1\n" * 5
        b = b"def process_data(y): return y + 1\n" * 5  # Very similar
        ncd = compute_ncd(a, b)
        assert ncd < 0.2  # Similar should be low

    def test_ncd_symmetric(self):
        a = b"hello world " * 20
        b = b"goodbye world " * 20
        ncd_ab = compute_ncd(a, b)
        ncd_ba = compute_ncd(b, a)
        assert ncd_ab == pytest.approx(ncd_ba, abs=0.01)


class TestDetectClones:
    """Test clone pair detection."""

    def test_finds_clones(self):
        # Two nearly identical files should be detected as clones
        files = {
            "a.py": b"def calculate(x): return x * 2 + 1\n" * 10,
            "b.py": b"def calculate(y): return y * 2 + 1\n" * 10,  # Clone of a
            "c.py": b"class TotallyDifferent: pass\n" * 10,  # Not a clone
        }
        roles = {}  # No special roles
        clones = detect_clones(files, roles)

        # Should find a-b as clones
        pairs = {(cp.file_a, cp.file_b) for cp in clones}
        # Could be (a, b) or (b, a) depending on sorting
        assert ("a.py", "b.py") in pairs or ("b.py", "a.py") in pairs

        # c should not be in any clone pair
        for cp in clones:
            assert "c.py" not in (cp.file_a, cp.file_b)

    def test_excludes_test_pairs(self):
        # Two test files should NOT be flagged as clones even if similar
        files = {
            "test_a.py": b"def test_foo(): assert True\n" * 10,
            "test_b.py": b"def test_bar(): assert True\n" * 10,
        }
        roles = {"test_a.py": "TEST", "test_b.py": "TEST"}
        clones = detect_clones(files, roles)
        assert len(clones) == 0

    def test_excludes_migration_pairs(self):
        # Two migration files should NOT be flagged as clones
        files = {
            "001_create.py": b"def upgrade(): pass\ndef downgrade(): pass\n" * 5,
            "002_update.py": b"def upgrade(): pass\ndef downgrade(): pass\n" * 5,
        }
        roles = {"001_create.py": "MIGRATION", "002_update.py": "MIGRATION"}
        clones = detect_clones(files, roles)
        assert len(clones) == 0

    def test_test_vs_production_still_flagged(self):
        # A test file that is nearly identical to a production file SHOULD be flagged
        files = {
            "impl.py": b"def process(): return 42\n" * 20,
            "test_impl.py": b"def process(): return 42\n" * 20,
        }
        roles = {"impl.py": "UTILITY", "test_impl.py": "TEST"}
        clones = detect_clones(files, roles)
        # This should be flagged because only ONE is a test
        assert len(clones) == 1

    def test_ncd_threshold(self):
        # Files with NCD just below 0.3 should be included
        # Files with NCD just above 0.3 should be excluded
        # This is hard to control precisely, so just test the boundary behavior
        clones = detect_clones(
            {
                "a.py": b"x" * 100,
                "b.py": b"x" * 100,  # Identical - definitely clone
            },
            {},
        )
        assert len(clones) == 1
        assert clones[0].ncd < 0.3

    def test_empty_files_skipped(self):
        files = {
            "a.py": b"",
            "b.py": b"",
        }
        clones = detect_clones(files, {})
        # Empty files should be skipped (nothing to compress)
        assert len(clones) == 0

    def test_clone_pair_has_sizes(self):
        files = {
            "a.py": b"content" * 100,
            "b.py": b"content" * 100,
        }
        clones = detect_clones(files, {})
        assert len(clones) == 1
        assert clones[0].size_a == 700
        assert clones[0].size_b == 700
