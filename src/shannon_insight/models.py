"""Backward-compatible re-exports.

Canonical locations:
- FileMetrics       → scanning.models
- Primitives        → signals.models
- PrimitiveValues   → signals.models
"""

from .scanning.models import FileMetrics as FileMetrics  # noqa: F401 — re-export
from .signals.models import Primitives as Primitives  # noqa: F401 — re-export
from .signals.models import PrimitiveValues as PrimitiveValues  # noqa: F401 — re-export
