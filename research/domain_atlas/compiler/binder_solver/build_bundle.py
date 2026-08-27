#!/usr/bin/env python3
"""Deterministically generate the candidate binder/solver research bundle.

The generator is deliberately data-only: it performs no discovery and no solving.
It serializes reviewed research records in a stable order so a clean rebuild can be
byte-compared.  The companion validator checks the constitutional separation laws.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EDITION = 1
STATUS = "reviewed_candidate"
PROVIDER_TARGET_ROOT = ROOT.parent / "provider_target_registry"
MODEL_CLASS_ROOT = ROOT.parent / "model_class_adjudication"


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


PROVIDER_TARGET_INPUT_FILES = [
    "manifest.json",
    "concrete-offers.jsonl",
    "target-occurrences.jsonl",
    "qualification-receipts.jsonl",
    "compatibility-matrix.jsonl",
]
PROVIDER_TARGET_INPUT_DIGESTS = {
    name: hashlib.sha256((PROVIDER_TARGET_ROOT / name).read_bytes()).hexdigest()
    for name in PROVIDER_TARGET_INPUT_FILES
}
PROVIDER_TARGET_OFFERS = load_jsonl(PROVIDER_TARGET_ROOT / "concrete-offers.jsonl")
PROVIDER_TARGET_OCCURRENCES = load_jsonl(PROVIDER_TARGET_ROOT / "target-occurrences.jsonl")
PROVIDER_TARGET_QUALIFICATIONS = load_jsonl(PROVIDER_TARGET_ROOT / "qualification-receipts.jsonl")
PROVIDER_TARGET_COMPATIBILITY = load_jsonl(PROVIDER_TARGET_ROOT / "compatibility-matrix.jsonl")
MODEL_CLASS_INPUT_FILES = [
    "manifest.json",
    "model-classes.jsonl",
    "classification-traces.jsonl",
    "adjudication-results.jsonl",
]
MODEL_CLASS_INPUT_DIGESTS = {
    name: hashlib.sha256((MODEL_CLASS_ROOT / name).read_bytes()).hexdigest()
    for name in MODEL_CLASS_INPUT_FILES
}


def rec(record_id: str, record_kind: str, **values):
    return {"id": record_id, "record_kind": record_kind, "edition": EDITION, "status": STATUS, **values}


def source(source_id, title, publisher, source_kind, url, year, topics, limitation="Does not qualify a SAN binding or deployed occurrence."):
    return rec(
        source_id,
        "source",
        title=title,
        publisher=publisher,
        source_kind=source_kind,
        url=url,
        publication_or_live_year=year,
        accessed_at="2026-08-25",
        supports_topics=topics,
        authority_scope="Authoritative only for its named standard, implementation, or reported research result.",
        limitations=[limitation, "Does not establish this candidate corpus as complete."],
    )


# Primary/authoritative sources are intentionally diverse.  A solver implementation's
# documentation is evidence about that implementation, never about universal semantics.
SOURCES = [
    source("source.bind.smtlib.27", "SMT-LIB Standard 2.7", "SMT-LIB Initiative", "standard", "https://smt-lib.org/language.shtml", 2026, ["smt", "models", "unknown", "unsat_cores"]),
    source("source.bind.z3.guide", "Z3 Guide", "Microsoft Research", "official_documentation", "https://microsoft.github.io/z3guide/", 2026, ["smt", "models", "optimization"]),
    source("source.bind.z3.objectives", "Combining Objectives", "Microsoft Research", "official_documentation", "https://microsoft.github.io/z3guide/docs/optimization/combiningobjectives/", 2026, ["lexicographic", "pareto", "multiobjective"]),
    source("source.bind.cvc5.api", "cvc5 Solver API", "cvc5 Project", "official_documentation", "https://cvc5.github.io/docs/latest/api/cpp/classcvc5_1_1Solver.html", 2026, ["smt", "unsat_core", "proof"]),
    source("source.bind.cvc5.proofs", "cvc5 Proof Production", "cvc5 Project", "official_documentation", "https://cvc5.github.io/docs/latest/proofs/proofs.html", 2026, ["proof", "alethe", "checking"]),
    source("source.bind.cvc5.understanding", "Interfaces for Understanding cvc5", "cvc5 Project", "official_technical_article", "https://cvc5.github.io/blog/2024/04/15/interfaces-for-understanding-cvc5.html", 2024, ["unsat_core", "difficulty", "proof"]),
    source("source.bind.alethe", "Alethe Proof Format", "veriT Project", "official_specification", "https://verit.loria.fr/documentation/alethe-spec.pdf", 2022, ["smt_proof", "independent_checking"]),
    source("source.bind.drat", "DRAT-trim Proof Checker", "DRAT-trim Authors", "reference_checker", "https://github.com/marijnheule/drat-trim", 2023, ["sat_proof", "unsat"]),
    source("source.bind.lrat", "LRAT: Linear RAT Proofs", "University of Texas", "primary_research", "https://www.cs.utexas.edu/~marijn/publications/LRAT.pdf", 2017, ["sat_proof", "verified_checking"]),
    source("source.bind.cakelpr", "cake_lpr Verified Proof Checker", "CakeML Project", "reference_checker", "https://github.com/tanyongkiam/cake_lpr", 2024, ["verified_checker", "lrat", "lpr"]),
    source("source.bind.veripb", "VeriPB Proof Checker", "VeriPB Project", "reference_checker", "https://gitlab.com/MIAOresearch/software/VeriPB", 2026, ["pseudo_boolean", "optimization_proof"]),
    source("source.bind.maxsat.format", "MaxSAT Evaluation Rules and Formats", "MaxSAT Evaluation", "official_specification", "https://maxsat-evaluations.github.io/2024/rules.html", 2024, ["maxsat", "weighted_soft_constraints"]),
    source("source.bind.satcomp.rules", "SAT Competition 2024 Rules", "SAT Competition", "official_specification", "https://satcompetition.github.io/2024/rules.html", 2024, ["sat", "proof_requirement", "resource_limits"]),
    source("source.bind.varisat", "Varisat Manual", "Varisat Project", "official_documentation", "https://jix.github.io/varisat/manual/0.2.0/", 2026, ["rust", "sat", "proof_logging"]),
    source("source.bind.rustsat", "RustSAT API", "RustSAT Project", "official_documentation", "https://docs.rs/rustsat/latest/rustsat/", 2026, ["rust", "sat", "optimization", "encodings"]),
    source("source.bind.minizinc.handbook", "MiniZinc Handbook", "MiniZinc Project", "official_documentation", "https://docs.minizinc.dev/en/stable/", 2026, ["constraint_programming", "solver_independent_model"]),
    source("source.bind.minizinc.checker", "Automatic Solution Checking", "MiniZinc Project", "official_documentation", "https://docs.minizinc.dev/en/stable/checkers.html", 2026, ["solution_checker", "qualification"]),
    source("source.bind.minizinc.json", "MiniZinc JSON Stream", "MiniZinc Project", "official_documentation", "https://docs.minizinc.dev/en/stable/json-stream.html", 2026, ["machine_output", "solver_status"]),
    source("source.bind.ortools.cpsat", "CP-SAT Solver", "Google OR-Tools", "official_documentation", "https://developers.google.com/optimization/cp/cp_solver", 2026, ["constraint_programming", "integer_model"]),
    source("source.bind.ortools.release.9_15", "OR-Tools v9.15 release", "Google OR-Tools", "official_release", "https://github.com/google/or-tools/releases/tag/v9.15", 2026, ["linear_programming", "version_identity"]),
    source("source.bind.ortools.glop_status.9_15", "GLOP to MPSolver status mapping at v9.15", "Google OR-Tools", "official_source", "https://github.com/google/or-tools/blob/v9.15/ortools/linear_solver/proto_solver/glop_proto_solver.cc", 2026, ["linear_programming", "status_mapping", "no_strengthening"]),
    source("source.bind.ortools.scheduling", "Employee Scheduling with CP-SAT", "Google OR-Tools", "official_documentation", "https://developers.google.com/optimization/scheduling/employee_scheduling", 2026, ["scheduling", "constraints"]),
    source("source.bind.scip", "SCIP Documentation", "SCIP Optimization Suite", "official_documentation", "https://www.scipopt.org/doc/html/", 2026, ["constraint_integer_programming", "mip"]),
    source("source.bind.highs", "HiGHS Documentation", "HiGHS Project", "official_documentation", "https://ergo-code.github.io/HiGHS/dev/", 2026, ["linear_programming", "mip", "solver_status"]),
    source("source.bind.highs.release.1_15_1", "HiGHS v1.15.1 release", "HiGHS Project", "official_release", "https://github.com/ERGO-Code/HiGHS/releases/tag/v1.15.1", 2026, ["linear_programming", "version_identity"]),
    source("source.bind.highs.model_status", "HiGHS model-status enumeration", "HiGHS Project", "official_documentation", "https://ergo-code.github.io/HiGHS/stable/interfaces/python/enums/", 2026, ["linear_programming", "status_mapping"]),
    source("source.bind.osqp", "OSQP Documentation", "OSQP Project", "official_documentation", "https://osqp.org/docs/", 2026, ["quadratic_programming", "infeasibility_certificates"]),
    source("source.bind.coinor.cbc", "CBC User Guide", "COIN-OR", "official_documentation", "https://www.coin-or.org/Cbc/cbcuserguide.html", 2026, ["mip", "branch_and_cut"]),
    source("source.bind.goodlp", "good_lp Rust API", "good_lp Project", "official_documentation", "https://docs.rs/good_lp/latest/good_lp/", 2026, ["rust", "optimization_model", "backend_boundary"]),
    source("source.bind.alloy", "Alloy Language Reference", "AlloyTools", "language_specification", "https://alloytools.org/spec.html", 2026, ["relational_model", "bounded_analysis"]),
    source("source.bind.tlaplus", "TLA+ Language and Tools", "TLA+ Foundation", "official_documentation", "https://lamport.azurewebsites.net/tla/tla.html", 2026, ["state_machine", "model_checking"]),
    source("source.bind.apalache", "Apalache Documentation", "Apalache Project", "official_documentation", "https://apalache-mc.org/docs/", 2026, ["symbolic_model_checking", "counterexample"]),
    source("source.bind.spin", "SPIN Model Checker", "SPIN Project", "official_documentation", "https://spinroot.com/spin/Man/", 2026, ["model_checking", "counterexample"]),
    source("source.bind.lean", "Lean Reference Manual", "Lean Project", "language_specification", "https://lean-lang.org/doc/reference/latest/", 2026, ["proof", "dependent_types"]),
    source("source.bind.coq", "Rocq Reference Manual", "Rocq Project", "language_specification", "https://rocq-prover.org/doc/V8.20.0/refman/", 2024, ["proof_assistant", "certified_checker"]),
    source("source.bind.isabelle", "Isabelle Documentation", "Isabelle Project", "official_documentation", "https://isabelle.in.tum.de/documentation.html", 2026, ["proof_assistant", "code_generation"]),
    source("source.bind.cue.spec", "CUE Language Specification", "CUE Project", "language_specification", "https://cuelang.org/docs/reference/spec/", 2026, ["unification", "defaults", "constraints"]),
    source("source.bind.dhall.standard", "Dhall Language Standard", "Dhall Project", "language_specification", "https://github.com/dhall-lang/dhall-lang/tree/master/standard", 2026, ["total_configuration", "normalization"]),
    source("source.bind.nickel.manual", "Nickel User Manual", "Nickel Project", "official_documentation", "https://nickel-lang.org/user-manual/", 2026, ["contracts", "configuration", "merge"]),
    source("source.bind.jsonschema.core", "JSON Schema Core 2020-12", "JSON Schema Project", "standard", "https://json-schema.org/draft/2020-12/json-schema-core", 2022, ["schema", "vocabulary", "applicator"]),
    source("source.bind.jsonschema.validation", "JSON Schema Validation 2020-12", "JSON Schema Project", "standard", "https://json-schema.org/draft/2020-12/json-schema-validation", 2022, ["assertion", "annotation", "validation"]),
    source("source.bind.shacl", "Shapes Constraint Language", "W3C", "recommendation", "https://www.w3.org/TR/shacl/", 2017, ["shape_validation", "validation_report"]),
    source("source.bind.owl.profiles", "OWL 2 Profiles", "W3C", "recommendation", "https://www.w3.org/TR/owl2-profiles/", 2012, ["semantic_subsumption", "reasoning_profile"]),
    source("source.bind.rdf.semantics", "RDF 1.1 Semantics", "W3C", "recommendation", "https://www.w3.org/TR/rdf11-mt/", 2014, ["entailment", "interpretation"]),
    source("source.bind.semver", "Semantic Versioning 2.0.0", "SemVer Project", "specification", "https://semver.org/spec/v2.0.0.html", 2013, ["version_identity", "compatibility_claim"]),
    source("source.bind.cargo.resolver", "Cargo Dependency Resolution", "Rust Project", "official_documentation", "https://doc.rust-lang.org/cargo/reference/resolver.html", 2026, ["package_resolution", "features", "lockfile"]),
    source("source.bind.cargo.features", "Cargo Features", "Rust Project", "official_documentation", "https://doc.rust-lang.org/cargo/reference/features.html", 2026, ["feature_model", "unification"]),
    source("source.bind.cargo.lock", "Cargo.lock Format", "Rust Project", "official_documentation", "https://doc.rust-lang.org/cargo/reference/manifest.html#the-lock-file", 2026, ["lockfile", "exact_version"]),
    source("source.bind.pubgrub", "PubGrub Version Solving", "Dart Pub Project", "official_algorithm_description", "https://github.com/dart-lang/pub/blob/master/doc/solver.md", 2026, ["package_resolution", "conflict_explanation"]),
    source("source.bind.pubgrub.rs", "PubGrub Rust", "pubgrub-rs Project", "official_documentation", "https://github.com/pubgrub-rs/pubgrub", 2026, ["rust", "package_resolution", "error_derivation"]),
    source("source.bind.libsolv", "libsolv", "openSUSE", "official_documentation", "https://github.com/openSUSE/libsolv", 2026, ["package_resolution", "sat"]),
    source("source.bind.cudf", "CUDF Specification", "Mancoosi Project", "specification", "https://www.mancoosi.org/cudf/", 2010, ["package_universe", "request", "solution"]),
    source("source.bind.conda.matchspec", "Conda MatchSpec", "Conda Project", "official_documentation", "https://docs.conda.io/projects/conda/en/latest/dev-guide/api/conda/models/match_spec/index.html", 2026, ["package_constraints", "channel_identity"]),
    source("source.bind.spack.concretizer", "Spack Concretizer", "Spack Project", "official_documentation", "https://spack.readthedocs.io/en/latest/packaging_guide_creation.html#dependency-specs", 2026, ["concretization", "variants", "targets"]),
    source("source.bind.spack.asp", "Using Answer Set Programming for HPC Dependency Solving", "ACM TOMS", "primary_research", "https://doi.org/10.1145/3569953", 2023, ["asp", "package_resolution", "optimization"]),
    source("source.bind.nix.derivation", "Nix Derivations", "Nix Project", "official_specification", "https://nix.dev/manual/nix/latest/language/derivations", 2026, ["declared_inputs", "build_identity"]),
    source("source.bind.nix.store", "Nix Store Object Model", "Nix Project", "official_specification", "https://nix.dev/manual/nix/latest/store/store-object.html", 2026, ["content_address", "dependency_closure"]),
    source("source.bind.guix.substitutes", "Guix Substitutes", "GNU Guix", "official_documentation", "https://guix.gnu.org/manual/en/html_node/Substitutes.html", 2026, ["binary_substitution", "trust"]),
    source("source.bind.debian.policy", "Debian Policy: Dependencies", "Debian Project", "standard", "https://www.debian.org/doc/debian-policy/ch-relationships.html", 2026, ["package_relations", "conflicts"]),
    source("source.bind.npm.packagejson", "npm package.json", "npm", "official_documentation", "https://docs.npmjs.com/cli/v11/configuring-npm/package-json", 2026, ["package_constraints", "peer_dependencies"]),
    source("source.bind.maven.model", "Maven Model", "Apache Maven", "official_documentation", "https://maven.apache.org/ref/current/maven-model/maven.html", 2026, ["dependency_management", "profiles"]),
    source("source.bind.uv.resolver", "uv Resolver", "Astral", "official_documentation", "https://docs.astral.sh/uv/reference/resolver-internals/", 2026, ["python_resolution", "forks", "conflicts"]),
    source("source.bind.pep508", "PEP 508 Dependency Specification", "Python Steering Council", "standard", "https://peps.python.org/pep-0508/", 2015, ["dependency_specifier", "environment_marker"]),
    source("source.bind.pep440", "PEP 440 Version Identification", "Python Steering Council", "standard", "https://peps.python.org/pep-0440/", 2013, ["version_identity", "specifier"]),
    source("source.bind.tosca.20", "TOSCA 2.0", "OASIS", "committee_specification", "https://docs.oasis-open.org/tosca/TOSCA/v2.0/csd07/TOSCA-v2.0-csd07.html", 2024, ["requirement", "capability", "topology"]),
    source("source.bind.terraform.plan", "Terraform Planning", "HashiCorp", "official_documentation", "https://developer.hashicorp.com/terraform/cli/run", 2026, ["plan", "apply", "unknown_value"]),
    source("source.bind.terraform.schema", "Terraform Provider Schemas", "HashiCorp", "official_documentation", "https://developer.hashicorp.com/terraform/plugin/framework/handling-data/schemas", 2026, ["provider_schema", "type_shape"]),
    source("source.bind.terraform.protocol", "Terraform Plugin Protocol", "HashiCorp", "official_specification", "https://developer.hashicorp.com/terraform/plugin/terraform-plugin-protocol", 2026, ["provider_protocol", "capability_boundary"]),
    source("source.bind.pddl", "PDDL 2.1", "Journal of Artificial Intelligence Research", "primary_specification", "https://www.cs.cmu.edu/afs/cs/project/jair/pub/volume20/fox03a-html/JAIR.html", 2003, ["planning", "actions", "durative_constraints"]),
    source("source.bind.anml", "ANML Language Specification", "NASA Ames", "language_specification", "https://github.com/anml-lang/anml", 2026, ["planning", "temporal_constraints"]),
    source("source.bind.k8s.scheduler", "Kubernetes Scheduler", "Kubernetes", "official_documentation", "https://kubernetes.io/docs/concepts/scheduling-eviction/kube-scheduler/", 2026, ["feasibility", "scoring", "binding"]),
    source("source.bind.k8s.framework", "Kubernetes Scheduling Framework", "Kubernetes", "official_documentation", "https://kubernetes.io/docs/concepts/scheduling-eviction/scheduling-framework/", 2026, ["scheduling_passes", "reserve", "permit", "bind"]),
    source("source.bind.k8s.resources", "Resource Management for Pods", "Kubernetes", "official_documentation", "https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/", 2026, ["request", "limit", "allocation"]),
    source("source.bind.k8s.quota", "Resource Quotas", "Kubernetes", "official_documentation", "https://kubernetes.io/docs/concepts/policy/resource-quotas/", 2026, ["quota", "admission"]),
    source("source.bind.k8s.dra", "Dynamic Resource Allocation", "Kubernetes", "official_documentation", "https://kubernetes.io/docs/concepts/scheduling-eviction/dynamic-resource-allocation/", 2026, ["resource_claim", "allocation", "device_class"]),
    source("source.bind.nomad.scheduling", "How Nomad Scheduling Works", "HashiCorp", "official_documentation", "https://developer.hashicorp.com/nomad/docs/concepts/scheduling/how-scheduling-works", 2026, ["feasibility", "ranking", "allocation_plan"]),
    source("source.bind.nomad.placement", "Nomad Allocation Placement", "HashiCorp", "official_documentation", "https://developer.hashicorp.com/nomad/docs/concepts/scheduling/placement", 2026, ["hard_constraint", "soft_affinity"]),
    source("source.bind.slurm.priority", "Slurm Multifactor Priority", "SchedMD", "official_documentation", "https://slurm.schedmd.com/priority_multifactor.html", 2026, ["scheduling", "priority"]),
    source("source.bind.slurm.reservations", "Slurm Reservations", "SchedMD", "official_documentation", "https://slurm.schedmd.com/reservations.html", 2026, ["reservation", "resource"]),
    source("source.bind.linux.cgroup2", "Control Group v2", "Linux Kernel", "official_documentation", "https://docs.kernel.org/admin-guide/cgroup-v2.html", 2026, ["resource_control", "accounting"]),
    source("source.bind.oci.runtime", "OCI Runtime Specification", "Open Container Initiative", "standard", "https://github.com/opencontainers/runtime-spec", 2026, ["runtime_contract", "configuration"]),
    source("source.bind.rust.reference", "The Rust Reference", "Rust Project", "language_specification", "https://doc.rust-lang.org/reference/", 2026, ["types", "traits", "unsafe"]),
    source("source.bind.rust.typestate", "Rust API Guidelines: Type Safety", "Rust Project", "official_guidelines", "https://rust-lang.github.io/api-guidelines/type-safety.html", 2026, ["newtype", "invalid_state", "traits"]),
    source("source.bind.rust.error", "Rust Error Handling", "Rust Project", "official_book", "https://doc.rust-lang.org/book/ch09-00-error-handling.html", 2026, ["result", "failure_catalog"]),
    source("source.bind.rust.async", "Asynchronous Programming in Rust", "Rust Project", "official_book", "https://rust-lang.github.io/async-book/", 2026, ["async", "cancellation"]),
    source("source.bind.rust.salsa", "Salsa Book", "Salsa Project", "official_documentation", "https://salsa-rs.github.io/salsa/", 2026, ["incremental_query", "tracked_input"]),
    source("source.bind.rust.query", "rustc Query System", "Rust Project", "official_documentation", "https://rustc-dev-guide.rust-lang.org/query.html", 2026, ["incremental_query", "dependency_tracking"]),
    source("source.bind.rust.incremental", "Incremental Compilation in Detail", "Rust Project", "official_documentation", "https://rustc-dev-guide.rust-lang.org/queries/incremental-compilation-in-detail.html", 2026, ["fingerprint", "invalidation"]),
    source("source.bind.bazel.skyframe", "Skyframe", "Bazel Project", "official_documentation", "https://bazel.googlesource.com/bazel/+/master/site/en/reference/skyframe.md", 2026, ["incremental_evaluation", "dependency_graph"]),
    source("source.bind.bazel.remote", "Bazel Remote Caching", "Bazel Project", "official_documentation", "https://bazel.build/remote/caching", 2026, ["action_digest", "cache"]),
    source("source.bind.bazel.hermeticity", "Bazel Hermeticity", "Bazel Project", "official_documentation", "https://bazel.build/basics/hermeticity", 2026, ["declared_input", "reproducibility"]),
    source("source.bind.buck2.incremental", "Buck2 Incremental Computation", "Meta", "official_documentation", "https://buck2.build/docs/developers/architecture/dice/", 2026, ["incremental_computation", "dependency_graph"]),
    source("source.bind.differential", "Differential Dataflow", "Timely Dataflow Project", "official_documentation", "https://github.com/TimelyDataflow/differential-dataflow", 2026, ["incremental_dataflow", "arrangements"]),
    source("source.bind.dbsp", "DBSP: Automatic Incremental View Maintenance", "PVLDB", "primary_research", "https://www.vldb.org/pvldb/vol16/p1601-budiu.pdf", 2023, ["incremental_computation", "algebraic_derivative"]),
    source("source.bind.egg", "egg: Fast and Extensible Equality Saturation", "ACM POPL", "primary_research", "https://doi.org/10.1145/3434304", 2021, ["e_graph", "equivalence"]),
    source("source.bind.egglog", "Better Together: Datalog and Equality Saturation", "ACM PLDI", "primary_research", "https://doi.org/10.1145/3591239", 2023, ["e_graph", "datalog", "explanation"]),
    source("source.bind.substrait.types", "Substrait Type System", "Substrait Project", "official_specification", "https://substrait.io/types/type_system/", 2026, ["logical_type", "variation", "compatibility"]),
    source("source.bind.substrait.extensions", "Substrait Extensions", "Substrait Project", "official_specification", "https://substrait.io/extensions/", 2026, ["extension_identity", "semantic_contract"]),
    source("source.bind.arrow.format", "Apache Arrow Columnar Format", "Apache Software Foundation", "official_specification", "https://arrow.apache.org/docs/format/Columnar.html", 2026, ["physical_layout", "type"]),
    source("source.bind.protobuf", "Protocol Buffers Language Guide", "Google", "official_documentation", "https://protobuf.dev/programming-guides/proto3/", 2026, ["schema_evolution", "wire_contract"]),
    source("source.bind.avro", "Apache Avro Specification", "Apache Software Foundation", "official_specification", "https://avro.apache.org/docs/current/specification/", 2026, ["schema_resolution", "encoding"]),
    source("source.bind.smithy", "Smithy Specification", "Smithy Project", "official_specification", "https://smithy.io/2.0/spec/", 2026, ["model", "traits", "protocol_binding"]),
    source("source.bind.in_toto", "in-toto Specification", "in-toto Project", "standard", "https://github.com/in-toto/docs/blob/master/in-toto-spec.md", 2026, ["supply_chain", "link_metadata"]),
    source("source.bind.slsa", "SLSA 1.2", "OpenSSF", "standard", "https://slsa.dev/spec/v1.2/", 2025, ["build_provenance", "verification"]),
    source("source.bind.sigstore.bundle", "Sigstore Bundle Format", "Sigstore Project", "official_specification", "https://docs.sigstore.dev/about/bundle/", 2026, ["verification_material", "transparency_log"]),
    source("source.bind.tuf", "The Update Framework Specification", "TUF Project", "standard", "https://theupdateframework.github.io/specification/latest/", 2026, ["metadata_expiry", "delegation", "rollback_protection"]),
    source("source.bind.spdx.30", "SPDX 3.0", "Linux Foundation", "standard", "https://spdx.github.io/spdx-spec/v3.0/", 2024, ["artifact_identity", "dependency"]),
    source("source.bind.cyclonedx.16", "CycloneDX 1.6", "OWASP", "standard", "https://cyclonedx.org/docs/1.6/json/", 2024, ["bom", "dependency", "vulnerability"]),
    source("source.bind.osv", "OSV Schema", "OpenSSF", "official_specification", "https://ossf.github.io/osv-schema/", 2026, ["vulnerability_range", "affected_versions"]),
    source("source.bind.reproducible", "Reproducible Builds Definition", "Reproducible Builds Project", "community_specification", "https://reproducible-builds.org/docs/definition/", 2026, ["reproducibility", "environment"]),
    source("source.bind.satune", "SATune: A Study-Driven Auto-tuning Approach for Configurable SAT Solver", "ACM FSE", "primary_research", "https://doi.org/10.1145/3611643.3616311", 2023, ["solver_configuration", "qualification"]),
    source("source.bind.scenic", "Scenic 3.0", "Scenic Project", "official_documentation", "https://docs.scenic-lang.org/en/latest/", 2025, ["probabilistic_scenario", "falsification"]),
    source("source.bind.metacp", "MiniZinc Challenge 2026 Rules", "MiniZinc Challenge", "official_rules", "https://www.minizinc.org/challenge/2026/rules/", 2026, ["solver_qualification", "resource_budget", "checker"]),
]


CONTEXTS = [
    rec("context.bind.registry_snapshot", "bounded_context", name="Registry Snapshot", owns=["immutable registry inputs", "exact editions", "content digests"], excludes=["live provider discovery", "semantic alias inference"]),
    rec("context.bind.candidate_enumeration", "bounded_context", name="Candidate Enumeration", owns=["structural indexing", "deterministic candidate set"], excludes=["semantic proof", "ranking"]),
    rec("context.bind.semantic_compatibility", "bounded_context", name="Semantic Compatibility", owns=["subsumption assertions", "type/shape/operation/law implication"], excludes=["provider claims by name", "resource allocation"]),
    rec("context.bind.constraint_model", "bounded_context", name="Constraint Model", owns=["hard constraints", "soft preferences", "decision variables", "assumption literals"], excludes=["solver engine implementation", "runtime state"]),
    rec("context.bind.feasibility", "bounded_context", name="Feasibility Solving", owns=["sat/unsat/unknown", "models", "unsat cores"], excludes=["business ranking", "qualification"]),
    rec("context.bind.optimization", "bounded_context", name="Optimization and Ranking", owns=["declared objective order", "Pareto/lexicographic policy", "stable tie break"], excludes=["weakening hard constraints", "qualifying offers"]),
    rec("context.bind.qualification", "bounded_context", name="Qualification", owns=["test profile", "exact subject/environment", "receipts and validity"], excludes=["capacity reservation", "vendor reputation"]),
    rec("context.bind.resource_admission", "bounded_context", name="Resource Admission and Allocation", owns=["quota", "budget", "reservation", "allocation", "lease/fence"], excludes=["semantic selection", "runtime conformance"]),
    rec("context.bind.runtime_verification", "bounded_context", name="Runtime Verification", owns=["probe observations", "SLO/resource/policy receipts", "drift detection"], excludes=["compile-time assumptions", "post-hoc semantic rewriting"]),
    rec("context.bind.invalidation", "bounded_context", name="Invalidation and Rebinding", owns=["dependency graph", "trigger evaluation", "incremental rebind", "migration plan"], excludes=["silent lockfile update", "automatic destructive apply"]),
    rec("context.bind.explanation", "bounded_context", name="Diagnostics and Proof Trace", owns=["support sets", "rejections", "unsat cores", "proof status"], excludes=["claiming minimality without proof", "human-friendly text as canonical identity"]),
]


METAMODEL = {
    "metamodel_id": "metamodel.compiler.binder_solver.v1",
    "edition": 1,
    "status": STATUS,
    "completion_claim": "candidate_not_complete",
    "inputs": ["frozen_registry_snapshot", "ir_requirement_graph", "authority_and_decision_graph", "evidence_snapshot", "resource_budget_envelope"],
    "outputs": ["candidate_set", "constraint_instance", "feasibility_result", "ranked_alternatives", "binding_plan", "proof_trace", "typed_gaps", "invalidation_index"],
    "identity_tuple": ["namespace", "stable_id", "edition", "occurrence_id_if_runtime", "content_digest_separately"],
    "result_sum_type": ["bound", "partially_bound", "unsat", "unknown", "refused"],
    "non_collapsible_phases": [
        "structural_matching", "semantic_subsumption", "constraint_solving", "optimization_ranking",
        "qualification", "allocation_admission", "runtime_verification"
    ],
    "constraint_classes": ["identity", "edition", "lifecycle", "semantic", "type", "shape", "operation", "law", "configuration", "authority", "policy", "resource", "budget", "dependency", "evidence", "target", "migration"],
    "truth_values": ["proved_true", "proved_false", "unknown", "not_applicable"],
    "constitutional_laws": [
        "exact identity is not a display name, alias, version range, or digest",
        "registry absence is not evidence that a capability does not exist",
        "structural match is not semantic compatibility",
        "semantic equivalence is not representation compatibility",
        "a provider declaration is not a qualification receipt",
        "documentation, executed test, independent appraisal, qualification, and vertical acceptance are distinct evidence states",
        "a projected binder offer must preserve the exact upstream offer, artifact, occurrence, compatibility, assessment, and exclusion identities",
        "feasibility is not optimality and ranking is not qualification",
        "hard constraints are never weakened into preferences",
        "a timeout or unsupported theory is unknown, never unsat",
        "an unsat core is sufficient conflict evidence but not necessarily minimum",
        "resource capacity is not quota, admission, reservation, allocation, or lease",
        "compile-time evidence is scoped and can be invalidated at runtime",
        "a stale receipt cannot silently qualify a changed occurrence",
        "incremental rebinding must equal a clean rebind over the same snapshot",
        "migration intent is not authority to execute external effects",
        "formal model class must be deterministically adjudicated from a closed typed declaration before solver or simulator offer enumeration",
        "a business problem-family name, provider label, LLM proposal or agent plan is not model-class evidence",
        "a relaxation, linearization, discretization or encoding cannot change the required model class without equivalence or authority-approved loss evidence",
        "a model, LLM, or agent proposal cannot satisfy parsing, typing, constraint, qualification, authorization, execution, or receipt obligations",
        "deterministic selection requires declared objective order and stable final tie-break",
        "a positive example with absent offers or receipts terminates in typed gaps"
    ],
    "upstream_alignment": {
        "compiler_metamodel": "../compiler-metamodel.json",
        "proof_catalog": "../proof-obligations.json",
        "ir_lowering": "../ir_lowering/",
        "library_registry": "../library_registry/",
        "provider_target_registry": "../provider_target_registry/"
        , "model_class_adjudication": "../model_class_adjudication/"
    },
    "upstream_snapshot_digests": {
        "provider_target_registry": PROVIDER_TARGET_INPUT_DIGESTS,
        "model_class_adjudication": MODEL_CLASS_INPUT_DIGESTS,
    },
}


def write_json(path: Path, value):
    path.write_text(json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_jsonl(path: Path, values):
    ordered = sorted(values, key=lambda r: r["id"])
    path.write_text("".join(json.dumps(v, sort_keys=True, ensure_ascii=False) + "\n" for v in ordered), encoding="utf-8")


def main():
    ROOT.mkdir(parents=True, exist_ok=True)
    write_json(ROOT / "metamodel.json", METAMODEL)
    write_jsonl(ROOT / "sources.jsonl", SOURCES)
    write_jsonl(ROOT / "contexts.jsonl", CONTEXTS)

    # Remaining files are assembled below after their static record catalogs.
    for filename, values in CATALOGS.items():
        write_jsonl(ROOT / filename, values)

    schema_dir = ROOT / "schemas"
    schema_dir.mkdir(exist_ok=True)
    write_json(schema_dir / "record.schema.json", RECORD_SCHEMA)
    write_json(schema_dir / "example.schema.json", EXAMPLE_SCHEMA)

    outputs = ["metamodel.json", "sources.jsonl", "contexts.jsonl", *sorted(CATALOGS), "schemas/record.schema.json", "schemas/example.schema.json"]
    files = []
    for name in sorted(outputs):
        data = (ROOT / name).read_bytes()
        files.append({"path": name, "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)})
    counts = {"sources": len(SOURCES), "contexts": len(CONTEXTS)}
    counts.update({name.removesuffix(".jsonl"): len(values) for name, values in CATALOGS.items()})
    write_json(ROOT / "manifest.json", {"bundle_id": "bundle.compiler.binder_solver.v1", "edition": 1, "status": STATUS, "completion_claim": "candidate_not_complete", "counts": counts, "files": files})


PHASES = [
    rec("phase.bind.structural", "binding_phase", ordinal=0, name="Structural matching", accepts=["exact requirement", "frozen offer index"], proves=["field presence", "identity and edition resolvability", "syntactic arity/cardinality compatibility"], must_not=["infer alias", "claim semantic compatibility", "rank provider"]),
    rec("phase.bind.semantic", "binding_phase", ordinal=1, name="Semantic subsumption", accepts=["structural candidates", "authority-scoped relation assertions"], proves=["directional implication", "type/shape/operation/law compatibility", "authorized loss"], must_not=["treat name equality as meaning", "invent ontology mappings"]),
    rec("phase.bind.constraints", "binding_phase", ordinal=2, name="Constraint solving", accepts=["hard constraints", "decision domains", "assumption literals"], proves=["sat model or checkable unsat evidence"], must_not=["score alternatives", "call unknown unsat"]),
    rec("phase.bind.optimization", "binding_phase", ordinal=3, name="Optimization and ranking", accepts=["feasible models", "authority-owned objective law"], proves=["objective values", "dominance or lexicographic comparison", "stable tie break"], must_not=["soften hard constraints", "hide rejected feasible models"]),
    rec("phase.bind.qualification", "binding_phase", ordinal=4, name="Qualification", accepts=["selected candidate", "qualification profile", "exact subject and target"], proves=["test execution scope", "pass/fail/unknown receipt", "evidence validity"], must_not=["promote documentation to receipt", "generalize beyond tested domain"]),
    rec("phase.bind.allocation", "binding_phase", ordinal=5, name="Allocation and admission", accepts=["qualified plan", "live quota/budget/capacity snapshot"], proves=["admission", "reservation", "allocation", "lease/fence"], must_not=["infer capacity from quota", "reserve without release law"]),
    rec("phase.bind.runtime", "binding_phase", ordinal=6, name="Runtime verification", accepts=["binding plan", "deployment occurrence", "runtime probes"], proves=["actual conformance", "resource/SLO/policy observations", "drift state"], must_not=["rewrite compiled semantics", "silently tolerate invalidation"]),
]

CONSTRAINT_KINDS = [
    rec("constraint.bind.identity.exact", "constraint_kind", class_="identity", hardness="hard", semantics="A reference resolves only to the exact stable identity in the frozen snapshot.", encoding="finite_domain_equality", diagnostic="diagnostic.bind.e1001"),
    rec("constraint.bind.edition.exact", "constraint_kind", class_="edition", hardness="hard", semantics="Required and offered editions satisfy an explicitly named compatibility relation; range overlap is insufficient.", encoding="relation_atom", diagnostic="diagnostic.bind.e1002"),
    rec("constraint.bind.lifecycle.allowed", "constraint_kind", class_="lifecycle", hardness="hard", semantics="Selected subjects are not revoked, withdrawn, expired, or forbidden in scope.", encoding="finite_enum", diagnostic="diagnostic.bind.e1003"),
    rec("constraint.bind.semantic.subsumption", "constraint_kind", class_="semantic", hardness="hard", semantics="Offer guarantee entails the requirement in the required direction under an authority-scoped assertion.", encoding="entailment_receipt", diagnostic="diagnostic.bind.e1201"),
    rec("constraint.bind.type.compatibility", "constraint_kind", class_="type", hardness="hard", semantics="Input/output value domains, nullability, partiality, units, and numeric postures are compatible.", encoding="typed_relation", diagnostic="diagnostic.bind.e1202"),
    rec("constraint.bind.shape.compatibility", "constraint_kind", class_="shape", hardness="hard", semantics="Cardinality, keys, order, nesting, topology, grain and change shape meet the requirement.", encoding="shape_predicate", diagnostic="diagnostic.bind.e1203"),
    rec("constraint.bind.operation.signature", "constraint_kind", class_="operation", hardness="hard", semantics="Every operation port and refusal/failure contract is satisfied.", encoding="port_unification_plus_laws", diagnostic="diagnostic.bind.e1204"),
    rec("constraint.bind.law.implication", "constraint_kind", class_="law", hardness="hard", semantics="Required pre/postconditions, algebraic laws, loss bounds and guarantees are entailed.", encoding="proof_obligation", diagnostic="diagnostic.bind.e1205"),
    rec("constraint.bind.configuration.total", "constraint_kind", class_="configuration", hardness="hard", semantics="Every decision point has one authorized concrete value or a typed unresolved state.", encoding="exactly_one_plus_precedence", diagnostic="diagnostic.bind.e1301"),
    rec("constraint.bind.authority.valid", "constraint_kind", class_="authority", hardness="hard", semantics="The value, override, waiver or migration is selected by valid non-revoked authority in scope.", encoding="validity_interval_and_scope", diagnostic="diagnostic.bind.e1302"),
    rec("constraint.bind.policy.precedence", "constraint_kind", class_="policy", hardness="hard", semantics="Applicable policies yield a deterministic non-conflicting decision under declared precedence.", encoding="stratified_rules", diagnostic="diagnostic.bind.e1303"),
    rec("constraint.bind.resource.finite", "constraint_kind", class_="resource", hardness="hard", semantics="Worst-case or authority-approved bounded demand fits a qualified offer and capacity posture.", encoding="linear_or_finite_arithmetic", diagnostic="diagnostic.bind.e1401"),
    rec("constraint.bind.budget.hard", "constraint_kind", class_="budget", hardness="hard", semantics="Precharged monetary, energy, time, privacy and retry budgets cannot be exceeded by the admitted plan.", encoding="multi_dimensional_inequality", diagnostic="diagnostic.bind.e1402"),
    rec("constraint.bind.dependency.closure", "constraint_kind", class_="dependency", hardness="hard", semantics="Exact transitive artifact/feature/target/license/vulnerability closure is feasible.", encoding="package_sat", diagnostic="diagnostic.bind.e1501"),
    rec("constraint.bind.evidence.current", "constraint_kind", class_="evidence", hardness="hard", semantics="Required receipt is exact-scope, passing, unexpired, unrevoked and unaffected by an invalidation trigger.", encoding="temporal_scope_predicate", diagnostic="diagnostic.bind.e1601"),
    rec("constraint.bind.target.compatible", "constraint_kind", class_="target", hardness="hard", semantics="ABI, architecture, OS/runtime, accelerator, locale/time and representation requirements match the target occurrence.", encoding="target_profile_entailment", diagnostic="diagnostic.bind.e1602"),
    rec("constraint.bind.migration.safe", "constraint_kind", class_="migration", hardness="hard", semantics="Existing state/in-flight work has an authorized, reversible-or-explicitly-irreversible transition plan.", encoding="state_transition_obligation", diagnostic="diagnostic.bind.e1701"),
    rec("constraint.bind.preference.cost", "constraint_kind", class_="cost_preference", hardness="soft", semantics="Minimize declared total cost only among hard-feasible candidates.", encoding="objective", diagnostic="diagnostic.bind.w2001"),
    rec("constraint.bind.preference.portability", "constraint_kind", class_="portability_preference", hardness="soft", semantics="Prefer offers with independently qualified substitutions when authority declares that objective.", encoding="objective", diagnostic="diagnostic.bind.w2002"),
]

ALGORITHMS = [
    rec("algorithm.bind.exact_index", "algorithm", phase_ref="phase.bind.structural", inputs=["sorted requirements", "sorted offer index"], outputs=["candidate edges", "rejection reasons"], determinism="lexical stable identity and edition order", partiality="unknown registry kinds become gaps", evidence_refs=["source.bind.tosca.20", "source.bind.terraform.schema"]),
    rec("algorithm.bind.subsumption", "algorithm", phase_ref="phase.bind.semantic", inputs=["candidate edges", "canonical relation assertions"], outputs=["compatibility claims", "proof obligations"], determinism="stratified relation evaluation", partiality="unsupported or undecidable profile is unknown", evidence_refs=["source.bind.owl.profiles", "source.bind.shacl", "source.bind.cue.spec"]),
    rec("algorithm.bind.csp", "algorithm", phase_ref="phase.bind.constraints", inputs=["finite domains", "constraint atoms"], outputs=["model", "unsat", "unknown"], determinism="backend-independent canonical instance plus checked output", partiality="timeout/incomplete theory is unknown", evidence_refs=["source.bind.minizinc.handbook", "source.bind.minizinc.checker"]),
    rec("algorithm.bind.sat_smt", "algorithm", phase_ref="phase.bind.constraints", inputs=["named hard assertions", "theory profile"], outputs=["model or unsat proof/core or unknown"], determinism="canonical assertion order; independent checker where available", partiality="solver status retained exactly", evidence_refs=["source.bind.smtlib.27", "source.bind.cvc5.proofs", "source.bind.drat"]),
    rec("algorithm.bind.pubgrub", "algorithm", phase_ref="phase.bind.constraints", inputs=["package/edition incompatibilities", "locked preferences"], outputs=["resolved closure or incompatibility derivation"], determinism="explicit version/source ordering", partiality="ecosystem semantics stay adapter-owned", evidence_refs=["source.bind.pubgrub", "source.bind.cargo.resolver"]),
    rec("algorithm.bind.asp_concretizer", "algorithm", phase_ref="phase.bind.constraints", inputs=["variants", "architectures", "dependencies", "preferences"], outputs=["concrete build DAG", "model"], determinism="canonical facts and explicit optimization priorities", partiality="only modeled compatibility is considered", evidence_refs=["source.bind.spack.asp", "source.bind.spack.concretizer"]),
    rec("algorithm.bind.lexicographic", "algorithm", phase_ref="phase.bind.optimization", inputs=["feasible candidates", "ordered objectives"], outputs=["ranked models", "objective vector"], determinism="objective order then stable identity", partiality="missing objective authority refuses ranking", evidence_refs=["source.bind.z3.objectives", "source.bind.nomad.scheduling"]),
    rec("algorithm.bind.pareto", "algorithm", phase_ref="phase.bind.optimization", inputs=["feasible candidates", "objective definitions"], outputs=["nondominated frontier"], determinism="frontier sorted by canonical objective tuple and identity", partiality="does not choose one member without selection authority", evidence_refs=["source.bind.z3.objectives", "source.bind.highs"]),
    rec("algorithm.bind.unsat_core", "algorithm", phase_ref="phase.bind.constraints", inputs=["named assertions", "unsat result"], outputs=["sufficient conflicting assumption set"], determinism="canonicalized returned set plus checker receipt", partiality="core not claimed minimum unless minimized and proved", evidence_refs=["source.bind.smtlib.27", "source.bind.cvc5.understanding"]),
    rec("algorithm.bind.incremental_query", "algorithm", phase_ref="phase.bind.runtime", inputs=["tracked snapshots", "dependency keys", "prior receipts"], outputs=["dirty subgraph", "recomputed results"], determinism="must byte-equal clean evaluation for same inputs", partiality="unknown dependency invalidates conservatively", evidence_refs=["source.bind.rust.salsa", "source.bind.rust.incremental", "source.bind.bazel.skyframe"]),
]

PASSES = [
    rec("pass.bind.freeze_inputs", "compiler_pass", ordinal=0, phase_ref="phase.bind.structural", consumes=["registry URIs", "IR graph"], produces=["content-addressed frozen snapshots"], refusals=["mutable input", "missing edition", "digest mismatch"], preserves=["stable identity distinct from digest"]),
    rec("pass.bind.resolve_identities", "compiler_pass", ordinal=1, phase_ref="phase.bind.structural", consumes=["frozen snapshot", "references"], produces=["resolved identities", "typed gaps"], refusals=["alias-only reference", "ambiguous edition"], preserves=["source anchors", "authority"]),
    rec("pass.bind.enumerate_candidates", "compiler_pass", ordinal=2, phase_ref="phase.bind.structural", consumes=["requirements", "offers"], produces=["candidate/rejection graph"], refusals=["none; empty set is data"], preserves=["all candidates and rejections"]),
    rec("pass.bind_prove_semantics", "compiler_pass", ordinal=3, phase_ref="phase.bind.semantic", consumes=["candidate graph", "semantic assertions"], produces=["entailed, contradicted or unknown edges"], refusals=["unsupported inference profile", "missing authority"], preserves=["direction and information loss"]),
    rec("pass.bind_build_constraints", "compiler_pass", ordinal=4, phase_ref="phase.bind.constraints", consumes=["compatible edges", "decisions", "budgets"], produces=["named canonical constraint instance"], refusals=["untyped constraint", "hardness unspecified"], preserves=["origin/support set per atom"]),
    rec("pass.bind_solve_hard", "compiler_pass", ordinal=5, phase_ref="phase.bind.constraints", consumes=["canonical constraint instance"], produces=["sat model, unsat evidence, or unknown"], refusals=["backend cannot represent exact domain"], preserves=["solver status and limits"]),
    rec("pass.bind_explain_unsat", "compiler_pass", ordinal=6, phase_ref="phase.bind.constraints", consumes=["unsat result", "named atoms"], produces=["core", "human projection", "repair candidates"], refusals=["unchecked proof"], preserves=["core IDs; repair is advisory"]),
    rec("pass.bind_rank_feasible", "compiler_pass", ordinal=7, phase_ref="phase.bind.optimization", consumes=["feasible models", "objective authority"], produces=["rank/frontier", "rejected alternatives"], refusals=["missing objective order", "incomparable units"], preserves=["hard feasibility"]),
    rec("pass.bind_plan_qualification", "compiler_pass", ordinal=8, phase_ref="phase.bind.qualification", consumes=["ranked candidates", "required proof profiles"], produces=["qualification executions or typed gaps"], refusals=["unidentified artifact/target/config"], preserves=["test domain and checker identity"]),
    rec("pass.bind_check_receipts", "compiler_pass", ordinal=9, phase_ref="phase.bind.qualification", consumes=["qualification receipts"], produces=["qualified/rejected/unknown candidates"], refusals=["stale", "scope mismatch", "uncheckable"], preserves=["raw receipt and limitations"]),
    rec("pass.bind_admit_resources", "compiler_pass", ordinal=10, phase_ref="phase.bind.allocation", consumes=["qualified physical plan", "quota/budget/capacity snapshots"], produces=["admission result"], refusals=["budget breach", "quota denial", "capacity unknown"], preserves=["separate truth roles"]),
    rec("pass.bind_reserve_allocate", "compiler_pass", ordinal=11, phase_ref="phase.bind.allocation", consumes=["admitted demands"], produces=["reservation", "allocation", "lease/fence"], refusals=["race lost", "fence unavailable"], preserves=["release/expiry obligation"]),
    rec("pass.bind_emit_plan", "compiler_pass", ordinal=12, phase_ref="phase.bind.runtime", consumes=["qualified/admitted bindings"], produces=["effect-free binding plan", "proof trace"], refusals=["blocking gap"], preserves=["no external mutation authority"]),
    rec("pass.bind_verify_runtime", "compiler_pass", ordinal=13, phase_ref="phase.bind.runtime", consumes=["deployment occurrence", "runtime probes"], produces=["verification receipts", "drift signals"], refusals=["unobservable guarantee"], preserves=["compiled contract"]),
    rec("pass.bind_invalidate", "compiler_pass", ordinal=14, phase_ref="phase.bind.runtime", consumes=["change event", "dependency index"], produces=["invalidated claims", "requalification/rebind queue"], refusals=["none; unknown scope invalidates conservatively"], preserves=["prior binding history"]),
    rec("pass.bind_rebind_incremental", "compiler_pass", ordinal=15, phase_ref="phase.bind.runtime", consumes=["dirty subgraph", "new frozen snapshots"], produces=["replacement plan", "migration diff"], refusals=["clean-rebuild mismatch", "migration authority absent"], preserves=["unaffected receipts only when trigger-safe"]),
]

DIAGNOSTICS = [
    rec("diagnostic.bind.e1001", "diagnostic", severity="error", title="Unknown exact identity", explanation="A display name, alias or missing registry record cannot be bound.", repair=["supply exact stable identity and edition", "adjudicate an alias relation with evidence"]),
    rec("diagnostic.bind.e1002", "diagnostic", severity="error", title="Edition relation absent", explanation="Version strings or overlapping ranges do not prove compatibility.", repair=["provide editioned compatibility relation and evidence"]),
    rec("diagnostic.bind.e1003", "diagnostic", severity="error", title="Lifecycle forbids subject", explanation="Candidate is revoked, withdrawn, expired or forbidden in this scope.", repair=["select a permitted edition", "obtain authorized waiver if policy allows"]),
    rec("diagnostic.bind.e1201", "diagnostic", severity="error", title="Semantic entailment unknown", explanation="Structural similarity does not establish directional subsumption.", repair=["provide authority-scoped semantic relation", "add exact conformance proof"]),
    rec("diagnostic.bind.e1202", "diagnostic", severity="error", title="Type contract incompatible", explanation="Value, nullability, unit, uncertainty or partiality posture differs.", repair=["insert an explicit authorized adapter", "choose compatible offer"]),
    rec("diagnostic.bind.e1203", "diagnostic", severity="error", title="Shape contract incompatible", explanation="Grain, keys, order, nesting, topology or cardinality cannot be preserved.", repair=["declare an authorized reshape and loss contract"]),
    rec("diagnostic.bind.e1204", "diagnostic", severity="error", title="Operation signature not offered", explanation="Required port/refusal/failure behavior is absent.", repair=["supply an exact operation offer"]),
    rec("diagnostic.bind.e1205", "diagnostic", severity="error", title="Required law not proved", explanation="API compatibility does not prove the semantic law.", repair=["execute or provide an independently checkable law oracle"]),
    rec("diagnostic.bind.e1301", "diagnostic", severity="error", title="Decision unresolved", explanation="A required configuration has no authorized concrete value.", repair=["bind by the declared authority", "remove requirement explicitly"]),
    rec("diagnostic.bind.e1302", "diagnostic", severity="error", title="Authority missing or revoked", explanation="The proposed value or override has no valid authority in scope.", repair=["provide scoped delegation and validity evidence"]),
    rec("diagnostic.bind.e1303", "diagnostic", severity="error", title="Policy conflict", explanation="Applicable hard policies have no deterministic precedence result.", repair=["adjudicate precedence; optimizer may not decide policy"]),
    rec("diagnostic.bind.e1401", "diagnostic", severity="error", title="Resource infeasible or unbounded", explanation="Demand is unbounded or exceeds an exact qualified resource offer.", repair=["bound demand", "change algorithm", "supply qualified capacity"]),
    rec("diagnostic.bind.e1402", "diagnostic", severity="error", title="Finite budget exceeded", explanation="At least one hard budget dimension is exceeded.", repair=["reduce demand", "increase budget through its authority"]),
    rec("diagnostic.bind.e1501", "diagnostic", severity="error", title="Dependency closure unsatisfied", explanation="Exact artifact/feature/target/license/vulnerability constraints conflict.", repair=["inspect incompatibility derivation or unsat core"]),
    rec("diagnostic.bind.e1601", "diagnostic", severity="error", title="Qualification receipt unavailable", explanation="Documentation or stale/mismatched evidence cannot qualify the candidate.", repair=["execute qualification on exact artifact, target and configuration"]),
    rec("diagnostic.bind.e1602", "diagnostic", severity="error", title="Target occurrence unsupported", explanation="Target profile or occurrence-scoped evidence does not satisfy requirements.", repair=["qualify a target occurrence"]),
    rec("diagnostic.bind.e1701", "diagnostic", severity="error", title="Migration not safe or authorized", explanation="Existing state/in-flight work lacks a valid transition disposition.", repair=["supply migration, compensation and authority records"]),
    rec("diagnostic.bind.e1801", "diagnostic", severity="error", title="Solver returned unknown", explanation="Timeout, resource exhaustion or unsupported theory is not unsatisfiability.", repair=["preserve unknown; use a qualified alternate checker/backend"]),
    rec("diagnostic.bind.e1802", "diagnostic", severity="error", title="Incremental/clean mismatch", explanation="Incremental rebinding differs from a clean bind on identical snapshots.", repair=["invalidate the incremental cache and fix dependency tracking"]),
    rec("diagnostic.bind.w2001", "diagnostic", severity="warning", title="Cost preference unavailable", explanation="Cost evidence is missing or incomparable; no cost ranking can be made.", repair=["provide unit/valid-time scoped cost evidence"]),
    rec("diagnostic.bind.w2002", "diagnostic", severity="warning", title="Portability objective withheld", explanation="Independent qualified substitution evidence is absent.", repair=["qualify two independent implementations"]),
]

PROOF_CONTRACTS = [
    rec("proof.bind.snapshot", "proof_contract", claim="All compiler inputs are immutable, exact-edition and digest-verified.", phase_ref="phase.bind.structural", checker="independent digest and identity checker", failure="diagnostic.bind.e1001"),
    rec("proof.bind.identity_edition", "proof_contract", claim="Every selected subject resolves to one exact identity and edition under an explicit compatibility relation.", phase_ref="phase.bind.structural", checker="registry reference checker", failure="diagnostic.bind.e1002"),
    rec("proof.bind.candidate_completeness_snapshot", "proof_contract", claim="All offers in the frozen snapshot satisfying the structural index predicate were enumerated.", phase_ref="phase.bind.structural", checker="reference enumeration implementation", failure="diagnostic.bind.e1001"),
    rec("proof.bind.semantic_subsumption", "proof_contract", claim="Each selected offer entails every required semantic, type, shape, operation and law contract in the required direction.", phase_ref="phase.bind.semantic", checker="profile-specific entailment/checker receipts", failure="diagnostic.bind.e1201"),
    rec("proof.bind.loss_authority", "proof_contract", claim="Every non-injective adapter has finite loss and authority to incur it.", phase_ref="phase.bind.semantic", checker="adapter law oracle plus authority checker", failure="diagnostic.bind.e1205"),
    rec("proof.bind.hard_constraint_preservation", "proof_contract", claim="Optimization did not weaken, omit or reinterpret any hard constraint.", phase_ref="phase.bind.optimization", checker="constraint-set digest equality", failure="diagnostic.bind.e1303"),
    rec("proof.bind.feasible_model", "proof_contract", claim="The candidate assignment satisfies all named hard constraints.", phase_ref="phase.bind.constraints", checker="independent model checker", failure="diagnostic.bind.e1801"),
    rec("proof.bind.unsat", "proof_contract", claim="The named hard constraint instance is unsatisfiable.", phase_ref="phase.bind.constraints", checker="independent proof checker or explicitly limited core validation", failure="diagnostic.bind.e1801"),
    rec("proof.bind.unknown_preserved", "proof_contract", claim="Every incomplete/timeout/unsupported result remains unknown and blocks claims that require proof.", phase_ref="phase.bind.constraints", checker="status transition validator", failure="diagnostic.bind.e1801"),
    rec("proof.bind.objective_authority", "proof_contract", claim="Objective set, order, units, aggregation and tie-break have valid authority.", phase_ref="phase.bind.optimization", checker="decision/authority validator", failure="diagnostic.bind.e1302"),
    rec("proof.bind.rank", "proof_contract", claim="Selected model is optimal or nondominated only under the declared objective law and solver guarantee.", phase_ref="phase.bind.optimization", checker="objective evaluator and bound/certificate checker", failure="diagnostic.bind.w2001"),
    rec("proof.bind.qualification_scope", "proof_contract", claim="Receipt subject digest, edition, target occurrence, configuration, test domain, checker and validity match exactly.", phase_ref="phase.bind.qualification", checker="receipt scope checker", failure="diagnostic.bind.e1601"),
    rec("proof.bind.evidence_ladder", "proof_contract", claim="Documentation, executed test, independent appraisal, qualification and vertical acceptance are never promoted into one another.", phase_ref="phase.bind.qualification", checker="evidence-class and authority transition checker", failure="diagnostic.bind.e1601"),
    rec("proof.bind.status_no_strengthening", "proof_contract", claim="A provider terminal status is never translated into a more precise canonical claim than the exact interface and executed oracle support.", phase_ref="phase.bind.semantic", checker="versioned status-map and oracle checker", failure="diagnostic.bind.e1201"),
    rec("proof.bind.independent_qualification", "proof_contract", claim="A critical portability offer has the declared minimum independent qualified implementations.", phase_ref="phase.bind.qualification", checker="independence and receipt checker", failure="diagnostic.bind.w2002"),
    rec("proof.bind.dependency_closure", "proof_contract", claim="Exact dependency, feature, target, license and vulnerability closure is permitted and reproducible.", phase_ref="phase.bind.constraints", checker="lock/provenance/policy checkers", failure="diagnostic.bind.e1501"),
    rec("proof.bind.resource_admission", "proof_contract", claim="Hard budget and quota authorities admit the plan independently of capacity.", phase_ref="phase.bind.allocation", checker="budget/quota checker", failure="diagnostic.bind.e1402"),
    rec("proof.bind.resource_allocation", "proof_contract", claim="Qualified capacity is reserved, allocated and protected by enforceable lease/fence with release obligations.", phase_ref="phase.bind.allocation", checker="allocator receipt checker", failure="diagnostic.bind.e1401"),
    rec("proof.bind.runtime_conformance", "proof_contract", claim="The deployed occurrence continues to satisfy the selected contract and finite envelope.", phase_ref="phase.bind.runtime", checker="runtime probe/oracle set", failure="diagnostic.bind.e1601"),
    rec("proof.bind.invalidation_closure", "proof_contract", claim="Every changed dependency reaches all claims whose support set includes it.", phase_ref="phase.bind.runtime", checker="dependency graph reachability and mutation tests", failure="diagnostic.bind.e1802"),
    rec("proof.bind.incremental_equivalence", "proof_contract", claim="Incremental rebind equals clean rebind for identical inputs.", phase_ref="phase.bind.runtime", checker="canonical output digest comparison", failure="diagnostic.bind.e1802"),
    rec("proof.bind.migration_authority", "proof_contract", claim="Migration plan covers state, in-flight work, rollback/roll-forward and effect authority.", phase_ref="phase.bind.runtime", checker="state transition and authority checker", failure="diagnostic.bind.e1701"),
]

DECISIONS = [
    rec("decision.bind.registry_snapshot", "decision_point", owner="registry_authority", binding_phase="declaration", allowed=["exact_snapshot_digest"], default_law="none", consequences=["candidate universe fixed"]),
    rec("decision.bind.compatibility_relation", "decision_point", owner="semantic_owner", binding_phase="language", allowed=["equivalent", "offer_narrower_but_sufficient", "offer_broader_with_restriction", "adapter_required", "incompatible", "unknown"], default_law="unknown", consequences=["directional proof obligations"]),
    rec("decision.bind.solver_profile", "decision_point", owner="compiler_policy_owner", binding_phase="physical", allowed=["finite_domain", "sat", "smt_decidable_profile", "cp", "mip", "asp", "package_specific"], default_law="none", consequences=["checker and completeness posture"]),
    rec("decision.bind.hardness", "decision_point", owner="requirement_authority", binding_phase="assurance", allowed=["hard", "soft"], default_law="hard_for_laws_and_policy", consequences=["feasibility vs ranking"]),
    rec("decision.bind.unknown_policy", "decision_point", owner="assurance_authority", binding_phase="assurance", allowed=["block", "allow_only_nonblocking_claim", "require_human_adjudication"], default_law="block", consequences=["partial compilation"]),
    rec("decision.bind.objective_combination", "decision_point", owner="product_and_budget_authority", binding_phase="physical", allowed=["lexicographic", "pareto_frontier", "weighted_sum_with_dimensionless_normalization", "satisficing"], default_law="none", consequences=["selected alternative or unresolved frontier"]),
    rec("decision.bind.tie_break", "decision_point", owner="compiler_constitution", binding_phase="physical", allowed=["canonical_stable_identity"], default_law="canonical_stable_identity", consequences=["reproducibility"]),
    rec("decision.bind.core_posture", "decision_point", owner="proof_policy_owner", binding_phase="evidence", allowed=["sufficient", "minimal_checked", "minimum_proved"], default_law="sufficient", consequences=["diagnostic claim strength"]),
    rec("decision.bind.qualification_profile", "decision_point", owner="capability_semantic_owner", binding_phase="physical", allowed=["exact_profile_ref"], default_law="none", consequences=["tests and applicability domain"]),
    rec("decision.bind.qualification_acceptance", "decision_point", owner="assurance_authority", binding_phase="assurance", allowed=["executed_internal_evidence_only", "independent_appraisal_required", "vertical_acceptance_required"], default_law="independent_appraisal_required", consequences=["evidence may narrow candidates without making them bindable"]),
    rec("decision.bind.solver_status_precision", "decision_point", owner="analytical_contract_owner", binding_phase="language", allowed=["safe_ambiguous_terminal_class", "precise_infeasible_vs_unbounded"], default_law="none", consequences=["eligible solver-interface offers and refusal behavior"]),
    rec("decision.bind.evidence_ttl", "decision_point", owner="risk_owner", binding_phase="assurance", allowed=["finite_duration", "event_trigger_only", "both"], default_law="both", consequences=["requalification frequency"]),
    rec("decision.bind.budget_dimensions", "decision_point", owner="budget_authorities", binding_phase="assurance", allowed=["money", "latency", "energy", "memory", "storage", "network", "privacy", "retry", "operator_time"], default_law="none", consequences=["hard feasibility envelope"]),
    rec("decision.bind.capacity_risk", "decision_point", owner="operations_authority", binding_phase="operations", allowed=["worst_case", "quantile_with_risk_limit", "reservation_backed"], default_law="none", consequences=["admission posture"]),
    rec("decision.bind.rebind_scope", "decision_point", owner="compiler_constitution", binding_phase="operations", allowed=["support_set_transitive_closure"], default_law="support_set_transitive_closure", consequences=["incremental dirty graph"]),
    rec("decision.bind.migration_mode", "decision_point", owner="change_authority", binding_phase="operations", allowed=["in_place", "dual_run", "shadow", "backfill", "cutover", "roll_forward", "rollback", "decommission"], default_law="none", consequences=["state/in-flight disposition"]),
]

REQUIREMENTS = [
    rec("requirement.bind.exact_identity", "capability_requirement", capability="exact identity/edition resolution", blocking=True, proof_refs=["proof.bind.identity_edition"], authority="compiler_constitution"),
    rec("requirement.bind.semantic_checker", "capability_requirement", capability="directional semantic/type/shape/operation/law checker", blocking=True, proof_refs=["proof.bind.semantic_subsumption"], authority="semantic_owner"),
    rec("requirement.bind.constraint_backend", "capability_requirement", capability="model/check hard finite constraints with sat/unsat/unknown", blocking=True, proof_refs=["proof.bind.feasible_model", "proof.bind.unknown_preserved"], authority="compiler_policy_owner"),
    rec("requirement.bind.unsat_checker", "capability_requirement", capability="check unsatisfiability evidence for selected profile", blocking=True, proof_refs=["proof.bind.unsat"], authority="proof_policy_owner"),
    rec("requirement.bind.objective_evaluator", "capability_requirement", capability="evaluate declared multiobjective law without changing hard constraints", blocking=True, proof_refs=["proof.bind.hard_constraint_preservation", "proof.bind.rank"], authority="budget_authorities"),
    rec("requirement.bind.qualification_runner", "capability_requirement", capability="execute qualification profile on exact artifact/target/configuration", blocking=True, proof_refs=["proof.bind.qualification_scope"], authority="capability_semantic_owner"),
    rec("requirement.bind.resource_admission", "capability_requirement", capability="separate quota/budget admission from capacity and allocation", blocking=True, proof_refs=["proof.bind.resource_admission", "proof.bind.resource_allocation"], authority="operations_authority"),
    rec("requirement.bind.runtime_probe", "capability_requirement", capability="observe runtime claims and emit scoped receipts", blocking=True, proof_refs=["proof.bind.runtime_conformance"], authority="operations_authority"),
    rec("requirement.bind.incremental_engine", "capability_requirement", capability="tracked invalidation and clean-equivalent incremental rebind", blocking=True, proof_refs=["proof.bind.invalidation_closure", "proof.bind.incremental_equivalence"], authority="compiler_constitution"),
    rec("requirement.bind.lp_safe_status_objective", "capability_requirement", capability="continuous linear-program execution with independently recomputed feasible solution/objective and no-strengthening safe terminal status", blocking=True, proof_refs=["proof.bind.identity_edition", "proof.bind.status_no_strengthening", "proof.bind.qualification_scope", "proof.bind.evidence_ladder"], authority="analytical_contract_owner"),
    rec("requirement.bind.lp_precise_terminal", "capability_requirement", capability="continuous linear-program execution that distinguishes infeasible from unbounded for the declared model class", blocking=True, proof_refs=["proof.bind.identity_edition", "proof.bind.status_no_strengthening", "proof.bind.qualification_scope", "proof.bind.evidence_ladder"], authority="analytical_contract_owner"),
    rec("requirement.bind.cp_sat_exact_scope", "capability_requirement", capability="closed bounded-integer CP-SAT execution with canonical/provider validation, independently checked solutions and preserved unknown status", blocking=True, proof_refs=["proof.bind.identity_edition", "proof.bind.status_no_strengthening", "proof.bind.qualification_scope", "proof.bind.evidence_ladder"], authority="analytical_contract_owner"),
    rec("requirement.bind.cp_sat_complete_enumeration", "capability_requirement", capability="complete finite CP-SAT solution enumeration with exact configuration and independent count/completion oracle", blocking=True, proof_refs=["proof.bind.identity_edition", "proof.bind.status_no_strengthening", "proof.bind.qualification_scope", "proof.bind.evidence_ladder"], authority="analytical_contract_owner"),
]

OFFERS = [
    rec("offer.bind.varisat.candidate", "capability_offer", subject="artifact:varisat@0.2.2", offers=["sat model", "DRAT proof logging"], exact_edition="0.2.2", target_scope="unqualified", binding_eligible=False, qualification_receipts=[], exclusions=["no SAN semantic checker", "no target/resource qualification"], evidence_refs=["source.bind.varisat"]),
    rec("offer.bind.cvc5.candidate", "capability_offer", subject="artifact:cvc5@documentation-current-2026-08-25", offers=["SMT models", "unsat cores", "proof production"], exact_edition="occurrence_not_fixed", target_scope="unqualified", binding_eligible=False, qualification_receipts=[], exclusions=["documentation snapshot is not an executable artifact receipt"], evidence_refs=["source.bind.cvc5.api", "source.bind.cvc5.proofs"]),
    rec("offer.bind.minizinc.candidate", "capability_offer", subject="artifact:minizinc@2.10.0", offers=["solver-independent constraint model", "solution checking"], exact_edition="2.10.0", target_scope="unqualified", binding_eligible=False, qualification_receipts=[], exclusions=["backend semantics and target remain unqualified"], evidence_refs=["source.bind.minizinc.handbook", "source.bind.minizinc.checker"]),
    rec("offer.bind.pubgrub_rs.candidate", "capability_offer", subject="artifact:pubgrub-rs@exact-version-required", offers=["version solving", "conflict derivation"], exact_edition="missing", target_scope="unqualified", binding_eligible=False, qualification_receipts=[], exclusions=["package domain adapter semantics absent"], evidence_refs=["source.bind.pubgrub.rs"]),
    rec("offer.bind.salsa.candidate", "capability_offer", subject="artifact:salsa@exact-version-required", offers=["incremental queries", "tracked inputs"], exact_edition="missing", target_scope="unqualified", binding_eligible=False, qualification_receipts=[], exclusions=["clean-equivalence conformance receipt absent"], evidence_refs=["source.bind.rust.salsa"]),
    rec("offer.bind.goodlp.candidate", "capability_offer", subject="artifact:good_lp@1.15.3", offers=["typed linear model abstraction", "multiple backend adapters"], exact_edition="1.15.3", target_scope="unqualified", binding_eligible=False, qualification_receipts=[], exclusions=["not itself a solver", "backend/license/numeric guarantees differ"], evidence_refs=["source.bind.goodlp"]),
    rec("offer.bind.k8s.scheduler.class", "capability_offer", subject="provider_class:kubernetes-scheduler", offers=["feasibility filter", "score", "reserve", "permit", "bind"], exact_edition="class-only", target_scope="no occurrence", binding_eligible=False, qualification_receipts=[], exclusions=["class documentation is not deployed capacity or allocation"], evidence_refs=["source.bind.k8s.framework"]),
    rec("offer.bind.nomad.scheduler.class", "capability_offer", subject="provider_class:nomad-scheduler", offers=["feasibility", "ranking", "allocation plan"], exact_edition="class-only", target_scope="no occurrence", binding_eligible=False, qualification_receipts=[], exclusions=["no deployed occurrence", "soft affinity is not a hard constraint"], evidence_refs=["source.bind.nomad.scheduling", "source.bind.nomad.placement"]),
]


def projected_offer_id(source_offer_id: str) -> str:
    if not source_offer_id.startswith("offer.ptr."):
        raise ValueError(f"unexpected provider-target offer identity: {source_offer_id}")
    return "offer.bind.ptr." + source_offer_id.removeprefix("offer.ptr.")


def project_provider_target_offers() -> list[dict]:
    qualifications_by_offer: dict[str, list[dict]] = {}
    for assessment in PROVIDER_TARGET_QUALIFICATIONS:
        qualifications_by_offer.setdefault(assessment["subject_ref"], []).append(assessment)
    occurrences_by_offer: dict[str, list[str]] = {}
    for occurrence in PROVIDER_TARGET_OCCURRENCES:
        occurrences_by_offer.setdefault(occurrence["offer_ref"], []).append(occurrence["target_occurrence_id"])
    compatibility_by_offer: dict[str, list[str]] = {}
    for cell in PROVIDER_TARGET_COMPATIBILITY:
        for endpoint in (cell["left_ref"], cell["right_ref"]):
            if endpoint.startswith("offer.ptr."):
                compatibility_by_offer.setdefault(endpoint, []).append(cell["compatibility_id"])

    records = []
    for offer in PROVIDER_TARGET_OFFERS:
        source_offer_id = offer["offer_id"]
        assessments = qualifications_by_offer.get(source_offer_id, [])
        executed_receipts = sorted({
            receipt_ref
            for assessment in assessments
            for receipt_ref in assessment.get("execution_receipt_refs", [])
        })
        evidence_classes = sorted({assessment["evidence_class"] for assessment in assessments})
        outcomes = sorted({assessment["outcome"] for assessment in assessments})
        records.append(rec(
            projected_offer_id(source_offer_id),
            "capability_offer",
            subject=source_offer_id,
            source_registry="san.provider-target-physical-binding-registry",
            source_offer_ref=source_offer_id,
            source_artifact_ref=offer["artifact_ref"],
            source_provider_organization_ref=offer["provider_organization_ref"],
            offers=offer["capability_class_refs"],
            exact_edition=offer["artifact_version"],
            target_scope="exact occurrences when present; otherwise profile/documentation scope only",
            source_target_profile_refs=offer["target_profile_refs"],
            source_target_occurrence_refs=sorted(occurrences_by_offer.get(source_offer_id, [])),
            source_compatibility_refs=sorted(compatibility_by_offer.get(source_offer_id, [])),
            binding_eligible=False,
            qualification_receipts=[],
            qualification_assessment_refs=sorted(assessment["qualification_receipt_id"] for assessment in assessments),
            executed_test_receipt_refs=executed_receipts,
            evidence_classes=evidence_classes,
            assessment_outcomes=outcomes,
            exclusions=offer["exclusions"],
            upstream_evidence_refs=offer["evidence_refs"],
            evidence_refs=[],
        ))
    return records


OFFERS.extend(project_provider_target_offers())

LIBRARIES = [
    rec("library.bind.model", "library_boundary", name="san-binding-model", kind="pure_semantic", owns=["typed identities", "requirements/offers", "constraints", "results"], excludes=["solver backend", "registry I/O"], rust_surface=["newtypes", "enums", "sealed traits"]),
    rec("library.bind.snapshot", "library_boundary", name="san-registry-snapshot", kind="pure_semantic", owns=["snapshot manifests", "digest verification", "exact lookup"], excludes=["network fetch", "alias inference"], rust_surface=["Snapshot<Verified>", "StableId", "Edition"]),
    rec("library.bind.enumerator", "library_boundary", name="san-candidate-enumerator", kind="pure_algorithm", owns=["structural index", "candidate/rejection graph"], excludes=["semantic proof", "ranking"], rust_surface=["CandidateEnumerator trait", "deterministic iterators"]),
    rec("library.bind.semantic", "library_boundary", name="san-semantic-compatibility", kind="pure_algorithm", owns=["directional relation evaluation", "compatibility claims"], excludes=["ontology ownership", "provider discovery"], rust_surface=["SubsumptionOracle trait", "UnknownReason"]),
    rec("library.bind.constraint_ir", "library_boundary", name="san-constraint-ir", kind="pure_semantic", owns=["named atoms", "support sets", "hard/soft split", "objective definitions"], excludes=["backend encodings"], rust_surface=["Constraint<H>", "AssumptionId", "ObjectiveVector"]),
    rec("library.bind.solver_spi", "library_boundary", name="san-solver-spi", kind="effect_port", owns=["sat/unsat/unknown interface", "limits", "model/proof artifacts"], excludes=["specific solver implementation"], rust_surface=["SolverBackend trait", "SolveOutcome enum", "CancellationToken"]),
    rec("library.bind.solver_adapters", "library_boundary", name="san-solver-adapters", kind="runtime_adapter_family", owns=["exact backend encodings", "process/FFI containment", "receipt capture"], excludes=["semantic requirements", "objective authority"], rust_surface=["adapter crates per backend", "unsafe isolated behind audited boundary"]),
    rec("library.bind.optimizer", "library_boundary", name="san-objective-selector", kind="pure_algorithm", owns=["lexicographic/Pareto/satisficing laws", "stable tie-break"], excludes=["hard constraint mutation", "cost discovery"], rust_surface=["SelectionLaw trait", "NonDominatedSet"]),
    rec("library.bind.qualification", "library_boundary", name="san-qualification-contract", kind="semantic_plus_effect_port", owns=["profiles", "execution requests", "receipt validation"], excludes=["test implementations", "provider reputation"], rust_surface=["Qualification<Planned/Executed/Checked>"] ),
    rec("library.bind.admission", "library_boundary", name="san-admission-contract", kind="semantic_plus_effect_port", owns=["budget/quota/capacity truth roles", "reservation/allocation/lease receipts"], excludes=["scheduler implementation"], rust_surface=["Demand<Bounded>", "AdmissionOutcome", "Lease<Fenced>"] ),
    rec("library.bind.invalidation", "library_boundary", name="san-binding-invalidation", kind="pure_algorithm", owns=["support-set index", "dirty closure", "incremental keys"], excludes=["change collection", "automatic migration"], rust_surface=["TrackedClaim", "InvalidationTrigger", "RebindKey"] ),
    rec("library.bind.trace", "library_boundary", name="san-binding-trace", kind="pure_semantic", owns=["decision traces", "unsat cores", "rejections", "proof statuses"], excludes=["localized presentation rendering"], rust_surface=["ProofStatus", "DiagnosticCode", "SupportSet"] ),
]

RUST_APPLICABILITY = [
    rec("rust.bind.newtype_identity", "rust_applicability", feature="newtype structs", applies_to="StableId, Edition, SnapshotDigest, OccurrenceId remain non-interchangeable", limitation="runtime registry closure is still required"),
    rec("rust.bind.enums_results", "rust_applicability", feature="closed enums", applies_to="SolveOutcome::{Sat,Unsat,Unknown,Refused} and proof status", limitation="open registry kinds should not be closed enums"),
    rec("rust.bind.typestate_snapshot", "rust_applicability", feature="typestate generics", applies_to="Snapshot<Unverified> -> Snapshot<Verified> and Qualification<Planned> -> Executed -> Checked", limitation="cannot prove external evidence truth"),
    rec("rust.bind.phantom_phase", "rust_applicability", feature="PhantomData phase markers", applies_to="prevent ranking of unproved candidates and allocation of unqualified plans", limitation="serialization must carry explicit phase tags too"),
    rec("rust.bind.sealed_traits", "rust_applicability", feature="sealed traits", applies_to="protect constitutional semantics such as hard constraint and stable identity", limitation="extension registries need explicit adapter interfaces"),
    rec("rust.bind.traits", "rust_applicability", feature="traits with associated types", applies_to="SolverBackend, SubsumptionOracle, QualificationRunner, Allocator", limitation="trait compatibility is not semantic conformance"),
    rec("rust.bind.result", "rust_applicability", feature="Result and domain error enums", applies_to="total refusal/failure catalog", limitation="Unknown must not be collapsed into Err or false"),
    rec("rust.bind.nonempty", "rust_applicability", feature="validated collection newtypes", applies_to="NonEmpty support sets, finite domains, objective order", limitation="constructors must remain private and checked"),
    rec("rust.bind.ordered", "rust_applicability", feature="BTreeMap/BTreeSet", applies_to="canonical deterministic iteration", limitation="semantic ordering must be explicitly defined"),
    rec("rust.bind.serde_acl", "rust_applicability", feature="serde DTO boundary", applies_to="wire/storage DTO translated into validated domain types", limitation="derive Deserialize must not bypass invariants"),
    rec("rust.bind.async_cancel", "rust_applicability", feature="async traits and cancellation tokens", applies_to="bounded solver/qualification/allocation effects", limitation="drop is not a universal cancellation guarantee"),
    rec("rust.bind.send_sync", "rust_applicability", feature="Send/Sync bounds", applies_to="make concurrency posture explicit per backend", limitation="thread safety is not solver determinism"),
    rec("rust.bind.unsafe_boundary", "rust_applicability", feature="small audited unsafe/FFI module", applies_to="external solver adapters", limitation="proof/checker separation remains mandatory"),
    rec("rust.bind.property_tests", "rust_applicability", feature="property/model/fuzz tests", applies_to="incremental equals clean, stable ordering, invalidation closure", limitation="tests are scoped evidence, not universal proof"),
    rec("rust.bind.no_std", "rust_applicability", feature="feature-gated no_std pure core", applies_to="portable semantic model where practical", limitation="solver/process/network adapters remain target-specific"),
]

INVALIDATIONS = [
    rec("invalidate.bind.requirement", "invalidation_rule", trigger="requirement identity/edition/contract changes", invalidates=["candidate enumeration", "semantic proof", "constraints", "rank", "qualification", "binding"], action="rebind transitive support closure"),
    rec("invalidate.bind.offer", "invalidation_rule", trigger="offer contract, exclusion, edition or lifecycle changes", invalidates=["candidate edge", "semantic proof", "selected binding"], action="re-enumerate affected requirements"),
    rec("invalidate.bind.semantic_assertion", "invalidation_rule", trigger="semantic relation or authority changes", invalidates=["subsumption proof", "downstream model"], action="reprove compatibility"),
    rec("invalidate.bind.decision", "invalidation_rule", trigger="configuration decision/default/precedence changes", invalidates=["constraint instance", "rank", "physical plan"], action="resolve authority and re-solve"),
    rec("invalidate.bind.objective", "invalidation_rule", trigger="objective set/order/unit/weight changes", invalidates=["ranking only unless encoded as hard"], action="rerank same feasible set when safe"),
    rec("invalidate.bind.solver", "invalidation_rule", trigger="backend artifact/config/limit changes", invalidates=["solver receipt", "sat/unsat/optimality claim"], action="re-solve and recheck"),
    rec("invalidate.bind.proof_checker", "invalidation_rule", trigger="checker artifact or trust policy changes", invalidates=["checked proof status"], action="recheck with permitted exact checker"),
    rec("invalidate.bind.qualification", "invalidation_rule", trigger="artifact/target/config/test-domain/checker changes or TTL expiry", invalidates=["qualification receipt", "binding eligibility"], action="requalify"),
    rec("invalidate.bind.dependency", "invalidation_rule", trigger="dependency/feature/license/vulnerability/advisory changes", invalidates=["closure", "artifact qualification", "binding"], action="resolve closure and requalify"),
    rec("invalidate.bind.provider", "invalidation_rule", trigger="provider behavior default, rollout, region, quota or documented limit changes", invalidates=["occurrence offer", "capacity/cost/compatibility evidence"], action="probe occurrence and rebind if needed"),
    rec("invalidate.bind.target", "invalidation_rule", trigger="target OS/runtime/ABI/architecture/driver/firmware changes", invalidates=["kernel/adapter qualification", "resource envelope"], action="requalify exact target"),
    rec("invalidate.bind.resource", "invalidation_rule", trigger="quota/budget/capacity/reservation/allocation/lease state changes", invalidates=["admission or allocation only; not semantics"], action="readmit/reallocate or suspend"),
    rec("invalidate.bind.runtime_drift", "invalidation_rule", trigger="runtime probe violates selected law/SLO/policy", invalidates=["runtime conformance", "release acceptance"], action="fail safe, retain evidence, requalify/rebind"),
    rec("invalidate.bind.authority", "invalidation_rule", trigger="delegation revoked or scope/validity expires", invalidates=["owned decisions", "waivers", "migration authority"], action="refuse dependent effects"),
    rec("invalidate.bind.corpus", "invalidation_rule", trigger="canonical registry snapshot replaced", invalidates=["candidate completeness claim for old snapshot only"], action="new compilation; old trace remains reproducible"),
]

INNOVATIONS = [
    rec("innovation.bind.egglog.2023", "innovation", year=2023, claim="Unifies Datalog-style relational reasoning with equality saturation and explanations.", significance="Candidate for explainable equivalence/relational closure, not a semantic authority.", evidence_refs=["source.bind.egglog"]),
    rec("innovation.bind.spack_asp.2023", "innovation", year=2023, claim="Spack's ASP concretizer expresses HPC variants, reuse and optimization in one solver model.", significance="Shows package resolution can retain rich target and build choices.", evidence_refs=["source.bind.spack.asp"]),
    rec("innovation.bind.dbsp.2023", "innovation", year=2023, claim="DBSP formalizes automatic incremental maintenance through algebraic derivatives.", significance="Relevant to incremental recomputation, subject to clean-equivalence proofs.", evidence_refs=["source.bind.dbsp"]),
    rec("innovation.bind.cvc5_explanations.2024", "innovation", year=2024, claim="cvc5 exposes richer unsat-core, difficulty and proof interfaces.", significance="Supports scoped diagnostics; output still requires checker policy.", evidence_refs=["source.bind.cvc5.understanding"]),
    rec("innovation.bind.cake_lpr.2024", "innovation", year=2024, claim="Verified proof checking reduces trust placed in a SAT solver process.", significance="Supports solver/checker separation.", evidence_refs=["source.bind.cakelpr"]),
    rec("innovation.bind.spdx3.2024", "innovation", year=2024, claim="SPDX 3.0 provides a more extensible artifact/software data model.", significance="Improves exact dependency and evidence identity exchange.", evidence_refs=["source.bind.spdx.30"]),
    rec("innovation.bind.cyclonedx16.2024", "innovation", year=2024, claim="CycloneDX 1.6 extends machine-readable BOM and related evidence vocabularies.", significance="Supports dependency/change invalidation inputs, not automatic compatibility.", evidence_refs=["source.bind.cyclonedx.16"]),
    rec("innovation.bind.slsa12.2025", "innovation", year=2025, claim="SLSA 1.2 refines provenance and verification contracts.", significance="Supports build evidence freshness and exact artifact qualification.", evidence_refs=["source.bind.slsa"]),
    rec("innovation.bind.scenic3.2025", "innovation", year=2025, claim="Scenic 3 evolves scenario-based simulation and falsification tooling.", significance="Useful for qualification/adversarial test-domain generation; stochastic evidence remains scoped.", evidence_refs=["source.bind.scenic"]),
    rec("innovation.bind.smtlib27.2026", "innovation", year=2026, claim="SMT-LIB 2.7 refreshes the common solver language and theory definitions.", significance="Improves backend-neutral exact constraint interchange while theory completeness remains explicit.", evidence_refs=["source.bind.smtlib.27"]),
    rec("innovation.bind.minizinc210.2026", "innovation", year=2026, claim="MiniZinc 2.10 maintains high-level solver-independent modeling and checker workflows.", significance="Reinforces model/backend/checker separation.", evidence_refs=["source.bind.minizinc.handbook", "source.bind.metacp"]),
    rec("innovation.bind.k8s_dra.2024_2026", "innovation", year=2026, claim="Kubernetes Dynamic Resource Allocation separates resource claims, classes, allocation and scheduling integration.", significance="Evidence that capability matching, admission and concrete allocation are different phases.", evidence_refs=["source.bind.k8s.dra"]),
]

GAPS = [
    rec("gap.bind.formal_semantics", "typed_gap", severity="blocking", missing="Formal semantics for every SAN requirement/offer/law kind", consequence="Subsumption can only be candidate/profile-specific", owner="semantic_domain_owners"),
    rec("gap.bind.registry_completeness", "typed_gap", severity="blocking", missing="Canonical complete offer registries", consequence="Candidate completeness is only relative to frozen snapshots", owner="registry_program"),
    rec("gap.bind.alias_adjudication", "typed_gap", severity="blocking", missing="Evidence-bearing canonical reference assertions for all external identities", consequence="Aliases remain unresolved", owner="context_map_program"),
    rec("gap.bind.solver_qualification", "typed_gap", severity="blocking", missing="Complete exact-scope solver qualification including operational, resource, security and acceptance profiles", consequence="Documentation and narrow executed-test evidence remain non-bindable", owner="compiler_qualification"),
    rec("gap.bind.proof_profiles", "typed_gap", severity="blocking", missing="Approved proof/checker profile per constraint theory", consequence="Unsat/optimality claims may remain unknown", owner="proof_governance"),
    rec("gap.bind.optimization_units", "typed_gap", severity="blocking", missing="Authority-owned normalization/utility laws for cross-dimensional objectives", consequence="Weighted ranking is refused", owner="budget_authorities"),
    rec("gap.bind.cost_occurrences", "typed_gap", severity="blocking", missing="Occurrence/time/workload-scoped cost and resource evidence", consequence="No production cost ranking", owner="provider_target_registry"),
    rec("gap.bind.qualification_profiles", "typed_gap", severity="blocking", missing="Executable profiles for domain laws, failures and numeric postures", consequence="Candidates cannot be qualified", owner="library_and_domain_owners"),
    rec("gap.bind.target_occurrences", "typed_gap", severity="blocking", missing="Exact deployed target occurrences and probes", consequence="No allocation or runtime plan", owner="operations"),
    rec("gap.bind.allocator", "typed_gap", severity="blocking", missing="Qualified allocation/admission adapters", consequence="Compiler stops before effects", owner="runtime_resource_domain"),
    rec("gap.bind.migration_library", "typed_gap", severity="blocking", missing="State/in-flight migration contracts for selected contributions", consequence="Replacement bindings cannot be applied", owner="change_domain"),
    rec("gap.bind.independent_implementation", "typed_gap", severity="blocking", missing="Two independent implementations of constitutional model/checker interfaces", consequence="Portability claim withheld", owner="library_program"),
    rec("gap.bind.vertical_case_links", "typed_gap", severity="blocking", missing="Adjudicated links from industry case refs to canonical methods/operations/sources", consequence="Vertical examples remain illustrative", owner="industry_integration"),
    rec("gap.bind.empirical_scale", "typed_gap", severity="nonblocking_research", missing="Scale benchmarks for million-record registry and hypergraph solving", consequence="Complexity/resource envelope unknown", owner="compiler_research"),
    rec("gap.bind.independent_appraisal", "typed_gap", severity="blocking", missing="Independent reproduction and appraisal of the exact provider/target/oracle evidence", consequence="Executed internal tests narrow candidates but do not make an offer binding eligible", owner="independent_assurance_authority"),
    rec("gap.bind.lp_precise_status", "typed_gap", severity="blocking", missing="Precise infeasible-versus-unbounded support on the selected exact solver interface", consequence="The offer cannot satisfy analytical contracts that require exact terminal classification", owner="analytical_contract_owner"),
    rec("gap.bind.vertical_lp_model_class", "typed_gap", severity="blocking", missing="Adjudicated proof that the vertical optimization subproblem is a finite-coefficient continuous LP rather than nonlinear, integer, stochastic or hybrid", consequence="A continuous-LP provider cannot be selected from a broad optimization label", owner="vertical_method_owner", adjudication_contract_ref="metamodel.compiler.model_class_adjudication.v1", current_broad_trace_ref="trace.mca.pipeline.broad_unclosed", candidate_screen_trace_ref="trace.mca.pipeline.lp_screen"),
    rec("gap.bind.vertical_acceptance", "typed_gap", severity="blocking", missing="Domain-authority acceptance of solution meaning, constraints, failure handling and operational use", consequence="A provider test pass cannot authorize a vertical decision or action", owner="vertical_domain_authority"),
    rec("gap.bind.cp_sat_enumeration_configuration", "typed_gap", severity="blocking", missing="Exact adapter propagation of complete-enumeration intent and completion oracle", consequence="A callback or one observed solution cannot establish enumeration completeness", owner="compiler_qualification"),
    rec("gap.bind.manufacturing_cp_sat_formulation", "typed_gap", severity="blocking", missing="Authority-reviewed mapping from the manufacturing case's complete orders, resources, calendars, setup, material, labor, safety and objective semantics into the exact supported CP-SAT fragment", consequence="A small job-shop fixture cannot qualify the enterprise formulation", owner="manufacturing_method_owner"),
]

EXAMPLES = [
    rec(
        "example.bind.microgrid.positive", "binding_example", vertical="energy_operations", polarity="positive",
        intent="Bind a day-ahead probabilistic net-load analytical design to pure/runtime contributions under a finite money, latency and energy budget; no automatic battery actuation.",
        requirements=["probabilistic forecast method applicability", "15-minute local-day time/unit semantics", "rolling-origin evaluation", "bounded-state pipeline", "human authority gate", "qualified algorithm/kernel/target"],
        trace=[
            {"phase":"phase.bind.structural","result":"partial","detail":"candidate offer registry contains no exact forecast-method/kernel chain"},
            {"phase":"phase.bind.semantic","result":"unknown","detail":"no authority-scoped method-to-algorithm applicability and unit/time adapter receipts"},
            {"phase":"phase.bind.constraints","result":"not_run","detail":"blocking semantic requirements cannot be encoded as satisfied"},
            {"phase":"phase.bind.qualification","result":"not_run","detail":"no exact artifact/target qualification receipts"}
        ],
        terminal_result="partially_bound",
        terminal_gaps=["gap.bind.registry_completeness", "gap.bind.qualification_profiles", "gap.bind.target_occurrences"],
        negative_twin_ref="example.bind.microgrid.negative",
        evidence_refs=["source.bind.minizinc.handbook", "source.bind.k8s.framework"]
    ),
    rec(
        "example.bind.microgrid.negative", "binding_example", vertical="energy_operations", polarity="negative_twin",
        intent="Choose the cheapest forecast stack and infer timezone, energy/power unit and missing-value behavior from field names.",
        requirements=["underspecified"],
        trace=[
            {"phase":"phase.bind.structural","result":"refused","detail":"names are not exact semantic identities"},
            {"phase":"phase.bind.semantic","result":"refused","detail":"timezone, kW/kWh and missingness defaults lack authority"}
        ],
        terminal_result="refused",
        terminal_gaps=["gap.bind.alias_adjudication", "gap.bind.formal_semantics"],
        negative_twin_ref="example.bind.microgrid.positive",
        evidence_refs=["source.bind.cue.spec", "source.bind.substrait.types"]
    ),
    rec(
        "example.bind.saccr.positive", "binding_example", vertical="banking_counterparty_credit_risk", polarity="positive",
        intent="Bind a governed SA-CCR exposure-at-default calculation and aggregation case while preserving legal entity, netting set, margin set, trade, collateral, as-of and regulation-edition identities.",
        requirements=["exact rule edition", "authority-owned netting/margin set", "trade and collateral source reconciliation", "formula/operation law oracles", "decimal/unit posture", "lineage and maker-checker", "qualified target and reproducible report snapshot"],
        trace=[
            {"phase":"phase.bind.structural","result":"partial","detail":"formula and source requirements resolve as needs; executable offers are absent"},
            {"phase":"phase.bind.semantic","result":"unknown","detail":"no canonical rule-edition/formula/operation assertion graph in this bundle"},
            {"phase":"phase.bind.constraints","result":"not_run","detail":"legal/semantic ownership gaps are hard"},
            {"phase":"phase.bind.qualification","result":"not_run","detail":"no independent numeric boundary or reconciliation receipts"}
        ],
        terminal_result="partially_bound",
        terminal_gaps=["gap.bind.vertical_case_links", "gap.bind.qualification_profiles", "gap.bind.target_occurrences"],
        negative_twin_ref="example.bind.saccr.negative",
        evidence_refs=["source.bind.smtlib.27", "source.bind.minizinc.checker", "source.bind.in_toto"]
    ),
    rec(
        "example.bind.saccr.negative", "binding_example", vertical="banking_counterparty_credit_risk", polarity="negative_twin",
        intent="Group trades by counterparty name, use current prices and floating point defaults, then pick the fastest SQL engine.",
        requirements=["underspecified and unsafe"],
        trace=[
            {"phase":"phase.bind.structural","result":"refused","detail":"counterparty display name is not legal-entity or netting-set identity"},
            {"phase":"phase.bind.semantic","result":"refused","detail":"regulation edition, as-of/valid time, collateral and numeric laws missing"},
            {"phase":"phase.bind.optimization","result":"forbidden","detail":"speed cannot rank infeasible semantic candidates"}
        ],
        terminal_result="refused",
        terminal_gaps=["gap.bind.alias_adjudication", "gap.bind.vertical_case_links", "gap.bind.formal_semantics"],
        negative_twin_ref="example.bind.saccr.positive",
        evidence_refs=["source.bind.jsonschema.validation", "source.bind.smtlib.27"]
    ),
    rec(
        "example.bind.pipeline_nomination.lp_screening.positive", "binding_example", vertical="oil_gas_midstream_pipeline", polarity="positive",
        upstream_case_ref="energy.case.nomination_capacity_optimization",
        model_class_adjudication_trace_ref="trace.mca.pipeline.lp_screen",
        model_class_adjudication_result_ref="result.trace.mca.pipeline.lp_screen",
        formal_model_class_refs=["class.mca.continuous_lp"],
        intent="Bind only an adjudicated finite-coefficient continuous-LP nomination-capacity screening subproblem; require precise infeasible-versus-unbounded classification, retain hydraulic and contract authority upstream, and emit a proposal rather than an operating command.",
        requirements=["adjudicated continuous-LP subproblem boundary", "exact status precision", "finite coefficients and budgets", "independently checked feasibility/objective", "independent provider appraisal", "vertical acceptance and operating-authority gate"],
        required_capability_refs=["capability.ptr.optimization_solver.continuous_linear_program_execution", "capability.ptr.optimization_solver.solution_and_objective_reporting", "capability.ptr.optimization_solver.precise_infeasible_unbounded_classification"],
        candidate_offer_refs=["offer.bind.ptr.highspy.highs.1_15_1"],
        refused_offer_refs=["offer.bind.ptr.ortools.glop_mpsolver_python.9_15_6755"],
        qualification_assessment_refs=["qualification.ptr.highspy.highs.1_15_1.precise_terminal_classification"],
        required_status_precision="precise_infeasible_vs_unbounded",
        automation_modality="deterministic_core_only",
        optional_extension_requirement_refs=[],
        trace=[
            {"phase":"phase.bind.structural","result":"pass_candidate","detail":"the linked deterministic adjudication trace closes only the finite-coefficient continuous-LP screening subproblem; it does not classify the broad pipeline case"},
            {"phase":"phase.bind.semantic","result":"partial","detail":"the precise-status capability excludes the exact GLOP/MPSolver offer and leaves the exact highspy/HiGHS offer as the sole current candidate"},
            {"phase":"phase.bind.constraints","result":"pass_candidate","detail":"the screening trace declares hydraulic, integer, stochastic and contract-priority semantics outside this exact LP cut; any boundary change invalidates classification and rebinding"},
            {"phase":"phase.bind.qualification","result":"partial","detail":"the precise highspy profile passed one executed test but lacks independent appraisal and full operational qualification"},
            {"phase":"phase.bind.allocation","result":"not_run","detail":"no production target, finite resource admission or vertical acceptance receipt exists"}
        ],
        terminal_result="partially_bound",
        terminal_gaps=["gap.bind.independent_appraisal", "gap.bind.solver_qualification", "gap.bind.vertical_acceptance"],
        negative_twin_ref="example.bind.pipeline_nomination.generic_solver.negative",
        evidence_refs=["source.bind.ortools.glop_status.9_15", "source.bind.highs.model_status"]
    ),
    rec(
        "example.bind.pipeline_nomination.generic_solver.negative", "binding_example", vertical="oil_gas_midstream_pipeline", polarity="negative_twin",
        upstream_case_ref="energy.case.nomination_capacity_optimization",
        model_class_adjudication_trace_ref="trace.mca.pipeline.broad_unclosed",
        model_class_adjudication_result_ref="result.trace.mca.pipeline.broad_unclosed",
        intent="Select OR-Tools by project name for the entire nomination problem, treat every MPSolver INFEASIBLE result as a proof of physical infeasibility, and issue a curtailment schedule.",
        requirements=["underspecified provider facade", "unproved model-class collapse", "strengthened terminal status", "unauthorized operational effect"],
        candidate_offer_refs=[],
        required_status_precision="silently_strengthened",
        automation_modality="deterministic_core_required_but_violated",
        optional_extension_requirement_refs=[],
        trace=[
            {"phase":"phase.bind.structural","result":"refused","detail":"project identity is not an exact solver/interface/version/target occurrence and the broad vertical problem is not proved to be a continuous LP"},
            {"phase":"phase.bind.semantic","result":"refused","detail":"the exact GLOP/MPSolver surface failed the precise terminal-classification profile; ambiguity cannot be strengthened"},
            {"phase":"phase.bind.qualification","result":"refused","detail":"executed internal evidence is not independent qualification or vertical acceptance"},
            {"phase":"phase.bind.runtime","result":"forbidden","detail":"an analytical proposal cannot directly authorize nomination curtailment or control effects"}
        ],
        terminal_result="refused",
        terminal_gaps=["gap.bind.vertical_lp_model_class", "gap.bind.lp_precise_status", "gap.bind.vertical_acceptance"],
        negative_twin_ref="example.bind.pipeline_nomination.lp_screening.positive",
        evidence_refs=["source.bind.ortools.release.9_15", "source.bind.ortools.glop_status.9_15"]
    ),
    rec(
        "example.bind.manufacturing_schedule.cp_sat.positive", "binding_example", vertical="manufacturing_finite_capacity_scheduling", polarity="positive",
        upstream_case_ref="mfg.case.finite_schedule",
        model_class_adjudication_trace_ref="trace.mca.manufacturing.cp_sat",
        model_class_adjudication_result_ref="result.trace.mca.manufacturing.cp_sat",
        formal_model_class_refs=["class.mca.cp_sat_integer", "class.mca.finite_domain_cp"],
        intent="Bind only the authority-reviewed bounded-integer CP-SAT fragment of a finite-capacity production schedule; independently verify every returned schedule and retain publication and dispatch authority outside the solver.",
        requirements=["closed CP-SAT formulation boundary", "integer-only canonical model", "exact interval/no-overlap semantics", "independently checked solution and objective", "exact adapter configuration", "independent provider appraisal", "manufacturing acceptance and publication authority"],
        required_capability_refs=["capability.ptr.optimization_solver.bounded_integer_cp_sat_execution", "capability.ptr.optimization_solver.fixed_interval_no_overlap_scheduling", "capability.ptr.optimization_solver.canonical_integer_model_validation", "capability.ptr.optimization_solver.unknown_limit_status_preservation"],
        candidate_offer_refs=["offer.bind.ptr.ortools.cp_sat_python.9_15_6755"],
        refused_offer_refs=[],
        qualification_assessment_refs=["qualification.ptr.ortools.cp_sat_python.9_15_6755.core", "qualification.ptr.ortools.cp_sat_python.9_15_6755.scheduling", "qualification.ptr.ortools.cp_sat_python.9_15_6755.limit_no_strengthening"],
        automation_modality="deterministic_core_only",
        optional_extension_requirement_refs=[],
        trace=[
            {"phase":"phase.bind.structural","result":"pass_candidate","detail":"the linked deterministic classification admits finite-domain CP and integer-only CP-SAT facets; it does not collapse the whole manufacturing case into a provider surface"},
            {"phase":"phase.bind.semantic","result":"partial","detail":"the exact offer exposes the required tested fragment, but the enterprise case-to-formulation mapping and all local constraints remain authority-owned and unaccepted"},
            {"phase":"phase.bind.constraints","result":"pass_candidate","detail":"core, interval/no-overlap and UNKNOWN-preservation fixtures passed independent deterministic checking on the recorded corrected adapter occurrence"},
            {"phase":"phase.bind.qualification","result":"partial","detail":"executed tests lack independent appraisal, portability, security, resource, performance and production qualification"},
            {"phase":"phase.bind.allocation","result":"not_run","detail":"no plant target, current input snapshot, manufacturing acceptance or publish/dispatch receipt exists"}
        ],
        terminal_result="partially_bound",
        terminal_gaps=["gap.bind.manufacturing_cp_sat_formulation", "gap.bind.independent_appraisal", "gap.bind.solver_qualification", "gap.bind.vertical_acceptance"],
        negative_twin_ref="example.bind.manufacturing_schedule.generic_optimizer.negative",
        evidence_refs=["source.bind.ortools.cpsat", "source.bind.ortools.scheduling"]
    ),
    rec(
        "example.bind.manufacturing_schedule.generic_optimizer.negative", "binding_example", vertical="manufacturing_finite_capacity_scheduling", polarity="negative_twin",
        upstream_case_ref="mfg.case.finite_schedule",
        model_class_adjudication_trace_ref="trace.mca.manufacturing.cp_sat",
        model_class_adjudication_result_ref="result.trace.mca.manufacturing.cp_sat",
        formal_model_class_refs=["class.mca.cp_sat_integer", "class.mca.finite_domain_cp"],
        intent="Choose OR-Tools by suite name, assume any callback enumerates every schedule, and publish the first returned assignment as the plant schedule.",
        requirements=["provider facade substituted for exact offer", "callback substituted for enumeration semantics", "fixture pass substituted for enterprise formulation acceptance", "unauthorized publication effect"],
        candidate_offer_refs=[],
        refused_offer_refs=["offer.bind.ptr.ortools.cp_sat_python.9_15_6755"],
        automation_modality="deterministic_core_required_but_violated",
        optional_extension_requirement_refs=[],
        trace=[
            {"phase":"phase.bind.structural","result":"refused","detail":"suite name is not an exact solver/interface/version/adapter/target occurrence, and the full case has no accepted lowering contract"},
            {"phase":"phase.bind.semantic","result":"refused","detail":"the retained first adapter occurrence proves that a callback without the exhaustive-enumeration parameter observes only a subset"},
            {"phase":"phase.bind.qualification","result":"refused","detail":"the corrected profile pass is executed internal evidence, not independent qualification or manufacturing acceptance"},
            {"phase":"phase.bind.runtime","result":"forbidden","detail":"a candidate analytical schedule cannot directly acquire publication or dispatch authority"}
        ],
        terminal_result="refused",
        terminal_gaps=["gap.bind.cp_sat_enumeration_configuration", "gap.bind.manufacturing_cp_sat_formulation", "gap.bind.vertical_acceptance"],
        negative_twin_ref="example.bind.manufacturing_schedule.cp_sat.positive",
        evidence_refs=["source.bind.ortools.cpsat", "source.bind.ortools.scheduling"]
    ),
]

BINDING_EVALUATIONS = [
    rec("evaluation.bind.constraint_backend.varisat", "requirement_offer_evaluation", requirement_ref="requirement.bind.constraint_backend", offer_ref="offer.bind.varisat.candidate", structural="compatible_subset", semantic="unknown", constraints="not_evaluated", qualification="missing", allocation="not_applicable", runtime="not_evaluated", binding_result="typed_gap", gap_refs=["gap.bind.solver_qualification"], reason="SAT subset is documented, but exact SAN encodings, target and checker receipts are absent."),
    rec("evaluation.bind.constraint_backend.cvc5", "requirement_offer_evaluation", requirement_ref="requirement.bind.constraint_backend", offer_ref="offer.bind.cvc5.candidate", structural="candidate", semantic="unknown", constraints="not_evaluated", qualification="missing", allocation="not_applicable", runtime="not_evaluated", binding_result="typed_gap", gap_refs=["gap.bind.solver_qualification", "gap.bind.proof_profiles"], reason="Documentation occurrence does not identify an executable artifact/target/configuration."),
    rec("evaluation.bind.constraint_backend.minizinc", "requirement_offer_evaluation", requirement_ref="requirement.bind.constraint_backend", offer_ref="offer.bind.minizinc.candidate", structural="modeling_frontend_only", semantic="unknown", constraints="not_evaluated", qualification="missing", allocation="not_applicable", runtime="not_evaluated", binding_result="typed_gap", gap_refs=["gap.bind.solver_qualification"], reason="Modeling frontend and underlying solver offers must remain distinct."),
    rec("evaluation.bind.unsat_checker.varisat", "requirement_offer_evaluation", requirement_ref="requirement.bind.unsat_checker", offer_ref="offer.bind.varisat.candidate", structural="candidate_for_drat", semantic="profile_specific", constraints="not_evaluated", qualification="missing", allocation="not_applicable", runtime="not_evaluated", binding_result="typed_gap", gap_refs=["gap.bind.proof_profiles", "gap.bind.solver_qualification"], reason="Proof logging is not an approved independently executed checker receipt."),
    rec("evaluation.bind.objective.goodlp", "requirement_offer_evaluation", requirement_ref="requirement.bind.objective_evaluator", offer_ref="offer.bind.goodlp.candidate", structural="candidate_for_linear_models", semantic="unknown", constraints="not_evaluated", qualification="missing", allocation="not_applicable", runtime="not_evaluated", binding_result="typed_gap", gap_refs=["gap.bind.optimization_units", "gap.bind.solver_qualification"], reason="A modeling facade is not an optimizer guarantee, and objective authority is absent."),
    rec("evaluation.bind.incremental.salsa", "requirement_offer_evaluation", requirement_ref="requirement.bind.incremental_engine", offer_ref="offer.bind.salsa.candidate", structural="candidate", semantic="unknown", constraints="not_evaluated", qualification="missing", allocation="not_applicable", runtime="not_evaluated", binding_result="typed_gap", gap_refs=["gap.bind.solver_qualification"], reason="Tracked-query documentation does not prove SAN support-set closure or clean-rebind equivalence."),
    rec("evaluation.bind.admission.k8s", "requirement_offer_evaluation", requirement_ref="requirement.bind.resource_admission", offer_ref="offer.bind.k8s.scheduler.class", structural="partial_candidate", semantic="unknown", constraints="not_evaluated", qualification="missing", allocation="missing_occurrence", runtime="not_evaluated", binding_result="typed_gap", gap_refs=["gap.bind.target_occurrences", "gap.bind.allocator"], reason="Scheduler class documentation is neither admission authority nor deployed capacity."),
    rec("evaluation.bind.admission.nomad", "requirement_offer_evaluation", requirement_ref="requirement.bind.resource_admission", offer_ref="offer.bind.nomad.scheduler.class", structural="partial_candidate", semantic="unknown", constraints="not_evaluated", qualification="missing", allocation="missing_occurrence", runtime="not_evaluated", binding_result="typed_gap", gap_refs=["gap.bind.target_occurrences", "gap.bind.allocator"], reason="Feasibility/ranking/allocation-plan concepts do not supply an exact occurrence receipt."),
    rec("evaluation.bind.lp_safe.ortools_glop_mpsolver_python.9_15_6755", "requirement_offer_evaluation", requirement_ref="requirement.bind.lp_safe_status_objective", offer_ref="offer.bind.ptr.ortools.glop_mpsolver_python.9_15_6755", structural="exact_capability_subset", semantic="executed_safe_profile_pass", constraints="six_fixture_oracle_pass", qualification="executed_not_independently_appraised", allocation="not_applicable", runtime="single_isolated_probe_occurrence_only", binding_result="typed_gap", gap_refs=["gap.bind.independent_appraisal", "gap.bind.solver_qualification"], source_qualification_assessment_refs=["qualification.ptr.ortools.glop_mpsolver_python.9_15_6755.safe_status_and_objective"], source_execution_receipt_refs=["receipt.run-20260826-macos-arm64-python3_14-001.ortools_glop_mpsolver.safe_status_and_objective"], reason="The safe no-strengthening profile passed on one exact target, but executed internal evidence is not independent qualification or production acceptance."),
    rec("evaluation.bind.lp_safe.highspy_highs.1_15_1", "requirement_offer_evaluation", requirement_ref="requirement.bind.lp_safe_status_objective", offer_ref="offer.bind.ptr.highspy.highs.1_15_1", structural="exact_capability_subset", semantic="executed_safe_profile_pass", constraints="six_fixture_oracle_pass", qualification="executed_not_independently_appraised", allocation="not_applicable", runtime="single_isolated_probe_occurrence_only", binding_result="typed_gap", gap_refs=["gap.bind.independent_appraisal", "gap.bind.solver_qualification"], source_qualification_assessment_refs=["qualification.ptr.highspy.highs.1_15_1.safe_status_and_objective"], source_execution_receipt_refs=["receipt.run-20260826-macos-arm64-python3_14-001.highspy_highs.safe_status_and_objective"], reason="The safe profile passed on one exact target, but the evidence has no independent appraisal or broader qualification."),
    rec("evaluation.bind.lp_precise.ortools_glop_mpsolver_python.9_15_6755", "requirement_offer_evaluation", requirement_ref="requirement.bind.lp_precise_terminal", offer_ref="offer.bind.ptr.ortools.glop_mpsolver_python.9_15_6755", structural="required_capability_absent", semantic="executed_precise_profile_fail", constraints="known_unbounded_fixture_misclassified_by_surface", qualification="scoped_rejection", allocation="not_applicable", runtime="single_isolated_probe_occurrence_only", binding_result="refused", gap_refs=["gap.bind.lp_precise_status"], source_qualification_assessment_refs=["qualification.ptr.ortools.glop_mpsolver_python.9_15_6755.precise_terminal_classification"], source_execution_receipt_refs=["receipt.run-20260826-macos-arm64-python3_14-001.ortools_glop_mpsolver.precise_terminal_classification"], reason="This exact interface cannot satisfy a contract requiring precise infeasible-versus-unbounded classification; the binder must not strengthen its status."),
    rec("evaluation.bind.lp_precise.highspy_highs.1_15_1", "requirement_offer_evaluation", requirement_ref="requirement.bind.lp_precise_terminal", offer_ref="offer.bind.ptr.highspy.highs.1_15_1", structural="exact_capability_subset", semantic="executed_precise_profile_pass", constraints="six_fixture_oracle_pass", qualification="executed_not_independently_appraised", allocation="not_applicable", runtime="single_isolated_probe_occurrence_only", binding_result="typed_gap", gap_refs=["gap.bind.independent_appraisal", "gap.bind.solver_qualification"], source_qualification_assessment_refs=["qualification.ptr.highspy.highs.1_15_1.precise_terminal_classification"], source_execution_receipt_refs=["receipt.run-20260826-macos-arm64-python3_14-001.highspy_highs.precise_terminal_classification"], reason="The precise terminal profile passed on one target, but independent appraisal and full qualification remain absent."),
    rec("evaluation.bind.cp_sat_exact.ortools_cp_sat_python.9_15_6755", "requirement_offer_evaluation", requirement_ref="requirement.bind.cp_sat_exact_scope", offer_ref="offer.bind.ptr.ortools.cp_sat_python.9_15_6755", structural="exact_capability_subset", semantic="executed_core_global_scheduling_limit_profiles_pass", constraints="ten_fixture_oracle_pass_for_declared_non_enumeration_profiles", qualification="executed_not_independently_appraised", allocation="not_applicable", runtime="single_corrected_isolated_probe_occurrence_only", binding_result="typed_gap", gap_refs=["gap.bind.independent_appraisal", "gap.bind.solver_qualification"], source_qualification_assessment_refs=["qualification.ptr.ortools.cp_sat_python.9_15_6755.core", "qualification.ptr.ortools.cp_sat_python.9_15_6755.global_constraints", "qualification.ptr.ortools.cp_sat_python.9_15_6755.scheduling", "qualification.ptr.ortools.cp_sat_python.9_15_6755.limit_no_strengthening"], source_execution_receipt_refs=["receipt.run-20260826-cpsat-macos-arm64-python3_14-002.ortools_cp_sat_python.core", "receipt.run-20260826-cpsat-macos-arm64-python3_14-002.ortools_cp_sat_python.global_constraints", "receipt.run-20260826-cpsat-macos-arm64-python3_14-002.ortools_cp_sat_python.scheduling", "receipt.run-20260826-cpsat-macos-arm64-python3_14-002.ortools_cp_sat_python.limit_no_strengthening"], reason="The declared exact fragment passed on one corrected configuration, but no independent appraisal, full provider qualification or vertical acceptance exists."),
    rec("evaluation.bind.cp_sat_enumeration.pre_parameter", "requirement_offer_evaluation", requirement_ref="requirement.bind.cp_sat_complete_enumeration", offer_ref="offer.bind.ptr.ortools.cp_sat_python.9_15_6755", structural="offer_capability_present_configuration_incompatible", semantic="executed_enumeration_profile_fail", constraints="callback_observed_one_of_two_solutions", qualification="scoped_rejection", allocation="not_applicable", runtime="pre_enumeration_parameter_probe_occurrence", binding_result="refused", gap_refs=["gap.bind.cp_sat_enumeration_configuration"], source_qualification_assessment_refs=["qualification.ptr.ortools.cp_sat_python.9_15_6755.pre_enumeration.enumeration"], source_execution_receipt_refs=["receipt.run-20260826-cpsat-macos-arm64-python3_14-001.ortools_cp_sat_python.enumeration"], reason="A callback without the provider's exhaustive-enumeration parameter is not a complete-enumeration implementation."),
    rec("evaluation.bind.cp_sat_enumeration.corrected", "requirement_offer_evaluation", requirement_ref="requirement.bind.cp_sat_complete_enumeration", offer_ref="offer.bind.ptr.ortools.cp_sat_python.9_15_6755", structural="exact_capability_and_configuration_subset", semantic="executed_enumeration_profile_pass", constraints="two_of_two_solutions_independently_validated", qualification="executed_not_independently_appraised", allocation="not_applicable", runtime="single_corrected_isolated_probe_occurrence_only", binding_result="typed_gap", gap_refs=["gap.bind.independent_appraisal", "gap.bind.solver_qualification"], source_qualification_assessment_refs=["qualification.ptr.ortools.cp_sat_python.9_15_6755.enumeration"], source_execution_receipt_refs=["receipt.run-20260826-cpsat-macos-arm64-python3_14-002.ortools_cp_sat_python.enumeration"], reason="The corrected configuration passed exact-scope enumeration, but its receipt remains internal, occurrence-scoped and unqualified."),
]

TRACE_CONTRACTS = [
    rec("tracecontract.bind.pass", "trace_contract", subject="compiler pass", required_fields=["pass_id", "input_snapshot_digests", "output_digest", "started_monotonic_sequence", "decision_refs", "support_set", "status", "diagnostic_refs"], status_domain=["succeeded", "refused", "failed", "cancelled", "unknown"], law="A pass trace never substitutes for its proof receipts."),
    rec("tracecontract.bind.candidate", "trace_contract", subject="requirement-offer edge", required_fields=["requirement_id", "offer_id", "structural_reasons", "semantic_claims", "rejections", "evidence_refs"], status_domain=["candidate", "rejected", "unknown"], law="Every considered edge and rejection remains inspectable."),
    rec("tracecontract.bind.solve", "trace_contract", subject="solver invocation", required_fields=["constraint_digest", "backend_artifact_digest", "configuration_digest", "limits", "status", "model_or_proof_digest", "checker_receipt_ref"], status_domain=["sat", "unsat", "unknown", "cancelled", "backend_error"], law="Unknown and backend error cannot become unsat."),
    rec("tracecontract.bind.rank", "trace_contract", subject="objective selection", required_fields=["feasible_set_digest", "objective_law_ref", "objective_vectors", "frontier", "selected_ref", "tie_break"], status_domain=["selected", "frontier_unresolved", "refused"], law="Ranking consumes only hard-feasible candidates."),
    rec("tracecontract.bind.qualification", "trace_contract", subject="qualification", required_fields=["profile_id", "subject_digest", "target_occurrence", "configuration_digest", "input_domain", "checker", "observations", "validity", "status"], status_domain=["passed", "failed", "unknown", "expired", "revoked"], law="Receipt scope cannot be widened by the binder."),
    rec("tracecontract.bind.invalidation", "trace_contract", subject="incremental rebind", required_fields=["change_event", "changed_keys", "support_edges", "dirty_claims", "retained_receipts", "recomputed_receipts", "clean_equivalence_digest"], status_domain=["rebound", "refused", "clean_mismatch"], law="A retained receipt must prove that no invalidation trigger intersects its support set."),
    rec("tracecontract.bind.provider_target_projection", "trace_contract", subject="provider-target registry projection", required_fields=["source_registry_digest", "source_offer_ref", "artifact_ref", "target_occurrence_refs", "compatibility_refs", "qualification_assessment_refs", "binding_eligible"], status_domain=["projected_exactly", "refused_drift", "source_missing"], law="Projection can preserve or weaken upstream claims but can never promote them."),
]

RECORD_SCHEMA = {
    "$schema":"https://json-schema.org/draft/2020-12/schema",
    "type":"object",
    "required":["id","record_kind","edition","status"],
    "properties":{
        "id":{"type":"string","pattern":"^[a-z][a-z0-9]*(\\.[a-z0-9_:-]+)+$"},
        "record_kind":{"type":"string","minLength":1},
        "edition":{"const":1},
        "status":{"const":STATUS}
    },
    "additionalProperties":True
}

EXAMPLE_SCHEMA = {
    "$schema":"https://json-schema.org/draft/2020-12/schema",
    "allOf":[{"$ref":"record.schema.json"}],
    "type":"object",
    "required":["id","record_kind","edition","status","vertical","polarity","intent","requirements","trace","terminal_result","terminal_gaps","negative_twin_ref","evidence_refs"],
    "properties":{
        "record_kind":{"const":"binding_example"},
        "polarity":{"enum":["positive","negative_twin"]},
        "terminal_result":{"enum":["bound","partially_bound","unsat","unknown","refused"]},
        "trace":{"type":"array","minItems":2}
    }
}

CATALOGS = {
    "binding-phases.jsonl": PHASES,
    "constraint-kinds.jsonl": CONSTRAINT_KINDS,
    "algorithms.jsonl": ALGORITHMS,
    "compiler-passes.jsonl": PASSES,
    "diagnostics.jsonl": DIAGNOSTICS,
    "proof-contracts.jsonl": PROOF_CONTRACTS,
    "decision-points.jsonl": DECISIONS,
    "requirements.jsonl": REQUIREMENTS,
    "offers.jsonl": OFFERS,
    "library-boundaries.jsonl": LIBRARIES,
    "rust-applicability.jsonl": RUST_APPLICABILITY,
    "invalidation-rules.jsonl": INVALIDATIONS,
    "innovations-2021-2026.jsonl": INNOVATIONS,
    "gaps.jsonl": GAPS,
    "examples.jsonl": EXAMPLES,
    "requirement-offer-evaluations.jsonl": BINDING_EVALUATIONS,
    "trace-contracts.jsonl": TRACE_CONTRACTS,
}


if __name__ == "__main__":
    main()
