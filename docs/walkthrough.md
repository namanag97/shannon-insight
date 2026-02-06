# Shannon Insight — End-to-End Walkthrough

How the framework actually works, traced through a concrete example.

---

## The Example Codebase

A small e-commerce backend. 18 files, built partly by AI, partly by hand:

```
src/
├── main.py              ← entry point
├── config.py            ← settings
├── models/
│   ├── user.py          ← User dataclass
│   ├── product.py       ← Product dataclass
│   └── order.py         ← Order dataclass
├── services/
│   ├── auth.py          ← authentication (heavily used, 1 author)
│   ├── cart.py          ← shopping cart (AI-generated, half stubs)
│   ├── payment.py       ← payment processing
│   └── shipping.py      ← shipping calculator (AI-generated, orphan)
├── api/
│   ├── routes.py        ← Flask routes (imports everything)
│   └── middleware.py    ← auth middleware
├── utils/
│   ├── validators.py    ← input validation
│   ├── cache.py         ← caching layer (imports from services — wrong direction!)
│   └── email.py         ← email sending (AI-generated, phantom imports)
├── db/
│   ├── connection.py    ← DB pool
│   └── queries.py       ← SQL queries
└── tests/
    └── test_auth.py     ← only test file
```

---

## Step 1: The User Runs the Command

```bash
$ shannon-insight -C src/ --save --verbose
```

The kernel activates. Here's what happens inside.

---

## Step 2: IR0 — FileSystem

**What happens:** Walk the directory, read every file, hash contents.

```
IR0 Output (18 entries):

  path                    size    hash        language
  ─────────────────────── ─────── ─────────── ────────
  main.py                 342     a1b2c3...   python
  config.py               218     d4e5f6...   python
  models/user.py          485     g7h8i9...   python
  models/product.py       512     j0k1l2...   python
  models/order.py         1,847   m3n4o5...   python
  services/auth.py        2,341   p6q7r8...   python
  services/cart.py        1,102   s9t0u1...   python
  services/payment.py     1,678   v2w3x4...   python
  services/shipping.py    894     y5z6a7...   python
  api/routes.py           2,890   b8c9d0...   python
  api/middleware.py        567    e1f2g3...   python
  utils/validators.py     723     h4i5j6...   python
  utils/cache.py          445     k7l8m9...   python
  utils/email.py          612     n0o1p2...   python
  db/connection.py        389     q3r4s5...   python
  db/queries.py           1,234   t6u7v8...   python
  tests/test_auth.py      567     w9x0y1...   python
```

**Time:** ~50ms. Just filesystem operations.

**What the user sees:** Nothing yet. This is internal.

---

## Step 3: IR1 — SyntacticForm

**What happens:** Parse each file's AST. Extract functions, classes, imports, calls.

Let's trace three interesting files:

### services/auth.py (the hub)

```
IR1 for auth.py:

  functions:
    ┌─────────────────┬────────┬───────┬────────┬───────────────────────────┐
    │ name            │ params │ body  │ sig    │ calls                     │
    │                 │        │ tok   │ tok    │                           │
    ├─────────────────┼────────┼───────┼────────┼───────────────────────────┤
    │ authenticate    │ 3      │ 147   │ 12     │ db.query, hash_pw, Token  │
    │ refresh_token   │ 1      │ 89    │ 8      │ db.query, Token.verify    │
    │ create_user     │ 2      │ 112   │ 10     │ db.query, hash_pw, email  │
    │ hash_pw         │ 1      │ 34    │ 6      │ bcrypt.hashpw             │
    │ verify_email    │ 1      │ 67    │ 7      │ db.query, email.send      │
    └─────────────────┴────────┴───────┴────────┴───────────────────────────┘

  imports:
    models.user.User         → resolved: models/user.py
    db.queries.get_user      → resolved: db/queries.py
    utils.email.send_email   → resolved: utils/email.py
    bcrypt                   → external, installed: yes

  classes: none
```

All functions have real implementations. body_tokens >> signature_tokens. Healthy.

### services/cart.py (the AI-generated stub file)

```
IR1 for cart.py:

  functions:
    ┌─────────────────┬────────┬───────┬────────┬───────────────────────────┐
    │ name            │ params │ body  │ sig    │ calls                     │
    │                 │        │ tok   │ tok    │                           │
    ├─────────────────┼────────┼───────┼────────┼───────────────────────────┤
    │ add_to_cart     │ 3      │ 78    │ 11     │ db.query, Product.get     │
    │ remove_from_cart│ 2      │ 3     │ 9      │ (none — just "pass")      │
    │ get_cart        │ 1      │ 4     │ 7      │ (none — returns [])       │
    │ apply_coupon    │ 2      │ 2     │ 9      │ (none — just "pass")      │
    │ checkout        │ 1      │ 3     │ 7      │ (none — just "...")       │
    └─────────────────┴────────┴───────┴────────┴───────────────────────────┘

  imports:
    models.product.Product   → resolved: models/product.py
    models.order.Order       → resolved: models/order.py
    services.payment         → resolved: services/payment.py
    db.queries               → resolved: db/queries.py
```

One function implemented, four are stubs. Classic AI generation pattern.

### utils/email.py (the phantom import file)

```
IR1 for email.py:

  functions:
    ┌─────────────────┬────────┬───────┬────────┬───────────────────────────┐
    │ name            │ params │ body  │ sig    │ calls                     │
    ├─────────────────┼────────┼───────┼────────┼───────────────────────────┤
    │ send_email      │ 3      │ 45    │ 11     │ EmailClient.send          │
    │ send_bulk       │ 2      │ 38    │ 9      │ EmailClient.batch         │
    │ format_template │ 2      │ 22    │ 8      │ jinja2.render             │
    └─────────────────┴────────┴───────┴────────┴───────────────────────────┘

  imports:
    utils.email_client.EmailClient  → resolved: NULL ← PHANTOM!
    jinja2                          → external, installed: no ← PHANTOM!
    config.EMAIL_SETTINGS           → resolved: config.py
```

Two phantom imports. The AI generated code that references modules that don't exist.

**Time:** ~200ms for 18 files.

---

## Step 4: IR2 — SemanticForm

**What happens:** Classify roles, extract concepts, measure completeness.

### services/auth.py

```
IR2 for auth.py:

  role:       SERVICE    (has functions with state access, imports models + DB)

  concepts:
    ┌───────────┬──────────────────────────────────────────────┬────────┐
    │ topic     │ tokens                                       │ weight │
    ├───────────┼──────────────────────────────────────────────┼────────┤
    │ auth      │ authenticate, token, verify, password, hash  │ 0.55   │
    │ user_mgmt │ create, user, email, profile                 │ 0.30   │
    │ email     │ email, send, verify_email                    │ 0.15   │
    └───────────┴──────────────────────────────────────────────┴────────┘

  concept_entropy: H = 1.40  (3 concepts — slightly unfocused)
  naming_drift:    0.12      (filename "auth" matches dominant concept — good)

  public_api:    [authenticate, refresh_token, create_user, verify_email]
  consumed_api:  [{db/queries.py: [get_user, save_user]},
                  {utils/email.py: [send_email]},
                  {models/user.py: [User]}]

  completeness:
    stub_ratio:         0.0    (all functions implemented)
    implementation_gini: 0.31  (moderate variation — healthy)
    todo_density:        0.0
```

### services/cart.py

```
IR2 for cart.py:

  role:       SERVICE

  concepts:
    ┌───────────┬────────────────────────────────────┬────────┐
    │ topic     │ tokens                             │ weight │
    ├───────────┼────────────────────────────────────┼────────┤
    │ cart      │ cart, add, remove, get, checkout    │ 0.80   │
    │ pricing   │ coupon, apply, discount             │ 0.20   │
    └───────────┴────────────────────────────────────┴────────┘

  concept_entropy: H = 0.72   (fairly focused — good)
  naming_drift:    0.08       (filename matches — good)

  completeness:
    stub_ratio:         0.80  ← RED FLAG: 4/5 functions are stubs
    implementation_gini: 0.89 ← RED FLAG: one function has all the logic
    todo_density:        0.0   (AI didn't even leave TODOs)
```

### services/shipping.py

```
IR2 for shipping.py:

  role:       SERVICE

  concepts:
    ┌───────────┬────────────────────────────────────┬────────┐
    │ topic     │ tokens                             │ weight │
    ├───────────┼────────────────────────────────────┼────────┤
    │ shipping  │ calculate, rate, weight, zone      │ 1.00   │
    └───────────┴────────────────────────────────────┴────────┘

  concept_entropy: H = 0.0    (perfectly focused)
  naming_drift:    0.05

  completeness:
    stub_ratio:    0.0         (all implemented)
    impl_gini:     0.22        (even implementation)
```

Shipping looks great in isolation. But nobody imports it. That'll show up in IR3.

**Time:** ~100ms.

---

## Step 5: IR3 — RelationshipGraph

**What happens:** Build the dependency graph. Compute centrality, cycles, blast radius, depth, phantoms.

### The Graph

```
                                    ┌──────────┐
                                    │ main.py  │ depth=0 (entry point)
                                    └────┬─────┘
                                         │
                                    ┌────▼─────┐
                                    │api/routes│ depth=1
                                    └──┬──┬──┬─┘
                         ┌─────────────┘  │  └─────────────────┐
                         ▼                ▼                     ▼
                   ┌───────────┐  ┌─────────────┐      ┌──────────────┐
                   │services/  │  │api/         │      │services/     │
                   │auth       │  │middleware   │      │payment       │
                   │depth=2    │  │depth=2      │      │depth=2       │
                   └──┬──┬──┬──┘  └──────┬──────┘      └──────┬───────┘
                      │  │  │            │                     │
            ┌─────────┘  │  └──────┐     │                     │
            ▼            ▼         ▼     │                     ▼
      ┌──────────┐ ┌──────────┐ ┌─┴─────┴──┐          ┌──────────┐
      │models/   │ │db/       │ │utils/     │          │models/   │
      │user      │ │queries   │ │validators │          │order     │
      │depth=3   │ │depth=3   │ │depth=3    │          │depth=3   │
      └──────────┘ └────┬─────┘ └───────────┘          └──────────┘
                        │
                   ┌────▼─────┐
                   │db/       │
                   │connection│
                   │depth=4   │
                   └──────────┘

      ┌────────────┐         ┌─────────────┐
      │services/   │         │utils/       │
      │cart        │ depth=2 │cache        │ depth=? (cycle!)
      └──┬──┬──────┘         └──┬──────────┘
         │  │                    │
         │  ▼                    ▼
         │ models/product   services/auth ← BACKWARD! utils importing services
         ▼
       models/order
       services/payment

   ╔══════════════════╗     ╔══════════════════╗
   ║ services/shipping║     ║ utils/email      ║
   ║ ORPHAN (depth=∞) ║     ║ has PHANTOMS     ║
   ║ nobody imports it║     ║ depth=3          ║
   ╚══════════════════╝     ╚══════════════════╝
```

### Computed Metrics

```
                        PageRank  In-deg  Blast   Depth  Orphan?
                        ────────  ──────  ──────  ─────  ───────
main.py                 0.031     0       0       0      no (entry)
api/routes.py           0.042     1       1       1      no
services/auth.py        0.147     3       5       2      no      ← HIGHEST
services/cart.py        0.038     1       1       2      no
services/payment.py     0.068     2       3       2      no
services/shipping.py    0.031     0       0       ∞      YES     ← ORPHAN
api/middleware.py        0.042    1       1       2      no
models/user.py          0.092     2       6       3      no
models/product.py       0.054     1       2       3      no
models/order.py         0.068     2       3       3      no
utils/validators.py     0.054     2       3       3      no
utils/cache.py          0.038     0       0       -      no (but has backward edge)
utils/email.py          0.054     1       2       3      no
db/queries.py           0.092     3       5       3      no
db/connection.py        0.054     1       4       4      no
config.py               0.042     1       2       -      no

Phantoms:     2 (utils/email.py → email_client, jinja2)
Orphans:      1 (services/shipping.py)
SCCs:         0 (utils/cache → services/auth is one-directional, not a cycle)
Modularity:   Q = 0.38
Fiedler:      λ₂ = 0.42
Orphan ratio: 1/17 = 0.059
Phantom ratio: 2/24 = 0.083

Centrality Gini: 0.48  (auth.py and db/queries.py dominate — moderate concentration)
```

### Distance Spaces (for interesting pairs)

```
Pair: services/auth.py ↔ utils/cache.py

  d_dependency:  1 (cache imports auth — close)
  d_semantic:    0.82 (completely different concepts — FAR)
  d_author:      0.90 (different authors — FAR)
  d_cochange:    0.15 (often change together — close)

  DISAGREEMENT: dependency says CLOSE, but semantics says FAR
  → ACCIDENTAL COUPLING (cache depends on auth but they're unrelated concepts)

  ALSO: cache is in utils/ but imports from services/
  → LAYER VIOLATION
```

```
Pair: services/auth.py ↔ services/payment.py

  d_dependency:  ∞ (no import between them)
  d_cochange:    0.10 (always change in same commits — very close)
  d_semantic:    0.45 (moderate concept overlap — both deal with "user" + "transaction")

  DISAGREEMENT: cochange says CLOSE, dependency says FAR
  → HIDDEN COUPLING (they always change together but there's no import)
```

```
Pair: services/shipping.py ↔ everything

  d_dependency:  ∞ to everything (orphan)
  d_semantic:    0.3 to services/cart.py (both deal with "order" concepts)

  DISAGREEMENT: semantics says CLOSE to cart, but dependency says completely disconnected
  → ORPHAN WITH SEMANTIC NEIGHBOR (shipping should probably be imported by cart)
```

**Time:** ~300ms for graph construction + algorithms.

---

## Step 6: IR4 — ArchitecturalModel

**What happens:** Collapse file graph to module graph. Infer layers. Detect violations.

### Module Graph

```
                ┌────────┐
    Layer 0     │  db/   │  Ca=5, Ce=0, I=0.0 (completely stable)
                └────┬───┘
                     │
                ┌────▼───┐   ┌──────────┐
    Layer 1     │models/ │   │ config   │
                └────┬───┘   └────┬─────┘
                     │            │
         ┌───────────┼────────────┘
         │           │
    ┌────▼───┐  ┌────▼──────┐
    │services│  │  utils/   │──→ services/ ← VIOLATION!
    │        │  │           │
    Layer 2  │  └───────────┘
    └────┬───┘   Layer 2 (should be layer 1, but backward edge)
         │
    ┌────▼───┐
    │  api/  │
    Layer 3  │
    └────┬───┘
         │
    ┌────▼───┐
    │ main   │
    Layer 4  │
    └────────┘
```

### Module Metrics

```
Module          Files  Cohesion  Coupling  I      A      D      Alignment  Role
──────          ─────  ────────  ────────  ─────  ─────  ─────  ─────────  ────
db/             2      1.00      0.38      0.00   0.00   1.00   1.00       INFRA
models/         3      0.00      0.55      0.00   0.80   0.20   1.00       MODEL
services/       4      0.08      0.52      0.62   0.00   0.38   0.75       SERVICE
utils/          3      0.00      0.71      0.71   0.00   0.29   0.67       UTILITY
api/            2      0.50      0.60      1.00   0.00   0.00   1.00       CLI
```

Observations:
- `db/` has D=1.0 (zone of pain: concrete and stable — everyone depends on it, hard to change)
- `services/` has low cohesion (0.08) — the files barely import each other
- `utils/` has 0.00 cohesion AND a backward edge to services/ — it's not really a utility layer
- `models/` has high abstractness (0.80) and low instability — good, on the main sequence

### Violations

```
Violation #1:
  utils/cache.py → services/auth.py
  Layer 2 → Layer 2 (lateral, but utils SHOULD be Layer 1)
  Type: BACKWARD (utility importing a service)
  Impact: 1 edge, symbols: [get_current_user]

Violation #2:
  tests/ not importing shipping.py
  (Not a violation per se, but contributes to the orphan problem)
```

### Architecture Patterns

```
is_layered:     YES (clear ordering exists, 1 violation)
is_modular:     PARTIAL (Q=0.38, some modules have low cohesion)
has_god_module: NO (no module owns >40% of edges)
hub_and_spoke:  YES (api/routes.py is the hub)

Architecture health: 0.62
```

**Time:** ~50ms (module-level computation is cheap).

---

## Step 7: IR5t — TemporalModel (parallel with IR0→IR4)

**What happens:** Parse git log. Compute churn, co-change, author distribution.

```
Git history: 127 commits over 4 months, 3 authors

Per-file temporal:

File                  Changes  Trajectory    Bus   Authors        Fix%
────                  ───────  ──────────    ───   ───────        ────
services/auth.py      47       CHURNING      1     alice(100%)    38%  ← BAD: 1 author, high fix%
services/cart.py      3        DORMANT       1     bot(100%)      0%   ← AI-generated, barely touched
services/payment.py   28       STABILIZING   2     alice,bob      21%
api/routes.py         35       CHURNING      2     alice,bob      31%
models/order.py       22       SPIKING       1     alice(100%)    45%  ← BAD: spiking + all fixes
db/queries.py         31       STABLE        2     alice,bob      16%
services/shipping.py  1        DORMANT       1     bot(100%)      0%   ← AI-generated, never touched
utils/email.py        2        DORMANT       1     bot(100%)      0%   ← AI-generated
```

### Co-change pairs

```
Pair                              CoΔ   Lift   Conf   Structural edge?
──────────────────────────────    ────  ─────  ─────  ────────────────
auth.py ↔ payment.py             18    3.2    0.72   NO  ← HIDDEN COUPLING
auth.py ↔ routes.py              22    2.1    0.58   YES (expected)
auth.py ↔ models/order.py        15    2.8    0.64   NO  ← HIDDEN COUPLING
routes.py ↔ middleware.py         19    3.5    0.79   YES (expected)
queries.py ↔ connection.py        12    2.4    0.52   YES (expected)
```

**Time:** ~400ms (git log parsing dominates).

---

## Step 8: IR5s — Signal Fusion

**What happens:** Combine all signals from IR1-IR5t into percentile-normalized scores.

### Per-file signal vector (showing 4 key files)

```
                         auth.py    cart.py    shipping.py  email.py
                         ────────   ────────   ───────────  ────────
D1 SIZE
  lines                  P82        P48        P35          P41
  function_count         P76        P76        P29          P53

D2 SHAPE
  max_nesting            P71        P24        P41          P35
  impl_gini              P41        P94 ←!!    P24          P35

D3 NAMING
  concept_count          P71        P41        P6           P41
  naming_drift           P18        P12        P6           P24

D4 REFERENCE
  pagerank               P94 ←!!    P35        P6           P47
  blast_radius           P88 ←!!    P24        P6           P35
  is_orphan              no         no         YES ←!!      no
  phantom_count          0          0          0            2 ←!!

D5 INFORMATION
  compression            P59        P24        P47          P41
  coherence              P53        P65        P94          P59
  cognitive_load         P82        P35        P24          P29

D6 CHANGE
  total_changes          P94 ←!!    P12        P6           P12
  churn_trajectory       CHURNING   DORMANT    DORMANT      DORMANT

D7 AUTHORSHIP
  bus_factor             1          1          1            1
  author_entropy         P6 ←!!     P6         P6           P6

D8 INTENT
  fix_ratio              P88 ←!!    P6         P6           P6

COMPOSITES
  risk_score             0.87 ←!!   0.18       0.04         0.31
  wiring_quality         0.92       0.35 ←!!   0.10 ←!!     0.28 ←!!
```

### Reading the vectors

**auth.py** — the dangerous hub:
```
High on: pagerank(P94), blast_radius(P88), changes(P94), fix_ratio(P88)
Low on: bus_factor(1), author_entropy(P6)
= Central file, constantly changing, mostly bug fixes, only one person understands it
= HIGH RISK HUB + KNOWLEDGE SILO
```

**cart.py** — the AI stub file:
```
High on: impl_gini(P94) — one function implemented, four stubs
Low on: changes(P12), cognitive_load(P35)
= Looks simple, but 80% is unimplemented
= HOLLOW CODE
```

**shipping.py** — the orphan:
```
Low on everything: pagerank(P6), blast_radius(P6), changes(P6)
is_orphan: YES
= Nobody uses it. It was generated and forgotten.
= ORPHAN CODE
```

**email.py** — the phantom:
```
phantom_count: 2
= References modules that don't exist
= PHANTOM IMPORTS
```

### Anomaly Detection (Mahalanobis distance)

```
File                  d_Mahalanobis  Anomalous?
────                  ─────────────  ──────────
services/auth.py      3.21           YES (extreme multi-dimensional outlier)
services/cart.py      2.87           YES (stub pattern unusual)
services/shipping.py  2.45           YES (orphan pattern unusual)
utils/cache.py        2.12           BORDERLINE (weird position — util importing service)
models/order.py       1.89           NO (within normal range)
...most files...      0.5-1.5        NO
```

### Codebase-Level Signals

```
Global signals:
  modularity:          0.38 (decent)
  fiedler_value:       0.42 (moderate connectivity)
  orphan_ratio:        0.059 (1 file)
  phantom_ratio:       0.083 (2 edges)
  glue_deficit:        0.29 (some composition missing)
  centrality_gini:     0.48 (moderate hub concentration)
  wiring_score:        0.71 (some AI quality issues)
  architecture_health: 0.62 (one layer violation, mixed cohesion)
  I(struct; change):   0.31 (changes partially respect modules)
  codebase_health:     0.58
```

### Health Scalar Field

```
File                 h(f)    Δh (health Laplacian)    Interpretation
────                 ────    ─────────────────────    ──────────────
db/connection.py     0.85    -0.12                    Healthy, neighbors slightly worse (normal for foundation)
models/user.py       0.78    +0.05                    Slightly worse than neighbors (auth.py drags it down)
services/auth.py     0.13    +0.52 ←!!                MUCH worse than all neighbors — THE WEAK LINK
services/cart.py     0.35    +0.18                    Worse than neighbors (stubs drag it down)
api/routes.py        0.41    -0.08                    About same as neighbors
utils/cache.py       0.48    +0.22                    Worse than neighbors (layer violation + poor position)
```

auth.py has Δh = +0.52 — it's dramatically unhealthier than everything around it. It's the single point dragging down the neighborhood.

**Time:** ~50ms for fusion.

---

## Step 9: IR6 — Insights

**What happens:** Evaluate all finding predicates against the signal field. Build evidence chains.

### Finding #1: HIGH RISK HUB

```
╔══════════════════════════════════════════════════════════════╗
║  HIGH RISK HUB                    Severity: 0.92            ║
║  services/auth.py                 Confidence: 0.88          ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  Evidence:                                                   ║
║                                                              ║
║  [IR3] PageRank: 0.147 (P94)                                ║
║        3 files import this directly, 5 affected transitively ║
║                                                              ║
║  [IR3] Blast radius: 5 files                                ║
║        Changes here can break: routes, middleware, cache,    ║
║        email, and transitively main.py                       ║
║                                                              ║
║  [IR5t] 47 changes in 4 months (P94), trajectory: CHURNING  ║
║         No sign of stabilization                             ║
║                                                              ║
║  [IR5t] Fix ratio: 38% — nearly half of all changes are     ║
║         bug fixes                                            ║
║                                                              ║
║  [IR2] 3 concepts (auth, user_mgmt, email) — slightly       ║
║        unfocused for a critical file                         ║
║                                                              ║
║  [IR5t] Bus factor: 1 (alice only)                           ║
║         Single point of knowledge failure                    ║
║                                                              ║
║  [Health] Δh = +0.52 — weakest link in its neighborhood     ║
║                                                              ║
║  Suggestion: Split auth logic from user management.          ║
║  Move verify_email to a dedicated notification service.      ║
║  Pair-program to spread knowledge beyond alice.              ║
║                                                              ║
║  Effort: HIGH    Impact: 0.31 health improvement             ║
╚══════════════════════════════════════════════════════════════╝
```

### Finding #2: HOLLOW CODE (AI stubs)

```
╔══════════════════════════════════════════════════════════════╗
║  HOLLOW CODE                      Severity: 0.71            ║
║  services/cart.py                 Confidence: 0.95           ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  Evidence:                                                   ║
║                                                              ║
║  [IR1] 4 of 5 functions are stubs (body < 5 tokens)         ║
║        remove_from_cart: "pass"                              ║
║        get_cart: "return []"                                 ║
║        apply_coupon: "pass"                                  ║
║        checkout: "..."                                       ║
║                                                              ║
║  [IR2] Stub ratio: 0.80                                     ║
║        Implementation Gini: 0.89 (extremely uneven)          ║
║        One function has all the logic, rest are shells        ║
║                                                              ║
║  [IR5t] Only 3 commits, all by bot — AI-generated            ║
║         No human has reviewed or extended this code           ║
║                                                              ║
║  Suggestion: Implement checkout flow (highest business       ║
║  value). get_cart and remove_from_cart are likely needed      ║
║  for checkout to work. apply_coupon can wait.                ║
║                                                              ║
║  Effort: MEDIUM    Impact: 0.08 health improvement           ║
╚══════════════════════════════════════════════════════════════╝
```

### Finding #3: ORPHAN CODE

```
╔══════════════════════════════════════════════════════════════╗
║  ORPHAN CODE                      Severity: 0.55            ║
║  services/shipping.py             Confidence: 0.99           ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  Evidence:                                                   ║
║                                                              ║
║  [IR3] In-degree: 0 — no file imports this                   ║
║        Not an entry point or test file                       ║
║        Unreachable from main.py (depth = ∞)                  ║
║                                                              ║
║  [IR2] Role: SERVICE — this should be imported somewhere     ║
║                                                              ║
║  [G6 distance] d_semantic to cart.py = 0.3 (close)           ║
║        shipping and cart share "order" vocabulary             ║
║        Likely intended to be used by cart's checkout flow     ║
║                                                              ║
║  [IR5t] 1 commit by bot — AI-generated, never integrated     ║
║                                                              ║
║  Suggestion: Wire shipping.py into cart.py's checkout         ║
║  function (which is currently a stub anyway).                ║
║                                                              ║
║  Effort: LOW    Impact: 0.04 health improvement              ║
╚══════════════════════════════════════════════════════════════╝
```

### Finding #4: PHANTOM IMPORTS

```
╔══════════════════════════════════════════════════════════════╗
║  PHANTOM IMPORTS                  Severity: 0.65            ║
║  utils/email.py                   Confidence: 0.99           ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  Evidence:                                                   ║
║                                                              ║
║  [IR1] 2 imports resolve to NULL:                            ║
║        "utils.email_client.EmailClient" — module not found   ║
║        "jinja2" — package not installed                      ║
║                                                              ║
║  [IR3] phantom_ratio for this file: 0.67 (2/3 imports)       ║
║        This file CANNOT work at runtime                      ║
║                                                              ║
║  [IR5t] 2 commits by bot — AI hallucinated these references  ║
║                                                              ║
║  Suggestion: Create utils/email_client.py with EmailClient   ║
║  class, or use an existing email library. Add jinja2 to      ║
║  dependencies.                                               ║
║                                                              ║
║  Effort: MEDIUM    Impact: 0.05 health improvement           ║
╚══════════════════════════════════════════════════════════════╝
```

### Finding #5: HIDDEN COUPLING

```
╔══════════════════════════════════════════════════════════════╗
║  HIDDEN COUPLING                  Severity: 0.78            ║
║  services/auth.py ↔ services/payment.py                     ║
║                                   Confidence: 0.82           ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  Evidence:                                                   ║
║                                                              ║
║  [G1] No import edge between these files                     ║
║  [G4] Co-changed 18 times, lift=3.2, confidence=0.72         ║
║       They change together 3.2x more than chance              ║
║                                                              ║
║  [G6] d_semantic = 0.45 — moderate concept overlap            ║
║       Both deal with "user" and "transaction" concepts        ║
║                                                              ║
║  Suggestion: The shared concept is likely "transaction        ║
║  authorization." Extract to a shared module or make the       ║
║  dependency explicit.                                        ║
║                                                              ║
║  Effort: MEDIUM    Impact: 0.06 health improvement           ║
╚══════════════════════════════════════════════════════════════╝
```

### Finding #6: LAYER VIOLATION

```
╔══════════════════════════════════════════════════════════════╗
║  LAYER VIOLATION                  Severity: 0.52            ║
║  utils/cache.py → services/auth.py                          ║
║                                   Confidence: 0.99           ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  Evidence:                                                   ║
║                                                              ║
║  [IR4] utils/ is Layer 2 (should be Layer 1: foundation)     ║
║        services/ is Layer 2 (business logic)                  ║
║        A utility should NOT depend on a service               ║
║                                                              ║
║  [IR3] cache.py imports auth.get_current_user                ║
║        This makes cache.py unusable without auth context      ║
║                                                              ║
║  [G1×G6] d_dependency CLOSE but d_semantic FAR               ║
║          cache and auth are completely unrelated concepts     ║
║          → ACCIDENTAL COUPLING                                ║
║                                                              ║
║  Suggestion: Inject user context as a parameter instead of    ║
║  importing auth. cache.py should be user-agnostic.           ║
║                                                              ║
║  Effort: LOW    Impact: 0.07 health improvement              ║
╚══════════════════════════════════════════════════════════════╝
```

---

## Step 10: What the User Actually Sees

```
$ shannon-insight -C src/ --save --verbose

Shannon Insight v2.0                                    Health: 58%
────────────────────────────────────────────────────────────────────

Scanned 17 files (Python) in 0.8s

 HIGH RISK HUB (1 file)

   services/auth.py
     Centrality P94 · Blast radius 5 files · Churning (47 changes)
     Fix ratio 38% · Bus factor 1 · Concepts 3
     Δh = +0.52 — weakest link in its neighborhood
     → Split auth from user management. Spread knowledge.

 HIDDEN COUPLING (1 pair)

   services/auth.py ↔ services/payment.py
     Co-changed 18× · Lift 3.2 · No import edge
     Shared concepts: user, transaction
     → Extract shared concept or make dependency explicit.

 HOLLOW CODE (1 file)

   services/cart.py
     4/5 functions are stubs · Implementation Gini 0.89
     AI-generated, no human review
     → Implement checkout flow first.

 PHANTOM IMPORTS (1 file)

   utils/email.py
     2 unresolved: email_client (missing), jinja2 (not installed)
     → Create email_client module or use existing library.

 ORPHAN CODE (1 file)

   services/shipping.py
     Zero imports · Semantically close to cart.py
     → Wire into cart checkout flow.

 LAYER VIOLATION (1 edge)

   utils/cache.py → services/auth.py
     Utility depends on service (wrong direction)
     → Inject user context as parameter.

────────────────────────────────────────────────────────────────────
6 findings · 2 high · 2 medium · 2 low
Wiring score: 0.71 · Architecture health: 0.62
Snapshot saved to .shannon/history.db
```

---

## Step 11: Next Run (2 weeks later)

```
$ shannon-insight -C src/ --save

Shannon Insight v2.0                                    Health: 64% ↑
────────────────────────────────────────────────────────────────────

 HIGH RISK HUB (1 file)                    ← PERSISTING (4 snapshots)

   services/auth.py — still churning, bus factor still 1

 HIDDEN COUPLING (1 pair)                  ← PERSISTING

 HOLLOW CODE                               ← RESOLVED ✓ (cart.py stubs filled in)

 PHANTOM IMPORTS                           ← PERSISTING (email_client still missing)

 ORPHAN CODE                               ← RESOLVED ✓ (shipping.py now imported by cart)

 LAYER VIOLATION                           ← PERSISTING

────────────────────────────────────────────────────────────────────
4 findings (was 6) · 2 resolved · 0 new · 0 regressions
Debt velocity: -1.0/run (paying down debt)
```

---

## Step 12: The Health Command

```
$ shannon-insight health --last 5

Shannon Insight — Codebase Health Trends
────────────────────────────────────────────────────────────────────

  Metric                  Current   Trend         Direction
  ──────                  ───────   ─────         ─────────
  Active findings         4         ▇▆▅▄▃        Improving ↓
  Wiring score            0.79      ▃▄▅▆▇        Improving ↑
  Architecture health     0.62      ▅▅▅▅▅        Stable
  Codebase health         0.64      ▃▄▄▅▅        Improving ↑
  Modularity              0.38      ▅▅▅▅▅        Stable
  Bus factor (min)        1         ▁▁▁▁▁        Stalled — needs attention
  Fix ratio (mean)        0.22      ▅▄▃▃▃        Improving ↓

────────────────────────────────────────────────────────────────────
Health improving at +1.5% per snapshot. Main blocker: bus factor on auth.py.
```

---

## Summary: Data Flow Timing

```
Step    IR          What                         Time      Parallel?
────    ──          ────                         ────      ─────────
1       IR0         Read files, hash             50ms      —
2       IR1         Parse AST, extract structure  200ms     } STRUCTURAL
3       IR2         Classify roles, concepts      100ms     } SPINE
4       IR5t        Parse git, compute temporal   400ms     TEMPORAL SPINE (parallel with 1-3)
5       IR3         Build graph, compute metrics  300ms     (waits for IR1 + IR5t)
6       IR4         Infer architecture            50ms      (waits for IR3)
7       IR5s        Fuse signals                  50ms      (waits for all)
8       IR6         Generate findings             20ms      (waits for IR5s)
                                                  ─────
                                          Total:  ~800ms (with parallelism)
                                                  ~1.2s (sequential)
```

For a 1000-file codebase: ~5-8 seconds with parallelism. The bottleneck is git log parsing and spectral decomposition.
