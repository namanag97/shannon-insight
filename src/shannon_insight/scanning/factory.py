"""Scanner factory — resolves language setting to scanner instances."""

from pathlib import Path
from typing import Optional

from ..config import AnalysisConfig
from ..logging_config import get_logger
from . import (
    BINARY_EXTENSIONS,
    DEFAULT_SOURCE_EXTENSIONS,
    ConfigurableScanner,
    get_all_known_extensions,
    get_language_config,
)
from .languages import SKIP_DIRS

logger = get_logger(__name__)

_ALIASES = {
    "react": "typescript",
    "javascript": "typescript",
    "cpp": "c",
}


class ScannerFactory:
    """Resolves a language setting into a list of (scanner, lang_name) tuples."""

    def __init__(
        self,
        root_dir: Path,
        settings: AnalysisConfig,
        file_paths: Optional[tuple[Path, ...]] = None,
    ):
        """Initialize factory.

        Args:
            root_dir: Root directory to scan
            settings: Analysis configuration
            file_paths: Optional pre-discovered file paths (relative to root).
                        If provided, avoids redundant filesystem walks.
        """
        self.root_dir = root_dir
        self.settings = settings
        self.file_paths = file_paths

    def create(self, language: str) -> tuple[list[tuple], list[str]]:
        """Return (scanners, detected_languages)."""
        if language != "auto":
            return self._explicit(language)
        return self._auto_detect()

    def _mk(self, lang_name, display_name=None):
        cfg = get_language_config(lang_name)
        scanner = ConfigurableScanner(
            str(self.root_dir),
            config=cfg,
            settings=self.settings,
            file_paths=self.file_paths,
        )
        return (scanner, display_name or lang_name)

    def _explicit(self, language: str) -> tuple[list[tuple], list[str]]:
        base_lang = _ALIASES.get(language, language)
        if base_lang == "universal":
            cfg = get_language_config("universal")
            scanner = ConfigurableScanner(
                str(self.root_dir),
                config=cfg,
                extensions=list(DEFAULT_SOURCE_EXTENSIONS),
                settings=self.settings,
                file_paths=self.file_paths,
            )
            return [(scanner, language)], [language]
        return [self._mk(base_lang, language)], [language]

    def _auto_detect(self) -> tuple[list[tuple], list[str]]:
        # Single tree walk to collect ALL extensions (was: multiple rglob calls per extension)
        found_exts: set[str] = set()
        known_exts = get_all_known_extensions()

        for p in self.root_dir.rglob("*"):
            if p.is_file() and not any(part in SKIP_DIRS for part in p.parts):
                ext = p.suffix.lower()
                if ext:
                    found_exts.add(ext)

        # Now check which language configs match (O(1) set lookups)
        candidates = [
            ({".go"}, "go", "go"),
            ({".ts", ".tsx"}, "typescript", "typescript"),
            ({".py"}, "python", "python"),
            ({".java"}, "java", "java"),
            ({".rs"}, "rust", "rust"),
            ({".c", ".cpp", ".cc", ".h", ".hpp"}, "c/c++", "c"),
            ({".rb"}, "ruby", "ruby"),
        ]

        scanners = []
        for lang_exts, display_name, config_name in candidates:
            if found_exts & lang_exts:  # Set intersection - any match?
                logger.info(f"Auto-detected: {display_name} files")
                scanners.append(self._mk(config_name, display_name))

        # Unknown extensions → universal scanner
        unknown_exts = found_exts - known_exts - BINARY_EXTENSIONS
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
