# Data ontology for composable analytics

## The correction

“Data type” has several meanings. Treating them as one flat list causes architectural errors.

```text
12.5
 |
 +-- carrier type: decimal(precision, scale)
 +-- semantic type: quantity | currency | probability | rate | score
 +-- observation role: measurement | outcome | cost | parameter
 +-- dataset structure: event log | time series | panel | cube
 `-- analytical use: describe | infer | forecast | optimize
```

The number is physically identical in every branch, but its valid operations, metadata,
uncertainty, aggregation, privacy, and interpretation differ.

## Canonical type stack

```text
L0  PHYSICAL LAYOUT
    bits, buffers, encoding, columnar representation
                     |
L1  CARRIER TYPE     v
    boolean, integer, decimal, text, timestamp, binary
                     |
L2  COMPOSITE TYPE   v
    optional, list, map, struct, union, key, reference, tensor
                     |
L3  SEMANTIC VALUE   v
    identifier, quantity, rate, probability, currency, status
                     |
L4  OBSERVATION      v
    entity, event, measurement, relationship, finding, decision
                     |
L5  STRUCTURE        v
    relation, event log, series, panel, graph, raster, ledger
                     |
L6  MACHINE          v
    validate, project, aggregate, infer, simulate, optimize
                     |
L7  ANALYTICS TYPE   v
    process discovery, experimentation, risk analytics
                     |
L8  DOMAIN PACK      v
    sports or oil vocabulary, rules, units, metrics, costs
                     |
L9  COMPOSITION      v
    wired machines, infrastructure, policies, and service levels
```

Only L3, L4, L8, and L9 are normally extended by a vertical domain. L0–L2 and L5–L7 are
horizontal platform contracts.

## Type equations

```text
FIELD TYPE =
    carrier
  × composites
  × semantic value type
  × qualifiers
  × missingness states
  × sensitivity
  × provenance obligation

DATASET TYPE =
    observation type
  × grain
  × keys
  × temporal model
  × analytical structure
  × update semantics
  × finality states
  × constraints

ANALYTICS REQUIREMENT =
    accepted input structures
  × required semantic roles
  × analytical machines
  × output structure
  × decision proximity
  × human role
  × execution properties

DOMAIN PACK =
    vocabulary
  + semantic refinements
  + observation contracts
  + units and calendars
  + metrics and aggregation rules
  + processes and state transitions
  + objectives, constraints, and costs
  + machine bindings
  + test fixtures
```

## The complete axis families

```text
MEANING
+-- carrier and composite type
+-- semantic value type
+-- measurement scale
+-- unit and dimension
`-- valid and invalid operations

OBSERVATION
+-- observation type
+-- subject and predicate
+-- observation unit
+-- grain and population
`-- collection mechanism

IDENTITY
+-- namespace and uniqueness scope
+-- identifier stability
+-- resolution policy
`-- reference integrity

TIME
+-- event time
+-- valid time
+-- system time
+-- processing time
+-- point versus interval
+-- calendar and timezone
+-- order, lateness and watermark
`-- revision policy

SPACE AND TOPOLOGY
+-- coordinate reference system
+-- vector, raster or trajectory
+-- topology, resolution and extent
+-- directionality and multiplicity
`-- relationship validity

MEASUREMENT QUALITY
+-- accuracy and precision
+-- resolution and calibration
+-- detection limit
+-- uncertainty
+-- quality flag
`-- measurement method

ABSENCE
+-- present
+-- not applicable
+-- not collected
+-- unknown
+-- withheld
+-- below detection
+-- structural zero
+-- censored
`-- not yet final

CAUSAL SEMANTICS
+-- treatment and outcome
+-- confounder and mediator
+-- instrument and effect modifier
+-- selection and collider
`-- negative control

UNCERTAINTY
+-- standard error
+-- confidence or credible interval
+-- prediction interval
+-- distribution
+-- scenario set
+-- bounds
`-- sensitivity range

CHANGE AND FINALITY
+-- append, upsert, correction, retraction
+-- snapshot, CDC, slowly changing dimension
`-- provisional, revised, final, superseded

PROVENANCE
+-- source, activity and responsible agent
+-- method and code version
+-- configuration and input versions
`-- generation time and derivation

GOVERNANCE
+-- owner and steward
+-- classification and purpose
+-- consent and lawful basis
+-- retention and residency
+-- access and minimum-group policy
`-- release policy

COMPUTATION
+-- batch or stream
+-- latency and ordering
+-- statefulness and determinism
+-- incrementality and partitioning
+-- resource profile
`-- failure semantics
```

## Non-negotiable distinctions

```text
identifier  != number
label       != identifier
null        != reason for missingness
zero        != missing
score       != probability
rate        != raw count
currency    != bare decimal
duration    != calendar interval
event time  != system time
valid time  != processing time
correction  != silent overwrite
association != causation
dataset row != declared grain
dashboard   != semantic model
SQL text    != portable logical plan
```

## Domain swap example

```text
                        SHARED HORIZONTAL TYPE SYSTEM
                       carrier.decimal + semantic.quantity
                                      |
              +-----------------------+-----------------------+
              |                                               |
        SPORTS DOMAIN                                    OIL DOMAIN
        player load                                      production volume
        quantity kind: force/time                        quantity kind: volume
        unit: N or s                                     unit: m3 or barrel
        grain: player/session                            grain: well/day
        calendar: competition                            calendar: production
        source: wearable/procedure                       source: meter/allocation
              |                                               |
              +-----------------------+-----------------------+
                                      |
                    contract -> normalize -> aggregate
                         -> metric -> diagnose -> decide
```

The algorithms remain unchanged. Domain meaning changes through typed qualifiers and bindings.

## Extension rule

A new domain-specific type is not accepted merely because it has a new name. It must declare a
canonical parent, carriers, qualifiers, permitted operations, prohibited inferences, version,
owner, sources, compatibility policy, and test fixtures. If it cannot do this, it is vocabulary,
not a machine-usable type.
