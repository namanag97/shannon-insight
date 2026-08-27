"""Gate G6: discovery determinism + filters, and Gate G7: golden manifest."""

import json
import os
from pathlib import Path

import pytest

from shannon_insight.facts.discovery import DiscoveryConfig, discover
from shannon_insight.intake import IntakeConfig, IntakeService
from shannon_insight.syntax.parser import analyze_source

CORPUS = Path(__file__).parents[2] / "fixtures" / "v4_corpus"
GOLDEN = CORPUS / "golden.json"


class TestDiscovery:
    def _tree(self, tmp_path: Path) -> Path:
        root = tmp_path / "proj"
        (root / "src").mkdir(parents=True)
        (root / "node_modules").mkdir()
        (root / "src" / "a.py").write_text("x = 1\n")
        (root / "src" / "b.js").write_text("const x=1;\n")
        (root / "node_modules" / "dep.js").write_text("const d=1;\n")
        (root / ".hidden.py").write_text("h=1\n")
        (root / "big.py").write_text("y=1\n" * 200_000)  # > size cap
        (root / "notes.txt").write_text("not code")
        return root

    def test_filters_and_determinism(self, tmp_path):
        cfg = DiscoveryConfig(max_file_size_mb=0.001)
        root = self._tree(tmp_path)
        first = [p.relative_to(root).as_posix() for p in discover(root, cfg)]
        second = [p.relative_to(root).as_posix() for p in discover(root, cfg)]
        assert first == second
        assert "src/a.py" in first and "src/b.js" in first
        assert all("node_modules" not in p for p in first)
        assert all(not p.startswith(".") for p in first)
        assert "big.py" not in first
        assert "notes.txt" not in first

    def test_missing_root_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            list(discover(tmp_path / "nope"))


class TestIntakeE2E:
    def test_corpus_without_git(self):
        rep = IntakeService().run(IntakeConfig(root=CORPUS, use_git=False))
        assert rep.parsed_count >= 12
        assert rep.has_git is False
        kinds = {e.kind for e in rep.events}
        assert {"files_discovered", "files_parsed", "intake_completed"} <= kinds
        langs = {f.language for f in rep.files}
        assert {"python", "go", "javascript", "typescript", "java", "rust", "ruby", "c"} <= langs

    def test_generated_bundle_fast_path(self, tmp_path):
        root = tmp_path / "bundle"
        root.mkdir()
        (root / "bundle.js").write_text("var x=1;" + ",".join(f"a{i}:{{v:{i}}}" for i in range(40_000)))
        s = analyze_source("bundle.js", (root / "bundle.js").read_bytes())
        assert s.is_generated is True
        assert s.content_hash


GOLDEN_KEYS = ("language", "lines", "function_count", "class_count",
               "import_count", "stub_ratio", "impl_gini", "max_nesting")


def _manifest() -> dict:
    out: dict[str, dict] = {}
    for path in sorted(discover(CORPUS)):
        rel = path.relative_to(CORPUS).as_posix()
        s = analyze_source(rel, path.read_bytes())
        entry = {
            "content_hash12": s.content_hash[:12],
            "total_tokens": s.total_tokens,
            **{k: getattr(s, k) for k in GOLDEN_KEYS},
            "functions": sorted(f.name for f in s.functions),
        }
        out[rel] = entry
    return out


@pytest.mark.skipif(os.environ.get("SHANNON_REGEN_GOLDEN") == "1", reason="regen mode")
def test_golden_manifest_matches():
    assert GOLDEN.exists(), "golden missing; run SHANNON_REGEN_GOLDEN=1 once"
    current = _manifest()
    golden = json.loads(GOLDEN.read_text())
    assert current == golden


def test_golden_manifest_regen_writes_if_requested(tmp_path):
    if os.environ.get("SHANNON_REGEN_GOLDEN") != "1":
        pytest.skip("set SHANNON_REGEN_GOLDEN=1 to rewrite golden")
    GOLDEN.write_text(json.dumps(_manifest(), indent=2, sort_keys=True))


class TestGitignoreGuide:
    def _tree(self, tmp_path: Path) -> Path:
        root = tmp_path / "repo"
        (root / "src" / "generated").mkdir(parents=True)
        (root / "src" / "keep.py").write_text("k=1\n")
        (root / "secret.py").write_text("s=1\n")
        (root / "src" / "gen_out.py").write_text("g=1\n")
        (root / "src" / "generated" / "out.py").write_text("o=1\n")
        (root / ".gitignore").write_text("secret.py\n")
        (root / "src" / ".gitignore").write_text("generated/\n")
        return root

    def test_root_gitignored_file_excluded(self, tmp_path):
        root = self._tree(tmp_path)
        rels = [p.relative_to(root).as_posix() for p in discover(root)]
        assert "secret.py" not in rels
        assert "src/keep.py" in rels

    def test_nested_gitignore_scopes_to_subdir(self, tmp_path):
        root = self._tree(tmp_path)
        rels = [p.relative_to(root).as_posix() for p in discover(root)]
        assert "src/generated/out.py" not in rels  # dir-pattern kills subtree
        assert "src/gen_out.py" in rels            # name-similar file untouched
        assert "src/keep.py" in rels

    def test_respect_flag_off_restores(self, tmp_path):
        root = self._tree(tmp_path)
        cfg = DiscoveryConfig(respect_gitignore=False, exclude_patterns=())
        rels = [p.relative_to(root).as_posix() for p in discover(root, cfg)]
        assert "secret.py" in rels


def test_classifier_table():
    from shannon_insight.facts.classify import FileClass, classify

    cases = {
        "tests/test_util.py": FileClass.TEST,
        "src/app_test.go": FileClass.TEST,
        "web/__tests__/a.tsx": FileClass.TEST,
        "vendor/lib/x.js": FileClass.VENDORED,
        "src/generated/pb2.py": FileClass.GENERATED,
        "app.min.js": FileClass.GENERATED,
        "pyproject.toml": FileClass.CONFIG,
        "README.md": FileClass.DOC,
        "data.csv": FileClass.DATA,
        "src/engine.py": FileClass.SOURCE,
    }
    for path, want in cases.items():
        got = classify(path).file_class
        assert got is want, f"{path}: {got} != {want}"


def test_git_context_on_fixture(git_repo):
    from shannon_insight.facts.git_extractor import git_context

    ctx = git_context(git_repo)
    assert ctx is not None
    assert ctx.total_commits >= 4
    assert ctx.partial_history is False
    assert ctx.branch  # master or main depending on git version

    partial = git_context(git_repo, max_commits=1)
    assert partial.partial_history is True


def test_intake_reports_branch_and_classes():
    rep = IntakeService().run(IntakeConfig(root=CORPUS, use_git=False))
    classes = rep.summary()["classes"]
    assert classes.get("test", 0) >= 1
    assert classes.get("source", 0) >= 5
