"""PhaseExecutor — Protocol for phase implementations.

Each phase in the pipeline is implemented as a PhaseExecutor. The protocol
defines the contract that all phase implementations must follow.

Design:
- Each executor is responsible for a single phase
- Executors report progress via ctx.advance()
- Executors check ctx.should_continue for cancellation
- Executors return PhaseResult (success or failure)
- Circuit breaker protection is handled by RuntimeKernel

Example:
    class ScanningExecutor(PhaseExecutor):
        phase = Phase.SCANNING
        timeout_seconds = 120

        def execute(self, ctx: RuntimeContext, store: AnalysisStore) -> PhaseResult:
            files = discover_files(ctx.root)
            ctx.set_phase_total(len(files))
            for f in files:
                if not ctx.should_continue:
                    return PhaseResult.fail(CancellationError())
                scan(f)
                ctx.advance()
            return PhaseResult.ok(items_processed=len(files))
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

from ..infrastructure.runtime import Phase

if TYPE_CHECKING:
    from ..infrastructure.runtime import RuntimeContext
    from ..insights.store import AnalysisStore
    from ..session import AnalysisSession

    from .result import PhaseResult


@runtime_checkable
class PhaseExecutor(Protocol):
    """Protocol for phase executors.

    Each phase executor implements the analysis logic for one phase
    of the pipeline. The RuntimeKernel orchestrates execution order,
    timeout handling, and circuit breaker protection.

    Attributes:
        phase: The Phase enum value this executor handles
        timeout_seconds: Maximum execution time for this phase
        name: Human-readable name for logging/progress

    Methods:
        execute: Run the phase against the store
    """

    phase: Phase
    timeout_seconds: int
    name: str

    def execute(
        self,
        ctx: "RuntimeContext",
        store: "AnalysisStore",
        session: "AnalysisSession",
    ) -> "PhaseResult":
        """Execute this phase of the analysis pipeline.

        Args:
            ctx: RuntimeContext for progress, cancellation, resource tracking
            store: AnalysisStore blackboard to read from and write to
            session: AnalysisSession with config and environment

        Returns:
            PhaseResult indicating success or failure

        Raises:
            Should NOT raise exceptions - wrap in PhaseResult.fail()

        Implementation Guidelines:
            1. Check ctx.should_continue regularly for cancellation
            2. Use ctx.set_phase_total() and ctx.advance() for progress
            3. Catch exceptions and return PhaseResult.fail(error)
            4. Return PhaseResult.ok() on success with items_processed
        """
        ...


class BaseExecutor:
    """Base class for phase executors with common functionality.

    Provides default implementations for common patterns:
    - Timeout handling
    - Progress reporting
    - Error wrapping

    Subclasses should override _execute() to implement phase logic.
    """

    phase: Phase
    timeout_seconds: int = 300  # 5 minutes default
    name: str = "BaseExecutor"

    def execute(
        self,
        ctx: "RuntimeContext",
        store: "AnalysisStore",
        session: "AnalysisSession",
    ) -> "PhaseResult":
        """Execute the phase with error handling.

        Wraps _execute() with try/except to ensure PhaseResult is returned.
        """
        from .result import PhaseResult

        try:
            return self._execute(ctx, store, session)
        except Exception as e:
            return PhaseResult.fail(e)

    def _execute(
        self,
        ctx: "RuntimeContext",
        store: "AnalysisStore",
        session: "AnalysisSession",
    ) -> "PhaseResult":
        """Override this method to implement phase logic.

        Args:
            ctx: RuntimeContext for progress and cancellation
            store: AnalysisStore to read/write
            session: AnalysisSession with config

        Returns:
            PhaseResult indicating success or failure
        """
        from .result import PhaseResult

        return PhaseResult.ok()
