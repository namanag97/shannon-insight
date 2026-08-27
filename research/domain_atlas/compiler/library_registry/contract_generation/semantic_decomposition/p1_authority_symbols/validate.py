#!/usr/bin/env python3
"""Validate P1 authority and symbol packets without granting decisions."""
from __future__ import annotations

import hashlib
import json

from build_p1 import ARCHETYPE_REFINEMENT_SOURCES, ARCHETYPE_SEMANTIC_AXES, EVIDENCE_LANE_EXACT_ARCHETYPES, HERE, MEASURE_LANE_EXACT_ARCHETYPES, OCCURRENCE_REFINEMENTS, POLICY_LANE_EXACT_ARCHETYPES, PRIMARY_RESEARCHED_ARCHETYPE_IDS, PRIMARY_SOURCES, analytical_result_classification_candidates, archetype_ontology, archetype_research_programs, authority_archetype_research, authority_contract_classification_candidates, capability_port_archetype_research, capability_port_classification_candidates, catchall_refinement_candidates, catchall_refinement_research, evidence_and_analytical_result_archetype_research, evidence_contract_classification_candidates, evidence_lane_refinement_candidates, failure_archetype_research, failure_contract_classification_candidates, high_fanout_research, identity_archetype_research, identity_contract_classification_candidates, measure_archetype_research, measure_contract_classification_candidates, measure_lane_refinement_candidates, model_artifact_archetype_research, model_artifact_contract_classification_candidates, occurrence_applicability, operation_archetype_research, operation_contract_classification_candidates, outputs, policy_archetype_research, policy_contract_classification_candidates, policy_lane_refinement_candidates, remaining_symbol_research_batches, representation_archetype_research, representation_contract_classification_candidates, resource_archetype_research, resource_contract_classification_candidates, shape_archetype_research, shape_contract_classification_candidates, source_packets, symbol_packets, time_archetype_research, time_contract_classification_candidates, work_waves


def main() -> int:
    assert __import__("subprocess").run([__import__("sys").executable, str(HERE / "build_p1.py"), "--check"], capture_output=True).returncode == 0
    manifest = json.loads((HERE / "manifest.json").read_text())
    for name, claim in manifest["files"].items():
        data = (HERE / name).read_bytes(); assert len(data) == claim["bytes"] and hashlib.sha256(data).hexdigest() == claim["sha256"], name
    summary = json.loads((HERE / "summary.json").read_text())
    assert summary["total_symbol_packets_with_bounded_primary_research"] == 210
    assert summary["archetype_researched_symbol_packets"] == 191
    assert summary["remaining_unresearched_symbol_packets"] == 0
    assert summary["remaining_unratified_symbol_packets"] == 191
    assert summary["residual_batched_unratified_symbol_packets"] == 191
    assert summary["total_owner_unratified_symbol_packets"] == 210
    assert summary["total_owner_unratified_symbol_occurrences"] == 666
    assert summary["remaining_open_primary_research_archetypes"] == 0
    assert summary["next_primary_research_archetype"] is None
    sources = source_packets(); symbols = symbol_packets(); waves = work_waves(symbols)
    research = high_fanout_research(symbols)
    applicability = occurrence_applicability(research)
    remaining_batches = remaining_symbol_research_batches(symbols, research)
    research_programs = archetype_research_programs(remaining_batches, sources)
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
    assert len(sources) == 23 and all(not row["structural_controls_missing"] for row in sources)
    assert all(row["decision"] == "UNRESOLVED" and row["status"] == "DECISION_PACKET_READY_AUTHORITY_UNRESOLVED" for row in sources)
    assert len(symbols) == 210 and [row["priority_rank"] for row in symbols] == list(range(1, 211))
    assert all(row["decision"] == "UNRESOLVED" and row["definition_evidence_strength"] == "LEXICAL_AND_STRUCTURAL_CANDIDATE_ONLY" for row in symbols)
    assert all(row["status"] == "ADJUDICATION_PACKET_READY_NO_SYMBOL_UNIFICATION" for row in symbols)
    packet_refs = {row["packet_id"] for row in symbols}
    assert {ref for wave in waves for ref in wave["packet_refs"]} == packet_refs
    assert sum(len(wave["packet_refs"]) for wave in waves) == len(symbols)
    source_ids = {row["source_id"] for row in PRIMARY_SOURCES}
    assert len(source_ids) == len(PRIMARY_SOURCES)
    authority_source_refs = ARCHETYPE_REFINEMENT_SOURCES["AUTHORITY_SECURITY_AND_CREDENTIAL"]
    assert len(authority_source_refs) == len(set(authority_source_refs)) == 11
    assert {"source.p1.nist.sp800-63-4", "source.p1.nist.sp800-162-abac", "source.p1.rfc6749.oauth2", "source.p1.spiffe.id"} <= set(authority_source_refs)
    representation_source_refs = ARCHETYPE_REFINEMENT_SOURCES["REPRESENTATION_CODEC_SCHEMA_AND_LAYOUT"]
    assert len(representation_source_refs) == len(set(representation_source_refs)) == 11
    resource_source_refs = ARCHETYPE_REFINEMENT_SOURCES["RESOURCE_BOUND_CAPACITY_AND_SCHEDULING"]
    assert len(resource_source_refs) == len(set(resource_source_refs)) == 6
    shape_source_refs = ARCHETYPE_REFINEMENT_SOURCES["SHAPE_TOPOLOGY_VIEW_AND_PROCESS"]
    assert len(shape_source_refs) == len(set(shape_source_refs)) == 9
    assert {"source.p1.rfc7946.geojson", "source.p1.ogc.sfa-1-2-1", "source.p1.nist.randomized-block-design", "source.p1.kernighan-lin.graph-partition", "source.p1.substrait.distribution", "source.p1.libpysal.spatial-weights"} <= set(shape_source_refs)
    assert len(research) == 19 and all(set(row["source_refs"]) <= source_ids and row["decision"] == "UNRESOLVED" for row in research)
    assert {row["symbol_ref"] for row in research} >= {"type.assignmentcut", "type.exposurecut", "type.metriccut", "type.evaluationscope", "type.policyedition", "type.evidencereceipt", "type.qualityrefusal"}
    assert all(row["non_collapse_laws"] and row["negative_twins"] and row["candidate_carrier_fields"] for row in research)
    assert {row["symbol_ref"] for row in research} == {
        "type.protocoledition",
        "type.contentdigest",
        "type.compatibility",
        "type.lease",
        "type.cancellationrequest",
        "type.lossreport",
        "trait.capabilityrequirement",
        "trait.capabilityoffer",
        "trait.conformanceoracle",
        "type.assignmentcut",
        "type.exposurecut",
        "type.metriccut",
        "type.evaluationscope",
        "type.policyedition",
        "type.evidencereceipt",
        "type.qualityrefusal",
        "type.graphview",
        "type.eventlogview",
        "type.processmodel",
    }
    expected_occurrences = {
        (row["symbol_ref"], occurrence["library_ref"])
        for row in research
        for occurrence in row["affected_occurrences"]
    }
    actual_occurrences = {(row["symbol_ref"], row["library_ref"]) for row in applicability}
    assert len(applicability) == len(actual_occurrences) == 268
    assert expected_occurrences == actual_occurrences
    assert set(OCCURRENCE_REFINEMENTS) < actual_occurrences
    assert sum(row["symbol_ref"].startswith("trait.") for row in applicability) == 81
    assert sum(row["symbol_ref"] == "type.evaluationscope" for row in applicability) == 37
    assert sum(row["symbol_ref"] == "type.policyedition" for row in applicability) == 37
    assert sum(row["symbol_ref"] == "type.evidencereceipt" for row in applicability) == 37
    assert sum(row["symbol_ref"] == "type.qualityrefusal" for row in applicability) == 37
    assert sum(row["symbol_ref"] == "type.graphview" for row in applicability) == 5
    assert sum(row["symbol_ref"] == "type.eventlogview" for row in applicability) == 4
    assert sum(row["symbol_ref"] == "type.processmodel" for row in applicability) == 4
    assert all(
        row["library_ref"].startswith("library.qor.")
        and row["qualified_public_name_candidate"] in {"QualityEvaluationScope", "QualityPolicyEdition", "QualityEvaluationEvidenceRecord", "QualityOperationRefusal"}
        and row["local_profile_ref"].startswith("profile.qor.")
        for row in applicability
        if row["symbol_ref"] in {"type.evaluationscope", "type.policyedition", "type.evidencereceipt", "type.qualityrefusal"}
    )
    assert all(row["local_residual_requirements"] and row["shared_non_collapse_laws"] for row in applicability)
    assert all(row["decision"] == "UNRESOLVED" and row["status"] == "CANDIDATE_UNRATIFIED_OWNER_DECISION_REQUIRED" for row in applicability)
    assert all(row["applicability_candidate"] != "APPLIES_AS_IS" for row in applicability)
    assert all(set(row["source_refs"]) <= source_ids for row in applicability)
    researched_packet_refs = {row["symbol_packet_ref"] for row in research}
    remaining_packet_refs = [ref for batch in remaining_batches for ref in batch["packet_refs"]]
    assert len(remaining_batches) > 0
    assert len(remaining_packet_refs) == len(set(remaining_packet_refs)) == 191
    assert researched_packet_refs.isdisjoint(remaining_packet_refs)
    assert researched_packet_refs | set(remaining_packet_refs) == packet_refs
    assert sum(batch["packet_count"] for batch in remaining_batches) == 191
    assert all(batch["packet_count"] == len(batch["packet_refs"]) == len(batch["symbol_refs"]) for batch in remaining_batches)
    assert all(batch["required_evidence_classes"] and batch["required_outputs"] for batch in remaining_batches)
    assert all(batch["classification_basis"] == "LEXICAL_AND_STRUCTURAL_ROUTING_ONLY_NOT_A_SEMANTIC_DECISION" for batch in remaining_batches)
    assert {batch["research_state"] for batch in remaining_batches} == {"BOUNDED_PRIMARY_RESEARCH_COMPLETE"}
    open_primary_batches = [batch for batch in remaining_batches if batch["research_state"] == "OPEN_PRIMARY_RESEARCH"]
    assert sum(batch["packet_count"] for batch in open_primary_batches) == 0
    assert sum(batch["represented_occurrence_count"] for batch in open_primary_batches) == 0
    assert {batch["research_archetype"] for batch in open_primary_batches} == set()
    assert sum(batch["packet_count"] for batch in remaining_batches if batch["research_state"] == "BOUNDED_PRIMARY_RESEARCH_COMPLETE") == 191
    assert all((batch["research_archetype"] in PRIMARY_RESEARCHED_ARCHETYPE_IDS) == (batch["research_state"] == "BOUNDED_PRIMARY_RESEARCH_COMPLETE") for batch in remaining_batches)
    ontology = archetype_ontology()
    ontology_ids = {row["archetype_id"] for row in ontology["archetypes"]}
    assert {batch["research_archetype"] for batch in remaining_batches} <= ontology_ids
    assert len(ontology_ids) == len(ARCHETYPE_SEMANTIC_AXES) == 18
    assert len(research_programs) == 17
    assert {row["archetype_id"] for row in research_programs} == ontology_ids - {"GENERAL_SEMANTIC_OWNER_DISCOVERY"}
    assert all(row["research_archetype"] != "GENERAL_SEMANTIC_OWNER_DISCOVERY" for row in remaining_batches)
    program_batches = [ref for row in research_programs for ref in row["batch_refs"]]
    assert len(program_batches) == len(set(program_batches)) == len(remaining_batches)
    assert set(program_batches) == {row["batch_id"] for row in remaining_batches}
    program_packets = [ref for row in research_programs for ref in row["packet_refs"]]
    assert len(program_packets) == len(set(program_packets)) == 191
    assert set(program_packets) == set(remaining_packet_refs)
    assert sum(row["represented_occurrence_count"] for row in research_programs) == sum(row["represented_occurrence_count"] for row in remaining_batches)
    assert sum(len(row["semantic_axis_refs"]) for row in research_programs) == 157
    assert all(row["decision_grain"] == "PER_SYMBOL_PACKET_AND_PER_OCCURRENCE" and not row["completion_claim"] for row in research_programs)
    assert all(len(row["source_authority_packet_refs"]) == len(row["family_refs"]) for row in research_programs)
    assert sum(row["symbol_packet_count"] for row in research_programs if row["research_state"] == "OPEN_PRIMARY_RESEARCH") == 0
    assert all((row["archetype_id"] in PRIMARY_RESEARCHED_ARCHETYPE_IDS) == (row["research_state"] == "BOUNDED_PRIMARY_RESEARCH_COMPLETE") for row in research_programs)
    assert len(archetype_research) == 17
    assert {row["archetype_id"] for row in archetype_research} == {"OPERATION_BOUNDARY_AND_EFFECT", "DOMAIN_CONTRACT_AND_ADAPTER_BOUNDARY", "ACTIVITY_EVENT_AND_AUDIT_OCCURRENCE", "CRYPTOGRAPHIC_SUITE_PERIOD_AND_AGILITY", "CAPABILITY_PORT_AND_CONFORMANCE", "POLICY_SCOPE_PROFILE_AND_EDITION", "IDENTITY_REFERENCE_VERSION_AND_DIGEST", "AUTHORITY_SECURITY_AND_CREDENTIAL", "TIME_LIFECYCLE_AND_CONTROL", "REPRESENTATION_CODEC_SCHEMA_AND_LAYOUT", "RESOURCE_BOUND_CAPACITY_AND_SCHEDULING", "SHAPE_TOPOLOGY_VIEW_AND_PROCESS", "MEASURE_QUALITY_COMPARISON_AND_FORMULA", "FAILURE_REFUSAL_AND_PARTIALITY", "ANALYTICAL_MODEL_ARTIFACT_AND_STATE", "EVIDENCE_RECEIPT_APPRAISAL_AND_RESULT", "ANALYTICAL_METHOD_RESULT_AND_DIAGNOSTIC"}
    assert all(set(row["source_refs"]) <= source_ids and row["decision"] == "UNRESOLVED" for row in archetype_research)
    assert len(operation_candidates) == 73
    assert sum(row["represented_occurrence_count"] for row in operation_candidates) == 152
    assert len({row["operation_ref"] for row in operation_candidates}) == 73
    assert all(row["candidate_semantic_role"] and row["candidate_effect_posture"] and row["decision"] == "UNRESOLVED" for row in operation_candidates)
    assert all(row["retry_and_idempotency_posture"].startswith("UNRESOLVED") for row in operation_candidates)
    assert {row["symbol_packet_ref"] for row in operation_candidates} == {ref for batch in remaining_batches if batch["research_archetype"] == "OPERATION_BOUNDARY_AND_EFFECT" for ref in batch["packet_refs"]}
    assert len(catchall_refinements) == 47 and sum(row["represented_occurrence_count"] for row in catchall_refinements) == 98
    assert len({row["symbol_ref"] for row in catchall_refinements}) == 47
    assert all(row["candidate_archetype"] != "GENERAL_SEMANTIC_OWNER_DISCOVERY" and set(row["source_refs"]) <= source_ids for row in catchall_refinements)
    assert len(capability_candidates) == 20 and sum(row["represented_occurrence_count"] for row in capability_candidates) == 40
    assert len({row["symbol_ref"] for row in capability_candidates}) == 20
    assert {row["symbol_packet_ref"] for row in capability_candidates} == {ref for batch in remaining_batches if batch["research_archetype"] == "CAPABILITY_PORT_AND_CONFORMANCE" for ref in batch["packet_refs"]}
    assert all(row["candidate_port_role"] and row["binding_posture"].startswith("UNBOUND") and row["decision"] == "UNRESOLVED" for row in capability_candidates)
    assert len(policy_lane_refinements) == len(POLICY_LANE_EXACT_ARCHETYPES) == 24
    assert sum(row["represented_occurrence_count"] for row in policy_lane_refinements) == 52
    assert {row["symbol_ref"] for row in policy_lane_refinements} == set(POLICY_LANE_EXACT_ARCHETYPES)
    assert all(row["candidate_archetype"] == POLICY_LANE_EXACT_ARCHETYPES[row["symbol_ref"]] and row["decision"] == "UNRESOLVED" for row in policy_lane_refinements)
    assert len(policy_candidates) == 18 and sum(row["represented_occurrence_count"] for row in policy_candidates) == 40
    assert len({row["symbol_ref"] for row in policy_candidates}) == 18
    assert {row["symbol_packet_ref"] for row in policy_candidates} == {ref for batch in remaining_batches if batch["research_archetype"] == "POLICY_SCOPE_PROFILE_AND_EDITION" for ref in batch["packet_refs"]}
    assert all(row["candidate_policy_role"] and row["activation_posture"].startswith("UNBOUND") and row["decision"] == "UNRESOLVED" for row in policy_candidates)
    quality_rule = next(row for row in policy_candidates if row["symbol_ref"] == "type.qualityrule")
    assert quality_rule["candidate_policy_role"] == "QUALITY_EVALUATION_RULE_SPECIFICATION"
    assert len({row["candidate_policy_profile"] for row in quality_rule["occurrence_profile_candidates"]}) == 2
    assert len(identity_candidates) == 11 and sum(row["represented_occurrence_count"] for row in identity_candidates) == 22
    assert {row["symbol_packet_ref"] for row in identity_candidates} == {ref for batch in remaining_batches if batch["research_archetype"] == "IDENTITY_REFERENCE_VERSION_AND_DIGEST" for ref in batch["packet_refs"]}
    assert all(row["candidate_identity_role"] and row["candidate_disposition_hypothesis"] and row["decision"] == "UNRESOLVED" for row in identity_candidates)
    object_identity = next(row for row in identity_candidates if row["symbol_ref"] == "type.objectidentity")
    assert object_identity["candidate_disposition_hypothesis"] == "QUALIFY_LOCAL_SYMBOL_IDS"
    assert len({row["candidate_identity_profile"] for row in object_identity["occurrence_profile_candidates"]}) == 2
    assert len(authority_candidates) == 10 and sum(row["represented_occurrence_count"] for row in authority_candidates) == 20
    assert {row["symbol_packet_ref"] for row in authority_candidates} == {ref for batch in remaining_batches if batch["research_archetype"] == "AUTHORITY_SECURITY_AND_CREDENTIAL" for ref in batch["packet_refs"]}
    assert all(row["candidate_authority_role"] and row["candidate_disposition_hypothesis"] and row["decision"] == "UNRESOLVED" for row in authority_candidates)
    fencing = next(row for row in authority_candidates if row["symbol_ref"] == "type.fencingtoken")
    assert fencing["candidate_disposition_hypothesis"] == "CANONICAL_SHARED_OWNER_AND_IMPORTS"
    assert len({row["candidate_authority_profile"] for row in fencing["occurrence_profile_candidates"]}) == 2
    assert len(representation_candidates) == 7 and sum(row["represented_occurrence_count"] for row in representation_candidates) == 14
    assert {row["symbol_packet_ref"] for row in representation_candidates} == {ref for batch in remaining_batches if batch["research_archetype"] == "REPRESENTATION_CODEC_SCHEMA_AND_LAYOUT" for ref in batch["packet_refs"]}
    assert all(row["candidate_representation_role"] and row["candidate_disposition_hypothesis"] and row["decision"] == "UNRESOLVED" for row in representation_candidates)
    assert {row["symbol_ref"] for row in representation_candidates} == {"type.documentview", "type.decoderesult", "type.encoderesult", "type.frame", "type.formulaast", "type.manifest", "type.attribute_bag"}
    manifest = next(row for row in representation_candidates if row["symbol_ref"] == "type.manifest")
    assert manifest["candidate_disposition_hypothesis"] == "QUALIFY_LOCAL_SYMBOL_IDS"
    assert len({row["candidate_representation_profile"] for row in manifest["occurrence_profile_candidates"]}) == 2
    formula_ast = next(row for row in representation_candidates if row["symbol_ref"] == "type.formulaast")
    assert formula_ast["candidate_disposition_hypothesis"] == "CANONICAL_SHARED_OWNER_AND_IMPORTS"
    assert len({row["candidate_representation_profile"] for row in formula_ast["occurrence_profile_candidates"]}) == 2
    frame = next(row for row in representation_candidates if row["symbol_ref"] == "type.frame")
    assert frame["candidate_disposition_hypothesis"] == "CANONICAL_SHARED_OWNER_AND_PROFILED_IMPORTS"
    assert len({row["candidate_representation_profile"] for row in frame["occurrence_profile_candidates"]}) == 2
    assert all(len({profile["candidate_representation_profile"] for profile in row["occurrence_profile_candidates"]}) == 2 for row in representation_candidates)
    assert len(resource_candidates) == 3 and sum(row["represented_occurrence_count"] for row in resource_candidates) == 6
    assert {row["symbol_packet_ref"] for row in resource_candidates} == {ref for batch in remaining_batches if batch["research_archetype"] == "RESOURCE_BOUND_CAPACITY_AND_SCHEDULING" for ref in batch["packet_refs"]}
    assert {row["symbol_ref"] for row in resource_candidates} == {"trait.reserve", "type.buffer", "type.resourcebudget"}
    assert all(row["candidate_resource_role"] and row["candidate_disposition_hypothesis"] and row["decision"] == "UNRESOLVED" for row in resource_candidates)
    reserve = next(row for row in resource_candidates if row["symbol_ref"] == "trait.reserve")
    buffer = next(row for row in resource_candidates if row["symbol_ref"] == "type.buffer")
    budget = next(row for row in resource_candidates if row["symbol_ref"] == "type.resourcebudget")
    assert reserve["candidate_disposition_hypothesis"] == buffer["candidate_disposition_hypothesis"] == "QUALIFY_LOCAL_SYMBOL_IDS"
    assert budget["candidate_disposition_hypothesis"] == "FAMILY_SHARED_OWNER_AND_IMPORTS"
    assert all(len({profile["candidate_resource_profile"] for profile in row["occurrence_profile_candidates"]}) == 2 for row in resource_candidates)
    assert len(shape_candidates) == 7 and sum(row["represented_occurrence_count"] for row in shape_candidates) == 15
    assert {row["symbol_packet_ref"] for row in shape_candidates} == {ref for batch in remaining_batches if batch["research_archetype"] == "SHAPE_TOPOLOGY_VIEW_AND_PROCESS" for ref in batch["packet_refs"]}
    assert {row["symbol_ref"] for row in shape_candidates} == {"trait.partition", "type.block", "type.geometry", "type.layoutprofile", "type.page", "type.region", "type.spatialweights"}
    assert all(row["candidate_shape_role"] and row["candidate_disposition_hypothesis"] and row["decision"] == "UNRESOLVED" for row in shape_candidates)
    shape_by_symbol = {row["symbol_ref"]: row for row in shape_candidates}
    assert all(shape_by_symbol[ref]["candidate_disposition_hypothesis"] == "QUALIFY_LOCAL_SYMBOL_IDS" for ref in {"trait.partition", "type.block", "type.layoutprofile", "type.page"})
    assert all(shape_by_symbol[ref]["candidate_disposition_hypothesis"] == "FAMILY_SHARED_OWNER_AND_IMPORTS" for ref in {"type.geometry", "type.region", "type.spatialweights"})
    assert all(len({profile["candidate_shape_profile"] for profile in row["occurrence_profile_candidates"]}) == row["represented_occurrence_count"] for row in shape_candidates)
    assert len(measure_lane_refinements) == len(MEASURE_LANE_EXACT_ARCHETYPES) == 6
    assert sum(row["represented_occurrence_count"] for row in measure_lane_refinements) == 13
    assert {row["symbol_ref"] for row in measure_lane_refinements} == set(MEASURE_LANE_EXACT_ARCHETYPES)
    assert all(row["candidate_archetype"] == MEASURE_LANE_EXACT_ARCHETYPES[row["symbol_ref"]] and row["decision"] == "UNRESOLVED" for row in measure_lane_refinements)
    assert len(measure_candidates) == 3 and sum(row["represented_occurrence_count"] for row in measure_candidates) == 6
    assert {row["symbol_ref"] for row in measure_candidates} == {"trait.dimensionalgebracontract", "type.dimensionalgebrainput", "type.bound"}
    assert {row["symbol_packet_ref"] for row in measure_candidates} == {ref for batch in remaining_batches if batch["research_archetype"] == "MEASURE_QUALITY_COMPARISON_AND_FORMULA" for ref in batch["packet_refs"]}
    assert all(row["candidate_measure_role"] and row["candidate_disposition_hypothesis"] and row["decision"] == "UNRESOLVED" for row in measure_candidates)
    bound = next(row for row in measure_candidates if row["symbol_ref"] == "type.bound")
    assert bound["candidate_disposition_hypothesis"] == "QUALIFY_LOCAL_SYMBOL_IDS"
    assert len({row["candidate_measure_profile"] for row in bound["occurrence_profile_candidates"]}) == 2
    assert all(row["candidate_disposition_hypothesis"] == "CANONICAL_SHARED_OWNER_AND_IMPORTS" for row in measure_candidates if row["symbol_ref"] != "type.bound")
    assert len(time_candidates) == 5 and sum(row["represented_occurrence_count"] for row in time_candidates) == 10
    assert {row["symbol_ref"] for row in time_candidates} == {"type.forecastorigin", "type.forecasthorizon", "type.disposition_due", "type.event_time", "type.retraction"}
    assert {row["symbol_packet_ref"] for row in time_candidates} == {ref for batch in remaining_batches if batch["research_archetype"] == "TIME_LIFECYCLE_AND_CONTROL" for ref in batch["packet_refs"]}
    assert all(row["candidate_time_role"] and row["candidate_disposition_hypothesis"] and row["decision"] == "UNRESOLVED" for row in time_candidates)
    retraction = next(row for row in time_candidates if row["symbol_ref"] == "type.retraction")
    assert retraction["candidate_disposition_hypothesis"] == "QUALIFY_LOCAL_SYMBOL_IDS"
    assert len({row["candidate_time_profile"] for row in retraction["occurrence_profile_candidates"]}) == 2
    assert all(row["candidate_disposition_hypothesis"] == "FAMILY_SHARED_OWNER_AND_IMPORTS" for row in time_candidates if row["symbol_ref"] != "type.retraction")
    event_time = next(row for row in time_candidates if row["symbol_ref"] == "type.event_time")
    assert len({row["candidate_time_profile"] for row in event_time["occurrence_profile_candidates"]}) == 2
    assert len(failure_candidates) == 3 and sum(row["represented_occurrence_count"] for row in failure_candidates) == 6
    assert {row["symbol_ref"] for row in failure_candidates} == {"type.canonicalizationerror", "type.dimensionalgebraerror", "type.publicationprofilerefusal"}
    assert {row["symbol_packet_ref"] for row in failure_candidates} == {ref for batch in remaining_batches if batch["research_archetype"] == "FAILURE_REFUSAL_AND_PARTIALITY" for ref in batch["packet_refs"]}
    assert all(row["candidate_failure_role"] and row["candidate_disposition_hypothesis"] and row["decision"] == "UNRESOLVED" for row in failure_candidates)
    assert next(row for row in failure_candidates if row["symbol_ref"] == "type.dimensionalgebraerror")["candidate_disposition_hypothesis"] == "CANONICAL_SHARED_OWNER_AND_IMPORTS"
    assert all(len({profile["candidate_failure_profile"] for profile in row["occurrence_profile_candidates"]}) == 2 for row in failure_candidates)
    assert len(model_artifact_candidates) == 2 and sum(row["represented_occurrence_count"] for row in model_artifact_candidates) == 4
    assert {row["symbol_ref"] for row in model_artifact_candidates} == {"type.baselineartifact", "type.fittedforecaster"}
    assert {row["symbol_packet_ref"] for row in model_artifact_candidates} == {ref for batch in remaining_batches if batch["research_archetype"] == "ANALYTICAL_MODEL_ARTIFACT_AND_STATE" for ref in batch["packet_refs"]}
    assert all(row["candidate_model_artifact_role"] and row["candidate_disposition_hypothesis"] == "FAMILY_SHARED_OWNER_AND_IMPORTS" and row["candidate_owner_hypothesis"] and row["decision"] == "UNRESOLVED" for row in model_artifact_candidates)
    assert all(len({profile["candidate_model_artifact_profile"] for profile in row["occurrence_profile_candidates"]}) == 2 for row in model_artifact_candidates)
    baseline = next(row for row in model_artifact_candidates if row["symbol_ref"] == "type.baselineartifact")
    fitted_forecaster = next(row for row in model_artifact_candidates if row["symbol_ref"] == "type.fittedforecaster")
    assert baseline["candidate_owner_hypothesis"] == "library.method_kernels.anomaly_baseline"
    assert fitted_forecaster["candidate_owner_hypothesis"] == "library.method_kernels.forecast_estimators"
    routing = {"ANALYTICAL_MODEL_ARTIFACT_AND_STATE": set(), "TIME_LIFECYCLE_AND_CONTROL": set()}
    for batch in remaining_batches:
        if batch["research_archetype"] in routing:
            routing[batch["research_archetype"]].update(batch["symbol_refs"])
    assert {"type.baselineartifact", "type.fittedforecaster"} <= routing["ANALYTICAL_MODEL_ARTIFACT_AND_STATE"]
    assert {"type.forecasthorizon", "type.forecastorigin"} <= routing["TIME_LIFECYCLE_AND_CONTROL"]
    routed_symbols = {batch["research_archetype"]: set() for batch in remaining_batches}
    for batch in remaining_batches:
        routed_symbols[batch["research_archetype"]].update(batch["symbol_refs"])
    assert {"type.block", "type.page"} <= routed_symbols["SHAPE_TOPOLOGY_VIEW_AND_PROCESS"]
    assert {"trait.dimensionalgebracontract", "type.dimensionalgebrainput", "type.bound"} <= routed_symbols["MEASURE_QUALITY_COMPARISON_AND_FORMULA"]
    assert "type.frame" in routed_symbols["REPRESENTATION_CODEC_SCHEMA_AND_LAYOUT"]
    assert len(evidence_lane_refinements) == len(EVIDENCE_LANE_EXACT_ARCHETYPES) == 19
    assert sum(row["represented_occurrence_count"] for row in evidence_lane_refinements) == 38
    assert {row["symbol_ref"] for row in evidence_lane_refinements} == set(EVIDENCE_LANE_EXACT_ARCHETYPES)
    assert all(row["candidate_archetype"] == EVIDENCE_LANE_EXACT_ARCHETYPES[row["symbol_ref"]] and row["decision"] == "UNRESOLVED" for row in evidence_lane_refinements)
    assert len(evidence_candidates) == 6 and sum(row["represented_occurrence_count"] for row in evidence_candidates) == 12
    assert {row["symbol_packet_ref"] for row in evidence_candidates} == {ref for batch in remaining_batches if batch["research_archetype"] == "EVIDENCE_RECEIPT_APPRAISAL_AND_RESULT" for ref in batch["packet_refs"]}
    assert all(row["candidate_evidence_role"] and row["decision"] == "UNRESOLVED" for row in evidence_candidates)
    assert len(analytical_result_candidates) == 5 and sum(row["represented_occurrence_count"] for row in analytical_result_candidates) == 11
    assert {row["symbol_packet_ref"] for row in analytical_result_candidates} == {ref for batch in remaining_batches if batch["research_archetype"] == "ANALYTICAL_METHOD_RESULT_AND_DIAGNOSTIC" for ref in batch["packet_refs"]}
    assert all(row["candidate_result_role"] and row["decision"] == "UNRESOLVED" for row in analytical_result_candidates)
    effect_estimate = next(row for row in analytical_result_candidates if row["symbol_ref"] == "type.effectestimate")
    assert effect_estimate["candidate_result_role"] == "CAUSAL_EFFECT_ESTIMATE"
    assert len({row["candidate_analytical_result_profile"] for row in effect_estimate["occurrence_profile_candidates"]}) == 3
    print(f"PASS P1 authority/symbol routing: 23 structurally ready authority packets; all 210 owner-unratified symbols and 666 occurrences have bounded primary research; 191 residual packets stay routed into {len(remaining_batches)} batches coordinated by {len(research_programs)} archetype programs and 157 semantic-axis lanes; failure research classifies 3 symbols/6 occurrences and model-artifact research classifies 2 symbols/4 occurrences while preserving owner, identity, lifecycle, authority, effect, fitness and acceptance gates")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
