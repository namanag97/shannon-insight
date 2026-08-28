#!/usr/bin/env python3
"""Iteration-4 challenge: semantic constraints/validity as an orthogonal axis."""
from __future__ import annotations

from iteration3_model import (
    ITERATION3_AXES,
    ITERATION3_CHALLENGES,
    ITERATION3_DEEP_CLAIMS,
    ITERATION3_INTERACTIONS,
    ITERATION3_PRIMARY_SOURCES,
)

ITERATION3_SUMMARY_BLOB_SHA = "878de27a8d808e0416f47c13092ca48789fd0703"
ITERATION3_AXIS_DELTA_BLOB_SHA = "ab526c6d53709a3d3bd042b4d362168b1913b53c"

EXTRA_PRIMARY_SOURCES = [
    {"source_id":"omg_ocl_24","issuer":"Object Management Group","title":"Object Constraint Language 2.4","url":"https://www.omg.org/spec/OCL/2.4/","source_class":"international_standard","retrieved_on":"2026-08-28","status":"PRIMARY_OR_OFFICIAL_CHALLENGE_SOURCE","completion_claim":False},
    {"source_id":"postgresql_18_constraints","issuer":"PostgreSQL Global Development Group","title":"PostgreSQL 18 Data Definition — Constraints","url":"https://www.postgresql.org/docs/18/ddl-constraints.html","source_class":"official_technical_specification","retrieved_on":"2026-08-28","status":"PRIMARY_OR_OFFICIAL_CHALLENGE_SOURCE","completion_claim":False},
    {"source_id":"postgresql_18_create_table","issuer":"PostgreSQL Global Development Group","title":"PostgreSQL 18 CREATE TABLE — Constraint Enforcement and Deferral","url":"https://www.postgresql.org/docs/current/sql-createtable.html","source_class":"official_technical_specification","retrieved_on":"2026-08-28","status":"PRIMARY_OR_OFFICIAL_CHALLENGE_SOURCE","completion_claim":False},
    {"source_id":"w3c_xml11","issuer":"W3C","title":"XML 1.1 Second Edition — Well-formedness and Validity Constraints","url":"https://www.w3.org/TR/xml11/","source_class":"standards_body_recommendation","retrieved_on":"2026-08-28","status":"PRIMARY_OR_OFFICIAL_CHALLENGE_SOURCE","completion_claim":False},
    {"source_id":"w3c_xmlschema11","issuer":"W3C","title":"XML Schema Definition Language 1.1 Part 1: Structures","url":"https://www.w3.org/TR/xmlschema11-1/","source_class":"standards_body_recommendation","retrieved_on":"2026-08-28","status":"PRIMARY_OR_OFFICIAL_CHALLENGE_SOURCE","completion_claim":False},
]

CONSTRAINT_AXIS = {
    "axis":"semantic_constraints_and_validity",
    "question":"What predicates, invariants, preconditions, postconditions, shape/value restrictions and relational constraints define a semantically valid value, state, configuration or operation?",
    "phase":"phase5_behavior_resources_and_proof",
    "facets":[
        {"facet":"invariant","patterns":[r"\b(invariant|must always hold|consistency invariant)\w*\b"],"laws":["an invariant constrains valid semantic states independently of whether it was checked or enforced"]},
        {"facet":"precondition","patterns":[r"\b(precondition|pre-condition|requires before|must hold before)\w*\b"],"laws":["precondition is a validity condition for operation entry, not authorization"]},
        {"facet":"postcondition","patterns":[r"\b(postcondition|post-condition|ensures after|must hold after)\w*\b"],"laws":["postcondition constrains a semantic transition result and is distinct from observed external outcome"]},
        {"facet":"type_or_value_constraint","patterns":[r"\b(check constraint|value constraint|range constraint|enum constraint|pattern constraint|datatype constraint|shape constraint)\w*\b"],"laws":["value/type restrictions are explicit predicates rather than parser success"]},
        {"facet":"relational_or_reference_constraint","patterns":[r"\b(foreign key|referential integrity|relationship constraint|reference constraint|cross.object constraint)\w*\b"],"laws":["relational constraints bind multiple semantic objects/identities and cannot be reduced to local value shape"]},
        {"facet":"uniqueness_or_exclusion_constraint","patterns":[r"\b(unique constraint|uniqueness constraint|exclusion constraint|mutually exclusive|xone)\w*\b"],"laws":["uniqueness/exclusion semantics include an equality/scope profile and are not mere cardinality metadata"]},
        {"facet":"conditional_or_composite_constraint","patterns":[r"\b(if then else|conditional constraint|and constraint|or constraint|not constraint|composite constraint)\w*\b"],"laws":["constraint composition/algebra is explicit and does not inherit normative permission semantics"]},
        {"facet":"constraint_dialect_or_profile","patterns":[r"\b(shacl|json schema|ocl|schema dialect|constraint language|validation vocabulary)\w*\b"],"laws":["constraint meaning is edition/dialect/profile scoped"]},
        {"facet":"enforcement_phase","patterns":[r"\b(deferred constraint|deferrable|not enforced|enforced constraint|check time)\w*\b"],"laws":["constraint existence, enforcement policy and evidence of satisfaction are distinct"]},
        {"facet":"violation_or_refusal","patterns":[r"\b(constraint violation|invalid state|validation failure|precondition failed|invariant violation)\w*\b"],"laws":["constraint violation/refusal is typed and does not silently become a domain breach or security denial"]},
    ],
    "non_collapse":[
        "semantic constraint is not validation evidence",
        "validity predicate is not deontic permission, prohibition or obligation",
        "precondition is not authorization",
        "postcondition is not observed external effect or accepted outcome",
        "parser or representation well-formedness is not semantic validity",
        "constraint definition is not enforcement",
        "constraint enforcement is not proof that all relevant business invariants were modeled",
        "NOT ENFORCED or deferred does not mean satisfied",
        "constraint cardinality is not the same semantic question as grain/cardinality",
        "constraint violation is not automatically a security violation or normative breach",
    ],
    "evidence_refs":["w3c_shacl","jsonschema_core","jsonschema_validation","omg_ocl_24","postgresql_18_constraints","postgresql_18_create_table","w3c_xml11","w3c_xmlschema11","openapi31"],
    "model_verdict":"ADD_RESEARCH_AXIS",
}

ITERATION4_AXES = list(ITERATION3_AXES) + [CONSTRAINT_AXIS]
ITERATION4_PRIMARY_SOURCES = ITERATION3_PRIMARY_SOURCES + EXTRA_PRIMARY_SOURCES
ITERATION4_DEEP_CLAIMS = list(ITERATION3_DEEP_CLAIMS) + [
    {"claim_id":"claim.macro.constraint.assertion-vs-evidence","supports_axis":"semantic_constraints_and_validity","source_refs":["jsonschema_core","jsonschema_validation","w3c_shacl"],"bounded_claim":"Constraint/assertion definitions state conditions an instance/data graph must satisfy, while validation execution produces a separate boolean/report/result artifact.","authority_limit":"JSON Schema and SHACL structural constraints do not establish complete domain semantics or business authority.","negative_twin":"A constraint can exist without ever being executed, and a successful validation report only proves the constraints that were actually declared and evaluated.","status":"BOUNDED_RESEARCH_CLAIM_NOT_AUTHORITY","completion_claim":False},
    {"claim_id":"claim.macro.constraint.invariant-pre-post","supports_axis":"semantic_constraints_and_validity","source_refs":["omg_ocl_24"],"bounded_claim":"OCL distinguishes invariant constraints from operation preconditions and postconditions, giving them different semantic scopes and evaluation times.","authority_limit":"OCL constrains UML/model instances and operations; it does not prove runtime enforcement or business authorization.","negative_twin":"An operation can be authorized yet invalid because its semantic precondition is false, or execute while later violating a postcondition.","status":"BOUNDED_RESEARCH_CLAIM_NOT_AUTHORITY","completion_claim":False},
    {"claim_id":"claim.macro.constraint.relational-integrity","supports_axis":"semantic_constraints_and_validity","source_refs":["postgresql_18_constraints","postgresql_18_create_table"],"bounded_claim":"Relational systems distinguish CHECK, UNIQUE, PRIMARY KEY, FOREIGN KEY and EXCLUSION constraints, including relation-spanning referential integrity and different enforcement semantics.","authority_limit":"Database constraints enforce declared storage predicates, not all application/domain invariants.","negative_twin":"A database can satisfy every declared foreign key and check constraint while violating a business invariant that was never encoded.","status":"BOUNDED_RESEARCH_CLAIM_NOT_AUTHORITY","completion_claim":False},
    {"claim_id":"claim.macro.constraint.definition-enforcement","supports_axis":"semantic_constraints_and_validity","source_refs":["postgresql_18_create_table","w3c_shacl"],"bounded_claim":"Constraint definition and constraint enforcement/validation are distinct. PostgreSQL permits deferrable and selected NOT ENFORCED constraints; SHACL separately defines shapes and validation processing/results.","authority_limit":"These systems have different enforcement models and do not establish one universal enforcement mechanism.","negative_twin":"A documented NOT ENFORCED constraint can define intended validity while current stored data violates it.","status":"BOUNDED_RESEARCH_CLAIM_NOT_AUTHORITY","completion_claim":False},
    {"claim_id":"claim.macro.constraint.wellformed-valid","supports_axis":"semantic_constraints_and_validity","source_refs":["w3c_xml11","w3c_xmlschema11","jsonschema_core"],"bounded_claim":"Well-formed representation and validity against declared constraints are distinct notions; a syntactically well-formed document may fail validity constraints.","authority_limit":"Representation/schema validity still does not imply domain truth or acceptance.","negative_twin":"A well-formed XML or JSON document can be invalid against its schema or semantically wrong despite schema validity.","status":"BOUNDED_RESEARCH_CLAIM_NOT_AUTHORITY","completion_claim":False},
    {"claim_id":"claim.macro.constraint.dialect-profile","supports_axis":"semantic_constraints_and_validity","source_refs":["jsonschema_core","jsonschema_validation","openapi31","w3c_shacl"],"bounded_claim":"Constraint semantics are scoped by declared schema vocabulary/dialect/profile and extensions; the same serialized keyword/token cannot be interpreted outside its declared constraint language context.","authority_limit":"Schema dialect selection does not establish domain-owner ratification or compatibility with another constraint system.","negative_twin":"A custom or optional vocabulary keyword can be ignored or interpreted differently by processors that do not support the same dialect/profile.","status":"BOUNDED_RESEARCH_CLAIM_NOT_AUTHORITY","completion_claim":False},
]
ITERATION4_CHALLENGES = list(ITERATION3_CHALLENGES) + [
    {"challenge_id":"macro.semantic-constraint-validity","candidate":"semantic_constraints_and_validity","verdict":"ADD_RESEARCH_AXIS","reason":"Normativity states what an actor is permitted/required to do; evidence/conformance states what observation proves conformance. Constraint semantics instead define the predicates that make values, states, relations or operation boundaries valid. SHACL, JSON Schema, OCL and relational constraints independently preserve that distinction.","counterfactual":"If validity constraints were reducible to normativity or evidence, an invariant/precondition could be replaced by an obligation record or a test receipt without changing semantics; primary standards explicitly separate the constraint from validation/enforcement/reporting.","source_refs":["w3c_shacl","jsonschema_validation","omg_ocl_24","postgresql_18_constraints","postgresql_18_create_table"]},
]
ITERATION4_INTERACTIONS = list(ITERATION3_INTERACTIONS) + [
    {"from_axis":"semantic_constraints_and_validity","to_axis":"evidence_and_conformance","relation":"REQUIRES_WITHOUT_COLLAPSE","law":"constraints define validity predicates; validation/conformance evidence records whether and how those predicates were evaluated"},
    {"from_axis":"semantic_constraints_and_validity","to_axis":"normativity_and_obligation","relation":"ORTHOGONAL","law":"domain/model invariants and preconditions constrain valid semantic states; deontic norms constrain permitted/prohibited/required conduct"},
    {"from_axis":"semantic_constraints_and_validity","to_axis":"representation","relation":"REQUIRES_WITHOUT_COLLAPSE","law":"constraint languages and schemas are representations of predicates; representation well-formedness is not satisfaction of the represented constraint"},
    {"from_axis":"semantic_constraints_and_validity","to_axis":"authority_and_trust","relation":"REQUIRES_WITHOUT_COLLAPSE","law":"an authority may issue or ratify constraints, but authority identity does not determine the predicate itself or prove its satisfaction"},
    {"from_axis":"semantic_constraints_and_validity","to_axis":"state_and_change","relation":"USES_WITHOUT_COLLAPSE","law":"invariants/pre/postconditions can constrain states/transitions, while state occurrence does not imply the relevant constraints were complete or enforced"},
    {"from_axis":"semantic_constraints_and_validity","to_axis":"effect_boundary","relation":"ORTHOGONAL","law":"operation/effect preconditions constrain whether a transition/effect is semantically admissible; authorization/execution/outcome remain separate"},
    {"from_axis":"semantic_constraints_and_validity","to_axis":"identity_and_equality","relation":"USES_WITHOUT_COLLAPSE","law":"unique/reference constraints depend on explicit equality and identity profiles; equality semantics alone does not state the constraint"},
    {"from_axis":"semantic_constraints_and_validity","to_axis":"grain_and_cardinality","relation":"USES_WITHOUT_COLLAPSE","law":"cardinality limits can be constraint predicates, but grain/cardinality also define semantic population shape independently of whether a limit is imposed"},
]
ITERATION4_CORRECTIONS = [
    {"correction_id":"correction.iter4.constraint-vs-conformance","problem":"The prior 24-axis model could describe conformance evidence and normative duties but lacked a first-class semantic question for invariants, preconditions, postconditions and validity predicates themselves.","new_axis":"semantic_constraints_and_validity","required_test":"the new axis must have independent primary-source support from at least four issuers, a nonempty 682-library candidate surface, complete unresolved routing, and explicit non-collapse relations to evidence/conformance and normativity","status":"CORRECTION_REQUIRED","completion_claim":False}
]
