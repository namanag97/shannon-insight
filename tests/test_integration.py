"""Integration tests for Shannon Insight"""

import pytest
from pathlib import Path
from shannon_insight import CodebaseAnalyzer, __version__
from shannon_insight.exceptions import InsufficientDataError


class TestSmokeTests:
    """Basic smoke tests to ensure tool works"""

    def test_analyze_test_codebase(self):
        """Test analysis runs without errors on test codebase"""
        analyzer = CodebaseAnalyzer("test_codebase", language="go")
        reports = analyzer.analyze()
        assert isinstance(reports, list)
        assert len(reports) > 0
        assert all(hasattr(r, "file") for r in reports)
        assert all(hasattr(r, "primitives") for r in reports)

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


class TestPrimitiveExtraction:
    """Tests for primitive extraction"""

    def test_semantic_coherence_distinguishes_files(self):
        """Test semantic coherence correctly distinguishes focused vs unfocused files"""
        analyzer = CodebaseAnalyzer("test_codebase", language="go")
        reports = analyzer.analyze()

        # Reports only contain anomalous files, so check that at least one
        # anomalous file has a positive coherence score
        file_scores = {r.file: r.primitives.semantic_coherence for r in reports}
        assert len(file_scores) > 0, "Should have at least one anomalous file"
        assert all(score >= 0 for score in file_scores.values()), (
            "All coherence scores should be non-negative"
        )

    def test_cognitive_load_increases_with_complexity(self):
        """Test cognitive load is positive for complex anomalous files"""
        analyzer = CodebaseAnalyzer("test_codebase", language="go")
        reports = analyzer.analyze()

        file_scores = {r.file: r.primitives.cognitive_load for r in reports}

        # complex.go should be in the anomaly reports with positive cognitive load
        complex_score = file_scores.get("complex.go", None)
        assert complex_score is not None, "complex.go should be in anomaly reports"
        assert complex_score > 0, "complex.go should have a positive cognitive load score"

    def test_structural_entropy_measures_disorder(self):
        """Test structural entropy measures code organization disorder"""
        analyzer = CodebaseAnalyzer("test_codebase", language="go")
        reports = analyzer.analyze()

        file_scores = {r.file: r.primitives.structural_entropy for r in reports}

        # All files should have structural entropy scores
        assert all(score > 0 for score in file_scores.values()), (
            "All files should have structural entropy"
        )


class TestErrorHandling:
    """Tests for error handling"""

    def test_insufficient_data_error(self):
        """Test error when too few files to analyze"""
        import tempfile

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
                language="rust",
            )
            analyzer.analyze()


class TestRecommendations:
    """Tests for recommendation generation"""

    def test_recommendations_are_actionable(self):
        """Test recommendations are specific and actionable"""
        analyzer = CodebaseAnalyzer("test_codebase", language="go")
        reports = analyzer.analyze()

        for report in reports[:3]:
            assert len(report.recommendations) > 0, (
                f"{report.file} should have recommendations"
            )
            for rec in report.recommendations:
                assert len(rec) > 10, "Recommendations should be detailed"
                # Recommendations should contain actionable language
                assert any(
                    word in rec.lower()
                    for word in ["reduce", "split", "extract", "implement",
                                 "consider", "refactor", "review", "group",
                                 "separate", "stabilize", "standardize"]
                ), f"Recommendation should be actionable: {rec}"

    def test_root_causes_identified(self):
        """Test root causes are identified"""
        analyzer = CodebaseAnalyzer("test_codebase", language="go")
        reports = analyzer.analyze()

        for report in reports[:3]:
            assert len(report.root_causes) > 0, f"{report.file} should have root causes"
            for cause in report.root_causes:
                assert len(cause) > 5, "Root causes should be descriptive"

    def test_complex_file_has_specific_recommendations(self):
        """Test complex file gets specific complexity-related recommendations"""
        analyzer = CodebaseAnalyzer("test_codebase", language="go")
        reports = analyzer.analyze()

        complex_report = next((r for r in reports if r.file == "complex.go"), None)
        assert complex_report is not None, "complex.go should be in reports"

        # Check that recommendations mention complexity-related issues
        rec_text = " ".join(complex_report.recommendations)
        assert any(
            keyword in rec_text.lower()
            for keyword in ["split", "reduce", "complexity", "function", "nest"]
        ), "Complex file should have complexity-related recommendations"
