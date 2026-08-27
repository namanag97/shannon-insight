#!/usr/bin/env python3
"""Deterministically build the conformance and qualification research candidate."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EDITION = 1
DATE = "2026-08-25"


def rec(identifier: str, kind: str, **fields):
    return {"id": identifier, "kind": kind, "edition": EDITION,
            "status": "candidate_research_record", **fields}


def write_json(path: Path, value) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def write_jsonl(path: Path, rows) -> None:
    path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows))


# Primary standards/specifications, original papers, and official project/tool documentation.
# A URL is authority only for the scope stated in the record, never proof of an implementation.
SOURCE_DATA = [
    ("iso29119_1", "ISO/IEC/IEEE 29119-1 software testing concepts", "https://www.iso.org/standard/81291.html", "test concepts and vocabulary", "standard", 2022),
    ("iso29119_2", "ISO/IEC/IEEE 29119-2 test processes", "https://standards.ieee.org/ieee/29119-2/10777/", "test process requirements", "standard", 2021),
    ("iso29119_3", "ISO/IEC/IEEE 29119-3 test documentation", "https://standards.ieee.org/ieee/29119-3/10778/", "test documentation", "standard", 2021),
    ("iso29119_4", "ISO/IEC/IEEE 29119-4 test techniques", "https://standards.ieee.org/ieee/29119-4/10779/", "test design techniques", "standard", 2021),
    ("iso25010", "ISO/IEC 25010 product quality model", "https://www.iso.org/standard/78176.html", "software product quality characteristics", "standard", 2023),
    ("iso25012", "ISO/IEC 25012 data quality model", "https://www.iso.org/standard/35736.html", "data quality characteristics", "standard", 2008),
    ("iso17025", "ISO/IEC 17025 testing laboratory competence", "https://www.iso.org/standard/66912.html", "laboratory competence and impartiality", "standard", 2017),
    ("iso5725", "ISO 5725 accuracy of measurement methods", "https://www.iso.org/standard/69418.html", "trueness and precision", "standard", 2019),
    ("iso3534", "ISO 3534 statistics vocabulary", "https://www.iso.org/standard/40145.html", "statistical vocabulary", "standard", 2006),
    ("iso8000", "ISO 8000 data quality", "https://www.iso.org/standard/81745.html", "data quality principles", "standard", 2022),
    ("iso8601", "ISO 8601 date and time", "https://www.iso.org/iso-8601-date-and-time-format.html", "date/time representation", "standard", 2019),
    ("iec61508", "IEC 61508 functional safety", "https://www.iec.ch/functional-safety", "functional safety lifecycle", "standard", 2010),
    ("iso26262", "ISO 26262 road vehicle functional safety", "https://www.iso.org/standard/68383.html", "automotive safety verification", "standard", 2018),
    ("iso21434", "ISO/SAE 21434 automotive cybersecurity", "https://www.iso.org/standard/70918.html", "automotive cybersecurity assurance", "standard", 2021),
    ("iso27001", "ISO/IEC 27001 information security management", "https://www.iso.org/standard/27001", "information security management", "standard", 2022),
    ("iso27034", "ISO/IEC 27034 application security", "https://www.iso.org/standard/44378.html", "application security", "standard", 2011),
    ("iso23894", "ISO/IEC 23894 risk management", "https://www.iso.org/standard/77304.html", "risk management for AI systems", "standard", 2023),
    ("do178c", "RTCA DO-178C software considerations", "https://www.rtca.org/products/do-178c/", "airborne software assurance", "standard", 2011),
    ("ecss_q_st_80c", "ECSS-Q-ST-80C software product assurance", "https://ecss.nl/standard/ecss-q-st-80c-rev-1-software-product-assurance-15-february-2017/", "space software assurance", "standard", 2017),
    ("wcag22", "W3C WCAG 2.2", "https://www.w3.org/TR/WCAG22/", "web accessibility success criteria", "standard", 2023),
    ("wai_aria12", "WAI-ARIA 1.2", "https://www.w3.org/TR/wai-aria-1.2/", "accessible role/state semantics", "standard", 2023),
    ("act_rules", "W3C Accessibility Conformance Testing Rules Format", "https://www.w3.org/TR/act-rules-format/", "accessibility rule interchange", "standard", 2022),
    ("jsonschema2020", "JSON Schema Draft 2020-12", "https://json-schema.org/draft/2020-12/json-schema-core", "JSON structural validation", "standard", 2022),
    ("shacl", "W3C SHACL", "https://www.w3.org/TR/shacl/", "RDF graph constraints", "standard", 2017),
    ("rdf12", "W3C RDF 1.2 Concepts", "https://www.w3.org/TR/rdf12-concepts/", "RDF data model", "standard", 2025),
    ("owl2", "W3C OWL 2 structural specification", "https://www.w3.org/TR/owl2-syntax/", "ontology structural semantics", "standard", 2012),
    ("sparql12", "W3C SPARQL 1.2 Query", "https://www.w3.org/TR/sparql12-query/", "graph query semantics", "standard", 2025),
    ("prov_o", "W3C PROV-O", "https://www.w3.org/TR/prov-o/", "provenance ontology", "standard", 2013),
    ("openapi31", "OpenAPI Specification 3.1", "https://spec.openapis.org/oas/v3.1.1.html", "HTTP API contract", "standard", 2024),
    ("asyncapi30", "AsyncAPI Specification 3.0", "https://www.asyncapi.com/docs/reference/specification/v3.0.0", "asynchronous API contract", "standard", 2024),
    ("rfc8259", "RFC 8259 JSON", "https://www.rfc-editor.org/rfc/rfc8259", "JSON syntax and interoperability", "standard", 2017),
    ("rfc8949", "RFC 8949 CBOR", "https://www.rfc-editor.org/rfc/rfc8949", "CBOR encoding", "standard", 2020),
    ("rfc9110", "RFC 9110 HTTP Semantics", "https://www.rfc-editor.org/rfc/rfc9110", "HTTP semantics", "standard", 2022),
    ("rfc8446", "RFC 8446 TLS 1.3", "https://www.rfc-editor.org/rfc/rfc8446", "TLS protocol semantics", "standard", 2018),
    ("rfc9000", "RFC 9000 QUIC", "https://www.rfc-editor.org/rfc/rfc9000", "QUIC transport semantics", "standard", 2021),
    ("rfc3339", "RFC 3339 timestamps", "https://www.rfc-editor.org/rfc/rfc3339", "Internet timestamp profile", "standard", 2002),
    ("rfc8785", "RFC 8785 JSON Canonicalization Scheme", "https://www.rfc-editor.org/rfc/rfc8785", "canonical JSON and digests", "standard", 2020),
    ("semver", "Semantic Versioning 2.0.0", "https://semver.org/spec/v2.0.0.html", "version compatibility declaration", "specification", 2013),
    ("spdx3", "SPDX 3.0 specification", "https://spdx.github.io/spdx-spec/v3.0/", "software bill of materials", "standard", 2024),
    ("slsa10", "SLSA v1.0 specification", "https://slsa.dev/spec/v1.0/", "build provenance assurance", "standard", 2023),
    ("in_toto", "in-toto specification", "https://in-toto.io/", "supply-chain layout and attestations", "standard", 2024),
    ("sigstore", "Sigstore documentation", "https://docs.sigstore.dev/", "artifact signing and transparency", "official_docs", 2026),
    ("oci_image", "OCI Image Format", "https://github.com/opencontainers/image-spec", "container image identity", "standard", 2025),
    ("oci_distribution", "OCI Distribution Specification", "https://github.com/opencontainers/distribution-spec", "artifact distribution", "standard", 2025),
    ("wasm_core3", "WebAssembly Core Specification 3.0", "https://www.w3.org/TR/wasm-core-3/", "WebAssembly execution semantics", "standard", 2025),
    ("wasm_component", "WebAssembly Component Model", "https://component-model.bytecodealliance.org/", "component interface semantics", "specification", 2026),
    ("nist_ssdf", "NIST SP 800-218 SSDF", "https://csrc.nist.gov/pubs/sp/800/218/final", "secure development practices", "standard", 2022),
    ("nist_800_53", "NIST SP 800-53 Rev. 5", "https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final", "security and privacy controls", "standard", 2020),
    ("nist_800_115", "NIST SP 800-115", "https://csrc.nist.gov/pubs/sp/800/115/final", "security testing and assessment", "standard", 2008),
    ("nist_cyberframework2", "NIST Cybersecurity Framework 2.0", "https://www.nist.gov/cyberframework", "cybersecurity outcomes", "standard", 2024),
    ("nist_acvp", "NIST Automated Cryptographic Validation Protocol", "https://pages.nist.gov/ACVP/", "cryptographic algorithm validation", "standard", 2026),
    ("nist_fips140_3", "FIPS 140-3", "https://csrc.nist.gov/pubs/fips/140-3/final", "cryptographic module validation", "standard", 2019),
    ("nist_tn1297", "NIST TN 1297 measurement uncertainty", "https://www.nist.gov/pml/nist-technical-note-1297", "measurement uncertainty", "standard", 1994),
    ("nist_ir8298", "NIST IR 8298 computational model V&V", "https://doi.org/10.6028/NIST.IR.8298", "model verification validation and uncertainty", "technical_report", 2020),
    ("nist_stats", "NIST Engineering Statistics Handbook", "https://www.itl.nist.gov/div898/handbook/", "statistical experiment and measurement", "official_docs", 2026),
    ("owasp_asvs", "OWASP ASVS", "https://owasp.org/www-project-application-security-verification-standard/", "application security verification", "standard", 2025),
    ("owasp_wstg", "OWASP Web Security Testing Guide", "https://owasp.org/www-project-web-security-testing-guide/", "web security test methods", "standard", 2025),
    ("owasp_samm", "OWASP SAMM", "https://owaspsamm.org/model/verification/", "security verification maturity", "standard", 2025),
    ("openssf_scorecard", "OpenSSF Scorecard", "https://scorecard.dev/", "software supply-chain checks", "official_docs", 2026),
    ("rust_test", "Rust test attribute", "https://doc.rust-lang.org/reference/attributes/testing.html", "Rust test execution semantics", "official_docs", 2026),
    ("cargo_test", "Cargo test command", "https://doc.rust-lang.org/cargo/commands/cargo-test.html", "Cargo test targets and execution", "official_docs", 2026),
    ("rust_unsafe", "Rust Reference unsafe", "https://doc.rust-lang.org/reference/unsafe-keyword.html", "unsafe obligations", "official_docs", 2026),
    ("rust_nomicon", "Rustonomicon", "https://doc.rust-lang.org/nomicon/", "unsafe Rust reasoning", "official_docs", 2026),
    ("miri", "Miri", "https://github.com/rust-lang/miri", "Rust interpreter undefined-behavior checks", "official_docs", 2026),
    ("cargo_fuzz", "Rust Fuzz Book", "https://rust-fuzz.github.io/book/", "coverage-guided fuzzing for Rust", "official_docs", 2026),
    ("libfuzzer", "LLVM libFuzzer", "https://llvm.org/docs/LibFuzzer.html", "coverage-guided fuzzing", "official_docs", 2026),
    ("llvm_sanitizers", "LLVM Sanitizers", "https://clang.llvm.org/docs/index.html", "memory thread and undefined behavior detection", "official_docs", 2026),
    ("kani", "Kani Rust Verifier", "https://model-checking.github.io/kani/", "bounded model checking for Rust", "official_docs", 2026),
    ("loom", "Loom", "https://docs.rs/loom/latest/loom/", "concurrent interleaving exploration", "official_docs", 2026),
    ("proptest", "Proptest", "https://docs.rs/proptest/latest/proptest/", "property testing and shrinking", "official_docs", 2026),
    ("quickcheck", "QuickCheck Rust", "https://docs.rs/quickcheck/latest/quickcheck/", "property testing", "official_docs", 2026),
    ("bolero", "Bolero", "https://github.com/camshaft/bolero", "property and fuzz testing", "official_docs", 2026),
    ("criterion", "Criterion.rs", "https://bheisler.github.io/criterion.rs/book/", "statistical microbenchmarking", "official_docs", 2026),
    ("iai_callgrind", "Iai-Callgrind", "https://iai-callgrind.github.io/iai-callgrind/", "deterministic instruction-level benchmarking", "official_docs", 2026),
    ("insta", "Insta snapshot testing", "https://insta.rs/docs/", "snapshot/golden testing", "official_docs", 2026),
    ("cargo_nextest", "cargo-nextest", "https://nexte.st/", "Rust test execution and retries", "official_docs", 2026),
    ("cargo_semver_checks", "cargo-semver-checks", "https://github.com/obi1kenobi/cargo-semver-checks", "Rust API compatibility checking", "official_docs", 2026),
    ("cargo_mutants", "cargo-mutants", "https://mutants.rs/", "Rust mutation testing", "official_docs", 2026),
    ("trybuild", "trybuild", "https://docs.rs/trybuild/latest/trybuild/", "Rust compile-fail UI testing", "official_docs", 2026),
    ("rustdoc_tests", "Rustdoc documentation tests", "https://doc.rust-lang.org/rustdoc/write-documentation/documentation-tests.html", "executable documentation", "official_docs", 2026),
    ("aflpp", "AFL++ documentation", "https://aflplus.plus/docs/", "coverage-guided fuzzing", "official_docs", 2026),
    ("libafl", "LibAFL book", "https://aflplus.plus/libafl-book/", "composable fuzzing", "official_docs", 2026),
    ("tla", "TLA+ specification language", "https://lamport.azurewebsites.net/tla/tla.html", "state-machine specification", "official_docs", 2026),
    ("apalache", "Apalache model checker", "https://apalache-mc.org/", "symbolic TLA+ model checking", "official_docs", 2026),
    ("alloy", "Alloy documentation", "https://alloytools.org/documentation.html", "relational model finding", "official_docs", 2026),
    ("jepsen", "Jepsen analyses", "https://jepsen.io/analyses", "distributed-system safety testing", "official_docs", 2026),
    ("foundationdb_sim", "FoundationDB testing", "https://apple.github.io/foundationdb/testing.html", "deterministic simulation testing", "official_docs", 2026),
    ("chaos_mesh", "Chaos Mesh documentation", "https://chaos-mesh.org/docs/", "cloud-native chaos experiments", "official_docs", 2026),
    ("litmus", "LitmusChaos documentation", "https://docs.litmuschaos.io/", "chaos experiment workflows", "official_docs", 2026),
    ("testcontainers", "Testcontainers", "https://testcontainers.com/", "ephemeral integration environments", "official_docs", 2026),
    ("pact", "Pact specification", "https://docs.pact.io/implementation_guides/pact_specification", "consumer-driven contract testing", "specification", 2026),
    ("sqlite_sltest", "SQLite SQL Logic Test", "https://www.sqlite.org/sqllogictest/doc/trunk/about.wiki", "SQL differential conformance", "official_docs", 2026),
    ("postgres_regress", "PostgreSQL regression tests", "https://www.postgresql.org/docs/current/regress.html", "database regression testing", "official_docs", 2026),
    ("arrow_integration", "Apache Arrow integration testing", "https://arrow.apache.org/docs/format/Integration.html", "cross-implementation Arrow conformance", "specification", 2026),
    ("parquet_testing", "Apache Parquet testing repository", "https://github.com/apache/parquet-testing", "cross-implementation Parquet fixtures", "official_docs", 2026),
    ("iceberg_compat", "Apache Iceberg compatibility", "https://iceberg.apache.org/spec/", "table format conformance", "specification", 2026),
    ("delta_protocol", "Delta Lake protocol", "https://github.com/delta-io/delta/blob/master/PROTOCOL.md", "Delta protocol conformance", "specification", 2026),
    ("avro_spec", "Apache Avro specification", "https://avro.apache.org/docs/current/specification/", "schema and binary format conformance", "specification", 2026),
    ("kafka_protocol", "Apache Kafka protocol", "https://kafka.apache.org/protocol", "Kafka wire protocol", "specification", 2026),
    ("tpc_h", "TPC-H specification", "https://www.tpc.org/tpch/", "decision-support benchmark", "benchmark_spec", 2026),
    ("tpc_ds", "TPC-DS specification", "https://www.tpc.org/tpcds/", "decision-support benchmark", "benchmark_spec", 2026),
    ("tpc_c", "TPC-C specification", "https://www.tpc.org/tpcc/", "transaction processing benchmark", "benchmark_spec", 2026),
    ("spec_cpu", "SPEC CPU benchmark", "https://www.spec.org/cpu2017/Docs/overview.html", "CPU benchmark rules", "benchmark_spec", 2017),
    ("ldbc_snb", "LDBC Social Network Benchmark", "https://ldbcouncil.org/benchmarks/snb/", "graph system benchmark", "benchmark_spec", 2026),
    ("mlperf", "MLPerf Inference rules", "https://github.com/mlcommons/inference_policies", "predictive-model performance benchmark rules", "benchmark_spec", 2026),
    ("scikit_cv", "scikit-learn cross-validation", "https://scikit-learn.org/stable/modules/cross_validation.html", "predictive evaluation splitting", "official_docs", 2026),
    ("scikit_calibration", "scikit-learn probability calibration", "https://scikit-learn.org/stable/modules/calibration.html", "probability calibration evaluation", "official_docs", 2026),
    ("scipy_test", "SciPy testing guidelines", "https://docs.scipy.org/doc/scipy/dev/contributor/testing.html", "scientific library testing", "official_docs", 2026),
    ("numpy_test", "NumPy testing guidelines", "https://numpy.org/doc/stable/reference/testing.html", "numerical assertions and tolerances", "official_docs", 2026),
    ("ieee754", "IEEE 754 floating-point arithmetic", "https://standards.ieee.org/ieee/754/6210/", "floating-point semantics", "standard", 2019),
    ("quickcheck_paper", "QuickCheck original paper", "https://doi.org/10.1145/351240.351266", "property-based testing method", "original_paper", 2000),
    ("metamorphic_paper", "Metamorphic testing original formulation", "https://doi.org/10.1142/S0218194001000433", "metamorphic testing method", "original_paper", 2001),
    ("differential_paper", "Differential testing for software", "https://doi.org/10.1145/75309.75313", "differential testing method", "original_paper", 1990),
    ("mutation_paper", "Mutation analysis original paper", "https://doi.org/10.1109/TSE.1978.231139", "mutation analysis method", "original_paper", 1978),
    ("delta_debugging", "Simplifying and isolating failure-inducing input", "https://doi.org/10.1109/TSE.2002.1039487", "counterexample minimization", "original_paper", 2002),
    ("ddmin_paper", "Delta debugging", "https://www.st.cs.uni-saarland.de/publications/files/zeller-esec-1999.pdf", "failure-inducing change isolation", "original_paper", 1999),
    ("statistical_power", "Statistical power analysis", "https://doi.org/10.1016/C2013-0-10517-X", "power and sample size", "original_book", 1988),
    ("conformal_prediction", "Distribution-free predictive inference", "https://doi.org/10.1007/978-3-319-33395-3", "predictive uncertainty coverage", "original_book", 2005),
    ("tripod", "TRIPOD reporting guideline", "https://www.tripod-statement.org/", "predictive model reporting", "guideline", 2026),
    ("probaST", "PROBAST predictive model risk of bias", "https://www.probast.org/", "predictive model bias appraisal", "guideline", 2026),
    ("acm_badges", "ACM artifact review and badging", "https://www.acm.org/publications/policies/artifact-review-and-badging-current", "artifact availability and reproducibility", "policy", 2026),
    ("repro_builds", "Reproducible Builds documentation", "https://reproducible-builds.org/docs/", "reproducible build techniques", "official_docs", 2026),
    ("source_date_epoch", "SOURCE_DATE_EPOCH specification", "https://reproducible-builds.org/specs/source-date-epoch/", "build time normalization", "specification", 2026),
    ("osv", "Open Source Vulnerability schema", "https://ossf.github.io/osv-schema/", "vulnerability identity and affected ranges", "specification", 2026),
]


CONTEXTS = [
    ("structural_schema", "schema validation", "structure"), ("static_type", "compile and type checking", "structure"),
    ("api_surface", "public API compatibility", "compatibility"), ("wire_protocol", "wire protocol conformance", "protocol"),
    ("serialization", "serialization round trip", "representation"), ("canonicalization", "canonical bytes and digest", "representation"),
    ("algebraic_law", "algebraic laws", "semantics"), ("domain_invariant", "domain invariants", "semantics"),
    ("state_machine", "state-machine safety and liveness", "semantics"), ("model_based", "model-based command traces", "semantics"),
    ("property_based", "property-based generation", "generation"), ("metamorphic", "metamorphic relations", "oracle"),
    ("differential", "differential implementation comparison", "oracle"), ("golden", "golden fixture and snapshot", "oracle"),
    ("conformance_suite", "normative conformance suite", "oracle"), ("cross_implementation", "cross-implementation interoperability", "oracle"),
    ("fuzz_parser", "parser and decoder fuzzing", "robustness"), ("fuzz_stateful", "stateful structured fuzzing", "robustness"),
    ("mutation", "mutation adequacy", "adequacy"), ("coverage", "structural and semantic coverage", "adequacy"),
    ("chaos", "chaos experiments", "resilience"), ("failure_injection", "deterministic failure injection", "resilience"),
    ("partition", "network partition behavior", "distributed"), ("crash_recovery", "crash and recovery", "distributed"),
    ("linearizability", "linearizability", "distributed"), ("serializability", "transaction serializability", "distributed"),
    ("exactly_once", "delivery and effect deduplication", "distributed"), ("replay", "deterministic replay", "change"),
    ("migration", "schema/state migration", "change"), ("restore", "backup restore correctness", "change"),
    ("backfill", "historical backfill equivalence", "change"), ("rolling_upgrade", "multi-version rolling upgrade", "change"),
    ("security_static", "security static analysis", "security"), ("security_dynamic", "security dynamic testing", "security"),
    ("crypto_vector", "cryptographic test vectors", "security"), ("supply_chain", "build and dependency provenance", "security"),
    ("threat_abuse", "threat and abuse-case testing", "security"), ("access_control", "authorization decision and enforcement", "security"),
    ("privacy", "privacy property testing", "privacy"), ("anonymization", "anonymization claim evaluation", "privacy"),
    ("performance_latency", "latency distribution", "performance"), ("performance_throughput", "throughput and saturation", "performance"),
    ("resource_memory", "memory envelope", "performance"), ("resource_io", "I/O and network envelope", "performance"),
    ("cost", "workload cost", "performance"), ("energy", "energy per useful work", "performance"),
    ("scalability", "scale-up and scale-out", "performance"), ("soak", "long-duration soak", "performance"),
    ("numerical_accuracy", "numerical accuracy", "numerical"), ("numerical_stability", "numerical stability", "numerical"),
    ("floating_point", "floating-point edge behavior", "numerical"), ("statistical_power", "sampling power", "statistical"),
    ("uncertainty", "measurement and predictive uncertainty", "statistical"), ("calibration", "probability calibration", "statistical"),
    ("predictive_validation", "predictive generalization", "statistical"), ("distribution_shift", "distribution-shift robustness", "statistical"),
    ("fairness_slices", "slice performance and fairness", "statistical"), ("reproducibility", "computational reproducibility", "reproducibility"),
    ("deterministic_build", "bit-reproducible build", "reproducibility"), ("environment_portability", "environment portability", "compatibility"),
    ("accessibility", "accessibility conformance", "human"), ("internationalization", "locale and internationalization", "human"),
    ("offline_recovery", "offline/device recovery", "human"), ("usability", "task usability", "human"),
    ("data_quality", "data quality law", "data"), ("reconciliation", "independent reconciliation", "data"),
    ("lineage", "lineage evidence", "data"), ("temporal", "valid and recording time", "data"),
    ("geospatial", "CRS and spatial operation", "data"), ("document", "document extraction and rendition", "data"),
    ("streaming", "stream time/watermark behavior", "data"), ("graph", "graph identity and traversal", "data"),
    ("process_mining", "event-object-process semantics", "analytics"), ("optimization", "optimization feasibility and optimality", "analytics"),
    ("counterparty_risk", "SA-CCR counterparty-risk calculation", "vertical"), ("acute_care", "acute-care temporal pathway", "vertical"),
]


ORACLE_TEMPLATES = [
    ("reference", "normative reference evaluator", "authoritative specification or executable reference"),
    ("law", "executable law predicate", "domain authority-approved invariant"),
    ("relation", "metamorphic or relational oracle", "declared input/output relation"),
    ("independent", "independent implementation comparison", "separately developed implementation"),
]

TEST_TEMPLATES = [
    ("example", "curated boundary examples", "exact boundaries and adversarial twins"),
    ("generated", "generated population", "declared generator, seed and shrinker"),
    ("exhaustive", "bounded exhaustive exploration", "explicit finite domain and bound"),
]


LIBRARIES = [
    ("identity", "exact subject/artifact/target/occurrence identity", "pure"),
    ("digest", "canonical content digests", "pure"), ("schema", "structural schema validation", "pure"),
    ("typecheck", "language/compiler type checks", "adapter"), ("law", "typed executable laws", "pure"),
    ("oracle_spi", "oracle interface and authority", "pure"), ("generator", "test population generators", "pure"),
    ("shrinker", "counterexample shrinking", "pure"), ("corpus", "versioned corpus storage", "runtime"),
    ("property", "property execution", "runtime"), ("model", "model-based trace generation", "runtime"),
    ("metamorphic", "metamorphic relation execution", "runtime"), ("differential", "differential comparison", "runtime"),
    ("golden", "golden fixture checking", "runtime"), ("conformance", "normative suite runner", "runtime"),
    ("fuzz", "coverage-guided fuzz runner", "adapter"), ("mutation", "mutation generation/scoring", "adapter"),
    ("coverage", "multi-axis coverage accounting", "runtime"), ("chaos", "chaos experiment control", "effect_port"),
    ("fault", "failure injection", "effect_port"), ("scheduler", "deterministic scheduler/simulation", "runtime"),
    ("security", "security test adapters", "adapter"), ("crypto_vector", "cryptographic vector runner", "runtime"),
    ("benchmark", "benchmark protocol", "runtime"), ("measurement", "measurement capture and uncertainty", "runtime"),
    ("statistics", "power, intervals and multiple comparisons", "pure"), ("numerical", "numeric tolerance policies", "pure"),
    ("predictive", "predictive evaluation plans", "pure"), ("accessibility", "accessibility rule runner", "adapter"),
    ("compatibility", "compatibility matrix evaluator", "pure"), ("replay", "replay harness", "runtime"),
    ("migration", "migration and rollback harness", "runtime"), ("restore", "backup/restore harness", "runtime"),
    ("environment", "hermetic environment descriptor", "pure"), ("sandbox", "isolated execution", "effect_port"),
    ("receipt", "immutable qualification receipts", "pure"), ("evidence", "evidence object storage", "runtime"),
    ("counterexample", "counterexample lifecycle", "pure"), ("waiver", "waiver/expiry/revocation", "pure"),
    ("appraisal", "independent appraisal workflow", "effect_port"), ("composition", "compositional guarantee algebra", "pure"),
    ("invalidation", "support-set invalidation", "pure"), ("qualification", "qualification state machine", "pure"),
    ("report", "human/machine qualification report", "pure"), ("ci_adapter", "CI execution adapter", "adapter"),
    ("target_probe", "deployed target probe", "effect_port"), ("artifact_attestation", "build/artifact attestation", "adapter"),
    ("vertical_oracle", "vertical authority oracle packs", "plugin"),
]


INNOVATIONS = [
    ("slsa_v1", 2023, "SLSA v1.0 stabilizes provenance levels and build-track requirements", "source.ce.slsa10"),
    ("spdx3", 2024, "SPDX 3.0 supplies a modular system model for software and data provenance", "source.ce.spdx3"),
    ("wasm_component", 2025, "WebAssembly component-model tooling enables typed cross-language component conformance", "source.ce.wasm_component"),
    ("rdf12", 2025, "RDF 1.2 adds directional language-tagged strings and modernized graph semantics", "source.ce.rdf12"),
    ("sparql12", 2025, "SPARQL 1.2 advances query conformance over RDF 1.2 datasets", "source.ce.sparql12"),
    ("wcag22", 2023, "WCAG 2.2 adds testable accessibility success criteria", "source.ce.wcag22"),
    ("iso29119_refresh", 2021, "ISO/IEC/IEEE 29119 testing parts were refreshed with current process and technique contracts", "source.ce.iso29119_4"),
    ("kani_contracts", 2024, "Kani contract verification connects Rust function contracts to bounded proofs", "source.ce.kani"),
    ("kani_playback", 2023, "Kani concrete playback turns proof counterexamples into executable tests", "source.ce.kani"),
    ("miri_provenance", 2022, "Miri strict-provenance checking strengthens executable unsafe-code oracles", "source.ce.miri"),
    ("loom_models", 2024, "Loom model instrumentation expands bounded interleaving tests for Rust concurrency", "source.ce.loom"),
    ("proptest_fork", 2024, "Proptest persistence and deterministic seeds improve counterexample replay", "source.ce.proptest"),
    ("bolero_unification", 2024, "Bolero unifies property, fuzz and bounded-model backends behind one harness", "source.ce.bolero"),
    ("libafl_modular", 2022, "LibAFL makes schedulers, observers, feedback and executors composable", "source.ce.libafl"),
    ("cargo_semver", 2022, "cargo-semver-checks derives Rust API compatibility queries from rustdoc data", "source.ce.cargo_semver_checks"),
    ("cargo_mutants", 2023, "cargo-mutants provides source-level mutation adequacy for Rust projects", "source.ce.cargo_mutants"),
    ("nextest_retries", 2022, "Nextest per-test retry and partition features expose flaky-test evidence", "source.ce.cargo_nextest"),
    ("iai_callgrind", 2022, "Iai-Callgrind offers instruction-count benchmarks less noisy than wall-clock timing", "source.ce.iai_callgrind"),
    ("foundationdb_determinism", 2021, "FoundationDB simulation practice demonstrates deterministic fault scheduling at system scale", "source.ce.foundationdb_sim"),
    ("chaos_mesh_workflows", 2022, "Chaos Mesh workflow and experiment CRDs make fault scenarios versionable", "source.ce.chaos_mesh"),
    ("acvp_automation", 2022, "ACVP automates cryptographic algorithm vector exchange and verdicts", "source.ce.nist_acvp"),
    ("nist_csf2", 2024, "NIST CSF 2.0 adds Govern and broadens assurance outcomes", "source.ce.nist_cyberframework2"),
    ("ssdf11", 2022, "NIST SSDF 1.1 connects secure-development practices to evidence tasks", "source.ce.nist_ssdf"),
    ("openapi311", 2024, "OpenAPI 3.1.1 clarifies JSON Schema alignment for contract tooling", "source.ce.openapi31"),
    ("asyncapi3", 2024, "AsyncAPI 3.0 separates operations and channels for event-interface conformance", "source.ce.asyncapi30"),
    ("arrow_integration", 2023, "Arrow integration JSON and IPC fixtures institutionalize cross-language compatibility testing", "source.ce.arrow_integration"),
    ("parquet_page_index", 2022, "Parquet testing corpora expanded cross-implementation coverage of modern encodings and indexes", "source.ce.parquet_testing"),
    ("iceberg_v3", 2025, "Iceberg format v3 makes newer row-lineage and variant semantics explicit qualification targets", "source.ce.iceberg_compat"),
    ("delta_kernel", 2023, "Delta Kernel creates a narrower protocol-engine conformance boundary", "source.ce.delta_protocol"),
    ("mlperf_power", 2022, "MLPerf expanded benchmark rules for power measurement and submission audit", "source.ce.mlperf"),
    ("conformal_mainstream", 2021, "Conformal prediction adoption makes empirical coverage a testable predictive guarantee", "source.ce.conformal_prediction"),
    ("reproducible_attestations", 2024, "Reproducible-build attestations combine bit equality with provenance evidence", "source.ce.repro_builds"),
]


def main() -> None:
    (ROOT / "schemas").mkdir(parents=True, exist_ok=True)

    sources = [rec(f"source.ce.{slug}", "source", title=title, url=url,
                   authority_scope=scope, source_kind=kind, publication_year=year,
                   retrieved_on=DATE, primary_or_official=True,
                   limitation="Authority is limited to the stated scope; citation is not executed qualification evidence.")
               for slug, title, url, scope, kind, year in SOURCE_DATA]

    contexts = []
    oracles = []
    techniques = []
    decisions = []
    proofs = []
    coverage = []
    for index, (slug, label, plane) in enumerate(CONTEXTS):
        cid = f"context.ce.{slug}"
        contexts.append(rec(cid, "test_context_family", label=label, assurance_plane=plane,
                            inside=["test-domain definition", "oracle selection", "coverage and receipt requirements"],
                            outside=["domain-semantic ownership", "provider implementation", "deployment authority"],
                            completion_claim=False))
        oracle_ids = []
        technique_ids = []
        for oslug, olabel, authority in ORACLE_TEMPLATES:
            oid = f"oracle.ce.{slug}.{oslug}"
            oracle_ids.append(oid)
            oracles.append(rec(oid, "oracle_contract", context_ref=cid, label=f"{label}: {olabel}",
                               authority_basis=authority, verdicts=["pass", "fail", "inconclusive", "invalid"],
                               requires_counterexample_on_fail=True,
                               cannot_establish=["registry completeness", "unscoped target equivalence", "future behavior"],
                               source_refs=[sources[(index + len(oracle_ids)) % len(sources)]["id"]]))
        for tslug, tlabel, population in TEST_TEMPLATES:
            tid = f"test.ce.{slug}.{tslug}"
            technique_ids.append(tid)
            techniques.append(rec(tid, "test_technique", context_ref=cid, label=f"{label}: {tlabel}",
                                  population_contract=population, requires_exact_subject=True,
                                  records_seed=tslug == "generated", records_environment=True,
                                  negative_twin_required=True, outcome_set=["pass", "fail", "inconclusive", "invalid"],
                                  source_refs=[sources[(index * 3 + len(technique_ids)) % len(sources)]["id"]]))
        decisions.append(rec(f"decision.ce.{slug}", "qualification_decision_point", context_ref=cid,
                             question=f"What evidence is sufficient to claim {label}?",
                             options=["mandatory gate", "risk-triggered gate", "advisory evidence", "not applicable with reason"],
                             authority="domain assurance owner", forbidden_default="infer pass from an absent failure",
                             invalidation_triggers=["law edition", "subject digest", "target occurrence", "configuration", "test population", "oracle edition"]))
        proofs.append(rec(f"proof.ce.{slug}", "proof_obligation", context_ref=cid,
                         claim=f"The exact scoped subject satisfies the declared {label} contract.",
                         acceptable_evidence=["checkable proof artifact", "executed test receipt", "independent appraisal receipt"],
                         unacceptable_evidence=["schema-valid declaration alone", "compiler success alone", "benchmark alone", "vendor documentation alone"],
                         failure_result="typed_refusal_or_unqualified", waiver_allowed=plane not in {"security", "semantics", "vertical"}))
        coverage.append(rec(f"coverage.ce.{slug}", "coverage_matrix_row", context_ref=cid,
                            oracle_refs=oracle_ids, test_refs=technique_ids,
                            required_axes=["semantic partitions", "boundary values", "states/transitions", "failure modes", "target matrix"],
                            current_evidence="taxonomy_only", qualification_effect="none"))

    libraries = [rec(f"library.ce.{slug}", "library_boundary", label=label, boundary_kind=kind,
                     purity=(kind == "pure"), owns=[label],
                     refuses=["implicit authority", "unversioned subject", "unscoped pass"],
                     decision_points_exposed=["policy edition", "evidence threshold", "invalidation policy"],
                     compiler_role="candidate boundary; implementation does not yet exist")
                 for slug, label, kind in LIBRARIES]

    innovations = [rec(f"innovation.ce.{slug}", "innovation", year=year, claim=claim,
                       source_refs=[source], non_llm=True,
                       qualification_implication="Candidate technique or evidence mechanism; adoption requires its own qualification.")
                   for slug, year, claim, source in INNOVATIONS]

    requirements = []
    offers = []
    mappings = []
    for i, (slug, label, plane) in enumerate(CONTEXTS[:24]):
        req_id = f"requirement.ce.{slug}"
        offer_id = f"offer.ce.harness.{slug}.candidate"
        requirements.append(rec(req_id, "qualification_requirement", context_ref=f"context.ce.{slug}",
                                exact_subject_required=True, independent_implementation_count=2 if slug in {"wire_protocol", "serialization", "cross_implementation"} else 1,
                                mandatory_proof_refs=[f"proof.ce.{slug}"],
                                coverage_ref=f"coverage.ce.{slug}", max_evidence_age_days=90,
                                waiver_policy="explicit authority, rationale, risk, expiry and revocation only"))
        offers.append(rec(offer_id, "qualification_offer", context_ref=f"context.ce.{slug}",
                           harness_boundary_ref=f"library.ce.{LIBRARIES[i % len(LIBRARIES)][0]}",
                           exact_artifact_identity=None, exact_target_occurrence=None,
                           evidence_receipt_refs=[], bindable=False,
                           refusal_reason="No exact executed occurrence receipt exists in this research corpus."))
        mappings.append(rec(f"mapping.ce.{slug}", "requirement_offer_mapping", requirement_ref=req_id,
                            offer_ref=offer_id, structural_match=True, semantically_qualified=False,
                            binding_eligible=False, gap="exact execution, oracle and occurrence evidence absent"))

    receipt_examples = [
        rec("receipt.ce.example.schema_only", "qualification_receipt", evidence_layer="schema_validation", outcome="pass", binding_effect="none", subject_digest="sha256:illustrative", target_occurrence_ref=None, oracle_ref=None, executed=False, independent=False),
        rec("receipt.ce.example.compile_only", "qualification_receipt", evidence_layer="compile_type_check", outcome="pass", binding_effect="none", subject_digest="sha256:illustrative", target_occurrence_ref=None, oracle_ref=None, executed=True, independent=False),
        rec("receipt.ce.example.law_unexecuted", "qualification_receipt", evidence_layer="semantic_law_proof", outcome="inconclusive", binding_effect="none", subject_digest="sha256:illustrative", target_occurrence_ref=None, oracle_ref="oracle.ce.algebraic_law.law", executed=False, independent=False),
        rec("receipt.ce.example.executed_missing_target", "qualification_receipt", evidence_layer="executed_test", outcome="inconclusive", binding_effect="none", subject_digest="sha256:illustrative", target_occurrence_ref=None, oracle_ref="oracle.ce.property_based.law", executed=True, independent=False),
        rec("receipt.ce.example.benchmark", "qualification_receipt", evidence_layer="benchmark", outcome="pass", binding_effect="performance_evidence_only", subject_digest="sha256:illustrative", target_occurrence_ref="target.illustrative.only", oracle_ref="oracle.ce.performance_latency.reference", executed=True, independent=False),
        rec("receipt.ce.example.observation", "qualification_receipt", evidence_layer="deployed_observation", outcome="inconclusive", binding_effect="none", subject_digest="sha256:illustrative", target_occurrence_ref="target.illustrative.only", oracle_ref=None, executed=True, independent=False),
        rec("receipt.ce.example.appraisal", "qualification_receipt", evidence_layer="independent_appraisal", outcome="inconclusive", binding_effect="none", subject_digest="sha256:illustrative", target_occurrence_ref="target.illustrative.only", oracle_ref=None, executed=False, independent=True),
        rec("receipt.ce.example.revoked", "qualification_receipt", evidence_layer="executed_test", outcome="invalid", binding_effect="none", subject_digest="sha256:illustrative", target_occurrence_ref="target.illustrative.only", oracle_ref="oracle.ce.replay.law", executed=True, independent=True, revoked=True),
    ]

    examples = [
        rec("example.ce.saccr.positive", "vertical_example", vertical="banking", analytical_case="SA-CCR exposure at default", subject="exact regulation edition + netting-set graph + deterministic calculator artifact", required_context_refs=["context.ce.counterparty_risk", "context.ce.numerical_accuracy", "context.ce.reconciliation", "context.ce.temporal"], result="unqualified", reason="No exact regulation edition, independently implemented oracle pair, test portfolio, or deployed target receipt is supplied."),
        rec("example.ce.saccr.negative_twin", "negative_twin", vertical="banking", forbidden_inference="same counterparty display name implies same legal entity or netting set", expected="refuse before calculation", catches="identity collapse can produce a numerically precise but legally false exposure"),
        rec("example.ce.acute_care.positive", "vertical_example", vertical="healthcare", analytical_case="temporal acute-care pathway and state-aware object-centric event analysis", subject="versioned temporal event/object graph, encounter-state semantics, code systems and pathway implementation", required_context_refs=["context.ce.acute_care", "context.ce.process_mining", "context.ce.temporal", "context.ce.predictive_validation"], result="unqualified", reason="No site-specific ground truth, temporal leakage audit, external validation or clinical authority appraisal is supplied."),
        rec("example.ce.acute_care.negative_twin", "negative_twin", vertical="healthcare", forbidden_inference="recording time or documentation order equals clinical occurrence order", expected="refuse causal/pathway claim", catches="temporal leakage and state reconstruction error survive schema and performance tests"),
    ]

    rust = [
        rec("rust.ce.identities", "rust_applicability", mechanism="newtypes and non-zero identifiers", can_enforce="artifact, target, occurrence, edition and digest are non-interchangeable", cannot_enforce="that an external identifier is truthful"),
        rec("rust.ce.typestate", "rust_applicability", mechanism="typestate", can_enforce="Candidate -> StructurallyValid -> SemanticallyChecked -> Executed -> Appraised transitions", cannot_enforce="that the oracle is authoritative"),
        rec("rust.ce.verdict", "rust_applicability", mechanism="closed enums", can_enforce="Pass | Fail | Inconclusive | Invalid | Waived remains total", cannot_enforce="correct real-world verdict"),
        rec("rust.ce.receipt", "rust_applicability", mechanism="immutable structs plus canonical serde boundary", can_enforce="receipt field presence and digestability", cannot_enforce="measurement authenticity"),
        rec("rust.ce.laws", "rust_applicability", mechanism="sealed traits and generic law suites", can_enforce="only governed law interfaces implement promotion hooks", cannot_enforce="domain completeness"),
        rec("rust.ce.generators", "rust_applicability", mechanism="Strategy/Arbitrary adapters", can_enforce="typed generators and reproducible seeds", cannot_enforce="population representativeness"),
        rec("rust.ce.effects", "rust_applicability", mechanism="effect ports and capability handles", can_enforce="pure qualification planning is separate from test execution", cannot_enforce="sandbox containment outside the process"),
        rec("rust.ce.no_unsafe", "rust_applicability", mechanism="unsafe isolation and Miri/fuzz gates", can_enforce="unsafe code is localized and evidence-required", cannot_enforce="absence of all undefined behavior"),
    ]

    evidence_layers = [
        rec("layer.ce.declaration", "evidence_layer", order=0, establishes="A claim was made in a fixed declaration.", does_not_establish="truth, executability or conformance", promotion_power="none"),
        rec("layer.ce.schema", "evidence_layer", order=1, establishes="The declaration has the required structural shape.", does_not_establish="type correctness or meaning", promotion_power="structural_only"),
        rec("layer.ce.compile", "evidence_layer", order=2, establishes="The exact artifact compiles/type-checks for the exact toolchain target.", does_not_establish="domain laws or runtime behavior", promotion_power="structural_only"),
        rec("layer.ce.semantic", "evidence_layer", order=3, establishes="A named semantic claim was proved or checked under explicit assumptions.", does_not_establish="behavior outside proof bounds or assumptions", promotion_power="semantic_claim_only"),
        rec("layer.ce.executed", "evidence_layer", order=4, establishes="Named tests ran on an exact artifact/environment/population.", does_not_establish="untested behavior or representative performance", promotion_power="scoped_test_only"),
        rec("layer.ce.benchmark", "evidence_layer", order=5, establishes="Measurements were observed under a benchmark protocol.", does_not_establish="semantic conformance or workload transferability", promotion_power="performance_claim_only"),
        rec("layer.ce.deployed", "evidence_layer", order=6, establishes="Behavior was observed at a deployed target occurrence.", does_not_establish="causality, future behavior or independent validation", promotion_power="occurrence_observation_only"),
        rec("layer.ce.appraisal", "evidence_layer", order=7, establishes="An independent named party appraised scoped evidence.", does_not_establish="universal correctness or perpetual validity", promotion_power="required_gate_when_declared"),
    ]

    population_axes = []
    for slug, label in [
        ("equivalence", "semantic equivalence classes"), ("boundaries", "exact and near-boundary values"),
        ("invalid", "invalid and malformed inputs"), ("states", "reachable and prohibited states"),
        ("transitions", "legal and illegal transitions"), ("sequences", "operation sequences and histories"),
        ("concurrency", "schedules and interleavings"), ("failures", "fault and recovery modes"),
        ("time", "clock, calendar, lateness and expiry"), ("scale", "cardinality and size orders"),
        ("skew", "frequency and key skew"), ("missing", "missingness and censoring mechanisms"),
        ("distribution", "population and deployment distributions"), ("slices", "risk and protected slices"),
        ("versions", "producer/consumer version pairs"), ("targets", "architectures and target occurrences"),
        ("config", "configuration feature combinations"), ("dependencies", "dependency and toolchain versions"),
        ("adversarial", "negative/adversarial twins"), ("historical", "replay and migration history"),
    ]:
        population_axes.append(rec(f"population.ce.{slug}", "population_axis", label=label,
                                   required_declaration=["included partitions", "excluded partitions", "sampling method", "coverage measure", "residual risk"],
                                   forbidden_claim="sampled observations imply exhaustive coverage"))

    verdict_rules = [
        rec("verdict.ce.pass", "verdict_rule", condition="all mandatory exact-scope gates pass and evidence is valid", result="pass", retry_effect="none"),
        rec("verdict.ce.fail", "verdict_rule", condition="a valid oracle produces a counterexample to a mandatory claim", result="fail", retry_effect="cannot erase prior counterexample"),
        rec("verdict.ce.timeout", "verdict_rule", condition="execution exceeds declared budget", result="inconclusive", retry_effect="new attempt is additional evidence"),
        rec("verdict.ce.flaky", "verdict_rule", condition="same scoped execution produces inconsistent outcomes", result="inconclusive", retry_effect="record every attempt and classify nondeterminism"),
        rec("verdict.ce.underpowered", "verdict_rule", condition="sample size/power is below declared requirement", result="inconclusive", retry_effect="increase justified sample; do not reinterpret"),
        rec("verdict.ce.stale", "verdict_rule", condition="evidence exceeds time or event freshness", result="invalid", retry_effect="requalify"),
        rec("verdict.ce.mismatch", "verdict_rule", condition="artifact, config, target, oracle or population identity mismatches", result="invalid", retry_effect="execute exact scope"),
        rec("verdict.ce.revoked", "verdict_rule", condition="authority revokes receipt or oracle", result="invalid", retry_effect="new authority decision and execution required"),
        rec("verdict.ce.waived", "verdict_rule", condition="authorized scoped waiver is active", result="waived_not_pass", retry_effect="waiver expires or is revoked independently"),
        rec("verdict.ce.unknown", "verdict_rule", condition="oracle has no determinate result", result="inconclusive", retry_effect="resolve oracle partiality"),
        rec("verdict.ce.nondeterministic_subject", "verdict_rule", condition="subject is intentionally nondeterministic", result="evaluate distributional/statistical contract", retry_effect="preserve seeds, traces and uncertainty"),
        rec("verdict.ce.environment_drift", "verdict_rule", condition="environment changes during execution", result="invalid", retry_effect="freeze or characterize environment"),
    ]

    independence_criteria = [
        rec("independence.ce.ownership", "independence_criterion", question="Are implementation decision authorities organizationally independent?", failure="shared owner weakens independence"),
        rec("independence.ce.code", "independence_criterion", question="Was code independently authored rather than ported or translated?", failure="shared code lineage disqualifies implementation independence"),
        rec("independence.ce.dependencies", "independence_criterion", question="Do implementations avoid a shared semantic kernel?", failure="shared decisive dependency creates correlated error"),
        rec("independence.ce.spec", "independence_criterion", question="Do both implement the normative specification rather than one copying the other?", failure="reference dependence is not independent agreement"),
        rec("independence.ce.tests", "independence_criterion", question="Were decisive tests independently constructed?", failure="shared fixtures can share blind spots"),
        rec("independence.ce.oracle", "independence_criterion", question="Is the adjudicating oracle independent of both implementations?", failure="implementation-as-oracle cannot settle disagreement"),
        rec("independence.ce.data", "independence_criterion", question="Are corroborating datasets/site populations genuinely external?", failure="resampled training/development data is internal validation"),
        rec("independence.ce.infrastructure", "independence_criterion", question="Are correlated toolchain/runtime failure modes disclosed?", failure="shared substrate limits assurance diversity"),
        rec("independence.ce.funding", "independence_criterion", question="Are conflicts, funding and incentives disclosed?", failure="undisclosed conflict blocks independent appraisal claim"),
        rec("independence.ce.reproduction", "independence_criterion", question="Can an independent party reproduce the receipt from retained artifacts?", failure="unreproducible appraisal remains limited"),
    ]

    composition_laws = [
        rec("composition.ce.assume_guarantee", "composition_law", premise="Each component guarantee is paired with explicit assumptions.", required_proof="Every upstream guarantee satisfies every downstream assumption."),
        rec("composition.ce.interface", "composition_law", premise="Interfaces have exact editions and carrier semantics.", required_proof="No implicit coercion, loss, default or ordering change."),
        rec("composition.ce.effects", "composition_law", premise="Effects are classified and authorized.", required_proof="Retries/replay do not duplicate non-idempotent effects."),
        rec("composition.ce.resources", "composition_law", premise="Resources and interference budgets are finite.", required_proof="Combined demand and contention stay within occurrence offers."),
        rec("composition.ce.time", "composition_law", premise="Clock, validity, recording, event and processing time are distinct.", required_proof="Composition preserves temporal law and lateness bounds."),
        rec("composition.ce.failure", "composition_law", premise="Each boundary declares failure and cancellation semantics.", required_proof="Failure propagation and compensation are total."),
        rec("composition.ce.security", "composition_law", premise="Trust boundaries and principals are explicit.", required_proof="No confused-deputy or privilege amplification path."),
        rec("composition.ce.privacy", "composition_law", premise="Purpose, consent and privacy budgets are explicit.", required_proof="Composition does not exceed allowed use or privacy loss."),
        rec("composition.ce.numerical", "composition_law", premise="Each numeric transform declares error and conditioning.", required_proof="Accumulated error remains within authority-set tolerance."),
        rec("composition.ce.statistical", "composition_law", premise="Study dependencies and multiplicity are explicit.", required_proof="Combined inference preserves declared error guarantees."),
        rec("composition.ce.version", "composition_law", premise="Multi-version pairs are qualified.", required_proof="Rolling states are covered, not inferred from endpoint versions."),
        rec("composition.ce.end_to_end", "composition_law", premise="All component proofs and boundaries are present.", required_proof="Execute integration negative twins; component pass alone cannot promote the composition."),
    ]

    waiver_contracts = [
        rec("waiver.ce.risk_acceptance", "waiver_contract", authority="named accountable risk owner", required=["failed/missing requirement", "scope", "rationale", "risk", "compensating controls", "issued_at", "expires_at", "revocation triggers"], prohibited=["conversion to pass", "inheritance by another occurrence", "perpetual expiry"]),
        rec("waiver.ce.emergency", "waiver_contract", authority="incident commander plus service owner", required=["incident reference", "minimal scope", "time limit", "rollback trigger", "post-event review"], prohibited=["silent production bypass", "automatic renewal"]),
        rec("waiver.ce.statistical", "waiver_contract", authority="study/domain authority", required=["underpowered limitation", "decision cost", "restricted claim", "expiry/new-data trigger"], prohibited=["claiming significance or equivalence"]),
        rec("waiver.ce.accessibility", "waiver_contract", authority="accessibility owner and product authority", required=["affected users", "alternative access", "remediation date", "support path"], prohibited=["automated-check pass as justification"]),
        rec("waiver.ce.security", "waiver_contract", authority="security risk owner", required=["threat", "exposure", "compensating controls", "monitoring", "expiry"], prohibited=["waiving mandatory law where policy forbids it"]),
        rec("waiver.ce.revocation", "waiver_contract", authority="original or superseding authority", required=["waiver reference", "effective time", "reason", "affected bindings"], prohibited=["deleting historical waiver evidence"]),
    ]

    state_machines = [rec("state_machine.ce.qualification", "qualification_state_machine",
        initial="candidate", terminal=["revoked", "invalid"],
        transitions=[
            {"from": "candidate", "command": "validate_structure", "to": "structurally_valid", "receipt": "schema receipt"},
            {"from": "structurally_valid", "command": "approve_laws", "to": "semantically_specified", "receipt": "law authority receipt"},
            {"from": "semantically_specified", "command": "execute_suite", "to": "executed", "receipt": "execution receipt"},
            {"from": "executed", "command": "independent_appraise", "to": "appraised", "receipt": "appraisal receipt"},
            {"from": "appraised", "command": "promote_exact_scope", "to": "qualified_for_exact_scope", "receipt": "qualification receipt"},
            {"from": "qualified_for_exact_scope", "command": "expire", "to": "expired", "receipt": "expiry event"},
            {"from": "qualified_for_exact_scope", "command": "revoke", "to": "revoked", "receipt": "revocation event"},
            {"from": "candidate", "command": "waive_scoped_gap", "to": "waived_for_exact_scope", "receipt": "waiver; never a pass"},
        ],
        forbidden=["schema_valid -> qualified", "benchmark_pass -> qualified", "retry_fail -> pass", "waived -> pass"]) ]

    gaps = [
        rec("gap.ce.no_actual_qualification", "gap", severity="constitutional", statement="No concrete library/provider/target occurrence is qualified by this corpus.", resolution="Execute exact scoped suites and issue independently checkable receipts."),
        rec("gap.ce.oracle_authority", "gap", severity="high", statement="Oracle authority is domain- and edition-specific and remains unadjudicated for most contexts.", resolution="Name accountable authority and published law edition per requirement."),
        rec("gap.ce.population", "gap", severity="high", statement="Test populations are taxonomy seeds, not demonstrated representative populations.", resolution="Publish population frames, generators, exclusions, power and residual risk."),
        rec("gap.ce.composition", "gap", severity="high", statement="Component passes do not yet compose into an end-to-end guarantee.", resolution="Prove assume/guarantee compatibility and test integration negative twins."),
        rec("gap.ce.two_impl", "gap", severity="high", statement="Independent implementation status cannot be inferred from different package names.", resolution="Appraise ownership, code lineage, shared dependencies, oracle independence and test independence."),
        rec("gap.ce.statistical", "gap", severity="high", statement="Universal tolerances and power thresholds do not exist.", resolution="Require estimand, error costs, alpha/beta, multiplicity, uncertainty and authority per study."),
        rec("gap.ce.flaky", "gap", severity="medium", statement="Retry policies can conceal nondeterministic failures.", resolution="Record every attempt, seeds, schedule, environment and classify flakiness separately from pass."),
        rec("gap.ce.accessibility", "gap", severity="medium", statement="Automated accessibility rules cannot establish full human accessibility.", resolution="Combine rules with assistive-technology and user-task appraisal."),
        rec("gap.ce.predictive", "gap", severity="high", statement="Predictive test performance cannot establish deployment utility or future stability.", resolution="External/temporal validation, calibration, shift monitoring and decision-utility evidence."),
        rec("gap.ce.vertical", "gap", severity="high", statement="Vertical law packs for SA-CCR and clinical pathways are illustrative only.", resolution="Bind exact authoritative editions, experts, cases and independent implementations."),
        rec("gap.ce.benchmark", "gap", severity="medium", statement="Benchmark scores are not semantic conformance and may not transfer workloads.", resolution="Preserve workload, target, environment, uncertainty and applicability evidence."),
        rec("gap.ce.waiver", "gap", severity="high", statement="No organization-specific waiver authorities or risk acceptances are supplied.", resolution="Configure named authority, scope, expiry, compensating controls and revocation."),
    ]

    metamodel = {
        "id": "san.conformance-evaluation-qualification-system", "edition": EDITION,
        "status": "candidate_research_contract", "completion_claim": False,
        "scope": "Executable laws, tests, appraisals and evidence receipts for promotion from candidate offer to scoped bindability.",
        "evidence_layers": ["declaration", "schema_validation", "compile_type_check", "semantic_law_proof", "executed_test", "benchmark", "deployed_observation", "independent_appraisal"],
        "qualification_states": ["candidate", "structurally_valid", "semantically_specified", "executed", "appraised", "qualified_for_exact_scope", "waived_for_exact_scope", "expired", "revoked", "invalid"],
        "verdicts": ["pass", "fail", "inconclusive", "invalid"],
        "constitutional_laws": [
            "Schema validity is not compilation; compilation is not semantic proof; semantic proof is not executed evidence.",
            "Executed test is not benchmark; benchmark is not deployed observation; observation is not independent appraisal.",
            "Every pass is scoped to exact subject artifact, dependencies, configuration, target occurrence, oracle edition, population and time.",
            "Absence of a failure is never evidence of a pass.",
            "Flaky, timed-out, underpowered, stale, mismatched or uncheckable evidence is inconclusive or invalid, never pass.",
            "A waiver is an expiring authority decision, not qualification evidence.",
            "A counterexample invalidates the matching universal claim until resolved, narrowed or explicitly waived.",
            "Two implementations count as independent only after code, dependency, owner, oracle and test-lineage appraisal.",
            "Component qualification composes only under proven assumptions, interfaces, interference budgets and integration laws.",
            "LLM or agent judgment may propose tests but cannot replace deterministic checks or accountable domain authority.",
            "Passing this corpus validator never qualifies a provider, target, library or analytical method."
        ],
        "upstream_alignment": [
            "research/domain_atlas/compiler/compiler-metamodel.json",
            "research/domain_atlas/compiler/proof-obligations.json",
            "research/domain_atlas/compiler/provider_target_registry/metamodel.json",
            "research/domain_atlas/compiler/binder_solver/metamodel.json"
        ]
    }

    receipt_schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema", "$id": "urn:san:conformance:qualification-receipt:1",
        "title": "Exact-scope qualification receipt", "type": "object", "additionalProperties": False,
        "required": ["receipt_id", "edition", "subject", "artifact_digest", "dependency_lock_digest", "configuration_digest", "target_occurrence", "oracle", "population", "execution", "verdict", "validity", "limitations", "evidence_objects", "invalidation_triggers"],
        "properties": {
            "receipt_id": {"type": "string", "minLength": 1}, "edition": {"type": "integer", "minimum": 1},
            "subject": {"type": "string"}, "artifact_digest": {"type": "string", "pattern": "^sha256:"},
            "dependency_lock_digest": {"type": "string", "pattern": "^sha256:"}, "configuration_digest": {"type": "string", "pattern": "^sha256:"},
            "target_occurrence": {"type": "string"}, "oracle": {"type": "object", "required": ["id", "edition", "authority"], "properties": {"id": {"type": "string"}, "edition": {"type": "integer"}, "authority": {"type": "string"}}},
            "population": {"type": "object", "required": ["definition", "size", "coverage", "seed_policy"], "properties": {"definition": {"type": "string"}, "size": {"type": "integer", "minimum": 0}, "coverage": {"type": "array", "items": {"type": "string"}}, "seed_policy": {"type": "string"}}},
            "execution": {"type": "object", "required": ["runner", "started_at", "ended_at", "environment_digest", "attempts"], "properties": {"runner": {"type": "string"}, "started_at": {"type": "string", "format": "date-time"}, "ended_at": {"type": "string", "format": "date-time"}, "environment_digest": {"type": "string"}, "attempts": {"type": "integer", "minimum": 1}}},
            "verdict": {"enum": ["pass", "fail", "inconclusive", "invalid"]},
            "validity": {"type": "object", "required": ["recorded_at", "expires_at", "revoked"], "properties": {"recorded_at": {"type": "string", "format": "date-time"}, "expires_at": {"type": "string", "format": "date-time"}, "revoked": {"type": "boolean"}}},
            "limitations": {"type": "array", "items": {"type": "string"}}, "evidence_objects": {"type": "array", "items": {"type": "string"}},
            "invalidation_triggers": {"type": "array", "minItems": 1, "items": {"type": "string"}},
            "independent_appraiser": {"type": ["string", "null"]}, "waiver_ref": {"type": ["string", "null"]}
        }
    }

    record_schema = {"$schema": "https://json-schema.org/draft/2020-12/schema", "type": "object",
                     "required": ["id", "kind", "edition", "status"], "properties": {
                         "id": {"type": "string", "pattern": "^[a-z][a-z0-9_.-]+$"},
                         "kind": {"type": "string", "minLength": 1}, "edition": {"type": "integer", "minimum": 1},
                         "status": {"type": "string", "minLength": 1}}, "additionalProperties": True}

    files = {
        "sources.jsonl": sources, "context-families.jsonl": contexts, "oracle-contracts.jsonl": oracles,
        "test-techniques.jsonl": techniques, "decision-points.jsonl": decisions,
        "proof-obligations.jsonl": proofs, "coverage-matrix.jsonl": coverage,
        "library-boundaries.jsonl": libraries, "innovations-2021-2026.jsonl": innovations,
        "requirements.jsonl": requirements, "offers.jsonl": offers, "requirement-offer-mappings.jsonl": mappings,
        "qualification-receipt-examples.jsonl": receipt_examples, "examples.jsonl": examples,
        "rust-applicability.jsonl": rust, "gaps.jsonl": gaps,
        "evidence-layer-contracts.jsonl": evidence_layers, "population-axes.jsonl": population_axes,
        "verdict-rules.jsonl": verdict_rules, "independence-criteria.jsonl": independence_criteria,
        "composition-laws.jsonl": composition_laws, "waiver-contracts.jsonl": waiver_contracts,
        "qualification-state-machines.jsonl": state_machines,
    }
    for name, rows in files.items():
        write_jsonl(ROOT / name, rows)
    write_json(ROOT / "metamodel.json", metamodel)
    write_json(ROOT / "qualification-receipt-contract.schema.json", receipt_schema)
    write_json(ROOT / "schemas" / "record.schema.json", record_schema)

    counts = {name: len(rows) for name, rows in files.items()}
    counts["oracle_test_decision_proof_records"] = len(oracles) + len(techniques) + len(decisions) + len(proofs)
    digests = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in files}
    manifest = {"id": "manifest.ce.v1", "edition": EDITION, "generated_on": DATE,
                "completion_claim": False, "actual_offer_qualified": False,
                "counts": counts, "sha256": digests,
                "thresholds": {"sources": 100, "contexts": 60, "oracle_test_decision_proof_records": 300,
                               "library_boundaries": 40, "innovations_2021_2026": 30, "unrelated_verticals": 2}}
    write_json(ROOT / "manifest.json", manifest)


if __name__ == "__main__":
    main()
