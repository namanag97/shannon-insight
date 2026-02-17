"""Signal registry and computation for Shannon Insight.

Re-exports from infrastructure.signals for backward compatibility.
The authoritative Signal enum and REGISTRY live in infrastructure.signals.
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
