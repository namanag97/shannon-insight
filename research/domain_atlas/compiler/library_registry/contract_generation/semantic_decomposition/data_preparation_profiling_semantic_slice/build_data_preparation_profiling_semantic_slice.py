#!/usr/bin/env python3
"""Build the evidence-backed data-preparation and profiling semantic slice."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
SEM = HERE.parent
AS_OF = "2026-08-27"
PRODUCTS = {"product.self_service_data_preparation"}
AXES = [
    "semantic_object", "semantic_role", "identity_and_equality", "grain_and_cardinality",
    "state_and_change", "time", "order_and_topology", "partiality_and_uncertainty",
    "authority_and_trust", "effect_boundary", "representation", "composition_algebra",
    "compatibility_and_evolution", "resources_and_failure", "evidence_and_conformance",
    "privacy_security_safety",
]

NEIGHBORS = {
    "library.csp.identity.canonicalization", "library.csp.identity.identifier-parser",
    "library.csp.quantity.partial-information", "library.data_contract.data_schema_binding",
    "library.data_contract.quality_service_obligations", "library.gmo.privacy_purpose_binding",
    "library.gmo.quality_core", "library.lineage_repository.port", "library.lpe.field-lineage",
    "library.lpe.formula-provenance", "library.lpe.lineage-core", "library.lpe.provenance-bundle",
    "library.method_kernels.data_quality_methods", "library.method_kernels.formula_algebra",
    "library.persistence.logical_types", "library.persistence.materialization",
    "library.persistence.schema_evolution", "library.persistence.table_identity",
    "library.qck.codec-kernels", "library.qck.expression-kernels", "library.qck.query-binding",
    "library.qck.query-equivalence-oracles", "library.qck.query-receipts",
    "library.qck.relational-kernels", "library.qck.relational-semantics",
    "library.qor.schema_conformance_kernel", "library.san_codec_kernel", "library.san_format_probe",
    "library.schema_mapping.compiler", "library.schema_mapping.executor",
    "library.schema_registry.artifact_profile", "library.schema_registry.subject_identity",
    "library.smf.formula_parser", "library.smf.semantic_type_checker",
    "library.spt.privacy_vocabulary", "library.transform_definition.compiler",
}

VACANCIES = [
    ("library.preparation.data_cut_admission", "Source occurrence, object/version cuts, schema/representation, policy, sample and reproducibility evidence need one admission result."),
    ("library.preparation.dialect_parse_plan", "Encoding, delimiter, quote, escape, header, locale, number/time and malformed-record policy require an editioned parse plan."),
    ("library.preparation.total_parse_result", "Parsed values, rejects, truncation, repairs, byte/row positions and residual bytes need a total result."),
    ("library.preparation.schema_hypothesis", "Inferred names, logical/physical types, null tokens, confidence, sample and counterexamples must remain hypotheses until accepted."),
    ("library.preparation.missingness_algebra", "Missing, absent field, empty, null token, invalid, redacted, not-applicable and unknown need distinct states."),
    ("library.preparation.occurrence_identity_map", "Row/record/field/cell identity through filter, sort, split, pivot, join, aggregate and explode needs a lineage map."),
    ("library.preparation.profile_request", "Exact/approximate measures, subject grain, population/sample, tolerances, budgets and privacy constraints need a request contract."),
    ("library.preparation.profile_result", "Counts, distributions, patterns, keys, dependencies, inclusion claims, uncertainty, algorithms and cuts need a typed result."),
    ("library.preparation.selection_view", "Facet/filter/sort/group state is a non-mutating view until explicitly captured by an operation."),
    ("library.preparation.operation_algebra", "Every transformation needs typed input/output, grain/cardinality, order, partiality, loss, determinism and failure semantics."),
    ("library.preparation.reshape_grain_map", "Pivot/unpivot/melt/spread/explode/nest operations need keys, value identity, collision and invertibility semantics."),
    ("library.preparation.join_cardinality_contract", "Keys, equality/null semantics, expected cardinality, fanout, unmatched rows, temporal scope and join loss need preflight."),
    ("library.preparation.expression_binding", "Expression AST, names, types, null/error propagation, functions, locale/time and determinism require an exact binding."),
    ("library.preparation.repair_proposal", "Observed anomaly, proposed value/operation, evidence, confidence, scope and accept/reject authority must remain distinct."),
    ("library.preparation.preview_contract", "Preview sample, ordering, truncation, approximation, stale state and full-run equivalence claims need explicit bounds."),
    ("library.preparation.recipe_edition", "Ordered operation graph, parameters, dependencies, provider-neutral semantics, input/output contracts and digest need an edition."),
    ("library.preparation.history_branch", "Undo/redo cursor, abandoned branches, inverse/replay/compensation semantics and authorship need durable history."),
    ("library.preparation.replay_compatibility", "Input drift, operation/provider versions, nondeterminism, external lookups and partial-result policy need a replay verdict."),
    ("library.preparation.data_diff", "Row/column/value identity, ordering, tolerance, unmatched/uncomparable states and information loss need one diff algebra."),
    ("library.preparation.prepared_output_edition", "Exact input, recipe, execution, diff, schema, lineage, quality disclosures, encoding and policy need an immutable output edition."),
    ("library.preparation.sensitive_value_view", "Profiling, preview, expressions, logs and exports need purpose-scoped masking/minimization and disclosure controls."),
]


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def declared_product_libraries() -> set[str]:
    rows = load_jsonl(SEM / "product_coordinate_binding_projection/subject-coordinate-binding-projections.jsonl")
    return {edge["concrete_library_ref"] for row in rows if row["product_ref"] in PRODUCTS for edge in row["concrete_bindings"]}


LIBRARIES = sorted(declared_product_libraries() | NEIGHBORS)


SOURCE_ROWS = [
    ("codd", "A Relational Model of Data for Large Shared Data Banks", "E. F. Codd", 1970, "primary_paper", "https://doi.org/10.1145/362384.362685", "Defines relations, tuples, attributes and data independence foundations.", "Relational algebra does not define interactive recipe lifecycle, carrier parsing or domain meaning."),
    ("rfc4180", "Common Format and MIME Type for CSV Files", "IETF", 2005, "internet_standard", "https://www.rfc-editor.org/rfc/rfc4180", "Registers text/csv and documents common delimiter, quoting and line conventions.", "CSV practice exceeds the memo and files are not self-describing or semantically typed."),
    ("rfc7111", "URI Fragment Identifiers for the text/csv Media Type", "IETF", 2014, "internet_standard", "https://www.rfc-editor.org/rfc/rfc7111", "Defines row, column and cell fragment selectors for CSV resources.", "Positional fragments are not stable occurrence identity across transformations or revisions."),
    ("csvw-model", "Model for Tabular Data and Metadata on the Web", "W3C", 2015, "web_standard", "https://www.w3.org/TR/tabular-data-model/", "Defines table groups, tables, rows, columns, cells, dialects, schemas and annotations.", "CSVW metadata does not make inferred schemas authoritative or transformations lossless."),
    ("csvw-metadata", "Metadata Vocabulary for Tabular Data", "W3C", 2015, "web_standard", "https://www.w3.org/TR/tabular-metadata/", "Defines machine-readable dialect, schema, datatype, key and foreign-key metadata.", "Metadata conformance is not data correctness or fitness for use."),
    ("csvw-validation", "Generating JSON from Tabular Data", "W3C", 2015, "web_standard", "https://www.w3.org/TR/csv2json/", "Defines deterministic transformations from annotated tables to JSON.", "One representation mapping does not preserve all source lexical or layout information."),
    ("json-schema", "JSON Schema Validation Draft 2020-12", "JSON Schema", 2022, "official_specification", "https://json-schema.org/draft/2020-12/json-schema-validation", "Defines assertion and annotation vocabularies for JSON instances.", "Validation success is scoped to a schema and is not source truth or repair authority."),
    ("frictionless-table", "Frictionless Table Schema", "Frictionless Data", 2025, "community_specification", "https://specs.frictionlessdata.io/table-schema/", "Defines fields, types, constraints, missing values, keys and foreign keys for tabular resources.", "Community schema metadata does not resolve every dialect, locale or semantic type."),
    ("arrow-format", "Apache Arrow Columnar Format", "Apache Arrow", 2026, "official_specification", "https://arrow.apache.org/docs/format/Columnar.html", "Defines arrays, schemas, record batches, nested types and validity bitmaps.", "Physical null layout and logical types do not define business missingness or row identity."),
    ("arrow-stats", "Apache Arrow Statistics Schema", "Apache Arrow", 2026, "official_specification", "https://arrow.apache.org/docs/format/StatisticsSchema.html", "Defines exact/approximate statistics attached to batches and fields.", "Physical statistics lack population, algorithm, privacy and fitness interpretation by themselves."),
    ("arrow-opaque", "Apache Arrow Canonical Opaque Extension Type", "Apache Arrow", 2026, "official_specification", "https://arrow.apache.org/docs/format/CanonicalExtensions.html", "Preserves unsupported external type identity without inventing false semantic interoperability.", "Opaque transport intentionally does not make values operable or semantically understood."),
    ("prov-o", "PROV-O", "W3C", 2013, "web_standard", "https://www.w3.org/TR/prov-o/", "Defines entities, activities, agents, derivation and attribution.", "Provenance can describe a recipe run but does not prove replay equivalence or correctness."),
    ("potters-wheel", "Potter's Wheel: An Interactive Data Cleaning System", "Raman and Hellerstein", 2001, "primary_paper", "https://www.vldb.org/conf/2001/P381.pdf", "Integrates interactive transformation, discrepancy detection, sampling and undo.", "Immediate sample feedback is not proof of full-data behavior or quality acceptance."),
    ("wrangler", "Wrangler: Interactive Visual Specification of Data Transformation Scripts", "Kandel et al.", 2011, "primary_paper", "https://doi.org/10.1145/1978942.1979444", "Combines direct manipulation, transform suggestions, preview and auditable histories.", "Suggested transforms and previews are proposals, not accepted semantics or full-run evidence."),
    ("tidy-data", "Tidy Data", "Hadley Wickham", 2014, "primary_paper", "https://doi.org/10.18637/jss.v059.i10", "Defines variables-as-columns, observations-as-rows and observational units as tables.", "Tidy organization is a useful profile, not universal truth for graphs, arrays, documents or events."),
    ("dplyr", "A Grammar of Data Manipulation", "dplyr contributors", 2026, "official_implementation_documentation", "https://dplyr.tidyverse.org/", "Documents composable select, filter, mutate, summarize, arrange, group and join verbs.", "Package behavior is implementation evidence and backend translations may differ."),
    ("openrefine", "OpenRefine User Manual", "OpenRefine", 2026, "official_implementation_documentation", "https://openrefine.org/docs.html", "Documents projects, facets, transformations, clustering, reconciliation and export.", "Product behavior is not a portable recipe or semantic authority."),
    ("openrefine-history", "OpenRefine History and Reusing Operations", "OpenRefine", 2026, "official_implementation_documentation", "https://openrefine.org/docs/manual/running/#history-undo-redo", "Documents durable ordered undo/redo and JSON operation extraction/application.", "Not every operation is extractable; undo history is not necessarily an algebraic inverse."),
    ("openrefine-facets", "OpenRefine Facets", "OpenRefine", 2026, "official_implementation_documentation", "https://openrefine.org/docs/manual/facets", "Distinguishes interactive facet/filter view state from operations and export selection.", "Some operations ignore facets, so visible selection does not imply transform scope."),
    ("openrefine-transform", "OpenRefine Transforming Data", "OpenRefine", 2026, "official_implementation_documentation", "https://openrefine.org/docs/manual/transforming/", "Documents row/column reordering, split/join, transpose, derived columns and clustering.", "Transformation availability does not supply type, loss, grain or authority semantics."),
    ("profiling-survey", "Profiling Relational Data: A Survey", "Abedjan, Golab and Naumann", 2015, "peer_reviewed_survey", "https://doi.org/10.1007/s00778-015-0389-y", "Classifies basic statistics, patterns, keys, dependencies and inclusion-dependency profiling.", "The survey focuses exact relational profiling and does not authorize inferred metadata."),
    ("metanome", "Data Profiling with Metanome", "Papenbrock et al.", 2015, "primary_system_paper", "https://www.vldb.org/pvldb/vol8/p1860-papenbrock.pdf", "Modularizes profiling algorithms, inputs, execution and result handling.", "Algorithm output depends on input cut, semantics and resource limits and remains a hypothesis."),
    ("tane", "TANE: An Efficient Algorithm for Discovering Functional and Approximate Dependencies", "Huhtala et al.", 1999, "primary_paper", "https://doi.org/10.1093/comjnl/42.2.100", "Discovers functional dependencies and approximate variants through a level-wise search.", "Observed dependency is not declared business law and may be accidental or time-limited."),
    ("hll", "HyperLogLog: The Analysis of a Near-Optimal Cardinality Estimation Algorithm", "Flajolet et al.", 2007, "primary_paper", "https://doi.org/10.46298/dmtcs.3545", "Defines a bounded-memory approximate distinct-count estimator.", "An estimate requires precision/error parameters and is not an exact profile value."),
    ("tdigest", "Computing Extremely Accurate Quantiles Using t-Digests", "Ted Dunning and Otmar Ertl", 2019, "primary_method_paper", "https://arxiv.org/abs/1902.04023", "Defines a mergeable sketch for approximate quantiles and tails.", "Approximation and merge order must be disclosed; a sketch is not the population distribution."),
    ("nadeef", "NADEEF: A Generalized Data Cleaning System", "Ebaid et al.", 2013, "primary_system_paper", "https://www.vldb.org/pvldb/vol6/p1218-tang.pdf", "Separates heterogeneous quality-rule interfaces, violation detection, repair and metadata.", "Detection and repair rules remain application-specific and repair is not source authority."),
    ("holoclean", "HoloClean: Holistic Data Repairs with Probabilistic Inference", "Rekatsinas et al.", 2017, "primary_paper", "https://doi.org/10.14778/3137628.3137631", "Combines constraints, external data and statistical signals into probabilistic repair candidates.", "Most-probable repair is model-dependent and not accepted truth or mutation authority."),
    ("raha", "Raha: A Configuration-Free Error Detection System", "Mahdavi et al.", 2019, "primary_paper", "https://doi.org/10.1145/3299869.3324956", "Combines detector configurations with representative labeling and learned error classification.", "Configuration-free does not mean assumption-free, authoritative or universally accurate."),
    ("data-civilizer", "The Data Civilizer System", "Deng et al.", 2017, "primary_system_paper", "https://people.csail.mit.edu/dongdeng/papers/cidr2017-civilizer.pdf", "Integrates discovery, profiling, join-path search and cleaning in data lakes.", "Discovered paths and cleaning suggestions are candidates and do not establish join fitness."),
    ("flashfill", "Automating String Processing in Spreadsheets Using Input-Output Examples", "Sumit Gulwani", 2011, "primary_paper", "https://doi.org/10.1145/1926385.1926423", "Synthesizes string transformations from examples.", "A program consistent with examples may fail elsewhere and remains a proposal until validated."),
    ("duckdb-sniffer", "DuckDB CSV Sniffer", "DuckDB", 2023, "official_technical_documentation", "https://duckdb.org/2023/10/27/csv-sniffer", "Uses multi-hypothesis sampling to infer dialect, header, types and malformed-row handling.", "Sampling can miss later counterexamples; best-effort parsing is not declared schema."),
    ("duckdb-csv", "DuckDB CSV Auto Detection", "DuckDB", 2026, "official_implementation_documentation", "https://duckdb.org/docs/current/data/csv/auto_detection", "Exposes dialect/type/header inference, sample size and user overrides.", "Implementation defaults and overrides are not portable unless captured in the recipe."),
    ("great-expectations", "Expectation Concepts", "Great Expectations", 2026, "official_product_documentation", "https://docs.greatexpectations.io/docs/core/introduction/", "Documents declarative expectations, validation definitions, checkpoints and results.", "Product expectations are market evidence; quality acceptance remains outside preparation authority."),
    ("iso8000-61", "ISO 8000-61:2016 Data Quality Management Process Reference Model", "ISO", 2016, "international_standard", "https://www.iso.org/standard/63086.html", "Defines process reference concepts for data-quality management.", "Quality management is broader than interactive preparation and does not prescribe transformations."),
    ("iso25012", "ISO/IEC 25012 Data Quality Model", "ISO/IEC", 2008, "international_standard", "https://www.iso.org/standard/35736.html", "Defines inherent and system-dependent data-quality characteristics.", "A quality model does not specify profiling algorithms, thresholds or repair authority."),
    ("jsonpath", "RFC 9535 JSONPath", "IETF", 2024, "internet_standard", "https://www.rfc-editor.org/rfc/rfc9535", "Defines selectors and normalized paths over JSON values.", "Selection result order, duplicates and node identity are not transformation lineage by themselves."),
    ("or2yw", "Modeling and Visualizing OpenRefine Histories as YesWorkflow Diagrams", "Packer et al.", 2021, "primary_paper", "https://arxiv.org/abs/2112.08259", "Maps operation histories to prospective workflow provenance.", "Prospective provenance does not prove replay compatibility or result equivalence."),
    ("repro-openrefine", "Modeling Provenance and Understanding Reproducibility for OpenRefine Workflows", "McPhillips et al.", 2019, "primary_paper", "https://www.usenix.org/system/files/tapp2019-paper-mcphillips_0.pdf", "Analyzes recipes, histories and provenance requirements for reproducible cleaning.", "Recorded operations alone may omit environment, source and external-service dependencies."),
    ("arrow-security", "Apache Arrow Security Considerations", "Apache Arrow", 2026, "official_specification", "https://arrow.apache.org/docs/format/Security.html", "Requires validation of untrusted buffers, offsets, encodings and UTF-8.", "Carrier validation does not establish logical-schema or domain validity."),
    ("data-diff", "Provenance and Data Differencing for Workflow Reproducibility Analysis", "Missier et al.", 2014, "primary_paper", "https://arxiv.org/abs/1406.0905", "Combines workflow provenance and data differencing to analyze reproducibility.", "A diff requires explicit identity, order and tolerance and does not identify the cause alone."),
]


def sources() -> list[dict[str, Any]]:
    return sorted(({"source_id": f"source.preparation.{k}", "title": t, "publisher": p, "year": y,
                    "source_kind": kind, "url": url, "supported_claim": claim,
                    "authority_limit": limit, "primary_or_official": True,
                    "status": "INDEPENDENTLY_RESEARCHED_PRIMARY_OR_OFFICIAL"}
                   for k, t, p, y, kind, url, claim, limit in SOURCE_ROWS), key=lambda r: r["source_id"])


MODULE_ROWS = [
    ("project-purpose", "Which user, analytical job, admitted source scope, intended output and prohibited use define a preparation project?", "project intent", ["openrefine", "wrangler"], []),
    ("source-occurrence", "Which immutable carrier/object/table editions and policy cut may be inspected without mutating the source?", "source ACL", ["prov-o", "csvw-model"], ["project-purpose"]),
    ("data-cut-admission", "Which exact object/table/row/column/version/sample selection enters the project with reproducibility evidence?", "cut contract", ["csvw-model", "prov-o"], ["source-occurrence"]),
    ("carrier-format-probe", "Which format/encoding hypotheses and bounded probe evidence precede parsing?", "format probe", ["rfc4180", "arrow-security"], ["data-cut-admission"]),
    ("dialect-plan", "Which delimiter, quote, escape, newline, header, locale and malformed-record decisions define parsing?", "parse plan", ["csvw-metadata", "duckdb-sniffer"], ["carrier-format-probe"]),
    ("parse-result", "Which values, rejects, byte/row positions, truncation and residual bytes result from parsing?", "total parse algebra", ["rfc4180", "csvw-model"], ["dialect-plan"]),
    ("logical-type-hypothesis", "Which logical types, null tokens, formats and confidence are inferred from which sample and counterexamples?", "schema inference", ["duckdb-sniffer", "frictionless-table"], ["parse-result"]),
    ("declared-schema-binding", "Which accepted schema and constraints bind the parsed occurrence, distinct from inference?", "schema binding", ["csvw-metadata", "json-schema"], ["logical-type-hypothesis"]),
    ("missingness", "Which absent/null/empty/invalid/redacted/unknown/not-applicable states survive parsing and transformations?", "partial information algebra", ["arrow-format", "frictionless-table"], ["parse-result"]),
    ("occurrence-identity", "How are records, rows, fields, columns and cells identified before and after transformations?", "occurrence map", ["csvw-model", "rfc7111", "prov-o"], ["declared-schema-binding"]),
    ("profile-request", "Which subject, exact/approximate measures, sample, tolerances, budgets and privacy constraints define profiling?", "profile plan", ["profiling-survey", "arrow-stats"], ["data-cut-admission"]),
    ("basic-profile", "Which counts, missingness, distinctness, ranges, quantiles, patterns and type observations result?", "column/table profile", ["profiling-survey", "hll", "tdigest"], ["profile-request"]),
    ("dependency-profile", "Which keys, unique combinations, functional/inclusion dependencies and conditional patterns are observed?", "metadata discovery", ["profiling-survey", "tane", "metanome"], ["profile-request"]),
    ("profile-interpretation", "Which exact or approximate observation is accidental, stable, violated or suitable for proposal?", "profile appraisal", ["metanome", "iso25012"], ["basic-profile", "dependency-profile"]),
    ("facet-view", "Which facets, filters, sort and grouping define a temporary view without changing data?", "selection state", ["openrefine-facets", "wrangler"], ["basic-profile"]),
    ("operation-contract", "Which typed inputs/outputs, grain/cardinality, order, partiality, loss and failure define an operation?", "transform algebra", ["codd", "wrangler"], ["occurrence-identity"]),
    ("expression-binding", "Which AST, names, types, functions, null/error propagation, locale/time and determinism bind an expression?", "expression semantics", ["dplyr", "flashfill"], ["operation-contract", "declared-schema-binding"]),
    ("select-filter-sort", "Which selection and ordering operation captures view state into a transform?", "relational transform", ["codd", "dplyr", "openrefine-facets"], ["facet-view", "operation-contract"]),
    ("derive-convert", "Which formula, cast, parse, normalize or derived-field operation creates values with lineage and failure states?", "value transform", ["dplyr", "openrefine-transform"], ["expression-binding"]),
    ("split-merge-fields", "Which split/merge/extract/concatenate operation changes field identity and handles residual content?", "field transform", ["openrefine-transform", "wrangler"], ["operation-contract"]),
    ("reshape", "Which pivot/unpivot/melt/spread/transpose/explode/nest operation changes grain and preserves collisions?", "reshape algebra", ["tidy-data", "openrefine-transform"], ["operation-contract"]),
    ("group-aggregate-window", "Which grouping keys, aggregate/window functions, order and empty-group semantics change grain?", "aggregation algebra", ["codd", "dplyr"], ["operation-contract"]),
    ("join-union", "Which keys, equality/null/time, cardinality/fanout, unmatched rows and schema alignment govern multi-input transforms?", "multi-relation algebra", ["codd", "data-civilizer"], ["operation-contract"]),
    ("deduplicate-cluster", "Which exact duplicate rule or heuristic value clustering proposes consolidation without acquiring entity authority?", "preparation repair proposal", ["openrefine", "raha"], ["basic-profile"]),
    ("error-detection", "Which constraint, pattern, outlier or learned signal proposes that an occurrence is erroneous?", "error proposal", ["nadeef", "raha"], ["profile-interpretation"]),
    ("repair-proposal", "Which candidate value or transform, evidence, confidence and scope is proposed but not yet accepted?", "repair candidate", ["holoclean", "nadeef"], ["error-detection"]),
    ("repair-acceptance", "Which competent user accepts/rejects/edits a repair without rewriting source authority?", "human judgment", ["openrefine", "holoclean"], ["repair-proposal"]),
    ("sampling", "Which probability/nonprobability sample, seed, strata, weights and intended claim define a subset?", "sample design", ["potters-wheel", "profiling-survey"], ["data-cut-admission"]),
    ("preview", "Which sample, truncation, ordering, approximation and stale-state bounds qualify interactive preview?", "preview contract", ["wrangler", "potters-wheel"], ["sampling", "operation-contract"]),
    ("recipe-definition", "Which ordered/graph operations, parameters, dependencies and input/output contracts form a recipe edition?", "recipe IR", ["wrangler", "openrefine-history"], ["derive-convert", "reshape", "join-union"]),
    ("history-branch", "Which authorship, cursor, undo/redo and abandoned branches identify project history?", "history algebra", ["openrefine-history", "or2yw"], ["recipe-definition"]),
    ("inverse-replay-compensation", "Is a rollback an algebraic inverse, deterministic replay from source, checkpoint restore or compensating edit?", "reversal semantics", ["openrefine-history", "repro-openrefine"], ["history-branch"]),
    ("recipe-typecheck", "Do operation ports, schema, grain, partiality and effect boundaries compose without silent coercion?", "recipe validation", ["json-schema", "codd"], ["recipe-definition"]),
    ("replay-compatibility", "Are new input, recipe/provider editions, external lookups and nondeterminism compatible with replay?", "replay verdict", ["repro-openrefine", "prov-o"], ["recipe-typecheck", "inverse-replay-compensation"]),
    ("full-execution", "Which exact input and recipe run under which provider/resource/effect cut and total outcome?", "execution request/receipt", ["prov-o", "wrangler"], ["replay-compatibility"]),
    ("data-diff", "Which row/column/value identities, order, tolerance and unmatched/uncomparable states compare outputs?", "diff algebra", ["data-diff", "prov-o"], ["full-execution"]),
    ("lineage-provenance", "Which output occurrence derives from which input occurrences and operations with what loss?", "lineage graph", ["prov-o", "or2yw"], ["full-execution"]),
    ("quality-handoff", "Which profile/validation/repair evidence is handed to Data Quality without claiming requirement satisfaction?", "quality ACL", ["iso8000-61", "great-expectations"], ["data-diff", "lineage-provenance"]),
    ("prepared-output", "Which input, recipe, run, schema, diff, lineage, encoding and policy identify a prepared output edition?", "output release", ["csvw-model", "prov-o"], ["quality-handoff"]),
    ("publication", "Which destination intent, authorization, attempt and receipt publish an output without owning storage/runtime?", "effect handoff", ["openrefine", "prov-o"], ["prepared-output"]),
    ("privacy-safety", "Which sensitive fields, purpose, masking, minimization, logs, retention and export controls govern interactive work?", "privacy profile", ["openrefine", "arrow-security"], ["project-purpose"]),
    ("preparation-product-boundary", "What project/recipe/preview/replay/diff/publication lifecycle belongs to Self-Service Data Preparation?", "product boundary", ["openrefine", "wrangler"], ["publication", "privacy-safety"]),
    ("batch-transform-seam", "Which accepted recipe may become a deployed, scheduled and operated transform build owned elsewhere?", "product ACL", ["wrangler", "prov-o"], ["preparation-product-boundary"]),
    ("profiling-capability-seam", "How is generic profiling shared with quality/catalog/preparation without becoming a separate product or authority?", "capability boundary", ["profiling-survey", "metanome"], ["profile-interpretation", "preparation-product-boundary"]),
]


def modules() -> list[dict[str, Any]]:
    return [{"module_id": f"module.preparation.{k}", "owned_question": q, "formalism": f,
             "source_refs": sorted(f"source.preparation.{s}" for s in refs),
             "dependency_refs": sorted(f"module.preparation.{d}" for d in deps),
             "authority_limit": "A profile, inferred schema, preview, suggested repair or prepared output remains scoped evidence; it does not mutate source truth, certify quality, deploy production execution or authorize downstream effects.",
             "research_status": "EVIDENCE_BACKED_CANDIDATE_UNRATIFIED"}
            for k, q, f, refs, deps in MODULE_ROWS]


LAW_STATEMENTS = [
    "Source occurrence is not admitted cut, parsed table, view, project state or prepared output.",
    "Read access is not mutation authority; preparation never silently rewrites the source.",
    "Carrier format is not schema, logical type, semantic type or domain meaning.",
    "Format probe is a hypothesis and not a successful parse or conformance verdict.",
    "Encoding, delimiter, quote, escape, header, locale and newline are separate parse decisions.",
    "Best-effort parsing is not lossless parsing; skipped or malformed records remain explicit.",
    "Parsed empty string, absent field, null token, invalid value, redacted value, unknown and not-applicable are distinct.",
    "Physical validity bitmap is not business missingness semantics.",
    "Inferred schema is not declared schema; declared schema is not observed conformance.",
    "Type inferred from a sample is not a type law for the unobserved population.",
    "Type coercion success is not semantic preservation or unit/currency/time-zone correctness.",
    "Row position is not stable record identity; column name is not stable field identity.",
    "Cell identity cannot survive filter, pivot, explode, join or aggregate by positional coincidence.",
    "Profile request is not profile result; profile result is not requirement, violation or quality verdict.",
    "Exact count is not approximate estimate; estimate without algorithm/error parameters is incomplete.",
    "Distinct count is not key uniqueness; observed uniqueness is not declared identifier authority.",
    "Functional dependency observed in one cut is not a business invariant or future guarantee.",
    "Inclusion dependency is not a declared foreign key or valid join path.",
    "Pattern frequency is not allowed-value enumeration or semantic type.",
    "Profile on a sample is not population profile without a sampling/uncertainty claim.",
    "Facet is not filter predicate, selected result, transform scope or materialized subset.",
    "Sort view is not permanent row order until an explicit operation captures it.",
    "Visible rows are not necessarily affected rows; operation scope must be explicit.",
    "Selection is not deletion; deletion proposal is not accepted removal or source mutation.",
    "Transformation syntax is not typed operation semantics or provider-independent portability.",
    "Expression text is not AST, binding, typechecked expression or evaluated value.",
    "Formula evaluation must make null, error, locale, time-zone, precision and nondeterminism explicit.",
    "Normalize/canonicalize is not semantic equivalence and must declare information loss.",
    "Split may leave residual content; merge/concatenate is not inverse without boundaries and escaping.",
    "Pivot and unpivot change grain and can collide, aggregate or invent missing combinations.",
    "Tidy data is a structural profile, not a universal model for every data kind.",
    "Filter preserves row grain but changes membership; aggregate changes grain and often loses identity.",
    "Explode changes cardinality; nest changes container grain; neither is a cosmetic reshape.",
    "Join key equality is not entity equality or referential authority.",
    "Join declaration is not fanout safety; expected cardinality must be checked against the exact cut.",
    "Inner, outer, semi, anti, as-of and interval joins have different membership and time semantics.",
    "Union-by-position is not union-by-name; either may require type widening and provenance retention.",
    "Deduplication is not entity resolution; value clustering is not master-data merge authority.",
    "Error signal is not defect judgment; defect judgment is not repair proposal or accepted correction.",
    "Most-probable repair is not truth; heuristic/model suggestion cannot acquire repair authority.",
    "Manual edit without source occurrence, rationale and recipe semantics is not reproducible preparation.",
    "Sampling for preview is not probability sampling or evidence of full-run correctness.",
    "Preview result is not full execution; truncation, approximation, ordering and stale state remain explicit.",
    "Transform suggested from examples is not validated outside the examples.",
    "Recipe is not project history, execution plan, execution run or output edition.",
    "Recipe edition identity includes ordered operations, parameters, dependencies and semantic versions.",
    "Undo is not always algebraic inverse; it may restore/replay prior state.",
    "Redo branch truncation is not deletion of historical evidence.",
    "Replay on a new cut is not reproduction of the old output; it is a new execution claim.",
    "Same recipe text with different provider/function/external-service editions may not be equivalent.",
    "Silent operation skip or coercion is forbidden; incompatibility returns a typed refusal or partial result.",
    "Data diff requires explicit row/field/value identity, order and tolerance.",
    "No difference under one comparator is not semantic equivalence or downstream fitness.",
    "Lineage assertion is not proof of correctness; provenance completeness is itself scoped.",
    "Prepared output is not quality-certified, catalog-published, production-deployed or analytically fit by default.",
    "Publication intent is not attempt, durable commit, acknowledgement or consumer acceptance.",
    "Profiling is a reusable capability; Preparation uses it for authoring while Quality interprets it against requirements.",
    "Self-Service Preparation owns interactive project and recipe lifecycle, not source connectivity, scheduled pipeline operation or generic query execution.",
    "Accepted preparation recipe may be handed to Batch Transform Build, but authoring acceptance is not deployment qualification.",
    "Notebook computation is broader than governed preparation; preparation is not arbitrary code execution.",
    "Privacy masking in preview is not erasure, anonymization or authorization to export.",
    "Models and agents may suggest dialects, types, transforms or repairs but cannot replace deterministic parsing, validation, provenance, user acceptance or effect authority.",
]


def laws() -> list[dict[str, Any]]:
    return [{"law_id": f"law.preparation.{i:03d}", "statement": s,
             "status": "EVIDENCE_BACKED_CANDIDATE_UNRATIFIED", "canonical_gaps_closed": 0}
            for i, s in enumerate(LAW_STATEMENTS, 1)]


METHOD_GROUPS = {
    "format_parse": ["format signature probe", "character encoding detection", "CSV dialect inference", "header inference", "column-count consistency scan", "JSON record-path selection", "fixed-width parsing", "delimited parsing", "regex parsing", "date/time parsing", "number/decimal parsing", "locale-aware parsing", "null-token recognition", "malformed-row quarantine", "schema-on-read", "explicit schema parse", "opaque unsupported type preservation"],
    "profiling": ["row/record count", "null/missing count", "distinct count exact", "HyperLogLog distinct estimate", "min/max", "mean/variance", "quantile exact", "t-digest quantile estimate", "frequency histogram", "top-k/heavy hitters", "string length profile", "value pattern profile", "type detection", "domain/range profile", "unique column discovery", "unique column-combination discovery", "functional dependency discovery", "approximate functional dependency", "inclusion dependency discovery", "conditional dependency discovery", "correlation/association profile", "schema drift profile", "nested structure profile"],
    "selection_sampling": ["text facet", "numeric facet", "timeline facet", "scatter facet", "custom expression facet", "filter predicate", "sort view", "group view", "simple random sample", "systematic sample", "stratified sample", "reservoir sample", "hash-stable sample", "head/tail preview", "rare-value sample", "error-focused sample", "full scan"],
    "value_field_transform": ["trim/collapse whitespace", "case normalization", "Unicode normalization", "find/replace", "regex extract/replace", "string split", "field merge/concatenate", "substring/token extraction", "type cast", "unit conversion", "date/time conversion", "number/decimal conversion", "derived formula", "lookup enrichment", "conditional value", "missing-value fill", "value map/recode", "rank/window derivation", "field rename", "field reorder", "field drop", "field duplicate"],
    "reshape_grain": ["row filter", "row sort", "distinct rows", "transpose", "pivot wider", "unpivot/melt longer", "split rows", "split columns", "explode list", "nest records", "flatten nested object", "group and aggregate", "window calculation", "record assembly", "record flattening", "one-hot encoding", "binning/discretization"],
    "multi_input": ["inner join", "left/right/full outer join", "semi join", "anti join", "cross join", "as-of join", "interval/range join", "fuzzy join", "union by position", "union by name", "intersect", "except", "coalesce sources", "schema mapping", "join path discovery", "join fanout preflight"],
    "clean_repair": ["constraint violation detection", "pattern violation detection", "outlier detection", "duplicate-row detection", "value clustering", "spell/lexical normalization", "reference lookup validation", "probabilistic error detection", "probabilistic repair proposal", "example-synthesized transform", "manual cell correction", "bulk accepted correction", "repair reject/abstain", "repair conflict adjudication"],
    "recipe_history": ["operation capture", "recipe typecheck", "ordered replay", "DAG replay", "undo by state restore", "redo", "history branch", "checkpoint restore", "inverse operation", "compensating operation", "recipe parameterization", "recipe extraction/import", "input compatibility check", "provider compatibility check", "external dependency pinning", "historical replay"],
    "assurance_diff": ["schema conformance", "row-count reconciliation", "column-count reconciliation", "key/cardinality assertion", "not-null assertion", "range/set assertion", "referential assertion", "sample/full differential", "row-level diff", "field-level diff", "tolerance-aware numeric diff", "order-aware diff", "unmatched/uncomparable report", "lineage completeness check", "preview/full-run differential", "cross-provider differential", "metamorphic transform test", "round-trip/invertibility test"],
    "publish": ["CSV export", "JSON export", "Arrow export", "Parquet export", "database-table materialization", "object publication", "schema/metadata sidecar", "recipe publication", "profile publication", "lineage publication", "prepared-output edition", "delta publication", "destination acknowledgement", "withdraw/supersede output"],
}


def methods() -> list[dict[str, Any]]:
    module_for = {"format_parse": "parse-result", "profiling": "profile-interpretation", "selection_sampling": "facet-view", "value_field_transform": "derive-convert", "reshape_grain": "reshape", "multi_input": "join-union", "clean_repair": "repair-acceptance", "recipe_history": "replay-compatibility", "assurance_diff": "data-diff", "publish": "prepared-output"}
    source_for = {"format_parse": ["csvw-model", "duckdb-sniffer"], "profiling": ["profiling-survey", "metanome"], "selection_sampling": ["openrefine-facets", "potters-wheel"], "value_field_transform": ["wrangler", "dplyr"], "reshape_grain": ["tidy-data", "openrefine-transform"], "multi_input": ["codd", "data-civilizer"], "clean_repair": ["nadeef", "holoclean", "raha"], "recipe_history": ["openrefine-history", "repro-openrefine"], "assurance_diff": ["data-diff", "json-schema"], "publish": ["prov-o", "csvw-model"]}
    rows = []
    for group, names in METHOD_GROUPS.items():
        for i, name in enumerate(names, 1):
            rows.append({"method_type_id": f"method.preparation.{group}.{i:02d}", "method_group": group,
                         "name": name, "semantic_module_ref": f"module.preparation.{module_for[group]}",
                         "source_refs": sorted(f"source.preparation.{s}" for s in source_for[group]),
                         "result_law": "Every method returns a typed, scoped, editioned result with occurrence/grain/cardinality identity, partiality, uncertainty, loss, provenance and refusals; it never silently mutates source truth or claims quality/effect authority.",
                         "llm_dependency": "none", "status": "EVIDENCE_BACKED_METHOD_TYPE_CANDIDATE_UNRATIFIED"})
    return rows


EXPERT_ROWS = [
    ("raman", "Vijayshankar Raman", "interactive data cleaning", "Interleave discrepancy detection and transforms while preserving samples, undo and full-run qualification.", ["potters-wheel"]),
    ("hellerstein", "Joseph Hellerstein", "interactive data systems", "Separate rapid sample feedback from full execution and expose reusable transformation programs.", ["potters-wheel", "wrangler"]),
    ("kandel", "Sean Kandel", "visual data wrangling", "Combine direct manipulation, suggestions, previews and auditable histories without making suggestions authoritative.", ["wrangler"]),
    ("heer", "Jeffrey Heer", "interactive visualization and wrangling", "Use visual profiles and previews to improve authoring while retaining exact operation semantics.", ["wrangler"]),
    ("paepcke", "Andreas Paepcke", "human-centered data transformation", "Make transform parameters reviewable and reusable across tools and datasets.", ["wrangler"]),
    ("wickham", "Hadley Wickham", "tidy data and manipulation grammars", "Expose variable, observation and observational-unit grain and use a small composable verb algebra.", ["tidy-data", "dplyr"]),
    ("naumann", "Felix Naumann", "data profiling and quality", "Treat basic statistics, keys and dependencies as typed metadata discoveries bound to an exact data cut.", ["profiling-survey", "metanome"]),
    ("abedjan", "Ziawasch Abedjan", "data profiling and error detection", "Separate profiling tasks, algorithms, outputs and learned error signals from declared constraints.", ["profiling-survey", "raha"]),
    ("golab", "Lukasz Golab", "profiling and data management", "Specify requested metadata and exact/approximate scope before interpreting profile outputs.", ["profiling-survey"]),
    ("papenbrock", "Thorsten Papenbrock", "dependency discovery", "Use interchangeable, benchmarkable profiling algorithms with typed input and result contracts.", ["metanome"]),
    ("ilyas", "Ihab Ilyas", "data cleaning and uncertainty", "Keep detection, candidate repair, probabilistic inference and accepted correction as separate states.", ["nadeef", "holoclean"]),
    ("chu", "Xu Chu", "constraint and statistical cleaning", "Combine constraints and statistics without treating a most-probable repair as source truth.", ["holoclean"]),
    ("rekatsinas", "Theodoros Rekatsinas", "probabilistic data repair", "Expose the intention/error model, candidates and probabilities behind holistic repair proposals.", ["holoclean"]),
    ("tang", "Nan Tang", "data cleaning systems", "Factor heterogeneous detectors/repairs and make human feedback and configuration evidence explicit.", ["nadeef", "raha"]),
    ("ouzzani", "Mourad Ouzzani", "generalized cleaning", "Separate extensible rule interfaces from the engine and metadata/review lifecycle.", ["nadeef", "raha"]),
    ("mahdivi", "Mohammad Mahdavi", "configuration-light error detection", "Record generated detector configurations, representative labels and residual assumptions.", ["raha"]),
    ("gulwani", "Sumit Gulwani", "programming by example", "Treat synthesized transformations as ranked hypotheses and validate them on counterexamples.", ["flashfill"]),
    ("codd", "E. F. Codd", "relational algebra", "Preserve relation, tuple, attribute and operator semantics beneath user-facing transform grammars.", ["codd"]),
    ("flajolet", "Philippe Flajolet", "probabilistic cardinality estimation", "Expose sketch precision and uncertainty rather than presenting approximate distinct counts as exact.", ["hll"]),
    ("dunning", "Ted Dunning", "streaming quantile sketches", "Bind quantile sketches to compression, merge and error behavior, especially at distribution tails.", ["tdigest"]),
    ("delpeuch", "Antonin Delpeuch", "OpenRefine and reconciliation", "Preserve project history, transform scope, replay limitations and external-service dependencies.", ["openrefine", "openrefine-history"]),
    ("mcphillips", "Timothy McPhillips", "workflow provenance", "Capture recipe, source, environment and prospective/retrospective provenance needed for reproducibility.", ["repro-openrefine", "or2yw"]),
    ("miller", "Renée J. Miller", "data integration and discovery", "Treat discovered join paths and schemas as candidates requiring semantic/cardinality fitness checks.", ["data-civilizer"]),
    ("castro-fernandez", "Raul Castro Fernandez", "data discovery and cleaning", "Integrate profiling and discovery while keeping path selection and quality judgment explicit.", ["data-civilizer", "raha"]),
    ("w3c-csvw", "W3C CSV on the Web Working Group", "tabular metadata", "Separate carrier dialect, table schema, rows/columns/cells and transformation metadata.", ["csvw-model", "csvw-metadata"]),
    ("arrow", "Apache Arrow format maintainers", "columnar representation", "Preserve logical/physical type, null layout, statistics exactness and unsupported-type opacity.", ["arrow-format", "arrow-stats", "arrow-opaque"]),
]


def experts() -> list[dict[str, Any]]:
    return [{"expert_id": f"expert.preparation.{k}", "name": n, "specialism": s,
             "learning_for_corpus": learn, "source_refs": sorted(f"source.preparation.{r}" for r in refs),
             "authority_limit": "Expert work informs bounded propositions; no person, paper, vendor or standards body becomes the SAN semantic owner.",
             "status": "LEARNING_PROFILE_NOT_ENDORSEMENT"}
            for k, n, s, learn, refs in EXPERT_ROWS]


INNOVATION_ROWS = [
    ("or2yw", 2021, "Prospective provenance from OpenRefine histories", "Makes operation histories queryable workflow artifacts while preserving reproducibility gaps.", ["or2yw"], "none"),
    ("arrow-parquet-nested", 2022, "Correct nested Arrow/Parquet translation", "Highlights explicit nullability, repetition and schema-loss requirements for flattening and carrier conversion.", ["arrow-format"], "none"),
    ("json-schema-2020", 2022, "JSON Schema 2020-12 validation vocabularies", "Separates assertion, annotation, evaluation and dialect semantics for structured preparation.", ["json-schema"], "none"),
    ("duckdb-sniffer", 2023, "Multi-hypothesis CSV dialect/type sniffer", "Makes sampled dialect/header/type inference inspectable and overrideable rather than hidden parser magic.", ["duckdb-sniffer"], "none"),
    ("jsonpath", 2024, "RFC 9535 JSONPath", "Standardizes selector semantics needed for nested-source cuts and expression bindings.", ["jsonpath"], "none"),
    ("openrefine-repro", 2024, "OpenRefine reproducibility modernization", "Strengthens operation serialization and reproducible recipe work while keeping environment/source dependencies explicit.", ["openrefine-history", "repro-openrefine"], "none"),
    ("schema-inference-function", 2024, "On-demand scalable schema inference", "Treats inferred schema as a queryable result with local/global merge rather than implicit ingestion truth.", ["duckdb-sniffer", "metanome"], "none"),
    ("soft-fd-repair", 2024, "Soft functional-dependency repair", "Adds weighted constraint trade-offs while preserving optimality/model assumptions and repair authority seams.", ["tane", "holoclean"], "none"),
    ("frictionless-current", 2025, "Current Frictionless Table Schema", "Maintains portable missing-value, type, key and constraint metadata for tabular packages.", ["frictionless-table"], "none"),
    ("arrow-opaque", 2026, "Canonical opaque external types", "Prevents adapters from inventing false semantic equivalence for unsupported source types.", ["arrow-opaque"], "none"),
    ("arrow-stats", 2026, "Arrow statistics schema", "Carries exact/approximate row and column statistics with explicit names and physical targets.", ["arrow-stats"], "none"),
    ("arrow-security", 2026, "Untrusted columnar-input validation guidance", "Moves buffer/offset/UTF-8 validation into preparation admission and decode qualification.", ["arrow-security"], "none"),
    ("openrefine-scope", 2026, "Explicit facet versus operation-scope documentation", "Documents cases where visible facets do not constrain transforms, motivating an executable scope contract.", ["openrefine-facets"], "none"),
    ("large-data-preview", 2026, "Bounded local/remote interactive preview", "Separates sample/preview execution from exact full-data execution and cross-provider differential evidence.", ["wrangler", "duckdb-csv"], "none"),
    ("assisted-preparation", 2026, "Governed assisted transform and repair proposals", "Allows models or agents to suggest dialects/types/transforms while deterministic typecheck, preview, review and replay remain authoritative.", ["wrangler", "raha"], "optional_ai_or_llm_proposal_only"),
]


def innovations() -> list[dict[str, Any]]:
    return [{"innovation_id": f"innovation.preparation.{k}", "year": y, "name": n,
             "compiler_relevance": rel, "source_refs": sorted(f"source.preparation.{r}" for r in refs),
             "ai_or_llm_dependency": dep, "status": "RECENT_INNOVATION_CANDIDATE_UNRATIFIED"}
            for k, y, n, rel, refs, dep in INNOVATION_ROWS]


def module_refs_for_library(ref: str) -> list[str]:
    t = ref.lower(); keys = {"project-purpose", "data-cut-admission", "operation-contract", "preparation-product-boundary"}
    if any(x in t for x in ("codec", "format", "parser", "schema", "logical_type")): keys |= {"carrier-format-probe", "dialect-plan", "parse-result", "logical-type-hypothesis", "declared-schema-binding", "missingness"}
    if any(x in t for x in ("profil", "quality")): keys |= {"profile-request", "basic-profile", "dependency-profile", "profile-interpretation", "quality-handoff", "profiling-capability-seam"}
    if any(x in t for x in ("selection", "predicate", "facet")): keys |= {"facet-view", "select-filter-sort", "sampling", "preview"}
    if any(x in t for x in ("formula", "expression", "typechecker")): keys |= {"expression-binding", "derive-convert", "recipe-typecheck"}
    if any(x in t for x in ("graph", "relational", "query", "mapping", "differential")): keys |= {"reshape", "group-aggregate-window", "join-union", "data-diff"}
    if any(x in t for x in ("recipe", "workspace", "transform_definition")): keys |= {"recipe-definition", "history-branch", "inverse-replay-compensation", "replay-compatibility", "batch-transform-seam"}
    if any(x in t for x in ("provenance", "lineage")): keys |= {"occurrence-identity", "lineage-provenance", "prepared-output"}
    if any(x in t for x in ("export", "materializ")): keys |= {"full-execution", "prepared-output", "publication"}
    if "privacy" in t: keys |= {"privacy-safety"}
    return sorted(f"module.preparation.{k}" for k in keys)


def library_bindings(source_ids: set[str]) -> list[dict[str, Any]]:
    direct = declared_product_libraries(); evidence = sorted(source_ids)[:7]
    return [{"library_ref": ref, "relationship_to_product": "DECLARED_CONCRETE_BINDING" if ref in direct else "JUSTIFIED_NEIGHBOR_IMPORT_OR_OWNER",
             "semantic_module_refs": module_refs_for_library(ref), "evidence_refs": evidence,
             "downstream_product_refs": sorted(PRODUCTS | {"product.batch_transform_build", "product.data_quality_operations"}),
             "downstream_contract_route": "DECLARED_PRODUCT_BINDING_UNRATIFIED" if ref in direct else "NEIGHBOR_IMPORT_CANDIDATE_UNRATIFIED",
             "refusal_reasons": ["OWNER_RATIFICATION_MISSING", "EXACT_CONTRACT_UNSELECTED", "QUALIFIED_IMPLEMENTATION_MISSING", "TWO_VERTICAL_ACCEPTANCE_MISSING"],
             "compiler_binding": "REFUSED", "completion_claim": False} for ref in LIBRARIES]


def findings() -> list[dict[str, Any]]:
    rows = [
        {"finding_id": "finding.preparation.product.retain-narrow.v1", "candidate_disposition": "RETAIN_SELF_SERVICE_DATA_PREPARATION_BUT_NARROW_IMPORTED_OWNERS", "product_ref": "product.self_service_data_preparation", "library_refs": sorted(declared_product_libraries()), "finding": "Retain admitted-cut, interactive project, facet/selection, recipe authoring/history, preview/replay/diff and prepared-output publication lifecycle; import source access, parsing/codec, relational execution, profiling/statistics, quality authority, storage and downstream effects.", "owner_decision": "UNRATIFIED", "canonical_gaps_closed": 0},
        {"finding_id": "finding.preparation.profiling-capability.v1", "candidate_disposition": "KEEP_PROFILING_AS_REUSABLE_CAPABILITY_NOT_NEW_PRODUCT", "library_refs": ["library.qor.data_profiling_kernel", "library.method_kernels.data_quality_methods"], "finding": "Profiling produces scoped descriptive/dependency observations reusable by preparation, catalog and quality. Preparation uses them to author; Data Quality interprets them against requirements. No independent product lifecycle is yet proven.", "owner_decision": "UNRATIFIED", "canonical_gaps_closed": 0},
        {"finding_id": "finding.preparation.batch-transform-seam.v1", "candidate_disposition": "HAND_ACCEPTED_RECIPE_TO_BATCH_TRANSFORM_AS_UNQUALIFIED_INPUT", "product_ref": "product.self_service_data_preparation", "neighbor_product_ref": "product.batch_transform_build", "library_refs": ["library.recipe.definition.compiler", "library.transform_definition.compiler"], "finding": "An accepted interactive recipe can seed a deployed transform definition only after compatibility, qualification, scheduling, resource, observability and operational acceptance owned by Batch Transform Build.", "owner_decision": "UNRATIFIED", "canonical_gaps_closed": 0},
        {"finding_id": "finding.preparation.preview-seam.v1", "candidate_disposition": "SPLIT_PREVIEW_FROM_FULL_EXECUTION_AND_PUBLICATION", "library_refs": ["library.recipe.replay.evaluator", "library.pipeline.materialization_publisher"], "finding": "Interactive preview is a bounded sample/approximation artifact; full execution and publication require exact cuts, receipts, differential evidence and destination effects.", "owner_decision": "UNRATIFIED", "canonical_gaps_closed": 0},
    ]
    for i, (ref, rationale) in enumerate(VACANCIES, 1):
        rows.append({"finding_id": f"finding.preparation.library-vacancy.{i:02d}", "candidate_disposition": "NEW_LIBRARY_BOUNDARY_CANDIDATE_UNRATIFIED", "proposed_library_ref": ref, "library_refs": [], "finding": rationale, "owner_decision": "UNRATIFIED", "canonical_gaps_closed": 0})
    return rows


def bounded_context() -> dict[str, Any]:
    return {"slice_id": "slice.data-preparation-profiling.v1", "retained_product": "product.self_service_data_preparation",
            "inside": ["immutable data-cut admission", "interactive project and view state", "profiling intake and interpretation for authoring", "typed recipe authoring and history", "preview, replay and diff", "repair proposal/acceptance", "prepared-output edition and publication handoff"],
            "imported_owners": ["source connectivity and mutation", "carrier codecs and generic parsing", "relational/query execution", "statistical profiling kernels", "quality requirements/defects/certification", "entity/master/reference authority", "storage/materialization runtime", "scheduled transform deployment", "downstream analytics and business effects"],
            "non_collapse_summary": "carrier != schema; inference != declaration; profile != quality; facet/view != transform; preview != full run; suggestion != accepted repair; recipe != history/run/output; output != certification/deployment",
            "product_boundary_candidates": [{"product_ref": "product.self_service_data_preparation", "status": "RETAIN_BUT_NARROW_UNRATIFIED"}],
            "profiling_disposition": "REUSABLE_CAPABILITY_NOT_INDEPENDENT_PRODUCT_UNRATIFIED",
            "status": "CANDIDATE_UNRATIFIED", "completion_claim": False}


def build() -> dict[str, Any]:
    src = sources(); source_ids = {r["source_id"] for r in src}; mods = modules(); bindings = library_bindings(source_ids)
    axes = [{"library_ref": b["library_ref"], "axis": axis, "semantic_module_refs": b["semantic_module_refs"], "evidence_refs": b["evidence_refs"], "decision_candidate": "UNRESOLVED_RESEARCHED_CANDIDATE", "coordinate_answers": [], "owner_decision": "UNRATIFIED", "canonical_gaps_closed": 0, "completion_claim": False} for b in bindings for axis in AXES]
    result = {"sources": src, "modules": mods, "laws": laws(), "methods": methods(), "experts": experts(), "innovations": innovations(), "libraries": bindings, "axes": axes, "findings": findings(), "context": bounded_context()}
    result["summary"] = {"slice_id": "slice.data-preparation-profiling.v1", "as_of": AS_OF,
        "primary_or_official_sources": len(src), "semantic_modules": len(mods), "non_collapse_laws": len(LAW_STATEMENTS),
        "method_types": sum(map(len, METHOD_GROUPS.values())), "expert_learning_profiles": len(EXPERT_ROWS), "recent_innovations": len(INNOVATION_ROWS),
        "declared_product_libraries": len(declared_product_libraries()), "justified_neighbor_libraries": len(NEIGHBORS), "bound_libraries": len(LIBRARIES),
        "library_axis_decision_candidates": len(axes), "candidate_new_products": 0, "candidate_new_library_vacancies": len(VACANCIES),
        "owner_decisions": 0, "exact_contracts_selected": 0, "qualified_implementations": 0, "canonical_gaps_closed": 0, "completion_claim": False}
    return result


def outputs() -> dict[str, str]:
    b = build(); files = {
        "primary-sources.jsonl": "".join(canonical(r) + "\n" for r in b["sources"]),
        "semantic-modules.jsonl": "".join(canonical(r) + "\n" for r in b["modules"]),
        "non-collapse-laws.jsonl": "".join(canonical(r) + "\n" for r in b["laws"]),
        "data-preparation-profiling-method-taxonomy.jsonl": "".join(canonical(r) + "\n" for r in b["methods"]),
        "expert-learning-profiles.jsonl": "".join(canonical(r) + "\n" for r in b["experts"]),
        "innovation-records.jsonl": "".join(canonical(r) + "\n" for r in b["innovations"]),
        "library-semantic-bindings.jsonl": "".join(canonical(r) + "\n" for r in b["libraries"]),
        "library-axis-decision-candidates.jsonl": "".join(canonical(r) + "\n" for r in b["axes"]),
        "product-capability-boundary-findings.jsonl": "".join(canonical(r) + "\n" for r in b["findings"]),
        "bounded-context.json": json.dumps(b["context"], ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        "summary.json": json.dumps(b["summary"], ensure_ascii=False, sort_keys=True, indent=2) + "\n"}
    claims = {n: {"bytes": len(v.encode()), "sha256": hashlib.sha256(v.encode()).hexdigest()} for n, v in files.items()}
    files["manifest.json"] = json.dumps({"manifest_id": "manifest.data-preparation-profiling-semantic-slice.v1", "as_of": AS_OF, "files": claims, "completion_claim": False}, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    return files


def main() -> int:
    for name, value in outputs().items(): (HERE / name).write_text(value)
    s = build()["summary"]
    print(f"BUILD PASS data-preparation/profiling semantic slice: {s['semantic_modules']} modules, {s['method_types']} methods, {s['bound_libraries']} libraries, {s['library_axis_decision_candidates']} unresolved axis decisions")
    return 0


if __name__ == "__main__": raise SystemExit(main())
