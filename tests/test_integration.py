"""Integration tests for Shannon Insight"""

import subprocess
import tempfile
from pathlib import Path

from shannon_insight import InsightKernel, __version__


class TestSmokeTests:
    """Basic smoke tests to ensure tool works"""

    def test_analyze_test_codebase(self):
        """Test analysis runs without errors on test codebase"""
        kernel = InsightKernel("test_codebase", language="go")
        result, snapshot = kernel.run()
        assert result is not None
        assert snapshot is not None
        assert snapshot.file_count > 0

    def test_cli_version(self):
        """Test CLI version command works"""
        result = subprocess.run(["shannon-insight", "--version"], capture_output=True, text=True)
        assert result.returncode == 0
        assert __version__ in result.stdout

    def test_cli_help(self):
        """Test CLI help command works"""
        result = subprocess.run(["shannon-insight", "--help"], capture_output=True, text=True)
        assert result.returncode == 0
        assert "Shannon Insight" in result.stdout

    def test_bare_command_works(self):
        """shannon-insight with -C should analyze the given path."""
        result = subprocess.run(
            ["shannon-insight", "-C", "test_codebase"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0

    def test_path_option(self):
        """shannon-insight -C <path> should work."""
        result = subprocess.run(
            ["shannon-insight", "-C", "test_codebase"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0

    def test_subcommand_help_explain(self):
        """shannon-insight explain --help should show explain help."""
        result = subprocess.run(
            ["shannon-insight", "explain", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "file" in result.stdout.lower() or "explain" in result.stdout.lower()

    def test_subcommand_help_diff(self):
        """shannon-insight diff --help should show diff help, not main help."""
        result = subprocess.run(
            ["shannon-insight", "diff", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "snapshot" in result.stdout.lower() or "diff" in result.stdout.lower()

    def test_json_flag(self):
        """--json should produce valid JSON."""
        result = subprocess.run(
            ["shannon-insight", "--json", "-C", "test_codebase"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        import json

        data = json.loads(result.stdout)
        assert "findings" in data

    def test_invalid_language_friendly_error(self):
        """Invalid language should give a friendly error at API level."""
        import pytest

        from shannon_insight.exceptions import ShannonInsightError
        from shannon_insight.scanning.languages import get_language_config

        with pytest.raises(ShannonInsightError, match="Unsupported language"):
            get_language_config("invalid")

    def test_fail_on_validates_input(self):
        """--fail-on with invalid value should error."""
        result = subprocess.run(
            ["shannon-insight", "--fail-on", "invalid", "-C", "test_codebase"],
            capture_output=True,
            text=True,
        )
        assert result.returncode != 0

    def test_no_save_by_default(self):
        """Running without --save should not create .shannon/."""
        import shutil

        with tempfile.TemporaryDirectory() as tmpdir:
            code_dir = Path(tmpdir) / "code"
            shutil.copytree("test_codebase", str(code_dir))
            # Remove any pre-existing .shannon/ copied from source
            shannon_dir = code_dir / ".shannon"
            if shannon_dir.exists():
                shutil.rmtree(shannon_dir)
            result = subprocess.run(
                ["shannon-insight", "-C", str(code_dir)],
                capture_output=True,
                text=True,
            )
            assert result.returncode == 0
            assert not (code_dir / ".shannon").exists()

    def test_default_output_is_quiet(self):
        """Default output should not contain INFO log lines."""
        result = subprocess.run(
            ["shannon-insight", "-C", "test_codebase"],
            capture_output=True,
            text=True,
        )
        assert "INFO" not in result.stderr
        assert "Auto-detected" not in result.stderr + result.stdout


class TestMultiLanguage:
    """Multi-language support tests"""

    def test_auto_detect_finds_multiple_languages(self):
        """Auto-detect should find both .go and .py files"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create Go files
            go_file = Path(tmpdir) / "main.go"
            go_file.write_text(
                'package main\n\nimport "fmt"\n\n'
                'func main() {\n\tfmt.Println("hi")\n}\n'
                "func helper() {\n\tif true {\n\t\treturn\n\t}\n}\n"
                "func another() {\n\tfor i := 0; i < 10; i++ {\n\t}\n}\n"
            )
            go_file2 = Path(tmpdir) / "util.go"
            go_file2.write_text(
                'package main\n\nimport "os"\n\n'
                "func readFile() {\n\tos.Exit(0)\n}\n"
                "func writeFile() {\n\tif true {\n\t\treturn\n\t}\n}\n"
            )
            go_file3 = Path(tmpdir) / "server.go"
            go_file3.write_text(
                'package main\n\nimport "net/http"\n\n'
                'func serve() {\n\thttp.ListenAndServe(":8080", nil)\n}\n'
                "func handler() {\n\tif true {\n\t\treturn\n\t}\n}\n"
            )

            # Create Python files
            py_file = Path(tmpdir) / "script.py"
            py_file.write_text(
                "import os\nimport sys\n\n"
                'def main():\n    print("hello")\n\n'
                "def helper():\n    if True:\n        return\n\n"
                "def another():\n    for i in range(10):\n        pass\n"
            )
            py_file2 = Path(tmpdir) / "util.py"
            py_file2.write_text(
                "import json\n\n"
                'def read_json():\n    return json.loads("{}")\n\n'
                "def write_json():\n    if True:\n        return\n"
            )
            py_file3 = Path(tmpdir) / "config.py"
            py_file3.write_text(
                "import pathlib\n\n"
                'def load():\n    return pathlib.Path(".")\n\n'
                "def save():\n    if True:\n        return\n"
            )

            kernel = InsightKernel(tmpdir, language="auto")
            result, snapshot = kernel.run()
            assert snapshot.file_count >= 6

    def test_explicit_language_still_works(self):
        """Specifying language should work"""
        kernel = InsightKernel("test_codebase", language="go")
        result, snapshot = kernel.run()
        assert snapshot.file_count > 0


class TestInsightFindings:
    """Tests for insight finding generation"""

    def test_findings_have_evidence(self):
        """Test that findings include evidence"""
        kernel = InsightKernel("test_codebase", language="go")
        result, snapshot = kernel.run()

        for finding in result.findings:
            assert finding.finding_type is not None
            assert finding.severity >= 0
            assert len(finding.files) > 0
            assert finding.suggestion is not None

    def test_findings_are_ranked_by_severity(self):
        """Test findings are ordered by severity (descending)"""
        kernel = InsightKernel("test_codebase", language="go")
        result, snapshot = kernel.run()

        if len(result.findings) >= 2:
            for i in range(len(result.findings) - 1):
                assert result.findings[i].severity >= result.findings[i + 1].severity

    def test_max_findings_respected(self):
        """Test max_findings parameter caps output"""
        kernel = InsightKernel("test_codebase", language="go")
        result, snapshot = kernel.run(max_findings=3)
        assert len(result.findings) <= 3


class TestSnapshotCapture:
    """Tests for snapshot capture"""

    def test_snapshot_has_metadata(self):
        """Test snapshot captures metadata"""
        kernel = InsightKernel("test_codebase", language="go")
        result, snapshot = kernel.run()

        assert snapshot.file_count > 0
        assert snapshot.tool_version != ""
        assert snapshot.timestamp != ""
        assert snapshot.analyzed_path != ""

    def test_snapshot_has_file_signals(self):
        """Test snapshot contains per-file signals"""
        kernel = InsightKernel("test_codebase", language="go")
        result, snapshot = kernel.run()

        assert len(snapshot.file_signals) > 0

    def test_snapshot_findings_match_result(self):
        """Test snapshot findings correspond to result findings"""
        kernel = InsightKernel("test_codebase", language="go")
        result, snapshot = kernel.run()

        assert len(snapshot.findings) == len(result.findings)


class TestErrorHandling:
    """Tests for error handling"""

    def test_empty_directory_returns_empty_result(self):
        """Test empty directory produces empty result"""
        with tempfile.TemporaryDirectory() as tmpdir:
            empty_dir = Path(tmpdir) / "empty"
            empty_dir.mkdir()

            kernel = InsightKernel(str(empty_dir), language="go")
            result, snapshot = kernel.run()
            assert len(result.findings) == 0
            assert snapshot.file_count == 0
