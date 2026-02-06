# Registry: Scales

The seven levels of granularity. Each dimension (see `dimensions.md`) is measured at one or more of these scales. They form a strict containment hierarchy: every entity at scale S(n) is composed of entities at scale S(n-1).

## S0: TOKEN

The atom. Individual characters, keywords, identifiers, literals, operators.

**Entity**: A single lexical token.
**Example SIZE measurement**: Character count.
**Example INFORMATION measurement**: Surprise (contextual information per token).
**Emergent properties**: None (atomic).

---

## S1: STATEMENT

A single instruction.

**Entity**: One executable statement or declaration.
**Example SIZE measurement**: Token count.
**Example REFERENCE measurement**: Variables used.
**Emergent properties**: None beyond token composition.

---

## S2: FUNCTION

A named computation.

**Entity**: Function, method, lambda, closure.
**Example SIZE measurement**: Parameters, body tokens, lines.
**Example REFERENCE measurement**: Calls made, variables read/written.
**Emergent properties**: Cyclomatic complexity (SHAPE), nesting depth (SHAPE), call targets (REFERENCE).

---

## S3: CLASS

Functions + shared state.

**Entity**: Class, struct, trait, interface.
**Example SIZE measurement**: Methods, fields.
**Example REFERENCE measurement**: Base classes, composed types.
**Emergent properties**: Inheritance depth (SHAPE), method size distribution (SHAPE).

---

## S4: FILE

A compilation unit. **This is the primary scale for most analysis.**

**Entity**: Source file.
**Example SIZE measurement**: Functions, LOC, classes.
**Example REFERENCE measurement**: Imports, exports.
**Emergent properties**: Import graph position (REFERENCE), bus factor (AUTHORSHIP), churn trajectory (CHANGE), fix ratio (INTENT). Most signals in `signals.md` operate at this scale.

---

## S5: MODULE

A directory / package of files.

**Entity**: Directory, Go package, Python package, npm workspace.
**Example SIZE measurement**: File count, total LOC.
**Example REFERENCE measurement**: Inter-module edges, cohesion, coupling.
**Emergent properties**: Cohesion/coupling (derived from REFERENCE), knowledge Gini (AUTHORSHIP), velocity (CHANGE), instability/abstractness (REFERENCE via Martin's metrics). Module detection rules defined in `modules/architecture/module-detection.md`.

---

## S6: CODEBASE

The entire system.

**Entity**: The whole project (or monorepo workspace).
**Example SIZE measurement**: Modules, total files.
**Example REFERENCE measurement**: Dependency graph topology, modularity.
**Emergent properties**: Architectural pattern (SHAPE), global bus factor (AUTHORSHIP), codebase health (composite). These are the "one number" summaries.

---

## Scale Inheritance

Each scale inherits from the one below via aggregation:

```
File SIZE = Σ function SIZE
Module SHAPE = arrangement of file SHAPE values
Codebase REFERENCE = topology of module REFERENCE edges
```

But each scale also has **emergent properties** not present below:
- FUNCTION has cyclomatic complexity — a STATEMENT does not
- FILE has import graph position — a FUNCTION within a file does not
- MODULE has cohesion/coupling — a single FILE does not
- CODEBASE has architectural pattern — no single MODULE has this

## Aggregation Operators

When lifting a signal from scale S(n) to S(n+1):

| Operator | When to use | Example |
|---|---|---|
| **sum** | Additive quantities | module.lines = Σ file.lines |
| **mean** | Intensity measures | module.cognitive_load = mean(file.cognitive_load) |
| **max** | Worst-case concerns | module.max_nesting = max(file.max_nesting) |
| **min** | Weakest-link concerns | module.bus_factor = min(critical_file.bus_factor) |
| **gini** | Distribution shape | module.size_gini = gini(file.lines) |
| **entropy** | Diversity/concentration | module.role_entropy = H(file.role distribution) |

Each signal in `signals.md` that exists at multiple scales specifies its aggregation operator.
