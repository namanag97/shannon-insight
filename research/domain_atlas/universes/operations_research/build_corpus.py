#!/usr/bin/env python3
"""Build the provider-neutral operations-research research corpus.

The compact Python source is the reviewable authoring form.  JSONL files are the
machine-consumable artifacts.  Records are candidates, not claims of closure.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
EDITION = 1
ACCESSED = "2026-08-26"


def write_jsonl(name: str, rows: list[dict]) -> None:
    path = ROOT / name
    path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows))


def write_manifest() -> None:
    artifacts = sorted(p for p in ROOT.rglob("*.json*") if p.name != "manifest.json" and "__pycache__" not in p.parts)
    files = {str(p.relative_to(ROOT)): {"bytes": len(p.read_bytes()), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()} for p in artifacts}
    (ROOT / "manifest.json").write_text(json.dumps({"manifest_id": "manifest.operations-research.v1", "edition": EDITION, "files": files, "completion_claim": False}, indent=2, sort_keys=True) + "\n")


SOURCE_ROWS = [
    ("src.informs.methodologies", "O.R. Methodologies", "INFORMS", "society_taxonomy", "https://www.informs.org/Explore/History-of-O.R.-Excellence/O.R.-Methodologies", "field scope and methodology families"),
    ("src.informs.faq", "FAQs About O.R. & Analytics", "INFORMS", "society_definition", "https://www.informs.org/Resource-Center/INFORMS-Student-Union/FAQs-About-O.R.-Analytics", "decision-centered definition and practice process"),
    ("src.informs.journals", "INFORMS Journals", "INFORMS", "society_publication_map", "https://www.informs.org/Publications/INFORMS-Journals", "breadth of OR application and method communities"),
    ("src.informs.sections", "INFORMS Sections", "INFORMS", "society_community_map", "https://www.informs.org/Communities/INFORMS-Sections", "application and method communities"),
    ("src.ifors.or", "What is Operational Research?", "IFORS", "society_definition", "https://www.ifors.org/what-is-or/", "international field definition"),
    ("src.mos.home", "Mathematical Optimization Society", "MOS", "society_scope", "https://www.mathopt.org/", "mathematical optimization field scope"),
    ("src.little.1961", "A Proof for the Queuing Formula: L = λW", "Operations Research", "primary_research", "https://doi.org/10.1287/opre.9.3.383", "Little's law under its stated stationary finite-mean conditions"),
    ("src.jackson.1957", "Networks of Waiting Lines", "Operations Research", "primary_research", "https://doi.org/10.1287/opre.5.4.518", "open queueing-network equilibrium under the paper's routing and service assumptions"),
    ("src.kendall.1953", "Stochastic Processes Occurring in the Theory of Queues and their Analysis by the Method of the Imbedded Markov Chain", "Annals of Mathematical Statistics", "primary_research", "https://doi.org/10.1214/aoms/1177728975", "queue notation and embedded-chain analysis for the paper's queue classes"),
    ("src.google.ortools", "OR-Tools", "Google", "official_documentation", "https://developers.google.com/optimization/", "routing, flows, mathematical and constraint optimization"),
    ("src.google.ortools.v9_15", "OR-Tools v9.15 release", "Google", "official_release", "https://github.com/google/or-tools/releases/tag/v9.15", "exact release identity for the executed OR-Tools wheel"),
    ("src.google.glop_mpsolver_status.v9_15", "GLOP-to-MPSolver status mapping at v9.15", "Google", "official_source", "https://github.com/google/or-tools/blob/v9.15/ortools/linear_solver/proto_solver/glop_proto_solver.cc", "versioned source mapping that collapses GLOP infeasible-or-unbounded into MPSolver infeasible"),
    ("src.google.cp_sat", "CP-SAT Solver", "Google", "official_documentation", "https://developers.google.com/optimization/cp/cp_solver", "integer-only model contract and typed solve statuses"),
    ("src.google.cp_model_proto.v9_15", "CP-SAT model and result protocol at v9.15", "Google", "official_source", "https://github.com/google/or-tools/blob/v9.15/ortools/sat/cp_model.proto", "exact model, constraint and response identity for the executed interface"),
    ("src.google.sat_parameters.v9_15", "CP-SAT parameter protocol at v9.15", "Google", "official_source", "https://github.com/google/or-tools/blob/v9.15/ortools/sat/sat_parameters.proto", "exact enumeration, search, resource and reproducibility parameter surface"),
    ("src.google.mip", "Integer Optimization", "Google", "official_documentation", "https://developers.google.com/optimization/mip", "MIP versus CP-SAT versus network-flow selection"),
    ("src.google.mathopt", "The MathOpt Service", "Google", "official_documentation", "https://developers.google.com/optimization/service/math_opt/overview", "solver-independent model and result interface"),
    ("src.google.mathopt_rest", "solveMathOptModel", "Google", "official_api_contract", "https://developers.google.com/optimization/service/reference/rest/v1/mathopt/solveMathOptModel", "limits, status, rays, bounds, solutions and solver capabilities"),
    ("src.google.pdlp", "Practical Large-Scale Linear Programming using PDHG", "Google Research", "primary_research", "https://research.google/pubs/practical-large-scale-linear-programming-using-primal-dual-hybrid-gradient/", "PDLP design and empirical evaluation"),
    ("src.google.large_scale", "Large-scale optimization", "Google Research", "official_research_program", "https://research.google/teams/algorithms-optimization/large-scale-optimization/", "first-order LP scaling and implementation posture"),
    ("src.dagstuhl.cp_sat_lp", "The CP-SAT-LP Solver", "Schloss Dagstuhl LIPIcs", "primary_research", "https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.CP.2023.3", "hybrid SAT, simplex, MIP technology and portfolio search"),
    ("src.jump.moi_solutions", "MathOptInterface Solutions", "JuMP", "official_documentation", "https://jump.dev/MathOptInterface.jl/stable/manual/solutions/", "typed termination, primal and dual status"),
    ("src.jump.solutions", "JuMP Solutions", "JuMP", "official_documentation", "https://jump.dev/JuMP.jl/stable/manual/solutions/", "solution inspection contract"),
    ("src.cvxpy.dcp", "Disciplined Convex Programming", "CVXPY", "official_documentation", "https://www.cvxpy.org/tutorial/dcp/", "static curvature and sign validation"),
    ("src.cvxpy.solvers", "Solver Features", "CVXPY", "official_documentation", "https://www.cvxpy.org/tutorial/solvers/index.html", "solver selection, warm starts, statistics and parameters"),
    ("src.minizinc.resources", "MiniZinc Resources", "MiniZinc", "official_documentation", "https://www.minizinc.org/resources/", "modeling language, standard library and solver interface"),
    ("src.minizinc.challenge", "MiniZinc Challenge", "MiniZinc", "official_benchmark", "https://www.minizinc.org/challenge/", "constraint solver qualification and benchmark protocol"),
    ("src.highs.home", "HiGHS", "HiGHS", "official_documentation", "https://highs.dev/", "open LP, MIP and QP solver capabilities"),
    ("src.highs.v1_15_1", "HiGHS v1.15.1 release", "HiGHS", "official_release", "https://github.com/ERGO-Code/HiGHS/releases/tag/v1.15.1", "exact release identity for the executed highspy wheel"),
    ("src.highs.python", "HiGHS Python interface", "HiGHS", "official_documentation", "https://ergo-code.github.io/HiGHS/stable/interfaces/python/", "highspy initialization, execution, status and solution access"),
    ("src.highs.hipdlp", "HiGHS Newsletter 26.0", "HiGHS", "official_project_update", "https://highs.dev/assets/HiGHS_Newsletter_26_0.pdf", "HiPDLP GPU development claim and roadmap"),
    ("src.scip.home", "SCIP Optimization Suite", "SCIP", "official_documentation", "https://scipopt.org/", "CIP, MIP, MINLP, plugins and release composition"),
    ("src.scip.v9", "The SCIP Optimization Suite 9.0", "SCIP authors", "primary_research", "https://arxiv.org/abs/2402.17702", "2024 solver, interface, symmetry, nonlinear and heuristic advances"),
    ("src.scip.release9", "Release notes for SCIP 9", "SCIP", "official_release_notes", "https://scipopt.org/scip/doc/html/RN9.php", "fine-grained SCIP 9 changes"),
    ("src.ipopt.docs", "Ipopt Documentation", "COIN-OR", "official_documentation", "https://coin-or.github.io/Ipopt/", "large-scale smooth nonlinear programming contract"),
    ("src.coinor.projects", "COIN-OR Projects", "COIN-OR", "official_project_registry", "https://www.coin-or.org/projects/", "open optimization infrastructure"),
    ("src.gurobi.status", "Optimization Status Codes", "Gurobi", "official_documentation", "https://docs.gurobi.com/projects/optimizer/en/current/reference/numericcodes/statuscodes.html", "solver status and limit semantics"),
    ("src.gurobi.infeasibility", "Infeasibility", "Gurobi", "official_documentation", "https://support.gurobi.com/hc/en-us/sections/360009927652-Infeasibility", "IIS and feasibility relaxation surfaces"),
    ("src.gurobi.releases", "Highlights of past Gurobi releases", "Gurobi", "official_release_notes", "https://support.gurobi.com/hc/en-us/articles/20031469571217-Highlights-of-past-Gurobi-releases", "recent global MINLP, nonlinear and PDHG features"),
    ("src.ibm.status", "Accessing solution status", "IBM CPLEX", "official_documentation", "https://www.ibm.com/docs/en/icos/22.1.2?topic=information-accessing-solution-status", "optimal, feasible, infeasible, unbounded, unknown and error distinctions"),
    ("src.ibm.conflict", "How to invoke the conflict refiner", "IBM CPLEX", "official_documentation", "https://www.ibm.com/docs/en/icos/22.1.1?topic=conflicts-how-invoke-conflict-refiner", "infeasibility diagnosis contract"),
    ("src.miplib", "MIPLIB 2017", "Zuse Institute Berlin and contributors", "official_benchmark", "https://miplib.zib.de/", "representative MIP benchmark instances and solution checks"),
    ("src.qplib", "QPLIB", "Zuse Institute Berlin", "official_benchmark", "https://qplib.zib.de/instances.html", "quadratic-program structure and instance corpus"),
    ("src.minlplib", "MINLPLib Documentation", "MINLPLib", "official_benchmark", "https://www.minlplib.org/doc.html", "MINLP instance semantics, bounds and solution points"),
    ("src.tsplib", "TSPLIB", "University of Heidelberg", "official_benchmark", "https://comopt.ifi.uni-heidelberg.de/software/TSPLIB95/index.html", "TSP and related routing benchmark instances"),
    ("src.qaplib", "QAPLIB", "Lehigh University COR@L", "official_benchmark", "https://coral.ise.lehigh.edu/data-sets/qaplib/", "quadratic assignment benchmark instances"),
    ("src.cupdlp", "cuPDLP.jl", "Jinwen Yang et al.", "primary_research", "https://arxiv.org/abs/2311.12180", "GPU first-order LP solving"),
    ("src.cupdlpx", "cuPDLPx", "MIT Lu Lab", "official_research_software", "https://github.com/MIT-Lu-Lab/cuPDLPx", "enhanced GPU restarted Halpern PDHG"),
    ("src.clarabel", "Clarabel", "Oxford Control Group", "primary_research_software", "https://github.com/oxfordcontrol/Clarabel.jl", "homogeneous-embedding conic solver with quadratic objectives"),
    ("src.pyvrp", "PyVRP: A High-Performance VRP Solver Package", "INFORMS Journal on Computing authors", "primary_research", "https://doi.org/10.1287/ijoc.2023.0055", "hybrid genetic search for VRP"),
    ("src.anylogic", "AnyLogic Features", "AnyLogic", "official_product_documentation", "https://www.anylogic.com/overview", "discrete-event, system-dynamics and agent-based simulation distinction"),
    ("src.wsc", "Winter Simulation Conference Archive", "Winter Simulation Conference", "official_research_archive", "https://informs-sim.org/", "simulation methods, verification and applications"),
    ("src.hexaly", "Hexaly optimization platform", "Hexaly", "official_company_evidence", "https://www.hexaly.com/", "claimed enriched MIP, automatic decomposition and solution patterns"),
    ("src.ortec", "ORTEC", "ORTEC", "official_company_evidence", "https://ortec.com/", "supply chain, workforce and applied decision-intelligence claims"),
    ("src.decisionbrain", "DecisionBrain", "DecisionBrain", "official_company_evidence", "https://decisionbrain.com/", "modular planning and scheduling solution claims"),
    ("src.artelys", "Artelys", "Artelys", "official_company_evidence", "https://www.artelys.com/", "OR consulting, energy, scheduling, network and solver claims"),
    ("src.mathco.scheduling", "Manufacturing scheduling optimization case", "MathCo", "official_company_case_claim", "https://mathco.com/casestudies/transforming-manufacturing-efficiency-with-ai-powered-scheduling-optimization/", "scheduling solution and claimed operational outcomes"),
    ("src.mathco.heuristics", "Manufacturing analytics solutions", "MathCo", "official_company_evidence", "https://mathco.com/genai-manufacturing-solutions/", "explicit heuristic scheduling and data-pipeline claim"),
    ("src.timefold", "Timefold Solver Introduction", "Timefold", "official_documentation", "https://docs.timefold.ai/timefold-solver/1.x/introduction", "constraint-satisfaction planning and score contracts"),
    ("src.nextmv", "Nextmv Documentation", "Nextmv", "official_documentation", "https://www.nextmv.io/docs", "decision applications, runs and operational optimization claims"),
    ("src.aimms", "AIMMS Documentation", "AIMMS", "official_documentation", "https://documentation.aimms.com/", "optimization modeling, solver interfaces, deployment and supported program types"),
    ("src.frontline", "Analytic Solver Platform", "Frontline Systems", "official_company_evidence", "https://www.solver.com/analytic-solver-platform", "spreadsheet optimization, simulation and analytics product claims"),
    ("src.riverlogic", "River Logic Platform", "River Logic", "official_company_evidence", "https://www.riverlogic.com/platform", "enterprise decision optimization product claims"),
    ("src.atoptima", "Atoptima", "Atoptima", "official_company_evidence", "https://atoptima.com/", "transport, logistics and supply-chain optimization solver claims"),
    ("src.simio", "Simio", "Simio", "official_company_evidence", "https://www.simio.com/", "discrete-event digital twins, scheduling and simulation product claims"),
    ("src.optibus", "Optibus", "Optibus", "official_company_evidence", "https://optibus.com/", "public-transport planning, scheduling and rostering product claims"),
    ("src.solvoyo", "Solvoyo", "Solvoyo", "official_company_evidence", "https://www.solvoyo.com/", "supply-chain decision automation product claims"),
    ("src.optimal_dynamics", "Optimal Dynamics", "Optimal Dynamics", "official_company_evidence", "https://www.optimaldynamics.com/", "truckload planning and sequential-decision product claims"),
    ("src.gams", "GAMS Documentation", "GAMS Development Corp.", "official_documentation", "https://www.gams.com/latest/docs/", "algebraic modeling and solver interfaces"),
    ("src.ampl", "AMPL Documentation", "AMPL Optimization", "official_documentation", "https://dev.ampl.com/", "algebraic model/data separation and solver interfaces"),
    ("src.pyomo", "Pyomo Documentation", "Pyomo", "official_documentation", "https://pyomo.readthedocs.io/en/stable/", "provider-neutral optimization modeling components"),
    ("src.osqp", "OSQP Documentation", "OSQP", "official_documentation", "https://osqp.org/docs/", "operator-splitting convex QP contract"),
    ("src.scs", "SCS Documentation", "SCS", "official_documentation", "https://www.cvxgrp.org/scs/", "first-order conic solver and status semantics"),
    ("src.bertismas", "Dimitris Bertsimas research profile", "MIT", "official_expert_profile", "https://dbertsim.mit.edu/", "robust, stochastic, discrete and convex optimization expertise"),
    ("src.barnhart", "Cynthia Barnhart profile", "MIT", "official_expert_profile", "https://mitsloan.mit.edu/faculty/directory/cynthia-barnhart", "large-scale transportation optimization expertise"),
    ("src.powell", "Warren Powell profile", "Princeton University", "official_expert_profile", "https://dof.princeton.edu/people/warren-buckler-powell", "sequential decision analytics and approximate dynamic programming"),
    ("src.vanhentenryck", "Pascal Van Hentenryck profile", "Georgia Tech", "official_expert_profile", "https://www.isye.gatech.edu/users/pascal-van-hentenryck", "constraint programming and optimization expertise"),
    ("src.goemans", "Michel Goemans profile", "MIT", "official_expert_profile", "https://math.mit.edu/directory/profile.html?pid=84", "approximation algorithms and combinatorial optimization"),
    ("src.ye", "Yinyu Ye profile", "Stanford University", "official_expert_profile", "https://profiles.stanford.edu/yinyu-ye", "interior-point, conic, robust and market optimization"),
]


SOURCES = [
    {
        "source_id": sid,
        "edition": EDITION,
        "title": title,
        "publisher": publisher,
        "kind": kind,
        "url": url,
        "primary_or_official": True,
        "authority_scope": supports,
        "limitations": "Authority is limited to the named field, implementation, benchmark, profile, or the publisher's own capability claims; it does not establish universal completeness.",
        "accessed_at": ACCESSED,
    }
    for sid, title, publisher, kind, url, supports in SOURCE_ROWS
]


FAMILIES = {
    "framing": {
        "inputs": ["decision owner", "decision horizon", "controllable actions", "state and observations", "affected parties"],
        "outputs": ["decision problem specification", "scope and authority record"],
        "assumptions": ["the decision and affected parties can be named", "objectives and constraints are not silently interchangeable"],
        "guarantee": "Produces a reviewable formulation, not a mathematical optimum.",
        "evidence": ["src.informs.faq", "src.informs.methodologies"],
    },
    "mathematical_programming": {
        "inputs": ["typed variables", "objective expression", "constraint expressions", "parameter data"],
        "outputs": ["mathematical-program model", "solver requirement set"],
        "assumptions": ["expression domains and numeric units are valid", "declared structure matches the actual functions"],
        "guarantee": "Model class alone guarantees no solution; convexity, integrality, tolerances and termination evidence determine valid claims.",
        "evidence": ["src.cvxpy.dcp", "src.minlplib", "src.ipopt.docs"],
    },
    "constraint_logic": {
        "inputs": ["decision variables and domains", "logical or global constraints", "optional objective"],
        "outputs": ["constraint model", "feasible assignment or qualified result"],
        "assumptions": ["finite domains or solver-supported encodings exist", "global-constraint semantics are explicit"],
        "guarantee": "Completeness or optimality is claimable only when the selected solver and termination receipt establish it.",
        "evidence": ["src.google.cp_sat", "src.minizinc.resources", "src.dagstuhl.cp_sat_lp"],
    },
    "exact_algorithm": {
        "inputs": ["qualified model instance", "algorithm configuration", "resource budget"],
        "outputs": ["incumbent", "bound or certificate", "termination receipt"],
        "assumptions": ["the algorithm supports the model class", "numerical and integrality tolerances are governed"],
        "guarantee": "Exact means capable of proof under its contract, not guaranteed to finish within a finite operational budget.",
        "evidence": ["src.scip.home", "src.gurobi.status", "src.ibm.status"],
    },
    "decomposition": {
        "inputs": ["structured model", "decomposition annotations or detector", "master-subproblem protocol"],
        "outputs": ["decomposed solve plan", "bounds and cuts or columns", "combined result"],
        "assumptions": ["coupling structure is valid", "subproblem results preserve the master contract"],
        "guarantee": "Proof properties depend on the specific decomposition and exactness of master and subproblem operations.",
        "evidence": ["src.scip.home", "src.scip.v9", "src.pyomo"],
    },
    "approximation_online": {
        "inputs": ["problem instance or request stream", "quality criterion", "budget"],
        "outputs": ["solution or online policy", "proved ratio or regret/competitive receipt when available"],
        "assumptions": ["the theorem's problem class and adversary/distribution model match deployment"],
        "guarantee": "Only the instantiated theorem establishes an approximation, regret or competitive bound.",
        "evidence": ["src.goemans", "src.ye", "src.informs.methodologies"],
    },
    "constructive_heuristic": {
        "inputs": ["problem representation", "construction rule", "feasibility checks or repair", "budget and seed"],
        "outputs": ["feasible or partially repaired incumbent", "construction trace"],
        "assumptions": ["the construction rule is defined for the instance", "constraint checking is complete enough for declared feasibility"],
        "guarantee": "No universal quality guarantee; feasibility and empirical quality require independent validation.",
        "evidence": ["src.google.ortools", "src.pyvrp", "src.mathco.heuristics"],
    },
    "local_metaheuristic": {
        "inputs": ["initial solution or population", "move/neighborhood operators", "acceptance and diversification policy", "budget and seed"],
        "outputs": ["best-known incumbent", "search trace and reproducibility receipt"],
        "assumptions": ["solution encoding and move effects are valid", "repair and feasibility policy are explicit"],
        "guarantee": "No universal optimality guarantee; quality is empirical unless paired with a separate certificate or bound.",
        "evidence": ["src.pyvrp", "src.minizinc.challenge", "src.hexaly"],
    },
    "hybrid_search": {
        "inputs": ["problem features", "candidate algorithms or operators", "selection or composition policy", "budget"],
        "outputs": ["selected/configured search plan", "incumbent and evidence"],
        "assumptions": ["training/benchmark instances represent the target regime", "component guarantees are not strengthened by composition"],
        "guarantee": "Hybridization does not itself imply exactness or better quality; receipts must preserve each component's guarantees.",
        "evidence": ["src.dagstuhl.cp_sat_lp", "src.scip.v9", "src.hexaly"],
    },
    "network_combinatorial": {
        "inputs": ["typed graph or set system", "weights/capacities", "side constraints"],
        "outputs": ["path, flow, matching, cut, tree, packing or location decision", "quality receipt"],
        "assumptions": ["graph direction, multiplicity and weight semantics are explicit", "side constraints do not silently change complexity class"],
        "guarantee": "Guarantees depend on the exact problem variant; adding side constraints may invalidate polynomial algorithms.",
        "evidence": ["src.google.ortools", "src.tsplib", "src.qaplib"],
    },
    "routing": {
        "inputs": ["stops, demands and service rules", "fleet/resources", "travel-time/cost model", "operational constraints"],
        "outputs": ["routes and schedules", "unserved/exception list", "quality and feasibility receipt"],
        "assumptions": ["travel and service semantics match execution", "dynamic changes and unserviceable demand are modeled"],
        "guarantee": "Routing variant and solve strategy determine guarantees; a feasible route can still be operationally invalid if source assumptions drift.",
        "evidence": ["src.google.ortools", "src.pyvrp", "src.tsplib"],
    },
    "scheduling": {
        "inputs": ["activities/jobs", "resources and calendars", "precedence and temporal constraints", "objectives and disruption state"],
        "outputs": ["schedule", "resource assignments", "violations or exceptions", "quality receipt"],
        "assumptions": ["duration, setup, eligibility and calendar semantics are explicit", "execution updates can be reconciled"],
        "guarantee": "A mathematically feasible schedule is not an executable commitment until authority, buffers and runtime state are checked.",
        "evidence": ["src.google.cp_sat", "src.minizinc.challenge", "src.decisionbrain"],
    },
    "inventory_planning": {
        "inputs": ["demand and uncertainty model", "lead times", "network and capacity", "cost and service policy"],
        "outputs": ["order, allocation, capacity or inventory policy", "service/cost risk receipt"],
        "assumptions": ["stock state and lead-time semantics are valid", "lost sales, backorders and substitutions are distinguished"],
        "guarantee": "Policy performance is conditional on the demand, lead-time and execution model.",
        "evidence": ["src.informs.methodologies", "src.ortec", "src.decisionbrain"],
    },
    "queues_reliability": {
        "inputs": ["arrival process", "service-time process", "resource discipline", "failure/repair model"],
        "outputs": ["delay, queue, capacity or reliability distribution", "design or control recommendation"],
        "assumptions": ["stationarity, independence and discipline assumptions are explicit", "steady-state existence is checked when claimed"],
        "guarantee": "Analytical results hold only for the declared stochastic process and stability regime.",
        "evidence": ["src.informs.methodologies", "src.wsc", "src.bertismas"],
    },
    "simulation": {
        "inputs": ["conceptual model", "state-transition/event equations", "input distributions and scenarios", "experiment design and seeds"],
        "outputs": ["replication traces", "estimated response distribution", "validation and uncertainty report"],
        "assumptions": ["conceptual model is fit for purpose", "warm-up, replications and random streams are governed"],
        "guarantee": "Simulation estimates behavior of the declared model, not truth about the real system; no optimum is implied.",
        "evidence": ["src.anylogic", "src.wsc"],
    },
    "sequential_control": {
        "inputs": ["state and observation model", "action space", "transition/response model", "horizon and reward/cost"],
        "outputs": ["policy or control trajectory", "value/risk estimate", "deployment constraints"],
        "assumptions": ["state sufficiency and dynamics assumptions are explicit", "feedback latency and actuation authority are modeled"],
        "guarantee": "Policy claims are conditional on dynamics, observability, horizon and approximation error.",
        "evidence": ["src.informs.methodologies", "src.powell", "src.ye"],
    },
    "markets_games_revenue": {
        "inputs": ["participants and feasible actions", "preferences/utility or demand", "information and timing", "market or mechanism rules"],
        "outputs": ["allocation, price, equilibrium or policy", "welfare/revenue/fairness receipt"],
        "assumptions": ["strategic behavior and information are modeled", "authority and incentive-compatibility claims are scoped"],
        "guarantee": "Equilibrium, truthfulness or revenue properties hold only under the specified game and participant assumptions.",
        "evidence": ["src.informs.methodologies", "src.ye"],
    },
    "human_decision": {
        "inputs": ["alternatives", "criteria and evidence", "preference/authority model", "affected-party constraints"],
        "outputs": ["ranking, choice, trade-off frontier or elicitation record", "decision rationale"],
        "assumptions": ["criteria scales and preference semantics are valid", "approval and recommendation are distinct"],
        "guarantee": "A formal preference model supports deliberation; it does not manufacture legitimacy or authority.",
        "evidence": ["src.informs.methodologies", "src.informs.sections"],
    },
    "postsolve_qualification": {
        "inputs": ["model snapshot", "solver/run receipt", "candidate solution, bounds or certificate", "qualification policy"],
        "outputs": ["validated result", "sensitivity/conflict/alternative report", "accept/reject decision"],
        "assumptions": ["model and data digests bind the result", "tolerances and qualification tests are declared"],
        "guarantee": "Qualification can narrow valid claims but cannot strengthen evidence absent from the solver or independent checker.",
        "evidence": ["src.google.mathopt_rest", "src.jump.moi_solutions", "src.ibm.conflict", "src.miplib"],
    },
}


METHOD_SPECS = {
    "framing": [
        ("decision_framing", "Decision framing", "Define the real choice, decision owner, affected parties, horizon and alternative actions."),
        ("problem_structuring", "Problem structuring", "Decompose an ill-structured operational problem into decisions, uncertainties, consequences and boundaries."),
        ("stakeholder_analysis", "Stakeholder and harmed-party analysis", "Identify actors who decide, execute, benefit, bear risk or can refuse a decision."),
        ("system_boundary_selection", "System-boundary selection", "Choose what dynamics and externalities are inside the analytical system and record exclusions."),
        ("decision_horizon_design", "Decision-horizon design", "Separate strategic, tactical, operational and real-time decisions and their coupling."),
        ("unit_of_decision_definition", "Unit-of-decision definition", "Define the atomic object, population and grain over which actions are selected."),
        ("baseline_and_counterfactual", "Baseline and counterfactual definition", "Define the no-change or comparator policy against which value is measured."),
        ("objective_elicitation", "Objective elicitation", "Elicit outcomes to minimize, maximize, target or lexicographically prioritize."),
        ("constraint_elicitation", "Constraint elicitation", "Discover physical, contractual, policy, safety and preference restrictions."),
        ("hard_soft_constraint_classification", "Hard/soft constraint classification", "Determine which restrictions are inviolable and which admit penalized or approved relaxation."),
        ("decision_authority_mapping", "Decision-authority mapping", "Bind recommendations, approvals, commitments and execution rights to actors."),
        ("value_of_model_assessment", "Value-of-model assessment", "Test whether analytical complexity can improve the decision enough to justify cost and delay."),
    ],
    "mathematical_programming": [
        ("linear_programming", "Linear programming", "Optimize a linear objective over continuous variables and linear constraints."),
        ("quadratic_programming", "Quadratic programming", "Optimize a quadratic objective subject to linear or supported quadratic constraints."),
        ("quadratically_constrained_programming", "Quadratically constrained programming", "Represent optimization with quadratic constraints and governed convexity/nonconvexity."),
        ("second_order_cone_programming", "Second-order cone programming", "Represent convex norm and conic constraints with second-order cones."),
        ("semidefinite_programming", "Semidefinite programming", "Optimize over positive-semidefinite matrix constraints."),
        ("conic_programming", "Conic programming", "Represent convex programs through affine maps into governed cones."),
        ("geometric_programming", "Geometric programming", "Optimize posynomial/monomial models through valid transformations."),
        ("nonlinear_programming", "Smooth nonlinear programming", "Optimize differentiable nonlinear objectives and constraints, generally to local stationarity unless globally qualified."),
        ("nonsmooth_optimization", "Nonsmooth optimization", "Optimize objectives or constraints without ordinary differentiability."),
        ("derivative_free_optimization", "Derivative-free optimization", "Search when derivatives are unavailable, unreliable or too expensive."),
        ("global_nonlinear_optimization", "Global nonlinear optimization", "Seek globally valid bounds and optima for nonconvex continuous models."),
        ("mixed_integer_linear_programming", "Mixed-integer linear programming", "Optimize linear models containing discrete and continuous decisions."),
        ("mixed_integer_quadratic_programming", "Mixed-integer quadratic programming", "Optimize mixed-integer models with quadratic objectives."),
        ("mixed_integer_conic_programming", "Mixed-integer conic programming", "Optimize discrete decisions coupled with convex conic structure."),
        ("mixed_integer_nonlinear_programming", "Mixed-integer nonlinear programming", "Optimize models combining integrality with nonlinear functions."),
        ("generalized_disjunctive_programming", "Generalized disjunctive programming", "Model logical alternatives and algebraic constraints as explicit disjunctions."),
        ("complementarity_programming", "Complementarity programming", "Model mutually complementary primal, dual or equilibrium conditions."),
        ("mathematical_program_with_equilibrium_constraints", "MPEC", "Optimize an upper-level objective constrained by equilibrium/complementarity conditions."),
        ("bilevel_programming", "Bilevel programming", "Model a leader decision whose feasibility or objective depends on a follower optimization."),
        ("multiobjective_programming", "Multi-objective programming", "Represent and explore multiple non-equivalent objectives without silently scalarizing them."),
        ("goal_programming", "Goal programming", "Minimize deviations from prioritized or weighted target levels."),
        ("lexicographic_optimization", "Lexicographic optimization", "Optimize ordered objectives while preserving higher-priority achievements."),
        ("robust_optimization", "Robust optimization", "Optimize against all parameter realizations in a declared uncertainty set."),
        ("distributionally_robust_optimization", "Distributionally robust optimization", "Optimize against probability distributions in a declared ambiguity set."),
        ("two_stage_stochastic_programming", "Two-stage stochastic programming", "Choose here-and-now decisions followed by recourse after uncertainty reveals."),
        ("multistage_stochastic_programming", "Multistage stochastic programming", "Optimize nonanticipative sequential decisions over an uncertainty tree or process."),
        ("chance_constrained_programming", "Chance-constrained programming", "Require constraints to hold with a declared probability under a specified distribution."),
        ("risk_averse_stochastic_programming", "Risk-averse stochastic programming", "Optimize distribution-sensitive risk measures rather than expectation alone."),
        ("parametric_optimization", "Parametric optimization", "Characterize solutions as parameters vary."),
        ("semi_infinite_programming", "Semi-infinite programming", "Optimize finitely many variables subject to infinitely indexed constraints."),
    ],
    "constraint_logic": [
        ("constraint_satisfaction", "Constraint satisfaction", "Find assignments satisfying declared variable-domain and constraint relations."),
        ("constraint_optimization", "Constraint optimization", "Optimize an objective over a constraint-satisfaction model."),
        ("global_constraint_modeling", "Global-constraint modeling", "Use semantic constraints such as all-different, cumulative and circuit with dedicated propagation."),
        ("sat_solving", "Boolean satisfiability solving", "Find or refute Boolean assignments satisfying a propositional formula."),
        ("maxsat", "Maximum satisfiability", "Maximize satisfied weighted or unweighted clauses while preserving declared hard clauses."),
        ("smt_solving", "Satisfiability modulo theories", "Solve logical formulas coupled to governed theories such as arithmetic or arrays."),
        ("answer_set_programming", "Answer-set programming", "Compute stable models of a declarative logic program."),
        ("cp_sat", "CP-SAT", "Solve bounded integer constraint models using SAT, propagation, LP relaxation and portfolio search."),
        ("lazy_clause_generation", "Lazy-clause generation", "Combine constraint propagation with learned clauses and explanation."),
        ("decision_diagram_optimization", "Decision-diagram optimization", "Use exact, restricted or relaxed decision diagrams to search and bound discrete decisions."),
    ],
    "exact_algorithm": [
        ("primal_simplex", "Primal simplex", "Traverse bases while maintaining primal feasibility to solve linear programs."),
        ("dual_simplex", "Dual simplex", "Traverse bases while maintaining dual feasibility, often after model changes or presolve."),
        ("interior_point", "Interior-point method", "Follow an interior central path to solve continuous convex or supported nonlinear programs."),
        ("active_set", "Active-set method", "Iteratively identify constraints active at a continuous optimum."),
        ("branch_and_bound", "Branch-and-bound", "Partition a discrete/nonconvex search space and prune with valid bounds."),
        ("cutting_plane", "Cutting-plane method", "Iteratively add valid inequalities separating invalid or fractional solutions."),
        ("branch_and_cut", "Branch-and-cut", "Combine branch-and-bound with dynamically generated valid cuts."),
        ("branch_and_price", "Branch-and-price", "Combine branching with column generation for huge variable spaces."),
        ("branch_cut_and_price", "Branch-cut-and-price", "Combine branching, cutting planes and dynamic columns under one proof process."),
        ("dynamic_programming_exact", "Exact dynamic programming", "Solve recursively decomposable decisions through exact state-value recurrences."),
        ("label_setting", "Label-setting algorithm", "Construct provably final labels for applicable shortest-path or resource-constrained states."),
        ("label_correcting", "Label-correcting algorithm", "Iteratively correct path labels until optimality conditions hold."),
        ("a_star", "A* search", "Find a least-cost path using an admissible/consistent heuristic under its theorem."),
        ("enumeration", "Complete enumeration", "Evaluate every candidate in a finite feasible set when tractable."),
        ("meet_in_the_middle", "Meet-in-the-middle", "Split and reconcile a combinatorial search to reduce exponential constants."),
        ("fixed_parameter_algorithm", "Fixed-parameter algorithm", "Solve a hard problem with complexity isolated to a declared structural parameter."),
    ],
    "decomposition": [
        ("benders_decomposition", "Benders decomposition", "Separate complicating variables from recourse/subproblems and add feasibility or optimality cuts."),
        ("logic_based_benders", "Logic-based Benders decomposition", "Derive master cuts from general subproblem inference rather than LP duality alone."),
        ("dantzig_wolfe", "Dantzig-Wolfe decomposition", "Reformulate block-angular models over extreme points/rays of substructures."),
        ("column_generation", "Column generation", "Generate improving variables through a pricing subproblem."),
        ("delayed_constraint_generation", "Delayed constraint generation", "Generate violated constraints only when needed."),
        ("lagrangian_relaxation", "Lagrangian relaxation", "Dualize complicating constraints to obtain bounds and decomposed subproblems."),
        ("lagrangian_decomposition", "Lagrangian decomposition", "Duplicate linking decisions and price consistency between decomposed blocks."),
        ("progressive_hedging", "Progressive hedging", "Coordinate scenario subproblems toward nonanticipative stochastic decisions."),
        ("nested_benders", "Nested Benders decomposition", "Apply stagewise Benders cuts to multistage stochastic programs."),
        ("admm_decomposition", "ADMM decomposition", "Coordinate separable convex subproblems through augmented-Lagrangian consensus updates."),
        ("scenario_decomposition", "Scenario decomposition", "Partition uncertain models by scenario while governing cross-scenario decisions."),
        ("automatic_structure_detection", "Automatic decomposition detection", "Infer candidate block/coupling structure and qualify it before choosing a decomposition."),
    ],
    "approximation_online": [
        ("constant_factor_approximation", "Constant-factor approximation", "Return a solution within a proved constant factor for a specific problem class."),
        ("ptas", "Polynomial-time approximation scheme", "Provide a configurable approximation ratio with polynomial runtime for fixed accuracy."),
        ("fptas", "Fully polynomial-time approximation scheme", "Provide approximation with runtime polynomial in input size and inverse accuracy."),
        ("randomized_rounding", "Randomized rounding", "Convert a fractional relaxation to discrete decisions with probabilistic guarantees."),
        ("primal_dual_approximation", "Primal-dual approximation", "Construct primal and dual objects together to prove a quality ratio."),
        ("competitive_analysis", "Online competitive algorithm", "Evaluate an online policy against an offline optimum under a specified adversary."),
        ("online_primal_dual", "Online primal-dual allocation", "Update prices and allocations as requests arrive with declared regret or competitive claims."),
        ("streaming_approximation", "Streaming approximation", "Approximate a combinatorial/statistical result under bounded passes and memory."),
    ],
    "constructive_heuristic": [
        ("greedy_construction", "Greedy construction", "Build a solution by repeatedly choosing the locally preferred feasible addition."),
        ("randomized_greedy", "Randomized greedy construction", "Sample among high-quality greedy candidates to diversify constructions."),
        ("insertion_heuristic", "Insertion heuristic", "Insert unassigned elements at selected positions while controlling incremental cost."),
        ("nearest_neighbor", "Nearest-neighbor construction", "Build a route or sequence by repeatedly choosing a nearest admissible next element."),
        ("clarke_wright_savings", "Clarke-Wright savings", "Merge routes based on estimated savings while maintaining routing feasibility."),
        ("sweep_heuristic", "Sweep heuristic", "Cluster and order spatial demand by angular sweep before routing."),
        ("priority_dispatching", "Priority dispatching rule", "Select the next job/activity using a governed operational priority rule."),
        ("list_scheduling", "List scheduling", "Assign precedence-ready tasks to resources following an explicit priority list."),
        ("first_fit", "First-fit packing", "Place each item into the first admissible container."),
        ("best_fit", "Best-fit packing", "Place each item into the admissible container leaving the least residual capacity."),
        ("regret_insertion", "Regret insertion", "Insert the element with greatest loss between its best and alternative placements."),
        ("feasibility_repair", "Feasibility repair", "Transform an infeasible candidate toward feasibility using prioritized violation repairs."),
    ],
    "local_metaheuristic": [
        ("hill_climbing", "Hill climbing", "Repeatedly accept improving local moves until a local optimum or budget is reached."),
        ("steepest_descent_local_search", "Steepest-descent local search", "Evaluate a neighborhood and accept its best improving move."),
        ("first_improvement_local_search", "First-improvement local search", "Accept the first improving move under a governed scan order."),
        ("two_opt", "2-opt", "Improve a tour or sequence by replacing two edges/adjacencies."),
        ("k_opt", "k-opt", "Search route/sequence reconnections involving k edges."),
        ("swap_relocate_exchange", "Swap/relocate/exchange neighborhoods", "Search assignment or routing solutions with atomic relocation and exchange moves."),
        ("variable_neighborhood_search", "Variable neighborhood search", "Systematically change neighborhoods to escape local optima."),
        ("large_neighborhood_search", "Large-neighborhood search", "Destroy and repair substantial solution portions."),
        ("adaptive_large_neighborhood_search", "Adaptive large-neighborhood search", "Adapt destroy/repair operator selection from observed performance."),
        ("tabu_search", "Tabu search", "Use adaptive memory to prevent cycling and guide diversification/intensification."),
        ("simulated_annealing", "Simulated annealing", "Accept worsening moves with a governed temperature schedule."),
        ("iterated_local_search", "Iterated local search", "Perturb local optima and reapply local improvement."),
        ("guided_local_search", "Guided local search", "Penalize repeatedly troublesome solution features to escape local optima."),
        ("grasp", "GRASP", "Repeat randomized greedy construction followed by local search."),
        ("genetic_algorithm", "Genetic algorithm", "Evolve a population using selection, crossover, mutation and replacement."),
        ("memetic_algorithm", "Memetic algorithm", "Combine population evolution with individual local improvement."),
        ("differential_evolution", "Differential evolution", "Generate continuous candidates through scaled vector differences and selection."),
        ("ant_colony_optimization", "Ant-colony optimization", "Construct solutions using pheromone-like adaptive trails and heuristic desirability."),
        ("particle_swarm_optimization", "Particle-swarm optimization", "Move a population through continuous search using personal and collective best states."),
        ("scatter_search", "Scatter search", "Systematically combine diverse elite solutions and improve offspring."),
        ("path_relinking", "Path relinking", "Explore trajectories connecting elite solutions."),
        ("cross_entropy_method", "Cross-entropy method", "Adapt a sampling distribution toward elite candidate regions."),
        ("evolution_strategy", "Evolution strategy", "Adapt continuous search distributions and strategy parameters across generations."),
    ],
    "hybrid_search": [
        ("hyperheuristic", "Hyper-heuristic", "Select or generate lower-level heuristics using problem-state and performance evidence."),
        ("algorithm_portfolio", "Algorithm portfolio", "Run or select complementary algorithms under a shared budget."),
        ("per_instance_algorithm_selection", "Per-instance algorithm selection", "Choose an algorithm/configuration from instance features and qualification evidence."),
        ("automated_algorithm_configuration", "Automated algorithm configuration", "Tune algorithm parameters over a declared training/validation instance distribution."),
        ("parallel_cooperative_search", "Parallel cooperative search", "Share incumbents, bounds or learned information among concurrent workers."),
        ("matheuristic", "Matheuristic", "Combine mathematical programming with problem-specific heuristic search."),
        ("relax_and_fix", "Relax-and-fix", "Sequentially impose integrality on variable blocks while relaxing future blocks."),
        ("fix_and_optimize", "Fix-and-optimize", "Repeatedly reoptimize selected variable neighborhoods while fixing the remainder."),
        ("local_branching", "Local branching", "Use a MIP constraint to search a neighborhood around an incumbent."),
        ("rins", "Relaxation-induced neighborhood search", "Fix variables whose incumbent and relaxation values agree and reoptimize the remainder."),
        ("feasibility_pump", "Feasibility pump", "Alternate relaxation and rounding/projection to seek an integer-feasible solution."),
        ("simulation_optimization_hybrid", "Simulation-optimization hybrid", "Use simulation responses to guide optimization when outcomes lack closed-form evaluation."),
    ],
    "network_combinatorial": [
        ("shortest_path", "Shortest path", "Find a minimum-cost path under the declared graph and weight semantics."),
        ("resource_constrained_shortest_path", "Resource-constrained shortest path", "Find a least-cost path satisfying one or more resource limits."),
        ("k_shortest_paths", "K shortest paths", "Enumerate multiple ordered path alternatives."),
        ("maximum_flow", "Maximum flow", "Maximize feasible flow from sources to sinks under capacities."),
        ("minimum_cost_flow", "Minimum-cost flow", "Route required flow at minimum cost subject to conservation and capacities."),
        ("multicommodity_flow", "Multicommodity flow", "Route multiple coupled commodities through shared capacity."),
        ("minimum_cut", "Minimum cut", "Find a minimum-capacity partition separating declared terminals."),
        ("bipartite_matching", "Bipartite matching", "Select compatible pairs without repeated endpoints."),
        ("weighted_matching", "Weighted matching", "Select disjoint pairs maximizing or minimizing total weight."),
        ("assignment_problem", "Assignment", "Match agents to tasks under one-to-one or capacity variants."),
        ("minimum_spanning_tree", "Minimum spanning tree", "Connect all nodes with an acyclic minimum-weight subgraph."),
        ("network_design", "Network design", "Choose links, capacities or facilities to meet flow/service objectives."),
        ("facility_location", "Facility location", "Choose facility sites and demand assignments under costs and service constraints."),
        ("set_covering", "Set covering", "Choose sets to cover required elements at minimum cost."),
        ("set_packing", "Set packing", "Choose mutually compatible sets maximizing value."),
        ("knapsack", "Knapsack", "Select items under capacity to maximize value."),
        ("bin_packing", "Bin packing", "Pack items into the fewest or lowest-cost admissible bins."),
        ("quadratic_assignment", "Quadratic assignment", "Assign facilities to locations with pairwise flow-distance costs."),
    ],
    "routing": [
        ("traveling_salesperson", "Traveling salesperson problem", "Find a minimum-cost tour visiting required nodes once under the declared distance semantics."),
        ("asymmetric_tsp", "Asymmetric TSP", "Find a tour with direction-dependent travel costs."),
        ("capacitated_vehicle_routing", "Capacitated vehicle routing", "Construct minimum-cost routes respecting vehicle capacity."),
        ("vehicle_routing_time_windows", "VRP with time windows", "Route demand while meeting service time windows."),
        ("pickup_delivery", "Pickup-and-delivery routing", "Route paired pickup and delivery requests with precedence and capacity."),
        ("dial_a_ride", "Dial-a-ride", "Schedule passenger pickups/drop-offs with ride-time and service constraints."),
        ("multi_depot_routing", "Multi-depot routing", "Route vehicles from and to multiple depots."),
        ("heterogeneous_fleet_routing", "Heterogeneous-fleet routing", "Choose routes and vehicle types with distinct capacity/cost/eligibility."),
        ("split_delivery_routing", "Split-delivery routing", "Permit demand to be served by multiple vehicle visits."),
        ("inventory_routing", "Inventory routing", "Jointly choose replenishment quantities, timing and vehicle routes."),
        ("arc_routing", "Arc routing", "Service required edges or arcs rather than nodes."),
        ("orienteering", "Orienteering", "Choose a value-maximizing subset of visits under a route budget."),
        ("dynamic_vehicle_routing", "Dynamic vehicle routing", "Replan routes as requests and execution state arrive."),
        ("stochastic_vehicle_routing", "Stochastic vehicle routing", "Plan routes under uncertain demand, travel or service."),
        ("green_vehicle_routing", "Energy/emission-aware routing", "Route with explicit energy, charging, emission or fuel constraints."),
        ("last_mile_delivery_routing", "Last-mile delivery routing", "Route dense delivery operations with customer, curb and service constraints."),
        ("crew_routing", "Crew routing", "Construct legal crew duties or pairings over a transport/service network."),
    ],
    "scheduling": [
        ("single_machine_scheduling", "Single-machine scheduling", "Sequence jobs on one machine under declared objectives and constraints."),
        ("parallel_machine_scheduling", "Parallel-machine scheduling", "Assign and sequence jobs across parallel resources."),
        ("flow_shop_scheduling", "Flow-shop scheduling", "Sequence jobs traversing machines in a common order."),
        ("job_shop_scheduling", "Job-shop scheduling", "Schedule job-specific operation routes across shared machines."),
        ("flexible_job_shop", "Flexible job-shop scheduling", "Choose eligible machines and times for job-shop operations."),
        ("open_shop_scheduling", "Open-shop scheduling", "Schedule job operations without a fixed machine order."),
        ("batch_scheduling", "Batch scheduling", "Form and sequence compatible production/service batches."),
        ("sequence_dependent_setup", "Sequence-dependent setup scheduling", "Schedule work with transition-dependent setup times/costs."),
        ("resource_constrained_project_scheduling", "Resource-constrained project scheduling", "Schedule precedence-constrained activities under renewable/nonrenewable resources."),
        ("project_portfolio_scheduling", "Project-portfolio scheduling", "Select and schedule coupled projects under shared resources and strategic objectives."),
        ("workforce_rostering", "Workforce rostering", "Assign people to shifts while meeting coverage, legality, skills and preferences."),
        ("employee_scheduling", "Employee task scheduling", "Assign employees to timed work under eligibility, availability and fairness constraints."),
        ("timetabling", "Timetabling", "Assign events to time/space slots under conflict and preference constraints."),
        ("appointment_scheduling", "Appointment scheduling", "Allocate appointment slots under demand, no-show, service and capacity uncertainty."),
        ("operating_room_scheduling", "Operating-room scheduling", "Schedule cases, staff, rooms and downstream resources under clinical constraints."),
        ("maintenance_scheduling", "Maintenance scheduling", "Time preventive/corrective work against failure, production and crew constraints."),
        ("turnaround_scheduling", "Turnaround/outage scheduling", "Coordinate dense interdependent maintenance activities in a shutdown window."),
        ("real_time_rescheduling", "Real-time rescheduling", "Repair an active schedule after disruptions while controlling instability."),
    ],
    "inventory_planning": [
        ("eoq", "Economic order quantity", "Balance stylized ordering and holding cost under deterministic assumptions."),
        ("newsvendor", "Newsvendor decision", "Choose a single-period quantity under uncertain demand and asymmetric over/underage costs."),
        ("base_stock_policy", "Base-stock policy", "Replenish inventory toward a target position under declared review and lead-time rules."),
        ("continuous_review_inventory", "Continuous-review inventory", "Set reorder points and quantities under continuous state monitoring."),
        ("periodic_review_inventory", "Periodic-review inventory", "Set order-up-to or quantity decisions at periodic reviews."),
        ("multi_echelon_inventory", "Multi-echelon inventory optimization", "Set inventories and replenishment across coupled network echelons."),
        ("service_parts_inventory", "Service-parts inventory", "Position intermittent-demand spares to meet availability/service targets."),
        ("lot_sizing", "Lot sizing", "Choose production/order quantities and setups over time."),
        ("production_planning", "Production planning", "Allocate capacity, materials and production quantities across products and periods."),
        ("sales_operations_planning", "Sales and operations planning", "Balance aggregate demand, supply, capacity and financial objectives across horizons."),
        ("capacity_planning", "Capacity planning", "Choose resource capacity additions, reservations or allocations over a horizon."),
        ("supply_demand_matching", "Supply-demand matching", "Allocate constrained supply to demand with service, priority and substitution rules."),
        ("assortment_optimization", "Assortment optimization", "Select offered products under demand substitution, space and commercial constraints."),
        ("safety_stock_optimization", "Safety-stock optimization", "Set buffers against demand and supply uncertainty under service targets."),
    ],
    "queues_reliability": [
        ("queueing_analysis", "Queueing analysis", "Estimate delay, queue length, utilization and loss under a declared queue model."),
        ("queueing_network", "Queueing-network analysis", "Analyze coupled service stations and customer routing."),
        ("loss_network", "Loss-network analysis", "Analyze blocking when requests require simultaneous finite resources."),
        ("capacity_dimensioning", "Capacity dimensioning", "Choose server/resource capacity to satisfy delay, loss or utilization criteria."),
        ("call_center_staffing", "Call-center staffing", "Set time-varying staffing against stochastic arrivals, service and abandonment."),
        ("reliability_block_diagram", "Reliability-block analysis", "Compute system reliability from series/parallel component structure."),
        ("markov_reliability", "Markov reliability model", "Model failure/repair state transitions and availability."),
        ("fault_tree_analysis", "Fault-tree analysis", "Derive system failure logic and probabilities from component events."),
        ("availability_optimization", "Availability optimization", "Choose redundancy, maintenance or spares to meet availability/cost goals."),
        ("renewal_process_analysis", "Renewal-process analysis", "Analyze repeated event/failure cycles and long-run reward."),
        ("survival_and_hazard_decision", "Survival/hazard decision analysis", "Use time-to-event risk in maintenance, replacement or intervention decisions."),
    ],
    "simulation": [
        ("monte_carlo_simulation", "Monte Carlo simulation", "Propagate sampled uncertainty through a model to estimate outcome distributions."),
        ("discrete_event_simulation", "Discrete-event simulation", "Simulate state changes at discrete event times in process/resource systems."),
        ("system_dynamics", "System-dynamics simulation", "Simulate aggregate stocks, flows and feedback loops over continuous time."),
        ("agent_based_simulation", "Agent-based simulation", "Simulate interacting autonomous modeled entities; this is not an LLM or software-agent runtime."),
        ("multimethod_simulation", "Multimethod simulation", "Combine discrete-event, system-dynamics and/or agent-based models with explicit interfaces."),
        ("continuous_simulation", "Continuous simulation", "Integrate continuous-time differential/algebraic system dynamics."),
        ("hybrid_discrete_continuous_simulation", "Hybrid discrete-continuous simulation", "Couple event-driven changes with continuous dynamics."),
        ("rare_event_simulation", "Rare-event simulation", "Estimate low-probability outcomes using governed variance-reduction or importance-sampling methods."),
        ("digital_twin_experiment", "Digital-twin experiment", "Run governed what-if experiments against a synchronized model of an operational asset/system."),
        ("simulation_input_modeling", "Simulation input modeling", "Fit and validate distributions, dependence and nonstationarity for simulation inputs."),
        ("simulation_verification", "Simulation verification", "Check that implementation correctly realizes the conceptual model."),
        ("simulation_validation", "Simulation validation", "Assess whether the conceptual/computational model is fit for its intended real-world use."),
        ("simulation_output_analysis", "Simulation output analysis", "Estimate uncertainty, warm-up effects and steady/transient responses from replications."),
        ("ranking_and_selection", "Simulation ranking and selection", "Allocate replications to select among alternatives with statistical error control."),
    ],
    "sequential_control": [
        ("dynamic_programming", "Dynamic programming", "Solve sequential decisions through Bellman recurrences."),
        ("approximate_dynamic_programming", "Approximate dynamic programming", "Approximate values or policies when exact state-space recursion is intractable."),
        ("markov_decision_process", "Markov decision process", "Optimize a policy for fully observed Markov state transitions."),
        ("partially_observed_mdp", "Partially observed MDP", "Optimize actions using beliefs when system state is not directly observed."),
        ("semi_markov_decision_process", "Semi-Markov decision process", "Model decisions with non-geometric or action-dependent transition times."),
        ("stochastic_control", "Stochastic control", "Choose feedback controls for stochastic dynamic systems."),
        ("optimal_control", "Optimal control", "Optimize continuous-time state/control trajectories under dynamics and path constraints."),
        ("model_predictive_control", "Model-predictive control", "Repeatedly optimize a finite horizon and apply the first control under feedback."),
        ("robust_control", "Robust control", "Design controls with stability/performance guarantees over declared uncertainty."),
        ("adaptive_control", "Adaptive control", "Update controller parameters or models from observed system response."),
        ("optimal_stopping", "Optimal stopping", "Choose when to stop a stochastic process to optimize expected or risk-sensitive reward."),
        ("multi_armed_bandit", "Multi-armed bandit", "Balance information acquisition and reward across repeated alternatives."),
        ("rolling_horizon_optimization", "Rolling-horizon optimization", "Repeatedly re-solve a finite planning window as time and observations advance."),
    ],
    "markets_games_revenue": [
        ("noncooperative_game", "Noncooperative-game analysis", "Analyze strategic choices and equilibria among independent participants."),
        ("cooperative_game", "Cooperative-game analysis", "Analyze coalition value and allocation among cooperating participants."),
        ("nash_equilibrium", "Nash-equilibrium computation", "Find strategy profiles with no profitable unilateral deviation under the model."),
        ("stackelberg_game", "Stackelberg-game optimization", "Optimize leader action anticipating follower best responses."),
        ("mechanism_design", "Mechanism design", "Design rules to produce desired allocation/incentive properties under private information."),
        ("auction_design", "Auction design and clearing", "Specify bids, allocation and payment/clearing rules."),
        ("market_clearing", "Market clearing", "Compute feasible allocation and prices balancing supply and demand under market rules."),
        ("matching_market", "Matching-market design", "Match participants under preferences, capacities and stability/fairness requirements."),
        ("revenue_management", "Revenue management", "Control availability/allocation of perishable capacity under uncertain demand."),
        ("dynamic_pricing", "Dynamic pricing", "Choose prices over time under demand response, inventory and policy constraints."),
        ("markdown_optimization", "Markdown optimization", "Schedule price reductions for finite inventory over a selling horizon."),
        ("bid_optimization", "Bid optimization", "Choose bid quantities/prices under market, risk and operational constraints."),
        ("portfolio_optimization", "Portfolio optimization", "Choose positions under return, risk, liquidity and policy constraints."),
        ("contract_design", "Contract design", "Choose terms to align incentives, allocate risk and satisfy authority constraints."),
    ],
    "human_decision": [
        ("multi_criteria_decision_analysis", "Multi-criteria decision analysis", "Compare alternatives across non-commensurate criteria using an explicit preference model."),
        ("multi_attribute_utility", "Multi-attribute utility analysis", "Construct utility across attributes under elicited independence and risk assumptions."),
        ("analytic_hierarchy_process", "Analytic hierarchy process", "Derive relative priorities from hierarchical pairwise comparisons with consistency checks."),
        ("outranking", "Outranking analysis", "Compare alternatives using concordance, discordance and veto semantics."),
        ("pareto_frontier_analysis", "Pareto-frontier analysis", "Enumerate or approximate nondominated trade-offs among objectives."),
        ("satisficing", "Satisficing", "Seek alternatives meeting aspiration levels rather than maximizing a scalar objective."),
        ("scenario_planning", "Scenario planning", "Construct plausible futures and evaluate strategy robustness without assigning false probabilities."),
        ("robust_decision_making", "Robust decision making", "Search policies that perform acceptably across many plausible futures."),
        ("value_of_information", "Value-of-information analysis", "Quantify the expected decision value of resolving uncertainty."),
        ("preference_elicitation", "Preference elicitation", "Elicit weights, utilities, priorities, thresholds or partial orders from decision makers."),
        ("group_decision", "Group-decision analysis", "Aggregate or deliberate over multiple actors' preferences without hiding disagreement."),
        ("decision_conferencing", "Decision conferencing", "Facilitate structured real-time model building and deliberation with accountable stakeholders."),
        ("human_override_analysis", "Human override analysis", "Record and assess why an authorized human accepted, changed or rejected a recommendation."),
    ],
    "postsolve_qualification": [
        ("feasibility_validation", "Independent feasibility validation", "Recompute every material constraint against the bound model/data snapshot."),
        ("objective_recomputation", "Objective recomputation", "Independently recompute objectives and components from returned decisions."),
        ("optimality_gap_analysis", "Optimality-gap analysis", "Interpret incumbent and bound under exact sign, scaling and tolerance semantics."),
        ("numerical_quality_analysis", "Numerical-quality analysis", "Inspect residuals, conditioning, scaling and integrality violations."),
        ("infeasibility_diagnosis", "Infeasibility diagnosis", "Identify conflicting constraints/bounds and distinguish proof from suspected infeasibility."),
        ("iis_analysis", "Irreducible inconsistent subsystem analysis", "Find a minimal-by-inclusion infeasible subsystem under solver semantics."),
        ("feasibility_relaxation", "Feasibility relaxation", "Find governed constraint/bound changes that recover feasibility."),
        ("unboundedness_diagnosis", "Unboundedness diagnosis", "Validate unbounded status and inspect a primal ray or modeling omission."),
        ("sensitivity_analysis", "Sensitivity analysis", "Measure solution or objective response to input perturbations."),
        ("post_optimality_analysis", "Post-optimality analysis", "Analyze valid ranges, reduced costs, shadow prices or discrete alternatives after solving."),
        ("shadow_price_analysis", "Shadow-price analysis", "Interpret marginal objective value of resource/constraint changes within validity ranges."),
        ("solution_pool_analysis", "Solution-pool analysis", "Collect and compare multiple feasible or near-optimal solutions."),
        ("alternative_solution_generation", "Alternative-solution generation", "Find structurally diverse alternatives satisfying quality thresholds."),
        ("stability_analysis", "Decision stability analysis", "Assess whether small input changes cause material decision changes."),
        ("stress_testing", "Decision stress testing", "Evaluate a candidate plan/policy against adverse scenarios and operational failures."),
        ("solver_benchmarking", "Solver benchmarking", "Compare qualified solvers/configurations on representative instances under a controlled protocol."),
        ("algorithm_ablation", "Algorithm ablation", "Measure the contribution of cuts, heuristics, neighborhoods or other components."),
        ("deterministic_replay", "Deterministic replay", "Reproduce a solve or explicitly explain nondeterministic divergence using bound artifacts and seeds."),
        ("actual_vs_planned_reconciliation", "Actual-versus-planned reconciliation", "Compare executed decisions and outcomes with the recommended plan and explain divergence."),
        ("decision_policy_monitoring", "Decision-policy monitoring", "Monitor feasibility, value, drift, overrides, latency and harms after deployment."),
    ],
}


def method_record(family: str, slug: str, name: str, intent: str) -> dict:
    spec = FAMILIES[family]
    heuristic = family in {"constructive_heuristic", "local_metaheuristic", "hybrid_search"}
    return {
        "method_id": f"or.method.{slug}",
        "edition": EDITION,
        "status": "sourced_candidate",
        "family_id": f"or.family.{family}",
        "name": name,
        "aliases": [],
        "intent": intent,
        "inputs": spec["inputs"],
        "outputs": spec["outputs"],
        "assumptions": spec["assumptions"],
        "guarantees": [spec["guarantee"]],
        "failure_result_states": [
            "invalid_model_or_data",
            "unsupported_capability",
            "infeasible_or_no_admissible_solution",
            "unbounded_or_ill_posed",
            "resource_limit_with_incumbent",
            "resource_limit_without_incumbent",
            "numerical_failure",
            "cancelled_or_interrupted",
        ],
        "runtime_budget": {
            "required_dimensions": ["wall_time", "deterministic_work_or_iterations", "memory", "threads_or_devices", "solution_or_node_limit"],
            "anytime": heuristic or family in {"exact_algorithm", "routing", "scheduling", "postsolve_qualification"},
            "cancellation_contract_required": True,
        },
        "evidence_refs": spec["evidence"],
        "compiler_implications": [
            "Select only an implementation whose offer satisfies the typed method and model requirements.",
            "Bind model, data, configuration, provider version, random seed and runtime budget into the run digest.",
            "Lower provider-specific statuses into the common result algebra without strengthening claims.",
        ],
        "gaps": ["Cross-industry qualification and independent implementation comparison remain open for this candidate."],
        "llm_dependency": "none",
    }


METHODS = [
    method_record(family, slug, name, intent)
    for family, items in METHOD_SPECS.items()
    for slug, name, intent in items
]


EXPERT_ROWS = [
    ("george_dantzig", "George Dantzig", "historical", ["linear programming", "simplex", "large-scale planning"], "Separate the algebraic model from its solution procedure; proofs, structure and operational formulation all matter.", ["src.informs.methodologies"]),
    ("richard_bellman", "Richard Bellman", "historical", ["dynamic programming", "optimal control"], "State, action, transition and value recursion are first-class semantic objects, and state-space explosion is a design constraint.", ["src.informs.methodologies"]),
    ("ralph_gomory", "Ralph Gomory", "historical", ["integer programming", "cutting planes"], "A discrete optimum needs valid bounds and cuts; a good incumbent is not a proof.", ["src.miplib"]),
    ("robert_bixby", "Robert Bixby", "contemporary", ["MIP solver engineering", "simplex", "commercial optimization"], "Performance comes from integrated presolve, cuts, heuristics, numerics and engineering, not one named algorithm.", ["src.miplib", "src.gurobi.releases"]),
    ("dimitris_bertsimas", "Dimitris Bertsimas", "contemporary", ["robust optimization", "stochastic systems", "discrete optimization", "applications"], "Uncertainty sets and tractability are model decisions; robustness must state what is protected against and at what conservatism cost.", ["src.bertismas"]),
    ("aharon_ben_tal", "Aharon Ben-Tal", "contemporary", ["robust optimization", "conic optimization"], "Robust counterparts and uncertainty geometry should be explicit compiler artifacts.", ["src.mos.home", "src.cvxpy.dcp"]),
    ("alexander_shapiro", "Alexander Shapiro", "contemporary", ["stochastic programming", "risk", "sample approximation"], "Sampling error, nonanticipativity and risk measures belong in the method contract, not only in data preparation.", ["src.informs.journals"]),
    ("yinyu_ye", "Yinyu Ye", "contemporary", ["interior-point methods", "conic optimization", "DRO", "market equilibrium"], "Algorithmic complexity, numerical realization and application structure need separate evidence.", ["src.ye"]),
    ("michel_goemans", "Michel Goemans", "contemporary", ["approximation algorithms", "combinatorial optimization"], "Approximation is a typed theorem over a precise problem variant, not a synonym for heuristic.", ["src.goemans"]),
    ("george_nemhauser", "George Nemhauser", "contemporary", ["integer programming", "combinatorial optimization"], "Strong formulations and polyhedral structure often dominate naive algorithm choice.", ["src.miplib", "src.informs.journals"]),
    ("gerard_cornuejols", "Gérard Cornuéjols", "contemporary", ["integer programming", "valid inequalities", "combinatorial optimization"], "Model structure and valid inequalities should survive lowering and be inspectable.", ["src.miplib", "src.scip.v9"]),
    ("andrea_lodi", "Andrea Lodi", "contemporary", ["mixed-integer programming", "solver engineering", "decomposition"], "Industrial MIP is an interaction of formulation, automatic machinery and domain-specific decomposition.", ["src.miplib", "src.scip.v9"]),
    ("pascal_van_hentenryck", "Pascal Van Hentenryck", "contemporary", ["constraint programming", "optimization", "disaster and energy applications"], "Constraint programming and mathematical programming are complementary representational and search systems.", ["src.vanhentenryck"]),
    ("laurent_perron", "Laurent Perron", "contemporary", ["CP-SAT", "constraint programming", "routing"], "Portfolio search, propagation, SAT learning and LP relaxation can be composed while preserving explicit status semantics.", ["src.dagstuhl.cp_sat_lp", "src.google.cp_sat"]),
    ("frederic_didier", "Frédéric Didier", "contemporary", ["CP-SAT", "constraint programming"], "A solver receipt must distinguish feasible, optimal, infeasible, invalid and unknown results.", ["src.dagstuhl.cp_sat_lp", "src.google.cp_sat"]),
    ("cynthia_barnhart", "Cynthia Barnhart", "contemporary", ["large-scale optimization", "air transportation", "network systems"], "Enterprise OR requires domain-specific decomposition, executable constraints and operations feedback around the mathematical core.", ["src.barnhart"]),
    ("gilbert_laporte", "Gilbert Laporte", "contemporary", ["vehicle routing", "location", "logistics"], "Routing names hide many materially different variants; time windows, fleet, pickup-delivery and uncertainty must be typed.", ["src.tsplib", "src.pyvrp"]),
    ("paolo_toth", "Paolo Toth", "contemporary", ["vehicle routing", "combinatorial optimization"], "Benchmarkable problem definitions and hybrid exact/heuristic methods are essential for routing systems.", ["src.tsplib", "src.pyvrp"]),
    ("fred_glover", "Fred Glover", "historical", ["tabu search", "metaheuristics", "scatter search"], "Adaptive memory and search policy are explicit algorithm semantics, not arbitrary solver magic.", ["src.informs.methodologies"]),
    ("marco_dorigo", "Marco Dorigo", "contemporary", ["ant-colony optimization", "metaheuristics"], "Population communication, randomness and update rules must be captured for replay and qualification.", ["src.informs.methodologies"]),
    ("kenneth_sorensen", "Kenneth Sörensen", "contemporary", ["metaheuristics", "industrial optimization"], "A metaphor is not a method contract; operators, acceptance, budget and evidence should be specified directly.", ["src.informs.journals"]),
    ("edmund_burke", "Edmund Burke", "contemporary", ["hyper-heuristics", "scheduling", "timetabling"], "Heuristic selection/generation is a separate level with its own training, generalization and budget contract.", ["src.minizinc.challenge"]),
    ("warren_powell", "Warren Powell", "contemporary", ["sequential decision analytics", "approximate dynamic programming", "transportation"], "Unify decisions through state, information, action, transition and objective while distinguishing policy classes.", ["src.powell"]),
    ("michael_pinedo", "Michael Pinedo", "contemporary", ["scheduling", "manufacturing and service operations"], "Scheduling requires a vocabulary of machine environments, job characteristics and objectives before selecting algorithms.", ["src.informs.methodologies"]),
    ("barry_nelson", "Barry Nelson", "contemporary", ["simulation output analysis", "ranking and selection"], "Simulation decisions need replication uncertainty and selection error control, not a single run.", ["src.wsc"]),
    ("michael_fu", "Michael Fu", "contemporary", ["simulation optimization", "stochastic gradient estimation"], "Optimization over noisy simulation responses needs an experiment and uncertainty contract.", ["src.wsc"]),
    ("david_simchi_levi", "David Simchi-Levi", "contemporary", ["supply chains", "inventory", "revenue management"], "End-to-end decisions couple forecasting, risk, optimization and execution; the interfaces must be explicit.", ["src.informs.journals"]),
    ("georgia_perakis", "Georgia Perakis", "contemporary", ["pricing", "revenue management", "supply chains"], "Demand response, optimization and policy/equity constraints must be modeled together without conflating prediction with decision.", ["src.informs.journals"]),
    ("john_hooker", "John Hooker", "contemporary", ["integrated optimization", "constraint programming", "decision ethics"], "Mathematical validity does not settle ethical legitimacy; value judgments and authority need explicit representation.", ["src.informs.journals", "src.informs.sections"]),
    ("haihao_lu", "Haihao Lu", "contemporary", ["first-order optimization", "PDLP", "large-scale LP"], "Algorithm and hardware structure can alter the practical solvable scale; accuracy and termination remain governed.", ["src.google.pdlp", "src.cupdlp"]),
    ("julian_hall", "Julian Hall", "contemporary", ["simplex", "HiGHS", "open solver engineering"], "Open solver infrastructure enables provider qualification, but versions and supported model classes must be pinned.", ["src.highs.home"]),
    ("paul_goulart", "Paul Goulart", "contemporary", ["conic optimization", "control", "Clarabel"], "A solver-specific embedding and certificate model belongs below a solver-neutral conic IR.", ["src.clarabel"]),
]


EXPERTS = [
    {
        "expert_id": f"or.expert.{slug}", "edition": EDITION, "name": name, "status": status,
        "expertise": expertise, "what_to_learn": learning, "evidence_refs": evidence,
        "limitations": "Representative expert, not an endorsement or exhaustive expert census; claims are limited to cited profiles/publications.",
    }
    for slug, name, status, expertise, learning, evidence in EXPERT_ROWS
]


COMPANY_ROWS = [
    ("gurobi", "Gurobi Optimization", "solver_company", "pure_or_specialist", ["mathematical optimization solver", "deployment services"], ["Gurobi Optimizer"], ["src.gurobi.status", "src.gurobi.releases"]),
    ("hexaly", "Hexaly", "solver_and_modeling_company", "pure_or_specialist", ["enriched MIP", "combinatorial optimization", "simulation optimization", "cloud solve"], ["Hexaly Optimizer", "Hexaly Modeler", "Hexaly Studio", "Hexaly Cloud"], ["src.hexaly"]),
    ("ampl", "AMPL Optimization", "modeling_system_company", "pure_or_specialist", ["algebraic modeling", "solver interfaces", "deployment tooling"], ["AMPL", "AMPL APIs"], ["src.ampl"]),
    ("gams", "GAMS Development Corp.", "modeling_system_company", "pure_or_specialist", ["algebraic modeling", "solver interfaces", "model/data exchange"], ["GAMS"], ["src.gams"]),
    ("ortec", "ORTEC", "vertical_optimization_software_and_services", "analytics_or_specialist", ["routing", "workforce", "supply-chain planning", "custom decision intelligence"], ["ORTEC supply-chain products", "ORTEC Workforce", "ORTEC Lumina"], ["src.ortec"]),
    ("decisionbrain", "DecisionBrain", "planning_scheduling_solution_company", "analytics_or_specialist", ["planning", "scheduling", "routing", "inventory", "low-code solution composition"], ["DB Gene", "Optimization Server"], ["src.decisionbrain"]),
    ("artelys", "Artelys", "or_consulting_software_solver_company", "analytics_or_specialist", ["energy systems", "scheduling", "network design", "nonlinear optimization", "constraint programming"], ["Artelys Crystal", "Knitro", "Kalis"], ["src.artelys"]),
    ("timefold", "Timefold", "planning_solver_company", "pure_or_specialist", ["constraint-satisfaction planning", "scheduling", "routing"], ["Timefold Solver", "Timefold Platform"], ["src.timefold"]),
    ("nextmv", "Nextmv", "decision_operations_company", "pure_or_specialist", ["decision application runs", "optimization deployment", "solver/model operations"], ["Nextmv Platform"], ["src.nextmv"]),
    ("anylogic", "The AnyLogic Company", "simulation_software_company", "pure_or_specialist", ["discrete-event simulation", "system dynamics", "agent-based simulation", "multimethod simulation"], ["AnyLogic", "AnyLogic Cloud"], ["src.anylogic"]),
    ("aimms", "AIMMS", "optimization_modeling_and_application_company", "pure_or_specialist", ["optimization modeling", "supply-chain applications", "solver integration"], ["AIMMS Developer", "AIMMS SC Navigator"], ["src.aimms"]),
    ("frontline", "Frontline Systems", "optimization_analytics_software_company", "analytics_or_specialist", ["spreadsheet optimization", "simulation", "analytics"], ["Analytic Solver"], ["src.frontline"]),
    ("river_logic", "River Logic", "decision_optimization_company", "analytics_or_specialist", ["prescriptive analytics", "enterprise planning", "digital planning twins"], ["Enterprise Optimizer"], ["src.riverlogic"]),
    ("optimal_dynamics", "Optimal Dynamics", "vertical_decision_software_company", "pure_or_specialist", ["truckload planning", "sequential decision analytics"], ["Dynamic Load Planning"], ["src.powell", "src.optimal_dynamics"]),
    ("atoptima", "Atoptima", "optimization_api_company", "pure_or_specialist", ["routing", "packing", "scheduling optimization APIs"], ["optimization APIs"], ["src.atoptima"]),
    ("simio", "Simio", "simulation_software_company", "pure_or_specialist", ["discrete-event simulation", "scheduling", "digital twins"], ["Simio"], ["src.simio", "src.wsc"]),
    ("optibus", "Optibus", "vertical_optimization_software_company", "analytics_or_specialist", ["public-transport planning", "scheduling", "rostering"], ["Optibus platform"], ["src.optibus"]),
    ("solvoyo", "Solvoyo", "supply_chain_optimization_company", "analytics_or_specialist", ["supply-chain planning", "inventory", "allocation", "transport"], ["Solvoyo platform"], ["src.solvoyo"]),
    ("mathco", "MathCo", "data_analytics_solution_company", "analytics_specialist_but_ai_heavy", ["custom data products", "decision applications", "scheduling", "heuristics", "data engineering"], ["NucliOS", "custom scheduling and analytics solutions"], ["src.mathco.scheduling", "src.mathco.heuristics"]),
]


COMPANIES = [
    {
        "company_id": f"or.company.{slug}", "edition": EDITION, "name": name, "company_pattern": pattern,
        "specialist_posture": purity, "claimed_capabilities": capabilities, "products_or_services": products,
        "verified_capabilities": ["Official evidence confirms the organization publicly offers the named products/services; independent performance and outcome verification is not implied."],
        "delivery_model": "software, services, or both as stated by the provider",
        "evidence_refs": evidence, "evidence_posture": "provider_claim_unless_primary_research_or_independent_benchmark_is_separately_cited",
        "compiler_learnings": ["Keep domain IR and result algebra provider-neutral.", "Model provider capabilities as versioned offers with qualification evidence.", "Do not create a bounded context or analytical type from a marketing label."],
        "limitations": "Company coverage is representative and open-world; corporate ownership, products and positioning require recurring review.",
        "llm_core_dependency": "not_required_for_the_classified_or_capabilities",
    }
    for slug, name, pattern, purity, capabilities, products, evidence in COMPANY_ROWS
]


INNOVATION_ROWS = [
    ("pdlp", "Practical PDLP for large-scale LP", 2021, "research_and_open_implementation", "Adapted primal-dual hybrid gradient with presolve, scaling, adaptive steps and restart made first-order LP solving practically competitive at large scale.", ["src.google.pdlp", "src.google.large_scale"], "First-order accuracy/runtime trade-offs remain instance dependent."),
    ("cp_sat_lp", "CP-SAT-LP hybrid solver architecture", 2023, "research_and_open_implementation", "Integrated SAT/LCG, propagation, simplex/MIP technology and diverse portfolio workers in a production constraint solver.", ["src.dagstuhl.cp_sat_lp", "src.google.cp_sat"], "Integral bounded modeling and solver-specific supported constraints must be respected."),
    ("mathopt", "MathOpt solver-neutral result and capability interface", 2024, "official_api", "Exposed interchangeable solvers with common model features, detailed termination, rays, bounds, warm starts, limits and solver-independent parameters.", ["src.google.mathopt", "src.google.mathopt_rest"], "Remote service remains experimental and capability support varies by backend."),
    ("scip9", "SCIP Optimization Suite 9.0", 2024, "peer_reviewed_release_report", "Added improved symmetry, nonlinear handlers, primal heuristics, cuts, branching, solver interfaces including Rust/C++, and suite-wide performance work.", ["src.scip.v9", "src.scip.release9"], "Release evidence does not guarantee superiority on a target corpus."),
    ("scip10", "SCIP Optimization Suite 10", 2025, "official_release", "Advanced the open CIP/MIP/MINLP, presolve and decomposition suite as a coordinated versioned distribution.", ["src.scip.home"], "Detailed feature-by-feature adjudication against version 9 remains a gap."),
    ("gurobi11_global_minlp", "Gurobi 11 global nonlinear/MINLP support", 2023, "official_release_claim", "Expanded exact nonlinear-function handling and global mixed-integer nonlinear optimization surfaces.", ["src.gurobi.releases"], "Provider claim; supported function classes, tolerances and global/local statuses must be checked per version."),
    ("gurobi13_pdhg", "Gurobi 13 PDHG on CPU/GPU", 2025, "official_release_claim", "Added a primal-dual hybrid-gradient path for huge LPs on CPU and GPU alongside a nonlinear barrier path.", ["src.gurobi.releases"], "Provider claim; benchmark and qualification evidence are workload specific."),
    ("cupdlp", "GPU-accelerated restarted PDHG for LP", 2023, "primary_research_and_open_software", "Demonstrated GPU-first first-order LP solving competitive on standard benchmark sets and exposed open implementations.", ["src.cupdlp"], "Hardware, precision, scaling and target accuracy materially affect comparisons."),
    ("cupdlpx", "cuPDLPx enhanced GPU first-order solver", 2025, "research_software", "Added restarted Halpern PDHG, adaptive restart and PID-controlled primal weighting for GPU LP solving.", ["src.cupdlpx"], "Ongoing research software; independent reproduction and production qualification remain required."),
    ("hipdlp", "HiPDLP GPU path in HiGHS", 2026, "official_roadmap_claim", "HiGHS announced an in-suite GPU PDLP implementation path intended to replace cuPDLP-C integration.", ["src.highs.hipdlp"], "Roadmap/development claim, not a completed stable capability contract."),
    ("clarabel", "Clarabel homogeneous-embedding conic solver", 2024, "primary_research_and_open_software", "Provided open Rust/Julia conic optimization with direct quadratic objectives, infeasibility detection and a novel homogeneous embedding.", ["src.clarabel"], "Convex conic scope; performance and numerical qualification remain instance dependent."),
    ("pyvrp", "PyVRP high-performance hybrid genetic search", 2024, "peer_reviewed_open_software", "Packaged a customizable C++/Python hybrid genetic search with strong VRP benchmark results and reusable operators.", ["src.pyvrp"], "Supported VRP variants and empirical quality do not imply universal routing coverage or proof of optimality."),
    ("highs_open_mip_qp", "HiGHS expansion as open LP/MIP/QP infrastructure", 2021, "official_open_project", "Matured a permissively licensed, multi-interface solver suite spanning large sparse LP, MIP and QP.", ["src.highs.home"], "The start year marks the review window, not a single release event; capability is version-specific."),
    ("minizinc_qualification", "Containerized MiniZinc solver qualification", 2026, "official_benchmark_protocol", "Challenge rules now specify containerized entries, common flags, budgets, intermediate solutions and quality/optimality scoring across solver classes.", ["src.minizinc.challenge"], "Competition performance is not equivalent to production suitability or all-instance superiority."),
    ("typed_solver_results", "Richer solver-neutral termination/result algebras", 2024, "interface_evolution", "MathOpt and MathOptInterface expose termination separately from primal/dual result status, limits, rays, bounds and result counts.", ["src.google.mathopt_rest", "src.jump.moi_solutions"], "Backends may not expose every certificate; adapters must not infer missing proof."),
    ("automatic_decomposition_productization", "Automatic decomposition as a product capability", 2026, "provider_claim", "Hexaly publicly positions automatic decomposition inside an enriched MIP/combinatorial modeling solver experience.", ["src.hexaly"], "Marketing claim; decomposition detection and performance need independent corpus qualification."),
    ("multimethod_simulation_productization", "Operational multimethod simulation", 2021, "established_capability_with_recent_product_evolution", "Simulation products increasingly package discrete-event, agent-based and system-dynamics composition with cloud experiments and optimization integration.", ["src.anylogic", "src.wsc"], "The conceptual innovation predates five years; this record concerns recent operational productization, not invention."),
    ("decisionops", "DecisionOps/run-governance product pattern", 2022, "provider_pattern", "Optimization vendors increasingly expose models as versioned runs with deployment, observability, scenario testing and operational APIs.", ["src.nextmv", "src.google.mathopt"], "No neutral DecisionOps standard was found; current semantics are provider-specific."),
]


INNOVATIONS = [
    {
        "innovation_id": f"or.innovation.{slug}", "edition": EDITION, "name": name, "year": year,
        "evidence_posture": posture, "non_llm": True, "problem_and_innovation": innovation,
        "evidence_refs": evidence, "limits": [limits],
        "compiler_implications": ["Represent this as a versioned capability offer or method implementation, not as a new business domain by default.", "Require benchmark, numerical, licensing, hardware and result-contract qualification before automatic selection."],
    }
    for slug, name, year, posture, innovation, evidence, limits in INNOVATION_ROWS
]


CONTEXT_ROWS = [
    ("decision_problem", "What operational choice is being made, by whom, over what horizon and affected scope?", ["decision framing", "scope", "owner", "affected parties", "horizon", "baseline"], ["solver implementation", "industry ontology ownership"]),
    ("decision_variable_domain", "What choices and state variables exist, and what values, units and identities may they take?", ["decision variables", "domains", "units", "index sets", "state variables"], ["objective preference", "provider data structures"]),
    ("objective_preference", "How are outcomes valued, prioritized and traded off?", ["objectives", "goals", "weights", "lexicographic priorities", "Pareto preference", "aspiration levels"], ["hard feasibility rules", "legal authority"]),
    ("constraint_policy", "Which restrictions are hard, soft, chance, conditional, relaxable or approval-gated?", ["constraint definitions", "hardness", "penalties", "relaxation authority", "precedence"], ["solver cuts", "UI validation alone"]),
    ("uncertainty_model", "What is unknown, when is it revealed and how is it represented?", ["random variables", "uncertainty sets", "ambiguity sets", "scenario processes", "information structure"], ["forecast model training", "generic data quality"]),
    ("scenario_set", "How are named possible futures versioned, weighted, stressed and related?", ["scenarios", "probabilities when justified", "stress variants", "scenario tree", "provenance"], ["simulation execution", "business planning workflow"]),
    ("model_ir", "What provider-neutral executable mathematical/constraint/network/simulation structure represents the decision?", ["model kinds", "expressions", "variables", "constraints", "objectives", "annotations"], ["domain problem framing", "provider-native bytecode"]),
    ("model_transformation", "Which semantics-preserving or explicitly lossy transformations lower a model?", ["canonicalization", "linearization", "reformulation", "relaxation", "presolve annotations", "proof obligations"], ["solver internal undocumented rewrites"]),
    ("decomposition_plan", "How is a model partitioned and how are master/subproblem results coordinated?", ["blocks", "couplings", "cut/column protocols", "convergence and proof semantics"], ["generic distributed compute scheduling"]),
    ("solver_capability", "What exact model, callback, certificate, limit, numeric and runtime features does an implementation offer?", ["requirements", "offers", "versions", "feature compatibility", "license and target"], ["business decision semantics", "provider marketing"]),
    ("solver_qualification", "Under what corpus and protocol is a solver/configuration acceptable for a problem regime?", ["benchmark corpus", "protocol", "hardware", "metrics", "failures", "reproducibility", "qualification verdict"], ["one-off solve execution"]),
    ("solver_selection", "Which qualified implementation and configuration should be bound to this model and budget?", ["candidate matching", "selection precedence", "fallback", "portfolio construction"], ["domain objective selection"]),
    ("solve_execution", "How is a bound model/data/configuration executed, observed, cancelled and receipted?", ["run identity", "artifact digests", "provider invocation", "progress", "cancellation", "resource accounting"], ["model authorship", "generic batch scheduler"]),
    ("budget_stopping", "What time, work, memory, node, solution, quality or risk limits govern termination?", ["budgets", "stopping rules", "anytime policy", "precharge", "cancellation semantics"], ["business SLA ownership"]),
    ("randomness_reproducibility", "How are random streams, seeds, parallel nondeterminism and replay governed?", ["seed sets", "random stream ownership", "determinism posture", "replay evidence"], ["general cryptographic randomness"]),
    ("exact_proof", "What evidence justifies optimal, infeasible or unbounded claims?", ["primal/dual bounds", "proof gap", "rays", "certificates", "checker results"], ["heuristic quality", "human approval"]),
    ("approximation_guarantee", "What formal approximation, regret or competitive guarantee applies to which problem class?", ["theorem identity", "ratio", "probability", "adversary/distribution model", "preconditions"], ["empirical heuristic benchmarking"]),
    ("heuristic_definition", "What construction/search procedure is actually being run and what quality is not guaranteed?", ["representation", "operators", "repair", "acceptance", "diversification", "budget", "seed"], ["solver qualification", "business constraints"]),
    ("neighborhood_move", "What local change is legal, how does it affect feasibility and how is it evaluated?", ["move types", "delta evaluation", "feasibility preservation", "undo", "composition"], ["global search policy"]),
    ("acceptance_diversification", "When are candidates accepted and how does search balance intensification/diversification?", ["acceptance", "memory", "temperature", "penalties", "restart", "population diversity"], ["domain objective semantics"]),
    ("hyperheuristic_portfolio", "How are algorithms/operators selected, configured, scheduled and learned from evidence?", ["portfolio", "algorithm selection", "configuration", "training corpus", "generalization limits"], ["individual algorithm internals"]),
    ("matheuristic_hybrid", "How are exact relaxations/bounds and heuristic neighborhoods composed without overstating guarantees?", ["hybrid protocol", "incumbent exchange", "bound ownership", "termination and proof propagation"], ["standalone solver implementation"]),
    ("infeasibility_diagnosis", "How are contradictory constraints identified and authorized repairs proposed?", ["conflict/IIS", "feasibility relaxation", "root-cause hypotheses", "repair authority"], ["arbitrary constraint deletion"]),
    ("solution_validation", "Is a returned solution feasible, correctly scored and admissible for execution?", ["independent checking", "tolerances", "objective recomputation", "domain validation", "verdict"], ["solver search"]),
    ("sensitivity_postoptimality", "How do decisions, values and bounds respond to input or constraint changes?", ["sensitivity", "dual/marginal values", "ranges", "discrete re-solves", "stability"], ["forecast sensitivity ownership"]),
    ("alternative_solution", "What materially diverse alternatives satisfy feasibility and quality thresholds?", ["solution pools", "diversity measures", "no-good constraints", "trade-off alternatives"], ["recommendation approval"]),
    ("simulation_model", "What conceptual and executable dynamic model is fit for a declared use?", ["entities/state", "events", "flows", "agents", "equations", "time", "verification", "validation"], ["LLM/software agents", "experiment orchestration"]),
    ("simulation_experiment", "How are scenarios, replications, random streams, warm-up and outputs designed and analyzed?", ["experiment design", "replications", "variance reduction", "output analysis", "selection"], ["simulation model semantics"]),
    ("queueing_system", "What arrival, service, routing, capacity and discipline define congestion?", ["arrival process", "service process", "queue discipline", "network", "stability", "performance measures"], ["generic workflow queues"]),
    ("sequential_decision_policy", "How does information state map to actions over time?", ["state", "observations", "actions", "transition", "policy", "value/risk", "nonanticipativity"], ["model-free LLM/agent behavior"]),
    ("human_decision", "How do preferences, judgment, authority and disagreement interact with analytical recommendations?", ["elicitation", "MCDA", "approval", "override", "rationale", "appeal"], ["solver optimality"]),
    ("decision_deployment", "How is a qualified solution or policy published as a callable, governed decision service?", ["decision contract", "input validation", "policy version", "fallback", "rollout", "rollback"], ["generic API gateway"]),
    ("plan_execution", "How are recommended decisions committed, dispatched and tracked against operational reality?", ["commitment", "dispatch", "execution acknowledgement", "exceptions", "replanning triggers"], ["source-system transaction ownership"]),
    ("outcome_feedback", "What happened after execution and how is value, harm and divergence attributed?", ["actual-versus-planned", "outcomes", "overrides", "exceptions", "causal caveats", "learning signals"], ["generic BI metric catalog"]),
    ("decision_lifecycle", "How are models, policies and providers versioned, reviewed, replayed, rolled back and retired?", ["versions", "drift", "review", "approval", "migration", "retirement", "historical replay"], ["general software release management"]),
    ("numerical_semantics", "What tolerances, scaling, precision and residual rules govern mathematical claims?", ["feasibility tolerance", "integrality tolerance", "optimality tolerance", "scaling", "precision", "NaN/Inf policy"], ["business unit semantics"]),
]


CONTEXTS = [
    {
        "context_id": f"or.context.{slug}", "edition": EDITION, "status": "candidate_not_adjudicated",
        "boundary_question": question, "inside": inside, "outside": outside,
        "intent": f"Own the language and invariants needed to answer: {question}",
        "inputs": ["versioned upstream contracts", "authority and policy configuration", "evidence-bound artifacts"],
        "outputs": ["typed owned artifact", "decision/refusal result", "provenance receipt"],
        "assumptions": ["neighbor contracts are versioned", "unknown semantics fail as typed gaps"],
        "guarantees": ["No claim is stronger than its bound evidence, model assumptions and result state.", "Provider-native concepts cross through an anti-corruption layer."],
        "failure_result_states": ["invalid_input", "missing_semantics", "unsupported_capability", "policy_refusal", "budget_exhausted", "inconclusive", "provider_failure"],
        "runtime_budget": {"required": True, "dimensions": ["latency", "work", "memory", "external_cost"], "not_applicable_must_be_explicit": True},
        "evidence_refs": ["src.informs.methodologies", "src.google.mathopt_rest", "src.jump.moi_solutions"],
        "compiler_implications": ["Give this candidate a single semantic owner only after context-map adjudication.", "Compile requirements to offers; never select a provider from name matching alone.", "Emit a typed gap when no implementation or vertical binding closes the contract."],
        "gaps": ["Aggregate boundaries, commands/events, ownership and neighbor relationships require cross-atlas adjudication."],
        "not_automatically_promoted_from": ["algorithm name", "vendor feature", "UI screen", "industry use-case label"],
        "llm_dependency": "none",
    }
    for slug, question, inside, outside in CONTEXT_ROWS
]


DECISION_SPECS = [
    ("decision_horizon", "What decision horizon, review cadence and information cut apply?", "DecisionHorizon", [], "analytical_design"),
    ("variable_domain", "Which variables exist and what domains, units, indices and state identities constrain them?", "VariableDomainPolicy", [], "semantic_closure"),
    ("objective_precedence", "How are objectives, goals, weights, lexicographic priorities and Pareto trade-offs governed?", "ObjectivePreferencePolicy", [], "analytical_design"),
    ("constraint_hardness", "Which constraints are hard, soft, chance, relaxable or authority-gated?", "ConstraintHardnessPolicy", [], "analytical_design"),
    ("uncertainty_representation", "Which scenarios, distributions, uncertainty sets and revelation structure apply?", "UncertaintyRepresentation", [], "analytical_design"),
    ("optimization_model_class", "Which LP, QP, conic, NLP, MIP, MINLP, CP, SAT, network or hybrid model class is valid?", "OptimizationModelClass", [], "logical_planning"),
    ("solver_requirement", "Which model features, callbacks, certificates, limits and target properties must a solver offer?", "SolverRequirement", [], "physical_binding"),
    ("numeric_tolerance", "Which feasibility, integrality, optimality, scaling and precision semantics govern claims?", "OptimizationNumericPolicy", [], "physical_binding"),
    ("solve_budget", "Which finite time, work, memory, node, solution and quality limits govern execution?", "SolveBudget", [], "deployment_binding"),
    ("certificate_requirement", "Which bound, gap, ray, proof, conflict or independent-check evidence is required?", "CertificateRequirement", [], "evidence_verification"),
    ("heuristic_quality", "Which feasibility, empirical-quality, reproducibility and no-optimality claim applies to heuristic search?", "HeuristicQualityPolicy", [], "analytical_design"),
    ("queue_arrival_process", "Which entity arrivals, batches, time variation, dependence, censoring and observation cut define queue demand?", "QueueArrivalProcessPolicy", [], "semantic_closure"),
    ("queue_service_process", "Which service-time, setup, interruption, preemption, failure and capacity semantics define service?", "QueueServiceProcessPolicy", [], "semantic_closure"),
    ("queue_structure_discipline", "Which stations, classes, buffers, routing, priorities, balking, reneging and service discipline define the queue or network?", "QueueStructureDiscipline", [], "semantic_closure"),
    ("queue_initialization_observation", "Which initial state, warm-up, transient, censoring and observation-window rules apply?", "QueueObservationPolicy", [], "analytical_design"),
    ("queue_performance_estimand", "Which waiting, queue, utilization, throughput, loss, abandonment or service-level quantity is estimated at what grain?", "QueuePerformanceEstimand", [], "analytical_design"),
    ("queue_stability", "Which recurrence, traffic-intensity, capacity or empirical stability condition is required before steady-state claims?", "QueueStabilityPolicy", [], "evidence_verification"),
    ("simulation_paradigm", "Which discrete-event, continuous, system-dynamics, agent-based or multimethod semantics apply?", "SimulationParadigm", ["discrete_event", "continuous", "system_dynamics", "agent_based", "multimethod"], "semantic_closure"),
    ("simulation_clock", "Which simulated-time, event-order, integration-step and simultaneous-event policy applies?", "SimulationClockPolicy", [], "semantic_closure"),
    ("simulation_random_stream", "How are random streams, seeds, substreams, common random numbers and replay governed?", "SimulationRandomStreamPolicy", [], "physical_binding"),
    ("simulation_initialization", "Which initial state, warm-up, transient deletion and termination policy apply?", "SimulationInitializationPolicy", [], "analytical_design"),
    ("simulation_replication", "How many replications, scenarios and variance-reduction pairings are required?", "SimulationReplicationPolicy", [], "analytical_design"),
    ("simulation_output", "Which estimands, confidence procedures, dependence and comparison rules govern output analysis?", "SimulationOutputPolicy", [], "analytical_design"),
    ("simulation_validation", "Which conceptual-model, code-verification, calibration, face-validity and predictive-validity evidence is required?", "SimulationValidationPolicy", [], "evidence_verification"),
]


def decision_record(spec: tuple) -> dict:
    slug, question, value_contract, allowed_values, phase = spec
    return {
        "decision_id": f"decision.operations_research.{slug}",
        "edition": EDITION,
        "status": "declared",
        "owner_context_ref": "or.context.decision_lifecycle",
        "question": question,
        "value_contract": value_contract,
        "allowed_values": allowed_values,
        "binding_phase": phase,
        "authority_ref": "authority.decision_owner_or_method_policy",
        "default_law": "forbidden",
        "default_value": None,
        "constraints": ["The resolved value must be valid for the decision, model and evidence contract."],
        "conflicts": ["Provider defaults cannot override an authored or authority-owned value."],
        "implications": ["Changing this value invalidates affected models, runs, results and evidence."],
        "affects_contracts": ["contract.operations_research.execution"],
        "evidence_required": ["decision authority", "resolved value", "applicability evidence"],
        "change_semantics": ["Recompile affected plans and requalify invalidated provider/target bindings."],
        "gaps": ["Vertical precedence and allowed-value closure remain binding-time obligations."],
    }


DECISIONS = [decision_record(spec) for spec in DECISION_SPECS]


LIBRARY_SPECS = [
    ("decision_problem_semantics", "semantic_pure", "or.context.decision_problem", ["DecisionProblem", "DecisionOwner", "AffectedParty", "DecisionHorizon", "AlternativeAction"], ["ValidateDecisionProblem", "ResolveDecisionScope"], ["decision_horizon"], ["src.informs.faq", "src.informs.methodologies"]),
    ("objective_preference_algebra", "semantic_pure", "or.context.objective_preference", ["ObjectiveExpression", "Goal", "PreferenceOrder", "LexicographicPriority", "ParetoPolicy"], ["ValidateObjective", "CompareOutcomes", "ComposePreferences"], ["objective_precedence"], ["src.informs.methodologies", "src.cvxpy.dcp"]),
    ("constraint_policy_algebra", "semantic_pure", "or.context.constraint_policy", ["ConstraintExpression", "HardConstraint", "SoftConstraint", "ChanceConstraint", "RelaxationAuthority"], ["ValidateConstraint", "ClassifyConstraint", "AuthorizeRelaxation"], ["constraint_hardness"], ["src.cvxpy.dcp", "src.google.mathopt_rest"]),
    ("optimization_model_ir", "semantic_pure", "or.context.model_ir", ["OptimizationModelIr", "VariableDomain", "Parameter", "ExpressionGraph", "ObjectiveSet", "ConstraintSet", "ModelFeatureSet"], ["TypecheckModel", "CanonicalizeModel", "ComputeModelDigest"], ["variable_domain", "uncertainty_representation", "optimization_model_class"], ["src.google.mathopt", "src.jump.moi_solutions", "src.cvxpy.dcp"]),
    ("solver_capability_contract", "semantic_pure", "or.context.solver_capability", ["SolverRequirement", "SolverOffer", "SupportedFeature", "TargetProfile", "CapabilityMismatch"], ["MatchSolverOffer", "ExplainCapabilityMismatch"], ["solver_requirement", "numeric_tolerance", "certificate_requirement"], ["src.google.mathopt_rest", "src.cvxpy.solvers", "src.jump.moi_solutions"]),
    ("optimization_solve_execution", "runtime_mechanism", "or.context.solve_execution", ["BoundOptimizationRun", "SolveCommand", "ProgressOccurrence", "CancellationRequest", "SolveExecutionReceipt"], ["ExecuteSolve", "ObserveProgress", "CancelSolve"], ["solver_requirement", "numeric_tolerance", "solve_budget"], ["src.google.mathopt_rest", "src.gurobi.status", "src.jump.moi_solutions"]),
    ("optimization_result_algebra", "semantic_pure", "or.context.exact_proof", ["OptimizationResult", "TerminationReason", "PrimalStatus", "DualStatus", "Incumbent", "Bound", "Gap", "Ray", "Certificate"], ["InterpretSolveResult", "CompareQualifiedResults", "RefuseStrengthening"], ["numeric_tolerance", "certificate_requirement"], ["src.google.mathopt_rest", "src.jump.moi_solutions", "src.gurobi.status"]),
    ("optimization_solution_validation", "test_oracle", "or.context.solution_validation", ["ValidationProfile", "FeasibilityVerdict", "ObjectiveRecomputation", "CertificateCheck", "ValidationReceipt"], ["ValidateSolution", "RecomputeObjective", "CheckCertificate"], ["numeric_tolerance", "certificate_requirement"], ["src.miplib", "src.qplib", "src.minlplib"]),
    ("infeasibility_diagnosis", "algorithm_pure", "or.context.infeasibility_diagnosis", ["ConflictSet", "IrreducibleInconsistentSubsystem", "FeasibilityRelaxation", "RepairProposal", "DiagnosisResult"], ["DiagnoseInfeasibility", "ComputeConflict", "ProposeFeasibilityRelaxation"], ["constraint_hardness", "numeric_tolerance", "certificate_requirement"], ["src.gurobi.infeasibility", "src.ibm.conflict"]),
    ("heuristic_search_contract", "algorithm_pure", "or.context.heuristic_definition", ["SolutionEncoding", "MoveOperator", "RepairPolicy", "AcceptancePolicy", "DiversificationPolicy", "HeuristicRunResult"], ["ConstructSolution", "SearchNeighborhood", "RepairCandidate", "ReplayHeuristic"], ["heuristic_quality", "solve_budget"], ["src.pyvrp", "src.minizinc.challenge", "src.informs.methodologies"]),
    ("queue_model_semantics", "semantic_pure", "or.context.queueing_system", ["QueueModel", "CustomerClass", "ArrivalProcess", "ServiceProcess", "ServiceStation", "Buffer", "RoutingMatrix", "QueueDiscipline", "QueueInitialState"], ["TypecheckQueueModel", "ResolveQueueState", "ClassifyQueueRegime"], ["queue_arrival_process", "queue_service_process", "queue_structure_discipline", "queue_initialization_observation"], ["src.kendall.1953", "src.jackson.1957"]),
    ("queue_performance_methods", "algorithm_pure", "or.context.queueing_system", ["QueuePerformanceEstimand", "WaitingTimeResult", "QueueLengthResult", "UtilizationResult", "ThroughputResult", "LossAbandonmentResult"], ["EstimateQueuePerformance", "ApplyLittleLaw", "RefuseSteadyStateClaim"], ["queue_performance_estimand", "queue_stability", "queue_initialization_observation"], ["src.little.1961", "src.kendall.1953"]),
    ("queue_network_methods", "algorithm_pure", "or.context.queueing_system", ["QueueNetwork", "RoutingFlow", "VisitRatio", "StationDemand", "NetworkPerformanceResult", "ResidualAssumption"], ["AnalyzeQueueNetwork", "PropagateClassFlows", "ReportNetworkResiduals"], ["queue_arrival_process", "queue_service_process", "queue_structure_discipline", "queue_stability"], ["src.jackson.1957", "src.little.1961"]),
    ("queue_inference_calibration", "algorithm_pure", "or.context.queueing_system", ["ArrivalObservation", "ServiceObservation", "CensoredWait", "QueueParameterEstimate", "GoodnessOfFitResult", "CalibrationReceipt"], ["EstimateArrivalProcess", "EstimateServiceProcess", "CalibrateQueueModel", "AssessQueueFit"], ["queue_arrival_process", "queue_service_process", "queue_initialization_observation", "queue_performance_estimand"], ["src.kendall.1953", "src.informs.methodologies"]),
    ("queue_model_validation", "test_oracle", "or.context.solution_validation", ["QueueValidationProfile", "FlowConservationVerdict", "LittleLawResidual", "StabilityVerdict", "QueueValidationReceipt"], ["ValidateQueueModel", "CheckFlowConservation", "CheckLittleLaw", "CheckStabilityClaim"], ["queue_structure_discipline", "queue_performance_estimand", "queue_stability"], ["src.little.1961", "src.jackson.1957", "src.kendall.1953"]),
    ("simulation_model_semantics", "semantic_pure", "or.context.simulation_model", ["SimulationModel", "SimulatedEntity", "SimulatedState", "Event", "StockFlow", "InteractionRule", "SimulationClock"], ["TypecheckSimulationModel", "ResolveSimulationClock", "ComposeSimulationParadigms"], ["simulation_paradigm", "simulation_clock"], ["src.anylogic", "src.wsc"]),
    ("simulation_experiment_design", "semantic_pure", "or.context.simulation_experiment", ["SimulationExperiment", "Scenario", "InitialState", "WarmupPolicy", "ReplicationPlan", "OutputEstimand"], ["DesignSimulationExperiment", "ValidateReplicationPlan", "SealSimulationExperiment"], ["simulation_initialization", "simulation_replication", "simulation_output"], ["src.wsc", "src.informs.methodologies"]),
    ("simulation_random_stream_control", "policy_pure", "or.context.randomness_reproducibility", ["RandomStreamFamily", "SeedSet", "SubstreamPlan", "CommonRandomNumberPlan", "RandomnessReceipt"], ["AllocateRandomStreams", "ReplayRandomStreams", "CompareCoupledRuns"], ["simulation_random_stream", "simulation_replication"], ["src.wsc", "src.google.ortools"]),
    ("simulation_execution", "runtime_mechanism", "or.context.solve_execution", ["BoundSimulationRun", "SimulationStep", "SimulationProgress", "CancellationRequest", "SimulationRunReceipt"], ["ExecuteSimulation", "AdvanceSimulation", "ObserveSimulation", "CancelSimulation"], ["simulation_clock", "simulation_initialization", "solve_budget"], ["src.anylogic", "src.simio", "src.wsc"]),
    ("simulation_output_analysis", "algorithm_pure", "or.context.simulation_experiment", ["SimulationObservation", "ReplicationResult", "TransientDeletion", "OutputEstimate", "ComparisonResult"], ["AnalyzeSimulationOutput", "EstimateSimulationUncertainty", "CompareScenarios"], ["simulation_replication", "simulation_output"], ["src.wsc", "src.informs.methodologies"]),
    ("simulation_verification_validation", "test_oracle", "or.context.solution_validation", ["ConceptualModelCheck", "CodeVerification", "CalibrationEvidence", "ValidationClaim", "SimulationValidationReceipt"], ["VerifySimulation", "ValidateSimulation", "RefuseRealityClaim"], ["simulation_validation"], ["src.wsc", "src.anylogic"]),
]


def library_record(spec: tuple) -> dict:
    slug, kind, owner, public_types, public_traits, decision_slugs, evidence_refs = spec
    pure = kind in {"semantic_pure", "algorithm_pure", "policy_pure", "test_oracle"}
    return {
        "library_id": f"library.operations_research.{slug}",
        "edition": EDITION,
        "status": "specified",
        "library_kind": kind,
        "semantic_owner_refs": [owner],
        "contributes_to_context_refs": [owner],
        "effect_boundary": "pure_no_io" if pure else "effectful_runtime",
        "public_types": public_types,
        "public_traits": public_traits,
        "operation_refs": [f"operation.operations_research.{slug}.{trait.lower()}" for trait in public_traits],
        "error_contracts": ["InvalidInput", "UnsupportedCapability", "Infeasible", "Unbounded", "Unknown", "NumericalFailure", "ResourceExhausted", "Cancelled", "ProviderFailure"],
        "decision_refs": [f"decision.operations_research.{item}" for item in decision_slugs],
        "requirement_refs": [f"requirement.operations_research.{slug}"],
        "offer_refs": [],
        "configuration_contracts": ["All semantics, limits, tolerances, seeds and provider configuration are explicit and digest-bound."],
        "effect_intents": [] if pure else ["ExecuteOperationsResearchRun"],
        "runtime_receipts": [] if pure else ["OperationsResearchRunReceipt"],
        "laws": ["Model, method, solver and result are distinct.", "No result claim is stronger than its termination and validation evidence.", "Unknown or unsupported semantics produce a typed refusal."],
        "oracles": ["exact small fixtures", "negative/adversarial twins", "cross-provider differential", "resource/cancellation checks"],
        "resource_contracts": ["All work, time, memory, threads, external cost and result limits are finite or refused."],
        "concurrency": ["Parallel search/simulation and schedule-dependent reproducibility are declared by the offer."],
        "cancellation": ["Long-running execution has explicit safe points and typed partial-result validity."],
        "unsafe_ffi_generated_policy": ["Pure libraries contain no unsafe/FFI; runtime/provider boundaries isolate and qualify it."],
        "dependencies": [],
        "targets": ["provider_neutral_contract"],
        "compatibility": ["Semantic, model, artifact, provider and ABI compatibility are checked separately."],
        "removal_seams": ["Provider/target implementations bind behind requirements and can be removed without changing owned semantics."],
        "forbidden_responsibilities": ["industry ontology ownership", "UI", "ambient defaults", "vendor-name dispatch", "business authorization", "LLM/generative dependency"],
        "evidence_refs": evidence_refs,
        "gaps": ["No implementation is qualified and two unrelated vertical acceptance receipts remain open."],
    }


LIBRARIES = [library_record(spec) for spec in LIBRARY_SPECS]


def capability_kind(kind: str) -> str:
    if kind == "semantic_pure":
        return "semantic_contract"
    if kind in {"algorithm_pure", "policy_pure"}:
        return "analytical_practice"
    if kind == "test_oracle":
        return "evidence"
    return "runtime_mechanism"


REQUIREMENTS = [
    {
        "record_kind": "capability_requirement",
        "requirement_id": f"requirement.operations_research.{row['library_id'].split('.')[-1]}",
        "edition": EDITION,
        "status": "declared",
        "subject_ref": row["library_id"],
        "capability_kind": capability_kind(row["library_kind"]),
        "contract_refs": [f"contract.operations_research.{row['library_id'].split('.')[-1]}"],
        "operation_refs": row["operation_refs"],
        "type_refs": ["type.operations_research.contract"],
        "required_guarantees": row["laws"],
        "applicability": {"when": ["The resolved decision or simulation plan requires this contribution."], "unless": [], "scope_refs": [row["library_id"]]},
        "cardinality": "exactly_one",
        "binding_phase": "semantic_closure" if row["library_kind"] == "semantic_pure" else ("evidence_verification" if row["library_kind"] == "test_oracle" else "physical_binding"),
        "criticality": "blocking",
        "selection_laws": ["Select by exact contract, model features, guarantees, target, limits and qualification evidence; never by provider name."],
        "fallback_law": "refuse",
        "prohibited_traits": ["hidden tolerances", "unbounded resources", "success boolean result collapse", "unqualified provider", "LLM/generative dependency"],
        "evidence_gates": ["semantic law tests", "model/result conformance", "target execution receipt", "version/configuration identity"],
        "owner_ref": row["contributes_to_context_refs"][0],
        "gaps": ["No provider is selected or qualified by this candidate corpus."],
    }
    for row in LIBRARIES
]


PROVIDER_SPECS = [
    ("ortools", "OR-Tools", ["solver_capability_contract", "optimization_solve_execution", "optimization_result_algebra"], ["src.google.ortools", "src.google.mathopt", "src.google.mathopt_rest"]),
    ("highs", "HiGHS", ["solver_capability_contract", "optimization_solve_execution", "optimization_result_algebra"], ["src.highs.home"]),
    ("scip", "SCIP", ["solver_capability_contract", "optimization_solve_execution", "optimization_result_algebra", "heuristic_search_contract"], ["src.scip.home", "src.scip.v9"]),
    ("gurobi", "Gurobi", ["solver_capability_contract", "optimization_solve_execution", "optimization_result_algebra", "infeasibility_diagnosis"], ["src.gurobi.status", "src.gurobi.infeasibility", "src.gurobi.releases"]),
    ("anylogic", "AnyLogic", ["simulation_model_semantics", "simulation_experiment_design", "simulation_execution", "simulation_output_analysis"], ["src.anylogic"]),
    ("simio", "Simio", ["simulation_model_semantics", "simulation_experiment_design", "simulation_execution", "simulation_output_analysis"], ["src.simio"]),
]


def provider_offer(spec: tuple) -> dict:
    slug, name, library_slugs, evidence_refs = spec
    return {
        "record_kind": "capability_offer",
        "offer_id": f"offer.operations_research.{slug}",
        "edition": EDITION,
        "status": "declared",
        "offer_kind": "provider_project_facade",
        "binding_eligible": False,
        "provider_ref": f"provider.operations_research.{slug}",
        "capability_kind": "runtime_mechanism",
        "contract_refs": [f"contract.operations_research.{item}" for item in library_slugs],
        "operation_refs": [f"operation.operations_research.provider.{slug}.execute"],
        "type_refs": ["type.operations_research.contract"],
        "guarantees": [f"Official material documents named {name} interfaces; no conformance, performance or outcome qualification is implied."],
        "limits": ["Exact version, model features, tolerances, target, configuration, status mapping, resource behavior and license require qualification."],
        "decision_refs": ["decision.operations_research.solver_requirement", "decision.operations_research.numeric_tolerance", "decision.operations_research.solve_budget"],
        "target_refs": ["target.operations_research.external_runtime"],
        "applicability": {"when": ["Every required contract and target behavior is independently qualified."], "unless": ["Any semantic, model, evidence, resource or policy gate fails."], "scope_refs": [f"provider.operations_research.{slug}"]},
        "exclusions": ["Provider name is not a semantic owner.", "No undocumented guarantee is offered.", "No LLM/generative capability is part of the core claim."],
        "conformance_receipts": [],
        "evidence_refs": evidence_refs,
        "validity": {"from": ACCESSED, "until": None, "recheck_triggers": ["provider release", "target/configuration change", "qualification expiry", "security or license change"]},
        "gaps": ["No executed SAN conformance receipt exists in this edition."],
    }


EXECUTION_RUN = "run-20260826-macos-arm64-python3_14-001"
EXECUTION_ROOT = (
    "research/domain_atlas/compiler/conformance_evaluation/executions/"
    f"lp_solver_exact_scope/runs/{EXECUTION_RUN}"
)
CPSAT_FAILED_RUN = "run-20260826-cpsat-macos-arm64-python3_14-001"
CPSAT_CORRECTED_RUN = "run-20260826-cpsat-macos-arm64-python3_14-002"
CPSAT_EXECUTION_ROOT = "research/domain_atlas/compiler/conformance_evaluation/executions/cp_sat_exact_scope/runs"


EXACT_PROVIDER_OFFERS = [
    {
        "record_kind": "capability_offer",
        "offer_id": "offer.operations_research.ortools.glop.mpsolver_python.9_15_6755",
        "edition": EDITION,
        "status": "executed_not_appraised_not_qualified",
        "offer_kind": "exact_adapter_artifact_offer",
        "binding_eligible": False,
        "provider_ref": "provider.operations_research.ortools.glop.mpsolver_python",
        "capability_kind": "runtime_mechanism",
        "contract_refs": ["contract.operations_research.lp.safe_status_and_objective.v1"],
        "partial_library_contract_refs": [
            "contract.operations_research.solver_capability_contract",
            "contract.operations_research.optimization_solve_execution",
            "contract.operations_research.optimization_result_algebra",
        ],
        "operation_refs": [
            "operation.operations_research.lp.execute_continuous_lp",
            "operation.operations_research.lp.interpret_glop_mpsolver_status_without_strengthening",
        ],
        "type_refs": ["type.operations_research.lp_exact_scope_contract"],
        "guarantees": [
            "The retained run passed six fixtures for the safe status/objective profile on one exact target occurrence.",
            "MPSolver INFEASIBLE is weakened to infeasible_or_unbounded for this GLOP adapter."
        ],
        "limits": [
            "Precise infeasible-versus-unbounded classification failed the retained protocol.",
            "Cancellation, progress, certificates, performance, security, license and vertical acceptance were not tested."
        ],
        "decision_refs": [
            "decision.operations_research.solver_requirement",
            "decision.operations_research.numeric_tolerance",
            "decision.operations_research.solve_budget",
        ],
        "target_refs": ["target.local.darwin.arm64.python-3.14.7.isolated-process"],
        "applicability": {
            "when": ["The exact safe continuous-LP contract is required and every remaining gate passes."],
            "unless": ["Precise terminal classification, in-process cohabitation or any untested guarantee is required."],
            "scope_refs": ["protocol.conformance.lp_solver_exact_scope.v1"],
        },
        "exclusions": [
            "OR-Tools project/suite identity is not this offer.",
            "The offer does not claim the full solve-execution or result-algebra contracts.",
            "No LLM/generative capability is part of the claim."
        ],
        "conformance_receipts": [],
        "executed_test_receipt_refs": [
            f"{EXECUTION_ROOT}/qualification-receipts.jsonl#receipt.{EXECUTION_RUN}.ortools_glop_mpsolver.safe_status_and_objective",
            f"{EXECUTION_ROOT}/qualification-receipts.jsonl#receipt.{EXECUTION_RUN}.ortools_glop_mpsolver.precise_terminal_classification",
        ],
        "passed_contract_refs": ["contract.operations_research.lp.safe_status_and_objective.v1"],
        "failed_contract_refs": ["contract.operations_research.lp.precise_terminal_classification.v1"],
        "evidence_refs": [
            "src.google.ortools.v9_15",
            "src.google.glop_mpsolver_status.v9_15",
        ],
        "validity": {
            "from": ACCESSED,
            "until": "2026-09-25",
            "recheck_triggers": [
                "artifact/dependency/adapter/target change",
                "protocol or oracle change",
                "security or license change",
            ],
        },
        "gaps": [
            "No independent appraisal or qualified deployed occurrence exists.",
            "Same-process cohabitation with the retained highspy offer failed on the observed target."
        ],
    },
    {
        "record_kind": "capability_offer",
        "offer_id": "offer.operations_research.highspy.highs.1_15_1",
        "edition": EDITION,
        "status": "executed_not_appraised_not_qualified",
        "offer_kind": "exact_adapter_artifact_offer",
        "binding_eligible": False,
        "provider_ref": "provider.operations_research.highspy.highs",
        "capability_kind": "runtime_mechanism",
        "contract_refs": [
            "contract.operations_research.lp.safe_status_and_objective.v1",
            "contract.operations_research.lp.precise_terminal_classification.v1",
        ],
        "partial_library_contract_refs": [
            "contract.operations_research.solver_capability_contract",
            "contract.operations_research.optimization_solve_execution",
            "contract.operations_research.optimization_result_algebra",
        ],
        "operation_refs": [
            "operation.operations_research.lp.execute_continuous_lp",
            "operation.operations_research.lp.interpret_highs_model_status",
        ],
        "type_refs": ["type.operations_research.lp_exact_scope_contract"],
        "guarantees": [
            "The retained run passed six fixtures for both safe status/objective and precise terminal-classification profiles on one exact target occurrence."
        ],
        "limits": [
            "Cancellation, progress, certificates, performance, security, license and vertical acceptance were not tested."
        ],
        "decision_refs": [
            "decision.operations_research.solver_requirement",
            "decision.operations_research.numeric_tolerance",
            "decision.operations_research.solve_budget",
        ],
        "target_refs": ["target.local.darwin.arm64.python-3.14.7.isolated-process"],
        "applicability": {
            "when": ["The exact retained continuous-LP scope is required and every remaining gate passes."],
            "unless": ["Any untested guarantee or in-process cohabitation with the retained OR-Tools wheel is required."],
            "scope_refs": ["protocol.conformance.lp_solver_exact_scope.v1"],
        },
        "exclusions": [
            "HiGHS project identity is not this exact highspy artifact offer.",
            "The offer does not claim the full solve-execution or result-algebra contracts.",
            "No LLM/generative capability is part of the claim."
        ],
        "conformance_receipts": [],
        "executed_test_receipt_refs": [
            f"{EXECUTION_ROOT}/qualification-receipts.jsonl#receipt.{EXECUTION_RUN}.highspy_highs.safe_status_and_objective",
            f"{EXECUTION_ROOT}/qualification-receipts.jsonl#receipt.{EXECUTION_RUN}.highspy_highs.precise_terminal_classification",
        ],
        "passed_contract_refs": [
            "contract.operations_research.lp.safe_status_and_objective.v1",
            "contract.operations_research.lp.precise_terminal_classification.v1",
        ],
        "failed_contract_refs": [],
        "evidence_refs": ["src.highs.v1_15_1", "src.highs.python"],
        "validity": {
            "from": ACCESSED,
            "until": "2026-09-25",
            "recheck_triggers": [
                "artifact/dependency/adapter/target change",
                "protocol or oracle change",
                "security or license change",
            ],
        },
        "gaps": [
            "No independent appraisal or qualified deployed occurrence exists.",
            "Same-process cohabitation with the retained OR-Tools offer failed on the observed target."
        ],
    },
    {
        "record_kind": "capability_offer",
        "offer_id": "offer.operations_research.ortools.cp_sat.python.9_15_6755",
        "edition": EDITION,
        "status": "executed_not_appraised_not_qualified",
        "offer_kind": "exact_adapter_artifact_offer",
        "binding_eligible": False,
        "provider_ref": "provider.operations_research.ortools.cp_sat.python",
        "capability_kind": "runtime_mechanism",
        "contract_refs": [
            "contract.operations_research.cp_sat.core.v1",
            "contract.operations_research.cp_sat.global_constraints.v1",
            "contract.operations_research.cp_sat.fixed_interval_scheduling.v1",
            "contract.operations_research.cp_sat.complete_enumeration.v1",
            "contract.operations_research.cp_sat.unknown_limit_no_strengthening.v1",
        ],
        "partial_library_contract_refs": [
            "contract.operations_research.solver_capability_contract",
            "contract.operations_research.optimization_solve_execution",
            "contract.operations_research.optimization_result_algebra",
            "contract.operations_research.optimization_solution_validation",
        ],
        "operation_refs": [
            "operation.operations_research.cp_sat.execute_closed_integer_model",
            "operation.operations_research.cp_sat.enumerate_all_solutions_when_declared",
            "operation.operations_research.cp_sat.validate_solution_and_status_without_strengthening",
        ],
        "type_refs": ["type.operations_research.cp_sat_exact_scope_contract"],
        "guarantees": [
            "The corrected retained run passed core, global-constraint, fixed-interval scheduling, complete-enumeration and UNKNOWN-preservation profiles on one exact target occurrence.",
            "Canonical fractional/inverted-domain inputs are refused before provider invocation and provider-invalid aggregate magnitudes remain MODEL_INVALID.",
        ],
        "limits": [
            "The first retained adapter configuration failed complete enumeration because callback observation did not propagate exhaustive-enumeration intent.",
            "Arbitrary CP/MIP/SAT features, portability, performance, security, license, production and vertical acceptance were not tested.",
        ],
        "decision_refs": [
            "decision.operations_research.solver_requirement",
            "decision.operations_research.numeric_tolerance",
            "decision.operations_research.solve_budget",
        ],
        "target_refs": ["target.local.darwin.arm64.python-3.14.7.isolated-process"],
        "applicability": {
            "when": ["The closed bounded-integer CP-SAT fragment and exact tested configuration are required and every remaining gate passes."],
            "unless": ["An omitted feature, different model class, untested guarantee, independent qualification or vertical authority is required."],
            "scope_refs": ["protocol.conformance.cp_sat_exact_scope.v1"],
        },
        "exclusions": [
            "OR-Tools project/suite identity is not this exact CP-SAT interface offer.",
            "A callback is not complete-enumeration intent or proof.",
            "The offer does not claim full generic optimization-library contracts.",
            "No LLM/generative capability is part of the claim.",
        ],
        "conformance_receipts": [],
        "executed_test_receipt_refs": [
            f"{CPSAT_EXECUTION_ROOT}/{CPSAT_FAILED_RUN}/qualification-receipts.jsonl#receipt.{CPSAT_FAILED_RUN}.ortools_cp_sat_python.enumeration",
            f"{CPSAT_EXECUTION_ROOT}/{CPSAT_CORRECTED_RUN}/qualification-receipts.jsonl#receipt.{CPSAT_CORRECTED_RUN}.ortools_cp_sat_python.core",
            f"{CPSAT_EXECUTION_ROOT}/{CPSAT_CORRECTED_RUN}/qualification-receipts.jsonl#receipt.{CPSAT_CORRECTED_RUN}.ortools_cp_sat_python.global_constraints",
            f"{CPSAT_EXECUTION_ROOT}/{CPSAT_CORRECTED_RUN}/qualification-receipts.jsonl#receipt.{CPSAT_CORRECTED_RUN}.ortools_cp_sat_python.scheduling",
            f"{CPSAT_EXECUTION_ROOT}/{CPSAT_CORRECTED_RUN}/qualification-receipts.jsonl#receipt.{CPSAT_CORRECTED_RUN}.ortools_cp_sat_python.enumeration",
            f"{CPSAT_EXECUTION_ROOT}/{CPSAT_CORRECTED_RUN}/qualification-receipts.jsonl#receipt.{CPSAT_CORRECTED_RUN}.ortools_cp_sat_python.limit_no_strengthening",
        ],
        "passed_contract_refs": [
            "contract.operations_research.cp_sat.core.v1",
            "contract.operations_research.cp_sat.global_constraints.v1",
            "contract.operations_research.cp_sat.fixed_interval_scheduling.v1",
            "contract.operations_research.cp_sat.complete_enumeration.v1",
            "contract.operations_research.cp_sat.unknown_limit_no_strengthening.v1",
        ],
        "failed_contract_refs": ["contract.operations_research.cp_sat.pre_parameter_complete_enumeration.v1"],
        "evidence_refs": [
            "src.google.ortools.v9_15", "src.google.cp_sat", "src.google.cp_model_proto.v9_15", "src.google.sat_parameters.v9_15",
        ],
        "validity": {
            "from": ACCESSED,
            "until": "2026-09-25",
            "recheck_triggers": [
                "artifact/dependency/adapter/target change",
                "model class, parameter, protocol or oracle change",
                "security or license change",
            ],
        },
        "gaps": [
            "No independent appraisal, portable qualification or deployed production occurrence exists.",
            "No manufacturing formulation or schedule publication/dispatch acceptance is implied.",
        ],
    },
]


OFFERS = [provider_offer(spec) for spec in PROVIDER_SPECS] + EXACT_PROVIDER_OFFERS
COMPILER_RECORDS = REQUIREMENTS + OFFERS


QUALIFICATION_SPECS = [
    ("decision_problem_semantics", "decision_problem_semantics", "Decision framing preserves owner, affected parties, alternatives, horizon, authority and scope.", ["single and multi-owner cases", "missing affected party", "horizon boundary", "unauthorized action"], ["scope/identity oracle", "authority refusal", "round-trip digest"]),
    ("objective_preference_algebra", "objective_preference_algebra", "Objective comparison preserves units, priority, direction, lexicographic and Pareto semantics.", ["single/multiobjective models", "unit mismatch", "lexicographic tie", "Pareto-incomparable outcomes"], ["algebraic ordering laws", "unit/type oracle", "reference comparison"]),
    ("constraint_policy_algebra", "constraint_policy_algebra", "Constraint handling preserves hardness, relaxation authority, chance semantics and penalty identity.", ["hard/soft twins", "unauthorized relaxation", "chance boundary", "inconsistent constraints"], ["satisfaction oracle", "authority oracle", "penalty/relaxation trace"]),
    ("optimization_model_ir", "optimization_model_ir", "Model IR preserves variable domains, expressions, objective, constraints, units, uncertainty and feature identity.", ["LP/QP/MIP/conic/CP fixtures", "domain mismatch", "lossy reformulation", "unsupported feature"], ["typechecking", "canonical digest", "round-trip/differential lowering"]),
    ("solver_capability_contract", "solver_capability_contract", "Capability matching refuses unsupported model, callback, certificate, numeric, target and budget requirements.", ["feature matrix", "unsupported callback", "certificate-required case", "target/license mismatch"], ["requirement-offer solver", "mismatch explanation", "negative capability twin"]),
    ("optimization_solve_execution", "optimization_solve_execution", "Solve execution preserves model/data/configuration identity, limits, cancellation, progress and partial-result truth.", ["optimal/infeasible/unbounded models", "time/node limit", "cancel with incumbent", "provider error"], ["run digest", "resource/cancellation receipt", "status trace"]),
    ("optimization_result_algebra", "optimization_result_algebra", "Result mapping never strengthens termination, feasibility, bound, gap, ray or certificate evidence.", ["all termination/result states", "limit with and without incumbent", "missing bound", "numeric failure"], ["typed status oracle", "bound/gap consistency", "no-strengthening law"]),
    ("optimization_solution_validation", "optimization_solution_validation", "Independent validation recomputes feasibility/objective and checks required proof evidence at declared tolerances.", ["MIPLIB/QPLIB/MINLPLib fixtures", "near-tolerance violations", "wrong objective", "invalid certificate"], ["independent checker", "objective residual", "mutation score"]),
    ("infeasibility_diagnosis", "infeasibility_diagnosis", "Infeasibility diagnosis preserves constraint identity, tolerances, conflict minimality posture and relaxation authority without deleting rules automatically.", ["known contradictory models", "redundant conflict", "near-tolerance feasibility", "unauthorized relaxation"], ["conflict/IIS reference", "feasibility recheck", "relaxation authority refusal"]),
    ("heuristic_search_contract", "heuristic_search_contract", "Heuristic execution preserves encoding, moves, repair, acceptance, randomness, stopping and empirical-quality limits without claiming optimality.", ["known routing/search fixtures", "invalid move", "repair failure", "seed replay"], ["feasibility checker", "trace replay", "benchmark quality distribution"]),
    ("queue_model_semantics", "queue_model_semantics", "Queue-model semantics preserve customer classes, arrivals, services, stations, buffers, routing, discipline, initial state and observation cuts.", ["M/M/1 and finite-buffer fixtures", "batch arrivals", "priority/preemption twin", "balking/reneging case"], ["model typechecker", "state-transition oracle", "discipline/routing negative twin"]),
    ("queue_performance_methods", "queue_performance_methods", "Queue performance estimates preserve the declared estimand, regime, observation cut, uncertainty and steady-state limits.", ["analytic M/M/1 fixtures", "unstable traffic", "finite observation window", "censored waits"], ["analytic reference", "Little-law residual", "steady-state refusal oracle"]),
    ("queue_network_methods", "queue_network_methods", "Queue-network analysis preserves classes, routing, station demand, flow conservation and the exact assumptions behind product-form or approximate results.", ["open Jackson network", "routing leak", "class-dependent service", "non-product-form residual"], ["flow-conservation oracle", "analytic network reference", "assumption residual report"]),
    ("queue_inference_calibration", "queue_inference_calibration", "Queue calibration separates observed arrivals, service, censoring and state from fitted process assumptions and reports lack of fit.", ["known arrival/service distributions", "time-varying arrivals", "right-censored waits", "nonstationary service"], ["parameter recovery", "goodness-of-fit", "information-cut leakage twin"]),
    ("queue_model_validation", "queue_model_validation", "Independent validation checks flow conservation, Little's law applicability/residuals, stability claims and reference fixtures without treating agreement as reality proof.", ["valid and invalid analytic queues", "flow imbalance", "unstable network", "mis-specified observation cut"], ["conservation checker", "Little-law applicability oracle", "stability/refusal oracle"]),
    ("simulation_model_semantics", "simulation_model_semantics", "Simulation model preserves paradigm, entities/state, time, event ordering, equations/interactions and composition semantics.", ["DES, SD, ABM and continuous fixtures", "simultaneous events", "unit/time mismatch", "invalid multimethod coupling"], ["model typechecker", "clock/event oracle", "composition law"]),
    ("simulation_experiment_design", "simulation_experiment_design", "Simulation experiment preserves scenarios, initial state, warm-up, replications, output estimands and prospective edition.", ["transient and steady-state cases", "insufficient replications", "post-run design mutation", "paired scenarios"], ["design identity", "replication oracle", "prospective-mutation refusal"]),
    ("simulation_random_stream_control", "simulation_random_stream_control", "Random-stream control preserves family, seed, substream independence, common-random-number coupling and replay.", ["independent/paired streams", "substream overlap", "parallel schedule twin", "seed replay"], ["stream identity", "distribution/correlation test", "replay oracle"]),
    ("simulation_execution", "simulation_execution", "Simulation execution preserves model/experiment/configuration identity, clock, limits, cancellation and partial-run validity.", ["finite-event run", "continuous integration", "event explosion", "cancelled run"], ["run digest", "time/order oracle", "resource/cancellation receipt"]),
    ("simulation_output_analysis", "simulation_output_analysis", "Output analysis preserves replication dependence, transient deletion, estimand, uncertainty and comparison semantics.", ["known stochastic process", "correlated replications", "warm-up twin", "rare-event output"], ["analytic reference", "coverage test", "paired/unpaired comparison oracle"]),
    ("simulation_verification_validation", "simulation_verification_validation", "Verification and validation distinguish code/model correctness from evidence that the model is fit for a declared use.", ["code defect mutants", "miscalibrated model", "out-of-scope use", "face-valid but predictive-invalid twin"], ["mutation/verification oracle", "calibration residual", "claim-scope refusal"]),
]


QUALIFICATION_PROFILES = [
    {
        "receipt_id": f"receipt.operations_research.{slug}",
        "edition": EDITION,
        "record_kind": "qualification_profile",
        "status": "template_not_executed",
        "subject_ref": f"library.operations_research.{library_slug}",
        "claim": claim,
        "scope": ["exact provider version", "exact build/features", "exact target", "exact model/configuration and operation set"],
        "environment": {},
        "configuration": {},
        "fixtures": fixtures,
        "oracles": oracles,
        "results": [],
        "limitations": ["This is an unexecuted qualification profile and proves no provider capability.", "Passing one profile proves only its exact claim and scope."],
        "evidence_refs": [],
        "validity": {"from": None, "until": None},
        "invalidation_triggers": ["provider version/build change", "target change", "configuration change", "fixture/oracle edition change", "dependency, security or license change"],
    }
    for slug, library_slug, claim, fixtures, oracles in QUALIFICATION_SPECS
]

GAP_CLASSES = {
    "coverage": (["semantic_object", "semantic_role"], ["reviewed OR taxonomy", "cross-industry counterexamples"]),
    "authority": (["authority_and_trust", "effect_boundary"], ["named semantic-owner decision", "decision-authority provenance"]),
    "evidence": (["partiality_and_uncertainty", "proof_and_conformance"], ["claim-to-primary-source appraisal", "theorem preconditions and counterexamples"]),
    "implementation": (["representation_and_interchange", "resource_and_operational_bounds"], ["exact implementation receipt", "executable law results"]),
    "qualification": (["proof_and_conformance"], ["two independent implementation differentials", "two unrelated vertical acceptance receipts"]),
}
GAPS = [
    {"gap_id": f"gap.operations-research.{kind}.v1", "gap_class": kind, "semantic_axes": axes, "scope_refs": [row["library_id"] for row in LIBRARIES], "closure_evidence": evidence, "blocked_outputs": ["canonical source authority", "selectable compiler offer", "completion claim"], "status": "OPEN"}
    for kind, (axes, evidence) in GAP_CLASSES.items()
]
GAP_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "https://san.example/spec/operations-research-gap-v1.schema.json",
    "type": "object", "additionalProperties": False,
    "required": ["gap_id", "gap_class", "semantic_axes", "scope_refs", "closure_evidence", "blocked_outputs", "status"],
    "properties": {"gap_id": {"type": "string", "minLength": 1}, "gap_class": {"enum": sorted(GAP_CLASSES)}, "semantic_axes": {"type": "array", "minItems": 1, "items": {"type": "string"}}, "scope_refs": {"type": "array", "minItems": 1, "items": {"type": "string"}}, "closure_evidence": {"type": "array", "minItems": 1, "items": {"type": "string"}}, "blocked_outputs": {"type": "array", "minItems": 1, "items": {"type": "string"}}, "status": {"const": "OPEN"}},
}


if __name__ == "__main__":
    write_jsonl("sources.jsonl", SOURCES)
    write_jsonl("methods.jsonl", METHODS)
    write_jsonl("experts.jsonl", EXPERTS)
    write_jsonl("companies.jsonl", COMPANIES)
    write_jsonl("innovations.jsonl", INNOVATIONS)
    write_jsonl("bounded-context-candidates.jsonl", CONTEXTS)
    write_jsonl("decision-points.jsonl", DECISIONS)
    write_jsonl("library-boundaries.jsonl", LIBRARIES)
    write_jsonl("compiler-requirements-offers.jsonl", COMPILER_RECORDS)
    write_jsonl("qualification-receipts.jsonl", QUALIFICATION_PROFILES)
    write_jsonl("gaps.jsonl", GAPS)
    (ROOT / "gap.schema.json").write_text(json.dumps(GAP_SCHEMA, indent=2, sort_keys=True) + "\n")
    write_manifest()
    print(json.dumps({
        "sources": len(SOURCES), "methods": len(METHODS), "experts": len(EXPERTS),
        "companies": len(COMPANIES), "innovations": len(INNOVATIONS), "contexts": len(CONTEXTS),
        "decisions": len(DECISIONS), "libraries": len(LIBRARIES), "requirements": len(REQUIREMENTS),
        "offers": len(OFFERS), "qualification_profiles": len(QUALIFICATION_PROFILES),
    }, sort_keys=True))
