"""Gates G1+G2: python walker deep asserts against hand-counted truth."""

from pathlib import Path

import pytest

from shannon_insight.core.errors import ShannonError
from shannon_insight.syntax.parser import analyze_source

CORPUS = Path(__file__).parents[2] / "fixtures" / "v4_corpus"


def _parse(name: str):
    return analyze_source(name, (CORPUS / name).read_bytes())


class TestAppPy:
    s = _parse("app.py")

    def test_function_count_matches_manual(self):
        # register, helper_wrapper, fetch, run, main, inner = 6
        assert self.s.function_count == 6

    def test_class_and_bases(self):
        assert self.s.class_count == 1
        svc = self.s.classes[0]
        assert svc.name == "Service"
        assert "ABC" in [b.rsplit(".", 1)[-1] for b in svc.bases]
        assert svc.is_abstract is True
        assert list(svc.method_names) == ["run"]

    def test_relative_import_level(self):
        rel = [i for i in self.s.imports if i.module.endswith("util") and i.is_relative]
        assert len(rel) == 1 and rel[0].level == 1

    def test_import_inventory(self):
        modules = {i.module for i in self.s.imports}
        assert {"os", "collections", "util"} <= modules

    def test_main_guard(self):
        assert self.s.has_main_guard is True

    def test_async_and_decorator(self):
        fetch = next(f for f in self.s.functions if f.name == "fetch")
        assert fetch.is_async is True
        assert "cache_result" in fetch.decorators

    def test_method_params(self):
        run = next(f for f in self.s.functions if f.name == "run")
        assert run.params == ("x", "y")
        assert run.is_method is True
        assert run.qualified_name == "Service.run"

    def test_nesting_depth(self):
        reg = next(f for f in self.s.functions if f.name == "register")
        assert reg.nesting_depth == 2

    def test_identifiers_captured(self):
        assert "register" in self.s.identifiers
        assert len(self.s.identifiers) > 10


class TestUtilPy:
    s = _parse("util.py")

    def test_stub_ratio_above_half(self):
        assert self.s.stub_ratio > 0.5

    def test_bimodal_gini(self):
        # real_work large; three stubs tiny
        assert self.s.impl_gini > 0.5

    def test_hard_stubs_flagged(self):
        todo = {f.name: f for f in self.s.functions}
        assert todo["todo_a"].is_hard_stub is True       # pass
        assert todo["todo_b"].is_hard_stub is False      # docstring-only, not marker
        assert todo["todo_c"].is_hard_stub is True       # raise NotImplementedError
        real = todo["real_work"]
        assert real.is_hard_stub is False
        assert real.has_docstring is False

    def test_comments_empty(self):
        assert isinstance(self.s.comments, tuple)


class TestDeepPy:
    s = _parse("deep.py")

    def test_nesting_and_cyclomatic(self):
        drill = self.s.functions[0]
        assert drill.nesting_depth == 4
        assert drill.cyclomatic == 5


class TestHostiles:
    def test_empty_file(self):
        s = _parse("empty.py")
        assert s.lines == 0 and s.function_count == 0
        assert s.impl_gini == 0.0 and s.total_tokens == 0

    def test_latin1_decodes(self):
        s = _parse("latin1.py")
        assert s.lines >= 3
        assert s.functions[0].name == "valeur"

    def test_unsupported_extension_raises_domain_error(self):
        with pytest.raises(ShannonError) as exc:
            analyze_source("blob.zzz", b"x")
        assert exc.value.code.value == "SC103"

    def test_syntax_error_file_flags_not_crashes(self):
        s = analyze_source("broken.py", b"def broken(:\n    pass\n")
        assert s.has_errors is True
