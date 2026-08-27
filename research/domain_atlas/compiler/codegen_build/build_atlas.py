#!/usr/bin/env python3
"""Deterministically build the post-typed-IR code-generation/build research atlas.

This is a candidate research corpus, not an implementation of a compiler.  The
generator deliberately keeps backend selection, emission, dependency resolution,
build execution, packaging, deployment and supply-chain evidence as separate
contracts so that a future compiler can type-check their boundaries.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
EDITION = 1
AS_OF = "2026-08-25"
STATUS = "researched_candidate_not_adjudicated"


def slug_words(slug: str) -> str:
    return slug.replace("_", " ")


def src(
    key: str,
    title: str,
    issuer: str,
    url: str,
    authority_class: str,
    year: int,
    scope: str,
    limitation: str = "Does not by itself prove implementation conformance, adoption, or a universal domain boundary.",
) -> dict[str, Any]:
    return {
        "source_id": f"cgb.source.{key}",
        "edition": EDITION,
        "status": STATUS,
        "title": title,
        "issuer": issuer,
        "url": url,
        "authority_class": authority_class,
        "publication_year": year,
        "primary_or_official": True,
        "claim_scope": scope,
        "limitations": limitation,
        "accessed_at": AS_OF,
    }


SOURCES = [
    src("rust-reference-linkage", "Rust Reference: Linkage", "Rust Project", "https://doc.rust-lang.org/reference/linkage.html", "official_documentation", 2026, "Rust crate types and linkage outputs."),
    src("rust-reference-abi", "Rust Reference: ABI", "Rust Project", "https://doc.rust-lang.org/reference/items/functions.html#extern-function-qualifier", "official_documentation", 2026, "Rust extern ABI declarations."),
    src("rust-ffi", "Rustonomicon: FFI", "Rust Project", "https://doc.rust-lang.org/nomicon/ffi.html", "official_documentation", 2026, "Rust foreign-function boundary mechanics and hazards."),
    src("rustc-codegen", "The rustc book: Codegen options", "Rust Project", "https://doc.rust-lang.org/rustc/codegen-options/", "official_documentation", 2026, "rustc target CPU, features, LTO, relocation, panic, debug and link controls."),
    src("rustc-targets", "The rustc book: Targets", "Rust Project", "https://doc.rust-lang.org/rustc/targets/index.html", "official_documentation", 2026, "Built-in and custom target selection."),
    src("rust-platform-support", "Rust platform support", "Rust Project", "https://doc.rust-lang.org/rustc/platform-support.html", "official_documentation", 2026, "Rust target support tiers and guarantees."),
    src("rust-symbol-mangling", "The rustc book: Symbol mangling", "Rust Project", "https://doc.rust-lang.org/rustc/symbol-mangling/index.html", "official_documentation", 2026, "Rust symbol-name encoding contracts."),
    src("rust-lto", "The rustc book: Linker-plugin LTO", "Rust Project", "https://doc.rust-lang.org/rustc/linker-plugin-lto.html", "official_documentation", 2026, "Cross-language linker-plugin LTO constraints."),
    src("rust-wasip2", "Rust platform support: wasm32-wasip2", "Rust Project", "https://doc.rust-lang.org/rustc/platform-support/wasm32-wasip2.html", "official_documentation", 2026, "Rust WebAssembly component/WASI target behavior."),
    src("cargo-manifest", "Cargo Reference: The Manifest Format", "Rust Project", "https://doc.rust-lang.org/cargo/reference/manifest.html", "official_documentation", 2026, "Cargo package, target and dependency declarations."),
    src("cargo-resolver", "Cargo Reference: Dependency Resolution", "Rust Project", "https://doc.rust-lang.org/cargo/reference/resolver.html", "official_documentation", 2026, "Cargo version and feature resolution semantics."),
    src("cargo-features", "Cargo Reference: Features", "Rust Project", "https://doc.rust-lang.org/cargo/reference/features.html", "official_documentation", 2026, "Cargo additive features and resolver interactions."),
    src("cargo-build-scripts", "Cargo Reference: Build Scripts", "Rust Project", "https://doc.rust-lang.org/cargo/reference/build-scripts.html", "official_documentation", 2026, "Build-script lifecycle, inputs and rustc/link directives."),
    src("cargo-config", "Cargo Reference: Configuration", "Rust Project", "https://doc.rust-lang.org/cargo/reference/config.html", "official_documentation", 2026, "Hierarchical Cargo configuration and target/tool settings."),
    src("cargo-profiles", "Cargo Reference: Profiles", "Rust Project", "https://doc.rust-lang.org/cargo/reference/profiles.html", "official_documentation", 2026, "Cargo compilation profile controls."),
    src("cargo-platform", "Cargo Reference: Platform-specific dependencies", "Rust Project", "https://doc.rust-lang.org/cargo/reference/specifying-dependencies.html#platform-specific-dependencies", "official_documentation", 2026, "Target-conditioned dependency declarations."),
    src("cargo-workspaces", "Cargo Reference: Workspaces", "Rust Project", "https://doc.rust-lang.org/cargo/reference/workspaces.html", "official_documentation", 2026, "Workspace membership, resolver and shared configuration."),
    src("cargo-package", "Cargo Reference: Packaging and publishing", "Rust Project", "https://doc.rust-lang.org/cargo/reference/publishing.html", "official_documentation", 2026, "Cargo package assembly and registry publication."),
    src("cargo-source-replacement", "Cargo Reference: Source replacement", "Rust Project", "https://doc.rust-lang.org/cargo/reference/source-replacement.html", "official_documentation", 2026, "Source replacement and vendoring checksums."),
    src("cargo-vendor", "cargo vendor", "Rust Project", "https://doc.rust-lang.org/cargo/commands/cargo-vendor.html", "official_documentation", 2026, "Vendored dependency source preparation."),
    src("cargo-metadata", "cargo metadata", "Rust Project", "https://doc.rust-lang.org/cargo/commands/cargo-metadata.html", "official_documentation", 2026, "Machine-readable resolved workspace and dependency graph."),
    src("cargo-semver", "Cargo SemVer Compatibility", "Rust Project", "https://doc.rust-lang.org/cargo/reference/semver.html", "official_documentation", 2026, "Rust/Cargo API change compatibility guidance."),
    src("cargo-sbom", "Cargo unstable feature: SBOM", "Rust Project", "https://doc.rust-lang.org/cargo/reference/unstable.html#sbom", "official_documentation", 2026, "Cargo compiler-time SBOM precursor data; explicitly unstable."),
    src("semver", "Semantic Versioning 2.0.0", "SemVer", "https://semver.org/spec/v2.0.0.html", "open_specification", 2013, "Version precedence and compatibility promises."),
    src("spdx3", "SPDX Specification 3.0.1", "Linux Foundation SPDX", "https://spdx.github.io/spdx-spec/v3.0.1/", "open_specification", 2025, "Software supply-chain object model including packages, files and relationships."),
    src("spdx-license-list", "SPDX License List", "Linux Foundation SPDX", "https://spdx.org/licenses/", "open_specification", 2026, "Standard license identifiers and exception identifiers."),
    src("cyclonedx16", "CycloneDX Specification 1.6", "OWASP Foundation", "https://cyclonedx.org/docs/1.6/json/", "open_specification", 2024, "CycloneDX BOM schema and component/service relationships."),
    src("slsa-provenance", "SLSA Provenance", "OpenSSF SLSA", "https://slsa.dev/spec/v1.1/provenance", "open_specification", 2025, "Artifact-to-build-process and input provenance predicate."),
    src("slsa-build-track", "SLSA Build Track", "OpenSSF SLSA", "https://slsa.dev/spec/v1.1/levels", "open_specification", 2025, "Build platform provenance expectations and levels."),
    src("in-toto-attestation", "in-toto Attestation Framework", "in-toto / CNCF", "https://github.com/in-toto/attestation/tree/main/spec", "open_specification", 2026, "Statement, predicate, envelope and bundle layers."),
    src("in-toto-layout", "in-toto Specification", "in-toto / CNCF", "https://github.com/in-toto/docs/blob/master/in-toto-spec.md", "open_specification", 2023, "Supply-chain layouts, links, functionaries and verification."),
    src("dsse", "Dead Simple Signing Envelope", "Secure Systems Lab", "https://github.com/secure-systems-lab/dsse/blob/master/envelope.md", "open_specification", 2021, "Signature envelope with payload-type binding."),
    src("sigstore-architecture", "Sigstore Architecture", "Sigstore / OpenSSF", "https://docs.sigstore.dev/about/overview/", "official_documentation", 2026, "Keyless signing roles across Fulcio, Rekor and signing clients."),
    src("sigstore-bundle", "Sigstore Bundle Format", "Sigstore / OpenSSF", "https://github.com/sigstore/protobuf-specs/blob/main/protos/sigstore_bundle.proto", "open_specification", 2026, "Verification material bundling for offline verification."),
    src("cosign", "Cosign signing and verification", "Sigstore / OpenSSF", "https://docs.sigstore.dev/cosign/signing/signing_with_blobs/", "official_documentation", 2026, "Artifact/blob signing and verification mechanics."),
    src("rekor", "Rekor", "Sigstore / OpenSSF", "https://docs.sigstore.dev/logging/overview/", "official_documentation", 2026, "Transparency-log inclusion and verification material."),
    src("fulcio", "Fulcio", "Sigstore / OpenSSF", "https://docs.sigstore.dev/certificate_authority/overview/", "official_documentation", 2026, "Short-lived signing certificates bound to identities."),
    src("tuf", "The Update Framework Specification", "TUF", "https://theupdateframework.github.io/specification/latest/", "open_specification", 2024, "Repository metadata roles, thresholds, freshness and rollback protection."),
    src("repro-definition", "Definitions — Reproducible Builds", "Reproducible Builds", "https://reproducible-builds.org/docs/definition/", "open_specification", 2026, "Definition of reproducible and deterministic builds."),
    src("source-date-epoch", "SOURCE_DATE_EPOCH", "Reproducible Builds", "https://reproducible-builds.org/docs/source-date-epoch/", "official_documentation", 2026, "Standardized timestamp input for build tools."),
    src("repro-build-path", "Build path — Reproducible Builds", "Reproducible Builds", "https://reproducible-builds.org/docs/build-path/", "official_documentation", 2026, "Build-path nondeterminism and prefix mapping."),
    src("reprotest", "reprotest", "Reproducible Builds", "https://salsa.debian.org/reproducible-builds/reprotest", "official_documentation", 2026, "Varying build environments to test reproducibility."),
    src("nix-store", "Nix Reference Manual: Store", "NixOS Foundation", "https://nix.dev/manual/nix/latest/store/", "official_documentation", 2026, "Content-addressed/derivation-addressed immutable store semantics."),
    src("nix-derivations", "Nix Reference Manual: Derivations", "NixOS Foundation", "https://nix.dev/manual/nix/latest/language/derivations", "official_documentation", 2026, "Build inputs and outputs described as derivations."),
    src("nix-repro", "NixOS Reproducible Builds", "NixOS Foundation", "https://reproducible.nixos.org/", "official_documentation", 2026, "Independent rebuild checks and remaining nondeterminism."),
    src("bazel-hermeticity", "Bazel: Hermeticity", "Bazel", "https://bazel.build/basics/hermeticity", "official_documentation", 2026, "Hermetic action inputs and build environment isolation."),
    src("bazel-remote-cache", "Bazel: Remote caching", "Bazel", "https://bazel.build/remote/caching", "official_documentation", 2026, "Action cache and content-addressable cache behavior."),
    src("bazel-platforms", "Bazel: Platforms", "Bazel", "https://bazel.build/extending/platforms", "official_documentation", 2026, "Constraint-based target and execution platform selection."),
    src("bazel-build-encyclopedia", "Bazel Build Encyclopedia", "Bazel", "https://bazel.build/reference/be/overview", "official_documentation", 2026, "Rules, attributes, targets, actions and outputs."),
    src("bzlmod", "Bazel external dependencies: Bzlmod", "Bazel", "https://bazel.build/external/overview", "official_documentation", 2026, "Module dependency resolution and lockfile mechanisms."),
    src("reapi", "Remote Execution API", "Bazel Remote APIs", "https://github.com/bazelbuild/remote-apis/blob/main/build/bazel/remote/execution/v2/remote_execution.proto", "open_specification", 2026, "Canonical action digests, CAS, action cache and remote execution."),
    src("oci-image", "OCI Image Format Specification", "Open Container Initiative", "https://github.com/opencontainers/image-spec/blob/main/spec.md", "open_specification", 2026, "Image manifests, indexes, configurations and filesystem layers."),
    src("oci-distribution", "OCI Distribution Specification", "Open Container Initiative", "https://github.com/opencontainers/distribution-spec/blob/main/spec.md", "open_specification", 2026, "Registry pull, push, content discovery and digest semantics."),
    src("oci-runtime", "OCI Runtime Specification", "Open Container Initiative", "https://github.com/opencontainers/runtime-spec/blob/main/spec.md", "open_specification", 2026, "Runtime bundle and lifecycle of a container occurrence."),
    src("oci-referrers", "OCI Distribution Referrers API", "Open Container Initiative", "https://github.com/opencontainers/distribution-spec/blob/main/spec.md#listing-referrers", "open_specification", 2026, "Discovering artifacts that refer to a digest-addressed subject."),
    src("wasm-core", "WebAssembly Core Specification 3.0", "W3C WebAssembly Community Group", "https://www.w3.org/TR/wasm-core-3/", "open_specification", 2025, "Core WebAssembly validation and execution semantics."),
    src("wasm-component", "WebAssembly Component Model", "Bytecode Alliance", "https://github.com/WebAssembly/component-model/tree/main/design/mvp", "open_specification", 2026, "Component types, composition and canonical ABI design."),
    src("wit", "WebAssembly Interface Types", "Bytecode Alliance", "https://component-model.bytecodealliance.org/design/wit.html", "official_documentation", 2026, "WIT packages, worlds, interfaces and resource types."),
    src("canonical-abi", "Component Model Canonical ABI", "Bytecode Alliance", "https://github.com/WebAssembly/component-model/blob/main/design/mvp/CanonicalABI.md", "open_specification", 2026, "Canonical lifting/lowering between component values and core Wasm."),
    src("wasi-02", "WASI 0.2", "Bytecode Alliance", "https://wasi.dev/interfaces", "open_specification", 2024, "WASI 0.2 interfaces published as WIT packages."),
    src("wasi-cli", "WASI CLI command world", "WebAssembly/WASI", "https://github.com/WebAssembly/wasi-cli", "open_specification", 2026, "CLI-oriented WASI world and interfaces."),
    src("sysv-abi", "System V ABI AMD64 Architecture Processor Supplement", "x86-64 psABI", "https://gitlab.com/x86-psABIs/x86-64-ABI", "open_specification", 2025, "AMD64 calling convention, data layout and object conventions."),
    src("itanium-cxx-abi", "Itanium C++ ABI", "Itanium C++ ABI Group", "https://itanium-cxx-abi.github.io/cxx-abi/abi.html", "open_specification", 2025, "C++ object model, mangling and exception ABI."),
    src("pe-coff", "PE/COFF Specification", "Microsoft", "https://learn.microsoft.com/en-us/windows/win32/debug/pe-format", "official_documentation", 2025, "Windows image and object file format."),
    src("k8s-api-conventions", "Kubernetes API Conventions", "Kubernetes", "https://github.com/kubernetes/community/blob/master/contributors/devel/sig-architecture/api-conventions.md", "open_specification", 2026, "Kubernetes object identity, spec/status and API evolution conventions."),
    src("k8s-deployment", "Kubernetes Deployments", "Kubernetes", "https://kubernetes.io/docs/concepts/workloads/controllers/deployment/", "official_documentation", 2026, "Deployment rollout and rollback behavior."),
    src("k8s-statefulset", "Kubernetes StatefulSets", "Kubernetes", "https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/", "official_documentation", 2026, "Stable identity and ordered stateful workload management."),
    src("k8s-job", "Kubernetes Jobs", "Kubernetes", "https://kubernetes.io/docs/concepts/workloads/controllers/job/", "official_documentation", 2026, "Run-to-completion workload semantics."),
    src("k8s-crd", "Kubernetes Custom Resources", "Kubernetes", "https://kubernetes.io/docs/concepts/extend-kubernetes/api-extension/custom-resources/", "official_documentation", 2026, "CRD schemas, versions and controllers."),
    src("k8s-ssa", "Kubernetes Server-Side Apply", "Kubernetes", "https://kubernetes.io/docs/reference/using-api/server-side-apply/", "official_documentation", 2026, "Declarative field ownership and conflict detection."),
    src("k8s-images", "Kubernetes Images", "Kubernetes", "https://kubernetes.io/docs/concepts/containers/images/", "official_documentation", 2026, "Image names, tags, digests and pull policy."),
    src("helm-charts", "Helm Chart Best Practices", "Helm", "https://helm.sh/docs/chart_best_practices/", "official_documentation", 2026, "Chart structure, values, templates and version conventions."),
    src("kustomize", "Kustomize", "Kubernetes SIG CLI", "https://kubectl.docs.kubernetes.io/references/kustomize/kustomization/", "official_documentation", 2026, "Declarative Kubernetes resource composition and transforms."),
    src("openapi311", "OpenAPI Specification 3.1.1", "OpenAPI Initiative", "https://spec.openapis.org/oas/v3.1.1.html", "open_specification", 2024, "HTTP API description and schema contracts."),
    src("asyncapi3", "AsyncAPI Specification 3.0.0", "AsyncAPI Initiative", "https://www.asyncapi.com/docs/reference/specification/v3.0.0", "open_specification", 2023, "Asynchronous API channels, operations and messages."),
    src("json-schema-core", "JSON Schema Core 2020-12", "JSON Schema", "https://json-schema.org/draft/2020-12/json-schema-core", "open_specification", 2022, "Schema resources, vocabularies, references and evaluation."),
    src("json-schema-validation", "JSON Schema Validation 2020-12", "JSON Schema", "https://json-schema.org/draft/2020-12/json-schema-validation", "open_specification", 2022, "Validation assertion and annotation vocabularies."),
    src("protobuf", "Protocol Buffers Language Guide", "Google", "https://protobuf.dev/programming-guides/proto3/", "official_documentation", 2026, "Protocol Buffer message declarations and evolution rules."),
    src("protoc-plugin", "Protocol Compiler Plugin API", "Google", "https://protobuf.dev/reference/cpp/api-docs/google.protobuf.compiler.plugin.pb", "open_specification", 2026, "protoc request/response protocol for code generators."),
    src("protobuf-editions", "Protocol Buffers Editions", "Google", "https://protobuf.dev/editions/overview/", "official_documentation", 2026, "Edition-based feature evolution for protobuf schemas."),
    src("grpc", "gRPC Core Concepts", "gRPC Authors", "https://grpc.io/docs/what-is-grpc/core-concepts/", "official_documentation", 2026, "Generated service/client contracts over protobuf."),
    src("buf-breaking", "Buf breaking change detection", "Buf", "https://buf.build/docs/breaking/", "official_documentation", 2026, "Configurable protobuf compatibility checks."),
    src("graphql", "GraphQL Specification", "GraphQL Foundation", "https://spec.graphql.org/October2021/", "open_specification", 2021, "GraphQL schema, validation and execution semantics."),
    src("typespec", "TypeSpec Emitters", "Microsoft", "https://typespec.io/docs/extending-typespec/emitter-basics/", "official_documentation", 2026, "Typed model traversal and target-specific emitters."),
    src("postgres-ddl", "PostgreSQL Explicit Locking", "PostgreSQL Global Development Group", "https://www.postgresql.org/docs/current/explicit-locking.html", "official_documentation", 2026, "DDL lock behavior relevant to migration planning."),
    src("flyway", "Flyway Migrations", "Redgate", "https://documentation.red-gate.com/flyway/flyway-concepts/migrations", "official_documentation", 2026, "Versioned and repeatable database migration execution."),
    src("liquibase", "Liquibase Changelog", "Liquibase", "https://docs.liquibase.com/concepts/changelogs/home.html", "official_documentation", 2026, "Ordered database change sets and checksums."),
    src("terraform-providers", "Terraform Provider Requirements", "HashiCorp", "https://developer.hashicorp.com/terraform/language/providers/requirements", "official_documentation", 2026, "Provider source addresses and version constraints."),
    src("terraform-lock", "Terraform Dependency Lock File", "HashiCorp", "https://developer.hashicorp.com/terraform/language/files/dependency-lock", "official_documentation", 2026, "Selected provider versions and checksums."),
    src("terraform-json", "Terraform JSON Output Format", "HashiCorp", "https://developer.hashicorp.com/terraform/internals/json-format", "official_documentation", 2026, "Machine-readable plans, state and values."),
    src("buildpacks", "Cloud Native Buildpacks Specification", "Cloud Native Buildpacks", "https://github.com/buildpacks/spec", "open_specification", 2026, "Buildpack lifecycle, build plan and OCI image outputs."),
    src("github-attestations", "GitHub Artifact Attestations", "GitHub", "https://docs.github.com/en/actions/security-for-github-actions/using-artifact-attestations", "official_documentation", 2026, "Workflow identity backed artifact attestations."),
    src("osv", "Open Source Vulnerability Schema", "OpenSSF", "https://ossf.github.io/osv-schema/", "open_specification", 2026, "Machine-readable vulnerability ranges and affected packages."),
    src("rustsec", "RustSec Advisory Database", "RustSec", "https://github.com/RustSec/advisory-db", "official_documentation", 2026, "Rust package vulnerability and informational advisories."),
    src("pypa-wheel", "Binary distribution format", "Python Packaging Authority", "https://packaging.python.org/en/latest/specifications/binary-distribution-format/", "open_specification", 2025, "Python wheel archive, tags and metadata."),
    src("npm-lock", "package-lock.json", "npm", "https://docs.npmjs.com/cli/v11/configuring-npm/package-lock-json", "official_documentation", 2025, "Concrete npm dependency tree and integrity metadata."),
    src("go-modules", "Go Modules Reference", "Go Project", "https://go.dev/ref/mod", "official_documentation", 2026, "Go module graph, version selection and checksums."),
    src("cmake-cross", "CMake Cross Compiling", "Kitware", "https://cmake.org/cmake/help/latest/manual/cmake-toolchains.7.html#cross-compiling", "official_documentation", 2026, "CMake toolchain files and host/target distinction."),
    src("meson-cross", "Meson Cross Compilation", "Meson", "https://mesonbuild.com/Cross-compilation.html", "official_documentation", 2026, "Meson build-machine, host-machine and target-machine configuration."),
    src("build-systems-carte", "Build Systems à la Carte", "Mokhov, Mitchell, Peyton Jones", "https://www.microsoft.com/en-us/research/uploads/prod/2018/03/build-systems.pdf", "original_research", 2018, "A formal decomposition of build systems by dependency discovery, scheduling and rebuilding."),
    src("shake-paper", "Shake Before Building", "Mitchell", "https://www.microsoft.com/en-us/research/wp-content/uploads/2016/03/shake.pdf", "original_research", 2012, "Dependency-tracking build semantics and incremental execution."),
    src("pluto-paper", "Pluto: Incremental Build System", "Erdweg et al.", "https://pluto-build.github.io/pluto/", "original_research", 2015, "Dynamic dependency tracking and sound incremental rebuilding."),
    src("nix-thesis", "The Purely Functional Software Deployment Model", "Dolstra", "https://edolstra.github.io/pubs/phd-thesis.pdf", "original_research", 2006, "Store paths and pure build functions for deployment."),
    src("trusting-trust", "Reflections on Trusting Trust", "Ken Thompson / ACM", "https://www.cs.cmu.edu/~rdriley/487/papers/Thompson_1984_ReflectionsonTrustingTrust.pdf", "original_research", 1984, "Compiler bootstrap trust attack and limits of source inspection."),
    src("bazel-paper", "Build Systems and Build Correctness", "Google Research", "https://research.google/pubs/build-systems-and-build-correctness/", "original_research", 2015, "Build correctness through declared dependencies and hermetic actions."),
    src("schema-facebook", "Schema Evolution in a Scale-out Data Store", "Facebook / VLDB", "https://www.vldb.org/pvldb/vol8/p1816-sheng.pdf", "original_research", 2015, "Large-scale database schema evolution mechanisms and operational constraints."),
    src("online-schema", "Online, Asynchronous Schema Change in F1", "Google / VLDB", "https://research.google/pubs/online-asynchronous-schema-change-in-f1/", "original_research", 2013, "Multi-version asynchronous schema change protocols."),
    src("repro-science", "Reproducible Builds: Increasing the Integrity of Software Supply Chains", "Lamb and Zacchiroli", "https://arxiv.org/abs/2104.06020", "original_research", 2021, "Threat model and ecosystem survey for reproducible builds."),
]


# slug, name, phase, purpose, primary source keys, two capabilities, two operations,
# explicit decision, pass transformation, principal artifact kind
CONTEXT_SEEDS = [
    ("target_contract", "Target Contract", "backend", "Own the declared machine, OS, environment, object format and support-tier requirements before selecting a backend.", ["rustc-targets", "rust-platform-support", "bazel-platforms"], ["declare target tuple", "qualify target support"], ["normalize target request", "validate target contract"], "Which target triple, support tier and runtime assumptions are authoritative?", "TypedTargetIntent -> TargetContract", "target-contract"),
    ("backend_selection", "Backend Selection", "backend", "Match typed IR semantics and target contracts to a qualified backend offer without selecting by tool name.", ["rustc-codegen", "typespec", "wasm-core"], ["advertise backend semantics", "bind backend offer"], ["enumerate backend offers", "select compatible backend"], "Which backend semantics and evidence threshold are required?", "TypedIR + TargetContract -> BackendBinding", "backend-binding"),
    ("target_feature", "Target Feature Negotiation", "backend", "Resolve CPU and platform feature requirements independently of target naming.", ["rustc-codegen", "bazel-platforms"], ["declare feature floor", "check feature closure"], ["resolve target features", "refuse unsafe feature mismatch"], "Are CPU features a minimum, exact set, or optimization-only preference?", "BackendBinding -> FeatureQualifiedBackend", "target-feature-set"),
    ("ir_backend_translation", "IR-to-Backend Translation", "backend", "Translate already-lowered typed IR into backend-specific machine or source structures while preserving declared semantics.", ["rustc-codegen", "wasm-core"], ["map backend types", "lower backend instructions"], ["translate typed node", "verify backend mapping"], "Which backend constructs faithfully implement each already-lowered IR operation?", "TypedIR -> BackendIR", "backend-ir"),
    ("native_codegen", "Native Machine Code Generation", "emission", "Emit target-specific object code from backend IR with explicit relocation, panic and optimization choices.", ["rustc-codegen", "sysv-abi", "pe-coff"], ["emit object sections", "configure code model"], ["compile backend module", "inspect object contract"], "Which relocation, code, panic, debug and optimization models apply?", "BackendIR -> NativeObject", "native-object"),
    ("wasm_core_codegen", "WebAssembly Core Generation", "emission", "Emit and validate core WebAssembly modules without conflating them with components.", ["wasm-core", "rustc-targets"], ["emit wasm module", "validate core module"], ["encode core wasm", "validate wasm bytes"], "Which proposal features and import/export surface are permitted?", "BackendIR -> CoreWasmModule", "wasm-core-module"),
    ("wasm_component_codegen", "WebAssembly Component Generation", "emission", "Lift core modules into typed components with WIT worlds and canonical ABI adapters.", ["wasm-component", "wit", "canonical-abi", "wasi-02"], ["compose component", "bind WIT world"], ["componentize module", "validate component types"], "Which WIT world, package version and canonical ABI options apply?", "CoreWasmModule + WITWorld -> WasmComponent", "wasm-component"),
    ("abi_ffi", "ABI and FFI Boundary", "emission", "Own calling convention, layout, symbol, ownership and unwind contracts across language boundaries.", ["rust-reference-abi", "rust-ffi", "sysv-abi", "itanium-cxx-abi"], ["declare foreign ABI", "verify layout contract"], ["generate binding shim", "run ABI conformance probe"], "Which ABI, ownership and unwind rules are binding at each foreign edge?", "ForeignInterface -> ABIShim", "ffi-binding"),
    ("source_ast", "Source AST Emission", "emission", "Construct target-language syntax trees before serialization so syntax and text formatting remain separable.", ["typespec", "protoc-plugin"], ["construct typed syntax tree", "preserve source mapping"], ["emit language AST", "validate emitted AST"], "Which language edition and syntax feature set constrain the AST?", "BackendIR -> SourceAST", "source-ast"),
    ("source_template", "Source Template Expansion", "emission", "Expand declared templates into source fragments while retaining template identity and parameters.", ["helm-charts", "typespec"], ["bind template parameters", "trace template expansion"], ["expand source template", "validate parameter completeness"], "Are templates logic-free, hygienic and version-pinned?", "Template + Parameters -> SourceASTFragment", "source-template"),
    ("generated_source", "Generated Source Ownership", "emission", "Own generated source identity, overwrite policy, protected regions and regeneration provenance.", ["protoc-plugin", "typespec", "cargo-build-scripts"], ["mark generated ownership", "detect manual divergence"], ["materialize generated source", "reconcile regeneration"], "May generated files be edited, checked in, or overwritten?", "SourceAST -> GeneratedSource", "generated-source"),
    ("deterministic_format", "Deterministic Formatting", "emission", "Serialize source and manifests canonically with pinned formatter semantics.", ["repro-definition", "source-date-epoch", "json-schema-core"], ["canonicalize text", "pin formatter profile"], ["format generated text", "compare canonical bytes"], "Which formatter version, line ending, ordering and encoding are normative?", "GeneratedText -> CanonicalGeneratedText", "format-receipt"),
    ("source_map_debug", "Source Map and Debug Metadata", "emission", "Relate generated and compiled locations to IR and source identities without polluting semantic identity.", ["rustc-codegen", "repro-build-path"], ["emit debug mapping", "redact build paths"], ["construct source map", "verify path remapping"], "Which debug detail and path-remapping policy applies?", "EmissionTrace -> DebugMetadata", "debug-metadata"),
    ("build_graph", "Build Graph", "build", "Own actions, declared inputs, dependencies, outputs and ordering independently of dependency version selection.", ["bazel-build-encyclopedia", "build-systems-carte", "shake-paper"], ["construct action graph", "detect dependency cycles"], ["plan build actions", "topologically schedule actions"], "Are dependencies static, dynamic, traced, or discovered in phases?", "BuildIntent -> BuildGraph", "build-graph"),
    ("invalidation", "Action Key and Invalidation", "build", "Compute change-sensitive action identities and conservative invalidation boundaries.", ["reapi", "pluto-paper", "shake-paper"], ["compute action key", "explain invalidation"], ["hash declared inputs", "invalidate dependent actions"], "Which semantic and incidental inputs participate in each action key?", "BuildAction -> ActionKey", "invalidation-explanation"),
    ("dependency_resolution", "Dependency Resolution", "resolution", "Select concrete package versions and sources before build execution.", ["cargo-resolver", "semver", "bzlmod", "go-modules"], ["solve version constraints", "lock dependency graph"], ["resolve dependency graph", "verify lock closure"], "Which resolver, registry universe, yanked policy and lock update mode apply?", "DependencyConstraints -> ResolvedDependencyGraph", "dependency-lock"),
    ("feature_resolution", "Feature Resolution", "resolution", "Resolve optional capabilities and target-conditioned edges without treating feature names as semantics.", ["cargo-features", "cargo-platform"], ["unify feature requests", "audit feature activation"], ["resolve feature closure", "explain activated feature"], "Which feature resolver and target partitions govern unification?", "FeatureRequests -> FeatureClosure", "feature-resolution"),
    ("toolchain_resolution", "Toolchain Resolution", "resolution", "Resolve exact compilers, linkers, formatters, generators and sysroots as build inputs.", ["cargo-config", "cmake-cross", "meson-cross"], ["pin toolchain closure", "qualify tool executable"], ["resolve toolchain", "verify toolchain digest"], "Which toolchain components, versions, digests and trust roots are required?", "ToolchainConstraints -> ToolchainClosure", "toolchain-lock"),
    ("cargo_workspace", "Rust and Cargo Workspace", "build", "Translate package/workspace intent into Cargo targets, profiles and graph queries.", ["cargo-manifest", "cargo-workspaces", "cargo-metadata", "cargo-profiles"], ["emit cargo manifests", "query cargo graph"], ["assemble cargo workspace", "inspect cargo metadata"], "Which workspace resolver, profile inheritance and target set apply?", "RustPackageIntent -> CargoWorkspace", "cargo-workspace"),
    ("cargo_build_script", "Cargo Build Script Boundary", "build", "Confine build.rs effects, declared rerun inputs and link directives.", ["cargo-build-scripts", "cargo-sbom"], ["declare build script inputs", "capture build script outputs"], ["execute build script sandboxed", "validate cargo directives"], "Which filesystem, environment, network and tool effects may build.rs observe?", "BuildScriptIntent -> BuildScriptAction", "build-script-receipt"),
    ("polyglot", "Polyglot Build Orchestration", "build", "Compose Rust, C/C++, Go, JavaScript and Python subgraphs without erasing their native resolution semantics.", ["cmake-cross", "meson-cross", "go-modules", "npm-lock", "pypa-wheel"], ["import foreign build graph", "bridge artifact edges"], ["plan polyglot build", "verify inter-tool dependencies"], "Which tool owns each dependency and action edge?", "PolyglotIntent -> FederatedBuildGraph", "polyglot-build-plan"),
    ("cross_compile", "Cross Compilation", "build", "Separate build, host and target platforms and qualify runnable tools for each.", ["rustc-targets", "cmake-cross", "meson-cross", "bazel-platforms"], ["classify platform roles", "select execution platform"], ["plan cross build", "probe target sysroot"], "Which binaries run during build and which run only on the target?", "BuildGraph + PlatformMatrix -> CrossBuildPlan", "cross-build-plan"),
    ("linking", "Linking and Binary Closure", "build", "Combine objects and libraries into an ABI-compatible loadable closure.", ["rust-reference-linkage", "rust-lto", "sysv-abi", "pe-coff"], ["resolve symbols", "construct link line"], ["link artifact", "inspect dynamic closure"], "Which linker, library order, symbol visibility, runtime and LTO contract apply?", "Objects + LinkContract -> LinkedBinary", "linked-binary"),
    ("package_assembly", "Package Assembly", "packaging", "Assemble compiled and generated materials into an ecosystem package without treating it as deployment state.", ["cargo-package", "pypa-wheel", "oci-image"], ["assemble package payload", "verify package contents"], ["stage package", "seal package archive"], "Which files, metadata, permissions and normalization rules belong in the package?", "Artifacts + PackageMetadata -> Package", "package"),
    ("package_metadata", "Package Metadata and Versioning", "packaging", "Own package identity, version, dependency declarations and compatibility claims.", ["semver", "cargo-semver", "cargo-manifest"], ["assign package version", "classify public change"], ["derive package metadata", "check version policy"], "What compatibility promise does the version encode for each consumer surface?", "PublicSurfaceDelta -> PackageVersion", "package-metadata"),
    ("schema_generation", "Schema Generation", "generation", "Emit schemas from typed contracts while preserving vocabulary and dialect decisions.", ["json-schema-core", "json-schema-validation", "protobuf", "openapi311"], ["emit schema dialect", "track schema provenance"], ["generate schema", "validate schema artifact"], "Which schema dialect, edition, identifiers and compatibility policy apply?", "TypedContract -> SchemaArtifact", "schema"),
    ("client_generation", "Client and SDK Generation", "generation", "Generate clients and servers from API contracts with target-language policy explicit.", ["openapi311", "asyncapi3", "protoc-plugin", "grpc", "typespec"], ["emit client surface", "map transport errors"], ["generate client SDK", "compile generated client"], "Which operations, auth hooks, nullability and error model are exposed?", "APIContract -> ClientSource", "client-sdk"),
    ("database_migration", "Database Migration Generation", "generation", "Plan forward, compatibility-window and reversal operations separately from schema declarations.", ["postgres-ddl", "flyway", "liquibase", "schema-facebook", "online-schema"], ["plan expand contract", "classify migration reversibility"], ["generate migration plan", "verify migration preconditions"], "Is rollback logically and operationally safe after data transformation?", "SchemaDelta -> MigrationPlan", "database-migration"),
    ("pipeline_manifest", "Pipeline Manifest Generation", "generation", "Emit pipeline definitions from typed plans while retaining execution-engine decisions.", ["json-schema-core", "build-systems-carte"], ["emit pipeline topology", "bind task artifacts"], ["generate pipeline manifest", "validate pipeline graph"], "Which engine API, retry, checkpoint and state semantics apply?", "TypedPipelinePlan -> PipelineManifest", "pipeline-manifest"),
    ("config_manifest", "Configuration Manifest Generation", "generation", "Emit configuration schemas and instances with secret references and environment overlays explicit.", ["json-schema-validation", "kustomize", "helm-charts"], ["emit config schema", "compose configuration overlays"], ["generate config manifest", "validate config instance"], "Which values are compile-time, deploy-time, runtime, secret or mutable?", "ConfigIntent -> ConfigManifest", "config-manifest"),
    ("infra_manifest", "Infrastructure Manifest Generation", "generation", "Emit infrastructure intent and provider constraints separately from applied infrastructure state.", ["terraform-providers", "terraform-lock", "terraform-json"], ["emit infrastructure intent", "lock infrastructure providers"], ["generate infrastructure module", "inspect infrastructure plan"], "Which provider versions and lifecycle policies are authorized?", "InfrastructureIntent -> InfrastructureManifest", "infra-manifest"),
    ("deployment_manifest", "Deployment Manifest Generation", "deployment", "Emit controller input that references immutable packages and explicit runtime policy.", ["k8s-api-conventions", "k8s-deployment", "k8s-images", "helm-charts"], ["emit workload specification", "pin deployable digest"], ["generate deployment manifest", "server-side dry run"], "Which controller API version, rollout strategy and artifact digest apply?", "DeployIntent + PackageDigest -> DeploymentManifest", "deployment-manifest"),
    ("test_generation", "Test Generation", "assurance", "Generate bounded conformance tests from typed obligations without claiming exhaustive correctness.", ["json-schema-validation", "buf-breaking", "cargo-semver"], ["derive conformance cases", "trace test obligation"], ["generate test case", "execute generated test"], "Which obligations are decidable by generated tests and which need other evidence?", "ProofObligations -> TestSuite", "test-suite"),
    ("oracle_fixture", "Oracle and Fixture Management", "assurance", "Version expected outcomes, golden bytes and fixtures independently of test executors.", ["reprotest", "repro-definition"], ["version golden oracle", "minimize fixture"], ["materialize fixture", "compare oracle outcome"], "Is the oracle normative, differential, metamorphic or observational?", "TestCase -> OracleFixture", "oracle-fixture"),
    ("documentation", "Documentation Generation", "generation", "Generate reference documentation from the same typed surfaces while distinguishing explanatory prose from executable contracts.", ["openapi311", "protobuf", "cargo-manifest"], ["emit reference docs", "trace documentation source"], ["generate documentation", "check documentation links"], "Which contract is normative when documentation and schemas disagree?", "TypedSurface -> Documentation", "documentation"),
    ("license", "License Compliance", "supply_chain", "Inventory declared and detected licenses, notices and policy decisions without inferring legal truth from an identifier.", ["spdx3", "spdx-license-list", "cargo-package"], ["collect license evidence", "evaluate license policy"], ["generate notice bundle", "record license disposition"], "Which policy and legal authority adjudicate ambiguous or conflicting licenses?", "DependencyClosure -> LicenseReport", "license-report"),
    ("advisory", "Vulnerability and Advisory Evaluation", "supply_chain", "Match advisories to versioned package occurrences with affected-range and remediation evidence explicit.", ["osv", "rustsec", "spdx3"], ["ingest advisory", "match affected occurrence"], ["scan dependency closure", "record advisory disposition"], "Which advisory sources, severity policy and exception authority apply?", "SBOM + Advisories -> VulnerabilityReport", "vulnerability-report"),
    ("sbom", "Software Bill of Materials", "supply_chain", "Describe the artifact's component and dependency inventory without claiming how it was built.", ["spdx3", "cyclonedx16", "cargo-sbom"], ["enumerate components", "serialize BOM"], ["construct SBOM", "validate SBOM references"], "Which BOM model, granularity and dependency completeness are required?", "ArtifactClosure -> SBOM", "sbom"),
    ("provenance", "Build Provenance and Attestation", "supply_chain", "Bind artifact subjects to declared build inputs, builder identity and process claims.", ["slsa-provenance", "slsa-build-track", "in-toto-attestation", "dsse"], ["construct provenance predicate", "bind attestation subject"], ["emit provenance statement", "verify attestation envelope"], "Which predicate, builder identity and verification policy support the claim?", "BuildReceipt -> ProvenanceAttestation", "provenance-attestation"),
    ("signing_identity", "Signing Identity and Transparency", "supply_chain", "Authenticate who signed a statement and record transparency evidence without equating identity with claim truth.", ["sigstore-architecture", "sigstore-bundle", "cosign", "rekor", "fulcio"], ["bind signing identity", "verify transparency inclusion"], ["sign artifact statement", "verify signature bundle"], "Which identity issuer, subject, key policy and transparency log are trusted?", "Statement -> SignedEnvelope", "signature-bundle"),
    ("hermetic_build", "Hermetic Build Environment", "build", "Restrict actions to declared tool, file, environment, clock, randomness and network inputs.", ["bazel-hermeticity", "nix-derivations", "bazel-paper"], ["declare action environment", "enforce input isolation"], ["sandbox build action", "audit undeclared access"], "Which ambient inputs are prohibited, virtualized or declared?", "BuildAction -> HermeticAction", "hermeticity-receipt"),
    ("reproducible_build", "Reproducible Build Verification", "assurance", "Compare independent builds for bit identity while keeping semantic conformance as a separate obligation.", ["repro-definition", "source-date-epoch", "repro-build-path", "nix-repro", "repro-science"], ["normalize nondeterminism", "compare independent outputs"], ["rebuild independently", "produce reproducibility diff"], "Which environment variations and equivalence relation define reproduction?", "BuildRecipe -> ReproducibilityResult", "reproducibility-receipt"),
    ("cache", "Local and Remote Build Cache", "build", "Reuse action results only when action keys fully capture result-affecting inputs and trust policy permits.", ["bazel-remote-cache", "reapi"], ["publish cached result", "validate cache hit"], ["lookup action result", "quarantine poisoned key"], "Which namespace, digest function, trust domain and eviction policy apply?", "ActionKey -> CachedActionResult", "cache-receipt"),
    ("remote_execution", "Remote Build Execution", "build", "Execute canonical actions on qualified remote workers with explicit platform and isolation evidence.", ["reapi", "bazel-platforms", "bazel-hermeticity"], ["dispatch remote action", "qualify execution worker"], ["upload action closure", "verify remote result"], "Which worker platform, isolation, timeout and trust policy apply?", "HermeticAction -> RemoteActionResult", "remote-execution-receipt"),
    ("artifact_repository", "Artifact Repository", "distribution", "Store and retrieve immutable artifacts, metadata and referrers under digest and retention policies.", ["oci-distribution", "oci-referrers", "tuf"], ["publish immutable artifact", "resolve artifact reference"], ["push artifact", "verify repository retrieval"], "Are mutable tags admissible for selection, or only as discovery hints?", "Package -> RepositoryOccurrence", "repository-record"),
    ("release_channel", "Release Channel", "release", "Bind immutable artifacts to named audiences and promotion policies without copying identity into tags.", ["tuf", "oci-distribution", "semver"], ["define release channel", "promote artifact digest"], ["stage release candidate", "publish channel metadata"], "Which evidence gates and authorities permit channel promotion?", "ArtifactDigest + Evidence -> ChannelAssignment", "release-channel-record"),
    ("rollout", "Rollout and Promotion", "deployment", "Create a running occurrence from a deployment manifest under progressive exposure and health gates.", ["k8s-deployment", "k8s-ssa", "k8s-images"], ["start rollout", "evaluate rollout gate"], ["apply deployment manifest", "promote rollout stage"], "Which observations, windows and authority advance or halt rollout?", "DeploymentManifest -> RunningOccurrence", "rollout-receipt"),
    ("rollback_artifact", "Artifact Rollback Strategy", "release", "Select a previously qualified immutable artifact and deployment description for redeployment.", ["k8s-deployment", "tuf", "oci-distribution"], ["select prior artifact", "validate rollback eligibility"], ["prepare artifact rollback", "redeploy prior artifact"], "Which prior digest remains compatible with current state and dependencies?", "ReleaseHistory -> RollbackDeployment", "rollback-artifact-plan"),
    ("state_rollback", "State Rollback and Roll-forward", "release", "Plan data/state compatibility, compensations and forward repair separately from artifact rollback.", ["flyway", "liquibase", "schema-facebook", "online-schema"], ["assess state reversibility", "plan roll-forward repair"], ["generate state recovery plan", "verify compatibility window"], "Can transformed state be reversed without loss, or must recovery roll forward?", "StateDelta + ReleaseHistory -> StateRecoveryPlan", "state-recovery-plan"),
    ("decommission", "Decommission and Retention", "release", "Retire running occurrences, channels and artifacts only after dependency, evidence and retention checks.", ["tuf", "oci-distribution", "k8s-api-conventions"], ["discover live references", "enforce retention hold"], ["plan decommission", "issue tombstone receipt"], "Which consumers, legal holds and rollback windows prevent deletion?", "OccurrenceGraph -> DecommissionPlan", "decommission-receipt"),
    ("evidence_receipt", "Build and Release Evidence Receipts", "assurance", "Issue scoped evidence about transformations, checks and effects without promoting evidence into truth automatically.", ["in-toto-attestation", "slsa-provenance", "sigstore-bundle", "spdx3"], ["issue scoped receipt", "verify receipt chain"], ["collect phase receipts", "evaluate evidence policy"], "Which claim, subject, producer, method, time and limitations does each receipt bind?", "PhaseResults -> EvidenceBundle", "evidence-bundle"),
]


DISTINCTION_LAWS = [
    ("lowering-vs-codegen", "non_collapse", "Typed IR lowering chooses semantic operations and representations; code generation begins only when backend/target encodings are selected.", "Reject a backend pass that silently changes already-lowered semantics.", "CGB_LOWERING_CODEGEN_COLLAPSE", ["rustc-codegen", "wasm-core"]),
    ("template-vs-generated-source", "non_collapse", "A source template is a parameterized generator input; generated source is a materialized output with its own digest and provenance.", "Record both template and generated-source identities.", "CGB_TEMPLATE_SOURCE_COLLAPSE", ["protoc-plugin", "typespec"]),
    ("generated-source-vs-binary", "non_collapse", "Generated source is not a compiled object, binary, package or runtime occurrence.", "Require a compilation receipt before relating generated source to compiled artifacts.", "CGB_SOURCE_BINARY_COLLAPSE", ["rust-reference-linkage"]),
    ("package-vs-manifest", "non_collapse", "A package contains distributable material; a deployment manifest declares desired controller input.", "Give each distinct identity, version and digest fields.", "CGB_PACKAGE_MANIFEST_COLLAPSE", ["oci-image", "k8s-deployment"]),
    ("manifest-vs-occurrence", "non_collapse", "A deployment manifest is not proof that a running occurrence exists or matches desired state.", "Require controller/runtime observation receipts.", "CGB_MANIFEST_OCCURRENCE_COLLAPSE", ["k8s-api-conventions", "oci-runtime"]),
    ("resolution-vs-execution", "non_collapse", "Dependency resolution selects a concrete graph; build execution performs actions over that graph.", "Persist the resolved graph independently of build action results.", "CGB_RESOLUTION_EXECUTION_COLLAPSE", ["cargo-resolver", "build-systems-carte"]),
    ("reproducibility-vs-conformance", "non_collapse", "Bit-for-bit reproducibility shows equality under tested rebuild conditions; it does not prove semantic correctness or contract conformance.", "Track reproducibility and conformance verdicts independently.", "CGB_REPRO_CONFORMANCE_COLLAPSE", ["repro-definition", "repro-science"]),
    ("sbom-vs-provenance", "non_collapse", "An SBOM inventories components and relationships; provenance claims how a subject was produced from inputs by a builder.", "Never satisfy a provenance obligation with an SBOM or vice versa.", "CGB_SBOM_PROVENANCE_COLLAPSE", ["spdx3", "cyclonedx16", "slsa-provenance"]),
    ("signature-vs-truth", "non_collapse", "A valid signature authenticates a signer and statement bytes under a trust policy; it does not establish that the signed claim is true.", "Evaluate claim evidence after signature verification.", "CGB_SIGNATURE_TRUTH_COLLAPSE", ["dsse", "sigstore-architecture"]),
    ("rollback-artifact-vs-state", "non_collapse", "Redeploying a prior artifact does not reverse database, queue, object-store or external side effects.", "Require an independent state compatibility or recovery plan.", "CGB_ARTIFACT_STATE_ROLLBACK_COLLAPSE", ["k8s-deployment", "online-schema"]),
    ("target-feature-subset", "compatibility", "Every required target feature must be supplied by the deployment CPU/runtime; optimization-only features may not become hidden requirements.", "Compare normalized required and offered feature sets.", "CGB_TARGET_FEATURE_MISSING", ["rustc-codegen"]),
    ("abi-exactness", "compatibility", "FFI compatibility requires matching calling convention, layout, symbol, ownership, unwind and runtime contracts, not merely matching type names.", "Discharge an ABI proof for every foreign edge.", "CGB_ABI_INCOMPATIBLE", ["rust-ffi", "sysv-abi", "itanium-cxx-abi"]),
    ("wasm-import-export", "compatibility", "A core Wasm consumer is compatible only when imports/exports and enabled proposals validate structurally and semantically.", "Run core validation and import resolution.", "CGB_WASM_INTERFACE_INCOMPATIBLE", ["wasm-core"]),
    ("component-world", "compatibility", "A component binding requires compatible WIT package/world identities and canonical ABI semantics.", "Resolve versioned WIT worlds before composition.", "CGB_COMPONENT_WORLD_INCOMPATIBLE", ["wasm-component", "wit", "canonical-abi"]),
    ("schema-consumer", "compatibility", "Schema compatibility is directional and consumer-specific; syntactic schema validity is insufficient.", "Evaluate the declared writer/reader or producer/consumer compatibility mode.", "CGB_SCHEMA_BREAKING_CHANGE", ["json-schema-core", "protobuf", "buf-breaking"]),
    ("semver-surface", "compatibility", "Version compatibility applies only to a named public surface and declared audience.", "Classify changes per surface before assigning a version.", "CGB_SEMVER_SURFACE_UNBOUND", ["semver", "cargo-semver"]),
    ("deployment-api-version", "compatibility", "A manifest must target an API version served by the destination and satisfy its schema/admission policy.", "Perform discovery and server-side validation before mutation.", "CGB_DEPLOYMENT_API_INCOMPATIBLE", ["k8s-api-conventions", "k8s-ssa"]),
    ("ir-digest-invalidation", "invalidation", "Any semantic typed-IR digest change invalidates every downstream backend action that consumes it.", "Include typed-IR digest in backend action keys.", "CGB_STALE_IR_CACHE", ["reapi", "pluto-paper"]),
    ("generator-version-invalidation", "invalidation", "Generator executable, version and configuration changes invalidate generated outputs even when input schemas are unchanged.", "Hash generator closure and decisions.", "CGB_STALE_GENERATOR_CACHE", ["reapi", "protoc-plugin"]),
    ("template-invalidation", "invalidation", "Template bytes, imports and bound parameters are distinct action-key inputs.", "Hash the full template closure.", "CGB_STALE_TEMPLATE_CACHE", ["bazel-hermeticity"]),
    ("dependency-lock-invalidation", "invalidation", "A resolved dependency graph or checksum change invalidates actions whose declared closure changes.", "Key actions by resolved identities and content digests.", "CGB_STALE_DEPENDENCY_CACHE", ["cargo-resolver", "npm-lock", "go-modules"]),
    ("feature-set-invalidation", "invalidation", "The normalized feature closure is an input even when source files are identical.", "Hash resolved features per target partition.", "CGB_STALE_FEATURE_CACHE", ["cargo-features"]),
    ("target-invalidation", "invalidation", "Target tuple, features, ABI and sysroot changes invalidate target artifacts.", "Hash the normalized target contract.", "CGB_STALE_TARGET_CACHE", ["rustc-targets", "cmake-cross"]),
    ("toolchain-invalidation", "invalidation", "Compiler, linker, formatter, generator and sysroot digests participate in action identity.", "Use content-addressed toolchain closures.", "CGB_STALE_TOOLCHAIN_CACHE", ["nix-derivations", "reapi"]),
    ("environment-invalidation", "invalidation", "Every allowed result-affecting environment variable must be declared and keyed; undeclared observation is a hermeticity failure.", "Provide a deny-by-default environment allowlist.", "CGB_UNDECLARED_ENVIRONMENT", ["bazel-hermeticity", "reapi"]),
    ("build-script-invalidation", "invalidation", "Build-script rerun declarations must conservatively cover all result-affecting reads.", "Trace or sandbox reads and compare them to declarations.", "CGB_BUILD_SCRIPT_UNDECLARED_INPUT", ["cargo-build-scripts"]),
    ("formatter-invalidation", "invalidation", "Formatter version and profile changes invalidate canonical generated text but need not invalidate pre-format AST identity.", "Keep AST and formatted-text keys separate.", "CGB_STALE_FORMAT_CACHE", ["repro-definition"]),
    ("schema-input-invalidation", "invalidation", "Transitive schema imports, dialect and generator options participate in generated client keys.", "Hash the resolved schema graph and generator contract.", "CGB_STALE_SCHEMA_CLIENT", ["json-schema-core", "protoc-plugin"]),
    ("cache-trust", "compatibility", "Matching action digests justify reuse only inside an accepted cache trust domain and digest policy.", "Verify result digests and cache namespace policy.", "CGB_CACHE_TRUST_REJECTED", ["reapi", "bazel-remote-cache"]),
    ("repository-digest", "compatibility", "Mutable repository tags may locate candidates but release and deployment identity must resolve to immutable digests.", "Persist and deploy the resolved digest.", "CGB_MUTABLE_TAG_AS_IDENTITY", ["oci-distribution", "k8s-images"]),
]


INNOVATION_SEEDS = [
    ("slsa-v1", 2023, "SLSA 1.0 stabilized provenance and the build track around artifact subjects and builders.", ["slsa-provenance", "slsa-build-track"]),
    ("slsa-v11", 2025, "SLSA 1.1 refined the specification while retaining typed provenance predicates.", ["slsa-provenance"]),
    ("in-toto-attestation-v12", 2026, "in-toto Attestation Framework 1.2 formalized layered statement, envelope and bundle evolution.", ["in-toto-attestation"]),
    ("sigstore-keyless", 2022, "Sigstore reached general availability for short-lived identity certificates plus transparency logging.", ["sigstore-architecture", "fulcio", "rekor"]),
    ("sigstore-bundles", 2024, "Sigstore bundles made verification material portable for offline and policy-driven verification.", ["sigstore-bundle"]),
    ("spdx3", 2024, "SPDX 3 introduced a modular object model spanning software and supply-chain relationships.", ["spdx3"]),
    ("cyclonedx16", 2024, "CycloneDX 1.6 expanded BOM modeling and evidence-oriented fields.", ["cyclonedx16"]),
    ("oci11", 2024, "OCI image and distribution 1.1 standardized artifact subject/referrer relationships.", ["oci-image", "oci-distribution", "oci-referrers"]),
    ("wasi02", 2024, "WASI 0.2 published component-model-native WIT interfaces.", ["wasi-02", "wit"]),
    ("rust-wasip2", 2024, "Rust added a wasm32-wasip2 target for components using WASI 0.2.", ["rust-wasip2"]),
    ("wasm-component-mvp", 2025, "Component-model tooling converged on typed composition and the canonical ABI MVP design.", ["wasm-component", "canonical-abi"]),
    ("wasm-core3", 2025, "WebAssembly Core 3.0 consolidated newer core language features in a W3C specification.", ["wasm-core"]),
    ("protobuf-editions", 2023, "Protocol Buffers Editions decoupled language feature evolution from proto2/proto3 syntax labels.", ["protobuf-editions"]),
    ("openapi311", 2024, "OpenAPI 3.1.1 clarified the 3.1 line and its JSON Schema relationship.", ["openapi311", "json-schema-core"]),
    ("asyncapi3", 2023, "AsyncAPI 3 separated operations from channels and refined reusable message structure.", ["asyncapi3"]),
    ("bzlmod-default", 2024, "Bzlmod became Bazel's default external dependency system with module resolution and lockfiles.", ["bzlmod"]),
    ("reapi-evolution", 2025, "Remote Execution API 2.x continued standardizing canonical actions, CAS and execution capability negotiation.", ["reapi"]),
    ("cargo-sparse", 2023, "Cargo made the sparse registry protocol the default for crates.io, changing registry transport without changing package identity.", ["cargo-config", "cargo-source-replacement"]),
    ("rust-2024", 2025, "The Rust 2024 edition made language-edition selection a concrete generated-source and toolchain input.", ["cargo-manifest", "rust-platform-support"]),
    ("cargo-sbom-precursor", 2025, "Cargo introduced unstable compiler-time SBOM precursor output, explicitly not a finished SBOM contract.", ["cargo-sbom", "spdx3"]),
    ("github-attestations", 2024, "GitHub Actions added artifact attestations backed by workflow identity and Sigstore infrastructure.", ["github-attestations", "sigstore-architecture"]),
    ("json-schema-bundling", 2022, "JSON Schema 2020-12 made schema resources, dynamic references and compound documents explicit generator concerns.", ["json-schema-core"]),
    ("k8s-ssa-stable", 2021, "Kubernetes server-side apply stabilized managed-field ownership and declarative conflict detection.", ["k8s-ssa"]),
    ("osv-ecosystem", 2021, "OSV established a package/ecosystem-aware machine-readable advisory schema and affected ranges.", ["osv"]),
    ("buildpacks-platform-api", 2022, "Cloud Native Buildpacks advanced a lifecycle contract that turns source plus buildpacks into OCI images with structured metadata.", ["buildpacks", "oci-image"]),
]


GAP_SEEDS = [
    ("enumeration-saturation", "No claim that all post-IR codegen/build contexts have been enumerated.", "independent domain and compiler review"),
    ("boundary-adjudication", "All context, aggregate and library seams remain candidates.", "formal split/merge and ownership adjudication"),
    ("source-freshness", "URLs and current-version statements were not independently archived or continuously freshness-checked.", "archival snapshot and scheduled source audit"),
    ("backend-conformance", "No native, source or Wasm backend has passed this atlas's offer qualification.", "backend-specific conformance suites"),
    ("rust-target-matrix", "Rust target-tier documentation does not prove every target/toolchain combination builds this corpus.", "per-target build and runtime matrix"),
    ("abi-layout-proof", "FFI layout and unwind proofs are specified but no ABI probe harness is implemented.", "cross-compiler ABI fixtures and probes"),
    ("component-compatibility", "WIT/component compatibility policy remains ecosystem- and consumer-specific.", "versioned component compatibility test corpus"),
    ("schema-semantics", "Cross-dialect semantic equivalence among OpenAPI, JSON Schema, protobuf and language types is unresolved.", "formal mapping and counterexample suite"),
    ("migration-reversibility", "Generated down migrations cannot generally recover discarded or transformed data.", "domain-specific backup, compensation and roll-forward policy"),
    ("build-script-tracing", "Portable complete tracing of build-script inputs is not implemented.", "sandbox adapters per supported OS"),
    ("hermetic-network", "The corpus specifies network denial but does not prove toolchains never embed network-dependent behavior.", "network namespace enforcement and audit"),
    ("reproducibility-coverage", "Reproducibility depends on varied independent rebuilds; one deterministic generator run is insufficient.", "multi-environment rebuild farm"),
    ("bootstrap-trust", "Pinned compiler digests do not solve compiler bootstrap or trusting-trust concerns.", "diverse double compilation or independently bootstrapped toolchains"),
    ("remote-worker-trust", "REAPI compatibility does not establish worker isolation or honesty.", "worker qualification, isolation evidence and result verification"),
    ("cache-poisoning", "Digest equality alone does not establish that an action key captured all inputs.", "action-key audits and cache trust segmentation"),
    ("sbom-completeness", "Source-, build- and binary-derived SBOM views can disagree and completeness is unproven.", "multi-view reconciliation with declared coverage"),
    ("license-legal", "SPDX identifiers and scanner output are not legal advice or final license adjudication.", "authorized legal review workflow"),
    ("advisory-lag", "Advisory absence is not proof of vulnerability absence and feeds may lag.", "multi-source monitoring and risk acceptance policy"),
    ("signer-truth", "Verified signing identity does not establish claim truth or authorization.", "claim-specific evidence and authorization policy"),
    ("release-health", "No universal rollout health threshold or observation window is defined.", "service-specific SLO and risk adjudication"),
    ("state-recovery", "Rollback compatibility cannot be inferred from artifact history alone.", "state inventory, backups, compatibility probes and rehearsal"),
    ("decommission-discovery", "Complete discovery of external consumers and legal holds is not proven.", "organization-specific dependency inventory and records policy"),
    ("artifact-retention", "Repository garbage collection semantics vary and may break referrer/evidence reachability.", "repository-specific retention qualification"),
    ("polyglot-locks", "Lockfile and checksum semantics differ across Cargo, Go, npm, Python and infrastructure tools.", "ecosystem-specific resolver adapters and normalized receipts"),
]


PROOF_SEEDS = [
    ("backend-semantic", "backend", "Backend mapping preserves every typed IR operation's declared law.", "mapping table plus conformance suite", "Does not prove performance or absence of compiler defects."),
    ("target-compatible", "backend", "Backend output requires no target feature absent from the declared deployment offer.", "feature-set subset check plus target probe", "Does not prove every deployed host reports truthfully."),
    ("emission-deterministic", "emission", "Identical generator closure and inputs emit identical bytes.", "repeat generation and digest comparison", "Does not prove semantic correctness."),
    ("generated-provenance", "emission", "Generated source identifies IR, generator, templates and decisions.", "reference and digest verification", "Does not make comments or headers cryptographic proof."),
    ("build-graph-complete", "build", "Every result-affecting action input is represented in the build graph.", "sandbox trace versus declaration", "Trace coverage is platform bounded."),
    ("dependency-locked", "resolution", "All selected dependencies have immutable identity and integrity material.", "resolver replay and checksum verification", "Does not prove dependency safety."),
    ("feature-explained", "resolution", "Every active feature has at least one requesting path.", "resolver activation-path report", "Does not prove feature semantics are compatible."),
    ("toolchain-pinned", "resolution", "All invoked toolchain components resolve to declared digests.", "execution trace against toolchain closure", "Does not solve bootstrap trust."),
    ("abi-conformant", "emission", "Foreign symbols, layouts and calling conventions match the declared ABI contract.", "compile/link probes and layout fixtures", "Does not prove memory ownership is used correctly at runtime."),
    ("package-complete", "packaging", "Package contains exactly the declared payload and metadata.", "archive manifest and digest verification", "Does not prove deployability."),
    ("schema-compatible", "generation", "A schema delta satisfies the chosen directional compatibility policy.", "dialect-specific compatibility checker", "Does not prove business-semantic compatibility."),
    ("migration-preconditions", "generation", "Migration preconditions and compatibility window hold for an identified state snapshot.", "dry run/probe against identified snapshot", "Does not guarantee later production state is unchanged."),
    ("tests-pass", "assurance", "Named generated tests produced recorded outcomes for identified inputs.", "test receipt and fixture digests", "Passing bounded tests is not proof of total correctness."),
    ("hermetic", "build", "A build action observed no undeclared inputs under the enforcing sandbox.", "sandbox access log and policy verdict", "Does not cover mechanisms invisible to the sandbox."),
    ("reproducible", "assurance", "Independent builds under declared variations produced identical artifact bytes.", "digest comparison across builders", "Does not prove semantic conformance or source correspondence by itself."),
    ("sbom-subject", "supply_chain", "An SBOM describes the artifact identified by its subject digest.", "subject digest and BOM reference verification", "Does not prove BOM completeness or build process."),
    ("provenance-subject", "supply_chain", "Provenance statement binds an artifact digest to declared materials and builder claim.", "attestation schema, signature and subject checks", "Does not prove builder claim truth without policy and platform evidence."),
    ("signing-identity", "supply_chain", "A verified identity signed the exact statement bytes under a trust policy.", "certificate/key, signature and transparency verification", "Does not prove statement truth or signer authorization."),
    ("repository-integrity", "distribution", "Retrieved artifact bytes match the selected immutable digest.", "client-side digest verification", "Does not prove tag freshness or artifact suitability."),
    ("release-authorized", "release", "Named authorities approved a digest for a channel after declared gates.", "policy evaluation over evidence bundle", "Does not prove runtime health."),
    ("rollout-observed", "deployment", "A controller reported a running occurrence for an identified manifest and artifact digest.", "controller and workload observation receipts", "Does not prove end-user correctness."),
    ("rollback-eligible", "release", "A prior artifact remains compatible with current declared interfaces and state window.", "compatibility checks and recovery rehearsal", "Does not reverse external side effects."),
    ("decommission-safe", "release", "No discovered live reference or retention hold blocks retirement.", "reference scan and authority approvals", "Discovery can be incomplete."),
]


NEGATIVE_FAILURES = [
    ("unknown-target", "target_contract", "target triple is syntactically valid but no qualified support offer exists", "CGB_TARGET_UNSUPPORTED"),
    ("cpu-feature-mismatch", "target_feature", "artifact requires +avx2 while deployment offer declares only baseline x86-64", "CGB_TARGET_FEATURE_MISSING"),
    ("abi-unwind-mismatch", "abi_ffi", "Rust unwinding may cross a C ABI boundary that forbids it", "CGB_ABI_INCOMPATIBLE"),
    ("undeclared-build-input", "cargo_build_script", "build.rs reads a generated header absent from rerun declarations and action inputs", "CGB_BUILD_SCRIPT_UNDECLARED_INPUT"),
    ("schema-breaking", "schema_generation", "protobuf field number is reused with incompatible meaning", "CGB_SCHEMA_BREAKING_CHANGE"),
    ("nondeterministic-time", "reproducible_build", "archive embeds ambient wall-clock time rather than declared SOURCE_DATE_EPOCH", "CGB_REPRODUCIBILITY_FAILED"),
    ("attestation-subject-mismatch", "provenance", "signed provenance subject digest differs from published artifact", "CGB_ATTESTATION_SUBJECT_MISMATCH"),
    ("tag-as-identity", "artifact_repository", "deployment records only mutable latest tag and not resolved digest", "CGB_MUTABLE_TAG_AS_IDENTITY"),
    ("artifact-only-rollback", "rollback_artifact", "prior binary is selected after an irreversible destructive migration without state recovery plan", "CGB_ARTIFACT_STATE_ROLLBACK_COLLAPSE"),
]


def sid(keys: list[str]) -> list[str]:
    return [f"cgb.source.{key}" for key in keys]


def cid(slug: str) -> str:
    return f"cgb.context.{slug}"


def generated_records() -> dict[str, list[dict[str, Any]]]:
    contexts: list[dict[str, Any]] = []
    capabilities: list[dict[str, Any]] = []
    operations: list[dict[str, Any]] = []
    decisions: list[dict[str, Any]] = []
    passes: list[dict[str, Any]] = []
    artifacts: list[dict[str, Any]] = []
    requirements: list[dict[str, Any]] = []
    offers: list[dict[str, Any]] = []
    boundaries: list[dict[str, Any]] = []

    for slug, name, phase, purpose, source_keys, cap_names, op_names, question, transform, artifact_kind in CONTEXT_SEEDS:
        context_id = cid(slug)
        cap_ids = [f"cgb.capability.{slug}.{i + 1}" for i in range(2)]
        op_ids = [f"cgb.operation.{slug}.{i + 1}" for i in range(2)]
        decision_id = f"cgb.decision.{slug}.primary"
        pass_id = f"cgb.pass.{slug}.primary"
        artifact_id = f"cgb.artifact.{slug}.primary"
        source_refs = sid(source_keys)
        contexts.append({
            "context_id": context_id,
            "edition": EDITION,
            "status": STATUS,
            "name": name,
            "phase": phase,
            "purpose": purpose,
            "owns": cap_names,
            "excludes": ["upstream semantic intent and typed IR lowering", "provider-internal behavior not expressed as an offer", "final adjudicated ownership"],
            "capability_refs": cap_ids,
            "operation_refs": op_ids,
            "decision_ref": decision_id,
            "pass_ref": pass_id,
            "artifact_ref": artifact_id,
            "source_refs": source_refs,
            "candidate_note": "Boundary, aggregate and name remain candidates pending independent split/merge adjudication.",
        })
        for i, capability_name in enumerate(cap_names):
            capabilities.append({
                "capability_id": cap_ids[i],
                "edition": EDITION,
                "status": STATUS,
                "owner_context": context_id,
                "name": capability_name,
                "contract": f"Provider-neutral ability to {capability_name} for an identified {slug_words(slug)} subject under explicit decisions.",
                "operation_ref": op_ids[i],
                "source_refs": source_refs[:2],
            })
        for i, operation_name in enumerate(op_names):
            effect_class = "pure" if i == 0 and phase not in {"deployment", "distribution", "release"} else "effectful"
            operations.append({
                "operation_id": op_ids[i],
                "edition": EDITION,
                "status": STATUS,
                "owner_context": context_id,
                "capability_ref": cap_ids[i],
                "name": operation_name,
                "effect_class": effect_class,
                "signature": {
                    "inputs": [{"name": "intent", "type": f"{name.replace(' ', '')}Intent"}, {"name": "decisions", "type": "ResolvedDecisionSet"}],
                    "output": {"type": f"{name.replace(' ', '')}{'Plan' if effect_class == 'pure' else 'Result'}"},
                    "errors": [f"CGB_{slug.upper()}_INVALID", "CGB_EVIDENCE_INSUFFICIENT"],
                },
                "preconditions": ["subject identity and edition are explicit", "all required decision values are resolved"],
                "postconditions": ["output references exact input identities", "limitations and evidence scope are recorded"],
                "source_refs": source_refs[:2],
            })
        decisions.append({
            "decision_id": decision_id,
            "edition": EDITION,
            "status": STATUS,
            "owner_context": context_id,
            "question": question,
            "binding_phase": phase,
            "authority_required": "declared compiler policy or authorized release policy; never a hidden provider default",
            "allowed_value_shape": "tagged finite choice or versioned structured policy",
            "no_default": True,
            "affects": op_ids + [pass_id, artifact_id],
            "source_refs": source_refs,
        })
        left, right = [part.strip() for part in transform.split("->", 1)]
        passes.append({
            "pass_id": pass_id,
            "edition": EDITION,
            "status": STATUS,
            "owner_context": context_id,
            "name": f"{name} pass",
            "stage": phase,
            "input_contract": left,
            "output_contract": right,
            "decision_refs": [decision_id],
            "determinism_inputs": ["input content digests", "pass implementation digest", "resolved decision set", "toolchain closure when applicable"],
            "invalidates_on": ["semantic input change", "pass implementation change", "decision change", "qualified target/toolchain change"],
            "receipt_type": f"cgb.receipt.{slug}.pass",
            "source_refs": source_refs,
        })
        artifacts.append({
            "artifact_id": artifact_id,
            "edition": EDITION,
            "status": STATUS,
            "owner_context": context_id,
            "artifact_kind": artifact_kind,
            "identity_contract": "media/kind identifier plus cryptographic digest; a mutable path or tag is never sufficient identity",
            "provenance_inputs": [pass_id, decision_id],
            "lifecycle": ["candidate", "generated", "verified", "published_or_retained", "retired"],
            "not_equivalent_to": "upstream input, neighboring lifecycle artifact, or running occurrence",
            "source_refs": source_refs[:2],
        })
        requirements.append({
            "requirement_id": f"cgb.requirement.{slug}.primary",
            "edition": EDITION,
            "status": STATUS,
            "owner_context": context_id,
            "required_capabilities": cap_ids,
            "required_operations": op_ids,
            "required_decisions": [decision_id],
            "compatibility_dimensions": ["structural", "semantic", "target_or_environment", "policy", "evidence"],
            "minimum_evidence": ["implementation identity", "conformance receipt scoped to the requested contract", "known limitations"],
            "refusal_if_unmatched": f"CGB_{slug.upper()}_NO_QUALIFIED_OFFER",
            "source_refs": source_refs,
        })
        offers.append({
            "offer_id": f"cgb.offer_template.{slug}.primary",
            "edition": EDITION,
            "status": STATUS,
            "owner_context": context_id,
            "offered_capabilities": cap_ids,
            "implementation_slot": f"{slug}_provider_or_toolchain_adapter",
            "must_declare": ["versions and digests", "supported target/contract subset", "configuration decisions", "effects and ambient inputs", "limitations and exclusions", "conformance evidence"],
            "unbound_until": ["requirement match succeeds", "policy accepts evidence", "all no-default decisions are resolved"],
            "non_claim": "This template is not evidence that any named tool or provider conforms.",
            "source_refs": source_refs,
        })
        boundary_kind = "pure_kernel" if phase in {"backend", "emission", "resolution", "generation"} else "effect_port_adapter"
        boundaries.append({
            "boundary_id": f"cgb.boundary.{slug}.primary",
            "edition": EDITION,
            "status": STATUS,
            "owner_context": context_id,
            "boundary_kind": boundary_kind,
            "pure_contracts": [f"normalize {slug_words(slug)} intent", f"validate {slug_words(slug)} compatibility", "compute deterministic plan or command description"],
            "effect_ports": ["content-addressed artifact store", "sandboxed process runner", "clock/randomness/network only when explicitly declared"],
            "adapter_responsibilities": ["translate plan to tool invocation", "capture stdout/stderr/status and output digests", "report observed toolchain and environment identity"],
            "forbidden_ambient_effects": ["undeclared network", "ambient clock in artifact identity", "unrecorded environment lookup", "mutable global registry state"],
            "source_refs": source_refs,
        })

    laws = [{
        "law_id": f"cgb.law.{key}",
        "edition": EDITION,
        "status": STATUS,
        "law_type": law_type,
        "statement": statement,
        "compiler_obligation": obligation,
        "failure_code": failure_code,
        "source_refs": sid(source_keys),
    } for key, law_type, statement, obligation, failure_code, source_keys in DISTINCTION_LAWS]

    proofs = [{
        "receipt_contract_id": f"cgb.receipt_contract.{key}",
        "edition": EDITION,
        "status": STATUS,
        "phase": phase,
        "claim": claim,
        "required_subject": "artifact or action identity with digest and media/kind",
        "required_producer": "identified tool, builder, verifier or authorized human role",
        "verification_method": method,
        "required_fields": ["receipt type and version", "subject digest", "producer identity", "method and inputs", "outcome", "issued time or declared timelessness", "limitations"],
        "non_claim": non_claim,
    } for key, phase, claim, method, non_claim in PROOF_SEEDS]

    innovations = [{
        "innovation_id": f"cgb.innovation.{key}",
        "edition": EDITION,
        "status": STATUS,
        "year": year,
        "development": development,
        "non_llm": True,
        "compiler_relevance": "Candidate evidence of a mechanism or ecosystem change; not evidence of adoption, completeness or preferred ownership.",
        "source_refs": sid(source_keys),
    } for key, year, development, source_keys in INNOVATION_SEEDS]

    gaps = [{
        "gap_id": f"cgb.gap.{key}",
        "edition": EDITION,
        "status": "open_explicit_gap",
        "description": description,
        "closure_evidence_required": closure,
        "blocks_completion_claim": True,
    } for key, description, closure in GAP_SEEDS]

    failures = [{
        "failure_id": f"cgb.failure.{key}",
        "edition": EDITION,
        "status": "expected_refusal",
        "context_ref": cid(context),
        "input_condition": condition,
        "expected_code": code,
        "must_not_emit": "publishable or deployable success artifact",
    } for key, context, condition, code in NEGATIVE_FAILURES]

    return {
        "sources.jsonl": SOURCES,
        "bounded-context-candidates.jsonl": contexts,
        "capabilities.jsonl": capabilities,
        "typed-operations.jsonl": operations,
        "decision-points.jsonl": decisions,
        "compiler-passes.jsonl": passes,
        "artifacts.jsonl": artifacts,
        "generation-requirements.jsonl": requirements,
        "backend-offer-templates.jsonl": offers,
        "compatibility-invalidation-laws.jsonl": laws,
        "library-toolchain-boundaries.jsonl": boundaries,
        "proof-receipt-contracts.jsonl": proofs,
        "innovations-2021-2026.jsonl": innovations,
        "gaps.jsonl": gaps,
        "examples/negative-failures.jsonl": failures,
    }


def obj_schema(record_id: str, required: dict[str, dict[str, Any]]) -> dict[str, Any]:
    common = {
        record_id: {"type": "string", "pattern": "^cgb\\."},
        "edition": {"type": "integer", "const": EDITION},
        "status": {"type": "string", "minLength": 1},
    }
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": f"https://shannon-insight.local/schemas/codegen-build/{record_id}.schema.json",
        "type": "object",
        "additionalProperties": False,
        "required": list(common) + list(required),
        "properties": {**common, **required},
    }


S = {"type": "string", "minLength": 1}
SA = {"type": "array", "minItems": 1, "uniqueItems": True, "items": S}
BOOL = {"type": "boolean"}
INT = {"type": "integer"}


def schemas() -> dict[str, dict[str, Any]]:
    signature = {
        "type": "object",
        "additionalProperties": False,
        "required": ["inputs", "output", "errors"],
        "properties": {
            "inputs": {"type": "array", "minItems": 1, "items": {"type": "object"}},
            "output": {"type": "object"},
            "errors": SA,
        },
    }
    return {
        "source": obj_schema("source_id", {"title": S, "issuer": S, "url": {"type": "string", "pattern": "^https://"}, "authority_class": {"enum": ["open_specification", "official_documentation", "original_research"]}, "publication_year": INT, "primary_or_official": {"const": True}, "claim_scope": S, "limitations": S, "accessed_at": S}),
        "context": obj_schema("context_id", {"name": S, "phase": S, "purpose": S, "owns": SA, "excludes": SA, "capability_refs": SA, "operation_refs": SA, "decision_ref": S, "pass_ref": S, "artifact_ref": S, "source_refs": SA, "candidate_note": S}),
        "capability": obj_schema("capability_id", {"owner_context": S, "name": S, "contract": S, "operation_ref": S, "source_refs": SA}),
        "operation": obj_schema("operation_id", {"owner_context": S, "capability_ref": S, "name": S, "effect_class": {"enum": ["pure", "effectful"]}, "signature": signature, "preconditions": SA, "postconditions": SA, "source_refs": SA}),
        "decision": obj_schema("decision_id", {"owner_context": S, "question": S, "binding_phase": S, "authority_required": S, "allowed_value_shape": S, "no_default": {"const": True}, "affects": SA, "source_refs": SA}),
        "pass": obj_schema("pass_id", {"owner_context": S, "name": S, "stage": S, "input_contract": S, "output_contract": S, "decision_refs": SA, "determinism_inputs": SA, "invalidates_on": SA, "receipt_type": S, "source_refs": SA}),
        "artifact": obj_schema("artifact_id", {"owner_context": S, "artifact_kind": S, "identity_contract": S, "provenance_inputs": SA, "lifecycle": SA, "not_equivalent_to": S, "source_refs": SA}),
        "requirement": obj_schema("requirement_id", {"owner_context": S, "required_capabilities": SA, "required_operations": SA, "required_decisions": SA, "compatibility_dimensions": SA, "minimum_evidence": SA, "refusal_if_unmatched": S, "source_refs": SA}),
        "offer": obj_schema("offer_id", {"owner_context": S, "offered_capabilities": SA, "implementation_slot": S, "must_declare": SA, "unbound_until": SA, "non_claim": S, "source_refs": SA}),
        "law": obj_schema("law_id", {"law_type": {"enum": ["non_collapse", "compatibility", "invalidation"]}, "statement": S, "compiler_obligation": S, "failure_code": S, "source_refs": SA}),
        "boundary": obj_schema("boundary_id", {"owner_context": S, "boundary_kind": {"enum": ["pure_kernel", "effect_port_adapter"]}, "pure_contracts": SA, "effect_ports": SA, "adapter_responsibilities": SA, "forbidden_ambient_effects": SA, "source_refs": SA}),
        "receipt": obj_schema("receipt_contract_id", {"phase": S, "claim": S, "required_subject": S, "required_producer": S, "verification_method": S, "required_fields": SA, "non_claim": S}),
        "innovation": obj_schema("innovation_id", {"year": {"type": "integer", "minimum": 2021, "maximum": 2026}, "development": S, "non_llm": {"const": True}, "compiler_relevance": S, "source_refs": SA}),
        "gap": obj_schema("gap_id", {"description": S, "closure_evidence_required": S, "blocks_completion_claim": {"const": True}}),
        "failure": obj_schema("failure_id", {"context_ref": S, "input_condition": S, "expected_code": S, "must_not_emit": S}),
    }


FILE_SCHEMAS = {
    "sources.jsonl": "source",
    "bounded-context-candidates.jsonl": "context",
    "capabilities.jsonl": "capability",
    "typed-operations.jsonl": "operation",
    "decision-points.jsonl": "decision",
    "compiler-passes.jsonl": "pass",
    "artifacts.jsonl": "artifact",
    "generation-requirements.jsonl": "requirement",
    "backend-offer-templates.jsonl": "offer",
    "compatibility-invalidation-laws.jsonl": "law",
    "library-toolchain-boundaries.jsonl": "boundary",
    "proof-receipt-contracts.jsonl": "receipt",
    "innovations-2021-2026.jsonl": "innovation",
    "gaps.jsonl": "gap",
    "examples/negative-failures.jsonl": "failure",
}


def native_example() -> dict[str, Any]:
    return {
        "example_id": "cgb.example.native-rust-service",
        "edition": EDITION,
        "status": STATUS,
        "description": "Rust service compiled for x86_64 Linux musl, packaged as an OCI image and deployed by immutable digest.",
        "typed_ir_input": {"id": "ir:payments-api:v7", "digest": "sha256:typed-ir-example", "note": "Already lowered; business semantics are not chosen by the codegen stages."},
        "target_contract": {"triple": "x86_64-unknown-linux-musl", "cpu": "x86-64-v2", "features": ["+sse2"], "panic": "abort", "crt": "static"},
        "selected_passes": ["cgb.pass.backend_selection.primary", "cgb.pass.native_codegen.primary", "cgb.pass.linking.primary", "cgb.pass.package_assembly.primary", "cgb.pass.deployment_manifest.primary"],
        "artifacts": [
            {"kind": "generated-source", "digest": "sha256:generated-source-example"},
            {"kind": "linked-binary", "digest": "sha256:linked-binary-example"},
            {"kind": "oci-image", "digest": "sha256:oci-image-example"},
            {"kind": "deployment-manifest", "digest": "sha256:k8s-manifest-example"},
        ],
        "evidence": ["cgb.receipt_contract.backend-semantic", "cgb.receipt_contract.abi-conformant", "cgb.receipt_contract.hermetic", "cgb.receipt_contract.reproducible", "cgb.receipt_contract.provenance-subject", "cgb.receipt_contract.release-authorized"],
        "explicit_non_equivalences": ["OCI image is not the Deployment manifest", "Deployment manifest is not a running Pod", "reproducible image bytes are not semantic conformance"],
    }


def wasm_example() -> dict[str, Any]:
    return {
        "example_id": "cgb.example.wasi-component",
        "edition": EDITION,
        "status": STATUS,
        "description": "Typed transform emitted as a core Wasm module, componentized against a versioned WIT world, then stored as an OCI artifact.",
        "typed_ir_input": {"id": "ir:customer-normalizer:v3", "digest": "sha256:typed-ir-wasm-example", "note": "Record normalization semantics were resolved before backend selection."},
        "target_contract": {"triple": "wasm32-wasip2", "world": "acme:data-transform@1.2.0/transformer", "wasi": "0.2", "imports": ["wasi:cli/environment@0.2.0"]},
        "selected_passes": ["cgb.pass.backend_selection.primary", "cgb.pass.wasm_core_codegen.primary", "cgb.pass.wasm_component_codegen.primary", "cgb.pass.package_assembly.primary", "cgb.pass.artifact_repository.primary"],
        "artifacts": [
            {"kind": "core-wasm-module", "digest": "sha256:core-wasm-example"},
            {"kind": "wasm-component", "digest": "sha256:component-example"},
            {"kind": "wit-package", "digest": "sha256:wit-example"},
            {"kind": "oci-artifact-manifest", "digest": "sha256:wasm-oci-example"},
        ],
        "evidence": ["cgb.receipt_contract.backend-semantic", "cgb.receipt_contract.target-compatible", "cgb.receipt_contract.emission-deterministic", "cgb.receipt_contract.repository-integrity"],
        "explicit_non_equivalences": ["core Wasm module is not a component", "WIT source is not the canonical ABI adapter", "OCI storage is not a running component occurrence"],
    }


def json_text(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def jsonl_text(records: list[dict[str, Any]]) -> str:
    return "".join(json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n" for record in records)


def manifest(records: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    counts = {name: len(values) for name, values in records.items()}
    principal = sum(counts[name] for name in ["capabilities.jsonl", "typed-operations.jsonl", "decision-points.jsonl", "compiler-passes.jsonl", "artifacts.jsonl"])
    source_roles = Counter(item["authority_class"] for item in records["sources.jsonl"])
    phases = Counter(item["phase"] for item in records["bounded-context-candidates.jsonl"])
    return {
        "atlas_id": "cgb.atlas.codegen-build.edition-1",
        "edition": EDITION,
        "as_of": AS_OF,
        "status": STATUS,
        "completion_claim": False,
        "llm_or_generative_codegen_in_scope": False,
        "counts": counts,
        "principal_record_count": principal,
        "principal_record_formula": "capabilities + typed operations + decisions + compiler passes + artifacts",
        "source_authority_counts": dict(sorted(source_roles.items())),
        "context_phase_counts": dict(sorted(phases.items())),
        "minimums_enforced": {"contexts": 40, "principal_records": 200, "sources": 60, "innovations_2021_2026": 20, "negative_failures": 5},
        "validation_scope": ["deterministic regeneration", "schema shape", "unique IDs", "internal references", "candidate status", "required distinction laws", "source depth and authority", "example references", "honest gaps"],
        "limitations": ["No compiler or backend is implemented.", "No provider is qualified by name.", "Source freshness and external conformance require independent review.", "Enumeration and boundary adjudication remain open gaps."],
    }


def render() -> dict[Path, str]:
    records = generated_records()
    output: dict[Path, str] = {ROOT / filename: jsonl_text(values) for filename, values in records.items()}
    output[ROOT / "manifest.json"] = json_text(manifest(records))
    output[ROOT / "examples/native-rust-service.json"] = json_text(native_example())
    output[ROOT / "examples/wasi-component.json"] = json_text(wasm_example())
    for name, schema in schemas().items():
        output[ROOT / "schemas" / f"{name}.schema.json"] = json_text(schema)
    return output


def main() -> int:
    for path, content in sorted(render().items()):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    print(f"generated {len(render())} files under {ROOT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
