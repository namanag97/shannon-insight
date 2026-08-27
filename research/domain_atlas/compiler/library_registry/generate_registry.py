#!/usr/bin/env python3
"""Deterministically normalize universe library hypotheses into the global registry.

This generator reads sibling universe research but writes only to this directory.  The
source projections are evidence, not canonical schemas.  Output ordering, dates, and
JSON formatting are fixed so identical inputs produce byte-identical registries.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable


HERE = Path(__file__).resolve().parent
ATLAS = HERE.parents[1]
UNIVERSES = ATLAS / "universes"
AS_OF = "2026-08-26"
EDITION = 1


def source(source_id: str, title: str, uri: str, authority: str, topic: str,
           published: str | None = None, source_kind: str = "official_project") -> dict[str, Any]:
    return {
        "record_kind": "evidence_source",
        "source_id": source_id,
        "edition": EDITION,
        "title": title,
        "uri": uri,
        "authority": authority,
        "source_kind": source_kind,
        "topic": topic,
        "published": published,
        "retrieved": AS_OF,
        "claim_scope": "Normative where the authority marks it normative; otherwise authoritative project guidance only.",
    }


# Primary or official material only. Community tools are represented by their owning project
# repositories and are evidence about that tool, never elevated into language law.
SOURCES = [
    source("source.rust.reference", "The Rust Reference", "https://doc.rust-lang.org/reference/", "Rust Project", "language semantics", source_kind="official_specification"),
    source("source.rust.reference.abi", "Rust Reference: Application Binary Interface", "https://doc.rust-lang.org/reference/abi.html", "Rust Project", "ABI", source_kind="official_specification"),
    source("source.rust.reference.extern", "Rust Reference: External Blocks", "https://doc.rust-lang.org/reference/items/external-blocks.html", "Rust Project", "FFI", source_kind="official_specification"),
    source("source.rust.reference.linkage", "Rust Reference: Linkage", "https://doc.rust-lang.org/reference/linkage.html", "Rust Project", "linkage and unwinding", source_kind="official_specification"),
    source("source.rust.reference.layout", "Rust Reference: Type Layout", "https://doc.rust-lang.org/reference/type-layout.html", "Rust Project", "layout", source_kind="official_specification"),
    source("source.rust.reference.behavior", "Rust Reference: Behavior Considered Undefined", "https://doc.rust-lang.org/reference/behavior-considered-undefined.html", "Rust Project", "unsafe invariants", source_kind="official_specification"),
    source("source.rust.reference.panic", "Rust Reference: Panic", "https://doc.rust-lang.org/reference/panic.html", "Rust Project", "panic and FFI", source_kind="official_specification"),
    source("source.rust.nomicon.ffi", "Rustonomicon: FFI", "https://doc.rust-lang.org/nomicon/ffi.html", "Rust Project", "FFI"),
    source("source.rust.nomicon.send-sync", "Rustonomicon: Send and Sync", "https://doc.rust-lang.org/nomicon/send-and-sync.html", "Rust Project", "thread safety"),
    source("source.rust.std.send", "std::marker::Send", "https://doc.rust-lang.org/std/marker/trait.Send.html", "Rust Project", "thread safety"),
    source("source.rust.std.sync", "std::marker::Sync", "https://doc.rust-lang.org/std/marker/trait.Sync.html", "Rust Project", "thread safety"),
    source("source.rust.std.future", "std::future::Future", "https://doc.rust-lang.org/std/future/trait.Future.html", "Rust Project", "async"),
    source("source.rust.api-guidelines", "Rust API Guidelines", "https://rust-lang.github.io/api-guidelines/", "Rust Library Team contributors", "API design"),
    source("source.rust.api-guidelines.checklist", "Rust API Guidelines Checklist", "https://rust-lang.github.io/api-guidelines/checklist.html", "Rust Library Team contributors", "API design"),
    source("source.rust.cargo.reference", "Cargo Reference", "https://doc.rust-lang.org/cargo/reference/", "Rust Project", "package and build"),
    source("source.rust.cargo.manifest", "Cargo Manifest Format", "https://doc.rust-lang.org/cargo/reference/manifest.html", "Rust Project", "package metadata"),
    source("source.rust.cargo.dependencies", "Cargo: Specifying Dependencies", "https://doc.rust-lang.org/cargo/reference/specifying-dependencies.html", "Rust Project", "dependency graph"),
    source("source.rust.cargo.resolver", "Cargo Dependency Resolution", "https://doc.rust-lang.org/cargo/reference/resolver.html", "Rust Project", "dependency graph"),
    source("source.rust.cargo.features", "Cargo Features", "https://doc.rust-lang.org/cargo/reference/features.html", "Rust Project", "feature graph"),
    source("source.rust.cargo.rust-version", "Cargo Rust Version", "https://doc.rust-lang.org/cargo/reference/rust-version.html", "Rust Project", "MSRV"),
    source("source.rust.cargo.semver", "Cargo SemVer Compatibility", "https://doc.rust-lang.org/cargo/reference/semver.html", "Rust Project", "compatibility"),
    source("source.rust.cargo.profiles", "Cargo Profiles", "https://doc.rust-lang.org/cargo/reference/profiles.html", "Rust Project", "build profile"),
    source("source.rust.cargo.build-scripts", "Cargo Build Scripts", "https://doc.rust-lang.org/cargo/reference/build-scripts.html", "Rust Project", "generated and native code"),
    source("source.rust.cargo.source-replacement", "Cargo Source Replacement", "https://doc.rust-lang.org/cargo/reference/source-replacement.html", "Rust Project", "dependency provenance"),
    source("source.rust.cargo.registries", "Cargo Registries", "https://doc.rust-lang.org/cargo/reference/registries.html", "Rust Project", "package distribution"),
    source("source.rust.cargo.publish", "Cargo Publishing", "https://doc.rust-lang.org/cargo/reference/publishing.html", "Rust Project", "release"),
    source("source.rust.cargo.metadata", "cargo metadata", "https://doc.rust-lang.org/cargo/commands/cargo-metadata.html", "Rust Project", "dependency graph"),
    source("source.rust.cargo.package", "cargo package", "https://doc.rust-lang.org/cargo/commands/cargo-package.html", "Rust Project", "packaging"),
    source("source.rust.cargo.lints", "Cargo Lints", "https://doc.rust-lang.org/cargo/reference/lints.html", "Rust Project", "conformance"),
    source("source.rust.rustdoc.tests", "rustdoc: Documentation Tests", "https://doc.rust-lang.org/rustdoc/write-documentation/documentation-tests.html", "Rust Project", "conformance"),
    source("source.rust.rustc.targets", "rustc Target Tier Policy", "https://doc.rust-lang.org/rustc/target-tier-policy.html", "Rust Project", "targets"),
    source("source.rust.edition2024.unsafe-op", "Rust 2024: unsafe_op_in_unsafe_fn", "https://doc.rust-lang.org/edition-guide/rust-2024/unsafe-op-in-unsafe-fn.html", "Rust Project", "unsafe code", "2024"),
    source("source.rust.rfc1105", "RFC 1105: API Evolution", "https://rust-lang.github.io/rfcs/1105-api-evolution.html", "Rust Project", "compatibility", "2015", "official_project_rfc"),
    source("source.rust.rfc3324", "RFC 3324: dyn upcasting", "https://rust-lang.github.io/rfcs/3324-dyn-upcasting.html", "Rust Project", "trait compatibility", "2022", "official_project_rfc"),
    source("source.webassembly.core", "WebAssembly Core Specification", "https://webassembly.github.io/spec/core/", "W3C WebAssembly Community Group", "WASM", source_kind="official_specification"),
    source("source.webassembly.component", "WebAssembly Component Model", "https://github.com/WebAssembly/component-model", "W3C WebAssembly Community Group", "component model", source_kind="official_specification"),
    source("source.webassembly.component.explainer", "Component Model Explainer", "https://github.com/WebAssembly/component-model/blob/main/design/mvp/Explainer.md", "W3C WebAssembly Community Group", "component boundaries", source_kind="official_specification"),
    source("source.webassembly.component.wit", "WebAssembly Interface Types (WIT)", "https://github.com/WebAssembly/component-model/blob/main/design/mvp/WIT.md", "W3C WebAssembly Community Group", "IDL", source_kind="official_specification"),
    source("source.webassembly.component.canonical-abi", "Component Model Canonical ABI", "https://github.com/WebAssembly/component-model/blob/main/design/mvp/CanonicalABI.md", "W3C WebAssembly Community Group", "ABI", source_kind="official_specification"),
    source("source.webassembly.component.concurrency", "Component Model Concurrency Explainer", "https://github.com/WebAssembly/component-model/blob/main/design/mvp/Concurrency.md", "W3C WebAssembly Community Group", "async cancellation concurrency", source_kind="official_specification"),
    source("source.webassembly.component.binary", "Component Model Binary Format", "https://github.com/WebAssembly/component-model/blob/main/design/mvp/Binary.md", "W3C WebAssembly Community Group", "serialization", source_kind="official_specification"),
    source("source.wasi.preview2", "WASI 0.2 (Preview 2)", "https://wasi.dev/interfaces", "WASI Subgroup", "capability interfaces", source_kind="official_specification"),
    source("source.bytecodealliance.wit-bindgen", "wit-bindgen", "https://github.com/bytecodealliance/wit-bindgen", "Bytecode Alliance", "generated bindings"),
    source("source.rust.wasm-bindgen", "wasm-bindgen Guide", "https://wasm-bindgen.github.io/wasm-bindgen/", "Rust and WebAssembly Working Group", "JS/WASM boundary"),
    source("source.semver.2", "Semantic Versioning 2.0.0", "https://semver.org/spec/v2.0.0.html", "Semantic Versioning maintainers", "versioning", "2013", "official_specification"),
    source("source.json-schema.2020-12", "JSON Schema Draft 2020-12", "https://json-schema.org/draft/2020-12", "JSON Schema project", "schema", "2022", "official_specification"),
    source("source.openapi.3.1.1", "OpenAPI Specification 3.1.1", "https://spec.openapis.org/oas/v3.1.1.html", "OpenAPI Initiative", "language-neutral API", "2024", "official_specification"),
    source("source.protobuf.proto3", "Protocol Buffers Language Guide (proto3)", "https://protobuf.dev/programming-guides/proto3/", "Google Protocol Buffers project", "serialization", source_kind="official_specification"),
    source("source.grpc.versioning", "gRPC Versioning Guide", "https://grpc.io/docs/guides/versioning/", "gRPC project", "API evolution"),
    source("source.ietf.rfc2119", "RFC 2119: Key words for requirements", "https://www.rfc-editor.org/rfc/rfc2119", "IETF", "normative language", "1997", "standards_body"),
    source("source.ietf.rfc8174", "RFC 8174: Ambiguity of Uppercase vs Lowercase", "https://www.rfc-editor.org/rfc/rfc8174", "IETF", "normative language", "2017", "standards_body"),
    source("source.ietf.rfc8949", "RFC 8949: CBOR", "https://www.rfc-editor.org/rfc/rfc8949", "IETF", "serialization", "2020", "standards_body"),
    source("source.ietf.rfc9457", "RFC 9457: Problem Details for HTTP APIs", "https://www.rfc-editor.org/rfc/rfc9457", "IETF", "typed errors", "2023", "standards_body"),
    source("source.ietf.rfc9110", "RFC 9110: HTTP Semantics", "https://www.rfc-editor.org/rfc/rfc9110", "IETF", "protocol semantics", "2022", "standards_body"),
    source("source.oci.image-spec", "OCI Image Format Specification", "https://github.com/opencontainers/image-spec", "Open Container Initiative", "artifact format", source_kind="official_specification"),
    source("source.oci.distribution-spec", "OCI Distribution Specification", "https://github.com/opencontainers/distribution-spec", "Open Container Initiative", "artifact distribution", source_kind="official_specification"),
    source("source.spdx.3.0.1", "SPDX Specification 3.0.1", "https://spdx.github.io/spdx-spec/v3.0.1/", "Linux Foundation SPDX", "SBOM and license", "2024", "official_specification"),
    source("source.cyclonedx.1.7", "CycloneDX Specification 1.7", "https://cyclonedx.org/specification/overview/", "OWASP CycloneDX / Ecma International", "SBOM", "2025", "official_specification"),
    source("source.slsa.1.2", "SLSA Specification 1.2", "https://slsa.dev/spec/v1.2/", "OpenSSF SLSA", "provenance", "2025", "official_specification"),
    source("source.in-toto.spec", "in-toto Specification", "https://github.com/in-toto/docs/blob/master/in-toto-spec.md", "in-toto project", "supply-chain attestations", source_kind="official_specification"),
    source("source.tuf.spec", "The Update Framework Specification", "https://theupdateframework.github.io/specification/latest/", "TUF project", "secure distribution", source_kind="official_specification"),
    source("source.sigstore.docs", "Sigstore Documentation", "https://docs.sigstore.dev/", "Sigstore project", "signing and transparency"),
    source("source.osv.schema", "Open Source Vulnerability Schema", "https://ossf.github.io/osv-schema/", "OpenSSF OSV", "advisories", source_kind="official_specification"),
    source("source.rustsec.advisory-db", "RustSec Advisory Database", "https://github.com/RustSec/advisory-db", "RustSec", "Rust advisories"),
    source("source.rustsec.cargo-audit", "cargo-audit", "https://github.com/RustSec/rustsec/tree/main/cargo-audit", "RustSec", "advisory checking"),
    source("source.mozilla.cargo-vet", "cargo-vet", "https://mozilla.github.io/cargo-vet/", "Mozilla", "dependency audits", "2022"),
    source("source.embark.cargo-deny", "cargo-deny", "https://embarkstudios.github.io/cargo-deny/", "Embark Studios", "dependency policy"),
    source("source.cargo-semver-checks", "cargo-semver-checks", "https://github.com/obi1kenobi/cargo-semver-checks", "cargo-semver-checks project", "API compatibility", "2021"),
    source("source.cargo-auditable", "cargo-auditable", "https://github.com/rust-secure-code/cargo-auditable", "Rust Secure Code Working Group contributors", "binary provenance", "2022"),
    source("source.cargo-cyclonedx", "cargo-cyclonedx", "https://github.com/CycloneDX/cyclonedx-rust-cargo", "OWASP CycloneDX", "Rust SBOM", "2022"),
    source("source.reproducible-builds", "Reproducible Builds", "https://reproducible-builds.org/docs/definition/", "Reproducible Builds project", "reproducibility", source_kind="official_project"),
    source("source.reproducible-builds.epoch", "SOURCE_DATE_EPOCH", "https://reproducible-builds.org/docs/source-date-epoch/", "Reproducible Builds project", "reproducibility"),
    source("source.nist.ssdf.1.1", "NIST SP 800-218: Secure Software Development Framework", "https://csrc.nist.gov/pubs/sp/800/218/final", "NIST", "secure development", "2022", "standards_body"),
    source("source.nist.c-scrm", "NIST SP 800-161 Rev. 1: Cybersecurity Supply Chain Risk Management", "https://csrc.nist.gov/pubs/sp/800/161/r1/final", "NIST", "supply-chain risk", "2022", "standards_body"),
    source("source.openssf.scorecard", "OpenSSF Scorecard", "https://github.com/ossf/scorecard", "OpenSSF", "project security signals", "2021"),
    source("source.openssf.s2c2f", "Secure Supply Chain Consumption Framework", "https://github.com/ossf/s2c2f", "OpenSSF", "dependency consumption", "2022"),
    source("source.iso.42010.2022", "ISO/IEC/IEEE 42010:2022 Architecture Description", "https://www.iso.org/standard/74393.html", "ISO/IEC/IEEE", "architecture description", "2022", "standards_body"),
    source("source.parnas.1972", "On the Criteria To Be Used in Decomposing Systems into Modules", "https://doi.org/10.1145/361598.361623", "David L. Parnas / ACM", "information hiding", "1972", "primary_paper"),
    source("source.cockburn.hexagonal", "Hexagonal Architecture", "https://alistair.cockburn.us/hexagonal-architecture", "Alistair Cockburn", "ports and adapters", "2005", "primary_architecture_source"),
    source("source.cockburn.component-strategy", "Component plus Strategy generalizes Ports and Adapters", "https://alistaircockburn.com/Component%20plus%20strategy.pdf", "Alistair Cockburn", "replaceability", "2022", "primary_architecture_source"),
    source("source.c4model.abstractions", "C4 Model: Abstractions", "https://c4model.com/abstractions", "Simon Brown", "architecture scope", source_kind="primary_architecture_source"),
    source("source.cloudevents.1.0", "CloudEvents Specification", "https://github.com/cloudevents/spec/blob/v1.0.2/cloudevents/spec.md", "CNCF CloudEvents", "event DTO", "2022", "official_specification"),
    source("source.opentelemetry.spec", "OpenTelemetry Specification", "https://opentelemetry.io/docs/specs/otel/", "CNCF OpenTelemetry", "telemetry receipts", source_kind="official_specification"),
    source("source.asyncapi.3", "AsyncAPI Specification 3.0", "https://www.asyncapi.com/docs/reference/specification/v3.0.0", "AsyncAPI Initiative", "async API", "2024", "official_specification"),
]


DECISION_SPECS = [
    ("semantic_owner", "Who owns the meaning exposed by this library family?", "SemanticOwnerRef", ["one_context", "shared_contract_with_named_authority", "unresolved_refuse"], "semantic_closure"),
    ("boundary_evidence", "What proves this is a replaceable library boundary?", "BoundaryEvidenceProfile", ["owner_and_independent_substitution", "owner_only_hypothesis", "reject_term_or_bundle"], "semantic_closure"),
    ("effect_boundary", "Where does pure decision logic stop and effect execution begin?", "EffectBoundary", ["pure_no_io", "pure_effect_intents", "effectful_runtime", "ffi_boundary", "generated_boundary"], "logical_planning"),
    ("async_posture", "Is each operation synchronous, asynchronous, or offered in both forms?", "AsyncPosture", ["sync", "async", "dual_explicit"], "logical_planning"),
    ("cancellation", "What cancellation and partial-result law applies?", "CancellationContract", ["not_applicable_bounded", "cooperative_safe_points", "abort_with_cleanup_receipt", "uncancellable_refuse"], "logical_planning"),
    ("thread_safety", "What thread-safety promise is part of the offer?", "ThreadSafety", ["single_thread_only", "send_not_sync", "send_and_sync", "target_specific"], "physical_binding"),
    ("concurrency_order", "Which schedule-dependent outcomes are permitted?", "ConcurrencyOrder", ["deterministic", "equivalent_modulo_order", "nondeterministic_with_receipt", "serial_only"], "logical_planning"),
    ("time_source", "How is time supplied?", "TimeSource", ["explicit_value", "clock_intent", "provider_clock_with_receipt", "forbidden"], "logical_planning"),
    ("randomness_source", "How is randomness supplied and replayed?", "RandomnessSource", ["explicit_seed", "entropy_intent_and_receipt", "forbidden"], "logical_planning"),
    ("state_model", "Where may durable or shared state live?", "StateModel", ["stateless", "caller_owned", "explicit_state_port", "provider_state_with_receipt"], "logical_planning"),
    ("resource_budget", "Which finite resource budget is enforced?", "ResourceBudget", ["caller_budget", "target_offer_budget", "compile_time_bound", "unbounded_refuse"], "physical_binding"),
    ("error_surface", "How are failures, refusals, cancellation and panic separated?", "ErrorSurface", ["typed_total_result", "typed_result_plus_documented_panic", "ffi_status_dto"], "semantic_closure"),
    ("panic_policy", "May a panic or exception cross the public boundary?", "PanicPolicy", ["never", "bug_only_same_runtime", "ffi_abort", "unwind_abi_explicit"], "physical_binding"),
    ("abi_contract", "Which ABI, if any, is stable?", "AbiContract", ["none_source_api_only", "c_abi", "wasm_canonical_abi", "target_specific_versioned"], "physical_binding"),
    ("serialization", "Which serialized DTO contract is stable?", "SerializationContract", ["none_in_process", "json_schema", "protobuf", "cbor_cddl", "wit"], "physical_binding"),
    ("acl_loss", "What loss may an anti-corruption adapter introduce?", "AclLossPolicy", ["lossless_only", "declared_loss_with_authority", "refuse_unknown"], "semantic_closure"),
    ("feature_additivity", "Are features additive and mutually composable?", "FeatureLaw", ["strictly_additive", "declared_conflicts", "no_features"], "physical_binding"),
    ("dependency_policy", "Which dependency classes may enter this boundary?", "DependencyPolicy", ["core_only", "audited_pure", "runtime_optional", "adapter_only"], "physical_binding"),
    ("msrv", "What minimum supported Rust version is promised and verified?", "RustVersion", ["explicit_verified", "explicit_unverified", "not_a_rust_artifact"], "physical_binding"),
    ("target_tier", "Which targets receive which verification level?", "TargetTierMap", ["tier1_ci", "tier2_build", "tier3_best_effort", "language_neutral"], "physical_binding"),
    ("no_std", "Must a Rust implementation support core/alloc without std?", "NoStdPolicy", ["required", "optional_feature", "not_supported", "not_a_rust_artifact"], "physical_binding"),
    ("license", "Which license expression is acceptable?", "SpdxExpression", ["authority_allowlist", "context_specific_review", "unresolved_refuse"], "assurance_insertion"),
    ("advisory", "What advisory state blocks qualification?", "AdvisoryPolicy", ["any_known_exploitable", "severity_threshold", "authority_waiver_only"], "evidence_verification"),
    ("sbom", "Which SBOM formats and lifecycle stage are required?", "SbomProfile", ["spdx_3", "cyclonedx_1_7", "both", "explicit_gap"], "evidence_verification"),
    ("reproducibility", "What reproducibility evidence is required?", "ReproducibilityProfile", ["bit_for_bit_two_builders", "hermetic_provenance", "best_effort_documented"], "evidence_verification"),
    ("unsafe_scope", "Where may unsafe code appear?", "UnsafeScope", ["forbidden", "audited_internal_module", "ffi_shim_only", "target_specific"], "physical_binding"),
    ("generated_code", "How is generated code versioned and reviewed?", "GeneratedCodePolicy", ["checked_in_and_diffed", "reproducible_at_build", "published_artifact_only", "forbidden"], "physical_binding"),
    ("compatibility", "Which compatibility dimensions gate a release?", "CompatibilityMatrix", ["semantic_api_serialization", "semantic_api_abi", "semantic_component_interface", "all_declared"], "evidence_verification"),
    ("deprecation", "What evidence and duration precede removal?", "DeprecationPolicy", ["edition_window", "major_version_window", "migration_complete", "authority_exception"], "product_packaging"),
    ("portable_offer", "When may an offer be described as portable?", "PortableOfferGate", ["two_independent_qualified_implementations", "never_single_implementation"], "evidence_verification"),
    ("conformance_mix", "Which independent oracle classes are mandatory?", "ConformanceProfile", ["law_property_differential", "model_fuzz_fixtures", "all_six"], "evidence_verification"),
    ("replacement", "What demonstrates removal or substitution without semantic drift?", "ReplacementProof", ["consumer_contract_suite", "differential_cutover", "migration_and_rollback", "refuse_unseamed"], "product_packaging"),
]


INNOVATIONS = [
    ("innovation.component-model", 2021, "WebAssembly Component Model", "Typed cross-language components separate interface contracts from core modules and hosts.", ["source.webassembly.component", "source.webassembly.component.explainer"]),
    ("innovation.wit", 2022, "WIT interface language", "A language-neutral interface contract can generate bindings without making generated code the semantic owner.", ["source.webassembly.component.wit"]),
    ("innovation.wasi-preview2", 2023, "WASI Preview 2", "Capability-oriented host interfaces make target requirements explicit.", ["source.wasi.preview2"]),
    ("innovation.canonical-abi", 2023, "Canonical ABI lift/lower", "Canonical lifting and lowering makes memory, encoding, ownership and cleanup boundary decisions inspectable.", ["source.webassembly.component.canonical-abi"]),
    ("innovation.component-async", 2025, "Component Model async ABI work", "Language-neutral tasks, streams, futures, backpressure and cancellation are modeled together.", ["source.webassembly.component.concurrency"]),
    ("innovation.cargo-semver-checks", 2021, "cargo-semver-checks", "Deterministic API-diff lints add evidence to, but do not replace, semantic compatibility review.", ["source.cargo-semver-checks", "source.rust.cargo.semver"]),
    ("innovation.cargo-vet", 2022, "cargo-vet", "Distributed dependency audits allow review evidence to follow exact dependency versions.", ["source.mozilla.cargo-vet"]),
    ("innovation.cargo-auditable", 2022, "cargo-auditable", "Embedding dependency metadata in binaries improves post-build attribution.", ["source.cargo-auditable"]),
    ("innovation.cargo-cyclonedx", 2022, "cargo-cyclonedx", "Cargo graphs can be exported as standardized SBOMs.", ["source.cargo-cyclonedx", "source.cyclonedx.1.7"]),
    ("innovation.rust-version-resolver", 2024, "MSRV-aware Cargo resolution", "Dependency selection can consider rust-version instead of treating MSRV as prose only.", ["source.rust.cargo.rust-version", "source.rust.cargo.resolver"]),
    ("innovation.rust-2024-unsafe", 2024, "Rust 2024 unsafe operation scoping", "Unsafe operations inside unsafe functions require explicit unsafe blocks, improving audit locality.", ["source.rust.edition2024.unsafe-op"]),
    ("innovation.spdx3", 2024, "SPDX 3.0", "A profile-oriented BOM model covers builds, security, data and provenance beyond package lists.", ["source.spdx.3.0.1"]),
    ("innovation.cyclonedx17", 2025, "CycloneDX 1.7", "A lifecycle-aware BOM object model describes components, services, dependencies and attestations.", ["source.cyclonedx.1.7"]),
    ("innovation.slsa10", 2023, "SLSA 1.0", "Approved build provenance levels turned supply-chain assurances into verifiable producer and platform claims.", ["source.slsa.1.2"]),
    ("innovation.slsa12", 2025, "SLSA 1.2 Source Track", "Source history, review and source provenance become separately attestable from builds.", ["source.slsa.1.2"]),
    ("innovation.osv", 2021, "OSV schema", "Version-precise open vulnerability records support deterministic affected-range matching.", ["source.osv.schema"]),
    ("innovation.openssf-scorecard", 2021, "OpenSSF Scorecard", "Automated repository security signals create scoped evidence without claiming semantic conformance.", ["source.openssf.scorecard"]),
    ("innovation.s2c2f", 2022, "Secure Supply Chain Consumption Framework", "Dependency intake, inventory, update and incident processes are treated as a consumption lifecycle.", ["source.openssf.s2c2f"]),
    ("innovation.sigstore-ga", 2022, "Sigstore keyless signing ecosystem", "Identity-bound signatures and transparency logs reduce reliance on long-lived signing keys.", ["source.sigstore.docs"]),
    ("innovation.openapi311", 2024, "OpenAPI 3.1.1", "A language-neutral API description aligned with JSON Schema supports typed transport contracts while preserving semantic separation.", ["source.openapi.3.1.1", "source.json-schema.2020-12"]),
    ("innovation.asyncapi3", 2024, "AsyncAPI 3.0", "Async channel, operation and message contracts can be versioned separately from broker products.", ["source.asyncapi.3"]),
    ("innovation.cloudevents102", 2022, "CloudEvents 1.0.2", "A small event envelope standardizes occurrence metadata without owning domain payload meaning.", ["source.cloudevents.1.0"]),
    ("innovation.otel-stable-signals", 2023, "OpenTelemetry stable telemetry signals", "Portable trace, metric and log structures make runtime receipts less provider-specific.", ["source.opentelemetry.spec"]),
    ("innovation.iso42010-2022", 2022, "ISO/IEC/IEEE 42010:2022", "Architecture descriptions distinguish the entity from views, model kinds and conformance claims.", ["source.iso.42010.2022"]),
    ("innovation.component-strategy", 2022, "Component plus Strategy", "Replaceable components and configurable strategies generalize ports and adapters beyond a fixed application hexagon.", ["source.cockburn.component-strategy"]),
]


REFUSED_GAPS = [
    ("one-library-per-term", "term_granularity", "A vocabulary term alone does not establish semantic ownership, cohesion, independent evolution, or replaceability."),
    ("vendor-sdk-bundle", "vendor_bundle", "A vendor SDK bundles unrelated capabilities and cannot own their semantics."),
    ("product-suite", "product_bundle", "A product or suite packages libraries, services and outcomes; it is not a reusable semantic contribution."),
    ("microservice-as-library", "deployment_collapse", "A deployed service occurrence is not a library family or implementation artifact."),
    ("crate-as-family", "package_collapse", "A Cargo crate is a publication unit and does not by itself prove a semantic boundary."),
    ("generated-sdk-owner", "generated_owner", "Generated code projects a contract; the generator and output do not acquire semantic ownership."),
    ("database-driver-domain", "adapter_collapse", "A database driver is an adapter unless a governed semantic contract and replacement seam are established."),
    ("framework-utilities", "grab_bag", "A utilities/framework bundle lacks one coherent owner and substitution law."),
    ("deployment-chart-library", "deployment_collapse", "A deployment chart is an operational artifact, not a library contribution."),
    ("binary-means-conformant", "evidence_collapse", "Existing code or a passing build is not evidence that semantic laws conform."),
    ("single-implementation-portable", "portability_evidence", "One implementation cannot establish a portable offer; two independent qualified implementations are required."),
    ("ambient-effects-helper", "hidden_effect", "A helper that reads clock, randomness, network, filesystem or process state implicitly violates the effect boundary."),
]


def slug(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9_.-]+", "-", value.strip()).lower()
    value = re.sub(r"[-_.]{2,}", ".", value).strip(".-_")
    return value or "unresolved"


def pascal(value: str) -> str:
    words = re.findall(r"[A-Za-z0-9]+", value)
    return "".join(word[:1].upper() + word[1:] for word in words) or "Unresolved"


def unique_strings(values: Iterable[Any]) -> list[str]:
    return sorted({str(v) for v in values if v is not None and str(v).strip()})


def read_jsonl(path: Path) -> list[tuple[int, dict[str, Any]]]:
    result = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if line.strip():
                value = json.loads(line)
                if isinstance(value, dict):
                    result.append((line_number, value))
    return result


def local_candidate_files() -> list[Path]:
    paths = {path for path in UNIVERSES.rglob("library-*.jsonl") if path.is_file()}
    # Some universes use the equally explicit plural registry name `libraries.jsonl`.
    # Filename convention must not decide whether a governed library contribution exists.
    paths.update(path for path in UNIVERSES.rglob("libraries.jsonl") if path.is_file())
    return sorted(paths, key=lambda p: p.as_posix())


def local_library_outputs() -> list[Path]:
    paths = {path for path in UNIVERSES.rglob("library-*") if path.is_file()}
    paths.update(path for path in UNIVERSES.rglob("libraries.jsonl") if path.is_file())
    return sorted(paths, key=lambda p: p.as_posix())


def source_library_id(raw: dict[str, Any]) -> str:
    value = raw.get("library_id") or raw.get("library_candidate_id") or raw.get("id")
    if not value:
        return "library.unresolved.missing-id"
    value = slug(str(value))
    if value.startswith("library."):
        return value
    if ".library." in value:
        before, after = value.split(".library.", 1)
        return f"library.{before}.{after}"
    return f"library.{value}"


def owner_context(raw: dict[str, Any]) -> str:
    candidates: list[str] = []
    for key in ("semantic_owner_context", "semantic_owner_ref", "owner_context", "owner_context_ref"):
        if raw.get(key):
            candidates.append(str(raw[key]))
    candidates.extend(raw.get("semantic_owner_refs") or [])
    candidates.extend(raw.get("owns_contexts") or [])
    candidates.extend(raw.get("contributes_to_context_refs") or [])
    if candidates:
        return slug(candidates[0])
    # Some source corpora declare a semantic family rather than repeating an
    # owner on every library row.  Preserve that authored boundary by deriving
    # its context namespace from the library's sovereign prefix.
    if raw.get("family"):
        source_id = str(raw.get("library_id") or raw.get("library_candidate_id") or raw.get("id") or "")
        parts = slug(source_id).split(".")
        namespace = parts[1] if len(parts) > 2 and parts[0] == "library" else "registry"
        return f"context.{namespace}.{slug(str(raw['family']))}"
    if raw.get("domain"):
        return f"context.spt.{slug(str(raw['domain']))}"
    return "context.registry.unresolved"


def candidate_kind(raw: dict[str, Any]) -> str:
    given = str(raw.get("library_kind") or raw.get("boundary_kind") or raw.get("effect_class") or raw.get("layer") or "")
    mapping = {
        "pure_semantic": "semantic_pure", "semantic_pure": "semantic_pure",
        "pure_algorithm": "algorithm_pure", "algorithm_pure": "algorithm_pure",
        "policy_pure": "policy_pure", "test_oracle": "test_oracle",
        "state_pure": "policy_pure", "state_reducer_pure": "policy_pure",
        "state_or_policy_evaluator_pure": "policy_pure",
        "policy_compiler_pure": "policy_pure", "policy_evaluator_pure": "policy_pure",
        "semantic_compiler_pure": "semantic_pure", "evidence_constructor_pure": "semantic_pure",
        "runtime_mechanism": "runtime_mechanism", "provider_adapter": "provider_adapter",
        "target_backend": "target_backend", "generated_support": "generated_support",
        "effectful": "runtime_mechanism", "runtime": "runtime_mechanism", "pure": "semantic_pure",
        "pure_kernel_with_explicit_effect_ports": "semantic_pure",
        "pure_semantic_kernel": "semantic_pure", "pure_algorithm_kernel": "algorithm_pure",
        "runtime_protocol": "runtime_mechanism", "runtime_effect": "runtime_mechanism",
        "stateful_semantic_library": "runtime_mechanism", "effectful_bridge": "runtime_mechanism",
        "effectful_controller": "runtime_mechanism", "effect_port": "effect_port_contract",
        "effect_port_contract": "effect_port_contract", "core_adapter": "effect_port_contract",
        "provider_port": "effect_port_contract",
        "protocol_adapter": "provider_adapter", "engine_adapter": "provider_adapter",
        "effectful_evidence_adapter": "provider_adapter", "test_harness": "test_oracle",
        "protocol_codec": "algorithm_pure",
    }
    return mapping.get(given, "candidate_unclassified")


def candidate_status(raw: dict[str, Any]) -> str:
    status = str(raw.get("status") or "hypothesis")
    if status in {"qualified", "implemented"}:
        # Local claim remains unqualified here until independent registry evidence is bound.
        return "observed_claim_unverified"
    if status == "specified":
        return "specified_unimplemented"
    return "candidate_unadjudicated"


def exact_type_tokens(value: Any) -> list[str]:
    text = str(value).strip()
    if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_:.-]*", text):
        return [text]
    if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_:.-]*<[A-Za-z0-9_:., <>&?'\[\]-]+>", text):
        return [token for token in re.findall(r"[A-Za-z_][A-Za-z0-9_:.-]*", text) if token not in {"Result", "Option", "Vec", "Box", "Arc"}]
    return []


def extract_types(raw: dict[str, Any], stem: str) -> list[dict[str, str]]:
    names: list[str] = []
    for key in ("public_types", "input_types", "output_types", "public_contracts", "input_contracts", "output_contracts"):
        for value in raw.get(key) or []:
            names.extend(exact_type_tokens(value))
    origin = "source_projection"
    if not names:
        names = [f"{stem}Input", f"{stem}Outcome", f"{stem}Error"]
        origin = "registry_placeholder_pending_owner"
    return [{"type_id": f"type.{slug(name)}", "name": name, "role": "public_contract", "origin": origin} for name in unique_strings(names)]


def extract_traits(raw: dict[str, Any], stem: str) -> list[dict[str, str]]:
    traits = list(raw.get("public_traits") or [])
    origin = "source_projection"
    if not traits:
        traits = [f"{stem}Contract"]
        origin = "registry_placeholder_pending_owner"
    return [{"trait_id": f"trait.{slug(name)}", "name": str(name), "object_safety": "must_be_declared_by_implementation", "origin": origin} for name in unique_strings(traits)]


def extract_operations(raw: dict[str, Any], library_id: str, stem: str, types: list[dict[str, str]], boundary: str) -> list[dict[str, Any]]:
    detailed = raw.get("operations") or []
    if detailed:
        result = []
        for operation in detailed:
            if not isinstance(operation, dict) or not operation.get("operation_ref"):
                continue
            operation_ref = str(operation["operation_ref"])
            purity = str(operation.get("purity") or ("pure" if boundary == "pure_no_io" else "effectful_explicit"))
            result.append({
                "operation_ref": slug(operation_ref) if operation_ref.startswith("operation.") else f"operation.{slug(operation_ref)}",
                "name": str(operation.get("name") or operation_ref.split(".")[-1]),
                "input_types": unique_strings(operation.get("input_types") or []),
                "output_type": str(operation.get("output_type") or f"Result<{stem}Outcome,{stem}Error>"),
                "purity": purity,
                "effect_intent_type": operation.get("effect_intent_type"),
                "receipt_type": operation.get("receipt_type"),
                "refusal_types": unique_strings(operation.get("refusal_types") or raw.get("error_contracts") or [f"{stem}Refusal", "UnsupportedCapability"]),
                "origin": "source_projection",
            })
        if result:
            return sorted(result, key=lambda row: row["operation_ref"])
    refs: list[str] = []
    refs.extend(raw.get("operation_refs") or [])
    refs.extend(raw.get("pure_operation_refs") or [])
    refs.extend(raw.get("effect_operation_refs") or [])
    if not refs:
        refs.extend(str(ref).replace("capability.", "operation.", 1) for ref in (raw.get("capability_refs") or []))
    origin = "source_projection"
    if not refs:
        refs = [f"operation.{library_id.removeprefix('library.')}.apply"]
        origin = "registry_placeholder_pending_owner"
    input_names = [str(x) for x in (raw.get("input_types") or raw.get("input_contracts") or []) if exact_type_tokens(x)]
    output_names = [str(x) for x in (raw.get("output_types") or raw.get("output_contracts") or []) if exact_type_tokens(x)]
    signature_from_source = bool(input_names and output_names)
    if not input_names:
        input_names = [types[0]["name"]]
    if not output_names:
        output_names = [f"Result<{stem}Outcome,{stem}Error>"]
    operation_origin = origin if signature_from_source else "registry_placeholder_pending_owner"
    effectful = boundary in {"effectful_runtime", "ffi_boundary", "generated_boundary"}
    return [{
        "operation_ref": slug(ref) if str(ref).startswith("operation.") else f"operation.{slug(ref)}",
        "name": str(ref).split(".")[-1],
        "input_types": input_names,
        "output_type": output_names[0],
        "purity": "unresolved_refuse" if boundary == "unresolved_refuse" else ("effectful_explicit" if effectful else "pure"),
        "effect_intent_type": f"{stem}EffectIntent" if effectful else None,
        "receipt_type": f"{stem}EffectReceipt" if effectful else None,
        "refusal_types": unique_strings(raw.get("error_contracts") or [f"{stem}Refusal", "UnsupportedCapability", "ResourceExhausted", "Cancelled"]),
        "origin": operation_origin,
    } for ref in unique_strings(refs)]


def normalize_candidate(path: Path, line_number: int, raw: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    library_id = source_library_id(raw)
    owner = owner_context(raw)
    name = str(raw.get("name") or library_id.split(".")[-1].replace("-", " ").replace("_", " ").title())
    stem = pascal(name)
    kind = candidate_kind(raw)
    effect_given = str(raw.get("effect_boundary") or raw.get("effect_class") or raw.get("boundary_kind") or "")
    effect_lower = effect_given.lower().replace("-", " ")
    if effect_given in {"pure_no_io", "pure_effect_intents", "effectful_runtime", "ffi_boundary", "generated_boundary"}:
        effect_boundary = effect_given
    elif "no i/o" in effect_lower or "no io" in effect_lower:
        effect_boundary = "pure_no_io"
    elif effect_given == "effectful" or "i/o" in effect_lower or "network" in effect_lower:
        effect_boundary = "effectful_runtime"
    elif str(raw.get("library_kind")) == "effect_port":
        effect_boundary = "pure_effect_intents"
    elif kind in {"runtime_mechanism", "provider_adapter", "target_backend"}:
        effect_boundary = "effectful_runtime"
    elif kind == "candidate_unclassified":
        effect_boundary = "unresolved_refuse"
    else:
        effect_boundary = "pure_effect_intents" if raw.get("port_candidates") else "pure_no_io"
    types = extract_types(raw, stem)
    traits = extract_traits(raw, stem)
    operations = extract_operations(raw, library_id, stem, types, effect_boundary)
    decision_refs = unique_strings(raw.get("decision_refs") or [])
    # Universe registries retain their own local evidence identifier conventions
    # (for example ``A-SRC-113``).  The sovereign registry uses one lowercase,
    # dotted identifier grammar, so local references must cross the ACL through
    # the same deterministic normalizer used for every other registry identity.
    evidence_refs = unique_strings(
        slug(value)
        for value in (raw.get("evidence_refs") or raw.get("source_refs") or raw.get("evidence_source_ids") or [])
    )
    evidence_refs.extend(["source.parnas.1972", "source.cockburn.hexagonal", "source.rust.api-guidelines.checklist"])
    raw_dependencies = raw.get("dependencies") or raw.get("allowed_dependencies") or []
    dependency_refs = []
    unresolved_dependencies = []
    for dep in raw_dependencies:
        value = str(dep.get("ref")) if isinstance(dep, dict) else str(dep)
        if value.startswith("library.") or ".library." in value:
            dependency_refs.append(source_library_id({"library_id": value}))
        else:
            dependency_refs.append(f"dependency.unresolved.{slug(value)}")
            unresolved_dependencies.append(value)
    responsibilities = unique_strings(raw.get("responsibilities") or ([raw.get("responsibility")] if raw.get("responsibility") else []) or ([raw.get("candidate_responsibility")] if raw.get("candidate_responsibility") else []) or ([raw.get("owns")] if raw.get("owns") else []))
    if not responsibilities:
        responsibilities = [f"Own the coherent {name} contract for {owner}.", "Define typed operations, laws and refusals independently of any provider."]
    exclusions = unique_strings(raw.get("explicit_exclusions") or raw.get("forbidden_responsibilities") or raw.get("forbidden_ownership") or raw.get("must_not_own") or [])
    if not exclusions:
        exclusions = ["product outcome promises", "provider selection", "ambient I/O", "deployment ownership"]
    local_gaps = unique_strings(raw.get("gaps") or ([raw.get("candidate_note")] if raw.get("candidate_note") else []))
    gaps = [{
        "gap_id": f"gap.{library_id.removeprefix('library.')}.implementation-evidence.v1",
        "gap_kind": "independent_implementation_evidence",
        "introduced_in": "registry-edition-1",
        "description": "No two independent law-conformant implementation artifacts are bound in this registry.",
        "blocking": True,
        "resolution_condition": "Bind at least two independently maintained implementations with passing scoped conformance receipts.",
    }]
    placeholder_dimensions = []
    if any(item["origin"] != "source_projection" for item in types):
        placeholder_dimensions.append("types")
    if any(item["origin"] != "source_projection" for item in traits):
        placeholder_dimensions.append("traits")
    if any(item["origin"] != "source_projection" for item in operations):
        placeholder_dimensions.append("operations")
    if placeholder_dimensions:
        gaps.append({
            "gap_id": f"gap.{library_id.removeprefix('library.')}.exact-api.v1",
            "gap_kind": "exact_api_contract_missing",
            "introduced_in": "registry-edition-1",
            "description": f"The source projection does not name exact {', '.join(placeholder_dimensions)}; registry placeholders are not adjudicated API commitments.",
            "blocking": True,
            "resolution_condition": "The semantic owner publishes exact versioned type, trait and operation signatures with refusal and effect contracts.",
        })
    declared_owner_candidates = unique_strings(
        list(raw.get("semantic_owner_refs") or [])
        + list(raw.get("owns_contexts") or [])
        + ([raw.get("semantic_owner_ref")] if raw.get("semantic_owner_ref") else [])
        + ([raw.get("semantic_owner_context")] if raw.get("semantic_owner_context") else [])
        + ([raw.get("owner_context")] if raw.get("owner_context") else [])
        + ([raw.get("owner_context_ref")] if raw.get("owner_context_ref") else [])
    )
    if len(declared_owner_candidates) > 1:
        gaps.append({
            "gap_id": f"gap.{library_id.removeprefix('library.')}.owner-cardinality.v1",
            "gap_kind": "ambiguous_semantic_owner",
            "introduced_in": "source-projection",
            "description": f"The source projects multiple owning contexts ({', '.join(declared_owner_candidates)}); the first is used only as a normalization anchor.",
            "blocking": True,
            "resolution_condition": "Adjudicate one meaning owner or create an explicit shared-contract authority before qualification.",
        })
    if not declared_owner_candidates and owner == "context.registry.unresolved":
        gaps.append({
            "gap_id": f"gap.{library_id.removeprefix('library.')}.semantic-owner.v1",
            "gap_kind": "semantic_owner_missing",
            "introduced_in": "source-projection",
            "description": "The source projection names responsibilities but no bounded context or shared-contract authority that owns their meaning; the boundary is refused.",
            "blocking": True,
            "resolution_condition": "Name and adjudicate one semantic owner or shared-contract authority, then repeat cohesion and replaceability review.",
        })
    if unresolved_dependencies:
        gaps.append({
            "gap_id": f"gap.{library_id.removeprefix('library.')}.dependency-identity.v1",
            "gap_kind": "dependency_identity_unresolved",
            "introduced_in": "source-projection",
            "description": f"Free-form dependency labels are not bindable identities: {', '.join(sorted(unresolved_dependencies))}.",
            "blocking": True,
            "resolution_condition": "Resolve each label to an editioned library, capability, runtime, provider, build or test dependency identity and prove cycle policy.",
        })
    if kind == "candidate_unclassified" or effect_boundary == "unresolved_refuse":
        gaps.append({
            "gap_id": f"gap.{library_id.removeprefix('library.')}.class-effect.v1",
            "gap_kind": "library_class_or_effect_boundary_missing",
            "introduced_in": "source-projection",
            "description": "The source projection does not establish a canonical library class and pure/effect boundary; execution is refused.",
            "blocking": True,
            "resolution_condition": "The semantic owner classifies the contribution and publishes explicit effect intents, receipts, ambient-effect prohibitions and conformance evidence.",
        })
    for index, text in enumerate(local_gaps, 1):
        gaps.append({
            "gap_id": f"gap.{library_id.removeprefix('library.')}.source-{index}.v1",
            "gap_kind": "source_declared_gap",
            "introduced_in": "source-projection",
            "description": text,
            "blocking": True,
            "resolution_condition": "The semantic owner adjudicates the source gap and binds versioned evidence.",
        })
    source_rel = path.relative_to(ATLAS.parent.parent).as_posix()
    scope = {
        "responsibilities": responsibilities,
        "exclusions": exclusions,
        "boundary_rationale": "Candidate boundary retained only because the source names an owner and a provider-independent contract; final cohesion and cycle review remain open.",
        "refusal_rule": "Reject a split derived only from vocabulary count, package layout, vendor identity, deployment shape, or product packaging.",
    }
    boundary_adjudication = raw.get("boundary_adjudication")
    if isinstance(boundary_adjudication, dict):
        scope["boundary_adjudication"] = {
            "decision_id": str(boundary_adjudication.get("decision_id", "")),
            "disposition": str(boundary_adjudication.get("disposition", "")),
            "subject_refs": unique_strings(boundary_adjudication.get("subject_refs") or []),
            "rationale": str(boundary_adjudication.get("rationale", "")),
            "no_compatibility_alias": bool(boundary_adjudication.get("no_compatibility_alias", False)),
        }
    contribution = {
        "record_kind": "library_contribution",
        "library_id": library_id,
        "edition": EDITION,
        "name": name,
        "status": "rejected_unresolved_owner" if owner == "context.registry.unresolved" else candidate_status(raw),
        "library_class": kind,
        "family_ref": f"family.{owner}",
        "semantic_owners": [{"context_ref": owner, "role": "meaning_owner", "authority_refs": [f"authority.{owner}"]}],
        "context_refs": unique_strings([owner] + list(raw.get("owns_contexts") or []) + list(raw.get("contributes_to_context_refs") or [])),
        "scope": scope,
        "api_contract": {"types": types, "traits": traits, "operations": operations},
        "effects": {
            "boundary": effect_boundary,
            "intents": ([{"type": f"{stem}EffectIntent", "required_fields": ["operation_ref", "parameters", "budget", "idempotency_key"]}] if effect_boundary in {"pure_effect_intents", "effectful_runtime", "ffi_boundary", "generated_boundary"} else []),
            "receipts": ([{"type": f"{stem}EffectReceipt", "required_fields": ["intent_digest", "outcome", "resource_usage", "evidence_refs"]}] if effect_boundary in {"effectful_runtime", "ffi_boundary", "generated_boundary"} else []),
            "ambient_effects_forbidden": ["clock", "randomness", "filesystem", "network", "environment", "process", "global mutable state"],
        },
        "typed_inputs": {
            "decision_refs": decision_refs,
            "configuration_types": unique_strings(raw.get("configuration_contracts") or [f"{stem}Config"]),
            "default_law": "No semantic default is inferred from provider, target, feature, environment or product name.",
        },
        "behavior": {
            "laws": unique_strings(raw.get("laws") or ["provider identity does not change meaning", "unsupported semantics are refused", "declared information loss is monotone and authorized"]),
            "invariants": ["illegal states are rejected before effects", "receipts bind the exact intent and configuration", "evidence claims remain scoped"],
            "refusals": unique_strings(raw.get("error_contracts") or [f"{stem}Refusal", "UnsupportedCapability", "InvalidConfiguration"]),
            "refusal_precedence": unique_strings(raw.get("refusal_precedence") or [
                "identity edition and authority failures precede semantic evaluation",
                "invalid configuration precedes resource execution",
                "resource exhaustion refuses rather than weakening the requested guarantee",
            ]),
            "errors": ["ResourceExhausted", "Cancelled", "ProviderFailure"],
        },
        "execution": {
            "mode": "unresolved_refuse" if effect_boundary == "unresolved_refuse" else ("mixed_explicit" if effect_boundary != "pure_no_io" else "sync"),
            "cancellation": unique_strings(raw.get("cancellation") or ["bounded pure operations declare not_applicable; long work accepts cooperative cancellation"]),
            "concurrency": unique_strings(raw.get("concurrency") or ["ordering and parallelism are typed offer properties"]),
            "thread_safety": "implementation_offer_must_declare_send_sync_or_language_equivalent",
            "determinism": "semantic result deterministic unless an explicit decision and receipt declare permitted nondeterminism",
        },
        "bounds": {
            "time": "finite deadline or operation-specific complexity bound; otherwise typed refusal",
            "state": "caller-owned or explicit state-port capacity; no hidden durable state",
            "resources": unique_strings(raw.get("resource_contracts") or ["finite CPU/work", "finite memory", "finite I/O and network", "bounded output", "budget refusal"]),
        },
        "boundaries": {
            "abi": "No stable Rust ABI is implied; C ABI or WebAssembly Canonical ABI requires a separate versioned adapter contract.",
            "serialization": "In-memory semantic types are not wire DTOs; each codec/schema is editioned independently.",
            "dtos": [f"{stem}RequestDto", f"{stem}OutcomeDto", f"{stem}ErrorDto"],
            "anti_corruption": "Foreign DTOs cross a named ACL that declares mapping loss, validation, error translation and version compatibility.",
        },
        "feature_dependency_graph": {
            "features": [{"feature_id": "core", "default": True, "additive": True}, {"feature_id": "std", "default": False, "additive": True}],
            "dependency_refs": unique_strings(dependency_refs),
            "feature_laws": ["features do not select domain semantics", "optional dependencies are activated only by additive features", "conflicting features are refused"],
        },
        "platform": {
            "msrv": {"value": None, "status": "implementation_artifact_not_bound"},
            "rust_editions": [],
            "targets": unique_strings(raw.get("targets") or ["language-neutral-contract"]),
            "no_std": "per_implementation_offer",
            "provider_requirements": ["bind an exact capability offer with current evidence"],
            "target_requirements": ["declare ABI, endianness, pointer width, atomic/thread, unwind and resource support where applicable"],
        },
        "supply_chain": {
            "license_expression": None,
            "advisory_policy": "OSV/RustSec or ecosystem-equivalent scan is required for each released artifact and dependency closure.",
            "sbom": "SPDX 3.0.1 or CycloneDX 1.7 bound to artifact digest",
            "reproducibility": "build recipe, locked inputs, toolchain and environment are digest-bound; two-builder reproduction is an evidence tier",
            "provenance": "SLSA provenance or equivalent attestation is required for qualified builds",
        },
        "code_risk": {
            "unsafe": unique_strings(raw.get("unsafe_ffi_generated_policy") or ["unsafe forbidden in semantic core unless separately audited"]),
            "ffi": "isolated in adapter; validate layout, ownership, lengths, alignment, panic/unwind and callback lifetime",
            "generated": "generator version, inputs and output digest recorded; generated code is never semantic authority",
        },
        "evolution": {
            "compatibility_dimensions": ["semantic_edition", "source_api", "behavioral", "serialization", "ABI", "MSRV", "target", "feature_graph"],
            "compatibility": unique_strings(raw.get("compatibility") or ["each dimension is evaluated independently"]),
            "migration": "publish typed adapters, loss declaration, fixtures, rollback and evidence invalidation triggers",
            "deprecation": "announce replacement and last-supported editions; removal requires authority and migration evidence",
        },
        "replacement": {
            "seams": unique_strings(raw.get("removal_seams") or ["capability requirement/offer port", "versioned DTO/ACL", "shared conformance suite"]),
            "substitution_law": "A substitute passes the same scoped semantic, failure, resource, effect and compatibility oracles without consumer knowledge of provider identity.",
        },
        "capabilities": {
            "required": [f"requirement.{library_id.removeprefix('library.')}.implementation"],
            "offered": [f"capability.{library_id.removeprefix('library.')}.contract"],
        },
        "conformance": {
            "oracles": unique_strings(raw.get("oracles") or ["law", "model", "property", "differential", "fuzz", "fixture"]),
            "fixtures": ["canonical positive cases", "negative twins", "edition migration corpus", "malformed and boundary corpus"],
            "fuzz": ["public parser/decoder/API boundary", "state machine and cancellation interleavings"],
            "model_tests": ["reference state machine or executable algebra"],
            "property_tests": ["laws and invariants over generated valid and invalid inputs"],
            "differential_tests": ["compare independent implementations under identical typed decisions and budgets"],
            "qualified_independent_implementation_count": 0,
            "portable_offer_gate": "requires_at_least_two_independent_qualified_implementations",
            "portable_offer": False,
        },
        "evidence_refs": unique_strings(evidence_refs),
        "gaps": gaps,
        "source_projection": {"path": source_rel, "line": line_number, "source_library_id": raw.get("library_id") or raw.get("library_candidate_id") or raw.get("id"), "source_status": raw.get("status"), "source_schema_is_canonical": False},
    }
    crosswalk = {
        "record_kind": "local_crosswalk",
        "crosswalk_id": f"crosswalk.{slug(path.parent.name)}.{slug(path.stem)}.{line_number:04d}",
        "edition": EDITION,
        "source_locator": f"{source_rel}#L{line_number}",
        "source_candidate_id": raw.get("library_id") or raw.get("library_candidate_id") or raw.get("id"),
        "normalized_library_ref": library_id,
        "mapping_status": "normalized_without_adjudication",
        "preserved_claims": sorted(raw.keys()),
        "normalization_notes": ["source shape retained as provenance", "missing contract dimensions become explicit registry gaps", "source status is not promoted to conformance status"],
    }
    return contribution, crosswalk


def decision_records() -> list[dict[str, Any]]:
    return [{
        "record_kind": "registry_decision",
        "decision_id": f"decision.library-registry.{key}",
        "edition": EDITION,
        "status": "declared",
        "owner_context_ref": "context.library-registry.governance",
        "question": question,
        "value_type": value_type,
        "allowed_values": values,
        "binding_phase": phase,
        "authority_ref": "authority.library-registry.semantic-governance",
        "default_law": "forbidden",
        "consequences": ["value is digest-bound in the offer or build", "a change invalidates affected evidence and bindings"],
        "evidence_refs": ["source.rust.api-guidelines", "source.iso.42010.2022"],
    } for key, question, value_type, values, phase in DECISION_SPECS]


def innovation_records() -> list[dict[str, Any]]:
    return [{
        "record_kind": "innovation",
        "innovation_id": innovation_id,
        "edition": EDITION,
        "year": year,
        "name": name,
        "non_llm": True,
        "registry_consequence": consequence,
        "evidence_refs": evidence,
        "adoption_status": "researched_not_mandated",
    } for innovation_id, year, name, consequence, evidence in INNOVATIONS]


def context_records(contributions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[str]] = defaultdict(list)
    for item in contributions:
        for context_ref in item["context_refs"]:
            grouped[context_ref].append(item["library_id"])
    return [{
        "record_kind": "library_design_context",
        "context_id": context_ref,
        "edition": EDITION,
        "status": "gap_anchor_no_owner" if context_ref == "context.registry.unresolved" else "source_observed_unadjudicated",
        "semantic_owner_ref": f"authority.{context_ref}",
        "library_refs": sorted(set(library_refs)),
        "boundary_law": "A library boundary is admitted only for coherent owned semantics and an independently substitutable contract; terms and product bundles are refused.",
        "evidence_refs": ["source.parnas.1972", "source.cockburn.hexagonal", "source.iso.42010.2022"],
    } for context_ref, library_refs in sorted(grouped.items())]


def family_records(contributions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in contributions:
        grouped[item["family_ref"]].append(item)
    return [{
        "record_kind": "library_family",
        "family_id": family_ref,
        "edition": EDITION,
        "status": "rejected_unresolved_owner" if family_ref == "family.context.registry.unresolved" else "candidate_unadjudicated",
        "semantic_owner_refs": sorted({x["semantic_owners"][0]["context_ref"] for x in members}),
        "contribution_refs": sorted(x["library_id"] for x in members),
        "cohesion_law": "Members share a semantic owner and compatibility vocabulary but remain separate contributions only where responsibilities and substitution seams differ.",
        "not_an_artifact": ["implementation", "crate_or_package", "build", "deployed_service", "product"],
        "evidence_refs": ["source.parnas.1972", "source.cockburn.component-strategy"],
    } for family_ref, members in sorted(grouped.items())]


def link_records(contributions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    by_context: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in contributions:
        library_id = item["library_id"]
        for context_ref in item["context_refs"]:
            records.append({
                "record_kind": "context_to_library",
                "link_id": f"link.context-library.{slug(context_ref)}.{slug(library_id)}",
                "edition": EDITION,
                "context_ref": context_ref,
                "library_ref": library_id,
                "relationship": "semantic_owner" if context_ref == item["semantic_owners"][0]["context_ref"] else "contributor",
                "status": "candidate",
                "evidence_refs": item["evidence_refs"],
            })
            by_context[context_ref].append(item)
        for operation in item["api_contract"]["operations"]:
            records.append({
                "record_kind": "operation_to_library",
                "link_id": f"link.operation-library.{slug(operation['operation_ref'])}.{slug(library_id)}",
                "edition": EDITION,
                "operation_ref": operation["operation_ref"],
                "library_ref": library_id,
                "role": "defines" if item["library_class"] in {"semantic_pure", "policy_pure"} else "implements_candidate",
                "status": "candidate",
                "evidence_refs": item["evidence_refs"],
            })
        if item["library_class"] in {"algorithm_pure", "runtime_mechanism", "target_backend", "provider_adapter", "candidate_unclassified"}:
            kernel_ref = f"kernel.{library_id.removeprefix('library.')}"
            records.append({
                "record_kind": "kernel_to_library",
                "link_id": f"link.kernel-library.{slug(kernel_ref)}.{slug(library_id)}",
                "edition": EDITION,
                "kernel_ref": kernel_ref,
                "library_ref": library_id,
                "role": "candidate_implementation_boundary",
                "status": "gap_unqualified",
                "evidence_refs": item["evidence_refs"],
            })
    # A dependency edge is asserted only within one owner context, from non-semantic
    # contributions to a semantic contract candidate. This is an architectural candidate,
    # not an implementation dependency claim.
    for context_ref, items in sorted(by_context.items()):
        semantic = sorted((x for x in items if x["library_class"] in {"semantic_pure", "policy_pure"}), key=lambda x: x["library_id"])
        if not semantic:
            continue
        anchor = semantic[0]
        for item in sorted(items, key=lambda x: x["library_id"]):
            if item["library_id"] == anchor["library_id"]:
                continue
            records.append({
                "record_kind": "dependency_edge",
                "edge_id": f"dependency.{slug(context_ref)}.{slug(item['library_id'])}.{slug(anchor['library_id'])}",
                "edition": EDITION,
                "from_ref": item["library_id"],
                "to_ref": anchor["library_id"],
                "dependency_kind": "semantic_contract_candidate",
                "optional": False,
                "feature_ref": None,
                "purpose": f"Reuse the owner-context contract for {context_ref} without duplicating meaning.",
                "cycle_policy": "semantic layers must be acyclic; cycle is a blocking review issue",
                "removal_seam": "replace through the same context-owned contract and conformance suite",
                "status": "candidate",
            })
    return records


def capability_records(contributions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    records = []
    for item in contributions:
        suffix = item["library_id"].removeprefix("library.")
        requirement_id = f"requirement.{suffix}.implementation"
        offer_id = f"offer.{suffix}.portable"
        records.append({
            "record_kind": "capability_requirement",
            "requirement_id": requirement_id,
            "edition": EDITION,
            "status": "blocked_missing_owner" if item["status"] == "rejected_unresolved_owner" else "declared",
            "subject_ref": item["library_id"],
            "capability_kind": "library_implementation",
            "required_contract_refs": [f"capability.{suffix}.contract"],
            "required_operation_refs": [x["operation_ref"] for x in item["api_contract"]["operations"]],
            "required_guarantees": item["behavior"]["laws"] + [item["replacement"]["substitution_law"]],
            "provider_requirements": item["platform"]["provider_requirements"],
            "target_requirements": item["platform"]["target_requirements"],
            "evidence_gates": ["law, model, property, fuzz and differential receipts are scoped", "license/advisory/SBOM/provenance policy passes", "resource, cancellation and target claims are tested"],
            "fallback_law": "refuse",
        })
        records.append({
            "record_kind": "capability_offer",
            "offer_id": offer_id,
            "edition": EDITION,
            "status": "withheld_unresolved_owner" if item["status"] == "rejected_unresolved_owner" else "withheld_insufficient_independent_implementations",
            "subject_ref": item["library_id"],
            "capability_kind": "portable_library_contract",
            "offered_contract_refs": [f"capability.{suffix}.contract"],
            "implementation_refs": [],
            "independence_criteria": ["different controlling maintainer or organization", "no shared implementation source", "independent build and conformance evidence"],
            "minimum_independent_qualified_implementations": 2,
            "observed_independent_qualified_implementations": 0,
            "portable": False,
            "evidence_refs": item["evidence_refs"],
            "gaps": [item["gaps"][0]["gap_id"]],
        })
    return records


def gap_records() -> list[dict[str, Any]]:
    return [{
        "record_kind": "typed_gap",
        "gap_id": f"gap.library-registry.refused.{key}.v1",
        "edition": EDITION,
        "status": "open_refusal",
        "subject_ref": f"rejected-boundary.{key}",
        "gap_kind": kind,
        "blocking": True,
        "description": description,
        "versioned_from": "registry-edition-1",
        "resolution_condition": "Provide a named semantic owner, coherent responsibilities, independent replacement seam, conformance laws and evidence; otherwise retain the refusal.",
        "prohibited_fallbacks": ["one library per term", "package/crate name dispatch", "vendor or product identity", "existing code presence"],
        "evidence_refs": ["source.parnas.1972", "source.cockburn.hexagonal", "source.iso.42010.2022"],
    } for key, kind, description in REFUSED_GAPS]


def review_records(contributions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in contributions:
        grouped[item["semantic_owners"][0]["context_ref"]].append(item)
    reviews = []
    for context_ref, items in sorted(grouped.items()):
        if len(items) < 2:
            continue
        type_to_libs: dict[str, set[str]] = defaultdict(set)
        for item in items:
            for public_type in item["api_contract"]["types"]:
                type_to_libs[public_type["name"].lower()].add(item["library_id"])
        overlaps = sorted((name, refs) for name, refs in type_to_libs.items() if len(refs) > 1)
        candidate_refs = sorted(x["library_id"] for x in items)
        matching_adjudications = []
        for item in items:
            adjudication = item.get("scope", {}).get("boundary_adjudication")
            if (
                isinstance(adjudication, dict)
                and adjudication.get("disposition") == "explicit_coexistence"
                and sorted(adjudication.get("subject_refs") or []) == candidate_refs
            ):
                matching_adjudications.append(adjudication)
        adjudication = matching_adjudications[0] if len(matching_adjudications) == 1 else None
        reviews.append({
            "record_kind": "review_issue",
            "review_id": f"review.duplicate-boundary.{slug(context_ref)}",
            "edition": EDITION,
            "review_kind": "possible_duplicate_or_conflict",
            "status": "adjudicated_explicit_coexistence" if adjudication else "open",
            "context_ref": context_ref,
            "candidate_refs": candidate_refs,
            "observed_overlaps": [{"public_type": name, "library_refs": sorted(refs)} for name, refs in overlaps],
            "conflict_checks": ["responsibility overlap", "operation ownership", "law inconsistency", "dependency cycle", "different names for equivalent contract", "same name for incompatible contract"],
            "resolution_rule": (
                f"{adjudication['decision_id']}: {adjudication['rationale']} No compatibility alias is admitted."
                if adjudication
                else "Owner adjudicates merge, split, specialization or explicit coexistence; spelling similarity alone is not decisive."
            ),
            "evidence_refs": ["source.parnas.1972", "source.iso.42010.2022"],
        })
    return reviews


def artifact_model_records() -> list[dict[str, Any]]:
    # These are type exemplars for the registry itself, not claims that an implementation exists.
    kinds = [
        ("implementation_artifact", "ImplementationArtifact", "Source/binary realization of one contribution in one language; conformance status is separate."),
        ("package_artifact", "PackageArtifact", "Distribution unit such as a Cargo crate, npm package, wheel or component package; may contain several artifacts."),
        ("build_artifact", "BuildArtifact", "Digest-addressed output of a declared recipe, toolchain, inputs and target."),
        ("deployed_service", "DeployedService", "Operational occurrence exposing one or more offers with deployment-owned limits and receipts."),
        ("product", "Product", "Commercial or user-facing bundle that packages contributions and services without acquiring semantic ownership."),
    ]
    return [{
        "record_kind": "artifact_kind_definition",
        "kind_id": f"artifact-kind.{key}",
        "edition": EDITION,
        "name": name,
        "definition": definition,
        "identity_fields": {
            "implementation_artifact": ["implementation_id", "library_ref", "language", "source_digest", "conformance_receipts"],
            "package_artifact": ["package_id", "ecosystem", "name", "version", "artifact_refs"],
            "build_artifact": ["build_id", "subject_digest", "recipe_digest", "toolchain", "target", "provenance_ref"],
            "deployed_service": ["deployment_id", "build_ref", "offer_refs", "target_ref", "validity", "runtime_receipts"],
            "product": ["product_id", "edition", "packaged_refs", "outcome_promises", "operator_refs"],
        }[key],
        "non_collapse_law": "This identity cannot be used as the library family, semantic owner, or proof of law conformance.",
        "evidence_refs": ["source.iso.42010.2022", "source.c4model.abstractions", "source.oci.image-spec"],
    } for key, name, definition in kinds]


def build_schema() -> dict[str, Any]:
    id_pattern = r"^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)+$"
    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://san.example/spec/library-registry-v1.schema.json",
        "title": "Governed reusable-library contribution registry",
        "description": "Normalized research metamodel. Source universe schemas are projections, not canonical.",
        "oneOf": [{"$ref": f"#/$defs/{name}"} for name in [
            "libraryContribution", "libraryFamily", "libraryDesignContext", "implementationArtifact", "packageArtifact", "buildArtifact", "deployedService", "product", "contextLink", "operationLink", "kernelLink", "dependencyEdge", "capabilityRequirement", "capabilityOffer", "registryDecision", "evidenceSource", "innovation", "typedGap", "reviewIssue", "localCrosswalk", "artifactKindDefinition"
        ]],
        "$defs": {
            "id": {"type": "string", "pattern": id_pattern},
            "refs": {"type": "array", "items": {"$ref": "#/$defs/id"}, "uniqueItems": True},
            "strings": {"type": "array", "items": {"type": "string"}, "uniqueItems": True},
            "base": {"type": "object", "required": ["record_kind", "edition"], "properties": {"record_kind": {"type": "string"}, "edition": {"type": "integer", "minimum": 1}}},
            "libraryContribution": {"type": "object", "required": ["record_kind", "library_id", "edition", "name", "status", "library_class", "family_ref", "semantic_owners", "context_refs", "scope", "api_contract", "effects", "typed_inputs", "behavior", "execution", "bounds", "boundaries", "feature_dependency_graph", "platform", "supply_chain", "code_risk", "evolution", "replacement", "capabilities", "conformance", "evidence_refs", "gaps", "source_projection"], "properties": {"record_kind": {"const": "library_contribution"}, "library_id": {"type": "string", "pattern": "^library\\."}, "edition": {"type": "integer", "minimum": 1}, "name": {"type": "string", "minLength": 1}, "status": {"enum": ["candidate_unadjudicated", "specified_unimplemented", "observed_claim_unverified", "rejected_unresolved_owner", "qualified", "deprecated", "retired"]}, "library_class": {"enum": ["semantic_pure", "algorithm_pure", "policy_pure", "test_oracle", "effect_port_contract", "runtime_mechanism", "provider_adapter", "target_backend", "generated_support", "candidate_unclassified"]}, "family_ref": {"$ref": "#/$defs/id"}, "semantic_owners": {"type": "array", "minItems": 1, "maxItems": 1, "items": {"type": "object"}}, "context_refs": {"$ref": "#/$defs/refs"}, "scope": {"type": "object"}, "api_contract": {"type": "object", "required": ["types", "traits", "operations"]}, "effects": {"type": "object", "required": ["boundary", "intents", "receipts", "ambient_effects_forbidden"]}, "typed_inputs": {"type": "object"}, "behavior": {"type": "object"}, "execution": {"type": "object"}, "bounds": {"type": "object"}, "boundaries": {"type": "object"}, "feature_dependency_graph": {"type": "object"}, "platform": {"type": "object"}, "supply_chain": {"type": "object"}, "code_risk": {"type": "object"}, "evolution": {"type": "object"}, "replacement": {"type": "object"}, "capabilities": {"type": "object"}, "conformance": {"type": "object"}, "evidence_refs": {"$ref": "#/$defs/refs"}, "gaps": {"type": "array"}, "source_projection": {"type": "object"}}, "additionalProperties": False},
            "libraryFamily": {"type": "object", "required": ["record_kind", "family_id", "edition", "status", "semantic_owner_refs", "contribution_refs", "cohesion_law", "not_an_artifact", "evidence_refs"], "properties": {"record_kind": {"const": "library_family"}, "family_id": {"$ref": "#/$defs/id"}, "edition": {"type": "integer"}, "status": {"type": "string"}, "semantic_owner_refs": {"$ref": "#/$defs/refs"}, "contribution_refs": {"$ref": "#/$defs/refs"}, "cohesion_law": {"type": "string"}, "not_an_artifact": {"$ref": "#/$defs/strings"}, "evidence_refs": {"$ref": "#/$defs/refs"}}, "additionalProperties": False},
            "libraryDesignContext": {"type": "object", "required": ["record_kind", "context_id", "edition", "status", "semantic_owner_ref", "library_refs", "boundary_law", "evidence_refs"], "properties": {"record_kind": {"const": "library_design_context"}, "context_id": {"$ref": "#/$defs/id"}, "edition": {"type": "integer"}, "status": {"type": "string"}, "semantic_owner_ref": {"$ref": "#/$defs/id"}, "library_refs": {"$ref": "#/$defs/refs"}, "boundary_law": {"type": "string"}, "evidence_refs": {"$ref": "#/$defs/refs"}}, "additionalProperties": False},
            "implementationArtifact": {"type": "object", "required": ["record_kind", "implementation_id", "edition", "status", "library_ref", "language", "source_digest", "maintainer_control_ref", "api_surface", "unsafe_ffi_generated", "conformance_receipts", "independence_group_ref", "evidence_refs", "gaps"], "properties": {"record_kind": {"const": "implementation_artifact"}, "implementation_id": {"$ref": "#/$defs/id"}, "edition": {"type": "integer"}, "status": {"enum": ["observed_unverified", "conformant", "qualified", "deprecated", "retired"]}, "library_ref": {"$ref": "#/$defs/id"}, "language": {"type": "string"}, "source_digest": {"type": "string"}, "maintainer_control_ref": {"$ref": "#/$defs/id"}, "api_surface": {"type": "object"}, "unsafe_ffi_generated": {"type": "object"}, "conformance_receipts": {"$ref": "#/$defs/refs"}, "independence_group_ref": {"$ref": "#/$defs/id"}, "evidence_refs": {"$ref": "#/$defs/refs"}, "gaps": {"$ref": "#/$defs/refs"}}, "additionalProperties": False},
            "packageArtifact": {"type": "object", "required": ["record_kind", "package_id", "edition", "ecosystem", "name", "version", "artifact_refs", "feature_graph", "dependency_graph", "license_expression", "advisory_refs", "sbom_ref", "publish_source"], "properties": {"record_kind": {"const": "package_artifact"}, "package_id": {"$ref": "#/$defs/id"}, "edition": {"type": "integer"}, "ecosystem": {"type": "string"}, "name": {"type": "string"}, "version": {"type": "string"}, "artifact_refs": {"$ref": "#/$defs/refs"}, "feature_graph": {"type": "object"}, "dependency_graph": {"type": "object"}, "license_expression": {"type": ["string", "null"]}, "advisory_refs": {"$ref": "#/$defs/refs"}, "sbom_ref": {"type": ["string", "null"]}, "publish_source": {"type": "string"}}, "additionalProperties": False},
            "buildArtifact": {"type": "object", "required": ["record_kind", "build_id", "edition", "package_ref", "implementation_refs", "recipe_digest", "source_digest", "toolchain", "target", "profile", "feature_set", "sbom_ref", "provenance_ref", "reproducible", "unsafe_summary"], "properties": {"record_kind": {"const": "build_artifact"}, "build_id": {"$ref": "#/$defs/id"}, "edition": {"type": "integer"}, "package_ref": {"$ref": "#/$defs/id"}, "implementation_refs": {"$ref": "#/$defs/refs"}, "recipe_digest": {"type": "string"}, "source_digest": {"type": "string"}, "toolchain": {"type": "object"}, "target": {"type": "object"}, "profile": {"type": "object"}, "feature_set": {"$ref": "#/$defs/strings"}, "sbom_ref": {"$ref": "#/$defs/id"}, "provenance_ref": {"$ref": "#/$defs/id"}, "reproducible": {"type": "object"}, "unsafe_summary": {"type": "object"}}, "additionalProperties": False},
            "deployedService": {"type": "object", "required": ["record_kind", "service_id", "edition", "build_ref", "offer_refs", "provider_ref", "target_ref", "limits", "validity", "runtime_receipt_refs"], "properties": {"record_kind": {"const": "deployed_service"}, "service_id": {"$ref": "#/$defs/id"}, "edition": {"type": "integer"}, "build_ref": {"$ref": "#/$defs/id"}, "offer_refs": {"$ref": "#/$defs/refs"}, "provider_ref": {"$ref": "#/$defs/id"}, "target_ref": {"$ref": "#/$defs/id"}, "limits": {"type": "object"}, "validity": {"type": "object"}, "runtime_receipt_refs": {"$ref": "#/$defs/refs"}}, "additionalProperties": False},
            "product": {"type": "object", "required": ["record_kind", "product_id", "edition", "packaged_refs", "external_semantic_owner_refs", "user_outcomes", "operator_obligations", "non_ownership_law"], "properties": {"record_kind": {"const": "product"}, "product_id": {"$ref": "#/$defs/id"}, "edition": {"type": "integer"}, "packaged_refs": {"$ref": "#/$defs/refs"}, "external_semantic_owner_refs": {"$ref": "#/$defs/refs"}, "user_outcomes": {"$ref": "#/$defs/strings"}, "operator_obligations": {"$ref": "#/$defs/strings"}, "non_ownership_law": {"type": "string"}}, "additionalProperties": False},
            "contextLink": {"$ref": "#/$defs/genericLinkContext"},
            "operationLink": {"$ref": "#/$defs/genericLinkOperation"},
            "kernelLink": {"$ref": "#/$defs/genericLinkKernel"},
            "genericLinkContext": {"type": "object", "required": ["record_kind", "link_id", "edition", "context_ref", "library_ref", "relationship", "status", "evidence_refs"], "properties": {"record_kind": {"const": "context_to_library"}, "link_id": {"$ref": "#/$defs/id"}, "edition": {"type": "integer"}, "context_ref": {"$ref": "#/$defs/id"}, "library_ref": {"$ref": "#/$defs/id"}, "relationship": {"type": "string"}, "status": {"type": "string"}, "evidence_refs": {"$ref": "#/$defs/refs"}}, "additionalProperties": False},
            "genericLinkOperation": {"type": "object", "required": ["record_kind", "link_id", "edition", "operation_ref", "library_ref", "role", "status", "evidence_refs"], "properties": {"record_kind": {"const": "operation_to_library"}, "link_id": {"$ref": "#/$defs/id"}, "edition": {"type": "integer"}, "operation_ref": {"$ref": "#/$defs/id"}, "library_ref": {"$ref": "#/$defs/id"}, "role": {"type": "string"}, "status": {"type": "string"}, "evidence_refs": {"$ref": "#/$defs/refs"}}, "additionalProperties": False},
            "genericLinkKernel": {"type": "object", "required": ["record_kind", "link_id", "edition", "kernel_ref", "library_ref", "role", "status", "evidence_refs"], "properties": {"record_kind": {"const": "kernel_to_library"}, "link_id": {"$ref": "#/$defs/id"}, "edition": {"type": "integer"}, "kernel_ref": {"$ref": "#/$defs/id"}, "library_ref": {"$ref": "#/$defs/id"}, "role": {"type": "string"}, "status": {"type": "string"}, "evidence_refs": {"$ref": "#/$defs/refs"}}, "additionalProperties": False},
            "dependencyEdge": {"type": "object", "required": ["record_kind", "edge_id", "edition", "from_ref", "to_ref", "dependency_kind", "optional", "feature_ref", "purpose", "cycle_policy", "removal_seam", "status"], "properties": {"record_kind": {"const": "dependency_edge"}, "edge_id": {"$ref": "#/$defs/id"}, "edition": {"type": "integer"}, "from_ref": {"$ref": "#/$defs/id"}, "to_ref": {"$ref": "#/$defs/id"}, "dependency_kind": {"type": "string"}, "optional": {"type": "boolean"}, "feature_ref": {"type": ["string", "null"]}, "purpose": {"type": "string"}, "cycle_policy": {"type": "string"}, "removal_seam": {"type": "string"}, "status": {"type": "string"}}, "additionalProperties": False},
            "capabilityRequirement": {"type": "object", "required": ["record_kind", "requirement_id", "edition", "status", "subject_ref", "capability_kind", "required_contract_refs", "required_operation_refs", "required_guarantees", "provider_requirements", "target_requirements", "evidence_gates", "fallback_law"], "properties": {"record_kind": {"const": "capability_requirement"}, "requirement_id": {"$ref": "#/$defs/id"}, "edition": {"type": "integer"}, "status": {"type": "string"}, "subject_ref": {"$ref": "#/$defs/id"}, "capability_kind": {"type": "string"}, "required_contract_refs": {"$ref": "#/$defs/refs"}, "required_operation_refs": {"$ref": "#/$defs/refs"}, "required_guarantees": {"$ref": "#/$defs/strings"}, "provider_requirements": {"$ref": "#/$defs/strings"}, "target_requirements": {"$ref": "#/$defs/strings"}, "evidence_gates": {"$ref": "#/$defs/strings"}, "fallback_law": {"const": "refuse"}}, "additionalProperties": False},
            "capabilityOffer": {"type": "object", "required": ["record_kind", "offer_id", "edition", "status", "subject_ref", "capability_kind", "offered_contract_refs", "implementation_refs", "independence_criteria", "minimum_independent_qualified_implementations", "observed_independent_qualified_implementations", "portable", "evidence_refs", "gaps"], "properties": {"record_kind": {"const": "capability_offer"}, "offer_id": {"$ref": "#/$defs/id"}, "edition": {"type": "integer"}, "status": {"type": "string"}, "subject_ref": {"$ref": "#/$defs/id"}, "capability_kind": {"type": "string"}, "offered_contract_refs": {"$ref": "#/$defs/refs"}, "implementation_refs": {"$ref": "#/$defs/refs"}, "independence_criteria": {"$ref": "#/$defs/strings"}, "minimum_independent_qualified_implementations": {"type": "integer", "minimum": 2}, "observed_independent_qualified_implementations": {"type": "integer", "minimum": 0}, "portable": {"type": "boolean"}, "evidence_refs": {"$ref": "#/$defs/refs"}, "gaps": {"$ref": "#/$defs/refs"}}, "additionalProperties": False},
            "registryDecision": {"type": "object", "required": ["record_kind", "decision_id", "edition", "status", "owner_context_ref", "question", "value_type", "allowed_values", "binding_phase", "authority_ref", "default_law", "consequences", "evidence_refs"], "properties": {"record_kind": {"const": "registry_decision"}, "decision_id": {"$ref": "#/$defs/id"}, "edition": {"type": "integer"}, "status": {"type": "string"}, "owner_context_ref": {"$ref": "#/$defs/id"}, "question": {"type": "string"}, "value_type": {"type": "string"}, "allowed_values": {"$ref": "#/$defs/strings"}, "binding_phase": {"type": "string"}, "authority_ref": {"$ref": "#/$defs/id"}, "default_law": {"type": "string"}, "consequences": {"$ref": "#/$defs/strings"}, "evidence_refs": {"$ref": "#/$defs/refs"}}, "additionalProperties": False},
            "evidenceSource": {"type": "object", "required": ["record_kind", "source_id", "edition", "title", "uri", "authority", "source_kind", "topic", "published", "retrieved", "claim_scope"], "properties": {"record_kind": {"const": "evidence_source"}, "source_id": {"$ref": "#/$defs/id"}, "edition": {"type": "integer"}, "title": {"type": "string"}, "uri": {"type": "string", "format": "uri"}, "authority": {"type": "string"}, "source_kind": {"type": "string"}, "topic": {"type": "string"}, "published": {"type": ["string", "null"]}, "retrieved": {"type": "string", "format": "date"}, "claim_scope": {"type": "string"}}, "additionalProperties": False},
            "innovation": {"type": "object", "required": ["record_kind", "innovation_id", "edition", "year", "name", "non_llm", "registry_consequence", "evidence_refs", "adoption_status"], "properties": {"record_kind": {"const": "innovation"}, "innovation_id": {"$ref": "#/$defs/id"}, "edition": {"type": "integer"}, "year": {"type": "integer", "minimum": 2021, "maximum": 2026}, "name": {"type": "string"}, "non_llm": {"const": True}, "registry_consequence": {"type": "string"}, "evidence_refs": {"$ref": "#/$defs/refs"}, "adoption_status": {"type": "string"}}, "additionalProperties": False},
            "typedGap": {"type": "object", "required": ["record_kind", "gap_id", "edition", "status", "subject_ref", "gap_kind", "blocking", "description", "versioned_from", "resolution_condition", "prohibited_fallbacks", "evidence_refs"], "properties": {"record_kind": {"const": "typed_gap"}, "gap_id": {"$ref": "#/$defs/id"}, "edition": {"type": "integer"}, "status": {"type": "string"}, "subject_ref": {"$ref": "#/$defs/id"}, "gap_kind": {"type": "string"}, "blocking": {"type": "boolean"}, "description": {"type": "string"}, "versioned_from": {"type": "string"}, "resolution_condition": {"type": "string"}, "prohibited_fallbacks": {"$ref": "#/$defs/strings"}, "evidence_refs": {"$ref": "#/$defs/refs"}}, "additionalProperties": False},
            "reviewIssue": {"type": "object", "required": ["record_kind", "review_id", "edition", "review_kind", "status", "context_ref", "candidate_refs", "observed_overlaps", "conflict_checks", "resolution_rule", "evidence_refs"], "properties": {"record_kind": {"const": "review_issue"}, "review_id": {"$ref": "#/$defs/id"}, "edition": {"type": "integer"}, "review_kind": {"type": "string"}, "status": {"type": "string"}, "context_ref": {"$ref": "#/$defs/id"}, "candidate_refs": {"$ref": "#/$defs/refs"}, "observed_overlaps": {"type": "array"}, "conflict_checks": {"$ref": "#/$defs/strings"}, "resolution_rule": {"type": "string"}, "evidence_refs": {"$ref": "#/$defs/refs"}}, "additionalProperties": False},
            "localCrosswalk": {"type": "object", "required": ["record_kind", "crosswalk_id", "edition", "source_locator", "source_candidate_id", "normalized_library_ref", "mapping_status", "preserved_claims", "normalization_notes"], "properties": {"record_kind": {"const": "local_crosswalk"}, "crosswalk_id": {"$ref": "#/$defs/id"}, "edition": {"type": "integer"}, "source_locator": {"type": "string"}, "source_candidate_id": {"type": "string"}, "normalized_library_ref": {"$ref": "#/$defs/id"}, "mapping_status": {"type": "string"}, "preserved_claims": {"$ref": "#/$defs/strings"}, "normalization_notes": {"$ref": "#/$defs/strings"}}, "additionalProperties": False},
            "artifactKindDefinition": {"type": "object", "required": ["record_kind", "kind_id", "edition", "name", "definition", "identity_fields", "non_collapse_law", "evidence_refs"], "properties": {"record_kind": {"const": "artifact_kind_definition"}, "kind_id": {"$ref": "#/$defs/id"}, "edition": {"type": "integer"}, "name": {"type": "string"}, "definition": {"type": "string"}, "identity_fields": {"$ref": "#/$defs/strings"}, "non_collapse_law": {"type": "string"}, "evidence_refs": {"$ref": "#/$defs/refs"}}, "additionalProperties": False},
        },
    }
    defs = schema["$defs"]
    defs.update({
        "semanticOwner": {"type": "object", "required": ["context_ref", "role", "authority_refs"], "properties": {"context_ref": {"$ref": "#/$defs/id"}, "role": {"const": "meaning_owner"}, "authority_refs": {"$ref": "#/$defs/refs"}}, "additionalProperties": False},
        "contributionScope": {"type": "object", "required": ["responsibilities", "exclusions", "boundary_rationale", "refusal_rule"], "properties": {"responsibilities": {"$ref": "#/$defs/strings"}, "exclusions": {"$ref": "#/$defs/strings"}, "boundary_rationale": {"type": "string"}, "refusal_rule": {"type": "string"}, "boundary_adjudication": {"$ref": "#/$defs/boundaryAdjudication"}}, "additionalProperties": False},
        "boundaryAdjudication": {"type": "object", "required": ["decision_id", "disposition", "subject_refs", "rationale", "no_compatibility_alias"], "properties": {"decision_id": {"$ref": "#/$defs/id"}, "disposition": {"enum": ["retain_as_is", "retain_but_narrow", "split", "merge", "rename", "replace", "retire", "explicit_coexistence"]}, "subject_refs": {"$ref": "#/$defs/refs"}, "rationale": {"type": "string", "minLength": 1}, "no_compatibility_alias": {"const": True}}, "additionalProperties": False},
        "publicType": {"type": "object", "required": ["type_id", "name", "role", "origin"], "properties": {"type_id": {"$ref": "#/$defs/id"}, "name": {"type": "string"}, "role": {"type": "string"}, "origin": {"enum": ["source_projection", "registry_placeholder_pending_owner"]}}, "additionalProperties": False},
        "publicTrait": {"type": "object", "required": ["trait_id", "name", "object_safety", "origin"], "properties": {"trait_id": {"$ref": "#/$defs/id"}, "name": {"type": "string"}, "object_safety": {"type": "string"}, "origin": {"enum": ["source_projection", "registry_placeholder_pending_owner"]}}, "additionalProperties": False},
        "publicOperation": {"type": "object", "required": ["operation_ref", "name", "input_types", "output_type", "purity", "effect_intent_type", "receipt_type", "refusal_types", "origin"], "properties": {"operation_ref": {"$ref": "#/$defs/id"}, "name": {"type": "string"}, "input_types": {"$ref": "#/$defs/strings"}, "output_type": {"type": "string"}, "purity": {"enum": ["pure", "effectful_explicit", "unresolved_refuse"]}, "effect_intent_type": {"type": ["string", "null"]}, "receipt_type": {"type": ["string", "null"]}, "refusal_types": {"$ref": "#/$defs/strings"}, "origin": {"enum": ["source_projection", "registry_placeholder_pending_owner"]}}, "additionalProperties": False},
        "apiContract": {"type": "object", "required": ["types", "traits", "operations"], "properties": {"types": {"type": "array", "minItems": 1, "items": {"$ref": "#/$defs/publicType"}}, "traits": {"type": "array", "minItems": 1, "items": {"$ref": "#/$defs/publicTrait"}}, "operations": {"type": "array", "minItems": 1, "items": {"$ref": "#/$defs/publicOperation"}}}, "additionalProperties": False},
        "intentOrReceipt": {"type": "object", "required": ["type", "required_fields"], "properties": {"type": {"type": "string"}, "required_fields": {"$ref": "#/$defs/strings"}}, "additionalProperties": False},
        "effectContract": {"type": "object", "required": ["boundary", "intents", "receipts", "ambient_effects_forbidden"], "properties": {"boundary": {"enum": ["pure_no_io", "pure_effect_intents", "effectful_runtime", "ffi_boundary", "generated_boundary", "unresolved_refuse"]}, "intents": {"type": "array", "items": {"$ref": "#/$defs/intentOrReceipt"}}, "receipts": {"type": "array", "items": {"$ref": "#/$defs/intentOrReceipt"}}, "ambient_effects_forbidden": {"$ref": "#/$defs/strings"}}, "additionalProperties": False},
        "typedInputs": {"type": "object", "required": ["decision_refs", "configuration_types", "default_law"], "properties": {"decision_refs": {"$ref": "#/$defs/refs"}, "configuration_types": {"$ref": "#/$defs/strings"}, "default_law": {"type": "string"}}, "additionalProperties": False},
        "behaviorContract": {"type": "object", "required": ["laws", "invariants", "refusals", "refusal_precedence", "errors"], "properties": {"laws": {"$ref": "#/$defs/strings"}, "invariants": {"$ref": "#/$defs/strings"}, "refusals": {"$ref": "#/$defs/strings"}, "refusal_precedence": {"$ref": "#/$defs/strings"}, "errors": {"$ref": "#/$defs/strings"}}, "additionalProperties": False},
        "executionContract": {"type": "object", "required": ["mode", "cancellation", "concurrency", "thread_safety", "determinism"], "properties": {"mode": {"enum": ["sync", "mixed_explicit", "unresolved_refuse"]}, "cancellation": {"$ref": "#/$defs/strings"}, "concurrency": {"$ref": "#/$defs/strings"}, "thread_safety": {"type": "string"}, "determinism": {"type": "string"}}, "additionalProperties": False},
        "boundsContract": {"type": "object", "required": ["time", "state", "resources"], "properties": {"time": {"type": "string"}, "state": {"type": "string"}, "resources": {"$ref": "#/$defs/strings"}}, "additionalProperties": False},
        "boundaryContract": {"type": "object", "required": ["abi", "serialization", "dtos", "anti_corruption"], "properties": {"abi": {"type": "string"}, "serialization": {"type": "string"}, "dtos": {"$ref": "#/$defs/strings"}, "anti_corruption": {"type": "string"}}, "additionalProperties": False},
        "featureGraph": {"type": "object", "required": ["features", "dependency_refs", "feature_laws"], "properties": {"features": {"type": "array", "items": {"type": "object", "required": ["feature_id", "default", "additive"], "properties": {"feature_id": {"type": "string"}, "default": {"type": "boolean"}, "additive": {"type": "boolean"}}, "additionalProperties": False}}, "dependency_refs": {"$ref": "#/$defs/refs"}, "feature_laws": {"$ref": "#/$defs/strings"}}, "additionalProperties": False},
        "platformContract": {"type": "object", "required": ["msrv", "rust_editions", "targets", "no_std", "provider_requirements", "target_requirements"], "properties": {"msrv": {"type": "object", "required": ["value", "status"]}, "rust_editions": {"$ref": "#/$defs/strings"}, "targets": {"$ref": "#/$defs/strings"}, "no_std": {"type": "string"}, "provider_requirements": {"$ref": "#/$defs/strings"}, "target_requirements": {"$ref": "#/$defs/strings"}}, "additionalProperties": False},
        "supplyChainContract": {"type": "object", "required": ["license_expression", "advisory_policy", "sbom", "reproducibility", "provenance"], "properties": {"license_expression": {"type": ["string", "null"]}, "advisory_policy": {"type": "string"}, "sbom": {"type": "string"}, "reproducibility": {"type": "string"}, "provenance": {"type": "string"}}, "additionalProperties": False},
        "codeRiskContract": {"type": "object", "required": ["unsafe", "ffi", "generated"], "properties": {"unsafe": {"$ref": "#/$defs/strings"}, "ffi": {"type": "string"}, "generated": {"type": "string"}}, "additionalProperties": False},
        "evolutionContract": {"type": "object", "required": ["compatibility_dimensions", "compatibility", "migration", "deprecation"], "properties": {"compatibility_dimensions": {"$ref": "#/$defs/strings"}, "compatibility": {"$ref": "#/$defs/strings"}, "migration": {"type": "string"}, "deprecation": {"type": "string"}}, "additionalProperties": False},
        "replacementContract": {"type": "object", "required": ["seams", "substitution_law"], "properties": {"seams": {"$ref": "#/$defs/strings"}, "substitution_law": {"type": "string"}}, "additionalProperties": False},
        "capabilityRefs": {"type": "object", "required": ["required", "offered"], "properties": {"required": {"$ref": "#/$defs/refs"}, "offered": {"$ref": "#/$defs/refs"}}, "additionalProperties": False},
        "conformanceContract": {"type": "object", "required": ["oracles", "fixtures", "fuzz", "model_tests", "property_tests", "differential_tests", "qualified_independent_implementation_count", "portable_offer_gate", "portable_offer"], "properties": {"oracles": {"$ref": "#/$defs/strings"}, "fixtures": {"$ref": "#/$defs/strings"}, "fuzz": {"$ref": "#/$defs/strings"}, "model_tests": {"$ref": "#/$defs/strings"}, "property_tests": {"$ref": "#/$defs/strings"}, "differential_tests": {"$ref": "#/$defs/strings"}, "qualified_independent_implementation_count": {"type": "integer", "minimum": 0}, "portable_offer_gate": {"const": "requires_at_least_two_independent_qualified_implementations"}, "portable_offer": {"type": "boolean"}}, "additionalProperties": False},
        "contributionGap": {"type": "object", "required": ["gap_id", "gap_kind", "introduced_in", "description", "blocking", "resolution_condition"], "properties": {"gap_id": {"$ref": "#/$defs/id"}, "gap_kind": {"type": "string"}, "introduced_in": {"type": "string"}, "description": {"type": "string"}, "blocking": {"type": "boolean"}, "resolution_condition": {"type": "string"}}, "additionalProperties": False},
        "sourceProjection": {"type": "object", "required": ["path", "line", "source_library_id", "source_status", "source_schema_is_canonical"], "properties": {"path": {"type": "string"}, "line": {"type": "integer", "minimum": 1}, "source_library_id": {"type": "string"}, "source_status": {"type": ["string", "null"]}, "source_schema_is_canonical": {"const": False}}, "additionalProperties": False},
    })
    contribution_properties = defs["libraryContribution"]["properties"]
    contribution_properties.update({
        "semantic_owners": {"type": "array", "minItems": 1, "maxItems": 1, "items": {"$ref": "#/$defs/semanticOwner"}},
        "scope": {"$ref": "#/$defs/contributionScope"},
        "api_contract": {"$ref": "#/$defs/apiContract"},
        "effects": {"$ref": "#/$defs/effectContract"},
        "typed_inputs": {"$ref": "#/$defs/typedInputs"},
        "behavior": {"$ref": "#/$defs/behaviorContract"},
        "execution": {"$ref": "#/$defs/executionContract"},
        "bounds": {"$ref": "#/$defs/boundsContract"},
        "boundaries": {"$ref": "#/$defs/boundaryContract"},
        "feature_dependency_graph": {"$ref": "#/$defs/featureGraph"},
        "platform": {"$ref": "#/$defs/platformContract"},
        "supply_chain": {"$ref": "#/$defs/supplyChainContract"},
        "code_risk": {"$ref": "#/$defs/codeRiskContract"},
        "evolution": {"$ref": "#/$defs/evolutionContract"},
        "replacement": {"$ref": "#/$defs/replacementContract"},
        "capabilities": {"$ref": "#/$defs/capabilityRefs"},
        "conformance": {"$ref": "#/$defs/conformanceContract"},
        "gaps": {"type": "array", "minItems": 1, "items": {"$ref": "#/$defs/contributionGap"}},
        "source_projection": {"$ref": "#/$defs/sourceProjection"},
    })
    return schema


def metamodel() -> dict[str, Any]:
    return {
        "metamodel_id": "san.domain-atlas.governed-library-registry",
        "edition": EDITION,
        "as_of": AS_OF,
        "completion_claim": False,
        "purpose": "Connect context-owned research contracts to replaceable Rust or multi-language implementations without collapsing semantics into artifacts or products.",
        "identity_chain": ["library_design_context", "library_family", "library_contribution", "implementation_artifact", "package_artifact", "build_artifact", "deployed_service", "product"],
        "non_collapse_laws": [
            "a family is an owned compatibility domain, not a package namespace",
            "a contribution is a reusable contract boundary, not one vocabulary term",
            "an implementation realizes a contribution but does not prove its laws by existing",
            "a crate/package is a distribution unit and may not be the semantic boundary",
            "a build is a target-specific occurrence of inputs, recipe and toolchain",
            "a deployed service is an operational occurrence with time-bounded offers",
            "a product packages contributions and outcomes but does not acquire semantic ownership",
        ],
        "portable_offer_gate": {"minimum_independent_qualified_implementations": 2, "independence_dimensions": ["control/maintainership", "implementation source", "build", "conformance execution"], "existing_code_is_conformance": False},
        "boundary_admission": ["one named semantic owner or explicit shared-contract authority", "coherent responsibilities and laws", "provider-neutral typed API", "effects isolated as intents and receipts", "independent removal/substitution seam", "finite bounds and typed refusals", "testable without a product or deployed provider"],
        "boundary_refusals": ["one-library-per-term", "vendor SDK or product bundle", "crate/package identity as sufficient evidence", "service or deployment identity", "generated code as semantic owner", "hidden ambient effects", "single implementation claimed portable"],
        "record_kinds": ["library_design_context", "library_family", "library_contribution", "implementation_artifact", "package_artifact", "build_artifact", "deployed_service", "product", "artifact_kind_definition", "context_to_library", "operation_to_library", "kernel_to_library", "dependency_edge", "capability_requirement", "capability_offer", "registry_decision", "evidence_source", "innovation", "typed_gap", "review_issue", "local_crosswalk"],
    }


PARTITIONS = {
    "library_design_context": "library-design-contexts.jsonl",
    "library_family": "library-families.jsonl",
    "library_contribution": "library-contributions.jsonl",
    "context_to_library": "context-to-library.jsonl",
    "operation_to_library": "operation-to-library.jsonl",
    "kernel_to_library": "kernel-to-library.jsonl",
    "dependency_edge": "dependency-edges.jsonl",
    "capability_requirement": "capability-requirements.jsonl",
    "capability_offer": "capability-offers.jsonl",
    "registry_decision": "decisions.jsonl",
    "evidence_source": "evidence-sources.jsonl",
    "innovation": "innovations-2021-2026.jsonl",
    "typed_gap": "typed-gaps.jsonl",
    "review_issue": "review-queue.jsonl",
    "local_crosswalk": "local-crosswalk.jsonl",
    "artifact_kind_definition": "artifact-kind-definitions.jsonl",
}


def canonical_line(record: dict[str, Any]) -> str:
    return json.dumps(record, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    text = "\n".join(canonical_line(record) for record in records) + ("\n" if records else "")
    path.write_text(text, encoding="utf-8")


def identity(record: dict[str, Any]) -> str:
    for key in ("library_id", "family_id", "context_id", "link_id", "edge_id", "requirement_id", "offer_id", "decision_id", "source_id", "innovation_id", "gap_id", "review_id", "crosswalk_id", "kind_id"):
        if key in record:
            return str(record[key])
    raise KeyError(record)


def generate() -> dict[str, Any]:
    contributions = []
    crosswalks = []
    inventory = []
    for path in local_library_outputs():
        is_candidate_registry = path.suffix == ".jsonl"
        if is_candidate_registry:
            record_count = len(read_jsonl(path))
            role = "candidate_registry"
        elif "schema" in path.name or "schema" in path.parts:
            record_count = 1
            role = "source_schema_noncanonical"
        elif "qualification" in path.name:
            record_count = 1
            role = "provider_qualification_contract"
        else:
            record_count = 1
            role = "supporting_library_output"
        inventory.append({
            "path": path.relative_to(ATLAS.parent.parent).as_posix(),
            "artifact_role": role,
            "records": record_count,
            "candidate_records": record_count if is_candidate_registry else 0,
            "source_schema_is_canonical": False,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        })
    for path in local_candidate_files():
        rows = read_jsonl(path)
        for line_number, raw in rows:
            contribution, crosswalk = normalize_candidate(path, line_number, raw)
            contributions.append(contribution)
            crosswalks.append(crosswalk)
    normalized_library_ids = {item["library_id"] for item in contributions}
    for item in contributions:
        missing_dependency_refs = sorted(
            ref for ref in item["feature_dependency_graph"]["dependency_refs"]
            if ref not in normalized_library_ids
        )
        if missing_dependency_refs:
            item["gaps"].append({
                "gap_id": f"gap.{item['library_id'].removeprefix('library.')}.dangling-dependency.v1",
                "gap_kind": "dependency_identity_unresolved",
                "introduced_in": "registry-edition-1",
                "description": f"Exact-looking library references do not resolve in the normalized registry: {', '.join(missing_dependency_refs)}.",
                "blocking": True,
                "resolution_condition": "Bind each reference to an existing editioned contribution or replace it with a typed capability requirement; spelling alone is not identity.",
            })
    contributions.sort(key=identity)
    crosswalks.sort(key=identity)
    records: list[dict[str, Any]] = []
    records.extend(context_records(contributions))
    records.extend(family_records(contributions))
    records.extend(contributions)
    records.extend(link_records(contributions))
    records.extend(capability_records(contributions))
    records.extend(decision_records())
    records.extend(SOURCES)
    records.extend(innovation_records())
    records.extend(gap_records())
    records.extend(review_records(contributions))
    records.extend(crosswalks)
    records.extend(artifact_model_records())
    records.sort(key=lambda x: (x["record_kind"], identity(x)))

    schema_path = HERE / "library-registry.schema.json"
    metamodel_path = HERE / "metamodel.json"
    schema_path.write_text(json.dumps(build_schema(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    metamodel_path.write_text(json.dumps(metamodel(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_jsonl(HERE / "registry.jsonl", records)
    for kind, filename in PARTITIONS.items():
        write_jsonl(HERE / filename, [record for record in records if record["record_kind"] == kind])

    counts: dict[str, int] = defaultdict(int)
    for record in records:
        counts[record["record_kind"]] += 1
    files = [schema_path, metamodel_path, HERE / "registry.jsonl"] + [HERE / filename for filename in PARTITIONS.values()]
    manifest = {
        "registry_id": "san.domain-atlas.governed-library-registry",
        "edition": EDITION,
        "as_of": AS_OF,
        "deterministic": True,
        "completion_claim": False,
        "source_inventory": inventory,
        "compiler_input_inventory": [{
            "path": (HERE.parent / "library-contribution.schema.json").relative_to(ATLAS.parent.parent).as_posix(),
            "artifact_role": "legacy_compiler_schema_noncanonical",
            "source_schema_is_canonical": False,
            "sha256": hashlib.sha256((HERE.parent / "library-contribution.schema.json").read_bytes()).hexdigest(),
        }],
        "counts": dict(sorted(counts.items())),
        "quality_gates": {
            "authoritative_primary_or_official_sources_minimum": 50,
            "library_design_contexts_minimum": 30,
            "normalized_contributions_or_typed_gaps_minimum": 180,
            "registry_decisions_minimum": 25,
            "non_llm_innovations_2021_2026_minimum": 20,
            "portable_offer_requires_independent_implementations": 2,
        },
        "file_sha256": {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in sorted(files, key=lambda p: p.name)},
    }
    (HERE / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


if __name__ == "__main__":
    print(json.dumps(generate()["counts"], sort_keys=True))
