"""Live dashboard server for Shannon Insight.

Requires optional ``[serve]`` dependencies::

    pip install shannon-codebase-insight[serve]
"""

from __future__ import annotations


def _check_deps() -> None:
    """Raise a clear error if [serve] dependencies are missing."""
    missing = []
    try:
        import starlette  # noqa: F401
    except ImportError:
        missing.append("starlette")
    try:
        import uvicorn  # noqa: F401
    except ImportError:
        missing.append("uvicorn")
    try:
        import watchfiles  # noqa: F401
    except ImportError:
        missing.append("watchfiles")

    if missing:
        raise ImportError(
            f"Missing serve dependencies: {', '.join(missing)}. "
            "Install with: pip install shannon-codebase-insight[serve]"
        )
