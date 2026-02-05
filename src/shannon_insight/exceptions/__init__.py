"""Exception hierarchy for Shannon Insight."""

from .analysis import (
    AnalysisError,
    FileAccessError,
    InsufficientDataError,
    ParsingError,
    PrimitiveExtractionError,
    UnsupportedLanguageError,
)
from .base import ShannonInsightError
from .config import (
    ConfigurationError,
    InvalidConfigError,
    InvalidPathError,
    SecurityError,
)

__all__ = [
    "ShannonInsightError",
    "AnalysisError",
    "FileAccessError",
    "ParsingError",
    "UnsupportedLanguageError",
    "InsufficientDataError",
    "PrimitiveExtractionError",
    "ConfigurationError",
    "InvalidPathError",
    "InvalidConfigError",
    "SecurityError",
]
