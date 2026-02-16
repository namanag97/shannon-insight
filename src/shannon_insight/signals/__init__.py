"""Signal registry and computation for Shannon Insight.

Exports the Signal enum (62+ signals) and REGISTRY with metadata.
"""

from .registry import (
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
