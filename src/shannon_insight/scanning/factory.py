"""Scanner factory — resolves language setting to scanner instances."""

from pathlib import Path
from typing import List, Tuple

from ..config import AnalysisSettings
from ..logging_config import get_logger
from . import (
    BINARY_EXTENSIONS,
    DEFAULT_SOURCE_EXTENSIONS,
    ConfigurableScanner,
    get_all_known_extensions,
    get_language_config,
)

logger = get_logger(__name__)

_SKIP_DIRS = {"venv", ".venv", "node_modules", "__pycache__", ".git", "dist", "build", "target"}

_ALIASES = {
    "react": "typescript",
    "javascript": "typescript",
    "cpp": "c",
}


class ScannerFactory:
    """Resolves a language setting into a list of (scanner, lang_name) tuples."""

    def __init__(self, root_dir: Path, settings: AnalysisSettings):
        self.root_dir = root_dir
        self.settings = settings

    def create(self, language: str) -> Tuple[List[Tuple], List[str]]:
        """Return (scanners, detected_languages)."""
        if language != "auto":
            return self._explicit(language)
        return self._auto_detect()

    def _mk(self, lang_name, display_name=None):
        cfg = get_language_config(lang_name)
        scanner = ConfigurableScanner(str(self.root_dir), config=cfg, settings=self.settings)
        return (scanner, display_name or lang_name)

    def _explicit(self, language: str) -> Tuple[List[Tuple], List[str]]:
        base_lang = _ALIASES.get(language, language)
        if base_lang == "universal":
            cfg = get_language_config("universal")
            scanner = ConfigurableScanner(
                str(self.root_dir),
                config=cfg,
                extensions=list(DEFAULT_SOURCE_EXTENSIONS),
                settings=self.settings,
            )
            return [(scanner, language)], [language]
        return [self._mk(base_lang, language)], [language]

    def _auto_detect(self) -> Tuple[List[Tuple], List[str]]:
        def _has_ext(ext: str) -> bool:
            for p in self.root_dir.rglob(f"*{ext}"):
                if not any(part in _SKIP_DIRS for part in p.parts):
                    return True
            return False

        candidates = [
            (_has_ext(".go"), "go", "go"),
            (_has_ext(".ts") or _has_ext(".tsx"), "typescript", "typescript"),
            (_has_ext(".py"), "python", "python"),
            (_has_ext(".java"), "java", "java"),
            (_has_ext(".rs"), "rust", "rust"),
            (_has_ext(".c") or _has_ext(".cpp") or _has_ext(".cc") or _has_ext(".h"), "c/c++", "c"),
            (_has_ext(".rb"), "ruby", "ruby"),
        ]

        known_exts = get_all_known_extensions()
        scanners = []
        for detected, display_name, config_name in candidates:
            if detected:
                logger.info(f"Auto-detected: {display_name} files")
                scanners.append(self._mk(config_name, display_name))

        # Unknown extensions → universal scanner
        unknown_exts: set[str] = set()
        for p in self.root_dir.rglob("*"):
            if p.is_file() and not any(part in _SKIP_DIRS for part in p.parts):
                ext = p.suffix.lower()
                if ext and ext not in known_exts and ext not in BINARY_EXTENSIONS:
                    unknown_exts.add(ext)

        if unknown_exts:
            logger.info(f"Auto-detected unknown extensions for universal scanner: {unknown_exts}")
            cfg = get_language_config("universal")
            scanner = ConfigurableScanner(
                str(self.root_dir),
                config=cfg,
                extensions=sorted(unknown_exts),
                settings=self.settings,
            )
            scanners.append((scanner, "universal"))

        if not scanners:
            logger.warning("Could not auto-detect language, falling back to universal scanner")
            cfg = get_language_config("universal")
            scanner = ConfigurableScanner(
                str(self.root_dir),
                config=cfg,
                extensions=list(DEFAULT_SOURCE_EXTENSIONS),
                settings=self.settings,
            )
            scanners.append((scanner, "universal"))

        detected_langs = [lang for _, lang in scanners]
        return scanners, detected_langs
