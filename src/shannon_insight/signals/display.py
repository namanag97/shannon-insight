"""Display scale conversion for composite scores.

All composites are computed as [0,1] internally but displayed on a
1-10 scale for user readability. This matches CodeScene's Code Health
scale and is more intuitive.

Usage:
    internal = 0.64
    display = to_display_scale(internal)  # Returns 6.4

JSON output provides both:
    {
        "risk_score": 0.64,
        "risk_score_display": 6.4
    }
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def to_display_scale(value: float) -> float:
    """Convert internal [0,1] composite to user-facing [1,10] scale.

    Rules:
    1. Clamp input to [0, 1] (log warning if out of range)
    2. Multiply by 10
    3. Round to 1 decimal place
    4. Floor at 1.0 (never show 0.0 on display scale)

    Args:
        value: Internal composite value in [0, 1]

    Returns:
        Display value in [1.0, 10.0]
    """
    # Warn and clamp if out of range
    if value > 1.0:
        logger.warning(f"Composite value {value:.4f} exceeds 1.0, clamping")
        value = 1.0
    if value < 0.0:
        logger.warning(f"Composite value {value:.4f} below 0.0, clamping")
        value = 0.0

    # Convert to 10-scale
    display = round(value * 10, 1)

    # Floor at 1.0 (avoid showing 0.0)
    return max(1.0, display)


def format_health_score(value: float) -> str:
    """Format a health score for display with color hint.

    Args:
        value: Internal composite value in [0, 1]

    Returns:
        Formatted string like "7.5/10" with health interpretation
    """
    display = to_display_scale(value)

    if display >= 8.0:
        status = "healthy"
    elif display >= 6.0:
        status = "fair"
    elif display >= 4.0:
        status = "warning"
    else:
        status = "critical"

    return f"{display:.1f}/10 ({status})"
