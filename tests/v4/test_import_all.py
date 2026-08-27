"""Import-all smoke test: catches syntax errors, missing imports, and
undefined names at module scope across the whole package (FM-23 class gate).
"""

from __future__ import annotations

import importlib
import pkgutil

import shannon_insight

_ALLOWED_ROOTS = {"shannon_insight"}


V4_ROOTS = (
    "shannon_insight.core.",
    "shannon_insight.syntax.",
    "shannon_insight.facts.",
    "shannon_insight.intake.",
)


def _iter_modules():
    for mod in pkgutil.walk_packages(shannon_insight.__path__, prefix="shannon_insight."):
        if mod.name.startswith(V4_ROOTS):
            yield mod.name


def test_every_module_imports() -> None:
    failures: list[tuple[str, str]] = []
    for name in sorted(_iter_modules()):
        if name.split(".")[-1].startswith("_") and not name.endswith("__"):
            continue
        try:
            importlib.import_module(name)
        except Exception as exc:  # noqa: BLE001 - this IS the assertion
            failures.append((name, repr(exc)))
    assert not failures, "\n".join(f"{n}: {e}" for n, e in failures)
