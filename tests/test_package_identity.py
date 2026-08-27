from __future__ import annotations

import pytest

from shannon_insight.core.package_identity import PackageIdentity, current_package_identity


def test_package_identity_is_application_domain_not_horizontal_platform() -> None:
    identity = current_package_identity()
    assert identity.application_id == "application.codebase_engineering_intelligence"
    assert identity.distribution_name == "shannon-codebase-insight"
    assert identity.product_plane == "APPLICATION_DOMAIN_PRODUCT"
    assert identity.horizontal_semantic_authority is False


def test_package_identity_cannot_mint_qualification_or_ratification() -> None:
    identity = current_package_identity()
    assert identity.qualified_contract_scope_count == 0
    assert identity.portable_offer_count == 0
    assert identity.executed_vertical_acceptance_count == 0
    assert identity.build_ready is False
    assert identity.ratified is False


def test_package_identity_refuses_promotional_construction() -> None:
    with pytest.raises(ValueError, match="horizontal semantic authority"):
        PackageIdentity(
            application_id="application.codebase_engineering_intelligence",
            distribution_name="shannon-codebase-insight",
            import_package="shannon_insight",
            product_plane="APPLICATION_DOMAIN_PRODUCT",
            disposition="RETAIN_AS_APPLICATION_DOMAIN_REFERENCE_PRODUCT",
            industry_scope=("software_engineering",),
            horizontal_semantic_authority=True,
            qualified_contract_scope_count=0,
            portable_offer_count=0,
            executed_vertical_acceptance_count=0,
            build_ready=False,
            ratified=False,
        )

    with pytest.raises(ValueError, match="external evidence"):
        PackageIdentity(
            application_id="application.codebase_engineering_intelligence",
            distribution_name="shannon-codebase-insight",
            import_package="shannon_insight",
            product_plane="APPLICATION_DOMAIN_PRODUCT",
            disposition="RETAIN_AS_APPLICATION_DOMAIN_REFERENCE_PRODUCT",
            industry_scope=("software_engineering",),
            horizontal_semantic_authority=False,
            qualified_contract_scope_count=0,
            portable_offer_count=0,
            executed_vertical_acceptance_count=0,
            build_ready=True,
            ratified=False,
        )
