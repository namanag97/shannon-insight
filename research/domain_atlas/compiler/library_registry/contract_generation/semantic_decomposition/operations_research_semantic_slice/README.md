# Operations research semantic slice

This generated research package decomposes deterministic operations research into independently
owned decision, optimization, heuristic, infeasibility, queueing, simulation, validation,
certificate and finding-handoff semantics. It binds every current `library.operations_research.*`
library plus the operations-research method bridge to the live 16-axis control plane.

The central boundary is deliberately not “an optimizer.” A compiler must preserve the sequence
`decision → policy/objective → model → capability → execution → result → validation → finding`,
and must keep queueing and simulation formalisms distinct. Solver status is not validation,
feasibility is not optimality, a timeout is not infeasibility, simulation verification is not
validation, and a result is not authority to act.

The current graph declares `product.optimization_solver` and `product.simulation_environment`.
Five queueing libraries, shared decision semantics, and the composition bridge have no declared
product consumer. The package records this as a boundary question rather than manufacturing a
queueing product or inferring use from names.

All semantic modules, laws, methods, expert lessons, innovations, bindings, axis questions and
product/capability findings are evidence-backed candidates. Owner ratification, exact contracts,
implementations, qualification, compiler binding and canonical gap closure remain zero.

Regenerate and validate:

```sh
python3 build_operations_research_semantic_slice.py
python3 validate.py
```
