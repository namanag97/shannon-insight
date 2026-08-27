#!/usr/bin/env python3
"""Build exact, provider-neutral data-marketplace contracts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
AS_OF = "2026-08-26"
EDITION = 1


def lines(rows: list[dict]) -> str:
    return "".join(json.dumps(row, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n" for row in rows)


def S(ident: str, title: str, publisher: str, url: str, scope: str, limit: str, kind: str = "official_specification") -> dict:
    return {"source_id": f"source.data-marketplace.{ident}", "title": title, "publisher": publisher,
            "url": url, "source_kind": kind, "claim_scope": scope, "scope_limit": limit}


SOURCES = [
    S("w3c.dcat3", "Data Catalog Vocabulary Version 3", "W3C", "https://www.w3.org/TR/vocab-dcat-3/", "catalog, catalog record, resource, dataset, distribution and data-service identity", "DCAT describes catalog resources; it does not define commercial offers, ranking, eligibility, approval, provisioning or consumption."),
    S("w3c.odrl22", "ODRL Information Model 2.2", "W3C", "https://www.w3.org/TR/odrl-model/", "policy, offer, agreement, party, asset, permission, prohibition, duty and constraint", "An ODRL Offer proposes rules but grants none; policy syntax does not prove authority, agreement, enforcement or fulfillment."),
    S("w3c.prov-o", "PROV-O: The PROV Ontology", "W3C", "https://www.w3.org/TR/prov-o/", "entity, activity, agent, attribution, derivation, delegation and invalidation", "Provenance records support assessment but do not prove source truth, approval, effect completion or billing correctness."),
    S("w3c.vc2", "Verifiable Credentials Data Model 2.0", "W3C", "https://www.w3.org/TR/vc-data-model-2.0/", "issuer, holder, verifier, presentation, evidence, status and validity", "Credential verification does not establish claim truth, issuer suitability for a use, eligibility or marketplace authority."),
    S("eclipse.dsp2025", "Dataspace Protocol 2025-1", "Eclipse Foundation", "https://eclipse-dataspace-protocol-base.github.io/DataspaceProtocol/", "catalog request, contract negotiation and transfer-process message/state protocols", "DSP coordinates data sharing; it does not define marketplace ranking, business approval, billing truth or application acceptance."),
    S("ids.ram4.offer", "IDS RAM 4: Data Offering", "International Data Spaces Association", "https://docs.internationaldataspaces.org/ids-knowledgebase/ids-ram-4/layers-of-the-reference-architecture-model/3-layers-of-the-reference-architecture-model/3_4_process_layer/3_4_2_data_offering", "provider data offering, self-description, broker and vocabulary references", "IDS offering is dataspace-specific and does not establish universal product, catalog or commercial semantics."),
    S("ids.ram4.negotiation", "IDS RAM 4: Contract Negotiation", "International Data Spaces Association", "https://docs.internationaldataspaces.org/ids-knowledgebase/ids-ram-4/layers-of-the-reference-architecture-model/3-layers-of-the-reference-architecture-model/3_4_process_layer/3_4_3_contract_negotiation", "offer, request, counter-offer, rejection, agreement, cancellation and signatures", "Negotiation state does not prove transfer, policy enforcement, use, payment or consumer acceptance."),
    S("tmf.tmf620", "Product Catalog Management API TMF620 v5", "TM Forum", "https://www.tmforum.org/open-digital-architecture/open-apis/product-catalog-management-api-TMF620/v5.0", "catalog, category, product specification and product offering management", "A telecom product-catalog API is evidence for identity and lifecycle separation, not a universal data-marketplace wire contract."),
    S("tmf.tmf679", "Product Offering Qualification API TMF679", "TM Forum", "https://www.tmforum.org/resources/standard/tmf679-product-offering-qualification-api-rest-specification-r19-0-0/", "task-based commercial-eligibility request and result", "Commercial qualification is not data-use-policy permission, business approval, entitlement or provisioned access."),
    S("tmf.tmf622", "Product Ordering Management API TMF622", "TM Forum", "https://www.tmforum.org/open-digital-architecture/open-apis/product-ordering-management-api-TMF622/v4.0", "orders based on catalog product offerings and order lifecycle", "Order semantics inform acquisition workflow but do not define data access, transfer or usage-control enforcement."),
    S("tmf.tmf651", "Agreement Management API TMF651", "TM Forum", "https://www.tmforum.org/resources/specifications/tmf651-agreement-management-api-rest-specification-r19-0-0/", "agreement specifications, agreement instances, offerings and engaged parties", "Agreement records do not establish signature authority, policy enforcement, fulfillment or payment."),
    S("tmf.tmf641", "Service Ordering Management API TMF641", "TM Forum", "https://www.tmforum.org/open-digital-architecture/open-apis/service-ordering-management-api-TMF641/v4.1", "service-order creation, update, retrieval, cancellation and notifications", "Service ordering is one fulfillment protocol and does not prove access, delivery contents or acceptance."),
    S("ietf.rfc7644", "RFC 7644: SCIM Protocol", "IETF", "https://www.rfc-editor.org/rfc/rfc7644.html", "cross-domain resource provisioning, retrieval, replacement, patching and deletion", "A SCIM success represents a provider resource effect only; it does not prove marketplace eligibility, entitlement semantics or usable data access."),
    S("ietf.rfc9110", "RFC 9110: HTTP Semantics", "IETF", "https://www.rfc-editor.org/rfc/rfc9110.html", "request methods, representations, status, validators, retries and caching", "HTTP success, location and validators do not establish business approval, semantic acceptance or downstream effect truth."),
    S("cncf.cloudevents1", "CloudEvents Specification 1.0", "CNCF", "https://github.com/cloudevents/spec/blob/v1.0.2/cloudevents/spec.md", "portable event envelope identity, source, type, subject, time and schema reference", "An event envelope does not define delivery, business semantics, authorization or state convergence."),
    S("nist.trec-relevance", "TREC English Relevance Judgments", "NIST", "https://trec.nist.gov/data/reljudge_eng.html", "query/document relevance judgments, pooling and collection-bound evaluation", "Relevance is assessor-, task-, corpus- and judgment-cut-bound; it is not truth, endorsement, eligibility or universal ranking quality."),
    S("finops.focus", "FOCUS Specification", "FinOps Foundation", "https://focus.finops.org/focus-specification/", "normalized technology billing, cost and usage records", "Usage and charge normalization does not make a marketplace observation an invoice, settlement or accounting truth."),
    S("iso.27560", "ISO/IEC TS 27560:2023 Consent record information structure", "ISO", "https://www.iso.org/standard/80392.html", "interoperable consent-record information structure", "Consent records are not generic commercial acceptance, data-use permission, fulfillment evidence or legal adjudication."),
    S("lf.odps41", "Open Data Product Specification 4.1", "Linux Foundation", "https://opendataproducts.org/v4.1/", "machine-readable data-product metadata, access, contracts, pricing, SLA and support references", "ODPS describes a product projection; it does not define marketplace offer authority, acquisition workflow or effect completion."),
]


def C(slug: str, name: str, question: str, outside: list[str]) -> dict:
    return {"context_id": f"context.data_marketplace.{slug}", "name": name, "sovereign_question": question,
            "inside": ["exact marketplace identities", "immutable editions", "typed decisions", "laws and refusals"],
            "outside": outside + ["provider qualification", "ambient persistence", "unauthorized external effects"],
            "owner": f"authority.data_marketplace.{slug}", "status": "specified_candidate"}


CONTEXTS = [
    C("merchandising", "Marketplace Merchandising", "For exact published product and terms editions, what offer is listable, visible, discoverable and rankable under an explicit catalog, audience and ranking cut?", ["data-product publication or product truth", "terms authorship", "policy permission", "recommendation authority"]),
    C("acquisition", "Marketplace Acquisition", "For an exact offer, consumer, purpose and evidence cut, what eligibility projection, request case, external decisions and fulfillment handoffs lead toward or refuse a subscription?", ["identity or credential issuance", "policy authorship and evaluation", "approval authority", "entitlement and provisioning effects"]),
    C("evidence", "Marketplace Evidence", "For an exact offer and subscription occurrence, what terms acknowledgements, usage references, charge references and marketplace receipts may be recorded without claiming downstream truth?", ["consent or agreement authority", "usage metering source truth", "invoice, settlement or accounting truth", "consumer outcome acceptance"]),
]


CONTEXT_BY_SEAM = {
    "offer_listing": "merchandising", "discovery_ranking": "merchandising", "eligibility_broker": "acquisition",
    "subscription_case": "acquisition", "fulfillment_handoff": "acquisition", "terms_usage_evidence": "evidence",
}


DECISIONS = {
    "offer_listing": ["offer_identity_authority", "bound_product_edition", "terms_and_price_editions", "audience_and_visibility", "listing_lifecycle", "publication_reconciliation"],
    "discovery_ranking": ["query_semantics", "facet_and_filter_profile", "candidate_coverage", "ranking_profile", "personalization_posture", "explanation_and_truncation"],
    "eligibility_broker": ["consumer_and_purpose_cut", "required_external_decisions", "credential_validation_profile", "combination_semantics", "indeterminate_posture", "eligibility_expiry"],
    "subscription_case": ["request_identity", "requested_offer_and_terms_cut", "approval_route", "maker_checker_policy", "case_timeout_and_withdrawal", "decision_reconciliation"],
    "fulfillment_handoff": ["provider_selection", "effect_protocol", "idempotency_scope", "completion_reconciliation", "subscription_binding", "termination_and_compensation"],
    "terms_usage_evidence": ["acknowledgement_semantics", "signer_authority_evidence", "usage_reference_scope", "charge_reference_scope", "receipt_disclosure", "retention_and_correction"],
}


DECISION_ROWS = [{"decision_id": f"decision.data_marketplace.{seam}.{decision}",
                  "owner_context": f"context.data_marketplace.{CONTEXT_BY_SEAM[seam]}",
                  "question": f"What exact {decision.replace('_', ' ')} applies?", "default": None,
                  "default_law": "forbidden", "status": "declared"}
                 for seam, values in DECISIONS.items() for decision in values]


def O(seam: str, name: str, inputs: list[str], output: str) -> dict:
    refusal = "".join(part.title() for part in seam.split("_")) + "Refusal"
    return {"operation_ref": f"operation.data_marketplace.{seam}.{name}", "input_types": inputs,
            "output_type": f"Result<{output},{refusal}>", "purity": "pure"}


def P(ident: str, name: str, kind: str, types: list[str], ops: list[dict], laws: list[str], errors: list[str], deps: list[str], evidence: list[str]) -> dict:
    return {"id": f"library.data_marketplace.{ident}", "seam": ident, "name": name, "kind": kind,
            "types": types, "ops": ops, "laws": laws, "errors": errors, "deps": deps,
            "evidence": [f"source.data-marketplace.{ref}" for ref in evidence]}


SPECS = [
    P("offer_listing", "Marketplace Offer and Listing Edition", "effect_port",
      ["MarketplaceOfferId", "OfferEditionId", "ListingEditionId", "OfferIssuerRef", "PublishedProductEditionRef", "TermsEditionRef", "PricePlanRef", "LicenseRef", "AudienceRef", "VisibilityScope", "TerritoryRef", "AvailabilityWindow", "OfferStatus", "ListingStatus", "OfferDraft", "ValidatedOfferEdition", "ListingPublicationIntent", "ListingPublicationReceipt", "ListingWithdrawalIntent", "OfferListingRefusal"],
      [O("offer_listing", "validate_offer_edition", ["OfferDraft", "OfferIdentityPolicy", "ExternalEditionBindings", "OfferIssuerAuthorityRef"], "ValidatedOfferEdition"), O("offer_listing", "derive_listing_projection", ["ValidatedOfferEdition", "ListingProfile", "AudiencePolicy"], "ListingProjection"), O("offer_listing", "plan_listing_publication", ["ListingProjection", "ListingTargetRef", "PublicationAuthorityRef", "PublicationPolicy"], "ListingPublicationIntent"), O("offer_listing", "plan_listing_withdrawal", ["ListingEditionId", "WithdrawalEvidence", "WithdrawalPolicy"], "ListingWithdrawalIntent")],
      ["Data product, published product edition, catalog resource, marketplace offer, offer edition, listing edition, policy offer, agreement, subscription and deployment are distinct.", "An offer binds exact externally owned product, terms, price, license, policy and support editions without acquiring their authority.", "ODRL Offer proposes rules and grants none; listed, visible, eligible, approved, agreed, provisioned, accessible and consumed remain distinct.", "Listing publication is an external effect intent reconciled from a target receipt; a receipt proves only the contracted listing effect.", "Listing visibility is audience- and time-bound and never implies endorsement, relevance, suitability or eligibility.", "Withdrawal, expiry, suspension, product recall, agreement termination, access revocation and deletion are distinct lifecycle acts."],
      ["OfferIssuerUnbound", "ProductEditionUnpublished", "ExternalEditionUnbound", "AudienceInvalid", "AvailabilityInvalid", "ListingConflict", "PublicationCompletionUnknown", "WithdrawalAuthorityMissing"], [],
      ["w3c.dcat3", "w3c.odrl22", "tmf.tmf620", "lf.odps41"]),
    P("discovery_ranking", "Marketplace Discovery and Ranking", "algorithm_pure",
      ["MarketplaceQuery", "QueryLanguageEdition", "CatalogCut", "AudienceCut", "CandidateOfferSet", "FacetDefinition", "FilterExpression", "SortExpression", "RankingProfileRef", "RankingFeatureRef", "RankingScore", "RankedOffer", "RankingEvidence", "CoverageEvidence", "TruncationMarker", "PersonalizationContext", "DiscoveryExplanation", "DiscoveryResult", "DiscoveryRankingRefusal"],
      [O("discovery_ranking", "normalize_marketplace_query", ["MarketplaceQuery", "QueryLanguageEdition", "NormalizationPolicy"], "NormalizedMarketplaceQuery"), O("discovery_ranking", "derive_candidate_offers", ["NormalizedMarketplaceQuery", "ListingProjectionSet", "CatalogCut", "CandidatePolicy"], "CandidateOfferSet"), O("discovery_ranking", "rank_candidate_offers", ["CandidateOfferSet", "RankingProfile", "RankingEvidenceCut", "ResourceBudget"], "RankedOfferSet"), O("discovery_ranking", "explain_discovery_result", ["RankedOfferSet", "CoverageEvidence", "ExplanationPolicy"], "DiscoveryResult")],
      ["Catalog membership, visibility, discoverability, query match, relevance judgment, ranking score, suitability, recommendation, eligibility and endorsement are distinct.", "Every result binds exact query, language, catalog, listing, audience, ranking-profile, feature, evidence, clock and resource cuts.", "Ranking score order has meaning only under the named profile; scores from different profiles or cuts are not silently comparable.", "Personalization is explicit, removable and bounded; it cannot acquire identity, purpose, policy or recommendation authority.", "Empty, filtered, truncated, timed-out and coverage-incomplete result sets remain distinct and none proves absence.", "Offline relevance judgments and click or selection observations are scoped evidence, not truth, product quality or causal benefit."],
      ["QueryUnsupported", "CatalogCutOpen", "AudienceUnresolved", "CandidateCoverageUnknown", "RankingProfileMissing", "FeatureUnavailable", "ResourceBudgetExceeded", "ResultTruncated", "ExplanationUnavailable"], ["library.data_marketplace.offer_listing"],
      ["w3c.dcat3", "nist.trec-relevance", "w3c.prov-o", "eclipse.dsp2025"]),
    P("eligibility_broker", "Marketplace Eligibility Evidence Broker", "algorithm_pure",
      ["EligibilityCaseId", "OfferEditionRef", "ConsumerRef", "PurposeRef", "EligibilityContextCut", "CredentialPresentationRef", "CredentialVerificationResultRef", "PolicyDecisionRef", "CommercialQualificationRef", "PublicationStateRef", "RequiredDecisionSet", "EligibilityEvidenceSet", "EvidenceAuthorityRef", "MarketplaceEligibilityStatus", "EligibilityReason", "EligibilityResidual", "EligibilityExpiry", "EligibilityExplanation", "EligibilityBrokerRefusal"],
      [O("eligibility_broker", "plan_eligibility_evidence_request", ["OfferEditionRef", "ConsumerRef", "PurposeRef", "EligibilityRequirements"], "EligibilityEvidenceRequestPlan"), O("eligibility_broker", "validate_eligibility_evidence", ["EligibilityEvidenceSet", "AuthorityTrustPolicy", "FreshnessPolicy"], "ValidatedEligibilityEvidence"), O("eligibility_broker", "derive_marketplace_eligibility", ["ValidatedEligibilityEvidence", "EligibilityCombinationPolicy", "EligibilityClock"], "MarketplaceEligibilityStatus"), O("eligibility_broker", "explain_marketplace_eligibility", ["MarketplaceEligibilityStatus", "EligibilityTrace", "DisclosurePolicy"], "EligibilityExplanation")],
      ["Discovery hint, marketplace eligibility, commercial qualification, data-use-policy decision, business approval, entitlement, provisioning and access are distinct.", "The marketplace requests and combines externally owned evidence; it does not issue identity, credentials, purpose, policy decisions, commercial qualification or entitlements.", "Credential verification proves integrity and status under a profile, not claim truth, issuer fitness or eligibility.", "Permit, deny, not-applicable, indeterminate, missing, stale and conflicting external decisions remain distinct until explicit combination.", "Every eligibility status binds exact offer, consumer, purpose, credential, policy, qualification, publication, evidence and clock cuts plus residuals and expiry.", "Eligibility never grants rights, signs an agreement, approves a request, provisions access or predicts consumer fitness."],
      ["ConsumerUnresolved", "PurposeMissing", "RequiredDecisionMissing", "CredentialInvalid", "IssuerUntrusted", "PolicyDecisionIndeterminate", "QualificationUnknown", "EvidenceConflict", "EligibilityExpired"], ["library.data_marketplace.offer_listing"],
      ["tmf.tmf679", "w3c.vc2", "w3c.odrl22", "eclipse.dsp2025"]),
    P("subscription_case", "Marketplace Subscription Request Case", "effect_port",
      ["SubscriptionRequestId", "RequestEditionId", "RequestorRef", "OfferEditionRef", "RequestedTermsEditionRef", "EligibilityStatusRef", "ApprovalRoute", "ApproverAuthorityRef", "ApprovalRequestIntent", "ApprovalDispatchReceipt", "ExternalApprovalDecisionRef", "RequestStatus", "RequestExpiry", "WithdrawalIntent", "NegotiationRef", "AgreementRef", "InFlightDisposition", "SubscriptionCase", "SubscriptionCaseRefusal"],
      [O("subscription_case", "validate_subscription_request", ["SubscriptionRequestDraft", "MarketplaceEligibilityStatus", "RequestPolicy"], "ValidatedSubscriptionRequest"), O("subscription_case", "plan_approval_route", ["ValidatedSubscriptionRequest", "ApprovalRoutingPolicy", "AuthorityDirectoryCut"], "ApprovalDispatchPlan"), O("subscription_case", "reconcile_external_decision", ["SubscriptionCase", "ExternalApprovalDecision", "DecisionValidationPolicy"], "SubscriptionCaseState"), O("subscription_case", "plan_request_withdrawal", ["SubscriptionCaseState", "WithdrawalAuthorityRef", "InFlightPolicy"], "WithdrawalIntent")],
      ["Subscription request, eligibility, approval request, approval decision, policy agreement, order, fulfillment, subscription binding and access are distinct.", "The marketplace owns the request case and routing plan but not approver identity, decision authority, negotiation agreement or effect execution.", "Maker-checker and separation-of-duty rules bind exact actors, roles, scopes and occurrences; organizational proximity never satisfies them.", "Approval dispatch or receipt is not approval; an external approval decision is validated and referenced rather than recreated.", "Request timeout, withdrawal, rejection, cancellation, agreement termination and fulfillment compensation are distinct.", "Unknown external completion is reconciled before retry; correlation and idempotency identities are explicit and bounded."],
      ["EligibilityUnsatisfied", "RequestConflict", "ApproverUnresolved", "ApprovalAuthorityInvalid", "MakerCheckerViolated", "DecisionSignatureInvalid", "RequestExpired", "WithdrawalForbidden", "DecisionCompletionUnknown"], ["library.data_marketplace.eligibility_broker"],
      ["tmf.tmf622", "tmf.tmf651", "ids.ram4.negotiation", "eclipse.dsp2025", "w3c.odrl22"]),
    P("fulfillment_handoff", "Marketplace Fulfillment Handoff", "effect_port",
      ["FulfillmentCaseId", "ApprovedRequestRef", "AgreementRef", "FulfillmentProviderRef", "ProviderQualificationRef", "ProvisioningTargetRef", "FulfillmentIntent", "FulfillmentAttemptId", "DispatchReceipt", "ProviderEffectReceipt", "ProvisionedResourceRef", "SubscriptionBindingId", "SubscriptionStatus", "AccessEvidenceRef", "TerminationIntent", "CompensationIntent", "CompletionStatus", "ReconciliationResult", "FulfillmentHandoffRefusal"],
      [O("fulfillment_handoff", "plan_fulfillment_handoff", ["ApprovedSubscriptionCase", "AgreementRef", "QualifiedProviderSet", "FulfillmentPolicy"], "FulfillmentIntent"), O("fulfillment_handoff", "reconcile_provider_receipt", ["FulfillmentIntent", "ProviderEffectReceipt", "ReceiptValidationPolicy"], "FulfillmentCompletionStatus"), O("fulfillment_handoff", "derive_subscription_binding", ["FulfillmentCompletionStatus", "AgreementRef", "BindingPolicy"], "SubscriptionBinding"), O("fulfillment_handoff", "plan_subscription_termination", ["SubscriptionBinding", "TerminationAuthorityRef", "TerminationPolicy"], "TerminationAndCompensationPlan")],
      ["Approved request, agreement, fulfillment intent, dispatch, provider effect, provisioned resource, entitlement, usable access, transfer, delivery and consumer acceptance are distinct.", "The marketplace coordinates a handoff and never self-provisions identity, entitlement, account, credential, endpoint, transfer or data-plane effect.", "Provider selection requires explicit qualification evidence; protocol compatibility or one successful response is not provider qualification.", "Every effect attempt binds request, agreement, provider, target, idempotency, clock and causal identities; unknown completion reconciles before retry.", "A provider receipt proves only the named provider effect under its contract; access and delivery require separately owned evidence.", "Termination, deprovisioning, access revocation, agreement termination, compensation, data deletion and subscription closure are distinct."],
      ["RequestUnapproved", "AgreementMissing", "ProviderUnqualified", "TargetUnsupported", "IdempotencyConflict", "DispatchUnknown", "ProviderReceiptInvalid", "ProvisioningUnknown", "BindingConflict", "TerminationAuthorityMissing", "CompensationOpen"], ["library.data_marketplace.subscription_case"],
      ["eclipse.dsp2025", "tmf.tmf641", "ietf.rfc7644", "ietf.rfc9110", "cncf.cloudevents1"]),
    P("terms_usage_evidence", "Marketplace Terms, Usage and Charge Evidence", "effect_port",
      ["MarketplaceEvidenceId", "SubscriptionBindingRef", "TermsEditionRef", "TermsAcknowledgement", "SignerRef", "SignerAuthorityEvidenceRef", "AcknowledgementInstant", "AgreementRef", "UsageObservationRef", "UsageSourceRef", "UsageCut", "ChargeReference", "BillingAccountRef", "InvoiceRef", "EvidenceProvenance", "MarketplaceReceipt", "CorrectionRef", "RetentionClassRef", "DisclosureView", "TermsUsageEvidenceRefusal"],
      [O("terms_usage_evidence", "validate_terms_acknowledgement", ["TermsAcknowledgement", "SignerAuthorityEvidence", "AcknowledgementPolicy"], "ValidatedTermsAcknowledgement"), O("terms_usage_evidence", "bind_usage_and_charge_references", ["SubscriptionBindingRef", "UsageObservationRefSet", "ChargeReferenceSet", "ReferencePolicy"], "MarketplaceEvidenceBundle"), O("terms_usage_evidence", "plan_marketplace_evidence_append", ["MarketplaceEvidenceBundle", "EvidenceStoreRef", "AppendPolicy"], "MarketplaceEvidenceAppendIntent"), O("terms_usage_evidence", "derive_marketplace_receipt", ["MarketplaceEvidenceBundle", "DisclosurePolicy", "RetentionPolicy"], "MarketplaceReceipt")],
      ["Terms text, terms edition, acknowledgement, consent, policy agreement, legal contract, signature, fulfillment and consumer acceptance are distinct.", "The marketplace validates and references external signer identity and authority; it does not create consent, agreement or legal validity.", "Usage observation, metered quantity, normalized billing record, charge, invoice, settlement, payment and accounting entry are distinct.", "A marketplace usage or charge reference preserves source, scope, unit, time and provenance and never becomes source or invoice truth.", "Marketplace receipt proves only included marketplace occurrences; it does not prove policy enforcement, delivered contents, useful consumption or outcome value.", "Append, disclosure, correction, retention, legal hold and deletion are explicit effects owned by their respective services and reconciled by receipts."],
      ["TermsEditionUnbound", "SignerUnresolved", "SignerAuthorityInvalid", "AcknowledgementAmbiguous", "UsageScopeExcessive", "UsageSourceUnbound", "ChargeReferenceUnresolved", "EvidenceConflict", "RetentionUnbound", "AppendCompletionUnknown"], ["library.data_marketplace.fulfillment_handoff"],
      ["w3c.odrl22", "w3c.prov-o", "iso.27560", "finops.focus", "tmf.tmf678"]),
]


def materialize(spec: dict) -> dict:
    seam = spec["seam"]
    return {"library_id": spec["id"], "name": spec["name"], "library_kind": spec["kind"],
            "semantic_owner_context": f"context.data_marketplace.{CONTEXT_BY_SEAM[seam]}", "status": "specified",
            "candidate_responsibility": spec["name"].lower(),
            "effect_boundary": "pure_effect_intents" if spec["kind"] == "effect_port" else "pure_no_io",
            "public_types": spec["types"], "public_traits": [spec["name"].replace(" ", "") + "Algebra"],
            "operation_refs": [op["operation_ref"] for op in spec["ops"]], "operations": spec["ops"],
            "decision_refs": [f"decision.data_marketplace.{seam}.{decision}" for decision in DECISIONS[seam]],
            "configuration_contracts": [spec["name"].replace(" ", "") + "Policy"], "laws": spec["laws"],
            "invariants": ["every identity, edition, authority, evidence cut, policy, time, state, intent and receipt is explicit",
                           "listing, discovery, eligibility, request, approval, agreement, fulfillment, access, usage, charge and acceptance remain distinct",
                           "no model or agent may issue identity, establish truth, rank with hidden semantics, approve, agree, provision, authorize access, accept evidence or ratify an outcome"],
            "error_contracts": spec["errors"] + ["UnsupportedEdition", "InvalidConfiguration", "ResourceBudgetExceeded"],
            "dependencies": spec["deps"], "evidence_refs": spec["evidence"],
            "oracles": ["canonical positive fixtures", "negative twins", "property and metamorphic laws", "total lifecycle model tests", "ranking and coverage corpus", "effect retry/reconciliation corpus", "two independent differential implementations"],
            "gaps": ["No implementation is qualified; two independent implementations and executed conformance remain required."],
            "must_not_own": ["data-product publication or source truth", "identity, credential, purpose or policy authority", "business approval or legal agreement authority", "entitlement, provisioning, access, transfer or delivery effects", "usage-metering, invoice, settlement or accounting truth", "consumer fitness, acceptance or outcome truth", "provider qualification"],
            "qualification_required": False}


LIBRARIES = [materialize(spec) for spec in SPECS]


NEGATIVES = [
    ("product_offer", "A data product, published edition, offer and listing are the same identity.", "Bind exact external editions and keep their owners and lifecycles distinct."),
    ("offer_grant", "An ODRL or commercial offer grants permission or access.", "Treat an offer as proposed terms; require separate agreement, policy, approval and fulfillment evidence."),
    ("listing_endorsement", "A visible listing is endorsed, relevant, suitable or eligible.", "Limit visibility to its audience, target and effective cut."),
    ("publication_listing", "Publishing a data product automatically creates or updates an offer listing.", "Require independent offer authority and listing effect receipt."),
    ("rank_truth", "Rank or score proves quality, truth or recommendation authority.", "Bind profile, features, evidence and cut; expose the explanation and limits."),
    ("empty_absence", "An empty marketplace query proves no offer exists.", "Distinguish filters, audience, coverage, truncation, timeout and absence."),
    ("click_relevance", "Clicks or selections prove relevance or causal value.", "Treat observations as biased scoped evidence, never truth."),
    ("credential_truth", "A verified credential proves its claims are true or sufficient for eligibility.", "Validate issuer suitability, status, purpose and policy separately."),
    ("permit_eligible", "A policy permit alone proves marketplace eligibility.", "Combine all named external decisions under an explicit policy and preserve residuals."),
    ("eligible_approved", "Eligibility approves a request, signs an agreement or grants access.", "Keep eligibility, approval, agreement, entitlement and effects separate."),
    ("dispatch_approval", "Approval request dispatch or delivery means approval.", "Reconcile a signed external decision from an authorized approver."),
    ("approval_provision", "Approval or agreement proves provisioning completed.", "Issue an effect intent and reconcile the provider's exact receipt."),
    ("provider_success_qualified", "A protocol response or successful provisioning attempt qualifies a provider.", "Require independent conformance and provider qualification evidence."),
    ("receipt_access", "A provisioning receipt proves usable data access or delivered contents.", "Keep provider effect, entitlement, access, transfer, delivery and acceptance evidence distinct."),
    ("retry_duplicate", "Unknown completion may be retried as a new request.", "Reconcile first and bind an explicit idempotency identity."),
    ("acceptance_consent", "Acknowledging marketplace terms creates consent, a legal agreement or policy permission.", "Reference the independently authoritative artifacts and signer authority."),
    ("usage_invoice", "Marketplace usage observations or charge references are invoice truth.", "Preserve source, unit, cut and provenance; let billing own invoice and settlement truth."),
    ("receipt_outcome", "A marketplace receipt proves useful consumption, product fitness or outcome value.", "Limit the receipt to exact marketplace occurrences and disclosed evidence."),
    ("termination_delete", "Subscription termination implies access revocation, deletion and obligations completed.", "Coordinate separately owned effects and preserve residual obligations."),
    ("agent_authority", "A model or agent may rank opaquely, decide eligibility, approve, negotiate, provision, accept evidence or ratify outcomes.", "Allow attributed proposals only; deterministic policies and named authorities retain consequential decisions."),
]


NEGATIVE_ROWS = [{"negative_id": f"negative.data-marketplace.{slug}", "unsafe_inference": unsafe,
                  "required_behavior": required, "status": "active"} for slug, unsafe, required in NEGATIVES]


COMPILER_ROWS = []
for library in LIBRARIES:
    stem = library["library_id"].removeprefix("library.")
    COMPILER_ROWS += [
        {"record_kind": "capability_requirement", "requirement_id": f"requirement.{stem}.implementation", "subject_ref": library["library_id"], "required_operations": library["operation_refs"], "required_decisions": library["decision_refs"], "fallback_law": "refuse", "status": "declared"},
        {"record_kind": "capability_offer", "offer_id": f"offer.{stem}.reference", "subject_ref": library["library_id"], "claimed_operations": library["operation_refs"], "qualified_implementation_count": 0, "portable": False, "selectable": False, "status": "specified_unimplemented"},
        {"record_kind": "binding_rule", "binding_rule_id": f"binding.{stem}", "requirement_ref": f"requirement.{stem}.implementation", "offer_ref": f"offer.{stem}.reference", "structural_match": True, "selection_law": "Structural match never promotes an unqualified or non-portable implementation.", "selectable": False, "status": "declared"},
    ]


FILES = {"sources.jsonl": SOURCES, "bounded-contexts.jsonl": CONTEXTS, "decision-points.jsonl": DECISION_ROWS,
         "library-contracts.jsonl": LIBRARIES, "compiler-contracts.jsonl": COMPILER_ROWS, "negative-twins.jsonl": NEGATIVE_ROWS}


def main() -> None:
    digests = {}
    for name, rows in FILES.items():
        payload = lines(rows)
        (ROOT / name).write_text(payload, encoding="utf-8")
        digests[name] = {"records": len(rows), "sha256": hashlib.sha256(payload.encode()).hexdigest()}
    manifest = {"manifest_id": "data_marketplace_governance_v0_1_0", "as_of": AS_OF, "edition": EDITION,
                "status": "specified_unimplemented_open_world", "files": digests, "completion_claim": False,
                "qualified_implementation_count": 0}
    (ROOT / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"BUILD PASS data marketplace: {len(SOURCES)} sources, {len(CONTEXTS)} contexts, {len(DECISION_ROWS)} decisions, {len(LIBRARIES)} exact libraries, {len(COMPILER_ROWS)} compiler contracts")


if __name__ == "__main__":
    main()
