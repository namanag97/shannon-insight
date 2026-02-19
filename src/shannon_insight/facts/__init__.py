"""Unified fact store for Shannon Insight.

This module provides immutable fact models, a content-addressable blob store,
and the SQL schema that ties them together.  Facts represent observed reality
(git commits, file content, parsed syntax) separated from derived signals.

Public API::

    from shannon_insight.facts import (
        # Enums
        ChangeType,
        # Identity & observation
        FileIdentity,
        FileObservation,
        # Git facts
        CommitFact,
        FileChangeFact,
        # Parsed facts
        ParsedSyntaxFact,
        ExtractedFunction,
        ExtractedClass,
        ExtractedImport,
        # Storage
        BlobStore,
        create_schema,
        SCHEMA_VERSION,
    )
"""

from shannon_insight.facts.blobs import BlobStore
from shannon_insight.facts.models import (
    ChangeType,
    CommitFact,
    ExtractedClass,
    ExtractedFunction,
    ExtractedImport,
    FileChangeFact,
    FileIdentity,
    FileObservation,
    ParsedSyntaxFact,
)
from shannon_insight.facts.schema import SCHEMA_VERSION, create_schema

__all__ = [
    # Enums
    "ChangeType",
    # Identity & observation
    "FileIdentity",
    "FileObservation",
    # Git facts
    "CommitFact",
    "FileChangeFact",
    # Parsed facts
    "ParsedSyntaxFact",
    "ExtractedFunction",
    "ExtractedClass",
    "ExtractedImport",
    # Storage
    "BlobStore",
    "create_schema",
    "SCHEMA_VERSION",
]
