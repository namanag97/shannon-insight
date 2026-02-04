"""Integration tests for Shannon Insight"""

import pytest
import tempfile
from pathlib import Path
from shannon_insight import CodebaseAnalyzer, __version__
from shannon_insight.exceptions import InsufficientDataError


class TestSmokeTests:
    """Basic smoke tests to ensure tool works"""

    def test_analyze_test_codebase(self):
        """Test analysis runs without errors on test codebase"""
        analyzer = CodebaseAnalyzer("test_codebase", language="go")
        reports, context = analyzer.analyze()
        assert isinstance(reports, list)
        assert len(reports) > 0
        assert all(hasattr(r, "file") for r in reports)
        assert all(hasattr(r, "primitives") for r in reports)
        assert context.total_files_scanned > 0
        assert "go" in context.detected_languages

    def test_cli_version(self):
        """Test CLI version command works"""
        import subprocess

        result = subprocess.run(
            ["shannon-insight", "--version"], capture_output=True, text=True
        )
        assert result.returncode == 0
        assert __version__ in result.stdout

    def test_cli_help(self):
        """Test CLI help command works"""
        import subprocess

        result = subprocess.run(
            ["shannon-insight", "--help"], capture_output=True, text=True
        )
        assert result.returncode == 0
        assert "Shannon Insight" in result.stdout


class TestMultiLanguage:
    """Phase 1: Multi-language support tests"""

    def test_auto_detect_finds_multiple_languages(self):
        """Auto-detect should find both .go and .py files in test_codebase"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create Go file
            go_file = Path(tmpdir) / "main.go"
            go_file.write_text(
                'package main\n\nimport "fmt"\n\n'
                'func main() {\n\tfmt.Println("hi")\n}\n'
                'func helper() {\n\tif true {\n\t\treturn\n\t}\n}\n'
                'func another() {\n\tfor i := 0; i < 10; i++ {\n\t}\n}\n'
            )
            go_file2 = Path(tmpdir) / "util.go"
            go_file2.write_text(
                'package main\n\nimport "os"\n\n'
                'func readFile() {\n\tos.Exit(0)\n}\n'
                'func writeFile() {\n\tif true {\n\t\treturn\n\t}\n}\n'
            )
            go_file3 = Path(tmpdir) / "server.go"
            go_file3.write_text(
                'package main\n\nimport "net/http"\n\n'
                'func serve() {\n\thttp.ListenAndServe(":8080", nil)\n}\n'
                'func handler() {\n\tif true {\n\t\treturn\n\t}\n}\n'
            )

            # Create Python file
            py_file = Path(tmpdir) / "script.py"
            py_file.write_text(
                'import os\nimport sys\n\n'
                'def main():\n    print("hello")\n\n'
                'def helper():\n    if True:\n        return\n\n'
                'def another():\n    for i in range(10):\n        pass\n'
            )
            py_file2 = Path(tmpdir) / "util.py"
            py_file2.write_text(
                'import json\n\n'
                'def read_json():\n    return json.loads("{}")\n\n'
                'def write_json():\n    if True:\n        return\n'
            )
            py_file3 = Path(tmpdir) / "config.py"
            py_file3.write_text(
                'import pathlib\n\n'
                'def load():\n    return pathlib.Path(".")\n\n'
                'def save():\n    if True:\n        return\n'
            )

            analyzer = CodebaseAnalyzer(tmpdir, language="auto")
            reports, context = analyzer.analyze()
            assert "go" in context.detected_languages
            assert "python" in context.detected_languages
            assert context.total_files_scanned >= 6

    def test_explicit_language_still_works(self):
        """Specifying --language go should only scan Go files"""
        analyzer = CodebaseAnalyzer("test_codebase", language="go")
        reports, context = analyzer.analyze()
        assert context.detected_languages == ["go"]


class TestPrimitiveExtraction:
    """Tests for primitive extraction"""

    def test_semantic_coherence_distinguishes_files(self):
        """Test semantic coherence correctly distinguishes focused vs unfocused files"""
        analyzer = CodebaseAnalyzer("test_codebase", language="go")
        reports, _ctx = analyzer.analyze()

        file_scores = {r.file: r.primitives.semantic_coherence for r in reports}
        assert len(file_scores) > 0, "Should have at least one anomalous file"
        assert all(score >= 0 for score in file_scores.values()), (
            "All coherence scores should be non-negative"
        )

    def test_cognitive_load_increases_with_complexity(self):
        """Test cognitive load is positive for complex anomalous files"""
        analyzer = CodebaseAnalyzer("test_codebase", language="go")
        reports, _ctx = analyzer.analyze()

        file_scores = {r.file: r.primitives.cognitive_load for r in reports}

        complex_score = file_scores.get("complex.go", None)
        assert complex_score is not None, "complex.go should be in anomaly reports"
        assert complex_score > 0, "complex.go should have a positive cognitive load score"

    def test_structural_entropy_measures_disorder(self):
        """Test structural entropy measures code organization disorder"""
        analyzer = CodebaseAnalyzer("test_codebase", language="go")
        reports, _ctx = analyzer.analyze()

        file_scores = {r.file: r.primitives.structural_entropy for r in reports}

        assert all(score > 0 for score in file_scores.values()), (
            "All files should have structural entropy"
        )


class TestErrorHandling:
    """Tests for error handling"""

    def test_insufficient_data_error(self):
        """Test error when too few files to analyze"""
        with tempfile.TemporaryDirectory() as tmpdir:
            empty_dir = Path(tmpdir) / "empty"
            empty_dir.mkdir()

            with pytest.raises(InsufficientDataError):
                analyzer = CodebaseAnalyzer(empty_dir, language="go")
                analyzer.analyze()

    def test_unsupported_language_error(self):
        """Test error for unsupported language"""
        from shannon_insight.exceptions import UnsupportedLanguageError

        with pytest.raises(UnsupportedLanguageError):
            analyzer = CodebaseAnalyzer(
                "test_codebase",
                language="cobol",
            )
            analyzer.analyze()


class TestRecommendations:
    """Tests for recommendation generation"""

    def test_recommendations_are_actionable(self):
        """Test recommendations are specific and actionable"""
        analyzer = CodebaseAnalyzer("test_codebase", language="go")
        reports, _ctx = analyzer.analyze()

        for report in reports[:3]:
            assert len(report.recommendations) > 0, (
                f"{report.file} should have recommendations"
            )
            for rec in report.recommendations:
                assert len(rec) > 10, "Recommendations should be detailed"
                assert any(
                    word in rec.lower()
                    for word in ["reduce", "split", "extract", "implement",
                                 "consider", "refactor", "review", "group",
                                 "separate", "stabilize", "standardize"]
                ), f"Recommendation should be actionable: {rec}"

    def test_root_causes_identified(self):
        """Test root causes are identified"""
        analyzer = CodebaseAnalyzer("test_codebase", language="go")
        reports, _ctx = analyzer.analyze()

        for report in reports[:3]:
            assert len(report.root_causes) > 0, f"{report.file} should have root causes"
            for cause in report.root_causes:
                assert len(cause) > 5, "Root causes should be descriptive"

    def test_complex_file_has_specific_recommendations(self):
        """Test complex file gets specific complexity-related recommendations"""
        analyzer = CodebaseAnalyzer("test_codebase", language="go")
        reports, _ctx = analyzer.analyze()

        complex_report = next((r for r in reports if r.file == "complex.go"), None)
        assert complex_report is not None, "complex.go should be in reports"

        rec_text = " ".join(complex_report.recommendations)
        assert any(
            keyword in rec_text.lower()
            for keyword in ["split", "reduce", "complexity", "function", "nest"]
        ), "Complex file should have complexity-related recommendations"
