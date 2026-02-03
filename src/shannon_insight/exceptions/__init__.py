"""Exception hierarchy for Shannon Insight."""

from .base import ShannonInsightError
from .analysis import (
    AnalysisError,
    FileAccessError,
    ParsingError,
    UnsupportedLanguageError,
    InsufficientDataError,
    PrimitiveExtractionError,
)
from .config import (
    ConfigurationError,
    InvalidPathError,
    InvalidConfigError,
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
