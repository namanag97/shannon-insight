#!/usr/bin/env python3
"""Build ranked source-authority and public-symbol adjudication packets."""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
SEM = HERE.parent
AS_OF = "2026-08-27"


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


PRIMARY_SOURCES = [
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.rfc9110.protocol-version", "title": "RFC 9110: HTTP Semantics", "issuer": "IETF", "edition_or_date": "June 2022", "uri": "https://www.rfc-editor.org/rfc/rfc9110.html", "bounded_claims": ["HTTP protocol version binds messaging syntax and sender conformance/capability under HTTP-specific rules", "HTTP core semantics and wire protocol versions evolve on partly independent axes"], "does_not_prove": ["a universal protocol-edition algebra", "ordinal compatibility across unrelated protocols"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.rfc9530.digest-fields", "title": "RFC 9530: Digest Fields", "issuer": "IETF", "edition_or_date": "February 2024", "uri": "https://www.rfc-editor.org/rfc/rfc9530.html", "bounded_claims": ["Content-Digest hashes actual HTTP message content under a named algorithm", "Repr-Digest hashes selected representation data", "digest fields do not define authentication authorization or privacy"], "does_not_prove": ["business identity", "semantic equality", "truth or authority"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.rfc3986.uri-identity", "title": "RFC 3986: Uniform Resource Identifier (URI): Generic Syntax", "issuer": "IETF", "edition_or_date": "January 2005", "uri": "https://www.rfc-editor.org/rfc/rfc3986.html", "bounded_claims": ["an identifier distinguishes a resource within a scope without necessarily embodying its identity", "URI assignment and scheme semantics are delegated to the scheme specification", "URI equivalence is purpose dependent and comparison cannot prove that unequal URIs identify different resources"], "does_not_prove": ["business-object identity from URI syntax", "authority or authenticity of a URI claimant", "one universal canonicalization or equality relation"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.rfc9562.uuid", "title": "RFC 9562: Universally Unique IDentifiers (UUIDs)", "issuer": "IETF", "edition_or_date": "May 2024", "uri": "https://www.rfc-editor.org/rfc/rfc9562.html", "bounded_claims": ["UUIDs are 128-bit identifiers intended to provide practical uniqueness across space and time", "name-based UUID equality depends on the same namespace and canonical name", "true global uniqueness cannot be guaranteed without shared knowledge"], "does_not_prove": ["the semantic kind of the identified subject", "authenticity authority or authorization", "same-subject identity across namespaces or identity epochs"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.w3c.did-core", "title": "Decentralized Identifiers (DIDs) v1.0", "issuer": "W3C", "edition_or_date": "W3C Recommendation 19 July 2022", "uri": "https://www.w3.org/TR/did-core/", "bounded_claims": ["a DID subject and DID controller are distinct roles", "DID URL resources are distinct from the DID subject", "alsoKnownAs assertions require relying-party judgment rather than automatic identity collapse"], "does_not_prove": ["that control is subject identity", "business role or authorization from identifier possession", "universal equivalence between different identifiers"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.rfc6920.named-information", "title": "RFC 6920: Naming Things with Hashes", "issuer": "IETF", "edition_or_date": "April 2013", "uri": "https://www.rfc-editor.org/rfc/rfc6920.html", "bounded_claims": ["a named-information URI identifies a digital object using a hash-algorithm suite and digest value", "hash-based names can authenticate retrieved bytes to the same degree as the trusted reference", "algorithm agility and exact suite identity remain part of the name"], "does_not_prove": ["business-semantic identity", "truth provenance or authorization of the named content", "identity of mutable or differently canonicalized representations"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.rfc8785.jcs", "title": "RFC 8785: JSON Canonicalization Scheme (JCS)", "issuer": "Independent Submission / RFC Editor", "edition_or_date": "June 2020", "uri": "https://www.rfc-editor.org/rfc/rfc8785.html", "bounded_claims": ["JCS defines an invariant JSON representation for repeatable hashing and signing", "canonicalization fixes serialization and property-order rules for an I-JSON subset", "the canonicalizer is a representation filter independent of the cryptographic scheme"], "does_not_prove": ["semantic equivalence of different JSON values", "domain identity or truth", "canonicalization outside the JCS profile"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.w3c.dcat3-versioning", "title": "Data Catalog Vocabulary (DCAT) Version 3", "issuer": "W3C", "edition_or_date": "W3C Recommendation 22 August 2024", "uri": "https://www.w3.org/TR/vocab-dcat-3/", "bounded_claims": ["resource identity, versioned resource, version chain, replacement and dataset-series membership are distinct relations", "version policy is community and workflow dependent", "a generic version relation can denote revisions editions adaptations or translations unless further qualified"], "does_not_prove": ["compatibility from version ordering", "one universal rule for when change creates a new version", "that current version means active accepted or authoritative"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.semver.2", "title": "Semantic Versioning 2.0.0", "issuer": "Semantic Versioning specification", "edition_or_date": "2.0.0", "uri": "https://semver.org/", "bounded_claims": ["version semantics are conditioned on a declared public API", "major minor and patch changes encode compatibility claims under that public API", "precedence ignores build metadata and is distinct from exact version identity"], "does_not_prove": ["behavioral data or business compatibility outside the declared API", "authority currentness deployment or activation", "compatibility when the public API is unspecified"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.otel.span-context", "title": "OpenTelemetry Specification: Overview and SpanContext", "issuer": "OpenTelemetry Project / CNCF", "edition_or_date": "current specification accessed 2026-08-26", "uri": "https://opentelemetry.io/docs/specs/otel/overview/", "bounded_claims": ["TraceId groups spans for one trace while SpanId identifies one span", "SpanContext carries identifiers and propagation options across process boundaries", "operation name identifies a class of work rather than an individual occurrence"], "does_not_prove": ["business transaction identity", "exactly-once execution or effect", "that trace span attempt and job identities are interchangeable"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.openlineage.run-identity", "title": "OpenLineage Run Facets", "issuer": "OpenLineage Project / LF AI & Data", "edition_or_date": "current specification accessed 2026-08-26", "uri": "https://openlineage.io/docs/spec/facets/run-facets/", "bounded_claims": ["each run has a separately trackable run identifier usually represented by a UUID", "run facets attach metadata to the run occurrence"], "does_not_prove": ["job identity from run identity", "attempt equivalence across retry policies", "exactly-once effects or successful completion"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.nist.sp800-63-4", "title": "NIST SP 800-63-4: Digital Identity Guidelines", "issuer": "National Institute of Standards and Technology", "edition_or_date": "Revision 4 final, July 2025", "uri": "https://pages.nist.gov/800-63-4/sp800-63.html", "bounded_claims": ["identity proofing, authentication and federation use distinct IAL, AAL and FAL assurance dimensions", "assurance-level selection is risk, user-group and service specific", "digital-identity controls augment rather than replace authorization and system controls"], "does_not_prove": ["a universal scalar assurance level", "authorization from successful authentication", "business acceptance outside the relying party and service context"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.nist.sp800-162-abac", "title": "NIST SP 800-162: Guide to Attribute Based Access Control Definition and Considerations", "issuer": "National Institute of Standards and Technology", "edition_or_date": "Updated final, August 2019", "uri": "https://csrc.nist.gov/pubs/sp/800/162/upd2/final", "bounded_claims": ["authorization evaluates subject, object, requested operation and environment attributes against policy or relationships", "digital policy and enforcement mechanisms are distinct from natural-language policy", "attribute association and policy decision inputs require assured bindings"], "does_not_prove": ["a permit decision from principal action and resource identifiers alone", "enforcement or completed effect from policy evaluation", "one universal authorization model"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.rfc6749.oauth2", "title": "RFC 6749: The OAuth 2.0 Authorization Framework", "issuer": "IETF", "edition_or_date": "October 2012", "uri": "https://www.rfc-editor.org/rfc/rfc6749.html", "bounded_claims": ["resource owner, client, authorization server and resource server are distinct roles", "authorization grant, access token and refresh token are distinct credentials", "requested and granted token scopes can differ and tokens bind duration and scope"], "does_not_prove": ["principal identity from bearer-token possession", "authorization outside the token audience scope and duration", "business effect from successful token validation"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.rfc7009.oauth-revocation", "title": "RFC 7009: OAuth 2.0 Token Revocation", "issuer": "IETF", "edition_or_date": "August 2013", "uri": "https://www.rfc-editor.org/rfc/rfc7009.html", "bounded_claims": ["token revocation invalidates a selected token under authorization-server policy", "propagation delay can exist across servers", "cascading revocation of related tokens and grants is policy dependent"], "does_not_prove": ["instant global revocation propagation", "that a success response identifies whether the submitted token was valid", "revocation or compensation of business effects already performed"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.rfc7517.jwk", "title": "RFC 7517: JSON Web Key (JWK)", "issuer": "IETF", "edition_or_date": "May 2015", "uri": "https://www.rfc-editor.org/rfc/rfc7517.html", "bounded_claims": ["kid is an optional case-sensitive hint used to match a key", "kid structure is unspecified and distinctness inside a key set is a SHOULD rather than an identity proof", "key type intended use and intended algorithm are separate JWK members"], "does_not_prove": ["global key identity", "key possession or authorization", "current validity permitted use or uncompromised state"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.oasis.pkcs11-3-1", "title": "PKCS #11 Specification Version 3.1", "issuer": "OASIS Open", "edition_or_date": "OASIS Standard 2023", "uri": "https://docs.oasis-open.org/pkcs11/pkcs11-spec/v3.1/os/pkcs11-spec-v3.1-os.html", "bounded_claims": ["object handles provide session and application scoped access to token objects", "an object handle need not remain fixed for the object's lifetime", "handle usability depends on session object existence and accessibility"], "does_not_prove": ["stable secret or key identity from an opaque handle", "authorization outside the provider session", "key material possession or permitted cryptographic purpose"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.kubernetes.multi-tenancy", "title": "Kubernetes Multi-tenancy", "issuer": "Kubernetes Project / CNCF", "edition_or_date": "documentation accessed 2026-08-26", "uri": "https://kubernetes.io/docs/concepts/security/multi-tenancy/", "bounded_claims": ["tenant meaning depends on the organizational and workload model", "isolation is multi-dimensional across control plane data plane network storage nodes and sandboxing", "namespace segmentation requires additional authorization network storage and security controls"], "does_not_prove": ["that tenant identity equals namespace identity", "a universal hard or soft isolation class", "effective isolation from a declared profile without deployed-control evidence"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.spiffe.id", "title": "SPIFFE ID Specification", "issuer": "SPIFFE Project / CNCF", "edition_or_date": "current specification accessed 2026-08-26", "uri": "https://spiffe.io/docs/latest/spiffe-specs/spiffe-id/", "bounded_claims": ["a workload identity is qualified by a trust-domain authority and path", "trust-domain namespaces can collide and remain administratively independent", "path meaning is administrator defined within the trust domain"], "does_not_prove": ["legal entity identity from a trust-domain string", "authorization from an authenticated workload identity", "semantic equality across trust domains"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.protobuf.proto3-evolution", "title": "Protocol Buffers Language Guide (proto3): Updating A Message Type", "issuer": "Google Protocol Buffers", "edition_or_date": "accessed 2026-08-26", "uri": "https://protobuf.dev/programming-guides/proto3/#updating", "bounded_claims": ["safe changes depend on the Protocol Buffers binary wire contract", "ProtoJSON and text format have different change compatibility"], "does_not_prove": ["semantic compatibility", "compatibility for unrelated schemas or runtimes"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.avro.schema-resolution", "title": "Apache Avro Specification: Schema Resolution", "issuer": "Apache Avro", "edition_or_date": "current specification accessed 2026-08-26", "uri": "https://avro.apache.org/docs/current/specification/#schema-resolution", "bounded_claims": ["Avro compatibility is evaluated by reader/writer schema resolution rules", "canonical schema form and schema resolution answer different questions"], "does_not_prove": ["business-semantic compatibility", "bidirectional compatibility without checking both directions"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.iceberg.evolution", "title": "Apache Iceberg Table Specification", "issuer": "Apache Iceberg", "edition_or_date": "current specification accessed 2026-08-26", "uri": "https://iceberg.apache.org/spec/", "bounded_claims": ["schema evolution uses stable field IDs and a constrained promotion relation", "format version changes are tied to forward-compatibility of readers"], "does_not_prove": ["API compatibility", "semantic equivalence of renamed business fields"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.cargo.semver", "title": "The Cargo Book: SemVer Compatibility", "issuer": "Rust Project", "edition_or_date": "current documentation accessed 2026-08-26", "uri": "https://doc.rust-lang.org/cargo/reference/semver.html", "bounded_claims": ["Cargo compatibility guidance focuses mainly on whether existing Rust use sites continue to build", "runtime behavioral compatibility often remains a maintainer judgment"], "does_not_prove": ["wire or data compatibility", "behavioral compatibility", "compatibility outside an exact Rust package surface"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.etcd.lease-api", "title": "etcd API: Lease API", "issuer": "etcd Project", "edition_or_date": "v3.6 documentation accessed 2026-08-26", "uri": "https://etcd.io/docs/v3.6/learning/api/#lease-api", "bounded_claims": ["etcd leases detect client liveness under a server-granted TTL", "lease expiry or revocation deletes attached keys", "requested TTL and ID are distinct from the server-granted lease response"], "does_not_prove": ["secret validity", "exclusive ownership of an external effect", "that lease expiry alone fences a stale actor"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.vault.lease-semantics", "title": "Vault: Lease, Renew, and Revoke", "issuer": "HashiCorp", "edition_or_date": "v2.x documentation accessed 2026-08-26", "uri": "https://developer.hashicorp.com/vault/docs/concepts/lease", "bounded_claims": ["Vault leases carry secret or token validity metadata including TTL and renewability", "a requested renewal increment is advisory and the returned lease must be inspected", "expiry, renewal and revocation are distinct lifecycle events"], "does_not_prove": ["coordination lock ownership", "effect fencing", "that all secret stores use Vault lease semantics"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.vault.lease-api", "title": "Vault HTTP API: /sys/leases", "issuer": "HashiCorp", "edition_or_date": "v2.x documentation accessed 2026-08-26", "uri": "https://developer.hashicorp.com/vault/api-docs/system/leases", "bounded_claims": ["lease lookup exposes issue time, expiry, renewal state and TTL", "revocation may be queued or synchronous", "forced revocation can ignore backend failures and therefore does not ensure downstream cleanup"], "does_not_prove": ["that a revocation request is a completed revocation", "that force-revoke proves credential invalidation", "generic lease semantics outside Vault"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.chubby.lock-service", "title": "The Chubby Lock Service for Loosely-Coupled Distributed Systems", "issuer": "Google Research", "edition_or_date": "OSDI 2006", "uri": "https://research.google/pubs/the-chubby-lock-service-for-loosely-coupled-distributed-systems/", "bounded_claims": ["Chubby is a coarse-grained distributed lock service with advisory locks", "the service emphasizes availability and reliability rather than high performance"], "does_not_prove": ["that every temporal grant is a lock", "that a lease alone prevents a stale holder from acting", "secret lease semantics"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.grpc.cancellation", "title": "gRPC Cancellation Guide", "issuer": "gRPC Project", "edition_or_date": "documentation accessed 2026-08-26", "uri": "https://grpc.io/docs/guides/cancellation/", "bounded_claims": ["cancellation signals discontinuation of client interest", "a server handler may still be executing after cancellation notification", "cessation is cooperative and propagation to upstream work varies by language or handler"], "does_not_prove": ["that cancellation request implies work termination", "that cancellation has one universal propagation policy", "that already committed effects are compensated"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.w3c.prov-dm", "title": "PROV-DM: The PROV Data Model", "issuer": "W3C", "edition_or_date": "W3C Recommendation 30 April 2013", "uri": "https://www.w3.org/TR/prov-dm/", "bounded_claims": ["PROV derivation connects a generated entity to a used entity through influence", "use and generation alone are not sufficient to infer derivation", "applications determine derivation conditions and may expand relations with domain detail"], "does_not_prove": ["a universal information-loss metric", "that every transformation is lossy", "business acceptability of a transformation"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.w3c.prov-constraints", "title": "Constraints of the PROV Data Model", "issuer": "W3C", "edition_or_date": "W3C Recommendation 30 April 2013", "uri": "https://www.w3.org/TR/prov-constraints/", "bounded_claims": ["PROV validity is closer to consistency than truth", "PROV validity and equivalence use normalization plus explicit uniqueness, ordering, type and impossibility constraints"], "does_not_prove": ["losslessness of an interchange mapping", "truth or authority of provenance statements", "preservation of application-specific observables"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.rfc9110.transforming-proxies", "title": "RFC 9110: HTTP Semantics, Message Transformations", "issuer": "IETF", "edition_or_date": "June 2022", "uri": "https://www.rfc-editor.org/rfc/rfc9110.html#name-message-transformations", "bounded_claims": ["HTTP distinguishes transformations significant to senders or recipients from transport-only changes", "transformation significance depends on application context", "some transformations are forbidden by an explicit no-transform directive"], "does_not_prove": ["a universal loss dimension set", "that every format conversion is harmful", "that a recipient accepts a transformed representation"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.arrow.cast-options", "title": "Apache Arrow C++ Compute Functions: CastOptions", "issuer": "Apache Arrow", "edition_or_date": "v20.0.0 documentation accessed 2026-08-26", "uri": "https://arrow.apache.org/docs/20.0/cpp/api/compute.html#_CPPv4N5arrow7compute11CastOptionsE", "bounded_claims": ["casting loss and safety are decomposed into distinct policies for integer overflow, temporal truncation or overflow, decimal or floating truncation and invalid UTF-8", "not matching all safe options does not imply matching all unsafe options"], "does_not_prove": ["provenance-interchange loss", "authorization-policy translation loss", "one total ordering of all loss dimensions"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.tosca.requirements-capabilities", "title": "OASIS Topology and Orchestration Specification for Cloud Applications Version 2.0", "issuer": "OASIS Open", "edition_or_date": "OASIS Standard 2025", "uri": "https://docs.oasis-open.org/tosca/TOSCA/v2.0/TOSCA-v2.0.html", "bounded_claims": ["a capability is a typed exposed feature that may fulfill another node's requirement", "a requirement identifies capability type, target selection constraints, relationship and cardinality", "assignment and matching uniquely bind a particular target capability"], "does_not_prove": ["a universal SAN capability algebra", "that a provider claim is true", "that type-compatible matching establishes semantic fitness or qualification"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.wasm-component.wit", "title": "WebAssembly Component Model: WIT Text Format", "issuer": "WebAssembly Community Group", "edition_or_date": "MVP design accessed 2026-08-26", "uri": "https://github.com/WebAssembly/component-model/blob/main/design/mvp/WIT.md", "bounded_claims": ["WIT worlds describe component imports and exports and interfaces group functions and types", "package-qualified names disambiguate definitions", "same plain names with different meanings require explicit conflict resolution"], "does_not_prove": ["semantic capability satisfaction", "provider qualification", "behavioral conformance beyond the declared interface"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.nist.conformance-testing", "title": "Conformance Testing", "issuer": "National Institute of Standards and Technology", "edition_or_date": "official guidance accessed 2026-08-26", "uri": "https://www.nist.gov/itl/ai/applied-ai-research-group/conformance-testing", "bounded_claims": ["conformance criteria must be stated in a specification or profile", "test suites compare legal and illegal inputs to expected results", "testing and certification programs are separate components", "falsification can establish non-conformance while passing tests cannot generally prove complete conformance"], "does_not_prove": ["fitness for a business purpose", "interoperability, security or performance unless explicitly tested", "semantic ownership of the tested specification"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.w3c.act-rules", "title": "Accessibility Conformance Testing Rules Format 1.1", "issuer": "W3C", "edition_or_date": "W3C Recommendation 12 February 2026", "uri": "https://www.w3.org/TR/act-rules-format/", "bounded_claims": ["a test rule binds applicability, expectations, test subject and expected result", "outcomes distinguish passed, failed, inapplicable, cannot-tell and untested", "rule examples validate implementations but do not guarantee absence of incorrect results", "rule and glossary editions affect results"], "does_not_prove": ["one universal oracle outcome set for every domain", "that a passed check is global certification", "requirements outside the rule's explicit mapping"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.consort.2025", "title": "CONSORT 2025 Statement: Updated Guideline for Reporting Randomized Trials", "issuer": "CONSORT Group / JAMA", "edition_or_date": "14 April 2025", "uri": "https://doi.org/10.1001/jama.2025.4347", "bounded_claims": ["random assignment, receipt of the intended intervention and inclusion in an analysis are separately reported populations", "outcomes bind a measurement variable, participant-level analysis metric, aggregation method and time point", "analysis populations, missing-data handling, interim analyses and stopping guidelines must be explicit"], "does_not_prove": ["a universal online-experiment data model", "that assignment implies exposure or adherence", "that a statistically eligible boundary authorizes an operational stop"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.consort.outcome-item", "title": "CONSORT 2025 Item 14: Outcomes", "issuer": "SPIRIT-CONSORT Group", "edition_or_date": "2025 guidance accessed 2026-08-26", "uri": "https://www.consort-spirit.org/item14-outcomes", "bounded_claims": ["an outcome definition separates the specific measurement variable, participant-level analysis metric, group aggregation and measurement time point", "primary and secondary outcome roles are prespecified"], "does_not_prove": ["metric correctness for every business domain", "that one metric role or aggregation is universally preferable", "that observed telemetry is complete"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.consort.interim-item", "title": "CONSORT 2025 Item 16b: Interim Analyses", "issuer": "SPIRIT-CONSORT Group", "edition_or_date": "2025 guidance accessed 2026-08-26", "uri": "https://www.consort-spirit.org/item16b-interimanalyses", "bounded_claims": ["multiple looks, their timing, triggers, methods and stopping rules must be disclosed and preferably predetermined", "the actor who decides to continue, stop or modify is distinct from the statistical comparison", "group-sequential methods adjust for repeated looks"], "does_not_prove": ["one stopping method for every experiment", "that crossing a statistical boundary itself performs or authorizes a stop", "validity of an unplanned analysis"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.microsoft.trustworthy-analysis", "title": "Trustworthy Analysis of Online A/B Tests: Pitfalls, Challenges and Solutions", "issuer": "Microsoft Research / ACM WSDM", "edition_or_date": "February 2017", "uri": "https://www.microsoft.com/en-us/research/publication/trustworthy-analysis-of-online-a-b-tests-pitfalls-challenges-and-solutions/", "bounded_claims": ["online experiment analysis depends on the exact randomization mechanism and randomization unit", "treating the randomization unit as independent and identically distributed can underestimate variance under some treatment-effect structures"], "does_not_prove": ["that every assigned unit is exposed", "one universal variance estimator", "that an assignment cut alone defines the analysis population"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.microsoft.triggered-analysis", "title": "Patterns of Trustworthy Experimentation: Post-Experiment Stage", "issuer": "Microsoft Research Experimentation Platform", "edition_or_date": "2021", "uri": "https://www.microsoft.com/en-us/research/articles/patterns-of-trustworthy-experimentation-post-experiment-stage/", "bounded_claims": ["triggered analysis requires a counterfactual trigger for both treatment and control", "post-trigger analysis excludes observations before first trigger", "trigger completeness can be challenged using sample-ratio and triggered-complement checks"], "does_not_prove": ["that filtering on any observed exposure is unbiased", "that exposure and assignment are the same occurrence", "that a triggered estimate directly equals the all-population effect"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.deng-hu.trigger-dilution", "title": "Diluted Treatment Effect Estimation for Trigger Analysis in Online Controlled Experiments", "issuer": "Alex Deng and Victor Hu / ACM WSDM", "edition_or_date": "February 2015", "uri": "https://www.exp-platform.com/Documents/wsdm2015-dilution.pdf", "bounded_claims": ["triggered analysis and all-population effect estimation answer different questions", "effect translation depends on trigger type and metric algebra", "naive or approximate dilution formulas can be wrong for ratio metrics"], "does_not_prove": ["that every trigger definition is causally valid", "one universal dilution formula", "that observed treatment exposure supplies the missing control counterfactual"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.microsoft.dirty-dozen", "title": "A Dirty Dozen: Twelve Common Metric Interpretation Pitfalls in Online Controlled Experiments", "issuer": "Microsoft Research / ACM KDD", "edition_or_date": "August 2017", "uri": "https://www.microsoft.com/en-us/research/publication/a-dirty-dozen-twelve-common-metric-interpretation-pitfalls-in-online-controlled-experiments/", "bounded_claims": ["metric movements can be invalidated or misinterpreted by telemetry loss, observation-unit imbalance, low power and other experiment-specific defects", "metric definition and business interpretation require explicit design and diagnostics"], "does_not_prove": ["a universal metric quality score", "that statistical significance implies business importance", "that a missing movement proves no effect"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.johari.always-valid", "title": "Always Valid Inference: Bringing Sequential Analysis to A/B Testing", "issuer": "Ramesh Johari, Leo Pekelis and David J. Walsh", "edition_or_date": "arXiv:1512.04922, December 2015", "uri": "https://arxiv.org/abs/1512.04922", "bounded_claims": ["ordinary fixed-sample p-values and confidence intervals are unreliable under endogenous continuous monitoring", "always-valid p-values and confidence intervals provide a defined interface for sequential decisions at data-dependent stopping times"], "does_not_prove": ["that any repeated-look method is anytime valid", "that statistical stopping eligibility is a deployment decision", "that optional stopping repairs biased exposure or metric cuts"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.fda.adaptive-design", "title": "Adaptive Designs for Clinical Trials of Drugs and Biologics: Guidance for Industry", "issuer": "US Food and Drug Administration", "edition_or_date": "Final guidance, November 2019", "uri": "https://www.fda.gov/regulatory-information/search-fda-guidance-documents/adaptive-design-clinical-trials-drugs-and-biologics-guidance-industry", "bounded_claims": ["comparative interim analyses and stopping or adaptation rules require prospective planning and evaluated operating characteristics", "multiple looks require methods that control error rates", "stopping criteria can be expressed on several statistical scales"], "does_not_prove": ["one stopping policy outside its regulatory scope", "that a computed boundary crossing is an authorized operational action", "that an unrecorded interim look is harmless"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.w3c.dqv", "title": "Data on the Web Best Practices: Data Quality Vocabulary", "issuer": "W3C", "edition_or_date": "W3C Working Group Note 15 December 2016", "uri": "https://www.w3.org/TR/vocab-dqv/", "bounded_claims": ["a quality measurement binds a metric, the resource computed on, a value and normally a unit", "a metric belongs to a quality dimension", "DQV supports quality information for user fitness judgments without defining one complete universal notion of quality"], "does_not_prove": ["a universal quality score", "that measurement implies fitness or certification", "the exact evaluation population, snapshot or policy lifecycle needed by every application"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.w3c.shacl", "title": "Shapes Constraint Language (SHACL)", "issuer": "W3C", "edition_or_date": "W3C Recommendation 20 July 2017", "uri": "https://www.w3.org/TR/shacl/", "bounded_claims": ["targets select focus nodes for a shape", "focus nodes, value nodes, shapes graph, data graph and validation results are distinct", "a validation report is scoped to the supplied shapes and data graphs"], "does_not_prove": ["quality outside the declared constraints or targets", "that nodes outside the target passed", "a universal non-RDF evaluation-scope carrier without profiling"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.oasis.xacml-3", "title": "eXtensible Access Control Markup Language Version 3.0 Plus Errata 01", "issuer": "OASIS Open", "edition_or_date": "OASIS Standard 12 July 2017", "uri": "https://docs.oasis-open.org/xacml/3.0/xacml-3.0-core-spec-en.pdf", "bounded_claims": ["policy and policy-set identity are versioned", "a target determines policy applicability to a request context", "a response can identify the exact policy identifiers and versions found applicable", "combining algorithms, obligations, advice and indeterminate results remain explicit semantics"], "does_not_prove": ["quality-policy meaning", "that version ordering establishes semantic compatibility", "that policy applicability is the same as authorization or effect execution"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.w3c.odrl-model", "title": "ODRL Information Model 2.2", "issuer": "W3C", "edition_or_date": "W3C Recommendation 15 February 2018", "uri": "https://www.w3.org/TR/odrl-model/", "bounded_claims": ["a policy has a unique identifier and one or more permission, prohibition or obligation rules", "profiles identify additional vocabulary semantics that processors must understand", "assets, parties, actions, constraints, inheritance and conflict strategy are separate policy components"], "does_not_prove": ["quality/reconciliation policy semantics", "that identical JSON policy shapes share an owner", "a universal policy merge or precedence rule"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.opa.bundles", "title": "Open Policy Agent: Bundles", "issuer": "Open Policy Agent Project", "edition_or_date": "documentation accessed 2026-08-26", "uri": "https://www.openpolicyagent.org/docs/management-bundles", "bounded_claims": ["a bundle manifest can bind a revision, language edition and owned roots", "bundle activation is distinct from download and validation failure preserves the previous active bundle", "snapshot and delta bundle lifecycles differ"], "does_not_prove": ["semantic compatibility between revisions", "that a revision token is a content digest", "that activation authorizes a business action"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.opa.decision-logs", "title": "Open Policy Agent: Decision Logs", "issuer": "Open Policy Agent Project", "edition_or_date": "documentation accessed 2026-08-26", "uri": "https://www.openpolicyagent.org/docs/management-decision-logs", "bounded_claims": ["a decision event can bind decision identifier, policy path, exact bundle revision, input, result, requester and timestamp", "decision-log masking and erasure affect retained evidence"], "does_not_prove": ["that the logged result was enforced", "that the policy was semantically correct", "that an input record completely represents the external world"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.ich.e9-r1", "title": "ICH E9(R1): Estimands and Sensitivity Analysis in Clinical Trials", "issuer": "International Council for Harmonisation", "edition_or_date": "Step 4, 20 November 2019", "uri": "https://database.ich.org/sites/default/files/E9-R1_Step4_Guideline_2019_1203.pdf", "bounded_claims": ["an estimand aligns treatment condition, population, variable, intercurrent-event strategy and population-level summary", "the main estimator should be aligned to the estimand and supported by sensitivity analysis for its assumptions", "intercurrent-event handling belongs to the clinical question rather than an after-the-fact data fix"], "does_not_prove": ["one estimand for every experiment", "that an estimand binding is an observed result", "that a sensitivity analysis repairs an incoherent analysis plan"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.w3c.dx-prof", "title": "The Profiles Vocabulary", "issuer": "W3C", "edition_or_date": "W3C Working Group Note 18 December 2019", "uri": "https://www.w3.org/TR/dx-prof/", "bounded_claims": ["a profile is a specification that constrains, extends, combines or guides use of identified base specifications", "profile identity, profile hierarchy, supporting resources, their roles and artifact locations are distinct", "individual communities define what conformance to their profiles means and how it is tested"], "does_not_prove": ["that profile identity is profile edition identity", "that a supporting validator establishes conformance outside its scope", "one universal publication-profile result algebra"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.kubernetes.scheduling-framework", "title": "Kubernetes Scheduling Framework", "issuer": "Kubernetes Project", "edition_or_date": "documentation accessed 2026-08-26", "uri": "https://kubernetes.io/docs/concepts/scheduling-eviction/scheduling-framework/", "bounded_claims": ["the scheduling framework is a pluggable architecture with ordered extension points", "one scheduling attempt separates a scheduling cycle that selects a node from a binding cycle that applies the decision", "plugins may be configured into named scheduler profiles"], "does_not_prove": ["that every scheduling policy has Kubernetes lifecycle semantics", "that a scheduling decision reserves or binds resources", "that one policy trait should own all scheduling algorithms"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.ieee.xes-2023", "title": "IEEE 1849-2023: eXtensible Event Stream (XES)", "issuer": "IEEE Standards Association", "edition_or_date": "2023", "uri": "https://standards.ieee.org/ieee/1849/10907/", "bounded_claims": ["XES defines an interoperable grammar and schemas for event logs and event streams", "extensions attach declared semantics to attributes under the XES representation"], "does_not_prove": ["that one case notion is appropriate", "source-event completeness", "a process model or conformance verdict"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.ocel-2", "title": "OCEL 2.0 Specification", "issuer": "OCEL Standard authors / RWTH Aachen", "edition_or_date": "16 October 2023", "uri": "https://www.ocel-standard.org/2.0/ocel20_specification.pdf", "bounded_claims": ["OCEL distinguishes uniquely identified events, objects, event and object types, attributes, event-to-object relations, object-to-object relations and qualifiers", "object attribute values may change over time", "JSON, XML and relational encodings represent the same object-centric event-log model"], "does_not_prove": ["one selected case or object projection", "complete capture of source-system behavior", "a discovered or normative process model"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.oced-whitepaper", "title": "Towards a Simple and Extensible Standard for Object-Centric Event Data", "issuer": "IEEE Task Force on Process Mining OCED Working Group", "edition_or_date": "2024 whitepaper", "uri": "https://arxiv.org/abs/2410.14495", "bounded_claims": ["object-centric event data standardization separates a core model from extensions and implementation choices", "source-to-event-data transformation is a governed interoperability problem"], "does_not_prove": ["a final ratified OCED standard", "that OCED and OCEL have identical identity or extension laws", "one universal analytical projection"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.fahland.event-knowledge-graphs", "title": "Process Mining over Multiple Behavioral Dimensions with Event Knowledge Graphs", "issuer": "Dirk Fahland / Process Mining Handbook", "edition_or_date": "2022", "uri": "https://doi.org/10.1007/978-3-031-08848-3_9", "bounded_claims": ["event knowledge graphs model behavior over multiple entities as a network of events", "construction, querying and aggregation expose multiple behavioral dimensions without first choosing one global case identifier"], "does_not_prove": ["that every graph view is an event knowledge graph", "that graph reachability is causal process behavior", "that an aggregation is a process model"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.ocel-to-tekg", "title": "Transforming Object-Centric Event Logs to Temporal Event Knowledge Graphs", "issuer": "Research paper authors", "edition_or_date": "2024", "uri": "https://arxiv.org/abs/2406.07596", "bounded_claims": ["an OCEL can be transformed into a temporal event knowledge graph under an explicit mapping", "the temporal graph makes events, objects and their time-related relations available for graph analysis"], "does_not_prove": ["a lossless or canonical transformation for every consumer", "that a TEKG is the source event log", "that the resulting graph is a discovered process model"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.state-aware-ocpm", "title": "State-Aware Object-Centric Process Mining: Enhancing OCEL 2.0 with Explicit State Transitions", "issuer": "Dina Kretzschmann, Alessandro Berti and Wil M. P. van der Aalst", "edition_or_date": "2025 paper", "uri": "https://www.alessandroberti.it/new_papers/2025_Dina_SAOCPM.pdf", "bounded_claims": ["state-aware object-centric analysis derives explicit state-change events from selected time-varying object attributes", "state derivation depends on the selected state attribute and reconstruction rule"], "does_not_prove": ["that every object attribute defines authoritative state", "that generated state-change events are source-system occurrences", "that state-aware projection is universally lossless"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.process-mining-overview", "title": "Process Mining: A 360 Degree Overview", "issuer": "Wil M. P. van der Aalst / Process Mining Handbook", "edition_or_date": "2022", "uri": "https://doi.org/10.1007/978-3-031-08848-3_1", "bounded_claims": ["process discovery produces a process model from event data", "hand-authored models may be normative while discovered models are generally descriptive", "conformance checking compares event data with a process model", "event logs are incomplete positive observations rather than exhaustive possible behavior"], "does_not_prove": ["that a discovered model is normative truth", "that high fitness establishes precision or correctness", "one universal process-model formalism"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.object-centric-petri-nets", "title": "Discovering Object-Centric Petri Nets", "issuer": "Wil M. P. van der Aalst and Alessandro Berti", "edition_or_date": "2020", "uri": "https://arxiv.org/abs/2010.02047", "bounded_claims": ["object-centric process discovery maps object-centric event data to a formal object-centric Petri-net model", "places correspond to object types and transitions can consume or produce collections of typed objects"], "does_not_prove": ["that all process models are Petri nets", "that discovery output is normative", "that an event-log projection and a process model share identity"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.rfc9943.scitt-receipts", "title": "RFC 9943: An Architecture for Trustworthy and Transparent Digital Supply Chains", "issuer": "IETF", "edition_or_date": "June 2026", "uri": "https://www.rfc-editor.org/rfc/rfc9943.html", "bounded_claims": ["a SCITT receipt is issued after a transparency service registers a signed statement", "the receipt supports verification of registration in a transparency-service ledger"], "does_not_prove": ["the truth or quality of the registered statement", "a quality-evaluation result", "business acceptance or fitness for use"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.w3c.vc-data-integrity", "title": "Verifiable Credential Data Integrity 1.0", "issuer": "W3C", "edition_or_date": "W3C Recommendation 15 May 2025", "uri": "https://www.w3.org/TR/vc-data-integrity/", "bounded_claims": ["a data-integrity proof binds a proof mechanism, verification parameters and proof value to a constrained digital document", "cryptographic purpose and verification method are explicit inputs to proof processing"], "does_not_prove": ["truth of the secured claims", "fitness or relying-party acceptance", "that cryptographic verification is the same as domain validation"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.intoto.statement-v1", "title": "in-toto Attestation Framework: Statement v1", "issuer": "in-toto Project", "edition_or_date": "v1 specification accessed 2026-08-26", "uri": "https://github.com/in-toto/attestation/blob/main/spec/v1/statement.md", "bounded_claims": ["a statement binds subjects to an identified predicate type and a predicate payload", "predicate type selects the schema and semantics needed to interpret the predicate"], "does_not_prove": ["that the predicate claim is true", "that the signer is authoritative for the relying purpose", "that a predicate-type identifier is itself evidence"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.pywhy.dowhy-effect-inference", "title": "DoWhy Effect Inference", "issuer": "PyWhy Project", "edition_or_date": "documentation accessed 2026-08-26", "uri": "https://www.pywhy.org/dowhy/main/user_guide/causal_tasks/causal_inference/index.html", "bounded_claims": ["causal modeling, identification, estimation and refutation are separate analytical stages", "an identified estimand is an input to estimation rather than an observed estimate", "refutation evaluates robustness of an obtained estimate under a selected method"], "does_not_prove": ["that identification assumptions are true", "that an estimate is a business decision", "that a refutation result supplies causal authority"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.scipy.optimize-result", "title": "SciPy OptimizeResult", "issuer": "SciPy Project", "edition_or_date": "v1.18 documentation accessed 2026-08-26", "uri": "https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.OptimizeResult.html", "bounded_claims": ["an optimization result separates solution, objective value, termination success/status/message, derivatives and evaluation counts", "some diagnostics may be approximate or unavailable depending on the solver"], "does_not_prove": ["global optimality unless the exact solver contract establishes it", "feasibility under unstated business constraints", "business acceptance or authorization"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.rfc9457.problem-details", "title": "RFC 9457: Problem Details for HTTP APIs", "issuer": "IETF", "edition_or_date": "July 2023", "uri": "https://www.rfc-editor.org/rfc/rfc9457.html", "bounded_claims": ["an HTTP problem type identifies interface-level error semantics", "an instance URI may identify one problem occurrence", "extensions can carry structured domain-specific details"], "does_not_prove": ["a protocol-independent domain refusal algebra", "that every negative analytical outcome is an API error", "retryability, compensation or unknown completion without domain rules"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.otel.span-status", "title": "OpenTelemetry Trace API: Span Status", "issuer": "OpenTelemetry Project", "edition_or_date": "stable specification accessed 2026-08-26", "uri": "https://opentelemetry.io/docs/specs/otel/trace/api/#set-status", "bounded_claims": ["span status distinguishes Unset, Error and explicitly validated Ok under telemetry conventions", "instrumentation-specific semantic conventions determine when Error is set"], "does_not_prove": ["domain operation success or quality fitness", "a total domain refusal taxonomy", "that missing status means successful execution"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.odata.operation-effects", "title": "OData Version 4.02 Part 1 and CSDL: Actions and Functions", "issuer": "OASIS Open", "edition_or_date": "OASIS Standard 2024", "uri": "https://docs.oasis-open.org/odata/odata/v4.02/odata-v4.02-part1-protocol.html", "bounded_claims": ["OData functions return data and must have no observable side effects", "OData actions may have observable side effects", "operation identity and binding are scoped by the OData schema"], "does_not_prove": ["that every SAN operation fits the OData action/function split", "transactional atomicity, retry safety or authorization", "that a read has no telemetry, resource or materialization effects"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.graphql.operation-kinds", "title": "GraphQL Specification September 2025: Executing Operations", "issuer": "GraphQL Foundation", "edition_or_date": "September 2025", "uri": "https://spec.graphql.org/September2025/", "bounded_claims": ["GraphQL separates query, mutation and subscription root operations", "mutation root fields execute serially because they are expected to have side effects", "a subscription maps a source stream to a response stream and has a distinct unsubscribe lifecycle"], "does_not_prove": ["database transaction atomicity", "delivery exactly once", "that every operation named query is side-effect free outside GraphQL semantics"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.oasis.wsrm-delivery", "title": "OASIS Web Services Reliable Messaging 1.1: Delivery Assurances", "issuer": "OASIS Open", "edition_or_date": "OASIS Standard 2007", "uri": "https://docs.oasis-open.org/ws-rx/wsrm/200702/wsrm-1.1-spec-os-01.html", "bounded_claims": ["delivery assurances distinguish at-least-once, at-most-once, exactly-once and in-order delivery", "duplicate filtering and retransmission obligations differ across assurances"], "does_not_prove": ["exactly-once business effect", "idempotency of the invoked domain operation", "transactional completion or client knowledge of completion"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.openapi.3-1-1", "title": "OpenAPI Specification 3.1.1", "issuer": "OpenAPI Initiative / Linux Foundation", "edition_or_date": "24 October 2024", "uri": "https://spec.openapis.org/oas/v3.1.1.html", "bounded_claims": ["an OpenAPI Description specifies an HTTP API surface including operations, parameters, request bodies, responses and security requirements", "operation identifiers are unique only within the described API surface", "OpenAPI descriptions can drive documentation, client/server generation and testing"], "does_not_prove": ["business-semantic identity of payload records", "that two provider schemas denote the same aggregate or lifecycle", "implementation correctness, authorization or accepted business effect"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.json-schema.2020-12", "title": "JSON Schema Core and Validation Draft 2020-12", "issuer": "JSON Schema Project", "edition_or_date": "16 June 2022", "uri": "https://json-schema.org/draft/2020-12/json-schema-core", "bounded_claims": ["JSON Schema defines structural validation, annotation and reference mechanisms for JSON data", "validation assertions apply to exact instance locations under a selected dialect and vocabulary"], "does_not_prove": ["domain invariants not encoded in the schema", "semantic equivalence between schemas", "aggregate ownership, lifecycle authority or lossless adapter mapping"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.rfc8949.cbor", "title": "RFC 8949: Concise Binary Object Representation (CBOR)", "issuer": "IETF", "edition_or_date": "December 2020", "uri": "https://www.rfc-editor.org/rfc/rfc8949.html", "bounded_claims": ["well-formed, valid and application-expected CBOR are distinct acceptance layers", "multiple valid encodings can represent the same CBOR data item unless a deterministic encoding profile is selected", "a protocol must define handling for invalid items and unknown semantics"], "does_not_prove": ["domain acceptance from successful generic decoding", "semantic identity from byte identity", "one universal deterministic encoding profile"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.whatwg.encoding", "title": "Encoding Standard", "issuer": "WHATWG", "edition_or_date": "Living Standard; corpus edition 1", "uri": "https://encoding.spec.whatwg.org/", "bounded_claims": ["text decoding is stateful across streamed input and carries an explicit error mode", "replacement and fatal error modes have observably different results", "encoding labels, byte-order marks and incomplete sequences affect interpretation"], "does_not_prove": ["semantic correctness of decoded text", "lossless reconstruction of the source bytes", "one encoding policy for every document or protocol"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.unicode.uax15", "title": "Unicode Standard Annex #15: Unicode Normalization Forms", "issuer": "Unicode Consortium", "edition_or_date": "Unicode 17.0, Revision 57, 30 July 2025", "uri": "https://www.unicode.org/reports/tr15/", "bounded_claims": ["canonical and compatibility equivalence are distinct relations", "NFC, NFD, NFKC and NFKD implement different normalization contracts", "normalization is idempotent under its selected form but higher-level processes still define their own equality"], "does_not_prove": ["business-semantic string equality", "formatting preservation under compatibility normalization", "safe identifier canonicalization without a protocol-specific profile"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.oasis.openformula-1-3", "title": "OpenDocument 1.3 Part 4: Recalculated Formula (OpenFormula) Format", "issuer": "OASIS Open", "edition_or_date": "OASIS Standard 2021", "uri": "https://docs.oasis-open.org/office/OpenDocument/v1.3/OpenDocument-v1.3-part4-formula.html", "bounded_claims": ["OpenFormula defines formula data types, syntax and evaluation semantics", "formula interchange depends on the exact language and function edition", "equivalent results are conditioned on equivalent inputs and specified evaluation behavior"], "does_not_prove": ["semantic equivalence from AST structural equality", "equivalent results across unspecified functions, locale or numeric behavior", "business validity of a syntactically valid formula"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.jcgm.vim3", "title": "JCGM 200:2012 International Vocabulary of Metrology (VIM), 3rd edition", "issuer": "Joint Committee for Guides in Metrology / BIPM", "edition_or_date": "2012 corrected edition", "uri": "https://www.bipm.org/en/doi/10.59161/jcgm200-2012", "bounded_claims": ["a quantity value is a number together with a reference expressing the magnitude of a quantity", "quantities of the same kind have the same dimension but equal dimensions do not imply equal quantity kinds", "a measurement result attributes a set of quantity values and relevant information to a measurand and is generally expressed with measurement uncertainty"], "does_not_prove": ["that every analytical estimate is a metrological measurement result", "validity of a conversion or algebra from dimensional equality alone", "fitness, conformance, truth or action authority from a measured value"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.ucum.2-2", "title": "The Unified Code for Units of Measure", "issuer": "UCUM Organization / Regenstrief Institute", "edition_or_date": "Version 2.2, 17 June 2024", "uri": "https://unitsofmeasure.org/ucum", "bounded_claims": ["unit expressions have distinct equality and commensurability relations", "equal expressions are commensurable but commensurable expressions need not be equal", "interval, logarithmic and other special units use explicit conversion functions and do not participate in ordinary ratio-scale unit algebra"], "does_not_prove": ["quantity-kind equality from unit commensurability", "business comparability from convertible units", "one context-free conversion rule for calendar, currency or other contextual quantities"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.google.mathopt-objective-bounds", "title": "Google MathOpt SolveResult and ObjectiveBounds", "issuer": "Google OR-Tools", "edition_or_date": "Operations Research API documentation accessed 27 August 2026", "uri": "https://developers.google.com/optimization/service/reference/rest/v1/mathopt/solveMathOptModel", "bounded_claims": ["primal and dual bounds make different claims about the optimal objective value", "bound orientation depends on minimization or maximization sense", "optimality gaps, termination reasons, feasibility statuses and solver tolerances qualify any bound claim"], "does_not_prove": ["an incumbent or returned solution from a bound alone", "exact global optimality outside the solver claim and tolerances", "business feasibility or acceptance under unstated constraints"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.mlflow.model-artifact", "title": "MLflow Models", "issuer": "MLflow Project / LF AI & Data", "edition_or_date": "documentation accessed 27 August 2026", "uri": "https://mlflow.org/docs/latest/ml/model/", "bounded_claims": ["a model artifact packages model content with flavors, dependencies, metadata and optional input/output signatures", "model signature, input example, serving payload and logged model version are distinct objects", "loading or serving a packaged artifact is separate from its training and evaluation evidence"], "does_not_prove": ["that a fitted or packaged model is validated, selected, deployed or currently fit", "semantic equivalence of two artifacts or baselines", "one lifecycle and owner for every analytical model kind"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.onnx.ir", "title": "Open Neural Network Exchange Intermediate Representation (ONNX IR) Specification", "issuer": "ONNX Project / LF AI & Data", "edition_or_date": "ONNX 1.23.0 documentation accessed 27 August 2026", "uri": "https://onnx.ai/onnx/repo-docs/IR.html", "bounded_claims": ["ModelProto is a top-level portable serialized model container associating metadata with an executable graph", "IR version, imported operator sets, graph, functions and metadata jointly constrain interpretation and executability", "model validation checks conformance to the ONNX representation and operator contracts"], "does_not_prove": ["training provenance, evaluation quality, selection, approval or deployment state", "semantic equivalence of models with different graphs, weights or operator editions", "deterministic predictions across unspecified runtimes, kernels or numeric environments"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.sktime.base-forecaster", "title": "sktime BaseForecaster interface", "issuer": "sktime Project", "edition_or_date": "main branch documentation accessed 27 August 2026", "uri": "https://github.com/sktime/sktime/blob/main/sktime/forecasting/base/_base.py", "bounded_claims": ["forecaster states distinguish new, fitted and optionally pretrained", "fit changes state to fitted, records a cutoff and writes fitted model attributes", "predict requires fitted state and consumes a forecasting horizon and compatible exogenous inputs"], "does_not_prove": ["that fitted means evaluated, selected, approved, deployed or fit for a relying purpose", "serialization or portability of an in-memory fitted forecaster", "forecast truth or operational action authority"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.nist.process-monitoring-baseline", "title": "NIST/SEMATECH e-Handbook: What are Process Control Techniques?", "issuer": "National Institute of Standards and Technology", "edition_or_date": "e-Handbook section 6.1.2 accessed 27 August 2026", "uri": "https://www.itl.nist.gov/div898/handbook/pmc/section1/pmc12.htm", "bounded_claims": ["historical observations are used in Phase I to estimate an initial population model and control limits", "observations outside limits are investigated and the baseline limits may be recomputed", "Phase II monitoring compares new observations against limits established at the end of Phase I"], "does_not_prove": ["that every analytical baseline is a control chart", "that an observation outside a baseline is an anomaly cause or authorized action", "one update, validity or retirement policy for every baseline artifact"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.rfc3339.timestamp", "title": "RFC 3339: Date and Time on the Internet: Timestamps", "issuer": "IETF", "edition_or_date": "July 2002", "uri": "https://www.rfc-editor.org/rfc/rfc3339.html", "bounded_claims": ["an Internet timestamp is an unambiguous representation of an instant with a stated UTC relationship", "unknown local offset is semantically distinct from UTC as the preferred reference point", "leap seconds and local-offset rules affect parsing and ordering"], "does_not_prove": ["event occurrence from timestamp syntax", "clock accuracy, synchronization or source authority", "calendar scheduling semantics or one universal temporal equality relation"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.w3c.owl-time", "title": "Time Ontology in OWL", "issuer": "W3C / OGC", "edition_or_date": "W3C Recommendation 19 October 2017 with 2022 draft updates", "uri": "https://www.w3.org/TR/owl-time/", "bounded_claims": ["instants, intervals, durations, temporal positions and interval relations are distinct concepts", "temporal positions and durations require an explicit temporal reference system", "calendar-clock, coordinate and ordinal time systems need not share one representation"], "does_not_prove": ["clock accuracy or occurrence truth", "one business lifecycle or due-date policy", "forecast-origin, event-time or retention authority from generic temporal relations"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.hyndman.fpp3", "title": "Forecasting: Principles and Practice, 3rd edition", "issuer": "Rob J. Hyndman and George Athanasopoulos / OTexts", "edition_or_date": "online edition updated 9 March 2026", "uri": "https://otexts.com/fpp3/", "bounded_claims": ["time-series forecasts estimate continuation beyond an available observation history", "rolling-origin evaluation changes the origin at which a forecast is based", "forecast accuracy must be evaluated on temporally separated training and test cuts"], "does_not_prove": ["one horizon representation for every irregular or calendar-indexed series", "that origin equals the final observed event time", "model fitness, forecast truth or operational action authority"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.nara.disposition-instructions", "title": "Preparing Disposition Instructions", "issuer": "U.S. National Archives and Records Administration", "edition_or_date": "guidance accessed 27 August 2026", "uri": "https://www.archives.gov/records-mgmt/scheduling/instructions", "bounded_claims": ["a disposition instruction separates cutoff, retention period and final action", "retention may run from creation/cutoff or from a named future event", "eligibility after a retention period remains conditioned on disposition authority and clear instructions"], "does_not_prove": ["that a computed due time authorizes destruction or transfer", "absence of a hold or competing authority", "completed disposition from eligibility or provider request"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.flink.changelog-retraction", "title": "Apache Flink Process Table Functions: Changelog and Retract Semantics", "issuer": "Apache Flink", "edition_or_date": "stable documentation accessed 27 August 2026", "uri": "https://nightlies.apache.org/flink/flink-docs-stable/docs/dev/table/functions/ptfs/", "bounded_claims": ["updating tables encode insert, update-before, update-after and delete changes", "a retract update withdraws the previous row value before adding a replacement", "retract and upsert encodings have different key and downstream requirements"], "does_not_prove": ["withdrawal of reliance on a governed record or claim", "physical deletion from a negative materialization update", "business authority, correction, supersession or recall semantics"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.ro-crate-1-2", "title": "RO-Crate Metadata Specification 1.2", "issuer": "Research Object Crate community", "edition_or_date": "Version 1.2", "uri": "https://www.researchobject.org/ro-crate/specification/1.2/", "bounded_claims": ["an RO-Crate metadata document distinguishes its descriptor, root data entity, data entities and contextual entities", "the graph may describe zero or more data and contextual entities and does not imply that every root file is a data entity", "entity identity and inclusion are expressed under the RO-Crate JSON-LD profile"], "does_not_prove": ["that a research-object manifest is a storage snapshot manifest", "complete current inventory of every external resource", "truth of descriptive metadata"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.iiif.presentation-3", "title": "IIIF Presentation API 3.0", "issuer": "IIIF Consortium", "edition_or_date": "Version 3.0.0", "uri": "https://iiif.io/api/presentation/3.0/", "bounded_claims": ["a Manifest, Canvas, Annotation Page, Annotation and content resource have distinct presentation roles", "a Canvas represents a view and content is associated through annotations with explicit motivations", "OCR transcription is modeled as derived supplementing content rather than the painted source content"], "does_not_prove": ["that rendered or OCR-derived text is observed source truth", "document identity from a presentation view", "lossless round-trip from a derived view to source bytes"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.rfc9113.http2-frames", "title": "RFC 9113: HTTP/2", "issuer": "IETF", "edition_or_date": "June 2022", "uri": "https://www.rfc-editor.org/rfc/rfc9113.html", "bounded_claims": ["an HTTP/2 frame is a profile-specific header and payload unit whose type determines payload semantics", "frame size, stream association, flags and unknown-type handling are protocol rules", "a frame can affect connection or stream state depending on its type and identifier"], "does_not_prove": ["one universal frame carrier across protocols", "business-message or event identity", "semantic acceptance from successful frame decoding"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.kubernetes.resource-management", "title": "Kubernetes Resource Management for Pods and Containers", "issuer": "Kubernetes Project / CNCF", "edition_or_date": "documentation at corpus edition 1", "uri": "https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/", "bounded_claims": ["resource request, scheduling capacity, runtime limit and observed usage are distinct", "resource kinds have typed quantities and different enforcement behavior", "a scheduler uses requests for placement while runtime and kernel mechanisms enforce limits"], "does_not_prove": ["that a request is a committed reservation", "identical enforcement for CPU memory storage and extended resources", "successful placement, continued availability or completed work"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.linux.cgroup-v2", "title": "Control Group v2", "issuer": "Linux kernel project", "edition_or_date": "kernel documentation at corpus edition 1", "uri": "https://docs.kernel.org/admin-guide/cgroup-v2.html", "bounded_claims": ["weight, hard protection, best-effort protection, throttle and hard maximum are different resource-control relations", "memory use is stateful and limits can be enforced through reclaim throttling refusal or OOM termination", "a configured maximum can be temporarily exceeded or observed asynchronously under documented conditions"], "does_not_prove": ["one scalar resource budget across resource kinds", "instantaneous or perfectly precise enforcement", "business-level reservation, fairness or successful completion"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.slurm.reservations", "title": "Slurm Advanced Resource Reservation Guide", "issuer": "SchedMD", "edition_or_date": "documentation at corpus edition 1", "uri": "https://slurm.schedmd.com/reservations.html", "bounded_claims": ["a reservation binds named resources, a time interval and authorized users or accounts", "reservation creation, update, deletion, activation and job use are distinct lifecycle events", "resources such as nodes cores licenses and burst buffers have qualified reservation semantics"], "does_not_prove": ["allocation or execution from reservation existence", "one reservation protocol for memory allocators or analytical budgets", "completed release or reclaimed capacity from a deletion request"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.arrow.columnar-buffers", "title": "Apache Arrow Columnar Format", "issuer": "Apache Arrow", "edition_or_date": "format documentation at corpus edition 1", "uri": "https://arrow.apache.org/docs/format/Columnar.html", "bounded_claims": ["columnar arrays use typed physical buffers such as validity offsets type identifiers and data", "buffer count order alignment length and interpretation depend on the logical type and format profile", "a physical buffer is part of a representation layout rather than a queueing-capacity policy"], "does_not_prove": ["queue capacity or overflow behavior", "ownership or lifetime of every implementation allocation", "semantic equality from equal byte regions"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.rabbitmq.queue-limits", "title": "RabbitMQ Queue Length Limit", "issuer": "Broadcom RabbitMQ", "edition_or_date": "documentation at corpus edition 1", "uri": "https://www.rabbitmq.com/docs/maxlength", "bounded_claims": ["queue capacity can be bounded by ready-message count bytes or both", "effective limits depend on declaration and policy precedence", "overflow can discard existing items, reject new publications or dead-letter under an explicit policy"], "does_not_prove": ["physical memory-buffer layout", "losslessness or delivery from accepted enqueue", "one universal queue-capacity or overflow model"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.parquet.page-index", "title": "Apache Parquet Page Index", "issuer": "Apache Parquet", "edition_or_date": "format documentation at corpus edition 1", "uri": "https://parquet.apache.org/docs/file-format/pageindex/", "bounded_claims": ["Parquet pages are column-chunk subdivisions addressed by offset and column indexes", "page minimum and maximum statistics are typed by column order and may be truncated conservative bounds", "page indexes support pruning and navigation rather than document presentation"], "does_not_prove": ["document-page identity or layout", "exact observed minimum and maximum from every stored bound", "predicate truth or row-level match without reader evaluation"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.rfc7946.geojson", "title": "RFC 7946: The GeoJSON Format", "issuer": "IETF", "edition_or_date": "August 2016", "uri": "https://www.rfc-editor.org/rfc/rfc7946.html", "bounded_claims": ["GeoJSON distinguishes Geometry, Feature and FeatureCollection objects", "GeoJSON positions use longitude then latitude in OGC CRS84 and optional height has a separately stated unit", "coordinate digit count does not establish measurement precision or uncertainty"], "does_not_prove": ["that a geometry is a domain feature or entity", "topological or business validity from syntactic validity", "semantic equality from equal JSON bytes or coordinate arrays"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.ogc.sfa-1-2-1", "title": "Simple Feature Access Part 1: Common Architecture", "issuer": "Open Geospatial Consortium", "edition_or_date": "Version 1.2.1, OGC 06-103r4, 28 May 2011", "uri": "https://www.ogc.org/standards/sfa/", "bounded_claims": ["the Simple Features model defines a geometry class hierarchy including points curves surfaces and collections", "each geometry is associated with a spatial reference system describing its coordinate space", "spatial predicates and geometric validity are defined under the selected geometry model"], "does_not_prove": ["feature or business-object identity from geometry", "one representation or precision policy for all spatial applications", "domain validity or fitness from geometric validity"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.nist.randomized-block-design", "title": "NIST/SEMATECH e-Handbook: Randomized Block Designs", "issuer": "National Institute of Standards and Technology", "edition_or_date": "handbook section 5.3.3.2, accessed 27 August 2026", "uri": "https://www.itl.nist.gov/div898/handbook/pri/section3/pri332.htm", "bounded_claims": ["experimental blocking groups trials so controlled nuisance factors are held constant while the factor of interest varies", "a blocking factor and treatment factor play different analytical roles", "randomized block analysis conditions treatment comparisons on the block design"], "does_not_prove": ["document-layout membership or geometric containment", "that a block is a physical storage subdivision", "valid randomization or balance without the exact design and assignment evidence"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.loc.alto-4-4", "title": "ALTO: Technical Metadata for Layout and Text Objects", "issuer": "Library of Congress / ALTO Editorial Board", "edition_or_date": "Schema version 4.4, 7 April 2023", "uri": "https://www.loc.gov/standards/alto/", "bounded_claims": ["ALTO describes layout and text metadata for physical text resources such as book and newspaper pages", "Page, print space, block, text line, string, reading order and processing references are distinct layout roles", "layout objects can carry coordinates, dimensions, styles, language, direction and processing provenance"], "does_not_prove": ["that an inferred block or region is source-semantic truth", "physical data-layout or access-path semantics", "one shared block or region identity across layout engines and document editions"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.kernighan-lin.graph-partition", "title": "An Efficient Heuristic Procedure for Partitioning Graphs", "issuer": "B. W. Kernighan and S. Lin", "edition_or_date": "Bell System Technical Journal 49(2), February 1970", "uri": "https://doi.org/10.1002/j.1538-7305.1970.tb01770.x", "bounded_claims": ["the studied graph-partition problem assigns graph nodes to subsets under subset-size constraints", "its objective minimizes the sum of costs on edges cut by the partition", "the proposed procedure is a heuristic and therefore its output is not an optimality proof"], "does_not_prove": ["runtime routing or data-placement semantics", "one graph-partition objective for every method", "optimality or stability of every returned partition"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.substrait.distribution", "title": "Substrait Relation Properties: Distribution", "issuer": "Substrait project", "edition_or_date": "specification accessed 27 August 2026", "uri": "https://substrait.io/relations/basics/#distribution", "bounded_claims": ["distribution describes properties of sibling data partitions in a relational plan", "distribution binds field references and a distribution type", "distribution and orderedness are separate relation properties"], "does_not_prove": ["graph-cut membership or objective value", "materialized placement or completed network exchange", "one runtime partitioner algorithm or fault-tolerance policy"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.libpysal.spatial-weights", "title": "libpysal Graph: Spatial Weights Graph", "issuer": "PySAL project", "edition_or_date": "stable project documentation accessed 27 August 2026", "uri": "https://pysal.org/libpysal/stable/generated/libpysal.graph.Graph.html", "bounded_claims": ["a spatial-weights graph binds focal and neighbor observation identifiers to weight values", "original binary and row-standardized transformations are distinct weight representations", "isolates, asymmetry, symmetrization and graph operations require explicit handling"], "does_not_prove": ["that geometry adjacency determines the only valid spatial weights", "that transformed weights are equal to original weights", "statistical validity or causal meaning for a downstream model"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.peppol.billing-3", "title": "Peppol BIS Billing 3.0", "issuer": "OpenPeppol", "edition_or_date": "May 2026 release", "uri": "https://docs.peppol.eu/poacc/billing/3.0/", "bounded_claims": ["the invoice profile binds EN 16931 concepts to UBL syntax, code lists and Peppol business rules", "invoice conformance depends on the exact profile and rule edition rather than a generic invoice-shaped object"], "does_not_prove": ["a universal invoice aggregate", "equivalence with Stripe or internal invoice records", "payment, settlement, tax acceptance or accounting finality"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.rfc7696.crypto-agility", "title": "RFC 7696: Guidelines for Cryptographic Algorithm Agility", "issuer": "IETF", "edition_or_date": "November 2015", "uri": "https://www.rfc-editor.org/rfc/rfc7696.html", "bounded_claims": ["protocols using cryptography need explicit algorithm or suite identifiers and migration capability", "mandatory-to-implement and currently selected algorithms are different concepts", "deprecated identifiers should remain stable rather than silently changing meaning"], "does_not_prove": ["that an algorithm suite is authorized for a deployment", "security strength for a purpose and time", "key validity or cryptoperiod"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.nist.sp800-57p1r5", "title": "NIST SP 800-57 Part 1 Revision 5: Recommendation for Key Management", "issuer": "NIST", "edition_or_date": "May 2020", "uri": "https://csrc.nist.gov/pubs/sp/800/57/pt1/r5/final", "bounded_claims": ["cryptographic key management distinguishes key types, purposes, protection requirements and usage periods", "cryptoperiod decisions depend on key use, security service, environment and risk"], "does_not_prove": ["one universal cryptoperiod", "algorithm-suite interoperability", "that an unexpired key remains uncompromised or authorized"]},
    {"record_kind": "bounded_primary_source", "source_id": "source.p1.otel.log-event-model", "title": "OpenTelemetry Logs Data Model and Event Semantic Conventions", "issuer": "OpenTelemetry Project", "edition_or_date": "specification accessed 2026-08-26", "uri": "https://opentelemetry.io/docs/specs/otel/logs/data-model/", "bounded_claims": ["a log record records an event and separates event timestamp from observed timestamp", "an event name identifies an event class or structure within the telemetry model", "resource, instrumentation scope, trace context, severity, body and attributes remain distinct fields"], "does_not_prove": ["that a recorded action occurred as claimed", "business authority, intent or accepted effect", "audit completeness, tamper resistance or legal admissibility"]},
]


def high_fanout_research(symbols: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_symbol = {row["symbol_ref"]: row for row in symbols}
    specs = [
        {"symbol_ref": "type.protocoledition", "disposition_hypothesis": "SCOPED_EDITION_REFERENCE_CANDIDATE", "source_refs": ["source.p1.rfc9110.protocol-version"], "finding": "Protocol edition must be scoped by protocol authority/name and specification set; its token is not globally ordinal and does not by itself prove compatibility.", "twins": ["HTTP/1.1 and HTTP/2 share core semantics while differing in wire expression.", "An intermediary can communicate with a different HTTP version than an upstream hop."], "carrier_fields": ["ProtocolAuthorityRef", "ProtocolName", "EditionToken", "SpecificationSetDigest"], "non_collapse_laws": ["edition token is not compatibility", "protocol edition is not semantic edition", "equal tokens under different authorities are not equal editions"]},
        {"symbol_ref": "type.contentdigest", "disposition_hypothesis": "SCOPED_DIGEST_EVIDENCE_CANDIDATE", "source_refs": ["source.p1.rfc9530.digest-fields"], "finding": "A digest must bind algorithm, byte/representation scope and transformation context. Content digest, representation digest, artifact identity and semantic identity are distinct.", "twins": ["Identical resource meaning can have different content digests after content encoding.", "A matching digest proves integrity relative to bytes and algorithm, not authenticity, authorization or truth."], "carrier_fields": ["DigestAlgorithmRef", "DigestBytes", "DigestScope", "RepresentationMetadataRef"], "non_collapse_laws": ["digest equality is not semantic equality", "integrity is not authenticity", "content digest is not representation digest"]},
        {"symbol_ref": "type.compatibility", "disposition_hypothesis": "PROFILED_DIRECTIONAL_RELATION_CANDIDATE", "source_refs": ["source.p1.protobuf.proto3-evolution", "source.p1.avro.schema-resolution", "source.p1.iceberg.evolution", "source.p1.cargo.semver"], "finding": "Compatibility is a directional, profile-scoped relation over exact subjects and consumer roles; it must not be a context-free boolean or unqualified global value.", "twins": ["A Protobuf change can be binary-wire safe but JSON unsafe.", "An Avro reader/writer pair can resolve in one direction but not the reverse.", "An Iceberg field evolution can preserve data reading while changing business meaning.", "A Rust API can keep compiling while runtime behavior changes."], "carrier_fields": ["CompatibilityProfileRef", "FromEditionRef", "ToEditionRef", "ConsumerRole", "DimensionSet", "AssessmentEvidence"], "non_collapse_laws": ["forward compatibility is not backward compatibility", "wire compatibility is not semantic compatibility", "source compatibility is not behavioral compatibility"]},
        {"symbol_ref": "type.lease", "disposition_hypothesis": "QUALIFIED_LEASE_PROFILES_OVER_TEMPORAL_GRANT_CONCEPT", "source_refs": ["source.p1.etcd.lease-api", "source.p1.vault.lease-semantics", "source.p1.vault.lease-api", "source.p1.chubby.lock-service"], "finding": "The unqualified Lease symbol must not be unified. Coordination liveness leases and secret-validity leases may refine a shared temporal-grant concept, but they have different subjects, expiry consequences, authority, renewal receipts and safety laws; fencing is a coordination-only refinement.", "twins": ["A requested TTL is not the server-granted TTL.", "Renewable is not renewed.", "Lease expiry is not observed downstream cleanup.", "A secret-validity lease is not a lock or leadership lease.", "Lock ownership is not effect fencing, and a stale holder can require a separate fencing token."], "carrier_fields": ["LeaseProfileRef", "LeaseId", "IssuerAuthorityRef", "SubjectRef", "GrantScope", "IssuedAt", "ExpiresAtOrTtl", "Renewability", "LifecycleStatus", "LifecycleEvidence"], "non_collapse_laws": ["lease request is not granted lease", "expiry is not revocation completion", "renewal request is not renewal receipt", "secret lease is not coordination lease", "lease validity is not effect authorization", "fencing token is not a universal lease field"], "local_refinements": ["CoordinationLease adds liveness attachment, keepalive policy, expiry consequences and optional monotonically ordered fencing evidence.", "SecretLease adds credential/version subject, validity promise, renewal/revocation authority and downstream cleanup evidence."]},
        {"symbol_ref": "type.cancellationrequest", "disposition_hypothesis": "SHARED_CANCELLATION_INTENT_WITH_PROFILED_RECEIPT_AND_OUTCOME_CANDIDATE", "source_refs": ["source.p1.grpc.cancellation"], "finding": "A reusable cancellation intent can name who asks to stop which occurrence, when and with what propagation scope, but notification, acceptance, propagation, cleanup and observed terminal outcome remain distinct and execution-profile-specific.", "twins": ["Caller discontinuation of interest is not proof that work stopped.", "Handler notification is not handler cooperation.", "Local cancellation is not transitive upstream cancellation.", "A terminal result racing with cancellation is not necessarily a cancelled result.", "Cancellation does not compensate already committed effects."], "carrier_fields": ["CancellationRequestId", "TargetOccurrenceRef", "IssuerAuthorityRef", "RequestedAt", "ReasonOrCause", "PropagationScope", "IdempotencyKey"], "non_collapse_laws": ["request is not receipt", "receipt is not cessation", "cessation is not compensation", "deadline expiry is a cancellation cause, not the cancellation request", "cancellation status is occurrence-scoped"], "local_refinements": ["Runtime defines propagation, cooperative polling, deadline interaction and receipt states.", "Optimization and simulation execution define safe points, incumbent or partial-result disposition, solver/provider interruption and deterministic replay consequences."]},
        {"symbol_ref": "type.lossreport", "disposition_hypothesis": "PROFILED_TRANSFORMATION_LOSS_ASSESSMENT_CANDIDATE", "source_refs": ["source.p1.w3c.prov-dm", "source.p1.w3c.prov-constraints", "source.p1.rfc9110.transforming-proxies", "source.p1.arrow.cast-options"], "finding": "Loss is not an intrinsic scalar property of an output. A reusable assessment envelope must bind the exact transformation, source and target editions, protected observables, loss dimensions, witnesses and assessor authority; audit adaptation, PROV interchange and table-format translation remain separate profiles.", "twins": ["A valid PROV document is not necessarily truthful or lossless relative to its source.", "A derivation relation does not state which fields or semantics were lost.", "Absence in a target representation is not deletion without a source-model and mapping cut.", "A cast safe for integer range can still truncate temporal or decimal precision.", "A semantically significant transformation can be acceptable under one consumer profile and forbidden under another."], "carrier_fields": ["TransformationOccurrenceRef", "SourceArtifactEditionRef", "TargetArtifactEditionRef", "MappingProfileRef", "ProtectedObservableProfileRef", "LossDimensionAssessments", "UnknownOrUnassessedDimensions", "ReversibilityAssessment", "EvidenceRefs", "AssessorAuthorityRef"], "non_collapse_laws": ["transformation is not loss", "provenance validity is not losslessness", "missing output feature is not proven information loss", "loss dimension is not total loss score", "technical loss assessment is not acceptance authority"], "local_refinements": ["AuditLogLossProfile covers event identity, ordering, actor/action/resource semantics, evidence chain and redaction.", "ProvInterchangeLossProfile covers PROV statements, identifiers, bundles, namespaces, constraints and extension terms.", "TableFormatTranslationLossProfile covers schema IDs, partition/sort semantics, snapshots, deletes, statistics, properties and feature correspondence."]},
        {"symbol_ref": "trait.capabilityrequirement", "disposition_hypothesis": "SHARED_CAPABILITY_REQUIREMENT_PORT_CANDIDATE", "source_refs": ["source.p1.tosca.requirements-capabilities", "source.p1.wasm-component.wit"], "finding": "A capability requirement is a consumer-owned, editioned predicate over a semantic contract, profile, cardinality and constraints. It is distinct from a structural import and must not name a provider implementation as part of its meaning.", "twins": ["A WIT import declares a structural dependency but does not prove semantic fitness.", "An optional requirement is not a silently weakened mandatory requirement.", "A type-compatible target can still violate bounds, behavior or evidence thresholds.", "A feature flag is not a capability requirement."], "carrier_fields": ["RequirementId", "ConsumerContextRef", "SemanticContractRef", "ProfileEditionRef", "ConstraintSet", "Cardinality", "MandatoryOrOptional", "EvidenceThreshold"], "non_collapse_laws": ["requirement is not provider selection", "requirement is not structural import", "optional is not absent", "constraint satisfaction is profile-scoped"]},
        {"symbol_ref": "trait.capabilityoffer", "disposition_hypothesis": "SHARED_CAPABILITY_OFFER_PORT_CANDIDATE", "source_refs": ["source.p1.tosca.requirements-capabilities", "source.p1.wasm-component.wit"], "finding": "A capability offer is a provider assertion about an exact implementation artifact and semantic/profile editions, with dimensions, bounds, targets and evidence. It is distinct from an export, a matched binding, a conformance result and qualification.", "twins": ["A WIT export exposes an interface but does not prove its behavioral semantics.", "An offer matching a capability type can fail a consumer constraint.", "Provider self-assertion is not independent qualification.", "An expired or invalidated evidence bundle cannot support a current offer."], "carrier_fields": ["OfferId", "ProviderRef", "ImplementationArtifactDigest", "SemanticContractRef", "ProfileEditionRef", "OfferedDimensions", "ResourceAndBehaviorBounds", "TargetAndFeatureSet", "EvidenceRefs", "ValidityWindow"], "non_collapse_laws": ["offer is not implementation identity alone", "offer is not export", "offer is not binding", "offer assertion is not qualification", "provider identity does not redefine contract meaning"]},
        {"symbol_ref": "trait.conformanceoracle", "disposition_hypothesis": "SHARED_SCOPED_CONFORMANCE_ORACLE_PORT_CANDIDATE", "source_refs": ["source.p1.nist.conformance-testing", "source.p1.w3c.act-rules"], "finding": "A conformance oracle evaluates a named test subject against an exact specification/profile edition using versioned applicability, cases and expected outcomes. Its result is scoped evidence; certification, qualification, interoperability and fitness decisions remain separate.", "twins": ["Passing every available test does not prove conformance in untested areas.", "Inapplicable is not passed, and cannot-tell is not failed.", "A reference implementation is not automatically the semantic specification.", "Conformance does not imply performance, security, interoperability or business fitness unless those requirements are in scope."], "carrier_fields": ["OracleId", "OracleEditionRef", "SpecificationOrProfileRef", "ApplicabilityDefinition", "TestSubjectRef", "CaseCorpusDigest", "ExpectedOutcomeMap", "CoverageClaim", "ExecutionEnvironmentRef", "OracleResultEvidence"], "non_collapse_laws": ["oracle is not specification owner", "test execution is not certification", "pass is not proof of exhaustive conformance", "inapplicable is not pass", "unknown and untested remain explicit"]},
        {"symbol_ref": "type.assignmentcut", "disposition_hypothesis": "SHARED_EXPERIMENT_ASSIGNMENT_CUT_CANDIDATE", "source_refs": ["source.p1.consort.2025", "source.p1.microsoft.trustworthy-analysis"], "finding": "An assignment cut is a versioned experiment-analysis boundary over eligible subjects, randomization units, realized allocations and assignment time/data scope. It preserves the assignment mechanism needed by the estimand and variance model; it is neither an exposure cut nor an analysis-population shortcut.", "twins": ["Eligibility is not realized assignment.", "A random allocation sequence is not the set of assignments that actually occurred.", "Assignment to a variant is not receipt of or exposure to that variant.", "The randomization unit is not necessarily the metric observation or analysis unit.", "Excluding assigned subjects after observing outcomes can destroy the protection supplied by randomization."], "carrier_fields": ["AssignmentCutId", "ExperimentRef", "ProtocolEditionRef", "EligibilityDefinitionRef", "RandomizationUnitDefinitionRef", "AssignmentMechanismRef", "VariantAllocationRef", "AssignmentOccurrencePredicate", "AssignmentTimeInterval", "DataSnapshotOrWatermarkRef", "IntegrityEvidenceRefs"], "non_collapse_laws": ["eligibility is not assignment", "allocation sequence is not realized assignment", "assignment is not exposure", "assignment population is not analysis population", "randomization unit is not observation unit", "cut availability is not cut validity"]},
        {"symbol_ref": "type.exposurecut", "disposition_hypothesis": "SHARED_EXPERIMENT_EXPOSURE_CUT_CANDIDATE", "source_refs": ["source.p1.consort.2025", "source.p1.microsoft.triggered-analysis", "source.p1.deng-hu.trigger-dilution"], "finding": "An exposure cut is a versioned experiment-analysis boundary over the treatment-relevant trigger or delivered intervention, including its counterfactual definition for comparison arms, exposure unit, first-exposure rule, event/time scope and evidence. Exposure-based restriction is valid only under an explicit design and assumptions; it cannot be inferred from assignment or telemetry presence.", "twins": ["Assignment to treatment is not actual exposure.", "Observed treatment triggering is not the unobserved control counterfactual.", "Filtering both arms by a treatment-affected post-assignment event can introduce selection bias.", "First exposure time is not assignment time.", "A triggered effect is not the all-population effect without a valid translation.", "A logged event is not proof of complete exposure capture."], "carrier_fields": ["ExposureCutId", "ExperimentRef", "ExposureDefinitionEditionRef", "ExposureUnitDefinitionRef", "CounterfactualTriggerRuleRef", "FirstExposureRule", "IncludedExposureOccurrencePredicate", "ExposureTimeInterval", "ObservationWindow", "DataSnapshotOrWatermarkRef", "IntegrityEvidenceRefs"], "non_collapse_laws": ["assignment is not exposure", "actual exposure is not counterfactual exposure", "telemetry presence is not exposure truth", "first exposure time is not assignment time", "triggered population effect is not all-population effect", "exposure restriction is not valid by default"]},
        {"symbol_ref": "type.metriccut", "disposition_hypothesis": "SHARED_EXPERIMENT_METRIC_OBSERVATION_CUT_CANDIDATE", "source_refs": ["source.p1.consort.2025", "source.p1.consort.outcome-item", "source.p1.microsoft.dirty-dozen", "source.p1.consort.interim-item", "source.p1.johari.always-valid", "source.p1.fda.adaptive-design"], "finding": "A metric cut is a versioned experiment-analysis boundary that binds the metric definition and role to its population, observation unit, source-event and time scope, participant-level analysis value, group aggregation, missingness/censoring policy and exact data cut. It does not by itself define an estimand, validate telemetry, authorize an interim look or decide that an experiment should stop.", "twins": ["A measurement variable is not the participant-level analysis metric or group aggregation.", "The assignment unit is not necessarily the observation or analysis unit.", "A primary, guardrail or diagnostic role is not the metric formula.", "Available telemetry is not complete telemetry.", "Statistical significance is not business importance.", "A repeated look under fixed-horizon inference is not valid merely because the data cut is reproducible.", "Crossing a stopping boundary is not the authority act that stops an experiment."], "carrier_fields": ["MetricCutId", "ExperimentRef", "MetricDefinitionEditionRef", "MetricRole", "AnalysisPopulationRef", "ObservationUnitDefinitionRef", "SourceSignalAndEventPredicate", "ParticipantLevelAnalysisMetric", "GroupAggregation", "MeasurementTimePointOrWindow", "MissingnessAndCensoringPolicyRef", "DataSnapshotOrWatermarkRef", "QualityEvidenceRefs"], "non_collapse_laws": ["measurement variable is not analysis metric", "analysis metric is not group aggregation", "metric definition is not metric observation", "availability is not completeness", "metric role is not metric algebra", "data cut is not interim-look authority", "stopping eligibility is not stop authorization"]},
        {"symbol_ref": "type.evaluationscope", "disposition_hypothesis": "QUALITY_RECONCILIATION_FAMILY_SCOPE_CARRIER_WITH_LOCAL_PROFILES_CANDIDATE", "source_refs": ["source.p1.w3c.dqv", "source.p1.w3c.shacl", "source.p1.oasis.xacml-3", "source.p1.w3c.odrl-model"], "finding": "A quality/reconciliation evaluation scope is an immutable, editioned selection contract binding the exact subject kind and subject version, inclusion predicate or target, grain, data and temporal cut, rule/metric/policy editions, excluded and unknown coverage, and evaluation environment. It says what an evaluation may support; it is not a result, population claim, authority scope or permission to mutate the subject.", "twins": ["A SHACL target selects focus nodes; nodes outside the target did not pass.", "The dataset containing quality observations is not necessarily the resource computed on.", "A sampled scope is not a population-wide claim without an inference contract.", "A resource identifier without a snapshot or watermark does not freeze the evaluated state.", "Policy applicability is not policy satisfaction or effect authorization.", "An empty result set is not complete coverage without an explicit closed-world frame."], "carrier_fields": ["EvaluationScopeId", "ScopeProfileRef", "SubjectKind", "SubjectEditionOrSnapshotRef", "SelectionPredicateOrTargetRef", "EvaluationGrain", "DataSnapshotOrWatermarkRef", "ValidTimeInterval", "RecordingTimeCut", "PolicyRuleMetricEditionRefs", "IncludedDimensions", "ExplicitExclusions", "UnknownOrUncoveredPolicy", "SamplingFrameAndInferenceRef", "EvaluationEnvironmentRef"], "non_collapse_laws": ["scope is not result", "target is not conformance", "resource identity is not resource snapshot", "sample scope is not population claim", "unknown coverage is not pass", "evaluation scope is not authorization scope", "scope inclusion is not mutation authority"]},
        {"symbol_ref": "type.policyedition", "disposition_hypothesis": "QUALITY_RECONCILIATION_FAMILY_POLICY_EDITION_WITH_LOCAL_PROFILES_CANDIDATE", "source_refs": ["source.p1.oasis.xacml-3", "source.p1.w3c.odrl-model", "source.p1.opa.bundles", "source.p1.opa.decision-logs"], "finding": "A quality/reconciliation policy edition is an immutable semantic snapshot under a named policy authority and profile, binding exact rules, dependencies, targets/applicability, precedence or combining semantics, defaults, effective interval and content evidence. A version token, deployment bundle revision, activation state and evaluation decision remain separate.", "twins": ["Equal version tokens under different policy authorities do not identify the same policy edition.", "A later version is not necessarily backward-compatible or semantically stronger.", "An OPA bundle revision can change policy and data and is not itself a semantic policy edition.", "A downloaded bundle is not an activated bundle.", "A policy found applicable is not proof that its constraints are satisfied.", "A policy decision log is not proof that the decision was enforced.", "Published, effective, active and retired are distinct lifecycle states."], "carrier_fields": ["PolicyEditionId", "PolicyAuthorityRef", "PolicyIdentityRef", "PolicyProfileEditionRef", "SemanticVersionToken", "CanonicalPolicyContentDigest", "RuleAndDependencyEditionRefs", "TargetOrApplicabilityContract", "ConflictCombiningAndPrecedenceSemantics", "ExplicitDefaults", "IssuedAt", "EffectiveInterval", "LifecycleStatus", "SupersedesOrAmendsRefs", "CompatibilityAndEvidenceInvalidationClaims"], "non_collapse_laws": ["policy identity is authority-scoped", "version token is not compatibility", "policy edition is not deployment bundle revision", "publication is not effectiveness", "download is not activation", "applicability is not satisfaction", "decision is not enforcement", "policy content is not policy authority"]},
        {"symbol_ref": "type.graphview", "disposition_hypothesis": "ANALYTICAL_GRAPH_FAMILY_TYPED_PROJECTION_CARRIER_CANDIDATE", "source_refs": ["source.p1.fahland.event-knowledge-graphs", "source.p1.ocel-to-tekg"], "finding": "A graph view is an immutable, scoped projection over an exact source graph edition. It binds node and edge selection, identity domains, types, direction, multiplicity, properties, weights, temporal cut, missing or unknown treatment and projection provenance. It is neither the source graph, a storage encoding, a path/result, an event log, nor a process model.", "twins": ["Two graph views over the same source can have different node or edge universes.", "A temporal event knowledge graph is not every graph used by an analytical method.", "Reachability is not causality.", "A weight property has no algorithmic meaning without a named profile.", "An induced subgraph and an edge-filtered projection can contain the same nodes but different semantics."], "carrier_fields": ["GraphViewId", "SourceGraphEditionRef", "NodeIdentityDomainRef", "EdgeIdentityDomainRef", "NodeAndEdgeTypeSelection", "DirectionMultiplicityAndSelfLoopPolicy", "PropertyProjection", "WeightSemanticsProfileRef", "TemporalOrSnapshotCutRef", "FilterPredicateEditionRef", "UnknownAndMissingPolicy", "ProjectionProvenanceAndLoss"], "non_collapse_laws": ["view is not source graph", "graph shape is not domain meaning", "reachability is not causality", "weight value is not weight semantics", "projection equality is not source-graph equality", "event knowledge graph is not process model"]},
        {"symbol_ref": "type.eventlogview", "disposition_hypothesis": "ANALYTICAL_PROCESS_FAMILY_GOVERNED_EVENT_DATA_PROJECTION_CANDIDATE", "source_refs": ["source.p1.ieee.xes-2023", "source.p1.ocel-2", "source.p1.oced-whitepaper", "source.p1.fahland.event-knowledge-graphs", "source.p1.state-aware-ocpm"], "finding": "An event-log view is an immutable analytical projection over exact source event data. It binds event identity and inclusion, activity classification, object or case correlation, order and tie-breaking, temporal cut, attribute projection, state-reconstruction rules, completeness/loss evidence and provenance. XES trace views, OCEL object-centric views, state-aware projections and event-knowledge-graph projections require distinct profiles.", "twins": ["A source-system record is not necessarily a domain event or an event-log event.", "One OCEL can yield multiple case-centric traces under different correlation rules.", "A generated state-change event is not a source-system occurrence.", "Timestamp equality does not supply a deterministic total order without a tie-break rule.", "A log containing only observed positive behavior is not the set of all possible behavior.", "An event-log view is not a process model or conformance result."], "carrier_fields": ["EventLogViewId", "SourceEventDataEditionRef", "EventIdentityAndInclusionPredicate", "ActivityClassifierEditionRef", "ObjectOrCaseCorrelationProfileRef", "OrderAndTieBreakProfileRef", "TemporalCutRef", "AttributeProjection", "StateReconstructionProfileRef", "CompletenessAndUnknownPolicy", "ProjectionProvenanceAndLoss", "RepresentationProfileRef"], "non_collapse_laws": ["source record is not event", "event data is not event-log projection", "object-centric log is not case trace set", "derived state-change event is not observed occurrence", "timestamp is not total order", "event log is not process model", "log completeness is not assumed"]},
        {"symbol_ref": "type.processmodel", "disposition_hypothesis": "QUALIFIED_PROCESS_MODEL_ENVELOPE_WITH_FORMALISM_SPECIFIC_SEMANTICS_CANDIDATE", "source_refs": ["source.p1.process-mining-overview", "source.p1.object-centric-petri-nets", "source.p1.fahland.event-knowledge-graphs"], "finding": "A process-model envelope may identify an exact formalism-specific behavioral model, its vocabulary bindings, role, edition, behavioral semantics, initial/final conditions, discovery or authorship provenance and evidence. Petri nets, object-centric Petri nets, BPMN, process trees, declarative constraints, directly-follows graphs and event-knowledge-graph aggregations do not become one algebra merely because all are called process models.", "twins": ["A discovered descriptive model is not an approved normative process.", "A diagram is not executable behavioral semantics.", "High event-log fitness is not precision, soundness or business correctness.", "An object-centric Petri net and a case-centric Petri net have different token and object semantics.", "A directly-follows graph does not express every permitted or forbidden behavior.", "A process model is not an event log, performance annotation or conformance verdict."], "carrier_fields": ["ProcessModelId", "ProcessModelEditionRef", "FormalismAndProfileEditionRef", "ModelRole", "ActivityEventAndObjectVocabularyBindings", "BehavioralSemanticsRef", "InitialAndFinalConditionRef", "DataResourceAndTimeExtensionRefs", "AuthorshipOrDiscoveryProvenance", "SoundnessAndValidationEvidence", "UnsupportedOrUnknownConstructs"], "non_collapse_laws": ["model is not event log", "discovered is not normative", "diagram is not semantics", "fitness is not correctness", "formalism profiles are not interchangeable", "process model is not conformance result", "process model is not performance result"]},
        {"symbol_ref": "type.evidencereceipt", "disposition_hypothesis": "QUALITY_FAMILY_EVALUATION_EVIDENCE_RECORD_WITH_LOCAL_PROFILES_CANDIDATE", "source_refs": ["source.p1.w3c.dqv", "source.p1.w3c.prov-dm", "source.p1.w3c.shacl", "source.p1.rfc9943.scitt-receipts"], "finding": "The quality/reconciliation family needs an immutable evaluation-evidence record binding an exact evaluation occurrence, subject snapshot and scope, policy/rule/metric/method editions, inputs and witnesses, scoped result, coverage and unknowns, producer and time, provenance/integrity, supersession and invalidation. Calling this record a receipt must not collapse it with a SCITT transparency receipt, an audit occurrence, a certificate, or acceptance.", "twins": ["A DQV quality measurement is not a transparency-ledger receipt.", "A SHACL validation result is not processor execution success outside the reported scope.", "A digest or signature establishes bounded integrity, not quality correctness.", "A quality certificate is an annotation or authority act, not the raw evaluation evidence record.", "Evidence that an evaluation ran is not evidence that its result is true or fit for use.", "Missing evidence is not negative evidence.", "A superseded result is not silently deleted."], "carrier_fields": ["QualityEvidenceRecordId", "EvaluationOccurrenceRef", "EvaluationScopeRef", "SubjectSnapshotRef", "PolicyRuleMetricAndMethodEditionRefs", "InputAndWitnessDigests", "ScopedResultRef", "CoverageAndUnknowns", "ProducerAndExecutionEnvironmentRef", "ObservedAtAndRecordedAt", "ProvenanceAndIntegrityEvidenceRefs", "SupersedesOrInvalidatesRefs", "RetentionAndDisclosureProfileRef"], "non_collapse_laws": ["evidence record is not evaluation result alone", "receipt is not acceptance", "integrity is not correctness", "quality evidence is not SCITT receipt", "report is not certificate", "missing evidence is not negative evidence", "supersession is not deletion"]},
        {"symbol_ref": "type.qualityrefusal", "disposition_hypothesis": "QUALITY_FAMILY_TYPED_REFUSAL_ENVELOPE_WITH_LOCAL_VARIANTS_CANDIDATE", "source_refs": ["source.p1.w3c.shacl", "source.p1.oasis.xacml-3", "source.p1.rfc9457.problem-details", "source.p1.otel.span-status"], "finding": "A quality refusal is a typed inability or unwillingness to complete a requested quality/reconciliation operation under its exact contract, not an unfavorable but successfully computed quality result. A family envelope can bind the refused operation and stage, category, occurrence, cause evidence, partial output, retry/recovery posture and unknown completion; each library must retain domain-specific variants and precedence.", "twins": ["A nonconforming validation result is not validator refusal.", "A detected anomaly is not detector failure.", "A reconciliation break is not reconciliation-execution failure.", "XACML NotApplicable, Deny and Indeterminate are different outcomes.", "Invalid input is not evidence that the subject has poor quality.", "Cancellation is not provider failure or resource exhaustion.", "A missing telemetry status is not successful completion.", "An HTTP Problem Details document is a transport representation, not the domain refusal itself."], "carrier_fields": ["QualityRefusalOccurrenceId", "OperationAndStageRef", "EvaluationScopeRef", "RefusalCategory", "DomainVariant", "CauseAndEvidenceRefs", "PartialOutputAndCoverage", "RetryAndRecoveryPosture", "CompletionKnowledge", "ObservedAt", "TransportMappingRefs"], "non_collapse_laws": ["negative quality result is not refusal", "invalid request is not subject defect", "not applicable is not deny", "indeterminate is not false", "cancelled is not failed", "resource exhaustion is not invalid input", "provider failure is not domain refusal", "unknown completion is not not-executed", "transport problem is not domain refusal"]},
    ]
    rows = []
    for spec in specs:
        symbol_ref = spec["symbol_ref"]
        packet = by_symbol[symbol_ref]
        rows.append({"record_kind": "high_fanout_symbol_semantic_research", "research_id": f"research.p1.{symbol_ref.replace('type.','')}.v1", "edition": 1, "symbol_packet_ref": packet["packet_id"], "symbol_ref": symbol_ref, "affected_family_refs": packet["family_refs"], "affected_occurrences": packet["occurrences"], "disposition_hypothesis": spec["disposition_hypothesis"], "bounded_finding": spec["finding"], "candidate_carrier_fields": spec["carrier_fields"], "non_collapse_laws": spec["non_collapse_laws"], "local_refinement_hypotheses": spec.get("local_refinements", []), "negative_twins": spec["twins"], "source_refs": spec["source_refs"], "remaining_owner_decisions": ["canonical owner", "exact equality relation", "local refinements and homonyms", "migration from duplicate declarations", "public name and edition"], "authority_limit": "Primary sources constrain a candidate seam within their own domains. They do not ratify a SAN owner, public API or automatic import disposition.", "decision": "UNRESOLVED", "status": "PRIMARY_RESEARCH_COMPLETE_OWNER_ADJUDICATION_REQUIRED"})
    return rows


OCCURRENCE_REFINEMENTS: dict[tuple[str, str], dict[str, Any]] = {
    ("type.protocoledition", "library.cp.protocol_codec"): {"applicability": "IMPORT_WITH_LOCAL_PROFILE_CANDIDATE", "profile": "profile.protocol-edition.wire-protocol", "name": "WireProtocolEdition", "residuals": ["protocol authority and name", "wire specification set", "negotiation and downgrade policy", "hop-scoped capability evidence"]},
    ("type.protocoledition", "library.experiment.analysis_binding.compiler"): {"applicability": "QUALIFIED_HOMONYM_CANDIDATE", "profile": "profile.protocol-edition.experiment-analysis-binding", "name": "ExperimentProtocolEdition", "residuals": ["experiment protocol identity", "analysis-binding edition", "preregistration relation", "domain evidence beyond HTTP"]},
    ("type.protocoledition", "library.experiment.conclusion.appraiser"): {"applicability": "QUALIFIED_HOMONYM_CANDIDATE", "profile": "profile.protocol-edition.experiment-conclusion", "name": "ExperimentProtocolEdition", "residuals": ["experiment protocol identity", "conclusion appraisal cut", "amendment and deviation semantics", "domain evidence beyond HTTP"]},
    ("type.protocoledition", "library.experiment.integrity.profile.compiler"): {"applicability": "QUALIFIED_HOMONYM_CANDIDATE", "profile": "profile.protocol-edition.experiment-integrity", "name": "ExperimentProtocolEdition", "residuals": ["experiment protocol identity", "integrity-profile binding", "amendment and deviation semantics", "domain evidence beyond HTTP"]},
    ("type.protocoledition", "library.method_kernels.experiment_protocol_semantics"): {"applicability": "QUALIFIED_HOMONYM_CANDIDATE", "profile": "profile.protocol-edition.experiment-method", "name": "ExperimentProtocolEdition", "residuals": ["design and estimand identity", "protocol amendment lineage", "execution deviation semantics", "domain evidence beyond HTTP"]},
    ("type.contentdigest", "library.lpe.digest-core"): {"applicability": "OWNER_CANDIDATE", "profile": "profile.digest.scoped-content", "name": "ScopedContentDigest", "residuals": ["algorithm registry authority", "content versus representation scope", "canonical byte cut", "verification result separate from digest value"]},
    ("type.contentdigest", "library.persistence.storage_identity"): {"applicability": "IMPORT_WITH_LOCAL_PROFILE_CANDIDATE", "profile": "profile.digest.storage-content", "name": "StorageContentDigest", "residuals": ["stored byte or representation cut", "encryption and compression transformation context", "object version binding", "digest must not become storage object identity"]},
    ("type.contentdigest", "library.san_content_identity"): {"applicability": "IMPORT_WITH_LOCAL_PROFILE_CANDIDATE", "profile": "profile.digest.codec-content", "name": "RepresentationContentDigest", "residuals": ["codec and canonicalization edition", "content versus representation choice", "transformation metadata", "library name must not imply semantic identity from digest equality"]},
    ("type.compatibility", "library.method_kernels.artifact_envelope"): {"applicability": "IMPORT_WITH_LOCAL_PROFILE_CANDIDATE", "profile": "profile.compatibility.method-artifact", "name": "MethodArtifactCompatibility", "residuals": ["artifact producer and consumer roles", "method-semantic dimensions", "runtime and dependency dimensions", "direction and evidence"]},
    ("type.compatibility", "library.persistence.schema_evolution"): {"applicability": "IMPORT_WITH_LOCAL_PROFILE_CANDIDATE", "profile": "profile.compatibility.data-schema", "name": "SchemaCompatibilityAssessment", "residuals": ["reader and writer editions", "wire or storage format", "field identity and promotion rules", "semantic and historical-data dimensions"]},
    ("type.compatibility", "library.san_wire_schema"): {"applicability": "IMPORT_WITH_LOCAL_PROFILE_CANDIDATE", "profile": "profile.compatibility.wire-schema", "name": "WireSchemaCompatibilityAssessment", "residuals": ["wire codec and schema editions", "producer and consumer roles", "binary versus text or JSON dimensions", "unknown-field and default semantics"]},
    ("type.lease", "library.runtime-resource.lease-fencing"): {"applicability": "QUALIFIED_HOMONYM_CANDIDATE", "profile": "profile.lease.coordination", "name": "CoordinationLease", "residuals": ["liveness subject and attachment", "keepalive and expiry policy", "stale-holder behavior", "separate monotonically ordered fencing evidence"]},
    ("type.lease", "library.spt.secret_handles"): {"applicability": "QUALIFIED_HOMONYM_CANDIDATE", "profile": "profile.lease.secret-validity", "name": "SecretLease", "residuals": ["opaque credential or version subject", "validity promise and issuer", "renewability metadata", "no secret value in diagnostics"]},
    ("type.lease", "library.spt.secret_provider"): {"applicability": "QUALIFIED_HOMONYM_CANDIDATE", "profile": "profile.lease.secret-validity", "name": "SecretLease", "residuals": ["renew and revoke intent ports", "authority and authorization", "queued versus completed revocation receipt", "downstream cleanup or invalidation evidence"]},
    ("type.cancellationrequest", "library.runtime-resource.deadline-cancellation"): {"applicability": "IMPORT_WITH_LOCAL_PROFILE_CANDIDATE", "profile": "profile.cancellation.runtime-occurrence", "name": "CancellationIntent", "residuals": ["target occurrence and authority", "deadline-trigger relation", "propagation policy", "notification, acceptance and cessation receipts"]},
    ("type.cancellationrequest", "library.operations_research.optimization_solve_execution"): {"applicability": "IMPORT_WITH_LOCAL_PROFILE_CANDIDATE", "profile": "profile.cancellation.optimization-run", "name": "SolveCancellationIntent", "residuals": ["solver safe points", "incumbent and bound disposition", "provider interruption capability", "partial receipt and deterministic replay consequences"]},
    ("type.cancellationrequest", "library.operations_research.simulation_execution"): {"applicability": "IMPORT_WITH_LOCAL_PROFILE_CANDIDATE", "profile": "profile.cancellation.simulation-run", "name": "SimulationCancellationIntent", "residuals": ["simulation step safe points", "partial trajectory disposition", "random-stream and checkpoint handling", "replay consequences"]},
    ("type.lossreport", "library.lpe.audit-log-adapter"): {"applicability": "IMPORT_WITH_LOCAL_PROFILE_CANDIDATE", "profile": "profile.transformation-loss.audit-log", "name": "AuditLogLossAssessment", "residuals": ["event identity and order", "actor-action-resource semantics", "evidence-chain preservation", "redaction and unknown-source fields"]},
    ("type.lossreport", "library.lpe.prov-interchange"): {"applicability": "IMPORT_WITH_LOCAL_PROFILE_CANDIDATE", "profile": "profile.transformation-loss.prov-interchange", "name": "ProvInterchangeLossAssessment", "residuals": ["PROV statement and identifier preservation", "bundle and namespace preservation", "constraint validity", "extension-term and inference loss"]},
    ("type.lossreport", "library.persistence.table_format_acl"): {"applicability": "IMPORT_WITH_LOCAL_PROFILE_CANDIDATE", "profile": "profile.transformation-loss.table-format", "name": "TableFormatLossAssessment", "residuals": ["field identity and schema semantics", "partition and sort semantics", "snapshot and delete semantics", "statistics, properties and unsupported feature correspondence"]},
    ("type.assignmentcut", "library.experiment.analysis_binding.compiler"): {"applicability": "IMPORT_SHARED_EXPERIMENT_CUT_WITH_BINDING_PROFILE_CANDIDATE", "profile": "profile.experiment-cut.analysis-binding.assignment", "name": "ExperimentAssignmentCut", "residuals": ["bind protocol and analysis editions to the assignment-cut reference", "validate eligibility, randomization unit, assignment mechanism and estimand alignment", "bind assignment population and post-assignment exclusion policy", "record integrity evidence and deviations without executing assignment or locking a data snapshot"]},
    ("type.assignmentcut", "library.method_kernels.experiment_analysis_cut_stopping"): {"applicability": "IMPORT_SHARED_EXPERIMENT_CUT_WITH_STOPPING_PROFILE_CANDIDATE", "profile": "profile.experiment-cut.analysis-stopping.assignment", "name": "ExperimentAssignmentCut", "residuals": ["evaluate assignment completeness at an exact snapshot or watermark", "bind late assignments and correction policy", "preserve the randomization-unit and analysis-unit relation", "cut availability does not authorize an interim look or operational stop"]},
    ("type.exposurecut", "library.experiment.analysis_binding.compiler"): {"applicability": "IMPORT_SHARED_EXPERIMENT_CUT_WITH_BINDING_PROFILE_CANDIDATE", "profile": "profile.experiment-cut.analysis-binding.exposure", "name": "ExperimentExposureCut", "residuals": ["bind the counterfactual exposure or trigger definition to the estimand", "validate exposure unit, first-exposure rule, observation window and population relation", "bind noncompliance and interference assumptions", "record exposure-definition amendments without executing exposure assignment or observation"]},
    ("type.exposurecut", "library.method_kernels.experiment_analysis_cut_stopping"): {"applicability": "IMPORT_SHARED_EXPERIMENT_CUT_WITH_STOPPING_PROFILE_CANDIDATE", "profile": "profile.experiment-cut.analysis-stopping.exposure", "name": "ExperimentExposureCut", "residuals": ["evaluate exposure completeness and counterfactual-trigger integrity at the data cut", "bind late exposure events, corrections and first-exposure recomputation policy", "refuse treatment-affected filtering without an admitted design", "cut availability does not authorize an interim look or operational stop"]},
    ("type.metriccut", "library.experiment.analysis_binding.compiler"): {"applicability": "IMPORT_SHARED_EXPERIMENT_CUT_WITH_BINDING_PROFILE_CANDIDATE", "profile": "profile.experiment-cut.analysis-binding.metric", "name": "ExperimentMetricCut", "residuals": ["bind metric definition edition, decision role, population, unit, time window and aggregation to the estimand", "bind missingness, censoring, multiplicity and sensitivity policies", "validate alignment with assignment and exposure cuts", "post-cut semantic mutation creates a new analysis edition and deviation evidence"]},
    ("type.metriccut", "library.method_kernels.experiment_analysis_cut_stopping"): {"applicability": "IMPORT_SHARED_EXPERIMENT_CUT_WITH_STOPPING_PROFILE_CANDIDATE", "profile": "profile.experiment-cut.analysis-stopping.metric", "name": "ExperimentMetricCut", "residuals": ["bind the reproducible data snapshot or watermark and late-arrival policy", "separate a data cut from an interim-look occurrence", "evaluate the prespecified fixed-horizon, group-sequential, alpha-spending or anytime-valid stopping policy", "return stopping eligibility evidence without deciding, authorizing or performing experiment cessation or deployment"]},
}


QOR_LOCAL_PROFILE_GROUPS: list[tuple[str, tuple[str, ...]]] = [
    ("policy_declaration", ("contract_declaration", "quality_policy", "quality_requirement", "rule_specification", "reconciliation_definition", "quality_slo")),
    ("reconciliation", ("accounting_control", "reconciliation_", "reference_master_alignment", "duplicate_entity_resolution")),
    ("validation", ("schema_conformance", "validation_execution", "test_case_management", "remediation_verification")),
    ("authority_action", ("certification_attestation", "correction_execution", "correction_proposal", "defect_adjudication", "quality_alerting", "quality_incident_case", "quarantine_release", "waiver_exception")),
    ("evidence_observation", ("contract_observation", "evidence_receipt", "lineage_quality_impact", "observability_instrumentation")),
]


def qor_local_profile(library_ref: str, symbol_ref: str) -> dict[str, Any]:
    slug = library_ref.removeprefix("library.qor.")
    group = "analytical_measurement"
    for candidate, patterns in QOR_LOCAL_PROFILE_GROUPS:
        if any(pattern in slug for pattern in patterns):
            group = candidate
            break
    group_residuals = {
        "policy_declaration": ["declaration authority, approval and issuance lifecycle", "intended subject and applicability boundary versus observed evaluation scope", "rule dependency, precedence, default and conflict semantics", "amendment, supersession, withdrawal and compatibility consequences"],
        "reconciliation": ["source sides, accounting populations and exact source cuts", "match key, comparison grain, control total and currency/unit semantics", "tolerance, materiality, residual, finality and reopen policy", "late-arrival, correction and restatement treatment"],
        "validation": ["specification, rule-suite and test-case editions", "test subject, positive/negative/boundary case applicability and expected outcomes", "unknown, inapplicable, skipped and untested semantics", "validation result versus publication, release or remediation authority"],
        "authority_action": ["actor, mandate, purpose, affected subject and case scope", "proposal, appraisal, approval, intent, execution and receipt separation", "expiry, revocation, appeal, compensation and irreversibility", "external authority source rather than semantic-kernel self-authorization"],
        "evidence_observation": ["observation subject, source signal and evidence-graph cut", "prospective declaration versus retrospective observation", "coverage, loss, missing and negative-evidence frame", "event, assertion, evidence, appraisal and relying-party decision separation"],
        "analytical_measurement": ["observed subject and population, selection predicate and time/data cut", "metric or method edition, unit, grain, baseline/reference and aggregation", "missingness, censoring, uncertainty and sampling-to-population limits", "measurement, detection, diagnosis, judgment and authorized action separation"],
    }[group]
    if symbol_ref == "type.evaluationscope":
        return {
            "applicability": "FAMILY_SHARED_QUALITY_SCOPE_IMPORT_WITH_LOCAL_PROFILE_CANDIDATE",
            "profile": f"profile.qor.evaluation-scope.{group}.{slug.replace('_', '-')}",
            "name": "QualityEvaluationScope",
            "residuals": ["exact quality/reconciliation subject kind and immutable subject edition or snapshot", "selection/target, grain, valid-time and recording-time boundaries", "explicit exclusions, unknown/uncovered treatment and closed/open-world assumption", *group_residuals],
        }
    if symbol_ref == "type.policyedition":
        return {
            "applicability": "FAMILY_SHARED_QUALITY_POLICY_EDITION_IMPORT_WITH_LOCAL_PROFILE_CANDIDATE",
            "profile": f"profile.qor.policy-edition.{group}.{slug.replace('_', '-')}",
            "name": "QualityPolicyEdition",
            "residuals": ["named quality/reconciliation policy authority and profile", "immutable semantic content, dependency editions and canonical digest", "published, effective, active, superseded and retired lifecycle separation", "policy compatibility and evidence-invalidation rules", *group_residuals],
        }
    if symbol_ref == "type.evidencereceipt":
        return {
            "applicability": "FAMILY_SHARED_QUALITY_EVIDENCE_RECORD_WITH_LOCAL_PROFILE_CANDIDATE",
            "profile": f"profile.qor.evaluation-evidence.{group}.{slug.replace('_', '-')}",
            "name": "QualityEvaluationEvidenceRecord",
            "residuals": ["exact evaluation occurrence, scope and immutable subject snapshot", "local scoped result kind and its successful negative or indeterminate outcomes", "input/witness digests, provenance, coverage, unknown and loss semantics", "retention, disclosure, supersession and invalidation rules", *group_residuals],
        }
    if symbol_ref == "type.qualityrefusal":
        return {
            "applicability": "FAMILY_SHARED_QUALITY_REFUSAL_ENVELOPE_WITH_LOCAL_VARIANTS_CANDIDATE",
            "profile": f"profile.qor.refusal.{group}.{slug.replace('_', '-')}",
            "name": "QualityOperationRefusal",
            "residuals": ["local discriminated refusal variants and precedence", "successful negative, nonconforming, anomalous or unmatched outcomes explicitly excluded", "retry, recovery, partial-output and unknown-completion semantics", "transport and telemetry mappings remain separate from the domain refusal", *group_residuals],
        }
    raise KeyError(f"missing QOR local profile for {symbol_ref}")


def analytical_graph_process_profile(library_ref: str, symbol_ref: str) -> dict[str, Any]:
    slug = library_ref.removeprefix("library.method_kernels.")
    common = {
        "type.graphview": ["exact source graph edition and subject scope", "node and edge identity/type domains, direction, multiplicity and self-loop policy", "property, weight, time and filter profile editions", "unknown, loss, provenance and resource-bound treatment"],
        "type.eventlogview": ["exact source event-data edition and immutable data cut", "event identity, activity classifier and inclusion predicate", "object/case correlation, ordering, tie-break and temporal profile", "completeness, derived-state, loss and provenance evidence"],
        "type.processmodel": ["formalism and behavioral-semantics edition", "descriptive, normative or prescriptive role", "activity/event/object vocabulary bindings and initial/final conditions", "authorship/discovery provenance, soundness evidence and unsupported constructs"],
    }[symbol_ref]
    details: dict[tuple[str, str], tuple[str, str, list[str]]] = {
        ("type.graphview", "graph_semantics"): ("FAMILY_TYPED_GRAPH_VIEW_OWNER_CANDIDATE", "TypedGraphView", ["own only the projection envelope, not domain graph vocabularies or algorithms", "declare projection equality separately from source graph equality"]),
        ("type.graphview", "graph_methods"): ("IMPORT_FAMILY_GRAPH_VIEW_WITH_ALGORITHM_PROFILE_CANDIDATE", "AlgorithmGraphView", ["algorithm capability requirements and supported graph classes", "result identity and semantics remain method-specific"]),
        ("type.graphview", "graph_centrality_methods"): ("IMPORT_FAMILY_GRAPH_VIEW_WITH_CENTRALITY_PROFILE_CANDIDATE", "CentralityGraphView", ["centrality-specific direction, weight, multiedge and component policy", "score normalization and comparability are result semantics, not view semantics"]),
        ("type.graphview", "graph_community_methods"): ("IMPORT_FAMILY_GRAPH_VIEW_WITH_COMMUNITY_PROFILE_CANDIDATE", "CommunityGraphView", ["community objective, resolution, overlap and randomness prerequisites", "community assignment and quality score are results, not view fields"]),
        ("type.graphview", "graph_traversal_path_methods"): ("IMPORT_FAMILY_GRAPH_VIEW_WITH_TRAVERSAL_PROFILE_CANDIDATE", "TraversalGraphView", ["reachability edge predicate, traversal direction and cycle policy", "path identity, path cost and enumeration order remain method/result semantics"]),
        ("type.eventlogview", "process_methods"): ("FAMILY_EVENT_LOG_VIEW_OWNER_CANDIDATE", "GovernedEventLogView", ["own the projection envelope while keeping XES, OCEL, OCED and graph encodings in profiles", "case-centric, object-centric, state-aware and graph views remain qualified"]),
        ("type.eventlogview", "process_discovery_methods"): ("IMPORT_EVENT_LOG_VIEW_WITH_DISCOVERY_PROFILE_CANDIDATE", "DiscoveryEventLogView", ["sampling, noise, lifecycle and population assumptions for discovery", "view construction does not create or validate a process model"]),
        ("type.eventlogview", "process_conformance_methods"): ("IMPORT_EVENT_LOG_VIEW_WITH_CONFORMANCE_PROFILE_CANDIDATE", "ConformanceEventLogView", ["event-to-model vocabulary mapping and alignment scope", "view construction does not produce a conformance verdict"]),
        ("type.eventlogview", "process_performance_methods"): ("IMPORT_EVENT_LOG_VIEW_WITH_PERFORMANCE_PROFILE_CANDIDATE", "PerformanceEventLogView", ["clock, duration, interval, queue/resource and censoring semantics", "performance measure, bottleneck or causal diagnosis is not stored in the view"]),
        ("type.processmodel", "process_methods"): ("FAMILY_PROCESS_MODEL_ENVELOPE_OWNER_CANDIDATE", "QualifiedProcessModel", ["own only the formalism-qualified envelope and capability negotiation", "do not invent a least-common-denominator behavioral algebra"]),
        ("type.processmodel", "process_discovery_methods"): ("IMPORT_PROCESS_MODEL_ENVELOPE_WITH_DISCOVERY_PROFILE_CANDIDATE", "DiscoveredProcessModel", ["discovery algorithm, hyperparameters, random seed and input-view digest", "candidate model, model selection and owner acceptance remain separate"]),
        ("type.processmodel", "process_conformance_methods"): ("IMPORT_PROCESS_MODEL_ENVELOPE_WITH_CONFORMANCE_PROFILE_CANDIDATE", "ConformanceProcessModel", ["alignment semantics, cost model and supported formalism", "model identity, alignment result and conformance judgment remain separate"]),
        ("type.processmodel", "process_performance_methods"): ("IMPORT_PROCESS_MODEL_ENVELOPE_WITH_PERFORMANCE_PROFILE_CANDIDATE", "PerformanceAnalysisProcessModel", ["performance annotation binding and model/log synchronization", "observed duration, bottleneck score and improvement claim remain analytical results"]),
    }
    applicability, name, residuals = details[(symbol_ref, slug)]
    return {
        "applicability": applicability,
        "profile": f"profile.analytical-process.{symbol_ref.removeprefix('type.')}.{slug.replace('_', '-')}",
        "name": name,
        "residuals": [*common, *residuals],
    }


def occurrence_applicability(research: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for item in research:
        for occurrence in item["affected_occurrences"]:
            key = (item["symbol_ref"], occurrence["library_ref"])
            if key in OCCURRENCE_REFINEMENTS:
                refinement = OCCURRENCE_REFINEMENTS[key]
            elif item["symbol_ref"] in {"type.evaluationscope", "type.policyedition", "type.evidencereceipt", "type.qualityrefusal"}:
                refinement = qor_local_profile(occurrence["library_ref"], item["symbol_ref"])
            elif item["symbol_ref"] in {"type.graphview", "type.eventlogview", "type.processmodel"}:
                refinement = analytical_graph_process_profile(occurrence["library_ref"], item["symbol_ref"])
            elif item["symbol_ref"] in {"trait.capabilityrequirement", "trait.capabilityoffer", "trait.conformanceoracle"}:
                local_slug = occurrence["library_ref"].replace("library.", "").replace("_", "-").replace(".", "-")
                if item["symbol_ref"] == "trait.capabilityrequirement":
                    residuals = ["local semantic contract and profile edition", "mandatory/optional and cardinality semantics", "local constraints and finite bounds", "minimum acceptable evidence"]
                    public_name = "CapabilityRequirement"
                    profile_kind = "requirement"
                elif item["symbol_ref"] == "trait.capabilityoffer":
                    residuals = ["exact implementation artifact and provider", "local semantic/profile editions", "offered behavior, resource, target and feature dimensions", "current bounded evidence and invalidators"]
                    public_name = "CapabilityOffer"
                    profile_kind = "offer"
                else:
                    residuals = ["exact local specification/profile edition", "applicability and test-subject cut", "positive, negative, boundary and inapplicable cases", "coverage, unknown and untested outcome semantics"]
                    public_name = "ConformanceOracle"
                    profile_kind = "oracle"
                refinement = {
                    "applicability": "FAMILY_SHARED_PORT_IMPORT_CANDIDATE",
                    "profile": f"profile.capability.{profile_kind}.{local_slug}",
                    "name": public_name,
                    "residuals": residuals,
                }
            else:
                raise KeyError(f"missing occurrence refinement for {key}")
            rows.append({
                "record_kind": "researched_symbol_occurrence_applicability_candidate",
                "applicability_id": f"applicability.p1.{item['symbol_ref'].replace('type.', '')}.{occurrence['library_ref'].replace('library.', '').replace('.', '-')}.v1",
                "edition": 1,
                "research_ref": item["research_id"],
                "symbol_ref": item["symbol_ref"],
                "family_ref": occurrence["family_id"],
                "library_ref": occurrence["library_ref"],
                "current_public_name": occurrence["name"],
                "current_definition_digest": occurrence["definition_digest"],
                "applicability_candidate": refinement["applicability"],
                "local_profile_ref": refinement["profile"],
                "qualified_public_name_candidate": refinement["name"],
                "local_residual_requirements": refinement["residuals"],
                "shared_non_collapse_laws": item["non_collapse_laws"],
                "source_refs": item["source_refs"],
                "owner_decisions_required": item["remaining_owner_decisions"],
                "compiler_law": "Do not import, rename, unify or generate this public symbol until the shared module, this applicability row and its local residuals are ratified together.",
                "decision": "UNRESOLVED",
                "status": "CANDIDATE_UNRATIFIED_OWNER_DECISION_REQUIRED",
            })
    return sorted(rows, key=lambda row: (row["symbol_ref"], row["library_ref"]))


RESEARCH_ARCHETYPES: dict[str, dict[str, Any]] = {
    "OPERATION_BOUNDARY_AND_EFFECT": {"question": "Do equal operation identifiers denote the same command/query, authority, effect, refusal and receipt contract?", "patterns": [], "evidence": ["operation use sites", "state/effect transition specifications", "authority and refusal rules", "idempotency and concurrency contracts", "negative same-name operations"]},
    "CAPABILITY_PORT_AND_CONFORMANCE": {"question": "Is this a provider-independent requirement/offer/oracle port, and which party owns each claim?", "patterns": ["capability", "conformance", "provider", "requirement", "offer", "oracle", "backend"], "evidence": ["port and adapter specifications", "capability negotiation standards", "conformance suite definitions", "provider substitution counterexamples"]},
    "POLICY_SCOPE_PROFILE_AND_EDITION": {"question": "What authority, subject, scope, edition and evaluation cut make this policy/profile value meaningful?", "patterns": ["policy", "scope", "profile", "edition", "cut", "assumption", "checkset", "estimand", "obligation", "attribute_bag", "retention_rule", "disposition_due"], "evidence": ["normative policy models", "scope and delegation rules", "edition/evolution specifications", "cross-context homonym counterexamples"]},
    "EVIDENCE_RECEIPT_APPRAISAL_AND_RESULT": {"question": "Is the value an occurrence receipt, assertion, evidence bundle, appraisal result or relying-party decision?", "patterns": ["evidence", "receipt", "appraisal", "verification", "result", "outcome", "proof", "attestation", "certificate", "predicate_type"], "evidence": ["evidence and provenance standards", "receipt and occurrence identity laws", "appraisal/decision authority models", "claims that remain unsupported"]},
    "ANALYTICAL_METHOD_RESULT_AND_DIAGNOSTIC": {"question": "Which method, input cut, assumptions and execution produced this analytical result, and what remains estimate, diagnostic, residual, unknown or unproved?", "patterns": [], "evidence": ["analytical method specifications", "result and diagnostic contracts", "assumption and uncertainty models", "termination and resource receipts", "result-versus-evidence-versus-decision counterexamples"]},
    "ANALYTICAL_MODEL_ARTIFACT_AND_STATE": {"question": "Which analytical method produced this model artifact, from which training cut and configuration, and which fitted, evaluated, selected, deployed or retired state does it represent?", "patterns": [], "evidence": ["statistical model artifact specifications", "training and evaluation lifecycle models", "parameter and feature-schema contracts", "fitted-versus-validated-versus-deployed counterexamples"]},
    "FAILURE_REFUSAL_AND_PARTIALITY": {"question": "Does the symbol represent invalid input, legitimate refusal, provider failure, resource exhaustion, cancellation or unknown outcome?", "patterns": ["error", "refusal", "failure", "fault", "violation", "invalid", "unknown"], "evidence": ["total failure taxonomies", "protocol error specifications", "refusal precedence rules", "partial/unknown outcome counterexamples"]},
    "IDENTITY_REFERENCE_VERSION_AND_DIGEST": {"question": "What is identified, under which authority and edition, with which equality and canonicalization relation?", "patterns": ["identity", "identifier", "digest", "checksum", "attemptid", "version", "handle", "reference", "_ref", "ref"], "evidence": ["identifier and namespace standards", "canonicalization specifications", "version/equality laws", "digest-versus-identity counterexamples"]},
    "TIME_LIFECYCLE_AND_CONTROL": {"question": "Which occurrence or subject lifecycle is controlled, and which requests, observations and terminal facts remain distinct?", "patterns": ["lease", "deadline", "cancel", "retract", "revok", "heartbeat", "time", "instant", "window", "lifecycle", "expiry", "expiration"], "evidence": ["lifecycle state machines", "temporal standards", "cancellation/revocation protocols", "race and stale-observation counterexamples"]},
    "RESOURCE_BOUND_CAPACITY_AND_SCHEDULING": {"question": "Is this a mathematical bound, storage unit, queue capacity, reservation or scheduling authority?", "patterns": ["bound", "buffer", "reserve", "scheduler", "quota", "capacity", "budget", "limit", "page", "block", "frame"], "evidence": ["resource and scheduling specifications", "mathematical bound definitions", "allocation/commitment protocols", "same-name physical/logical counterexamples"]},
    "REPRESENTATION_CODEC_SCHEMA_AND_LAYOUT": {"question": "Which semantic object, representation, codec, schema edition and loss/compatibility relation does this symbol govern?", "patterns": ["codec", "encode", "decode", "schema", "layout", "manifest", "format", "ast", "document", "serialization", "wire"], "evidence": ["format and codec specifications", "schema evolution rules", "canonical representation laws", "lossy round-trip counterexamples"]},
    "SHAPE_TOPOLOGY_VIEW_AND_PROCESS": {"question": "Is this a carrier shape, topology, projection/view or domain process model, and what information does it preserve?", "patterns": ["graph", "table", "view", "eventlog", "processmodel", "topology", "tree", "collection", "dataset", "geometry", "region", "spatialweights", "partition"], "evidence": ["formal data models", "graph/table/process semantics", "projection and grain laws", "shape-versus-meaning counterexamples"]},
    "AUTHORITY_SECURITY_AND_CREDENTIAL": {"question": "Which authority may issue, delegate, attenuate, authorize or revoke this security-bearing object or action?", "patterns": ["credential", "access", "author", "secret", "privacy", "trust", "permission", "principal", "tenant", "key", "token", "assurance_level", "isolation_class"], "evidence": ["security and authorization standards", "delegation and revocation models", "credential lifecycle specifications", "proof-versus-authority counterexamples"]},
    "MEASURE_QUALITY_COMPARISON_AND_FORMULA": {"question": "What population, dimensions, units, uncertainty and decision cut give this measure/comparison/formula meaning?", "patterns": ["metric", "measure", "quality", "comparison", "score", "estimate", "formula", "dimension", "algebra", "effect", "baselineartifact"], "evidence": ["measurement and quantity standards", "quality and uncertainty models", "formula/metric semantic specifications", "aggregation and comparability counterexamples"]},
    "DOMAIN_CONTRACT_AND_ADAPTER_BOUNDARY": {"question": "Which bounded context owns this business record, which standard/profile edition constrains it, and what does each adapter preserve or lose?", "patterns": [], "evidence": ["business-domain standards and profiles", "provider API and schema editions", "aggregate identity and lifecycle rules", "field-level adapter transformations and loss", "negative same-shape business records"]},
    "ACTIVITY_EVENT_AND_AUDIT_OCCURRENCE": {"question": "Is this an intended action, executed activity, domain event, observed event or audit record, and which occurrence and time does it identify?", "patterns": [], "evidence": ["event and activity data models", "audit-record semantic conventions", "occurrence identity and dual-time rules", "intent-versus-execution-versus-observation counterexamples"]},
    "CRYPTOGRAPHIC_SUITE_PERIOD_AND_AGILITY": {"question": "Which cryptographic purpose, algorithm-suite edition, parameter set, key usage period and migration authority make this value meaningful?", "patterns": [], "evidence": ["cryptographic algorithm registries and profiles", "algorithm-agility specifications", "key-management and cryptoperiod guidance", "deployment-policy and compromise counterexamples"]},
    "GENERAL_SEMANTIC_OWNER_DISCOVERY": {"question": "Do repeated declarations share one semantic owner and equality/lifecycle contract, or are they qualified homonyms?", "patterns": [], "evidence": ["domain-owner definitions", "identity/equality/lifecycle laws", "all operation use sites", "negative homonym twins"]},
}


# This is a research-routing tensor, not a claim that every symbol in an archetype has
# the same meaning.  It states which already-governed semantic questions must be asked
# while researching that kind of collision.  Per-symbol and per-occurrence decisions
# remain mandatory downstream.
ARCHETYPE_SEMANTIC_AXES: dict[str, list[str]] = {
    "OPERATION_BOUNDARY_AND_EFFECT": ["semantic_object", "semantic_role", "state_and_change", "time", "authority_and_trust", "effect_boundary", "resources_and_failure", "evidence_and_conformance"],
    "CAPABILITY_PORT_AND_CONFORMANCE": ["semantic_object", "semantic_role", "authority_and_trust", "compatibility_and_evolution", "resources_and_failure", "evidence_and_conformance"],
    "POLICY_SCOPE_PROFILE_AND_EDITION": ["semantic_object", "identity_and_equality", "grain_and_cardinality", "time", "authority_and_trust", "compatibility_and_evolution", "evidence_and_conformance"],
    "EVIDENCE_RECEIPT_APPRAISAL_AND_RESULT": ["semantic_object", "semantic_role", "identity_and_equality", "time", "partiality_and_uncertainty", "authority_and_trust", "evidence_and_conformance"],
    "ANALYTICAL_METHOD_RESULT_AND_DIAGNOSTIC": ["semantic_object", "semantic_role", "identity_and_equality", "grain_and_cardinality", "state_and_change", "time", "partiality_and_uncertainty", "authority_and_trust", "representation", "composition_algebra", "resources_and_failure", "evidence_and_conformance"],
    "ANALYTICAL_MODEL_ARTIFACT_AND_STATE": ["semantic_object", "semantic_role", "identity_and_equality", "grain_and_cardinality", "state_and_change", "time", "partiality_and_uncertainty", "authority_and_trust", "representation", "compatibility_and_evolution", "resources_and_failure", "evidence_and_conformance"],
    "FAILURE_REFUSAL_AND_PARTIALITY": ["semantic_object", "semantic_role", "identity_and_equality", "state_and_change", "time", "partiality_and_uncertainty", "authority_and_trust", "effect_boundary", "representation", "compatibility_and_evolution", "resources_and_failure", "evidence_and_conformance"],
    "IDENTITY_REFERENCE_VERSION_AND_DIGEST": ["semantic_object", "identity_and_equality", "authority_and_trust", "representation", "compatibility_and_evolution", "evidence_and_conformance"],
    "TIME_LIFECYCLE_AND_CONTROL": ["semantic_object", "semantic_role", "identity_and_equality", "state_and_change", "time", "order_and_topology", "partiality_and_uncertainty", "authority_and_trust", "effect_boundary", "representation", "compatibility_and_evolution", "resources_and_failure", "evidence_and_conformance"],
    "RESOURCE_BOUND_CAPACITY_AND_SCHEDULING": ["semantic_object", "identity_and_equality", "grain_and_cardinality", "state_and_change", "time", "order_and_topology", "partiality_and_uncertainty", "authority_and_trust", "effect_boundary", "resources_and_failure", "evidence_and_conformance"],
    "REPRESENTATION_CODEC_SCHEMA_AND_LAYOUT": ["semantic_object", "identity_and_equality", "partiality_and_uncertainty", "representation", "compatibility_and_evolution", "composition_algebra", "evidence_and_conformance"],
    "SHAPE_TOPOLOGY_VIEW_AND_PROCESS": ["semantic_object", "semantic_role", "identity_and_equality", "grain_and_cardinality", "state_and_change", "time", "order_and_topology", "partiality_and_uncertainty", "representation", "composition_algebra", "compatibility_and_evolution", "evidence_and_conformance"],
    "AUTHORITY_SECURITY_AND_CREDENTIAL": ["semantic_object", "identity_and_equality", "state_and_change", "time", "authority_and_trust", "effect_boundary", "privacy_security_safety", "evidence_and_conformance"],
    "MEASURE_QUALITY_COMPARISON_AND_FORMULA": ["semantic_object", "semantic_role", "identity_and_equality", "grain_and_cardinality", "time", "partiality_and_uncertainty", "representation", "compatibility_and_evolution", "composition_algebra", "evidence_and_conformance"],
    "DOMAIN_CONTRACT_AND_ADAPTER_BOUNDARY": ["semantic_object", "identity_and_equality", "grain_and_cardinality", "state_and_change", "time", "authority_and_trust", "representation", "compatibility_and_evolution", "evidence_and_conformance"],
    "ACTIVITY_EVENT_AND_AUDIT_OCCURRENCE": ["semantic_object", "identity_and_equality", "state_and_change", "time", "order_and_topology", "authority_and_trust", "privacy_security_safety", "evidence_and_conformance"],
    "CRYPTOGRAPHIC_SUITE_PERIOD_AND_AGILITY": ["semantic_object", "identity_and_equality", "state_and_change", "time", "authority_and_trust", "privacy_security_safety", "representation", "compatibility_and_evolution", "evidence_and_conformance"],
    "GENERAL_SEMANTIC_OWNER_DISCOVERY": ["semantic_object", "semantic_role", "identity_and_equality", "state_and_change", "authority_and_trust", "compatibility_and_evolution", "evidence_and_conformance"],
}

SEMANTIC_AXIS_PHASE: dict[str, int] = {
    "semantic_object": 1,
    "identity_and_equality": 1,
    "grain_and_cardinality": 1,
    "state_and_change": 2,
    "time": 2,
    "order_and_topology": 2,
    "partiality_and_uncertainty": 2,
    "authority_and_trust": 3,
    "effect_boundary": 3,
    "privacy_security_safety": 3,
    "representation": 4,
    "compatibility_and_evolution": 4,
    "semantic_role": 5,
    "composition_algebra": 5,
    "resources_and_failure": 5,
    "evidence_and_conformance": 5,
}


# These names first arrived in one lexical policy/profile bucket, but the bucket spans
# seven different semantic objects.  The exact map prevents carrier spelling from
# collapsing plan declarations, evaluation evidence, identifiers, time controls,
# authority obligations, request-context representation and physical/document layout.
POLICY_LANE_EXACT_ARCHETYPES: dict[str, str] = {
    "type.analysisassumptionbinding": "POLICY_SCOPE_PROFILE_AND_EDITION",
    "type.assignmentcheckset": "POLICY_SCOPE_PROFILE_AND_EDITION",
    "type.experimentanalysisedition": "POLICY_SCOPE_PROFILE_AND_EDITION",
    "type.experimentanalysisresultedition": "ANALYTICAL_METHOD_RESULT_AND_DIAGNOSTIC",
    "type.experimentestimandbinding": "POLICY_SCOPE_PROFILE_AND_EDITION",
    "type.experimentintegrityprofile": "POLICY_SCOPE_PROFILE_AND_EDITION",
    "type.exposurecheckset": "POLICY_SCOPE_PROFILE_AND_EDITION",
    "type.guardrailcheckset": "POLICY_SCOPE_PROFILE_AND_EDITION",
    "type.integrityescalationpolicy": "POLICY_SCOPE_PROFILE_AND_EDITION",
    "type.metricpipelinecheckset": "POLICY_SCOPE_PROFILE_AND_EDITION",
    "type.publicationprofileedition": "POLICY_SCOPE_PROFILE_AND_EDITION",
    "type.publicationprofileevidence": "EVIDENCE_RECEIPT_APPRAISAL_AND_RESULT",
    "type.publicationprofileid": "IDENTITY_REFERENCE_VERSION_AND_DIGEST",
    "type.publicationprofileresult": "POLICY_SCOPE_PROFILE_AND_EDITION",
    "type.attribute_bag": "REPRESENTATION_CODEC_SCHEMA_AND_LAYOUT",
    "type.disposition_due": "TIME_LIFECYCLE_AND_CONTROL",
    "type.obligation": "AUTHORITY_SECURITY_AND_CREDENTIAL",
    "type.policy_set": "POLICY_SCOPE_PROFILE_AND_EDITION",
    "type.resource_scope": "POLICY_SCOPE_PROFILE_AND_EDITION",
    "type.retention_rule": "POLICY_SCOPE_PROFILE_AND_EDITION",
    "trait.publicationprofilecontract": "POLICY_SCOPE_PROFILE_AND_EDITION",
    "type.layoutprofile": "SHAPE_TOPOLOGY_VIEW_AND_PROCESS",
    "type.appraisalpolicy": "POLICY_SCOPE_PROFILE_AND_EDITION",
    "trait.schedulerpolicy": "POLICY_SCOPE_PROFILE_AND_EDITION",
}


EVIDENCE_LANE_EXACT_ARCHETYPES: dict[str, str] = {
    "type.assignmentcheckset": "POLICY_SCOPE_PROFILE_AND_EDITION",
    "type.experimentanalysisresultedition": "ANALYTICAL_METHOD_RESULT_AND_DIAGNOSTIC",
    "type.experimentconclusionappraisal": "EVIDENCE_RECEIPT_APPRAISAL_AND_RESULT",
    "type.exposurecheckset": "POLICY_SCOPE_PROFILE_AND_EDITION",
    "type.guardrailcheckset": "POLICY_SCOPE_PROFILE_AND_EDITION",
    "type.metricpipelinecheckset": "POLICY_SCOPE_PROFILE_AND_EDITION",
    "type.codecreceipt": "EVIDENCE_RECEIPT_APPRAISAL_AND_RESULT",
    "type.kernelreceipt": "EVIDENCE_RECEIPT_APPRAISAL_AND_RESULT",
    "type.decoderesult": "REPRESENTATION_CODEC_SCHEMA_AND_LAYOUT",
    "type.encoderesult": "REPRESENTATION_CODEC_SCHEMA_AND_LAYOUT",
    "type.publicationprofileevidence": "EVIDENCE_RECEIPT_APPRAISAL_AND_RESULT",
    "type.publicationprofileresult": "POLICY_SCOPE_PROFILE_AND_EDITION",
    "type.decision_receipt": "EVIDENCE_RECEIPT_APPRAISAL_AND_RESULT",
    "type.predicate_type": "IDENTITY_REFERENCE_VERSION_AND_DIGEST",
    "type.comparisonresult": "ANALYTICAL_METHOD_RESULT_AND_DIAGNOSTIC",
    "type.verificationresult": "EVIDENCE_RECEIPT_APPRAISAL_AND_RESULT",
    "type.dimensionalgebraoutcome": "ANALYTICAL_METHOD_RESULT_AND_DIAGNOSTIC",
    "type.identificationresult": "ANALYTICAL_METHOD_RESULT_AND_DIAGNOSTIC",
    "type.compatibilityresult": "CAPABILITY_PORT_AND_CONFORMANCE",
}


# The original measurement lane mixed declarations, model state, method results and
# physical/optimization bounds because their names contained measure-shaped words.
# Exact routing preserves those distinctions before any lexical pattern is applied.
MEASURE_LANE_EXACT_ARCHETYPES: dict[str, str] = {
    "type.effectestimate": "ANALYTICAL_METHOD_RESULT_AND_DIAGNOSTIC",
    "type.baselineartifact": "ANALYTICAL_MODEL_ARTIFACT_AND_STATE",
    "type.qualityrule": "POLICY_SCOPE_PROFILE_AND_EDITION",
    "trait.dimensionalgebracontract": "MEASURE_QUALITY_COMPARISON_AND_FORMULA",
    "type.dimensionalgebrainput": "MEASURE_QUALITY_COMPARISON_AND_FORMULA",
    "type.bound": "MEASURE_QUALITY_COMPARISON_AND_FORMULA",
}


def research_archetype(packet: dict[str, Any]) -> str:
    symbol_ref = packet["symbol_ref"].lower()
    if packet["symbol_kind"] == "operation":
        return "OPERATION_BOUNDARY_AND_EFFECT"
    if symbol_ref in MEASURE_LANE_EXACT_ARCHETYPES:
        return MEASURE_LANE_EXACT_ARCHETYPES[symbol_ref]
    if symbol_ref in EVIDENCE_LANE_EXACT_ARCHETYPES:
        return EVIDENCE_LANE_EXACT_ARCHETYPES[symbol_ref]
    if symbol_ref in POLICY_LANE_EXACT_ARCHETYPES:
        return POLICY_LANE_EXACT_ARCHETYPES[symbol_ref]
    if symbol_ref.startswith("type.contract.platform-commercial-support."):
        return "DOMAIN_CONTRACT_AND_ADAPTER_BOUNDARY"
    if symbol_ref in {"type.contract.application.effect_receipt", "type.contract.application.execution_receipt"}:
        return "EVIDENCE_RECEIPT_APPRAISAL_AND_RESULT"
    if symbol_ref == "type.contract.application.effect_intent":
        return "DOMAIN_CONTRACT_AND_ADAPTER_BOUNDARY"
    if symbol_ref == "type.contract.application.integration_event":
        return "ACTIVITY_EVENT_AND_AUDIT_OCCURRENCE"
    if symbol_ref == "type.contract.application.state_transition":
        return "TIME_LIFECYCLE_AND_CONTROL"
    if symbol_ref in {"type.contract.application.command", "type.contract.application.query"}:
        return "DOMAIN_CONTRACT_AND_ADAPTER_BOUNDARY"
    if symbol_ref == "type.action":
        return "ACTIVITY_EVENT_AND_AUDIT_OCCURRENCE"
    if symbol_ref in {"type.algorithm_suite", "type.cryptoperiod"}:
        return "CRYPTOGRAPHIC_SUITE_PERIOD_AND_AGILITY"
    # Exact semantic routing precedes lexical heuristics.  In particular, "forecast"
    # contains the substring "ast" but a forecast origin/horizon is temporal and a
    # fitted forecaster is a lifecycle-bearing analytical model artifact, not an AST.
    if symbol_ref == "type.fittedforecaster":
        return "ANALYTICAL_MODEL_ARTIFACT_AND_STATE"
    if symbol_ref in {"type.forecasthorizon", "type.forecastorigin"}:
        return "TIME_LIFECYCLE_AND_CONTROL"
    # Resource-shaped words hide several different semantic objects.  Route the
    # exact public symbol before patterns so research asks the right sovereign
    # question instead of treating every block, bound, frame or page as capacity.
    if symbol_ref in {"type.block", "type.page"}:
        return "SHAPE_TOPOLOGY_VIEW_AND_PROCESS"
    if symbol_ref == "type.frame":
        return "REPRESENTATION_CODEC_SCHEMA_AND_LAYOUT"
    if symbol_ref in {
        "trait.align", "trait.fitnuisance", "trait.reconcile", "trait.replay", "trait.transform",
        "trait.computechecksum", "trait.getobjectrange", "trait.preparetablecommit",
        "trait.prunerowgroups", "trait.scanmanifests", "trait.translatetablemetadata",
        "trait.validateschemachange", "trait.verifychecksum", "trait.verifymigratedtable",
    }:
        return "CAPABILITY_PORT_AND_CONFORMANCE"
    ordered = [
        "CAPABILITY_PORT_AND_CONFORMANCE",
        "FAILURE_REFUSAL_AND_PARTIALITY",
        "TIME_LIFECYCLE_AND_CONTROL",
        "AUTHORITY_SECURITY_AND_CREDENTIAL",
        "IDENTITY_REFERENCE_VERSION_AND_DIGEST",
        "POLICY_SCOPE_PROFILE_AND_EDITION",
        "EVIDENCE_RECEIPT_APPRAISAL_AND_RESULT",
        "REPRESENTATION_CODEC_SCHEMA_AND_LAYOUT",
        "RESOURCE_BOUND_CAPACITY_AND_SCHEDULING",
        "SHAPE_TOPOLOGY_VIEW_AND_PROCESS",
        "MEASURE_QUALITY_COMPARISON_AND_FORMULA",
    ]
    for archetype in ordered:
        if any(pattern in symbol_ref for pattern in RESEARCH_ARCHETYPES[archetype]["patterns"]):
            return archetype
    return "GENERAL_SEMANTIC_OWNER_DISCOVERY"


def remaining_symbol_research_batches(symbols: list[dict[str, Any]], research: list[dict[str, Any]]) -> list[dict[str, Any]]:
    researched = {row["symbol_ref"] for row in research}
    groups: dict[tuple[str, str, str, str], list[dict[str, Any]]] = collections.defaultdict(list)
    for packet in symbols:
        if packet["symbol_ref"] in researched:
            continue
        archetype = research_archetype(packet)
        if packet["symbol_kind"] == "operation":
            cluster_key = packet["symbol_ref"].rsplit(".", 1)[0]
        elif packet["research_route"] == "FAMILY_SHARED_OWNER_OR_LOCAL_IMPORT_RESEARCH":
            cluster_key = "+".join(packet["family_refs"])
        elif packet["research_route"] == "HOMONYM_OR_DEFINITION_CONFLICT_RESEARCH":
            cluster_key = packet["symbol_ref"]
        else:
            cluster_key = "+".join(packet["family_refs"])
        groups[(packet["research_route"], packet["symbol_kind"], archetype, cluster_key)].append(packet)
    ranked = sorted(
        groups.items(),
        key=lambda item: (-sum(packet["priority_score"] for packet in item[1]), item[0]),
    )
    rows = []
    for rank, ((route, kind, archetype, cluster_key), packets) in enumerate(ranked, 1):
        packets = sorted(packets, key=lambda packet: (packet["priority_rank"], packet["symbol_ref"]))
        definition_conflicts = sum(len(packet["definition_digests"]) > 1 for packet in packets)
        research_state = "BOUNDED_PRIMARY_RESEARCH_COMPLETE" if archetype in PRIMARY_RESEARCHED_ARCHETYPE_IDS else "OPEN_PRIMARY_RESEARCH"
        rows.append({
            "record_kind": "remaining_symbol_semantic_research_batch",
            "batch_id": f"batch.p1.remaining-symbols.{rank:02d}.v1",
            "edition": 1,
            "priority_rank": rank,
            "research_route": route,
            "symbol_kind": kind,
            "research_archetype": archetype,
            "semantic_cluster_key": cluster_key,
            "classification_basis": "LEXICAL_AND_STRUCTURAL_ROUTING_ONLY_NOT_A_SEMANTIC_DECISION",
            "sovereign_question": RESEARCH_ARCHETYPES[archetype]["question"],
            "packet_refs": [packet["packet_id"] for packet in packets],
            "symbol_refs": [packet["symbol_ref"] for packet in packets],
            "packet_count": len(packets),
            "represented_occurrence_count": sum(packet["library_count"] for packet in packets),
            "family_refs": sorted({family for packet in packets for family in packet["family_refs"]}),
            "definition_conflict_count": definition_conflicts,
            "required_evidence_classes": RESEARCH_ARCHETYPES[archetype]["evidence"],
            "required_outputs": ["bounded semantic proposition and authority limit", "candidate owner or qualified homonyms", "identity/equality/lifecycle laws", "negative twins and falsification attempts", "one explicit applicability row per occurrence", "local residual requirements and migration hypothesis", "named owner decision still required"],
            "execution_law": "Research the shared proposition once, then project it to every packet and occurrence; lexical batch membership never implies a shared owner or applicability.",
            "research_state": research_state,
            "status": "OWNER_AND_OCCURRENCE_ADJUDICATION_REQUIRED" if research_state == "BOUNDED_PRIMARY_RESEARCH_COMPLETE" else "OPEN_ARCHETYPE_RESEARCH_BATCH",
        })
    return rows


def archetype_ontology() -> dict[str, Any]:
    return {
        "ontology_id": "ontology.p1.remaining-symbol-research-archetypes.v1",
        "edition": 1,
        "as_of": AS_OF,
        "classification_basis": "routing only; owner, equality, lifecycle and applicability remain unresolved",
        "archetypes": [
            {"archetype_id": key, **value}
            for key, value in RESEARCH_ARCHETYPES.items()
        ],
        "non_collapse_laws": ["lexical class is not semantic type", "batch membership is not shared ownership", "shared evidence is not per-occurrence applicability", "research completion is not owner ratification"],
        "completion_claim": False,
    }


def archetype_research_programs(
    batches: list[dict[str, Any]],
    authorities: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Compress research coordination while preserving every owner decision."""
    authority_by_family = {row["family_id"]: row["packet_id"] for row in authorities}
    axis_ontology = load_jsonl(SEM / "semantic-execution-phases.jsonl")
    governed_axes = {
        ref.removeprefix("lane.semantic-axis.").replace("-", "_")
        for phase in axis_ontology
        for ref in phase["axis_lane_refs"]
    }
    groups: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    for batch in batches:
        groups[batch["research_archetype"]].append(batch)

    rows = []
    for archetype in RESEARCH_ARCHETYPES:
        members = sorted(groups.get(archetype, []), key=lambda row: row["priority_rank"])
        if not members:
            continue
        axes = ARCHETYPE_SEMANTIC_AXES[archetype]
        assert set(axes) <= governed_axes
        family_refs = sorted({ref for row in members for ref in row["family_refs"]})
        research_state = "BOUNDED_PRIMARY_RESEARCH_COMPLETE" if archetype in PRIMARY_RESEARCHED_ARCHETYPE_IDS else "OPEN_PRIMARY_RESEARCH"
        rows.append({
            "record_kind": "remaining_symbol_archetype_research_program",
            "research_program_id": f"program.p1.symbol-archetype.{archetype.lower().replace('_', '-')}.v1",
            "edition": 1,
            "archetype_id": archetype,
            "sovereign_question": RESEARCH_ARCHETYPES[archetype]["question"],
            "batch_refs": [row["batch_id"] for row in members],
            "batch_count": len(members),
            "packet_refs": [ref for row in members for ref in row["packet_refs"]],
            "symbol_packet_count": sum(row["packet_count"] for row in members),
            "symbol_refs": [ref for row in members for ref in row["symbol_refs"]],
            "represented_occurrence_count": sum(row["represented_occurrence_count"] for row in members),
            "family_refs": family_refs,
            "source_authority_packet_refs": [authority_by_family[ref] for ref in family_refs],
            "semantic_axis_refs": axes,
            "semantic_phase_refs": [f"constitution.semantic-axis.phase{phase}" for phase in sorted({SEMANTIC_AXIS_PHASE[axis] for axis in axes})],
            "parallel_research_lane_refs": [f"lane.semantic-axis.{axis.replace('_', '-')}" for axis in axes],
            "required_evidence_classes": RESEARCH_ARCHETYPES[archetype]["evidence"],
            "required_outputs": [
                "one bounded archetype proposition and explicit authority limit",
                "axis-indexed definitions, laws, counterexamples and unresolved questions",
                "one candidate owner or qualified-homonym disposition per symbol packet",
                "one explicit applicability decision per exact occurrence",
                "library-local residual and migration requirements",
                "named owner ratification with exact source and target digests",
            ],
            "entry_gate": "Every referenced source-authority packet is structurally ready; semantic research may proceed, but binding waits for its owner disposition.",
            "execution_law": "Reuse questions, sources and counterexample searches across the archetype and its semantic axes; never copy a conclusion, owner, equality relation or applicability decision from one member to another.",
            "decision_grain": "PER_SYMBOL_PACKET_AND_PER_OCCURRENCE",
            "coordination_grain": "PER_ARCHETYPE",
            "research_state": research_state,
            "completion_claim": False,
            "status": "PRIMARY_RESEARCH_COMPLETE_OWNER_DECISIONS_UNRESOLVED" if research_state == "BOUNDED_PRIMARY_RESEARCH_COMPLETE" else "OPEN_COORDINATED_RESEARCH_PROGRAM_OWNER_DECISIONS_UNRESOLVED",
        })
    return rows


OPERATION_ROLE_DETAILS: dict[str, dict[str, Any]] = {
    "DESCRIBE_OR_READ": {"effect": "NO_REQUESTED_DOMAIN_EFFECT_CANDIDATE", "completion": ["request accepted", "snapshot selected", "result produced", "result completely delivered"]},
    "DECLARE_OR_BIND": {"effect": "SPECIFICATION_OR_BINDING_STATE_EFFECT_POSSIBLE", "completion": ["declaration parsed", "references resolved", "binding validated", "edition published or activated"]},
    "VALIDATE_OR_APPRAISE": {"effect": "APPRAISAL_RESULT_WITHOUT_SUBJECT_MUTATION_CANDIDATE", "completion": ["evaluation executed", "coverage known", "result produced", "decision or authorization separately issued"]},
    "DERIVE_OR_TRANSFORM": {"effect": "DERIVED_OUTPUT_EFFECT_CANDIDATE", "completion": ["inputs fixed", "transformation executed", "partial or complete result produced", "result materialized or delivered"]},
    "PLAN_OR_PREPARE": {"effect": "PLAN_OR_PREPARED_STATE_ONLY_CANDIDATE", "completion": ["proposal constructed", "preconditions checked", "prepared state recorded", "commit or external effect separately authorized"]},
    "REQUEST_OR_SUBMIT": {"effect": "ASYNC_EXECUTION_OR_AUTHORITY_REQUEST_EFFECT_POSSIBLE", "completion": ["intent accepted", "work admitted", "execution started", "terminal effect observed"]},
    "CONTROL_RUNNING_OCCURRENCE": {"effect": "RUNNING_PROCESS_OR_VIEW_STATE_EFFECT_POSSIBLE", "completion": ["control intent accepted", "target occurrence notified", "safe point reached", "cessation or transition observed"]},
    "MUTATE_STATE": {"effect": "DOMAIN_OR_PRESENTATION_STATE_EFFECT_POSSIBLE", "completion": ["preconditions satisfied", "mutation attempted", "state committed", "effect visible and durable"]},
    "AUTHORITY_ACTION": {"effect": "AUTHORITY_OR_CREDENTIAL_STATE_EFFECT_POSSIBLE", "completion": ["proposal made", "authority appraised", "decision issued", "revocation or authorization propagated"]},
    "APPEND_OR_RECORD": {"effect": "PERSISTED_OCCURRENCE_OR_FACT_EFFECT_POSSIBLE", "completion": ["record intent accepted", "fact durably appended", "index or projection updated", "downstream notification delivered"]},
    "STREAM_OR_SUBSCRIBE": {"effect": "STREAM_LIFECYCLE_AND_DELIVERY_EFFECT_POSSIBLE", "completion": ["subscription or stream accepted", "source bound", "zero or more results delivered", "stream completed, cancelled or failed"]},
    "DISPATCH_OR_EMIT": {"effect": "EXTERNAL_DISPATCH_EFFECT_POSSIBLE", "completion": ["semantic action constructed", "dispatch accepted", "recipient delivery observed", "recipient business effect separately observed"]},
    "OBSERVE_AND_MATERIALIZE": {"effect": "READ_PLUS_LOCAL_MATERIALIZATION_EFFECT_POSSIBLE", "completion": ["source observation acquired", "observation cut fixed", "local record materialized", "downstream use separately authorized"]},
}


def classify_operation_role(operation_ref: str) -> str:
    verb = operation_ref.rsplit(".", 1)[-1].replace("-", "_")
    exact: dict[str, str] = {
        "record": "APPEND_OR_RECORD",
        "describe_api": "DESCRIBE_OR_READ",
        "scan_manifests": "DESCRIBE_OR_READ",
        "get_object_range": "DESCRIBE_OR_READ",
        "capture_output": "OBSERVE_AND_MATERIALIZE",
        "prepare_table_commit": "PLAN_OR_PREPARE",
        "request_credential": "REQUEST_OR_SUBMIT",
        "submit_query": "REQUEST_OR_SUBMIT",
        "cancel_request": "CONTROL_RUNNING_OCCURRENCE",
        "suppress_evaluation": "CONTROL_RUNNING_OCCURRENCE",
        "freeze_live_view": "CONTROL_RUNNING_OCCURRENCE",
        "open_live_view": "CONTROL_RUNNING_OCCURRENCE",
        "resume_stream": "CONTROL_RUNNING_OCCURRENCE",
        "authorize_interaction": "AUTHORITY_ACTION",
        "attenuate_scope": "AUTHORITY_ACTION",
        "revoke_credential": "AUTHORITY_ACTION",
        "stream_result": "STREAM_OR_SUBSCRIBE",
        "emit_semantic_action": "DISPATCH_OR_EMIT",
        "transition_alert": "MUTATE_STATE",
        "apply_patch": "MUTATE_STATE",
        "clear_output": "MUTATE_STATE",
        "acknowledge_provisional": "MUTATE_STATE",
        "display_revision_risk": "DERIVE_OR_TRANSFORM",
        "display_watermark": "DERIVE_OR_TRANSFORM",
    }
    if verb in exact:
        return exact[verb]
    if verb.startswith(("test_", "evaluate_", "validate_", "verify_")):
        return "VALIDATE_OR_APPRAISE"
    if verb.startswith(("define_", "declare_", "bind_", "normalize_")):
        return "DECLARE_OR_BIND"
    if verb.startswith(("construct_", "label_", "provide_", "sanitize_", "compose_", "lower_", "aggregate", "filter", "inner_join", "project", "sort_", "expand_", "virtualize_", "compute_", "translate_", "compress", "decompress", "matrix_", "spatial_", "prune_")):
        return "DERIVE_OR_TRANSFORM"
    raise KeyError(f"unclassified operation role: {operation_ref}")


def operation_archetype_research() -> list[dict[str, Any]]:
    return [{
        "record_kind": "archetype_semantic_research_candidate",
        "research_id": "research.p1.archetype.operation-boundary-and-effect.v1",
        "edition": 1,
        "archetype_id": "OPERATION_BOUNDARY_AND_EFFECT",
        "bounded_finding": "An operation contract must distinguish purpose, requested effect, target and authority from execution occurrence, delivery, retries, partial/unknown completion, evidence and accepted business outcome. Query/function, action/mutation and subscription/control are qualified roles, not universal semantics inferred from a verb.",
        "required_contract_dimensions": ["operation identity and immutable semantic edition", "request occurrence and correlation identity", "actor, authority, purpose and target subject", "input values, subject snapshot, preconditions and expected version", "semantic role and requested effect boundary", "atomicity, isolation, visibility and durability scope", "safety, idempotency, deduplication and retry policy", "deadline, cancellation, compensation and irreversibility", "partial output, refusal, provider failure and unknown completion", "result, receipt, evidence, provenance and accepted outcome", "stream/backpressure/order/delivery profile where applicable", "privacy, disclosure, resource and cost bounds"],
        "non_collapse_laws": ["operation definition is not request occurrence", "request acceptance is not execution start", "execution start is not effect commit", "delivery exactly once is not business effect exactly once", "safe is not side-effect-free implementation", "idempotent intended effect is not identical response or one execution", "cancellation intent is not cessation or rollback", "result is not receipt, evidence or acceptance", "query, command, plan, validation, transformation and subscription are distinct roles", "transport success is not domain success", "unknown completion is not failure and not success"],
        "source_refs": ["source.p1.rfc9110.protocol-version", "source.p1.odata.operation-effects", "source.p1.graphql.operation-kinds", "source.p1.grpc.cancellation", "source.p1.oasis.wsrm-delivery", "source.p1.w3c.prov-dm", "source.p1.rfc9457.problem-details", "source.p1.otel.span-status"],
        "authority_limit": "The sources establish bounded distinctions in their own protocols. They do not classify a SAN operation by name, grant an owner, or prove transaction, delivery or effect semantics for any occurrence.",
        "decision": "UNRESOLVED",
        "status": "PRIMARY_RESEARCH_COMPLETE_SYMBOL_AND_OCCURRENCE_ADJUDICATION_REQUIRED",
    }]


def operation_contract_classification_candidates(
    batches: list[dict[str, Any]],
    symbols: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    packet_by_ref = {row["packet_id"]: row for row in symbols}
    operation_batches = [row for row in batches if row["research_archetype"] == "OPERATION_BOUNDARY_AND_EFFECT"]
    rows = []
    universal_twins = ["definition versus invocation", "intent versus effect", "attempt versus completion", "domain result versus transport status", "retry versus replay", "receipt versus acceptance"]
    for batch in operation_batches:
        for packet_ref in batch["packet_refs"]:
            packet = packet_by_ref[packet_ref]
            operation_ref = packet["symbol_ref"]
            role = classify_operation_role(operation_ref)
            detail = OPERATION_ROLE_DETAILS[role]
            rows.append({
                "record_kind": "operation_contract_classification_candidate",
                "candidate_id": f"candidate.p1.operation-contract.{operation_ref.removeprefix('operation.').replace('.', '-')}.v1",
                "edition": 1,
                "research_ref": "research.p1.archetype.operation-boundary-and-effect.v1",
                "research_program_ref": "program.p1.symbol-archetype.operation-boundary-and-effect.v1",
                "batch_ref": batch["batch_id"],
                "symbol_packet_ref": packet_ref,
                "operation_ref": operation_ref,
                "family_refs": packet["family_refs"],
                "affected_occurrences": packet["occurrences"],
                "represented_occurrence_count": packet["library_count"],
                "candidate_semantic_role": role,
                "candidate_effect_posture": detail["effect"],
                "completion_distinctions": detail["completion"],
                "retry_and_idempotency_posture": "UNRESOLVED_NEVER_INFER_FROM_OPERATION_NAME",
                "transaction_and_compensation_posture": "UNRESOLVED_REQUIRES_BOUNDED_CONTEXT_RULES",
                "negative_twins": universal_twins,
                "classification_basis": "PRIMARY_RESEARCH_CONSTRAINED_LEXICAL_AND_FAMILY_ROUTING_ONLY_NOT_A_SEMANTIC_DECISION",
                "required_owner_decisions": ["exact semantic role", "requested and incidental effect boundaries", "authority and target", "atomicity/isolation/visibility/durability scope", "retry/idempotency/deduplication semantics", "cancellation/partial/unknown outcome semantics", "result/receipt/evidence/acceptance separation", "exact occurrence applicability and migration"],
                "authority_limit": "This role and effect posture route research. They do not authorize execution, establish safety/idempotency, or change any public contract.",
                "decision": "UNRESOLVED",
                "status": "CANDIDATE_REQUIRES_SYMBOL_AND_OCCURRENCE_OWNER_ADJUDICATION",
            })
    return sorted(rows, key=lambda row: row["operation_ref"])


REFINED_CATCHALL_SYMBOLS = {
    "type.action", "type.algorithm_suite", "type.assurance_level", "type.attribute_bag",
    "type.cryptoperiod", "type.disposition_due", "type.isolation_class", "type.obligation",
    "type.predicate_type", "type.retention_rule", "trait.align", "trait.fitnuisance",
    "trait.reconcile", "trait.replay", "trait.transform", "type.analysisassumptionbinding",
    "type.assignmentcheckset", "type.experimentestimandbinding", "type.exposurecheckset",
    "type.guardrailcheckset", "trait.computechecksum", "trait.getobjectrange",
    "trait.prunerowgroups", "trait.verifychecksum", "type.baselineartifact", "type.geometry",
    "type.region", "type.spatialweights", "trait.isolationbackend", "trait.targetbackend",
    "trait.partition", "type.attemptid",
    "type.contract.application.command", "type.contract.application.effect_intent",
    "type.contract.application.integration_event", "type.contract.application.query",
}


ARCHETYPE_REFINEMENT_SOURCES: dict[str, list[str]] = {
    "DOMAIN_CONTRACT_AND_ADAPTER_BOUNDARY": ["source.p1.openapi.3-1-1", "source.p1.json-schema.2020-12", "source.p1.peppol.billing-3"],
    "ACTIVITY_EVENT_AND_AUDIT_OCCURRENCE": ["source.p1.w3c.prov-dm", "source.p1.w3c.prov-constraints", "source.p1.otel.log-event-model"],
    "CRYPTOGRAPHIC_SUITE_PERIOD_AND_AGILITY": ["source.p1.rfc7696.crypto-agility", "source.p1.nist.sp800-57p1r5"],
    "CAPABILITY_PORT_AND_CONFORMANCE": ["source.p1.tosca.requirements-capabilities", "source.p1.wasm-component.wit", "source.p1.nist.conformance-testing"],
    "POLICY_SCOPE_PROFILE_AND_EDITION": ["source.p1.oasis.xacml-3", "source.p1.w3c.odrl-model", "source.p1.opa.bundles", "source.p1.opa.decision-logs", "source.p1.ich.e9-r1", "source.p1.w3c.dx-prof", "source.p1.kubernetes.scheduling-framework", "source.p1.consort.2025", "source.p1.w3c.dqv", "source.p1.w3c.shacl"],
    "EVIDENCE_RECEIPT_APPRAISAL_AND_RESULT": ["source.p1.w3c.prov-dm", "source.p1.w3c.shacl", "source.p1.oasis.xacml-3", "source.p1.rfc9943.scitt-receipts", "source.p1.w3c.vc-data-integrity", "source.p1.intoto.statement-v1", "source.p1.otel.log-event-model"],
    "ANALYTICAL_METHOD_RESULT_AND_DIAGNOSTIC": ["source.p1.ich.e9-r1", "source.p1.pywhy.dowhy-effect-inference", "source.p1.scipy.optimize-result", "source.p1.w3c.prov-dm"],
    "ANALYTICAL_MODEL_ARTIFACT_AND_STATE": ["source.p1.mlflow.model-artifact", "source.p1.onnx.ir", "source.p1.sktime.base-forecaster", "source.p1.nist.process-monitoring-baseline", "source.p1.w3c.prov-dm"],
    "FAILURE_REFUSAL_AND_PARTIALITY": ["source.p1.rfc9457.problem-details", "source.p1.otel.span-status", "source.p1.oasis.xacml-3", "source.p1.rfc8785.jcs", "source.p1.ucum.2-2", "source.p1.oasis.openformula-1-3", "source.p1.w3c.dx-prof"],
    "IDENTITY_REFERENCE_VERSION_AND_DIGEST": ["source.p1.rfc3986.uri-identity", "source.p1.rfc9562.uuid", "source.p1.w3c.did-core", "source.p1.rfc6920.named-information", "source.p1.rfc9530.digest-fields", "source.p1.rfc8785.jcs", "source.p1.w3c.prov-dm", "source.p1.w3c.dcat3-versioning", "source.p1.semver.2", "source.p1.intoto.statement-v1", "source.p1.w3c.vc-data-integrity", "source.p1.otel.span-context", "source.p1.openlineage.run-identity"],
    "AUTHORITY_SECURITY_AND_CREDENTIAL": ["source.p1.nist.sp800-63-4", "source.p1.nist.sp800-162-abac", "source.p1.oasis.xacml-3", "source.p1.rfc6749.oauth2", "source.p1.rfc7009.oauth-revocation", "source.p1.rfc7517.jwk", "source.p1.oasis.pkcs11-3-1", "source.p1.w3c.vc-data-integrity", "source.p1.kubernetes.multi-tenancy", "source.p1.spiffe.id", "source.p1.chubby.lock-service"],
    "TIME_LIFECYCLE_AND_CONTROL": ["source.p1.rfc3339.timestamp", "source.p1.w3c.owl-time", "source.p1.hyndman.fpp3", "source.p1.nara.disposition-instructions", "source.p1.otel.log-event-model", "source.p1.w3c.prov-dm", "source.p1.w3c.prov-constraints", "source.p1.flink.changelog-retraction", "source.p1.etcd.lease-api", "source.p1.vault.lease-semantics"],
    "RESOURCE_BOUND_CAPACITY_AND_SCHEDULING": ["source.p1.kubernetes.resource-management", "source.p1.linux.cgroup-v2", "source.p1.slurm.reservations", "source.p1.arrow.columnar-buffers", "source.p1.rabbitmq.queue-limits", "source.p1.kubernetes.scheduling-framework"],
    "REPRESENTATION_CODEC_SCHEMA_AND_LAYOUT": ["source.p1.rfc8949.cbor", "source.p1.whatwg.encoding", "source.p1.unicode.uax15", "source.p1.oasis.openformula-1-3", "source.p1.ro-crate-1-2", "source.p1.iiif.presentation-3", "source.p1.rfc9113.http2-frames", "source.p1.json-schema.2020-12", "source.p1.rfc8785.jcs", "source.p1.iceberg.evolution", "source.p1.oasis.xacml-3"],
    "SHAPE_TOPOLOGY_VIEW_AND_PROCESS": ["source.p1.rfc7946.geojson", "source.p1.ogc.sfa-1-2-1", "source.p1.nist.randomized-block-design", "source.p1.loc.alto-4-4", "source.p1.kernighan-lin.graph-partition", "source.p1.substrait.distribution", "source.p1.libpysal.spatial-weights", "source.p1.parquet.page-index", "source.p1.iiif.presentation-3"],
    "MEASURE_QUALITY_COMPARISON_AND_FORMULA": ["source.p1.jcgm.vim3", "source.p1.ucum.2-2", "source.p1.oasis.openformula-1-3", "source.p1.google.mathopt-objective-bounds", "source.p1.parquet.page-index", "source.p1.w3c.dqv"],
}


PRIMARY_RESEARCHED_ARCHETYPE_IDS = frozenset({
    "OPERATION_BOUNDARY_AND_EFFECT",
    "DOMAIN_CONTRACT_AND_ADAPTER_BOUNDARY",
    "ACTIVITY_EVENT_AND_AUDIT_OCCURRENCE",
    "CRYPTOGRAPHIC_SUITE_PERIOD_AND_AGILITY",
    "CAPABILITY_PORT_AND_CONFORMANCE",
    "POLICY_SCOPE_PROFILE_AND_EDITION",
    "IDENTITY_REFERENCE_VERSION_AND_DIGEST",
    "AUTHORITY_SECURITY_AND_CREDENTIAL",
    "REPRESENTATION_CODEC_SCHEMA_AND_LAYOUT",
    "RESOURCE_BOUND_CAPACITY_AND_SCHEDULING",
    "SHAPE_TOPOLOGY_VIEW_AND_PROCESS",
    "EVIDENCE_RECEIPT_APPRAISAL_AND_RESULT",
    "ANALYTICAL_METHOD_RESULT_AND_DIAGNOSTIC",
    "MEASURE_QUALITY_COMPARISON_AND_FORMULA",
    "TIME_LIFECYCLE_AND_CONTROL",
    "FAILURE_REFUSAL_AND_PARTIALITY",
    "ANALYTICAL_MODEL_ARTIFACT_AND_STATE",
})


def catchall_refinement_research() -> list[dict[str, Any]]:
    return [
        {
            "record_kind": "archetype_semantic_research_candidate",
            "research_id": "research.p1.archetype.domain-contract-adapter-boundary.v1",
            "edition": 1,
            "archetype_id": "DOMAIN_CONTRACT_AND_ADAPTER_BOUNDARY",
            "bounded_finding": "A provider or wire schema can describe a carrier surface but cannot own a business record merely by encoding it. A domain contract binds bounded-context ownership, business identity, aggregate/lifecycle rules, authority, time and canonical meaning; every adapter separately declares profile edition, mapping direction, preservation, loss and refusal.",
            "required_contract_dimensions": ["bounded context and semantic owner", "business identity, equality and aggregate membership", "lifecycle, valid/recording time and correction rules", "authority, actor roles and allowed effects", "canonical domain model and exact edition", "external standard/profile and provider schema editions", "directional mapping, canonicalization and information-loss report", "structural and semantic validation", "refusal, residual, provenance and reconciliation evidence"],
            "non_collapse_laws": ["schema validity is not domain validity", "provider payload is not canonical domain contract", "same record name is not shared aggregate identity", "adapter mapping is not semantic equality", "successful transport is not accepted business effect", "lossless syntax round-trip is not lossless business meaning"],
            "source_refs": ARCHETYPE_REFINEMENT_SOURCES["DOMAIN_CONTRACT_AND_ADAPTER_BOUNDARY"],
            "authority_limit": "OpenAPI, JSON Schema and Peppol constrain their own interface, structure and billing profiles. They do not choose SAN aggregate boundaries or ratify mappings for other commercial records.",
            "decision": "UNRESOLVED",
            "status": "PRIMARY_RESEARCH_COMPLETE_DOMAIN_OWNER_AND_ADAPTER_ADJUDICATION_REQUIRED",
        },
        {
            "record_kind": "archetype_semantic_research_candidate",
            "research_id": "research.p1.archetype.activity-event-audit-occurrence.v1",
            "edition": 1,
            "archetype_id": "ACTIVITY_EVENT_AND_AUDIT_OCCURRENCE",
            "bounded_finding": "An action kind, an activity execution, a domain event and an audit/log record are separate semantic objects. An audit occurrence must bind what was observed or asserted, by whom, about which subject and operation, at occurrence and observation times, with provenance, integrity, disclosure and completeness limits.",
            "required_contract_dimensions": ["action/activity/event class identity and edition", "execution or observation occurrence identity", "actor, authority, subject, object and purpose", "intent, attempted effect, observed effect and outcome", "occurrence, observation and recording time", "correlation, causation and trace context", "source, instrumentation and provenance", "integrity, redaction, retention and disclosure", "coverage, gaps, duplication and ordering"],
            "non_collapse_laws": ["action kind is not action occurrence", "activity is not event", "event is not log record", "event time is not observed time", "actor identity is not authority", "audit record is evidence not truth", "recorded intent is not completed effect", "absence from an audit log is not proof of non-occurrence"],
            "source_refs": ARCHETYPE_REFINEMENT_SOURCES["ACTIVITY_EVENT_AND_AUDIT_OCCURRENCE"],
            "authority_limit": "PROV and OpenTelemetry constrain provenance and telemetry records. They do not establish business truth, audit completeness, legal admissibility or the authority of the recorded actor.",
            "decision": "UNRESOLVED",
            "status": "PRIMARY_RESEARCH_COMPLETE_AUDIT_DOMAIN_OWNER_ADJUDICATION_REQUIRED",
        },
        {
            "record_kind": "archetype_semantic_research_candidate",
            "research_id": "research.p1.archetype.cryptographic-suite-period-agility.v1",
            "edition": 1,
            "archetype_id": "CRYPTOGRAPHIC_SUITE_PERIOD_AND_AGILITY",
            "bounded_finding": "Algorithm-suite identity, protocol interoperability, deployment permission, security strength, key purpose, cryptoperiod, compromise state and migration policy are independent coordinates. Stable identifiers and agility permit migration; they do not make every suite safe or every unexpired key authorized.",
            "required_contract_dimensions": ["cryptographic purpose and security service", "suite identifier, registry authority and immutable edition", "component algorithms, modes, parameter and key-size profile", "mandatory, permitted, selected, deprecated and prohibited states", "key type, purpose and originator/recipient usage periods", "effective interval, cryptoperiod basis and time source", "negotiation, downgrade resistance and compatibility", "compromise, revocation, migration and emergency transition", "provider capability and independent conformance evidence"],
            "non_collapse_laws": ["algorithm identifier is not algorithm strength", "suite support is not deployment permission", "mandatory-to-implement is not mandatory-to-use", "cryptoperiod is not certificate validity", "unexpired is not uncompromised", "deprecation is not identifier deletion", "interoperability is not security", "agility is not automatic migration"],
            "source_refs": ARCHETYPE_REFINEMENT_SOURCES["CRYPTOGRAPHIC_SUITE_PERIOD_AND_AGILITY"],
            "authority_limit": "RFC 7696 and NIST SP 800-57 provide protocol and key-management guidance. Deployment policy, risk acceptance and exact cryptoperiod remain purpose- and owner-specific.",
            "decision": "UNRESOLVED",
            "status": "PRIMARY_RESEARCH_COMPLETE_SECURITY_OWNER_ADJUDICATION_REQUIRED",
        },
    ]


def catchall_refinement_candidates(
    symbols: list[dict[str, Any]],
    researched: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    researched_refs = {row["symbol_ref"] for row in researched}
    targets = [row for row in symbols if row["symbol_ref"] not in researched_refs and (row["symbol_ref"] in REFINED_CATCHALL_SYMBOLS or row["symbol_ref"].startswith("type.contract.platform-commercial-support."))]
    rows = []
    for packet in targets:
        archetype = research_archetype(packet)
        assert archetype != "GENERAL_SEMANTIC_OWNER_DISCOVERY"
        sources = ARCHETYPE_REFINEMENT_SOURCES[archetype]
        rows.append({
            "record_kind": "catchall_symbol_archetype_refinement_candidate",
            "refinement_id": f"refinement.p1.catchall.{packet['symbol_ref'].replace('.', '-')}.v1",
            "edition": 1,
            "symbol_packet_ref": packet["packet_id"],
            "symbol_ref": packet["symbol_ref"],
            "family_refs": packet["family_refs"],
            "affected_occurrences": packet["occurrences"],
            "represented_occurrence_count": packet["library_count"],
            "candidate_archetype": archetype,
            "candidate_semantic_axis_refs": ARCHETYPE_SEMANTIC_AXES[archetype],
            "source_refs": sources,
            "required_evidence_classes": RESEARCH_ARCHETYPES[archetype]["evidence"],
            "sovereign_question": RESEARCH_ARCHETYPES[archetype]["question"],
            "required_owner_decisions": ["semantic owner and bounded context", "exact definition, identity, equality and lifecycle", "shared import versus qualified homonym", "per-occurrence applicability and local residuals", "migration and public-name disposition"],
            "classification_basis": "BOUNDED_PRIMARY_RESEARCH_PLUS_EXACT_FAMILY_AND_USE_SITE_ROUTING_NOT_A_SEMANTIC_DECISION",
            "authority_limit": "Archetype routing selects research questions and evidence classes only; it does not unify symbols, grant ownership or decide occurrence applicability.",
            "decision": "UNRESOLVED",
            "status": "CATCHALL_REMOVED_TARGETED_ARCHETYPE_RESEARCH_AND_OWNER_DECISION_REQUIRED",
        })
    return sorted(rows, key=lambda row: row["symbol_ref"])


CAPABILITY_PORT_ROLE_DETAILS: dict[str, dict[str, str]] = {
    "ANALYTICAL_METHOD_PORT": {"lifecycle_position": "SEMANTIC_PORT_DEFINITION", "effect_posture": "METHOD_SPECIFIC_UNRESOLVED"},
    "COMPUTE_PORT": {"lifecycle_position": "SEMANTIC_PORT_DEFINITION", "effect_posture": "DERIVED_RESULT_WITH_INCIDENTAL_RESOURCE_EFFECTS_CANDIDATE"},
    "STORAGE_READ_PORT": {"lifecycle_position": "SEMANTIC_PORT_DEFINITION", "effect_posture": "READ_WITH_IO_AND_PARTIAL_DELIVERY_EFFECTS_CANDIDATE"},
    "PREPARATION_PORT": {"lifecycle_position": "SEMANTIC_PORT_DEFINITION", "effect_posture": "PREPARED_STATE_WITHOUT_COMMIT_CANDIDATE"},
    "CONFORMANCE_CHECK_PORT": {"lifecycle_position": "SEMANTIC_PORT_DEFINITION", "effect_posture": "APPRAISAL_WITHOUT_SUBJECT_MUTATION_CANDIDATE"},
    "TRANSFORMATION_PORT": {"lifecycle_position": "SEMANTIC_PORT_DEFINITION", "effect_posture": "DERIVED_REPRESENTATION_WITH_EXPLICIT_LOSS_CANDIDATE"},
    "BACKEND_PROVIDER_PORT": {"lifecycle_position": "IMPLEMENTATION_PORT", "effect_posture": "PROVIDER_RUNTIME_EFFECTS_UNRESOLVED"},
    "PROVIDER_CAPABILITY_OFFER": {"lifecycle_position": "PROVIDER_ASSERTION", "effect_posture": "ASSERTION_ONLY_NO_RUNTIME_EFFECT_PROVED"},
    "CONFORMANCE_EVALUATION_RESULT": {"lifecycle_position": "SCOPED_APPRAISAL_RESULT", "effect_posture": "RESULT_ONLY_NO_QUALIFICATION_OR_SELECTION_AUTHORITY"},
    "CONFORMANCE_EVIDENCE_RECEIPT": {"lifecycle_position": "EVIDENCE_RECORD", "effect_posture": "EVIDENCE_ONLY_NO_CONFORMANCE_TRUTH_OR_ACCEPTANCE"},
    "REQUIREMENT_SATISFACTION_RESULT": {"lifecycle_position": "MATCH_OR_SATISFACTION_RESULT", "effect_posture": "COMPARISON_ONLY_NO_SELECTION_BINDING_OR_INVOCATION"},
}


def classify_capability_port_role(symbol_ref: str) -> str:
    exact = {
        "type.capabilityoffer": "PROVIDER_CAPABILITY_OFFER",
        "type.conformanceresult": "CONFORMANCE_EVALUATION_RESULT",
        "type.conformancereceipt": "CONFORMANCE_EVIDENCE_RECEIPT",
        "type.compatibilityresult": "REQUIREMENT_SATISFACTION_RESULT",
        "trait.isolationbackend": "BACKEND_PROVIDER_PORT",
        "trait.targetbackend": "BACKEND_PROVIDER_PORT",
        "trait.getobjectrange": "STORAGE_READ_PORT",
        "trait.scanmanifests": "STORAGE_READ_PORT",
        "trait.preparetablecommit": "PREPARATION_PORT",
        "trait.validateschemachange": "CONFORMANCE_CHECK_PORT",
        "trait.verifychecksum": "CONFORMANCE_CHECK_PORT",
        "trait.verifymigratedtable": "CONFORMANCE_CHECK_PORT",
        "trait.translatetablemetadata": "TRANSFORMATION_PORT",
        "trait.computechecksum": "COMPUTE_PORT",
        "trait.prunerowgroups": "COMPUTE_PORT",
        "trait.align": "ANALYTICAL_METHOD_PORT",
        "trait.fitnuisance": "ANALYTICAL_METHOD_PORT",
        "trait.reconcile": "ANALYTICAL_METHOD_PORT",
        "trait.replay": "ANALYTICAL_METHOD_PORT",
        "trait.transform": "ANALYTICAL_METHOD_PORT",
    }
    return exact[symbol_ref]


def capability_port_archetype_research() -> list[dict[str, Any]]:
    return [{
        "record_kind": "archetype_semantic_research_candidate",
        "research_id": "research.p1.archetype.capability-port-conformance.v1",
        "edition": 1,
        "archetype_id": "CAPABILITY_PORT_AND_CONFORMANCE",
        "bounded_finding": "A semantic port defines required behavior; a consumer requirement, provider offer, satisfaction result, selected binding, implementation artifact, conformance result, evidence receipt, independent qualification and runtime invocation are distinct lifecycle objects. Interface shape and a matching offer are necessary but insufficient for semantic substitutability or portability.",
        "required_contract_dimensions": ["semantic port identity, owner and immutable edition", "operation/type surface and structural signature", "preconditions, postconditions, invariants, effects and refusals", "resource, performance, determinism, cancellation and target constraints", "consumer requirement with mandatory/optional/cardinality semantics", "provider offer bound to artifact, provider, target and evidence edition", "satisfaction/matching result with unknown and residual constraints", "selected binding and compiler lowering decision", "scoped conformance oracle and evaluation result", "evidence receipt and independent qualification", "runtime invocation, outcome and current availability", "compatibility, withdrawal, substitution and portability rules"],
        "non_collapse_laws": ["language trait is not semantic capability", "port signature is not behavior", "requirement is not offer", "offer is not current availability", "matching is not selection", "selection is not binding success", "binding is not invocation", "conformance result is not evidence receipt", "passing tests is not complete proof", "conformance is not interoperability or fitness", "one implementation is not portability", "provider adapter is not semantic owner"],
        "source_refs": ["source.p1.tosca.requirements-capabilities", "source.p1.wasm-component.wit", "source.p1.nist.conformance-testing", "source.p1.w3c.act-rules", "source.p1.openapi.3-1-1"],
        "authority_limit": "TOSCA, WIT, NIST, ACT and OpenAPI constrain their own topology, interface and testing models. They do not prove semantic substitutability, select a SAN provider or ratify any local port owner.",
        "decision": "UNRESOLVED",
        "status": "PRIMARY_RESEARCH_COMPLETE_PORT_OWNER_AND_OCCURRENCE_ADJUDICATION_REQUIRED",
    }]


def capability_port_classification_candidates(
    batches: list[dict[str, Any]],
    symbols: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    packet_by_ref = {row["packet_id"]: row for row in symbols}
    capability_batches = [row for row in batches if row["research_archetype"] == "CAPABILITY_PORT_AND_CONFORMANCE"]
    rows = []
    for batch in capability_batches:
        for packet_ref in batch["packet_refs"]:
            packet = packet_by_ref[packet_ref]
            symbol_ref = packet["symbol_ref"]
            role = classify_capability_port_role(symbol_ref)
            detail = CAPABILITY_PORT_ROLE_DETAILS[role]
            rows.append({
                "record_kind": "capability_port_classification_candidate",
                "candidate_id": f"candidate.p1.capability-port.{symbol_ref.replace('.', '-')}.v1",
                "edition": 1,
                "research_ref": "research.p1.archetype.capability-port-conformance.v1",
                "research_program_ref": "program.p1.symbol-archetype.capability-port-and-conformance.v1",
                "batch_ref": batch["batch_id"],
                "symbol_packet_ref": packet_ref,
                "symbol_ref": symbol_ref,
                "family_refs": packet["family_refs"],
                "affected_occurrences": packet["occurrences"],
                "represented_occurrence_count": packet["library_count"],
                "candidate_port_role": role,
                "candidate_lifecycle_position": detail["lifecycle_position"],
                "candidate_effect_posture": detail["effect_posture"],
                "binding_posture": "UNBOUND_OWNER_AND_PROVIDER_DECISIONS_REQUIRED",
                "required_owner_decisions": ["semantic port owner and exact edition", "signature versus domain behavior contract", "effects, refusals and partial/unknown outcomes", "requirement/offer/matching/binding lifecycle position", "conformance oracle scope and outcomes", "provider evidence, qualification and portability", "per-occurrence import, qualified homonym or split", "migration and compiler lowering"],
                "non_collapse_laws": ["trait is not capability offer", "offer is not proof", "result is not receipt", "conformance is not qualification", "binding is not execution", "adapter is not semantic owner"],
                "classification_basis": "BOUNDED_PRIMARY_RESEARCH_PLUS_SYMBOL_AND_USE_SITE_ROUTING_NOT_A_BINDING_DECISION",
                "authority_limit": "This candidate selects a lifecycle question and research profile only; it does not prove compatibility, conformance, provider suitability or runtime availability.",
                "decision": "UNRESOLVED",
                "status": "CANDIDATE_REQUIRES_PORT_OWNER_AND_OCCURRENCE_ADJUDICATION",
            })
    return sorted(rows, key=lambda row: row["symbol_ref"])


POLICY_ROLE_DETAILS: dict[str, dict[str, str]] = {
    "ANALYSIS_PLAN_BINDING": {"semantic_position": "DECLARATIVE_ANALYSIS_PLAN_COMPONENT", "effect_posture": "NO_OBSERVATION_EVALUATION_OR_EXECUTION_AUTHORITY"},
    "IMMUTABLE_ANALYSIS_PLAN_EDITION": {"semantic_position": "IMMUTABLE_PLAN_SNAPSHOT", "effect_posture": "SEALED_DECLARATION_NOT_ACTIVE_EXECUTION"},
    "PROFILE_SPECIFICATION": {"semantic_position": "CONSTRAINT_EXTENSION_AND_GUIDANCE_SPECIFICATION", "effect_posture": "SPECIFICATION_ONLY_NO_CONFORMANCE_RESULT"},
    "PROFILE_EDITION": {"semantic_position": "IMMUTABLE_PROFILE_SNAPSHOT", "effect_posture": "PUBLISHED_MEANING_NOT_ACTIVATION_OR_RESULT"},
    "DECISION_POLICY": {"semantic_position": "DECLARED_DECISION_RULE_SET", "effect_posture": "POLICY_EVALUATION_DOES_NOT_PERFORM_EXTERNAL_EFFECT"},
    "POLICY_COMPOSITION": {"semantic_position": "COMPOSED_RULE_AND_PRECEDENCE_SET", "effect_posture": "DECLARATION_NOT_EVALUATION_OR_ENFORCEMENT"},
    "APPLICABILITY_SCOPE": {"semantic_position": "SUBJECT_TARGET_AND_CONTEXT_SELECTION", "effect_posture": "SCOPE_MEMBERSHIP_NOT_SATISFACTION_OR_PERMISSION"},
    "LIFECYCLE_POLICY_RULE": {"semantic_position": "TIME_AND_DISPOSITION_RULE", "effect_posture": "DUE_OR_ELIGIBLE_NOT_EXECUTED_DISPOSITION"},
    "PROFILE_CONTRACT_PORT": {"semantic_position": "PROFILE_BEHAVIOR_CONTRACT", "effect_posture": "PORT_DEFINITION_NOT_PROVIDER_OFFER_OR_RESULT"},
    "APPRAISAL_DECISION_POLICY": {"semantic_position": "CLAIM_APPRAISAL_RULE_SET", "effect_posture": "APPRAISAL_RULES_NOT_RELYING_PARTY_ACCEPTANCE"},
    "SCHEDULING_STRATEGY_POLICY": {"semantic_position": "PLACEMENT_SELECTION_STRATEGY", "effect_posture": "SELECTION_PROPOSAL_NOT_BINDING_EFFECT"},
    "PROSPECTIVE_CHECK_SPECIFICATION": {"semantic_position": "PRESPECIFIED_EVALUATION_RULE_SET", "effect_posture": "CHECK_DEFINITION_NOT_OBSERVED_CHECK_RESULT"},
    "POLICY_COMPILATION_RESULT": {"semantic_position": "COMPILED_POLICY_PROFILE_OUTPUT", "effect_posture": "COMPILATION_RESULT_NOT_ACTIVATION_PUBLICATION_OR_EFFECT"},
    "QUALITY_EVALUATION_RULE_SPECIFICATION": {"semantic_position": "TYPED_QUALITY_CONSTRAINT_PREDICATE_OR_EVALUATION_SPECIFICATION", "effect_posture": "RULE_DEFINITION_ONLY_NOT_MEASUREMENT_RESULT_REPAIR_CERTIFICATION_OR_AUTHORITY"},
}


def classify_policy_role(symbol_ref: str) -> str:
    exact = {
        "type.analysisassumptionbinding": "ANALYSIS_PLAN_BINDING",
        "type.experimentanalysisedition": "IMMUTABLE_ANALYSIS_PLAN_EDITION",
        "type.experimentestimandbinding": "ANALYSIS_PLAN_BINDING",
        "type.experimentintegrityprofile": "PROFILE_SPECIFICATION",
        "type.integrityescalationpolicy": "DECISION_POLICY",
        "type.publicationprofileedition": "PROFILE_EDITION",
        "type.policy_set": "POLICY_COMPOSITION",
        "type.resource_scope": "APPLICABILITY_SCOPE",
        "type.retention_rule": "LIFECYCLE_POLICY_RULE",
        "trait.publicationprofilecontract": "PROFILE_CONTRACT_PORT",
        "type.appraisalpolicy": "APPRAISAL_DECISION_POLICY",
        "trait.schedulerpolicy": "SCHEDULING_STRATEGY_POLICY",
        "type.assignmentcheckset": "PROSPECTIVE_CHECK_SPECIFICATION",
        "type.exposurecheckset": "PROSPECTIVE_CHECK_SPECIFICATION",
        "type.guardrailcheckset": "PROSPECTIVE_CHECK_SPECIFICATION",
        "type.metricpipelinecheckset": "PROSPECTIVE_CHECK_SPECIFICATION",
        "type.publicationprofileresult": "POLICY_COMPILATION_RESULT",
        "type.qualityrule": "QUALITY_EVALUATION_RULE_SPECIFICATION",
    }
    return exact[symbol_ref]


def policy_occurrence_profiles(symbol_ref: str, occurrences: list[dict[str, Any]]) -> list[dict[str, str]]:
    exact = {
        ("type.qualityrule", "library.method_kernels.data_quality_methods"): "DATA_QUALITY_METHOD_CONSUMER_PROFILE_IMPORTING_AN_EDITIONED_RULE_WITH_METHOD_INPUT_AND_RESULT_BINDINGS",
        ("type.qualityrule", "library.qor.rule_specification_kernel"): "QUALITY_AND_RECONCILIATION_RULE_SPECIFICATION_OWNER_CANDIDATE_WITH_TYPED_SCOPE_PREDICATE_SEVERITY_AND_REMEDIATION_METADATA",
    }
    return [
        {
            "library_ref": occurrence["library_ref"],
            "candidate_policy_profile": exact.get(
                (symbol_ref, occurrence["library_ref"]),
                "CANDIDATE_POLICY_ROLE_REQUIRES_LOCAL_AUTHORITY_SCOPE_EDITION_EVALUATION_AND_EFFECT_ADJUDICATION",
            ),
        }
        for occurrence in occurrences
    ]


def policy_archetype_research() -> list[dict[str, Any]]:
    return [{
        "record_kind": "archetype_semantic_research_candidate",
        "research_id": "research.p1.archetype.policy-scope-profile-edition.v1",
        "edition": 1,
        "archetype_id": "POLICY_SCOPE_PROFILE_AND_EDITION",
        "bounded_finding": "A governed policy or profile is a declaration under a named authority, not a decision or effect. Its semantic definition, immutable edition, applicability scope, evaluation input, evaluation occurrence and result, returned obligation or advice, selected enforcement action, activation state, execution receipt and decision log are separate lifecycle objects. Experiment analysis bindings and scheduling strategies are domain-qualified policy components: the former bind a prespecified analytical question and assumptions, while the latter proposes placement before a separate binding cycle.",
        "required_contract_dimensions": ["policy/profile identity, semantic owner, issuer and immutable edition", "purpose, subject/asset/resource scope and actor roles", "base specifications, imported profiles and extension vocabulary", "rules, constraints, parameters, dependencies and canonical content digest", "combining, precedence, conflict, default and indeterminate semantics", "validity, effective interval, publication, approval, activation, supersession and retirement", "evaluation request/input attributes with authority, freshness and provenance", "applicability, satisfaction, decision and residual/unknown outcomes", "obligations, advice, duties and consequence semantics", "enforcement intent, attempt, effect, receipt and decision-log separation", "compatibility, migration, withdrawal and in-flight decision treatment", "profile validation, conformance, qualification and business acceptance evidence"],
        "non_collapse_laws": ["policy definition is not policy edition", "profile identity is not profile edition", "scope membership is not rule satisfaction", "applicability is not permit", "attribute bag is not policy", "evaluation result is not enforcement", "obligation is not evidence of fulfillment", "decision log is not effect receipt", "downloaded or published is not active", "plan binding is not observed result", "estimand is not estimate", "scheduler selection is not resource binding", "profile conformance is not fitness or acceptance"],
        "source_refs": ARCHETYPE_REFINEMENT_SOURCES["POLICY_SCOPE_PROFILE_AND_EDITION"],
        "authority_limit": "XACML, ODRL, OPA, ICH, CONSORT, W3C PROF and Kubernetes constrain their own policy, profile, analysis and scheduling models. They do not establish one universal policy algebra, choose a SAN owner or authorize a local business effect.",
        "decision": "UNRESOLVED",
        "status": "PRIMARY_RESEARCH_COMPLETE_POLICY_OWNER_AND_OCCURRENCE_ADJUDICATION_REQUIRED",
    }]


def policy_lane_refinement_candidates(
    batches: list[dict[str, Any]],
    symbols: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    batch_by_packet = {packet_ref: row for row in batches for packet_ref in row["packet_refs"]}
    packet_by_symbol = {row["symbol_ref"]: row for row in symbols}
    rows = []
    for symbol_ref, archetype in sorted(POLICY_LANE_EXACT_ARCHETYPES.items()):
        packet = packet_by_symbol[symbol_ref]
        batch = batch_by_packet[packet["packet_id"]]
        rows.append({
            "record_kind": "policy_lane_archetype_refinement_candidate",
            "refinement_id": f"refinement.p1.policy-lane.{symbol_ref.replace('.', '-')}.v1",
            "edition": 1,
            "symbol_packet_ref": packet["packet_id"],
            "batch_ref": batch["batch_id"],
            "symbol_ref": symbol_ref,
            "family_refs": packet["family_refs"],
            "affected_occurrences": packet["occurrences"],
            "represented_occurrence_count": packet["library_count"],
            "candidate_archetype": archetype,
            "candidate_semantic_axis_refs": ARCHETYPE_SEMANTIC_AXES[archetype],
            "source_refs": ARCHETYPE_REFINEMENT_SOURCES[archetype],
            "classification_basis": "BOUNDED_PRIMARY_RESEARCH_PLUS_EXACT_SYMBOL_AND_USE_SITE_ROUTING_NOT_A_SEMANTIC_DECISION",
            "authority_limit": "This correction removes a lexical policy-bucket collapse. It does not establish shared meaning, ownership, import applicability or a public name.",
            "decision": "UNRESOLVED",
            "status": "CANDIDATE_REQUIRES_ARCHETYPE_OWNER_AND_OCCURRENCE_ADJUDICATION",
        })
    return rows


def policy_contract_classification_candidates(
    batches: list[dict[str, Any]],
    symbols: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    packet_by_ref = {row["packet_id"]: row for row in symbols}
    rows = []
    for batch in (row for row in batches if row["research_archetype"] == "POLICY_SCOPE_PROFILE_AND_EDITION"):
        for packet_ref in batch["packet_refs"]:
            packet = packet_by_ref[packet_ref]
            symbol_ref = packet["symbol_ref"]
            role = classify_policy_role(symbol_ref)
            detail = POLICY_ROLE_DETAILS[role]
            rows.append({
                "record_kind": "policy_contract_classification_candidate",
                "candidate_id": f"candidate.p1.policy-contract.{symbol_ref.replace('.', '-')}.v1",
                "edition": 1,
                "research_ref": "research.p1.archetype.policy-scope-profile-edition.v1",
                "research_program_ref": "program.p1.symbol-archetype.policy-scope-profile-and-edition.v1",
                "batch_ref": batch["batch_id"],
                "symbol_packet_ref": packet_ref,
                "symbol_ref": symbol_ref,
                "family_refs": packet["family_refs"],
                "affected_occurrences": packet["occurrences"],
                "represented_occurrence_count": packet["library_count"],
                "candidate_policy_role": role,
                "candidate_semantic_position": detail["semantic_position"],
                "candidate_effect_posture": detail["effect_posture"],
                "occurrence_profile_candidates": policy_occurrence_profiles(symbol_ref, packet["occurrences"]),
                "activation_posture": "UNBOUND_PUBLICATION_APPROVAL_ACTIVATION_AND_OWNER_DECISIONS_REQUIRED",
                "required_owner_decisions": ["semantic owner, issuer and exact identity/edition", "purpose, subject, target and applicability scope", "rules, dependencies, profiles and precedence/default semantics", "validity, publication, approval, activation and retirement lifecycle", "evaluation input, result, obligation/advice and indeterminate semantics", "enforcement, effect, receipt and evidence boundaries", "per-occurrence import, qualified homonym or split", "compatibility, migration and compiler lowering"],
                "non_collapse_laws": ["declaration is not evaluation", "applicability is not satisfaction", "decision is not enforcement", "obligation is not fulfillment", "edition is not activation", "plan is not result", "selection is not binding", "evidence is not acceptance"],
                "classification_basis": "BOUNDED_PRIMARY_RESEARCH_PLUS_SYMBOL_AND_USE_SITE_ROUTING_NOT_AN_AUTHORITY_OR_ACTIVATION_DECISION",
                "authority_limit": "This candidate selects a policy lifecycle role and research profile only; it does not ratify the policy, activate it, decide a request or authorize an effect.",
                "decision": "UNRESOLVED",
                "status": "CANDIDATE_REQUIRES_POLICY_OWNER_AND_OCCURRENCE_ADJUDICATION",
            })
    return sorted(rows, key=lambda row: row["symbol_ref"])


IDENTITY_ROLE_DETAILS: dict[str, dict[str, Any]] = {
    "ACTOR_REFERENCE": {
        "semantic_position": "REFERENCE_TO_AN_ACTOR_IDENTITY_UNDER_A_NAMED_IDENTITY_DOMAIN",
        "candidate_disposition": "FAMILY_SHARED_OWNER_AND_IMPORTS",
        "local_requirements": ["identity-domain and subject reference", "identity epoch or immutable edition", "actor role and authority kept outside the identifier"],
    },
    "LEGAL_HOLD_REFERENCE": {
        "semantic_position": "REFERENCE_TO_A_GOVERNED_HOLD_RECORD_NOT_THE_HOLD_RULE_OR_EFFECT",
        "candidate_disposition": "FAMILY_SHARED_OWNER_AND_IMPORTS",
        "local_requirements": ["hold-owner context and hold-record identity", "hold edition and lifecycle state", "scope, authority and disposition effects resolved separately"],
    },
    "AUDITED_OBJECT_REFERENCE": {
        "semantic_position": "REFERENCE_TO_AN_AUDIT_SUBJECT_UNDER_A_QUALIFIED_OBJECT_IDENTITY_DOMAIN",
        "candidate_disposition": "FAMILY_SHARED_OWNER_AND_IMPORTS",
        "local_requirements": ["object-kind and namespace authority", "object identity epoch or immutable edition", "audit occurrence and observed state kept separate"],
    },
    "POLICY_DEFINITION_REFERENCE": {
        "semantic_position": "REFERENCE_TO_A_POLICY_DEFINITION_OR_EXACT_EDITION",
        "candidate_disposition": "FAMILY_SHARED_OWNER_AND_IMPORTS",
        "local_requirements": ["policy authority and identity", "definition-versus-edition discriminator", "activation and evaluation result kept separate"],
    },
    "PREDICATE_SCHEMA_TYPE_IDENTIFIER": {
        "semantic_position": "IDENTIFIER_FOR_A_PREDICATE_SCHEMA_OR_SEMANTIC_TYPE",
        "candidate_disposition": "FAMILY_SHARED_OWNER_AND_IMPORTS",
        "local_requirements": ["type-identifier scheme and authority", "predicate schema edition and resolution evidence", "predicate truth and appraisal kept separate"],
    },
    "CRYPTOGRAPHIC_PROOF_REFERENCE": {
        "semantic_position": "REFERENCE_TO_A_SPECIFIC_PROOF_OR_SIGNATURE_OCCURRENCE",
        "candidate_disposition": "FAMILY_SHARED_OWNER_AND_IMPORTS",
        "local_requirements": ["proof occurrence identifier and proof-set or chain scope", "cryptosuite and verification-method editions", "verification result and claim truth kept separate"],
    },
    "ATTESTATION_SUBJECT_REPRESENTATION_DIGEST": {
        "semantic_position": "ALGORITHM_QUALIFIED_DIGEST_OVER_AN_EXACT_ATTESTED_REPRESENTATION",
        "candidate_disposition": "FAMILY_SHARED_OWNER_AND_IMPORTS",
        "local_requirements": ["digest algorithm and canonical representation scope", "subject descriptor and media or artifact kind", "business identity, provenance and authenticity kept separate"],
    },
    "SECRET_PROVIDER_VERSION_REFERENCE": {
        "semantic_position": "OPAQUE_PROVIDER_SCOPED_SECRET_VERSION_REFERENCE",
        "candidate_disposition": "FAMILY_SHARED_OWNER_AND_IMPORTS",
        "local_requirements": ["provider and secret identity", "opaque version token and identity epoch", "rotation order, compatibility and active status kept separate"],
    },
    "QUALIFIED_DOMAIN_OBJECT_IDENTITY": {
        "semantic_position": "DOMAIN_QUALIFIED_OBJECT_IDENTITY_WITH_INCOMPATIBLE_PROCESS_AND_STORAGE_PROFILES",
        "candidate_disposition": "QUALIFY_LOCAL_SYMBOL_IDS",
        "local_requirements": ["bounded context, object kind and namespace authority", "identity lifecycle and reuse policy", "process-object and storage-object equality relations must not be unified"],
    },
    "PUBLICATION_PROFILE_IDENTITY": {
        "semantic_position": "IDENTITY_OF_A_CROSS_METHOD_PUBLICATION_PROFILE_DEFINITION",
        "candidate_disposition": "CANONICAL_SHARED_OWNER_AND_IMPORTS",
        "local_requirements": ["publication-profile semantic owner and namespace", "profile definition identity versus immutable edition", "forecast and spatial refinements remain explicit"],
    },
    "RUNTIME_ATTEMPT_OCCURRENCE_IDENTITY": {
        "semantic_position": "IDENTITY_OF_ONE_RUNTIME_ATTEMPT_OCCURRENCE",
        "candidate_disposition": "FAMILY_SHARED_OWNER_AND_IMPORTS",
        "local_requirements": ["parent work and retry lineage", "attempt identity namespace and identity epoch", "trace, run, task, effect and idempotency identities kept separate"],
    },
}


def classify_identity_role(symbol_ref: str) -> str:
    return {
        "type.actor_ref": "ACTOR_REFERENCE",
        "type.legal_hold_ref": "LEGAL_HOLD_REFERENCE",
        "type.object_ref": "AUDITED_OBJECT_REFERENCE",
        "type.policy_ref": "POLICY_DEFINITION_REFERENCE",
        "type.predicate_type": "PREDICATE_SCHEMA_TYPE_IDENTIFIER",
        "type.signature_ref": "CRYPTOGRAPHIC_PROOF_REFERENCE",
        "type.subject_digest": "ATTESTATION_SUBJECT_REPRESENTATION_DIGEST",
        "type.version_ref": "SECRET_PROVIDER_VERSION_REFERENCE",
        "type.objectidentity": "QUALIFIED_DOMAIN_OBJECT_IDENTITY",
        "type.publicationprofileid": "PUBLICATION_PROFILE_IDENTITY",
        "type.attemptid": "RUNTIME_ATTEMPT_OCCURRENCE_IDENTITY",
    }[symbol_ref]


def identity_occurrence_profiles(symbol_ref: str, occurrences: list[dict[str, Any]]) -> list[dict[str, str]]:
    profiles = []
    for occurrence in occurrences:
        library_ref = occurrence["library_ref"]
        if symbol_ref == "type.objectidentity" and library_ref == "library.method_kernels.process_event_projection":
            profile = "PROCESS_EVENT_OBJECT_IDENTITY_BOUND_TO_EVENT_DATA_EDITION_OBJECT_TYPE_AND_SOURCE_NAMESPACE"
        elif symbol_ref == "type.objectidentity" and library_ref == "library.persistence.storage_identity":
            profile = "STORAGE_OBJECT_IDENTITY_BOUND_TO_STORAGE_NAMESPACE_KEY_AND_VERSION_OR_GENERATION"
        elif symbol_ref == "type.publicationprofileid" and library_ref.startswith("library.forecast."):
            profile = "SHARED_PUBLICATION_PROFILE_IDENTITY_WITH_FORECAST_PUBLICATION_REFINEMENT"
        elif symbol_ref == "type.publicationprofileid" and library_ref.startswith("library.spatial_result."):
            profile = "SHARED_PUBLICATION_PROFILE_IDENTITY_WITH_SPATIAL_RESULT_REFINEMENT"
        else:
            profile = "CANDIDATE_SHARED_ROLE_REQUIRES_LOCAL_IDENTITY_SCOPE_AND_LIFECYCLE_ADJUDICATION"
        profiles.append({"library_ref": library_ref, "candidate_identity_profile": profile})
    return profiles


def identity_archetype_research() -> list[dict[str, Any]]:
    return [{
        "record_kind": "archetype_semantic_research_candidate",
        "research_id": "research.p1.archetype.identity-reference-version-digest.v1",
        "edition": 1,
        "archetype_id": "IDENTITY_REFERENCE_VERSION_AND_DIGEST",
        "bounded_finding": "An identifier distinguishes a subject only inside an explicit scheme, namespace, authority, scope and identity epoch. Identifier value, reference, locator, resolved representation, alias assertion, semantic subject, immutable edition, version relation, canonical representation and digest evidence are separate objects. UUID or digest uniqueness does not supply business meaning, authenticity, authority or cross-context equality; version precedence does not establish compatibility or active status.",
        "required_contract_dimensions": ["semantic subject kind and bounded-context owner", "identifier scheme, namespace authority, scope or tenant and canonical lexical form", "subject identity epoch, reuse prohibition and tombstone policy", "identifier equality versus owner-adjudicated subject-equivalence relation", "reference direction, resolution method, resolver edition and unresolved or ambiguous outcome", "locator and retrieved representation kept separate from subject identity", "alias, alternate, specialization, merge, split and supersession provenance", "definition identity, immutable edition identity and version-family relationship", "version token syntax, ordering policy, compatibility claims and active/current state", "canonicalization profile, exact representation scope, digest algorithm and digest bytes", "authority, controller, role, capability and authorization kept outside identifier equality", "migration, external-reference disposition and evidence invalidation"],
        "non_collapse_laws": ["identifier is not subject", "reference is not resolved object", "identifier equality is not cross-scheme subject equality", "locator equality is not resource equality", "UUID uniqueness is not semantic identity or authenticity", "controller is not subject or authorization", "alias assertion is not accepted equivalence", "definition identity is not edition identity", "version precedence is not compatibility, currency or activation", "canonical bytes are not canonical meaning", "digest equality is not business-semantic equality, provenance or truth", "actor identity is not role or authority", "attempt identity is not job, trace, idempotency or effect identity", "process object identity is not storage object identity", "predicate type identifier is not predicate truth", "proof reference is not a verified proof"],
        "source_refs": ARCHETYPE_REFINEMENT_SOURCES["IDENTITY_REFERENCE_VERSION_AND_DIGEST"],
        "authority_limit": "URI, UUID, DID, named-information, canonicalization, provenance, versioning, attestation and tracing specifications constrain their own identifier domains. They do not select a SAN semantic owner, prove two domain subjects equal, authorize an actor or ratify any cross-context import.",
        "decision": "UNRESOLVED",
        "status": "PRIMARY_RESEARCH_COMPLETE_IDENTITY_OWNER_AND_OCCURRENCE_ADJUDICATION_REQUIRED",
    }]


def identity_contract_classification_candidates(
    batches: list[dict[str, Any]],
    symbols: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    packet_by_ref = {row["packet_id"]: row for row in symbols}
    rows = []
    for batch in (row for row in batches if row["research_archetype"] == "IDENTITY_REFERENCE_VERSION_AND_DIGEST"):
        for packet_ref in batch["packet_refs"]:
            packet = packet_by_ref[packet_ref]
            symbol_ref = packet["symbol_ref"]
            role = classify_identity_role(symbol_ref)
            detail = IDENTITY_ROLE_DETAILS[role]
            source_refs = list(ARCHETYPE_REFINEMENT_SOURCES["IDENTITY_REFERENCE_VERSION_AND_DIGEST"])
            rows.append({
                "record_kind": "identity_contract_classification_candidate",
                "candidate_id": f"candidate.p1.identity-contract.{symbol_ref.replace('.', '-')}.v1",
                "edition": 1,
                "research_ref": "research.p1.archetype.identity-reference-version-digest.v1",
                "research_program_ref": "program.p1.symbol-archetype.identity-reference-version-and-digest.v1",
                "batch_ref": batch["batch_id"],
                "symbol_packet_ref": packet_ref,
                "symbol_ref": symbol_ref,
                "family_refs": packet["family_refs"],
                "affected_occurrences": packet["occurrences"],
                "represented_occurrence_count": packet["library_count"],
                "candidate_identity_role": role,
                "candidate_semantic_position": detail["semantic_position"],
                "candidate_disposition_hypothesis": detail["candidate_disposition"],
                "local_identity_requirements": detail["local_requirements"],
                "occurrence_profile_candidates": identity_occurrence_profiles(symbol_ref, packet["occurrences"]),
                "source_refs": source_refs,
                "required_owner_decisions": ["semantic subject kind and bounded-context owner", "scheme, namespace authority, scope and canonical lexical form", "identity epoch, lifecycle and identifier-reuse policy", "exact equality, alias, alternate and specialization relations", "reference resolution and unresolved or ambiguous outcomes", "definition, edition, version, current and compatibility separation", "canonicalization and digest representation scope", "per-occurrence shared import, qualified homonym or split", "migration, tombstone and external-reference disposition"],
                "non_collapse_laws": ["identifier is not subject", "reference is not object", "UUID is not business identity", "digest is not semantic equality", "version is not compatibility", "actor identity is not authority", "attempt identity is not effect identity"],
                "classification_basis": "BOUNDED_PRIMARY_RESEARCH_PLUS_SYMBOL_AND_USE_SITE_ROUTING_NOT_AN_IDENTITY_OR_OWNER_DECISION",
                "authority_limit": "This candidate selects an identity lifecycle role and a falsifiable disposition hypothesis only; it does not establish subject equality, shared ownership, authority, compatibility or a valid resolution.",
                "decision": "UNRESOLVED",
                "status": "CANDIDATE_REQUIRES_IDENTITY_OWNER_AND_OCCURRENCE_ADJUDICATION",
            })
    return sorted(rows, key=lambda row: row["symbol_ref"])


AUTHORITY_ROLE_DETAILS: dict[str, dict[str, Any]] = {
    "TYPED_ASSURANCE_PROFILE": {
        "semantic_position": "RISK_AND_FUNCTION_SCOPED_ASSURANCE_PROFILE",
        "candidate_disposition": "FAMILY_SHARED_OWNER_AND_IMPORTS",
        "local_requirements": ["assurance function and profile edition", "service, user group, threat and risk context", "identity proofing, authentication and federation levels kept distinct"],
    },
    "CREDENTIAL_REFERENCE": {
        "semantic_position": "REFERENCE_TO_AN_ISSUED_CREDENTIAL_UNDER_AN_ISSUER_AND_PURPOSE",
        "candidate_disposition": "FAMILY_SHARED_OWNER_AND_IMPORTS",
        "local_requirements": ["credential kind issuer subject audience and purpose", "issuance, validity, suspension and revocation state", "credential possession, authentication and authorization kept separate"],
    },
    "ISOLATION_PROFILE_CLASS": {
        "semantic_position": "DECLARED_MULTI_CONTROL_ISOLATION_PROFILE_NOT_AN_ASSURANCE_RESULT",
        "candidate_disposition": "FAMILY_SHARED_OWNER_AND_IMPORTS",
        "local_requirements": ["threat and tenant model", "control-plane, compute, network, storage and side-channel dimensions", "deployed-control and conformance evidence"],
    },
    "PROVIDER_SCOPED_KEY_REFERENCE": {
        "semantic_position": "REFERENCE_TO_KEY_MATERIAL_UNDER_PROVIDER_KEYSET_AND_USAGE_CONTEXT",
        "candidate_disposition": "FAMILY_SHARED_OWNER_AND_IMPORTS",
        "local_requirements": ["provider key set key type and identity epoch", "allowed purpose algorithm and cryptoperiod", "possession validity compromise and authorization kept separate"],
    },
    "POLICY_OBLIGATION_DECLARATION": {
        "semantic_position": "POLICY_RESULT_DUTY_OR_OBLIGATION_REQUIRING_SEPARATE_FULFILLMENT",
        "candidate_disposition": "FAMILY_SHARED_OWNER_AND_IMPORTS",
        "local_requirements": ["issuing policy decision and obligated party", "action resource deadline and consequence", "enforcement attempt effect and fulfillment evidence"],
    },
    "AUTHORIZATION_REQUEST_TUPLE": {
        "semantic_position": "POLICY_EVALUATION_INPUT_OVER_PRINCIPAL_ACTION_RESOURCE_AND_ENVIRONMENT",
        "candidate_disposition": "FAMILY_SHARED_OWNER_AND_IMPORTS",
        "local_requirements": ["principal, action and resource identity editions", "environment attributes purpose and data cut", "decision, enforcement and effect kept separate"],
    },
    "PRINCIPAL_REFERENCE": {
        "semantic_position": "REFERENCE_TO_A_PRINCIPAL_IN_AN_AUTHORITY_DOMAIN",
        "candidate_disposition": "FAMILY_SHARED_OWNER_AND_IMPORTS",
        "local_requirements": ["principal kind issuer or trust domain and identity epoch", "authentication context and freshness", "roles attributes delegation and authorization kept separate"],
    },
    "OPAQUE_SECRET_PROVIDER_HANDLE": {
        "semantic_position": "PROVIDER_AND_SESSION_SCOPED_HANDLE_TO_SECRET_MATERIAL",
        "candidate_disposition": "FAMILY_SHARED_OWNER_AND_IMPORTS",
        "local_requirements": ["provider session and secret identity", "handle lifetime accessibility and version", "secret bytes exposure and permitted operations kept separate"],
    },
    "TENANT_SCOPE_REFERENCE": {
        "semantic_position": "REFERENCE_TO_A_TENANT_SCOPE_UNDER_A_NAMED_TENANCY_MODEL",
        "candidate_disposition": "FAMILY_SHARED_OWNER_AND_IMPORTS",
        "local_requirements": ["tenant kind authority hierarchy and lifecycle", "resource and identity scope mappings", "namespace, account, project and isolation boundary kept separate"],
    },
    "MONOTONIC_FENCING_ORDER_WITNESS": {
        "semantic_position": "MONOTONIC_COORDINATION_EPOCH_PRESENTED_TO_EFFECT_SINKS",
        "candidate_disposition": "CANONICAL_SHARED_OWNER_AND_IMPORTS",
        "local_requirements": ["issuing coordination authority and monotonic order domain", "protected resource and effect-sink comparison rule", "lease ownership commit success and stale-writer rejection evidence kept separate"],
    },
}


def classify_authority_role(symbol_ref: str) -> str:
    return {
        "type.assurance_level": "TYPED_ASSURANCE_PROFILE",
        "type.credential_ref": "CREDENTIAL_REFERENCE",
        "type.isolation_class": "ISOLATION_PROFILE_CLASS",
        "type.key_ref": "PROVIDER_SCOPED_KEY_REFERENCE",
        "type.obligation": "POLICY_OBLIGATION_DECLARATION",
        "type.principal_action_resource": "AUTHORIZATION_REQUEST_TUPLE",
        "type.principal_ref": "PRINCIPAL_REFERENCE",
        "type.secret_handle": "OPAQUE_SECRET_PROVIDER_HANDLE",
        "type.tenant_ref": "TENANT_SCOPE_REFERENCE",
        "type.fencingtoken": "MONOTONIC_FENCING_ORDER_WITNESS",
    }[symbol_ref]


def authority_occurrence_profiles(symbol_ref: str, occurrences: list[dict[str, Any]]) -> list[dict[str, str]]:
    rows = []
    for occurrence in occurrences:
        library_ref = occurrence["library_ref"]
        if symbol_ref == "type.fencingtoken" and library_ref == "library.runtime-resource.fencing-token":
            profile = "CANONICAL_FENCING_TOKEN_ISSUANCE_ORDER_AND_VALIDATION_OWNER_CANDIDATE"
        elif symbol_ref == "type.fencingtoken" and library_ref == "library.persistence.cache_fill_coordination":
            profile = "PERSISTENCE_CACHE_FILL_IMPORT_REQUIRING_EFFECT_SINK_STALE_TOKEN_REJECTION"
        else:
            profile = "CANDIDATE_FAMILY_SHARED_ROLE_REQUIRES_LOCAL_AUTHORITY_SCOPE_AND_LIFECYCLE_ADJUDICATION"
        rows.append({"library_ref": library_ref, "candidate_authority_profile": profile})
    return rows


def authority_archetype_research() -> list[dict[str, Any]]:
    return [{
        "record_kind": "archetype_semantic_research_candidate",
        "research_id": "research.p1.archetype.authority-security-credential.v1",
        "edition": 1,
        "archetype_id": "AUTHORITY_SECURITY_AND_CREDENTIAL",
        "bounded_finding": "Identity, authentication, credential issuance, authorization evaluation, obligation, enforcement, external effect and acceptance are separate authority stages. Every security-bearing value must bind its issuer or trust domain, exact subject and purpose, scope and audience, validity and revocation state, delegation or attenuation chain, relying-party policy and evidence cut. Assurance and isolation are typed profiles with dimensions and conformance evidence, not universal scalar labels. A fencing token is an ordered coordination witness only when every protected effect sink compares it in the same monotonic domain.",
        "required_contract_dimensions": ["principal, actor, subject, resource and tenant identity domains", "issuer, controller, resource owner, authorization server, relying party and enforcement-point roles", "credential, key, secret-handle and token kind plus exact issuer/provider edition", "purpose, audience, resource, action and granted scope", "identity proofing, authentication, federation and domain-specific assurance dimensions", "delegation, attenuation, impersonation and separation-of-duty limits", "issuance, activation, validity, expiry, suspension, revocation and propagation state", "policy request, evaluation occurrence, decision, obligation or advice and indeterminate outcome", "enforcement intent, attempt, partial or unknown completion, external effect and receipt", "tenant and isolation profile across control, compute, network, storage and side-channel dimensions", "key purpose, cryptoperiod, rotation, compromise and provider-handle lifetime", "fencing-token authority, monotonic order domain, sink comparison and stale-writer evidence", "audit, provenance, disclosure, appeal, compatibility and migration"],
        "non_collapse_laws": ["identity is not authentication", "authentication is not authorization", "credential is not principal", "credential possession is not permitted use", "authorization grant is not access token", "requested scope is not granted or effective scope", "policy evaluation is not enforcement", "obligation is not fulfillment", "revocation request is not globally propagated revocation", "assurance level is not a universal security score", "tenant is not namespace or isolation boundary", "isolation profile is not deployed isolation proof", "key reference is not key possession, validity or authorized use", "secret handle is not secret identity or secret bytes", "fencing token order is not effect exclusion unless the sink enforces it", "permit decision is not completed business effect"],
        "source_refs": ARCHETYPE_REFINEMENT_SOURCES["AUTHORITY_SECURITY_AND_CREDENTIAL"],
        "authority_limit": "NIST, XACML, OAuth, JWK, PKCS #11, VC Data Integrity, Kubernetes, SPIFFE and Chubby constrain their own assurance, authorization, credential, provider-handle, isolation, identity and fencing models. They do not select a SAN authority, grant access, prove deployed isolation or ratify a cross-context security carrier.",
        "decision": "UNRESOLVED",
        "status": "PRIMARY_RESEARCH_COMPLETE_AUTHORITY_OWNER_AND_OCCURRENCE_ADJUDICATION_REQUIRED",
    }]


def authority_contract_classification_candidates(
    batches: list[dict[str, Any]],
    symbols: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    packet_by_ref = {row["packet_id"]: row for row in symbols}
    rows = []
    for batch in (row for row in batches if row["research_archetype"] == "AUTHORITY_SECURITY_AND_CREDENTIAL"):
        for packet_ref in batch["packet_refs"]:
            packet = packet_by_ref[packet_ref]
            symbol_ref = packet["symbol_ref"]
            role = classify_authority_role(symbol_ref)
            detail = AUTHORITY_ROLE_DETAILS[role]
            rows.append({
                "record_kind": "authority_contract_classification_candidate",
                "candidate_id": f"candidate.p1.authority-contract.{symbol_ref.replace('.', '-')}.v1",
                "edition": 1,
                "research_ref": "research.p1.archetype.authority-security-credential.v1",
                "research_program_ref": "program.p1.symbol-archetype.authority-security-and-credential.v1",
                "batch_ref": batch["batch_id"],
                "symbol_packet_ref": packet_ref,
                "symbol_ref": symbol_ref,
                "family_refs": packet["family_refs"],
                "affected_occurrences": packet["occurrences"],
                "represented_occurrence_count": packet["library_count"],
                "candidate_authority_role": role,
                "candidate_semantic_position": detail["semantic_position"],
                "candidate_disposition_hypothesis": detail["candidate_disposition"],
                "local_authority_requirements": detail["local_requirements"],
                "occurrence_profile_candidates": authority_occurrence_profiles(symbol_ref, packet["occurrences"]),
                "source_refs": list(ARCHETYPE_REFINEMENT_SOURCES["AUTHORITY_SECURITY_AND_CREDENTIAL"]),
                "required_owner_decisions": ["semantic owner and exact security-bearing object kind", "issuer controller subject audience purpose action and resource roles", "scope delegation attenuation and separation-of-duty laws", "assurance or isolation profile dimensions and evidence", "issuance validity expiry suspension revocation and propagation", "evaluation obligation enforcement effect and receipt separation", "provider handle or key lifecycle and permitted use", "per-occurrence import qualified homonym or split", "migration external-reference and in-flight authorization disposition"],
                "non_collapse_laws": ["identity is not authentication", "authentication is not authorization", "credential is not principal", "decision is not enforcement", "obligation is not fulfillment", "revocation request is not propagated revocation", "tenant is not isolation", "fencing token is not lock ownership or effect completion"],
                "classification_basis": "BOUNDED_PRIMARY_RESEARCH_PLUS_SYMBOL_AND_USE_SITE_ROUTING_NOT_AN_AUTHORIZATION_OR_SECURITY_DECISION",
                "authority_limit": "This candidate selects an authority lifecycle role and falsifiable disposition hypothesis only; it grants no identity, credential validity, authorization, isolation assurance, effect or acceptance.",
                "decision": "UNRESOLVED",
                "status": "CANDIDATE_REQUIRES_AUTHORITY_OWNER_AND_OCCURRENCE_ADJUDICATION",
            })
    return sorted(rows, key=lambda row: row["symbol_ref"])


REPRESENTATION_ROLE_DETAILS: dict[str, dict[str, Any]] = {
    "DOCUMENT_DERIVED_VIEW": {
        "semantic_position": "PROVENANCE_BOUND_DERIVED_VIEW_OVER_A_DOCUMENT_REPRESENTATION",
        "candidate_disposition": "FAMILY_SHARED_OWNER_AND_IMPORTS",
        "local_requirements": ["source document artifact and representation edition", "page, region, coordinate and reading-order systems", "render, OCR, layout and extraction method editions", "confidence, omissions, normalization and loss report"],
    },
    "DECODER_EXECUTION_OUTCOME": {
        "semantic_position": "CODEC_EXECUTION_OUTCOME_FROM_BYTES_TO_A_TYPED_REPRESENTATION",
        "candidate_disposition": "CROSS_FAMILY_SHARED_ENVELOPE_AND_LOCAL_PROFILES",
        "local_requirements": ["source byte sequence and media or wire type", "codec, schema, dialect and profile editions", "stream state, bytes consumed and unconsumed remainder", "well-formedness, validity, expectedness, warnings and unknown extensions"],
    },
    "ENCODER_EXECUTION_OUTCOME": {
        "semantic_position": "CODEC_EXECUTION_OUTCOME_FROM_A_TYPED_VALUE_TO_BYTES",
        "candidate_disposition": "CROSS_FAMILY_SHARED_ENVELOPE_AND_LOCAL_PROFILES",
        "local_requirements": ["source semantic carrier and edition", "codec, schema, canonicalization and target profile editions", "produced bytes, warnings, substitutions and omitted fields", "determinism, canonicality and round-trip claim kept explicit"],
    },
    "PROFILED_FRAME_ENVELOPE": {
        "semantic_position": "BOUNDED_SEQUENCE_UNIT_UNDER_AN_EXACT_FRAMING_PROFILE",
        "candidate_disposition": "CANONICAL_SHARED_OWNER_AND_PROFILED_IMPORTS",
        "local_requirements": ["framing profile, protocol and edition", "header fields, payload kind, length units and maximums", "stream or channel association, ordering and continuation rules", "unknown types, malformed boundaries, truncation and state-transition handling"],
    },
    "FORMULA_SYNTAX_TREE": {
        "semantic_position": "EDITION_BOUND_FORMULA_SYNTAX_TREE_WITH_SEPARATE_SEMANTIC_BINDING",
        "candidate_disposition": "CANONICAL_SHARED_OWNER_AND_IMPORTS",
        "local_requirements": ["formula-language grammar and AST schema editions", "source locations, lexical preservation and normalization", "name, unit, type and function-registry bindings", "evaluation semantics, provenance and equivalence relation"],
    },
    "QUALIFIED_MANIFEST_GRAPH": {
        "semantic_position": "PROFILE_QUALIFIED_MEMBERSHIP_AND_METADATA_GRAPH",
        "candidate_disposition": "QUALIFY_LOCAL_SYMBOL_IDS",
        "local_requirements": ["manifest kind, profile and schema edition", "root subject, member identity and inclusion relation", "snapshot or observation cut and completeness claim", "external references, tombstones, integrity and provenance"],
    },
    "POLICY_REQUEST_ATTRIBUTE_MULTISET": {
        "semantic_position": "TYPED_MULTISET_OF_POLICY_REQUEST_ATTRIBUTES_NOT_A_POLICY_OR_DECISION",
        "candidate_disposition": "FAMILY_SHARED_OWNER_AND_IMPORTS",
        "local_requirements": ["attribute category, identifier, datatype and issuer", "subject, resource, action, environment and purpose scope", "multiplicity, order, equality and missing-value semantics", "provenance, freshness, trust and indeterminate handling"],
    },
}


def classify_representation_role(symbol_ref: str) -> str:
    return {
        "type.documentview": "DOCUMENT_DERIVED_VIEW",
        "type.decoderesult": "DECODER_EXECUTION_OUTCOME",
        "type.encoderesult": "ENCODER_EXECUTION_OUTCOME",
        "type.frame": "PROFILED_FRAME_ENVELOPE",
        "type.formulaast": "FORMULA_SYNTAX_TREE",
        "type.manifest": "QUALIFIED_MANIFEST_GRAPH",
        "type.attribute_bag": "POLICY_REQUEST_ATTRIBUTE_MULTISET",
    }[symbol_ref]


def representation_occurrence_profiles(symbol_ref: str, occurrences: list[dict[str, Any]]) -> list[dict[str, str]]:
    profiles = []
    exact = {
        ("type.documentview", "library.method_kernels.document_classification_methods"): "DOCUMENT_CLASSIFICATION_VIEW_WITH_EXACT_RENDER_OCR_LAYOUT_AND_LABEL_PROVENANCE",
        ("type.documentview", "library.method_kernels.document_information_extraction"): "DOCUMENT_EXTRACTION_VIEW_WITH_PAGE_REGION_READING_ORDER_AND_SOURCE_ANCHORS",
        ("type.decoderesult", "library.cp.protocol_codec"): "PROTOCOL_DECODE_OUTCOME_WITH_WIRE_EDITION_STREAM_STATE_AND_UNKNOWN_FIELD_POLICY",
        ("type.decoderesult", "library.persistence.metadata_codec_spi"): "METADATA_DECODE_OUTCOME_WITH_TABLE_FORMAT_SCHEMA_AND_EXTENSION_POLICY",
        ("type.encoderesult", "library.cp.protocol_codec"): "PROTOCOL_ENCODE_OUTCOME_WITH_WIRE_EDITION_CANONICALITY_AND_DOWNGRADE_LOSS",
        ("type.encoderesult", "library.persistence.metadata_codec_spi"): "METADATA_ENCODE_OUTCOME_WITH_TABLE_FORMAT_EDITION_CANONICALITY_AND_UNKNOWN_PRESERVATION",
        ("type.frame", "library.san_framing"): "CANONICAL_FRAME_BOUNDARY_AND_LIMIT_OWNER_CANDIDATE_WITHOUT_PROTOCOL_SEMANTICS",
        ("type.frame", "library.cp.protocol_codec"): "PROTOCOL_CODEC_IMPORT_REQUIRING_EXACT_FRAME_PROFILE_TYPE_FLAGS_STREAM_AND_STATE_RULES",
        ("type.formulaast", "library.method_kernels.formula_algebra"): "CANONICAL_FORMULA_SYNTAX_AND_SEMANTIC_BINDING_OWNER_CANDIDATE",
        ("type.formulaast", "library.lpe.formula-provenance"): "LINEAGE_IMPORT_WITH_SOURCE_SPANS_BINDING_EDITION_AND_DERIVATION_PROVENANCE",
        ("type.manifest", "library.lpe.research-object"): "RESEARCH_OBJECT_MANIFEST_QUALIFIED_BY_RO_CRATE_LIKE_ROOT_DATA_AND_CONTEXT_GRAPH",
        ("type.manifest", "library.persistence.snapshot_graph"): "STORAGE_SNAPSHOT_MANIFEST_QUALIFIED_BY_TABLE_SNAPSHOT_MEMBERSHIP_AND_SEQUENCE",
        ("type.attribute_bag", "library.spt.policy_evaluator"): "POLICY_EVALUATION_REQUEST_ATTRIBUTE_MULTISET_WITH_MISSING_AND_INDETERMINATE_SEMANTICS",
        ("type.attribute_bag", "library.spt.policy_enforcer"): "ENFORCEMENT_CONTEXT_ATTRIBUTE_MULTISET_WITH_OBSERVED_FRESHNESS_AND_DECISION_BINDING",
    }
    for occurrence in occurrences:
        library_ref = occurrence["library_ref"]
        profiles.append({
            "library_ref": library_ref,
            "candidate_representation_profile": exact.get(
                (symbol_ref, library_ref),
                "CANDIDATE_SHARED_REPRESENTATION_ROLE_REQUIRES_LOCAL_PROFILE_LOSS_AND_COMPATIBILITY_ADJUDICATION",
            ),
        })
    return profiles


def representation_archetype_research() -> list[dict[str, Any]]:
    return [{
        "record_kind": "archetype_semantic_research_candidate",
        "research_id": "research.p1.archetype.representation-codec-schema-layout.v1",
        "edition": 1,
        "archetype_id": "REPRESENTATION_CODEC_SCHEMA_AND_LAYOUT",
        "bounded_finding": "A semantic object, one of its representations, a schema or dialect, a framing profile, a frame occurrence, a codec execution, a normalized or canonical form, a digest, a derived document view and a round-trip claim are separate objects. Decode success must distinguish byte consumption, well-formedness, format validity and application expectedness. Encode success must state substitutions, omissions, extension handling and canonicality. A generic frame may own bounded sequence mechanics, but payload type, flags, stream association, size limits and state effects remain protocol-profile semantics. Compatibility is directional and binds writer, reader, schema, profile and edition. AST equality is syntactic unless a formula-semantic equivalence is separately proved. The unqualified name Manifest is a demonstrated homonym between research-object metadata graphs and storage snapshot membership graphs.",
        "required_contract_dimensions": ["semantic subject kind, owner and immutable edition", "representation kind, media or wire type and representation identity", "schema, dialect, vocabulary, profile and codec editions", "framing profile, header, payload kind, length unit, maximum, stream association and continuation rules", "encoder or decoder execution occurrence and implementation offer", "stream state, consumed bytes, remainder and terminal knowledge", "well-formedness, format validity, application expectedness and domain acceptance", "unknown field, extension, duplicate, order and default handling", "character encoding, BOM and Unicode normalization profile", "loss, substitution, omission, precision and residual report", "deterministic or canonical encoding profile and exact digest scope", "directional writer-reader compatibility and migration matrix", "round-trip relation, source-target editions and equivalence oracle", "document page, region, coordinate, reading-order and derived OCR/layout provenance", "formula grammar, AST schema, semantic bindings and evaluation edition", "manifest profile, root subject, membership relation, cut and completeness claim"],
        "non_collapse_laws": ["semantic object is not representation", "byte identity is not semantic identity", "frame is not message, stream, transport packet or business event", "generic frame boundary is not protocol payload semantics", "parse success is not format validity", "format validity is not application expectedness or domain acceptance", "decode result is not round-trip proof", "encode success is not losslessness or canonicality", "canonical representation is not canonical meaning or truth", "Unicode canonical equivalence is not compatibility equivalence or business equality", "AST structural equality is not formula semantic equivalence", "document bytes are not a derived DocumentView", "OCR text and layout are derived evidence not observed source truth", "manifest inventory is not necessarily complete or current", "research-object manifest is not storage snapshot manifest", "attribute bag is not policy, decision or enforcement", "backward compatibility is not forward or bidirectional compatibility"],
        "source_refs": ARCHETYPE_REFINEMENT_SOURCES["REPRESENTATION_CODEC_SCHEMA_AND_LAYOUT"],
        "authority_limit": "CBOR, WHATWG Encoding, Unicode normalization, OpenFormula, RO-Crate, IIIF, HTTP/2 framing, JSON Schema, JCS, Iceberg and XACML constrain their own representation domains. They do not select SAN semantic owners, prove lossless translation, establish domain acceptance or unify homonymous carriers.",
        "decision": "UNRESOLVED",
        "status": "PRIMARY_RESEARCH_COMPLETE_REPRESENTATION_OWNER_AND_OCCURRENCE_ADJUDICATION_REQUIRED",
    }]


def representation_contract_classification_candidates(
    batches: list[dict[str, Any]],
    symbols: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    packet_by_ref = {row["packet_id"]: row for row in symbols}
    rows = []
    for batch in (row for row in batches if row["research_archetype"] == "REPRESENTATION_CODEC_SCHEMA_AND_LAYOUT"):
        for packet_ref in batch["packet_refs"]:
            packet = packet_by_ref[packet_ref]
            symbol_ref = packet["symbol_ref"]
            role = classify_representation_role(symbol_ref)
            detail = REPRESENTATION_ROLE_DETAILS[role]
            rows.append({
                "record_kind": "representation_contract_classification_candidate",
                "candidate_id": f"candidate.p1.representation-contract.{symbol_ref.replace('.', '-')}.v1",
                "edition": 1,
                "research_ref": "research.p1.archetype.representation-codec-schema-layout.v1",
                "research_program_ref": "program.p1.symbol-archetype.representation-codec-schema-and-layout.v1",
                "batch_ref": batch["batch_id"],
                "symbol_packet_ref": packet_ref,
                "symbol_ref": symbol_ref,
                "family_refs": packet["family_refs"],
                "affected_occurrences": packet["occurrences"],
                "represented_occurrence_count": packet["library_count"],
                "candidate_representation_role": role,
                "candidate_semantic_position": detail["semantic_position"],
                "candidate_disposition_hypothesis": detail["candidate_disposition"],
                "local_representation_requirements": detail["local_requirements"],
                "occurrence_profile_candidates": representation_occurrence_profiles(symbol_ref, packet["occurrences"]),
                "source_refs": list(ARCHETYPE_REFINEMENT_SOURCES["REPRESENTATION_CODEC_SCHEMA_AND_LAYOUT"]),
                "required_owner_decisions": ["semantic subject and representation owners", "schema dialect profile codec framing and canonicalization editions", "frame boundary payload type stream association size and malformed-input rules", "well-formed validity expectedness and domain-acceptance boundaries", "unknown extension default order and duplicate handling", "loss precision normalization and residual semantics", "directional compatibility and exact round-trip equivalence relation", "per-occurrence import qualified homonym or split", "migration external-reference and historical-replay disposition"],
                "non_collapse_laws": ["object is not representation", "frame is not message stream packet or event", "generic framing is not protocol payload semantics", "decode success is not semantic acceptance", "encode success is not losslessness", "canonical bytes are not semantic truth", "AST equality is not formula equivalence", "derived document view is not source fact", "manifest is not one universal semantic type", "attribute bag is not policy or decision"],
                "classification_basis": "BOUNDED_PRIMARY_RESEARCH_PLUS_SYMBOL_AND_USE_SITE_ROUTING_NOT_A_REPRESENTATION_OWNER_OR_COMPATIBILITY_DECISION",
                "authority_limit": "This candidate selects a representation lifecycle role and falsifiable disposition hypothesis only; it does not prove validity, losslessness, canonicality, compatibility, semantic equality or domain acceptance.",
                "decision": "UNRESOLVED",
                "status": "CANDIDATE_REQUIRES_REPRESENTATION_OWNER_AND_OCCURRENCE_ADJUDICATION",
            })
    return sorted(rows, key=lambda row: row["symbol_ref"])


RESOURCE_ROLE_DETAILS: dict[str, dict[str, Any]] = {
    "RESERVATION_LIFECYCLE_PORT": {
        "semantic_position": "REQUEST_OR_TRANSITION_PORT_IN_A_QUALIFIED_RESOURCE_RESERVATION_LIFECYCLE",
        "candidate_disposition": "QUALIFY_LOCAL_SYMBOL_IDS",
        "local_requirements": ["resource vector, units, pool and authority", "request, hold, commitment, allocation and use identities", "validity interval, expiry, renewal, release and reclaim semantics", "atomicity, partial grant, concurrency, idempotency and receipt"],
    },
    "QUALIFIED_BUFFER_RESOURCE": {
        "semantic_position": "RESOURCE_OR_CAPACITY_OBJECT_REQUIRING_EXACT_BUFFER_KIND",
        "candidate_disposition": "QUALIFY_LOCAL_SYMBOL_IDS",
        "local_requirements": ["logical queue capacity versus physical memory-region kind", "count, byte, element, alignment and ownership units", "overflow, backpressure, spill, drop, refusal and reclamation policy", "lifetime, mutability, sharing, usage accounting and evidence"],
    },
    "FINITE_ANALYTICAL_RESOURCE_BUDGET": {
        "semantic_position": "DECLARED_FINITE_BUDGET_VECTOR_FOR_A_PURE_ANALYTICAL_OR_COMPILATION_OCCURRENCE",
        "candidate_disposition": "FAMILY_SHARED_OWNER_AND_IMPORTS",
        "local_requirements": ["budget dimensions, units and subject occurrence", "hard, soft, advisory or weighted enforcement posture", "consumption accounting, checkpoints and remaining budget", "exhaustion, partial artifact, cancellation and reproducibility receipt"],
    },
}


def classify_resource_role(symbol_ref: str) -> str:
    return {
        "trait.reserve": "RESERVATION_LIFECYCLE_PORT",
        "type.buffer": "QUALIFIED_BUFFER_RESOURCE",
        "type.resourcebudget": "FINITE_ANALYTICAL_RESOURCE_BUDGET",
    }[symbol_ref]


def resource_occurrence_profiles(symbol_ref: str, occurrences: list[dict[str, Any]]) -> list[dict[str, str]]:
    exact = {
        ("trait.reserve", "library.qck.memory-runtime"): "EPHEMERAL_MEMORY_RUNTIME_RESERVATION_ATTEMPT_WITH_ALLOCATOR_POOL_QUANTITY_AND_FAILURE_PROFILE",
        ("trait.reserve", "library.runtime-resource.reservation-ledger"): "TIME_SCOPED_CAPACITY_LEDGER_RESERVATION_WITH_HOLD_COMMIT_RELEASE_AND_EXPIRY_PROFILE",
        ("type.buffer", "library.operations_research.queue_model_semantics"): "LOGICAL_QUEUE_WAITING_CAPACITY_WITH_DISCIPLINE_OVERFLOW_LOSS_AND_BLOCKING_PROFILE",
        ("type.buffer", "library.persistence.columnar_layout"): "TYPED_PHYSICAL_COLUMNAR_MEMORY_REGION_WITH_ALIGNMENT_OFFSETS_VALIDITY_AND_OWNERSHIP_PROFILE",
        ("type.resourcebudget", "library.experiment.analysis_binding.compiler"): "FINITE_EXPERIMENT_ANALYSIS_BINDING_COMPILATION_BUDGET_WITH_EXHAUSTION_AND_PARTIAL_DIAGNOSTIC_PROFILE",
        ("type.resourcebudget", "library.experiment.conclusion.appraiser"): "FINITE_CONCLUSION_APPRAISAL_AND_EXPLANATION_BUDGET_WITH_COVERAGE_AND_PARTIAL_RESULT_PROFILE",
    }
    rows = []
    for occurrence in occurrences:
        library_ref = occurrence["library_ref"]
        rows.append({
            "library_ref": library_ref,
            "candidate_resource_profile": exact.get(
                (symbol_ref, library_ref),
                "CANDIDATE_RESOURCE_ROLE_REQUIRES_LOCAL_KIND_UNIT_LIFECYCLE_ENFORCEMENT_AND_FAILURE_ADJUDICATION",
            ),
        })
    return rows


def resource_archetype_research() -> list[dict[str, Any]]:
    return [{
        "record_kind": "archetype_semantic_research_candidate",
        "research_id": "research.p1.archetype.resource-bound-capacity-scheduling.v1",
        "edition": 1,
        "archetype_id": "RESOURCE_BOUND_CAPACITY_AND_SCHEDULING",
        "bounded_finding": "Resource kind, physical capacity, schedulable or allocatable capacity, request, quota, reservation hold, committed allocation, runtime limit, priority or weight, observed usage, remaining budget and reclaimed capacity are distinct objects. Every resource contract must bind a typed vector of dimensions and units, pool and subject, authority and tenant, time interval and clock, lifecycle state, overcommit and precedence policy, enforcement point, partiality and failure semantics. A buffer is not one universal carrier: a queue buffer is a logical waiting-capacity model with discipline and overflow behavior, while a columnar buffer is a typed physical memory region. Likewise a memory-runtime reserve port and a durable time-scoped reservation ledger do not share one lifecycle merely because both use the verb reserve.",
        "required_contract_dimensions": ["resource kind, dimension vector, units and conversion rules", "pool, topology, locality, ownership and tenant scope", "physical, advertised, allocatable, schedulable, reserved, committed, used, reclaimable and observed quantities", "request, quota, reservation, allocation, usage observation and receipt identities", "requester, pool owner, scheduler, allocator, enforcement point and observer authorities", "hard maximum, soft high-water mark, protection, guarantee, weight, priority and advisory target", "start, end, TTL, deadline, accounting interval, clock and stale-observation policy", "proposed, admitted, held, committed, active, resized, preempted, released, expired and reclaimed states", "atomic versus partial grant and multi-resource all-or-nothing policy", "overcommit, borrowing, hierarchy, fairness, precedence and admission control", "buffer capacity, queue discipline, overflow, backpressure, spill, drop, dead-letter and refusal", "memory-region ownership, lifetime, alignment, mutability and sharing", "concurrent reservation, idempotency, fencing, stale-holder and double-allocation rules", "consumption accounting, checkpoint, remaining budget and exhaustion boundary", "throttle, reclaim, eviction, termination, degradation, cancellation, partial artifact and unknown outcome", "audit, usage, enforcement, release, reclamation and conformance evidence"],
        "non_collapse_laws": ["capacity is not allocatable or schedulable capacity", "request is not reservation", "reservation is not committed allocation", "allocation is not observed usage", "quota is not guarantee or current availability", "limit is not request, protection, weight or fairness", "declared budget is not enforced budget", "successful reserve call is not durable hold, allocation or use", "release request is not reclaimed capacity", "scheduler selection is not binding, activation or execution", "resource exhaustion is not a negative analytical result", "deadline is not CPU, work or memory budget", "queue buffer is not columnar memory buffer", "buffer capacity is not current occupancy", "overflow policy is not lossless delivery", "unbounded token is not infinite physical resource", "partial grant is not full admission", "preemption is not compensation of completed effects"],
        "source_refs": ARCHETYPE_REFINEMENT_SOURCES["RESOURCE_BOUND_CAPACITY_AND_SCHEDULING"],
        "authority_limit": "Kubernetes, Linux cgroup v2, Slurm, Arrow, RabbitMQ and the Kubernetes scheduling framework constrain their own requests, limits, reservations, buffers and scheduling lifecycles. They do not select SAN resource owners, equate memory and ledger reservations, guarantee enforcement or ratify any shared carrier.",
        "decision": "UNRESOLVED",
        "status": "PRIMARY_RESEARCH_COMPLETE_RESOURCE_OWNER_AND_OCCURRENCE_ADJUDICATION_REQUIRED",
    }]


def resource_contract_classification_candidates(
    batches: list[dict[str, Any]],
    symbols: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    packet_by_ref = {row["packet_id"]: row for row in symbols}
    rows = []
    for batch in (row for row in batches if row["research_archetype"] == "RESOURCE_BOUND_CAPACITY_AND_SCHEDULING"):
        for packet_ref in batch["packet_refs"]:
            packet = packet_by_ref[packet_ref]
            symbol_ref = packet["symbol_ref"]
            role = classify_resource_role(symbol_ref)
            detail = RESOURCE_ROLE_DETAILS[role]
            rows.append({
                "record_kind": "resource_contract_classification_candidate",
                "candidate_id": f"candidate.p1.resource-contract.{symbol_ref.replace('.', '-')}.v1",
                "edition": 1,
                "research_ref": "research.p1.archetype.resource-bound-capacity-scheduling.v1",
                "research_program_ref": "program.p1.symbol-archetype.resource-bound-capacity-and-scheduling.v1",
                "batch_ref": batch["batch_id"],
                "symbol_packet_ref": packet_ref,
                "symbol_ref": symbol_ref,
                "family_refs": packet["family_refs"],
                "affected_occurrences": packet["occurrences"],
                "represented_occurrence_count": packet["library_count"],
                "candidate_resource_role": role,
                "candidate_semantic_position": detail["semantic_position"],
                "candidate_disposition_hypothesis": detail["candidate_disposition"],
                "local_resource_requirements": detail["local_requirements"],
                "occurrence_profile_candidates": resource_occurrence_profiles(symbol_ref, packet["occurrences"]),
                "source_refs": list(ARCHETYPE_REFINEMENT_SOURCES["RESOURCE_BOUND_CAPACITY_AND_SCHEDULING"]),
                "required_owner_decisions": ["resource kind dimensions units pool topology and owner", "request reservation allocation usage and reclamation identity boundaries", "time lifecycle authority hierarchy and precedence", "hard soft advisory weighted quota and guarantee semantics", "atomic or partial multi-resource grant and concurrency", "overcommit fairness preemption backpressure overflow spill and loss", "enforcement point accounting evidence and unknown completion", "per-occurrence import qualified homonym or split", "migration in-flight reservation historical receipt and external-reference disposition"],
                "non_collapse_laws": ["capacity is not availability", "request is not reservation", "reservation is not allocation", "allocation is not usage", "limit is not guarantee", "budget declaration is not enforcement", "release is not reclamation", "queue buffer is not memory buffer", "scheduler selection is not execution"],
                "classification_basis": "BOUNDED_PRIMARY_RESEARCH_PLUS_SYMBOL_AND_USE_SITE_ROUTING_NOT_A_RESOURCE_OWNER_RESERVATION_OR_ALLOCATION_DECISION",
                "authority_limit": "This candidate selects a resource lifecycle role and falsifiable disposition hypothesis only; it reserves, allocates, enforces, releases and reclaims no resource and proves no availability or fairness property.",
                "decision": "UNRESOLVED",
                "status": "CANDIDATE_REQUIRES_RESOURCE_OWNER_AND_OCCURRENCE_ADJUDICATION",
            })
    return sorted(rows, key=lambda row: row["symbol_ref"])


SHAPE_ROLE_DETAILS: dict[str, dict[str, Any]] = {
    "QUALIFIED_PARTITION_OPERATION": {
        "semantic_position": "CONTEXT_QUALIFIED_OPERATION_PRODUCING_MEMBERSHIP_OR_RUNTIME_DISTRIBUTION",
        "candidate_disposition": "QUALIFY_LOCAL_SYMBOL_IDS",
        "local_requirements": ["partitioned subject, member identity and coverage", "objective, constraints and admissible membership relation", "determinism, stability, residual and quality evidence", "logical plan, materialization, routing and effect completion kept separate"],
    },
    "QUALIFIED_BLOCK": {
        "semantic_position": "CONTEXT_QUALIFIED_GROUPING_OR_LAYOUT_NODE",
        "candidate_disposition": "QUALIFY_LOCAL_SYMBOL_IDS",
        "local_requirements": ["block kind and semantic owner", "member identity, coverage, overlap and ordering", "source, derivation and edition identity", "document-layout and experimental-design laws kept separate"],
    },
    "SPATIAL_GEOMETRY_VALUE": {
        "semantic_position": "SPATIAL_REFERENCE_BOUND_GEOMETRIC_VALUE_WITH_EXPLICIT_TOPOLOGY_AND_PRECISION_PROFILE",
        "candidate_disposition": "FAMILY_SHARED_OWNER_AND_IMPORTS",
        "local_requirements": ["geometry kind, dimensionality and coordinate sequence", "CRS, axis order, units and coordinate epoch", "precision, tolerance, validity and topology model", "feature identity, provenance and transformation loss kept separate"],
    },
    "QUALIFIED_LAYOUT_PROFILE": {
        "semantic_position": "CONTEXT_QUALIFIED_DECLARATION_OF_LAYOUT_DECISIONS_NOT_A_LAYOUT_RESULT",
        "candidate_disposition": "QUALIFY_LOCAL_SYMBOL_IDS",
        "local_requirements": ["layout subject, context and profile edition", "declared decision dimensions, constraints and defaults", "compatibility, canonicalization and unsupported dimensions", "document reading layout and physical data layout kept separate"],
    },
    "QUALIFIED_PAGE": {
        "semantic_position": "CONTEXT_QUALIFIED_SUBDIVISION_WITH_LOCAL_IDENTITY_AND_ORDERING",
        "candidate_disposition": "QUALIFY_LOCAL_SYMBOL_IDS",
        "local_requirements": ["parent object and page kind", "identity, ordinal, boundary and address", "content coverage, ordering and lifecycle", "document presentation and columnar storage semantics kept separate"],
    },
    "DOCUMENT_REGION": {
        "semantic_position": "DOCUMENT_EDITION_BOUND_SPATIAL_OR_LOGICAL_REGION_WITH_SOURCE_ANCHORS",
        "candidate_disposition": "FAMILY_SHARED_OWNER_AND_IMPORTS",
        "local_requirements": ["document, page and representation edition", "coordinate space, geometry and source anchors", "logical role, membership, overlap and reading order", "observed, authored and inferred provenance plus confidence"],
    },
    "SPATIAL_WEIGHT_GRAPH": {
        "semantic_position": "OBSERVATION_EDITION_BOUND_WEIGHTED_NEIGHBOR_RELATION_WITH_EXPLICIT_TRANSFORMATION",
        "candidate_disposition": "FAMILY_SHARED_OWNER_AND_IMPORTS",
        "local_requirements": ["observation identity domain, order and data cut", "neighbor construction, distance or topology rule and parameters", "directedness, symmetry, diagonal and isolate policy", "original weights, transformation, normalization and downstream model role"],
    },
}


def classify_shape_role(symbol_ref: str) -> str:
    return {
        "trait.partition": "QUALIFIED_PARTITION_OPERATION",
        "type.block": "QUALIFIED_BLOCK",
        "type.geometry": "SPATIAL_GEOMETRY_VALUE",
        "type.layoutprofile": "QUALIFIED_LAYOUT_PROFILE",
        "type.page": "QUALIFIED_PAGE",
        "type.region": "DOCUMENT_REGION",
        "type.spatialweights": "SPATIAL_WEIGHT_GRAPH",
    }[symbol_ref]


def shape_occurrence_profiles(symbol_ref: str, occurrences: list[dict[str, Any]]) -> list[dict[str, str]]:
    exact = {
        ("trait.partition", "library.method_kernels.graph_methods"): "GRAPH_NODE_PARTITION_METHOD_WITH_MEMBERSHIP_COVERAGE_OBJECTIVE_CONSTRAINT_AND_HEURISTIC_QUALITY_PROFILE",
        ("trait.partition", "library.qck.exchange-runtime"): "RUNTIME_DATA_EXCHANGE_PARTITION_PORT_WITH_DISTRIBUTION_KEYS_CHANNEL_TOPOLOGY_ROUTING_AND_DELIVERY_PROFILE",
        ("type.block", "library.method_kernels.document_content_graph"): "DOCUMENT_CONTENT_GRAPH_BLOCK_WITH_DOCUMENT_PAGE_SOURCE_ANCHORS_STRUCTURE_ROLE_AND_READING_ORDER_PROFILE",
        ("type.block", "library.method_kernels.document_layout_methods"): "DERIVED_DOCUMENT_LAYOUT_BLOCK_WITH_COORDINATE_SEGMENTATION_ROLE_CONFIDENCE_AND_METHOD_PROVENANCE_PROFILE",
        ("type.block", "library.method_kernels.experiment_randomization_methods"): "EXPERIMENTAL_DESIGN_BLOCK_WITH_UNIT_MEMBERSHIP_NUISANCE_FACTOR_BALANCE_AND_WITHIN_BLOCK_RANDOMIZATION_PROFILE",
        ("type.geometry", "library.method_kernels.spatial_methods"): "GENERAL_SPATIAL_GEOMETRY_IMPORT_WITH_CRS_TRANSFORM_PREDICATE_AND_INTERPOLATION_PROFILE",
        ("type.geometry", "library.method_kernels.vector_geometry_topology"): "VECTOR_GEOMETRY_TOPOLOGY_IMPORT_WITH_VALIDITY_OVERLAY_REPAIR_PRECISION_AND_PREDICATE_PROFILE",
        ("type.layoutprofile", "library.method_kernels.document_layout_methods"): "DOCUMENT_LAYOUT_ANALYSIS_PROFILE_WITH_COORDINATES_SEGMENTATION_READING_ORDER_ROLES_AND_MODEL_EDITION",
        ("type.layoutprofile", "library.san_layout"): "PHYSICAL_DATA_LAYOUT_PROFILE_WITH_BLOCK_GRAIN_SHARDING_ACCESS_PATH_LOCALITY_AND_REPRESENTATION_EDITION",
        ("type.page", "library.method_kernels.document_content_graph"): "DOCUMENT_PAGE_WITH_DOCUMENT_REPRESENTATION_ORDINAL_COORDINATE_SPACE_CONTENT_ANCHORS_AND_PRESENTATION_PROVENANCE",
        ("type.page", "library.persistence.columnar_layout"): "COLUMNAR_STORAGE_PAGE_WITH_COLUMN_CHUNK_PARENT_ENCODING_ROW_RANGE_OFFSETS_STATISTICS_AND_FORMAT_EDITION",
        ("type.region", "library.method_kernels.document_content_graph"): "DOCUMENT_CONTENT_REGION_WITH_SOURCE_ANCHORS_LOGICAL_MEMBERSHIP_AND_STRUCTURE_GRAPH_ROLE",
        ("type.region", "library.method_kernels.document_layout_methods"): "DERIVED_DOCUMENT_LAYOUT_REGION_WITH_GEOMETRY_SEGMENTATION_ROLE_READING_ORDER_CONFIDENCE_AND_PROVENANCE",
        ("type.spatialweights", "library.method_kernels.spatial_methods"): "GENERAL_SPATIAL_WEIGHT_GRAPH_IMPORT_WITH_NEIGHBOR_CONSTRUCTION_CRS_DISTANCE_TRANSFORMATION_AND_ISOLATE_PROFILE",
        ("type.spatialweights", "library.method_kernels.spatial_statistics_methods"): "SPATIAL_STATISTICS_WEIGHT_GRAPH_IMPORT_WITH_OBSERVATION_ORDER_MODEL_ROLE_NORMALIZATION_ASYMMETRY_AND_LAG_PROFILE",
    }
    rows = []
    for occurrence in occurrences:
        library_ref = occurrence["library_ref"]
        rows.append({
            "library_ref": library_ref,
            "candidate_shape_profile": exact.get(
                (symbol_ref, library_ref),
                "CANDIDATE_SHAPE_ROLE_REQUIRES_LOCAL_SUBJECT_IDENTITY_GRAIN_TOPOLOGY_REPRESENTATION_AND_LOSS_ADJUDICATION",
            ),
        })
    return rows


def shape_archetype_research() -> list[dict[str, Any]]:
    return [{
        "record_kind": "archetype_semantic_research_candidate",
        "research_id": "research.p1.archetype.shape-topology-view-process.v1",
        "edition": 1,
        "archetype_id": "SHAPE_TOPOLOGY_VIEW_AND_PROCESS",
        "bounded_finding": "Carrier shape, domain meaning, topology, partition relation, partition-producing method, physical distribution, view or projection, materialized layout and execution result are distinct semantic objects. Every shape-bearing contract must bind the subject and edition, identity and equality relation, grain and coverage, order and topology, coordinate or reference system, derivation and information loss, lifecycle and temporal cut, compatibility and conformance evidence. Equal placeholder names do not unify graph partition with runtime exchange, document block with experimental block, document page with columnar page, or document layout profile with physical data layout. Geometry, document region and spatial weights remain plausible family-shared carriers only under explicit local profiles and named owner adjudication.",
        "required_contract_dimensions": ["semantic subject, role, bounded-context owner and exact edition", "element, member, node, edge, cell, page, block, region and parent identity domains", "equality, equivalence, isomorphism, topological equality and representation equality", "grain, cardinality, membership, coverage, overlap, multiplicity and residual", "order, adjacency, direction, connectivity, hierarchy, containment and reading order", "coordinate reference system, axis order, units, dimensionality, precision and topology model", "partition objective, constraints, algorithm or routing policy, determinism and quality evidence", "logical relation, derived view, materialized placement, runtime routing and completed exchange", "source, derivation method, temporal or snapshot cut, confidence, uncertainty and information loss", "representation profile, canonicalization, directional compatibility and migration", "partial, invalid, disconnected, isolated, ambiguous, unsupported and resource-exhausted outcomes", "conformance, negative twins, reproducibility and provenance evidence"],
        "non_collapse_laws": ["carrier shape is not semantic meaning", "partition relation is not partition algorithm", "graph partition is not runtime data distribution", "partition plan is not materialized placement or completed exchange", "document block is not experimental-design block", "document page is not columnar-storage page", "document layout profile is not physical data layout profile", "layout profile is not layout result", "geometry is not feature or domain entity", "geometry without CRS axis order and units is incomplete", "geometric validity is not business validity", "region is not necessarily a geometry or source-authored object", "spatial weights are not geometry adjacency alone", "transformed weights are not original weights", "symmetry and connectedness are not defaults", "derived view is not source", "same members do not imply same partition objective or topology"],
        "source_refs": ARCHETYPE_REFINEMENT_SOURCES["SHAPE_TOPOLOGY_VIEW_AND_PROCESS"],
        "authority_limit": "RFC 7946, OGC SFA, NIST experimental-design guidance, ALTO, Kernighan-Lin, Substrait, libpysal, Parquet and IIIF constrain their own geometry, blocking, document-layout, graph-partition, data-distribution, spatial-weight, storage-page and presentation models. They do not select SAN owners, prove cross-context equality or ratify any shared carrier.",
        "decision": "UNRESOLVED",
        "status": "PRIMARY_RESEARCH_COMPLETE_SHAPE_OWNER_AND_OCCURRENCE_ADJUDICATION_REQUIRED",
    }]


def shape_contract_classification_candidates(
    batches: list[dict[str, Any]],
    symbols: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    packet_by_ref = {row["packet_id"]: row for row in symbols}
    rows = []
    for batch in (row for row in batches if row["research_archetype"] == "SHAPE_TOPOLOGY_VIEW_AND_PROCESS"):
        for packet_ref in batch["packet_refs"]:
            packet = packet_by_ref[packet_ref]
            symbol_ref = packet["symbol_ref"]
            role = classify_shape_role(symbol_ref)
            detail = SHAPE_ROLE_DETAILS[role]
            rows.append({
                "record_kind": "shape_contract_classification_candidate",
                "candidate_id": f"candidate.p1.shape-contract.{symbol_ref.replace('.', '-')}.v1",
                "edition": 1,
                "research_ref": "research.p1.archetype.shape-topology-view-process.v1",
                "research_program_ref": "program.p1.symbol-archetype.shape-topology-view-and-process.v1",
                "batch_ref": batch["batch_id"],
                "symbol_packet_ref": packet_ref,
                "symbol_ref": symbol_ref,
                "family_refs": packet["family_refs"],
                "affected_occurrences": packet["occurrences"],
                "represented_occurrence_count": packet["library_count"],
                "candidate_shape_role": role,
                "candidate_semantic_position": detail["semantic_position"],
                "candidate_disposition_hypothesis": detail["candidate_disposition"],
                "local_shape_requirements": detail["local_requirements"],
                "occurrence_profile_candidates": shape_occurrence_profiles(symbol_ref, packet["occurrences"]),
                "source_refs": list(ARCHETYPE_REFINEMENT_SOURCES["SHAPE_TOPOLOGY_VIEW_AND_PROCESS"]),
                "required_owner_decisions": ["semantic subject role and bounded-context owner", "identity equality equivalence and canonical representation", "grain membership coverage overlap cardinality and residual", "order topology coordinate reference precision and validity", "partition objective method plan placement routing and exchange boundaries", "source derivation temporal cut uncertainty and information loss", "representation compatibility migration and historical replay", "per-occurrence shared import qualified homonym or split", "external-reference and public-name disposition"],
                "non_collapse_laws": ["shape is not meaning", "partition relation is not algorithm or exchange", "graph partition is not runtime distribution", "document block is not experimental block", "document page is not storage page", "document layout is not physical data layout", "geometry is not feature", "region is not necessarily geometry", "spatial weights are not adjacency alone", "transformed weights are not original weights", "view is not source"],
                "classification_basis": "BOUNDED_PRIMARY_RESEARCH_PLUS_SYMBOL_AND_USE_SITE_ROUTING_NOT_A_SHAPE_OWNER_EQUALITY_OR_APPLICABILITY_DECISION",
                "authority_limit": "This candidate selects a shape/topology role and falsifiable disposition hypothesis only; it does not establish shared ownership, geometric or statistical validity, partition optimality, runtime placement, semantic equality or losslessness.",
                "decision": "UNRESOLVED",
                "status": "CANDIDATE_REQUIRES_SHAPE_OWNER_AND_OCCURRENCE_ADJUDICATION",
            })
    return sorted(rows, key=lambda row: row["symbol_ref"])


def measure_lane_refinement_candidates(
    batches: list[dict[str, Any]],
    symbols: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    batch_by_packet = {packet_ref: row for row in batches for packet_ref in row["packet_refs"]}
    packet_by_symbol = {row["symbol_ref"]: row for row in symbols}
    rows = []
    for symbol_ref, archetype in sorted(MEASURE_LANE_EXACT_ARCHETYPES.items()):
        packet = packet_by_symbol[symbol_ref]
        batch = batch_by_packet[packet["packet_id"]]
        rows.append({
            "record_kind": "measure_lane_archetype_refinement_candidate",
            "refinement_id": f"refinement.p1.measure-lane.{symbol_ref.replace('.', '-')}.v1",
            "edition": 1,
            "symbol_packet_ref": packet["packet_id"],
            "batch_ref": batch["batch_id"],
            "symbol_ref": symbol_ref,
            "family_refs": packet["family_refs"],
            "affected_occurrences": packet["occurrences"],
            "represented_occurrence_count": packet["library_count"],
            "candidate_archetype": archetype,
            "candidate_semantic_axis_refs": ARCHETYPE_SEMANTIC_AXES[archetype],
            "source_refs": ARCHETYPE_REFINEMENT_SOURCES[archetype],
            "classification_basis": "BOUNDED_PRIMARY_RESEARCH_PLUS_EXACT_SYMBOL_AND_USE_SITE_ROUTING_NOT_A_SEMANTIC_OWNER_OR_RESULT_DECISION",
            "authority_limit": "This correction removes a lexical measurement-bucket collapse. It does not establish shared ownership, dimensional validity, model fitness, estimate truth, rule applicability, bound tightness or public-name disposition.",
            "decision": "UNRESOLVED",
            "status": "CANDIDATE_REQUIRES_ARCHETYPE_OWNER_AND_OCCURRENCE_ADJUDICATION",
        })
    return rows


MEASURE_ROLE_DETAILS: dict[str, dict[str, Any]] = {
    "QUANTITY_DIMENSION_ALGEBRA_CONTRACT": {
        "semantic_position": "PROVIDER_INDEPENDENT_CONTRACT_FOR_TYPED_QUANTITY_DIMENSION_UNIT_AND_CONVERSION_ALGEBRA",
        "candidate_disposition": "CANONICAL_SHARED_OWNER_AND_IMPORTS",
        "local_requirements": ["system of quantities, base-dimension basis and quantity-kind vocabulary", "unit system, scale, offset, logarithmic and contextual conversion profiles", "valid operations, rational exponents, canonical form and equality relations", "exact, rounded, uncertain, unsupported and invalid-operation outcomes"],
    },
    "TYPED_QUANTITY_ALGEBRA_EXPRESSION_INPUT": {
        "semantic_position": "UNEVALUATED_TYPED_INPUT_EXPRESSION_FOR_A_NAMED_QUANTITY_ALGEBRA_EDITION",
        "candidate_disposition": "CANONICAL_SHARED_OWNER_AND_IMPORTS",
        "local_requirements": ["algebra edition and expression representation", "quantity kinds, dimensions, units, numeric domains and source spans", "variables, constants, references, partial inputs and contextual conversion evidence", "input syntax kept separate from dimensional validity, evaluation and outcome"],
    },
    "QUALIFIED_BOUND_WITNESS": {
        "semantic_position": "CONTEXT_QUALIFIED_ORDER_BOUND_WITH_EXPLICIT_SUBJECT_RELATION_ORIENTATION_SCOPE_AND_TIGHTNESS",
        "candidate_disposition": "QUALIFY_LOCAL_SYMBOL_IDS",
        "local_requirements": ["optimization primal/dual objective bound versus physical column-statistics lower/upper bound", "subject, order relation, orientation, units, data/problem cut and producer", "tolerance, truncation, null/NaN, conservative/tight and unknown semantics", "pruning, gap, feasibility, optimality and row-level truth boundaries"],
    },
}


def classify_measure_role(symbol_ref: str) -> str:
    return {
        "trait.dimensionalgebracontract": "QUANTITY_DIMENSION_ALGEBRA_CONTRACT",
        "type.dimensionalgebrainput": "TYPED_QUANTITY_ALGEBRA_EXPRESSION_INPUT",
        "type.bound": "QUALIFIED_BOUND_WITNESS",
    }[symbol_ref]


def measure_occurrence_profiles(symbol_ref: str, occurrences: list[dict[str, Any]]) -> list[dict[str, str]]:
    exact = {
        ("trait.dimensionalgebracontract", "library.csp.quantity.dimension-algebra"): "CANONICAL_QUANTITY_AND_DIMENSION_ALGEBRA_OWNER_CANDIDATE_WITH_UNIT_SYSTEM_CONVERSION_VALIDITY_AND_PARTIALITY_LAWS",
        ("trait.dimensionalgebracontract", "library.smf.dimension_algebra"): "SEMANTIC_METRIC_FORMULA_IMPORT_OF_QUANTITY_ALGEBRA_WITH_FORMULA_LANGUAGE_PROFILE_AND_NO_OWNER_REDECLARATION",
        ("type.dimensionalgebrainput", "library.csp.quantity.dimension-algebra"): "CANONICAL_TYPED_QUANTITY_ALGEBRA_INPUT_OWNER_CANDIDATE_WITH_EXPRESSION_REPRESENTATION_AND_CONTEXT_BINDINGS",
        ("type.dimensionalgebrainput", "library.smf.dimension_algebra"): "FORMULA_LAYER_IMPORT_OF_TYPED_QUANTITY_ALGEBRA_INPUT_WITH_METRIC_SYMBOL_AND_FORMULA_SOURCE_PROFILE",
        ("type.bound", "library.operations_research.optimization_result_algebra"): "OPTIMIZATION_PRIMAL_OR_DUAL_OBJECTIVE_BOUND_WITNESS_WITH_SENSE_TOLERANCE_INCUMBENT_GAP_STATUS_AND_PROBLEM_CUT_PROFILE",
        ("type.bound", "library.persistence.file_statistics"): "PHYSICAL_COLUMN_STATISTICS_LOWER_OR_UPPER_BOUND_WITH_TYPE_SORT_ORDER_TRUNCATION_NULL_NAN_TIGHTNESS_AND_DATA_CUT_PROFILE",
    }
    return [
        {
            "library_ref": occurrence["library_ref"],
            "candidate_measure_profile": exact.get(
                (symbol_ref, occurrence["library_ref"]),
                "CANDIDATE_MEASURE_ROLE_REQUIRES_LOCAL_SUBJECT_KIND_UNIT_ORDER_SCOPE_UNCERTAINTY_AND_USE_ADJUDICATION",
            ),
        }
        for occurrence in occurrences
    ]


def measure_archetype_research() -> list[dict[str, Any]]:
    return [{
        "record_kind": "archetype_semantic_research_candidate",
        "research_id": "research.p1.archetype.measure-quality-comparison-formula.v1",
        "edition": 1,
        "archetype_id": "MEASURE_QUALITY_COMPARISON_AND_FORMULA",
        "bounded_finding": "Quantity, quantity kind, dimension, unit, numerical value, measurand, measured value, measurement result and uncertainty are distinct semantic objects. A dimension algebra must bind its system of quantities, base-dimension basis, unit and conversion profile, expression representation, valid operations, equality and commensurability relations, exactness and partial outcomes. A bound is not one universal measure: an optimization primal or dual objective bound is qualified by problem cut, objective sense, feasibility and tolerance claims, whereas a physical file-statistics bound is qualified by data cut, physical/logical type, sort order, truncation, null/NaN and conservative or tight semantics. Neither kind may silently establish row-level truth, an incumbent, feasibility, optimality or business acceptance.",
        "required_contract_dimensions": ["semantic subject, quantity or bound kind and bounded-context owner", "quantity kind, dimension vector, unit, scale, offset, logarithmic or contextual conversion profile", "numeric domain, precision, rounding, tolerance, uncertainty and missing/unknown representation", "algebra and formula language edition, expression syntax, variables, constants and source bindings", "valid operations, dimensional compatibility, commensurability, canonicalization and evaluation partiality", "measurand, population, grain, observation or evaluation cut and aggregation", "lower/upper or primal/dual relation, optimization sense, incumbent and objective semantics", "physical type, logical type, sort order, truncation, null, NaN and tight/conservative statistics semantics", "producer, method, solver or writer edition, execution occurrence and provenance", "compatibility, migration, reproducibility, conformance and negative-boundary evidence", "diagnostic, measurement, estimate, rule, artifact, decision and action-authority boundaries"],
        "non_collapse_laws": ["quantity is not unit or numeric value", "dimension equality is not quantity-kind equality", "commensurability is not equality", "dimensional compatibility is not valid contextual conversion", "formula input is not formula outcome", "syntactic validity is not dimensional validity", "measurement result is not bare numeric value", "uncertainty is not tolerance", "optimization bound is not observed minimum or maximum", "bound orientation depends on optimization sense", "objective bound is not incumbent, feasibility or optimality proof", "file-statistics bound is not necessarily an exact observed extremum", "pruning evidence cannot establish row-level predicate truth", "quality rule is not quality measurement or repair authority", "effect estimate is not estimand, identification result or causal truth", "baseline artifact is not observation, threshold or anomaly result"],
        "source_refs": ARCHETYPE_REFINEMENT_SOURCES["MEASURE_QUALITY_COMPARISON_AND_FORMULA"],
        "authority_limit": "VIM, UCUM, OpenFormula, MathOpt, Parquet and DQV constrain their own metrology, unit, formula, optimization, storage-statistics and quality vocabularies. They do not select a SAN owner, unify optimization and storage bounds, validate a business formula or authorize a decision.",
        "decision": "UNRESOLVED",
        "status": "PRIMARY_RESEARCH_COMPLETE_MEASURE_OWNER_AND_OCCURRENCE_ADJUDICATION_REQUIRED",
    }]


def measure_contract_classification_candidates(
    batches: list[dict[str, Any]],
    symbols: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    packet_by_ref = {row["packet_id"]: row for row in symbols}
    rows = []
    for batch in (row for row in batches if row["research_archetype"] == "MEASURE_QUALITY_COMPARISON_AND_FORMULA"):
        for packet_ref in batch["packet_refs"]:
            packet = packet_by_ref[packet_ref]
            symbol_ref = packet["symbol_ref"]
            role = classify_measure_role(symbol_ref)
            detail = MEASURE_ROLE_DETAILS[role]
            rows.append({
                "record_kind": "measure_contract_classification_candidate",
                "candidate_id": f"candidate.p1.measure-contract.{symbol_ref.replace('.', '-')}.v1",
                "edition": 1,
                "research_ref": "research.p1.archetype.measure-quality-comparison-formula.v1",
                "research_program_ref": "program.p1.symbol-archetype.measure-quality-comparison-and-formula.v1",
                "batch_ref": batch["batch_id"],
                "symbol_packet_ref": packet_ref,
                "symbol_ref": symbol_ref,
                "family_refs": packet["family_refs"],
                "affected_occurrences": packet["occurrences"],
                "represented_occurrence_count": packet["library_count"],
                "candidate_measure_role": role,
                "candidate_semantic_position": detail["semantic_position"],
                "candidate_disposition_hypothesis": detail["candidate_disposition"],
                "local_measure_requirements": detail["local_requirements"],
                "occurrence_profile_candidates": measure_occurrence_profiles(symbol_ref, packet["occurrences"]),
                "source_refs": list(ARCHETYPE_REFINEMENT_SOURCES["MEASURE_QUALITY_COMPARISON_AND_FORMULA"]),
                "required_owner_decisions": ["semantic subject quantity or bound kind and owner", "quantity kind dimension unit conversion and equality relations", "numeric domain precision rounding uncertainty tolerance and partiality", "algebra formula representation canonicalization and compatibility editions", "measurand population grain data or problem cut and aggregation", "bound relation orientation sense tightness producer and evidence", "null NaN truncation feasibility optimality pruning and unknown semantics", "per-occurrence shared import qualified homonym or split", "migration historical replay external-reference and public-name disposition"],
                "non_collapse_laws": ["quantity is not unit or number", "dimension equality is not quantity-kind equality", "commensurability is not equality", "formula input is not outcome", "optimization bound is not file-statistics bound", "bound is not incumbent or optimality proof", "file bound is not row-level predicate truth", "uncertainty is not tolerance"],
                "classification_basis": "BOUNDED_PRIMARY_RESEARCH_PLUS_SYMBOL_AND_USE_SITE_ROUTING_NOT_A_MEASURE_OWNER_VALIDITY_TIGHTNESS_OR_APPLICABILITY_DECISION",
                "authority_limit": "This candidate selects a measure/bound role and falsifiable disposition hypothesis only; it proves no dimensional validity, conversion correctness, bound tightness, feasibility, optimality, predicate truth or business fitness.",
                "decision": "UNRESOLVED",
                "status": "CANDIDATE_REQUIRES_MEASURE_OWNER_AND_OCCURRENCE_ADJUDICATION",
            })
    return sorted(rows, key=lambda row: row["symbol_ref"])


TIME_ROLE_DETAILS: dict[str, dict[str, Any]] = {
    "FORECAST_ORIGIN_COORDINATE": {
        "semantic_position": "FORECAST_ISSUE_OR_INFORMATION_CUT_COORDINATE_ON_AN_EXPLICIT_TIME_AXIS",
        "candidate_disposition": "FAMILY_SHARED_OWNER_AND_IMPORTS",
        "local_requirements": ["series identity and immutable observation/information cut", "time axis, temporal reference system, calendar, frequency and precision", "origin instant/index and availability-versus-event-time policy", "training, fitting, issue and evaluation occurrences kept separate"],
    },
    "FORECAST_HORIZON_COORDINATE": {
        "semantic_position": "ORDERED_FORECAST_TARGET_OFFSET_OR_POSITION_SET_RELATIVE_TO_A_BOUND_ORIGIN",
        "candidate_disposition": "FAMILY_SHARED_OWNER_AND_IMPORTS",
        "local_requirements": ["forecast origin and target series/grain", "ordered offsets or target positions plus calendar/frequency semantics", "inclusive/exclusive, sparse/irregular and multi-step representation", "horizon kept separate from duration, window, lead time and realized target events"],
    },
    "DISPOSITION_ELIGIBILITY_DUE": {
        "semantic_position": "DERIVED_EARLIEST_DISPOSITION_ELIGIBILITY_POSITION_UNDER_AN_EXACT_SCHEDULE_EDITION",
        "candidate_disposition": "FAMILY_SHARED_OWNER_AND_IMPORTS",
        "local_requirements": ["record/asset scope, cutoff or triggering event and retention schedule edition", "calendar, duration arithmetic, later/earlier precedence and recomputation cut", "holds, exceptions, competing authorities and unknown trigger posture", "eligibility kept separate from authorization, request, execution and receipt"],
    },
    "SOURCE_EVENT_OCCURRENCE_TIME": {
        "semantic_position": "CLAIMED_EVENT_OCCURRENCE_POSITION_MEASURED_BY_THE_ORIGIN_CLOCK",
        "candidate_disposition": "FAMILY_SHARED_OWNER_AND_IMPORTS",
        "local_requirements": ["event occurrence identity and source clock domain", "temporal reference system, offset, precision and uncertainty", "source authority, synchronization, correction and late/out-of-order posture", "observed, ingested, recorded, processed and committed times kept separate"],
    },
    "QUALIFIED_RETRACTION_TRANSITION": {
        "semantic_position": "CONTEXT_QUALIFIED_WITHDRAWAL_TRANSITION_REQUIRING_EXACT_SUBJECT_EFFECT_AND_AUTHORITY",
        "candidate_disposition": "QUALIFY_LOCAL_SYMBOL_IDS",
        "local_requirements": ["governed record/reliance withdrawal versus materialized relation negative update", "subject and prior edition/value identity, transition occurrence and effective time", "issuer authority, reason, replacement/supersession and downstream propagation", "retraction kept separate from correction, invalidation, deletion, erasure, recall and compensation"],
    },
    "APPLICATION_STATE_TRANSITION": {
        "semantic_position": "APPLICATION_AGGREGATE_OR_WORKFLOW_TRANSITION_RECORD_UNDER_AN_EXACT_STATE_MACHINE_EDITION",
        "candidate_disposition": "FAMILY_SHARED_OWNER_AND_IMPORTS",
        "local_requirements": ["subject and prior/new state identities", "command, invariant and expected-version binding", "transition occurrence and effective/recording times", "authorization, emitted events, refusals and effect handoff kept separate"],
    },
}


def classify_time_role(symbol_ref: str) -> str:
    return {
        "type.forecastorigin": "FORECAST_ORIGIN_COORDINATE",
        "type.forecasthorizon": "FORECAST_HORIZON_COORDINATE",
        "type.disposition_due": "DISPOSITION_ELIGIBILITY_DUE",
        "type.event_time": "SOURCE_EVENT_OCCURRENCE_TIME",
        "type.retraction": "QUALIFIED_RETRACTION_TRANSITION",
        "type.contract.application.state_transition": "APPLICATION_STATE_TRANSITION",
    }[symbol_ref]


def time_occurrence_profiles(symbol_ref: str, occurrences: list[dict[str, Any]]) -> list[dict[str, str]]:
    exact = {
        ("type.forecastorigin", "library.method_kernels.forecasting_methods"): "FORECAST_METHOD_IMPORT_OF_ORIGIN_WITH_ISSUE_TRAINING_INPUT_AVAILABILITY_AND_MODEL_FIT_CUT_PROFILE",
        ("type.forecastorigin", "library.method_kernels.time_series_semantics"): "CANONICAL_TIME_SERIES_FORECAST_ORIGIN_OWNER_CANDIDATE_WITH_AXIS_CALENDAR_FREQUENCY_AND_INFORMATION_CUT_LAWS",
        ("type.forecasthorizon", "library.method_kernels.forecasting_methods"): "FORECAST_METHOD_IMPORT_OF_ORDERED_TARGET_HORIZON_WITH_MULTI_STEP_OUTPUT_AND_EVALUATION_PROFILE",
        ("type.forecasthorizon", "library.method_kernels.time_series_semantics"): "CANONICAL_TIME_SERIES_FORECAST_HORIZON_OWNER_CANDIDATE_WITH_ORIGIN_RELATIVE_OFFSET_AND_TARGET_POSITION_LAWS",
        ("type.disposition_due", "library.spt.deletion_provider"): "DISPOSITION_ELIGIBILITY_IMPORT_FOR_PROVIDER_REQUEST_WITHOUT_DESTRUCTION_TRANSFER_OR_ERASURE_AUTHORITY",
        ("type.disposition_due", "library.spt.retention_calculus"): "RETENTION_CALCULUS_OWNER_CANDIDATE_FOR_SCHEDULE_CUTOFF_TRIGGER_CALENDAR_HOLD_AND_ELIGIBILITY_DERIVATION",
        ("type.event_time", "library.spt.audit_event_types"): "AUDIT_EVENT_OCCURRENCE_TIME_OWNER_CANDIDATE_WITH_SOURCE_CLOCK_PRECISION_UNCERTAINTY_AND_EVENT_IDENTITY_PROFILE",
        ("type.event_time", "library.spt.audit_sink"): "AUDIT_SINK_IMPORT_OF_SOURCE_EVENT_TIME_KEPT_DISTINCT_FROM_OBSERVED_INGESTED_RECORDED_AND_COMMIT_TIMES",
        ("type.retraction", "library.lpe.record-lifecycle"): "GOVERNED_RECORD_OR_RELIANCE_RETRACTION_WITH_ISSUER_REASON_EFFECTIVE_TIME_REPLACEMENT_PROPAGATION_AND_APPEAL_PROFILE",
        ("type.retraction", "library.persistence.materialization"): "MATERIALIZED_RELATION_RETRACT_CHANGE_WITH_ROW_KEY_PRIOR_VALUE_LOGICAL_TIME_MULTIPLICITY_ORDER_AND_SINK_PROFILE",
    }
    return [
        {
            "library_ref": occurrence["library_ref"],
            "candidate_time_profile": exact.get(
                (symbol_ref, occurrence["library_ref"]),
                "CANDIDATE_TEMPORAL_ROLE_REQUIRES_LOCAL_SUBJECT_CLOCK_REFERENCE_SYSTEM_ORDER_AUTHORITY_EFFECT_AND_EVIDENCE_ADJUDICATION",
            ),
        }
        for occurrence in occurrences
    ]


def time_archetype_research() -> list[dict[str, Any]]:
    return [{
        "record_kind": "archetype_semantic_research_candidate",
        "research_id": "research.p1.archetype.time-lifecycle-control.v1",
        "edition": 1,
        "archetype_id": "TIME_LIFECYCLE_AND_CONTROL",
        "bounded_finding": "Temporal syntax, instant, interval, duration, period, ordinal/index position, calendar position, source event time, observed time, processing time, valid time, recording time, deadline, eligibility due time, forecast origin, forecast horizon, lifecycle transition request, transition occurrence and terminal fact are distinct. Every temporal carrier must bind its semantic subject and role, time axis/reference system and calendar, precision and uncertainty, clock/source authority, ordering and equality relation, immutable observation/evaluation cut, lifecycle state, effect boundary and evidence. Forecast origin/horizon are time-series coordinates rather than generic instants or durations. Disposition due is derived eligibility rather than authority or execution. Event time is a source occurrence claim rather than observation or recording time. Governed-record retraction and materialized-relation retract updates require qualified identities because their subjects, authorities and effects differ.",
        "required_contract_dimensions": ["semantic subject, temporal role, bounded-context owner and exact edition", "instant, interval, duration, period, index, calendar position or lifecycle transition kind", "time axis, temporal reference system, calendar, clock, zone/offset and leap-second profile", "precision, resolution, granularity, tolerance, uncertainty and unknown/open endpoint", "identity, equality, simultaneity, ordering, overlap and tie-breaking relation", "event, observed, ingested, processed, committed, valid and recording time separation", "forecast series, origin, information cut, ordered horizon and target positions", "retention cutoff/trigger, schedule edition, duration arithmetic, holds, precedence and eligibility cut", "requested, eligible, authorized, attempted, effective, observed and recorded transition states", "correction, supersession, retraction, invalidation, deletion, erasure, recall and compensation separation", "concurrency, stale observation, late/out-of-order arrival, recomputation and idempotency", "representation, compatibility, migration, provenance and conformance evidence"],
        "non_collapse_laws": ["timestamp syntax is not occurrence truth", "instant is not event", "duration is not interval or calendar period", "equal local text is not equal instant without offset/reference rules", "event time is not observed or recorded time", "valid time is not recording time", "forecast origin is not necessarily last observation time", "forecast horizon is not duration alone", "disposition due is not authorization or completed disposition", "eligibility is not effect", "retraction is not correction or supersession", "retraction is not deletion or erasure", "record retraction is not materialized-row retract", "request is not transition occurrence", "transition occurrence is not propagation completion", "late observation is not reordered truth"],
        "source_refs": ARCHETYPE_REFINEMENT_SOURCES["TIME_LIFECYCLE_AND_CONTROL"],
        "authority_limit": "RFC 3339, OWL-Time, forecasting literature, NARA, OpenTelemetry, PROV, Flink, etcd and Vault constrain their own timestamp, temporal, forecasting, disposition, event, provenance, changelog and lease models. They do not select a SAN owner, prove an occurrence, authorize disposition or unify record and materialization retraction.",
        "decision": "UNRESOLVED",
        "status": "PRIMARY_RESEARCH_COMPLETE_TIME_OWNER_AND_OCCURRENCE_ADJUDICATION_REQUIRED",
    }]


def time_contract_classification_candidates(
    batches: list[dict[str, Any]],
    symbols: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    packet_by_ref = {row["packet_id"]: row for row in symbols}
    rows = []
    for batch in (row for row in batches if row["research_archetype"] == "TIME_LIFECYCLE_AND_CONTROL"):
        for packet_ref in batch["packet_refs"]:
            packet = packet_by_ref[packet_ref]
            symbol_ref = packet["symbol_ref"]
            role = classify_time_role(symbol_ref)
            detail = TIME_ROLE_DETAILS[role]
            rows.append({
                "record_kind": "time_contract_classification_candidate",
                "candidate_id": f"candidate.p1.time-contract.{symbol_ref.replace('.', '-')}.v1",
                "edition": 1,
                "research_ref": "research.p1.archetype.time-lifecycle-control.v1",
                "research_program_ref": "program.p1.symbol-archetype.time-lifecycle-and-control.v1",
                "batch_ref": batch["batch_id"],
                "symbol_packet_ref": packet_ref,
                "symbol_ref": symbol_ref,
                "family_refs": packet["family_refs"],
                "affected_occurrences": packet["occurrences"],
                "represented_occurrence_count": packet["library_count"],
                "candidate_time_role": role,
                "candidate_semantic_position": detail["semantic_position"],
                "candidate_disposition_hypothesis": detail["candidate_disposition"],
                "local_time_requirements": detail["local_requirements"],
                "occurrence_profile_candidates": time_occurrence_profiles(symbol_ref, packet["occurrences"]),
                "source_refs": list(ARCHETYPE_REFINEMENT_SOURCES["TIME_LIFECYCLE_AND_CONTROL"]),
                "required_owner_decisions": ["semantic subject temporal role owner and exact edition", "time axis reference system calendar clock zone offset precision and uncertainty", "identity equality ordering overlap tie and open-end semantics", "event observed processing valid recording and commit time boundaries", "forecast origin information cut horizon target and evaluation boundaries", "retention trigger duration schedule hold precedence eligibility and authority", "transition request occurrence effect propagation receipt and terminal knowledge", "retraction correction supersession invalidation deletion erasure recall and compensation boundaries", "late stale concurrent replay recomputation and idempotency semantics", "per-occurrence shared import qualified homonym or split", "representation compatibility migration historical replay and public-name disposition"],
                "non_collapse_laws": ["timestamp is not event", "event time is not observed or recorded time", "duration is not interval", "forecast horizon is not duration alone", "due is not authorized", "request is not occurrence", "retraction is not deletion", "record retraction is not row retract"],
                "classification_basis": "BOUNDED_PRIMARY_RESEARCH_PLUS_SYMBOL_AND_USE_SITE_ROUTING_NOT_A_TEMPORAL_OWNER_OCCURRENCE_AUTHORITY_OR_EFFECT_DECISION",
                "authority_limit": "This candidate selects a temporal/lifecycle role and falsifiable disposition hypothesis only; it proves no occurrence, clock accuracy, model fitness, disposition authority, completed transition or propagation.",
                "decision": "UNRESOLVED",
                "status": "CANDIDATE_REQUIRES_TIME_OWNER_AND_OCCURRENCE_ADJUDICATION",
            })
    return sorted(rows, key=lambda row: row["symbol_ref"])


FAILURE_ROLE_DETAILS: dict[str, dict[str, Any]] = {
    "PROFILED_CANONICALIZATION_FAILURE": {
        "semantic_position": "TYPED_FAILURE_OF_A_NAMED_CANONICALIZATION_PROFILE_STAGE_OR_PRECONDITION",
        "candidate_disposition": "CANONICAL_SHARED_OWNER_AND_PROFILED_IMPORTS",
        "local_requirements": ["semantic object, canonicalization profile and exact edition", "parse/validation/normalization/serialization/stability stage", "invalid input, unsupported construct, non-finite value, duplicate/order and resource variants", "failure kept separate from noncanonical-but-accepted input, digest mismatch and semantic inequality"],
    },
    "DIMENSION_ALGEBRA_SEMANTIC_ERROR": {
        "semantic_position": "PURE_TYPED_FAILURE_OR_UNDEFINED_OUTCOME_OF_AN_EXACT_QUANTITY_DIMENSION_ALGEBRA",
        "candidate_disposition": "CANONICAL_SHARED_OWNER_AND_IMPORTS",
        "local_requirements": ["algebra and input expression editions", "unknown symbol, incompatible kind/dimension, invalid operation and unsupported unit profile variants", "source span/path, partial derivation and residual diagnostics", "semantic error kept separate from parser, provider, resource and cancellation failures"],
    },
    "PUBLICATION_PROFILE_COMPILATION_REFUSAL": {
        "semantic_position": "TYPED_REFUSAL_TO_COMPILE_OR_ACCEPT_A_PUBLICATION_PROFILE_REQUEST_UNDER_AN_EXACT_DOMAIN_PROFILE",
        "candidate_disposition": "CANONICAL_SHARED_OWNER_AND_PROFILED_IMPORTS",
        "local_requirements": ["publication-profile identity, edition, domain profile and compiler stage", "invalid declaration, unresolved reference, incompatible constraint, missing authority/evidence and unsupported capability variants", "coverage, partial diagnostics, retryability and correction path", "refusal kept separate from nonconformance result, publication denial, delivery failure and recall"],
    },
}


def classify_failure_role(symbol_ref: str) -> str:
    return {
        "type.canonicalizationerror": "PROFILED_CANONICALIZATION_FAILURE",
        "type.dimensionalgebraerror": "DIMENSION_ALGEBRA_SEMANTIC_ERROR",
        "type.publicationprofilerefusal": "PUBLICATION_PROFILE_COMPILATION_REFUSAL",
    }[symbol_ref]


def failure_occurrence_profiles(symbol_ref: str, occurrences: list[dict[str, Any]]) -> list[dict[str, str]]:
    exact = {
        ("type.canonicalizationerror", "library.csp.identity.canonicalization"): "GENERIC_SEMANTIC_CANONICALIZATION_FAILURE_OWNER_CANDIDATE_WITH_PROFILE_STAGE_PATH_PARTIALITY_AND_STABILITY_REQUIREMENTS",
        ("type.canonicalizationerror", "library.lpe.canonical-json"): "JCS_PROFILED_CANONICAL_JSON_FAILURE_WITH_I_JSON_NUMBER_STRING_PROPERTY_ORDER_SERIALIZATION_AND_RESOURCE_VARIANTS",
        ("type.dimensionalgebraerror", "library.csp.quantity.dimension-algebra"): "CANONICAL_QUANTITY_DIMENSION_ALGEBRA_ERROR_OWNER_CANDIDATE_WITH_TYPED_INVALID_UNDEFINED_UNSUPPORTED_AND_UNKNOWN_VARIANTS",
        ("type.dimensionalgebraerror", "library.smf.dimension_algebra"): "SEMANTIC_FORMULA_IMPORT_OF_DIMENSION_ALGEBRA_ERROR_WITH_FORMULA_SOURCE_SPAN_SYMBOL_BINDING_AND_DIAGNOSTIC_PROFILE",
        ("type.publicationprofilerefusal", "library.forecast.publication.profile.compiler"): "FORECAST_PUBLICATION_PROFILE_COMPILATION_REFUSAL_WITH_ORIGIN_HORIZON_VINTAGE_UNCERTAINTY_AUDIENCE_AND_AUTHORITY_VARIANTS",
        ("type.publicationprofilerefusal", "library.spatial_result.publication.profile.compiler"): "SPATIAL_PUBLICATION_PROFILE_COMPILATION_REFUSAL_WITH_CRS_GEOMETRY_ACCURACY_LINEAGE_DISCLOSURE_AND_AUTHORITY_VARIANTS",
    }
    return [
        {
            "library_ref": occurrence["library_ref"],
            "candidate_failure_profile": exact.get(
                (symbol_ref, occurrence["library_ref"]),
                "CANDIDATE_FAILURE_ROLE_REQUIRES_LOCAL_OPERATION_STAGE_CATEGORY_PARTIALITY_RETRY_EFFECT_AND_EVIDENCE_ADJUDICATION",
            ),
        }
        for occurrence in occurrences
    ]


def failure_archetype_research() -> list[dict[str, Any]]:
    return [{
        "record_kind": "archetype_semantic_research_candidate",
        "research_id": "research.p1.archetype.failure-refusal-partiality.v1",
        "edition": 1,
        "archetype_id": "FAILURE_REFUSAL_AND_PARTIALITY",
        "bounded_finding": "Invalid input, semantic undefinedness, unsupported capability, not-applicable evaluation, successful negative domain result, legitimate refusal, cancellation, deadline, resource exhaustion, provider/infrastructure failure, partial result, unknown completion and completed effect with failed acknowledgement are distinct outcomes. A reusable failure carrier must bind the requested operation and stage, exact semantic/profile editions and input cut, failure occurrence/category/domain variant, cause and evidence, partial output and coverage, retry/recovery/compensation posture, completion and effect knowledge, authority and transport mapping. Canonicalization and publication-profile failures may share an outer envelope only through explicit profiles; the dimension-algebra error belongs to the quantity algebra and is imported by the formula layer.",
        "required_contract_dimensions": ["operation, stage, subject, semantic owner and exact profile editions", "failure occurrence identity, category, typed domain variant and precedence", "input validity, semantic undefinedness, not applicability and negative-result boundaries", "cancellation, deadline, resource exhaustion, provider failure and dependency failure boundaries", "partial output, completed dimensions, residual, unknown and unsupported coverage", "requested, attempted, committed, observed, acknowledged and compensated effect knowledge", "retry safety, idempotency, deduplication, backoff, recovery and operator-action posture", "cause chain, sensitive detail policy, provenance, integrity and evidence", "domain carrier versus HTTP/telemetry/log/exception representation", "compatibility, migration, exhaustive handling and unknown-variant behavior", "appraisal, acceptance, authorization and business-conclusion boundaries"],
        "non_collapse_laws": ["negative domain result is not failure", "invalid request is not subject defect", "not applicable is not false or deny", "semantic undefinedness is not provider failure", "refusal is not cancellation", "cancellation request is not cessation", "deadline is not proof no effect occurred", "resource exhaustion is not unsupported capability", "provider failure is not domain refusal", "partial result is not failure without a contract", "unknown completion is not failure or success", "error value is not exception or transport problem document", "retryable is not idempotent", "logged error is not failure truth", "compensation is not erasure of prior effect"],
        "source_refs": ARCHETYPE_REFINEMENT_SOURCES["FAILURE_REFUSAL_AND_PARTIALITY"],
        "authority_limit": "RFC 9457, OpenTelemetry, XACML, JCS, UCUM, OpenFormula and PROF constrain their own transport, telemetry, policy, canonicalization, unit, formula and profile semantics. They do not define one universal failure algebra, select SAN owners, prove completion or authorize retry, compensation or acceptance.",
        "decision": "UNRESOLVED",
        "status": "PRIMARY_RESEARCH_COMPLETE_FAILURE_OWNER_AND_OCCURRENCE_ADJUDICATION_REQUIRED",
    }]


def failure_contract_classification_candidates(
    batches: list[dict[str, Any]],
    symbols: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    packet_by_ref = {row["packet_id"]: row for row in symbols}
    rows = []
    for batch in (row for row in batches if row["research_archetype"] == "FAILURE_REFUSAL_AND_PARTIALITY"):
        for packet_ref in batch["packet_refs"]:
            packet = packet_by_ref[packet_ref]
            symbol_ref = packet["symbol_ref"]
            role = classify_failure_role(symbol_ref)
            detail = FAILURE_ROLE_DETAILS[role]
            rows.append({
                "record_kind": "failure_contract_classification_candidate",
                "candidate_id": f"candidate.p1.failure-contract.{symbol_ref.replace('.', '-')}.v1",
                "edition": 1,
                "research_ref": "research.p1.archetype.failure-refusal-partiality.v1",
                "research_program_ref": "program.p1.symbol-archetype.failure-refusal-and-partiality.v1",
                "batch_ref": batch["batch_id"],
                "symbol_packet_ref": packet_ref,
                "symbol_ref": symbol_ref,
                "family_refs": packet["family_refs"],
                "affected_occurrences": packet["occurrences"],
                "represented_occurrence_count": packet["library_count"],
                "candidate_failure_role": role,
                "candidate_semantic_position": detail["semantic_position"],
                "candidate_disposition_hypothesis": detail["candidate_disposition"],
                "local_failure_requirements": detail["local_requirements"],
                "occurrence_profile_candidates": failure_occurrence_profiles(symbol_ref, packet["occurrences"]),
                "source_refs": list(ARCHETYPE_REFINEMENT_SOURCES["FAILURE_REFUSAL_AND_PARTIALITY"]),
                "required_owner_decisions": ["operation stage subject owner and exact profile editions", "failure occurrence category domain variant and precedence", "invalid undefined unsupported not-applicable negative-result refusal and failure boundaries", "cancellation deadline resource provider dependency partial and unknown-completion semantics", "partial output residual coverage effect and acknowledgement knowledge", "retry idempotency dedup recovery compensation and operator-action posture", "cause evidence sensitive detail provenance and integrity", "domain carrier transport mapping exception and telemetry representation boundaries", "per-occurrence shared import profiled import qualified homonym or split", "compatibility migration exhaustive handling and public-name disposition"],
                "non_collapse_laws": ["negative result is not failure", "invalid is not refusal", "not applicable is not false", "cancelled is not failed", "resource exhaustion is not unsupported", "provider failure is not domain refusal", "partial is not unknown", "retryable is not idempotent", "transport error is not domain failure"],
                "classification_basis": "BOUNDED_PRIMARY_RESEARCH_PLUS_SYMBOL_AND_USE_SITE_ROUTING_NOT_A_FAILURE_OWNER_COMPLETION_RETRY_OR_EFFECT_DECISION",
                "authority_limit": "This candidate selects a failure/refusal role and falsifiable disposition hypothesis only; it proves no cause, completion, retry safety, compensation, conformance or business acceptance.",
                "decision": "UNRESOLVED",
                "status": "CANDIDATE_REQUIRES_FAILURE_OWNER_AND_OCCURRENCE_ADJUDICATION",
            })
    return sorted(rows, key=lambda row: row["symbol_ref"])


MODEL_ARTIFACT_ROLE_DETAILS: dict[str, dict[str, Any]] = {
    "ANOMALY_BASELINE_MODEL_ARTIFACT": {
        "semantic_position": "VERSIONED_REFERENCE_MODEL_ARTIFACT_PRODUCED_FROM_A_BOUND_POPULATION_DATA_CUT_FEATURE_SCHEMA_AND_BASELINE_METHOD",
        "candidate_disposition": "FAMILY_SHARED_OWNER_AND_IMPORTS",
        "candidate_owner": "library.method_kernels.anomaly_baseline",
        "local_requirements": ["baseline subject population segment and operating regime", "reference/training data cut, feature/schema editions and time window", "baseline method, configuration, learned statistics/state and uncertainty", "validity/applicability window, drift/update triggers, supersession and provenance", "baseline kept separate from current observation, threshold, alert and anomaly judgment"],
    },
    "FITTED_FORECAST_MODEL_ARTIFACT": {
        "semantic_position": "VERSIONED_FORECASTER_ARTIFACT_PRODUCED_BY_FITTING_AN_EXACT_MODEL_SPECIFICATION_TO_A_BOUND_TRAINING_CUT",
        "candidate_disposition": "FAMILY_SHARED_OWNER_AND_IMPORTS",
        "candidate_owner": "library.method_kernels.forecast_estimators",
        "local_requirements": ["forecast target, population, time axis, cutoff and schema editions", "model specification, hyperparameters, learned state and fitting method", "training data cut, exogenous features, transformations, randomness and environment", "artifact signature, operator/runtime dependencies, fit occurrence and provenance", "fitted kept separate from evaluated, selected, approved, deployed, active, fit-for-use and prediction"],
    },
}


def classify_model_artifact_role(symbol_ref: str) -> str:
    return {
        "type.baselineartifact": "ANOMALY_BASELINE_MODEL_ARTIFACT",
        "type.fittedforecaster": "FITTED_FORECAST_MODEL_ARTIFACT",
    }[symbol_ref]


def model_artifact_occurrence_profiles(symbol_ref: str, occurrences: list[dict[str, Any]]) -> list[dict[str, str]]:
    exact = {
        ("type.baselineartifact", "library.method_kernels.anomaly_baseline"): "ANOMALY_BASELINE_ARTIFACT_OWNER_CANDIDATE_BINDING_REFERENCE_POPULATION_DATA_CUT_FEATURE_SCHEMA_METHOD_LEARNED_STATE_VALIDITY_DRIFT_AND_PROVENANCE",
        ("type.baselineartifact", "library.method_kernels.anomaly_detectors"): "ANOMALY_DETECTOR_IMPORT_OF_A_VERSIONED_BASELINE_ARTIFACT_WITH_COMPATIBILITY_APPLICABILITY_AND_DRIFT_PRECONDITIONS",
        ("type.fittedforecaster", "library.method_kernels.forecast_estimators"): "FITTED_FORECASTER_ARTIFACT_OWNER_CANDIDATE_BINDING_MODEL_SPEC_TRAINING_CUT_TARGET_FEATURES_TRANSFORMS_LEARNED_STATE_CUTOFF_RANDOMNESS_ENVIRONMENT_AND_PROVENANCE",
        ("type.fittedforecaster", "library.method_kernels.forecasting_methods"): "FORECASTING_METHOD_IMPORT_OF_A_FITTED_FORECASTER_WITH_TARGET_HORIZON_FEATURE_SCHEMA_RUNTIME_AND_ARTIFACT_COMPATIBILITY_PRECONDITIONS",
    }
    return [
        {
            "library_ref": occurrence["library_ref"],
            "candidate_model_artifact_profile": exact.get(
                (symbol_ref, occurrence["library_ref"]),
                "CANDIDATE_MODEL_ARTIFACT_REQUIRES_LOCAL_METHOD_DATA_CUT_SCHEMA_STATE_LIFECYCLE_COMPATIBILITY_AND_PROVENANCE_ADJUDICATION",
            ),
        }
        for occurrence in occurrences
    ]


def model_artifact_archetype_research() -> list[dict[str, Any]]:
    return [{
        "record_kind": "archetype_semantic_research_candidate",
        "research_id": "research.p1.archetype.analytical-model-artifact-and-state.v1",
        "edition": 1,
        "archetype_id": "ANALYTICAL_MODEL_ARTIFACT_AND_STATE",
        "bounded_finding": "A model specification, fitting/training occurrence, fitted artifact edition, evaluation result, selection decision, approval, deployment, active serving instance, prediction, monitoring result and retirement are distinct semantic objects and lifecycle states. A fitted artifact binds an exact model or baseline method to learned state, a data cut, target/feature schemas, time/cutoff, configuration, randomness/runtime dependencies and provenance. A baseline artifact is a reference-model artifact, not a current observation, threshold, alert or anomaly judgment. Refit or baseline recomputation creates a new semantic artifact edition; a content digest identifies bytes under an exact representation and does not prove semantic equivalence, fitness or approval.",
        "required_contract_dimensions": ["artifact kind, semantic owner, stable edition identity and equality", "model/baseline specification, method and exact configuration editions", "training/reference population, data cut, target, features, transformations and schema", "learned state, parameters/statistics, randomness, software, operator set and runtime environment", "fit/training occurrence, producer, timestamps, inputs, outputs and provenance", "evaluation evidence, selection, approval and relying-purpose fitness as separate relations", "deployment edition, serving/runtime state, monitoring, drift, supersession and retirement", "input/output signature, portability, compatibility, migration and conformance", "uncertainty, validity/applicability window, exclusions and failure/partiality", "privacy, disclosure, licensing, security and resource bounds where applicable"],
        "non_collapse_laws": ["model specification is not fitted artifact", "fit occurrence is not fitted artifact identity", "fitted is not evaluated", "evaluated is not selected", "selected is not approved", "approved is not deployed", "deployed is not active serving", "artifact is not runtime instance", "artifact is not prediction", "baseline is not observation", "baseline is not threshold", "threshold crossing is not anomaly diagnosis", "content digest is not semantic equivalence", "format validation is not execution compatibility", "portability is not deterministic numerical equivalence", "refit or baseline recomputation creates a new artifact edition", "monitoring or drift evidence does not mutate historical artifact truth"],
        "source_refs": ARCHETYPE_REFINEMENT_SOURCES["ANALYTICAL_MODEL_ARTIFACT_AND_STATE"],
        "authority_limit": "MLflow, ONNX, sktime, NIST process monitoring and PROV constrain packaging, representation, forecaster state, baseline construction and provenance in their own scopes. They do not select SAN owners, prove model equivalence or fitness, grant approval or deployment authority, or guarantee deterministic predictions across unspecified runtimes.",
        "decision": "UNRESOLVED",
        "status": "PRIMARY_RESEARCH_COMPLETE_MODEL_ARTIFACT_OWNER_AND_OCCURRENCE_ADJUDICATION_REQUIRED",
    }]


def model_artifact_contract_classification_candidates(
    batches: list[dict[str, Any]],
    symbols: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    packet_by_ref = {row["packet_id"]: row for row in symbols}
    rows = []
    for batch in (row for row in batches if row["research_archetype"] == "ANALYTICAL_MODEL_ARTIFACT_AND_STATE"):
        for packet_ref in batch["packet_refs"]:
            packet = packet_by_ref[packet_ref]
            symbol_ref = packet["symbol_ref"]
            role = classify_model_artifact_role(symbol_ref)
            detail = MODEL_ARTIFACT_ROLE_DETAILS[role]
            rows.append({
                "record_kind": "model_artifact_contract_classification_candidate",
                "candidate_id": f"candidate.p1.model-artifact-contract.{symbol_ref.replace('.', '-')}.v1",
                "edition": 1,
                "research_ref": "research.p1.archetype.analytical-model-artifact-and-state.v1",
                "research_program_ref": "program.p1.symbol-archetype.analytical-model-artifact-and-state.v1",
                "batch_ref": batch["batch_id"],
                "symbol_packet_ref": packet_ref,
                "symbol_ref": symbol_ref,
                "family_refs": packet["family_refs"],
                "affected_occurrences": packet["occurrences"],
                "represented_occurrence_count": packet["library_count"],
                "candidate_model_artifact_role": role,
                "candidate_semantic_position": detail["semantic_position"],
                "candidate_disposition_hypothesis": detail["candidate_disposition"],
                "candidate_owner_hypothesis": detail["candidate_owner"],
                "local_artifact_requirements": detail["local_requirements"],
                "occurrence_profile_candidates": model_artifact_occurrence_profiles(symbol_ref, packet["occurrences"]),
                "source_refs": list(ARCHETYPE_REFINEMENT_SOURCES["ANALYTICAL_MODEL_ARTIFACT_AND_STATE"]),
                "required_owner_decisions": ["artifact semantic kind owner identity equality and editioning", "method specification training/reference data cut target features transforms and schemas", "learned state parameters statistics randomness environment and runtime dependencies", "fit/training occurrence provenance integrity privacy disclosure and licensing", "evaluation selection approval deployment serving monitoring drift supersession and retirement separations", "signature portability compatibility migration conformance and deterministic-runtime requirements", "partial invalid unsupported stale incompatible and unavailable artifact outcomes", "per-occurrence owner import local refinement or qualified-homonym disposition", "public-name migration and no compatibility alias"],
                "non_collapse_laws": ["specification is not fitted artifact", "fitted is not evaluated selected approved or deployed", "artifact is not runtime instance or prediction", "baseline is not observation threshold alert or diagnosis", "digest is not semantic equivalence", "format validity is not fitness or execution compatibility"],
                "classification_basis": "BOUNDED_PRIMARY_RESEARCH_PLUS_SYMBOL_AND_USE_SITE_ROUTING_NOT_A_MODEL_OWNER_IDENTITY_FITNESS_APPROVAL_DEPLOYMENT_OR_COMPATIBILITY_DECISION",
                "authority_limit": "This candidate selects a model-artifact role, owner hypothesis and import seam only; it proves no semantic equivalence, fitness, approval, deployment, prediction truth or runtime conformance.",
                "decision": "UNRESOLVED",
                "status": "CANDIDATE_REQUIRES_MODEL_ARTIFACT_OWNER_AND_OCCURRENCE_ADJUDICATION",
            })
    return sorted(rows, key=lambda row: row["symbol_ref"])


EVIDENCE_ROLE_DETAILS: dict[str, dict[str, str]] = {
    "RUNTIME_EXECUTION_RECEIPT": {"lifecycle_position": "EXECUTION_OCCURRENCE_EVIDENCE", "authority_posture": "RECORDS_ATTEMPT_AND_OUTCOME_WITHOUT_PROVING_SEMANTIC_CORRECTNESS"},
    "PROFILE_EVIDENCE_SET": {"lifecycle_position": "POLICY_COMPILATION_INPUT_EVIDENCE", "authority_posture": "SUPPORTS_PROFILE_COMPILATION_WITHOUT_ACTIVATING_OR_AUTHORIZING_PUBLICATION"},
    "POLICY_DECISION_EVIDENCE_RECORD": {"lifecycle_position": "POLICY_EVALUATION_RECORD", "authority_posture": "RECORDS_INPUT_POLICY_AND_DECISION_WITHOUT_PROVING_ENFORCEMENT"},
    "VERIFICATION_APPRAISAL_RESULT": {"lifecycle_position": "SCOPED_VERIFICATION_RESULT", "authority_posture": "VERIFIES_DECLARED_PROPERTY_ONLY_WITHOUT_PROVING_TRUTH_OR_FITNESS"},
    "CLAIM_APPRAISAL_RESULT": {"lifecycle_position": "CLAIM_ARGUMENT_EVIDENCE_APPRAISAL", "authority_posture": "APPRAISAL_WITHOUT_RELYING_PARTY_ACCEPTANCE_OR_ACTION_AUTHORITY"},
}


def classify_evidence_role(symbol_ref: str) -> str:
    return {
        "type.codecreceipt": "RUNTIME_EXECUTION_RECEIPT",
        "type.kernelreceipt": "RUNTIME_EXECUTION_RECEIPT",
        "type.publicationprofileevidence": "PROFILE_EVIDENCE_SET",
        "type.decision_receipt": "POLICY_DECISION_EVIDENCE_RECORD",
        "type.verificationresult": "VERIFICATION_APPRAISAL_RESULT",
        "type.experimentconclusionappraisal": "CLAIM_APPRAISAL_RESULT",
        "type.contract.application.effect_receipt": "RUNTIME_EXECUTION_RECEIPT",
        "type.contract.application.execution_receipt": "RUNTIME_EXECUTION_RECEIPT",
    }[symbol_ref]


ANALYTICAL_RESULT_ROLE_DETAILS: dict[str, dict[str, str]] = {
    "SEALED_ANALYSIS_RESULT_EDITION": {"result_position": "IMMUTABLE_ANALYSIS_RESULT_SNAPSHOT", "claim_posture": "RESULT_EDITION_NOT_CONCLUSION_DECISION_OR_PUBLICATION"},
    "COMPARISON_RESULT": {"result_position": "METHOD_SCOPED_RELATION_RESULT", "claim_posture": "COMPARISON_UNDER_EXACT_EQUIVALENCE_TOLERANCE_AND_INPUT_CUT"},
    "ALGEBRA_EVALUATION_OUTCOME": {"result_position": "FORMULA_OR_ALGEBRA_EVALUATION_OUTCOME", "claim_posture": "DERIVED_OUTCOME_NOT_OBSERVED_BUSINESS_FACT"},
    "CAUSAL_IDENTIFICATION_RESULT": {"result_position": "IDENTIFIED_ESTIMAND_OR_NONIDENTIFIABILITY_RESULT", "claim_posture": "IDENTIFICATION_UNDER_ASSUMPTIONS_NOT_EFFECT_ESTIMATE_OR_CAUSAL_TRUTH"},
    "CAUSAL_EFFECT_ESTIMATE": {"result_position": "ESTIMATOR_OUTPUT_BOUND_TO_ESTIMAND_POPULATION_DATA_CUT_ASSUMPTIONS_METHOD_AND_UNCERTAINTY", "claim_posture": "ESTIMATE_NOT_IDENTIFICATION_RESULT_CAUSAL_TRUTH_BUSINESS_CONCLUSION_OR_ACTION_AUTHORITY"},
}


def classify_analytical_result_role(symbol_ref: str) -> str:
    return {
        "type.experimentanalysisresultedition": "SEALED_ANALYSIS_RESULT_EDITION",
        "type.comparisonresult": "COMPARISON_RESULT",
        "type.dimensionalgebraoutcome": "ALGEBRA_EVALUATION_OUTCOME",
        "type.identificationresult": "CAUSAL_IDENTIFICATION_RESULT",
        "type.effectestimate": "CAUSAL_EFFECT_ESTIMATE",
    }[symbol_ref]


def analytical_result_occurrence_profiles(symbol_ref: str, occurrences: list[dict[str, Any]]) -> list[dict[str, str]]:
    exact = {
        ("type.effectestimate", "library.method_kernels.causal_effect_estimators"): "CAUSAL_ESTIMATOR_OUTPUT_WITH_ESTIMAND_ESTIMATOR_SAMPLE_DATA_CUT_POINT_OR_DISTRIBUTIONAL_ESTIMATE_AND_UNCERTAINTY_PROFILE",
        ("type.effectestimate", "library.method_kernels.causal_methods"): "GENERAL_CAUSAL_METHOD_RESULT_IMPORT_WITH_IDENTIFICATION_ASSUMPTIONS_ESTIMAND_AND_ESTIMATION_STAGE_PROFILE",
        ("type.effectestimate", "library.method_kernels.causal_refutation_sensitivity"): "REFERENCE_EFFECT_ESTIMATE_IMPORT_FOR_SENSITIVITY_OR_REFUTATION_COMPARISON_WITHOUT_REISSUING_CAUSAL_AUTHORITY",
    }
    return [
        {
            "library_ref": occurrence["library_ref"],
            "candidate_analytical_result_profile": exact.get(
                (symbol_ref, occurrence["library_ref"]),
                "CANDIDATE_ANALYTICAL_RESULT_REQUIRES_LOCAL_QUESTION_INPUT_METHOD_ASSUMPTION_UNCERTAINTY_AND_ACCEPTANCE_ADJUDICATION",
            ),
        }
        for occurrence in occurrences
    ]


def evidence_and_analytical_result_archetype_research() -> list[dict[str, Any]]:
    return [
        {
            "record_kind": "archetype_semantic_research_candidate",
            "research_id": "research.p1.archetype.evidence-receipt-appraisal-result.v1",
            "edition": 1,
            "archetype_id": "EVIDENCE_RECEIPT_APPRAISAL_AND_RESULT",
            "bounded_finding": "A claim or assertion, supporting evidence item, evidence bundle, cryptographic proof, evaluation request, evaluation occurrence, scoped result, execution receipt, transparency-registration receipt, appraisal verdict, policy decision, certificate, relying-party acceptance and authorized action are distinct lifecycle objects. Each evidence-bearing record must state exactly which bounded claim it can support, under which subject/input cut, method or policy edition, producer authority, time, provenance, integrity and coverage limits.",
            "required_contract_dimensions": ["claim, proposition or assertion identity and exact subject", "evidence item and bundle identity, content and provenance", "producer, issuer, evaluator and relying-party roles and authority scopes", "evaluation request, method/policy/rule edition and input snapshot", "evaluation occurrence, environment, time, budget and completion state", "typed result, verdict, coverage, unknowns and residuals", "execution receipt versus transparency-registration or inclusion receipt", "proof purpose, verification method, canonicalization and integrity scope", "appraisal criteria, defeaters, conflicts and precedence", "decision, obligation/advice, enforcement, certification and acceptance separation", "supersession, invalidation, revocation, retention and disclosure"],
            "non_collapse_laws": ["claim is not evidence", "evidence is not proof", "proof integrity is not claim truth", "result is not receipt", "execution receipt is not transparency receipt", "verification is not validation", "validation is not certification", "appraisal is not relying-party acceptance", "policy decision is not enforcement", "decision log is not effect receipt", "missing evidence is not negative evidence", "supersession is not deletion"],
            "source_refs": ARCHETYPE_REFINEMENT_SOURCES["EVIDENCE_RECEIPT_APPRAISAL_AND_RESULT"],
            "authority_limit": "PROV, SHACL, XACML, SCITT, VC Data Integrity, in-toto and OpenTelemetry constrain their own evidence, validation, decision, receipt and event models. They do not make any SAN claim true, select a relying-party policy or authorize an effect.",
            "decision": "UNRESOLVED",
            "status": "PRIMARY_RESEARCH_COMPLETE_EVIDENCE_OWNER_AND_OCCURRENCE_ADJUDICATION_REQUIRED",
        },
        {
            "record_kind": "archetype_semantic_research_candidate",
            "research_id": "research.p1.archetype.analytical-method-result-diagnostic.v1",
            "edition": 1,
            "archetype_id": "ANALYTICAL_METHOD_RESULT_AND_DIAGNOSTIC",
            "bounded_finding": "An analytical result is a method-scoped derived object bound to an exact question or estimand, input/data cut, method and parameter editions, assumptions, execution occurrence and termination state. Identified expression, estimate, prediction, comparison, optimization solution, diagnostic, sensitivity/refutation result, uncertainty, residual and evidence receipt remain distinct. Method success means only what the method contract states; it is not truth, causal authority, business importance, acceptance or permission to act.",
            "required_contract_dimensions": ["analytical question, estimand, objective or comparison relation", "subject/population, grain and immutable input/data cut", "method, algorithm, formula and parameter editions", "assumptions, admissibility, missingness and identifiability conditions", "execution occurrence, implementation offer, environment, random stream and resource budget", "termination, convergence, feasibility, optimality and completion knowledge", "primary result payload and semantic type", "uncertainty, diagnostics, warnings, residuals and unsupported dimensions", "sensitivity, robustness, refutation and counterfactual comparisons", "provenance, integrity, reproducibility and execution receipts", "appraisal, conclusion, decision, publication and action boundaries"],
            "non_collapse_laws": ["identified estimand is not estimate", "estimate is not causal truth", "prediction is not observation", "comparison result is not equivalence without a declared relation", "solver success is not global optimality", "termination is not semantic success", "diagnostic is not refusal", "result is not evidence receipt", "robustness check is not proof", "statistical significance is not business importance", "method result is not conclusion or action authority"],
            "source_refs": ARCHETYPE_REFINEMENT_SOURCES["ANALYTICAL_METHOD_RESULT_AND_DIAGNOSTIC"],
            "authority_limit": "ICH, PyWhy, SciPy and PROV constrain their own estimand, causal, optimization and provenance models. They do not define one universal result type or ratify the owner, assumptions or acceptance policy of any SAN analytical method.",
            "decision": "UNRESOLVED",
            "status": "PRIMARY_RESEARCH_COMPLETE_ANALYTICAL_RESULT_OWNER_AND_OCCURRENCE_ADJUDICATION_REQUIRED",
        },
    ]


def evidence_lane_refinement_candidates(
    batches: list[dict[str, Any]],
    symbols: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    batch_by_packet = {packet_ref: row for row in batches for packet_ref in row["packet_refs"]}
    packet_by_symbol = {row["symbol_ref"]: row for row in symbols}
    rows = []
    for symbol_ref, archetype in sorted(EVIDENCE_LANE_EXACT_ARCHETYPES.items()):
        packet = packet_by_symbol[symbol_ref]
        batch = batch_by_packet[packet["packet_id"]]
        rows.append({
            "record_kind": "evidence_lane_archetype_refinement_candidate",
            "refinement_id": f"refinement.p1.evidence-lane.{symbol_ref.replace('.', '-')}.v1",
            "edition": 1,
            "symbol_packet_ref": packet["packet_id"],
            "batch_ref": batch["batch_id"],
            "symbol_ref": symbol_ref,
            "family_refs": packet["family_refs"],
            "affected_occurrences": packet["occurrences"],
            "represented_occurrence_count": packet["library_count"],
            "candidate_archetype": archetype,
            "candidate_semantic_axis_refs": ARCHETYPE_SEMANTIC_AXES[archetype],
            "source_refs": ARCHETYPE_REFINEMENT_SOURCES[archetype],
            "classification_basis": "BOUNDED_PRIMARY_RESEARCH_PLUS_EXACT_SYMBOL_AND_USE_SITE_ROUTING_NOT_A_TRUTH_OR_ACCEPTANCE_DECISION",
            "authority_limit": "This correction selects an archetype and lifecycle question only; it does not establish claim truth, shared ownership, applicability, qualification, certification or acceptance.",
            "decision": "UNRESOLVED",
            "status": "CANDIDATE_REQUIRES_ARCHETYPE_OWNER_AND_OCCURRENCE_ADJUDICATION",
        })
    return rows


def evidence_contract_classification_candidates(
    batches: list[dict[str, Any]],
    symbols: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    packet_by_ref = {row["packet_id"]: row for row in symbols}
    rows = []
    for batch in (row for row in batches if row["research_archetype"] == "EVIDENCE_RECEIPT_APPRAISAL_AND_RESULT"):
        for packet_ref in batch["packet_refs"]:
            packet = packet_by_ref[packet_ref]
            symbol_ref = packet["symbol_ref"]
            role = classify_evidence_role(symbol_ref)
            detail = EVIDENCE_ROLE_DETAILS[role]
            rows.append({
                "record_kind": "evidence_contract_classification_candidate",
                "candidate_id": f"candidate.p1.evidence-contract.{symbol_ref.replace('.', '-')}.v1",
                "edition": 1,
                "research_ref": "research.p1.archetype.evidence-receipt-appraisal-result.v1",
                "research_program_ref": "program.p1.symbol-archetype.evidence-receipt-appraisal-and-result.v1",
                "batch_ref": batch["batch_id"],
                "symbol_packet_ref": packet_ref,
                "symbol_ref": symbol_ref,
                "family_refs": packet["family_refs"],
                "affected_occurrences": packet["occurrences"],
                "represented_occurrence_count": packet["library_count"],
                "candidate_evidence_role": role,
                "candidate_lifecycle_position": detail["lifecycle_position"],
                "candidate_authority_posture": detail["authority_posture"],
                "required_owner_decisions": ["claim/result/receipt semantic owner and exact edition", "subject and immutable input/evaluation cut", "producer/evaluator/issuer/relying-party authority", "method, policy, proof and canonicalization editions", "coverage, unknowns, residuals and defeaters", "integrity, provenance, supersession and disclosure", "decision, enforcement, certification and acceptance boundaries", "per-occurrence import, qualified homonym or split"],
                "non_collapse_laws": ["claim is not evidence", "proof is not truth", "result is not receipt", "receipt is not acceptance", "verification is not certification", "decision is not enforcement"],
                "classification_basis": "BOUNDED_PRIMARY_RESEARCH_PLUS_SYMBOL_AND_USE_SITE_ROUTING_NOT_A_TRUTH_OR_ACCEPTANCE_DECISION",
                "authority_limit": "This candidate selects an evidence lifecycle role only; it does not prove the recorded claim, grant authority, certify a subject or authorize reliance.",
                "decision": "UNRESOLVED",
                "status": "CANDIDATE_REQUIRES_EVIDENCE_OWNER_AND_OCCURRENCE_ADJUDICATION",
            })
    return sorted(rows, key=lambda row: row["symbol_ref"])


def analytical_result_classification_candidates(
    batches: list[dict[str, Any]],
    symbols: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    packet_by_ref = {row["packet_id"]: row for row in symbols}
    rows = []
    for batch in (row for row in batches if row["research_archetype"] == "ANALYTICAL_METHOD_RESULT_AND_DIAGNOSTIC"):
        for packet_ref in batch["packet_refs"]:
            packet = packet_by_ref[packet_ref]
            symbol_ref = packet["symbol_ref"]
            role = classify_analytical_result_role(symbol_ref)
            detail = ANALYTICAL_RESULT_ROLE_DETAILS[role]
            rows.append({
                "record_kind": "analytical_result_classification_candidate",
                "candidate_id": f"candidate.p1.analytical-result.{symbol_ref.replace('.', '-')}.v1",
                "edition": 1,
                "research_ref": "research.p1.archetype.analytical-method-result-diagnostic.v1",
                "research_program_ref": "program.p1.symbol-archetype.analytical-method-result-and-diagnostic.v1",
                "batch_ref": batch["batch_id"],
                "symbol_packet_ref": packet_ref,
                "symbol_ref": symbol_ref,
                "family_refs": packet["family_refs"],
                "affected_occurrences": packet["occurrences"],
                "represented_occurrence_count": packet["library_count"],
                "candidate_result_role": role,
                "candidate_result_position": detail["result_position"],
                "candidate_claim_posture": detail["claim_posture"],
                "occurrence_profile_candidates": analytical_result_occurrence_profiles(symbol_ref, packet["occurrences"]),
                "required_owner_decisions": ["analytical question/estimand/objective and owner", "input population, grain and immutable data cut", "method, parameters, assumptions and implementation offer", "termination, convergence, feasibility and completion semantics", "result payload, uncertainty, diagnostics and residuals", "provenance, execution receipt and reproducibility evidence", "appraisal, conclusion, publication and action boundaries", "per-occurrence import, qualified homonym or split"],
                "non_collapse_laws": ["method result is not truth", "identified estimand is not estimate", "termination is not semantic success", "diagnostic is not evidence receipt", "result is not conclusion", "conclusion is not authority to act"],
                "classification_basis": "BOUNDED_PRIMARY_RESEARCH_PLUS_SYMBOL_AND_USE_SITE_ROUTING_NOT_A_RESULT_TRUTH_OR_ACCEPTANCE_DECISION",
                "authority_limit": "This candidate selects a method-result role only; it does not validate assumptions, strengthen a claim, establish truth or authorize a conclusion or action.",
                "decision": "UNRESOLVED",
                "status": "CANDIDATE_REQUIRES_ANALYTICAL_RESULT_OWNER_AND_OCCURRENCE_ADJUDICATION",
            })
    return sorted(rows, key=lambda row: row["symbol_ref"])


def source_packets() -> list[dict[str, Any]]:
    packages = {row["family_id"]: row for row in load_jsonl(SEM / "structured_projection/source-authority-work-packages.jsonl")}
    audits = {row["family_id"]: row for row in load_jsonl(SEM / "source_authority_audit/readiness-audits.jsonl")}
    rows = []
    for family_id, package in packages.items():
        audit = audits[family_id]
        rows.append({
            "record_kind": "source_authority_adjudication_packet",
            "packet_id": f"packet.p1.source-authority.{family_id.split('.')[-1]}.v1",
            "edition": 1,
            "family_id": family_id,
            "library_count": package["library_count"],
            "library_refs": package["library_refs"],
            "source_path": package["source_path"],
            "source_digest": package["source_file_sha256"],
            "validator_receipt_ref": audit["validator_receipt_ref"],
            "structural_readiness": audit["readiness"],
            "structural_controls_missing": audit["missing_or_failed_controls"],
            "decision": "UNRESOLVED",
            "allowed_decisions": ["ADOPT_CANONICAL", "ADOPT_WITH_TRANSFORM", "SPLIT", "MERGE", "REPLACE", "REJECT", "UNRESOLVED"],
            "required_adjudication": package["required_outputs"],
            "required_evidence": ["schema authority", "record authority", "bounded primary evidence claims", "conflict appraisal", "field-level transformation decision", "named ratifier"],
            "non_collapse_laws": ["validator pass is not source authority", "schema authority is not record authority", "source adoption is not semantic ratification", "source digest identity is not truth"],
            "priority_score": package["library_count"] * 100,
            "authority_limit": "This packet proves structural readiness and binds the exact source digest. Only a named authority decision with bounded evidence may adopt any source field.",
            "status": "DECISION_PACKET_READY_AUTHORITY_UNRESOLVED",
        })
    rows.sort(key=lambda row: (-row["priority_score"], row["family_id"]))
    for rank, row in enumerate(rows, 1):
        row["priority_rank"] = rank
    return rows


def symbol_packets() -> list[dict[str, Any]]:
    collisions = load_jsonl(SEM / "p0_identity_grain/global-symbol-collisions.jsonl")
    rows = []
    for collision in collisions:
        conflicting = collision["definition_digest_count"] > 1
        cross_family = collision["family_count"] > 1
        if conflicting:
            research_route = "HOMONYM_OR_DEFINITION_CONFLICT_RESEARCH"
        elif cross_family:
            research_route = "CROSS_FAMILY_SHARED_OWNER_HYPOTHESIS_RESEARCH"
        else:
            research_route = "FAMILY_SHARED_OWNER_OR_LOCAL_IMPORT_RESEARCH"
        priority_score = collision["family_count"] * 1000 + collision["library_count"] * 100 + collision["definition_digest_count"] * 10
        rows.append({
            "record_kind": "public_symbol_adjudication_packet",
            "packet_id": collision["collision_id"].replace("collision.p0", "packet.p1"),
            "edition": 1,
            "collision_ref": collision["collision_id"],
            "symbol_kind": collision["symbol_kind"],
            "symbol_ref": collision["symbol_ref"],
            "family_refs": collision["family_refs"],
            "library_count": collision["library_count"],
            "occurrences": collision["occurrences"],
            "definition_digests": collision["definition_digests"],
            "definition_evidence_strength": "LEXICAL_AND_STRUCTURAL_CANDIDATE_ONLY",
            "research_route": research_route,
            "shared_owner_hypothesis": not conflicting,
            "decision": "UNRESOLVED",
            "allowed_dispositions": collision["allowed_dispositions"],
            "required_questions": ["Do occurrences denote the same semantic object and equality relation?", "Which bounded context owns the meaning?", "Are carrier shape and lifecycle identical or merely similarly named?", "Which libraries import the owner and which require qualified local symbols?", "What migration removes duplicate declarations without compatibility aliases?"],
            "required_evidence": ["owner definitions", "identity and equality laws", "lifecycle and time laws", "operation use sites", "negative homonym twins", "named owner decision"],
            "compiler_refusal": collision["compiler_refusal"],
            "priority_score": priority_score,
            "authority_limit": "Equal names or identical placeholder digests do not establish semantic equality or a shared owner. This packet routes adjudication only.",
            "status": "ADJUDICATION_PACKET_READY_NO_SYMBOL_UNIFICATION",
        })
    rows.sort(key=lambda row: (-row["priority_score"], row["symbol_kind"], row["symbol_ref"]))
    for rank, row in enumerate(rows, 1):
        row["priority_rank"] = rank
    return rows


def work_waves(symbols: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str], list[dict[str, Any]]] = collections.defaultdict(list)
    for row in symbols:
        groups[(row["research_route"], row["symbol_kind"])].append(row)
    waves = []
    ordered = sorted(groups.items(), key=lambda item: (-sum(row["priority_score"] for row in item[1]), item[0]))
    for index, ((route, kind), rows) in enumerate(ordered, 1):
        waves.append({
            "record_kind": "symbol_adjudication_work_wave",
            "wave_id": f"wave.p1.symbol.{index:02d}",
            "edition": 1,
            "research_route": route,
            "symbol_kind": kind,
            "packet_refs": [row["packet_id"] for row in rows],
            "packet_count": len(rows),
            "represented_occurrence_count": sum(row["library_count"] for row in rows),
            "family_refs": sorted({family for row in rows for family in row["family_refs"]}),
            "execution_law": "Research shared semantic definitions and counterexamples once for the wave, then require an explicit decision for every packet; do not infer member decisions from the modal result.",
            "status": "OPEN_BATCH_RESEARCH_WAVE",
        })
    return waves


def schema() -> dict[str, Any]:
    return {"$schema": "https://json-schema.org/draft/2020-12/schema", "$id": "https://san.example/spec/p1-symbol-adjudication-packet-v1.schema.json", "type": "object", "required": ["record_kind", "packet_id", "edition", "symbol_kind", "symbol_ref", "family_refs", "library_count", "occurrences", "definition_digests", "definition_evidence_strength", "research_route", "shared_owner_hypothesis", "decision", "allowed_dispositions", "required_questions", "required_evidence", "compiler_refusal", "priority_score", "authority_limit", "status", "priority_rank"]}


def outputs() -> dict[str, str]:
    sources = source_packets(); symbols = symbol_packets(); waves = work_waves(symbols); research = high_fanout_research(symbols)
    applicability = occurrence_applicability(research)
    remaining_batches = remaining_symbol_research_batches(symbols, research)
    archetype_programs = archetype_research_programs(remaining_batches, sources)
    archetype_research = operation_archetype_research() + catchall_refinement_research() + capability_port_archetype_research() + policy_archetype_research() + identity_archetype_research() + authority_archetype_research() + representation_archetype_research() + resource_archetype_research() + shape_archetype_research() + measure_archetype_research() + time_archetype_research() + failure_archetype_research() + model_artifact_archetype_research() + evidence_and_analytical_result_archetype_research()
    operation_candidates = operation_contract_classification_candidates(remaining_batches, symbols)
    catchall_refinements = catchall_refinement_candidates(symbols, research)
    capability_candidates = capability_port_classification_candidates(remaining_batches, symbols)
    policy_lane_refinements = policy_lane_refinement_candidates(remaining_batches, symbols)
    policy_candidates = policy_contract_classification_candidates(remaining_batches, symbols)
    identity_candidates = identity_contract_classification_candidates(remaining_batches, symbols)
    authority_candidates = authority_contract_classification_candidates(remaining_batches, symbols)
    representation_candidates = representation_contract_classification_candidates(remaining_batches, symbols)
    resource_candidates = resource_contract_classification_candidates(remaining_batches, symbols)
    shape_candidates = shape_contract_classification_candidates(remaining_batches, symbols)
    measure_lane_refinements = measure_lane_refinement_candidates(remaining_batches, symbols)
    measure_candidates = measure_contract_classification_candidates(remaining_batches, symbols)
    time_candidates = time_contract_classification_candidates(remaining_batches, symbols)
    failure_candidates = failure_contract_classification_candidates(remaining_batches, symbols)
    model_artifact_candidates = model_artifact_contract_classification_candidates(remaining_batches, symbols)
    evidence_lane_refinements = evidence_lane_refinement_candidates(remaining_batches, symbols)
    evidence_candidates = evidence_contract_classification_candidates(remaining_batches, symbols)
    analytical_result_candidates = analytical_result_classification_candidates(remaining_batches, symbols)
    open_primary_batches = [row for row in remaining_batches if row["research_state"] == "OPEN_PRIMARY_RESEARCH"]
    open_primary_rollup = []
    for archetype in sorted({row["research_archetype"] for row in open_primary_batches}):
        members = [row for row in open_primary_batches if row["research_archetype"] == archetype]
        open_primary_rollup.append({
            "archetype_id": archetype,
            "batch_count": len(members),
            "symbol_packet_count": sum(row["packet_count"] for row in members),
            "represented_occurrence_count": sum(row["represented_occurrence_count"] for row in members),
            "symbol_refs": sorted(ref for row in members for ref in row["symbol_refs"]),
        })
    open_primary_rollup.sort(key=lambda row: (-row["symbol_packet_count"], -row["represented_occurrence_count"], row["archetype_id"]))
    route_counts = collections.Counter(row["research_route"] for row in symbols)
    summary = {
        "program_id": "program.p1-source-authority-and-symbol-adjudication.v1", "edition": 1, "as_of": AS_OF,
        "completion_claim": False, "source_authority_packets": len(sources), "structurally_ready_source_packets": sum(not row["structural_controls_missing"] for row in sources),
        "ratified_source_authorities": 0, "symbol_adjudication_packets": len(symbols), "symbol_work_waves": len(waves),
        "symbol_route_counts": dict(sorted(route_counts.items())), "represented_symbol_occurrences": sum(row["library_count"] for row in symbols),
        "unified_public_symbols": 0, "canonical_exact_gaps_closed": 0,
        "high_fanout_symbols_with_primary_research": len(research),
        "researched_symbol_occurrence_applicability_candidates": len(applicability),
        "ratified_symbol_occurrence_applicability_decisions": 0,
        "remaining_symbol_research_batches": len(remaining_batches),
        "remaining_symbol_archetype_research_programs": len(archetype_programs),
        "archetype_semantic_axis_research_lanes": sum(len(row["semantic_axis_refs"]) for row in archetype_programs),
        "archetype_primary_research_findings": len(archetype_research),
        "operation_contract_classification_candidates": len(operation_candidates),
        "operation_candidate_occurrences": sum(row["represented_occurrence_count"] for row in operation_candidates),
        "catchall_symbol_refinement_candidates": len(catchall_refinements),
        "catchall_candidate_occurrences": sum(row["represented_occurrence_count"] for row in catchall_refinements),
        "remaining_general_catchall_batches": sum(row["research_archetype"] == "GENERAL_SEMANTIC_OWNER_DISCOVERY" for row in remaining_batches),
        "capability_port_classification_candidates": len(capability_candidates),
        "capability_port_candidate_occurrences": sum(row["represented_occurrence_count"] for row in capability_candidates),
        "policy_lane_refinement_candidates": len(policy_lane_refinements),
        "policy_lane_refinement_occurrences": sum(row["represented_occurrence_count"] for row in policy_lane_refinements),
        "policy_contract_classification_candidates": len(policy_candidates),
        "policy_contract_candidate_occurrences": sum(row["represented_occurrence_count"] for row in policy_candidates),
        "identity_contract_classification_candidates": len(identity_candidates),
        "identity_contract_candidate_occurrences": sum(row["represented_occurrence_count"] for row in identity_candidates),
        "authority_contract_classification_candidates": len(authority_candidates),
        "authority_contract_candidate_occurrences": sum(row["represented_occurrence_count"] for row in authority_candidates),
        "representation_contract_classification_candidates": len(representation_candidates),
        "representation_contract_candidate_occurrences": sum(row["represented_occurrence_count"] for row in representation_candidates),
        "resource_contract_classification_candidates": len(resource_candidates),
        "resource_contract_candidate_occurrences": sum(row["represented_occurrence_count"] for row in resource_candidates),
        "shape_contract_classification_candidates": len(shape_candidates),
        "shape_contract_candidate_occurrences": sum(row["represented_occurrence_count"] for row in shape_candidates),
        "measure_lane_refinement_candidates": len(measure_lane_refinements),
        "measure_lane_refinement_occurrences": sum(row["represented_occurrence_count"] for row in measure_lane_refinements),
        "measure_contract_classification_candidates": len(measure_candidates),
        "measure_contract_candidate_occurrences": sum(row["represented_occurrence_count"] for row in measure_candidates),
        "time_contract_classification_candidates": len(time_candidates),
        "time_contract_candidate_occurrences": sum(row["represented_occurrence_count"] for row in time_candidates),
        "failure_contract_classification_candidates": len(failure_candidates),
        "failure_contract_candidate_occurrences": sum(row["represented_occurrence_count"] for row in failure_candidates),
        "model_artifact_contract_classification_candidates": len(model_artifact_candidates),
        "model_artifact_contract_candidate_occurrences": sum(row["represented_occurrence_count"] for row in model_artifact_candidates),
        "evidence_lane_refinement_candidates": len(evidence_lane_refinements),
        "evidence_lane_refinement_occurrences": sum(row["represented_occurrence_count"] for row in evidence_lane_refinements),
        "evidence_contract_classification_candidates": len(evidence_candidates),
        "evidence_contract_candidate_occurrences": sum(row["represented_occurrence_count"] for row in evidence_candidates),
        "analytical_result_classification_candidates": len(analytical_result_candidates),
        "analytical_result_candidate_occurrences": sum(row["represented_occurrence_count"] for row in analytical_result_candidates),
        "archetype_researched_symbol_packets": sum(row["packet_count"] for row in remaining_batches if row["research_state"] == "BOUNDED_PRIMARY_RESEARCH_COMPLETE"),
        "total_symbol_packets_with_bounded_primary_research": len(research) + sum(row["packet_count"] for row in remaining_batches if row["research_state"] == "BOUNDED_PRIMARY_RESEARCH_COMPLETE"),
        "remaining_unresearched_symbol_packets": sum(row["packet_count"] for row in open_primary_batches),
        "remaining_unratified_symbol_packets": sum(row["packet_count"] for row in remaining_batches),
        "residual_batched_unratified_symbol_packets": sum(row["packet_count"] for row in remaining_batches),
        "total_owner_unratified_symbol_packets": len(symbols),
        "total_owner_unratified_symbol_occurrences": sum(row["library_count"] for row in symbols),
        "remaining_open_primary_research_archetypes": len(open_primary_rollup),
        "open_primary_research_archetype_priority": open_primary_rollup,
        "next_primary_research_archetype": open_primary_rollup[0]["archetype_id"] if open_primary_rollup else None,
        "finding": "All upstream corpora are structurally ready, so source authority and high-fanout public-symbol ownership are now the first semantic blockers. Identical placeholder definitions remain insufficient evidence for unification.",
    }
    files = {
        "source-authority-packets.jsonl": "".join(canonical(row) + "\n" for row in sources),
        "symbol-adjudication-packets.jsonl": "".join(canonical(row) + "\n" for row in symbols),
        "symbol-work-waves.jsonl": "".join(canonical(row) + "\n" for row in waves),
        "primary-sources.jsonl": "".join(canonical(row) + "\n" for row in PRIMARY_SOURCES),
        "high-fanout-semantic-research.jsonl": "".join(canonical(row) + "\n" for row in research),
        "symbol-occurrence-applicability.jsonl": "".join(canonical(row) + "\n" for row in applicability),
        "remaining-symbol-research-batches.jsonl": "".join(canonical(row) + "\n" for row in remaining_batches),
        "archetype-research-programs.jsonl": "".join(canonical(row) + "\n" for row in archetype_programs),
        "archetype-semantic-research.jsonl": "".join(canonical(row) + "\n" for row in archetype_research),
        "operation-contract-classification-candidates.jsonl": "".join(canonical(row) + "\n" for row in operation_candidates),
        "catchall-symbol-archetype-refinements.jsonl": "".join(canonical(row) + "\n" for row in catchall_refinements),
        "capability-port-classification-candidates.jsonl": "".join(canonical(row) + "\n" for row in capability_candidates),
        "policy-lane-archetype-refinements.jsonl": "".join(canonical(row) + "\n" for row in policy_lane_refinements),
        "policy-contract-classification-candidates.jsonl": "".join(canonical(row) + "\n" for row in policy_candidates),
        "identity-contract-classification-candidates.jsonl": "".join(canonical(row) + "\n" for row in identity_candidates),
        "authority-contract-classification-candidates.jsonl": "".join(canonical(row) + "\n" for row in authority_candidates),
        "representation-contract-classification-candidates.jsonl": "".join(canonical(row) + "\n" for row in representation_candidates),
        "resource-contract-classification-candidates.jsonl": "".join(canonical(row) + "\n" for row in resource_candidates),
        "shape-contract-classification-candidates.jsonl": "".join(canonical(row) + "\n" for row in shape_candidates),
        "measure-lane-archetype-refinements.jsonl": "".join(canonical(row) + "\n" for row in measure_lane_refinements),
        "measure-contract-classification-candidates.jsonl": "".join(canonical(row) + "\n" for row in measure_candidates),
        "time-contract-classification-candidates.jsonl": "".join(canonical(row) + "\n" for row in time_candidates),
        "failure-contract-classification-candidates.jsonl": "".join(canonical(row) + "\n" for row in failure_candidates),
        "model-artifact-contract-classification-candidates.jsonl": "".join(canonical(row) + "\n" for row in model_artifact_candidates),
        "evidence-lane-archetype-refinements.jsonl": "".join(canonical(row) + "\n" for row in evidence_lane_refinements),
        "evidence-contract-classification-candidates.jsonl": "".join(canonical(row) + "\n" for row in evidence_candidates),
        "analytical-result-classification-candidates.jsonl": "".join(canonical(row) + "\n" for row in analytical_result_candidates),
        "symbol-research-archetype-ontology.json": json.dumps(archetype_ontology(), sort_keys=True, indent=2) + "\n",
        "symbol-adjudication-packet.schema.json": json.dumps(schema(), sort_keys=True, indent=2) + "\n",
        "summary.json": json.dumps(summary, sort_keys=True, indent=2) + "\n",
    }
    manifest = {name: {"bytes": len(text.encode()), "sha256": hashlib.sha256(text.encode()).hexdigest()} for name, text in files.items()}
    files["manifest.json"] = json.dumps({"manifest_id": "manifest.p1-authority-symbols.v1", "as_of": AS_OF, "files": manifest, "completion_claim": False}, sort_keys=True, indent=2) + "\n"
    return files


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--check", action="store_true"); args = parser.parse_args()
    stale = []
    for name, text in outputs().items():
        path = HERE / name
        if args.check:
            if not path.is_file() or path.read_text() != text: stale.append(name)
        else: path.write_text(text)
    if stale:
        print("STALE " + ", ".join(stale)); return 1
    summary = json.loads(outputs()["summary.json"])
    print(f"{'CHECK' if args.check else 'BUILD'} PASS P1: {summary['source_authority_packets']} authority packets, {summary['symbol_adjudication_packets']} symbol packets in {summary['symbol_work_waves']} waves; zero inferred authority or unification")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
