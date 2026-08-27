"""FRESH-BUILD runtime kernel — simple analysis orchestrator.

This module implements the lightweight RuntimeKernel described in FRESH-BUILD.md.
It is separate from the production RuntimeKernel in kernel/runtime_kernel.py,
which has circuit-breakers, partial results, and full observability.

Use the production kernel (RuntimeKernel from kernel/runtime_kernel.py) for
real workloads. Use this module as a reference or for testing the new tensor
pipeline (tensor/, extract/, populate/, algorithms/, cross_layer/, finders/).
"""

from __future__ import annotations

import time
from pathlib import Path

from ..extract.concepts import compute_tfidf
from ..extract.git import extract_git_history
from ..extract.syntax import extract_syntax
from ..finders.catalog import run_finders
from ..populate.authors import populate_authors
from ..populate.cochange import populate_cochange
from ..populate.combined import populate_combined
from ..populate.imports import populate_imports
from ..populate.semantic import populate_semantic
from ..signals.fusion import compute_all_signals
from ..tensor.core import RelationTensor
from .context import Phase, RuntimeContext
from .fresh_result import AnalysisResult


class FreshKernel:
    """Lightweight analysis orchestrator for the FRESH-BUILD tensor pipeline."""

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
        exclude = self.config.get(
            "exclude_patterns",
            [
                "__pycache__",
                ".git",
                "node_modules",
                ".venv",
                "venv",
                "*.pyc",
                "*.pyo",
                "*.so",
                "*.dylib",
            ],
        )

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
        import math
        from collections import Counter, defaultdict

        import numpy as np

        # Group changes by file
        changes_per_file = defaultdict(list)
        authors_per_file: dict = defaultdict(Counter)

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
            entropy = 0.0
            for count in author_counts.values():
                p = count / total_author
                if p > 0:
                    entropy -= p * math.log2(p)

            bus_factor = 2**entropy

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

        # Clone layer (if clone_pairs available in context)
        # Clone detection is expensive so we skip it here in FreshKernel
        # It will be populated by the main kernel when clone_pairs are available

        # Combined
        populate_combined(tensor)

        return tensor
