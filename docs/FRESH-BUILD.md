# Shannon Insight: Fresh Build Guide

**One document to build the entire system from scratch.**

This guide provides everything needed to implement Shannon Insight end-to-end: tensor core, algorithms, signals, finders, runtime, CLI, UI, and persistence.

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Project Structure](#2-project-structure)
3. [The Core Tensor](#3-the-core-tensor)
4. [Level 0-1: Extraction](#4-level-0-1-extraction)
5. [Level 2: Tensor Population](#5-level-2-tensor-population)
6. [Level 3: Graph Algorithms](#6-level-3-graph-algorithms)
7. [Level 4: Cross-Layer Analysis](#7-level-4-cross-layer-analysis)
8. [Level 5: Signal Fusion](#8-level-5-signal-fusion)
9. [Level 6: Finders](#9-level-6-finders)
10. [Runtime Kernel](#10-runtime-kernel)
11. [Persistence](#11-persistence)
12. [CLI](#12-cli)
13. [Server & UI](#13-server--ui)
14. [Testing Strategy](#14-testing-strategy)
15. [Implementation Order](#15-implementation-order)

---

## 1. Architecture Overview

### The Core Idea

Shannon Insight analyzes codebases by building a **4D relationship tensor**:

```
T ∈ ℝ^(N × N × K × R)

N = number of files
K = number of time windows (default 12 months)
R = 5 relationship types
```

### Data Flow

```
┌──────────────────────────────────────────────────────────────────────┐
│                         RAW INPUTS                                   │
│              Files on Disk    +    Git Repository                    │
└─────────────────────────────────┬────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    LEVEL 0-1: EXTRACTION                             │
│                                                                      │
│   syntax = parse(files)           commits = parse(git_log)          │
│   imports = extract(syntax)       changes = extract(git_numstat)    │
│   concepts = tfidf(identifiers)   authors = group_by_file(commits)  │
│                                                                      │
└─────────────────────────────────┬────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    LEVEL 2: TENSOR POPULATION                        │
│                                                                      │
│   T[:,:,t,0] ← resolved_imports      (IMPORT)                       │
│   T[:,:,t,1] ← cochange_lift         (COCHANGE)                     │
│   T[:,:,t,2] ← author_jaccard        (AUTHOR)                       │
│   T[:,:,t,3] ← concept_cosine        (SEMANTIC)                     │
│   T[:,:,t,4] ← weighted_sum          (COMBINED)                     │
│                                                                      │
└─────────────────────────────────┬────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    LEVEL 3-4: ALGORITHMS                             │
│                                                                      │
│   For each slice T[:,:,t,r]:                                        │
│     pagerank     = PowerIteration(slice)                            │
│     communities  = Louvain(slice)                                   │
│     eigenvalues  = SpectralDecomposition(Laplacian(slice))          │
│     cycles       = TarjanSCC(slice)                                 │
│     depth        = BFS(slice, entry_points)                         │
│     blast_radius = BFS(slice.T, each_node)                          │
│                                                                      │
│   Cross-layer:                                                       │
│     hidden_coupling = T[:,:,t,COCHANGE] - T[:,:,t,IMPORT]           │
│     conway_violations = T[:,:,t,IMPORT] * (1 - T[:,:,t,AUTHOR])     │
│                                                                      │
└─────────────────────────────────┬────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    LEVEL 5: SIGNAL FUSION                            │
│                                                                      │
│   For each file:                                                     │
│     Collect 36 raw signals                                          │
│     Normalize to percentiles (tier-aware)                           │
│     Compute composites (risk_score, health_score)                   │
│     Compute delta_h (health Laplacian)                              │
│                                                                      │
└─────────────────────────────────┬────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    LEVEL 6: FINDERS                                  │
│                                                                      │
│   For each file:                                                     │
│     Check 22 finder predicates                                      │
│     Emit Finding if condition matches                               │
│                                                                      │
└─────────────────────────────────┬────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────────┐
│                         OUTPUTS                                      │
│                                                                      │
│   CLI: JSON/text report, exit codes                                 │
│   Server: REST API + WebSocket                                      │
│   UI: React dashboard                                               │
│   Persistence: SQLite snapshots                                     │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

### The 5 Relationship Types

| R | Name | Weight Formula | Meaning |
|---|------|----------------|---------|
| 0 | IMPORT | 1.0 | File i imports file j |
| 1 | COCHANGE | lift = P(A∩B) / (P(A)×P(B)) | Temporal coupling |
| 2 | AUTHOR | Jaccard(authors_i, authors_j) | Team ownership |
| 3 | SEMANTIC | cosine(concepts_i, concepts_j) | Vocabulary similarity |
| 4 | COMBINED | 0.4×R0 + 0.3×R1 + 0.2×R2 + 0.1×R3 | Weighted fusion |

---

## 2. Project Structure

```
shannon-insight/
├── src/shannon_insight/
│   │
│   ├── tensor/                    # Core data structure
│   │   ├── __init__.py
│   │   ├── core.py               # RelationTensor class
│   │   ├── index.py              # NodeIndex (path ↔ int)
│   │   └── slicing.py            # Slice operations
│   │
│   ├── extract/                   # Level 0-1: Data extraction
│   │   ├── __init__.py
│   │   ├── syntax.py             # AST parsing → FileSyntax
│   │   ├── git.py                # Git log → Commits, FileChanges
│   │   ├── concepts.py           # TF-IDF → concept vectors
│   │   └── models.py             # FileSyntax, Commit, etc.
│   │
│   ├── populate/                  # Level 2: Fill tensor
│   │   ├── __init__.py
│   │   ├── imports.py            # T[:,:,t,0]
│   │   ├── cochange.py           # T[:,:,t,1]
│   │   ├── authors.py            # T[:,:,t,2]
│   │   ├── semantic.py           # T[:,:,t,3]
│   │   └── combined.py           # T[:,:,t,4]
│   │
│   ├── algorithms/                # Level 3: Graph algorithms
│   │   ├── __init__.py
│   │   ├── pagerank.py
│   │   ├── louvain.py
│   │   ├── spectral.py
│   │   ├── scc.py
│   │   ├── bfs.py
│   │   └── metrics.py            # Gini, etc.
│   │
│   ├── cross_layer/               # Level 4: Multi-graph analysis
│   │   ├── __init__.py
│   │   ├── hidden_coupling.py
│   │   ├── conway.py
│   │   ├── mutual_info.py
│   │   └── temporal.py           # Velocities, trends
│   │
│   ├── signals/                   # Level 5: Signal fusion
│   │   ├── __init__.py
│   │   ├── registry.py           # Signal enum
│   │   ├── models.py             # FileSignals, ModuleSignals
│   │   ├── normalization.py      # Percentiles, tiers
│   │   ├── composites.py         # risk_score, health_score
│   │   └── fusion.py             # Main computation
│   │
│   ├── finders/                   # Level 6: Pattern detection
│   │   ├── __init__.py
│   │   ├── base.py               # Finder protocol
│   │   ├── catalog.py            # All 22 finders
│   │   └── models.py             # Finding, Evidence
│   │
│   ├── kernel/                    # Runtime orchestration
│   │   ├── __init__.py
│   │   ├── runtime.py            # RuntimeKernel
│   │   ├── phases.py             # Phase enum, execution
│   │   ├── context.py            # RuntimeContext
│   │   └── result.py             # AnalysisResult
│   │
│   ├── persistence/               # Storage
│   │   ├── __init__.py
│   │   ├── database.py           # SQLite operations
│   │   ├── snapshot.py           # Snapshot model
│   │   └── diff.py               # Snapshot comparison
│   │
│   ├── server/                    # HTTP API + WebSocket
│   │   ├── __init__.py
│   │   ├── app.py                # Starlette app
│   │   ├── routes.py             # REST endpoints
│   │   ├── websocket.py          # Live updates
│   │   └── frontend/             # React SPA (built)
│   │
│   ├── cli/                       # Command-line interface
│   │   ├── __init__.py
│   │   ├── main.py               # Typer app entry
│   │   ├── analyze.py            # Main analysis command
│   │   ├── serve.py              # Server command
│   │   └── report.py             # Report generation
│   │
│   └── config.py                  # Pydantic settings
│
├── tests/
│   ├── fixtures/                  # Test codebases
│   ├── tensor/
│   ├── extract/
│   ├── populate/
│   ├── algorithms/
│   ├── signals/
│   ├── finders/
│   ├── kernel/
│   └── integration/
│
├── docs/
│   ├── FRESH-BUILD.md            # This file
│   └── architecture/
│       ├── TENSOR-ARCHITECTURE.md
│       └── MATH-DAG.md
│
└── pyproject.toml
```

---

## 3. The Core Tensor

### `tensor/core.py`

```python
"""Core 4D relationship tensor."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterator
import numpy as np
from scipy import sparse

# Relationship type constants
IMPORT = 0
COCHANGE = 1
AUTHOR = 2
SEMANTIC = 3
COMBINED = 4

RELATION_NAMES = ["IMPORT", "COCHANGE", "AUTHOR", "SEMANTIC", "COMBINED"]


@dataclass
class RelationTensor:
    """
    T ∈ ℝ^(N × N × K × R) stored as dict of sparse matrices.

    Storage: Dict[(t, r), csr_matrix] for efficient slicing.

    Usage:
        tensor = RelationTensor(n_files=100, n_windows=12)
        tensor.add_edge("a.py", "b.py", t=0, r=IMPORT, weight=1.0)

        # Get adjacency matrix for IMPORT at time 0
        A = tensor.slice(t=0, r=IMPORT)

        # Run PageRank
        pr = pagerank(A)
    """
    n_files: int
    n_windows: int = 12
    n_relations: int = 5

    # Node index: path ↔ int
    node_index: dict[str, int] = field(default_factory=dict)
    index_node: dict[int, str] = field(default_factory=dict)

    # Sparse storage: (t, r) → csr_matrix
    _slices: dict[tuple[int, int], sparse.csr_matrix] = field(default_factory=dict)

    # COO accumulator for building
    _coords: dict[tuple[int, int], list] = field(default_factory=dict)
    _values: dict[tuple[int, int], list] = field(default_factory=dict)
    _finalized: bool = False

    def register_node(self, path: str) -> int:
        """Register a file path and return its index."""
        if path not in self.node_index:
            idx = len(self.node_index)
            if idx >= self.n_files:
                raise ValueError(f"Exceeded n_files={self.n_files}")
            self.node_index[path] = idx
            self.index_node[idx] = path
        return self.node_index[path]

    def add_edge(self, src: str, dst: str, t: int, r: int, weight: float = 1.0):
        """Add weighted edge to tensor (accumulates, call finalize() when done)."""
        if self._finalized:
            raise RuntimeError("Tensor already finalized. Create new instance.")

        i = self.register_node(src)
        j = self.register_node(dst)

        key = (t, r)
        if key not in self._coords:
            self._coords[key] = []
            self._values[key] = []

        self._coords[key].append((i, j))
        self._values[key].append(weight)

    def finalize(self):
        """Convert COO accumulators to CSR matrices."""
        n = len(self.node_index)

        for (t, r), coords in self._coords.items():
            if not coords:
                continue
            rows, cols = zip(*coords)
            data = self._values[(t, r)]

            coo = sparse.coo_matrix(
                (data, (rows, cols)),
                shape=(n, n),
                dtype=np.float32
            )
            # Sum duplicates and convert to CSR
            self._slices[(t, r)] = coo.tocsr()

        # Clear accumulators
        self._coords.clear()
        self._values.clear()
        self._finalized = True

    def slice(self, t: int, r: int) -> sparse.csr_matrix:
        """Get adjacency matrix T[:,:,t,r]."""
        if not self._finalized:
            self.finalize()

        key = (t, r)
        if key in self._slices:
            return self._slices[key]

        # Return empty matrix
        n = len(self.node_index)
        return sparse.csr_matrix((n, n), dtype=np.float32)

    def slice_all_time(self, r: int) -> list[sparse.csr_matrix]:
        """Get T[:,:,:,r] as list of matrices for temporal analysis."""
        return [self.slice(t, r) for t in range(self.n_windows)]

    def slice_all_relations(self, t: int) -> list[sparse.csr_matrix]:
        """Get T[:,:,t,:] as list of matrices for cross-layer analysis."""
        return [self.slice(t, r) for r in range(self.n_relations)]

    @property
    def n_nodes(self) -> int:
        return len(self.node_index)

    @property
    def n_edges(self) -> int:
        return sum(m.nnz for m in self._slices.values())

    def edge_density(self, t: int, r: int) -> float:
        """Fraction of possible edges that exist."""
        n = self.n_nodes
        if n < 2:
            return 0.0
        return self.slice(t, r).nnz / (n * (n - 1))
```

### `tensor/index.py`

```python
"""Node indexing utilities."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class NodeIndex:
    """Bidirectional mapping between file paths and integer indices."""

    _path_to_idx: dict[str, int]
    _idx_to_path: dict[int, str]

    @classmethod
    def from_paths(cls, paths: list[str]) -> NodeIndex:
        """Create index from sorted list of paths."""
        sorted_paths = sorted(paths)
        path_to_idx = {p: i for i, p in enumerate(sorted_paths)}
        idx_to_path = {i: p for p, i in path_to_idx.items()}
        return cls(path_to_idx, idx_to_path)

    def __len__(self) -> int:
        return len(self._path_to_idx)

    def __getitem__(self, key: str | int) -> int | str:
        if isinstance(key, str):
            return self._path_to_idx[key]
        return self._idx_to_path[key]

    def __contains__(self, path: str) -> bool:
        return path in self._path_to_idx

    def paths(self) -> list[str]:
        return [self._idx_to_path[i] for i in range(len(self))]
```

---

## 4. Level 0-1: Extraction

### `extract/models.py`

```python
"""Extraction data models."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


@dataclass(frozen=True)
class Function:
    name: str
    params: int
    body_tokens: int
    signature_tokens: int
    nesting_depth: int
    start_line: int
    end_line: int

    @property
    def is_stub(self) -> bool:
        return self.body_tokens < 5


@dataclass(frozen=True)
class Import:
    module: str
    names: tuple[str, ...]
    level: int  # 0 = absolute, 1+ = relative
    line: int

    @property
    def is_relative(self) -> bool:
        return self.level > 0


@dataclass
class FileSyntax:
    path: str
    language: str
    content_hash: str
    lines: int
    functions: list[Function]
    classes: list[str]
    imports: list[Import]
    identifiers: frozenset[str]
    complexity: int
    max_nesting: int
    has_main_guard: bool = False

    @property
    def function_count(self) -> int:
        return len(self.functions)

    @property
    def class_count(self) -> int:
        return len(self.classes)

    @property
    def import_count(self) -> int:
        return len(self.imports)

    @property
    def stub_ratio(self) -> float:
        if not self.functions:
            return 0.0
        return sum(1 for f in self.functions if f.is_stub) / len(self.functions)

    @property
    def impl_gini(self) -> float:
        """Gini coefficient of function body sizes."""
        if len(self.functions) < 2:
            return 0.0
        sizes = sorted(f.body_tokens for f in self.functions)
        n = len(sizes)
        total = sum(sizes)
        if total == 0:
            return 0.0
        return (2 * sum(i * s for i, s in enumerate(sizes, 1))) / (n * total) - (n + 1) / n


@dataclass(frozen=True)
class Commit:
    hash: str
    timestamp: int  # Unix seconds
    author: str
    subject: str
    files: tuple[str, ...]

    @property
    def is_fix(self) -> bool:
        s = self.subject.lower()
        return any(kw in s for kw in ["fix", "bug", "patch", "issue", "error"])

    @property
    def is_refactor(self) -> bool:
        s = self.subject.lower()
        return any(kw in s for kw in ["refactor", "clean", "rename", "move"])


@dataclass(frozen=True)
class FileChange:
    commit_hash: str
    path: str
    change_type: Literal["A", "M", "D", "R"]
    additions: int = 0
    deletions: int = 0
    old_path: str | None = None  # For renames


@dataclass
class GitHistory:
    commits: list[Commit]
    changes: list[FileChange]

    @property
    def total_commits(self) -> int:
        return len(self.commits)

    def changes_for_file(self, path: str) -> list[FileChange]:
        return [c for c in self.changes if c.path == path]

    def files_in_commit(self, commit_hash: str) -> list[str]:
        return [c.path for c in self.changes if c.commit_hash == commit_hash]
```

### `extract/syntax.py`

```python
"""Syntax extraction from source files."""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

from .models import FileSyntax, Function, Import

# Language detection by extension
LANG_MAP = {
    ".py": "python",
    ".go": "go",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".js": "javascript",
    ".jsx": "javascript",
    ".java": "java",
    ".rs": "rust",
    ".rb": "ruby",
    ".c": "c",
    ".cpp": "cpp",
    ".h": "c",
    ".hpp": "cpp",
}


def detect_language(path: str) -> str:
    """Detect language from file extension."""
    suffix = Path(path).suffix.lower()
    return LANG_MAP.get(suffix, "unknown")


def extract_syntax(path: str, content: bytes) -> FileSyntax:
    """Extract syntax information from file content."""
    text = content.decode("utf-8", errors="replace")
    content_hash = hashlib.sha256(content).hexdigest()
    language = detect_language(path)

    lines = text.count("\n") + 1

    # Language-specific extraction
    if language == "python":
        return _extract_python(path, text, content_hash, lines)
    else:
        return _extract_generic(path, text, content_hash, lines, language)


def _extract_python(path: str, text: str, content_hash: str, lines: int) -> FileSyntax:
    """Extract syntax from Python file."""
    import ast

    try:
        tree = ast.parse(text)
    except SyntaxError:
        return _extract_generic(path, text, content_hash, lines, "python")

    functions = []
    classes = []
    imports = []
    identifiers = set()
    max_nesting = 0
    complexity = 1
    has_main_guard = False

    for node in ast.walk(tree):
        # Functions
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            body_tokens = sum(1 for _ in ast.walk(node)) - 1
            sig_tokens = len(node.args.args) + len(node.args.kwonlyargs)
            functions.append(Function(
                name=node.name,
                params=len(node.args.args),
                body_tokens=body_tokens,
                signature_tokens=sig_tokens,
                nesting_depth=0,  # Simplified
                start_line=node.lineno,
                end_line=node.end_lineno or node.lineno,
            ))
            identifiers.add(node.name)

        # Classes
        elif isinstance(node, ast.ClassDef):
            classes.append(node.name)
            identifiers.add(node.name)

        # Imports
        elif isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(Import(
                    module=alias.name,
                    names=(),
                    level=0,
                    line=node.lineno,
                ))
        elif isinstance(node, ast.ImportFrom):
            imports.append(Import(
                module=node.module or "",
                names=tuple(a.name for a in node.names),
                level=node.level,
                line=node.lineno,
            ))

        # Complexity
        elif isinstance(node, (ast.If, ast.For, ast.While, ast.Try, ast.ExceptHandler)):
            complexity += 1
        elif isinstance(node, ast.BoolOp):
            complexity += len(node.values) - 1

        # Names
        elif isinstance(node, ast.Name):
            identifiers.add(node.id)

    # Check for if __name__ == "__main__"
    for node in ast.walk(tree):
        if isinstance(node, ast.If):
            if isinstance(node.test, ast.Compare):
                if any(isinstance(c, ast.Str) and c.s == "__main__" for c in node.test.comparators):
                    has_main_guard = True
                    break

    return FileSyntax(
        path=path,
        language="python",
        content_hash=content_hash,
        lines=lines,
        functions=functions,
        classes=classes,
        imports=imports,
        identifiers=frozenset(identifiers),
        complexity=complexity,
        max_nesting=max_nesting,
        has_main_guard=has_main_guard,
    )


def _extract_generic(path: str, text: str, content_hash: str, lines: int, language: str) -> FileSyntax:
    """Fallback regex-based extraction."""
    # Simple patterns
    func_pattern = re.compile(r'\b(?:def|func|function|fn)\s+(\w+)')
    class_pattern = re.compile(r'\bclass\s+(\w+)')
    import_pattern = re.compile(r'(?:import|from|require|use)\s+["\']?(\w+)')

    functions = [
        Function(name=m.group(1), params=0, body_tokens=10, signature_tokens=2,
                 nesting_depth=0, start_line=0, end_line=0)
        for m in func_pattern.finditer(text)
    ]
    classes = [m.group(1) for m in class_pattern.finditer(text)]
    imports = [
        Import(module=m.group(1), names=(), level=0, line=0)
        for m in import_pattern.finditer(text)
    ]
    identifiers = frozenset(re.findall(r'\b[a-zA-Z_]\w*\b', text))

    return FileSyntax(
        path=path,
        language=language,
        content_hash=content_hash,
        lines=lines,
        functions=functions,
        classes=classes,
        imports=imports,
        identifiers=identifiers,
        complexity=1,
        max_nesting=0,
        has_main_guard=False,
    )
```

### `extract/git.py`

```python
"""Git history extraction."""
from __future__ import annotations

import subprocess
from pathlib import Path

from .models import Commit, FileChange, GitHistory


def extract_git_history(repo_path: Path, max_commits: int = 10000) -> GitHistory:
    """Extract commits and file changes from git repository."""
    commits = _parse_commits(repo_path, max_commits)
    changes = _parse_changes(repo_path, max_commits)
    return GitHistory(commits=commits, changes=changes)


def _parse_commits(repo_path: Path, max_commits: int) -> list[Commit]:
    """Parse git log for commit metadata."""
    cmd = [
        "git", "-C", str(repo_path), "log",
        f"-n{max_commits}",
        "--format=%H|%at|%ae|%s",
        "--name-only",
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return []

    commits = []
    current_hash = None
    current_ts = 0
    current_author = ""
    current_subject = ""
    current_files = []

    for line in result.stdout.strip().split("\n"):
        if "|" in line and line.count("|") == 3:
            # Save previous commit
            if current_hash:
                commits.append(Commit(
                    hash=current_hash,
                    timestamp=current_ts,
                    author=current_author,
                    subject=current_subject,
                    files=tuple(current_files),
                ))

            # Parse new commit
            parts = line.split("|", 3)
            current_hash = parts[0]
            current_ts = int(parts[1]) if parts[1].isdigit() else 0
            current_author = parts[2]
            current_subject = parts[3]
            current_files = []
        elif line.strip():
            current_files.append(line.strip())

    # Save last commit
    if current_hash:
        commits.append(Commit(
            hash=current_hash,
            timestamp=current_ts,
            author=current_author,
            subject=current_subject,
            files=tuple(current_files),
        ))

    return commits


def _parse_changes(repo_path: Path, max_commits: int) -> list[FileChange]:
    """Parse git log --numstat for file changes."""
    cmd = [
        "git", "-C", str(repo_path), "log",
        f"-n{max_commits}",
        "--format=%H",
        "--numstat",
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return []

    changes = []
    current_hash = ""

    for line in result.stdout.strip().split("\n"):
        line = line.strip()
        if not line:
            continue

        if len(line) == 40 and all(c in "0123456789abcdef" for c in line):
            current_hash = line
        elif "\t" in line and current_hash:
            parts = line.split("\t")
            if len(parts) >= 3:
                add_str, del_str, path = parts[0], parts[1], parts[2]
                additions = int(add_str) if add_str.isdigit() else 0
                deletions = int(del_str) if del_str.isdigit() else 0
                changes.append(FileChange(
                    commit_hash=current_hash,
                    path=path,
                    change_type="M",
                    additions=additions,
                    deletions=deletions,
                ))

    return changes
```

### `extract/concepts.py`

```python
"""Concept extraction using TF-IDF."""
from __future__ import annotations

import math
import re
from collections import Counter


def tokenize_identifiers(identifiers: frozenset[str]) -> list[str]:
    """Split identifiers into tokens."""
    tokens = []
    for ident in identifiers:
        # Split camelCase
        parts = re.sub(r'([a-z])([A-Z])', r'\1_\2', ident)
        # Split on underscores
        for part in parts.split("_"):
            if part and len(part) > 1:
                tokens.append(part.lower())
    return tokens


def compute_tfidf(
    documents: dict[str, frozenset[str]]
) -> tuple[dict[str, dict[str, float]], dict[str, list[tuple[str, float]]]]:
    """
    Compute TF-IDF vectors for documents.

    Returns:
        - tfidf_vectors: {path: {term: score}}
        - concepts: {path: [(term, score), ...]}  # Top 10
    """
    # Tokenize all documents
    doc_tokens: dict[str, list[str]] = {}
    for path, identifiers in documents.items():
        doc_tokens[path] = tokenize_identifiers(identifiers)

    # Compute document frequencies
    df: Counter[str] = Counter()
    for tokens in doc_tokens.values():
        df.update(set(tokens))

    n_docs = len(documents)
    idf = {term: math.log(n_docs / count) for term, count in df.items()}

    # Compute TF-IDF
    tfidf_vectors: dict[str, dict[str, float]] = {}
    concepts: dict[str, list[tuple[str, float]]] = {}

    for path, tokens in doc_tokens.items():
        if not tokens:
            tfidf_vectors[path] = {}
            concepts[path] = []
            continue

        tf = Counter(tokens)
        total = len(tokens)

        tfidf = {}
        for term, count in tf.items():
            tfidf[term] = (count / total) * idf.get(term, 0)

        tfidf_vectors[path] = tfidf

        # Top 10 concepts
        sorted_terms = sorted(tfidf.items(), key=lambda x: -x[1])[:10]
        concepts[path] = sorted_terms

    return tfidf_vectors, concepts


def cosine_similarity(vec_a: dict[str, float], vec_b: dict[str, float]) -> float:
    """Compute cosine similarity between two sparse vectors."""
    if not vec_a or not vec_b:
        return 0.0

    # Dot product
    common = set(vec_a.keys()) & set(vec_b.keys())
    dot = sum(vec_a[k] * vec_b[k] for k in common)

    # Norms
    norm_a = math.sqrt(sum(v * v for v in vec_a.values()))
    norm_b = math.sqrt(sum(v * v for v in vec_b.values()))

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot / (norm_a * norm_b)
```

---

## 5. Level 2: Tensor Population

### `populate/imports.py`

```python
"""Populate IMPORT layer (R=0)."""
from __future__ import annotations

from pathlib import Path

from ..tensor.core import RelationTensor, IMPORT
from ..extract.models import FileSyntax


def resolve_import(imp, source_path: str, file_set: set[str]) -> str | None:
    """Resolve import to target file path."""
    source_dir = str(Path(source_path).parent)

    if imp.is_relative:
        # Relative import
        target_dir = source_dir
        for _ in range(imp.level - 1):
            target_dir = str(Path(target_dir).parent)

        if imp.module:
            candidates = [
                f"{target_dir}/{imp.module.replace('.', '/')}.py",
                f"{target_dir}/{imp.module.replace('.', '/')}/__init__.py",
            ]
        else:
            candidates = [f"{target_dir}/__init__.py"]
    else:
        # Absolute import
        module_path = imp.module.replace(".", "/")
        candidates = [
            f"{module_path}.py",
            f"{module_path}/__init__.py",
            f"src/{module_path}.py",
            f"src/{module_path}/__init__.py",
        ]

    for candidate in candidates:
        # Normalize
        normalized = str(Path(candidate))
        if normalized in file_set:
            return normalized

    return None


def populate_imports(
    tensor: RelationTensor,
    syntax_map: dict[str, FileSyntax],
    t: int = -1,
):
    """Fill T[:,:,t,IMPORT] from resolved imports."""
    file_set = set(syntax_map.keys())

    # Use last time window if -1
    if t == -1:
        t = tensor.n_windows - 1

    for source_path, syntax in syntax_map.items():
        for imp in syntax.imports:
            target = resolve_import(imp, source_path, file_set)
            if target and target != source_path:
                tensor.add_edge(source_path, target, t, IMPORT, weight=1.0)
```

### `populate/cochange.py`

```python
"""Populate COCHANGE layer (R=1)."""
from __future__ import annotations

import math
from collections import Counter, defaultdict
from itertools import combinations

from ..tensor.core import RelationTensor, COCHANGE
from ..extract.models import GitHistory


# 90-day half-life
DECAY_LAMBDA = math.log(2) / 90


def populate_cochange(
    tensor: RelationTensor,
    git_history: GitHistory,
    now_timestamp: int,
    window_days: int = 30,
):
    """Fill T[:,:,t,COCHANGE] with lift scores."""
    # Group commits by time window
    window_seconds = window_days * 86400
    min_ts = min(c.timestamp for c in git_history.commits) if git_history.commits else now_timestamp

    # Count co-occurrences with decay
    cochange_counts: Counter[tuple[str, str]] = Counter()
    file_counts: Counter[str] = Counter()
    total_weight = 0.0

    for commit in git_history.commits:
        # Skip bulk commits
        if len(commit.files) > 50:
            continue

        days_ago = (now_timestamp - commit.timestamp) / 86400
        weight = math.exp(-DECAY_LAMBDA * days_ago)

        for f in commit.files:
            file_counts[f] += weight

        for a, b in combinations(sorted(commit.files), 2):
            cochange_counts[(a, b)] += weight

        total_weight += weight

    if total_weight == 0:
        return

    # Compute lift and populate tensor
    min_count = 3

    for (a, b), count in cochange_counts.items():
        if count < min_count:
            continue

        p_ab = count / total_weight
        p_a = file_counts[a] / total_weight
        p_b = file_counts[b] / total_weight

        if p_a == 0 or p_b == 0:
            continue

        lift = p_ab / (p_a * p_b)

        if lift > 1.0:
            # Determine time window
            t = tensor.n_windows - 1  # Current window

            tensor.add_edge(a, b, t, COCHANGE, weight=lift)
            tensor.add_edge(b, a, t, COCHANGE, weight=lift)  # Symmetric
```

### `populate/authors.py`

```python
"""Populate AUTHOR layer (R=2)."""
from __future__ import annotations

from collections import defaultdict
from itertools import combinations

from ..tensor.core import RelationTensor, AUTHOR
from ..extract.models import GitHistory


def populate_authors(
    tensor: RelationTensor,
    git_history: GitHistory,
    min_jaccard: float = 0.1,
):
    """Fill T[:,:,t,AUTHOR] with Jaccard similarity."""
    # Build author sets per file
    authors_per_file: dict[str, set[str]] = defaultdict(set)

    for commit in git_history.commits:
        for f in commit.files:
            authors_per_file[f].add(commit.author)

    # Compute pairwise Jaccard
    files = list(authors_per_file.keys())
    t = tensor.n_windows - 1

    for a, b in combinations(files, 2):
        authors_a = authors_per_file[a]
        authors_b = authors_per_file[b]

        intersection = len(authors_a & authors_b)
        union = len(authors_a | authors_b)

        if union == 0:
            continue

        jaccard = intersection / union

        if jaccard >= min_jaccard:
            tensor.add_edge(a, b, t, AUTHOR, weight=jaccard)
            tensor.add_edge(b, a, t, AUTHOR, weight=jaccard)
```

### `populate/semantic.py`

```python
"""Populate SEMANTIC layer (R=3)."""
from __future__ import annotations

from itertools import combinations

from ..tensor.core import RelationTensor, SEMANTIC
from ..extract.concepts import cosine_similarity


def populate_semantic(
    tensor: RelationTensor,
    tfidf_vectors: dict[str, dict[str, float]],
    min_cosine: float = 0.3,
    max_neighbors: int = 10,
):
    """Fill T[:,:,t,SEMANTIC] with cosine similarity."""
    files = list(tfidf_vectors.keys())
    t = tensor.n_windows - 1

    # For each file, find top-k most similar
    for a in files:
        vec_a = tfidf_vectors[a]
        if not vec_a:
            continue

        similarities = []
        for b in files:
            if a == b:
                continue
            vec_b = tfidf_vectors[b]
            if not vec_b:
                continue

            sim = cosine_similarity(vec_a, vec_b)
            if sim >= min_cosine:
                similarities.append((b, sim))

        # Keep top-k
        similarities.sort(key=lambda x: -x[1])
        for b, sim in similarities[:max_neighbors]:
            tensor.add_edge(a, b, t, SEMANTIC, weight=sim)
```

### `populate/combined.py`

```python
"""Populate COMBINED layer (R=4)."""
from __future__ import annotations

from ..tensor.core import RelationTensor, IMPORT, COCHANGE, AUTHOR, SEMANTIC, COMBINED


def populate_combined(
    tensor: RelationTensor,
    weights: tuple[float, float, float, float] = (0.4, 0.3, 0.2, 0.1),
):
    """Fill T[:,:,t,COMBINED] as weighted sum of other layers."""
    tensor.finalize()  # Ensure slices are built

    w_import, w_cochange, w_author, w_semantic = weights

    for t in range(tensor.n_windows):
        # Get all slices
        A_import = tensor.slice(t, IMPORT)
        A_cochange = tensor.slice(t, COCHANGE)
        A_author = tensor.slice(t, AUTHOR)
        A_semantic = tensor.slice(t, SEMANTIC)

        # Weighted sum (sparse)
        A_combined = (
            w_import * A_import +
            w_cochange * A_cochange +
            w_author * A_author +
            w_semantic * A_semantic
        )

        # Store in tensor (need to unfinilaize and re-add)
        # For simplicity, store directly
        tensor._slices[(t, COMBINED)] = A_combined.tocsr()
```

---

## 6. Level 3: Graph Algorithms

### `algorithms/pagerank.py`

```python
"""PageRank algorithm."""
from __future__ import annotations

import numpy as np
from scipy import sparse


def pagerank(
    A: sparse.csr_matrix,
    damping: float = 0.85,
    max_iterations: int = 50,
    tolerance: float = 1e-6,
) -> np.ndarray:
    """
    Compute PageRank scores.

    Args:
        A: Adjacency matrix (N x N)
        damping: Damping factor (default 0.85)
        max_iterations: Maximum iterations
        tolerance: Convergence threshold

    Returns:
        Array of PageRank scores (length N)
    """
    n = A.shape[0]
    if n == 0:
        return np.array([])

    # Out-degree
    out_degree = np.array(A.sum(axis=1)).flatten()
    dangling = out_degree == 0
    out_degree[dangling] = 1  # Avoid division by zero

    # Row-normalize
    D_inv = sparse.diags(1.0 / out_degree)
    M = D_inv @ A

    # Initialize
    pr = np.ones(n) / n

    for _ in range(max_iterations):
        # Dangling node contribution
        dangling_sum = pr[dangling].sum() / n

        # PageRank iteration
        pr_new = (1 - damping) / n + damping * (M.T @ pr + dangling_sum)

        # Check convergence
        if np.max(np.abs(pr_new - pr)) < tolerance:
            break

        pr = pr_new

    return pr
```

### `algorithms/louvain.py`

```python
"""Louvain community detection."""
from __future__ import annotations

import numpy as np
from scipy import sparse
from collections import defaultdict


def louvain(
    A: sparse.csr_matrix,
    resolution: float = 1.0,
) -> tuple[dict[int, int], float]:
    """
    Louvain community detection.

    Args:
        A: Adjacency matrix (symmetric, weighted)
        resolution: Resolution parameter (higher = smaller communities)

    Returns:
        - community: {node_idx: community_id}
        - modularity: Q score
    """
    n = A.shape[0]
    if n == 0:
        return {}, 0.0

    # Make symmetric
    A = (A + A.T) / 2

    # Total edge weight
    m = A.sum() / 2
    if m == 0:
        return {i: i for i in range(n)}, 0.0

    # Degree
    k = np.array(A.sum(axis=1)).flatten()

    # Initialize: each node in own community
    community = {i: i for i in range(n)}

    # Phase 1: Local moving
    improved = True
    while improved:
        improved = False
        nodes = list(range(n))
        np.random.shuffle(nodes)

        for i in nodes:
            current_comm = community[i]

            # Find neighbors' communities
            neighbors = A[i].nonzero()[1]
            neighbor_comms = set(community[j] for j in neighbors)
            neighbor_comms.add(current_comm)

            best_comm = current_comm
            best_delta = 0.0

            for c in neighbor_comms:
                if c == current_comm:
                    continue

                # Compute modularity gain
                delta = _modularity_gain(A, k, m, i, c, community, resolution)
                if delta > best_delta:
                    best_delta = delta
                    best_comm = c

            if best_comm != current_comm:
                community[i] = best_comm
                improved = True

    # Renumber communities
    unique_comms = sorted(set(community.values()))
    comm_map = {c: i for i, c in enumerate(unique_comms)}
    community = {i: comm_map[c] for i, c in community.items()}

    # Compute final modularity
    Q = _compute_modularity(A, k, m, community, resolution)

    return community, Q


def _modularity_gain(A, k, m, i, target_comm, community, resolution):
    """Compute modularity gain from moving node i to target_comm."""
    # Sum of weights from i to target community
    k_i_in = sum(A[i, j] for j in range(A.shape[0]) if community[j] == target_comm)

    # Sum of degrees in target community
    sum_tot = sum(k[j] for j in range(A.shape[0]) if community[j] == target_comm)

    return k_i_in - resolution * k[i] * sum_tot / (2 * m)


def _compute_modularity(A, k, m, community, resolution):
    """Compute modularity Q."""
    Q = 0.0
    for i in range(A.shape[0]):
        for j in range(A.shape[0]):
            if community[i] == community[j]:
                Q += A[i, j] - resolution * k[i] * k[j] / (2 * m)
    return Q / (2 * m)
```

### `algorithms/spectral.py`

```python
"""Spectral graph analysis."""
from __future__ import annotations

import numpy as np
from scipy import sparse
from scipy.sparse.linalg import eigsh


def spectral_analysis(
    A: sparse.csr_matrix,
    k: int = 10,
) -> tuple[float, float, np.ndarray]:
    """
    Compute spectral properties of graph.

    Args:
        A: Adjacency matrix
        k: Number of eigenvalues to compute

    Returns:
        - fiedler_value: Second smallest eigenvalue (algebraic connectivity)
        - spectral_gap: λ₃ - λ₂
        - eigenvalues: First k eigenvalues
    """
    n = A.shape[0]
    if n < 3:
        return 0.0, 0.0, np.array([])

    # Compute Laplacian
    D = sparse.diags(np.array(A.sum(axis=1)).flatten())
    L = D - A

    # Compute smallest eigenvalues
    k = min(k, n - 1)
    try:
        eigenvalues, _ = eigsh(L, k=k, which='SM')
        eigenvalues = np.sort(eigenvalues)
    except Exception:
        return 0.0, 0.0, np.array([])

    # Fiedler value (λ₂)
    fiedler = eigenvalues[1] if len(eigenvalues) > 1 else 0.0

    # Spectral gap (λ₃ - λ₂)
    gap = (eigenvalues[2] - eigenvalues[1]) if len(eigenvalues) > 2 else 0.0

    return fiedler, gap, eigenvalues
```

### `algorithms/scc.py`

```python
"""Strongly connected components (Tarjan's algorithm)."""
from __future__ import annotations

from scipy import sparse


def tarjan_scc(A: sparse.csr_matrix) -> list[set[int]]:
    """
    Find strongly connected components.

    Args:
        A: Adjacency matrix (directed)

    Returns:
        List of SCCs, each as a set of node indices
    """
    n = A.shape[0]
    if n == 0:
        return []

    index_counter = [0]
    stack = []
    lowlinks = {}
    index = {}
    on_stack = set()
    sccs = []

    def strongconnect(v):
        index[v] = index_counter[0]
        lowlinks[v] = index_counter[0]
        index_counter[0] += 1
        stack.append(v)
        on_stack.add(v)

        # Visit successors
        for w in A[v].nonzero()[1]:
            if w not in index:
                strongconnect(w)
                lowlinks[v] = min(lowlinks[v], lowlinks[w])
            elif w in on_stack:
                lowlinks[v] = min(lowlinks[v], index[w])

        # Root of SCC
        if lowlinks[v] == index[v]:
            scc = set()
            while True:
                w = stack.pop()
                on_stack.remove(w)
                scc.add(w)
                if w == v:
                    break
            sccs.append(scc)

    for v in range(n):
        if v not in index:
            strongconnect(v)

    return sccs


def find_cycles(A: sparse.csr_matrix) -> tuple[list[set[int]], dict[int, bool]]:
    """
    Find SCCs and mark nodes in cycles.

    Returns:
        - cycles: List of SCCs with size > 1
        - cycle_member: {node: True if in a cycle}
    """
    sccs = tarjan_scc(A)
    cycles = [scc for scc in sccs if len(scc) > 1]

    cycle_member = {}
    for i in range(A.shape[0]):
        cycle_member[i] = any(i in scc for scc in cycles)

    return cycles, cycle_member
```

### `algorithms/bfs.py`

```python
"""BFS-based algorithms."""
from __future__ import annotations

from collections import deque
import numpy as np
from scipy import sparse


def bfs_depth(
    A: sparse.csr_matrix,
    sources: set[int],
) -> dict[int, int]:
    """
    Compute shortest path distance from sources to all nodes.

    Args:
        A: Adjacency matrix
        sources: Set of source node indices

    Returns:
        {node: depth} where depth = -1 if unreachable
    """
    n = A.shape[0]
    depth = {i: -1 for i in range(n)}

    queue = deque()
    for s in sources:
        depth[s] = 0
        queue.append(s)

    while queue:
        u = queue.popleft()
        for v in A[u].nonzero()[1]:
            if depth[v] == -1:
                depth[v] = depth[u] + 1
                queue.append(v)

    return depth


def blast_radius(A: sparse.csr_matrix) -> dict[int, set[int]]:
    """
    Compute blast radius for each node (who is affected if this changes).

    Uses reverse edges: if A→B, then changing B affects A.
    """
    A_T = A.T.tocsr()
    n = A.shape[0]

    result = {}
    for v in range(n):
        # BFS from v on reversed graph
        visited = set()
        queue = deque([v])
        while queue:
            u = queue.popleft()
            for w in A_T[u].nonzero()[1]:
                if w not in visited and w != v:
                    visited.add(w)
                    queue.append(w)
        result[v] = visited

    return result
```

### `algorithms/metrics.py`

```python
"""Statistical metrics."""
from __future__ import annotations

import numpy as np


def gini(values: np.ndarray) -> float:
    """
    Compute Gini coefficient.

    Args:
        values: Array of non-negative values

    Returns:
        Gini coefficient in [0, 1]
    """
    if len(values) == 0:
        return 0.0

    values = np.sort(values)
    n = len(values)
    total = values.sum()

    if total == 0:
        return 0.0

    # G = (2 × Σ i × x_i) / (n × Σ x_i) - (n+1)/n
    weighted_sum = sum(i * v for i, v in enumerate(values, 1))
    return (2 * weighted_sum) / (n * total) - (n + 1) / n


def entropy(distribution: dict[str, float]) -> float:
    """
    Compute Shannon entropy.

    Args:
        distribution: {category: count/weight}

    Returns:
        Entropy in bits
    """
    total = sum(distribution.values())
    if total == 0:
        return 0.0

    H = 0.0
    for count in distribution.values():
        if count > 0:
            p = count / total
            H -= p * np.log2(p)

    return H
```

---

## 7. Level 4: Cross-Layer Analysis

### `cross_layer/hidden_coupling.py`

```python
"""Hidden coupling detection."""
from __future__ import annotations

from scipy import sparse

from ..tensor.core import RelationTensor, IMPORT, COCHANGE


def find_hidden_coupling(
    tensor: RelationTensor,
    t: int = -1,
    threshold: float = 1.5,
) -> list[tuple[int, int, float]]:
    """
    Find file pairs that co-change but don't import.

    Returns:
        List of (src, dst, lift) tuples
    """
    if t == -1:
        t = tensor.n_windows - 1

    A_import = tensor.slice(t, IMPORT)
    A_cochange = tensor.slice(t, COCHANGE)

    hidden = []

    # Find edges in cochange but not import
    cx = A_cochange.tocoo()
    for i, j, v in zip(cx.row, cx.col, cx.data):
        if v >= threshold and A_import[i, j] == 0:
            hidden.append((i, j, v))

    return hidden


def hidden_coupling_count(
    tensor: RelationTensor,
    t: int = -1,
) -> dict[int, int]:
    """Count hidden coupling edges per node."""
    hidden = find_hidden_coupling(tensor, t)

    counts: dict[int, int] = {}
    for i, j, _ in hidden:
        counts[i] = counts.get(i, 0) + 1
        counts[j] = counts.get(j, 0) + 1

    return counts
```

### `cross_layer/conway.py`

```python
"""Conway's law analysis."""
from __future__ import annotations

from scipy import sparse

from ..tensor.core import RelationTensor, IMPORT, AUTHOR


def find_conway_violations(
    tensor: RelationTensor,
    t: int = -1,
    min_import_weight: float = 0.5,
    max_author_overlap: float = 0.2,
) -> list[tuple[int, int]]:
    """
    Find imports across team boundaries.

    Returns:
        List of (src, dst) edges with low author overlap
    """
    if t == -1:
        t = tensor.n_windows - 1

    A_import = tensor.slice(t, IMPORT)
    A_author = tensor.slice(t, AUTHOR)

    violations = []

    cx = A_import.tocoo()
    for i, j, v in zip(cx.row, cx.col, cx.data):
        if v >= min_import_weight:
            author_overlap = A_author[i, j]
            if author_overlap < max_author_overlap:
                violations.append((i, j))

    return violations


def conway_alignment(tensor: RelationTensor, t: int = -1) -> float:
    """
    Compute overall Conway alignment score.

    Returns:
        Score in [0, 1] where 1 = perfect alignment
    """
    violations = find_conway_violations(tensor, t)
    A_import = tensor.slice(t if t >= 0 else tensor.n_windows - 1, IMPORT)

    total_imports = A_import.nnz
    if total_imports == 0:
        return 1.0

    return 1 - len(violations) / total_imports
```

### `cross_layer/mutual_info.py`

```python
"""Mutual information between graph layers."""
from __future__ import annotations

import numpy as np
from scipy import sparse


def edge_mutual_info(
    A1: sparse.csr_matrix,
    A2: sparse.csr_matrix,
    bins: int = 10,
) -> float:
    """
    Compute mutual information between two graphs based on edge co-occurrence.

    Args:
        A1, A2: Adjacency matrices (same shape)
        bins: Number of bins for discretization

    Returns:
        Mutual information in bits
    """
    n = A1.shape[0]
    if n < 2:
        return 0.0

    # Flatten to edge vectors
    v1 = A1.toarray().flatten()
    v2 = A2.toarray().flatten()

    # Discretize
    def discretize(v):
        if v.max() == v.min():
            return np.zeros_like(v, dtype=int)
        return np.digitize(v, np.linspace(v.min(), v.max(), bins))

    d1 = discretize(v1)
    d2 = discretize(v2)

    # Joint histogram
    joint = np.zeros((bins + 1, bins + 1))
    for i in range(len(d1)):
        joint[d1[i], d2[i]] += 1
    joint /= joint.sum()

    # Marginals
    p1 = joint.sum(axis=1)
    p2 = joint.sum(axis=0)

    # MI
    mi = 0.0
    for i in range(bins + 1):
        for j in range(bins + 1):
            if joint[i, j] > 0 and p1[i] > 0 and p2[j] > 0:
                mi += joint[i, j] * np.log2(joint[i, j] / (p1[i] * p2[j]))

    return mi
```

---

## 8. Level 5: Signal Fusion

### `signals/registry.py`

```python
"""Signal definitions."""
from __future__ import annotations

from enum import Enum, auto
from dataclasses import dataclass


class Polarity(Enum):
    HIGH_IS_BAD = auto()
    HIGH_IS_GOOD = auto()
    NEUTRAL = auto()


@dataclass(frozen=True)
class SignalMeta:
    name: str
    dtype: type
    polarity: Polarity
    percentileable: bool = True


# All 36 file-level signals
SIGNALS = {
    # Syntax (Level 1)
    "lines": SignalMeta("lines", int, Polarity.HIGH_IS_BAD),
    "function_count": SignalMeta("function_count", int, Polarity.NEUTRAL),
    "class_count": SignalMeta("class_count", int, Polarity.NEUTRAL),
    "import_count": SignalMeta("import_count", int, Polarity.NEUTRAL),
    "complexity": SignalMeta("complexity", int, Polarity.HIGH_IS_BAD),
    "max_nesting": SignalMeta("max_nesting", int, Polarity.HIGH_IS_BAD),
    "stub_ratio": SignalMeta("stub_ratio", float, Polarity.HIGH_IS_BAD),
    "impl_gini": SignalMeta("impl_gini", float, Polarity.HIGH_IS_BAD),

    # Semantic (Level 2)
    "concept_count": SignalMeta("concept_count", int, Polarity.NEUTRAL),
    "concept_entropy": SignalMeta("concept_entropy", float, Polarity.HIGH_IS_BAD),
    "semantic_coherence": SignalMeta("semantic_coherence", float, Polarity.HIGH_IS_GOOD),

    # Graph (Level 3)
    "pagerank": SignalMeta("pagerank", float, Polarity.HIGH_IS_BAD),
    "betweenness": SignalMeta("betweenness", float, Polarity.HIGH_IS_BAD),
    "in_degree": SignalMeta("in_degree", int, Polarity.NEUTRAL),
    "out_degree": SignalMeta("out_degree", int, Polarity.NEUTRAL),
    "blast_radius_size": SignalMeta("blast_radius_size", int, Polarity.HIGH_IS_BAD),
    "depth": SignalMeta("depth", int, Polarity.NEUTRAL),
    "is_orphan": SignalMeta("is_orphan", bool, Polarity.HIGH_IS_BAD, percentileable=False),
    "cycle_member": SignalMeta("cycle_member", bool, Polarity.HIGH_IS_BAD, percentileable=False),
    "community": SignalMeta("community", int, Polarity.NEUTRAL, percentileable=False),

    # Cross-layer (Level 4)
    "hidden_coupling_count": SignalMeta("hidden_coupling_count", int, Polarity.HIGH_IS_BAD),
    "conway_violation_count": SignalMeta("conway_violation_count", int, Polarity.HIGH_IS_BAD),

    # Temporal (Level 1 git)
    "total_changes": SignalMeta("total_changes", int, Polarity.HIGH_IS_BAD),
    "churn_cv": SignalMeta("churn_cv", float, Polarity.HIGH_IS_BAD),
    "churn_slope": SignalMeta("churn_slope", float, Polarity.NEUTRAL),
    "bus_factor": SignalMeta("bus_factor", float, Polarity.HIGH_IS_GOOD),
    "author_entropy": SignalMeta("author_entropy", float, Polarity.HIGH_IS_GOOD),
    "fix_ratio": SignalMeta("fix_ratio", float, Polarity.HIGH_IS_BAD),

    # Composites (Level 5)
    "risk_score": SignalMeta("risk_score", float, Polarity.HIGH_IS_BAD),
    "wiring_quality": SignalMeta("wiring_quality", float, Polarity.HIGH_IS_GOOD),
    "health_score": SignalMeta("health_score", float, Polarity.HIGH_IS_GOOD),
    "delta_h": SignalMeta("delta_h", float, Polarity.NEUTRAL),
}
```

### `signals/models.py`

```python
"""Signal data models."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class FileSignals:
    """All signals for a single file."""
    path: str

    # Syntax
    lines: int = 0
    function_count: int = 0
    class_count: int = 0
    import_count: int = 0
    complexity: int = 0
    max_nesting: int = 0
    stub_ratio: float = 0.0
    impl_gini: float = 0.0

    # Semantic
    concept_count: int = 0
    concept_entropy: float = 0.0
    semantic_coherence: float = 0.5

    # Graph
    pagerank: float = 0.0
    betweenness: float = 0.0
    in_degree: int = 0
    out_degree: int = 0
    blast_radius_size: int = 0
    depth: int = 0
    is_orphan: bool = False
    cycle_member: bool = False
    community: int = 0

    # Cross-layer
    hidden_coupling_count: int = 0
    conway_violation_count: int = 0

    # Temporal
    total_changes: int = 0
    churn_cv: float = 0.0
    churn_slope: float = 0.0
    bus_factor: float = 1.0
    author_entropy: float = 0.0
    fix_ratio: float = 0.0

    # Composites
    risk_score: float = 0.0
    wiring_quality: float = 1.0
    health_score: float = 10.0
    delta_h: float = 0.0

    # Percentiles (computed after)
    percentiles: dict[str, float] = field(default_factory=dict)


@dataclass
class GlobalSignals:
    """Codebase-level signals."""
    file_count: int = 0
    total_lines: int = 0
    total_commits: int = 0

    modularity: float = 0.0
    fiedler_value: float = 0.0
    spectral_gap: float = 0.0
    cycle_count: int = 0
    centrality_gini: float = 0.0

    orphan_ratio: float = 0.0
    phantom_ratio: float = 0.0
    clone_ratio: float = 0.0

    wiring_score: float = 1.0
    architecture_health: float = 1.0
    codebase_health: float = 10.0
```

### `signals/fusion.py`

```python
"""Signal fusion: compute all signals from tensor."""
from __future__ import annotations

import numpy as np

from ..tensor.core import RelationTensor, IMPORT, COCHANGE
from ..algorithms.pagerank import pagerank
from ..algorithms.louvain import louvain
from ..algorithms.spectral import spectral_analysis
from ..algorithms.scc import find_cycles
from ..algorithms.bfs import bfs_depth, blast_radius
from ..algorithms.metrics import gini
from ..cross_layer.hidden_coupling import hidden_coupling_count
from ..extract.models import FileSyntax, GitHistory
from .models import FileSignals, GlobalSignals
from .normalization import compute_percentiles
from .composites import compute_risk, compute_wiring, compute_health


def compute_all_signals(
    tensor: RelationTensor,
    syntax_map: dict[str, FileSyntax],
    git_history: GitHistory,
    churn_data: dict[str, dict],  # path -> {cv, slope, bus_factor, ...}
    concepts: dict[str, list[tuple[str, float]]],
    t: int = -1,
) -> tuple[dict[str, FileSignals], GlobalSignals]:
    """
    Compute all signals from tensor and extracted data.

    Returns:
        - file_signals: {path: FileSignals}
        - global_signals: GlobalSignals
    """
    if t == -1:
        t = tensor.n_windows - 1

    # Get slices
    A_import = tensor.slice(t, IMPORT)
    A_cochange = tensor.slice(t, COCHANGE)

    n = tensor.n_nodes

    # Graph algorithms
    pr = pagerank(A_import)
    communities, modularity = louvain(A_import)
    fiedler, spectral_gap, _ = spectral_analysis(A_import)
    cycles, cycle_member = find_cycles(A_import)

    # Find entry points for depth
    entry_points = set()
    for path, syntax in syntax_map.items():
        if syntax.has_main_guard:
            entry_points.add(tensor.node_index[path])

    if not entry_points:
        # Fallback: nodes with in_degree=0 and out_degree>0
        in_deg = np.array(A_import.sum(axis=0)).flatten()
        out_deg = np.array(A_import.sum(axis=1)).flatten()
        for i in range(n):
            if in_deg[i] == 0 and out_deg[i] > 0:
                entry_points.add(i)

    depths = bfs_depth(A_import, entry_points) if entry_points else {i: 0 for i in range(n)}
    blast_radii = blast_radius(A_import)

    # Cross-layer
    hidden_counts = hidden_coupling_count(tensor, t)

    # Degree
    in_degree = np.array(A_import.sum(axis=0)).flatten()
    out_degree = np.array(A_import.sum(axis=1)).flatten()

    # Build FileSignals
    file_signals: dict[str, FileSignals] = {}

    for path in tensor.node_index:
        idx = tensor.node_index[path]
        syntax = syntax_map.get(path)
        churn = churn_data.get(path, {})
        concept_list = concepts.get(path, [])

        fs = FileSignals(path=path)

        # Syntax signals
        if syntax:
            fs.lines = syntax.lines
            fs.function_count = syntax.function_count
            fs.class_count = syntax.class_count
            fs.import_count = syntax.import_count
            fs.complexity = syntax.complexity
            fs.max_nesting = syntax.max_nesting
            fs.stub_ratio = syntax.stub_ratio
            fs.impl_gini = syntax.impl_gini

        # Semantic
        fs.concept_count = len(concept_list)
        if concept_list:
            weights = [w for _, w in concept_list]
            total = sum(weights)
            if total > 0:
                probs = [w / total for w in weights]
                fs.concept_entropy = -sum(p * np.log2(p) for p in probs if p > 0)
        fs.semantic_coherence = 1 / (1 + fs.concept_entropy)

        # Graph
        fs.pagerank = pr[idx]
        fs.in_degree = int(in_degree[idx])
        fs.out_degree = int(out_degree[idx])
        fs.blast_radius_size = len(blast_radii.get(idx, set()))
        fs.depth = depths.get(idx, -1)
        fs.is_orphan = in_degree[idx] == 0
        fs.cycle_member = cycle_member.get(idx, False)
        fs.community = communities.get(idx, 0)

        # Cross-layer
        fs.hidden_coupling_count = hidden_counts.get(idx, 0)

        # Temporal
        fs.total_changes = churn.get("total_changes", 0)
        fs.churn_cv = churn.get("cv", 0.0)
        fs.churn_slope = churn.get("slope", 0.0)
        fs.bus_factor = churn.get("bus_factor", 1.0)
        fs.author_entropy = churn.get("author_entropy", 0.0)
        fs.fix_ratio = churn.get("fix_ratio", 0.0)

        file_signals[path] = fs

    # Compute percentiles
    compute_percentiles(file_signals)

    # Compute composites
    for fs in file_signals.values():
        fs.risk_score = compute_risk(fs)
        fs.wiring_quality = compute_wiring(fs)
        fs.health_score = compute_health(fs)

    # Health Laplacian (delta_h)
    health_values = {tensor.node_index[fs.path]: fs.health_score for fs in file_signals.values()}
    for path, fs in file_signals.items():
        idx = tensor.node_index[path]
        neighbors = list(A_import[idx].nonzero()[1]) + list(A_import[:, idx].nonzero()[0])
        neighbors = [n for n in neighbors if n != idx]
        if neighbors:
            mean_neighbor = np.mean([health_values.get(n, 10.0) for n in neighbors])
            fs.delta_h = fs.health_score - mean_neighbor
        else:
            fs.delta_h = 0.0

    # Global signals
    global_signals = GlobalSignals(
        file_count=n,
        total_lines=sum(fs.lines for fs in file_signals.values()),
        total_commits=git_history.total_commits,
        modularity=modularity,
        fiedler_value=fiedler,
        spectral_gap=spectral_gap,
        cycle_count=len(cycles),
        centrality_gini=gini(pr),
        orphan_ratio=sum(1 for fs in file_signals.values() if fs.is_orphan) / max(n, 1),
    )

    return file_signals, global_signals
```

### `signals/normalization.py`

```python
"""Percentile normalization."""
from __future__ import annotations

import numpy as np

from .models import FileSignals
from .registry import SIGNALS


def compute_percentiles(file_signals: dict[str, FileSignals]):
    """Compute percentiles for all percentileable signals."""
    n = len(file_signals)

    if n == 0:
        return

    # Determine tier
    if n < 15:
        tier = "ABSOLUTE"
    elif n < 50:
        tier = "BAYESIAN"
    else:
        tier = "FULL"

    # Collect values per signal
    for signal_name, meta in SIGNALS.items():
        if not meta.percentileable:
            continue

        values = []
        for fs in file_signals.values():
            val = getattr(fs, signal_name, 0)
            values.append((fs.path, val))

        if tier == "ABSOLUTE":
            # No percentiles for small codebases
            continue

        # Sort and compute percentiles
        sorted_vals = sorted(values, key=lambda x: x[1])

        for rank, (path, val) in enumerate(sorted_vals):
            pctl = rank / max(n - 1, 1)  # [0, 1]
            file_signals[path].percentiles[signal_name] = pctl
```

### `signals/composites.py`

```python
"""Composite signal computation."""
from __future__ import annotations

from .models import FileSignals


def compute_risk(fs: FileSignals) -> float:
    """Compute risk_score composite."""
    pctl = fs.percentiles.get

    # Instability factor
    instability = 1.0 if fs.churn_cv > 0.5 else 0.3

    # Weighted sum
    risk = (
        0.25 * pctl("pagerank", fs.pagerank) +
        0.20 * pctl("blast_radius_size", fs.blast_radius_size / 100) +
        0.20 * pctl("complexity", fs.complexity / 50) +
        0.20 * instability +
        0.15 * max(0, 1 - fs.bus_factor / 5)
    )

    return min(max(risk, 0.0), 1.0)


def compute_wiring(fs: FileSignals) -> float:
    """Compute wiring_quality composite."""
    phantom_ratio = 0.0  # Would need unresolved imports
    hidden_ratio = fs.hidden_coupling_count / max(fs.in_degree + fs.out_degree, 1)

    quality = 1 - (
        0.30 * float(fs.is_orphan) +
        0.25 * fs.stub_ratio +
        0.25 * phantom_ratio +
        0.20 * min(hidden_ratio, 1.0)
    )

    return min(max(quality, 0.0), 1.0)


def compute_health(fs: FileSignals) -> float:
    """Compute health_score composite (1-10 scale)."""
    pctl = fs.percentiles.get

    # Neighborhood coherence placeholder
    neighborhood_coherence = 1 - min(fs.hidden_coupling_count / 5, 1.0)

    raw_health = 1 - (
        0.25 * fs.risk_score +
        0.20 * (1 - fs.wiring_quality) +
        0.20 * pctl("complexity", fs.complexity / 50) +
        0.15 * float(fs.is_orphan) +
        0.20 * (1 - neighborhood_coherence)
    )

    # Scale to 1-10
    return 1 + 9 * min(max(raw_health, 0.0), 1.0)
```

---

## 9. Level 6: Finders

### `finders/base.py`

```python
"""Finder protocol and base classes."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Literal

from ..signals.models import FileSignals


@dataclass
class Evidence:
    signal: str
    value: float
    percentile: float
    description: str


@dataclass
class Finding:
    type: str
    severity: Literal["CRITICAL", "HIGH", "MEDIUM", "LOW"]
    files: list[str]
    title: str
    description: str
    suggestion: str
    evidence: list[Evidence] = field(default_factory=list)
    confidence: float = 1.0


@dataclass
class Finder:
    name: str
    condition: Callable[[FileSignals], bool]
    severity: Literal["CRITICAL", "HIGH", "MEDIUM", "LOW"]
    title_template: str
    description_template: str
    suggestion: str
    evidence_signals: list[str] = field(default_factory=list)
```

### `finders/catalog.py`

```python
"""All 22 finders."""
from __future__ import annotations

from .base import Finder, Finding, Evidence
from ..signals.models import FileSignals


# Define all finders
FINDERS = [
    Finder(
        name="HIGH_RISK_HUB",
        condition=lambda s: (
            s.percentiles.get("pagerank", 0) > 0.85 and
            s.percentiles.get("blast_radius_size", 0) > 0.75
        ),
        severity="CRITICAL",
        title_template="{path} is a high-risk hub",
        description_template="Central file with large blast radius ({blast_radius_size} files affected)",
        suggestion="Consider extracting interfaces or splitting responsibilities",
        evidence_signals=["pagerank", "blast_radius_size"],
    ),

    Finder(
        name="GOD_FILE",
        condition=lambda s: (
            s.lines > 500 and
            (s.percentiles.get("complexity", 0) > 0.90 or s.in_degree > 10)
        ),
        severity="HIGH",
        title_template="{path} is a god file",
        description_template="Large file ({lines} lines) with high complexity or many dependents",
        suggestion="Split into smaller, focused modules",
        evidence_signals=["lines", "complexity", "in_degree"],
    ),

    Finder(
        name="HIDDEN_COUPLING",
        condition=lambda s: s.hidden_coupling_count >= 2,
        severity="MEDIUM",
        title_template="{path} has hidden coupling",
        description_template="Co-changes with {hidden_coupling_count} files without explicit imports",
        suggestion="Make coupling explicit via imports or extract shared dependency",
        evidence_signals=["hidden_coupling_count"],
    ),

    Finder(
        name="ORPHAN_CODE",
        condition=lambda s: s.is_orphan and s.depth != 0,  # Not entry point
        severity="LOW",
        title_template="{path} is orphaned",
        description_template="No other files import this file",
        suggestion="Verify this code is still needed, or add proper imports",
        evidence_signals=["is_orphan", "in_degree"],
    ),

    Finder(
        name="UNSTABLE_FILE",
        condition=lambda s: s.churn_cv > 1.0 and s.total_changes > 10,
        severity="MEDIUM",
        title_template="{path} is unstable",
        description_template="High churn volatility (CV={churn_cv:.2f}) with {total_changes} changes",
        suggestion="Stabilize interfaces or add tests to prevent regressions",
        evidence_signals=["churn_cv", "total_changes"],
    ),

    Finder(
        name="CYCLE_MEMBER",
        condition=lambda s: s.cycle_member,
        severity="HIGH",
        title_template="{path} is in a dependency cycle",
        description_template="Part of a circular dependency chain",
        suggestion="Break cycle by extracting shared interface or inverting dependency",
        evidence_signals=["cycle_member"],
    ),

    Finder(
        name="BUS_FACTOR_RISK",
        condition=lambda s: (
            s.bus_factor < 2 and
            s.percentiles.get("pagerank", 0) > 0.75
        ),
        severity="HIGH",
        title_template="{path} has bus factor risk",
        description_template="Important file ({pagerank:.3f} PageRank) maintained by <2 people",
        suggestion="Spread knowledge through pair programming or documentation",
        evidence_signals=["bus_factor", "pagerank"],
    ),

    Finder(
        name="HOLLOW_CODE",
        condition=lambda s: s.stub_ratio > 0.5 and s.function_count > 3,
        severity="LOW",
        title_template="{path} has hollow code",
        description_template="{stub_ratio:.0%} of functions are stubs",
        suggestion="Implement or remove placeholder code",
        evidence_signals=["stub_ratio", "function_count"],
    ),

    Finder(
        name="VOLATILE_CORE",
        condition=lambda s: (
            s.percentiles.get("pagerank", 0) > 0.75 and
            s.churn_cv > 0.8
        ),
        severity="HIGH",
        title_template="{path} is a volatile core module",
        description_template="Central file with high change volatility",
        suggestion="Stabilize core module or reduce its responsibilities",
        evidence_signals=["pagerank", "churn_cv"],
    ),

    Finder(
        name="COMPLEX_HOTSPOT",
        condition=lambda s: (
            s.percentiles.get("complexity", 0) > 0.80 and
            s.total_changes > 20
        ),
        severity="MEDIUM",
        title_template="{path} is a complex hotspot",
        description_template="Frequently changed ({total_changes}x) complex code",
        suggestion="Refactor to reduce complexity before next change",
        evidence_signals=["complexity", "total_changes"],
    ),
]


def run_finders(file_signals: dict[str, FileSignals]) -> list[Finding]:
    """Run all finders on signals and return findings."""
    findings = []

    for path, fs in file_signals.items():
        for finder in FINDERS:
            try:
                if finder.condition(fs):
                    evidence = []
                    for sig in finder.evidence_signals:
                        val = getattr(fs, sig, 0)
                        pctl = fs.percentiles.get(sig, 0)
                        evidence.append(Evidence(
                            signal=sig,
                            value=val,
                            percentile=pctl,
                            description=f"{sig}={val}",
                        ))

                    findings.append(Finding(
                        type=finder.name,
                        severity=finder.severity,
                        files=[path],
                        title=finder.title_template.format(path=path, **vars(fs)),
                        description=finder.description_template.format(**vars(fs)),
                        suggestion=finder.suggestion,
                        evidence=evidence,
                    ))
            except Exception:
                continue  # Skip on errors

    return findings
```

---

## 10. Runtime Kernel

### `kernel/context.py`

```python
"""Runtime context."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Callable
import time


class Phase(Enum):
    INIT = auto()
    EXTRACT = auto()
    POPULATE = auto()
    ALGORITHMS = auto()
    CROSS_LAYER = auto()
    FUSION = auto()
    FINDERS = auto()
    PERSIST = auto()
    DONE = auto()


@dataclass
class RuntimeContext:
    """Execution context for kernel."""
    root: Path
    phase: Phase = Phase.INIT
    start_time: float = field(default_factory=time.time)

    # Progress tracking
    total_files: int = 0
    processed_files: int = 0

    # Cancellation
    _cancelled: bool = False

    # Callbacks
    on_progress: Callable[[str, float], None] | None = None

    def cancel(self):
        self._cancelled = True

    @property
    def cancelled(self) -> bool:
        return self._cancelled

    def advance(self, message: str = ""):
        self.processed_files += 1
        if self.on_progress:
            progress = self.processed_files / max(self.total_files, 1)
            self.on_progress(message, progress)

    @property
    def elapsed(self) -> float:
        return time.time() - self.start_time
```

### `kernel/result.py`

```python
"""Analysis result model."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ..signals.models import FileSignals, GlobalSignals
from ..finders.base import Finding


@dataclass
class AnalysisResult:
    """Complete result of analysis run."""

    # Core outputs
    file_signals: dict[str, FileSignals] = field(default_factory=dict)
    global_signals: GlobalSignals | None = None
    findings: list[Finding] = field(default_factory=list)

    # Metadata
    duration_seconds: float = 0.0
    file_count: int = 0
    commit_count: int = 0
    error_count: int = 0

    # Status
    success: bool = True
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "success": self.success,
            "duration_seconds": self.duration_seconds,
            "file_count": self.file_count,
            "commit_count": self.commit_count,
            "finding_count": len(self.findings),
            "findings": [
                {
                    "type": f.type,
                    "severity": f.severity,
                    "files": f.files,
                    "title": f.title,
                    "description": f.description,
                    "suggestion": f.suggestion,
                }
                for f in self.findings
            ],
            "global_signals": {
                "codebase_health": self.global_signals.codebase_health if self.global_signals else 0,
                "modularity": self.global_signals.modularity if self.global_signals else 0,
                "cycle_count": self.global_signals.cycle_count if self.global_signals else 0,
            },
            "errors": self.errors,
        }
```

### `kernel/runtime.py`

```python
"""Runtime kernel - main orchestrator."""
from __future__ import annotations

from pathlib import Path
import time

from .context import RuntimeContext, Phase
from .result import AnalysisResult

from ..tensor.core import RelationTensor
from ..extract.syntax import extract_syntax
from ..extract.git import extract_git_history
from ..extract.concepts import compute_tfidf
from ..populate.imports import populate_imports
from ..populate.cochange import populate_cochange
from ..populate.authors import populate_authors
from ..populate.semantic import populate_semantic
from ..populate.combined import populate_combined
from ..signals.fusion import compute_all_signals
from ..finders.catalog import run_finders


class RuntimeKernel:
    """Main analysis orchestrator."""

    def __init__(self, root: Path, config: dict | None = None):
        self.root = root
        self.config = config or {}
        self.context = RuntimeContext(root=root)

    def run(self) -> AnalysisResult:
        """Execute full analysis pipeline."""
        result = AnalysisResult()

        try:
            # Phase 1: Extract
            self.context.phase = Phase.EXTRACT
            syntax_map, git_history, churn_data = self._extract()

            result.file_count = len(syntax_map)
            result.commit_count = git_history.total_commits

            # Phase 2: Populate tensor
            self.context.phase = Phase.POPULATE
            tensor = self._populate(syntax_map, git_history)

            # Phase 3: Compute concepts
            tfidf, concepts = compute_tfidf({p: s.identifiers for p, s in syntax_map.items()})

            # Phase 4: Compute signals
            self.context.phase = Phase.FUSION
            file_signals, global_signals = compute_all_signals(
                tensor=tensor,
                syntax_map=syntax_map,
                git_history=git_history,
                churn_data=churn_data,
                concepts=concepts,
            )

            result.file_signals = file_signals
            result.global_signals = global_signals

            # Phase 5: Run finders
            self.context.phase = Phase.FINDERS
            result.findings = run_finders(file_signals)

            result.success = True

        except Exception as e:
            result.success = False
            result.errors.append(str(e))

        result.duration_seconds = self.context.elapsed
        self.context.phase = Phase.DONE

        return result

    def _extract(self) -> tuple[dict, any, dict]:
        """Extract syntax and git data."""
        syntax_map = {}

        # Find files
        exclude = self.config.get("exclude_patterns", [
            "__pycache__", ".git", "node_modules", ".venv", "venv",
            "*.pyc", "*.pyo", "*.so", "*.dylib",
        ])

        for path in self.root.rglob("*"):
            if not path.is_file():
                continue

            rel_path = str(path.relative_to(self.root))

            # Skip excluded
            if any(ex in rel_path for ex in exclude):
                continue

            # Skip binary
            if path.suffix in [".pyc", ".pyo", ".so", ".dylib", ".dll", ".exe"]:
                continue

            try:
                content = path.read_bytes()
                syntax = extract_syntax(rel_path, content)
                syntax_map[rel_path] = syntax
            except Exception:
                continue

        # Git history
        git_history = extract_git_history(self.root)

        # Compute churn data
        churn_data = self._compute_churn(git_history)

        return syntax_map, git_history, churn_data

    def _compute_churn(self, git_history) -> dict:
        """Compute per-file churn metrics."""
        from collections import Counter, defaultdict
        import math
        import numpy as np

        # Group changes by file
        changes_per_file = defaultdict(list)
        authors_per_file = defaultdict(Counter)

        for commit in git_history.commits:
            for f in commit.files:
                changes_per_file[f].append(commit.timestamp)
                authors_per_file[f][commit.author] += 1

        churn_data = {}

        for path, timestamps in changes_per_file.items():
            if not timestamps:
                continue

            # Window counts (30-day windows)
            window_size = 30 * 86400
            min_ts = min(timestamps)
            windows = [(ts - min_ts) // window_size for ts in timestamps]
            window_counts = Counter(windows)
            counts = [window_counts.get(i, 0) for i in range(max(windows) + 1)] if windows else [0]

            # Stats
            total = len(timestamps)
            mean = np.mean(counts) if counts else 0
            std = np.std(counts) if len(counts) > 1 else 0
            cv = std / max(mean, 1)

            # Slope
            if len(counts) > 1:
                slope = np.polyfit(range(len(counts)), counts, 1)[0]
            else:
                slope = 0

            # Author entropy
            author_counts = authors_per_file[path]
            total_author = sum(author_counts.values())
            entropy = 0
            for count in author_counts.values():
                p = count / total_author
                if p > 0:
                    entropy -= p * math.log2(p)

            bus_factor = 2 ** entropy

            # Fix ratio
            fix_count = sum(1 for c in git_history.commits if path in c.files and c.is_fix)
            fix_ratio = fix_count / max(total, 1)

            churn_data[path] = {
                "total_changes": total,
                "cv": cv,
                "slope": slope,
                "bus_factor": bus_factor,
                "author_entropy": entropy,
                "fix_ratio": fix_ratio,
            }

        return churn_data

    def _populate(self, syntax_map, git_history) -> RelationTensor:
        """Build tensor from extracted data."""
        n_files = len(syntax_map)
        tensor = RelationTensor(n_files=n_files, n_windows=12)

        # Register all nodes
        for path in sorted(syntax_map.keys()):
            tensor.register_node(path)

        now = int(time.time())

        # Populate layers
        populate_imports(tensor, syntax_map)
        populate_cochange(tensor, git_history, now)
        populate_authors(tensor, git_history)

        # Semantic needs TF-IDF
        tfidf, _ = compute_tfidf({p: s.identifiers for p, s in syntax_map.items()})
        populate_semantic(tensor, tfidf)

        # Combined
        populate_combined(tensor)

        return tensor
```

---

## 11. Persistence

### `persistence/database.py`

```python
"""SQLite persistence."""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from datetime import datetime

from ..kernel.result import AnalysisResult


class Database:
    """SQLite database for snapshots."""

    SCHEMA = """
    CREATE TABLE IF NOT EXISTS snapshots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        commit_sha TEXT,
        duration_seconds REAL,
        file_count INTEGER,
        finding_count INTEGER,
        codebase_health REAL,
        data_json TEXT
    );

    CREATE INDEX IF NOT EXISTS idx_snapshots_timestamp ON snapshots(timestamp);
    """

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript(self.SCHEMA)

    def save_snapshot(self, result: AnalysisResult, commit_sha: str | None = None):
        """Save analysis result as snapshot."""
        data = result.to_dict()

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO snapshots (
                    timestamp, commit_sha, duration_seconds,
                    file_count, finding_count, codebase_health, data_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                datetime.now().isoformat(),
                commit_sha,
                result.duration_seconds,
                result.file_count,
                len(result.findings),
                result.global_signals.codebase_health if result.global_signals else 0,
                json.dumps(data),
            ))

    def get_latest(self) -> dict | None:
        """Get most recent snapshot."""
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute("""
                SELECT data_json FROM snapshots
                ORDER BY timestamp DESC LIMIT 1
            """).fetchone()

            if row:
                return json.loads(row[0])
        return None

    def get_history(self, limit: int = 10) -> list[dict]:
        """Get recent snapshots."""
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute("""
                SELECT timestamp, codebase_health, finding_count, file_count
                FROM snapshots
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,)).fetchall()

            return [
                {
                    "timestamp": row[0],
                    "codebase_health": row[1],
                    "finding_count": row[2],
                    "file_count": row[3],
                }
                for row in rows
            ]
```

---

## 12. CLI

### `cli/main.py`

```python
"""CLI entry point."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import typer

from ..kernel.runtime import RuntimeKernel
from ..persistence.database import Database

app = typer.Typer(
    name="shannon-insight",
    help="Codebase analysis using information theory and graph algorithms.",
)


@app.command()
def analyze(
    path: Path = typer.Argument(Path("."), help="Path to repository"),
    json_output: bool = typer.Option(False, "--json", "-j", help="Output JSON"),
    save: bool = typer.Option(False, "--save", "-s", help="Save snapshot"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """Analyze a codebase."""
    if not path.exists():
        typer.echo(f"Error: Path {path} does not exist", err=True)
        raise typer.Exit(1)

    # Run analysis
    kernel = RuntimeKernel(path)
    result = kernel.run()

    # Save if requested
    if save:
        db_path = path / ".shannon" / "shannon.db"
        db = Database(db_path)
        db.save_snapshot(result)

    # Output
    if json_output:
        typer.echo(json.dumps(result.to_dict(), indent=2))
    else:
        _print_summary(result)

    # Exit code
    if not result.success:
        raise typer.Exit(1)

    critical = sum(1 for f in result.findings if f.severity == "CRITICAL")
    if critical > 0:
        raise typer.Exit(2)


def _print_summary(result):
    """Print human-readable summary."""
    typer.echo(f"\nShannon Insight Analysis")
    typer.echo("=" * 40)
    typer.echo(f"Files analyzed: {result.file_count}")
    typer.echo(f"Commits analyzed: {result.commit_count}")
    typer.echo(f"Duration: {result.duration_seconds:.1f}s")

    if result.global_signals:
        typer.echo(f"\nCodebase Health: {result.global_signals.codebase_health:.1f}/10")
        typer.echo(f"Modularity: {result.global_signals.modularity:.2f}")
        typer.echo(f"Cycles: {result.global_signals.cycle_count}")

    typer.echo(f"\nFindings: {len(result.findings)}")

    by_severity = {}
    for f in result.findings:
        by_severity[f.severity] = by_severity.get(f.severity, 0) + 1

    for sev in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
        if sev in by_severity:
            typer.echo(f"  {sev}: {by_severity[sev]}")

    # Show top findings
    if result.findings:
        typer.echo("\nTop Issues:")
        for f in result.findings[:5]:
            typer.echo(f"  [{f.severity}] {f.title}")


@app.command()
def serve(
    path: Path = typer.Argument(Path("."), help="Path to repository"),
    port: int = typer.Option(8080, "--port", "-p", help="Server port"),
):
    """Start web server for dashboard."""
    typer.echo(f"Starting server on http://localhost:{port}")

    from ..server.app import create_app
    import uvicorn

    app = create_app(path)
    uvicorn.run(app, host="0.0.0.0", port=port)


def main():
    app()


if __name__ == "__main__":
    main()
```

---

## 13. Server & UI

### `server/app.py`

```python
"""Starlette web application."""
from __future__ import annotations

from pathlib import Path
import json

from starlette.applications import Starlette
from starlette.responses import JSONResponse, HTMLResponse
from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles
from starlette.websockets import WebSocket

from ..kernel.runtime import RuntimeKernel
from ..persistence.database import Database


def create_app(repo_path: Path) -> Starlette:
    """Create Starlette application."""

    kernel = RuntimeKernel(repo_path)
    db_path = repo_path / ".shannon" / "shannon.db"
    db = Database(db_path)

    # Cache last result
    cache = {"result": None}

    async def index(request):
        """Serve main page."""
        return HTMLResponse("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Shannon Insight</title>
            <script src="https://cdn.tailwindcss.com"></script>
        </head>
        <body class="bg-gray-100">
            <div id="app" class="container mx-auto p-4">
                <h1 class="text-3xl font-bold mb-4">Shannon Insight</h1>
                <div id="health" class="text-6xl font-bold mb-4">--</div>
                <div id="findings" class="space-y-2"></div>
            </div>
            <script>
                fetch('/api/state')
                    .then(r => r.json())
                    .then(data => {
                        document.getElementById('health').textContent =
                            data.global_signals?.codebase_health?.toFixed(1) + '/10';

                        const findings = document.getElementById('findings');
                        data.findings?.slice(0, 10).forEach(f => {
                            const div = document.createElement('div');
                            div.className = 'p-2 bg-white rounded shadow';
                            div.textContent = `[${f.severity}] ${f.title}`;
                            findings.appendChild(div);
                        });
                    });
            </script>
        </body>
        </html>
        """)

    async def api_state(request):
        """Get current analysis state."""
        if cache["result"] is None:
            cache["result"] = kernel.run()
        return JSONResponse(cache["result"].to_dict())

    async def api_refresh(request):
        """Trigger re-analysis."""
        cache["result"] = kernel.run()
        return JSONResponse({"status": "ok"})

    async def api_history(request):
        """Get analysis history."""
        history = db.get_history()
        return JSONResponse(history)

    async def api_file(request):
        """Get signals for specific file."""
        path = request.query_params.get("path")
        if not path or not cache["result"]:
            return JSONResponse({"error": "Not found"}, status_code=404)

        fs = cache["result"].file_signals.get(path)
        if not fs:
            return JSONResponse({"error": "File not found"}, status_code=404)

        return JSONResponse({
            "path": fs.path,
            "health_score": fs.health_score,
            "risk_score": fs.risk_score,
            "pagerank": fs.pagerank,
            "complexity": fs.complexity,
            "lines": fs.lines,
            "bus_factor": fs.bus_factor,
        })

    routes = [
        Route("/", index),
        Route("/api/state", api_state),
        Route("/api/refresh", api_refresh, methods=["POST"]),
        Route("/api/history", api_history),
        Route("/api/file", api_file),
    ]

    return Starlette(routes=routes)
```

---

## 14. Testing Strategy

### Test Structure

```
tests/
├── conftest.py              # Fixtures
├── fixtures/
│   ├── simple_repo/         # Minimal test repo
│   ├── cyclic_repo/         # Repo with cycles
│   └── large_repo/          # Performance testing
│
├── tensor/
│   ├── test_core.py         # RelationTensor
│   └── test_slicing.py      # Slice operations
│
├── extract/
│   ├── test_syntax.py       # Syntax extraction
│   ├── test_git.py          # Git extraction
│   └── test_concepts.py     # TF-IDF
│
├── populate/
│   ├── test_imports.py      # Import layer
│   ├── test_cochange.py     # CoChange layer
│   └── test_combined.py     # Combined layer
│
├── algorithms/
│   ├── test_pagerank.py     # PageRank
│   ├── test_louvain.py      # Louvain
│   ├── test_scc.py          # SCC
│   └── test_bfs.py          # BFS algorithms
│
├── signals/
│   ├── test_fusion.py       # Signal computation
│   └── test_composites.py   # Composite scores
│
├── finders/
│   └── test_catalog.py      # All finders
│
├── kernel/
│   └── test_runtime.py      # End-to-end
│
└── integration/
    └── test_full_pipeline.py
```

### Key Test Fixtures

```python
# tests/conftest.py
import pytest
from pathlib import Path
import tempfile
import subprocess


@pytest.fixture
def simple_repo(tmp_path):
    """Create minimal test repository."""
    # Create files
    (tmp_path / "main.py").write_text("""
from utils import helper

def main():
    helper()

if __name__ == "__main__":
    main()
""")

    (tmp_path / "utils.py").write_text("""
def helper():
    return 42
""")

    # Init git
    subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
    subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Initial"],
        cwd=tmp_path,
        capture_output=True,
        env={"GIT_AUTHOR_NAME": "Test", "GIT_AUTHOR_EMAIL": "test@test.com",
             "GIT_COMMITTER_NAME": "Test", "GIT_COMMITTER_EMAIL": "test@test.com"}
    )

    return tmp_path


@pytest.fixture
def cyclic_repo(tmp_path):
    """Create repo with circular dependencies."""
    (tmp_path / "a.py").write_text("from b import B\nclass A: pass")
    (tmp_path / "b.py").write_text("from c import C\nclass B: pass")
    (tmp_path / "c.py").write_text("from a import A\nclass C: pass")

    # Init git
    subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
    subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Cycle"],
        cwd=tmp_path,
        capture_output=True,
        env={"GIT_AUTHOR_NAME": "Test", "GIT_AUTHOR_EMAIL": "test@test.com",
             "GIT_COMMITTER_NAME": "Test", "GIT_COMMITTER_EMAIL": "test@test.com"}
    )

    return tmp_path
```

### Example Tests

```python
# tests/tensor/test_core.py
import pytest
from shannon_insight.tensor.core import RelationTensor, IMPORT


def test_tensor_creation():
    tensor = RelationTensor(n_files=10, n_windows=12)
    assert tensor.n_files == 10
    assert tensor.n_windows == 12
    assert tensor.n_nodes == 0


def test_add_edge():
    tensor = RelationTensor(n_files=10, n_windows=12)
    tensor.add_edge("a.py", "b.py", t=0, r=IMPORT, weight=1.0)
    tensor.finalize()

    A = tensor.slice(t=0, r=IMPORT)
    assert A[0, 1] == 1.0


def test_slice_empty():
    tensor = RelationTensor(n_files=10, n_windows=12)
    tensor.register_node("a.py")
    tensor.finalize()

    A = tensor.slice(t=5, r=IMPORT)
    assert A.nnz == 0


# tests/algorithms/test_pagerank.py
import numpy as np
from scipy import sparse
from shannon_insight.algorithms.pagerank import pagerank


def test_pagerank_simple():
    # Simple chain: A → B → C
    A = sparse.csr_matrix([
        [0, 1, 0],
        [0, 0, 1],
        [0, 0, 0],
    ])

    pr = pagerank(A)

    # C should have highest rank (most important)
    assert pr[2] > pr[1] > pr[0]


def test_pagerank_star():
    # Star: all point to center
    A = sparse.csr_matrix([
        [0, 1, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 1, 0, 0, 0],
        [0, 1, 0, 0, 0],
        [0, 1, 0, 0, 0],
    ])

    pr = pagerank(A)

    # Node 1 should have highest rank
    assert pr[1] == max(pr)


# tests/kernel/test_runtime.py
def test_full_analysis(simple_repo):
    from shannon_insight.kernel.runtime import RuntimeKernel

    kernel = RuntimeKernel(simple_repo)
    result = kernel.run()

    assert result.success
    assert result.file_count == 2
    assert "main.py" in result.file_signals
    assert "utils.py" in result.file_signals
```

---

## 15. Implementation Order

### Phase 1: Foundation (Week 1)

| Day | Task | Files |
|-----|------|-------|
| 1 | Tensor core | `tensor/core.py`, `tensor/index.py` |
| 2 | Syntax extraction | `extract/syntax.py`, `extract/models.py` |
| 3 | Git extraction | `extract/git.py` |
| 4 | Tests for extraction | `tests/extract/` |
| 5 | Concepts (TF-IDF) | `extract/concepts.py` |

### Phase 2: Population (Week 2)

| Day | Task | Files |
|-----|------|-------|
| 1 | Import populator | `populate/imports.py` |
| 2 | CoChange populator | `populate/cochange.py` |
| 3 | Author populator | `populate/authors.py` |
| 4 | Semantic populator | `populate/semantic.py` |
| 5 | Combined + tests | `populate/combined.py`, `tests/populate/` |

### Phase 3: Algorithms (Week 3)

| Day | Task | Files |
|-----|------|-------|
| 1 | PageRank | `algorithms/pagerank.py` |
| 2 | Louvain | `algorithms/louvain.py` |
| 3 | SCC, BFS | `algorithms/scc.py`, `algorithms/bfs.py` |
| 4 | Spectral | `algorithms/spectral.py` |
| 5 | Cross-layer | `cross_layer/*.py` |

### Phase 4: Signals (Week 4)

| Day | Task | Files |
|-----|------|-------|
| 1 | Signal models | `signals/models.py`, `signals/registry.py` |
| 2 | Normalization | `signals/normalization.py` |
| 3 | Composites | `signals/composites.py` |
| 4 | Fusion | `signals/fusion.py` |
| 5 | Tests | `tests/signals/` |

### Phase 5: Finders + Kernel (Week 5)

| Day | Task | Files |
|-----|------|-------|
| 1 | Finder base | `finders/base.py` |
| 2 | All finders | `finders/catalog.py` |
| 3 | Runtime kernel | `kernel/runtime.py` |
| 4 | Persistence | `persistence/database.py` |
| 5 | Integration tests | `tests/integration/` |

### Phase 6: CLI + Server (Week 6)

| Day | Task | Files |
|-----|------|-------|
| 1 | CLI analyze | `cli/main.py` |
| 2 | CLI serve | `cli/main.py` |
| 3 | Server API | `server/app.py` |
| 4 | Basic UI | `server/app.py` (inline HTML) |
| 5 | Polish + docs | README, pyproject.toml |

---

## References

### Existing Documentation

- [TENSOR-ARCHITECTURE.md](./architecture/TENSOR-ARCHITECTURE.md) — Architecture overview
- [MATH-DAG.md](./architecture/MATH-DAG.md) — Complete mathematical specification
- [v2/registry/signals.md](./v2/registry/signals.md) — Signal definitions
- [v2/registry/finders.md](./v2/registry/finders.md) — Finder specifications
- [v2/FAILURE-MODES.md](./v2/FAILURE-MODES.md) — Common bugs to avoid

### External

- [TensorLy](http://tensorly.org/) — Tensor operations
- [PyData Sparse](https://sparse.pydata.org/) — Sparse arrays
- [NetworkX](https://networkx.org/) — Graph algorithms reference
- [SciPy Sparse](https://docs.scipy.org/doc/scipy/reference/sparse.html) — Sparse matrices
