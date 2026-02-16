"""Pipeline — the top-level orchestrator for v2 analysis.

Executes the full analysis pipeline:
    1. Creates RuntimeContext (root path, tier)
    2. Creates FactStore
    3. Scans files and creates FILE entities
    4. Computes basic signals (LINES, FUNCTION_COUNT)
    5. Returns AnalysisResult with findings (empty until finders are wired)

Usage:
    from shannon_insight.infrastructure.pipeline import run_pipeline

    result = run_pipeline("/path/to/repo")
    print(len(result.store.files()))
    print(result.findings)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List

from shannon_insight.infrastructure.entities import Entity, EntityId, EntityType
from shannon_insight.infrastructure.patterns import Finding
from shannon_insight.infrastructure.runtime import RuntimeContext, determine_tier
from shannon_insight.infrastructure.signals import Signal
from shannon_insight.infrastructure.store import FactStore


@dataclass
class AnalysisResult:
    """The output of a full pipeline run.

    Attributes:
        store:    Populated FactStore with entities, signals, and relations.
        findings: List of findings detected by pattern matching.
        context:  RuntimeContext capturing environment details.
    """

    store: FactStore
    findings: List[Finding] = field(default_factory=list)
    context: RuntimeContext = field(default_factory=lambda: RuntimeContext(root=""))


def run_pipeline(root: str) -> AnalysisResult:
    """Execute the full analysis pipeline.

    For now, this is a minimal implementation that:
    1. Creates RuntimeContext
    2. Creates FactStore
    3. Scans files and creates FILE entities
    4. Computes basic signals (LINES, FUNCTION_COUNT)
    5. Returns empty findings list (finders not wired yet)

    Args:
        root: Absolute path to the codebase root directory.

    Returns:
        AnalysisResult with populated store, empty findings, and context.
    """
    root_path = Path(root)

    # Collect Python files (skip __pycache__)
    py_files = [
        f for f in root_path.glob("**/*.py")
        if "__pycache__" not in str(f)
    ]

    # Initialize context with tier based on file count
    context = RuntimeContext(
        root=root,
        tier=determine_tier(len(py_files)),
    )

    # Initialize store
    store = FactStore(root=root)

    # Scan files and create entities with basic signals
    for py_file in py_files:
        rel_path = str(py_file.relative_to(root_path))
        entity_id = EntityId(EntityType.FILE, rel_path)
        entity = Entity(id=entity_id)
        store.add_entity(entity)

        # Compute basic signals
        try:
            content = py_file.read_text()
            lines = len(content.splitlines())
            # Count 'def ' for functions (simple heuristic)
            functions = content.count("\ndef ") + (
                1 if content.startswith("def ") else 0
            )

            store.set_signal(entity_id, Signal.LINES, lines)
            store.set_signal(entity_id, Signal.FUNCTION_COUNT, functions)
        except Exception:
            pass

    # Return result (no finders wired yet)
    return AnalysisResult(
        store=store,
        findings=[],
        context=context,
    )
