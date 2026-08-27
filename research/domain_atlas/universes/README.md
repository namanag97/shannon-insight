# Open-world coverage universes

These registries prevent the bounded-context atlas from being designed around a small set of
familiar vendors, tables and BI metrics.

```text
Source-system universe
  x Data-type/observation/structure universe
  x Application-behavior universe (commands, queries, state, workflow, events, projections, effects)
  x Operation/algebra universe
  x Analytical-practice/method universe
  x Horizontal bounded-context atlas
  x Vertical enterprise/domain packs
```

## Completeness semantics

The universes are open. “Complete” cannot mean that every future vendor, formula or algorithm is
hard-coded. It means:

1. every encountered instance maps to a governed class or produces an explicit extension gap;
2. class identity, semantics and evidence are sufficient for deterministic compiler decisions;
3. extensions add records without adding compiler name branches;
4. unknown capability or meaning fails closed;
5. recurring independent audits do not reveal unowned semantic or operational behavior; and
6. the registry publishes current coverage, gaps, review date and evidence posture.

## Four record contracts

### Source system

```text
identity + family + logical models + objects + authority
+ read/write/change/discovery modes + time/order/finality
+ schema behavior + consistency/transaction boundary
+ security + limits + cost + hazards + verification
```

Concrete products and deployments are instances. A new vendor is not automatically a new source
class.

### Data type

```text
carrier representation
+ semantic value type
+ observation role
+ structural/modality algebra
+ vertical domain meaning
+ uncertainty/missingness/time/provenance qualifiers
```

These layers must not be collapsed into a database column type.

## Application behavior universe

Application behavior is a separate horizontal contract plane for enterprise applications. It
keeps commands/queries, aggregate state/transitions, workflow and saga coordination,
domain/integration events, projections, effect intents/receipts, and execution evidence distinct.
It imports data, persistence, dataflow, policy/authority, runtime, provenance and consumption
semantics without taking ownership of them. The candidate package is
`application_behavior/`; it has no qualified implementation or bindable offer and cannot be
promoted by schema validation alone.

### Operation

```text
stable operation identity + owning algebra/context
+ typed inputs/outputs + parameters + pre/postconditions
+ totality/partiality + determinism + idempotency
+ state/effects + information loss + complexity/budgets
+ batch/stream/incremental behavior + evidence + provider requirements
```

Operators such as `join`, `aggregate`, `resample`, `reproject`, `compact`, `publish` and `approve`
do not share one universal signature merely because they are all verbs.

### Analytical practice/type

```text
decision intent + study design + population/grain/time
+ method family + assumptions + data shape
+ output/uncertainty/evidence + decision proximity
+ lifecycle/latency/human role/privacy/domain portability
```

Named vertical applications are compositions over this record, not automatically new analytical
engines.

## Optional model/agent extension boundary

LLM, generative, prompt, RAG and agent-memory semantics are excluded from the **core dependency
graph**, not from the atlas. They occupy a separate extension namespace that imports deterministic
types, policies, tools, budgets, effects, evaluations and receipts from the core. Core records never
depend on the extension, and removing the extension cannot change a core domain meaning.

```text
core intent/types/laws/compiler/effect control
                       ^
                       | imports
        optional model/agent extension
                       |
                       v
      proposal/observation/draft/plan
                       |
          deterministic validation
                       |
        authority + effect execution
                       |
                    receipt
```

A model output is not automatically a fact, proof, decision or authorized command. Agentic
orchestration does not replace canonical-reference adjudication, binding, resource admission,
security enforcement, conformance testing or runtime receipts. Classical statistics, numerical
methods, optimization, process mining and governed statistical learning remain core analytical
methods.

## Honest inherited baseline

The prior corpus is useful but incomplete:

- 60 analytics types, not the prose-claimed 300;
- 56 source-system classes;
- 96 layered carrier/value/observation/structure/composite type records;
- 53 horizontal machines but no normalized operation registry; and
- analytics-machine coverage of 37 covered, 20 partial and 3 gap.

Run `audit_universes.py` to regenerate the authoritative baseline report.
