"""DiscoveryExecutor — Find source files to analyze.

This phase discovers all source files that match the configuration criteria:
- Language extensions (Python, Go, TypeScript, etc.)
- Size limits (max_file_size_mb)
- Exclusion patterns (node_modules, vendor, etc.)
- File count limits (max_files)

The discovered file paths are stored in store._discovered_files for use
by subsequent phases.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from ...infrastructure.runtime import Phase
from ...logging_config import get_logger
from ..executor import BaseExecutor
from ..result import PhaseResult

if TYPE_CHECKING:
    from ...infrastructure.runtime import RuntimeContext
    from ...insights.store import AnalysisStore
    from ...session import AnalysisSession

logger = get_logger(__name__)


class DiscoveryExecutor(BaseExecutor):
    """Discover source files to analyze.

    Uses environment file_paths if pre-discovered, otherwise walks
    the directory tree applying filters.
    """

    phase = Phase.DISCOVERY
    timeout_seconds = 60  # Discovery should be fast
    name = "discovery"

    def _execute(
        self,
        ctx: RuntimeContext,
        store: AnalysisStore,
        session: AnalysisSession,
    ) -> PhaseResult:
        """Discover source files."""
        root = Path(store.root_dir)

        # Use pre-discovered paths from environment if available
        if session.env.file_paths:
            file_paths = [root / p for p in session.env.file_paths]
            logger.debug(f"Using {len(file_paths)} pre-discovered files from environment")
        else:
            # Fall back to directory walk
            file_paths = self._discover_files(ctx, session, root)

        # Apply file limit
        if len(file_paths) > session.config.max_files:
            logger.warning(
                f"Limiting to {session.config.max_files} files (found {len(file_paths)})"
            )
            file_paths = file_paths[: session.config.max_files]

        # Store discovered paths in context for later phases
        # We use a list attribute on the context for phase-to-phase data
        ctx._discovered_files = file_paths  # type: ignore

        logger.info(f"Discovered {len(file_paths)} source files")
        return PhaseResult.ok(items_processed=len(file_paths))

    def _discover_files(
        self,
        ctx: RuntimeContext,
        session: AnalysisSession,
        root: Path,
    ) -> list[Path]:
        """Walk directory tree to find source files."""
        from ...file_ops import should_skip_file
        from ...scanning import get_all_known_extensions
        from ...scanning.languages import SKIP_DIRS

        known_exts = get_all_known_extensions()
        config = session.config
        file_paths: list[Path] = []

        for p in root.rglob("*"):
            # Check cancellation
            if not ctx.should_continue:
                break

            if not p.is_file():
                continue

            # Skip excluded directories
            if any(part in SKIP_DIRS for part in p.parts):
                continue

            # Skip based on exclusion patterns
            if should_skip_file(p, config.exclude_patterns):
                continue

            # Check extension
            ext = p.suffix.lower()
            if ext not in known_exts:
                continue

            # Check file size
            try:
                if p.stat().st_size > config.max_file_size_bytes:
                    continue
            except OSError:
                continue

            file_paths.append(p)

            # Check file limit
            if len(file_paths) >= config.max_files:
                break

        return file_paths
