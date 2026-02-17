"""Signal Registry — backward compatibility re-export.

DEPRECATED: Import from shannon_insight.infrastructure.signals instead.

This module re-exports the Signal enum and REGISTRY from infrastructure.signals
for backward compatibility. All signal definitions live in infrastructure/signals.py.
"""

from shannon_insight.infrastructure.signals import (
    REGISTRY,
    Signal,
    SignalMeta,
    percentileable_signals,
    register,
    signals_by_phase,
    signals_by_scope,
)

__all__ = [
    "REGISTRY",
    "Signal",
    "SignalMeta",
    "percentileable_signals",
    "register",
    "signals_by_phase",
    "signals_by_scope",
]
