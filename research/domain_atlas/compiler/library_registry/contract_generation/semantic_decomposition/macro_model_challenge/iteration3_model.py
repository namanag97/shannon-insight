#!/usr/bin/env python3
"""Iteration-3 macro-model correction: split quantitative value from observation/metrology."""
from __future__ import annotations

from copy import deepcopy

from iteration2_model import (
    CROSS_AXIS_INTERACTIONS,
    ITERATION2_AXES,
    ITERATION2_CHALLENGES,
    ITERATION2_DEEP_CLAIMS,
    ITERATION2_PRIMARY_SOURCES,
)

ITERATION2_SUMMARY_BLOB_SHA = "cddb51d49a0a1bdc3de6ff88644bae459a54db1e"
ITERATION2_AXIS_DELTA_BLOB_SHA = "27b0b2bc92d82f709530d95c9e913e7b546a61d1"

EXTRA_PRIMARY_SOURCES = [
    {"source_id":"iso_4217_current","issuer":"ISO","title":"ISO 4217:2015 Codes for the representation of currencies","url":"https://www.iso.org/standard/64758.html","source_class":"international_standard","retrieved_on":"2026-08-28","status":"PRIMARY_OR_OFFICIAL_CHALLENGE_SOURCE","completion_claim":False},
    {"source_id":"xbrl_units_registry","issuer":"XBRL International","title":"Units Registry 1.0","url":"https://specifications.xbrl.org/work-product-index-registries-units-registry-1.0.html","source_class":"industry_standard","retrieved_on":"2026-08-28","status":"PRIMARY_OR_OFFICIAL_CHALLENGE_SOURCE","completion_claim":False},
    {"source_id":"xbrl_reporting_requirements","issuer":"XBRL International","title":"Defining Reporting Requirements","url":"https://specifications.xbrl.org/reporting-requirements.html","source_class":"industry_standard","retrieved_on":"2026-08-28","status":"PRIMARY_OR_OFFICIAL_CHALLENGE_SOURCE","completion_claim":False},
    {"source_id":"fpml_money","issuer":"FpML / ISDA","title":"FpML Money complex type","url":"https://www.fpml.org/spec/fpml-5-5-13-rec-5/html/transparency/schemaDocumentation/schemas/fpml-shared-5-5_xsd/complexTypes/Money.html","source_class":"industry_standard","retrieved_on":"2026-08-28","status":"PRIMARY_OR_OFFICIAL_CHALLENGE_SOURCE","completion_claim":False},
    {"source_id":"gs1_epcis_quantity","issuer":"GS1","title":"EPCIS 2.0.1 QuantityElement","url":"https://ref.gs1.org/standards/epcis/2.0.1/","source_class":"industry_standard","retrieved_on":"2026-08-28","status":"PRIMARY_OR_OFFICIAL_CHALLENGE_SOURCE","completion_claim":False},
    {"source_id":"fhir_r5_datatypes","issuer":"HL7","title":"FHIR R5 Datatypes: Quantity, Money and Ratio","url":"https://hl7.org/fhir/R5/datatypes.html","source_class":"international_standard","retrieved_on":"2026-08-28","status":"PRIMARY_OR_OFFICIAL_CHALLENGE_SOURCE","completion_claim":False},
]

QUANTITY_AXIS = {
    "axis":"quantity_and_value_semantics",
    "question":"What kind of quantitative value is this, with what magnitude, unit/currency, scale/basis, ratio/rate structure and comparison/conversion law?",
    "phase":"phase1_subject_and_grain",
    "facets":[
        {"facet":"quantity_or_value_kind","patterns":[r"\b(quantity kind|quantity|amount|notional|monetary|money|value kind)\w*\b"],"laws":["quantitative kind is distinct from magnitude and representation"]},
        {"facet":"magnitude_or_numeric_value","patterns":[r"\b(magnitude|numeric value|amount value|decimal value)\w*\b"],"laws":["magnitude is interpreted only together with its quantitative kind and unit/basis"]},
        {"facet":"unit_or_currency","patterns":[r"\b(unit of measure|unit|uom|currency|iso 4217|ucum|qudt)\b"],"laws":["unit/currency is part of quantitative interpretation, not decorative metadata"]},
        {"facet":"count_or_measure_amount","patterns":[r"\b(count|quantity element|how many|how much)\w*\b"],"laws":["count and continuous measure amount are distinct quantitative semantics"]},
        {"facet":"ratio_rate_or_denominator","patterns":[r"\b(ratio|rate|numerator|denominator|per unit|per-unit|frequency)\w*\b"],"laws":["ratio/rate preserves numerator, denominator/basis and dimensional semantics"]},
        {"facet":"percentage_fraction_or_index","patterns":[r"\b(percent|percentage|fraction|index value|basis point)\w*\b"],"laws":["percentage/fraction/index conventions are explicit and cannot be inferred from bare decimals"]},
        {"facet":"price_notional_or_valuation_basis","patterns":[r"\b(price|notional|valuation|present value|fair value|strike price|settlement amount)\w*\b"],"laws":["price, notional, valuation and settlement amount retain distinct bases and time/reference semantics"]},
        {"facet":"precision_rounding_or_minor_unit","patterns":[r"\b(precision|rounding|minor unit|decimal places|quantization)\w*\b"],"laws":["precision/rounding/minor-unit rules are explicit and cannot be reconstructed from formatted output"]},
    ],
    "non_collapse":[
        "quantitative kind is not magnitude",
        "unit/currency is not magnitude",
        "currency is not an SI physical unit even when both are carried as unit-like codes",
        "count is not continuous physical measure",
        "ratio is not a scalar with its denominator forgotten",
        "percentage decimal representation is not the percentage semantic convention",
        "price is not notional and not settlement amount",
        "valuation result is not direct observation",
    ],
    "evidence_refs":["iso_4217_current","xbrl_units_registry","xbrl_reporting_requirements","fpml_money","gs1_epcis_quantity","fhir_r5_datatypes","bipm_si","iso_80000_1","ucum","qudt_schema"],
    "model_verdict":"ADD_RESEARCH_AXIS_BY_SPLIT",
}

OBSERVATION_AXIS = {
    "axis":"observation_measurement_and_metrology",
    "question":"What property was observed/measured, by what act/procedure/instrument, with what result, calibration and metrological traceability?",
    "phase":"phase2_dynamics_and_information",
    "facets":[
        {"facet":"observed_property_or_measurand","patterns":[r"\b(observed property|observable|measurand|phenomenon)\b"],"laws":["property/measurand is distinct from observation act and result"]},
        {"facet":"observation_or_measurement_act","patterns":[r"\b(observation|measurement|measure|sample)\w*\b"],"laws":["observation occurrence is independently identifiable from its result"]},
        {"facet":"procedure_instrument_or_sensor","patterns":[r"\b(procedure|instrument|sensor|device|method of measurement|calibrat)\w*\b"],"laws":["procedure/instrument is part of interpretation and evidence"]},
        {"facet":"measurement_or_observation_result","patterns":[r"\b(measurement result|observed value|reading|result value)\w*\b"],"laws":["result remains scoped to observed property, subject, procedure and time"]},
        {"facet":"calibration_or_reference_standard","patterns":[r"\b(calibration|reference standard|reference material)\w*\b"],"laws":["calibration is an evidence-bearing relation rather than unit conversion"]},
        {"facet":"metrological_traceability","patterns":[r"\b(metrological traceability|calibration chain|traceable measurement)\w*\b"],"laws":["traceability requires a documented reference chain with uncertainty contributions"]},
        {"facet":"sampling_feature_or_specimen","patterns":[r"\b(sampling feature|specimen|sample subject|feature of interest)\w*\b"],"laws":["sampling feature/specimen remains distinct from ultimate feature of interest"]},
    ],
    "non_collapse":[
        "observation act is not observation result",
        "procedure/instrument is not observed property",
        "unit conversion is not calibration",
        "measurement uncertainty is not measurement error",
        "instrument reading is not accepted domain fact",
        "sampling feature/specimen is not target population or ultimate feature of interest",
        "measurement result may be a quantity but quantity semantics exist independently of observation",
    ],
    "evidence_refs":["bipm_gum","bipm_vim","iso_19156","ogc_om","ogc_sensorthings","ogc_sensorml","w3c_ssn","nist_measurement"],
    "model_verdict":"ADD_RESEARCH_AXIS_BY_SPLIT",
}

ITERATION3_AXES = [axis for axis in deepcopy(ITERATION2_AXES) if axis["axis"] != "measurement_and_observation"]
ITERATION3_AXES = [QUANTITY_AXIS, OBSERVATION_AXIS] + ITERATION3_AXES
ITERATION3_PRIMARY_SOURCES = ITERATION2_PRIMARY_SOURCES + EXTRA_PRIMARY_SOURCES

ITERATION3_DEEP_CLAIMS = []
for claim in deepcopy(ITERATION2_DEEP_CLAIMS):
    if claim["supports_axis"] == "measurement_and_observation":
        claim["supports_axis"] = "observation_measurement_and_metrology"
    ITERATION3_DEEP_CLAIMS.append(claim)
ITERATION3_DEEP_CLAIMS += [
    {"claim_id":"claim.macro.quantity.monetary-unit","supports_axis":"quantity_and_value_semantics","source_refs":["iso_4217_current","xbrl_units_registry","xbrl_reporting_requirements"],"bounded_claim":"Monetary numeric facts require explicit currency/unit semantics; ISO 4217 currency identity and minor-unit relationships are part of interpretation rather than formatting.","authority_limit":"Currency codes do not provide valuation method, exchange rate, legal ownership or accounting policy.","negative_twin":"100 USD and 100 EUR have equal numeric magnitude but are not equal monetary values without an explicit conversion relation and time/basis.","status":"BOUNDED_RESEARCH_CLAIM_NOT_AUTHORITY","completion_claim":False},
    {"claim_id":"claim.macro.quantity.money-amount-pair","supports_axis":"quantity_and_value_semantics","source_refs":["fpml_money","fhir_r5_datatypes","iso_4217_current"],"bounded_claim":"Financial standards model Money as an amount plus currency; the numeric component alone is semantically incomplete.","authority_limit":"Money datatypes do not establish price source, valuation authority or settlement finality.","negative_twin":"The decimal 10.00 without currency cannot be safely compared, aggregated or settled as a monetary amount.","status":"BOUNDED_RESEARCH_CLAIM_NOT_AUTHORITY","completion_claim":False},
    {"claim_id":"claim.macro.quantity.ratio-denominator","supports_axis":"quantity_and_value_semantics","source_refs":["fhir_r5_datatypes","xbrl_reporting_requirements"],"bounded_claim":"Ratios/rates preserve numerator and denominator/basis semantics and must not be flattened into a dimensionless scalar merely because serialization is numeric.","authority_limit":"FHIR/XBRL do not define every enterprise rate convention.","negative_twin":"5 mg/10 mL and 0.5 mg/mL can be numerically transformable while retaining different declared numerator/denominator provenance and precision.","status":"BOUNDED_RESEARCH_CLAIM_NOT_AUTHORITY","completion_claim":False},
    {"claim_id":"claim.macro.quantity.count-measure","supports_axis":"quantity_and_value_semantics","source_refs":["gs1_epcis_quantity","bipm_si","iso_80000_1"],"bounded_claim":"Counts and physical measure amounts are distinct: GS1 EPCIS uses an omitted UOM for positive-integer counts and a UOM for variable physical measures.","authority_limit":"EPCIS quantity semantics apply to its supply-chain objects, not all count/measure models.","negative_twin":"A quantity of 10 can mean ten items or ten kilograms; magnitude and object class alone do not choose the semantics.","status":"BOUNDED_RESEARCH_CLAIM_NOT_AUTHORITY","completion_claim":False},
    {"claim_id":"claim.macro.quantity.percentage-rate-basis","supports_axis":"quantity_and_value_semantics","source_refs":["fhir_r5_datatypes","fpml_money","xbrl_reporting_requirements"],"bounded_claim":"Rates, percentages and monetary amounts require explicit quantitative conventions/bases; a decimal representation such as 0.05 does not by itself state whether the semantic value is 5%, a unitless ratio, a rate, or an amount.","authority_limit":"The cited standards provide domain examples rather than one universal percentage convention.","negative_twin":"0.05 can be a 5% premium rate, a probability, a unitless ratio or a physical coefficient with different comparison/aggregation laws.","status":"BOUNDED_RESEARCH_CLAIM_NOT_AUTHORITY","completion_claim":False},
    {"claim_id":"claim.macro.quantity.fact-context","supports_axis":"quantity_and_value_semantics","source_refs":["xbrl_reporting_requirements","xbrl_units_registry","fhir_r5_datatypes"],"bounded_claim":"A quantitative fact is interpreted with concept/kind, unit/currency and contextual basis; formatting or raw numeric equality does not determine quantitative equality.","authority_limit":"Reporting and healthcare datatype standards do not define every quantitative business concept.","negative_twin":"Two facts with identical decimals but different units, currencies, concepts or ratio bases cannot be silently equated.","status":"BOUNDED_RESEARCH_CLAIM_NOT_AUTHORITY","completion_claim":False},
]

ITERATION3_CHALLENGES = ITERATION2_CHALLENGES + [
    {"challenge_id":"macro.measurement-quantity-split","candidate":"measurement_and_observation","verdict":"SPLIT_RESEARCH_AXIS","reason":"Iteration 2 conflated quantitative value structure with observation/metrology. Physical quantity/unit laws generalize to non-observational values, while observation/procedure/calibration/traceability are process/evidence semantics. Financial standards additionally require currency, amount, ratio, percentage and price conventions that are not metrology.","split_into":["quantity_and_value_semantics","observation_measurement_and_metrology"],"source_refs":["xbrl_units_registry","iso_4217_current","fpml_money","gs1_epcis_quantity","fhir_r5_datatypes","bipm_vim","iso_19156"]},
]

ITERATION3_INTERACTIONS = [row for row in CROSS_AXIS_INTERACTIONS if row["from_axis"] != "measurement_and_observation" and row["to_axis"] != "measurement_and_observation"] + [
    {"from_axis":"quantity_and_value_semantics","to_axis":"observation_measurement_and_metrology","relation":"ORTHOGONAL_WITH_LINK","law":"an observation/measurement result may carry quantity semantics, while targets, prices, notionals, rates and declared amounts can exist without an observation act"},
    {"from_axis":"quantity_and_value_semantics","to_axis":"representation","relation":"REQUIRES_WITHOUT_COLLAPSE","law":"unit/currency/ratio basis is semantic interpretation; textual formatting and serialization are representations"},
    {"from_axis":"quantity_and_value_semantics","to_axis":"identity_and_equality","relation":"REQUIRES_WITHOUT_COLLAPSE","law":"quantitative equality requires compatible kind/unit/basis semantics beyond numeric equality"},
    {"from_axis":"quantity_and_value_semantics","to_axis":"scope_population_and_eligibility","relation":"USES_WITHOUT_COLLAPSE","law":"rates and denominated measures may import denominator/population support, but population scope is not the numeric value kind"},
    {"from_axis":"observation_measurement_and_metrology","to_axis":"identity_and_equality","relation":"REQUIRES_WITHOUT_COLLAPSE","law":"property, observation, result, instrument/procedure and sampling-feature identities remain distinct"},
    {"from_axis":"observation_measurement_and_metrology","to_axis":"partiality_and_uncertainty","relation":"REQUIRES_WITHOUT_COLLAPSE","law":"measurement uncertainty may use generic uncertainty carriers but does not collapse calibration/error/traceability into uncertainty"},
    {"from_axis":"observation_measurement_and_metrology","to_axis":"provenance_and_derivation","relation":"REQUIRES_WITHOUT_COLLAPSE","law":"measurement provenance records procedure/instrument/reference history while metrological traceability imposes stronger reference-chain conditions"},
]

ITERATION3_CORRECTIONS = [
    {"correction_id":"correction.iter3.measurement-quantity-split","iteration2_axis":"measurement_and_observation","replacement_axes":["quantity_and_value_semantics","observation_measurement_and_metrology"],"problem":"The iteration-2 axis coupled unit/quantity semantics with observation/calibration semantics and therefore under-modeled monetary, rate, ratio, price, notional and other declared quantitative values that are not instrument observations.","required_test":"both replacement axes must be independently evidence-backed by at least three issuers, each must produce its own 682-cell review surface, and the old axis must not appear in the iteration-3 effective candidate set","status":"CORRECTION_REQUIRED","completion_claim":False},
]
