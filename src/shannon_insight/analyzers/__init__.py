"""Language analyzers"""

from .base import BaseScanner
from .scanner import ConfigurableScanner, BINARY_EXTENSIONS
from .languages import (
    LanguageConfig,
    LANGUAGES,
    DEFAULT_SOURCE_EXTENSIONS,
    get_language_config,
    get_all_known_extensions,
)


# ── Backward-compatible factory functions ──────────────────────────
# These return ConfigurableScanner instances configured for each language,
# preserving the old GoScanner(...), PythonScanner(...) etc. API.

def _make_compat_scanner(lang_name, root_dir, extensions=None, settings=None):
    cfg = get_language_config(lang_name)
    return ConfigurableScanner(root_dir, config=cfg, extensions=extensions, settings=settings)


class _ScannerFactory:
    """Creates backward-compatible scanner classes."""
    def __init__(self, lang_name):
        self._lang = lang_name

    def __call__(self, root_dir, extensions=None, settings=None):
        return _make_compat_scanner(self._lang, root_dir, extensions=extensions, settings=settings)


GoScanner = _ScannerFactory("go")
PythonScanner = _ScannerFactory("python")
TypeScriptScanner = _ScannerFactory("typescript")
JavaScanner = _ScannerFactory("java")
RustScanner = _ScannerFactory("rust")
CScanner = _ScannerFactory("c")
RubyScanner = _ScannerFactory("ruby")
UniversalScanner = _ScannerFactory("universal")


__all__ = [
    "BaseScanner",
    "ConfigurableScanner",
    "LanguageConfig",
    "LANGUAGES",
    "DEFAULT_SOURCE_EXTENSIONS",
    "BINARY_EXTENSIONS",
    "get_language_config",
    "get_all_known_extensions",
    "GoScanner",
    "PythonScanner",
    "TypeScriptScanner",
    "JavaScanner",
    "RustScanner",
    "CScanner",
    "RubyScanner",
    "UniversalScanner",
]
