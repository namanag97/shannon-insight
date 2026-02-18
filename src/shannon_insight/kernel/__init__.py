"""RuntimeKernel — The new analysis orchestrator for Shannon Insight.

This module provides the RuntimeKernel, which replaces InsightKernel with:
- RuntimeContext integration (bounded resources, lifecycle, observability)
- Circuit breaker protection for failing phases
- Full error collection (no swallowing)
- Partial result support (continue on phase failure)

Usage:
    >>> from shannon_insight.kernel import RuntimeKernel
    >>> from shannon_insight.session import AnalysisSession
    >>>
    >>> session = AnalysisSession(config, env)
    >>> kernel = RuntimeKernel(session)
    >>> result = kernel.run()
    >>>
    >>> if result.success:
    ...     print(f"Found {len(result.findings)} issues")
    >>> elif result.partial:
    ...     print(f"Partial: {len(result.findings)} findings, {len(result.errors)} errors")

Components:
    - RuntimeKernel: Main orchestrator
    - RuntimeResult: Complete result with findings, metrics, errors
    - PhaseResult: Result of a single phase
    - PhaseExecutor: Protocol for phase implementations
    - phases/: Individual phase executors
"""

from .executor import BaseExecutor, PhaseExecutor
from .result import PhaseResult, RuntimeResult
from .runtime_kernel import RuntimeKernel, create_runtime_kernel

__all__ = [
    # Main classes
    "RuntimeKernel",
    "RuntimeResult",
    "PhaseResult",
    # Executor protocol
    "PhaseExecutor",
    "BaseExecutor",
    # Factory function
    "create_runtime_kernel",
]
