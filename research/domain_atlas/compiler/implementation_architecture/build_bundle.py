#!/usr/bin/env python3
"""Build the deterministic implementation-architecture research bundle.

The generator is deliberately boring: fixed inputs, sorted records, canonical JSON,
no clock, network, locale, random source or filesystem enumeration order.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
COMPILER = ROOT.parent
EDITION = 1
STATUS = "researched_candidate_not_implemented"


def stable_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def write_json(path: Path, value: object) -> None:
    path.write_text(stable_json(value) + "\n", encoding="utf-8", newline="\n")


def write_jsonl(path: Path, rows: list[dict], id_key: str = "id") -> None:
    ordered = sorted(rows, key=lambda row: row[id_key])
    path.write_text("".join(stable_json(row) + "\n" for row in ordered), encoding="utf-8", newline="\n")


# slug, question, owns, excludes, input, output, invariant, family
CONTEXTS = [
    ("intent_language", "What exact declarations may an author make?", "grammar, declaration kinds, explicit defaults", "resolution and effects", "source bytes", "lossless concrete syntax tree", "unknown syntax is an error, never an extension guess", "front_end"),
    ("lexing_parsing", "How are bytes converted into anchored syntax?", "lexing, parsing, error recovery, source spans", "name meaning", "source bytes plus language edition", "token stream and CST", "recovery nodes cannot silently become valid declarations", "front_end"),
    ("module_import", "Which exact modules and snapshots are imported?", "import graph, cycle policy, import integrity", "semantic alias adjudication", "CST imports and lock snapshot", "closed module graph", "mutable or floating imports are refused", "identity"),
    ("declaration_ast", "What authored structure survives parsing?", "typed declaration AST and source anchors", "canonical identity resolution", "CST", "declaration AST", "AST construction preserves omissions and authored order", "front_end"),
    ("schema_validation", "Does authored data satisfy its declared structural contract?", "schema edition and structural validation", "domain truth", "documents and exact schema identity", "validation report", "schema-valid never implies semantically valid", "front_end"),
    ("source_anchor", "Where did every claim originate?", "byte spans, document identities, generated anchors", "claim correctness", "source snapshot", "stable anchors", "normalization cannot erase original evidence location", "evidence"),
    ("exact_identity", "What exact thing does a reference denote?", "stable ID, edition, occurrence, digest separation", "alias authorization", "raw reference", "identity query", "identity, edition, occurrence and digest never collapse", "identity"),
    ("edition_resolution", "Which exact compatible edition is selected?", "edition constraints, lock resolution, coexistence", "semantic compatibility proof", "identity plus edition constraint", "locked edition graph", "resolution has no floating latest default", "identity"),
    ("namespace_context", "In which bounded vocabulary is a name interpreted?", "namespaces, scoped names, context ownership", "cross-context translation", "name plus context", "scoped symbol", "one spelling may denote different concepts across contexts", "identity"),
    ("canonical_reference", "Is a foreign occurrence authorized to map to a canonical concept?", "asserted mappings and counterclaims", "automatic ontology invention", "source occurrence and candidate IDs", "adjudicated mapping or gap", "string similarity is never authority", "adjudication"),
    ("review_queue", "Which uncertain mappings require human authority?", "review batches, dispositions, evidence links", "silent compiler fallback", "mapping candidates", "signed review decisions", "unreviewed means unresolved", "adjudication"),
    ("authority_precedence", "Whose decision controls each configurable point?", "authority scopes, precedence, delegation, revocation", "business policy content", "claims and authorities", "effective decision set", "ties or gaps in required authority stop compilation", "policy"),
    ("context_language", "What does each term mean inside a bounded context?", "glossary terms, homonyms, translations", "global universal vocabulary", "context definitions", "editioned language graph", "translations are explicit directional claims", "semantics"),
    ("hypergraph_model", "How are n-ary typed claims represented without flattening meaning?", "typed nodes, relation claims, roles, scopes", "physical persistence", "resolved semantic records", "immutable graph batch", "n-ary relations are reified; edge labels are typed IDs", "graph"),
    ("graph_storage", "How are immutable graph batches durably stored?", "append, lookup, snapshot persistence ports", "semantic inference", "canonical graph batch", "commit receipt", "storage success is not graph validity", "storage"),
    ("graph_index", "Which exact indexes accelerate closed queries?", "identity, edition, adjacency, reverse-support indexes", "truth ownership", "committed graph snapshot", "rebuildable indexes", "index loss cannot lose canonical facts", "storage"),
    ("graph_transaction", "What changes become visible atomically?", "optimistic transaction, expected snapshot, conflict", "distributed consensus implementation", "base snapshot and patch", "new snapshot or conflict", "partial graph publication is impossible", "storage"),
    ("snapshot_lock", "What immutable corpus does one compilation observe?", "snapshot manifests and transitive digests", "live discovery", "registry roots", "frozen compilation snapshot", "a run never mixes registry revisions", "identity"),
    ("content_address", "What bytes are content-identical?", "digest suites, domain separation, digest verification", "stable business identity", "canonical bytes", "content digest", "digest equality proves bytes only", "identity"),
    ("canonical_serialization", "Which unique bytes encode a semantic record?", "ordering, number/string policy, encoding edition", "semantic canonicalization", "typed record", "canonical bytes", "unsupported numbers or ambiguous maps are refused", "serialization"),
    ("semantic_type_system", "What values and relations are legal?", "semantic kinds, carriers, units, nullability, refinements", "external truth", "resolved IR", "typed IR or diagnostics", "no string-dispatched types", "checking"),
    ("law_catalog", "Which executable and documentary laws constrain meaning?", "law identity, scope, checker, counterexample domain", "proof execution", "law declarations", "closed law set", "a prose law without a checker remains unproved", "checking"),
    ("type_checker", "Does every node satisfy kind, type, cardinality and effect rules?", "typing judgments and derivations", "provider qualification", "resolved IR and type environment", "typed IR receipt", "error recovery never manufactures a successful derivation", "checking"),
    ("law_checker", "Are required invariants discharged at their exact scope?", "law dispatch by typed identity, proof status", "solver truth", "typed IR and proof obligations", "proved, contradicted or unknown", "unknown is never proved", "checking"),
    ("effect_system", "Which operations are pure, planned or effectful?", "effect capabilities, authority and receipts", "runtime execution", "typed operations", "effect-annotated IR", "compile planning cannot authorize runtime mutation", "checking"),
    ("lifecycle_typestate", "Are lifecycle transitions legal at compile time?", "states, transitions, constructors, refusal catalog", "runtime observation", "entity state IR", "transition proof", "illegal transitions are unrepresentable or refused", "checking"),
    ("pass_registry", "Which exact pass implementation may run?", "pass IDs, editions, pre/postconditions, digests", "pass scheduling", "registered pass offers", "qualified pass registry", "a pass name cannot select implementation", "passes"),
    ("pass_scheduler", "What deterministic pass order respects dependencies?", "phase graph, stable topological schedule, barriers", "pass semantics", "qualified pass set", "pass schedule", "ambiguous cycles stop; independent order has stable tie-break", "passes"),
    ("rewrite_engine", "How are local transformations proposed and applied?", "typed patterns, match sets, rewrite receipts", "equivalence truth", "IR and rewrite rules", "candidate rewritten IR", "matches are enumerated in canonical order", "passes"),
    ("equivalence_checker", "Does an optimization preserve declared meaning?", "equivalence obligations and checker adapters", "cost ranking", "before/after IR and law scope", "proof, contradiction or unknown", "cost never proves equivalence", "proof"),
    ("stage_legality", "Is every node legal in the current IR stage?", "stage ownership, allowed kinds, materialization gaps", "lowering choice", "IR stage", "legality report", "unknown or illegal nodes block full lowering", "passes"),
    ("requirement_ir", "What exact capability must a solution provide?", "directional semantic, structural, policy and resource requirements", "offer discovery", "lowered intent", "requirement graph", "hard requirements cannot become weights", "binding"),
    ("offer_ir", "What exact capability does an implementation claim?", "offer scope, exclusions, decisions, evidence requirements", "provider truth", "registry offer declarations", "offer graph", "marketing names confer no capability", "binding"),
    ("candidate_enumerator", "Which offers are structurally eligible for deeper checking?", "indexed candidate and rejection enumeration", "semantic proof", "requirements and offers", "candidate graph", "structural match is never semantic satisfaction", "binding"),
    ("semantic_subsumption", "Does an offer directionally satisfy a semantic requirement?", "types, laws, loss, variance, applicability", "global feasibility", "candidate edge", "proved, contradicted or unknown edge", "unknown mappings fail closed", "binding"),
    ("constraint_ir", "How are named hard constraints and preferences represented?", "atoms, theories, supports, objective dimensions", "solver implementation", "checked candidate graph", "solver-neutral problem", "hard and soft constraints have distinct types", "solver"),
    ("solver_adapter", "How is a finite problem submitted to an exact solver?", "solver SPI, limits, result verification", "business objective choice", "constraint problem and budget", "sat, unsat, unknown or refused", "timeouts and unsupported theories are unknown, not unsat", "solver"),
    ("model_checker", "Does a returned model really satisfy the submitted problem?", "independent model and proof checking", "solver search", "problem, model or proof", "checked result receipt", "unchecked solver output cannot bind", "proof"),
    ("objective_selection", "How are feasible alternatives compared?", "lexicographic, Pareto and satisficing policies", "feasibility", "feasible models and authority policy", "selected frontier and trace", "weighted sums require declared units and normalization", "solver"),
    ("unsat_diagnostics", "Why can no solution satisfy the exact intent?", "named cores, explanations, repair candidates", "claim of minimum core", "checked unsat result", "sufficient core and diagnostics", "sufficient is not minimal unless separately proved", "diagnostics"),
    ("qualification_registry", "Which exact implementation/config/target claims were tested?", "receipts, scopes, expiry and invalidation", "live capacity", "qualification evidence", "valid or stale qualification", "documentation is not a qualification receipt", "qualification"),
    ("provider_occurrence", "Which deployed provider occurrence exists now?", "organization, offer, region, edition, configuration occurrence", "semantic ownership", "provider observations", "occurrence snapshot", "provider class is not occurrence", "qualification"),
    ("resource_admission", "Can finite budgets and quotas admit the plan?", "demand, budget, quota, reservation, lease contracts", "scheduler execution", "physical requirements and live offers", "admission plan or refusal", "capacity, quota, budget, allocation and usage do not collapse", "runtime"),
    ("physical_plan", "Which qualified algorithms, kernels and resources realize logical intent?", "physical operator graph and fallback plans", "runtime mutation", "bound logical plan", "effect-free physical plan", "unqualified targets remain typed gaps", "runtime"),
    ("backend_registry", "Which deterministic backend can emit a target contract?", "backend offers, ABI and target feature checks", "backend execution", "physical plan and target profile", "backend binding", "backend selection cannot re-decide semantics", "codegen"),
    ("codegen_interface", "How is checked IR translated into target artifacts?", "backend SPI, source maps, emission receipts", "build execution", "backend-bound IR", "artifact plan", "generation is deterministic for exact inputs", "codegen"),
    ("build_interface", "How are declared build actions executed hermetically?", "action graph, environment, toolchain and result receipts", "semantic proof", "artifact plan and locked tools", "build artifacts and logs", "undeclared input invalidates the action key", "build"),
    ("artifact_store", "Where are immutable generated and built artifacts retained?", "put/get by digest, retention and corruption checks", "semantic identity", "artifact bytes", "artifact receipt", "mutable tags are never artifact identity", "storage"),
    ("evidence_store", "Where are scoped claims and raw observations retained?", "claim-evidence graph, validity and recording time", "claim adjudication", "evidence records", "immutable evidence snapshot", "evidence scope travels with the observation", "evidence"),
    ("provenance_attestation", "How are subject, process and signer claims separated?", "provenance statements, envelopes, trust policy", "claim truth", "artifact and build receipt", "attestation set", "signature authenticates bytes, not truth or authorization", "evidence"),
    ("incremental_dep_graph", "Which computations depend on which exact inputs?", "query keys, support sets, old/new dependency graph", "semantic change classification", "query reads and outputs", "dependency snapshot", "every result-affecting read becomes support", "incremental"),
    ("invalidation_engine", "What must be recomputed after an exact change?", "change keys, transitive dirty closure, durability policy", "migration execution", "old/new snapshots", "dirty query set", "incremental result must equal clean result", "incremental"),
    ("cache", "When may a prior result be safely reused?", "action keys, trust namespace, eviction, negative cache", "proof of semantic truth", "query/action key and receipt", "cache hit or miss", "cache key completeness is a proof obligation", "incremental"),
    ("concurrency", "Which independent computations may execute together?", "deterministic scheduling boundaries and isolation", "semantic ordering", "pass/query DAG", "concurrent execution plan", "parallelism cannot change canonical outputs", "runtime"),
    ("cancellation_budget", "How do time, memory and work limits stop safely?", "cancellation tokens, fuel, deadlines, cleanup", "unsat inference", "work plan and finite budgets", "completed or cancelled result", "cancelled means unknown/partial, never success or unsat", "runtime"),
    ("transaction_replay", "Can a prior compilation be replayed exactly?", "journals, snapshot roots, pass receipts and replay", "external effect replay", "compilation record", "replay comparison", "replay performs no undeclared external effects", "migration"),
    ("migration", "How do schema, IR and registry editions evolve?", "upcasters, semantic diffs, dual reads, cutover plans", "automatic destructive rollout", "old/new editions", "migration plan and residual gaps", "migration is a plan, not authority to mutate", "migration"),
    ("extension_plugin", "How can new semantics or backends be isolated?", "editioned extension manifests, capabilities, sandbox", "core semantic mutation", "signed plugin artifact and manifest", "qualified extension offer", "unknown extension semantics remain opaque and unbindable", "extension"),
    ("optional_agent", "How may models or agents propose work without becoming authorities?", "proposal, tool-intent and validation seam", "canonical adjudication and proof", "bounded prompt/tool contract", "untrusted proposal", "all proposals pass deterministic validation and authority", "extension"),
    ("security_policy", "What may each compiler component read, compute and emit?", "capabilities, trust boundaries, secrets, tenant isolation", "enterprise policy authorship", "principal and operation", "permit, deny or indeterminate", "deny/indeterminate cannot become permit", "security"),
    ("resource_accounting", "What work and storage did compilation consume?", "typed CPU, memory, I/O, network and cost observations", "business value", "runtime receipts", "usage ledger", "estimated, reserved and observed resources remain distinct", "runtime"),
    ("diagnostic_protocol", "How are refusals, gaps and source-linked explanations exposed?", "stable codes, spans, causes, fixes and machine payloads", "truth inference", "failed judgment", "diagnostic graph", "human text is rendering; code and typed payload are contract", "diagnostics"),
    ("cli_api", "What stable batch interface does the tool expose?", "commands, exit semantics, stdin/stdout contracts", "interactive UI", "arguments and snapshots", "artifacts, diagnostics and exit status", "stdout machine mode is canonical and log-free", "api"),
    ("library_api", "What embeddable Rust interface exposes compilation?", "request/result types, sync boundaries and effect ports", "global singleton state", "CompilationRequest", "CompilationOutcome", "library behavior equals CLI behavior for same inputs", "api"),
    ("observability", "How can compiler behavior be inspected without changing it?", "structured traces, metrics, pass timing and audit events", "semantic result", "execution events", "telemetry artifacts", "telemetry failure cannot alter canonical compilation output", "operations"),
    ("testing_conformance", "What proves implementations honor the architecture contracts?", "goldens, properties, fuzzing, model checking, independent implementations", "production qualification", "implementations and test domains", "conformance receipts", "one green example never establishes general conformance", "testing"),
]


assert len(CONTEXTS) >= 60


EXTRA_SOURCES = [
    ("Rust Reference", "Rust Project", "official_documentation", "https://doc.rust-lang.org/reference/"),
    ("Rust Compiler Development Guide: Query System", "Rust Project", "official_documentation", "https://rustc-dev-guide.rust-lang.org/query.html"),
    ("Rust Compiler Development Guide: Incremental Compilation", "Rust Project", "official_documentation", "https://rustc-dev-guide.rust-lang.org/queries/incremental-compilation-in-detail.html"),
    ("Salsa overview", "Salsa Project", "official_documentation", "https://salsa-rs.github.io/salsa/overview.html"),
    ("Salsa algorithm", "Salsa Project", "official_documentation", "https://salsa-rs.github.io/salsa/reference/algorithm.html"),
    ("Rowan crate documentation", "rust-analyzer Project", "official_documentation", "https://docs.rs/rowan/latest/rowan/"),
    ("Petgraph crate documentation", "Petgraph Project", "official_documentation", "https://docs.rs/petgraph/latest/petgraph/"),
    ("SlotMap crate documentation", "SlotMap Project", "official_documentation", "https://docs.rs/slotmap/latest/slotmap/"),
    ("Serde data model", "Serde Project", "official_documentation", "https://serde.rs/data-model.html"),
    ("rkyv crate documentation", "rkyv Project", "official_documentation", "https://docs.rs/rkyv/latest/rkyv/"),
    ("Postcard wire format", "Postcard Project", "official_documentation", "https://postcard.jamesmunns.com/wire-format.html"),
    ("BLAKE3 specification", "BLAKE3 Team", "official_specification", "https://github.com/BLAKE3-team/BLAKE3-specs/blob/master/blake3.pdf"),
    ("JSON Canonicalization Scheme", "IETF", "open_specification", "https://www.rfc-editor.org/rfc/rfc8785"),
    ("Concise Binary Object Representation", "IETF", "open_specification", "https://www.rfc-editor.org/rfc/rfc8949"),
    ("SQLite atomic commit", "SQLite Project", "official_documentation", "https://sqlite.org/atomiccommit.html"),
    ("SQLite isolation", "SQLite Project", "official_documentation", "https://sqlite.org/isolation.html"),
    ("redb crate documentation", "redb Project", "official_documentation", "https://docs.rs/redb/latest/redb/"),
    ("Tower Service trait", "Tower Project", "official_documentation", "https://docs.rs/tower-service/latest/tower_service/trait.Service.html"),
    ("Tokio CancellationToken", "Tokio Project", "official_documentation", "https://docs.rs/tokio-util/latest/tokio_util/sync/struct.CancellationToken.html"),
    ("Rayon crate documentation", "Rayon Project", "official_documentation", "https://docs.rs/rayon/latest/rayon/"),
    ("Loom crate documentation", "Tokio Project", "official_documentation", "https://docs.rs/loom/latest/loom/"),
    ("Wasmtime ResourceLimiter", "Bytecode Alliance", "official_documentation", "https://docs.rs/wasmtime/latest/wasmtime/trait.ResourceLimiter.html"),
    ("Wasmtime fuel", "Bytecode Alliance", "official_documentation", "https://docs.wasmtime.dev/api/wasmtime/struct.Config.html#method.consume_fuel"),
    ("WebAssembly Component Model", "Bytecode Alliance", "open_specification", "https://component-model.bytecodealliance.org/"),
    ("WASI capability model", "Bytecode Alliance", "official_documentation", "https://github.com/WebAssembly/WASI/blob/main/docs/Capabilities.md"),
    ("MLIR Language Reference", "LLVM Project", "official_specification", "https://mlir.llvm.org/docs/LangRef/"),
    ("MLIR Pass Infrastructure", "LLVM Project", "official_documentation", "https://mlir.llvm.org/docs/PassManagement/"),
    ("MLIR Dialect Conversion", "LLVM Project", "official_documentation", "https://mlir.llvm.org/docs/DialectConversion/"),
    ("MLIR Diagnostic Infrastructure", "LLVM Project", "official_documentation", "https://mlir.llvm.org/docs/Diagnostics/"),
    ("LLVM Language Reference", "LLVM Project", "official_specification", "https://llvm.org/docs/LangRef.html"),
    ("Tree-sitter documentation", "Tree-sitter Project", "official_documentation", "https://tree-sitter.github.io/tree-sitter/"),
    ("Language Server Protocol diagnostics", "Microsoft", "open_specification", "https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#diagnostic"),
    ("SMT-LIB Standard", "SMT-LIB Initiative", "open_specification", "https://smt-lib.org/language.shtml"),
    ("cvc5 proofs documentation", "cvc5 Project", "official_documentation", "https://cvc5.github.io/docs/latest/proofs/proofs.html"),
    ("Z3 guide", "Microsoft Research", "official_documentation", "https://microsoft.github.io/z3guide/"),
    ("OR-Tools CP-SAT", "Google", "official_documentation", "https://developers.google.com/optimization/cp/cp_solver"),
    ("MiniZinc Handbook", "MiniZinc Project", "official_documentation", "https://docs.minizinc.dev/en/stable/"),
    ("Clingo guide", "Potassco", "official_documentation", "https://github.com/potassco/guide/releases"),
    ("Cargo resolver", "Rust Project", "official_documentation", "https://doc.rust-lang.org/cargo/reference/resolver.html"),
    ("PubGrub guide", "PubGrub Project", "official_documentation", "https://pubgrub-rs-guide.netlify.app/"),
    ("Spack concretizer", "Spack Project", "official_documentation", "https://spack.readthedocs.io/en/latest/packaging_guide_creation.html#dependency-specifications"),
    ("Bazel Skyframe", "Bazel Project", "official_documentation", "https://bazel.build/reference/skyframe"),
    ("Bazel hermeticity", "Bazel Project", "official_documentation", "https://bazel.build/basics/hermeticity"),
    ("Buck2 DICE computations", "Meta", "official_documentation", "https://github.com/facebook/buck2/blob/main/dice/dice/docs/writing_computations.md"),
    ("Nix language derivations", "Nix Project", "official_documentation", "https://nix.dev/manual/nix/latest/language/derivations"),
    ("Apache Calcite architecture", "Apache Software Foundation", "official_documentation", "https://calcite.apache.org/docs/algebra.html"),
    ("Apache DataFusion architecture", "Apache Software Foundation", "official_documentation", "https://datafusion.apache.org/contributor-guide/architecture.html"),
    ("Substrait specification", "Substrait Project", "open_specification", "https://substrait.io/"),
    ("Differential Dataflow", "Frank McSherry", "original_research", "https://github.com/TimelyDataflow/differential-dataflow"),
    ("DBSP paper", "DBSP Authors", "original_research", "https://arxiv.org/abs/2203.16684"),
    ("W3C PROV-O", "W3C", "open_specification", "https://www.w3.org/TR/prov-o/"),
    ("SPARQL 1.1 Query", "W3C", "open_specification", "https://www.w3.org/TR/sparql11-query/"),
    ("RDF 1.2 Concepts", "W3C", "open_specification", "https://www.w3.org/TR/rdf12-concepts/"),
    ("OCI Image Specification", "Open Container Initiative", "open_specification", "https://github.com/opencontainers/image-spec"),
    ("SLSA specification", "OpenSSF", "open_specification", "https://slsa.dev/spec/"),
    ("in-toto Attestation Framework", "in-toto Project", "open_specification", "https://github.com/in-toto/attestation"),
    ("The Update Framework", "TUF Project", "open_specification", "https://theupdateframework.github.io/specification/latest/"),
    ("Sigstore bundle format", "Sigstore Project", "open_specification", "https://docs.sigstore.dev/about/bundle/"),
    ("OpenTelemetry specification", "CNCF", "open_specification", "https://opentelemetry.io/docs/specs/"),
    ("JSON Schema 2020-12", "JSON Schema", "open_specification", "https://json-schema.org/draft/2020-12"),
    ("CUE language specification", "CUE Project", "open_specification", "https://cuelang.org/docs/reference/spec/"),
    ("Common Expression Language", "Google", "open_specification", "https://github.com/google/cel-spec"),
    ("SemVer 2.0.0", "Semantic Versioning", "open_specification", "https://semver.org/spec/v2.0.0.html"),
]


LIBRARIES = [
    ("source-model", "semantic_pure", "source snapshots, spans and diagnostics anchors", ["SourceSnapshot", "Span", "Anchored<T>"]),
    ("syntax", "algorithm_pure", "lossless parsing and explicit recovery nodes", ["SyntaxTree<Unresolved>", "ParseDiagnostic"]),
    ("declaration", "semantic_pure", "editioned authored declarations", ["DeclarationAst<E>", "ExplicitOrOmitted<T>"]),
    ("identity", "semantic_pure", "stable identity, edition, occurrence and digest newtypes", ["SemanticId", "EditionId", "OccurrenceId", "ContentDigest"]),
    ("module-graph", "algorithm_pure", "locked import closure and cycle diagnostics", ["ModuleGraph<Locked>", "ImportRef"]),
    ("canonical-reference", "semantic_pure", "authorized directional canonical mappings", ["MappingAssertion", "AdjudicationStatus"]),
    ("review-contract", "semantic_pure", "manual review queues and signed dispositions", ["ReviewBatch", "ReviewDecision"]),
    ("authority", "semantic_pure", "scoped authority, delegation and precedence", ["AuthorityScope", "DecisionOwner", "Precedence"]),
    ("hypergraph", "semantic_pure", "typed nodes and reified n-ary relation claims", ["Node<K>", "RelationClaim<R>", "RoleBinding"]),
    ("graph-index", "algorithm_pure", "rebuildable adjacency and support indexes", ["GraphIndex", "SupportSet"]),
    ("graph-store-contract", "effect_port", "atomic graph commits and immutable snapshots", ["GraphStore", "CommitIntent", "CommitReceipt"]),
    ("canonical-encoding", "algorithm_pure", "unique byte encoding and digest domain separation", ["CanonicalEncode", "DigestSuite"]),
    ("semantic-types", "semantic_pure", "closed compiler kinds and refinement contracts", ["SemanticType", "Refinement", "TypedValue<T>"]),
    ("law-model", "semantic_pure", "law identity, scope and three-valued proof status", ["LawId", "Obligation", "Judgment"]),
    ("type-checker", "algorithm_pure", "typing derivations and cardinality checking", ["TypeChecker", "Derivation"]),
    ("law-checker", "algorithm_pure", "typed law dispatch and scoped proof receipts", ["LawChecker<L>", "ProofReceipt"]),
    ("effects", "semantic_pure", "pure, planned and runtime effect distinctions", ["EffectSet", "EffectIntent", "EffectReceipt"]),
    ("lifecycle", "semantic_pure", "typestate transition rules", ["Entity<S>", "Transition<S,T>"]),
    ("ir-core", "semantic_pure", "staged IR nodes and legality", ["Ir<S>", "NodeKind", "StageLegality"]),
    ("pass-contract", "semantic_pure", "pass pre/postconditions and support sets", ["PassSpec<I,O>", "PassReceipt"]),
    ("pass-engine", "algorithm_pure", "stable scheduling and transactional pass application", ["PassEngine", "PassSchedule"]),
    ("rewrite", "algorithm_pure", "typed pattern matching and rewrite proposals", ["RewriteRule<I,O>", "RewriteTrace"]),
    ("equivalence", "algorithm_plus_checker_port", "optimization equivalence obligations", ["EquivalenceClaim", "EquivalenceChecker"]),
    ("requirements", "semantic_pure", "hard requirements and authorized preferences", ["Requirement<H>", "Preference<S>"]),
    ("offers", "semantic_pure", "scoped implementation offers and exclusions", ["Offer", "OfferScope"]),
    ("candidate-enumerator", "algorithm_pure", "structural candidate and rejection graph", ["CandidateEnumerator", "CandidateEdge"]),
    ("semantic-subsumption", "algorithm_plus_checker_port", "directional compatibility judgments", ["SubsumptionQuery", "CompatibilityJudgment"]),
    ("constraint-ir", "semantic_pure", "named solver-neutral atoms and objectives", ["Constraint<H>", "Theory", "ObjectiveVector"]),
    ("solver-spi", "effect_port", "sandboxed solver invocation and checked result", ["Solver", "SolveBudget", "SolveOutcome"]),
    ("objective-policy", "algorithm_pure", "Pareto, lexicographic and satisficing selection", ["SelectionPolicy", "FeasibleFrontier"]),
    ("diagnostics", "semantic_pure", "stable codes, cause graph and typed repair hints", ["DiagnosticCode", "Diagnostic", "RepairCandidate"]),
    ("qualification", "semantic_pure", "exact-scope qualification receipts and expiry", ["QualificationReceipt", "EvidenceScope"]),
    ("provider-target", "semantic_pure", "provider offers, targets and occurrences", ["ProviderOffer", "TargetProfile", "TargetOccurrence"]),
    ("admission", "semantic_plus_effect_port", "demand, budget, quota, reservation and lease", ["Demand", "Budget", "AdmissionOutcome"]),
    ("physical-plan", "semantic_pure", "qualified algorithms, kernels and fallback graph", ["PhysicalPlan<Qualified>", "FallbackPlan"]),
    ("backend-spi", "effect_port", "deterministic code-generation backend boundary", ["Backend", "ArtifactPlan", "EmissionReceipt"]),
    ("artifact-evidence-store", "effect_port", "digest-addressed artifacts and evidence", ["ArtifactStore", "EvidenceStore", "PutReceipt"]),
    ("incremental", "algorithm_pure", "query dependency tracking and dirty closure", ["QueryKey", "DependencyGraph", "InvalidationSet"]),
    ("runtime-control", "effect_port", "finite budgets, cancellation and isolated execution", ["Cancellation", "ResourceLimiter", "ExecutionReceipt"]),
    ("compiler-api", "application_orchestration", "CLI/library parity and compilation orchestration", ["CompilationRequest", "CompilationOutcome", "CompilerService"]),
]


PERSISTENCE = [
    ("semantic_node", "stable_id, kind_id, edition_id, payload_digest", "stable_id+edition_id"),
    ("relation_claim", "claim_id, relation_kind_id, scope_id, status", "claim_id"),
    ("role_binding", "claim_id, role_id, node_id, ordinal", "claim_id+role_id+ordinal"),
    ("source_anchor", "anchor_id, document_digest, byte_start, byte_end", "anchor_id"),
    ("authority_claim", "claim_id, principal_id, scope_id, valid_time, record_time", "claim_id"),
    ("mapping_assertion", "assertion_id, source_occurrence_id, canonical_id, disposition", "assertion_id"),
    ("snapshot_manifest", "snapshot_id, root_digests, schema_edition", "snapshot_id"),
    ("graph_commit", "commit_id, parent_snapshot_id, patch_digest, receipt_digest", "commit_id"),
    ("adjacency_index", "snapshot_id, relation_kind_id, node_id, direction, claim_ids", "snapshot_id+relation_kind_id+node_id+direction"),
    ("support_edge", "derived_id, input_key, reason_kind", "derived_id+input_key"),
    ("query_result", "query_key_digest, input_snapshot_id, result_digest, status", "query_key_digest+input_snapshot_id"),
    ("pass_receipt", "run_id, pass_id, pass_edition, input_digest, output_digest", "run_id+pass_id"),
    ("proof_receipt", "proof_id, obligation_id, checker_id, outcome, scope_digest", "proof_id"),
    ("diagnostic", "diagnostic_id, code_id, severity, subject_id, payload_digest", "diagnostic_id"),
    ("requirement", "requirement_id, subject_id, hard_or_soft, payload_digest", "requirement_id"),
    ("offer", "offer_id, artifact_id, target_scope, payload_digest", "offer_id"),
    ("candidate_edge", "requirement_id, offer_id, phase, judgment", "requirement_id+offer_id+phase"),
    ("qualification_receipt", "receipt_id, artifact_digest, target_occurrence_id, config_digest, expiry", "receipt_id"),
    ("artifact", "artifact_digest, media_type, size, store_receipt", "artifact_digest"),
    ("evidence_observation", "evidence_id, claim_id, valid_time, record_time, raw_digest", "evidence_id"),
    ("compilation_run", "run_id, request_digest, snapshot_id, outcome, output_manifest_digest", "run_id"),
    ("change_event", "event_id, changed_key, old_digest, new_digest, observed_at", "event_id"),
    ("migration_plan", "plan_id, from_edition, to_edition, state, residual_gap_ids", "plan_id"),
    ("effect_receipt", "receipt_id, intent_digest, authority_id, occurrence_id, outcome", "receipt_id"),
]


DIAGNOSTIC_CODES = [
    "syntax_unknown", "syntax_recovery_unresolved", "schema_edition_unknown", "import_unlocked", "import_cycle",
    "identity_unknown", "edition_missing", "edition_conflict", "occurrence_missing", "digest_mismatch",
    "namespace_ambiguous", "canonical_mapping_unreviewed", "canonical_mapping_conflict", "authority_missing", "authority_tie",
    "authority_revoked", "type_unknown", "kind_mismatch", "cardinality_violation", "unit_mismatch",
    "time_model_missing", "effect_forbidden", "lifecycle_transition_illegal", "law_checker_missing", "law_contradicted",
    "law_unknown", "stage_illegal_node", "pass_dependency_cycle", "pass_precondition_failed", "pass_nondeterministic",
    "rewrite_unproved", "requirement_unsatisfied", "offer_scope_mismatch", "semantic_subsumption_unknown", "constraint_theory_unsupported",
    "solver_timeout", "solver_unknown", "solver_model_invalid", "unsat_proof_invalid", "objective_authority_missing",
    "qualification_missing", "qualification_stale", "target_occurrence_stale", "resource_budget_exceeded", "admission_unknown",
    "backend_unqualified", "artifact_corrupt", "cache_key_incomplete", "cancellation_partial", "plugin_capability_denied",
    "plugin_edition_unsupported", "agent_output_untrusted", "migration_loss_unapproved", "replay_diverged", "security_indeterminate",
    "transaction_conflict", "evidence_scope_mismatch", "build_undeclared_input", "runtime_receipt_missing", "internal_invariant_broken",
]


INNOVATIONS = [
    (2021, "Cargo feature resolver version 2", "stronger feature unification boundaries inform editioned dependency solving"),
    (2021, "WebAssembly interface-types/component-model convergence", "typed portable extension interfaces without native ABI trust"),
    (2021, "SLSA provenance framework", "separates build provenance levels from artifact identity"),
    (2021, "Sigstore keyless signing public deployment", "short-lived identity and transparency material for artifact statements"),
    (2021, "OpenTelemetry trace context and semantic-convention maturation", "portable pass and effect tracing contracts"),
    (2021, "Alethe SMT proof format adoption", "solver proof exchange suitable for independent checking"),
    (2022, "DBSP incremental view-maintenance algebra", "incremental recomputation with algebraic correctness arguments"),
    (2022, "Buck2 DICE", "async demand-driven dependency computation with equality-based resurrection"),
    (2022, "SLSA v0.1 provenance predicate", "subject-bound build provenance standardization"),
    (2022, "Sigstore general availability", "production transparency and bundle verification workflows"),
    (2022, "CycloneDX 1.4 formulation and services expansion", "richer dependency and service artifact inventories"),
    (2022, "CUE workflow and module evolution", "constraints plus data as a configuration validation substrate"),
    (2023, "WASI Preview 2 and component model implementations", "capability-oriented plugin isolation with typed worlds"),
    (2023, "SLSA specification v1.0", "stable provenance tracks and explicit build claims"),
    (2023, "Cargo sparse registry protocol", "changes exact package-index occurrence and cache semantics"),
    (2023, "RFC 9457 Problem Details", "machine-stable diagnostics independent from human rendering"),
    (2023, "OCI image-spec 1.1 release candidates and referrers work", "artifact relations without mutable tag inference"),
    (2023, "cvc5 proof production expansion", "checkable proof objects for more solver theories"),
    (2023, "Substrait extension governance maturation", "editioned portable operation and type extension identities"),
    (2024, "SPDX 3.0", "graph-native software supply-chain data with profiles"),
    (2024, "CycloneDX 1.6", "cryptographic and formulation evidence in component inventories"),
    (2024, "DataFusion modular query-engine architecture publication", "explicit logical, physical and execution extension seams"),
    (2024, "Salsa tracked/interned input model redesign", "distinct identity and dependency semantics for incremental IR"),
    (2024, "WebAssembly component model async and resource design", "typed resource lifetimes at extension boundaries"),
    (2024, "in-toto attestation framework stabilization", "predicate-independent subject-bound evidence envelopes"),
    (2025, "RDF 1.2 working specifications", "modernized graph dataset, triple-term and interoperability semantics"),
    (2025, "MLIR bytecode and extensible dialect refinements", "versioned multi-level IR persistence and extension boundaries"),
    (2025, "Rust edition 2024 ecosystem adoption", "edition coexistence as distinct from package semantic version"),
    (2025, "OCI referrers production adoption", "content-addressed linkage among artifacts, SBOMs and attestations"),
    (2026, "Salsa durability and retained-value refinements", "more explicit invalidation and lifecycle tradeoffs for Rust query engines"),
]


def load_sources() -> list[dict]:
    raw: dict[str, dict] = {}
    for path in sorted(COMPILER.glob("*/sources.jsonl"), key=lambda p: p.as_posix()):
        if path.parent == ROOT:
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            url = row.get("url")
            if not url:
                continue
            raw.setdefault(url, {
                "title": row.get("title", url),
                "publisher": row.get("publisher") or row.get("issuer") or "Named source owner",
                "source_kind": row.get("source_kind") or row.get("authority_class") or "official_documentation",
                "url": url,
            })
    for title, publisher, kind, url in EXTRA_SOURCES:
        raw[url] = {"title": title, "publisher": publisher, "source_kind": kind, "url": url}
    rows = []
    for url, item in sorted(raw.items()):
        digest = hashlib.sha256(url.encode()).hexdigest()[:16]
        kind = str(item["source_kind"])
        primary = any(token in kind for token in ("official", "spec", "standard", "research", "paper", "technical_report", "reference_checker", "book"))
        rows.append({
            "id": f"source.impl.{digest}", "record_kind": "source", "edition": EDITION,
            "status": "reviewed_candidate", "title": item["title"], "publisher": item["publisher"],
            "source_kind": kind, "primary_or_authoritative": primary, "url": url, "accessed_at": "2026-08-25",
            "supports": "Only the named specification, implementation mechanism or reported research result.",
            "does_not_support": "Completeness, provider qualification, implementation correctness or universal semantic ownership.",
        })
    return rows


def source_refs(sources: list[dict], index: int, count: int = 3) -> list[str]:
    return [sources[(index * count + offset) % len(sources)]["id"] for offset in range(count)]


def make_records(sources: list[dict]) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {k: [] for k in [
        "contexts", "capabilities", "operations", "decisions", "laws", "components", "ports",
        "persistence", "passes", "requirements", "offers", "libraries", "rust", "diagnostics",
        "performance", "threats", "innovations", "examples", "comparisons", "gaps",
        "apis", "tests",
    ]}
    for i, (slug, question, owns, excludes, input_kind, output_kind, invariant, family) in enumerate(CONTEXTS):
        cid = f"context.impl.{slug}"
        refs = source_refs(sources, i)
        out["contexts"].append({
            "id": cid, "record_kind": "bounded_context_candidate", "edition": EDITION, "status": STATUS,
            "question": question, "owns": owns, "explicitly_excludes": excludes, "input_contract": input_kind,
            "output_contract": output_kind, "constitutional_invariant": invariant, "family": family,
            "source_refs": refs,
        })
        for n, (verb, desc) in enumerate([
            ("validate", f"decide whether {input_kind} satisfies the closed {slug} contract"),
            ("explain", f"produce source-linked evidence and typed refusals for {slug} judgments"),
        ], 1):
            out["capabilities"].append({
                "id": f"capability.impl.{slug}.{verb}", "record_kind": "capability", "edition": EDITION,
                "status": STATUS, "context_ref": cid, "description": desc, "source_refs": refs[:2],
            })
            out["operations"].append({
                "id": f"operation.impl.{slug}.{verb}", "record_kind": "typed_operation", "edition": EDITION,
                "status": STATUS, "context_ref": cid, "verb": verb, "input": input_kind,
                "output": output_kind if verb == "validate" else "typed diagnostic graph",
                "failure": "typed refusal or unknown; never implicit fallback", "totality": "total over valid carrier; partial over unresolved meaning",
                "source_refs": refs[:2],
            })
        out["decisions"].append({
            "id": f"decision.impl.{slug}.policy", "record_kind": "decision_point", "edition": EDITION,
            "status": STATUS, "context_ref": cid, "question": question,
            "allowed_values": ["explicit_authority_value", "editioned_policy_default", "refuse_unresolved"],
            "default_law": "No operational default may invent semantic meaning.", "binding_phase": family,
            "authority_required": True, "source_refs": refs,
        })
        out["laws"].append({
            "id": f"law.impl.{slug}.constitution", "record_kind": "law", "edition": EDITION,
            "status": STATUS, "context_ref": cid, "statement": invariant,
            "checker_contract": f"checker.impl.{slug}", "on_unknown": "refuse_or_emit_typed_gap",
            "counterexample_required": True, "source_refs": refs,
        })
        component_id = f"component.impl.{slug}"
        out["components"].append({
            "id": component_id, "record_kind": "component_contract", "edition": EDITION, "status": STATUS,
            "context_ref": cid, "component_kind": "pure_kernel" if family not in {"storage", "runtime", "codegen", "build", "extension", "operations"} else "effect_adapter_or_orchestrator",
            "owns": owns, "forbids": [excludes, "ambient network", "ambient clock", "string-based semantic dispatch"],
            "transaction_boundary": "returns immutable result or typed failure; effects require separate intent/receipt",
            "source_refs": refs,
        })
        out["ports"].extend([
            {"id": f"port.impl.{slug}.input", "record_kind": "port_contract", "edition": EDITION, "status": STATUS,
             "component_ref": component_id, "direction": "input", "payload": input_kind,
             "protocol": "versioned typed value", "effects": [], "source_refs": refs[:1]},
            {"id": f"port.impl.{slug}.output", "record_kind": "port_contract", "edition": EDITION, "status": STATUS,
             "component_ref": component_id, "direction": "output", "payload": output_kind,
             "protocol": "Result<typed output, NonEmpty<Diagnostic>>", "effects": [], "source_refs": refs[:1]},
        ])
        out["passes"].append({
            "id": f"pass.impl.{slug}", "record_kind": "algorithm_pass_mapping", "edition": EDITION, "status": STATUS,
            "context_ref": cid, "algorithm_family": "stable traversal plus context-specific checker",
            "precondition": f"input conforms to prior stage before {slug}", "postcondition": invariant,
            "determinism_key": "input digest + pass implementation digest + decision-set digest + registry snapshot",
            "parallelism": "only disjoint subjects with canonical merge", "source_refs": refs,
        })
        if i < 48:
            rid = f"requirement.impl.{slug}"
            oid = f"offer.impl.{slug}.candidate"
            out["requirements"].append({
                "id": rid, "record_kind": "implementation_requirement", "edition": EDITION, "status": STATUS,
                "context_ref": cid, "hard": True, "requires": [invariant, "typed diagnostics", "deterministic iteration", "source/evidence retention"],
                "binding_phase": family, "source_refs": refs,
            })
            out["offers"].append({
                "id": oid, "record_kind": "implementation_offer_candidate", "edition": EDITION, "status": STATUS,
                "context_ref": cid, "claims": ["candidate interface shape only"], "exclusions": ["not qualified", "not bound", "no deployed occurrence"],
                "qualification_required": True, "satisfies_requirement_ref": rid, "binding_status": "unbound",
                "source_refs": refs,
            })

    for i, (name, kind, owns, rust_surface) in enumerate(LIBRARIES):
        out["libraries"].append({
            "id": f"library.impl.san-{name}", "record_kind": "library_boundary", "edition": EDITION,
            "status": STATUS, "name": f"san-{name}", "library_kind": kind, "owns": owns,
            "rust_surface": rust_surface, "forbidden": ["application UI", "ambient configuration", "provider-name dispatch", "hidden defaults"],
            "replacement_seam": "editioned trait or pure function plus shared conformance suite",
            "source_refs": source_refs(sources, i, 4),
        })
        out["rust"].append({
            "id": f"rust.impl.san-{name}", "record_kind": "rust_applicability", "edition": EDITION, "status": STATUS,
            "library_ref": f"library.impl.san-{name}", "applicable_features": [
                "newtypes for semantic identity", "non_exhaustive enums at open integration boundaries",
                "sealed traits for constitutional semantics", "Result with typed non-empty diagnostics",
                "typestate only where transition proof is local", "BTreeMap/BTreeSet for canonical iteration",
            ],
            "limits": ["Rust cannot prove external evidence true", "types cannot decide authority", "traits do not prove conformance"],
            "candidate_crates_are_mechanisms_not_selections": ["serde", "salsa", "rowan", "petgraph", "slotmap", "tower", "tokio-util", "wasmtime"],
            "source_refs": source_refs(sources, i + 40, 4),
        })

    for i, (name, fields, key) in enumerate(PERSISTENCE):
        out["persistence"].append({
            "id": f"schema.impl.{name}", "record_kind": "persistence_schema_candidate", "edition": EDITION,
            "status": STATUS, "logical_relation": name, "fields": [x.strip() for x in fields.split(",")],
            "candidate_primary_key": key, "temporal_policy": "immutable rows or explicit valid/record time; no in-place semantic history erasure",
            "index_policy": "derive indexes from canonical facts; indexes are rebuildable",
            "storage_non_selection": "Relational/embedded KV implementations require benchmark and failure qualification; this record selects none.",
            "source_refs": source_refs(sources, i + 80, 3),
        })

    for i, code in enumerate(DIAGNOSTIC_CODES):
        out["diagnostics"].append({
            "id": f"diagnostic.impl.{code}", "record_kind": "diagnostic_contract", "edition": EDITION, "status": STATUS,
            "stable_code": f"SAN-IMPL-{i+1:04d}", "category": code.split("_")[0], "severity": "error",
            "payload_required": ["subject_id", "source_anchors", "phase", "cause_ids", "support_set", "machine_remediation_options"],
            "human_rendering_is_contract": False, "exit_class": "refused_or_incomplete",
            "source_refs": source_refs(sources, i + 120, 2),
        })

    perf_names = [
        "source_bytes", "syntax_nodes", "graph_nodes", "graph_claims", "graph_roles", "snapshot_bytes", "index_bytes",
        "parse_time", "resolve_time", "typecheck_time", "lawcheck_time", "candidate_edges", "constraint_atoms", "constraint_clauses",
        "solver_time", "solver_memory", "proof_bytes", "unsat_core_size", "pass_count", "pass_work_units", "cache_hit_ratio",
        "dirty_query_count", "recomputed_query_count", "peak_memory", "artifact_bytes", "evidence_bytes", "plugin_fuel",
        "plugin_memory", "cancel_latency", "diagnostic_count", "network_bytes", "operator_review_items",
    ]
    for i, name in enumerate(perf_names):
        out["performance"].append({
            "id": f"resource.impl.{name}", "record_kind": "performance_resource_dimension", "edition": EDITION, "status": STATUS,
            "dimension": name, "measure_kind": "count_or_duration_or_bytes_as_named", "hard_budget_capable": True,
            "estimate_reserve_observe_distinct": True, "cardinality_key": "compilation_run_id+phase+subject_kind",
            "failure_semantics": "budget exhaustion returns cancelled/unknown with partial receipts",
            "source_refs": source_refs(sources, i + 180, 2),
        })

    threat_names = [
        "semantic_confusion", "homonym_alias_injection", "edition_downgrade", "mutable_import", "registry_poisoning",
        "review_authority_spoof", "digest_confusion", "canonicalization_collision", "parser_resource_exhaustion", "schema_bomb",
        "graph_cardinality_explosion", "index_corruption", "transaction_torn_write", "cache_poisoning", "support_set_omission",
        "solver_model_spoof", "solver_timeout_dos", "unsat_core_misrepresentation", "proof_checker_bug", "plugin_escape",
        "plugin_capability_escalation", "secret_exfiltration", "cross_tenant_leak", "artifact_substitution", "attestation_subject_mismatch",
        "provider_occurrence_drift", "budget_bypass", "cancellation_cleanup_failure", "diagnostic_data_leak", "agent_prompt_injection",
        "agent_tool_confused_deputy", "migration_history_erasure", "replay_external_effect", "telemetry_semantic_interference",
    ]
    for i, name in enumerate(threat_names):
        out["threats"].append({
            "id": f"threat.impl.{name}", "record_kind": "threat_model_entry", "edition": EDITION, "status": STATUS,
            "threat": name, "assets": ["semantic integrity", "authority integrity", "evidence integrity", "availability"],
            "trust_boundary": "untrusted authored/imported/provider/plugin/model input -> deterministic core",
            "required_controls": ["exact identities", "finite budgets", "typed validation", "least capability", "immutable receipt", "fail closed"],
            "residual_risk": "checker defect or incomplete external evidence requires independent review and conformance",
            "source_refs": source_refs(sources, i + 220, 3),
        })

    for i, (year, name, relevance) in enumerate(INNOVATIONS):
        out["innovations"].append({
            "id": f"innovation.impl.{i+1:02d}", "record_kind": "innovation_2021_2026", "edition": EDITION,
            "status": "researched_candidate", "year": year, "name": name, "relevance": relevance,
            "non_llm_core": True, "adoption_non_claim": "Candidate design input; not selected or independently qualified.",
            "source_refs": source_refs(sources, i + 260, 3),
        })

    comparisons = [
        ("rustc_query", "fine-grained red/green query dependency graph", "not a persistent enterprise semantic store"),
        ("salsa", "Rust incremental tracked/input/interned identities", "current lifecycle and persistence constraints need qualification"),
        ("buck2_dice", "async demand-driven computations and equality resurrection", "build-oriented semantics are not domain authority"),
        ("bazel_skyframe", "hermetic action graph and incremental evaluation", "action keys do not prove semantic equivalence"),
        ("nix", "content/derivation-addressed reproducible build model", "external runtime and semantic claims remain separate"),
        ("mlir", "dialects, stage legality, pass isolation and progressive lowering", "compiler IR framework is not the enterprise domain ontology"),
        ("llvm", "target lowering, data layout and verifier contracts", "too low-level for authored analytical meaning"),
        ("calcite", "relational algebra, traits and planner rules", "relational plans cover only part of SAN's hypergraph and authority model"),
        ("datafusion", "Rust logical/physical planner and execution extension seams", "query execution is one backend family, not the compiler core"),
        ("substrait", "portable typed compute-plan exchange", "extensions and semantics need exact edition qualification"),
        ("sqlite", "transactional embedded relational persistence", "one writer/storage profile may not meet all corpus scales"),
        ("redb", "embedded transactional Rust key-value storage", "indexes and durability behavior require exact workload qualification"),
        ("petgraph", "in-memory graph algorithms", "not a durable typed hypergraph or MVCC store"),
        ("rdf_sparql", "open graph semantics and query interoperability", "open-world/RDF identity rules cannot be silently imposed on closed compiler judgments"),
        ("z3_cvc5", "SMT theories, models and proof capabilities", "solver success must be independently checked and UNKNOWN retained"),
        ("ortools_minizinc", "CP/optimization modeling and finite-domain search", "optimization preference cannot replace hard semantic feasibility"),
        ("wasmtime_component", "typed, capability-limited portable extension runtime", "sandbox does not establish plugin semantic correctness"),
        ("serde", "broad Rust data-model translation", "generic serialization is not canonical serialization"),
    ]
    for i, (system, learns, nonclaim) in enumerate(comparisons):
        out["comparisons"].append({
            "id": f"comparison.impl.{system}", "record_kind": "system_comparison", "edition": EDITION,
            "status": STATUS, "system": system, "applicable_mechanism": learns, "must_not_infer": nonclaim,
            "selection_criteria": ["semantic fit", "failure semantics", "determinism", "evidence", "resource envelope", "replacement seam"],
            "source_refs": source_refs(sources, i + 300, 4),
        })

    out["examples"] = make_examples(sources)
    api_specs = [
        ("cli.compile", "cli", "compile --intent <path> --snapshot <digest> --output <dir>", "CompilationOutcome", "never performs deployment effects"),
        ("cli.check", "cli", "check --intent <path> --through <stage>", "CheckOutcome", "stops at requested pure stage"),
        ("cli.explain", "cli", "explain --diagnostic <id> --format json|text", "DiagnosticGraph", "text is a rendering of typed payload"),
        ("cli.diff", "cli", "diff --old <snapshot> --new <snapshot>", "SemanticDiff", "does not infer migration safety"),
        ("cli.replay", "cli", "replay --run <manifest-digest>", "ReplayComparison", "external effects disabled"),
        ("cli.snapshot", "cli", "snapshot lock --roots <manifest>", "LockedSnapshot", "rejects mutable/floating references"),
        ("cli.adjudication-export", "cli", "review export --batch <id>", "ReviewBatch", "exports uncertainty, never resolves it"),
        ("cli.adjudication-import", "cli", "review import --decision <path>", "ReviewImportReceipt", "requires scoped authority signature"),
        ("cli.qualify", "cli", "qualify --profile <id> --artifact <digest> --target <occurrence>", "QualificationReceipt", "runs named suite; docs are insufficient"),
        ("cli.query", "cli", "query --snapshot <digest> --query <typed-query>", "QueryResult", "closed typed query only"),
        ("library.compiler", "rust_library", "Compiler::compile(CompilationRequest, &dyn EffectPorts)", "CompilationOutcome", "no global mutable state"),
        ("library.frontend", "rust_library", "FrontEnd::parse(SourceSnapshot, LanguageEdition)", "Result<DeclarationAst<Unresolved>, Diagnostics>", "preserves recovery nodes"),
        ("library.resolver", "rust_library", "Resolver::resolve(Ast, LockedSnapshot)", "Result<Ir<Resolved>, Diagnostics>", "no network discovery"),
        ("library.checker", "rust_library", "Checker::check(Ir<Resolved>, LawSet)", "CheckOutcome<Ir<Checked>>", "unknown retained"),
        ("library.lower", "rust_library", "PassEngine::run(Ir<S>, PassSchedule<S,T>)", "PassOutcome<Ir<T>>", "transactional pass result"),
        ("library.bind", "rust_library", "Binder::bind(RequirementGraph, OfferSnapshot, BindBudget)", "BindingOutcome", "offers remain untrusted until checked"),
        ("library.store", "rust_library", "GraphStore::commit(ExpectedSnapshot, GraphPatch)", "Result<CommitReceipt, Conflict>", "atomic publication"),
        ("library.evidence", "rust_library", "EvidenceStore::put(EvidenceObservation)", "PutReceipt", "immutable and scope-preserving"),
        ("library.backend", "rust_library", "Backend::emit(Ir<BackendBound>, TargetContract)", "ArtifactPlan", "cannot alter semantic decisions"),
        ("library.cancel", "rust_library", "Compiler::compile_with_budget(Request, Cancellation, ResourceBudget)", "CompilationOutcome", "cancelled outcome is distinct"),
    ]
    for i, (name, surface, signature, result, nonclaim) in enumerate(api_specs):
        out["apis"].append({
            "id": f"api.impl.{name}", "record_kind": "api_contract", "edition": EDITION, "status": STATUS,
            "surface": surface, "signature": signature, "result_contract": result,
            "determinism": "same exact request, snapshot and implementation closure yields byte-identical canonical outcome",
            "nonclaim": nonclaim, "source_refs": source_refs(sources, i + 380, 3),
        })
    test_specs = [
        ("parser_golden", "golden", "CST and diagnostics are byte-stable"),
        ("parser_fuzz", "fuzz", "all bytes terminate within finite budget without panic"),
        ("unknown_symbol_negative", "exact_boundary", "unknown names never resolve by similarity"),
        ("identity_newtype_compile_fail", "compile_fail", "semantic ID cannot substitute for occurrence or digest"),
        ("canonical_encoding_property", "property", "equal semantic record produces one byte encoding"),
        ("digest_domain_separation", "property", "different artifact domains cannot collide by omitted prefix"),
        ("graph_transaction_crash", "fault_injection", "published snapshot is old or new, never torn"),
        ("index_rebuild", "differential", "recomputed indexes answer identically to retained indexes"),
        ("type_checker_negative", "negative_twin", "invalid kind/cardinality/unit examples are refused"),
        ("law_unknown", "exact_boundary", "missing checker yields unknown, not proved"),
        ("pass_determinism", "property", "pass output independent of hash-map and thread schedule"),
        ("rewrite_equivalence", "model", "bounded counterexamples detect unsound rewrite candidates"),
        ("solver_model_check", "differential", "every SAT model is checked independently"),
        ("unsat_proof_check", "proof", "UNSAT promotion requires checked proof or scoped trusted checker"),
        ("solver_timeout", "fault_injection", "timeout returns unknown and partial evidence"),
        ("objective_separation", "property", "preferences cannot alter feasible set"),
        ("qualification_scope", "exact_boundary", "artifact/target/config mismatch invalidates receipt"),
        ("cache_key_mutation", "mutation", "omitting any declared input causes a failing test"),
        ("incremental_clean_equivalence", "differential", "incremental output equals clean output"),
        ("parallel_schedule", "loom_or_model", "allowed interleavings preserve canonical result"),
        ("cancellation_cleanup", "fault_injection", "leases/temp artifacts are released and partial receipt emitted"),
        ("plugin_escape", "adversarial", "filesystem/network/clock access denied absent capability"),
        ("agent_proposal_injection", "adversarial", "proposal cannot bypass parser, resolver, law or authority"),
        ("vertical_negative_twins", "conformance", "energy and SA-CCR forbidden inferences stop at exact stage"),
        ("two_implementation_differential", "independent", "two implementations agree on canonical outcomes and diagnostics"),
    ]
    for i, (name, method, oracle) in enumerate(test_specs):
        out["tests"].append({
            "id": f"test.impl.{name}", "record_kind": "conformance_test_contract", "edition": EDITION, "status": STATUS,
            "method": method, "oracle": oracle, "required_evidence": ["exact test-domain digest", "implementation digest", "raw observations", "limitations"],
            "production_nonclaim": "Passing this scoped test does not qualify every workload or deployment.",
            "source_refs": source_refs(sources, i + 410, 3),
        })
    gap_names = [
        "normative grammar not adjudicated", "canonical registries incomplete", "hypergraph scale profile absent",
        "persistent store not qualified", "checker implementations absent", "solver/checker diversity absent",
        "provider occurrences incomplete", "target qualification receipts absent", "backend implementations absent",
        "migration upcasters unimplemented", "extension ABI not frozen", "security review absent", "resource benchmarks absent",
        "incremental clean-build equivalence untested", "two independent implementations absent", "cross-version replay untested",
        "authority key and revocation operations unspecified", "tenant isolation not implemented", "artifact retention policy unadjudicated",
        "production operations and recovery drills absent", "full compiler remains unimplemented",
    ]
    for i, gap in enumerate(gap_names):
        out["gaps"].append({
            "id": f"gap.impl.{i+1:03d}", "record_kind": "blocking_gap", "edition": EDITION,
            "status": "open", "description": gap, "compiler_behavior": "fail_closed_or_stop_before_affected_stage",
            "owner_needed": "named domain authority plus implementation and independent reviewer",
            "evidence_needed": "exact artifact, scoped conformance receipt and negative tests",
        })
    return out


def make_examples(sources: list[dict]) -> list[dict]:
    common = {
        "edition": EDITION, "record_kind": "prototype_trace", "status": STATUS,
        "core_is_deterministic": True, "optional_agent_role": "an agent may propose mappings only; deterministic validation and authority remain mandatory",
    }
    traces = [
        {
            **common, "id": "example.impl.energy-grid-positive", "vertical": "electric_power_operations",
            "intent": "Produce a day-ahead probabilistic net-load plan with explicit timezone, units, forecast horizon, reliability quantiles and resource budget.",
            "stages": ["parse declaration", "lock exact imports", "resolve canonical source/type/method IDs", "type and law check units/time/uncertainty", "lower case to forecast and scenario requirements", "enumerate offers", "solve hard compatibility", "require target qualification", "emit physical-plan gap until evidence exists"],
            "expected": "partially_bound_with_typed_qualification_gap", "source_refs": source_refs(sources, 340, 5),
        },
        {
            **common, "id": "example.impl.energy-grid-negative-twin", "vertical": "electric_power_operations",
            "intent": "Infer timezone and MW/MWh semantics from column names and choose the cheapest forecast service.",
            "stages": ["parse declaration", "resolution detects absent authority for timezone and units", "emit type/time diagnostics", "stop before candidate ranking"],
            "expected": "refused_before_binding", "forbidden_inference": "field names cannot establish timezone, unit, validity or aggregation semantics", "source_refs": source_refs(sources, 345, 5),
        },
        {
            **common, "id": "example.impl.bank-sacc-r-positive", "vertical": "banking_counterparty_credit_risk",
            "intent": "Compile an edition-locked SA-CCR exposure calculation with legal-entity, netting-set, collateral, trade-state, supervisory-factor and reporting-time authority.",
            "stages": ["parse declaration", "lock regulation and registry editions", "resolve legal entity and netting-set identities", "check eligibility and aggregation laws", "lower method to formula/algorithm/kernel requirements", "enumerate offers", "solve feasibility", "stop at unqualified target occurrence"],
            "expected": "partially_bound_with_typed_qualification_gap", "source_refs": source_refs(sources, 350, 5),
        },
        {
            **common, "id": "example.impl.bank-sacc-r-negative-twin", "vertical": "banking_counterparty_credit_risk",
            "intent": "Treat counterparty display name as legal entity and group all trades with the same name into one netting set.",
            "stages": ["parse declaration", "canonical reference mapping remains unreviewed", "identity and authority checks fail", "stop before method lowering"],
            "expected": "refused_before_semantic_lowering", "forbidden_inference": "display-name equality is not legal-entity or netting-set identity", "source_refs": source_refs(sources, 355, 5),
        },
    ]
    return traces


def build() -> None:
    sources = load_sources()
    records = make_records(sources)
    file_map = {
        "contexts": "contexts.jsonl", "capabilities": "capabilities.jsonl", "operations": "operations.jsonl",
        "decisions": "decision-points.jsonl", "laws": "laws.jsonl", "components": "components.jsonl",
        "ports": "ports.jsonl", "persistence": "persistence-schema-candidates.jsonl",
        "passes": "algorithm-pass-mappings.jsonl", "requirements": "requirements.jsonl", "offers": "offers.jsonl",
        "libraries": "library-boundaries.jsonl", "rust": "rust-applicability.jsonl", "diagnostics": "diagnostics.jsonl",
        "performance": "performance-resource-model.jsonl", "threats": "threat-model.jsonl",
        "innovations": "innovations-2021-2026.jsonl", "examples": "prototype-traces.jsonl",
        "comparisons": "system-comparisons.jsonl", "gaps": "gaps.jsonl",
        "apis": "api-contracts.jsonl", "tests": "conformance-tests.jsonl",
    }
    write_jsonl(ROOT / "sources.jsonl", sources)
    for key, filename in file_map.items():
        write_jsonl(ROOT / filename, records[key])

    metamodel = {
        "id": "metamodel.compiler.implementation_architecture", "edition": EDITION,
        "status": STATUS, "completion_claim": False,
        "pipeline": [
            "parse", "lock_imports", "resolve_exact_identity", "adjudicate_canonical_references",
            "type_and_law_check", "lower_semantics", "enumerate_candidates", "prove_subsumption",
            "solve_hard_constraints", "select_authorized_objective", "qualify_occurrence", "admit_resources",
            "plan_codegen", "build", "emit_evidence", "observe_and_invalidate",
        ],
        "result_sum_type": ["complete", "partial_with_gaps", "unsat_with_checked_core", "unknown", "refused", "cancelled"],
        "constitutional_laws": [
            "unknown meaning fails closed", "no string-based semantic dispatch", "stable identity != edition != occurrence != digest",
            "parse != resolve != adjudicate", "type checking != law proof", "structural match != semantic satisfaction",
            "feasible != preferred != qualified != admitted", "plan != effect authority", "cache hit != proof",
            "incremental result == clean result for identical snapshots", "model or agent output is an untrusted proposal",
        ],
        "persistence_candidate": "append-only canonical fact and receipt log plus transactional snapshot manifest and rebuildable relational/adjacency indexes",
        "hypergraph_rule": "Represent every n-ary semantic relation as a typed claim node with role bindings; do not encode role meaning in untyped edge strings.",
    }
    write_json(ROOT / "architecture-metamodel.json", metamodel)

    generated = ["sources.jsonl", *file_map.values(), "architecture-metamodel.json"]
    digests = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in sorted(generated)}
    principal = sum(len(records[k]) for k in ["capabilities", "operations", "decisions", "laws"])
    primary_sources = sum(1 for row in sources if row["primary_or_authoritative"])
    manifest = {
        "id": "manifest.compiler.implementation_architecture", "edition": EDITION, "status": STATUS,
        "completion_claim": False, "counts": {"sources": len(sources), "primary_or_authoritative_sources": primary_sources,
                                                 **{key: len(value) for key, value in records.items()},
                                                 "principal_capability_operation_decision_law": principal},
        "thresholds": {"sources": 100, "contexts": 60, "principal_records": 300, "libraries": 40, "innovations": 30},
        "generated_file_sha256": digests,
        "generator_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    write_json(ROOT / "manifest.json", manifest)


if __name__ == "__main__":
    build()
