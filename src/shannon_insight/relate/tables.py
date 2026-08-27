"""Family tables: language semantics as DATA (seam ②).

One universal interpreter (interpreter.py) executes these tables. Adding a
language = adding a row here; touching zero engine code. The residual rows
are the irreducible semantic residue of each ecosystem's normative binding
specification (PEP-328, NodeJS RESOLVE_ALGORITHM, Go module identity,
JVM package⇄dir contract, Rust crate paths, C preprocessor inclusion).
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class FamilyTable:
    family: str
    languages: frozenset[str]

    #: applied to a base path (posix, extension-less): "{base}.py" ...
    file_templates: tuple[str, ...]
    #: how ImportDecl.module encodes relative position
    relative_style: str  # "dots" | "slash" | "crate" | "none"
    #: which directories count as import search roots
    search_roots: tuple[str, ...] = ("",)  # "" = repo root; "src" adds src-layout
    alias_sources: tuple[str, ...] = ()  # subset of {"tsconfig"}
    workspace_kind: str | None = None  # "npm" | "cargo" | None
    manifest_ecosystem: str = ""
    stdlib: frozenset[str] = field(default_factory=frozenset)
    stdlib_prefixes: tuple[str, ...] = ()  # e.g. java/jvm "java."
    dir_targets: bool = False  # imports bind to package DIRECTORIES (go/jvm-wildcard)
    dir_file_glob: str = ""  # "*.go" / "*.java" when dir_targets
    include_style: bool = False  # C: quoted-relative + angle-system duality
    loadpath_dirs: tuple[str, ...] = ()  # ruby: "", "lib"
    max_dir_files: int = 25  # safety cap for directory-target families


_PY_STDLIB = frozenset(
    """abc argparse array ast asyncio base64 binascii bisect builtins bz2 calendar
cmath cmd collections concurrent configparser contextlib contextvars copy
copyreg csv ctypes curses dataclasses datetime decimal difflib dis doctest
email enum errno faulthandler fileinput fnmatch fractions ftplib functools
gc getopt getpass gettext glob gzip hashlib heapq hmac html http imaplib
importlib inspect io ipaddress itertools json keyword linecache locale
logging lzma marshal math mimetypes mmap multiprocessing numbers operator
os pathlib pdb pickle pickletools pkgutil platform plistlib poplib posixpath
pprint profile pstats pty pwd py_compile pyclbr queue quopri random re
readline reprlib resource rlcompleter runpy sched secrets select selectors
shelve shlex shutil signal site smtplib socket socketserver sqlite3 ssl
stat statistics string stringprep struct subprocess symtable sys sysconfig
tarfile tempfile termios textwrap threading time timeit tkinter token
tokenize tomllib trace traceback tracemalloc tty types typing unicodedata
unittest urllib uuid venv warnings wave weakref webbrowser wsgiref xml
xmlrpc zipfile zipimport zlib zoneinfo""".split()
)

_JS_BUILTINS = frozenset(
    """assert buffer child_process cluster console constants crypto dgram
diagnostics_channel dns domain events fs http http2 https inspector module
net os path perf_hooks process punycode querystring readline repl stream
string_decoder timers tls trace_events tty url util v8 vm worker_threads zlib""".split()
)

_GO_STDLIB = frozenset(
    """archive bufio bytes cmp compress container crypto database debug dial
embed encoding errors expvar flag fmt go hash heap html image index io json
log maps math mime net os path plugin pprof reflect regexp runtime slices
sort strconv strings sync syscall testing text template time unicode unsafe
url utf8 websocket""".split()
)

_RUST_CORE = frozenset({"std", "core", "alloc", "proc_macro", "test"})

_RUBY_CORE = frozenset(
    """json set date time csv ostruct forwardable digest uri net http openssl
zlib stringio tempfile tmpdir pathname find etc io/console logger securerandom
shellwords singleton benchmark delegate drb erb error_highlight fiddle fiber
mutex_m nkf objspace observer open3 pstore psych racc rdoc readline resolv
ripper syslog win32ole""".split()
)


PYTHON = FamilyTable(
    family="python",
    languages=frozenset({"python"}),
    file_templates=("{base}.py", "{base}/__init__.py"),
    relative_style="dots",
    search_roots=("", "src"),
    manifest_ecosystem="pypi",
    stdlib=_PY_STDLIB,
)

NODE = FamilyTable(
    family="node",
    languages=frozenset({"javascript", "typescript", "tsx"}),
    file_templates=(
        "{base}",
        "{base}.ts",
        "{base}.tsx",
        "{base}.d.ts",
        "{base}.js",
        "{base}.jsx",
        "{base}/index.ts",
        "{base}/index.tsx",
        "{base}/index.js",
        "{base}.json",
    ),
    relative_style="slash",
    search_roots=("",),
    alias_sources=("tsconfig",),
    workspace_kind="npm",
    manifest_ecosystem="npm",
    stdlib=_JS_BUILTINS,
)

GO = FamilyTable(
    family="go",
    languages=frozenset({"go"}),
    file_templates=("{base}",),
    relative_style="none",
    search_roots=("",),
    manifest_ecosystem="gomod",
    stdlib=_GO_STDLIB,
    dir_targets=True,
    dir_file_glob="*.go",
)

JVM = FamilyTable(
    family="jvm",
    languages=frozenset({"java"}),
    file_templates=("{base}.java", "{base}.kt"),
    relative_style="none",
    search_roots=("",),
    manifest_ecosystem="maven",
    stdlib_prefixes=("java.", "javax.", "jdk.", "javafx.", "sun.", "com.sun."),
    dir_targets=True,
    dir_file_glob="*.java",
)

RUST = FamilyTable(
    family="rust",
    languages=frozenset({"rust"}),
    file_templates=("{base}.rs", "{base}/mod.rs"),
    relative_style="crate",
    search_roots=("",),
    workspace_kind="cargo",
    manifest_ecosystem="crates",
    stdlib=_RUST_CORE,
)

RUBY_C = FamilyTable(
    family="ruby_c",
    languages=frozenset({"ruby", "c", "cpp"}),
    file_templates=("{base}", "{base}.rb", "{base}.h"),
    relative_style="mixed",  # ruby require_relative slash-levels; C quoted-relative
    search_roots=("", "lib"),
    loadpath_dirs=("", "lib"),
    manifest_ecosystem="gems",
    stdlib=_RUBY_CORE,
    include_style=True,
)

FAMILIES: dict[str, FamilyTable] = {t.family: t for t in (PYTHON, NODE, GO, JVM, RUST, RUBY_C)}

_LANGUAGE_TO_FAMILY: dict[str, FamilyTable] = {}
for _t in FAMILIES.values():
    for _lang in _t.languages:
        _LANGUAGE_TO_FAMILY.setdefault(_lang, _t)


def table_for_language(language: str) -> FamilyTable:
    return _LANGUAGE_TO_FAMILY[language]


__all__ = ["FAMILIES", "FamilyTable", "table_for_language"]
