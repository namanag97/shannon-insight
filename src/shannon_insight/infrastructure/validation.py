"""Phase validation contracts -- re-export from canonical location.

The validation implementation lives in insights/validation.py (Pattern 4 from
infrastructure.md). This module re-exports for discoverability from the
infrastructure package.
"""

from shannon_insight.insights.validation import (
    PhaseValidationError,
    run_all_validations,
    validate_after_scanning,
    validate_after_structural,
    validate_signal_field,
)

__all__ = [
    "PhaseValidationError",
    "run_all_validations",
    "validate_after_scanning",
    "validate_after_structural",
    "validate_signal_field",
]
