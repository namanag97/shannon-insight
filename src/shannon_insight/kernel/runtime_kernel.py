"""RuntimeKernel — The new orchestrator for Shannon Insight analysis.

This module provides the RuntimeKernel, which replaces InsightKernel with:
- RuntimeContext integration (bounded resources, lifecycle, observability)
- Circuit breaker protection for failing phases
- Full error collection (no swallowing)
- Partial result support (continue on phase failure)
- Checkpoint/resume for long operations

Usage:
    >>> from shannon_insight.kernel import RuntimeKernel
    >>>
    >>> # Simple usage
    >>> kernel = RuntimeKernel(session)
    >>> result = kernel.run()
    >>> if result.success:
    ...     print(f"Found {len(result.findings)} issues")
    >>>
    >>> # With progress callback
    >>> def on_progress(msg, current, total):
    ...     print(f"{msg}: {current}/{total}")
    >>> result = kernel.run(on_progress=on_progress)
    >>>
    >>> # Access detailed metrics
    >>> print(result.metrics.summary())

Design:
    The kernel orchestrates 7 phases in order:
    1. DISCOVERY - Find source files
    2. SCANNING - Extract syntax
    3. STRUCTURAL - Build graph, compute centrality
    4. TEMPORAL - Extract git history
    5. FUSION - Compute signals
    6. PATTERNS - Detect issues
    7. REPORTING - Rank and capture snapshot

    Each phase:
    - Has a dedicated PhaseExecutor
    - Is protected by a circuit breaker
    - Reports progress via RuntimeContext
    - Can be skipped on timeout or repeated failures
"""

from __future__ import annotations

import concurrent.futures
from typing import TYPE_CHECKING, Callable, Optional

from ..infrastructure.runtime import (
    CancellationError,
    Phase,
    PhaseError,
    RuntimeContext,
    TimeoutError,
)
from ..logging_config import get_logger
from .phases import PHASE_EXECUTORS
from .result import PhaseResult, RuntimeResult

if TYPE_CHECKING:
    from ..insights.store import AnalysisStore
    from ..session import AnalysisSession

logger = get_logger(__name__)

# Type alias for progress callback
ProgressCallback = Optional[Callable[[str, int, int], None]]


class RuntimeKernel:
    """The new analysis orchestrator with RuntimeContext integration.

    RuntimeKernel replaces InsightKernel with:
    - Bounded execution (memory, time limits)
    - Circuit breaker protection (auto-skip failing phases)
    - Full observability (metrics, errors, warnings)
    - Partial results (continue when possible)
    - Graceful cancellation (Ctrl+C handled)

    Attributes:
        session: AnalysisSession with config and environment
        memory_limit_mb: Memory limit for the run
        total_timeout_seconds: Total timeout for all phases
        phase_timeout_seconds: Default timeout per phase

    Example:
        >>> kernel = RuntimeKernel(session)
        >>> result = kernel.run()
        >>> print(result.summary())
    """

    def __init__(
        self,
        session: AnalysisSession,
        memory_limit_mb: int = 2048,
        total_timeout_seconds: int = 1800,
        phase_timeout_seconds: int = 300,
        enable_provenance: bool = False,
        use_fact_store: bool = False,
    ):
        """Initialize the runtime kernel.

        Args:
            session: AnalysisSession with config and environment
            memory_limit_mb: Memory limit in MB (default: 2048)
            total_timeout_seconds: Total timeout in seconds (default: 1800)
            phase_timeout_seconds: Per-phase timeout in seconds (default: 300)
            enable_provenance: Enable provenance tracking
            use_fact_store: Enable persistent FactStore for caching and
                           identity resolution (.shannon/facts.db)
        """
        self.session = session
        self.memory_limit_mb = memory_limit_mb
        self.total_timeout_seconds = total_timeout_seconds
        self.phase_timeout_seconds = phase_timeout_seconds
        self.enable_provenance = enable_provenance
        self.use_fact_store = use_fact_store
        self._facts_db = None  # Lazy-initialized persistent FactStore

        # Phase executors (in order)
        self._executors = list(PHASE_EXECUTORS)

    def _get_facts_db(self):
        """Get or create the persistent FactStore (lazy init).

        Returns the facts.store.FactStore instance, creating it on first call
        if use_fact_store is enabled. Returns None if not enabled.
        """
        if not self.use_fact_store:
            return None
        if self._facts_db is None:
            from pathlib import Path

            from ..facts.store import FactStore as PersistentFactStore

            root = str(self.session.env.root)
            db_path = Path(root) / ".shannon" / "facts.db"
            db_path.parent.mkdir(parents=True, exist_ok=True)
            self._facts_db = PersistentFactStore.open(db_path)
            logger.debug(f"Opened persistent FactStore at {db_path}")
        return self._facts_db

    def run(
        self,
        max_findings: int = 10,
        on_progress: ProgressCallback = None,
    ) -> RuntimeResult:
        """Execute the full analysis pipeline.

        Args:
            max_findings: Maximum findings to return (default: 10)
            on_progress: Optional progress callback (msg, current, total)

        Returns:
            RuntimeResult with findings, snapshot, metrics, errors
        """
        from ..insights.store import AnalysisStore

        # Create runtime context
        ctx = RuntimeContext.create(
            root=self.session.env.root,
            config=self.session.config,
            env=self.session.env,
            memory_limit_mb=self.memory_limit_mb,
            total_timeout_seconds=self.total_timeout_seconds,
            progress_callback=on_progress,
        )

        # Create analysis store
        store = AnalysisStore(
            root_dir=str(self.session.env.root),
            session=self.session,
            enable_provenance=self.enable_provenance,
        )

        # Wire persistent FactStore if enabled
        facts_db = self._get_facts_db()
        if facts_db is not None:
            store.facts_db = facts_db

        # Track results
        errors: list[Exception] = []
        warnings: list[str] = []
        phases_completed = 0
        phases_failed = 0

        with ctx:
            try:
                # Run each phase in order
                for executor in self._executors:
                    # Check if we should continue
                    if not ctx.should_continue:
                        warnings.append("Analysis cancelled")
                        break

                    # Execute phase with circuit breaker protection
                    phase_result = self._execute_phase(ctx, store, executor)

                    if phase_result.success:
                        phases_completed += 1
                    else:
                        phases_failed += 1
                        if phase_result.error:
                            errors.append(phase_result.error)
                            ctx.record_error(phase_result.error)
                        # Continue with next phase (graceful degradation)

                # Transition to terminal state
                if ctx.should_continue and phases_failed == 0:
                    ctx.transition(Phase.COMPLETE)
                elif phases_completed > 0:
                    # Partial success
                    pass
                else:
                    ctx.transition(Phase.FAILED)

            except CancellationError as e:
                errors.append(e)
                ctx.transition(Phase.CANCELLED)
            except Exception as e:
                errors.append(e)
                ctx.record_error(e)
                ctx.transition(Phase.FAILED)

        # Build result
        insight_result = getattr(ctx, "_insight_result", None)
        snapshot = getattr(ctx, "_snapshot", None)
        findings = insight_result.findings if insight_result else []

        # Collect warnings from context
        warnings.extend(ctx.warnings)

        # Determine success status
        success = phases_failed == 0 and len(errors) == 0
        partial = phases_completed > 0 and (phases_failed > 0 or len(errors) > 0)
        cancelled = ctx.current_phase == Phase.CANCELLED

        return RuntimeResult(
            findings=findings,
            snapshot=snapshot,
            metrics=ctx.metrics,
            errors=errors,
            warnings=warnings,
            success=success,
            partial=partial,
            cancelled=cancelled,
        )

    def _execute_phase(
        self,
        ctx: RuntimeContext,
        store: AnalysisStore,
        executor,
    ) -> PhaseResult:
        """Execute a single phase with timeout and circuit breaker.

        Args:
            ctx: RuntimeContext
            store: AnalysisStore
            executor: PhaseExecutor to run

        Returns:
            PhaseResult indicating success or failure
        """
        phase = executor.phase

        # Check circuit breaker
        if phase in ctx._circuit_breakers and ctx._circuit_breakers[phase].is_open:
            logger.warning(f"Phase {phase.name} skipped (circuit open)")
            return PhaseResult.fail(PhaseError(f"Circuit breaker open for {phase.name}", phase))

        # Transition to phase
        try:
            with ctx.phase_context(phase):
                # Run with timeout
                timeout = getattr(executor, "timeout_seconds", self.phase_timeout_seconds)
                result = self._run_with_timeout(
                    lambda: executor.execute(ctx, store, self.session),
                    timeout,
                    executor.name,
                    phase,
                )
                return result
        except TimeoutError as e:
            logger.warning(f"Phase {phase.name} timed out")
            return PhaseResult.fail(e)
        except Exception as e:
            logger.warning(f"Phase {phase.name} failed: {e}")
            return PhaseResult.fail(PhaseError(str(e), phase, e))

    def _run_with_timeout(
        self,
        func: Callable[[], PhaseResult],
        timeout: float,
        name: str,
        phase: Phase,
    ) -> PhaseResult:
        """Run a function with timeout.

        Args:
            func: Function to run
            timeout: Timeout in seconds
            name: Name for error reporting
            phase: Phase for error context

        Returns:
            PhaseResult from func or fail result on timeout
        """
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(func)
            try:
                return future.result(timeout=timeout)
            except concurrent.futures.TimeoutError:
                raise TimeoutError(
                    f"Phase '{name}' exceeded {timeout}s timeout",
                    timeout_seconds=timeout,
                    phase=phase,
                )


def create_runtime_kernel(
    session: AnalysisSession,
    **kwargs,
) -> RuntimeKernel:
    """Factory function to create a RuntimeKernel.

    Args:
        session: AnalysisSession with config and environment
        **kwargs: Additional arguments passed to RuntimeKernel

    Returns:
        Configured RuntimeKernel instance
    """
    return RuntimeKernel(session, **kwargs)
