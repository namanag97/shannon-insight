#!/usr/bin/env python3
"""Build the deterministic mathematical-model-class adjudication candidate.

This package classifies a closed, typed model declaration before provider matching.
It is intentionally not a solver, an optimizer catalogue, or an agentic classifier.
The same feature set always yields the same facets, refusals, and proof gaps.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
RESEARCH_ROOT = ROOT.parents[2]
EDITION = 1
STATUS = "reviewed_candidate"
ACCESSED_AT = "2026-08-26"


def rec(record_id: str, record_kind: str, **values: object) -> dict:
    return {
        "id": record_id,
        "record_kind": record_kind,
        "edition": EDITION,
        "status": STATUS,
        **values,
    }


def source(
    source_id: str,
    title: str,
    publisher: str,
    source_kind: str,
    url: str,
    year: int,
    topics: list[str],
    authority_scope: str,
) -> dict:
    return rec(
        source_id,
        "source",
        title=title,
        publisher=publisher,
        source_kind=source_kind,
        url=url,
        publication_or_live_year=year,
        accessed_at=ACCESSED_AT,
        supports_topics=topics,
        authority_scope=authority_scope,
        limitations=[
            "This source does not prove that a SAN model occurrence satisfies the documented class.",
            "This source does not qualify a provider, target occurrence, vertical solution, or effect.",
        ],
    )


SOURCES = [
    source(
        "source.mca.moi.standard_form",
        "MathOptInterface standard-form problem",
        "JuMP / MathOptInterface Project",
        "official_documentation",
        "https://jump.dev/MathOptInterface.jl/stable/manual/standard_form/",
        2026,
        ["function_in_set", "affine", "quadratic", "nonlinear", "cones", "integrality"],
        "Authoritative for the documented function-in-set representation and built-in function/set kinds.",
    ),
    source(
        "source.mca.moi.models",
        "MathOptInterface model and optimizer attributes",
        "JuMP / MathOptInterface Project",
        "official_documentation",
        "https://jump.dev/MathOptInterface.jl/stable/manual/models/",
        2026,
        ["objective", "constraints", "termination", "primal_status", "dual_status", "bounds"],
        "Authoritative for the documented MOI model and result interface, not universal provider behavior.",
    ),
    source(
        "source.mca.mosek.cookbook",
        "MOSEK Modeling Cookbook 3.4",
        "MOSEK ApS",
        "official_modeling_reference",
        "https://docs.mosek.com/modeling-cookbook/index.html",
        2025,
        ["linear", "quadratic", "conic", "socp", "sdp", "exponential_cone", "power_cone", "mixed_integer"],
        "Authoritative for the cookbook's mathematical definitions and reformulations; provider-specific claims remain scoped.",
    ),
    source(
        "source.mca.cvxpy.dcp",
        "Disciplined Convex Programming",
        "CVXPY Project",
        "official_documentation",
        "https://www.cvxpy.org/tutorial/dcp/",
        2026,
        ["curvature", "sign", "convexity_certificate", "unknown_curvature"],
        "Authoritative for CVXPY DCP rules, including their sound-but-incomplete classification behavior.",
    ),
    source(
        "source.mca.scip.problem_classes",
        "What types of optimization problems does SCIP solve?",
        "SCIP Optimization Suite",
        "official_documentation",
        "https://scipopt.org/doc/html/WHATPROBLEMS.php",
        2026,
        ["mip", "minlp", "constraint_integer_programming", "problem_class_subsumption"],
        "Authoritative for SCIP's documented problem classes and scope, not for arbitrary provider equivalence.",
    ),
    source(
        "source.mca.ortools.cp",
        "Constraint optimization",
        "Google OR-Tools",
        "official_documentation",
        "https://developers.google.com/optimization/cp",
        2026,
        ["constraint_programming", "feasibility", "scheduling", "cp_sat"],
        "Authoritative for OR-Tools' documented distinction between CP and linear programming.",
    ),
    source(
        "source.mca.ortools.cpsat",
        "CP-SAT Solver",
        "Google OR-Tools",
        "official_documentation",
        "https://developers.google.com/optimization/cp/cp_solver",
        2026,
        ["integer_arithmetic", "cp_sat", "termination_status"],
        "Authoritative for the documented CP-SAT integer-only model interface and status vocabulary.",
    ),
    source(
        "source.mca.ortools.mathopt_result",
        "MathOpt solve result and termination contract",
        "Google OR-Tools",
        "official_api_reference",
        "https://developers.google.com/optimization/service/reference/rest/v1/mathopt/solveMathOptModel",
        2026,
        ["termination_reason", "feasibility", "infeasible_or_unbounded", "objective_bounds", "limits"],
        "Authoritative for the documented MathOpt API result algebra, not for stronger solver-native claims.",
    ),
    source(
        "source.mca.minizinc.handbook",
        "MiniZinc Handbook",
        "MiniZinc Project",
        "official_language_documentation",
        "https://docs.minizinc.dev/en/stable/",
        2026,
        ["constraint_model", "finite_domain", "global_constraint", "solver_independent_model"],
        "Authoritative for the MiniZinc language and documented flattening/interface semantics.",
    ),
    source(
        "source.mca.smtlib.standard",
        "SMT-LIB Standard",
        "SMT-LIB Initiative",
        "standard",
        "https://smt-lib.org/language.shtml",
        2026,
        ["sat", "smt", "theory", "unknown", "model"],
        "Authoritative for the named SMT-LIB language edition and its result vocabulary.",
    ),
    source(
        "source.mca.bertsimas_sim.robust",
        "The Price of Robustness",
        "INFORMS Operations Research",
        "primary_research",
        "https://www.mit.edu/~dbertsim/papers/melvyn/The-Price-Of-Robustness-OR52.pdf",
        2004,
        ["robust_optimization", "uncertainty_set", "protection_budget", "robust_counterpart"],
        "Primary evidence for the paper's robust-linear-optimization formulation and guarantees.",
    ),
    source(
        "source.mca.shapiro.stochastic",
        "Stochastic Programming",
        "Optimization Online",
        "primary_research_survey",
        "https://optimization-online.org/wp-content/uploads/2006/01/1323.pdf",
        2006,
        ["stochastic_programming", "two_stage", "recourse", "scenario"],
        "Primary scholarly evidence for the survey's stochastic-programming definitions and distinctions.",
    ),
    source(
        "source.mca.casadi.optimal_control",
        "CasADi documentation",
        "CasADi Project",
        "official_documentation",
        "https://web.casadi.org/docs/",
        2026,
        ["nonlinear_programming", "ode", "dae", "optimal_control", "discretization"],
        "Authoritative for CasADi's documented expression, NLP, integration, and optimal-control building blocks.",
    ),
    source(
        "source.mca.fmi.3_0_2",
        "Functional Mock-up Interface 3.0.2",
        "Modelica Association Project FMI",
        "standard",
        "https://fmi-standard.org/docs/3.0.2/",
        2024,
        ["model_exchange", "co_simulation", "scheduled_execution", "ode", "dae", "events"],
        "Authoritative for FMI 3.0.2 interface identities and state-machine contracts, not simulation validity.",
    ),
    source(
        "source.mca.anylogic.multimethod",
        "AnyLogic overview",
        "AnyLogic",
        "official_provider_documentation",
        "https://www.anylogic.com/overview/",
        2026,
        ["discrete_event", "agent_based_simulation", "system_dynamics", "multimethod"],
        "Evidence for the provider's documented simulation modalities, not neutral taxonomy completeness or model validity.",
    ),
    source(
        "source.mca.pddl.2_1",
        "PDDL2.1: An Extension to PDDL for Expressing Temporal Planning Domains",
        "Journal of Artificial Intelligence Research",
        "primary_specification",
        "https://www.cs.cmu.edu/afs/cs/project/jair/pub/volume20/fox03a-html/JAIR.html",
        2003,
        ["planning", "actions", "durative_actions", "numeric_fluents"],
        "Primary specification evidence for PDDL 2.1 planning semantics.",
    ),
    source(
        "source.mca.moi.paper",
        "MathOptInterface: a data structure for mathematical optimization problems",
        "INFORMS Journal on Computing",
        "primary_research",
        "https://doi.org/10.1287/ijoc.2021.1067",
        2021,
        ["optimization_ir", "function_set_pair", "bridge", "solver_interface"],
        "Primary evidence for MOI's data-model and bridging design; not a proof of every bridge's equivalence.",
    ),
]


AXIS_SPECS = [
    ("problem_role", "What is requested: satisfaction, optimization, estimation, control, or experiment?", "No solver class follows from a business use-case name."),
    ("variable_domain", "What values may decisions and states take?", "Continuous, integer, binary, finite-domain, symbolic, and mixed domains are not interchangeable."),
    ("expression_structure", "What algebra or relation kinds occur in objectives and constraints?", "Affine, quadratic, conic, nonlinear, logical, differential, and black-box expressions remain distinct."),
    ("geometry_proof", "What curvature, convexity, and regularity facts are actually certified?", "Unknown curvature is not nonconvexity and is not certified convexity."),
    ("uncertainty_information", "What is unknown, how represented, and when revealed?", "Scenarios, probability laws, uncertainty sets, ambiguity sets, and chance constraints are distinct contracts."),
    ("temporal_decision", "Are decisions static, staged, feedback, partially observed, online, or continuous-time?", "A time index alone does not prove a multistage or control formulation."),
    ("execution_semantics", "Is the declared artifact solved, searched, simulated, integrated, checked, or composed?", "Simulation, optimization, constraint solving, theorem satisfiability, and specialized algorithms do not imply each other."),
    ("proof_claim", "What claim may a result make?", "Feasible, locally optimal, globally optimal, bounded-quality, statistically estimated, and unknown are distinct."),
    ("composition_boundary", "Is this one closed formulation or a graph of coupled submodels?", "A hybrid must retain every interface, approximation, synchronization, and authority boundary."),
]

AXES = [
    rec(
        f"axis.mca.{axis_id}",
        "classification_axis",
        name=axis_id.replace("_", " ").title(),
        adjudication_question=question,
        non_collapse_law=law,
    )
    for axis_id, question, law in AXIS_SPECS
]


ATOM_GROUPS: dict[str, list[tuple[str, str]]] = {
    "problem_role": [
        ("role.feasibility", "Find any admissible assignment."),
        ("role.optimization", "Optimize an explicit objective or ordered objective family."),
        ("role.estimation", "Estimate behavior or uncertainty rather than prove an optimum."),
        ("role.control", "Choose a policy or control trajectory over dynamics."),
        ("role.planning", "Choose actions whose transition semantics lead toward goals."),
    ],
    "variable_domain": [
        ("vars.continuous_only", "All decision variables are real-valued over declared bounds."),
        ("vars.any_integer", "At least one decision variable has an integer domain."),
        ("vars.binary", "At least one decision variable is restricted to zero or one."),
        ("vars.finite_discrete", "Variables range over finite enumerated domains."),
        ("vars.symbolic", "Variables include nonnumeric symbolic or theory-sorted values."),
        ("vars.mixed", "More than one materially distinct variable-domain family occurs."),
    ],
    "objective_form": [
        ("objective.none", "No optimization objective is declared."),
        ("objective.affine", "Every objective expression is affine."),
        ("objective.quadratic_convex", "A minimization quadratic objective has certified positive-semidefinite curvature, or the sign-adjusted maximization analogue."),
        ("objective.quadratic_indefinite", "A quadratic objective is certified indefinite/nonconvex."),
        ("objective.nonlinear_convex", "The objective is nonquadratic and certified convex for minimization or concave for maximization."),
        ("objective.nonlinear_general", "The objective contains general nonlinear structure without a convex-only claim."),
        ("objective.black_box", "The objective is available only through governed evaluation calls."),
        ("objective.multiobjective", "Multiple objectives have explicit Pareto, lexicographic, goal, or scalarization semantics."),
    ],
    "constraint_form": [
        ("constraints.affine", "Every algebraic constraint is affine or a variable bound."),
        ("constraints.quadratic_convex", "At least one quadratic constraint is certified convex in its admitted direction."),
        ("constraints.quadratic_nonconvex", "At least one quadratic constraint is nonconvex."),
        ("constraints.soc", "Second-order or rotated-second-order cone membership occurs."),
        ("constraints.sdp", "Positive-semidefinite cone membership occurs."),
        ("constraints.exponential_cone", "Exponential-cone membership occurs."),
        ("constraints.power_cone", "Power-cone membership occurs."),
        ("constraints.nonlinear_convex", "General nonquadratic constraints are certified convex in admitted orientation."),
        ("constraints.nonlinear_general", "General nonlinear constraints occur without a convex-only claim."),
        ("constraints.global_cp", "Constraint-programming global constraints occur."),
        ("constraints.boolean", "Boolean clauses or propositional formulas occur."),
        ("constraints.smt_theory", "Satisfiability-modulo-theories formulas occur."),
        ("constraints.pseudo_boolean", "Pseudo-Boolean constraints occur."),
        ("constraints.complementarity", "Complementarity or equilibrium relations occur."),
        ("constraints.ode_dae", "Ordinary differential or differential-algebraic equations occur."),
        ("constraints.transition", "Explicit state/action transition relations occur."),
        ("constraints.black_box", "Feasibility is known only through a governed evaluator."),
    ],
    "geometry_proof": [
        ("proof.scope_closed", "The subproblem boundary is closed and all in-scope semantics are enumerated."),
        ("proof.coefficients_finite", "All required numeric coefficients and bounds are finite or explicitly allowed infinities."),
        ("proof.domains_complete", "Every decision variable has an explicit domain, bounds, units, and index identity."),
        ("proof.convexity", "Convexity is certified by an admitted rule, theorem, or independently checkable certificate."),
        ("proof.psd", "The relevant quadratic form is certified positive semidefinite in the required orientation."),
        ("proof.reformulation_equivalent", "A reformulation is proved equivalent over the declared domain and tolerances."),
        ("proof.discretization_bounded", "Discretization error and applicability are bounded for the declared purpose."),
        ("proof.simulation_validated", "The conceptual/computational simulation model is validated for the declared use."),
        ("proof.network_structure", "Network conservation, incidence, capacities, and cost structure are certified."),
        ("proof.status_precision", "Required terminal, feasibility, bound, and optimality status precision is explicit."),
        ("proof.vertical_acceptance", "The full vertical acceptance gate has a valid receipt."),
    ],
    "uncertainty_information": [
        ("uncertainty.none", "All model inputs are treated as fixed for this solve occurrence."),
        ("uncertainty.probability_law", "A governed probability law represents uncertainty."),
        ("uncertainty.scenarios", "A finite governed scenario set or tree represents uncertainty."),
        ("uncertainty.set", "A governed uncertainty set defines robust feasibility."),
        ("uncertainty.ambiguity_set", "A governed set of probability laws defines distributional robustness."),
        ("uncertainty.chance_constraint", "A probability-of-violation constraint occurs."),
        ("uncertainty.decision_dependent", "A decision changes the uncertainty law, observations, or admissible set."),
        ("information.two_stage", "Decisions split into before-observation and recourse stages."),
        ("information.multistage", "Three or more revelation/decision stages occur."),
        ("information.nonanticipativity", "Policies are forbidden from using information not yet revealed."),
        ("information.recourse", "Later corrective decisions are explicitly represented."),
    ],
    "temporal_decision": [
        ("time.static", "All decisions are selected in one information stage."),
        ("time.sequential", "State, action, observation, and transition repeat over ordered stages."),
        ("time.markov", "A declared state is sufficient for the transition/reward model."),
        ("time.partially_observed", "Decision makers observe signals rather than full state."),
        ("time.continuous", "Continuous-time dynamics or controls occur."),
        ("time.online", "Decisions arrive and must be committed before all future inputs are known."),
    ],
    "execution_semantics": [
        ("execution.math_programming", "An algebraic mathematical program is to be solved."),
        ("execution.constraint_programming", "A constraint-programming model is searched/propagated."),
        ("execution.cp_sat", "An integer CP-SAT model is compiled to the exact documented interface."),
        ("execution.sat", "A propositional satisfiability model is checked."),
        ("execution.smt", "A theory-sorted satisfiability model is checked."),
        ("execution.specialized_network", "A certified specialized network algorithm is requested."),
        ("execution.dynamic_programming", "A recurrence/value function is evaluated or optimized."),
        ("execution.simulation", "A governed simulation experiment is executed."),
        ("execution.simulation_optimization", "An optimizer governs repeated simulation evaluations."),
        ("execution.integration", "ODE/DAE numerical integration is requested."),
        ("execution.hybrid", "Multiple execution semantics are coupled in one explicit composition graph."),
    ],
    "simulation_form": [
        ("simulation.discrete_event", "State changes at explicitly scheduled events."),
        ("simulation.continuous", "Continuous-time equations are numerically integrated."),
        ("simulation.system_dynamics", "Aggregate stocks, flows, feedback, and delays are simulated."),
        ("simulation.agent_based", "Modeled entities follow interaction/behavior rules."),
        ("simulation.monte_carlo", "Repeated randomized trials estimate an outcome distribution."),
        ("simulation.co_simulation", "Separately executed submodels exchange values at governed synchronization points."),
        ("simulation.multimethod", "Two or more simulation paradigms are explicitly composed."),
    ],
    "special_structure": [
        ("structure.network_flow", "The model is a flow/conservation problem on a directed or undirected network."),
        ("structure.bilevel", "One optimization problem is constrained by another problem's response/optimality."),
        ("structure.equilibrium", "A fixed point, variational inequality, game, or market equilibrium is sought."),
        ("structure.planning_actions", "Typed actions, preconditions, effects, and goals are explicit."),
        ("structure.black_box", "A key response has no admitted symbolic relation."),
        ("structure.composite_graph", "Submodels and their typed coupling edges are explicit."),
    ],
    "extension_boundary": [
        ("extension.predictive_model", "A fitted statistical/predictive artifact supplies a typed input or estimate."),
        ("extension.generative_proposal", "A generative model may propose declarations, explanations, or alternatives."),
        ("extension.tool_agent", "A tool-using agent may propose a plan or tool invocation intent."),
        ("extension.modeled_entity_agent", "The word agent denotes an entity inside an agent-based simulation."),
        ("extension.human_judgment", "A human supplies a governed judgment or approval."),
    ],
}


FEATURE_ATOMS = []
for group, values in ATOM_GROUPS.items():
    axis_ref = {
        "objective_form": "axis.mca.expression_structure",
        "constraint_form": "axis.mca.expression_structure",
        "simulation_form": "axis.mca.execution_semantics",
        "special_structure": "axis.mca.composition_boundary",
        "extension_boundary": "axis.mca.composition_boundary",
    }.get(group, f"axis.mca.{group}")
    for atom_id, semantics in values:
        FEATURE_ATOMS.append(
            rec(
                f"feature.mca.{atom_id}",
                "feature_atom",
                axis_ref=axis_ref,
                symbol=atom_id,
                semantics=semantics,
                absence_semantics="unknown_unless_an_exclusive_sibling_is_proved",
            )
        )


def model_class(
    class_id: str,
    name: str,
    role: str,
    all_of: list[str],
    none_of: list[str],
    evidence_refs: list[str],
    claim: str,
    not_equivalent_to: list[str],
    any_of_groups: list[list[str]] | None = None,
) -> dict:
    return rec(
        f"class.mca.{class_id}",
        "model_class",
        name=name,
        classification_role=role,
        sound_sufficient_predicate={
            "all_of": all_of,
            "any_of_groups": any_of_groups or [],
            "none_of": none_of,
        },
        admitted_claim=claim,
        not_equivalent_to=not_equivalent_to,
        evidence_refs=evidence_refs,
        binding_law="A matched class creates provider requirements; it never selects or qualifies a provider.",
    )


MATH_CORE = ["proof.scope_closed", "proof.coefficients_finite", "proof.domains_complete"]
STATIC_DETERMINISTIC = ["uncertainty.none", "time.static"]
NO_NONLINEAR = [
    "constraints.quadratic_convex", "constraints.quadratic_nonconvex", "constraints.soc", "constraints.sdp",
    "constraints.exponential_cone", "constraints.power_cone", "constraints.nonlinear_convex",
    "constraints.nonlinear_general", "constraints.complementarity", "constraints.ode_dae",
    "constraints.black_box", "objective.quadratic_convex", "objective.quadratic_indefinite",
    "objective.nonlinear_convex", "objective.nonlinear_general", "objective.black_box",
]

MODEL_CLASSES = [
    model_class("continuous_lp", "Continuous linear program", "base_formulation", MATH_CORE + ["execution.math_programming", "vars.continuous_only", "objective.affine", "constraints.affine"], ["vars.any_integer", "vars.binary", *NO_NONLINEAR], ["source.mca.moi.standard_form", "source.mca.mosek.cookbook"], "The closed deterministic algebraic subproblem is an LP over continuous variables.", ["continuous relaxation of a MIP", "linearized nonlinear model without equivalence proof", "network flow with unproved structure"]),
    model_class("milp", "Mixed-integer linear program", "base_formulation", MATH_CORE + ["execution.math_programming", "vars.any_integer", "objective.affine", "constraints.affine"], NO_NONLINEAR, ["source.mca.scip.problem_classes", "source.mca.ortools.cpsat"], "The closed algebraic subproblem is linear and contains at least one integer decision variable.", ["continuous LP", "CP model", "LP relaxation"]),
    model_class("binary_linear", "Binary linear program", "refinement", MATH_CORE + ["execution.math_programming", "vars.binary", "objective.affine", "constraints.affine"], NO_NONLINEAR, ["source.mca.scip.problem_classes"], "The linear model contains binary decision variables.", ["SAT encoding", "continuous relaxation"]),
    model_class("convex_qp", "Convex quadratic program", "base_formulation", MATH_CORE + ["execution.math_programming", "vars.continuous_only", "objective.quadratic_convex", "constraints.affine", "proof.psd", "proof.convexity"], ["vars.any_integer", "objective.quadratic_indefinite", "constraints.quadratic_convex", "constraints.quadratic_nonconvex", "constraints.nonlinear_general"], ["source.mca.moi.standard_form", "source.mca.mosek.cookbook"], "The continuous model has a certified convex quadratic objective and affine constraints.", ["indefinite QP", "QCQP", "MIQP"]),
    model_class("nonconvex_qp", "Nonconvex quadratic program", "base_formulation", MATH_CORE + ["execution.math_programming", "vars.continuous_only", "objective.quadratic_indefinite", "constraints.affine"], ["vars.any_integer", "proof.convexity"], ["source.mca.moi.standard_form", "source.mca.scip.problem_classes"], "The continuous quadratic objective is certified nonconvex/indefinite.", ["convex QP", "global optimum proof"]),
    model_class("miqp", "Mixed-integer quadratic program", "base_formulation", MATH_CORE + ["execution.math_programming", "vars.any_integer", "constraints.affine"], ["constraints.quadratic_convex", "constraints.quadratic_nonconvex"], ["source.mca.moi.standard_form", "source.mca.scip.problem_classes"], "The model has integer variables and a quadratic objective with affine constraints.", ["QP", "MILP"], any_of_groups=[["objective.quadratic_convex", "objective.quadratic_indefinite"]]),
    model_class("convex_qcqp", "Convex quadratically constrained quadratic program", "base_formulation", MATH_CORE + ["execution.math_programming", "vars.continuous_only", "constraints.quadratic_convex", "proof.convexity"], ["vars.any_integer", "constraints.quadratic_nonconvex"], ["source.mca.mosek.cookbook"], "The continuous quadratic objective/constraint system is certified convex.", ["nonconvex QCQP", "SOCP reformulation without equivalence proof"], any_of_groups=[["objective.affine", "objective.quadratic_convex"]]),
    model_class("nonconvex_qcqp", "Nonconvex quadratically constrained quadratic program", "base_formulation", MATH_CORE + ["execution.math_programming", "vars.continuous_only", "constraints.quadratic_nonconvex"], ["vars.any_integer", "proof.convexity"], ["source.mca.scip.problem_classes"], "The continuous model has at least one nonconvex quadratic constraint.", ["convex QCQP", "SOCP"]),
    model_class("miqcqp", "Mixed-integer quadratically constrained quadratic program", "base_formulation", MATH_CORE + ["execution.math_programming", "vars.any_integer"], [], ["source.mca.scip.problem_classes", "source.mca.mosek.cookbook"], "The model combines integrality with quadratic constraints.", ["MIQP", "MISOCP"], any_of_groups=[["constraints.quadratic_convex", "constraints.quadratic_nonconvex"]]),
    model_class("socp", "Second-order cone program", "base_formulation", MATH_CORE + ["execution.math_programming", "vars.continuous_only", "objective.affine", "constraints.soc", "proof.convexity"], ["vars.any_integer", "constraints.quadratic_nonconvex", "constraints.nonlinear_general"], ["source.mca.mosek.cookbook", "source.mca.moi.standard_form"], "The continuous model is represented by affine maps into second-order cones.", ["nonconvex QCQP", "MISOCP"]),
    model_class("misocp", "Mixed-integer second-order cone program", "base_formulation", MATH_CORE + ["execution.math_programming", "vars.any_integer", "objective.affine", "constraints.soc", "proof.convexity"], ["constraints.quadratic_nonconvex"], ["source.mca.mosek.cookbook"], "The model combines integer domains with certified second-order-cone constraints.", ["SOCP", "generic MINLP"]),
    model_class("sdp", "Semidefinite program", "base_formulation", MATH_CORE + ["execution.math_programming", "vars.continuous_only", "objective.affine", "constraints.sdp", "proof.convexity"], ["vars.any_integer"], ["source.mca.mosek.cookbook", "source.mca.moi.standard_form"], "The model uses affine mappings into the positive-semidefinite cone.", ["matrix-valued nonlinear model", "MISOCP"]),
    model_class("exponential_conic", "Exponential-cone program", "base_formulation", MATH_CORE + ["execution.math_programming", "vars.continuous_only", "objective.affine", "constraints.exponential_cone", "proof.convexity"], ["vars.any_integer"], ["source.mca.mosek.cookbook"], "The model uses admitted exponential-cone membership.", ["arbitrary exponential nonlinear program"]),
    model_class("power_conic", "Power-cone program", "base_formulation", MATH_CORE + ["execution.math_programming", "vars.continuous_only", "objective.affine", "constraints.power_cone", "proof.convexity"], ["vars.any_integer"], ["source.mca.mosek.cookbook"], "The model uses admitted power-cone membership.", ["arbitrary power nonlinear program"]),
    model_class("convex_nlp", "Certified convex nonlinear program", "base_formulation", MATH_CORE + ["execution.math_programming", "vars.continuous_only", "proof.convexity"], ["vars.any_integer", "objective.quadratic_indefinite", "constraints.quadratic_nonconvex"], ["source.mca.cvxpy.dcp", "source.mca.mosek.cookbook"], "The nonquadratic continuous model is certified convex under the admitted composition rules.", ["DCP-unknown model", "general NLP"], any_of_groups=[["objective.nonlinear_convex", "constraints.nonlinear_convex"]]),
    model_class("general_nlp", "General continuous nonlinear program", "base_formulation", MATH_CORE + ["execution.math_programming", "vars.continuous_only"], ["vars.any_integer"], ["source.mca.scip.problem_classes", "source.mca.casadi.optimal_control"], "The closed continuous model contains general nonlinear expressions; convexity/globality require separate facts.", ["convex NLP", "global optimum proof"], any_of_groups=[["objective.nonlinear_general", "constraints.nonlinear_general", "objective.black_box", "constraints.black_box"]]),
    model_class("minlp", "Mixed-integer nonlinear program", "base_formulation", MATH_CORE + ["execution.math_programming", "vars.any_integer"], [], ["source.mca.scip.problem_classes"], "The closed algebraic model combines integer domains with nonlinear expressions.", ["MILP", "continuous NLP"], any_of_groups=[["objective.nonlinear_general", "objective.nonlinear_convex", "constraints.nonlinear_general", "constraints.nonlinear_convex", "constraints.quadratic_nonconvex"]]),
    model_class("finite_domain_cp", "Finite-domain constraint program", "base_formulation", ["proof.scope_closed", "proof.domains_complete", "execution.constraint_programming", "vars.finite_discrete", "constraints.global_cp"], [], ["source.mca.minizinc.handbook", "source.mca.ortools.cp"], "The model is a finite-domain constraint program with explicit global/reified relations.", ["MILP merely because a linear encoding exists", "CP-SAT occurrence"]),
    model_class("cp_sat_integer", "CP-SAT integer model", "provider_neutral_interface_class", ["proof.scope_closed", "proof.domains_complete", "execution.cp_sat", "vars.any_integer"], ["vars.continuous_only"], ["source.mca.ortools.cpsat"], "The exact lowered model satisfies the integer-only CP-SAT interface contract.", ["generic CP", "MIP provider equivalence"]),
    model_class("sat", "Propositional satisfiability problem", "base_formulation", ["proof.scope_closed", "execution.sat", "constraints.boolean"], ["constraints.smt_theory"], ["source.mca.smtlib.standard"], "The model is propositional satisfiability over Boolean formulas.", ["SMT", "MaxSAT", "CP"]),
    model_class("smt", "Satisfiability modulo theories problem", "base_formulation", ["proof.scope_closed", "execution.smt", "constraints.smt_theory"], [], ["source.mca.smtlib.standard"], "The model is satisfiability modulo explicitly declared theories and logics.", ["SAT", "proof of decidability for an arbitrary theory combination"]),
    model_class("pseudo_boolean", "Pseudo-Boolean optimization/feasibility", "base_formulation", ["proof.scope_closed", "vars.binary", "constraints.pseudo_boolean"], [], ["source.mca.moi.standard_form", "source.mca.smtlib.standard"], "The model uses linear integer relations over Boolean variables with explicit objective semantics if any.", ["CNF SAT", "binary MILP provider equivalence"]),
    model_class("network_flow", "Certified network-flow specialization", "special_structure", MATH_CORE + ["execution.specialized_network", "structure.network_flow", "constraints.affine", "proof.network_structure"], ["constraints.nonlinear_general", "constraints.quadratic_nonconvex"], ["source.mca.ortools.cp", "source.mca.moi.standard_form"], "The subproblem satisfies the declared network conservation/capacity/cost specialization.", ["every graph optimization problem", "nonlinear hydraulic flow"]),
    model_class("bilevel", "Bilevel mathematical program", "composition_structure", MATH_CORE + ["execution.math_programming", "structure.bilevel"], [], ["source.mca.scip.problem_classes", "source.mca.moi.standard_form"], "The model contains an explicit leader/follower or nested-optimal-response contract.", ["one flattened model without equivalence proof"]),
    model_class("complementarity_equilibrium", "Complementarity or equilibrium model", "composition_structure", MATH_CORE + ["execution.math_programming"], [], ["source.mca.scip.problem_classes", "source.mca.moi.standard_form"], "The model contains complementarity or equilibrium/fixed-point relations.", ["ordinary NLP", "market simulation"], any_of_groups=[["constraints.complementarity", "structure.equilibrium"]]),
    model_class("two_stage_stochastic", "Two-stage stochastic program with recourse", "uncertainty_modifier", ["proof.scope_closed", "uncertainty.probability_law", "information.two_stage", "information.recourse", "information.nonanticipativity"], ["uncertainty.none"], ["source.mca.shapiro.stochastic"], "The problem has governed before/after-information decisions, probability semantics, recourse, and nonanticipativity.", ["deterministic scenario list", "robust optimization"]),
    model_class("multistage_stochastic", "Multistage stochastic program", "uncertainty_modifier", ["proof.scope_closed", "uncertainty.probability_law", "information.multistage", "information.nonanticipativity"], ["uncertainty.none"], ["source.mca.shapiro.stochastic"], "The problem has three or more governed information/decision stages under a probability law.", ["rolling deterministic re-solve", "two-stage program"]),
    model_class("robust_optimization", "Robust optimization model", "uncertainty_modifier", ["proof.scope_closed", "uncertainty.set"], ["uncertainty.none"], ["source.mca.bertsimas_sim.robust"], "Feasibility/performance is required over a governed uncertainty set.", ["scenario stress test", "stochastic expectation model"]),
    model_class("distributionally_robust", "Distributionally robust optimization model", "uncertainty_modifier", ["proof.scope_closed", "uncertainty.ambiguity_set"], ["uncertainty.none"], ["source.mca.bertsimas_sim.robust", "source.mca.shapiro.stochastic"], "The model optimizes against a governed ambiguity set of probability laws.", ["ordinary robust optimization", "one fitted distribution"]),
    model_class("chance_constrained", "Chance-constrained optimization model", "uncertainty_modifier", ["proof.scope_closed", "uncertainty.probability_law", "uncertainty.chance_constraint"], ["uncertainty.none"], ["source.mca.shapiro.stochastic"], "The model constrains violation probability under an admitted probability law.", ["soft constraint", "empirical percentile without error contract"]),
    model_class("dynamic_program", "Dynamic-programming formulation", "temporal_formulation", ["proof.scope_closed", "execution.dynamic_programming", "time.sequential", "constraints.transition"], [], ["source.mca.pddl.2_1"], "A state/action transition and recurrence/value relation define a sequential decision problem.", ["any time-indexed MILP", "simulation"]),
    model_class("mdp", "Markov decision process", "temporal_formulation", ["proof.scope_closed", "time.sequential", "time.markov", "uncertainty.probability_law", "constraints.transition"], ["time.partially_observed"], ["source.mca.shapiro.stochastic"], "A governed Markov state, action, transition law, and objective define the process.", ["POMDP", "unvalidated learned simulator"]),
    model_class("pomdp", "Partially observed Markov decision process", "temporal_formulation", ["proof.scope_closed", "time.sequential", "time.markov", "time.partially_observed", "uncertainty.probability_law", "constraints.transition"], [], ["source.mca.shapiro.stochastic"], "A governed latent Markov state and observation process define the decision problem.", ["fully observed MDP", "generic agent"]),
    model_class("optimal_control", "Continuous-time optimal-control problem", "temporal_formulation", ["proof.scope_closed", "role.control", "time.continuous", "constraints.ode_dae"], [], ["source.mca.casadi.optimal_control"], "A control trajectory/policy is optimized subject to governed continuous-time dynamics.", ["ODE simulation", "discretized NLP without error contract"]),
    model_class("planning", "Action-planning problem", "temporal_formulation", ["proof.scope_closed", "role.planning", "structure.planning_actions", "constraints.transition"], [], ["source.mca.pddl.2_1"], "Actions, preconditions, effects, time semantics, and goals define a planning problem.", ["LLM-generated plan", "workflow definition"]),
    model_class("discrete_event_simulation", "Discrete-event simulation", "simulation_formulation", ["proof.scope_closed", "execution.simulation", "simulation.discrete_event"], [], ["source.mca.anylogic.multimethod", "source.mca.fmi.3_0_2"], "The experiment advances modeled time between scheduled state-changing events.", ["queueing theorem", "optimization proof"]),
    model_class("continuous_simulation", "Continuous simulation", "simulation_formulation", ["proof.scope_closed", "execution.simulation", "simulation.continuous", "constraints.ode_dae"], [], ["source.mca.fmi.3_0_2", "source.mca.casadi.optimal_control"], "The experiment numerically integrates continuous-time equations and handles declared events.", ["optimal control", "physical truth"]),
    model_class("system_dynamics_simulation", "System-dynamics simulation", "simulation_formulation", ["proof.scope_closed", "execution.simulation", "simulation.system_dynamics"], [], ["source.mca.anylogic.multimethod"], "The experiment evolves aggregate stocks, flows, feedback, and delays.", ["discrete-event simulation", "causal proof"]),
    model_class("agent_based_simulation", "Agent-based simulation", "simulation_formulation", ["proof.scope_closed", "execution.simulation", "simulation.agent_based", "extension.modeled_entity_agent"], [], ["source.mca.anylogic.multimethod"], "Modeled entities interact under declared behavior rules; the word agent has no LLM implication.", ["tool-using software agent", "autonomous authority"]),
    model_class("monte_carlo_experiment", "Monte Carlo experiment", "simulation_formulation", ["proof.scope_closed", "execution.simulation", "simulation.monte_carlo", "role.estimation"], [], ["source.mca.shapiro.stochastic"], "Repeated governed random trials estimate a declared response distribution or integral.", ["stochastic optimization", "proof of real-world validity"]),
    model_class("co_simulation", "Co-simulation composition", "simulation_formulation", ["proof.scope_closed", "execution.simulation", "simulation.co_simulation", "structure.composite_graph"], [], ["source.mca.fmi.3_0_2"], "Submodels exchange data at explicit synchronization points under a declared master/scheduling contract.", ["one monolithic simulation", "FMI compatibility without validation"]),
    model_class("simulation_optimization", "Simulation optimization", "composition_structure", ["proof.scope_closed", "execution.simulation_optimization", "execution.simulation", "role.optimization", "structure.composite_graph"], [], ["source.mca.anylogic.multimethod", "source.mca.shapiro.stochastic"], "An explicit optimizer controls governed simulation experiments and interprets noisy responses under a budget.", ["simulation alone", "algebraic optimizer alone"]),
    model_class("hybrid_composite", "Hybrid composed decision model", "composition_structure", ["proof.scope_closed", "execution.hybrid", "structure.composite_graph"], [], ["source.mca.fmi.3_0_2", "source.mca.moi.paper"], "Multiple model/execution semantics are coupled through explicit typed interfaces and loss/error contracts.", ["one solver class", "silent model collapse"]),
]


PROOF_SPECS = [
    ("scope_closure", "Every in-scope law, variable, objective, constraint, uncertainty source, and submodel is enumerated; omitted scope is explicit.", "refusal.mca.open_scope"),
    ("domain_totality", "Every variable has domain, bounds, units, index identity, time meaning, and missing-value policy.", "refusal.mca.domain_unknown"),
    ("expression_totality", "Every expression node has a typed operator, operands, units, curvature facts, and source span.", "refusal.mca.expression_unknown"),
    ("finite_numeric_input", "NaN, invalid infinities, overflow, and unit-incompatible coefficients are rejected before classification.", "refusal.mca.non_finite"),
    ("convexity_certificate", "Convexity claims cite an admitted rule/certificate; unknown curvature remains unknown.", "refusal.mca.convexity_unknown"),
    ("quadratic_psd", "The sign-adjusted Hessian/quadratic form has an admitted PSD certificate for convex-QP use.", "refusal.mca.psd_missing"),
    ("reformulation_equivalence", "Bridges, linearizations, cone reformulations, encodings, and eliminations preserve declared semantics or expose approved loss.", "refusal.mca.unproved_reformulation"),
    ("integrality_preservation", "Relaxation, rounding, and encoding preserve or explicitly weaken integer-domain claims under authority.", "refusal.mca.integrality_erased"),
    ("uncertainty_semantics", "Each unknown is assigned probability, scenario, set, ambiguity, or epistemic status with provenance.", "refusal.mca.uncertainty_omitted"),
    ("scenario_probability", "Scenario weights are normalized, justified, time-indexed, and distinct from unweighted stress cases.", "refusal.mca.scenario_law_missing"),
    ("information_revelation", "Observation time, decision time, stages, recourse, and nonanticipativity are explicit.", "refusal.mca.anticipative_policy"),
    ("robust_set_validity", "Uncertainty/ambiguity sets have membership, calibration, coverage intent, and nonemptiness semantics.", "refusal.mca.robust_set_invalid"),
    ("network_specialization", "Conservation, topology, capacities, costs, gains/losses, and side constraints satisfy the claimed network specialization.", "refusal.mca.network_structure_unproved"),
    ("dynamics_discretization", "ODE/DAE/transition semantics, initial/boundary conditions, solver tolerances, and discretization error are governed.", "refusal.mca.dynamics_unbounded"),
    ("simulation_validity", "Conceptual-model validity, implementation verification, warm-up, replications, seeds, input models, and output uncertainty are governed.", "refusal.mca.simulation_not_validated"),
    ("black_box_contract", "A black-box evaluator declares domain, determinism/noise, failure, cost, cancellation, and budget semantics.", "refusal.mca.black_box_opaque"),
    ("result_claim_precision", "Terminal reason, primal/dual status, incumbent, bound, gap, local/global scope, tolerances, and limits remain distinct.", "refusal.mca.status_strengthened"),
    ("solution_recomputation", "Feasibility and objective are independently recomputed where the exact class allows it.", "refusal.mca.solution_unchecked"),
    ("provider_conformance", "Exact adapter, implementation artifact, version, target occurrence, class subset, statuses, limits, and numerical profile are qualified.", "refusal.mca.provider_unqualified"),
    ("vertical_acceptance", "Source fitness, semantics, method validity, physical conformance, operations, authority, outcomes, and change gates pass for the vertical.", "refusal.mca.vertical_unaccepted"),
    ("authority_effect", "An analytical result remains a proposal until separately authorized effect intent and execution receipt exist.", "refusal.mca.effect_unauthorized"),
    ("agent_removal", "Removing generative/agent extensions leaves parsing, typing, adjudication, solving, validation, authorization, execution, and receipts intact.", "refusal.mca.agent_dependency"),
    ("predictive_artifact", "A fitted predictive artifact is editioned, calibrated/evaluated for use, and consumed through a typed uncertainty contract.", "refusal.mca.predictive_unqualified"),
    ("composition_interfaces", "Every hybrid edge declares variables, units, time, causality, synchronization, approximation, failure, and authority.", "refusal.mca.hybrid_edge_unknown"),
    ("finite_execution", "Time, memory, work, threads/devices, random trials, solver limits, cost, cancellation, and partial-result policy are finite.", "refusal.mca.budget_missing"),
]

PROOF_OBLIGATIONS = [
    rec(
        f"proof.mca.{proof_id}",
        "proof_obligation",
        statement=statement,
        failure_ref=failure_ref,
        discharge_states=["proved", "refuted", "unknown", "not_applicable"],
        no_strengthening_law="Only a valid scoped receipt may move unknown to proved; a proposal or provider declaration cannot.",
    )
    for proof_id, statement, failure_ref in PROOF_SPECS
]


REFUSAL_SPECS = [
    ("open_scope", "The declared model boundary is open, implicit, or still contains unresolved submodels.", "refuse_class_and_provider_binding"),
    ("domain_unknown", "At least one variable domain, bound, unit, identity, or time meaning is unknown.", "refuse_class_and_provider_binding"),
    ("expression_unknown", "An expression or foreign function has unknown typed semantics.", "refuse_requested_class"),
    ("non_finite", "A required coefficient or bound is NaN, unsupported infinity, overflowing, or unit-invalid.", "refuse_execution"),
    ("convexity_unknown", "A convex-only class is requested without a sound curvature/convexity proof.", "refuse_convex_class"),
    ("psd_missing", "A convex quadratic claim lacks a PSD certificate in the required orientation.", "refuse_convex_qp"),
    ("unproved_reformulation", "A linearization, relaxation, encoding, discretization, or cone bridge lacks equivalence/loss proof.", "retain_source_class_and_refuse_target_claim"),
    ("integrality_erased", "An integer/binary decision was relaxed or rounded without authorized loss semantics.", "refuse_original_problem_claim"),
    ("uncertainty_omitted", "Uncertainty materially affects the decision but was omitted from the declared deterministic class.", "refuse_deterministic_class"),
    ("scenario_law_missing", "A stochastic claim uses scenarios without an admitted probability/revelation law.", "refuse_stochastic_class"),
    ("anticipative_policy", "A decision or feature uses information unavailable at its commitment time.", "refuse_policy_or_solution"),
    ("robust_set_invalid", "An uncertainty/ambiguity set is undefined, empty, uncalibrated, or has unknown authority.", "refuse_robust_class"),
    ("network_structure_unproved", "Graph-shaped data is present but flow-specialization invariants are not proved.", "refuse_specialized_network_algorithm"),
    ("dynamics_unbounded", "Dynamics, initial/boundary conditions, discretization, or error tolerance are incomplete.", "refuse_control_or_dynamic_claim"),
    ("simulation_not_validated", "Simulation implementation may run but fitness for the declared decision is unproved.", "refuse_real_world_or_decision_claim"),
    ("black_box_opaque", "A black-box response lacks domain, failure, noise, resource, or cancellation semantics.", "refuse_automatic_search"),
    ("status_strengthened", "A provider status was mapped to a stronger feasibility, bound, or optimality claim.", "refuse_result"),
    ("solution_unchecked", "Returned variables/objective violate or have not been checked against the canonical model.", "refuse_result"),
    ("provider_unqualified", "A class match exists but no exact qualified offer/occurrence satisfies it.", "typed_gap_not_fallback"),
    ("vertical_unaccepted", "Provider conformance exists without vertical method/operations/authority/outcome acceptance.", "refuse_deployment"),
    ("effect_unauthorized", "A model result, simulation outcome, human suggestion, or agent plan is being treated as authority to act.", "refuse_effect"),
    ("agent_dependency", "A deterministic obligation depends on an LLM or agent extension being present or agreeing.", "refuse_compilation"),
    ("predictive_unqualified", "A score or fitted predictive artifact lacks the calibration/evaluation contract required by the downstream model.", "refuse_input_or_propagate_unknown"),
    ("hybrid_edge_unknown", "A composition edge lacks time, units, causality, loss, synchronization, or failure semantics.", "refuse_composite_class"),
    ("budget_missing", "Execution has no finite admitted resource/cost/cancellation envelope.", "refuse_execution"),
    ("simulation_is_not_optimization", "Simulation evidence is offered as feasibility, optimality, or physical-truth proof.", "refuse_claim"),
    ("heuristic_is_not_proof", "A heuristic incumbent is offered as a global optimum without a valid bound/certificate.", "refuse_optimality_claim"),
    ("relaxation_is_not_original", "A relaxation result is offered as a result for the original discrete/nonlinear/stochastic model.", "refuse_claim"),
    ("modeled_agent_confusion", "An entity in agent-based simulation is being treated as a tool-using LLM agent, or vice versa.", "refuse_semantic_mapping"),
]

REFUSAL_RULES = [
    rec(
        f"refusal.mca.{refusal_id}",
        "refusal_rule",
        trigger=trigger,
        disposition=disposition,
        recoverability="requires_new_typed_declaration_or_scoped_evidence",
    )
    for refusal_id, trigger, disposition in REFUSAL_SPECS
]


DECISION_SPECS = [
    ("subproblem_boundary", "Which laws and coupled submodels are inside this classification occurrence?", "vertical_method_owner", "ir.analytical_design"),
    ("problem_role", "Is the requested result feasibility, optimization, estimation, control, planning, or experiment?", "analytical_contract_owner", "ir.analytical_design"),
    ("variable_domains", "What domain, bounds, units, time, and identity does every decision/state variable have?", "model_semantics_owner", "ir.logical_operations"),
    ("objective_order", "What objective sense, order, scalarization, tolerance, and tie-break are authoritative?", "preference_authority", "ir.logical_operations"),
    ("constraint_semantics", "Which restrictions are hard, soft, chance, relaxable, or approval-gated?", "constraint_authority", "ir.assurance"),
    ("expression_algebra", "Which function/set/operator kinds occur and what are their exact editions?", "model_ir_owner", "ir.logical_operations"),
    ("geometry_certificate", "Which convexity, PSD, smoothness, monotonicity, or regularity claims are proved?", "method_owner", "ir.assurance"),
    ("uncertainty_representation", "Are unknowns represented by laws, scenarios, sets, ambiguity sets, or unresolved epistemic gaps?", "uncertainty_owner", "ir.analytical_design"),
    ("information_revelation", "When is each value known relative to each decision and commitment?", "time_and_authority_owner", "ir.analytical_design"),
    ("temporal_form", "Is the problem static, staged, sequential, online, partially observed, or continuous-time?", "method_owner", "ir.analytical_design"),
    ("simulation_role", "Is simulation the result, a validator, a response oracle, or a component inside optimization?", "simulation_experiment_owner", "ir.analytical_design"),
    ("transformation_loss", "Does each bridge preserve meaning or introduce an approved approximation/relaxation?", "transformation_authority", "ir.assurance"),
    ("proof_claim", "Which feasibility, bound, optimality, statistical, or validity claim is required?", "result_contract_owner", "ir.assurance"),
    ("provider_status_precision", "Which native statuses and certificates must survive the anti-corruption layer?", "qualification_owner", "ir.physical"),
    ("predictive_input", "Does a fitted predictive artifact enter, with what cutoff, calibration, uncertainty, and failure semantics?", "predictive_contract_owner", "ir.analytical_design"),
    ("optional_agent_extension", "Is generative/agent assistance requested, removable, and forbidden from satisfying deterministic obligations?", "automation_modality_owner", "ir.assurance"),
    ("effect_authority", "Who may convert an analytical proposal into an effect intent and execution?", "effect_authority", "ir.assurance"),
]

DECISION_POINTS = [
    rec(
        f"decision.mca.{decision_id}",
        "decision_point",
        question=question,
        authority=authority,
        binding_phase=phase,
        unresolved_disposition="typed_gap_or_refusal",
        default_law="No provider, model, prompt, agent, or implementation default may resolve this decision silently.",
    )
    for decision_id, question, authority, phase in DECISION_SPECS
]


AUTOMATION_BOUNDARIES = [
    rec("boundary.mca.deterministic_core", "automation_boundary", name="Deterministic adjudication core", modality="deterministic_required", owns=["parse and type check", "feature extraction", "class predicates", "proof/refusal state", "provider requirements", "decision trace"], may_not_be_satisfied_by=["LLM output", "agent plan", "provider marketing label"]),
    rec("boundary.mca.predictive_model", "automation_boundary", name="Predictive/statistical model input", modality="deterministic_analytical_method", owns=["fitted-artifact identity", "prediction contract", "calibration/evaluation", "uncertainty output"], may_not_be_satisfied_by=["unversioned score", "agent opinion", "post-cutoff leakage"]),
    rec("boundary.mca.generative_proposal", "automation_boundary", name="Optional generative proposal", modality="optional_or_intent_required", owns=["candidate declaration", "candidate explanation", "candidate alternative"], may_not_be_satisfied_by=["canonical class proof", "provider qualification", "effect authority", "receipt verification"]),
    rec("boundary.mca.tool_agent", "automation_boundary", name="Optional tool-agent proposal", modality="optional_or_intent_required", owns=["candidate plan", "candidate tool-call intent", "context/invocation receipt"], may_not_be_satisfied_by=["authorization", "effect execution", "solver result", "vertical acceptance"]),
    rec("boundary.mca.modeled_agent", "automation_boundary", name="Modeled agent inside simulation", modality="deterministic_or_stochastic_simulation_entity", owns=["entity state", "behavior rule", "interaction rule", "random stream if any"], may_not_be_satisfied_by=["LLM-agent semantics by name", "real-world person authority"]),
    rec("boundary.mca.human_judgment", "automation_boundary", name="Governed human judgment", modality="human_authority_or_review", owns=["explicit judgment", "approval/refusal", "rationale and scope"], may_not_be_satisfied_by=["unattributed UI click", "generated rationale", "assumed consent"]),
]


CONTEXTS = [
    rec("context.mca.feature_extraction", "bounded_context", name="Model Feature Extraction", owns=["typed feature atoms", "source-span links", "unknown facts"], excludes=["provider selection", "business ontology ownership"]),
    rec("context.mca.class_adjudication", "bounded_context", name="Model Class Adjudication", owns=["sound sufficient predicates", "multi-axis facets", "class refusal"], excludes=["solver execution", "vertical acceptance"]),
    rec("context.mca.transformation_proof", "bounded_context", name="Model Transformation Proof", owns=["equivalence", "relaxation/loss", "error contract", "bridge provenance"], excludes=["undocumented solver presolve", "business approval"]),
    rec("context.mca.result_claim", "bounded_context", name="Result Claim Semantics", owns=["feasibility", "bounds", "optimality scope", "limits", "no-strengthening"], excludes=["operational effect authority", "model validity"]),
    rec("context.mca.composition", "bounded_context", name="Hybrid Model Composition", owns=["submodel graph", "typed coupling edges", "synchronization", "error propagation"], excludes=["silent flattening", "provider-owned orchestration meaning"]),
    rec("context.mca.extension_boundary", "bounded_context", name="Model and Agent Extension Boundary", owns=["optional proposal roles", "removal proof", "proposal-to-core ACL"], excludes=["deterministic adjudication", "authorization", "effects"]),
]


LIBRARIES = [
    rec("library.mca.feature_ir", "library_boundary", name="Model feature IR", library_kind="pure_semantic", owns=["feature atoms", "typed expression/domain facts", "unknown-state algebra"], side_effects="none"),
    rec("library.mca.class_predicates", "library_boundary", name="Model-class predicate algebra", library_kind="pure_semantic", owns=["sound sufficient predicates", "facet lattice", "class trace"], side_effects="none"),
    rec("library.mca.convexity_oracle", "library_boundary", name="Convexity and curvature oracle contract", library_kind="pure_oracle_contract", owns=["rule vocabulary", "certificate verification", "unknown result"], side_effects="none"),
    rec("library.mca.reformulation_proof", "library_boundary", name="Reformulation proof contract", library_kind="pure_semantic", owns=["source/target model relation", "equivalence/loss/error evidence"], side_effects="none"),
    rec("library.mca.uncertainty_ir", "library_boundary", name="Uncertainty and information IR", library_kind="pure_semantic", owns=["laws/scenarios/sets", "revelation", "recourse", "nonanticipativity"], side_effects="none"),
    rec("library.mca.simulation_contract", "library_boundary", name="Simulation model/experiment contract", library_kind="pure_semantic", owns=["simulation modality", "experiment", "randomness", "validity claim"], side_effects="none"),
    rec("library.mca.result_acl", "library_boundary", name="Solver/simulator result anti-corruption layer", library_kind="pure_adapter_contract", owns=["status mapping", "no-strengthening", "claim scope"], side_effects="none"),
    rec("library.mca.trace", "library_boundary", name="Adjudication trace and receipt", library_kind="pure_evidence", owns=["facts read", "predicates matched", "refusals", "residual gaps"], side_effects="none"),
    rec("library.mca.extension_acl", "library_boundary", name="Optional model/agent proposal ACL", library_kind="pure_adapter_contract", owns=["proposal parsing", "taint/provenance", "core revalidation"], side_effects="none"),
    rec("library.mca.provider_requirement_projection", "library_boundary", name="Class-to-provider requirement projection", library_kind="pure_compiler", owns=["required function/set support", "status precision", "target and qualification requirements"], side_effects="none"),
]


NON_COLLAPSE_RULES = [
    ("business_case_not_model_class", "An industry case or product label does not determine its formulation class."),
    ("problem_family_not_formulation", "Routing, scheduling, allocation, planning, and nomination are problem families that may admit several formulations."),
    ("model_class_not_algorithm", "LP, MILP, CP, stochastic, robust, and simulation classes are not simplex, branch-and-bound, propagation, decomposition, or Monte Carlo algorithms."),
    ("algorithm_not_provider", "An algorithm name is not an exact library, adapter, version, target occurrence, or qualification receipt."),
    ("class_is_multi_axis", "A model may be simultaneously MILP, two-stage stochastic, multistage, bilevel, or hybrid; classification is not one flat enum."),
    ("subclass_not_equivalence", "Because every LP can be admitted by some more general solver class does not make the classes semantically equivalent."),
    ("relaxation_not_equivalence", "A continuous relaxation, approximation, surrogate, or linearization does not inherit the original model's claim."),
    ("simulation_not_optimization", "Simulation estimates behavior of a declared model; it does not prove an optimum or real-system truth."),
    ("predictive_not_agentic", "A fitted predictive/statistical model is an analytical artifact, not an agent merely because software invokes it."),
    ("abm_agent_not_llm_agent", "An agent in agent-based simulation is a modeled entity, not necessarily generative or tool-using software."),
    ("proposal_not_proof", "A human, LLM, or agent may propose a class, but deterministic predicates and evidence adjudicate it."),
    ("provider_label_not_support", "A provider's broad optimization or simulation label does not establish exact feature, status, target, or numerical support."),
    ("provider_test_not_vertical_acceptance", "Executed provider tests do not establish business-model validity, operational fitness, authority, or outcome safety."),
    ("local_not_global", "A local stationary solution, heuristic incumbent, or time-limited feasible result is not a global optimum."),
    ("status_no_strengthening", "Unknown and infeasible-or-unbounded may not be mapped to infeasible, unbounded, feasible, or optimal."),
]


CLASSIFICATION_RULES = [
    rec(
        f"rule.mca.classify.{row['id'].split('.')[-1]}",
        "classification_rule",
        class_ref=row["id"],
        predicate=row["sound_sufficient_predicate"],
        semantics="Emit the class facet iff the complete declared fact set satisfies this sound sufficient predicate.",
    )
    for row in MODEL_CLASSES
] + [
    rec(f"rule.mca.noncollapse.{rule_id}", "non_collapse_rule", statement=statement)
    for rule_id, statement in NON_COLLAPSE_RULES
]


def transformation(
    transformation_id: str,
    name: str,
    relation: str,
    source_classes: list[str],
    target_classes: list[str],
    proof_refs: list[str],
    transferred_claims: list[str],
    forbidden_claims: list[str],
    evidence_refs: list[str],
) -> dict:
    return rec(
        f"transform.mca.{transformation_id}",
        "model_transformation_kind",
        name=name,
        semantic_relation=relation,
        source_class_refs=source_classes,
        possible_target_class_refs=target_classes,
        required_proof_refs=proof_refs,
        transferred_claims=transferred_claims,
        forbidden_claims=forbidden_claims,
        evidence_refs=evidence_refs,
        applicability_status="candidate_rule_not_executed",
        invalidation_law="Any source model, domain, coefficient, tolerance, uncertainty, information, or target-interface change invalidates the transformation receipt.",
    )


TRANSFORMATIONS = [
    transformation("affine_canonicalization", "Affine canonicalization", "semantic_equivalence", ["class.mca.continuous_lp", "class.mca.milp"], ["class.mca.continuous_lp", "class.mca.milp"], ["proof.mca.expression_totality", "proof.mca.reformulation_equivalence"], ["feasibility", "objective", "bounds", "optimality_scope"], ["numerical-equivalence claim without tolerance/scaling analysis"], ["source.mca.moi.standard_form", "source.mca.moi.paper"]),
    transformation("variable_scaling", "Variable and row scaling", "bijective_solution_mapping_if_nonzero_finite", ["class.mca.continuous_lp", "class.mca.milp", "class.mca.convex_qp", "class.mca.general_nlp"], [], ["proof.mca.finite_numeric_input", "proof.mca.reformulation_equivalence"], ["mapped feasibility", "mapped objective", "mapped optimality_scope"], ["identical floating-point trajectory", "unchanged tolerances"], ["source.mca.mosek.cookbook"]),
    transformation("slack_introduction", "Slack/surplus-variable introduction", "equisatisfiable_with_decoding", ["class.mca.continuous_lp", "class.mca.milp", "class.mca.general_nlp"], [], ["proof.mca.domain_totality", "proof.mca.reformulation_equivalence"], ["feasibility through decoder", "objective if auxiliary variables are neutral"], ["identity of solution vectors without projection"], ["source.mca.moi.standard_form"]),
    transformation("epigraph_hypograph", "Epigraph or hypograph reformulation", "semantic_equivalence_under_orientation_and_domain", ["class.mca.convex_qp", "class.mca.convex_qcqp", "class.mca.convex_nlp"], ["class.mca.socp", "class.mca.exponential_conic", "class.mca.power_conic", "class.mca.sdp"], ["proof.mca.convexity_certificate", "proof.mca.reformulation_equivalence"], ["feasibility", "objective after declared projection", "convex optimality_scope"], ["arbitrary nonlinear equivalence"], ["source.mca.mosek.cookbook", "source.mca.cvxpy.dcp"]),
    transformation("conic_reformulation", "Certified conic reformulation", "semantic_equivalence_under_exact_cone_representation", ["class.mca.convex_qp", "class.mca.convex_qcqp", "class.mca.convex_nlp"], ["class.mca.socp", "class.mca.sdp", "class.mca.exponential_conic", "class.mca.power_conic"], ["proof.mca.convexity_certificate", "proof.mca.reformulation_equivalence"], ["feasibility", "objective", "duality claims admitted by the exact cone model"], ["equivalence from visual/algebraic similarity"], ["source.mca.mosek.cookbook"]),
    transformation("finite_domain_encoding", "Finite-domain or Boolean encoding", "equisatisfiable_with_total_encoder_decoder", ["class.mca.finite_domain_cp", "class.mca.sat", "class.mca.pseudo_boolean"], ["class.mca.sat", "class.mca.pseudo_boolean", "class.mca.milp"], ["proof.mca.domain_totality", "proof.mca.integrality_preservation", "proof.mca.reformulation_equivalence"], ["satisfiability through decoder", "objective only with weight/order proof"], ["same propagation", "same proof format", "same resource behavior"], ["source.mca.minizinc.handbook", "source.mca.smtlib.standard"]),
    transformation("continuous_relaxation", "Continuous relaxation of integer domains", "outer_relaxation_bound_producing", ["class.mca.milp", "class.mca.binary_linear", "class.mca.miqp", "class.mca.miqcqp", "class.mca.misocp", "class.mca.minlp"], ["class.mca.continuous_lp", "class.mca.convex_qp", "class.mca.convex_qcqp", "class.mca.socp", "class.mca.general_nlp"], ["proof.mca.integrality_preservation", "proof.mca.reformulation_equivalence"], ["relaxation bound in declared objective orientation", "possible infeasibility implication only in sound direction"], ["original-model feasibility", "original-model optimality", "rounding validity"], ["source.mca.scip.problem_classes", "source.mca.moi.standard_form"]),
    transformation("convex_relaxation", "Convex outer relaxation", "outer_relaxation_bound_producing", ["class.mca.nonconvex_qp", "class.mca.nonconvex_qcqp", "class.mca.general_nlp", "class.mca.minlp"], ["class.mca.convex_qp", "class.mca.convex_qcqp", "class.mca.socp", "class.mca.sdp", "class.mca.convex_nlp"], ["proof.mca.convexity_certificate", "proof.mca.reformulation_equivalence"], ["relaxation bound", "valid cuts under their exact proof"], ["source-model feasible solution", "global optimum without gap closure"], ["source.mca.mosek.cookbook", "source.mca.scip.problem_classes"]),
    transformation("exact_linearization", "Exact domain-bounded linearization", "semantic_equivalence_only_with_domain_certificate", ["class.mca.miqp", "class.mca.miqcqp", "class.mca.minlp", "class.mca.finite_domain_cp"], ["class.mca.milp"], ["proof.mca.domain_totality", "proof.mca.integrality_preservation", "proof.mca.reformulation_equivalence"], ["feasibility and objective through exact decoder"], ["equivalence when bounds, big-M constants, or logical cases are unproved"], ["source.mca.scip.problem_classes", "source.mca.moi.standard_form"]),
    transformation("piecewise_linear_approximation", "Piecewise-linear approximation", "bounded_approximation", ["class.mca.convex_nlp", "class.mca.general_nlp", "class.mca.optimal_control"], ["class.mca.continuous_lp", "class.mca.milp"], ["proof.mca.domain_totality", "proof.mca.reformulation_equivalence"], ["approximate objective/feasibility only within declared error envelope"], ["exact equivalence", "unqualified original-model optimality"], ["source.mca.mosek.cookbook"]),
    transformation("ode_dae_discretization", "ODE/DAE transcription or discretization", "numerical_approximation_with_error_contract", ["class.mca.optimal_control", "class.mca.continuous_simulation"], ["class.mca.general_nlp", "class.mca.convex_nlp", "class.mca.continuous_simulation"], ["proof.mca.dynamics_discretization", "proof.mca.reformulation_equivalence"], ["discretized-model claim plus declared error/tolerance"], ["continuous-time feasibility or stability without error proof"], ["source.mca.casadi.optimal_control", "source.mca.fmi.3_0_2"]),
    transformation("finite_scenario_deterministic_equivalent", "Finite-scenario deterministic equivalent", "equivalent_relative_to_scenario_and_information_contract", ["class.mca.two_stage_stochastic", "class.mca.multistage_stochastic"], ["class.mca.continuous_lp", "class.mca.milp", "class.mca.convex_qp", "class.mca.general_nlp"], ["proof.mca.scenario_probability", "proof.mca.information_revelation", "proof.mca.reformulation_equivalence"], ["scenario-law objective and feasibility", "nonanticipative policy through decoder"], ["population-law guarantee", "erasure of scenario/revelation provenance"], ["source.mca.shapiro.stochastic"]),
    transformation("robust_counterpart", "Robust counterpart construction", "equivalent_relative_to_uncertainty_set", ["class.mca.robust_optimization"], ["class.mca.continuous_lp", "class.mca.socp", "class.mca.sdp", "class.mca.convex_nlp"], ["proof.mca.robust_set_validity", "proof.mca.reformulation_equivalence"], ["set-wise robust feasibility under the exact uncertainty contract"], ["probabilistic coverage not supplied by the set contract"], ["source.mca.bertsimas_sim.robust", "source.mca.mosek.cookbook"]),
    transformation("chance_constraint_approximation", "Chance-constraint approximation", "one_sided_or_statistical_approximation", ["class.mca.chance_constrained"], ["class.mca.socp", "class.mca.milp", "class.mca.convex_nlp"], ["proof.mca.uncertainty_semantics", "proof.mca.scenario_probability", "proof.mca.reformulation_equivalence"], ["only the proved conservative or finite-sample guarantee"], ["exact chance-feasibility", "distribution-free guarantee unless proved"], ["source.mca.shapiro.stochastic", "source.mca.mosek.cookbook"]),
    transformation("sample_average_approximation", "Sample-average approximation", "statistical_approximation", ["class.mca.two_stage_stochastic", "class.mca.multistage_stochastic", "class.mca.chance_constrained"], ["class.mca.continuous_lp", "class.mca.milp", "class.mca.general_nlp"], ["proof.mca.scenario_probability", "proof.mca.simulation_validity", "proof.mca.finite_execution"], ["sample-problem result", "statistical error statement if separately proved"], ["true-distribution optimum", "zero sampling error"], ["source.mca.shapiro.stochastic"]),
    transformation("surrogate_replacement", "Surrogate replacement of an expensive/black-box response", "empirical_approximation", ["class.mca.general_nlp", "class.mca.simulation_optimization", "class.mca.hybrid_composite"], ["class.mca.continuous_lp", "class.mca.convex_qp", "class.mca.general_nlp"], ["proof.mca.black_box_contract", "proof.mca.predictive_artifact", "proof.mca.simulation_validity"], ["surrogate-domain prediction with validation uncertainty"], ["source-model feasibility", "source-model optimum", "causal mechanism"], ["source.mca.cvxpy.dcp", "source.mca.anylogic.multimethod"]),
    transformation("decomposition", "Exact decomposition with coordination", "equivalent_only_when_master_subproblem_protocol_closes", ["class.mca.continuous_lp", "class.mca.milp", "class.mca.two_stage_stochastic", "class.mca.robust_optimization"], [], ["proof.mca.scope_closure", "proof.mca.composition_interfaces", "proof.mca.reformulation_equivalence"], ["source-model claim only after convergence/certificate criteria pass"], ["subproblem feasibility as global feasibility", "partial coordination as optimum"], ["source.mca.shapiro.stochastic", "source.mca.moi.paper"]),
    transformation("presolve_elimination", "Presolve elimination and recovery", "equisatisfiable_or_equivalent_with_recovery_map", ["class.mca.continuous_lp", "class.mca.milp", "class.mca.convex_qp", "class.mca.general_nlp"], [], ["proof.mca.reformulation_equivalence", "proof.mca.result_claim_precision"], ["recovered source-model solution and proof claims supported by the receipt"], ["unmapped presolved result as source result"], ["source.mca.ortools.mathopt_result", "source.mca.mosek.cookbook"]),
    transformation("lagrangian_relaxation", "Lagrangian relaxation", "bound_producing_relaxation", ["class.mca.milp", "class.mca.minlp", "class.mca.robust_optimization"], [], ["proof.mca.reformulation_equivalence", "proof.mca.result_claim_precision"], ["valid dual/relaxation bound in declared orientation"], ["primal feasibility", "zero duality gap without proof"], ["source.mca.mosek.cookbook", "source.mca.scip.problem_classes"]),
    transformation("dualization", "Primal/dual transformation", "weak_duality_bound_or_equivalence_under_strong_duality", ["class.mca.continuous_lp", "class.mca.convex_qp", "class.mca.socp", "class.mca.sdp", "class.mca.convex_nlp"], [], ["proof.mca.convexity_certificate", "proof.mca.reformulation_equivalence", "proof.mca.result_claim_precision"], ["weak-duality bound always within exact assumptions", "equivalent optimum only with strong-duality conditions"], ["primal feasibility from dual feasibility", "strong duality by default"], ["source.mca.mosek.cookbook", "source.mca.ortools.mathopt_result"]),
    transformation("rounding_repair", "Rounding and feasibility repair", "candidate_solution_generation", ["class.mca.continuous_lp", "class.mca.convex_qp"], ["class.mca.milp", "class.mca.miqp"], ["proof.mca.integrality_preservation", "proof.mca.solution_recomputation"], ["source-model feasible incumbent only after exact validation"], ["optimality", "feasibility before validation", "bound preservation"], ["source.mca.scip.problem_classes"]),
    transformation("simulation_as_response_oracle", "Simulation as governed response oracle", "statistical_estimation_not_equivalence", ["class.mca.discrete_event_simulation", "class.mca.continuous_simulation", "class.mca.agent_based_simulation"], ["class.mca.simulation_optimization", "class.mca.hybrid_composite"], ["proof.mca.simulation_validity", "proof.mca.black_box_contract", "proof.mca.finite_execution"], ["estimated response distribution and uncertainty"], ["optimization proof", "real-world truth", "deterministic replay unless proved"], ["source.mca.anylogic.multimethod", "source.mca.fmi.3_0_2"]),
    transformation("co_simulation_partition", "Partition into co-simulated submodels", "compositional_approximation_or_equivalence_per_sync_contract", ["class.mca.continuous_simulation", "class.mca.hybrid_composite"], ["class.mca.co_simulation", "class.mca.hybrid_composite"], ["proof.mca.composition_interfaces", "proof.mca.dynamics_discretization", "proof.mca.simulation_validity"], ["co-simulation result under exact synchronization/error contract"], ["monolithic equivalence", "zero coupling error"], ["source.mca.fmi.3_0_2"]),
]


def provider_result_contract(row: dict) -> list[str]:
    role = row["classification_role"]
    class_id = row["id"]
    if "simulation" in class_id:
        return ["invalid_model", "unsupported", "completed_or_partial_experiment", "seed_and_random_stream_receipt", "estimate_and_uncertainty", "cancelled_or_resource_limited", "validation_scope"]
    if class_id in {"class.mca.sat", "class.mca.smt", "class.mca.pseudo_boolean", "class.mca.finite_domain_cp", "class.mca.cp_sat_integer"}:
        return ["invalid_model", "unsupported", "sat_or_feasible", "unsat_or_infeasible", "unknown", "model_or_assignment", "proof_or_core_when_required", "resource_limit", "cancellation"]
    if role in {"uncertainty_modifier", "temporal_formulation", "composition_structure"}:
        return ["lowering_or_native_support_receipt", "facet_preservation", "assumption_and_approximation_scope", "terminal_and_resource_status", "solution_or_policy_decoder"]
    return ["invalid_model", "unsupported", "infeasible", "unbounded_or_not_applicable", "feasible_incumbent", "primal_and_dual_bounds_when_defined", "local_or_global_optimality_scope", "numerical_failure", "resource_limit", "cancellation"]


PROVIDER_REQUIREMENTS = [
    rec(
        f"requirement.mca.{row['id'].removeprefix('class.mca.')}.provider",
        "model_class_provider_requirement",
        class_ref=row["id"],
        required_feature_atoms=sorted(row["sound_sufficient_predicate"]["all_of"]),
        required_any_of_feature_groups=row["sound_sufficient_predicate"]["any_of_groups"],
        prohibited_feature_atoms=sorted(row["sound_sufficient_predicate"]["none_of"]),
        required_result_contract=provider_result_contract(row),
        exact_subject_tuple=["implementation_artifact", "adapter", "version", "target_occurrence", "configuration", "numeric_posture", "resource_envelope"],
        qualification_dimensions=["model_generation", "valid_and_invalid_inputs", "terminal_status", "solution_recomputation", "numerics_and_tolerances", "limits_and_cancellation", "resource_and_cost", "security_and_dependencies", "independent_appraisal", "vertical_acceptance_separately"],
        binding_status="unbound_no_qualified_offer_asserted",
        fallback_law="No broader class, relaxation, model proposal, agent plan, or vendor name may silently satisfy this requirement.",
    )
    for row in MODEL_CLASSES
]


TRANSFORMATION_TRACES = [
    rec("transform_trace.mca.milp_to_lp_relaxation", "transformation_trace", source_class_refs=["class.mca.milp"], transformation_ref="transform.mca.continuous_relaxation", target_class_refs=["class.mca.continuous_lp"], proof_receipt_refs=[], expected_relation="outer_relaxation_bound_producing", allowed_claims=["relaxation bound"], refused_claims=["original-model feasibility", "original-model optimality"], expected_disposition="candidate_rule_unexecuted"),
    rec("transform_trace.mca.pipeline_unproved_linearization", "transformation_trace", source_class_refs=[], transformation_ref="transform.mca.exact_linearization", target_class_refs=["class.mca.continuous_lp"], proof_receipt_refs=[], expected_relation="semantic_equivalence_only_with_domain_certificate", allowed_claims=[], refused_claims=["pipeline broad problem is LP", "LP infeasibility proves physical infeasibility"], expected_disposition="refused_missing_scope_domain_and_equivalence"),
    rec("transform_trace.mca.robust_lp_counterpart", "transformation_trace", source_class_refs=["class.mca.robust_optimization"], transformation_ref="transform.mca.robust_counterpart", target_class_refs=["class.mca.continuous_lp"], proof_receipt_refs=[], expected_relation="equivalent_relative_to_uncertainty_set", allowed_claims=["uncertainty-set robust feasibility after proof"], refused_claims=["probabilistic coverage by implication"], expected_disposition="candidate_rule_unexecuted"),
    rec("transform_trace.mca.two_stage_deterministic_equivalent", "transformation_trace", source_class_refs=["class.mca.two_stage_stochastic", "class.mca.milp"], transformation_ref="transform.mca.finite_scenario_deterministic_equivalent", target_class_refs=["class.mca.milp"], proof_receipt_refs=[], expected_relation="equivalent_relative_to_scenario_and_information_contract", allowed_claims=["finite-scenario nonanticipative policy after proof"], refused_claims=["true-distribution optimality", "erasure of scenario lineage"], expected_disposition="candidate_rule_unexecuted"),
    rec("transform_trace.mca.optimal_control_discretization", "transformation_trace", source_class_refs=["class.mca.optimal_control"], transformation_ref="transform.mca.ode_dae_discretization", target_class_refs=["class.mca.general_nlp"], proof_receipt_refs=[], expected_relation="numerical_approximation_with_error_contract", allowed_claims=["discretized-model result with error envelope"], refused_claims=["continuous-time feasibility without error proof"], expected_disposition="candidate_rule_unexecuted"),
    rec("transform_trace.mca.simulation_oracle", "transformation_trace", source_class_refs=["class.mca.discrete_event_simulation"], transformation_ref="transform.mca.simulation_as_response_oracle", target_class_refs=["class.mca.simulation_optimization"], proof_receipt_refs=[], expected_relation="statistical_estimation_not_equivalence", allowed_claims=["estimated noisy response"], refused_claims=["global optimum", "real-world truth"], expected_disposition="candidate_rule_unexecuted"),
    rec("transform_trace.mca.agent_claims_exact_linearization", "transformation_trace", source_class_refs=["class.mca.general_nlp"], transformation_ref="transform.mca.exact_linearization", target_class_refs=["class.mca.continuous_lp"], proof_receipt_refs=[], proposal_refs=["extension.generative_proposal"], expected_relation="semantic_equivalence_only_with_domain_certificate", allowed_claims=[], refused_claims=["LLM statement as equivalence proof", "provider binding"], expected_disposition="refused_proposal_is_not_proof"),
]


def trace(
    trace_id: str,
    name: str,
    vertical: str,
    facts: list[str],
    requested: list[str],
    expected: list[str],
    expected_disposition: str,
    external_blockers: list[str] | None = None,
    negative_twin_ref: str | None = None,
) -> dict:
    return rec(
        f"trace.mca.{trace_id}",
        "classification_trace",
        name=name,
        vertical=vertical,
        facts=sorted(facts),
        requested_class_refs=sorted(requested),
        expected_class_refs=sorted(expected),
        expected_disposition=expected_disposition,
        external_blockers=external_blockers or [],
        negative_twin_ref=negative_twin_ref,
        execution_posture="deterministic_predicate_evaluation_only",
    )


LP_FACTS = MATH_CORE + [
    "role.optimization", "execution.math_programming", "vars.continuous_only", "objective.affine",
    "constraints.affine", "uncertainty.none", "time.static", "proof.status_precision",
]

TRACES = [
    trace("fixture.continuous_lp", "Canonical finite continuous-LP fixture", "compiler_conformance", LP_FACTS, ["class.mca.continuous_lp"], ["class.mca.continuous_lp"], "classified_not_provider_bound"),
    trace("fixture.binary_twin", "Binary-variable negative twin of the LP fixture", "compiler_conformance", [x for x in LP_FACTS if x != "vars.continuous_only"] + ["vars.any_integer", "vars.binary"], ["class.mca.continuous_lp"], ["class.mca.binary_linear", "class.mca.milp"], "requested_class_refused", negative_twin_ref="trace.mca.fixture.continuous_lp"),
    trace("pipeline.broad_unclosed", "Broad pipeline nomination problem with unresolved hydraulics and commitments", "oil_gas_midstream_pipeline", ["role.optimization", "execution.hybrid", "structure.composite_graph", "constraints.nonlinear_general", "vars.mixed", "uncertainty.scenarios"], ["class.mca.continuous_lp"], [], "requested_class_refused", external_blockers=["refusal.mca.open_scope", "refusal.mca.domain_unknown", "refusal.mca.uncertainty_omitted"]),
    trace("pipeline.lp_screen", "Closed continuous-LP nomination-capacity screening subproblem", "oil_gas_midstream_pipeline", LP_FACTS + ["structure.network_flow"], ["class.mca.continuous_lp"], ["class.mca.continuous_lp"], "classified_but_vertical_unaccepted", external_blockers=["refusal.mca.provider_unqualified", "refusal.mca.vertical_unaccepted"]),
    trace("commerce.two_stage_milp", "Two-stage stochastic tender-allocation model", "commerce_order_to_cash", MATH_CORE + ["role.optimization", "execution.math_programming", "vars.any_integer", "vars.binary", "objective.affine", "constraints.affine", "uncertainty.probability_law", "uncertainty.scenarios", "information.two_stage", "information.recourse", "information.nonanticipativity", "time.sequential", "proof.status_precision"], ["class.mca.milp", "class.mca.two_stage_stochastic"], ["class.mca.binary_linear", "class.mca.milp", "class.mca.two_stage_stochastic"], "classified_not_provider_bound"),
    trace("energy.robust_socp", "Robust second-order-cone planning model", "energy_grid_planning", MATH_CORE + ["role.optimization", "execution.math_programming", "vars.continuous_only", "objective.affine", "constraints.soc", "proof.convexity", "uncertainty.set", "time.static"], ["class.mca.socp", "class.mca.robust_optimization"], ["class.mca.robust_optimization", "class.mca.socp"], "classified_not_provider_bound"),
    trace("manufacturing.cp_sat", "Finite-domain job-shop model lowered to CP-SAT", "manufacturing_scheduling", ["proof.scope_closed", "proof.domains_complete", "role.optimization", "execution.constraint_programming", "execution.cp_sat", "vars.any_integer", "vars.finite_discrete", "constraints.global_cp", "constraints.affine", "time.static"], ["class.mca.finite_domain_cp", "class.mca.cp_sat_integer"], ["class.mca.cp_sat_integer", "class.mca.finite_domain_cp"], "classified_not_provider_bound"),
    trace("health.simulation_optimization", "Bed-flow simulation optimization", "health_acute_care", ["proof.scope_closed", "role.optimization", "role.estimation", "execution.simulation", "execution.simulation_optimization", "execution.hybrid", "simulation.discrete_event", "simulation.monte_carlo", "structure.composite_graph", "proof.simulation_validated"], ["class.mca.simulation_optimization"], ["class.mca.discrete_event_simulation", "class.mca.hybrid_composite", "class.mca.monte_carlo_experiment", "class.mca.simulation_optimization"], "classified_not_provider_bound"),
    trace("ecology.agent_based", "Modeled-entity agent-based simulation", "ecology_population", ["proof.scope_closed", "role.estimation", "execution.simulation", "simulation.agent_based", "extension.modeled_entity_agent", "proof.simulation_validated"], ["class.mca.agent_based_simulation"], ["class.mca.agent_based_simulation"], "classified_not_provider_bound"),
    trace("fixture.lp_with_llm_proposal", "LP fixture with removable LLM proposal stage", "compiler_conformance", LP_FACTS + ["extension.generative_proposal", "extension.tool_agent"], ["class.mca.continuous_lp"], ["class.mca.continuous_lp"], "classified_not_provider_bound", negative_twin_ref="trace.mca.fixture.continuous_lp"),
]


GAPS = [
    rec("gap.mca.expression_ir", "typed_gap", missing="A complete cross-universe expression/function/set IR with units, domains, source spans, and curvature facts.", consequence="Some declared models cannot yet be deterministically feature-extracted.", owner="model_ir_owner", severity="blocking"),
    rec("gap.mca.convexity_oracles", "typed_gap", missing="Independently reviewed convexity, PSD, and conic-representability oracle implementations.", consequence="Convex-only class claims remain proof-contract candidates.", owner="method_assurance_owner", severity="blocking"),
    rec("gap.mca.transformation_receipts", "typed_gap", missing="Executable equivalence/loss receipts for linearization, bridges, relaxations, and discretizations.", consequence="Target-class projection must fail closed.", owner="transformation_owner", severity="blocking"),
    rec("gap.mca.uncertainty_ir", "typed_gap", missing="Fully adjudicated probability/scenario/set/ambiguity/revelation schemas across all industries.", consequence="Stochastic and robust classes cannot be inferred from labels.", owner="uncertainty_owner", severity="blocking"),
    rec("gap.mca.hybrid_interface", "typed_gap", missing="Executable coupling-edge and error-propagation contracts for optimization/simulation/control hybrids.", consequence="Hybrid composition is classified but cannot be flattened or bound automatically.", owner="composition_owner", severity="blocking"),
    rec("gap.mca.provider_projection", "typed_gap", missing="Complete class-feature-status-to-offer projection for all exact provider occurrences.", consequence="A class match cannot select a provider.", owner="provider_registry_owner", severity="blocking"),
    rec("gap.mca.vertical_model_boundaries", "typed_gap", missing="Adjudicated subproblem boundaries for the full vertical-case corpus.", consequence="Most vertical optimization labels remain open-scope problems.", owner="vertical_method_owner", severity="blocking"),
    rec("gap.mca.independent_review", "typed_gap", missing="Independent mathematical-programming, CP, simulation, control, and uncertainty review of the predicates.", consequence="This remains a candidate contract, not a certified complete taxonomy.", owner="independent_appraisal_owner", severity="blocking"),
    rec("gap.mca.result_oracles", "typed_gap", missing="Cross-class independent solution/status/bound/optimality oracles and adversarial fixtures.", consequence="Provider outputs cannot be universally normalized or qualified.", owner="qualification_owner", severity="blocking"),
    rec("gap.mca.open_world", "typed_gap", missing="Evidence that the finite class and feature catalogue covers every future formalism.", consequence="Unknown formalisms must extend the registry, never be forced into the nearest name.", owner="corpus_steward", severity="permanent_open_world"),
]


UPSTREAM_FILES = {
    "compiler_metamodel": ROOT.parent / "compiler-metamodel.json",
    "operations_research_contexts": RESEARCH_ROOT / "domain_atlas/universes/operations_research/bounded-context-candidates.jsonl",
    "operations_research_methods": RESEARCH_ROOT / "domain_atlas/universes/operations_research/methods.jsonl",
    "predictive_ml_manifest": RESEARCH_ROOT / "domain_atlas/universes/predictive_ml_models/manifest.json",
    "model_agent_manifest": RESEARCH_ROOT / "domain_atlas/universes/model_agent_extension/manifest.json",
    "binder_examples": ROOT.parent / "binder_solver/examples.jsonl",
    "vertical_compositions": RESEARCH_ROOT / "product_ontology/composition_pilots/deterministic_verticals/vertical-compositions.jsonl",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


METAMODEL = {
    "metamodel_id": "metamodel.compiler.model_class_adjudication.v1",
    "edition": EDITION,
    "status": STATUS,
    "completion_claim": False,
    "purpose": "Deterministically derive or refuse mathematical/constraint/simulation/control model-class facets from a closed typed declaration before provider matching.",
    "inputs": ["closed_subproblem_declaration", "typed_feature_facts", "proof_receipts", "requested_claim_and_class", "external_vertical_blockers"],
    "outputs": ["matched_class_facets", "requested_class_disposition", "proof_gaps", "refusals", "provider_requirement_projection_input", "adjudication_trace"],
    "classification_shape": "multi_axis_nonexclusive_facets_with_sound_sufficient_predicates",
    "truth_values": ["proved", "refuted", "unknown", "not_applicable"],
    "constitutional_laws": [
        "business problem family, formal model class, transformation, algorithm, provider offer, target occurrence, result claim, and operational effect remain separate identities",
        "classification is multi-axis; stochastic, robust, staged, bilevel, simulation, and hybrid facets may refine a base formulation",
        "unknown expression, domain, geometry, uncertainty, time, or composition semantics fail closed for every class that needs them",
        "a more general solver's acceptance of an encoding does not make source and target model classes equivalent",
        "relaxation, linearization, discretization, surrogate replacement, scenario expansion, and encoding require equivalence or explicit loss receipts",
        "simulation evidence is not optimization proof and neither is proof that the real system matches the model",
        "a heuristic incumbent, local solution, or time-limited feasible result is not a global optimum",
        "provider documentation and executed tests do not establish vertical acceptance",
        "predictive/statistical fitted models are analytical artifacts, not agentic by default",
        "agent-based simulation entities are not LLM or tool-using agents by name",
        "generative models and tool agents may propose but cannot satisfy parsing, typing, classification, solving, validation, qualification, authorization, execution, or receipt obligations",
        "removing every generative/agent extension leaves the deterministic core and its artifacts valid",
        "an analytical result is a proposal until a separate authority creates an effect intent and an execution receipt",
    ],
    "upstream_snapshot_digests": {key: sha256(path) for key, path in UPSTREAM_FILES.items()},
}


CATALOGS = {
    "sources.jsonl": SOURCES,
    "classification-axes.jsonl": AXES,
    "feature-atoms.jsonl": FEATURE_ATOMS,
    "model-classes.jsonl": MODEL_CLASSES,
    "classification-rules.jsonl": CLASSIFICATION_RULES,
    "transformation-kinds.jsonl": TRANSFORMATIONS,
    "transformation-traces.jsonl": TRANSFORMATION_TRACES,
    "provider-requirements.jsonl": PROVIDER_REQUIREMENTS,
    "proof-obligations.jsonl": PROOF_OBLIGATIONS,
    "refusal-rules.jsonl": REFUSAL_RULES,
    "decision-points.jsonl": DECISION_POINTS,
    "automation-boundaries.jsonl": AUTOMATION_BOUNDARIES,
    "bounded-contexts.jsonl": CONTEXTS,
    "library-boundaries.jsonl": LIBRARIES,
    "classification-traces.jsonl": TRACES,
    "gaps.jsonl": GAPS,
}


def class_matches(row: dict, facts: set[str]) -> bool:
    predicate = row["sound_sufficient_predicate"]
    if not set(predicate["all_of"]).issubset(facts):
        return False
    if set(predicate["none_of"]) & facts:
        return False
    return all(set(group) & facts for group in predicate["any_of_groups"])


def adjudicate(trace_record: dict) -> dict:
    facts = set(trace_record["facts"])
    matched = sorted(row["id"] for row in MODEL_CLASSES if class_matches(row, facts))
    requested = set(trace_record["requested_class_refs"])
    missing_requested = sorted(requested - set(matched))
    blockers = sorted(trace_record.get("external_blockers", []))
    if missing_requested:
        disposition = "requested_class_refused"
    elif "refusal.mca.vertical_unaccepted" in blockers:
        disposition = "classified_but_vertical_unaccepted"
    else:
        disposition = "classified_not_provider_bound"
    return {
        "trace_ref": trace_record["id"],
        "matched_class_refs": matched,
        "missing_requested_class_refs": missing_requested,
        "external_blockers": blockers,
        "disposition": disposition,
        "provider_bindable": False,
    }


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_jsonl(path: Path, values: list[dict]) -> None:
    ordered = sorted(values, key=lambda row: row["id"])
    path.write_text("".join(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n" for row in ordered), encoding="utf-8")


def main() -> None:
    write_json(ROOT / "metamodel.json", METAMODEL)
    for filename, values in CATALOGS.items():
        write_jsonl(ROOT / filename, values)
    results = [adjudicate(row) for row in sorted(TRACES, key=lambda row: row["id"])]
    write_jsonl(ROOT / "adjudication-results.jsonl", [rec(f"result.{row['trace_ref']}", "adjudication_result", **row) for row in results])

    generated = ["metamodel.json", *CATALOGS.keys(), "adjudication-results.jsonl"]
    counts = {filename: sum(1 for line in (ROOT / filename).read_text(encoding="utf-8").splitlines() if line.strip()) for filename in CATALOGS}
    counts["adjudication-results.jsonl"] = len(results)
    manifest = {
        "bundle_id": "bundle.compiler.model_class_adjudication.v1",
        "edition": EDITION,
        "status": STATUS,
        "completion_claim": False,
        "generated_files": generated,
        "record_counts": counts,
        "file_sha256": {filename: sha256(ROOT / filename) for filename in generated},
        "upstream_snapshot_digests": METAMODEL["upstream_snapshot_digests"],
        "qualified_provider_offers": 0,
        "vertical_acceptance_receipts": 0,
    }
    write_json(ROOT / "manifest.json", manifest)


if __name__ == "__main__":
    main()
