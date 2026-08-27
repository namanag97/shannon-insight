"""Gate G1: multilanguage parse conformance."""

from pathlib import Path

import pytest

from shannon_insight.syntax.parser import analyze_source

CORPUS = Path(__file__).parents[2] / "fixtures" / "v4_corpus"

# (file, language, expect_functions_min, expect_imports_min)
CASES = [
    ("app.py", "python", 6, 3),
    ("calc.go", "go", 2, 1),
    ("app.js", "javascript", 3, 2),
    ("service.ts", "typescript", None, 1),  # functions vary by grammar; import pinned
    ("hello.java", "java", 2, 2),
    ("lib.rs", "rust", None, 1),
    ("thing.rb", "ruby", None, 1),
    ("main.c", "c", 2, 2),
]


@pytest.mark.parametrize("fname,lang,min_fns,min_imps", CASES)
def test_parses_with_minimum_shape(fname, lang, min_fns, min_imps):
    s = analyze_source(fname, (CORPUS / fname).read_bytes())
    assert s.language == lang
    assert s.parser_version
    if min_fns is not None:
        assert s.function_count >= min_fns, f"{fname}: {s.function_count} < {min_fns}"
    assert s.import_count >= min_imps


def test_go_package_and_java_package():
    go = analyze_source("calc.go", (CORPUS / "calc.go").read_bytes())
    assert go.package == "main"
    java = analyze_source("hello.java", (CORPUS / "hello.java").read_bytes())
    assert java.package == "com.example"


def test_js_exports_and_alias_shapes():
    js = analyze_source("app.js", (CORPUS / "app.js").read_bytes())
    names = {e.name for e in js.exports}
    assert {"top", "Widget"} <= names
    mods = {i.module for i in js.imports}
    assert "./util" in mods and "fs" in mods


def test_rust_todo_hard_stub():
    rs = analyze_source("lib.rs", (CORPUS / "lib.rs").read_bytes())
    helper = next(f for f in rs.functions if f.name == "helper")
    assert helper.is_hard_stub is True
    reg = next(f for f in rs.functions if f.name == "new")
    assert reg.exported is True or reg.visibility == "public"


def test_c_system_vs_local_include():
    c = analyze_source("main.c", (CORPUS / "main.c").read_bytes())
    system = [i for i in c.imports if i.is_system]
    local = [i for i in c.imports if not i.is_system]
    assert any(i.module == "stdio.h" for i in system)
    assert any("local" in i.module for i in local)


def test_tsx_interface_and_abstract_class():
    ts = analyze_source("service.ts", (CORPUS / "service.ts").read_bytes())
    shape_iface = [c for c in ts.classes if c.name == "Shape"]
    assert shape_iface and shape_iface[0].is_interface is True
    shape2d = next(c for c in ts.classes if c.name == "Shape2D")
    assert shape2d.is_abstract is True
    assert "Base" in [b.rsplit(".", 1)[-1] for b in shape2d.bases]
