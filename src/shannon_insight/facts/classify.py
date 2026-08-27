"""File classification: what KIND of file is this?

Decided by cheap evidence (path segments, naming conventions, extension) at
acquisition time — no parsing required. Downstream consumers (hotspot filters,
test-twin lookup, noise suppression) depend on this, so it must be a
first-class acquisition fact, not a late heuristic.

Classification order (first match wins):
    VENDORED → GENERATED(name) → IGNORED_CLASS → TEST → DOC/DATA/CONFIG → SOURCE
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import PurePosixPath


class FileClass(Enum):
    SOURCE = "source"
    TEST = "test"
    GENERATED = "generated"
    VENDORED = "vendored"
    CONFIG = "config"
    DOC = "doc"
    DATA = "data"
    UNKNOWN = "unknown"


_VENDORED_SEGMENTS = frozenset(
    {
        "node_modules",
        "vendor",
        "third_party",
        "thirdparty",
        "site-packages",
        "dist-packages",
        "__pycache__",
        ".tox",
        "venv",
        ".venv",
        "target",
        "bower_components",
        "packages-lock",
    }
)

_GENERATED_SEGMENTS = frozenset({"generated", "gen", "_gen", "autogen", "protobuf", "proto_out"})
_GENERATED_SUFFIXES = (
    ".min.js",
    ".min.css",
    ".map",
    ".d.ts",
    ".pb.go",
    "_pb2.py",
    ".g.dart",
    ".lock",
)

_TEST_SEGMENTS = frozenset({"test", "tests", "spec", "specs", "__tests__", "testing"})
_CONFIG_EXTS = frozenset(
    {".toml", ".yaml", ".yml", ".ini", ".cfg", ".conf", ".properties", ".env", ".editorconfig"}
)
_DOC_EXTS = frozenset({".md", ".rst", ".adoc", ".txt"})
_DATA_EXTS = frozenset({".csv", ".tsv", ".parquet", ".pkl", ".npy", ".sqlite", ".db"})

_TEST_FILE_PATTERNS = (
    "test_*.py",
    "*_test.py",
    "*_test.go",
    "*_test.rs",
    "*.test.js",
    "*.test.ts",
    "*.test.tsx",
    "*.spec.js",
    "*.spec.ts",
    "*_test.cc",
    "*_test.cpp",
)
_TEST_NAME_PREFIXES = ("test_",)


@dataclass(frozen=True)
class ClassEvidence:
    file_class: FileClass
    rule: str


def classify(rel_posix: str) -> ClassEvidence:
    """Classify by repo-relative POSIX path. Pure + deterministic."""
    p = PurePosixPath(rel_posix.lower())
    parts = set(p.parts[:-1])
    name = p.name

    if parts & _VENDORED_SEGMENTS or name.endswith(_GENERATED_SUFFIXES[:4]) is False and False:
        return ClassEvidence(FileClass.VENDORED, "vendor_segment")
    if any(seg in _VENDORED_SEGMENTS for seg in p.parts):
        return ClassEvidence(FileClass.VENDORED, "vendor_segment")
    if parts & _GENERATED_SEGMENTS or name.endswith(_GENERATED_SUFFIXES):
        return ClassEvidence(FileClass.GENERATED, "generated_pattern")

    ext = p.suffix
    if name.startswith(_TEST_FILE_PATTERNS[:2][0]) or _matches_test_pattern(name):
        return ClassEvidence(FileClass.TEST, "test_filename")
    if parts & _TEST_SEGMENTS and ext in (
        ".py",
        ".go",
        ".js",
        ".jsx",
        ".ts",
        ".tsx",
        ".rs",
        ".java",
        ".rb",
        ".c",
        ".cpp",
    ):
        return ClassEvidence(FileClass.TEST, "test_dir")

    if ext in _DOC_EXTS:
        return ClassEvidence(FileClass.DOC, "doc_ext")
    if ext in _DATA_EXTS:
        return ClassEvidence(FileClass.DATA, "data_ext")
    if ext in _CONFIG_EXTS or name in {"dockerfile", "makefile", ".gitignore", ".mailmap"}:
        return ClassEvidence(FileClass.CONFIG, "config_name")

    if ext == ".lock":
        return ClassEvidence(FileClass.GENERATED, "lockfile")
    return ClassEvidence(FileClass.SOURCE, "default_source")


def _matches_test_pattern(name: str) -> bool:
    import fnmatch

    return any(fnmatch.fnmatch(name, pat) for pat in _TEST_FILE_PATTERNS)


def is_test_path(rel_posix: str) -> bool:
    return classify(rel_posix).file_class is FileClass.TEST


__all__ = ["ClassEvidence", "FileClass", "classify", "is_test_path"]
