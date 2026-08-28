#!/usr/bin/env python3
"""Iteration-2 corrections and new macro-axis challenges.

Iteration 1 is immutable evidence. This file refines one contaminated discovery rule and adds two
orthogonal questions only after primary-source challenge: causal/interventional semantics and
stochastic mechanism/assignment. It also records explicit rejected alternatives.
"""
from __future__ import annotations

from copy import deepcopy

from source_model import DEEP_EVIDENCE_CLAIMS, MACRO_CHALLENGES, PRIMARY_SOURCES, PROPOSED_AXES

ITERATION1_SUMMARY_SHA256 = "6059a146a89910d6b0838402c10107fb9548e255"
ITERATION1_AXIS_DELTA_SHA256 = "caff86121ad6c1ffaed03c00543a0e2c0519303d"

EXTRA_PRIMARY_SOURCES = [
    {
        "source_id": "pearl_1995_causal_diagrams",
        "issuer": "Biometrika / Oxford University Press",
        "title": "Causal diagrams for empirical research",
        "url": "https://academic.oup.com/biomet/article-abstract/82/4/669/251647",
        "source_class": "primary_research_paper",
        "retrieved_on": "2026-08-28",
        "status": "PRIMARY_OR_OFFICIAL_CHALLENGE_SOURCE",
        "completion_claim": False,
    },
    {
        "source_id": "rubin_1974_causal_effects",
        "issuer": "American Psychological Association",
        "title": "Estimating causal effects of treatments in randomized and nonrandomized studies",
        "url": "https://doi.org/10.1037/h0037350",
        "source_class": "primary_research_paper",
        "retrieved_on": "2026-08-28",
        "status": "PRIMARY_OR_OFFICIAL_CHALLENGE_SOURCE",
        "completion_claim": False,
    },
    {
        "source_id": "holland_1986_causal_inference",
        "issuer": "American Statistical Association / Taylor & Francis",
        "title": "Statistics and Causal Inference",
        "url": "https://doi.org/10.1080/01621459.1986.10478354",
        "source_class": "primary_research_paper",
        "retrieved_on": "2026-08-28",
        "status": "PRIMARY_OR_OFFICIAL_CHALLENGE_SOURCE",
        "completion_claim": False,
    },
    {
        "source_id": "rosenbaum_rubin_1983_propensity",
        "issuer": "Biometrika / Oxford University Press",
        "title": "The central role of the propensity score in observational studies for causal effects",
        "url": "https://academic.oup.com/biomet/article-abstract/70/1/41/240879",
        "source_class": "primary_research_paper",
        "retrieved_on": "2026-08-28",
        "status": "PRIMARY_OR_OFFICIAL_CHALLENGE_SOURCE",
        "completion_claim": False,
    },
    {
        "source_id": "angrist_imbens_rubin_1996_iv",
        "issuer": "American Statistical Association / Taylor & Francis",
        "title": "Identification of Causal Effects Using Instrumental Variables",
        "url": "https://doi.org/10.1080/01621459.1996.10476902",
        "source_class": "primary_research_paper",
        "retrieved_on": "2026-08-28",
        "status": "PRIMARY_OR_OFFICIAL_CHALLENGE_SOURCE",
        "completion_claim": False,
    },
    {
        "source_id": "hernan_robins_whatif",
        "issuer": "Harvard T.H. Chan School of Public Health",
        "title": "Causal Inference: What If",
        "url": "https://www.hsph.harvard.edu/miguel-hernan/wp-content/uploads/sites/1268/2024/01/hernanrobins_WhatIf_2jan24.pdf",
        "source_class": "foundational_research_book",
        "retrieved_on": "2026-08-28",
        "status": "PRIMARY_OR_OFFICIAL_CHALLENGE_SOURCE",
        "completion_claim": False,
    },
    {
        "source_id": "nist_sp800_90a_r1",
        "issuer": "NIST",
        "title": "SP 800-90A Rev. 1 Recommendation for Random Number Generation Using Deterministic Random Bit Generators",
        "url": "https://csrc.nist.gov/pubs/sp/800/90/a/r1/final",
        "source_class": "government_standard",
        "retrieved_on": "2026-08-28",
        "status": "PRIMARY_OR_OFFICIAL_CHALLENGE_SOURCE",
        "completion_claim": False,
    },
    {
        "source_id": "nist_sp800_90b",
        "issuer": "NIST",
        "title": "SP 800-90B Recommendation for the Entropy Sources Used for Random Bit Generation",
        "url": "https://csrc.nist.gov/pubs/sp/800/90/b/final",
        "source_class": "government_standard",
        "retrieved_on": "2026-08-28",
        "status": "PRIMARY_OR_OFFICIAL_CHALLENGE_SOURCE",
        "completion_claim": False,
    },
    {
        "source_id": "nist_sp800_90c",
        "issuer": "NIST",
        "title": "SP 800-90C Recommendation for Random Bit Generator Constructions",
        "url": "https://csrc.nist.gov/pubs/sp/800/90/c/final",
        "source_class": "government_standard",
        "retrieved_on": "2026-08-28",
        "status": "PRIMARY_OR_OFFICIAL_CHALLENGE_SOURCE",
        "completion_claim": False,
    },
    {
        "source_id": "r_rng",
        "issuer": "R Core Team",
        "title": "R Random Number Generation",
        "url": "https://search.r-project.org/R/refmans/base/html/Random.html",
        "source_class": "official_technical_specification",
        "retrieved_on": "2026-08-28",
        "status": "PRIMARY_OR_OFFICIAL_CHALLENGE_SOURCE",
        "completion_claim": False,
    },
    {
        "source_id": "numpy_seedsequence",
        "issuer": "NumPy",
        "title": "numpy.random.SeedSequence",
        "url": "https://numpy.org/doc/stable/reference/random/bit_generators/generated/numpy.random.SeedSequence.html",
        "source_class": "official_technical_specification",
        "retrieved_on": "2026-08-28",
        "status": "PRIMARY_OR_OFFICIAL_CHALLENGE_SOURCE",
        "completion_claim": False,
    },
    {
        "source_id": "ich_e9_randomisation",
        "issuer": "ICH / FDA",
        "title": "E9 Statistical Principles for Clinical Trials",
        "url": "https://www.fda.gov/media/71336/download",
        "source_class": "government_standard",
        "retrieved_on": "2026-08-28",
        "status": "PRIMARY_OR_OFFICIAL_CHALLENGE_SOURCE",
        "completion_claim": False,
    },
    {
        "source_id": "nist_sp800_226_dp",
        "issuer": "NIST",
        "title": "SP 800-226 Guidelines for Evaluating Differential Privacy Guarantees",
        "url": "https://csrc.nist.gov/pubs/sp/800/226/final",
        "source_class": "government_standard",
        "retrieved_on": "2026-08-28",
        "status": "PRIMARY_OR_OFFICIAL_CHALLENGE_SOURCE",
        "completion_claim": False,
    },
    {
        "source_id": "minizinc_spec",
        "issuer": "MiniZinc",
        "title": "MiniZinc Specification",
        "url": "https://docs.minizinc.dev/en/stable/spec.html",
        "source_class": "official_technical_specification",
        "retrieved_on": "2026-08-28",
        "status": "PRIMARY_OR_OFFICIAL_CHALLENGE_SOURCE",
        "completion_claim": False,
    },
    {
        "source_id": "ibm_cplex_objective",
        "issuer": "IBM",
        "title": "CPLEX Objective in LP file format",
        "url": "https://www.ibm.com/docs/en/icos/22.1.2?topic=representation-objective-in-lp-file-format",
        "source_class": "official_technical_specification",
        "retrieved_on": "2026-08-28",
        "status": "PRIMARY_OR_OFFICIAL_CHALLENGE_SOURCE",
        "completion_claim": False,
    },
    {
        "source_id": "pyomo_constraints",
        "issuer": "Pyomo",
        "title": "Pyomo Constraints",
        "url": "https://pyomo.readthedocs.io/en/stable/explanation/modeling/math_programming/constraints.html",
        "source_class": "official_technical_specification",
        "retrieved_on": "2026-08-28",
        "status": "PRIMARY_OR_OFFICIAL_CHALLENGE_SOURCE",
        "completion_claim": False,
    },
]


def refined_iteration1_axes() -> list[dict]:
    axes = deepcopy(PROPOSED_AXES)
    for axis in axes:
        if axis["axis"] != "scope_population_and_eligibility":
            continue
        for facet in axis["facets"]:
            if facet["facet"] == "contextual_constraint":
                facet["facet"] = "population_applicability_predicate"
                facet["patterns"] = [
                    r"\b(population predicate|cohort definition|analysis population|target population)\w*\b",
                    r"\b(eligibility criteri|inclusion criteri|exclusion criteri|membership rule)\w*\b",
                    r"\b(risk set|analysis set|intention.to.treat|per.protocol)\w*\b",
                    r"\b(segment predicate|population filter|sampling frame)\w*\b",
                ]
                facet["laws"] = [
                    "applicability to a population is an explicit predicate/analysis-set relation and cannot be inferred from a generic context or scope label"
                ]
        axis["non_collapse"].append("generic scope/context metadata is not a population applicability predicate")
    return axes


CAUSAL_AXIS = {
    "axis": "causal_and_interventional_semantics",
    "question": "What intervention, treatment/exposure, outcome, causal estimand and identification assumptions make a result causal rather than associational?",
    "phase": "phase2_dynamics_and_information",
    "facets": [
        {"facet": "treatment_intervention_or_exposure", "patterns": [r"\b(treatment|intervention|exposure|assigned treatment|do operator)\w*\b"], "laws": ["intervention/exposure identity and feasible values are explicit"]},
        {"facet": "outcome_or_response", "patterns": [r"\b(outcome|response variable|potential outcome)\w*\b"], "laws": ["outcome identity and observation window are explicit"]},
        {"facet": "causal_estimand", "patterns": [r"\b(causal effect|treatment effect|estimand|ate|att|late|risk difference under)\w*\b"], "laws": ["causal estimand is distinct from estimator, estimate and decision"]},
        {"facet": "potential_outcome_or_counterfactual", "patterns": [r"\b(potential outcome|counterfactual|what if|under treatment|under intervention)\w*\b"], "laws": ["counterfactual state is not realized observation"]},
        {"facet": "assignment_or_treatment_mechanism", "patterns": [r"\b(assignment mechanism|treatment assignment|randomi[sz]ed assignment|propensity score)\w*\b"], "laws": ["assignment mechanism is part of causal identification, not merely execution order"]},
        {"facet": "causal_graph_or_structural_mechanism", "patterns": [r"\b(causal graph|causal diagram|dag|structural causal|causal mechanism)\w*\b"], "laws": ["causal edges encode assumptions beyond graph reachability or temporal order"]},
        {"facet": "identification_assumption", "patterns": [r"\b(exchangeability|ignorability|unconfounded|instrumental variable|identifia|positivity|consistency)\w*\b"], "laws": ["identification assumptions and their scope are explicit and challengeable"]},
        {"facet": "confounding_or_adjustment_set", "patterns": [r"\b(confound|adjustment set|backdoor|covariate adjustment|matching)\w*\b"], "laws": ["adjustment is justified by a causal identification argument, not association alone"]},
    ],
    "non_collapse": [
        "temporal precedence is not causation",
        "graph edge is not causal edge",
        "association is not causal effect",
        "prediction is not causal effect",
        "intervention is not observation",
        "causal estimand is not estimator or estimate",
        "counterfactual is not realized outcome",
        "identifiability is not estimability, precision or implementation success",
    ],
    "evidence_refs": [
        "pearl_1995_causal_diagrams",
        "rubin_1974_causal_effects",
        "holland_1986_causal_inference",
        "rosenbaum_rubin_1983_propensity",
        "angrist_imbens_rubin_1996_iv",
        "hernan_robins_whatif",
        "fda_e9r1",
    ],
    "model_verdict": "ADD_RESEARCH_AXIS",
}

STOCHASTIC_AXIS = {
    "axis": "stochastic_mechanism_and_assignment",
    "question": "What source, algorithm, state, seed, stream, assignment rule or randomized mechanism governs stochastic behavior and reproducibility?",
    "phase": "phase2_dynamics_and_information",
    "facets": [
        {"facet": "entropy_source", "patterns": [r"\b(entropy source|min.entropy|noise source|true random)\w*\b"], "laws": ["entropy source identity/health is distinct from deterministic generator state"]},
        {"facet": "prng_or_drbg_algorithm", "patterns": [r"\b(prng|rng|random number generator|drbg|bit generator|mersenne|pcg)\w*\b"], "laws": ["generator algorithm and edition are explicit"]},
        {"facet": "seed_or_initial_state", "patterns": [r"\b(seed|random seed|rng state|initial state)\w*\b"], "laws": ["seed/state is an explicit input/evidence coordinate and not a promise of statistical independence"]},
        {"facet": "stream_or_substream", "patterns": [r"\b(random stream|substream|spawn key|child stream|independent stream)\w*\b"], "laws": ["stream partition/spawn relation is explicit and cannot be inferred from thread identity"]},
        {"facet": "assignment_randomization", "patterns": [r"\b(randomi[sz]ation|random assignment|allocation sequence|assignment schedule)\w*\b"], "laws": ["assignment mechanism is distinct from realized assignment and treatment receipt"]},
        {"facet": "randomized_algorithm_or_mechanism", "patterns": [r"\b(randomized algorithm|stochastic algorithm|random noise|noise mechanism|monte carlo)\w*\b"], "laws": ["randomized mechanism identity/parameters are explicit"]},
        {"facet": "reproducibility_profile", "patterns": [r"\b(reproducib|rng version|seed sequence|deterministic replay)\w*\b"], "laws": ["reproducibility binds implementation/version/state and environment assumptions"]},
        {"facet": "randomness_quality_or_independence", "patterns": [r"\b(independent random|randomness test|statistical quality|entropy validation)\w*\b"], "laws": ["quality/independence claims require bounded evidence and are not implied by a seed"]},
    ],
    "non_collapse": [
        "randomness mechanism is not uncertainty representation",
        "entropy source is not deterministic generator",
        "seed is not generator algorithm and does not prove independence",
        "random assignment mechanism is not realized assignment",
        "randomized mechanism is not nondeterministic ambient behavior",
        "reproducibility is not statistical validity",
        "privacy noise mechanism is not generic measurement error",
    ],
    "evidence_refs": [
        "nist_sp800_90a_r1",
        "nist_sp800_90b",
        "nist_sp800_90c",
        "r_rng",
        "numpy_seedsequence",
        "ich_e9_randomisation",
        "nist_sp800_226_dp",
        "rubin_1974_causal_effects",
    ],
    "model_verdict": "ADD_RESEARCH_AXIS",
}

ITERATION2_AXES = refined_iteration1_axes() + [CAUSAL_AXIS, STOCHASTIC_AXIS]
ITERATION2_PRIMARY_SOURCES = PRIMARY_SOURCES + EXTRA_PRIMARY_SOURCES

ITERATION2_DEEP_CLAIMS = DEEP_EVIDENCE_CLAIMS + [
    {
        "claim_id": "claim.macro.causal.association-not-causation",
        "supports_axis": "causal_and_interventional_semantics",
        "source_refs": ["holland_1986_causal_inference", "hernan_robins_whatif"],
        "bounded_claim": "Causal contrasts answer intervention/counterfactual questions and are not interchangeable with associations observed between exposed and unexposed groups.",
        "authority_limit": "These sources define causal-inference semantics and frameworks, not a universal domain treatment policy.",
        "negative_twin": "A strong predictive association may remain noncausal under confounding.",
        "status": "BOUNDED_RESEARCH_CLAIM_NOT_AUTHORITY",
        "completion_claim": False,
    },
    {
        "claim_id": "claim.macro.causal.graph-not-topology",
        "supports_axis": "causal_and_interventional_semantics",
        "source_refs": ["pearl_1995_causal_diagrams", "hernan_robins_whatif"],
        "bounded_claim": "A causal graph encodes causal and subject-matter assumptions used for identification; it is not merely a graph-topology or temporal-order relation.",
        "authority_limit": "A graph does not make its assumptions true and does not identify effects when required assumptions fail.",
        "negative_twin": "Two variables can be connected in a dependency graph without either being a valid intervention cause of the other.",
        "status": "BOUNDED_RESEARCH_CLAIM_NOT_AUTHORITY",
        "completion_claim": False,
    },
    {
        "claim_id": "claim.macro.causal.assignment-mechanism",
        "supports_axis": "causal_and_interventional_semantics",
        "source_refs": ["rubin_1974_causal_effects", "rosenbaum_rubin_1983_propensity", "ich_e9_randomisation"],
        "bounded_claim": "Treatment-assignment mechanism is part of the causal design/identification contract; random assignment and covariate-conditioned observational assignment have different guarantees.",
        "authority_limit": "Assignment semantics do not prove adherence, outcome measurement quality or causal assumptions after protocol deviations.",
        "negative_twin": "The same observed treatment groups can support different causal claims depending on how assignment occurred.",
        "status": "BOUNDED_RESEARCH_CLAIM_NOT_AUTHORITY",
        "completion_claim": False,
    },
    {
        "claim_id": "claim.macro.causal.estimand-estimator",
        "supports_axis": "causal_and_interventional_semantics",
        "source_refs": ["fda_e9r1", "hernan_robins_whatif"],
        "bounded_claim": "The causal effect/estimand of interest must be specified independently of the statistical estimator and resulting numerical estimate.",
        "authority_limit": "Specifying an estimand does not make it identifiable, estimable, unbiased or policy-relevant.",
        "negative_twin": "Two estimators can target one estimand, while one estimator can be applied to different estimands under changed population/intercurrent-event strategies.",
        "status": "BOUNDED_RESEARCH_CLAIM_NOT_AUTHORITY",
        "completion_claim": False,
    },
    {
        "claim_id": "claim.macro.causal.identification-estimation",
        "supports_axis": "causal_and_interventional_semantics",
        "source_refs": ["pearl_1995_causal_diagrams", "angrist_imbens_rubin_1996_iv"],
        "bounded_claim": "Causal identification depends on explicit assumptions and can target effects for specific populations; numerical estimation follows only after an effect is identified under those assumptions.",
        "authority_limit": "Identification under stated assumptions does not establish assumption truth or implementation correctness.",
        "negative_twin": "A low-variance estimator can precisely estimate an associational quantity when the desired causal estimand is not identified.",
        "status": "BOUNDED_RESEARCH_CLAIM_NOT_AUTHORITY",
        "completion_claim": False,
    },
    {
        "claim_id": "claim.macro.causal.population-specific-effect",
        "supports_axis": "causal_and_interventional_semantics",
        "source_refs": ["angrist_imbens_rubin_1996_iv", "fda_e9r1", "rosenbaum_rubin_1983_propensity"],
        "bounded_claim": "A causal effect is scoped to a target population/subpopulation and assignment/intervention semantics; effects such as local average treatment effects cannot silently generalize to all subjects.",
        "authority_limit": "These frameworks do not provide automatic transportability beyond their target populations and assumptions.",
        "negative_twin": "A valid complier-average effect can differ from the average treatment effect in the full eligible population.",
        "status": "BOUNDED_RESEARCH_CLAIM_NOT_AUTHORITY",
        "completion_claim": False,
    },
    {
        "claim_id": "claim.macro.stochastic.entropy-generator-separation",
        "supports_axis": "stochastic_mechanism_and_assignment",
        "source_refs": ["nist_sp800_90a_r1", "nist_sp800_90b", "nist_sp800_90c"],
        "bounded_claim": "Entropy sources, deterministic random-bit generators and complete random-bit-generator constructions are distinct components with separate validation obligations.",
        "authority_limit": "Cryptographic RBG standards do not define all statistical simulation or experimental assignment requirements.",
        "negative_twin": "A deterministic generator can replay perfectly from state while providing no fresh entropy.",
        "status": "BOUNDED_RESEARCH_CLAIM_NOT_AUTHORITY",
        "completion_claim": False,
    },
    {
        "claim_id": "claim.macro.stochastic.seed-version-state",
        "supports_axis": "stochastic_mechanism_and_assignment",
        "source_refs": ["r_rng", "numpy_seedsequence"],
        "bounded_claim": "Reproducible pseudorandom execution depends on generator kind/version and explicit seed/state/stream construction, not just a generic random flag.",
        "authority_limit": "Reproducing a pseudorandom stream does not prove distributional suitability or scientific validity.",
        "negative_twin": "The same integer seed under different generator algorithms or versions can produce different streams.",
        "status": "BOUNDED_RESEARCH_CLAIM_NOT_AUTHORITY",
        "completion_claim": False,
    },
    {
        "claim_id": "claim.macro.stochastic.randomization-realized-assignment",
        "supports_axis": "stochastic_mechanism_and_assignment",
        "source_refs": ["ich_e9_randomisation", "rubin_1974_causal_effects"],
        "bounded_claim": "A randomization schedule/mechanism is distinct from each realized treatment assignment and from treatment actually received; the schedule must be preplanned and reproducible where required.",
        "authority_limit": "Random assignment does not prove adherence, blinding success or outcome validity.",
        "negative_twin": "A subject can be randomly assigned treatment A yet receive treatment B or no treatment.",
        "status": "BOUNDED_RESEARCH_CLAIM_NOT_AUTHORITY",
        "completion_claim": False,
    },
    {
        "claim_id": "claim.macro.stochastic.randomness-not-uncertainty",
        "supports_axis": "stochastic_mechanism_and_assignment",
        "source_refs": ["nist_sp800_90a_r1", "nist_sp800_90b", "r_rng"],
        "bounded_claim": "A mechanism that generates random/pseudorandom values is an execution process with state and provenance; a probability distribution or uncertainty interval is a semantic description and need not imply such a mechanism.",
        "authority_limit": "Random-number standards do not define epistemic uncertainty semantics.",
        "negative_twin": "A fixed analytic probability distribution can be evaluated deterministically, while a simulation can draw random samples from it.",
        "status": "BOUNDED_RESEARCH_CLAIM_NOT_AUTHORITY",
        "completion_claim": False,
    },
    {
        "claim_id": "claim.macro.stochastic.dp-mechanism",
        "supports_axis": "stochastic_mechanism_and_assignment",
        "source_refs": ["nist_sp800_226_dp", "nist_sp800_90a_r1"],
        "bounded_claim": "Differentially private algorithms commonly rely on deliberately randomized noise mechanisms whose mechanism and parameters affect the guarantee; random noise is not generic measurement error.",
        "authority_limit": "NIST differential-privacy guidance does not validate a particular implementation merely because it adds noise.",
        "negative_twin": "Adding arbitrary random noise can reduce utility without satisfying a differential-privacy guarantee.",
        "status": "BOUNDED_RESEARCH_CLAIM_NOT_AUTHORITY",
        "completion_claim": False,
    },
    {
        "claim_id": "claim.macro.stochastic.stream-independence",
        "supports_axis": "stochastic_mechanism_and_assignment",
        "source_refs": ["numpy_seedsequence", "nist_sp800_90c"],
        "bounded_claim": "Parallel/substream construction is a distinct semantic obligation: child streams require a documented derivation/independence posture rather than thread-local guessing.",
        "authority_limit": "Spawn construction does not prove independence for arbitrary custom generators or scientific workflows.",
        "negative_twin": "Two workers initialized with accidentally identical state can appear independent while emitting identical pseudorandom sequences.",
        "status": "BOUNDED_RESEARCH_CLAIM_NOT_AUTHORITY",
        "completion_claim": False,
    },
]

ITERATION2_CHALLENGES = MACRO_CHALLENGES + [
    {
        "challenge_id": "macro.causal-interventional",
        "candidate": "causal_and_interventional_semantics",
        "verdict": "ADD_RESEARCH_AXIS",
        "reason": "Causal treatment/intervention, counterfactual, estimand and identification assumptions are not graph topology, temporal order, prediction or uncertainty. Existing order_and_topology must stop treating the token 'causal' as sufficient causal semantics.",
        "counterfactual": "If causal meaning were reducible to topology/order, any directed or preceding relation could be used as a causal edge without intervention or identification assumptions, which the causal literature explicitly rejects.",
    },
    {
        "challenge_id": "macro.stochastic-mechanism",
        "candidate": "stochastic_mechanism_and_assignment",
        "verdict": "ADD_RESEARCH_AXIS",
        "reason": "Entropy sources, deterministic generator algorithms, seed/state, streams, randomization schedules and randomized mechanisms are execution semantics distinct from probabilistic uncertainty and from ambient nondeterminism.",
        "counterfactual": "If uncertainty semantics were sufficient, recording a probability distribution would be enough to reproduce a randomized execution or validate a treatment-allocation mechanism; it is not.",
    },
    {
        "challenge_id": "macro.objective-preference",
        "candidate": "objective_preference_and_decision_criterion",
        "verdict": "REJECT_NEW_AXIS_COMPOSE",
        "reason": "Optimization languages distinguish objective, constraints and solve sense, but the repository already has a sovereign intent/objective-constraint context. Objective/preference is a domain contract imported by optimization/decision libraries, not a missing universal semantic question over every library.",
        "composition": ["semantic_object", "semantic_role", "normativity_and_obligation", "scope_population_and_eligibility"],
        "source_refs": ["minizinc_spec", "ibm_cplex_objective", "pyomo_constraints"],
    },
]

CROSS_AXIS_INTERACTIONS = [
    {"from_axis": "measurement_and_observation", "to_axis": "identity_and_equality", "relation": "REQUIRES_WITHOUT_COLLAPSE", "law": "measurement/observation subjects, procedures, instruments and results require scoped identity, but identity alone supplies no quantity/unit/calibration semantics"},
    {"from_axis": "measurement_and_observation", "to_axis": "partiality_and_uncertainty", "relation": "REQUIRES_WITHOUT_COLLAPSE", "law": "measurement uncertainty may use uncertainty carriers, but uncertainty is not measurement error, calibration or traceability"},
    {"from_axis": "measurement_and_observation", "to_axis": "provenance_and_derivation", "relation": "REQUIRES_WITHOUT_COLLAPSE", "law": "calibration and observation provenance are required evidence relations, but provenance does not establish metrological traceability by itself"},
    {"from_axis": "scope_population_and_eligibility", "to_axis": "grain_and_cardinality", "relation": "ORTHOGONAL", "law": "row/collection cardinality never determines target-population membership or denominator support"},
    {"from_axis": "scope_population_and_eligibility", "to_axis": "time", "relation": "REQUIRES_WITHOUT_COLLAPSE", "law": "population membership may be time/cut dependent; time alone does not define eligibility"},
    {"from_axis": "normativity_and_obligation", "to_axis": "authority_and_trust", "relation": "REQUIRES_WITHOUT_COLLAPSE", "law": "norms require authorized issuers/deciders, but authority does not determine whether a state is permission, prohibition, duty, waiver, fulfillment or breach"},
    {"from_axis": "normativity_and_obligation", "to_axis": "effect_boundary", "relation": "ORTHOGONAL", "law": "an obligation or prohibition is not its enforcement attempt or external effect"},
    {"from_axis": "provenance_and_derivation", "to_axis": "order_and_topology", "relation": "USES_WITHOUT_COLLAPSE", "law": "provenance can be graph-shaped and ordered while generation/usage/derivation relations retain semantics beyond topology"},
    {"from_axis": "provenance_and_derivation", "to_axis": "authority_and_trust", "relation": "ORTHOGONAL", "law": "source/derivation provenance records where something came from; separate authority decides whether that source was authoritative"},
    {"from_axis": "epistemic_status", "to_axis": "partiality_and_uncertainty", "relation": "ORTHOGONAL", "law": "an observed or simulated value may each be uncertain; epistemic status and uncertainty type are independent questions"},
    {"from_axis": "causal_and_interventional_semantics", "to_axis": "order_and_topology", "relation": "USES_WITHOUT_COLLAPSE", "law": "causal graphs may be directed/acyclic, but topology/order does not establish causal edge semantics"},
    {"from_axis": "causal_and_interventional_semantics", "to_axis": "epistemic_status", "relation": "REQUIRES_WITHOUT_COLLAPSE", "law": "causal estimates/counterfactuals have epistemic status, while causal identification additionally requires intervention/assignment/assumption semantics"},
    {"from_axis": "causal_and_interventional_semantics", "to_axis": "scope_population_and_eligibility", "relation": "REQUIRES_WITHOUT_COLLAPSE", "law": "causal estimands are population scoped; population membership alone does not identify a causal effect"},
    {"from_axis": "stochastic_mechanism_and_assignment", "to_axis": "partiality_and_uncertainty", "relation": "ORTHOGONAL", "law": "random mechanisms generate stochastic executions; uncertainty represents incomplete/probabilistic knowledge and may exist without random execution"},
    {"from_axis": "stochastic_mechanism_and_assignment", "to_axis": "provenance_and_derivation", "relation": "REQUIRES_WITHOUT_COLLAPSE", "law": "reproducible stochastic runs require generator/version/state provenance, but provenance alone does not define the stochastic mechanism"},
    {"from_axis": "stochastic_mechanism_and_assignment", "to_axis": "causal_and_interventional_semantics", "relation": "USES_WITHOUT_COLLAPSE", "law": "randomized assignment may support causal identification, but causal semantics also cover nonrandomized interventions and assumptions"},
]

ITERATION2_CORRECTIONS = [
    {
        "correction_id": "correction.iter2.scope-generic-token-contamination",
        "axis": "scope_population_and_eligibility",
        "iteration1_problem": "The contextual_constraint facet matched bare scope/context/applicability/constraint/segment, producing 357 candidate facet occurrences and making one analytical family appear 100% covered from generic vocabulary.",
        "iteration2_change": "Replace the generic matcher with explicit population/cohort/analysis-set/eligibility/membership/risk-set/segment-predicate phrases. No bare scope or context token is evidence.",
        "required_test": "iteration-2 scope candidate cells and contextual/applicability occurrences must fall materially while all cells remain losslessly candidate or unresolved.",
        "status": "CORRECTION_REQUIRED",
        "completion_claim": False,
    },
    {
        "correction_id": "correction.iter2.causal-token-in-order-topology",
        "axis": "order_and_topology",
        "iteration1_problem": "The historical partial_order discovery pattern includes the token causal/happens-before, which can route causal terminology into ordering without preserving intervention, estimand or identification semantics.",
        "iteration2_change": "Retain causal/happens-before only as ordering discovery evidence; add a separate causal/interventional axis and a non-collapse law that causal effect/edge semantics require explicit causal contracts.",
        "required_test": "causal axis must be independently evidence-backed and must not inherit applicability from generic directed/ordered graph matches.",
        "status": "CORRECTION_REQUIRED",
        "completion_claim": False,
    },
]
