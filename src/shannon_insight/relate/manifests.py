"""Ecosystem manifest readers (R2).

One pass over well-known manifest files builds the externals truth-source:
declared dependencies, workspace member maps, tsconfig path aliases, the Go
module prefix. Readers degrade individually — a malformed manifest never
fails the run (FM-lint: per-item isolation).

Enables the Knip-proven three-way dependency taxonomy:
  UNLISTED_EXTERNAL  imported, never declared      (phantom flavor A)
  UNUSED_DECLARED    declared, never imported       (dead-dependency fuel)
  EXTERNAL           declared AND imported          (healthy)
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ManifestFacts:
    declared: dict[str, frozenset[str]] = field(default_factory=dict)  # ecosystem -> names
    workspaces: dict[str, str] = field(default_factory=dict)  # pkg name -> dir posix
    ws_kind: dict[str, str] = field(default_factory=dict)  # pkg name -> npm|cargo
    tsconfig_paths: dict[str, tuple[str, ...]] = field(default_factory=dict)
    go_module: str | None = None
    go_modules: dict[str, str] = field(default_factory=dict)  # module path -> root dir posix
    self_names: frozenset[str] = field(default_factory=frozenset)


_MANIFEST_SKIP_DIRS = frozenset(
    {
        ".git",
        ".venv",
        "venv",
        "node_modules",
        "__pycache__",
        ".tox",
        ".mypy_cache",
        ".pytest_cache",
        ".shannon",
        "dist",
        "build",
        "target",
        "site-packages",
        "bower_components",
    }
)


def _manifest_rel_dirs(root: Path, max_depth: int = 3) -> list[str]:
    """Repo-root '' plus nested project dirs (bounded depth), deterministic."""
    out = [""]
    frontier = [""]
    for _ in range(max_depth):
        nxt: list[str] = []
        for d in frontier:
            base = root / d if d else root
            try:
                children = sorted(base.iterdir(), key=lambda p: p.name)
            except OSError:
                continue
            for child in children:
                if (
                    not child.is_dir()
                    or child.name.startswith(".")
                    or child.name in _MANIFEST_SKIP_DIRS
                ):
                    continue
                nxt.append(f"{d}/{child.name}" if d else child.name)
        out.extend(nxt)
        frontier = nxt
    return sorted(out)


def _prefix(rel_dir: str, value: str) -> str:
    return normalize_manifest_dir(f"{rel_dir}/{value}" if rel_dir else value)


def normalize_manifest_dir(path: str) -> str:
    parts: list[str] = []
    for piece in path.split("/"):
        if piece in ("", "."):
            continue
        if piece == "..":
            if parts and parts[-1] != "..":
                parts.pop()
            else:
                parts.append("..")
        else:
            parts.append(piece)
    return "/".join(parts)


def _read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def _strip_json_comments(text: str) -> str:
    out = []
    in_str = False
    esc = False
    i = 0
    while i < len(text):
        ch = text[i]
        if in_str:
            out.append(ch)
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            i += 1
            continue
        if ch == '"':
            in_str = True
            out.append(ch)
            i += 1
            continue
        if ch == "/" and i + 1 < len(text) and text[i + 1] == "/":
            while i < len(text) and text[i] != "\n":
                i += 1
            continue
        if ch == "/" and i + 1 < len(text) and text[i + 1] == "*":
            i += 2
            while i + 1 < len(text) and not (text[i] == "*" and text[i + 1] == "/"):
                i += 1
            i += 2
            continue
        out.append(ch)
        i += 1
    return "".join(out)


def _norm_dep(raw: str) -> str:
    return re.split(r"[<>=!\[\s;,]", raw.strip(), maxsplit=1)[0].lower()


def _read_package_json(root: Path, mf: ManifestFacts, rel_dir: str = "") -> None:
    raw = _read_text(root / rel_dir / "package.json")
    if raw is None:
        return
    try:
        data = json.loads(_strip_json_comments(raw))
    except json.JSONDecodeError:
        return
    if not isinstance(data, dict):
        return
    deps: set[str] = set()
    for key in ("dependencies", "devDependencies", "peerDependencies", "optionalDependencies"):
        section = data.get(key)
        if isinstance(section, dict):
            deps |= {str(k) for k in section}
    if deps:
        existing = set(mf.declared.get("npm", frozenset()))
        mf.declared["npm"] = frozenset(existing | deps)
    name = data.get("name")
    if isinstance(name, str):
        mf.workspaces.setdefault(name, rel_dir.rstrip("/") or ".")
        mf.ws_kind.setdefault(name, "npm")
        mf.self_names = mf.self_names | {name}
    ws = data.get("workspaces")
    if isinstance(ws, list):
        for entry in ws:
            if not isinstance(entry, str) or any(c in entry for c in "*?["):
                continue
            sub = entry.rstrip("/")
            _read_package_json(root, mf, f"{rel_dir}{sub}/".lstrip("/"))


def _read_pnpm_workspace(root: Path, mf: ManifestFacts) -> None:
    raw = _read_text(root / "pnpm-workspace.yaml")
    if raw is None:
        return
    in_packages = False
    for line in raw.splitlines():
        if line.startswith("packages:"):
            in_packages = True
            continue
        if in_packages:
            stripped = line.strip().strip("-\"' ")
            if not stripped:
                in_packages = False
                continue
            if not any(c in stripped for c in "*?["):
                _read_package_json(root, mf, stripped.rstrip("/") + "/")


def _read_tsconfig(root: Path, mf: ManifestFacts, rel_dir: str = "") -> None:
    for candidate in ("tsconfig.json", "jsconfig.json"):
        raw = _read_text(root / rel_dir / candidate if rel_dir else root / candidate)
        if raw is None:
            continue
        try:
            data = json.loads(_strip_json_comments(raw))
        except json.JSONDecodeError:
            continue
        opts = data.get("compilerOptions") if isinstance(data, dict) else None
        if not isinstance(opts, dict):
            continue
        paths = opts.get("paths")
        if isinstance(paths, dict):
            mapped = {
                str(k): tuple(_prefix(rel_dir, str(t)) for t in v if isinstance(t, str))
                for k, v in paths.items()
                if isinstance(v, list)
            }
            mf.tsconfig_paths.update(mapped)
        return


def _read_go_mod(root: Path, mf: ManifestFacts, rel_dir: str = "") -> None:
    raw = _read_text(root / rel_dir / "go.mod" if rel_dir else root / "go.mod")
    if raw is None:
        return
    m = re.search(r"^module\s+(\S+)", raw, re.M)
    if m:
        mf.go_modules.setdefault(m.group(1), rel_dir)
        if mf.go_module is None:
            mf.go_module = m.group(1)


def _read_cargo(root: Path, mf: ManifestFacts, rel_dir: str = "") -> None:
    raw = _read_text(root / rel_dir / "Cargo.toml" if rel_dir else root / "Cargo.toml")
    if raw is None:
        return
    section = None
    for line in raw.splitlines():
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            section = stripped[1:-1]
            continue
        if section == "package" and "=" in stripped:
            key, _, val = stripped.partition("=")
            if key.strip() == "name":
                name = val.strip().strip('"')
                mf.workspaces.setdefault(name, rel_dir)
                mf.ws_kind.setdefault(name, "cargo")
                mf.self_names = mf.self_names | {name}
        if section == "workspace" and stripped.startswith("members"):
            _, _, val = stripped.partition("=")
            for item in re.findall(r'"([^"]+)"', val):
                if not any(c in item for c in "*?["):
                    member_dir = normalize_manifest_dir(f"{rel_dir}/{item}" if rel_dir else item)
                    sub_raw = _read_text(root / member_dir / "Cargo.toml")
                    m = re.search(r'^\s*name\s*=\s*"([^"]+)"', sub_raw or "", re.M)
                    if m:
                        mf.workspaces.setdefault(m.group(1), member_dir)
                        mf.ws_kind.setdefault(m.group(1), "cargo")
        if section == "dependencies" and stripped and not stripped.startswith("#"):
            name = stripped.split("=")[0].strip().strip('"')
            if name:
                existing = set(mf.declared.get("crates", frozenset()))
                mf.declared["crates"] = frozenset(existing | {name})


def _read_pyproject(root: Path, mf: ManifestFacts, rel_dir: str = "") -> None:
    raw = _read_text(root / rel_dir / "pyproject.toml" if rel_dir else root / "pyproject.toml")
    if raw is None:
        return
    in_project = False
    in_deps = False
    for line in raw.splitlines():
        stripped = line.strip()
        if stripped.startswith("["):
            in_project = stripped == "[project]"
            in_deps = False
            continue
        if not in_project:
            continue
        if stripped.startswith("name"):
            _, _, val = stripped.partition("=")
            name = val.strip().strip("\"'")
            if name:
                mf.self_names = mf.self_names | {name}
        elif stripped.startswith("dependencies"):
            in_deps = "=" in stripped and "[" in stripped
            inline = re.findall(r'"([^"]+)"', stripped)
            if inline:
                existing = set(mf.declared.get("pypi", frozenset()))
                mf.declared["pypi"] = frozenset(existing | {_norm_dep(d) for d in inline})
        elif in_deps and stripped.startswith('"'):
            dep = stripped.strip('",')
            if dep:
                existing = set(mf.declared.get("pypi", frozenset()))
                mf.declared["pypi"] = frozenset(existing | {_norm_dep(dep)})


def _read_gemfile(root: Path, mf: ManifestFacts, rel_dir: str = "") -> None:
    raw = _read_text(root / rel_dir / "Gemfile" if rel_dir else root / "Gemfile")
    if raw is None:
        return
    gems = set(re.findall(r"""gem\s+["']([\w.\-]+)["']""", raw))
    if gems:
        existing = set(mf.declared.get("gems", frozenset()))
        mf.declared["gems"] = frozenset(existing | gems)


def read_manifests(root: Path) -> ManifestFacts:
    """Read every manifest found at root and in nested project dirs (depth 3).

    Per-manifest isolation: one malformed file never fails the pass.
    """
    mf = ManifestFacts()
    for rel_dir in _manifest_rel_dirs(root):
        _read_package_json(root, mf, f"{rel_dir}/" if rel_dir else "")
        _read_tsconfig(root, mf, rel_dir)
        _read_go_mod(root, mf, rel_dir)
        _read_cargo(root, mf, rel_dir)
        _read_pyproject(root, mf, rel_dir)
        _read_gemfile(root, mf, rel_dir)
    _read_pnpm_workspace(root, mf)
    return mf


__all__ = ["ManifestFacts", "read_manifests"]
