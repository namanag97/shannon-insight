#!/usr/bin/env python3
"""Build an evidence-backed semantic slice for deterministic operations research."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
SEM = HERE.parent
REGISTRY = SEM.parents[1]
AS_OF = "2026-08-27"

AXES = [
    "semantic_object", "semantic_role", "identity_and_equality", "grain_and_cardinality",
    "state_and_change", "time", "order_and_topology", "partiality_and_uncertainty",
    "authority_and_trust", "effect_boundary", "representation", "composition_algebra",
    "compatibility_and_evolution", "resources_and_failure", "evidence_and_conformance",
    "privacy_security_safety",
]

LIBRARIES = [
    "library.method_kernels.operations_research_bridge",
    "library.operations_research.constraint_policy_algebra",
    "library.operations_research.decision_problem_semantics",
    "library.operations_research.heuristic_search_contract",
    "library.operations_research.infeasibility_diagnosis",
    "library.operations_research.objective_preference_algebra",
    "library.operations_research.optimization_model_ir",
    "library.operations_research.optimization_result_algebra",
    "library.operations_research.optimization_solution_validation",
    "library.operations_research.optimization_solve_execution",
    "library.operations_research.queue_inference_calibration",
    "library.operations_research.queue_model_semantics",
    "library.operations_research.queue_model_validation",
    "library.operations_research.queue_network_methods",
    "library.operations_research.queue_performance_methods",
    "library.operations_research.simulation_execution",
    "library.operations_research.simulation_experiment_design",
    "library.operations_research.simulation_model_semantics",
    "library.operations_research.simulation_output_analysis",
    "library.operations_research.simulation_random_stream_control",
    "library.operations_research.simulation_verification_validation",
    "library.operations_research.solver_capability_contract",
]


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def slug(value: str) -> str:
    return value.replace("_", "-").replace(".", "-")


def sources() -> list[dict[str, Any]]:
    rows = [
        ("moi-solutions", "MathOptInterface — Solutions", ["JuMP / MathOptInterface contributors"], 2026, "official_interface_specification", "https://jump.dev/MathOptInterface.jl/stable/manual/solutions/", "Separates termination status, result count, primal status, dual status, objective value, bound and certificate semantics.", "An interface taxonomy reports solver claims; it does not independently prove a result or select tolerances."),
        ("moi-models", "MathOptInterface — Models", ["JuMP / MathOptInterface contributors"], 2026, "official_interface_specification", "https://jump.dev/MathOptInterface.jl/stable/manual/models/", "Defines a provider-neutral model interface over typed functions, sets, attributes and supported capabilities.", "The interface does not establish the business meaning or authority of a decision problem."),
        ("minizinc-flatzinc", "MiniZinc Handbook — FlatZinc solver interface", ["MiniZinc project"], 2026, "official_language_specification", "https://docs.minizinc.dev/en/stable/fzn-spec.html", "Separates satisfy, minimize and maximize solve items, assignments and complete-search result markers.", "A modeling language does not make all solver transformations lossless or all returned assignments acceptable decisions."),
        ("ortools-cpsat", "OR-Tools CP-SAT solver status contract", ["Google OR-Tools", "Laurent Perron", "Frédéric Didier"], 2025, "official_solver_documentation", "https://developers.google.com/optimization/cp/cp_solver", "Distinguishes OPTIMAL, FEASIBLE, INFEASIBLE, MODEL_INVALID and UNKNOWN outcomes.", "CP-SAT statuses apply to that admitted model and run; they are not a universal result algebra or independent proof."),
        ("google-mathopt", "Google MathOpt solve result protocol", ["Google Operations Research"], 2024, "official_api_specification", "https://developers.google.com/optimization/service/reference/rest/v1/mathopt/solveMathOptModel", "Separates solver termination, solution feasibility claims, primal/dual problem statuses and objective bounds.", "The protocol explicitly permits un-certified solver claims and therefore cannot be treated as validation evidence by itself."),
        ("highs", "HiGHS high-performance linear optimization software", ["Julian Hall", "HiGHS contributors"], 2026, "official_reference_implementation", "https://highs.dev/", "Provides an open implementation family for sparse LP, MIP and QP with serial and parallel algorithms.", "One implementation cannot own provider-neutral optimization semantics or satisfy independent-implementation qualification alone."),
        ("exact-rational-mip", "A computational status update for exact rational mixed integer programming", ["Leon Eifler", "Ambros Gleixner"], 2022, "peer_reviewed_primary_research", "https://doi.org/10.1007/s10107-021-01749-5", "Combines exact repair, rational LP refinement and independently verifiable optimality certificates while measuring computational cost.", "The evaluated framework covers a bounded selection of MIP methods and does not make every solver result exact."),
        ("vipr", "VIPR — Verifying Integer Programming Results", ["Kevin K. H. Cheung", "Ambros Gleixner", "Daniel E. Steffy", "Leon Eifler"], 2024, "official_certificate_specification_and_checker", "https://github.com/scipopt/vipr", "Specifies and checks exact-rational certificates for bounded classes of mixed-integer programming results.", "A valid certificate proves only its encoded instance and supported derivation rules; incomplete derivations and unsupported cuts remain explicit."),
        ("scip-exact", "SCIP 10 — numerically exact solving mode", ["SCIP Optimization Suite contributors"], 2026, "official_reference_implementation_documentation", "https://www.scipopt.org/doc-10.0.0/html/EXACT.php", "Exposes exact rational solving, safe plugin requirements and optional VIPR proof logging with known completion constraints.", "Exact mode and proof logging still require configuration, supported plugins, certificate completion and an independent checker."),
        ("cp-proof-logging", "A Multi-Stage Proof Logging Framework to Certify the Correctness of CP Solvers", ["Maarten Flippo", "Konstantin Sidorov", "Imko Marijnissen", "Jeff Smits", "Emir Demirović"], 2024, "peer_reviewed_primary_research", "https://doi.org/10.4230/LIPIcs.CP.2024.11", "Introduces solver proof scaffolds completed and checked in stages for constraint programming.", "The framework is an innovation candidate, not evidence that current CP providers universally emit complete proofs."),
        ("little-law", "A Proof for the Queuing Formula: L = λW", ["John D. C. Little"], 1961, "foundational_peer_reviewed_research", "https://doi.org/10.1287/opre.9.3.383", "States explicit finiteness, stationarity, transitivity and nonzero-rate conditions for the queueing conservation relation.", "Satisfaction of L=λW does not identify arrival/service distributions, stability, bottlenecks or causes."),
        ("whitt-little-law", "A review of L = λW and extensions", ["Ward Whitt"], 1991, "peer_reviewed_synthesis", "https://www.columbia.edu/~ww2040/ReviewLlamW91.pdf", "Separates time/customer averages and explains sample-path, distributional, network and conservation-law extensions.", "The review does not authorize a fitted queue model or make one average relation a complete model-validation oracle."),
        ("sargent-vv", "Verification and validation of simulation models", ["Robert G. Sargent"], 2013, "peer_reviewed_primary_methodology", "https://doi.org/10.1057/jos.2012.20", "Separates conceptual-model validity, data validity, computerized-model verification and operational validity.", "Validation is purpose- and evidence-scoped; it is not proof that a simulation is the real system."),
        ("wsc-output", "A practical introduction to analysis of simulation output data", ["Christine S. M. Currie", "Russell C. H. Cheng"], 2016, "peer_reviewed_tutorial", "https://informs-sim.org/wsc16papers/013.pdf", "Distinguishes terminating and steady-state output analysis, warm-up, replication and alternative comparison.", "A tutorial constrains method choices but does not select an experiment design or justify independence for a particular run."),
        ("rngstreams", "RngStreams — MRG32k3a streams and substreams", ["Pierre L'Ecuyer", "University of Montreal"], 2026, "official_reference_implementation_and_primary_research", "https://github.com/umontreal-simul/RngStreams", "Defines reproducible long streams/substreams backed by a studied combined multiple recursive generator.", "A seed or stream identifier alone does not prove statistical independence or reproduce model code, schedules and environments."),
        ("asme-vvuq", "ASME VVUQ standards program", ["ASME"], 2026, "standards_program", "https://www.asme.org/codes-standards/publications-information/verification-validation-uncertainty", "Maintains separate terminology, verification, validation and uncertainty-quantification standards for scoped modeling domains.", "Domain-specific VVUQ standards do not automatically validate enterprise discrete-event simulations or optimization models."),
        ("des-reproducibility", "On the reproducibility of discrete-event simulation studies in health research", ["Amy Heather", "Thomas Monks", "Alison Harper", "Navonil Mustafee", "Andrew Mayne"], 2025, "peer_reviewed_empirical_research", "https://doi.org/10.1080/17477778.2025.2552177", "Empirically tests computational reproducibility of open healthcare DES models and identifies edition, parameter, code, licensing and output-generation barriers.", "Evidence from eight models in one application field does not define universal simulation validity or guarantee computational reproducibility."),
    ]
    return [{"source_id": f"source.or.{sid}", "title": title, "authors_or_publisher": authors, "year": year, "source_kind": kind, "url": url, "bounded_implication": implication, "authority_limit": limit} for sid,title,authors,year,kind,url,implication,limit in rows]


def modules() -> list[dict[str, Any]]:
    rows = [
        ("decision-problem", "What decision, alternatives, horizon, affected parties and admissible evidence define the problem before mathematical encoding?", "decision semantics and authority envelope", ["moi-models"], []),
        ("constraint-policy", "Which conditions are hard, soft or probabilistic, and who may propose versus authorize relaxation?", "typed constraint and authority algebra", ["minizinc-flatzinc"], ["decision-problem"]),
        ("objective-preference", "How are objectives, priorities, lexicographic orders and Pareto relations represented without inventing utility?", "preorder and multi-objective algebra", ["minizinc-flatzinc"], ["decision-problem"]),
        ("optimization-model-ir", "How is a decision problem lowered into typed variables, domains, expressions, constraints, objectives and required features with declared loss?", "typed optimization IR", ["moi-models", "minizinc-flatzinc"], ["constraint-policy", "objective-preference"]),
        ("solver-capability", "Can a provider satisfy the exact model features, numeric, certificate, resource and target requirements?", "requirement/offer matching algebra", ["moi-models", "google-mathopt"], ["optimization-model-ir"]),
        ("solve-execution", "How is bounded optimization execution started, progressed, cancelled and receipted without changing result semantics?", "bounded runtime state machine", ["moi-solutions", "ortools-cpsat"], ["solver-capability"]),
        ("optimization-result", "What independently typed termination, result-count, primal, dual, bound, gap, ray and certificate claims did a run return?", "product result/status algebra", ["moi-solutions", "google-mathopt", "ortools-cpsat"], ["solve-execution"]),
        ("solution-validation", "Does a returned point, bound or certificate satisfy the admitted model under a named numeric/exact oracle?", "independent conformance oracle", ["vipr", "exact-rational-mip", "scip-exact"], ["optimization-result"]),
        ("heuristic-search", "How are representation, neighborhood, acceptance, diversification, repair, budgets and replay evidence exposed for non-proof search?", "budgeted search transition system", ["ortools-cpsat"], ["optimization-model-ir"]),
        ("infeasibility-diagnosis", "Which conflicts, IIS candidates, relaxations and repairs explain an infeasibility claim without asserting a unique cause or authority?", "conflict and repair-proposal algebra", ["moi-solutions", "google-mathopt"], ["optimization-result", "constraint-policy"]),
        ("queue-model", "What customer classes, arrivals, services, resources, disciplines, capacities, routing and abandonment define a queueing system?", "stochastic process/network semantics", ["little-law", "whitt-little-law"], ["decision-problem"]),
        ("queue-calibration", "How are arrival, service, routing and abandonment assumptions inferred from censored, time-varying observations?", "statistical estimation with residuals", ["whitt-little-law"], ["queue-model"]),
        ("queue-performance", "Which occupancy, waiting, sojourn, throughput, service-level and utilization measures are valid under which averaging regime?", "queue measure algebra", ["little-law", "whitt-little-law"], ["queue-model"]),
        ("queue-network", "How do classes, stations, routing, blocking and synchronization compose into a queueing network?", "open/closed queue network composition", ["whitt-little-law"], ["queue-model"]),
        ("queue-validation", "Which conservation, stability, distributional and predictive checks support or falsify a fitted queue model?", "scoped queue conformance oracle", ["little-law", "whitt-little-law"], ["queue-calibration", "queue-performance"]),
        ("simulation-model", "What conceptual entities, state, events, resources, processes, time advance and input distributions constitute the simulation model?", "simulation model semantics", ["sargent-vv", "asme-vvuq"], ["decision-problem"]),
        ("simulation-design", "Which scenarios, factors, responses, warm-up, horizon, replication, variance-reduction and stopping rules define an experiment?", "statistical experiment contract", ["wsc-output"], ["simulation-model"]),
        ("random-stream-control", "How are generator, seed, stream, substream and allocation policies bound to stochastic inputs?", "random-stream allocation algebra", ["rngstreams", "des-reproducibility"], ["simulation-design"]),
        ("simulation-execution", "How are simulations run, cancelled, checkpointed and receipted under explicit schedule and resource semantics?", "bounded simulation runtime state machine", ["des-reproducibility"], ["simulation-design", "random-stream-control"]),
        ("simulation-output", "How are transient/steady-state outputs, dependence, censoring, uncertainty and comparisons analyzed?", "statistical output-analysis algebra", ["wsc-output"], ["simulation-execution"]),
        ("simulation-vv", "How are conceptual validity, data validity, computerized-model verification, operational validity and uncertainty kept distinct?", "claim-evidence VVUQ graph", ["sargent-vv", "asme-vvuq"], ["simulation-model", "simulation-output"]),
        ("proof-logging", "How can a solver emit a bounded derivation for an independent checker without equating execution with proof?", "certificate language and checker", ["vipr", "cp-proof-logging", "scip-exact"], ["optimization-result"]),
        ("finding-handoff", "How does an OR result remain a scoped recommendation or finding until an external authority acts?", "claim-evidence-residual envelope", ["google-mathopt", "sargent-vv"], ["solution-validation", "queue-validation", "simulation-vv"]),
        ("or-bridge", "How are decision, method and result references composed without assigning semantic ownership to a facade?", "typed reference resolver", ["moi-models", "sargent-vv"], ["decision-problem", "finding-handoff"]),
    ]
    return [{"module_id":f"module.or.{mid}","question":question,"formalism":formalism,"source_refs":[f"source.or.{s}" for s in srcs],"imports":[f"module.or.{x}" for x in imports],"status":"EVIDENCE_BACKED_CANDIDATE_OWNER_UNRATIFIED"} for mid,question,formalism,srcs,imports in rows]


LIBRARY_MODULES = {
    "library.method_kernels.operations_research_bridge":["or-bridge"],
    "library.operations_research.constraint_policy_algebra":["constraint-policy"],
    "library.operations_research.decision_problem_semantics":["decision-problem"],
    "library.operations_research.heuristic_search_contract":["heuristic-search"],
    "library.operations_research.infeasibility_diagnosis":["infeasibility-diagnosis"],
    "library.operations_research.objective_preference_algebra":["objective-preference"],
    "library.operations_research.optimization_model_ir":["optimization-model-ir"],
    "library.operations_research.optimization_result_algebra":["optimization-result", "proof-logging"],
    "library.operations_research.optimization_solution_validation":["solution-validation", "proof-logging"],
    "library.operations_research.optimization_solve_execution":["solve-execution"],
    "library.operations_research.queue_inference_calibration":["queue-calibration"],
    "library.operations_research.queue_model_semantics":["queue-model"],
    "library.operations_research.queue_model_validation":["queue-validation"],
    "library.operations_research.queue_network_methods":["queue-network"],
    "library.operations_research.queue_performance_methods":["queue-performance"],
    "library.operations_research.simulation_execution":["simulation-execution"],
    "library.operations_research.simulation_experiment_design":["simulation-design"],
    "library.operations_research.simulation_model_semantics":["simulation-model"],
    "library.operations_research.simulation_output_analysis":["simulation-output"],
    "library.operations_research.simulation_random_stream_control":["random-stream-control"],
    "library.operations_research.simulation_verification_validation":["simulation-vv"],
    "library.operations_research.solver_capability_contract":["solver-capability"],
}


def laws() -> list[dict[str, Any]]:
    rows = [
        ("decision-is-not-model", "A decision problem is not its optimization, queueing or simulation encoding; lowering must declare exclusions and loss.", ["moi-models", "sargent-vv"]),
        ("hard-soft-chance-distinct", "Hard, soft and chance constraints have different satisfaction and authority semantics.", ["minizinc-flatzinc"]),
        ("relaxation-is-not-authority", "A relaxation or repair proposal cannot change policy without an external relaxation authority.", ["google-mathopt"]),
        ("objective-is-not-preference", "An objective expression, achieved value, preference order and utility judgment are distinct.", ["minizinc-flatzinc"]),
        ("feasible-is-not-optimal", "A feasible point is not an optimal point and a locally solved result is not global optimality.", ["moi-solutions", "ortools-cpsat"]),
        ("incumbent-is-not-bound", "A primal incumbent and an objective bound constrain different sides of the unknown optimum.", ["moi-solutions", "google-mathopt"]),
        ("termination-is-not-result", "Why execution stopped, whether a result exists, and the primal/dual status of each result are independent coordinates.", ["moi-solutions"]),
        ("solver-claim-is-not-validation", "A solver status or feasibility claim is not an independently checked solution or certificate.", ["google-mathopt", "vipr"]),
        ("timeout-is-not-infeasible", "A time, memory, node, iteration or custom limit cannot be reported as proven infeasibility.", ["moi-solutions", "ortools-cpsat"]),
        ("infeasible-unbounded-unknown-distinct", "Infeasible, unbounded, infeasible-or-unbounded, no-result and unknown outcomes must remain distinct.", ["moi-solutions", "google-mathopt"]),
        ("conflict-is-not-root-cause", "An IIS or conflict is neither necessarily unique nor a causal explanation of the world problem.", ["google-mathopt"]),
        ("heuristic-is-not-proof", "A heuristic best-known solution or search exhaustion under a budget is not an optimality proof.", ["ortools-cpsat"]),
        ("seed-is-not-reproduction", "A seed or stream identifier cannot reproduce a run without model, code, configuration, generator, allocation, schedule and environment identity.", ["rngstreams", "des-reproducibility"]),
        ("stream-is-not-independence", "Distinct random-stream identifiers do not by themselves prove statistical independence.", ["rngstreams"]),
        ("observation-is-not-queue-model", "Observed arrivals, departures and occupancy do not uniquely determine queue classes, disciplines, service processes or routing.", ["whitt-little-law"]),
        ("little-law-is-not-validity", "Agreement with L=λW is a scoped conservation check, not proof of stationarity, stability or complete model validity.", ["little-law", "whitt-little-law"]),
        ("utilization-is-not-bottleneck", "High utilization is not by itself a bottleneck diagnosis or causal root cause.", ["whitt-little-law"]),
        ("queue-stability-is-not-performance", "A stable queue can still violate latency, loss, fairness or service-level objectives.", ["whitt-little-law"]),
        ("simulation-is-not-world", "A simulation model and execution are representations of an intended use, not the real system or future truth.", ["sargent-vv", "asme-vvuq"]),
        ("verification-is-not-validation", "Correct implementation of a conceptual model is distinct from evidence that the model is adequate for its intended use.", ["sargent-vv", "asme-vvuq"]),
        ("replication-is-not-independent-implementation", "Repeated runs with different random streams are not independent implementations of the model or engine.", ["wsc-output"]),
        ("warmup-is-not-censoring-default", "Warm-up deletion, termination horizon, censoring and initial-state policies must be explicit and cannot be silently inferred.", ["wsc-output"]),
        ("scenario-comparison-is-not-causal-effect", "A simulation or optimization scenario difference is not an identified causal effect in the world.", ["wsc-output", "sargent-vv"]),
        ("capability-is-not-semantic-support", "A provider name or broad solver class does not satisfy an exact feature, numeric, certificate, target and resource requirement.", ["moi-models", "google-mathopt"]),
        ("proof-log-is-not-universal-proof", "A checked proof log establishes only the admitted instance, rules, checker and certificate completeness.", ["vipr", "cp-proof-logging", "scip-exact"]),
        ("result-is-not-authorized-action", "An optimal, validated or simulated result remains a finding until an external decision authority accepts and acts on it.", ["google-mathopt", "sargent-vv"]),
    ]
    return [{"law_id":f"law.or.{lid}","statement":statement,"source_refs":[f"source.or.{x}" for x in refs],"status":"EVIDENCE_BACKED_CANDIDATE_OWNER_UNRATIFIED","completion_claim":False} for lid,statement,refs in rows]


def methods() -> list[dict[str, Any]]:
    rows = [
        ("decision-framing","decision","world alternatives and authority","decision problem plus assumption ledger","not a mathematical model"),
        ("linear-programming","optimization","linear model","primal/dual results and bounds","continuous linear class only"),
        ("mixed-integer-programming","optimization","linear model with integrality","incumbent, bound, gap and certificate candidates","global claim requires proof semantics"),
        ("quadratic-convex-optimization","optimization","quadratic/conic model","solution and dual evidence","convexity and numeric regime explicit"),
        ("nonlinear-local-optimization","optimization","nonlinear model and start","stationary/local result","not global optimality"),
        ("constraint-programming","optimization","finite-domain constraint model","assignment/status/proof candidate","search and propagation semantics explicit"),
        ("multi-objective-optimization","optimization","objectives and preference relation","Pareto/lexicographic result set","no implicit scalar utility"),
        ("robust-optimization","optimization","uncertainty set and robust policy","robust-feasible solution","uncertainty-set validity external"),
        ("stochastic-programming","optimization","scenario/probability model","policy and stochastic objective","sampling error explicit"),
        ("dynamic-programming","optimization","state/action/transition/value model","policy/value result","state and horizon assumptions explicit"),
        ("branch-and-bound","exact_search","model plus branching/bounding rules","incumbent, bound, proof tree","proof depends on numeric and pruning soundness"),
        ("cutting-plane","exact_search","relaxation and valid inequalities","strengthened bound/certificate derivation","cut validity must be checkable"),
        ("local-search","heuristic","solution encoding and neighborhood","best-known solution and trace","no optimality claim"),
        ("metaheuristic","heuristic","search policy, randomness and budget","best-known portfolio result","replay and stopping semantics explicit"),
        ("large-neighborhood-search","heuristic","incumbent, destroy and repair operators","iterative incumbent result","repair failure and budget explicit"),
        ("constraint-relaxation","diagnostic","infeasible model and authority profile","ranked relaxation proposals","proposal is not authorization"),
        ("iis-conflict-analysis","diagnostic","infeasibility claim/model","conflict or IIS candidates","not necessarily unique or causal"),
        ("solution-certificate-checking","validation","model, result and certificate","checked bounded claim","checker/rule scope explicit"),
        ("mm1-queue-analysis","queueing","declared M/M/1 assumptions","stationary measures","distribution and stability assumptions explicit"),
        ("gg1-queue-approximation","queueing","general interarrival/service summaries","approximate delay measures","approximation residual explicit"),
        ("multi-server-queue-analysis","queueing","class, arrival, service and server model","occupancy/wait/service measures","discipline and abandonment explicit"),
        ("queue-network-analysis","queueing","stations, classes and routing","network performance measures","open/closed/blocking semantics explicit"),
        ("queue-inference","queueing","censored event observations","arrival/service/routing estimates","identifiability and drift explicit"),
        ("queue-conservation-validation","queueing","matched arrivals/departures/occupancy","conservation residuals","not complete model validation"),
        ("discrete-event-simulation","simulation","event/state/resource process model","time-ordered run observations","event ordering and tie-breaking explicit"),
        ("monte-carlo-simulation","simulation","probability model and sampling plan","sample estimates","stream allocation and error explicit"),
        ("agent-based-simulation","simulation","agent rules and interaction topology","emergent run observations","not LLM-dependent; micro rules are assumptions"),
        ("system-dynamics-simulation","simulation","stocks, flows and equations","trajectory estimates","structural/parameter validity explicit"),
        ("terminating-output-analysis","simulation_analysis","finite-horizon independent replications","estimates and intervals","horizon/censoring explicit"),
        ("steady-state-output-analysis","simulation_analysis","nonterminating stochastic run","steady-state estimates","warm-up, batching and dependence explicit"),
        ("variance-reduction","simulation_analysis","coupled stream/allocation design","lower-variance comparison","coupling and unbiasedness conditions explicit"),
        ("simulation-experiment-design","simulation_analysis","factors, scenarios and response plan","comparison/response surface evidence","multiplicity and stopping explicit"),
        ("conceptual-model-validation","simulation_vv","conceptual model and intended use","validity evidence/defeaters","not code verification"),
        ("computerized-model-verification","simulation_vv","implemented model and specification","verification evidence","not world validity"),
        ("operational-validation","simulation_vv","outputs and system evidence","purpose-scoped adequacy claim","not universal truth"),
    ]
    return [{"method_id":f"method.or.{mid}","method_class":klass,"input_semantics":inp,"output_semantics":out,"authority_limit":limit,"status":"RESEARCHED_METHOD_BOUNDARY_CANDIDATE"} for mid,klass,inp,out,limit in rows]


def experts() -> list[dict[str, Any]]:
    rows = [
        ("john-little","John D. C. Little",["little-law"],["State the averaging regime and theorem assumptions.","Use conservation laws as falsifiers, not complete models."]),
        ("ward-whitt","Ward Whitt",["whitt-little-law"],["Keep customer averages, time averages and distributional extensions distinct.","Model nonstationarity and network/class scope explicitly."]),
        ("robert-sargent","Robert G. Sargent",["sargent-vv"],["Separate conceptual validity, data validity, code verification and operational validity.","Bind validation to intended use and document defeaters."]),
        ("pierre-lecuyer","Pierre L'Ecuyer",["rngstreams"],["Treat random streams and substreams as allocated semantic resources.","Record generator, state and allocation rather than only a seed."]),
        ("amy-heather","Amy Heather",["des-reproducibility"],["Treat model code, parameters, environment, scenario runners and output-generation code as one reproducibility closure.","Test reported results by executing shared artifacts rather than inferring reproducibility from availability."]),
        ("julian-hall","Julian Hall",["highs"],["Separate high-performance provider engineering from provider-neutral contracts.","Qualify sparse LP/MIP/QP capabilities individually."]),
        ("ambros-gleixner","Ambros Gleixner",["exact-rational-mip","vipr"],["Keep fast floating execution distinct from exact repair and independent checking.","Make proof formats and checker scope first-class outputs."]),
        ("leon-eifler","Leon Eifler",["exact-rational-mip","vipr"],["Expose numerical rigor as a selectable contract with measured cost.","Do not label a result exact when unsupported derivations remain."]),
        ("laurent-perron","Laurent Perron",["ortools-cpsat"],["Return FEASIBLE separately from OPTIMAL and UNKNOWN separately from INFEASIBLE.","Validate models before search and expose bounded search status."]),
        ("oscar-dowson","Oscar Dowson",["moi-solutions","moi-models"],["Use product result/status types rather than one overloaded solver status.","Make solver bridges document exact status mappings and supported attributes."]),
        ("christine-currie","Christine S. M. Currie",["wsc-output"],["Treat stochastic output as dependent experimental data.","Design warm-up and replication rather than applying ordinary formulas blindly."]),
        ("kevin-cheung","Kevin K. H. Cheung",["vipr"],["Emit independently checkable result evidence.","Version certificate grammar and distinguish completion from checking."]),
    ]
    return [{"expert_id":f"expert.or.{eid}","name":name,"contribution_refs":[f"source.or.{x}" for x in refs],"learnable_design_laws":lessons,"authority_limit":"Expert work constrains candidates; it does not make the expert SAN's semantic or operational owner."} for eid,name,refs,lessons in rows]


def innovations() -> list[dict[str, Any]]:
    rows = [
        ("exact-rational-mip-at-practical-scale",2022,["exact-rational-mip"],"Exact repair, rational LP refinement and certificate production substantially improve rigorous MIP solving while retaining explicit cost."),
        ("product-status-result-algebra",2023,["moi-solutions","google-mathopt"],"Modern provider-neutral interfaces expose termination, primal/dual feasibility, result count, bounds and certificates as separate coordinates."),
        ("safe-verified-gomory-cuts",2024,["vipr"],"VIPR 1.1 supports incomplete derivations and verified rational cutting-plane workflows rather than opaque optimality claims."),
        ("multi-stage-cp-proof-logging",2024,["cp-proof-logging"],"Constraint solvers can emit lightweight proof scaffolds for later completion and independent formal checking."),
        ("simulation-reproducibility-contracts",2025,["des-reproducibility"],"Empirical DES reproducibility work makes software editions, estimation, model sharing and random-stream allocation auditable inputs."),
        ("exact-scip-with-proof-output",2026,["scip-exact"],"SCIP 10 integrates exact arithmetic, safe-plugin constraints and optional proof output with explicit certificate-completion limitations."),
        ("open-high-performance-solver-substitution",2026,["highs"],"A mature open LP/MIP/QP provider broadens independent implementation and removable-provider options for enterprise optimization."),
    ]
    return [{"innovation_id":f"innovation.or.{iid}","year":year,"source_refs":[f"source.or.{x}" for x in refs],"core_delta":delta,"ai_or_llm_dependency":False,"status":"EVIDENCE_BACKED_INNOVATION_CANDIDATE"} for iid,year,refs,delta in rows]


AXIS_QUESTIONS = {
    "semantic_object":"Which decision problems, policies, models, runs, solutions, bounds, certificates, queue systems, simulations and findings are distinct subjects?",
    "semantic_role":"Which objects are requirements, assumptions, observations, models, offers, executions, claims, evidence, proposals or authorized decisions?",
    "identity_and_equality":"What identifies a problem, model edition, configuration, provider offer, run, stream, result, certificate and validation receipt, and under which equivalence?",
    "grain_and_cardinality":"What are the variable, constraint, objective, scenario, class, station, replication, observation and result multiplicities?",
    "state_and_change":"Which model/run/search/queue/simulation/validation states exist and which transitions are legal, terminal, resumable or superseding?",
    "time":"Which decision horizon, event/simulation time, wall time, validity time, observation window, warm-up and stopping time govern each claim?",
    "order_and_topology":"Which preference, event, search, queue-network, causal-assumption and proof-derivation orders or graphs are asserted?",
    "partiality_and_uncertainty":"How are unknown, no-result, approximate, censored, sampled, interval, gap, residual and invalid-model outcomes represented and propagated?",
    "authority_and_trust":"Who may define objectives, constraints, relaxations, assumptions, tolerances, acceptance criteria and operational adoption?",
    "effect_boundary":"How are pure model/analysis/validation functions separated from compute execution, publication and business mutation?",
    "representation":"Which model, solver, certificate, queue, simulation, trace and receipt carriers are used and what translation loss is declared?",
    "composition_algebra":"Under which preconditions do decision, model, capability, execution, result, validation and finding modules compose?",
    "compatibility_and_evolution":"What changes preserve decision, model, provider, numeric, experiment, result, certificate and evidence compatibility, and what requires rerun?",
    "resources_and_failure":"What finite time, memory, nodes, iterations, scenarios, replications, proof size and cancellation bounds apply, and which partial outcomes survive?",
    "evidence_and_conformance":"Which fixtures, exact small cases, proof checkers, conservation laws, calibration residuals, V&V evidence and independent implementations support each claim?",
    "privacy_security_safety":"What sensitive inputs, affected parties, adversarial models, harmful recommendations and unsafe actuation paths exist, and who controls disclosure/action?",
}


def boundary_findings(products_by_library: dict[str, set[str]]) -> list[dict[str, Any]]:
    queue_libs = sorted(x for x in LIBRARIES if ".queue_" in x)
    return [
        {"finding_id":"finding.or.optimization-product-cohesion.v1","subject_refs":sorted(x for x in LIBRARIES if products_by_library[x]=={"product.optimization_solver"}),"current_product_refs":["product.optimization_solver"],"candidate_disposition":"RETAIN_PRODUCT_BUT_REQUIRE_DECISION_AND_FINDING_IMPORTS","reason":"The current nine-library solver product coherently spans model, execution, result and validation, but decision framing and non-authoritative handoff are shared imports rather than solver-owned semantics.","owner_decision":"UNRATIFIED"},
        {"finding_id":"finding.or.simulation-product-cohesion.v1","subject_refs":sorted(x for x in LIBRARIES if products_by_library[x]=={"product.simulation_environment"}),"current_product_refs":["product.simulation_environment"],"candidate_disposition":"RETAIN_PRODUCT_WITH_VV_SEAMS_EXPLICIT","reason":"Model, experiment, randomness, execution, output and V&V form a coherent environment only while their non-collapse laws remain public seams.","owner_decision":"UNRATIFIED"},
        {"finding_id":"finding.or.queue-capability-boundary.v1","subject_refs":queue_libs,"current_product_refs":[],"candidate_disposition":"CAPABILITY_OR_WORKBENCH_BOUNDARY_RESEARCH_REQUIRED","reason":"Five cohesive queueing libraries have no declared product consumer in the captured graph. Queueing is a reusable analytical capability; evidence does not yet justify a standalone product versus imports into simulation, capacity and process products.","owner_decision":"UNRATIFIED"},
        {"finding_id":"finding.or.decision-shared-primitive.v1","subject_refs":["library.operations_research.decision_problem_semantics"],"current_product_refs":[],"candidate_disposition":"SHARED_SEMANTIC_PRIMITIVE_IMPORT_REQUIRED","reason":"Decision framing precedes optimization, queueing and simulation and therefore must not be owned by the optimization solver or simulation runtime.","owner_decision":"UNRATIFIED"},
        {"finding_id":"finding.or.bridge-composition-only.v1","subject_refs":["library.method_kernels.operations_research_bridge"],"current_product_refs":[],"candidate_disposition":"COMPOSITION_ONLY_NO_SEMANTIC_OWNERSHIP","reason":"The bridge may resolve method/result references but must not absorb decision, model, result, validation or authority semantics.","owner_decision":"UNRATIFIED"},
    ]


def build() -> dict[str, Any]:
    source_rows=sources(); module_rows=modules(); law_rows=laws(); method_rows=methods(); expert_rows=experts(); innovation_rows=innovations()
    contributions={row["library_id"]:row for row in load_jsonl(REGISTRY/"library-contributions.jsonl")}
    coordinate_dockets={row["library_ref"]:row for row in load_jsonl(SEM/"library_coordinate_binding_projection/library-coordinate-binding-dockets.jsonl")}
    exact_dockets={row["library_ref"]:row for row in load_jsonl(SEM/"p5_exact_contract_adjudication/exact-contract-dockets.jsonl")}
    products_by_library={ref:set() for ref in LIBRARIES}; subjects_by_library={ref:set() for ref in LIBRARIES}
    for subject in load_jsonl(SEM/"product_coordinate_binding_projection/subject-coordinate-binding-projections.jsonl"):
        for edge in subject["concrete_bindings"]:
            ref=edge["concrete_library_ref"]
            if ref in products_by_library:
                products_by_library[ref].add(subject["product_ref"]);subjects_by_library[ref].add(subject["subject_ref"])
    target_occurrences={(row["axis"],row["library_ref"]):row for row in load_jsonl(SEM/"targeted_evidence_cluster_adjudication/member-adjudication-occurrences.jsonl")}
    module_by_id={row["module_id"]:row for row in module_rows}
    library_rows=[]; axis_rows=[]
    for ref in LIBRARIES:
        mods=[f"module.or.{x}" for x in LIBRARY_MODULES[ref]]
        evidence=sorted({src for mod in mods for src in module_by_id[mod]["source_refs"]})
        if ref=="library.method_kernels.operations_research_bridge": disposition="COMPOSITION_ONLY_NO_SEMANTIC_OWNERSHIP"
        elif ref=="library.operations_research.decision_problem_semantics": disposition="RETAIN_SHARED_SEMANTIC_PRIMITIVE"
        else: disposition="RETAIN_NARROW_MODULE_BOUNDARY"
        library_rows.append({"record_kind":"operations_research_library_semantic_binding_candidate","binding_id":f"binding.or-semantic-slice.{slug(ref)}.v1","library_ref":ref,"library_name":contributions[ref]["name"],"semantic_module_refs":mods,"evidence_refs":evidence,"exact_contract_docket_ref":exact_dockets[ref]["docket_id"],"coordinate_binding_docket_ref":coordinate_dockets[ref]["binding_docket_id"],"downstream_subject_refs":sorted(subjects_by_library[ref]),"downstream_product_refs":sorted(products_by_library[ref]),"boundary_disposition_candidate":disposition,"compiler_binding":"REFUSED","refusal_reasons":["OWNER_RATIFICATION_MISSING","MEMBER_AXIS_APPLICABILITY_UNRATIFIED","EXACT_CONTRACT_UNSELECTED","IMPLEMENTATIONS_UNQUALIFIED"],"completion_claim":False})
        for axis in AXES:
            target=target_occurrences.get((axis,ref))
            axis_rows.append({"record_kind":"operations_research_library_axis_decision_candidate","decision_candidate_id":f"decision-candidate.or-axis.{slug(ref)}.{axis.replace('_','-')}.v1","library_ref":ref,"axis":axis,"semantic_module_refs":mods,"coordinate_question":AXIS_QUESTIONS[axis],"applicability_candidate":"REQUIRED_EXPLICIT_PROFILE","evidence_refs":evidence,"targeted_member_adjudication_occurrence_ref":target["occurrence_id"] if target else None,"coordinate_answers":[],"member_applicability":"PROPOSED_OWNER_REVIEW_REQUIRED","owner_decision":"UNRATIFIED","status":"EVIDENCE_BACKED_DECISION_QUESTION_NOT_ANSWER","canonical_gaps_closed":0,"completion_claim":False})
    findings=boundary_findings(products_by_library)
    context={"record_kind":"bounded_context_candidate","context_id":"context.operations-research-semantic-slice.v1","as_of":AS_OF,"vision":"How can constrained decisions, queueing systems and simulated systems be modeled, solved or experimented on while preserving assumptions, uncertainty, proof status, validation and external decision authority?","inside":["decision-problem semantics","constraint and objective semantics","typed optimization models","heuristic and exact solve contracts","result, bound and certificate algebra","infeasibility diagnosis","queueing models, inference, performance and validation","simulation model, experiment, randomness, execution, output and V&V","scoped finding handoff"],"outside":["industry ontology ownership","source ingestion and feature engineering","causal identification from observational data","predictive model lifecycle","business authorization and actuation","provider deployment","UI and workflow"],"neighbors":[{"context_ref":"context.domain-decision-authority","relationship":"anti_corruption_layer"},{"context_ref":"context.runtime-resource-control","relationship":"customer_supplier"},{"context_ref":"context.statistical-inference","relationship":"published_language"},{"context_ref":"context.analytical-finding","relationship":"open_host_service"}],"published_language":["DecisionProblem","ConstraintPolicy","ObjectivePreference","OptimizationModel","SolverRequirement","SolveReceipt","OptimizationResult","ValidationReceipt","QueueModel","SimulationExperiment","RandomStreamAllocation","SimulationResult","AnalyticalFindingEnvelope"],"ratification":"WITHHELD","completion_claim":False}
    summary={"program_id":"program.operations-research-semantic-slice.v1","as_of":AS_OF,"primary_or_official_sources":len(source_rows),"semantic_modules":len(module_rows),"non_collapse_laws":len(law_rows),"method_types":len(method_rows),"expert_learning_profiles":len(expert_rows),"recent_non_ai_innovations":len(innovation_rows),"bound_libraries":len(library_rows),"library_axis_decision_candidates":len(axis_rows),"product_capability_boundary_findings":len(findings),"downstream_products":len({x for vals in products_by_library.values() for x in vals}),"libraries_without_declared_product_consumer":sum(not vals for vals in products_by_library.values()),"owner_decisions":0,"exact_contracts_selected":0,"qualified_implementations":0,"canonical_gaps_closed":0,"completion_claim":False}
    return {"context":context,"sources":source_rows,"modules":module_rows,"laws":law_rows,"methods":method_rows,"experts":expert_rows,"innovations":innovation_rows,"libraries":library_rows,"axes":axis_rows,"findings":findings,"summary":summary}


def outputs() -> dict[str,str]:
    b=build(); files={
        "bounded-context.json":json.dumps(b["context"],ensure_ascii=False,sort_keys=True,indent=2)+"\n",
        "primary-sources.jsonl":"".join(canonical(x)+"\n" for x in b["sources"]),
        "semantic-modules.jsonl":"".join(canonical(x)+"\n" for x in b["modules"]),
        "non-collapse-laws.jsonl":"".join(canonical(x)+"\n" for x in b["laws"]),
        "operations-research-method-taxonomy.jsonl":"".join(canonical(x)+"\n" for x in b["methods"]),
        "expert-learning-profiles.jsonl":"".join(canonical(x)+"\n" for x in b["experts"]),
        "innovation-records.jsonl":"".join(canonical(x)+"\n" for x in b["innovations"]),
        "library-semantic-bindings.jsonl":"".join(canonical(x)+"\n" for x in b["libraries"]),
        "library-axis-decision-candidates.jsonl":"".join(canonical(x)+"\n" for x in b["axes"]),
        "product-capability-boundary-findings.jsonl":"".join(canonical(x)+"\n" for x in b["findings"]),
        "summary.json":json.dumps(b["summary"],ensure_ascii=False,sort_keys=True,indent=2)+"\n",
    }
    claims={name:{"bytes":len(value.encode()),"sha256":hashlib.sha256(value.encode()).hexdigest()} for name,value in files.items()}
    files["manifest.json"]=json.dumps({"manifest_id":"manifest.operations-research-semantic-slice.v1","as_of":AS_OF,"files":claims,"completion_claim":False},sort_keys=True,indent=2)+"\n"
    return files


def main() -> int:
    for name,value in outputs().items(): (HERE/name).write_text(value)
    s=build()["summary"]
    print(f"BUILD PASS operations research semantic slice: {s['semantic_modules']} modules, {s['method_types']} methods, {s['bound_libraries']} libraries and {s['library_axis_decision_candidates']} unresolved axis decisions")
    return 0


if __name__ == "__main__": raise SystemExit(main())
