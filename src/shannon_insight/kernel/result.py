"""RuntimeResult — The result of a RuntimeKernel execution.

This module provides the RuntimeResult dataclass, which captures the complete
outcome of an analysis run including:
- Findings and snapshot (the main outputs)
- Metrics (timing, memory, phase details)
- Errors and warnings (full observability)
- Status flags (success, partial, cancelled)

Example:
    >>> result = kernel.run()
    >>> if result.success:
    ...     print(f"Found {len(result.findings)} issues")
    >>> elif result.partial:
    ...     print(f"Partial results: {len(result.findings)} findings, {len(result.errors)} errors")
    >>> else:
    ...     print(f"Failed: {result.errors}")
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ..infrastructure.runtime import RuntimeMetrics
    from ..insights.models import Finding
    from ..persistence.models import TensorSnapshot


@dataclass
class RuntimeResult:
    """Complete result of a RuntimeKernel execution.

    This result captures everything that happened during analysis,
    enabling full observability and graceful handling of partial failures.

    Attributes:
        findings: List of code issues detected (may be empty)
        snapshot: TensorSnapshot for persistence (may be None on failure)
        metrics: RuntimeMetrics with timing and resource usage
        errors: List of exceptions that occurred (may be recoverable)
        warnings: List of warning messages
        success: True if analysis completed without errors
        partial: True if some phases succeeded but others failed
        cancelled: True if analysis was cancelled (Ctrl+C, timeout, etc.)

    Example:
        >>> result = kernel.run()
        >>> print(result.summary())
        RuntimeResult: SUCCESS
          Duration: 12.3s
          Findings: 15
          Phases: 7/7 complete
    """

    findings: list[Finding] = field(default_factory=list)
    snapshot: Optional[TensorSnapshot] = None
    metrics: Optional[RuntimeMetrics] = None
    errors: list[Exception] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    success: bool = False
    partial: bool = False
    cancelled: bool = False

    @property
    def status(self) -> str:
        """Human-readable status string."""
        if self.cancelled:
            return "CANCELLED"
        if self.success:
            return "SUCCESS"
        if self.partial:
            return "PARTIAL"
        return "FAILED"

    def summary(self) -> str:
        """Generate a human-readable summary of the result."""
        lines = [f"RuntimeResult: {self.status}"]

        if self.metrics:
            lines.append(f"  Duration: {self.metrics.duration_seconds:.1f}s")
            lines.append(f"  Memory peak: {self.metrics.memory_peak_mb:.0f}MB")

        lines.append(f"  Findings: {len(self.findings)}")

        if self.errors:
            lines.append(f"  Errors: {len(self.errors)}")
            for err in self.errors[:3]:  # Show first 3
                lines.append(f"    - {type(err).__name__}: {str(err)[:50]}")
            if len(self.errors) > 3:
                lines.append(f"    ... and {len(self.errors) - 3} more")

        if self.warnings:
            lines.append(f"  Warnings: {len(self.warnings)}")

        return "\n".join(lines)


@dataclass
class PhaseResult:
    """Result of a single phase execution.

    Each phase executor returns a PhaseResult to report success/failure
    and any phase-specific data.

    Attributes:
        success: True if phase completed without errors
        error: Exception if phase failed (None on success)
        data: Optional phase-specific data for downstream phases
        items_processed: Number of items processed in this phase
        items_failed: Number of items that failed processing
    """

    success: bool = True
    error: Optional[Exception] = None
    data: Optional[dict] = None
    items_processed: int = 0
    items_failed: int = 0

    @classmethod
    def ok(cls, items_processed: int = 0, data: Optional[dict] = None) -> "PhaseResult":
        """Create a successful phase result."""
        return cls(success=True, items_processed=items_processed, data=data)

    @classmethod
    def fail(cls, error: Exception, items_processed: int = 0) -> "PhaseResult":
        """Create a failed phase result."""
        return cls(success=False, error=error, items_processed=items_processed)
