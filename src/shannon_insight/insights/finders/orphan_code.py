"""ORPHAN_CODE — files with no imports and not entry points.

Scope: FILE
Severity: 0.55
Hotspot: NO (structural-only)

An orphan file has in_degree=0 and is neither an entry point nor a test.
These files may be dead code or missing integration.
"""

from __future__ import annotations

from pathlib import PurePosixPath
from typing import TYPE_CHECKING

from ..models import Evidence, Finding

if TYPE_CHECKING:
    from ..store_v2 import AnalysisStore

_MAX_FINDINGS = 10  # Cap output to avoid flooding


class OrphanCodeFinder:
    """Detects orphan files that no other code imports."""

    name = "orphan_code"
    api_version = "2.0"
    requires = frozenset({"signal_field"})
    error_mode = "skip"
    hotspot_filtered = False  # Structural-only
    tier_minimum = "ABSOLUTE"  # Works in all tiers
    deprecated = False
    deprecation_note = None

    # Constants
    BASE_SEVERITY = 0.55

    def find(self, store: AnalysisStore) -> list[Finding]:
        """Detect orphan files.

        Returns:
            List of findings for orphan files, sorted by severity desc.
        """
        if not store.signal_field.available:
            return []

        field = store.signal_field.value

        # Build set of files that are actually imported (via any mechanism)
        actually_imported = self._build_init_reexports(store)
        actually_imported |= self._find_absolute_import_targets(store)

        findings: list[Finding] = []

        for path, fs in sorted(field.per_file.items()):
            if not fs.is_orphan:
                continue

            # __init__.py files are package markers, imported implicitly
            if path.endswith("__init__.py"):
                continue

            # Check if file is actually imported by any mechanism
            if path in actually_imported:
                continue

            # Build evidence
            evidence = [
                Evidence(
                    signal="in_degree",
                    value=float(fs.in_degree),
                    percentile=0.0,
                    description="No files import this",
                ),
                Evidence(
                    signal="role",
                    value=0.0,
                    percentile=0.0,
                    description=f"Classified as {fs.role}",
                ),
            ]
            if fs.depth == -1:
                evidence.append(
                    Evidence(
                        signal="depth",
                        value=-1.0,
                        percentile=0.0,
                        description="Unreachable from entry points",
                    )
                )

            findings.append(
                Finding(
                    finding_type=self.name,
                    severity=self.BASE_SEVERITY,
                    title=f"Orphan file: {path}",
                    files=[path],
                    evidence=evidence,
                    suggestion="Wire into dependency graph or remove if unused.",
                    confidence=1.0,  # Boolean condition, full confidence
                    effort="LOW",
                    scope="FILE",
                )
            )

        findings.sort(key=lambda f: f.severity, reverse=True)
        return findings[:_MAX_FINDINGS]

    def _find_absolute_import_targets(self, store: AnalysisStore) -> set[str]:
        """Find files that are imported via absolute imports.

        The dependency graph often misses absolute imports like:
            from shannon_insight.signals.composites import compute_composites

        This method checks all file_syntax imports and resolves absolute
        import sources to file paths by stripping package prefixes.
        """
        imported: set[str] = set()

        if not store.file_syntax.available:
            return imported

        file_syntax = store.file_syntax.value
        all_paths = set(file_syntax.keys())

        # Build module-to-path mapping for all known files
        # e.g., "signals/composites.py" can be reached via:
        #   - "signals.composites" → signals/composites.py
        #   - "composites" → signals/composites.py (if unique)
        path_by_module: dict[str, str] = {}
        for path in all_paths:
            mod_path = path.replace("/", ".").removesuffix(".py")
            mod_path = mod_path.removesuffix(".__init__")
            path_by_module[mod_path] = path

            # Also store each suffix for partial matching
            parts = mod_path.split(".")
            for i in range(len(parts)):
                suffix = ".".join(parts[i:])
                if suffix:
                    # Don't overwrite if already set (keep shortest path)
                    path_by_module.setdefault(suffix, path)

        # Collect all import sources across the codebase
        for syntax in file_syntax.values():
            for imp in syntax.imports:
                if not imp.source:
                    continue

                source = imp.source.lstrip(".")

                # Try to resolve: strip package prefixes progressively
                # "shannon_insight.signals.composites" → try each suffix:
                #   "shannon_insight.signals.composites"
                #   "signals.composites"
                #   "composites"
                parts = source.split(".")
                for i in range(len(parts)):
                    suffix = ".".join(parts[i:])
                    if suffix in path_by_module:
                        imported.add(path_by_module[suffix])
                        break

        return imported

    def _build_init_reexports(self, store: AnalysisStore) -> set[str]:
        """Find files re-exported via their parent __init__.py or sibling imports.

        A file is considered re-exported (not truly orphaned) if:
        1. Parent __init__.py imports it (direct re-export)
        2. Any sibling file in the same directory imports it
        3. The file is in a queries/plugins/scanners directory (convention-based import)
        """
        reexported: set[str] = set()

        if not store.structural.available:
            return reexported

        graph = store.structural.value.graph

        # Build reverse adjacency: who imports whom
        imported_by: dict[str, set[str]] = {}
        for source, targets in graph.adjacency.items():
            for target in targets:
                imported_by.setdefault(target, set()).add(source)

        # Check 1: files imported by their parent __init__.py
        for init_path in graph.adjacency:
            if not init_path.endswith("__init__.py"):
                continue

            init_dir = str(PurePosixPath(init_path).parent)
            imported_by_init = set(graph.adjacency.get(init_path, []))

            for imported_path in imported_by_init:
                imported_dir = str(PurePosixPath(imported_path).parent)
                if imported_dir == init_dir:
                    reexported.add(imported_path)

        # Check 2: files imported by any sibling in the same directory
        all_paths = set(graph.adjacency.keys())
        all_paths.update(t for targets in graph.adjacency.values() for t in targets)

        for path in all_paths:
            if path in imported_by:
                path_dir = str(PurePosixPath(path).parent)
                for importer in imported_by[path]:
                    importer_dir = str(PurePosixPath(importer).parent)
                    if importer_dir == path_dir:
                        reexported.add(path)
                        break

        # Check 3: convention-based directories where files are loaded dynamically
        dynamic_dirs = {"queries", "plugins", "scanners", "finders", "analyzers"}
        for path in all_paths:
            parts = PurePosixPath(path).parts
            if any(d in parts for d in dynamic_dirs) and not path.endswith("__init__.py"):
                # Check if the parent __init__.py exists in the set
                parent_init = str(PurePosixPath(path).parent / "__init__.py")
                if parent_init in all_paths:
                    reexported.add(path)

        return reexported
