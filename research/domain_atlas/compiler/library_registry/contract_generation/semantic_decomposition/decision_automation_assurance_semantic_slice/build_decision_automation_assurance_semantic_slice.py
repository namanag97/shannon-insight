#!/usr/bin/env python3
"""Build the evidence-backed decision-automation and assurance semantic slice."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
SEM = HERE.parent
AS_OF = "2026-08-27"
PRODUCTS = {"product.decision_automation", "product.assurance_case_appraisal"}
AXES = [
    "semantic_object", "semantic_role", "identity_and_equality", "grain_and_cardinality",
    "state_and_change", "time", "order_and_topology", "partiality_and_uncertainty",
    "authority_and_trust", "effect_boundary", "representation", "composition_algebra",
    "compatibility_and_evolution", "resources_and_failure", "evidence_and_conformance",
    "privacy_security_safety",
]

NEIGHBORS = {
    "library.cbv.decision_handoff_algebra", "library.cbv.disclosure_model",
    "library.cbv.policy_projection", "library.cp.conformance_oracle",
    "library.csp.authority.authority-conformance", "library.csp.authority.policy-algebra",
    "library.csp.authority.policy-decision", "library.csp.decision.compensation",
    "library.csp.decision.feedback-loop", "library.csp.decision.judgment-port",
    "library.csp.identity.identity-claim", "library.csp.identity.identity-conformance",
    "library.csp.time.temporal-conformance", "library.data_use_policy.decision_evaluation",
    "library.data_use_policy.decision_evidence", "library.data_use_policy.obligation_protocol",
    "library.data_use_policy.policy_edition", "library.data_use_policy.request_context",
    "library.data_use_policy.rule_combination", "library.gmo.audit_receipts",
    "library.gmo.change_review_policy", "library.gmo.policy_client",
    "library.gmo.records_governance", "library.lpe.audit-event-core",
    "library.lpe.audit-trail-reconstructor", "library.lpe.compiler-evidence-binding",
    "library.lpe.provenance-assertion", "library.lpe.retention-policy",
    "library.mae.adversarial_oracle", "library.mae.claim_validation_bridge",
    "library.mae.effect_intent_bridge", "library.mae.effect_receipt_bridge",
    "library.mae.proposal_types", "library.operations_research.constraint_policy_algebra",
    "library.operations_research.decision_problem_semantics", "library.qck.kernel-conformance",
    "library.qor.certification_attestation_kernel", "library.qor.evidence_receipt_kernel",
    "library.qor.rule_specification_kernel", "library.qor.test_case_management_kernel",
    "library.qor.waiver_exception_kernel", "library.review.issue.lifecycle",
    "library.spt.attestation_verifier", "library.spt.authorization_ast",
    "library.spt.evidence_envelopes", "library.spt.policy_enforcer",
    "library.spt.policy_evaluator", "library.spt.use_policy_compiler",
}

VACANCIES = [
    ("library.decision.requirement_graph", "Decision requirements, dependencies, services, information needs and authorities need an editioned graph."),
    ("library.decision.expression_profile", "Expression syntax, types, null/error semantics, functions and determinism need a portable profile."),
    ("library.decision.total_evaluation_result", "Value, not-applicable, unknown, indeterminate, denied and error need a total result algebra."),
    ("library.decision.trace", "Inputs, matched rules, intermediate values, editions, external calls, redactions and result need a replayable trace."),
    ("library.decision.table_analyzer", "Gaps, overlaps, conflicts, redundancy, reachability and hit-policy violations need counterexample-bearing analysis."),
    ("library.decision.policy_applicability", "Subject, purpose, resource, action, context, validity and missing attributes need an applicability result."),
    ("library.decision.combining_algebra", "Rule and policy combining order, precedence, obligations, advice and indeterminate propagation need an algebra."),
    ("library.decision.test_corpus", "Examples, boundaries, counterexamples, properties, mutations and expected traces need an editioned corpus."),
    ("library.decision.semantic_diff", "Model editions need directional behavior, coverage, authority and migration diffs rather than text diffs."),
    ("library.decision.action_proposal_contract", "Decision result, proposed action, rationale, purpose, target, risk and requested authority must remain distinct."),
    ("library.decision.authority_handoff", "Proposal submission and external authority verdict need a typed ACL without importing authorization ownership."),
    ("library.assurance.argument_graph", "Claims, contexts, assumptions, strategies, support, challenge and evidence links need a portable graph."),
    ("library.assurance.defeater_graph", "Rebutting, undercutting and undermining defeaters, status, precedence and disposition need first-class identity."),
    ("library.assurance.evidence_admission", "Evidence occurrence, source, subject, method, relevance, integrity, freshness and admissibility need a result."),
    ("library.assurance.appraisal_plan", "Claim scope, criteria, methods, populations, samples, appraisers, budgets and independence need an approved plan edition."),
    ("library.assurance.appraiser_appointment", "Person/organization, mandate, competence, independence, conflicts and validity need occurrence-scoped evidence."),
    ("library.assurance.evidence_quality_vector", "Relevance, sufficiency, validity, integrity, authenticity, freshness and independence cannot collapse to one score."),
    ("library.assurance.performed_work", "Planned versus performed methods, populations, deviations, failures and receipts need an immutable comparison."),
    ("library.assurance.finding", "Observation, criteria, basis, scope, uncertainty, severity and appraiser need a challengeable finding."),
    ("library.assurance.challenge", "Issue, challenger standing, response, evidence, deadlines, escalation and disposition need a lifecycle."),
    ("library.assurance.bounded_verdict", "Result, scope, criteria, evidence, limitations, residuals, validity and issuer authority need one typed verdict."),
    ("library.assurance.verdict_lifecycle", "Issue, seal, disclose, expire, challenge, supersede, withdraw, revoke and reappraise need append-only transitions."),
    ("library.assurance.appraisal_policy", "Evidence-to-appraisal-result rules and appraisal-result-to-reliance rules must be separate editioned policies."),
    ("library.assurance.reliance_handoff", "A bounded verdict may inform but never become the relying party's acceptance or business decision."),
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
    ("dmn15", "Decision Model and Notation 1.5", "OMG", 2023, "standard", "https://www.omg.org/spec/DMN/1.5/PDF", "Defines decision requirements, boxed expressions, FEEL, decision tables, hit policies and model interchange.", "DMN evaluation is not domain policy authority, authorization or effect execution."),
    ("dmn-tck", "DMN Technology Compatibility Kit", "DMN TCK Community", 2026, "official_conformance_suite", "https://github.com/dmn-tck/tck", "Provides cross-implementation DMN examples and expected results.", "Passing available cases does not prove complete semantics, fitness or portability."),
    ("xacml", "eXtensible Access Control Markup Language 3.0", "OASIS", 2013, "standard", "https://docs.oasis-open.org/xacml/3.0/xacml-3.0-core-spec-os-en.html", "Defines request/response, Permit/Deny/Indeterminate/NotApplicable, combining, obligations and advice.", "XACML authorization semantics are one decision profile and do not execute enforcement effects."),
    ("opa", "Open Policy Agent Documentation", "Open Policy Agent", 2026, "official_documentation", "https://www.openpolicyagent.org/docs/", "Defines policy-as-code evaluation over structured inputs and deployment modes.", "OPA is implementation evidence, not the universal policy or authority model."),
    ("rego", "Rego Policy Language", "Open Policy Agent", 2026, "official_language_documentation", "https://www.openpolicyagent.org/docs/policy-language", "Defines declarative rules over nested structured data.", "A Rego result is not automatically an authorization, action or business decision."),
    ("opa-logs", "OPA Decision Logs", "Open Policy Agent", 2026, "official_documentation", "https://www.openpolicyagent.org/docs/management-decision-logs", "Defines decision identifiers, inputs, bundle revisions, paths and trace metadata.", "A decision log is audit evidence, not an effect or outcome receipt."),
    ("opa-bundles", "OPA Bundles and Signature Verification", "Open Policy Agent", 2026, "official_documentation", "https://www.openpolicyagent.org/docs/management-bundles", "Defines editioned policy/data bundles, activation and verification.", "Bundle signature proves integrity under a key, not policy correctness or mandate."),
    ("opa1", "OPA 1.0", "Open Policy Agent", 2024, "official_release", "https://www.openpolicyagent.org/blog/announcing-opa-1-0-a-new-standard-for-policy-as-code-a6d8427ee828", "Makes Rego v1 syntax and stricter checks the default with migration support.", "Language stabilization does not prove a policy expresses intended domain rules."),
    ("cedar", "Cedar Policy Language Reference", "Cedar Project", 2026, "official_language_documentation", "https://docs.cedarpolicy.com/", "Defines typed principal-action-resource-context authorization policies.", "Cedar is authorization-specific and does not own general business decisions."),
    ("cedar-auth", "How Cedar Authorization Works", "Cedar Project", 2026, "official_documentation", "https://docs.cedarpolicy.com/auth/authorization.html", "Defines default deny, forbid-overrides-permit and diagnostic evaluation.", "One combining discipline cannot silently replace DMN, XACML or vertical precedence."),
    ("cedar-validation", "Cedar Policy Validation", "Cedar Project", 2026, "official_documentation", "https://docs.cedarpolicy.com/policies/validation.html", "Defines schema validation and reports a Lean proof plus Rust differential testing.", "Validation soundness is scoped and does not prove authorization intent or data truth."),
    ("cedar-paper", "Cedar: A New Language for Expressive, Fast, Safe, and Analyzable Authorization", "Cedar authors", 2024, "primary_paper", "https://doi.org/10.1145/3689743", "Presents Cedar semantics, validation, analysis and performance design.", "Research results remain scoped to Cedar's language and tested assumptions."),
    ("datalog", "What You Always Wanted to Know About Datalog", "Ceri, Gottlob and Tanca", 1989, "primary_survey", "https://doi.org/10.1109/69.43410", "Defines Datalog syntax, model-theoretic and fixed-point semantics.", "Datalog inference is not decision authority or an assurance verdict."),
    ("rete", "Rete: A Fast Algorithm for the Many Pattern/Many Object Pattern Match Problem", "Charles Forgy", 1982, "primary_paper", "https://doi.org/10.1016/0004-3702(82)90020-0", "Defines incremental discrimination networks for production-rule matching.", "Efficient matching does not specify conflict resolution, truth or authority."),
    ("nist-zero-trust", "NIST SP 800-207 Zero Trust Architecture", "NIST", 2020, "government_standard", "https://csrc.nist.gov/pubs/sp/800/207/final", "Separates policy decision and policy enforcement points.", "Security architecture does not define all business decision semantics."),
    ("sacm23", "Structured Assurance Case Metamodel 2.3", "OMG", 2023, "standard", "https://www.omg.org/spec/SACM/2.3/PDF", "Defines assurance-case argumentation, artifacts, terminology and package interchange.", "Metamodel conformance does not establish claim validity or appraiser independence."),
    ("sacm-machine", "SACM Machine-Readable Metamodel", "OMG", 2023, "normative_model", "https://www.omg.org/spec/SACM/machine-readable", "Publishes normative machine-readable assurance metamodel artifacts.", "Interchange syntax does not define domain criteria or bounded verdict acceptance."),
    ("iso15026", "ISO/IEC/IEEE 15026-2:2022 Assurance Case", "ISO/IEC/IEEE", 2022, "international_standard", "https://www.iso.org/standard/80625.html", "Defines assurance-case concepts and content for systems and software.", "The standard does not make a case true or transfer relying-party authority."),
    ("gsn", "Goal Structuring Notation Community Standard Version 3", "Assurance Case Working Group", 2021, "community_standard", "https://scsc.uk/gsn", "Defines graphical goal, strategy, solution, context, assumption and justification notation.", "A well-formed GSN graph is not a sound or sufficient argument."),
    ("toulmin", "The Uses of Argument", "Stephen Toulmin", 1958, "primary_book", "https://archive.org/details/usesofargument0000toul", "Distinguishes claim, data, warrant, backing, qualifier and rebuttal.", "The general argument model does not prescribe assurance evidence criteria."),
    ("dung", "On the Acceptability of Arguments and Its Fundamental Role in Nonmonotonic Reasoning", "Phan Minh Dung", 1995, "primary_paper", "https://doi.org/10.1016/0004-3702(94)00041-X", "Defines abstract argumentation frameworks and acceptability semantics.", "Abstract attacks do not supply claim meaning, evidence quality or authority."),
    ("walton", "Argumentation Schemes", "Walton, Reed and Macagno", 2008, "primary_book", "https://doi.org/10.1017/CBO9780511802034", "Catalogs defeasible argument schemes and critical questions.", "A scheme structures inquiry but does not itself establish a verdict."),
    ("assurance20", "Assurance 2.0", "Robin Bloomfield and John Rushby", 2024, "primary_monograph", "https://arxiv.org/abs/2205.04522", "Develops explicit logical arguments, defeaters, evidence and confidence for assurance cases.", "The approach is a method candidate and does not replace accountable appraisal."),
    ("defeaters", "Defeaters and Eliminative Argumentation in Assurance 2.0", "John Rushby", 2022, "primary_paper", "https://arxiv.org/abs/2205.04523", "Makes doubts and counterarguments first-class and requires their disposition.", "Eliminating recorded defeaters does not prove all possible defeaters were found."),
    ("confidence", "A New Approach to Creating Clear Safety Arguments", "Hawkins et al.", 2011, "primary_paper", "https://www-users.cs.york.ac.uk/~rhawkins/papers/SSS11.pdf", "Separates safety arguments from confidence arguments and evidence concerns.", "Confidence structure does not authorize system acceptance."),
    ("dynamic-cases", "Dynamic Safety Cases for Through-Life Safety Assurance", "Kelly and McDermid", 2001, "primary_paper", "https://www-users.cs.york.ac.uk/~tpk/dsc.pdf", "Relates assurance cases to changing systems and operational evidence.", "Runtime updates require controlled validity and cannot rewrite historical verdicts."),
    ("safety-case-patterns", "A Systematic Approach to Safety Case Maintenance", "Kelly and McDermid", 1997, "primary_paper", "https://www-users.cs.york.ac.uk/~tpk/papers/maint.pdf", "Introduces structured patterns and maintenance concerns for assurance arguments.", "Pattern reuse requires local applicability and evidence."),
    ("rfc9334", "RFC 9334 RATS Architecture", "IETF", 2023, "internet_standard", "https://www.rfc-editor.org/rfc/rfc9334", "Separates attester, verifier, relying party, evidence, reference values, endorsements and appraisal policies.", "Attestation result is input to a relying decision, not the decision itself."),
    ("rfc9711", "RFC 9711 Entity Attestation Token", "IETF", 2025, "internet_standard", "https://www.rfc-editor.org/rfc/rfc9711", "Defines claims-set tokens for RATS evidence and attestation results.", "Token validity does not prove every claim or establish relying policy."),
    ("rfc9999", "RFC 9999 RATS Conceptual Message Wrapper", "IETF", 2026, "internet_standard", "https://www.rfc-editor.org/rfc/rfc9999", "Defines protocol-agnostic wrappers for RATS conceptual messages.", "A wrapper preserves role/type metadata but does not perform appraisal."),
    ("cose", "RFC 9052 CBOR Object Signing and Encryption", "IETF", 2022, "internet_standard", "https://www.rfc-editor.org/rfc/rfc9052", "Defines protected cryptographic message structures.", "Signature verification proves cryptographic properties, not mandate or truth."),
    ("prov", "PROV-O", "W3C", 2013, "web_standard", "https://www.w3.org/TR/prov-o/", "Defines entities, activities, agents, derivation and attribution.", "Provenance is not evidence admissibility, conformance or verdict authority."),
    ("in-toto", "in-toto Attestation Framework", "in-toto", 2026, "official_specification", "https://github.com/in-toto/attestation", "Defines subjects, predicates and signed attestations for supply-chain claims.", "An attestation is a statement by an issuer, not independent appraisal."),
    ("slsa", "SLSA Specification 1.1", "OpenSSF", 2025, "community_standard", "https://slsa.dev/spec/v1.1/", "Defines build provenance and increasing supply-chain assurance requirements.", "SLSA levels are scoped supply-chain claims, not universal product assurance."),
    ("dsse", "Dead Simple Signing Envelope", "Secure Systems Lab", 2021, "official_specification", "https://github.com/secure-systems-lab/dsse/blob/master/protocol.md", "Defines a simple signature envelope with payload type binding.", "Envelope validity does not establish payload semantics, truth or authority."),
    ("sigstore", "Sigstore Transparency Log", "Sigstore", 2026, "official_documentation", "https://docs.sigstore.dev/logging/overview/", "Defines transparency-log inclusion and verification for signing events.", "Transparency and non-equivocation do not establish claim correctness."),
    ("scitt", "SCITT Architecture", "IETF SCITT Working Group", 2025, "standards_track_draft", "https://datatracker.ietf.org/doc/draft-ietf-scitt-architecture/", "Defines signed statements, transparency services, receipts, feeds and auditors.", "Draft status and transparency receipts do not create claim truth or appraisal authority."),
    ("iso17020", "ISO/IEC 17020 Conformity Assessment — Inspection Bodies", "ISO/IEC", 2012, "international_standard", "https://www.iso.org/standard/52994.html", "Defines competence, impartiality and consistency requirements for inspection bodies.", "Organizational conformity does not prove each appraisal occurrence correct."),
    ("iso17025", "ISO/IEC 17025 Testing and Calibration Laboratories", "ISO/IEC", 2017, "international_standard", "https://www.iso.org/standard/66912.html", "Defines competence, impartiality and consistent laboratory operation.", "Laboratory accreditation is not evidence relevance or a relying verdict."),
    ("nist-ssdf", "NIST SP 800-218 Secure Software Development Framework", "NIST", 2022, "government_standard", "https://csrc.nist.gov/pubs/sp/800/218/final", "Defines outcome-oriented secure development practices and evidence needs.", "Practice conformance is scoped and does not imply a product is risk-free."),
    ("metamorphic", "Metamorphic Testing: A Review of Challenges and Opportunities", "Chen et al.", 2018, "peer_reviewed_survey", "https://doi.org/10.1145/3143561", "Defines relations for testing systems without complete oracles.", "Metamorphic relations require domain validity and do not replace exact conformance."),
    ("mutation", "Mutation Testing Advances: An Analysis and Survey", "Jia and Harman", 2011, "peer_reviewed_survey", "https://doi.org/10.1109/TSE.2010.62", "Surveys mutation operators and adequacy analysis.", "Mutation score is not semantic correctness or assurance verdict."),
    ("property", "QuickCheck: A Lightweight Tool for Random Testing of Haskell Programs", "Claessen and Hughes", 2000, "primary_paper", "https://doi.org/10.1145/351240.351266", "Defines property-based randomized test generation and shrinking.", "Passing generated cases cannot prove untested properties or authority."),
]


def sources() -> list[dict[str, Any]]:
    return sorted(({"source_id": f"source.decision_assurance.{k}", "title": t, "publisher": p,
                    "year": y, "source_kind": kind, "url": url, "supported_claim": claim,
                    "authority_limit": limit, "primary_or_official": True,
                    "status": "INDEPENDENTLY_REVIEWED_SOURCE_CANDIDATE"}
                   for k, t, p, y, kind, url, claim, limit in SOURCE_ROWS), key=lambda r: r["source_id"])


MODULE_ROWS = [
    ("decision-purpose", "Which decision service, population, purpose, harmed parties and negative mission bound the model?", "decision scope", ["dmn15"], []),
    ("decision-requirements", "Which decisions, information requirements, knowledge sources and services form the requirements graph?", "requirements graph", ["dmn15"], ["decision-purpose"]),
    ("decision-expression", "Which expression profile, types, null/error values, functions and nondeterminism are permitted?", "expression contract", ["dmn15", "datalog"], ["decision-requirements"]),
    ("decision-table", "Which inputs, outputs, rules, annotations and hit policy define a decision table?", "table contract", ["dmn15"], ["decision-expression"]),
    ("policy-model", "Which targets, rules, conditions, effects, obligations, advice and combining policy define evaluation?", "policy contract", ["xacml", "cedar"], ["decision-expression"]),
    ("applicability", "Which subject, purpose, action, resource, context, validity and missing facts determine applicability?", "applicability result", ["xacml", "cedar-auth"], ["policy-model"]),
    ("combining", "Which precedence and combination algebra handles multiple applicable rules and partial results?", "combining algebra", ["xacml", "cedar-auth"], ["applicability"]),
    ("static-analysis", "Which gaps, overlaps, conflicts, shadows, redundancies, cycles and unsupported constructs are proven?", "analysis report", ["dmn15", "cedar-validation"], ["decision-table", "policy-model"]),
    ("decision-compilation", "Which typed model edition lowers to which provider-neutral executable IR?", "compiled decision", ["dmn15", "opa"], ["static-analysis"]),
    ("decision-evaluation", "Which canonical inputs and exact edition produce which total value/refusal and intermediates?", "evaluation occurrence", ["dmn15", "xacml"], ["decision-compilation"]),
    ("decision-trace", "Which rules, values, bundles, functions, redactions and timing explain one result?", "decision trace", ["opa-logs", "dmn15"], ["decision-evaluation"]),
    ("decision-testing", "Which examples, properties, mutations, counterexamples and cross-provider cases qualify semantics?", "test corpus", ["dmn-tck", "property", "mutation"], ["static-analysis"]),
    ("decision-edition", "How do model editions publish, supersede, revoke, retire and replay historically?", "edition lifecycle", ["opa-bundles", "dmn15"], ["decision-testing"]),
    ("decision-semantic-diff", "Which input regions, results, traces and authority obligations change between editions?", "semantic diff", ["dmn-tck", "cedar-validation"], ["decision-edition"]),
    ("action-proposal", "Which decision result supports which non-authoritative proposed action?", "proposal", ["nist-zero-trust"], ["decision-trace"]),
    ("authorization-handoff", "Which external principal/purpose/resource/action authority accepts or refuses the proposal?", "authority ACL", ["xacml", "nist-zero-trust"], ["action-proposal"]),
    ("effect-handoff", "Which authorized effect intent, attempt, receipt, completion and outcome remain outside decision evaluation?", "effect ACL", ["nist-zero-trust"], ["authorization-handoff"]),
    ("feedback", "Which observed outcomes may trigger review without rewriting the historical decision?", "feedback evidence", ["prov"], ["effect-handoff"]),
    ("decision-product-boundary", "What authoring/analysis/edition/invocation/trace/proposal lifecycle belongs to Decision Automation?", "product boundary", ["dmn15", "opa", "cedar"], ["feedback"]),
    ("claim-scope", "Which proposition, subject occurrence, scope, criteria, reliance purpose and time define the claim?", "claim contract", ["sacm23", "iso15026"], []),
    ("argument-graph", "Which claims, strategies, support, contexts, assumptions and evidence form the argument?", "argument graph", ["sacm23", "gsn", "toulmin"], ["claim-scope"]),
    ("defeaters", "Which rebutting, undercutting or undermining doubts attack claims, warrants or evidence?", "defeater graph", ["dung", "defeaters"], ["argument-graph"]),
    ("criteria-binding", "Which externally owned criteria edition applies to which claim and subject scope?", "criteria ACL", ["iso15026"], ["claim-scope"]),
    ("appraisal-plan", "Which methods, populations, samples, environments, appraisers, budgets and independence are approved?", "appraisal plan", ["iso15026", "sacm23"], ["criteria-binding"]),
    ("appraiser-appointment", "Which mandate, competence, independence, conflict and validity qualify one appraiser occurrence?", "appointment", ["iso17020", "iso17025"], ["appraisal-plan"]),
    ("evidence-occurrence", "Which exact artifact/observation/testimony/result occurrence is offered for which subject and claim?", "evidence item", ["sacm23", "prov"], ["argument-graph"]),
    ("evidence-admission", "Which relevance, integrity, authenticity, freshness, custody and disclosure checks admit evidence?", "admission result", ["sacm23", "cose"], ["evidence-occurrence"]),
    ("evidence-quality", "Which independent quality dimensions, uncertainty and counterevidence qualify admitted evidence?", "quality vector", ["assurance20", "confidence"], ["evidence-admission"]),
    ("attestation", "Which issuer makes which authenticated statement about which subject under which profile?", "attestation", ["rfc9334", "in-toto"], ["evidence-occurrence"]),
    ("rats-appraisal", "Which evidence, reference values, endorsements and policy produce which attestation result?", "RATS appraisal", ["rfc9334", "rfc9711"], ["attestation"]),
    ("transparency", "Which signed statement, log inclusion, receipt, feed and non-equivocation evidence exist?", "transparency evidence", ["sigstore", "scitt"], ["attestation"]),
    ("reproduction", "Which exact environment, inputs and procedure reproduce or fail to reproduce a result?", "reproduction result", ["slsa", "nist-ssdf"], ["evidence-admission"]),
    ("performed-work", "Which planned methods actually ran, on which populations, with which deviations and receipts?", "performed work", ["iso15026", "iso17025"], ["appraiser-appointment", "evidence-quality"]),
    ("finding", "Which scoped observation against criteria follows from performed work and evidence?", "finding", ["sacm23", "iso15026"], ["performed-work"]),
    ("challenge", "Which issue, contrary evidence, response, deadline and escalation challenge a finding or case?", "challenge case", ["dung", "walton"], ["finding", "defeaters"]),
    ("defeater-disposition", "Which material defeaters are sustained, mitigated, accepted as residual or unresolved?", "defeater verdict", ["assurance20", "defeaters"], ["challenge"]),
    ("bounded-verdict", "Which scoped result, support, limitations, residuals, validity and issuer mandate may be issued?", "bounded verdict", ["iso15026", "assurance20"], ["defeater-disposition"]),
    ("verdict-lifecycle", "How does a verdict seal, disclose, expire, challenge, supersede, withdraw, revoke and reappraise?", "verdict lifecycle", ["dynamic-cases", "sacm23"], ["bounded-verdict"]),
    ("disclosure", "Which audience receives which minimized claim/evidence/verdict projection?", "disclosure projection", ["rfc9711", "scitt"], ["verdict-lifecycle"]),
    ("reliance-handoff", "How may a relying authority consume a verdict without transferring its decision authority?", "reliance ACL", ["rfc9334", "iso15026"], ["disclosure"]),
    ("assurance-product-boundary", "What claim/argument/plan/appraisal/challenge/verdict lifecycle belongs to Assurance Case Appraisal?", "product boundary", ["sacm23", "iso15026"], ["reliance-handoff"]),
    ("shared-evidence-seam", "Which evidence carriers and policy inputs can both products import without merging their lifecycles?", "shared capability seam", ["sacm23", "dmn15"], ["decision-product-boundary", "assurance-product-boundary"]),
    ("policy-homonyms", "How are business-decision, authorization, governance, appraisal and runtime policies kept distinct?", "language split", ["dmn15", "xacml", "rfc9334"], ["shared-evidence-seam"]),
    ("automation-boundary", "How may models/agents propose rules, evidence or tests without acquiring decision, appraisal or effect authority?", "automation seam", ["cedar-validation", "assurance20"], ["policy-homonyms"]),
]


def modules() -> list[dict[str, Any]]:
    return [{"module_id": f"module.decision_assurance.{k}", "sovereign_question": q,
             "owned_semantic_object": owned,
             "source_refs": sorted(f"source.decision_assurance.{s}" for s in srcs),
             "dependency_refs": sorted(f"module.decision_assurance.{d}" for d in deps),
             "authority_limit": "The module defines a candidate semantic boundary; it does not ratify policy, evidence, authority, effects, verdicts or implementations.",
             "status": "EVIDENCE_BACKED_SEMANTIC_MODULE_CANDIDATE_UNRATIFIED"}
            for k, q, owned, srcs, deps in MODULE_ROWS]


LAW_STATEMENTS = [
    "Decision requirement is not model, model is not edition, edition is not invocation, and invocation is not result.",
    "Decision result is not action proposal, authorization, effect intent, execution receipt or observed outcome.",
    "Prediction, causal estimate, simulation result and optimizer recommendation may be inputs but are not governed decisions.",
    "Decision service ownership does not imply ownership of the vertical facts or policy authority it consumes.",
    "Schema validity is not semantic correctness, table completeness or policy fitness.",
    "Null, absent, unknown, not-applicable, indeterminate, denied and evaluation error remain distinct.",
    "Rule applicability is not rule truth, rule priority or final combined decision.",
    "Rule order is not priority unless the declared combining algebra says so.",
    "First-applicable, priority, deny-overrides, permit-overrides and collect are non-equivalent algebras.",
    "A table overlap may be valid under one hit policy and invalid under another.",
    "No matched rule is not automatically deny, allow, false, zero or missing.",
    "A default is an explicit rule of the decision profile, not absence of semantics.",
    "External function calls require edition, purity, time, failure and replay semantics.",
    "Same edition plus canonical inputs is deterministic or explicitly returns declared nondeterminism.",
    "Decision trace is not an effect receipt or proof that the outcome occurred.",
    "Textual diff is not semantic behavior diff.",
    "Test pass is not proof of completeness, correctness, fitness or authorization.",
    "Conformance to one implementation is not portable conformance.",
    "Mutation score, coverage and property tests are evidence dimensions, not verdicts.",
    "A model or agent proposal remains tainted input until deterministic validation and accountable acceptance.",
    "Human override is a new authority occurrence, not mutation of the prior decision result.",
    "Feedback may trigger review but never rewrites historical inputs, editions or results.",
    "Business decision policy, authorization policy, governance policy, appraisal policy and retry policy are homonyms, not one type.",
    "Policy decision point is not policy enforcement point.",
    "Authorization is scoped to principal, purpose, action, resource, context and time.",
    "Authorization to attempt an effect is not evidence of successful completion.",
    "Claim is not argument, evidence, finding, defeater, appraisal, verdict or relying decision.",
    "A claim identity includes subject occurrence, scope, criteria edition, reliance purpose and time.",
    "Argument graph well-formedness is not soundness, sufficiency or truth.",
    "Context, assumption, warrant, strategy and evidence support have different roles.",
    "Support relation is not entailment unless an explicit logic and premises establish it.",
    "Rebutting, undercutting and undermining defeaters remain distinct.",
    "Absence of known defeaters is not proof that no defeater exists.",
    "Unresolved material defeaters cannot be silently averaged away.",
    "Evidence occurrence is not the source object, abstract evidence type or claim it supports.",
    "Evidence relevance, sufficiency, validity, integrity, authenticity, freshness and independence do not collapse to one score.",
    "Integrity and signature validity do not prove truth, relevance, competence or mandate.",
    "Provenance and custody do not prove correctness.",
    "Attestation is an authenticated statement, not independent appraisal.",
    "Attester, verifier, appraiser, verdict issuer and relying party are distinct roles even when one entity performs several.",
    "RATS evidence, attestation result and relying-party appraisal result remain distinct.",
    "Reference value is not universal known-good truth and remains editioned and scoped.",
    "Endorsement is not evidence appraisal or relying authorization.",
    "Transparency-log inclusion proves registration/inclusion properties, not statement truth.",
    "Non-equivocation is not completeness, correctness or disclosure authority.",
    "Evidence bundle is a carrier and does not become an assurance case by aggregation.",
    "Evidence admission is not evidence acceptance for every claim.",
    "Appraisal plan is not performed work; deviation is not silently conforming work.",
    "Appraiser competence, mandate, independence and conflict are occurrence-scoped evidence, not brand identity.",
    "Accreditation of an organization is not proof that one appraisal occurrence is correct.",
    "Finding is not verdict and verdict is not relying decision.",
    "Waiver accepts a bounded residual under authority; it does not erase a defect or defeater.",
    "Approval, issuance, sealing, disclosure and reliance are distinct events and authorities.",
    "Verdict scope cannot exceed claim, criteria, performed work or admitted evidence scope.",
    "Verdict validity, evidence freshness and criteria validity have independent clocks.",
    "Supersession, withdrawal and revocation do not delete historical verdicts.",
    "Reappraisal creates a new occurrence and cannot rewrite the prior appraisal.",
    "Selective disclosure may preserve verification while intentionally losing context; loss is explicit.",
    "Assurance Case Appraisal does not author domain criteria, accredit providers or make the relying decision.",
    "Decision Automation and Assurance Case Appraisal may share evidence carriers but not aggregate roots or authority.",
    "Generic custody, signature, disclosure and record lifecycle are imported capabilities, not assurance-owned universal meanings.",
    "A decision model may be appraised, but appraisal does not execute or authorize that model.",
    "Every refusal preserves reason, scope, edition, evidence and responsible owner.",
    "Finite time, memory, payload, evidence, privacy and disclosure budgets are declared.",
    "No provider brand, paper, expert or standard becomes the canonical semantic owner.",
]


def laws() -> list[dict[str, Any]]:
    return [{"law_id": f"law.decision_assurance.noncollapse.{i:02d}", "statement": s,
             "law_kind": "NON_COLLAPSE_OR_AUTHORITY_SEAM",
             "compiler_consequence": "Type/refusal/ACL boundaries must preserve this distinction before lowering or binding.",
             "status": "CANDIDATE_UNRATIFIED"} for i, s in enumerate(LAW_STATEMENTS, 1)]


METHOD_GROUPS = {
    "representation": ["decision requirements diagram", "decision service", "literal expression", "context expression", "relation expression", "function definition", "invocation expression", "list expression", "decision table", "business knowledge model", "rule set", "production rule", "Datalog program", "authorization policy", "policy set", "policy template", "constraint model", "decision tree", "scorecard", "stateful decision graph"],
    "static_analysis": ["schema/type validation", "name/dependency resolution", "cycle detection", "decision-table gap analysis", "overlap analysis", "conflict analysis", "shadowed-rule detection", "redundant-rule detection", "unreachable-rule detection", "hit-policy validation", "missing-default analysis", "unsupported-function detection", "purity analysis", "nondeterminism analysis", "symbolic evaluation", "counterexample generation", "semantic equivalence checking", "semantic diff", "blast-radius analysis", "termination/resource analysis"],
    "evaluation": ["unique hit", "any hit", "priority hit", "first hit", "collect hit", "rule-order hit", "output-order hit", "deny overrides", "permit overrides", "first applicable", "only-one applicable", "default deny", "forbid overrides permit", "least fixed point", "RETE matching", "partial evaluation", "incremental evaluation", "memoized evaluation", "sandboxed external function", "total typed refusal"],
    "verification": ["example test", "boundary-value test", "pairwise combinatorial test", "property-based test", "model-based test", "mutation test", "metamorphic test", "fuzz test", "cross-provider differential", "TCK conformance", "condition coverage", "decision coverage", "rule coverage", "MC/DC", "trace replay", "historical-edition replay", "migration differential", "performance/resource qualification"],
    "argument": ["GSN goal decomposition", "GSN strategy", "GSN solution binding", "context/assumption/justification binding", "CAE argument", "SACM argument package", "Toulmin layout", "abstract argumentation framework", "grounded semantics", "preferred semantics", "stable semantics", "defeasible argument scheme", "critical-question review", "eliminative induction", "confidence argument", "Bayesian confidence network", "assurance pattern instantiation", "modular assurance case", "away-goal/reference", "dialectical challenge review"],
    "evidence_appraisal": ["relevance appraisal", "sufficiency appraisal", "validity appraisal", "integrity verification", "authenticity verification", "freshness appraisal", "custody appraisal", "provenance appraisal", "competence appraisal", "mandate appraisal", "independence appraisal", "conflict-of-interest appraisal", "population/sample appraisal", "repeatability appraisal", "reproducibility appraisal", "uncertainty appraisal", "contrary-evidence search", "missing-evidence analysis", "sensitivity analysis", "residual-risk appraisal"],
    "attestation": ["RATS evidence appraisal", "reference-value comparison", "endorsement validation", "appraisal-policy evaluation", "EAT validation", "nonce/freshness validation", "signature verification", "key-status validation", "COSE envelope validation", "DSSE validation", "in-toto attestation validation", "SLSA provenance appraisal", "transparency inclusion verification", "consistency/non-equivocation verification", "feed completeness check", "selective-disclosure verification", "reproduction evaluation", "attestation-result translation"],
    "verdict_governance": ["appraisal plan review", "planned/performed differential", "finding issuance", "defeater classification", "defeater disposition", "challenge intake", "challenge adjudication", "appeal escalation", "waiver assessment", "bounded-verdict issuance", "limitation/residual disclosure", "expiry evaluation", "supersession", "withdrawal", "revocation propagation", "reappraisal", "reliance-purpose check", "verdict semantic diff"],
    "handoff": ["action proposal", "authority request", "authority verdict", "effect intent", "effect attempt", "effect receipt", "outcome observation", "compensation proposal", "unknown-completion reconciliation", "human judgment port", "model-generated proposal", "optimizer recommendation handoff", "causal-estimate handoff", "override occurrence", "feedback signal", "policy review trigger"],
}


def methods() -> list[dict[str, Any]]:
    module_for = {"representation": "decision-expression", "static_analysis": "static-analysis", "evaluation": "decision-evaluation", "verification": "decision-testing", "argument": "argument-graph", "evidence_appraisal": "evidence-quality", "attestation": "rats-appraisal", "verdict_governance": "verdict-lifecycle", "handoff": "effect-handoff"}
    source_for = {"representation": ["dmn15", "xacml"], "static_analysis": ["cedar-validation", "dmn15"], "evaluation": ["dmn15", "xacml", "datalog"], "verification": ["dmn-tck", "property", "mutation"], "argument": ["sacm23", "gsn", "dung"], "evidence_appraisal": ["assurance20", "iso15026"], "attestation": ["rfc9334", "rfc9711", "scitt"], "verdict_governance": ["iso15026", "defeaters"], "handoff": ["nist-zero-trust", "rfc9334"]}
    rows = []
    for group, names in METHOD_GROUPS.items():
        for i, name in enumerate(names, 1):
            rows.append({"method_type_id": f"method.decision_assurance.{group}.{i:02d}", "method_group": group,
                         "name": name, "semantic_module_ref": f"module.decision_assurance.{module_for[group]}",
                         "source_refs": sorted(f"source.decision_assurance.{s}" for s in source_for[group]),
                         "result_law": "Every result is typed, scoped, editioned, replayable and authority-bounded; method output never silently becomes authorization, effect, truth, verdict or reliance.",
                         "llm_dependency": "none", "status": "EVIDENCE_BACKED_METHOD_TYPE_CANDIDATE_UNRATIFIED"})
    return rows


EXPERT_ROWS = [
    ("vanthienen", "Jan Vanthienen", "decision tables and business rules", "Make completeness, overlap, consistency and hit-policy semantics analyzable.", ["dmn15"]),
    ("silver", "Bruce Silver", "DMN modeling and conformance", "Separate requirements diagrams, boxed expressions and executable decision-table semantics.", ["dmn15", "dmn-tck"]),
    ("taylor", "James Taylor", "decision management", "Treat decision models as governed services distinct from predictive inputs and effects.", ["dmn15"]),
    ("forgy", "Charles Forgy", "production-rule evaluation", "Separate matching-network efficiency from conflict resolution and authority.", ["rete"]),
    ("gottlob", "Georg Gottlob", "logic programming", "Use explicit fixed-point and model semantics for rule composition.", ["datalog"]),
    ("sandall", "Torin Sandall", "policy as code", "Keep policy evaluation portable over structured inputs with bundles, tests and decision logs.", ["opa", "rego"]),
    ("hinrichs", "Tim Hinrichs", "declarative policy", "Separate policy definition/evaluation from enforcement and application business logic.", ["opa", "rego"]),
    ("nelson", "Greg Nelson", "formally analyzed authorization", "Combine a small authorization language with validation, formal semantics and differential testing.", ["cedar-paper", "cedar-validation"]),
    ("paverd", "Andrew Paverd", "authorization-language verification", "Use mechanized semantics and counterexamples without confusing soundness scope with policy intent.", ["cedar-paper", "cedar-validation"]),
    ("toulmin", "Stephen Toulmin", "argument structure", "Keep claims, data, warrants, backing, qualifiers and rebuttals distinct.", ["toulmin"]),
    ("dung", "Phan Minh Dung", "abstract argumentation", "Make attack relations and acceptability semantics explicit rather than hiding conflict.", ["dung"]),
    ("walton", "Douglas Walton", "defeasible argumentation", "Use argument schemes plus critical questions to expose presumptions and exceptions.", ["walton"]),
    ("bloomfield", "Robin Bloomfield", "assurance cases", "Use explicit claims, evidence, defeaters and bounded confidence rather than narrative confidence.", ["assurance20"]),
    ("rushby", "John Rushby", "formal methods and Assurance 2.0", "Treat defeaters as first-class review objects and distinguish deductive validity from evidential soundness.", ["assurance20", "defeaters"]),
    ("kelly", "Tim Kelly", "safety-case patterns", "Modularize assurance arguments and control their evolution across system change.", ["gsn", "dynamic-cases", "safety-case-patterns"]),
    ("mcdermid", "John McDermid", "system safety assurance", "Bind reusable argument patterns to local evidence and through-life change.", ["dynamic-cases", "safety-case-patterns"]),
    ("hawkins", "Richard Hawkins", "confidence arguments", "Separate the primary safety argument from confidence in evidence and reasoning.", ["confidence"]),
    ("habli", "Ibrahim Habli", "safety assurance and ethics", "Keep lifecycle, affected-party and independent appraisal concerns visible in assurance.", ["confidence", "iso15026"]),
    ("denney", "Ewen Denney", "formalized assurance cases", "Generate and check structured cases while retaining human/domain appraisal authority.", ["sacm23", "gsn"]),
    ("pai", "Ganesh Pai", "assurance-case automation", "Represent claim-evidence trace and change impact without equating automation with assurance.", ["sacm23", "gsn"]),
    ("thaler", "Dave Thaler", "remote attestation architecture", "Separate attester, verifier, relying party and their independently governed policies.", ["rfc9334", "rfc9711"]),
    ("birkholz", "Henk Birkholz", "attestation and transparency", "Keep evidence, appraisal results, signed statements and transparency receipts typed by role.", ["rfc9334", "scitt"]),
    ("lundblade", "Laurence Lundblade", "Entity Attestation Token", "Bind claims sets, freshness and verification profiles without treating tokens as relying decisions.", ["rfc9711"]),
    ("claessen", "Koen Claessen", "property-based testing", "Generate and shrink counterexamples against declared executable laws.", ["property"]),
    ("hughes", "John Hughes", "property-based and model-based testing", "Use properties and state models to test behavior beyond example cases.", ["property"]),
    ("chen", "Tsong Yueh Chen", "metamorphic testing", "Use justified relations when exact oracles are partial, while preserving relation applicability.", ["metamorphic"]),
]


def experts() -> list[dict[str, Any]]:
    return [{"expert_id": f"expert.decision_assurance.{k}", "name": n, "specialism": s,
             "learning_for_corpus": learn, "source_refs": sorted(f"source.decision_assurance.{r}" for r in refs),
             "authority_limit": "Expert work informs bounded propositions; no person, vendor, standard or paper becomes the semantic owner.",
             "status": "LEARNING_PROFILE_NOT_ENDORSEMENT"} for k, n, s, learn, refs in EXPERT_ROWS]


INNOVATION_ROWS = [
    ("gsn3", 2021, "GSN Community Standard Version 3", "Strengthens portable structured argument notation while leaving soundness and evidence appraisal open.", ["gsn"], "none"),
    ("dsse", 2021, "DSSE payload-type-bound signing", "Separates a reusable signature carrier from the semantics and truth of the signed statement.", ["dsse"], "none"),
    ("iso15026", 2022, "Revised ISO/IEC/IEEE assurance-case standard", "Refreshes the assurance-case contract while preserving relying-party authority.", ["iso15026"], "none"),
    ("assurance20", 2022, "Assurance 2.0 defeater-centered argumentation", "Makes defeaters and eliminative review first-class rather than burying doubts in prose.", ["assurance20", "defeaters"], "none"),
    ("cose", 2022, "COSE standard publication", "Provides typed cryptographic envelopes while explicitly not supplying claim meaning or mandate.", ["cose"], "none"),
    ("dmn15", 2023, "DMN 1.5", "Advances executable decision interchange, FEEL and table semantics with conformance vectors.", ["dmn15", "dmn-tck"], "none"),
    ("sacm23", 2023, "SACM 2.3", "Advances machine-readable argument, artifact and terminology packages for assurance cases.", ["sacm23", "sacm-machine"], "none"),
    ("rats", 2023, "RATS architecture standardization", "Separates evidence appraisal from relying-party appraisal and their policy owners.", ["rfc9334"], "none"),
    ("slsa1", 2023, "SLSA 1.x provenance levels", "Makes supply-chain provenance claims profile-bound and incrementally adoptable.", ["slsa"], "none"),
    ("cedar-vgd", 2024, "Verification-guided Cedar development", "Uses Lean semantics, proof, property tests and Rust differential testing as layered evidence.", ["cedar-paper", "cedar-validation"], "none"),
    ("opa1", 2024, "OPA 1.0 and Rego v1", "Tightens language defaults, static checks and migration behavior for policy-as-code estates.", ["opa1"], "none"),
    ("eat", 2025, "Entity Attestation Token RFC", "Standardizes typed claims-set tokens for evidence and attestation results with freshness concerns.", ["rfc9711"], "none"),
    ("scitt", 2025, "SCITT transparency architecture", "Adds interoperable signed-statement registration, receipts, feeds and non-equivocation evidence.", ["scitt"], "none"),
    ("cmw", 2026, "RATS Conceptual Message Wrapper", "Carries role-typed evidence and appraisal messages without collapsing their semantics.", ["rfc9999"], "none"),
    ("assisted-authoring", 2026, "Governed assisted rule/argument proposal", "Allows models or agents to propose rules, tests, evidence links or defeaters while deterministic checks and accountable authorities retain control.", ["cedar-validation", "assurance20"], "optional_ai_or_llm_proposal_only"),
]


def innovations() -> list[dict[str, Any]]:
    return [{"innovation_id": f"innovation.decision_assurance.{k}", "year": y, "name": n,
             "compiler_relevance": rel, "source_refs": sorted(f"source.decision_assurance.{r}" for r in refs),
             "ai_or_llm_dependency": dep, "status": "RECENT_INNOVATION_CANDIDATE_UNRATIFIED"}
            for k, y, n, rel, refs, dep in INNOVATION_ROWS]


def module_refs_for_library(ref: str) -> list[str]:
    text = ref.lower()
    keys = {"shared-evidence-seam", "policy-homonyms", "automation-boundary"}
    if any(x in text for x in ("decision", "policy", "rule", "authorization_ast")):
        keys |= {"decision-requirements", "decision-expression", "decision-table", "policy-model", "applicability", "combining", "decision-evaluation", "decision-product-boundary"}
    if any(x in text for x in ("conformance", "oracle", "test_case", "adversarial")):
        keys |= {"static-analysis", "decision-testing", "decision-semantic-diff", "performed-work"}
    if any(x in text for x in ("ledger", "audit", "record", "retention", "provenance")):
        keys |= {"decision-trace", "evidence-occurrence", "verdict-lifecycle"}
    if any(x in text for x in ("claim", "argument", "evidence", "assurance", "accountability", "quality", "certification")):
        keys |= {"claim-scope", "argument-graph", "defeaters", "appraisal-plan", "evidence-admission", "evidence-quality", "finding", "bounded-verdict", "assurance-product-boundary"}
    if any(x in text for x in ("attest", "signature", "rats", "envelope", "reproduction")):
        keys |= {"attestation", "rats-appraisal", "transparency", "reproduction"}
    if any(x in text for x in ("custody", "disclosure")):
        keys |= {"evidence-admission", "disclosure"}
    if any(x in text for x in ("authorizer", "effect", "proposal", "judgment", "compensation", "feedback", "handoff")):
        keys |= {"action-proposal", "authorization-handoff", "effect-handoff", "feedback"}
    if "waiver" in text or "review" in text:
        keys |= {"challenge", "defeater-disposition", "verdict-lifecycle"}
    if "identity" in text:
        keys |= {"appraiser-appointment", "attestation"}
    if "time" in text:
        keys |= {"decision-edition", "verdict-lifecycle"}
    return sorted(f"module.decision_assurance.{k}" for k in keys)


def library_bindings(source_ids: set[str]) -> list[dict[str, Any]]:
    direct = declared_product_libraries()
    evidence = sorted(source_ids)[:8]
    return [{"library_ref": ref,
             "relationship_to_products": "DECLARED_CONCRETE_BINDING" if ref in direct else "JUSTIFIED_NEIGHBOR_IMPORT_OR_OWNER",
             "semantic_module_refs": module_refs_for_library(ref), "evidence_refs": evidence,
             "downstream_product_refs": sorted(PRODUCTS | {"product.data_use_policy", "product.lineage_provenance", "product.workflow_case"}),
             "downstream_contract_route": "DECLARED_PRODUCT_BINDING_UNRATIFIED" if ref in direct else "NEIGHBOR_IMPORT_CANDIDATE_UNRATIFIED",
             "refusal_reasons": ["OWNER_RATIFICATION_MISSING", "EXACT_CONTRACT_UNSELECTED", "QUALIFIED_IMPLEMENTATION_MISSING", "TWO_VERTICAL_ACCEPTANCE_MISSING"],
             "compiler_binding": "REFUSED", "completion_claim": False} for ref in LIBRARIES]


def findings() -> list[dict[str, Any]]:
    rows = [
        {"finding_id": "finding.decision_assurance.products.retain-separate.v1", "candidate_disposition": "RETAIN_TWO_INDEPENDENT_PRODUCTS_WITH_TYPED_ACL", "product_refs": sorted(PRODUCTS), "library_refs": sorted(declared_product_libraries()), "finding": "Decision Automation owns model/edition/analysis/invocation/result/trace/proposal lifecycle. Assurance Case Appraisal owns claim/argument/plan/appraisal/challenge/bounded-verdict lifecycle. Either is independently adoptable; evidence and policy imports do not merge them.", "owner_decision": "UNRATIFIED", "canonical_gaps_closed": 0},
        {"finding_id": "finding.decision_assurance.decision-authority-seam.v1", "candidate_disposition": "RECLASSIFY_AUTHORIZER_AND_EFFECT_PORT_AS_IMPORTED_AUTHORITY_CAPABILITIES", "product_ref": "product.decision_automation", "library_refs": ["library.csp.decision.action-authorizer", "library.csp.decision.effect-port"], "finding": "A deterministic decision result may form a proposal, but external principal/purpose/resource/action authority owns authorization and an effect runtime owns attempt/completion/outcome receipts.", "owner_decision": "UNRATIFIED", "canonical_gaps_closed": 0},
        {"finding_id": "finding.decision_assurance.generic-evidence-seam.v1", "candidate_disposition": "RECLASSIFY_GENERIC_EVIDENCE_CARRIERS_AS_IMPORTED_CAPABILITIES", "product_ref": "product.assurance_case_appraisal", "library_refs": ["library.lpe.custody-core", "library.lpe.disclosure-core", "library.lpe.evidence-bundle", "library.lpe.record-lifecycle", "library.lpe.signature-envelope"], "finding": "Assurance owns claim-bound admission/appraisal and verdict use of these artifacts, not universal custody, disclosure, bundle, record or cryptographic carrier semantics.", "owner_decision": "UNRATIFIED", "canonical_gaps_closed": 0},
        {"finding_id": "finding.decision_assurance.attestation-seam.v1", "candidate_disposition": "SPLIT_ATTESTATION_APPRAISAL_VERDICT_AND_RELIANCE", "product_ref": "product.assurance_case_appraisal", "library_refs": ["library.lpe.attestation-core", "library.lpe.rats-appraisal", "library.gmo.assurance_appraisal_plan"], "finding": "An attestation is an issuer statement; RATS appraisal produces an attestation result; assurance appraisal produces a bounded verdict; the relying authority independently decides use or action.", "owner_decision": "UNRATIFIED", "canonical_gaps_closed": 0},
        {"finding_id": "finding.decision_assurance.policy-homonym.v1", "candidate_disposition": "SPLIT_POLICY_HOMONYM_INTO_TYPED_POLICY_KINDS", "library_refs": ["library.gmo.policy_model", "library.csp.authority.policy-algebra", "library.data_use_policy.policy_edition"], "finding": "Business-decision, authorization, governance, data-use, appraisal and runtime-control policies have different subjects, results, owners and combining laws; the compiler must never bind them by the word policy.", "owner_decision": "UNRATIFIED", "canonical_gaps_closed": 0},
    ]
    for i, (ref, rationale) in enumerate(VACANCIES, 1):
        rows.append({"finding_id": f"finding.decision_assurance.library-vacancy.{i:02d}", "candidate_disposition": "NEW_LIBRARY_BOUNDARY_CANDIDATE_UNRATIFIED", "proposed_library_ref": ref, "library_refs": [], "finding": rationale, "owner_decision": "UNRATIFIED", "canonical_gaps_closed": 0})
    return rows


def bounded_context() -> dict[str, Any]:
    return {"slice_id": "slice.decision-automation-assurance.v1",
            "retained_products": sorted(PRODUCTS),
            "decision_automation_inside": ["decision requirements and expressions", "tables/rules/hit policies", "static analysis and testing", "editioned compilation and invocation", "total result and trace", "non-authoritative action proposal"],
            "assurance_appraisal_inside": ["claim and argument graph", "criteria binding and appraisal plan", "appraiser occurrence qualification", "evidence admission and quality", "findings, defeaters and challenge", "bounded verdict lifecycle"],
            "imported_owners": ["vertical facts and criteria", "identity/accreditation/mandate authority", "generic custody/signature/disclosure/records/provenance", "authorization and effect execution", "test/runtime implementations", "relying-party acceptance and business action"],
            "non_collapse_summary": "result != proposal != authorization != effect != outcome; claim != evidence != finding != verdict != reliance; signature/custody/transparency != truth; attestation != appraisal; policy homonyms remain typed",
            "product_boundary_candidates": [{"product_ref": p, "status": "RETAIN_BUT_NARROW_UNRATIFIED"} for p in sorted(PRODUCTS)],
            "candidate_new_products": [], "status": "CANDIDATE_UNRATIFIED", "completion_claim": False}


def build() -> dict[str, Any]:
    src = sources(); source_ids = {r["source_id"] for r in src}; mods = modules(); bindings = library_bindings(source_ids)
    axes = [{"library_ref": b["library_ref"], "axis": axis, "semantic_module_refs": b["semantic_module_refs"], "evidence_refs": b["evidence_refs"], "decision_candidate": "UNRESOLVED_RESEARCHED_CANDIDATE", "coordinate_answers": [], "owner_decision": "UNRATIFIED", "canonical_gaps_closed": 0, "completion_claim": False} for b in bindings for axis in AXES]
    result = {"sources": src, "modules": mods, "laws": laws(), "methods": methods(), "experts": experts(), "innovations": innovations(), "libraries": bindings, "axes": axes, "findings": findings(), "context": bounded_context()}
    result["summary"] = {"slice_id": "slice.decision-automation-assurance.v1", "as_of": AS_OF,
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
        "decision-automation-assurance-method-taxonomy.jsonl": "".join(canonical(r) + "\n" for r in b["methods"]),
        "expert-learning-profiles.jsonl": "".join(canonical(r) + "\n" for r in b["experts"]),
        "innovation-records.jsonl": "".join(canonical(r) + "\n" for r in b["innovations"]),
        "library-semantic-bindings.jsonl": "".join(canonical(r) + "\n" for r in b["libraries"]),
        "library-axis-decision-candidates.jsonl": "".join(canonical(r) + "\n" for r in b["axes"]),
        "product-capability-boundary-findings.jsonl": "".join(canonical(r) + "\n" for r in b["findings"]),
        "bounded-context.json": json.dumps(b["context"], ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        "summary.json": json.dumps(b["summary"], ensure_ascii=False, sort_keys=True, indent=2) + "\n"}
    claims = {name: {"bytes": len(value.encode()), "sha256": hashlib.sha256(value.encode()).hexdigest()} for name, value in files.items()}
    files["manifest.json"] = json.dumps({"manifest_id": "manifest.decision-automation-assurance-semantic-slice.v1", "as_of": AS_OF, "files": claims, "completion_claim": False}, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    return files


def main() -> int:
    for name, value in outputs().items():
        (HERE / name).write_text(value)
    summary = build()["summary"]
    print(f"BUILD PASS decision-automation/assurance semantic slice: {summary['semantic_modules']} modules, {summary['method_types']} methods, {summary['bound_libraries']} libraries, {summary['library_axis_decision_candidates']} unresolved axis decisions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
