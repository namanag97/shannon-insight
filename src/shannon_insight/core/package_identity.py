"""Runtime-visible identity for the bounded Shannon Codebase Insight application.

This module intentionally contains implementation identity, not horizontal semantic authority.
Research corpora remain outside the runtime package and qualification remains an external,
evidence-bearing decision.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class PackageIdentity:
    """Stable, non-promotional identity of the installed Python application."""

    application_id: str
    distribution_name: str
    import_package: str
    product_plane: str
    disposition: str
    industry_scope: Tuple[str, ...]
    horizontal_semantic_authority: bool
    qualified_contract_scope_count: int
    portable_offer_count: int
    executed_vertical_acceptance_count: int
    build_ready: bool
    ratified: bool

    def __post_init__(self) -> None:
        if self.horizontal_semantic_authority:
            raise ValueError("application package cannot claim horizontal semantic authority")
        if self.qualified_contract_scope_count < 0:
            raise ValueError("qualified_contract_scope_count cannot be negative")
        if self.portable_offer_count < 0:
            raise ValueError("portable_offer_count cannot be negative")
        if self.executed_vertical_acceptance_count < 0:
            raise ValueError("executed_vertical_acceptance_count cannot be negative")
        if self.build_ready or self.ratified:
            raise ValueError(
                "build-ready or ratified identity requires external evidence and cannot be minted here"
            )


_IDENTITY = PackageIdentity(
    application_id="application.codebase_engineering_intelligence",
    distribution_name="shannon-codebase-insight",
    import_package="shannon_insight",
    product_plane="APPLICATION_DOMAIN_PRODUCT",
    disposition="RETAIN_AS_APPLICATION_DOMAIN_REFERENCE_PRODUCT",
    industry_scope=(
        "software_engineering",
        "developer_productivity",
        "software_architecture_and_quality",
    ),
    horizontal_semantic_authority=False,
    qualified_contract_scope_count=0,
    portable_offer_count=0,
    executed_vertical_acceptance_count=0,
    build_ready=False,
    ratified=False,
)


def current_package_identity() -> PackageIdentity:
    """Return the immutable identity of this installed application distribution."""

    return _IDENTITY
