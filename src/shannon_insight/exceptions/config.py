"""Configuration and security exceptions: paths, settings, access control."""

from pathlib import Path
from typing import Any, Optional

from .base import ShannonInsightError


class ConfigurationError(ShannonInsightError):
    """Base class for configuration-related errors."""

    pass


class InvalidPathError(ConfigurationError):
    """Raised when a provided path is invalid."""

    def __init__(self, path: Path, reason: str):
        super().__init__(f"Invalid path: {path}", details={"path": str(path), "reason": reason})
        self.path = path
        self.reason = reason


class InvalidConfigError(ConfigurationError):
    """Raised when configuration values are invalid."""

    def __init__(self, key: str, value: Any, reason: str):
        super().__init__(
            f"Invalid configuration for {key}: {value}",
            details={"key": key, "value": str(value), "reason": reason},
        )
        self.key = key
        self.value = value
        self.reason = reason


class SecurityError(ConfigurationError):
    """Raised when a security violation is detected."""

    def __init__(self, reason: str, filepath: Optional[Path] = None):
        details = {"reason": reason}
        if filepath:
            details["filepath"] = str(filepath)

        super().__init__(f"Security violation: {reason}", details=details)
        self.reason = reason
        self.filepath = filepath
