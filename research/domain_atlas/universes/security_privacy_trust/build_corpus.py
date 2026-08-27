#!/usr/bin/env python3
"""Deterministically build the security, privacy, and trust candidate universe.

The source is intentionally plain Python data so that review happens in version control.  It
contains hypotheses and compiler vocabulary, not legal advice or claims of completeness.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SCHEMAS = HERE / "schemas"
EDITION = 1
AS_OF = "2026-08-25"
STATUS = "sourced_candidate"
SURFACES = (
    "source_occurrences",
    "types_shapes",
    "pipelines",
    "persistence",
    "runtime",
    "governance",
    "lineage",
    "consumption",
)


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_jsonl(path: Path, values: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for value in values:
            handle.write(json.dumps(value, sort_keys=True) + "\n")


def write_manifest() -> None:
    artifacts = sorted(p for p in HERE.rglob("*.json*") if p.name != "manifest.json" and "__pycache__" not in p.parts)
    files = {str(p.relative_to(HERE)): {"bytes": len(p.read_bytes()), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()} for p in artifacts}
    write_json(HERE / "manifest.json", {"manifest_id": "manifest.security-privacy-trust.v1", "edition": EDITION, "files": files, "completion_claim": False})


def source(
    source_id: str,
    title: str,
    publisher: str,
    url: str,
    domains: list[str],
    claim: str,
    *,
    kind: str = "primary_standard",
    date: str | None = None,
    limitation: str = "Defines a bounded control, protocol, model, or result; it does not establish end-to-end platform sufficiency.",
) -> dict:
    return {
        "source_id": source_id,
        "edition": EDITION,
        "status": STATUS,
        "title": title,
        "publisher": publisher,
        "source_kind": kind,
        "url": url,
        "publication_date": date,
        "accessed_at": AS_OF,
        "domains": domains,
        "claim_supported": claim,
        "authority_scope": "Publisher-controlled specification, guidance, implementation documentation, law, or original research.",
        "limitations": limitation,
        "occurrences": [
            {"registry": "bounded-context-candidates", "concept": domains[0]},
            *[{"registry": "capabilities", "concept": domain} for domain in domains[1:3]],
        ],
    }


# Primary authorities dominate this registry.  Research papers are original peer-reviewed work,
# not surveys.  Legal texts are evidence of obligation vocabulary only; compiler lowering is a
# separate, explicitly fallible step.
SOURCES = [
    source("src.nist.privacy-framework-1", "NIST Privacy Framework 1.0", "NIST", "https://www.nist.gov/privacy-framework/privacy-framework", ["privacy-risk", "data-processing", "governance"], "Privacy risk management and cybersecurity risk management overlap but are not interchangeable.", date="2020-01-16", kind="authority_framework"),
    source("src.nist.ir8062", "An Introduction to Privacy Engineering and Risk Management in Federal Systems", "NIST", "https://csrc.nist.gov/pubs/ir/8062/final", ["privacy-risk", "predictability", "manageability", "disassociability"], "Privacy engineering objectives can be treated as distinct system properties.", date="2017-01", kind="authority_guidance"),
    source("src.nist.sp800-53r5", "Security and Privacy Controls for Information Systems and Organizations", "NIST", "https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final", ["controls", "audit", "access", "privacy"], "Control objectives require tailoring and evidence; catalog presence is not implementation proof.", date="2020-09", kind="authority_guidance"),
    source("src.nist.sp800-63-4", "Digital Identity Guidelines", "NIST", "https://csrc.nist.gov/pubs/sp/800/63/4/final", ["identity", "authentication", "federation"], "Identity proofing, authentication, and federation use distinct assurance models.", date="2025-07", kind="authority_guidance"),
    source("src.nist.sp800-162", "Guide to Attribute Based Access Control Definition and Considerations", "NIST", "https://csrc.nist.gov/pubs/sp/800/162/upd2/final", ["authorization", "attributes", "policy"], "ABAC evaluates subject, object, action and environment attributes against policy.", date="2019-02", kind="authority_guidance"),
    source("src.nist.sp800-207", "Zero Trust Architecture", "NIST", "https://csrc.nist.gov/pubs/sp/800/207/final", ["zero-trust", "policy-decision", "policy-enforcement"], "Policy decision and policy enforcement are separate trust-boundary roles.", date="2020-08", kind="authority_guidance"),
    source("src.nist.sp800-57p1r5", "Recommendation for Key Management: Part 1", "NIST", "https://csrc.nist.gov/pubs/sp/800/57/pt1/r5/final", ["key-management", "cryptoperiod", "key-lifecycle"], "Key purpose, strength, cryptoperiod, storage and compromise response are lifecycle decisions.", date="2020-05", kind="authority_guidance"),
    source("src.nist.sp800-188", "De-Identifying Government Datasets: Techniques and Governance", "NIST", "https://csrc.nist.gov/pubs/sp/800/188/final", ["deidentification", "governance", "reidentification-risk"], "De-identification is a governed risk-management process, not a one-time field transform.", date="2023-03", kind="authority_guidance"),
    source("src.nist.sp800-226", "Guidelines for Evaluating Differential Privacy Guarantees", "NIST", "https://csrc.nist.gov/pubs/sp/800/226/final", ["differential-privacy", "privacy-budget", "evaluation"], "Differential privacy implementations require evaluation beyond the mathematical definition.", date="2025-03-06", kind="authority_guidance"),
    source("src.nist.sp800-92", "Guide to Computer Security Log Management", "NIST", "https://csrc.nist.gov/pubs/sp/800/92/final", ["audit", "logging", "retention"], "Log generation, transmission, storage, analysis and disposal have distinct operational risks.", date="2006-09", kind="authority_guidance"),
    source("src.nist.sp800-61r3", "Incident Response Recommendations and Considerations for Cybersecurity Risk Management", "NIST", "https://csrc.nist.gov/pubs/sp/800/61/r3/final", ["incident-response", "evidence", "recovery"], "Incident response integrates preparation, detection, response and recovery with governance.", date="2025-04", kind="authority_guidance"),
    source("src.nist.sp800-218", "Secure Software Development Framework Version 1.1", "NIST", "https://csrc.nist.gov/pubs/sp/800/218/final", ["software-supply-chain", "secure-development", "provenance"], "Secure development practices require protected artifacts and provenance-capable processes.", date="2022-02", kind="authority_guidance"),
    source("src.nist.csf2", "Cybersecurity Framework 2.0", "NIST", "https://www.nist.gov/cyberframework", ["govern", "identify", "protect", "detect", "respond", "recover"], "Cybersecurity outcomes span governance through recovery and require organization-specific profiles.", date="2024-02-26", kind="authority_framework"),
    source("src.nist.fips203", "FIPS 203: Module-Lattice-Based Key-Encapsulation Mechanism Standard", "NIST", "https://csrc.nist.gov/pubs/fips/203/final", ["post-quantum", "key-establishment", "crypto-agility"], "ML-KEM standardizes post-quantum key encapsulation with defined parameter sets.", date="2024-08-13"),
    source("src.nist.fips204", "FIPS 204: Module-Lattice-Based Digital Signature Standard", "NIST", "https://csrc.nist.gov/pubs/fips/204/final", ["post-quantum", "digital-signature", "crypto-agility"], "ML-DSA standardizes post-quantum digital signatures with defined parameter sets.", date="2024-08-13"),
    source("src.nist.fips205", "FIPS 205: Stateless Hash-Based Digital Signature Standard", "NIST", "https://csrc.nist.gov/pubs/fips/205/final", ["post-quantum", "digital-signature", "crypto-agility"], "SLH-DSA provides a stateless hash-based post-quantum signature family.", date="2024-08-13"),
    source("src.w3c.prov-o", "PROV-O: The PROV Ontology", "W3C", "https://www.w3.org/TR/prov-o/", ["provenance", "entity", "activity", "agent"], "Entities, activities, agents and derivation relations form a provenance model."),
    source("src.w3c.odrl-model", "ODRL Information Model 2.2", "W3C", "https://www.w3.org/TR/odrl-model/", ["data-use-policy", "permission", "prohibition", "duty"], "Permissions, prohibitions and duties can be expressed as policy, but enforcement is out of model scope."),
    source("src.w3c.dpv2", "Data Privacy Vocabulary 2.0", "W3C Data Privacy Vocabularies and Controls Community Group", "https://www.w3.org/community/reports/dpvcg/CG-FINAL-dpv-20240801/", ["purpose", "personal-data", "processing", "legal-basis", "rights"], "DPV supplies machine-readable vocabulary for privacy concepts without deciding local legal applicability.", date="2024-08-01", kind="community_specification"),
    source("src.w3c.webauthn3", "Web Authentication Level 3", "W3C", "https://www.w3.org/TR/webauthn-3/", ["authentication", "public-key-credential", "attestation", "phishing-resistance"], "WebAuthn separates relying party, client and authenticator roles and scopes credentials to relying parties.", date="2026-05-26", kind="candidate_recommendation"),
    source("src.w3c.vc2", "Verifiable Credentials Data Model 2.0", "W3C", "https://www.w3.org/TR/vc-data-model-2.0/", ["credential", "issuer", "holder", "verifier", "status"], "Issuance, holding and verification are distinct roles; a verified credential is not authorization by itself.", date="2025-05-15"),
    source("src.w3c.vc-data-integrity", "Verifiable Credential Data Integrity 1.0", "W3C", "https://www.w3.org/TR/vc-data-integrity/", ["proof", "verification", "cryptographic-integrity"], "Data integrity proofs bind secured data and cryptographic material under explicit verification algorithms.", date="2025-05-15"),
    source("src.w3c.trace-context", "Trace Context Level 2", "W3C", "https://www.w3.org/TR/trace-context-2/", ["trace-context", "correlation", "privacy"], "Cross-boundary trace identifiers aid correlation but create privacy and abuse risks.", kind="candidate_recommendation"),
    source("src.ietf.rfc6749", "RFC 6749: The OAuth 2.0 Authorization Framework", "IETF", "https://www.rfc-editor.org/rfc/rfc6749", ["authorization", "grant", "token-issuance"], "An authorization grant is exchanged for an access token; approval, issuance and enforcement are distinct events."),
    source("src.ietf.rfc9700", "RFC 9700: Best Current Practice for OAuth 2.0 Security", "IETF", "https://www.rfc-editor.org/rfc/rfc9700", ["oauth-security", "token-replay", "least-privilege"], "Modern OAuth security guidance deprecates unsafe flows and recommends sender constraints and restricted privilege.", date="2025-01"),
    source("src.ietf.rfc9449", "RFC 9449: OAuth 2.0 Demonstrating Proof of Possession", "IETF", "https://www.rfc-editor.org/rfc/rfc9449", ["proof-of-possession", "token-replay", "nonce"], "A DPoP proof demonstrates key possession but is not itself authentication or access control.", date="2023-09"),
    source("src.ietf.rfc7643", "RFC 7643: System for Cross-domain Identity Management Core Schema", "IETF", "https://www.rfc-editor.org/rfc/rfc7643", ["identity-provisioning", "principal", "group"], "SCIM defines interoperable resource schemas for users and groups."),
    source("src.ietf.rfc7644", "RFC 7644: System for Cross-domain Identity Management Protocol", "IETF", "https://www.rfc-editor.org/rfc/rfc7644", ["identity-provisioning", "lifecycle", "bulk-operation"], "SCIM protocol operations provision and deprovision identity resources across domains."),
    source("src.ietf.rfc8446", "RFC 8446: The Transport Layer Security Protocol Version 1.3", "IETF", "https://www.rfc-editor.org/rfc/rfc8446", ["transport-security", "confidentiality", "integrity"], "TLS protects a transport channel; it does not authorize application data use."),
    source("src.ietf.rfc9180", "RFC 9180: Hybrid Public Key Encryption", "IETF", "https://www.rfc-editor.org/rfc/rfc9180", ["encryption", "key-establishment", "context-binding"], "HPKE composes key encapsulation, derivation and authenticated encryption modes.", date="2022-02"),
    source("src.ietf.rfc9334", "RFC 9334: Remote ATtestation procedureS Architecture", "IETF", "https://www.rfc-editor.org/rfc/rfc9334", ["remote-attestation", "evidence", "endorsement", "result"], "Attestation evidence, endorsements, appraisal policy and attestation results are different artifacts.", date="2023-01"),
    source("src.ietf.rfc9052", "RFC 9052: CBOR Object Signing and Encryption", "IETF", "https://www.rfc-editor.org/rfc/rfc9052", ["signing", "encryption", "message-security"], "COSE defines signed, MACed and encrypted message structures with algorithm controls.", date="2022-08"),
    source("src.ietf.rfc8725", "RFC 8725: JSON Web Token Best Current Practices", "IETF", "https://www.rfc-editor.org/rfc/rfc8725", ["token-validation", "algorithm-confusion", "context-separation"], "JWT validation must constrain algorithms and separate validation rules across token kinds."),
    source("src.ietf.rfc9458", "RFC 9458: Oblivious HTTP", "IETF", "https://www.rfc-editor.org/rfc/rfc9458", ["oblivious-transport", "unlinkability", "relay"], "Oblivious HTTP separates client identity visibility from message content visibility.", date="2024-01"),
    source("src.ietf.rfc9576", "RFC 9576: The Privacy Pass Architecture", "IETF", "https://www.rfc-editor.org/rfc/rfc9576", ["privacy-pass", "unlinkable-token", "anti-abuse"], "Privacy Pass balances unlinkable authorization with issuance and redemption controls.", date="2024-06"),
    source("src.ietf.rfc9635", "RFC 9635: Grant Negotiation and Authorization Protocol", "IETF", "https://www.rfc-editor.org/rfc/rfc9635", ["authorization", "grant-negotiation", "continuation"], "GNAP models grant negotiation, key-bound access and continuation as explicit protocol artifacts.", date="2024-10"),
    source("src.ietf.rfc9162", "RFC 9162: Certificate Transparency Version 2.0", "IETF", "https://www.rfc-editor.org/rfc/rfc9162", ["transparency-log", "inclusion-proof", "consistency-proof"], "Merkle log inclusion and consistency proofs support detection of equivocation and omission.", date="2021-12"),
    source("src.oasis.xacml3", "eXtensible Access Control Markup Language 3.0 Core", "OASIS", "https://docs.oasis-open.org/xacml/3.0/xacml-3.0-core-spec-os-en.html", ["authorization-policy", "policy-decision", "attributes", "obligations"], "XACML separates policy administration, decision, information and enforcement roles."),
    source("src.oasis.saml2", "Security Assertion Markup Language 2.0 Core", "OASIS", "https://docs.oasis-open.org/security/saml/v2.0/saml-core-2.0-os.pdf", ["federation", "assertion", "authentication-statement", "authorization-decision"], "SAML distinguishes authentication, attribute and authorization-decision statements."),
    source("src.oasis.kmip21", "Key Management Interoperability Protocol Specification 2.1", "OASIS", "https://docs.oasis-open.org/kmip/kmip-spec/v2.1/os/kmip-spec-v2.1-os.html", ["key-management", "cryptographic-object", "lifecycle-operation"], "KMIP defines typed cryptographic objects, attributes and lifecycle operations.", date="2020-12"),
    source("src.oasis.csaf2", "Common Security Advisory Framework 2.0", "OASIS", "https://docs.oasis-open.org/csaf/csaf/v2.0/os/csaf-v2.0-os.html", ["vulnerability-advisory", "product-status", "remediation"], "CSAF represents machine-readable product vulnerability advisories and status.", date="2022-11"),
    source("src.spiffe.spec", "SPIFFE Identity and Verifiable Identity Document Specifications", "SPIFFE / CNCF", "https://github.com/spiffe/spiffe/tree/main/standards", ["workload-identity", "trust-domain", "svid", "federation"], "SPIFFE assigns workload identities in trust domains and defines verifiable identity documents.", kind="open_source_specification"),
    source("src.opa.docs", "Open Policy Agent Documentation", "Open Policy Agent / CNCF", "https://www.openpolicyagent.org/docs/latest/", ["policy-decision", "policy-bundle", "decision-log", "partial-evaluation"], "OPA evaluates policy separately from application enforcement and supports signed bundles and decision logs.", kind="open_source_specification"),
    source("src.cedar.spec", "Cedar Policy Language Specification", "Cedar", "https://docs.cedarpolicy.com/", ["authorization-policy", "schema", "validation", "entity"], "Cedar defines an analyzable authorization language with schema validation and explicit principal/action/resource requests.", kind="open_source_specification", date="2023"),
    source("src.k8s.secrets", "Good Practices for Kubernetes Secrets", "Kubernetes / CNCF", "https://kubernetes.io/docs/concepts/security/secrets-good-practices/", ["secrets", "rbac", "encryption-at-rest"], "Secrets require least-privilege API access and protection at rest and in distribution.", kind="official_documentation"),
    source("src.k8s.multitenancy", "Multi-tenancy", "Kubernetes / CNCF", "https://kubernetes.io/docs/concepts/security/multi-tenancy/", ["tenancy", "namespace-isolation", "node-isolation", "network-isolation"], "Multi-tenancy requires control-plane and data-plane isolation choices appropriate to trust level.", kind="official_documentation"),
    source("src.otel.logs", "OpenTelemetry Logs Data Model", "OpenTelemetry / CNCF", "https://opentelemetry.io/docs/specs/otel/logs/data-model/", ["logs", "trace-correlation", "severity", "resource"], "Log records carry event time, observed time, severity, resource, scope and trace correlation as distinct fields.", kind="open_source_specification"),
    source("src.openlineage.spec", "OpenLineage Specification", "OpenLineage / LF AI & Data", "https://github.com/OpenLineage/OpenLineage/blob/main/spec/OpenLineage.md", ["lineage", "run", "job", "dataset", "facets"], "Observed run events and dataset facets convey lineage but do not prove correctness.", kind="open_source_specification"),
    source("src.slsa.v1", "Supply-chain Levels for Software Artifacts 1.0", "OpenSSF", "https://slsa.dev/spec/v1.0/", ["supply-chain", "provenance", "build-integrity"], "SLSA defines producer-focused build and provenance requirements.", date="2023-04", kind="open_source_specification"),
    source("src.in-toto.attestation", "in-toto Attestation Framework", "in-toto / CNCF", "https://github.com/in-toto/attestation/tree/main/spec", ["attestation", "statement", "predicate", "subject"], "Attestations bind subjects to typed predicates through a common statement envelope.", kind="open_source_specification"),
    source("src.tuf.spec", "The Update Framework Specification", "TUF / CNCF", "https://theupdateframework.github.io/specification/latest/", ["software-update", "rollback", "freeze", "key-compromise"], "Threshold roles, versioning and expiration mitigate update rollback, freeze and key compromise.", kind="open_source_specification"),
    source("src.sigstore.architecture", "Sigstore Architecture", "Sigstore / OpenSSF", "https://docs.sigstore.dev/about/system_config/", ["signature", "transparency-log", "short-lived-certificate"], "Sigstore combines identity-bound short-lived certificates, signatures and transparency logging.", kind="official_documentation"),
    source("src.spdx3", "SPDX Specification 3.0.1", "SPDX / Linux Foundation", "https://spdx.github.io/spdx-spec/v3.0.1/", ["sbom", "artifact-identity", "relationship"], "SPDX represents systems, software, packages, files and their relationships for supply-chain evidence.", date="2024", kind="open_source_specification"),
    source("src.cyclonedx16", "CycloneDX Specification 1.6", "OWASP Foundation", "https://cyclonedx.org/docs/1.6/json/", ["sbom", "vulnerability", "cryptographic-asset", "data-governance"], "CycloneDX models components, services, vulnerabilities, cryptographic assets and annotations.", date="2024", kind="open_source_specification"),
    source("src.confidential-containers", "Confidential Containers Documentation", "Confidential Containers / CNCF", "https://confidentialcontainers.org/docs/", ["confidential-computing", "attestation", "workload-isolation"], "Confidential containers combine hardware-isolated execution with attestation-aware workload launch.", kind="official_documentation", date="2022"),
    source("src.edpb.pseudonymisation", "Guidelines 01/2025 on Pseudonymisation", "European Data Protection Board", "https://www.edpb.europa.eu/our-work-tools/documents/public-consultations/2025/guidelines-012025-pseudonymisation_en", ["pseudonymisation", "additional-information", "risk"], "Pseudonymised data remains personal data when attribution using additional information remains possible.", date="2025-01-16", kind="privacy_authority_guidance"),
    source("src.ico.anonymisation", "Anonymisation, pseudonymisation and privacy enhancing technologies guidance", "UK Information Commissioner's Office", "https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/data-sharing/anonymisation/", ["anonymisation", "pseudonymisation", "reidentification-risk"], "Anonymisation and pseudonymisation require different risk and governance treatment.", kind="privacy_authority_guidance"),
    source("src.cnil.pia", "Privacy Impact Assessment Method", "CNIL", "https://www.cnil.fr/en/privacy-impact-assessment-pia", ["privacy-impact", "risk", "controls"], "A privacy impact assessment links processing context, risk scenarios, controls and residual risk.", kind="privacy_authority_guidance"),
    source("src.eu.gdpr", "Regulation (EU) 2016/679", "European Union", "https://eur-lex.europa.eu/eli/reg/2016/679/oj", ["legal-obligation", "purpose-limitation", "rights", "retention"], "The regulation supplies legal obligation vocabulary; applicability and lawful basis require competent interpretation.", kind="primary_law", limitation="Primary legal text used only to identify obligation vocabulary; this corpus does not give legal advice or determine applicability."),
    source("src.usenix.zanzibar", "Zanzibar: Google's Consistent, Global Authorization System", "USENIX", "https://www.usenix.org/conference/atc19/presentation/pang", ["authorization", "relationship-tuples", "consistency"], "A relationship-based authorization service can model group membership and object relations at scale.", kind="peer_reviewed_original_research", date="2019"),
    source("src.ndss.macaroons", "Macaroons: Cookies with Contextual Caveats for Decentralized Authorization in the Cloud", "NDSS", "https://www.ndss-symposium.org/ndss2014/programme/macaroons-cookies-contextual-caveats-decentralized-authorization-cloud/", ["capability-token", "attenuation", "caveat"], "Capabilities can be attenuated with contextual caveats without central reissuance.", kind="peer_reviewed_original_research", date="2014"),
    source("src.linddun.paper", "LINDDUN privacy threat modeling methodology", "LINDDUN / KU Leuven", "https://linddun.org/", ["privacy-threat", "linkability", "detectability", "unawareness"], "Privacy threat modeling requires categories beyond confidentiality threats.", kind="official_method_documentation", date="2011"),
    source("src.k-anonymity.paper", "k-Anonymity: A Model for Protecting Privacy", "International Journal of Uncertainty, Fuzziness and Knowledge-Based Systems", "https://doi.org/10.1142/S0218488502001648", ["k-anonymity", "quasi-identifier", "deidentification"], "k-anonymity bounds equivalence-class size but not attribute disclosure or arbitrary auxiliary information.", kind="peer_reviewed_original_research", date="2002"),
    source("src.l-diversity.paper", "l-Diversity: Privacy Beyond k-Anonymity", "ACM", "https://doi.org/10.1145/1217299.1217302", ["l-diversity", "attribute-disclosure", "deidentification"], "l-diversity addresses some homogeneous sensitive-value risks left by k-anonymity.", kind="peer_reviewed_original_research", date="2007"),
    source("src.t-closeness.paper", "t-Closeness: Privacy Beyond k-Anonymity and l-Diversity", "IEEE", "https://doi.org/10.1109/ICDE.2007.367856", ["t-closeness", "distribution-disclosure", "deidentification"], "t-closeness constrains divergence between class and population sensitive-value distributions.", kind="peer_reviewed_original_research", date="2007"),
    source("src.dp.paper", "Differential Privacy", "ICALP / Microsoft Research", "https://www.microsoft.com/en-us/research/publication/differential-privacy/", ["differential-privacy", "privacy-loss", "composition"], "Differential privacy provides a composable bound on output distribution change from one individual's data.", kind="peer_reviewed_original_research", date="2006"),
    source("src.prio.paper", "Prio: Private, Robust, and Scalable Computation of Aggregate Statistics", "USENIX", "https://www.usenix.org/conference/nsdi17/technical-sessions/presentation/corrigan-gibbs", ["secure-aggregation", "secret-sharing", "robustness"], "Distributed aggregation can reveal approved aggregates without revealing each participant's value.", kind="peer_reviewed_original_research", date="2017"),
    source("src.psi.paper", "Private Set Intersection: Are Garbled Circuits Better than Custom Protocols?", "USENIX", "https://www.usenix.org/conference/usenixsecurity12/technical-sessions/presentation/huang", ["private-set-intersection", "secure-computation", "leakage"], "PSI reveals a set intersection subject to protocol-specific leakage and adversary assumptions.", kind="peer_reviewed_original_research", date="2012"),
    source("src.sgx.paper", "Innovative Instructions and Software Model for Isolated Execution", "ACM", "https://doi.org/10.1145/2487726.2488368", ["trusted-execution", "enclave", "attestation"], "Hardware enclaves isolate code and data under a hardware-specific threat model.", kind="peer_reviewed_original_research", date="2013"),
    source("src.privacy-budget-ledger.paper", "Privacy Budget Scheduling", "USENIX", "https://www.usenix.org/conference/osdi21/presentation/lécuyer", ["privacy-budget", "scheduling", "accounting"], "A privacy resource scheduler can allocate and track budgets across analytical workloads.", kind="peer_reviewed_original_research", date="2021"),
]


EVIDENCE_BY_DOMAIN = {
    "identity": ["src.nist.sp800-63-4", "src.ietf.rfc7643", "src.ietf.rfc7644", "src.w3c.webauthn3", "src.oasis.saml2", "src.spiffe.spec", "src.w3c.vc2", "src.w3c.vc-data-integrity"],
    "authorization": ["src.nist.sp800-162", "src.oasis.xacml3", "src.cedar.spec", "src.ietf.rfc6749", "src.ietf.rfc8725", "src.usenix.zanzibar", "src.ndss.macaroons"],
    "policy": ["src.nist.sp800-207", "src.oasis.xacml3", "src.opa.docs"],
    "secrets": ["src.nist.sp800-57p1r5", "src.oasis.kmip21", "src.k8s.secrets"],
    "crypto": ["src.nist.sp800-57p1r5", "src.ietf.rfc8446", "src.ietf.rfc9180"],
    "tenancy": ["src.k8s.multitenancy", "src.nist.sp800-207", "src.confidential-containers"],
    "privacy": ["src.nist.privacy-framework-1", "src.nist.ir8062", "src.w3c.dpv2", "src.cnil.pia", "src.w3c.trace-context"],
    "consent": ["src.w3c.odrl-model", "src.w3c.dpv2", "src.eu.gdpr"],
    "retention": ["src.eu.gdpr", "src.nist.sp800-53r5", "src.nist.sp800-92"],
    "rights": ["src.eu.gdpr", "src.w3c.dpv2", "src.nist.privacy-framework-1"],
    "deidentification": ["src.nist.sp800-188", "src.edpb.pseudonymisation", "src.ico.anonymisation", "src.k-anonymity.paper", "src.l-diversity.paper", "src.t-closeness.paper"],
    "differential_privacy": ["src.nist.sp800-226", "src.dp.paper", "src.privacy-budget-ledger.paper"],
    "secure_computation": ["src.prio.paper", "src.psi.paper", "src.sgx.paper"],
    "threat": ["src.nist.csf2", "src.linddun.paper", "src.nist.sp800-53r5"],
    "audit": ["src.nist.sp800-92", "src.otel.logs", "src.w3c.prov-o", "src.openlineage.spec"],
    "evidence": ["src.w3c.prov-o", "src.ietf.rfc9334", "src.ietf.rfc9162"],
    "supply_chain": ["src.slsa.v1", "src.in-toto.attestation", "src.tuf.spec", "src.sigstore.architecture"],
    "incident": ["src.nist.sp800-61r3", "src.nist.csf2", "src.otel.logs"],
}


def evidence(domain: str) -> list[str]:
    return EVIDENCE_BY_DOMAIN[domain]


def cross_map(domain: str, _evidence_ids: list[str]) -> dict:
    vocabulary = {
        "identity": ["principal_ref", "credential_ref", "assurance_level"],
        "authorization": ["principal_action_resource", "policy_ref", "decision_receipt"],
        "policy": ["policy_set", "attribute_bag", "obligation"],
        "secrets": ["secret_handle", "version_ref", "lease"],
        "crypto": ["key_ref", "algorithm_suite", "cryptoperiod"],
        "tenancy": ["tenant_ref", "isolation_class", "resource_scope"],
        "privacy": ["data_category", "data_subject_ref", "processing_context"],
        "consent": ["purpose_ref", "permission", "withdrawal_state"],
        "retention": ["retention_rule", "disposition_due", "legal_hold_ref"],
        "rights": ["request_ref", "verified_subject", "response_scope"],
        "deidentification": ["release_profile", "quasi_identifier_set", "risk_measure"],
        "differential_privacy": ["privacy_unit", "epsilon_delta", "budget_ledger_ref"],
        "secure_computation": ["participant_ref", "approved_function", "leakage_profile"],
        "threat": ["asset_ref", "trust_boundary_ref", "abuse_precondition"],
        "audit": ["actor_ref", "action", "object_ref", "event_time"],
        "evidence": ["subject_digest", "predicate_type", "signature_ref"],
        "supply_chain": ["artifact_digest", "builder_identity", "provenance_ref"],
        "incident": ["case_ref", "observation_ref", "chain_of_custody"],
    }[domain]
    return {
        "source_occurrences": [f"source_boundary:{domain}", f"source_authority:{vocabulary[0]}", "source_read_write_scope"],
        "types_shapes": vocabulary,
        "pipelines": [f"gate:{domain}", f"propagate:{vocabulary[0]}", "refuse:unknown_semantics"],
        "persistence": [f"partition:{domain}", "encrypt:declared_policy", "retain:declared_schedule"],
        "runtime": [f"enforce:{domain}", "fail_closed_when_required", "emit_scoped_receipt"],
        "governance": [f"owner:{domain}", "policy_edition", "exception_expiry"],
        "lineage": ["bind_input_output_identity", "record_policy_and_decision", "preserve_evidence_links"],
        "consumption": ["authorize_consumer", "constrain_use_and_egress", "account_for_disclosure"],
    }


CONTEXT_SEEDS = [
    ("identity_principal", "identity", "Identity Principal", "Owns stable principal references and lifecycle; not authentication or authorization."),
    ("authentication", "identity", "Authentication", "Establishes confidence in a presented principal; does not grant data access."),
    ("credential_lifecycle", "identity", "Credential Lifecycle", "Owns credential enrollment, issuance, rotation, suspension and revocation."),
    ("workload_identity", "identity", "Workload Identity", "Owns runtime workload principals and attested identity documents."),
    ("federation_trust", "identity", "Federation Trust", "Owns cross-domain issuer, audience, metadata and trust-anchor agreements."),
    ("authorization_policy", "authorization", "Authorization Policy", "Owns prospective principal/action/resource rules; not authentication."),
    ("policy_information", "policy", "Policy Information", "Owns authoritative attributes and freshness evidence used in decisions."),
    ("policy_decision", "policy", "Policy Decision", "Owns permit, deny, indeterminate and obligations; not enforcement."),
    ("policy_enforcement", "policy", "Policy Enforcement", "Owns interception and faithful enforcement at the effect boundary."),
    ("entitlement_relationship", "authorization", "Entitlement Relationship", "Owns relationship tuples, groups and delegated grants."),
    ("approval_workflow", "authorization", "Approval Workflow", "Owns human or automated approval; approval is not token or credential issuance."),
    ("capability_token", "authorization", "Capability Token", "Owns attenuated, audience-bound capabilities and caveats."),
    ("secrets_management", "secrets", "Secrets Management", "Owns opaque secret versions, leases and delivery; not general configuration."),
    ("key_management", "crypto", "Key Management", "Owns cryptographic key purpose, custody, rotation, destruction and compromise state."),
    ("cryptographic_policy", "crypto", "Cryptographic Policy", "Owns approved suites, strengths, modes and migration decisions."),
    ("encryption_protection", "crypto", "Encryption Protection", "Owns confidentiality transforms and envelope metadata; not access authorization."),
    ("tenancy_boundary", "tenancy", "Tenancy Boundary", "Owns tenant identity and isolation expectations across control and data planes."),
    ("isolation_control", "tenancy", "Isolation Control", "Owns process, compute, storage, network and metadata separation mechanisms."),
    ("data_classification", "privacy", "Data Classification", "Owns security sensitivity labels; not privacy purpose or lawful basis."),
    ("privacy_purpose", "privacy", "Privacy Purpose", "Owns declared purposes and compatibility relations; not security classification."),
    ("consent_permission", "consent", "Consent and Permission", "Owns recorded permission state and withdrawal; not every legal basis."),
    ("data_use_agreement", "consent", "Data-use Agreement", "Owns platform-readable permissions, prohibitions and duties."),
    ("residency_locality", "privacy", "Residency and Locality", "Owns allowed storage, processing, transit and support locations."),
    ("retention_disposition", "retention", "Retention and Disposition", "Owns event-based schedules, holds, deletion and disposition proof."),
    ("rights_request", "rights", "Data-subject Rights Request", "Owns verified scope, fulfillment orchestration and response evidence."),
    ("minimization_collection", "privacy", "Collection and Minimization", "Owns necessity, proportionality and field-level collection gates."),
    ("deidentification", "deidentification", "De-identification", "Owns release transforms and governed risk claims."),
    ("reidentification_risk", "deidentification", "Re-identification Risk", "Owns attacker model, auxiliary-data assumptions and release evaluation."),
    ("differential_privacy", "differential_privacy", "Differential Privacy", "Owns privacy units, adjacency, mechanisms, composition and budget accounting."),
    ("secure_computation", "secure_computation", "Secure Computation", "Owns participant, adversary, function and leakage contracts for PET execution."),
    ("clean_room", "secure_computation", "Data Clean Room", "Owns admitted inputs, approved queries, output controls and multi-party evidence."),
    ("threat_model", "threat", "Threat Model", "Owns assets, actors, trust boundaries, preconditions and mitigations."),
    ("abuse_prevention", "threat", "Abuse Prevention", "Owns rate, fraud, misuse and exfiltration controls without redefining authorization."),
    ("audit_event", "audit", "Audit Event", "Owns normalized security-relevant observations; not provenance proof."),
    ("provenance_evidence", "evidence", "Provenance and Evidence", "Owns derivation assertions, attestations and verification results; not an audit log."),
    ("tamper_evident_log", "evidence", "Tamper-evident Log", "Owns append, inclusion, consistency and checkpoint proofs."),
    ("supply_chain_attestation", "supply_chain", "Supply-chain Attestation", "Owns subject digests, predicates, builders, signatures and transparency references."),
    ("incident_evidence", "incident", "Incident Evidence", "Owns case-scoped preservation, chain of custody and reconstruction artifacts."),
    ("safety_control", "incident", "Safety Control", "Owns kill, quarantine, containment and recovery interlocks for data-platform harm."),
    ("governance_exception", "policy", "Governance Exception", "Owns scoped, approved, expiring deviations with compensating controls."),
    ("data_access_session", "authorization", "Data Access Session", "Owns time-bounded consumer sessions and continuous re-authorization."),
    ("deletion_execution", "retention", "Deletion Execution", "Owns deletion propagation, tombstones, backup expiry and verification."),
    ("subject_identity_resolution", "rights", "Subject Identity Resolution", "Owns privacy-preserving linkage of requesters to records."),
    ("disclosure_accounting", "audit", "Disclosure Accounting", "Owns who received which governed data under which decision."),
    ("trust_registry", "identity", "Trust Registry", "Owns accepted issuers, verifiers, anchors, status and policy editions."),
]


def context_record(seed: tuple[str, str, str, str]) -> dict:
    short, domain, name, boundary = seed
    ev = evidence(domain)
    return {
        "context_id": f"spt.{short}",
        "edition": EDITION,
        "status": STATUS,
        "name": name,
        "domain": domain,
        "boundary": boundary,
        "aggregate_roots": [f"{short}_definition", f"{short}_edition", f"{short}_receipt"],
        "invariants": ["Every effect binds to an explicit tenant, principal or system authority.", "Unknown semantics or stale evidence produce a typed refusal."],
        "commands": [f"register_{short}", f"evaluate_{short}", f"revoke_{short}"],
        "events": [f"{short}_registered", f"{short}_evaluated", f"{short}_revoked"],
        "refusals": ["authority_missing", "scope_mismatch", "evidence_stale", "semantic_gap"],
        "evidence_source_ids": ev,
        "cross_platform_map": cross_map(domain, ev),
    }


CONTEXTS = [context_record(seed) for seed in CONTEXT_SEEDS]
CONTEXT_DOMAIN = {record[0]: record[1] for record in CONTEXT_SEEDS}


ASSET_SEEDS = [
    ("principal", "identity", "identity_asset", "May cross identity, tenant and federation boundaries."),
    ("authenticator", "identity", "credential_asset", "Private authentication material remains within its authenticator boundary."),
    ("session", "identity", "runtime_asset", "Crosses client, gateway and service boundaries with bounded lifetime."),
    ("credential", "identity", "credential_asset", "Issuer, holder and verifier are distinct trust roles."),
    ("authorization_grant", "authorization", "authority_asset", "Approval or grant crosses into issuance but is not an access token."),
    ("entitlement_tuple", "authorization", "policy_asset", "Relationship store and decision service are separate boundaries."),
    ("policy_bundle", "policy", "policy_asset", "Administration signs policy distributed to decision points."),
    ("attribute_assertion", "policy", "evidence_asset", "Attribute authority, cache and decision point have separate freshness risks."),
    ("access_token", "authorization", "bearer_or_pop_asset", "Issuer, client and resource server boundaries create replay exposure."),
    ("dataset", "privacy", "data_asset", "Moves across source, pipeline, persistence and consumer boundaries."),
    ("field_value", "privacy", "data_asset", "Sensitivity can differ from the enclosing dataset and change under combination."),
    ("security_classification", "privacy", "metadata_asset", "Label propagation crosses schema, lineage and enforcement systems."),
    ("purpose_declaration", "privacy", "governance_asset", "Purpose authority and executing pipeline are distinct boundaries."),
    ("consent_artifact", "consent", "permission_asset", "Capture channel, ledger and enforcement path have different evidence."),
    ("data_use_contract", "consent", "policy_asset", "External obligation must be translated into testable platform terms."),
    ("retention_schedule", "retention", "governance_asset", "Schedule authority and storage deletion mechanisms are distinct."),
    ("residency_constraint", "privacy", "governance_asset", "Control plane, data plane, backup and support access locations differ."),
    ("cryptographic_key", "crypto", "high_value_secret", "Custody boundary differs from data protected by the key."),
    ("secret_version", "secrets", "high_value_secret", "Manager, delivery agent and consuming workload are separate boundaries."),
    ("encrypted_payload", "crypto", "protected_data_asset", "Ciphertext confidentiality depends on key and metadata boundaries."),
    ("tenant_namespace", "tenancy", "isolation_asset", "Logical naming does not itself prove compute or storage isolation."),
    ("compute_enclave", "secure_computation", "execution_boundary", "Host, hardware, guest and remote verifier have distinct trust."),
    ("clean_room_input", "secure_computation", "private_input", "Participant, operator and other participants must be independently modeled."),
    ("approved_aggregate", "secure_computation", "controlled_output", "Output crosses from restricted computation into consumption."),
    ("privacy_budget", "differential_privacy", "scarce_governance_asset", "Budget must compose across analysts, queries, datasets and releases."),
    ("deidentified_release", "deidentification", "risk_bearing_output", "Release boundary changes attacker access and auxiliary information."),
    ("rights_case", "rights", "case_asset", "Identity verification must be separated from record disclosure."),
    ("audit_record", "audit", "observation_asset", "Producer, collector, store and analyst form successive trust boundaries."),
    ("provenance_graph", "evidence", "derivation_asset", "Assertions may be reported by untrusted producers and require validation."),
    ("attestation_evidence", "evidence", "evidence_asset", "Attester, verifier, endorser and relying party are distinct roles."),
    ("transparency_checkpoint", "evidence", "integrity_asset", "Log operator and independent monitors must not be conflated."),
    ("software_artifact", "supply_chain", "executable_asset", "Source, build, registry and deployment boundaries permit substitution."),
    ("sbom", "supply_chain", "inventory_evidence", "Inventory describes components but does not prove the built artifact contains them."),
    ("provenance_attestation", "supply_chain", "supply_chain_evidence", "Signature proves signer control, not truth of predicate."),
    ("incident_bundle", "incident", "case_evidence", "Collection, preservation, transfer and analysis require chain of custody."),
    ("waiver", "policy", "temporary_authority", "Approval authority and enforcement point must agree on scope and expiry."),
    ("lineage_edge", "evidence", "observation_asset", "Observed derivation is not necessarily causal proof."),
    ("compiler_requirement", "policy", "intent_asset", "Requirement is provider-neutral and must not name an implementation as proof."),
    ("capability_offer", "policy", "provider_evidence", "Offer claims require qualification and freshness."),
    ("decision_receipt", "policy", "decision_evidence", "Receipt is scoped to input facts, policy edition and evaluation time."),
]


ASSETS = []
for short, domain, kind, boundary in ASSET_SEEDS:
    ev = evidence(domain)
    ASSETS.append({
        "asset_id": f"asset.spt.{short}", "edition": EDITION, "status": STATUS,
        "name": short.replace("_", " ").title(), "asset_kind": kind, "domain": domain,
        "trust_boundary": boundary, "confidentiality": "explicit_classification_required",
        "integrity": "identity_and_edition_must_be_verifiable", "availability": "budget_and_failure_policy_required",
        "tenant_scope": "explicit", "authority_owner": f"spt.{next(k for k, d, *_ in CONTEXT_SEEDS if d == domain)}",
        "evidence_source_ids": ev, "cross_platform_map": cross_map(domain, ev),
    })


THREAT_SEEDS = [
    ("credential_stuffing", "identity", "authentication", "reuse of compromised secrets", "account takeover"),
    ("phishing_proxy", "identity", "authentication", "attacker mediates an authentication ceremony", "credential or session theft"),
    ("mfa_fatigue", "identity", "authentication", "repeated unsolicited approval prompts", "fraudulent authentication"),
    ("session_fixation", "identity", "authentication", "attacker controls or predicts session identity", "principal impersonation"),
    ("federation_confusion", "identity", "federation_trust", "issuer, audience or subject binding is ambiguous", "cross-domain impersonation"),
    ("token_theft", "authorization", "capability_token", "bearer artifact is disclosed", "unauthorized resource use"),
    ("token_replay", "authorization", "capability_token", "reusable token or proof lacks replay controls", "repeated unauthorized effects"),
    ("confused_deputy", "authorization", "policy_enforcement", "more privileged service acts for an unbound caller", "authority amplification"),
    ("stale_entitlement", "authorization", "entitlement_relationship", "revocation has not propagated", "access after authority ended"),
    ("privilege_creep", "authorization", "entitlement_relationship", "grants accumulate without recertification", "excess authority"),
    ("approval_issuance_confusion", "authorization", "approval_workflow", "approval is treated as an issued credential", "untracked access"),
    ("policy_bypass", "policy", "policy_enforcement", "effect path omits the enforcement point", "unmediated action"),
    ("attribute_poisoning", "policy", "policy_information", "untrusted or stale attributes enter a decision", "incorrect permit"),
    ("pdp_unavailable", "policy", "policy_decision", "decision service cannot answer", "fail-open access or denial"),
    ("pep_fail_open", "policy", "policy_enforcement", "enforcer treats indeterminate as permit", "unauthorized effect"),
    ("authorization_toctou", "policy", "policy_enforcement", "facts change between decision and effect", "decision/effect mismatch"),
    ("idor", "authorization", "policy_enforcement", "resource identifier is accepted without object authorization", "cross-object disclosure"),
    ("tenant_breakout", "tenancy", "isolation_control", "compute, storage or metadata isolation fails", "cross-tenant access"),
    ("tenant_identifier_spoofing", "tenancy", "tenancy_boundary", "caller-controlled tenant context is trusted", "cross-tenant effect"),
    ("shared_cache_bleed", "tenancy", "isolation_control", "cache key omits tenant or policy dimensions", "cross-tenant disclosure"),
    ("noisy_neighbor", "tenancy", "isolation_control", "shared resource has no enforceable quota", "availability loss"),
    ("secret_leak_log", "secrets", "secrets_management", "secret material is serialized into telemetry", "credential compromise"),
    ("secret_lease_overrun", "secrets", "secrets_management", "consumer retains secret beyond lease", "revocation failure"),
    ("key_compromise", "crypto", "key_management", "key custody or material is breached", "confidentiality or authenticity loss"),
    ("key_purpose_confusion", "crypto", "cryptographic_policy", "same key is reused across incompatible purposes", "cross-protocol attack"),
    ("algorithm_downgrade", "crypto", "cryptographic_policy", "peer selects weaker or forbidden suite", "reduced protection"),
    ("nonce_reuse", "crypto", "encryption_protection", "nonce uniqueness requirement is violated", "plaintext or key recovery"),
    ("plaintext_metadata_leak", "crypto", "encryption_protection", "sensitive fields remain outside encryption coverage", "side information disclosure"),
    ("purpose_creep", "privacy", "privacy_purpose", "data is used for an undeclared or incompatible purpose", "privacy harm"),
    ("collection_overreach", "privacy", "minimization_collection", "unneeded fields or population are admitted", "excess exposure"),
    ("classification_purpose_confusion", "privacy", "data_classification", "security label is treated as purpose permission", "impermissible use"),
    ("consent_drift", "consent", "consent_permission", "recorded consent no longer matches subject choice", "use after withdrawal"),
    ("dark_pattern_capture", "consent", "consent_permission", "interface manipulates or obscures choice", "invalid permission evidence"),
    ("residency_bypass", "privacy", "residency_locality", "replica, backup, transit or support path leaves allowed locality", "location constraint breach"),
    ("retention_overrun", "retention", "retention_disposition", "data survives disposition due", "unnecessary exposure"),
    ("deletion_incomplete", "retention", "deletion_execution", "replica, index, feature, backup or derived output survives", "false deletion claim"),
    ("hold_collision", "retention", "retention_disposition", "deletion and preservation orders conflict silently", "spoliation or over-retention"),
    ("rights_subject_misbinding", "rights", "subject_identity_resolution", "requester is linked to the wrong records", "wrong-person disclosure or deletion"),
    ("rights_scope_omission", "rights", "rights_request", "lineage-derived copies are not discovered", "incomplete fulfillment"),
    ("singling_out", "deidentification", "reidentification_risk", "release distinguishes one individual", "identity or behavior exposure"),
    ("linkability", "deidentification", "reidentification_risk", "records across contexts can be linked", "profile reconstruction"),
    ("attribute_disclosure", "deidentification", "deidentification", "equivalence class reveals a sensitive value", "sensitive attribute inference"),
    ("auxiliary_reidentification", "deidentification", "reidentification_risk", "external data joins quasi-identifiers", "identity recovery"),
    ("pseudonym_reversal", "deidentification", "deidentification", "mapping or additional information is reachable", "attribution to person"),
    ("small_cell_disclosure", "deidentification", "deidentification", "rare aggregate identifies a small group", "sensitive inference"),
    ("membership_inference", "differential_privacy", "differential_privacy", "outputs differ materially when one unit participates", "participation disclosure"),
    ("differencing_attack", "differential_privacy", "differential_privacy", "overlapping queries isolate a contribution", "individual value inference"),
    ("budget_bypass", "differential_privacy", "differential_privacy", "queries use separate ledgers or identities", "unbounded privacy loss"),
    ("unit_mismatch", "differential_privacy", "differential_privacy", "adjacency or privacy unit is modeled incorrectly", "invalid guarantee"),
    ("clean_room_collusion", "secure_computation", "clean_room", "participants combine views outside assumed threshold", "private input recovery"),
    ("query_exfiltration", "secure_computation", "clean_room", "approved language permits encoding rows into outputs", "row-level disclosure"),
    ("output_threshold_gaming", "secure_computation", "clean_room", "many related queries evade cell thresholds", "reconstruction"),
    ("enclave_side_channel", "secure_computation", "secure_computation", "hardware leakage is outside nominal isolation", "private input disclosure"),
    ("attestation_spoofing", "evidence", "provenance_evidence", "evidence is replayed or bound to wrong challenge", "false trust decision"),
    ("audit_truncation", "audit", "audit_event", "producer or collector drops events", "missing activity evidence"),
    ("log_injection", "audit", "audit_event", "untrusted content forges record boundaries or fields", "misleading investigation"),
    ("clock_manipulation", "audit", "audit_event", "event time or ordering source is tampered", "false sequence"),
    ("provenance_spoofing", "evidence", "provenance_evidence", "producer reports false derivation", "false lineage claim"),
    ("log_equivocation", "evidence", "tamper_evident_log", "operator presents inconsistent histories", "selective concealment"),
    ("artifact_substitution", "supply_chain", "supply_chain_attestation", "artifact differs from attested subject digest", "unverified code execution"),
    ("dependency_confusion", "supply_chain", "supply_chain_attestation", "resolver chooses attacker-controlled package", "build compromise"),
    ("rollback_attack", "supply_chain", "supply_chain_attestation", "older vulnerable metadata or artifact is accepted", "known-vulnerable execution"),
    ("pipeline_replay", "supply_chain", "supply_chain_attestation", "valid artifact or request is replayed in wrong context", "duplicate or unauthorized processing"),
    ("compromised_builder", "supply_chain", "supply_chain_attestation", "authorized build service emits malicious output", "signed compromise"),
    ("alert_suppression", "incident", "incident_evidence", "detection or notification path is disabled", "delayed containment"),
    ("evidence_contamination", "incident", "incident_evidence", "response actions overwrite or mix case evidence", "unreliable reconstruction"),
    ("containment_overscope", "incident", "safety_control", "kill or quarantine target is too broad", "unnecessary platform outage"),
]


THREATS = []
for short, domain, context, precondition, impact in THREAT_SEEDS:
    ev = evidence(domain)
    THREATS.append({
        "threat_id": f"threat.spt.{short}", "edition": EDITION, "status": STATUS,
        "name": short.replace("_", " ").title(), "threat_kind": "abuse_case_candidate",
        "owner_context": f"spt.{context}", "asset_refs": [f"asset.spt.{ASSET_SEEDS[len(THREATS) % len(ASSET_SEEDS)][0]}"],
        "actor_model": "external, insider, compromised workload, or colluding participant as applicable",
        "precondition": precondition, "abuse_flow": ["obtain precondition", "cross or confuse trust boundary", "exercise unintended effect"],
        "impact": impact, "detection_evidence": ["decision receipt", "audit event", "runtime anomaly"],
        "mitigation_classes": ["prevent", "detect", "contain", "recover"], "residual_risk_required": True,
        "evidence_source_ids": ev, "cross_platform_map": cross_map(domain, ev),
    })


CAPABILITY_SEEDS = [
    ("resolve_principal", "identity", "identity_principal"), ("register_principal", "identity", "identity_principal"),
    ("deprovision_principal", "identity", "identity_principal"), ("enroll_authenticator", "identity", "credential_lifecycle"),
    ("authenticate_principal", "identity", "authentication"), ("step_up_authentication", "identity", "authentication"),
    ("verify_phishing_resistance", "identity", "authentication"), ("issue_credential", "identity", "credential_lifecycle"),
    ("rotate_credential", "identity", "credential_lifecycle"), ("revoke_credential", "identity", "credential_lifecycle"),
    ("issue_workload_identity", "identity", "workload_identity"), ("federate_trust_domain", "identity", "federation_trust"),
    ("validate_issuer_audience", "identity", "federation_trust"), ("publish_trust_registry", "identity", "trust_registry"),
    ("author_policy", "authorization", "authorization_policy"), ("validate_policy_schema", "authorization", "authorization_policy"),
    ("resolve_policy_attributes", "policy", "policy_information"), ("evaluate_policy", "policy", "policy_decision"),
    ("explain_policy_decision", "policy", "policy_decision"), ("enforce_policy_decision", "policy", "policy_enforcement"),
    ("propagate_obligations", "policy", "policy_enforcement"), ("manage_relationship_tuple", "authorization", "entitlement_relationship"),
    ("recertify_entitlement", "authorization", "entitlement_relationship"), ("approve_access_request", "authorization", "approval_workflow"),
    ("issue_attenuated_capability", "authorization", "capability_token"), ("bind_token_to_sender", "authorization", "capability_token"),
    ("continuously_reauthorize_session", "authorization", "data_access_session"),
    ("store_secret_version", "secrets", "secrets_management"), ("lease_secret", "secrets", "secrets_management"),
    ("revoke_secret_lease", "secrets", "secrets_management"), ("generate_key", "crypto", "key_management"),
    ("wrap_data_key", "crypto", "key_management"), ("rotate_key", "crypto", "key_management"),
    ("destroy_key", "crypto", "key_management"), ("declare_crypto_suite", "crypto", "cryptographic_policy"),
    ("migrate_crypto_suite", "crypto", "cryptographic_policy"), ("encrypt_payload", "crypto", "encryption_protection"),
    ("verify_ciphertext_context", "crypto", "encryption_protection"), ("scope_tenant_context", "tenancy", "tenancy_boundary"),
    ("isolate_tenant_compute", "tenancy", "isolation_control"), ("isolate_tenant_storage", "tenancy", "isolation_control"),
    ("isolate_tenant_network", "tenancy", "isolation_control"), ("enforce_tenant_quota", "tenancy", "isolation_control"),
    ("classify_data", "privacy", "data_classification"), ("declare_processing_purpose", "privacy", "privacy_purpose"),
    ("test_purpose_compatibility", "privacy", "privacy_purpose"), ("capture_permission", "consent", "consent_permission"),
    ("withdraw_permission", "consent", "consent_permission"), ("compile_data_use_contract", "consent", "data_use_agreement"),
    ("enforce_data_residency", "privacy", "residency_locality"), ("schedule_disposition", "retention", "retention_disposition"),
    ("apply_legal_hold", "retention", "retention_disposition"), ("propagate_deletion", "retention", "deletion_execution"),
    ("verify_deletion", "retention", "deletion_execution"), ("open_rights_request", "rights", "rights_request"),
    ("resolve_subject_records", "rights", "subject_identity_resolution"), ("fulfill_rights_request", "rights", "rights_request"),
    ("gate_collection", "privacy", "minimization_collection"), ("minimize_projection", "privacy", "minimization_collection"),
    ("pseudonymize_identifier", "deidentification", "deidentification"), ("anonymize_release", "deidentification", "deidentification"),
    ("measure_reidentification_risk", "deidentification", "reidentification_risk"),
    ("declare_privacy_unit", "differential_privacy", "differential_privacy"), ("allocate_privacy_budget", "differential_privacy", "differential_privacy"),
    ("compose_privacy_loss", "differential_privacy", "differential_privacy"), ("execute_secure_aggregation", "secure_computation", "secure_computation"),
    ("execute_private_set_intersection", "secure_computation", "secure_computation"), ("attest_confidential_workload", "secure_computation", "secure_computation"),
    ("admit_clean_room_query", "secure_computation", "clean_room"), ("control_clean_room_output", "secure_computation", "clean_room"),
    ("model_threat", "threat", "threat_model"), ("rate_limit_abuse", "threat", "abuse_prevention"),
    ("detect_exfiltration", "threat", "abuse_prevention"), ("emit_audit_event", "audit", "audit_event"),
    ("account_for_disclosure", "audit", "disclosure_accounting"), ("record_provenance", "evidence", "provenance_evidence"),
    ("verify_attestation", "evidence", "provenance_evidence"), ("append_transparency_event", "evidence", "tamper_evident_log"),
    ("verify_inclusion_consistency", "evidence", "tamper_evident_log"), ("produce_build_provenance", "supply_chain", "supply_chain_attestation"),
    ("verify_artifact_supply_chain", "supply_chain", "supply_chain_attestation"), ("preserve_incident_evidence", "incident", "incident_evidence"),
    ("contain_data_platform_incident", "incident", "safety_control"), ("authorize_expiring_exception", "policy", "governance_exception"),
]


CAPABILITIES = []
for short, domain, context in CAPABILITY_SEEDS:
    ev = evidence(domain)
    CAPABILITIES.append({
        "capability_id": f"cap.spt.{short}", "edition": EDITION, "status": STATUS,
        "name": short.replace("_", " ").title(), "owner_context": f"spt.{context}", "domain": domain,
        "intent": f"Provider-neutrally {short.replace('_', ' ')} with explicit authority and evidence.",
        "inputs": ["tenant_scope", "authority_ref", "policy_edition", "typed_subject"],
        "outputs": ["typed_result", "decision_or_effect_receipt"],
        "preconditions": ["authority is current", "input identity and scope are explicit"],
        "postconditions": ["effect is scoped", "evidence links input, policy and outcome"],
        "non_capabilities": ["vendor feature label", "implicit legal determination", "unverified control claim"],
        "evidence_source_ids": ev, "cross_platform_map": cross_map(domain, ev),
    })


OPERATION_SEEDS = [
    "resolve_principal", "register_principal", "suspend_principal", "deprovision_principal", "enroll_authenticator",
    "challenge_authenticator", "verify_authentication_assertion", "issue_session", "refresh_session", "terminate_session",
    "issue_credential", "rotate_credential", "revoke_credential", "publish_credential_status", "verify_federation_assertion",
    "register_trust_anchor", "issue_workload_svid", "rotate_workload_svid", "compile_authorization_policy", "validate_authorization_policy",
    "fetch_policy_attributes", "evaluate_authorization_request", "return_policy_obligations", "enforce_authorization_decision",
    "write_relationship_tuple", "delete_relationship_tuple", "check_relationship", "request_approval", "record_approval",
    "issue_access_token", "attenuate_capability", "revoke_access_token", "open_data_access_session", "reauthorize_data_access_session",
    "put_secret_version", "lease_secret_version", "renew_secret_lease", "revoke_secret_lease", "generate_cryptographic_key",
    "import_cryptographic_key", "wrap_data_key", "unwrap_data_key", "rotate_cryptographic_key", "destroy_cryptographic_key",
    "encrypt_value", "decrypt_value", "sign_artifact", "verify_signature", "negotiate_crypto_suite",
    "bind_tenant_context", "allocate_tenant_partition", "check_tenant_isolation", "apply_tenant_quota", "assign_security_classification",
    "propagate_security_classification", "register_processing_purpose", "check_purpose_compatibility", "record_consent", "withdraw_consent",
    "compile_use_policy", "check_residency_plan", "schedule_retention", "place_legal_hold", "release_legal_hold",
    "issue_deletion_tombstone", "delete_primary_copy", "expire_backup_copy", "verify_deletion_receipt", "verify_rights_requester",
    "discover_subject_records", "export_subject_records", "rectify_subject_record", "gate_collection_field", "project_minimum_fields",
    "tokenize_identifier", "generalize_quasi_identifier", "suppress_small_cell", "estimate_reidentification_risk", "approve_deidentified_release",
    "reserve_privacy_budget", "commit_privacy_spend", "refund_unspent_budget", "add_dp_noise", "verify_dp_configuration",
    "run_private_set_intersection", "run_secure_aggregate", "verify_enclave_attestation", "admit_clean_room_input", "admit_clean_room_query",
    "release_clean_room_output", "register_threat_scenario", "evaluate_abuse_signal", "throttle_actor", "quarantine_output",
    "emit_security_audit_event", "append_disclosure_record", "record_lineage_assertion", "verify_attestation_evidence",
    "append_transparency_log", "verify_log_inclusion", "verify_log_consistency", "generate_sbom", "produce_provenance_attestation",
    "verify_artifact_digest", "verify_supply_chain_policy", "open_incident_case", "preserve_evidence_item", "record_chain_of_custody",
    "contain_tenant", "revoke_compromised_authority", "authorize_governance_exception", "expire_governance_exception",
]


def operation_domain(name: str) -> str:
    exact_overrides = {
        "compile_use_policy": "consent",
        "generate_sbom": "supply_chain",
        "produce_provenance_attestation": "supply_chain",
        "verify_artifact_digest": "supply_chain",
        "verify_supply_chain_policy": "supply_chain",
        "authorize_governance_exception": "policy",
        "expire_governance_exception": "policy",
        "revoke_compromised_authority": "incident",
    }
    if name in exact_overrides:
        return exact_overrides[name]
    for tokens, domain in [
        (("principal", "authenticator", "authentication", "session", "credential", "federation", "trust_anchor", "svid"), "identity"),
        (("authorization", "relationship", "approval", "access_token", "capability", "data_access"), "authorization"),
        (("policy", "governance_exception"), "policy"), (("secret",), "secrets"),
        (("key", "encrypt", "decrypt", "signature", "crypto"), "crypto"), (("tenant", "isolation", "quota"), "tenancy"),
        (("classification", "purpose", "residency", "collection", "minimum"), "privacy"), (("consent", "use_policy"), "consent"),
        (("retention", "hold", "deletion", "primary_copy", "backup_copy"), "retention"), (("rights", "subject_records", "subject_record"), "rights"),
        (("tokenize", "generalize", "small_cell", "reidentification", "deidentified"), "deidentification"),
        (("privacy_budget", "privacy_spend", "dp_"), "differential_privacy"), (("private_set", "secure_aggregate", "enclave", "clean_room"), "secure_computation"),
        (("threat", "abuse", "throttle", "quarantine"), "threat"), (("audit", "disclosure"), "audit"),
        (("lineage", "attestation", "transparency", "log_inclusion", "log_consistency"), "evidence"),
        (("sbom", "provenance_attestation", "artifact", "supply_chain"), "supply_chain"),
        (("incident", "evidence_item", "chain_of_custody", "contain", "compromised_authority"), "incident"),
    ]:
        if any(token in name for token in tokens):
            return domain
    return "policy"


def operation_context(name: str, domain: str) -> str:
    """Select a semantic owner without making vendor/runtime placement the owner."""
    rules = {
        "identity": [
            (("svid",), "workload_identity"), (("federation", "trust_anchor"), "federation_trust"),
            (("authenticator",), "credential_lifecycle"), (("credential",), "credential_lifecycle"),
            (("authentication", "session"), "authentication"), (("principal",), "identity_principal"),
        ],
        "authorization": [
            (("relationship",), "entitlement_relationship"), (("approval",), "approval_workflow"),
            (("token", "capability"), "capability_token"), (("data_access",), "data_access_session"),
            (("authorization_policy",), "authorization_policy"),
        ],
        "policy": [
            (("attribute",), "policy_information"), (("enforce",), "policy_enforcement"),
            (("decision", "obligation", "evaluate_authorization"), "policy_decision"),
            (("exception",), "governance_exception"), (("policy",), "authorization_policy"),
        ],
        "secrets": [(("secret",), "secrets_management")],
        "crypto": [
            (("encrypt", "decrypt"), "encryption_protection"), (("suite",), "cryptographic_policy"),
            (("key",), "key_management"), (("sign", "signature"), "cryptographic_policy"),
        ],
        "tenancy": [(("bind_tenant",), "tenancy_boundary"), (("tenant", "isolation", "quota"), "isolation_control")],
        "privacy": [
            (("classification",), "data_classification"), (("purpose",), "privacy_purpose"),
            (("residency",), "residency_locality"), (("collection", "minimum"), "minimization_collection"),
        ],
        "consent": [(("consent",), "consent_permission"), (("use_policy",), "data_use_agreement")],
        "retention": [
            (("deletion", "primary_copy", "backup_copy"), "deletion_execution"),
            (("retention", "hold"), "retention_disposition"),
        ],
        "rights": [(("verify_rights", "subject_records", "subject_record"), "subject_identity_resolution"), (("rights",), "rights_request")],
        "deidentification": [(("risk",), "reidentification_risk"), (("tokenize", "generalize", "suppress", "release"), "deidentification")],
        "differential_privacy": [(("privacy", "dp_"), "differential_privacy")],
        "secure_computation": [(("clean_room",), "clean_room"), (("private_set", "secure_aggregate", "enclave"), "secure_computation")],
        "threat": [(("threat",), "threat_model"), (("abuse", "throttle", "quarantine"), "abuse_prevention")],
        "audit": [(("disclosure",), "disclosure_accounting"), (("audit",), "audit_event")],
        "evidence": [(("transparency", "log_inclusion", "log_consistency"), "tamper_evident_log"), (("lineage", "attestation"), "provenance_evidence")],
        "supply_chain": [(("sbom", "provenance", "artifact", "supply_chain"), "supply_chain_attestation")],
        "incident": [(("contain", "revoke_compromised"), "safety_control"), (("incident", "evidence_item", "chain_of_custody"), "incident_evidence")],
    }
    for tokens, context in rules[domain]:
        if any(token in name for token in tokens):
            return context
    return next(short for short, candidate_domain, *_ in CONTEXT_SEEDS if candidate_domain == domain)


OPERATIONS = []
for name in OPERATION_SEEDS:
    domain = operation_domain(name)
    ev = evidence(domain)
    OPERATIONS.append({
        "operation_id": f"op.spt.{name}", "edition": EDITION, "status": STATUS,
        "name": name.replace("_", " ").title(), "owner_context": f"spt.{operation_context(name, domain)}",
        "domain": domain,
        "signature": {"input": f"{name}_request", "output": f"result<{name}_receipt,{name}_refusal>"},
        "effects": ["none"] if name.startswith(("verify_", "check_", "estimate_", "evaluate_", "resolve_", "discover_")) else [f"writes:{domain}_state", "emits:audit_receipt"],
        "idempotency": "explicit_idempotency_key_or_naturally_idempotent_proof_required",
        "preconditions": ["typed authority", "explicit tenant and purpose scope", "policy edition available"],
        "postconditions": ["outcome is attributable", "refusal is typed", "effect evidence is durable when effectful"],
        "failures": ["unauthorized", "stale_evidence", "scope_mismatch", "unsupported_capability", "provider_failure"],
        "information_loss": "must_be_declared_for_release_or_deletion_operations",
        "evidence_source_ids": ev, "cross_platform_map": cross_map(domain, ev),
    })


DECISION_SEEDS = [
    ("principal_namespace", "identity", "identity_principal", "Which authority owns each principal namespace?", ["local", "federated", "composite"]),
    ("identity_assurance", "identity", "authentication", "Which identity and authentication assurance are required?", ["risk_profile", "assurance_level", "step_up_rule"]),
    ("authenticator_class", "identity", "authentication", "Which authenticator classes are acceptable?", ["phishing_resistant", "multi_factor", "hardware_bound"]),
    ("session_lifetime", "identity", "authentication", "How long may a session remain valid without reauthentication?", ["absolute", "idle", "risk_adaptive"]),
    ("federation_anchor", "identity", "federation_trust", "Which issuers, audiences and anchors are trusted?", ["allowlist", "registry", "contract"]),
    ("workload_identity_source", "identity", "workload_identity", "Which runtime evidence may create a workload principal?", ["node_attestation", "orchestrator", "external_issuer"]),
    ("policy_model", "authorization", "authorization_policy", "Which authorization model owns this resource?", ["rbac", "abac", "rebac", "capability", "composed"]),
    ("decision_combining", "policy", "policy_decision", "How are multiple policy results combined?", ["deny_overrides", "permit_overrides", "first_applicable", "only_one_applicable"]),
    ("indeterminate_action", "policy", "policy_enforcement", "What happens when policy evaluation is indeterminate?", ["deny", "quarantine", "human_review"]),
    ("attribute_freshness", "policy", "policy_information", "How fresh must each decision attribute be?", ["request_bound", "ttl", "event_invalidated"]),
    ("decision_effect_binding", "policy", "policy_enforcement", "How is a decision bound to the eventual effect?", ["transaction", "signed_receipt", "short_lived_handle"]),
    ("approval_authority", "authorization", "approval_workflow", "Who may approve which access scope?", ["owner", "delegate", "policy_automation"]),
    ("approval_to_issuance", "authorization", "approval_workflow", "Which issuance step consumes an approval?", ["single_use", "bounded_reuse", "manual"]),
    ("token_form", "authorization", "capability_token", "Which token semantics are required?", ["opaque", "self_contained", "sender_constrained", "attenuable"]),
    ("revocation_latency", "authorization", "capability_token", "What maximum revocation latency is tolerable?", ["online_check", "short_lived", "push_revocation"]),
    ("secret_delivery", "secrets", "secrets_management", "How is a secret delivered without uncontrolled persistence?", ["agent", "mounted_memory", "api_lease"]),
    ("secret_rotation_overlap", "secrets", "secrets_management", "May old and new secret versions overlap?", ["none", "bounded_dual", "consumer_acknowledged"]),
    ("key_purpose", "crypto", "key_management", "What single purpose and protection level owns each key?", ["encryption", "signing", "mac", "wrapping", "derivation"]),
    ("key_custody", "crypto", "key_management", "Where may plaintext key material exist?", ["hsm_only", "trusted_process", "split_custody"]),
    ("crypto_agility", "crypto", "cryptographic_policy", "How will suite deprecation and migration occur?", ["versioned_envelope", "dual_write", "read_old_write_new"]),
    ("encryption_granularity", "crypto", "encryption_protection", "At what layer is confidentiality applied?", ["transport", "volume", "object", "field", "application"]),
    ("tenant_isolation_class", "tenancy", "tenancy_boundary", "What threat-based isolation class applies?", ["logical", "namespace", "process", "node", "cluster", "account"]),
    ("tenant_key_scope", "tenancy", "isolation_control", "Are encryption keys shared, tenant-specific or object-specific?", ["shared", "tenant", "object"]),
    ("tenant_quota", "tenancy", "isolation_control", "Which resources require hard tenant quotas?", ["compute", "memory", "io", "requests", "all"]),
    ("classification_scheme", "privacy", "data_classification", "Which authority and vocabulary own security classification?", ["organization", "contract", "regulated_profile"]),
    ("purpose_vocabulary", "privacy", "privacy_purpose", "Which controlled purpose vocabulary and hierarchy apply?", ["registry", "contract_profile", "local"]),
    ("purpose_compatibility", "privacy", "privacy_purpose", "Who decides whether a new purpose is compatible?", ["rule", "data_steward", "privacy_authority"]),
    ("permission_basis", "consent", "consent_permission", "Is consent or another declared authority being represented?", ["consent", "contract_permission", "legal_obligation_marker", "other"]),
    ("withdrawal_effect", "consent", "consent_permission", "Which future processing stops after withdrawal?", ["immediate", "bounded_propagation", "case_review"]),
    ("use_contract_lowering", "consent", "data_use_agreement", "Which clauses can be compiled into platform checks?", ["purpose", "recipient", "operation", "location", "time", "output"]),
    ("residency_scope", "privacy", "residency_locality", "Which activities are location-constrained?", ["storage", "processing", "transit", "backup", "support"]),
    ("retention_trigger", "retention", "retention_disposition", "Which event starts the retention clock?", ["collection", "last_use", "contract_end", "subject_event", "case_close"]),
    ("retention_conflict", "retention", "retention_disposition", "How are deletion schedules and holds resolved?", ["preserve_with_reason", "delete", "escalate"]),
    ("deletion_semantics", "retention", "deletion_execution", "What counts as deletion for each storage class?", ["logical_tombstone", "crypto_erasure", "physical_erase", "expiry"]),
    ("backup_disposition", "retention", "deletion_execution", "When and how do deleted records leave backups?", ["natural_expiry", "selective_rewrite", "crypto_erasure"]),
    ("rights_identity_proof", "rights", "subject_identity_resolution", "What proof is proportionate for a rights request?", ["existing_session", "document_proof", "knowledge", "manual"]),
    ("rights_lineage_scope", "rights", "rights_request", "Which derived assets are within fulfillment scope?", ["direct", "derived", "recipient", "archive"]),
    ("collection_necessity", "privacy", "minimization_collection", "Who proves each collected field is necessary?", ["purpose_owner", "schema_owner", "review_board"]),
    ("deidentification_claim", "deidentification", "deidentification", "Is the output pseudonymized, de-identified, or claimed anonymous?", ["pseudonymized", "deidentified", "anonymous_claim"]),
    ("attacker_auxiliary_data", "deidentification", "reidentification_risk", "Which auxiliary information and access are assumed?", ["public", "partner", "insider", "arbitrary"]),
    ("release_risk_threshold", "deidentification", "reidentification_risk", "Which authority accepts residual re-identification risk?", ["data_owner", "privacy_officer", "review_board"]),
    ("dp_privacy_unit", "differential_privacy", "differential_privacy", "What adjacent datasets differ by one protected unit?", ["person", "device", "household", "event", "custom"]),
    ("dp_budget_scope", "differential_privacy", "differential_privacy", "Across which releases must privacy loss compose?", ["dataset", "person", "purpose", "consumer", "global"]),
    ("secure_computation_adversary", "secure_computation", "secure_computation", "Which corruption and collusion threshold is assumed?", ["semi_honest", "malicious", "threshold", "tee_hostile"]),
    ("clean_room_query_language", "secure_computation", "clean_room", "Which bounded query language is admitted?", ["templates", "restricted_sql", "approved_program"]),
    ("clean_room_output_control", "secure_computation", "clean_room", "Which output protections compose?", ["threshold", "noise", "review", "rate_limit"]),
    ("threat_acceptance", "threat", "threat_model", "Who accepts residual risk for which asset and period?", ["owner", "security_authority", "joint"]),
    ("audit_minimum", "audit", "audit_event", "Which events and fields are mandatory for accountability?", ["access", "decision", "change", "disclosure", "administration"]),
    ("audit_privacy", "audit", "audit_event", "How are audit usefulness and sensitive-data minimization balanced?", ["pseudonymize", "tokenize", "segregate", "short_retention"]),
    ("evidence_trust", "evidence", "provenance_evidence", "Which producer claims need signatures, attestation or corroboration?", ["signature", "attestation", "independent_observer", "multiple"]),
    ("transparency_monitoring", "evidence", "tamper_evident_log", "Who independently checks inclusion and consistency?", ["consumer", "monitor", "witness"]),
    ("supply_chain_level", "supply_chain", "supply_chain_attestation", "Which provenance and build controls are required?", ["provenance", "hosted_build", "hardened_build"]),
    ("artifact_promotion", "supply_chain", "supply_chain_attestation", "Which verified evidence gates artifact promotion?", ["signature", "provenance", "sbom", "vulnerability", "policy"]),
    ("incident_evidence_scope", "incident", "incident_evidence", "Which volatile and durable evidence must be preserved?", ["logs", "traces", "state", "artifact", "memory"]),
    ("containment_scope", "incident", "safety_control", "What is the smallest safe containment boundary?", ["session", "principal", "tenant", "pipeline", "cluster"]),
    ("exception_expiry", "policy", "governance_exception", "When must a governance exception stop applying?", ["absolute_time", "condition", "deployment_edition"]),
]


DECISIONS = []
for short, domain, context, question, choices in DECISION_SEEDS:
    ev = evidence(domain)
    DECISIONS.append({
        "decision_id": f"decision.spt.{short}", "edition": EDITION, "status": STATUS,
        "owner_context": f"spt.{context}", "domain": domain, "question": question,
        "allowed_value_kinds": choices, "binding_phase": "intent_or_compile_before_effect",
        "default_law": "No hidden default; unresolved values become typed compiler gaps.",
        "authority_required": "named domain owner with tenant and data scope", "evidence_required": ["decision trace", "policy edition", "authority receipt"],
        "evidence_source_ids": ev, "cross_platform_map": cross_map(domain, ev),
    })


INVARIANT_SEEDS = [
    ("authentication_not_authorization", "identity", "invariant", "Successful authentication never implies permission for a data action."),
    ("authorization_requires_resource_action", "authorization", "invariant", "Authorization binds principal, action, resource, context and policy edition."),
    ("approval_not_issuance", "authorization", "invariant", "Approval is an input to issuance and cannot substitute for an issued scoped authority."),
    ("issuance_not_enforcement", "authorization", "invariant", "Issued authority is checked again at the effect boundary."),
    ("pdp_not_pep", "policy", "invariant", "A policy decision cannot prove that every effect path enforced it."),
    ("indeterminate_not_permit", "policy", "refusal", "Indeterminate policy outcomes cannot be coerced to permit."),
    ("stale_attribute_refused", "policy", "refusal", "A decision refuses attributes older than the declared freshness bound."),
    ("obligation_must_propagate", "policy", "invariant", "Permit obligations remain bound to the effect and its receipt."),
    ("secret_never_plaintext_log", "secrets", "refusal", "Secret material is refused at telemetry and error serialization boundaries."),
    ("secret_handle_not_value", "secrets", "invariant", "A secret handle is not interchangeable with the secret value."),
    ("key_has_single_declared_purpose", "crypto", "invariant", "Every cryptographic key has an explicit permitted purpose set."),
    ("encryption_not_access_control", "crypto", "invariant", "Possession of decrypt capability does not establish authorization to use plaintext."),
    ("unknown_algorithm_refused", "crypto", "refusal", "Unknown, forbidden or context-incompatible cryptographic suites are refused."),
    ("nonce_uniqueness_proven", "crypto", "invariant", "Modes requiring unique nonces bind a uniqueness strategy and scope."),
    ("compromised_key_quarantined", "crypto", "refusal", "New effects under a compromised key are refused pending explicit recovery policy."),
    ("tenant_context_not_caller_claim", "tenancy", "invariant", "Tenant context derives from authenticated authority, not an untrusted field alone."),
    ("tenant_partition_key_complete", "tenancy", "invariant", "Every shared index and cache key contains the complete tenant isolation dimension."),
    ("cross_tenant_join_refused", "tenancy", "refusal", "Cross-tenant joins require explicit multi-tenant authority and output policy."),
    ("quota_before_admission", "tenancy", "invariant", "Hard tenant budgets are checked before expensive work is admitted."),
    ("classification_not_purpose", "privacy", "invariant", "Security classification does not establish a privacy purpose or permission."),
    ("purpose_bound_to_operation", "privacy", "invariant", "Purpose is bound to the concrete operation, dataset, recipient and time."),
    ("unknown_purpose_refused", "privacy", "refusal", "Unknown or non-comparable purposes are not treated as compatible."),
    ("permission_withdrawal_monotone", "consent", "invariant", "Withdrawal prevents new dependent use after the declared propagation bound."),
    ("consent_not_universal_basis", "consent", "invariant", "Consent artifacts are not used to represent every possible legal authority."),
    ("legal_text_not_directly_executable", "consent", "invariant", "A legal obligation becomes enforceable only through an approved bounded platform contract."),
    ("unlowered_clause_gap", "consent", "refusal", "A clause with no faithful platform lowering remains a gap, never a guessed check."),
    ("residency_covers_replicas", "privacy", "invariant", "Residency checks include primary, replica, backup, transit and operator access paths."),
    ("unknown_location_refused", "privacy", "refusal", "A plan with an unresolved processing or persistence location is not admitted."),
    ("retention_trigger_explicit", "retention", "invariant", "Every schedule names a trigger event, duration, holds and disposition action."),
    ("hold_collision_escalated", "retention", "refusal", "Conflicting deletion and preservation instructions require typed escalation."),
    ("deletion_receipt_scoped", "retention", "invariant", "Deletion evidence names each storage class and excludes no hidden derivative."),
    ("backup_expiry_not_immediate_deletion", "retention", "invariant", "Backup expiry is recorded separately from primary deletion."),
    ("rights_identity_minimized", "rights", "invariant", "Rights-request verification collects no more proof than proportionate to risk."),
    ("rights_disclosure_requires_binding", "rights", "refusal", "Record export is refused when requester-to-record binding is ambiguous."),
    ("lineage_drives_rights_discovery", "rights", "invariant", "Fulfillment scope records lineage search completeness and gaps."),
    ("collection_requires_necessity", "privacy", "refusal", "A field without a declared necessary purpose is refused at collection."),
    ("pseudonymization_not_anonymization", "deidentification", "invariant", "Pseudonymized data is never labeled anonymous while additional information enables attribution."),
    ("anonymous_claim_requires_attacker_model", "deidentification", "refusal", "An anonymity claim without a release context and attacker model is refused."),
    ("deidentification_risk_reassessed", "deidentification", "invariant", "Material changes in data, recipient or auxiliary information trigger reassessment."),
    ("small_groups_not_released", "deidentification", "refusal", "Outputs below approved disclosure thresholds are suppressed or protected."),
    ("dp_unit_explicit", "differential_privacy", "invariant", "Every differential privacy guarantee names adjacency and privacy unit."),
    ("dp_budget_atomic", "differential_privacy", "invariant", "Budget reservation and spend commit are atomic with output release."),
    ("dp_budget_exhaustion_refused", "differential_privacy", "refusal", "Output release is refused when composed privacy loss exceeds budget."),
    ("dp_claim_configuration_bound", "differential_privacy", "invariant", "A privacy claim binds mechanism, parameters, clipping, contribution bounds and accountant."),
    ("secure_function_allowlisted", "secure_computation", "refusal", "Secure computation runs only an approved function under declared leakage."),
    ("attestation_not_authorization", "secure_computation", "invariant", "Valid enclave attestation does not by itself authorize data release."),
    ("clean_room_output_composed", "secure_computation", "invariant", "Output controls compose across queries, users and time."),
    ("collusion_assumption_explicit", "secure_computation", "invariant", "Participant corruption and collusion thresholds are declared."),
    ("threat_has_asset_boundary", "threat", "invariant", "Every threat references an asset and trust boundary."),
    ("residual_risk_owned", "threat", "refusal", "Deployment is refused when material residual risk lacks a named accepting authority."),
    ("audit_event_not_provenance", "audit", "invariant", "An audit observation is not treated as causal provenance or integrity proof."),
    ("audit_actor_not_free_text", "audit", "invariant", "Actor identity is a typed reference with authentication context."),
    ("audit_failure_visible", "audit", "invariant", "Dropped, delayed or rejected audit events produce operational evidence."),
    ("evidence_subject_digest_bound", "evidence", "invariant", "Attestation verification binds the exact subject digest and predicate type."),
    ("signature_not_truth", "evidence", "invariant", "A valid signature proves key use and integrity, not truth of every signed claim."),
    ("log_consistency_checked", "evidence", "refusal", "A transparency checkpoint is not trusted without applicable consistency evidence."),
    ("provenance_not_audit_log", "evidence", "invariant", "Provenance assertions and security audit events remain separate linked records."),
    ("artifact_digest_before_execution", "supply_chain", "refusal", "Artifact identity mismatch is refused before execution."),
    ("attestation_freshness", "supply_chain", "invariant", "Supply-chain evidence declares issuance, expiry and revocation status."),
    ("rollback_protected", "supply_chain", "refusal", "Expired or lower-version update metadata is refused."),
    ("replay_has_new_authority", "supply_chain", "invariant", "A replay or backfill is a new authorized run, not silent history mutation."),
    ("incident_chain_of_custody", "incident", "invariant", "Each evidence transfer records actor, time, digest and purpose."),
    ("containment_scope_checked", "incident", "refusal", "Containment is refused or escalated when target scope is ambiguous."),
    ("exception_expires", "policy", "invariant", "Every exception has scope, owner, compensating control and finite expiry."),
]


INVARIANTS = []
for short, domain, kind, statement in INVARIANT_SEEDS:
    ev = evidence(domain)
    INVARIANTS.append({
        "rule_id": f"rule.spt.{short}", "edition": EDITION, "status": STATUS,
        "rule_kind": kind, "domain": domain, "statement": statement,
        "compiler_action": "prove_or_refuse" if kind == "invariant" else "typed_refusal",
        "failure_code": f"spt_{short}", "evidence_source_ids": ev, "cross_platform_map": cross_map(domain, ev),
    })


# Requirements are deliberately provider-neutral.  Offers are claims to qualify, never assumed facts.
REQUIREMENTS = []
for index, capability in enumerate(CAPABILITIES[:48]):
    REQUIREMENTS.append({
        "requirement_id": f"req.spt.{capability['capability_id'].split('.')[-1]}", "edition": EDITION, "status": STATUS,
        "capability_ref": capability["capability_id"], "owner_context": capability["owner_context"],
        "requirement_kind": "compiler_capability_requirement", "must_support": capability["intent"],
        "constraints": ["tenant scoped", "policy edition aware", "typed refusal", "receipt emitting"],
        "qualification_evidence": ["conformance test", "configuration snapshot", "fresh capability statement"],
        "unknown_offer_action": "compile_gap", "evidence_source_ids": capability["evidence_source_ids"],
        "cross_platform_map": capability["cross_platform_map"],
    })


OFFER_CLASSES = [
    ("identity_provider", "identity"), ("authenticator_verifier", "identity"), ("workload_identity_issuer", "identity"),
    ("policy_decision_service", "policy"), ("policy_enforcement_adapter", "policy"), ("relationship_store", "authorization"),
    ("secret_manager", "secrets"), ("key_management_service", "crypto"), ("cryptographic_module", "crypto"),
    ("tenant_isolated_runtime", "tenancy"), ("residency_aware_storage", "privacy"), ("retention_executor", "retention"),
    ("rights_discovery_service", "rights"), ("deidentification_engine", "deidentification"), ("privacy_accountant", "differential_privacy"),
    ("secure_aggregation_runtime", "secure_computation"), ("clean_room_runtime", "secure_computation"),
    ("audit_store", "audit"), ("attestation_verifier", "evidence"), ("transparency_log", "evidence"),
    ("supply_chain_verifier", "supply_chain"), ("incident_evidence_vault", "incident"),
]


OFFERS = []
for short, domain in OFFER_CLASSES:
    ev = evidence(domain)
    OFFERS.append({
        "offer_id": f"offer-template.spt.{short}", "edition": EDITION, "status": STATUS,
        "offer_kind": short, "provider_binding": None,
        "declared_capabilities": [c["capability_id"] for c in CAPABILITIES if c["domain"] == domain][:4],
        "limits": ["throughput", "latency", "object_count", "retention", "region", "failure_mode"],
        "assurance": ["implementation identity", "version", "configuration", "conformance receipts"],
        "qualification_state": "unqualified_template", "evidence_source_ids": ev, "cross_platform_map": cross_map(domain, ev),
    })


MAPPINGS = []
for index, context in enumerate(CONTEXTS):
    domain_caps = [c for c in CAPABILITIES if c["domain"] == context["domain"]]
    domain_ops = [o for o in OPERATIONS if o["domain"] == context["domain"]]
    domain_reqs = [r for r in REQUIREMENTS if r["owner_context"] == context["context_id"]]
    MAPPINGS.append({
        "mapping_id": f"mapping.spt.{context['context_id'].split('.')[-1]}", "edition": EDITION, "status": STATUS,
        "context_ref": context["context_id"], "intent_inputs": ["data_action_intent", "principal_and_tenant", "governance_profile"],
        "required_capabilities": [c["capability_id"] for c in domain_caps[:3]],
        "candidate_operations": [o["operation_id"] for o in domain_ops[:4]],
        "requirement_refs": [r["requirement_id"] for r in domain_reqs[:3]],
        "offer_match_law": "All constraints and assurance evidence must be proven; name or category similarity is insufficient.",
        "gap_output": "typed_requirement_gap", "cross_platform_map": context["cross_platform_map"],
        "evidence_source_ids": context["evidence_source_ids"],
    })


LIBRARY_SEEDS = [
    ("principal_types", "identity", "pure", "Principal, credential and assurance value types only."),
    ("authentication_protocols", "identity", "effectful", "Protocol verification adapters; no authorization decisions."),
    ("authorization_ast", "authorization", "pure", "Policy expression and request types; no identity proofing."),
    ("policy_evaluator", "policy", "pure", "Deterministic decision over explicit attributes and policy edition."),
    ("policy_enforcer", "policy", "effectful", "Effect interception and obligation execution."),
    ("relationship_graph", "authorization", "effectful", "Relationship tuple persistence and consistency."),
    ("secret_handles", "secrets", "pure", "Opaque handles and lease metadata; never secret values in diagnostics."),
    ("secret_provider", "secrets", "effectful", "Secret version and lease lifecycle provider boundary."),
    ("crypto_types", "crypto", "pure", "Algorithm, key purpose and envelope metadata types."),
    ("crypto_provider", "crypto", "effectful", "Qualified cryptographic operations and key custody."),
    ("tenant_scope", "tenancy", "pure", "Non-forgeable tenant references and partition key derivation."),
    ("isolation_provider", "tenancy", "effectful", "Compute, storage and network isolation enforcement."),
    ("privacy_vocabulary", "privacy", "pure", "Purpose, category, processing and location value types."),
    ("use_policy_compiler", "consent", "pure", "Bounded translation from governed clauses to platform requirements."),
    ("retention_calculus", "retention", "pure", "Trigger, duration, hold precedence and due-date calculation."),
    ("deletion_provider", "retention", "effectful", "Storage-class deletion and verification adapters."),
    ("rights_case", "rights", "effectful", "Case state, discovery and disclosure orchestration."),
    ("deidentification_metrics", "deidentification", "pure", "Release-risk metrics under explicit attacker assumptions."),
    ("privacy_accountant", "differential_privacy", "effectful", "Atomic privacy budget reservation and spend."),
    ("secure_computation_protocol", "secure_computation", "effectful", "Qualified multi-party or trusted-execution provider."),
    ("audit_event_types", "audit", "pure", "Normalized typed event schema with redaction policy."),
    ("audit_sink", "audit", "effectful", "Durable, failure-visible event collection."),
    ("evidence_envelopes", "evidence", "pure", "Digest, signature, statement and predicate structures."),
    ("attestation_verifier", "evidence", "effectful", "Nonce-bound verification and appraisal boundary."),
    ("supply_chain_policy", "supply_chain", "pure", "Artifact promotion predicates over verified evidence."),
    ("incident_evidence_store", "incident", "effectful", "Case-scoped preservation and chain-of-custody boundary."),
]


LIBRARIES = []
for short, domain, effect, boundary in LIBRARY_SEEDS:
    ev = evidence(domain)
    LIBRARIES.append({
        "library_id": f"library.spt.{short}", "edition": EDITION, "status": STATUS,
        "domain": domain, "effect_class": effect, "owns": boundary,
        "must_not_own": ["business-specific legal determination", "provider selection", "unrelated orchestration"],
        "public_types": cross_map(domain, ev)["types_shapes"], "required_receipts": ["decision receipt", "effect receipt"] if effect == "effectful" else [],
        "evidence_source_ids": ev, "cross_platform_map": cross_map(domain, ev),
    })


EVIDENCE_SEEDS = [
    ("authentication_receipt", "identity", "asserts a scoped authentication ceremony result"),
    ("credential_status_snapshot", "identity", "records issuer status checked at verification time"),
    ("federation_metadata_snapshot", "identity", "binds issuer, keys, endpoints and expiry"),
    ("authorization_decision_receipt", "policy", "binds request facts, policy edition, result and obligations"),
    ("enforcement_receipt", "policy", "records that an effect path applied a decision"),
    ("approval_receipt", "authorization", "records approver, scope, conditions and expiry"),
    ("token_issuance_receipt", "authorization", "records issued token class, audience, scope and expiry without secret material"),
    ("secret_lease_receipt", "secrets", "records handle, version, consumer and lease expiry"),
    ("key_lifecycle_receipt", "crypto", "records key purpose, state transition and custody authority"),
    ("crypto_operation_receipt", "crypto", "records suite, key reference and context without plaintext"),
    ("tenant_isolation_test", "tenancy", "records control-plane and data-plane isolation probes"),
    ("tenant_quota_snapshot", "tenancy", "records enforced resource budgets"),
    ("classification_receipt", "privacy", "records classifier, vocabulary and confidence"),
    ("purpose_compatibility_receipt", "privacy", "records old and proposed purposes and authority"),
    ("permission_ledger_entry", "consent", "records capture, withdrawal and propagation state"),
    ("use_contract_compilation", "consent", "records lowered clauses and unlowered gaps"),
    ("residency_plan_receipt", "privacy", "records every planned storage, processing, transit and support locality"),
    ("retention_schedule_receipt", "retention", "records trigger, due date, holds and disposition"),
    ("deletion_receipt", "retention", "records storage class, object scope, method and verification"),
    ("rights_case_receipt", "rights", "records verified scope, searches, actions, omissions and response"),
    ("minimization_gate_receipt", "privacy", "records fields admitted or refused and purpose necessity"),
    ("deidentification_release_report", "deidentification", "records transform, attacker model, metrics and reviewer"),
    ("reidentification_test_report", "deidentification", "records attack suite, auxiliary data and observed risk"),
    ("privacy_budget_ledger", "differential_privacy", "records reservations, spends, refunds and composition"),
    ("dp_release_receipt", "differential_privacy", "records unit, mechanism, parameters, clipping and accountant"),
    ("secure_computation_transcript", "secure_computation", "records participants, function, attestation and approved outputs"),
    ("clean_room_query_receipt", "secure_computation", "records admitted query and composed output controls"),
    ("threat_assessment", "threat", "records assets, boundaries, assumptions, mitigations and residual risk"),
    ("audit_delivery_receipt", "audit", "records accepted, delayed, dropped and rejected event counts"),
    ("disclosure_record", "audit", "records recipient, data scope, purpose, decision and time"),
    ("provenance_statement", "evidence", "records entity/activity/agent derivation assertion"),
    ("attestation_result", "evidence", "records evidence, endorsement and appraisal policy result"),
    ("transparency_proof", "evidence", "records checkpoint plus inclusion and consistency proof"),
    ("sbom_document", "supply_chain", "records declared component inventory and relationships"),
    ("build_provenance", "supply_chain", "records subject digest, builder, materials and invocation"),
    ("artifact_promotion_receipt", "supply_chain", "records verified evidence and policy outcome"),
    ("incident_chain_of_custody", "incident", "records evidence digest, transfers and analysis copies"),
    ("containment_receipt", "incident", "records target scope, authority, action, impact and reversal"),
]


EVIDENCE_RECORDS = []
for short, domain, claim in EVIDENCE_SEEDS:
    ev = evidence(domain)
    EVIDENCE_RECORDS.append({
        "evidence_id": f"evidence.spt.{short}", "edition": EDITION, "status": STATUS,
        "domain": domain, "claim_scope": claim, "subject_identity": "required",
        "producer_identity": "required", "event_time": "required_with_clock_quality", "observed_time": "required",
        "integrity": ["canonical encoding or exact bytes", "digest", "signature or protected store as applicable"],
        "freshness": "explicit expiry, checkpoint, or collection time", "limitations": ["Evidence may be false at source.", "Integrity is not semantic truth.", "Absence is not proof unless completeness is independently established."],
        "evidence_source_ids": ev, "cross_platform_map": cross_map(domain, ev),
    })


INNOVATION_SEEDS = [
    ("privacy_budget_scheduling", 2021, "differential_privacy", "Privacy budget schedulers make privacy loss a reservable workload resource.", "src.privacy-budget-ledger.paper"),
    ("confidential_containers", 2022, "secure_computation", "Confidential-container stacks bind workload launch to hardware-isolated execution and attestation.", "src.confidential-containers"),
    ("ssdf_1_1", 2022, "supply_chain", "SSDF 1.1 aligns secure development practices with software supply-chain risk.", "src.nist.sp800-218"),
    ("hpke_standard", 2022, "crypto", "HPKE standardizes composable public-key encryption modes.", "src.ietf.rfc9180"),
    ("cose_internet_standard", 2022, "crypto", "COSE gives constrained ecosystems typed signed and encrypted envelopes.", "src.ietf.rfc9052"),
    ("csaf_2", 2022, "supply_chain", "CSAF 2.0 enables machine-readable vulnerability status and remediation exchange.", "src.oasis.csaf2"),
    ("rats_architecture", 2023, "evidence", "RATS standardizes attester, verifier, endorser, evidence and attestation-result roles.", "src.ietf.rfc9334"),
    ("dpop", 2023, "authorization", "DPoP sender-constrains OAuth tokens with per-request proof of key possession.", "src.ietf.rfc9449"),
    ("nist_deidentification_governance", 2023, "deidentification", "NIST SP 800-188 treats de-identification as technique plus governance and risk evaluation.", "src.nist.sp800-188"),
    ("slsa_1_0", 2023, "supply_chain", "SLSA 1.0 stabilizes build-track requirements and provenance expectations.", "src.slsa.v1"),
    ("cedar_language", 2023, "authorization", "Cedar makes schema-validated, analyzable authorization policy a portable library boundary.", "src.cedar.spec"),
    ("oblivious_http", 2024, "privacy", "Oblivious HTTP separates a relay's client-network view from a gateway's plaintext request view.", "src.ietf.rfc9458"),
    ("privacy_pass_architecture", 2024, "secure_computation", "Privacy Pass defines unlinkable issuance and redemption roles for privacy-preserving anti-abuse.", "src.ietf.rfc9576"),
    ("gnap", 2024, "authorization", "GNAP represents grant negotiation, continuation and key-bound access explicitly.", "src.ietf.rfc9635"),
    ("nist_csf_2_govern", 2024, "incident", "CSF 2.0 adds Govern as a first-class cybersecurity outcome function.", "src.nist.csf2"),
    ("dpv_2", 2024, "privacy", "DPV 2.0 expands machine-readable purpose, processing, rights and risk vocabulary.", "src.w3c.dpv2"),
    ("ml_kem", 2024, "crypto", "FIPS 203 standardizes ML-KEM for post-quantum key establishment.", "src.nist.fips203"),
    ("ml_dsa", 2024, "crypto", "FIPS 204 standardizes ML-DSA post-quantum signatures.", "src.nist.fips204"),
    ("slh_dsa", 2024, "crypto", "FIPS 205 standardizes stateless hash-based post-quantum signatures.", "src.nist.fips205"),
    ("spdx_3", 2024, "supply_chain", "SPDX 3.0 generalizes graph relationships and profiles for supply-chain evidence.", "src.spdx3"),
    ("cyclonedx_1_6_crypto_assets", 2024, "supply_chain", "CycloneDX 1.6 adds richer cryptographic-asset inventory and attestations.", "src.cyclonedx16"),
    ("oauth_security_bcp", 2025, "authorization", "RFC 9700 consolidates modern OAuth attacks and deprecates unsafe patterns.", "src.ietf.rfc9700"),
    ("nist_dp_evaluation", 2025, "differential_privacy", "NIST SP 800-226 evaluates differential-privacy products across threat model, data, mechanism and implementation.", "src.nist.sp800-226"),
    ("vc_data_model_2", 2025, "identity", "Verifiable Credentials 2.0 stabilizes issuer-holder-verifier artifacts, status and proof extension points.", "src.w3c.vc2"),
    ("pseudonymisation_guidelines", 2025, "deidentification", "EDPB guidance sharpens the distinction between pseudonymisation and anonymisation.", "src.edpb.pseudonymisation"),
    ("digital_identity_guidelines_4", 2025, "identity", "NIST SP 800-63-4 updates identity proofing, authentication and federation assurance guidance.", "src.nist.sp800-63-4"),
    ("incident_response_r3", 2025, "incident", "NIST SP 800-61r3 aligns incident response with CSF 2.0 risk outcomes.", "src.nist.sp800-61r3"),
    ("webauthn_level_3", 2026, "identity", "WebAuthn Level 3 advances scoped public-key authentication and privacy-aware authenticator behavior.", "src.w3c.webauthn3"),
]


INNOVATIONS = []
for short, year, domain, novelty, source_id in INNOVATION_SEEDS:
    INNOVATIONS.append({
        "innovation_id": f"innovation.spt.{short}", "edition": EDITION, "status": STATUS,
        "year": year, "domain": domain, "novelty": novelty,
        "platform_consequence": "Candidate capability, decision, evidence, or threat-model extension; adoption requires provider qualification.",
        "maturity": "standard, guidance, or demonstrated research as identified by source_kind",
        "limitations": "Recency is not proof of superiority or ecosystem availability.",
        "evidence_source_ids": [source_id], "cross_platform_map": cross_map(domain, [source_id]),
    })


GAP_SEEDS = [
    ("legal_to_contract", "consent", "No universal faithful translation exists from legal text to executable platform contracts."),
    ("purpose_compatibility", "privacy", "Purpose compatibility remains contextual and authority-dependent."),
    ("residency_observability", "privacy", "Many providers cannot prove every control-plane, support, backup and transit locality."),
    ("derived_deletion", "retention", "Deletion propagation through aggregates, features, caches and learned statistical artifacts is not uniformly specified."),
    ("backup_verification", "retention", "Selective deletion and independently verifiable deletion in immutable backups remain weak."),
    ("rights_identity", "rights", "Proportionate identity proofing for rights requests lacks portable assurance profiles."),
    ("pseudonymization_claims", "deidentification", "Portable claim vocabulary rarely binds pseudonym mapping custody and attacker access."),
    ("anonymization_portability", "deidentification", "Anonymity is release-context dependent and cannot be a timeless dataset property."),
    ("privacy_budget_interchange", "differential_privacy", "No broadly adopted interoperable ledger protocol composes privacy loss across engines."),
    ("dp_implementation_conformance", "differential_privacy", "Mechanism implementations lack routine end-to-end conformance evidence."),
    ("clean_room_semantics", "secure_computation", "The term data clean room has no single technical isolation or leakage contract."),
    ("query_composition", "secure_computation", "Cross-session output-control composition is inconsistently exposed by clean-room systems."),
    ("enclave_side_channels", "secure_computation", "Hardware isolation claims vary and often exclude important side channels and denial of service."),
    ("policy_language_interop", "policy", "Authorization policy languages lack lossless cross-language translation."),
    ("decision_effect_atomicity", "policy", "Distributed policy decision and effect enforcement rarely share atomic state."),
    ("tenant_isolation_evidence", "tenancy", "Tenant isolation tiers lack portable conformance receipts across compute, storage, network and metadata."),
    ("audit_completeness", "audit", "A log can prove integrity of received records without proving omitted events never occurred."),
    ("provenance_truth", "evidence", "Signed provenance still depends on producer honesty and observation coverage."),
    ("attestation_appraisal", "evidence", "Portable evidence does not imply portable appraisal policy or trustworthy endorsements."),
    ("supply_chain_runtime_binding", "supply_chain", "Build provenance is not always bound to the exact runtime bytes and configuration."),
    ("replay_authority", "supply_chain", "Data pipeline replay authorization and evidence are not standardized across runtimes."),
    ("incident_clock_quality", "incident", "Cross-system clocks and event loss weaken deterministic incident reconstruction."),
    ("crypto_agility_inventory", "crypto", "Platforms often lack complete key, algorithm, envelope and dependency inventories for migration."),
    ("consent_propagation", "consent", "Withdrawal propagation across external recipients lacks uniform acknowledgements and proof."),
]


GAPS = []
for short, domain, statement in GAP_SEEDS:
    ev = evidence(domain)
    GAPS.append({
        "gap_id": f"gap.spt.{short}", "edition": EDITION, "status": "open_candidate_gap",
        "domain": domain, "statement": statement, "compiler_behavior": "emit_typed_gap_and_refuse_when_required",
        "closure_evidence": ["bounded semantics", "owner adjudication", "conformance tests", "independent review"],
        "evidence_source_ids": ev, "cross_platform_map": cross_map(domain, ev),
    })


REGISTRIES = {
    "sources": ("source_id", SOURCES),
    "bounded-context-candidates": ("context_id", CONTEXTS),
    "assets-trust-boundaries": ("asset_id", ASSETS),
    "threat-abuse-cases": ("threat_id", THREATS),
    "capabilities": ("capability_id", CAPABILITIES),
    "operations": ("operation_id", OPERATIONS),
    "decisions": ("decision_id", DECISIONS),
    "invariants-refusals": ("rule_id", INVARIANTS),
    "compiler-requirements": ("requirement_id", REQUIREMENTS),
    "capability-offers": ("offer_id", OFFERS),
    "compiler-mappings": ("mapping_id", MAPPINGS),
    "library-boundaries": ("library_id", LIBRARIES),
    "evidence": ("evidence_id", EVIDENCE_RECORDS),
    "innovations": ("innovation_id", INNOVATIONS),
    "gaps": ("gap_id", GAPS),
}


REQUIRED_BY_REGISTRY = {
    "sources": ["source_id", "title", "publisher", "url", "source_kind", "domains", "claim_supported", "occurrences"],
    "bounded-context-candidates": ["context_id", "name", "domain", "boundary", "aggregate_roots", "invariants", "commands", "events", "refusals", "cross_platform_map"],
    "assets-trust-boundaries": ["asset_id", "name", "asset_kind", "domain", "trust_boundary", "authority_owner", "cross_platform_map"],
    "threat-abuse-cases": ["threat_id", "name", "threat_kind", "owner_context", "asset_refs", "actor_model", "precondition", "abuse_flow", "impact", "mitigation_classes", "cross_platform_map"],
    "capabilities": ["capability_id", "name", "owner_context", "domain", "intent", "inputs", "outputs", "preconditions", "postconditions", "cross_platform_map"],
    "operations": ["operation_id", "name", "owner_context", "domain", "signature", "effects", "idempotency", "preconditions", "postconditions", "failures", "cross_platform_map"],
    "decisions": ["decision_id", "owner_context", "domain", "question", "allowed_value_kinds", "binding_phase", "default_law", "cross_platform_map"],
    "invariants-refusals": ["rule_id", "rule_kind", "domain", "statement", "compiler_action", "failure_code", "cross_platform_map"],
    "compiler-requirements": ["requirement_id", "capability_ref", "owner_context", "requirement_kind", "must_support", "constraints", "unknown_offer_action", "cross_platform_map"],
    "capability-offers": ["offer_id", "offer_kind", "provider_binding", "declared_capabilities", "limits", "assurance", "qualification_state", "cross_platform_map"],
    "compiler-mappings": ["mapping_id", "context_ref", "intent_inputs", "required_capabilities", "candidate_operations", "requirement_refs", "offer_match_law", "gap_output", "cross_platform_map"],
    "library-boundaries": ["library_id", "domain", "effect_class", "owns", "must_not_own", "public_types", "required_receipts", "cross_platform_map"],
    "evidence": ["evidence_id", "domain", "claim_scope", "subject_identity", "producer_identity", "event_time", "integrity", "freshness", "limitations", "cross_platform_map"],
    "innovations": ["innovation_id", "year", "domain", "novelty", "platform_consequence", "maturity", "limitations", "cross_platform_map"],
    "gaps": ["gap_id", "domain", "statement", "compiler_behavior", "closure_evidence", "cross_platform_map"],
}


def infer_schema(values: list[object]) -> dict:
    """Infer a conservative structural schema from every generated value for one field."""
    present = [value for value in values if value is not None]
    nullable = len(present) != len(values)
    if not present:
        return {"type": ["string", "null"]}
    kinds = {type(value) for value in present}
    if len(kinds) > 1:
        return {}
    exemplar = present[0]
    if isinstance(exemplar, bool):
        base: dict = {"type": "boolean"}
    elif isinstance(exemplar, int):
        base = {"type": "integer"}
    elif isinstance(exemplar, str):
        base = {"type": "string", "minLength": 1}
    elif isinstance(exemplar, list):
        elements = [element for value in present for element in value]
        base = {"type": "array", "items": infer_schema(elements) if elements else {}, "minItems": 1}
    elif isinstance(exemplar, dict):
        shared = set.intersection(*(set(value) for value in present))
        base = {
            "type": "object",
            "required": sorted(shared),
            "properties": {field: infer_schema([value[field] for value in present if field in value]) for field in sorted(set.union(*(set(value) for value in present)))},
        }
    else:
        return {}
    if nullable:
        scalar_type = base.get("type")
        if isinstance(scalar_type, str):
            base["type"] = [scalar_type, "null"]
    return base


def registry_schema(name: str, identifier: str, required: list[str]) -> dict:
    records = REGISTRIES[name][1]
    properties = {
        identifier: {"type": "string", "minLength": 3},
        "edition": {"type": "integer", "minimum": 1},
        "status": {"type": "string", "enum": [STATUS, "open_candidate_gap"]},
        "evidence_source_ids": {"type": "array", "items": {"type": "string"}, "minItems": 1, "uniqueItems": True},
        "cross_platform_map": {
            "type": "object", "required": list(SURFACES), "additionalProperties": False,
            "properties": {surface: {"type": "array", "items": {"type": "string"}, "minItems": 1} for surface in SURFACES},
        },
    }
    # Other registry-specific properties deliberately allow structured extension while core fields
    # remain required.  The validator adds semantic and referential checks JSON Schema cannot express.
    for field in required:
        if field not in properties:
            properties[field] = infer_schema([record.get(field) for record in records])
    core_required = [identifier, "edition", "status", *required]
    if name != "sources":
        core_required.append("evidence_source_ids")
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": f"https://san.local/domain-atlas/security-privacy-trust/{name}.schema.json",
        "title": f"Security Privacy Trust {name} candidate",
        "type": "object", "additionalProperties": True,
        "required": sorted(set(core_required)),
        "properties": properties,
    }


def main() -> int:
    for name, (identifier, records) in REGISTRIES.items():
        write_jsonl(HERE / f"{name}.jsonl", records)
        write_json(SCHEMAS / f"{name}.schema.json", registry_schema(name, identifier, REQUIRED_BY_REGISTRY[name]))

    counts = {name: len(records) for name, (_, records) in REGISTRIES.items()}
    combined = counts["capabilities"] + counts["operations"] + counts["threat-abuse-cases"] + counts["decisions"]
    cited_sources = {
        source_id
        for name, (_, records) in REGISTRIES.items() if name != "sources"
        for record in records
        for source_id in record.get("evidence_source_ids", [])
    }
    write_json(HERE / "coverage-report.json", {
        "report_id": "san.domain-atlas.security-privacy-trust.coverage",
        "edition": EDITION, "as_of": AS_OF, "status": "candidate_corpus_incomplete",
        "counts": counts, "combined_capability_operation_threat_decision_candidates": combined,
        "primary_source_count": len(SOURCES), "cited_source_count": len(cited_sources),
        "recent_innovation_count": len(INNOVATIONS),
        "bounded_context_count": len(CONTEXTS), "cross_platform_surfaces": list(SURFACES),
        "completion_claim": False,
        "limits": [
            "Open-world enumeration cannot prove that every security, privacy or trust concept has been found.",
            "Legal texts identify obligation vocabulary but this corpus does not decide applicability or provide legal advice.",
            "Provider capabilities and control effectiveness require independent qualification and recurring evidence.",
            "Research candidates require split/merge, domain-owner adjudication and two-unrelated-platform validation.",
            "Generative-model methods are excluded from the core universe.",
        ],
    })
    write_manifest()
    print("WROTE security/privacy/trust corpus: " + ", ".join(f"{name}={count}" for name, count in counts.items()) + f", combined={combined}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
