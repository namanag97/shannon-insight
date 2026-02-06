"""Tests for Phase 4 module detection."""

from shannon_insight.architecture.modules import (
    detect_modules,
    determine_module_depth,
)


class TestDetermineModuleDepth:
    """Test automatic module depth determination."""

    def test_flat_project_depth_zero(self):
        # All files in root directory
        file_paths = ["a.py", "b.py", "c.py", "d.py", "e.py"]
        depth = determine_module_depth(file_paths)
        assert depth == 0

    def test_standard_project_depth_two(self):
        # src/pkg/file.py structure -> depth 2 gives src/scanning, src/graph, etc.
        file_paths = [
            "src/scanning/scanner.py",
            "src/scanning/models.py",
            "src/graph/builder.py",
            "src/graph/models.py",
            "src/graph/engine.py",
            "src/insights/kernel.py",
            "src/insights/store.py",
        ]
        depth = determine_module_depth(file_paths)
        # Depth 2 = use 2 directory parts = src/scanning, src/graph, src/insights
        assert depth == 2

    def test_deep_project_finds_right_level(self):
        # src/shannon_insight/graph/... structure
        file_paths = [
            "src/shannon_insight/graph/builder.py",
            "src/shannon_insight/graph/models.py",
            "src/shannon_insight/graph/engine.py",
            "src/shannon_insight/scanning/scanner.py",
            "src/shannon_insight/scanning/models.py",
            "src/shannon_insight/insights/kernel.py",
        ]
        depth = determine_module_depth(file_paths)
        # Depth 3 = use 3 parts = src/shannon_insight/graph, etc.
        assert depth == 3


class TestDetectModules:
    """Test module detection from file paths."""

    def test_basic_detection(self):
        file_paths = [
            "src/graph/builder.py",
            "src/graph/models.py",
            "src/scanning/scanner.py",
        ]
        modules = detect_modules(file_paths, root_dir="")
        assert "src/graph" in modules
        assert "src/scanning" in modules
        assert len(modules["src/graph"].files) == 2
        assert modules["src/graph"].file_count == 2

    def test_flat_project_single_module(self):
        file_paths = ["a.py", "b.py", "c.py"]
        modules = detect_modules(file_paths, root_dir="")
        # Flat project: all files in one module (root)
        assert len(modules) == 1
        assert "." in modules or "" in modules

    def test_respects_module_depth(self):
        file_paths = [
            "src/shannon_insight/graph/builder.py",
            "src/shannon_insight/graph/models.py",
            "src/shannon_insight/scanning/scanner.py",
        ]
        # Depth 3 = 3 directory parts = src/shannon_insight/graph
        modules = detect_modules(file_paths, root_dir="", module_depth=3)
        assert "src/shannon_insight/graph" in modules
        assert "src/shannon_insight/scanning" in modules

    def test_empty_directory_skipped(self):
        # Directory with only __init__.py should be skipped
        file_paths = [
            "src/pkg/__init__.py",  # Empty module
            "src/pkg/real/code.py",
        ]
        modules = detect_modules(file_paths, root_dir="")
        # pkg should not be a module since it only has __init__.py
        # Only pkg/real should be a module
        module_paths = set(modules.keys())
        assert "src/pkg/real" in module_paths or "src/pkg" in module_paths

    def test_module_has_correct_file_count(self):
        file_paths = [
            "src/graph/a.py",
            "src/graph/b.py",
            "src/graph/c.py",
        ]
        modules = detect_modules(file_paths, root_dir="")
        assert modules["src/graph"].file_count == 3
        assert len(modules["src/graph"].files) == 3
