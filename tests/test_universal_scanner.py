"""Tests for the UniversalScanner (language-agnostic fallback analyzer)."""

import tempfile
from collections import Counter
from pathlib import Path

import pytest

from shannon_insight.analyzers import ConfigurableScanner, get_language_config

# Backward-compatible alias
def UniversalScanner(root_dir, extensions=None, settings=None):
    cfg = get_language_config("universal")
    return ConfigurableScanner(root_dir, config=cfg, extensions=extensions, settings=settings)
from shannon_insight.exceptions import InsufficientDataError


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_scanner(tmpdir: str, extensions=None) -> UniversalScanner:
    return UniversalScanner(tmpdir, extensions=extensions)


def _write(tmpdir: str, name: str, content: str) -> Path:
    p = Path(tmpdir) / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)
    return p


# ---------------------------------------------------------------------------
# Token counting
# ---------------------------------------------------------------------------

class TestTokenCounting:
    def test_strips_c_style_comments(self):
        code = "int x = 1; // comment\nint y = 2; /* block */\n"
        scanner = _make_scanner("/tmp", extensions=[".c"])
        tokens = scanner._count_tokens(code)
        # Should not count words inside comments
        assert tokens > 0
        clean = "int x = 1;\nint y = 2;\n"
        assert scanner._count_tokens(clean) <= tokens + 2  # roughly similar

    def test_strips_hash_comments(self):
        code = "x = 1  # this is a comment\ny = 2\n"
        scanner = _make_scanner("/tmp")
        tokens = scanner._count_tokens(code)
        assert tokens > 0
        # "this", "is", "a", "comment" should not appear
        clean = "x = 1\ny = 2\n"
        assert scanner._count_tokens(clean) <= tokens

    def test_strips_strings(self):
        code = 'val = "hello world"\nother = 42\n'
        scanner = _make_scanner("/tmp")
        tokens = scanner._count_tokens(code)
        assert tokens > 0


# ---------------------------------------------------------------------------
# Import extraction
# ---------------------------------------------------------------------------

class TestImportExtraction:
    def test_python_imports(self):
        code = "import os\nfrom pathlib import Path\n"
        scanner = _make_scanner("/tmp")
        imports = scanner._extract_imports(code)
        assert "os" in imports
        assert "pathlib" in imports

    def test_c_includes(self):
        code = '#include <stdio.h>\n#include "mylib.h"\n'
        scanner = _make_scanner("/tmp")
        imports = scanner._extract_imports(code)
        assert "stdio.h" in imports
        assert "mylib.h" in imports

    def test_rust_use(self):
        code = "use std::io;\nuse crate::utils;\n"
        scanner = _make_scanner("/tmp")
        imports = scanner._extract_imports(code)
        assert "std::io" in imports
        assert "crate::utils" in imports

    def test_js_from_import(self):
        code = "import foo from 'bar'\n"
        scanner = _make_scanner("/tmp")
        imports = scanner._extract_imports(code)
        assert "bar" in imports

    def test_require(self):
        code = "const x = require('lodash')\n"
        scanner = _make_scanner("/tmp")
        imports = scanner._extract_imports(code)
        assert "lodash" in imports

    def test_scala_import(self):
        code = "import scala.collection.mutable\nimport akka.actor\n"
        scanner = _make_scanner("/tmp")
        imports = scanner._extract_imports(code)
        assert "scala.collection.mutable" in imports
        assert "akka.actor" in imports


# ---------------------------------------------------------------------------
# Function counting
# ---------------------------------------------------------------------------

class TestFunctionCounting:
    def test_def_keyword(self):
        code = "def foo():\n    pass\ndef bar():\n    pass\n"
        scanner = _make_scanner("/tmp")
        assert scanner._count_functions(code) >= 2

    def test_func_keyword(self):
        code = "func main() {\n}\nfunc helper() {\n}\n"
        scanner = _make_scanner("/tmp")
        assert scanner._count_functions(code) >= 2

    def test_fn_keyword(self):
        code = "fn compute(x: i32) -> i32 {\n    x + 1\n}\n"
        scanner = _make_scanner("/tmp")
        assert scanner._count_functions(code) >= 1

    def test_function_keyword(self):
        code = "function greet(name) {\n    console.log(name)\n}\n"
        scanner = _make_scanner("/tmp")
        assert scanner._count_functions(code) >= 1

    def test_sub_keyword(self):
        code = "sub process {\n    my $x = 1;\n}\n"
        scanner = _make_scanner("/tmp")
        assert scanner._count_functions(code) >= 1

    def test_mixed_styles(self):
        code = (
            "def py_func():\n    pass\n"
            "func go_func() {\n}\n"
            "fn rust_func() {\n}\n"
        )
        scanner = _make_scanner("/tmp")
        assert scanner._count_functions(code) >= 3


# ---------------------------------------------------------------------------
# Complexity estimation
# ---------------------------------------------------------------------------

class TestComplexityEstimation:
    def test_base_complexity(self):
        code = "x = 1\n"
        scanner = _make_scanner("/tmp")
        assert scanner._estimate_complexity(code) == 1.0

    def test_increases_with_branching(self):
        simple = "x = 1\n"
        complex_code = "if x:\n  pass\nelse:\n  pass\nfor i in range(10):\n  pass\n"
        scanner = _make_scanner("/tmp")
        assert scanner._estimate_complexity(complex_code) > scanner._estimate_complexity(simple)

    def test_counts_logical_operators(self):
        code = "if a && b || c:\n  pass\n"
        scanner = _make_scanner("/tmp")
        # base(1) + if(1) + &&(1) + ||(1) = 4
        assert scanner._estimate_complexity(code) >= 4

    def test_counts_ruby_keywords(self):
        code = "unless done\n  next\nend\n"
        scanner = _make_scanner("/tmp")
        assert scanner._estimate_complexity(code) >= 2  # base + unless


# ---------------------------------------------------------------------------
# Nesting depth
# ---------------------------------------------------------------------------

class TestNestingDepth:
    def test_brace_based(self):
        code = "func main() {\n  if true {\n    for {\n    }\n  }\n}\n"
        scanner = _make_scanner("/tmp")
        assert scanner._compute_nesting(code) >= 3

    def test_indent_based(self):
        code = "def foo():\n    if True:\n        for x in y:\n            pass\n"
        scanner = _make_scanner("/tmp")
        assert scanner._compute_nesting(code) >= 3

    def test_takes_maximum(self):
        # Mix of both — scanner should pick whichever is deeper
        code = (
            "def foo():\n"
            "        deeply_indented = True\n"  # indent depth 2
            "func bar() {\n  {\n    {\n    }\n  }\n}\n"  # brace depth 3
        )
        scanner = _make_scanner("/tmp")
        assert scanner._compute_nesting(code) >= 3


# ---------------------------------------------------------------------------
# Skip logic
# ---------------------------------------------------------------------------

class TestSkipLogic:
    def test_skips_binary_extensions(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            _write(tmpdir, "image.png", "fake png data")
            scanner = _make_scanner(tmpdir, extensions=[".png"])
            p = Path(tmpdir) / "image.png"
            assert scanner._should_skip(p) is True

    def test_skips_vendor_dirs(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            _write(tmpdir, "vendor/lib.scala", "object Lib {}")
            scanner = _make_scanner(tmpdir, extensions=[".scala"])
            p = Path(tmpdir) / "vendor" / "lib.scala"
            assert scanner._should_skip(p) is True

    def test_skips_test_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            _write(tmpdir, "test_main.scala", "object Test {}")
            scanner = _make_scanner(tmpdir, extensions=[".scala"])
            p = Path(tmpdir) / "test_main.scala"
            assert scanner._should_skip(p) is True

    def test_skips_binary_content(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            p = Path(tmpdir) / "data.weird"
            p.write_bytes(b"hello\x00world")
            scanner = _make_scanner(tmpdir, extensions=[".weird"])
            assert scanner._should_skip(p) is True

    def test_does_not_skip_normal_source(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            _write(tmpdir, "main.scala", "object Main { def run() = {} }")
            scanner = _make_scanner(tmpdir, extensions=[".scala"])
            p = Path(tmpdir) / "main.scala"
            assert scanner._should_skip(p) is False


# ---------------------------------------------------------------------------
# Integration: full scan produces valid FileMetrics
# ---------------------------------------------------------------------------

class TestIntegrationScan:
    def _create_scala_project(self, tmpdir):
        """Create a minimal multi-file Scala project."""
        files = {
            "Main.scala": (
                "import scala.io\n"
                "import scala.util\n\n"
                "object Main {\n"
                "  def main(args: Array[String]): Unit = {\n"
                "    if (args.length > 0) {\n"
                "      println(args(0))\n"
                "    } else {\n"
                "      println(\"no args\")\n"
                "    }\n"
                "  }\n"
                "  def helper(): Int = {\n"
                "    val x = 42\n"
                "    x\n"
                "  }\n"
                "}\n"
            ),
            "Utils.scala": (
                "import scala.collection.mutable\n\n"
                "object Utils {\n"
                "  def compute(x: Int): Int = {\n"
                "    for (i <- 0 until x) {\n"
                "      if (i % 2 == 0) {\n"
                "        println(i)\n"
                "      }\n"
                "    }\n"
                "    x * 2\n"
                "  }\n"
                "  def format(s: String): String = {\n"
                "    s.trim\n"
                "  }\n"
                "}\n"
            ),
            "Config.scala": (
                "object Config {\n"
                "  def load(): Map[String, String] = {\n"
                "    Map(\"key\" -> \"value\")\n"
                "  }\n"
                "  def save(): Unit = {\n"
                "    println(\"saved\")\n"
                "  }\n"
                "}\n"
            ),
        }
        for name, content in files.items():
            _write(tmpdir, name, content)

    def test_scan_produces_file_metrics(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            self._create_scala_project(tmpdir)
            scanner = UniversalScanner(tmpdir, extensions=[".scala"])
            results = scanner.scan()
            assert len(results) == 3
            for fm in results:
                assert fm.lines > 0
                assert fm.tokens > 0
                assert fm.complexity_score >= 1
                assert fm.nesting_depth >= 0
                assert isinstance(fm.function_sizes, list)

    def test_empty_file_produces_zeroed_metrics(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            _write(tmpdir, "empty.scala", "")
            scanner = UniversalScanner(tmpdir, extensions=[".scala"])
            results = scanner.scan()
            assert len(results) == 1
            fm = results[0]
            assert fm.lines == 0
            assert fm.tokens == 0
            assert fm.functions == 0


# ---------------------------------------------------------------------------
# Integration with core: auto-detect picks up unknown extensions
# ---------------------------------------------------------------------------

class TestCoreIntegration:
    def _create_multi_file(self, tmpdir, ext, count=3):
        """Create count files of a given extension with enough content."""
        for i in range(count):
            content = (
                f"import lib{i}\n\n"
                f"def func_{i}():\n"
                f"    if True:\n"
                f"        pass\n"
                f"    for x in range(10):\n"
                f"        pass\n\n"
                f"def helper_{i}():\n"
                f"    return {i}\n"
            )
            _write(tmpdir, f"file{i}{ext}", content)

    def test_auto_detect_unknown_extension(self):
        """Auto-detect should pick up .scala files via universal scanner."""
        from shannon_insight import CodebaseAnalyzer

        with tempfile.TemporaryDirectory() as tmpdir:
            self._create_multi_file(tmpdir, ".scala")
            analyzer = CodebaseAnalyzer(tmpdir, language="auto")
            _reports, context = analyzer.analyze()
            assert "universal" in context.detected_languages
            assert context.total_files_scanned >= 3

    def test_explicit_universal_language(self):
        """--language universal should work explicitly."""
        from shannon_insight import CodebaseAnalyzer

        with tempfile.TemporaryDirectory() as tmpdir:
            self._create_multi_file(tmpdir, ".scala")
            analyzer = CodebaseAnalyzer(tmpdir, language="universal")
            reports, context = analyzer.analyze()
            assert "universal" in context.detected_languages

    def test_universal_coexists_with_specific(self):
        """Universal scanner should coexist with language-specific scanners."""
        from shannon_insight import CodebaseAnalyzer

        with tempfile.TemporaryDirectory() as tmpdir:
            # Python files (known)
            self._create_multi_file(tmpdir, ".py")
            # Kotlin files (unknown → universal)
            for i in range(3):
                content = (
                    f"import kotlin.io\n\n"
                    f"fun main{i}() {{\n"
                    f"    if (true) {{\n"
                    f"        println(\"hi\")\n"
                    f"    }}\n"
                    f"}}\n"
                    f"fun helper{i}() {{\n"
                    f"    for (i in 0..10) {{\n"
                    f"        println(i)\n"
                    f"    }}\n"
                    f"}}\n"
                )
                _write(tmpdir, f"app{i}.kt", content)

            analyzer = CodebaseAnalyzer(tmpdir, language="auto")
            reports, context = analyzer.analyze()
            assert "python" in context.detected_languages
            assert "universal" in context.detected_languages

    def test_metrics_produce_valid_primitives(self):
        """Universal scanner metrics should feed into valid primitive scores."""
        from shannon_insight import CodebaseAnalyzer

        with tempfile.TemporaryDirectory() as tmpdir:
            self._create_multi_file(tmpdir, ".scala", count=5)
            analyzer = CodebaseAnalyzer(tmpdir, language="universal")
            reports, context = analyzer.analyze()
            for report in reports:
                p = report.primitives
                assert p.structural_entropy >= 0
                assert p.cognitive_load >= 0
                assert p.semantic_coherence >= 0

    def test_compression_fallback_for_unknown_syntax(self):
        """Files with no recognisable function keywords should still get
        cognitive load scores via the compression-based fallback."""
        from shannon_insight import CodebaseAnalyzer

        with tempfile.TemporaryDirectory() as tmpdir:
            # Haskell-like files: no def/fn/func/function/sub keywords
            for i in range(4):
                content = (
                    f"module Lib{i} where\n\n"
                    + "\n".join(
                        f"compute{j} :: Int -> Int\n"
                        f"compute{j} x = if x > 0 then x * {j} else 0\n"
                        for j in range(10)
                    )
                    + "\n"
                )
                # Pad to exceed compression MIN_SIZE_THRESHOLD (512 bytes)
                content += "-- " + "x" * 600 + "\n"
                _write(tmpdir, f"Lib{i}.hs", content)

            analyzer = CodebaseAnalyzer(tmpdir, language="universal")
            reports, context = analyzer.analyze()
            assert context.total_files_scanned >= 4
            # At least some files should have non-zero cognitive load
            # even though no function keywords were detected
            loads = [r.primitives.cognitive_load for r in reports]
            assert any(load > 0 for load in loads), (
                "Compression fallback should produce non-zero cognitive load"
            )
