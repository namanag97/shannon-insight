"""Curated search seeds for the global expert-portfolio evidence graph.

The family assignment is a research routing hypothesis, not an expertise claim.  It
only decides which bibliography query and review queue a person enters.  Expertise
and contribution claims are admitted later, artifact by artifact.
"""

FAMILY_GROUPS = {
    "process_case_mining": {
        "families": [
            "process_discovery",
            "conformance_checking",
            "object_centric_event_data",
            "process_prediction_and_intervention",
        ],
        "experts": [
            "Wil van der Aalst", "Dirk Fahland", "Marlon Dumas",
            "Josep Carmona", "Alessandro Berti", "Boudewijn van Dongen",
            "Massimiliano de Leoni", "Marcello La Rosa", "Jan Mendling",
            "Artem Polyvyanyy", "Sebastiaan van Zelst", "Jorge Munoz-Gama",
        ],
        "lesson": "Keep event identity, object/case correlation, ordering, discovery, conformance, diagnosis, prediction, and intervention as distinct contracts.",
    },
    "databases_query": {
        "families": [
            "query_optimization",
            "transaction_processing",
            "columnar_vectorized_execution",
            "approximate_and_adaptive_query_processing",
        ],
        "experts": [
            "Michael Stonebraker", "Hector Garcia-Molina", "Goetz Graefe",
            "Surajit Chaudhuri", "Volker Markl", "Anastasia Ailamaki",
            "Dan Suciu", "Christopher Re", "Peter Boncz", "Andy Pavlo",
            "Stratos Idreos", "Samuel Madden",
        ],
        "lesson": "Separate logical semantics, equivalence rules, statistics, physical plans, runtime adaptation, transactions, and observed execution receipts.",
    },
    "streaming_distributed": {
        "families": [
            "event_time_and_stream_semantics",
            "distributed_consensus_and_replication",
            "dataflow_checkpointing_and_recovery",
            "log_based_and_incremental_processing",
        ],
        "experts": [
            "Leslie Lamport", "Barbara Liskov", "Jeffrey Dean",
            "Sanjay Ghemawat", "Matei Zaharia", "Martin Kleppmann",
            "Tyler Akidau", "Paris Carbone", "Stephan Ewen",
            "Kostas Tzoumas", "Neha Narkhede", "Jay Kreps",
        ],
        "lesson": "Make event time, ordering, replay, checkpoint, delivery, durability, consistency, recovery, and side-effect semantics independently selectable and provable.",
    },
    "storage_lakehouse": {
        "families": [
            "storage_engine_architecture",
            "distributed_analytic_storage",
            "table_format_and_catalog_protocols",
            "transactional_and_cloud_data_management",
        ],
        "experts": [
            "Jim Gray", "David J. DeWitt", "Michael Franklin", "Michael Armbrust",
            "Reynold Xin", "Michael Cafarella", "Raghu Ramakrishnan",
            "Pat Helland", "Daniel Abadi", "Remzi Arpaci-Dusseau",
            "Margo Seltzer", "Donald Kossmann",
        ],
        "lesson": "Do not collapse file format, table protocol, catalog, storage engine, transaction protocol, deployment, or managed product into one type.",
    },
    "quality_lineage_cleaning": {
        "families": [
            "data_quality_constraints",
            "entity_resolution_and_integration",
            "lineage_provenance_and_explanation",
            "data_cleaning_and_debugging",
        ],
        "experts": [
            "Felix Naumann", "Ihab Ilyas", "Divesh Srivastava", "Paolo Papotti",
            "Xu Chu", "Theodoros Rekatsinas", "Alexandra Meliou", "Eugene Wu",
            "Juliana Freire", "Tova Milo", "Cong Yu", "Erhard Rahm",
        ],
        "lesson": "Separate detection, evidence, adjudication, correction, reconciliation, fitness-for-use, provenance, and explanation authority.",
    },
    "semantics_ontology": {
        "families": [
            "knowledge_representation_and_reasoning",
            "ontology_engineering_and_alignment",
            "conceptual_modeling_and_identity",
            "semantic_web_and_linked_data",
        ],
        "experts": [
            "Thomas Gruber", "Nicola Guarino", "Giancarlo Guizzardi",
            "Deborah McGuinness", "Ian Horrocks", "Pascal Hitzler",
            "Mark Musen", "Natasha Noy", "Steffen Staab", "Dieter Fensel",
            "Oscar Corcho", "Christopher Welty",
        ],
        "lesson": "Compile declared meanings, identity criteria, constraints, mappings, inference regimes, provenance, and inconsistency policies as separate governed artifacts.",
    },
    "causal_experimental_statistics": {
        "families": [
            "structural_causal_models",
            "potential_outcomes_and_design",
            "longitudinal_and_semiparametric_causal_inference",
            "heterogeneous_effects_and_policy_evaluation",
        ],
        "experts": [
            "Judea Pearl", "Donald Rubin", "Guido Imbens", "James Robins",
            "Miguel Hernan", "Elias Bareinboim", "Susan Athey",
            "Victor Chernozhukov", "Peter Spirtes", "Thomas Richardson",
            "Jennifer Hill", "Kosuke Imai",
        ],
        "lesson": "Require population, intervention, comparison, outcome, time, estimand, assumptions, identification, estimator, diagnostics, and uncertainty before execution.",
    },
    "forecasting_time_series": {
        "families": [
            "classical_time_series_and_state_space",
            "forecast_evaluation_and_combination",
            "hierarchical_and_reconciled_forecasting",
            "probabilistic_and_intermittent_forecasting",
        ],
        "experts": [
            "Rob Hyndman", "George Athanasopoulos", "Fotios Petropoulos",
            "James W. Taylor", "Spyros Makridakis", "Souhaib Ben Taieb",
            "Tao Hong", "Tilmann Gneiting", "Francis Diebold",
            "Siem Jan Koopman", "Andrew Harvey", "Everette Gardner",
        ],
        "lesson": "Expose horizon, information set, temporal availability, hierarchy, loss, backtest origin, benchmark, reconciliation, update cadence, and probabilistic calibration.",
    },
    "operations_research": {
        "families": [
            "linear_mixed_integer_and_conic_optimization",
            "constraint_programming_and_hybrid_search",
            "stochastic_robust_and_sequential_optimization",
            "routing_scheduling_and_network_optimization",
        ],
        "experts": [
            "Dimitris Bertsimas", "Pascal Van Hentenryck", "Andrea Lodi",
            "George Nemhauser", "Gerard Cornuejols", "Warren Powell",
            "Cynthia Barnhart", "Gilbert Laporte", "Michel Bierlaire",
            "Peter Stuckey", "Laurence Wolsey", "Alexander Shapiro",
        ],
        "lesson": "Keep problem variant, formulation, exactness, relaxation, search, heuristic, uncertainty, status, bound, certificate, tolerance, and budget explicit.",
    },
    "simulation_decision_analysis": {
        "families": [
            "discrete_event_and_agent_simulation",
            "monte_carlo_and_output_analysis",
            "simulation_optimization",
            "decision_analysis_and_multi_criteria_methods",
        ],
        "experts": [
            "Averill Law", "Barry Nelson", "Michael Fu", "Shane Henderson",
            "Sigrun Andradottir", "Stephen Chick", "Russell Cheng",
            "James R. Swisher", "Thomas Saaty", "Ralph Keeney", "Howard Raiffa",
            "James Evans",
        ],
        "lesson": "Represent model boundary, stochastic inputs, random stream, warm-up, replication, output estimator, decision criterion, preference model, and sensitivity analysis.",
    },
    "visualization_hci": {
        "families": [
            "visual_encoding_and_grammar",
            "interaction_and_visual_analytics",
            "perception_accessibility_and_uncertainty",
            "narrative_explanation_and_evaluation",
        ],
        "experts": [
            "Tamara Munzner", "Jeffrey Heer", "Ben Shneiderman", "John Stasko",
            "Jock Mackinlay", "Pat Hanrahan", "Fernanda Viegas",
            "Martin Wattenberg", "Jessica Hullman", "Miriah Meyer",
            "Robert Kosara", "Catherine Plaisant",
        ],
        "lesson": "Separate semantic query, result, visual encoding, interaction state, accessibility, uncertainty, explanation, narrative, and empirical evaluation.",
    },
    "spatial_scientific_media": {
        "families": [
            "spatial_databases_and_indexing",
            "trajectory_raster_and_coverage_analytics",
            "scientific_arrays_and_workflows",
            "multimedia_content_and_similarity",
        ],
        "experts": [
            "Michael Goodchild", "Hanan Samet", "Erik G. Hoel", "Markus Schneider",
            "Mohamed Mokbel", "Shashi Shekhar", "Peter Baumann", "Bertram Ludascher",
            "Alexander Szalay", "Valerio Pascucci", "Claudio T. Silva",
            "Ramesh Jain",
        ],
        "lesson": "Keep coordinate reference, topology, coverage support, resolution, uncertainty, array chunking, workflow provenance, media representation, and similarity semantics explicit.",
    },
    "compression_encoding": {
        "families": [
            "lossless_and_entropy_coding",
            "succinct_indexes_and_compressed_text",
            "integer_columnar_and_bitmap_encoding",
            "schema_based_binary_serialization",
        ],
        "experts": [
            "David A. Huffman", "Jacob Ziv", "Abraham Lempel", "Paolo Ferragina",
            "Giovanni Manzini", "Gonzalo Navarro", "Daniel Lemire",
            "Alistair Moffat", "Sebastian Wild", "Julien Le Dem",
            "Doug Cutting", "Kenton Varda",
        ],
        "lesson": "Model semantic carrier, logical value, encoding, framing, layout, container, codec, loss contract, random access, evolution, and decoder compatibility separately.",
    },
    "privacy_security_trust": {
        "families": [
            "differential_privacy_and_accounting",
            "secure_computation_and_cryptographic_data_processing",
            "access_control_policy_and_information_flow",
            "privacy_context_identity_and_governance",
        ],
        "experts": [
            "Cynthia Dwork", "Aaron Roth", "Frank McSherry", "Kunal Talwar",
            "Vitaly Shmatikov", "Helen Nissenbaum", "Latanya Sweeney",
            "Kobbi Nissim", "Adam D. Smith", "Dawn Song", "Jean-Pierre Hubaux",
            "George Danezis",
        ],
        "lesson": "Separate identity, authentication, authorization, approval, enforcement, purpose, consent, privacy loss, cryptographic claim, audit evidence, and governance authority.",
    },
    "compiler_runtime_reliability": {
        "families": [
            "compiler_ir_and_program_transformation",
            "parallel_runtime_and_hardware_mapping",
            "distributed_reliability_and_failure_semantics",
            "testing_verification_and_performance_diagnosis",
        ],
        "experts": [
            "Chris Lattner", "Vikram Adve", "Saman Amarasinghe", "Torsten Hoefler",
            "Emery Berger", "John Regehr", "George Candea", "Peter Alvaro",
            "Peter Bailis", "Rodrigo Fonseca", "Arvind", "Todd Mytkowicz",
        ],
        "lesson": "Preserve typed IR, legality, equivalence, capability negotiation, target qualification, resource effects, cancellation, failure, replay, reproducibility, and proof receipts.",
    },
}


def rows():
    result = []
    for domain, group in FAMILY_GROUPS.items():
        families = group["families"]
        for index, name in enumerate(group["experts"]):
            result.append({
                "name": name,
                "domain": domain,
                "family": families[index // 3],
                "secondary_families": [families[(index // 3 + 1) % len(families)]],
                "compiler_lesson": group["lesson"],
            })
    return result


if __name__ == "__main__":
    data = rows()
    assert len(data) == 180, len(data)
    assert len({row["name"] for row in data}) == 180
    assert len({row["family"] for row in data}) == 60
    print(f"{len(data)} expert seeds; {len({row['family'] for row in data})} families")
