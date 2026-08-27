# Composable analytics domain model

This is the platform-facing layer of the research catalogue. It models analytics as a typed
composition graph, not as a list of vendor features.

## The decomposition

```text
platform = horizontal machines + vertical domain pack + deployment profile

horizontal machine = implementation + typed ports + deterministic contract + configuration
vertical domain pack = vocabulary + data contracts + metrics + rules + parameters + costs
deployment profile = selected machines + bindings + wiring + service-level objectives
```

The horizontal axis is reusable across industries. The vertical axis contains all meaning that
changes when sports is replaced by oil and gas. A horizontal machine may refer to abstract roles
such as `asset`, `event`, `quantity`, `location`, and `interval`; it must never contain concepts
such as `player`, `shot`, `well`, or `barrel`.

## Files

- `composition.schema.json` — structural schema for registries, domain packs, and compositions.
- `horizontal_registry.json` — reusable machine and library boundaries.
- `domain_packs/sports.json` — sports semantics and bindings.
- `domain_packs/oil_and_gas.json` — oil-and-gas semantics and bindings.
- `platform_examples.json` — two compositions using the same horizontal machines.
- `analytics_type_machine_map.json` — honest covered/partial/gap mapping for all researched types.
- `validate_composition.py` — schema-independent referential and wiring validator.

## Why this model

The atomic reusable unit is a **machine**, with input and output ports. A **library** groups
machines that share implementation dependencies, but it is not the unit of composition. Data is
split into immutable contracts, replaceable domain assets, and runtime datasets. Wiring is a DAG
of port-to-port edges. Configuration is split into four scopes so customization cannot leak:

1. machine defaults — domain-neutral execution choices;
2. domain bindings — vocabulary, metrics, rules, units, costs, and parameters;
3. composition overrides — use-case choices;
4. runtime secrets/state — referenced, never embedded in a domain pack.

## Boundary test

A horizontal component is correctly bounded when the sports composition can be changed to oil
and gas by replacing the domain pack and bindings while leaving every machine definition intact.
The validator enforces port types, dependency declarations, acyclic wiring, required assets, and
the absence of vertical terms in horizontal definitions.

## Validate

```bash
python3 research/analytics_landscape/composition/validate_composition.py
```

This is a horizontal seed, not a claim of exhaustive implementation coverage. Each `coverage`
field records the remaining decomposition work explicitly.
