# Exact-scope CP-SAT provider execution

Status: **candidate executable protocol; retained executions are evidence, never qualification by themselves**.

This pilot tests one narrow provider-neutral model class against one exact provider occurrence:

```text
finite-domain scheduling/assignment need
  -> closed integer-only CP-SAT model class
     -> OR-Tools CP-SAT solver
        -> Python adapter
           -> ortools 9.15.6755 wheel and native members
              -> isolated target occurrence + fixed configuration
```

Every arrow is typed. The OR-Tools project name is not a provider offer, CP-SAT is not generic
constraint programming or MILP, and an executed result is not independent qualification or
business acceptance.

## What the protocol challenges

Ten deterministic fixtures cover:

- bounded integer-linear optimization;
- Boolean exactly-one and finite-domain all-different constraints;
- fixed intervals, precedence, no-overlap and makespan minimization;
- complete solution enumeration;
- canonical refusal of fractional coefficients and inverted domains;
- provider-side invalid-model handling; and
- preservation of `UNKNOWN` under a zero deterministic-work budget.

The oracle independently checks domains, constraints, interval identities, non-overlap, objective
values and enumeration count. `FEASIBLE` is not strengthened to `OPTIMAL`; `UNKNOWN` is not
strengthened to `INFEASIBLE`.

## Agent and predictive-model boundary

An LLM or tool-using agent may help turn declared intent into a candidate model. Its output enters
through an anti-corruption boundary as an untrusted proposal. The deterministic adapter, model
validator, solver, result checker, qualification policy and effect authority remain unchanged and
authoritative. Removing the optional agent extension leaves this entire execution path intact.

Predictive ML is a separate analytical-method family. A forecast may supply a versioned parameter
or scenario only when an explicit contract permits it; the fitted model is not an LLM agent and it
does not silently acquire scheduling, authorization or effect authority.

## Deliberate exclusions

The pilot does not establish support for arbitrary CP, MILP, SAT/SMT, optional intervals,
cumulative constraints, hints, assumptions, cores, proof certificates, parallel determinism,
performance, scalability, security, licensing, production fitness or any manufacturing vertical.
It cannot create a bindable or portable offer without independent appraisal, broader provider
qualification and separate vertical acceptance.

## Artifacts

- `protocol.json` — exact subject, profiles, fixtures, sources, exclusions and non-collapse laws.
- `provider_adapter.py` — isolated provider ACL and exact status mapping.
- `run_execution.py` — append-only executor, independent oracle and receipt generator.
- `validate_execution.py` — digest, semantic, receipt-contract and non-overclaim validator.
- `runs/<run-id>/` — immutable retained evidence for one attempt.

Run a new attempt with a unique identifier:

```sh
python3 research/domain_atlas/compiler/conformance_evaluation/executions/cp_sat_exact_scope/run_execution.py \
  --run-id <new-unique-run-id>
```

Validate one attempt or every retained attempt:

```sh
python3 research/domain_atlas/compiler/conformance_evaluation/executions/cp_sat_exact_scope/validate_execution.py \
  research/domain_atlas/compiler/conformance_evaluation/executions/cp_sat_exact_scope/runs/<run-id>

python3 research/domain_atlas/compiler/conformance_evaluation/executions/cp_sat_exact_scope/validate_execution.py
```

A passing validator proves internal consistency with this candidate protocol only. It does not
qualify the offer or authorize a schedule or operational effect.

## Retained falsification history

The first retained run, `run-20260826-cpsat-macos-arm64-python3_14-001`, failed the enumeration
profile: attaching a solution callback observed one solution, but the adapter had not carried the
declarative enumeration intent into CP-SAT's `enumerate_all_solutions` parameter. The run is kept
unchanged. It is evidence that callback presence is not enumeration semantics and that adapter
configuration is part of the exact offer. A subsequent run uses the corrected adapter; it does not
erase or overwrite the falsifying run.
