# Shannon Insight: Worked Examples

This document walks through concrete calculations with real numbers, showing exactly how Shannon Insight's algorithms produce their results.

---

## Table of Contents

1. [PageRank Computation](#example-1-pagerank-computation)
2. [Shannon Entropy and Bus Factor](#example-2-shannon-entropy-and-bus-factor)
3. [Gini Coefficient](#example-3-gini-coefficient)
4. [Semantic Coherence](#example-4-semantic-coherence)
5. [NCD Clone Detection](#example-5-ncd-clone-detection)
6. [God File Detection](#example-6-god-file-detection)
7. [Risk Score Computation](#example-7-risk-score-computation)
8. [Health Laplacian and Weak Link](#example-8-health-laplacian-and-weak-link)
9. [Martin Metrics and Zone of Pain](#example-9-martin-metrics-and-zone-of-pain)
10. [Co-change Lift and Hidden Coupling](#example-10-co-change-lift-and-hidden-coupling)
11. [Louvain Modularity](#example-11-louvain-modularity)
12. [Confidence Score Calculation](#example-12-confidence-score-calculation)
13. [Churn Trajectory Classification](#example-13-churn-trajectory-classification)

---

## Example 1: PageRank Computation

**Given dependency graph (4 files)**:

```
A -> B
A -> C
B -> C
C -> A
```

Where A imports B and C; B imports C; C imports A (a cycle).

**Step 1: Initialize**

```
PR(A) = PR(B) = PR(C) = 1/3 = 0.333
d = 0.85, N = 3
```

(File D has no edges, so we exclude it; in practice it would get the baseline (1-d)/N.)

**Step 2: First iteration**

For each node, compute the incoming contribution:

```
PR_new(A) = (1 - 0.85) / 3 + 0.85 * [PR(C) / out_degree(C)]
          = 0.05 + 0.85 * [0.333 / 1]
          = 0.05 + 0.283
          = 0.333

PR_new(B) = (1 - 0.85) / 3 + 0.85 * [PR(A) / out_degree(A)]
          = 0.05 + 0.85 * [0.333 / 2]
          = 0.05 + 0.142
          = 0.192

PR_new(C) = (1 - 0.85) / 3 + 0.85 * [PR(A) / out_degree(A) + PR(B) / out_degree(B)]
          = 0.05 + 0.85 * [0.333 / 2 + 0.333 / 1]
          = 0.05 + 0.85 * [0.167 + 0.333]
          = 0.05 + 0.85 * 0.500
          = 0.05 + 0.425
          = 0.475
```

After iteration 1: PR(A)=0.333, PR(B)=0.192, PR(C)=0.475

**Step 3: Second iteration**

```
PR_new(A) = 0.05 + 0.85 * [0.475 / 1]
          = 0.05 + 0.404
          = 0.454

PR_new(B) = 0.05 + 0.85 * [0.333 / 2]
          = 0.05 + 0.142
          = 0.192

PR_new(C) = 0.05 + 0.85 * [0.333/2 + 0.192/1]
          = 0.05 + 0.85 * [0.167 + 0.192]
          = 0.05 + 0.85 * 0.359
          = 0.05 + 0.305
          = 0.355
```

After iteration 2: PR(A)=0.454, PR(B)=0.192, PR(C)=0.355

**Step 4: Continue iterating until convergence...**

After convergence (approximately 15 iterations):

```
PR(C) ~ 0.43  (highest -- C receives imports from both A and B)
PR(A) ~ 0.39  (second -- A receives from C)
PR(B) ~ 0.18  (lowest -- B only receives from A)
```

**Interpretation**: C is the most important file in this dependency graph. Both A and B depend on it, and A depends on it through a cycle. A change to C has the highest potential impact.

---

## Example 2: Shannon Entropy and Bus Factor

**Given**: A file `core/engine.py` has been modified by 3 authors:

```
Alice:  40 commits
Bob:    8 commits
Carol:  2 commits
Total:  50 commits
```

**Step 1: Compute probabilities**

```
p(Alice) = 40/50 = 0.80
p(Bob)   = 8/50  = 0.16
p(Carol) = 2/50  = 0.04
```

**Step 2: Compute author entropy**

```
H = -(0.80 * log2(0.80) + 0.16 * log2(0.16) + 0.04 * log2(0.04))
  = -(0.80 * (-0.322) + 0.16 * (-2.644) + 0.04 * (-4.644))
  = -((-0.258) + (-0.423) + (-0.186))
  = -(-0.867)
  = 0.867 bits
```

**Step 3: Compute bus factor**

```
bus_factor = 2^H = 2^0.867 = 1.824
```

**Interpretation**: The effective author count is 1.82. Alice dominates the authorship (80%), so despite having 3 contributors, the file effectively has fewer than 2 independent maintainers. If Alice leaves, the remaining authors have limited coverage. This file has bus_factor = 1.82, which is above the KNOWLEDGE_SILO threshold of 1.5 but only barely.

**Comparison with equal distribution**: If all three authors had contributed equally (16.67 commits each):
```
H = -(3 * (1/3 * log2(1/3))) = -(3 * (1/3 * (-1.585))) = 1.585 bits
bus_factor = 2^1.585 = 3.0
```

With equal contributions, bus_factor equals the actual number of authors.

---

## Example 3: Gini Coefficient

**Given**: A file has 5 functions with the following body token counts:

```
function_a: 120 tokens
function_b: 115 tokens
function_c: 5 tokens    (stub)
function_d: 3 tokens    (stub)
function_e: 2 tokens    (stub)
```

**Step 1: Sort ascending**

```
x = [2, 3, 5, 115, 120]
n = 5
```

**Step 2: Compute sums**

```
SUM(i * x_i) = 1*2 + 2*3 + 3*5 + 4*115 + 5*120
             = 2 + 6 + 15 + 460 + 600
             = 1083

SUM(x_i) = 2 + 3 + 5 + 115 + 120 = 245
```

**Step 3: Apply formula**

```
G = (2 * 1083) / (5 * 245) - (5 + 1) / 5
  = 2166 / 1225 - 6/5
  = 1.768 - 1.200
  = 0.568
```

**Interpretation**: impl_gini = 0.568. This is close to the threshold of 0.6 for the HOLLOW_CODE finder. The bimodal distribution (two complete functions and three stubs) is characteristic of AI-generated code where scaffolding was created but not all functions were implemented.

**Uniform case**: If all functions had 50 tokens each:
```
SUM(i * x_i) = 1*50 + 2*50 + 3*50 + 4*50 + 5*50 = 750
G = (2 * 750) / (5 * 250) - 6/5 = 1500/1250 - 1.2 = 1.2 - 1.2 = 0.0
```

Perfectly uniform implementation gives Gini = 0.

---

## Example 4: Semantic Coherence

**Given**: A file `data_processor.py` with 3 functions:

```python
def load_data(path):       # tokens: "load", "data", "path", "read", "csv", "parse"
def transform_data(df):    # tokens: "transform", "data", "clean", "filter", "normalize"
def save_results(output):  # tokens: "save", "results", "output", "write", "csv", "export"
```

**Step 1: Build TF-IDF vectors** (simplified, assuming equal IDF for illustration)

```
Function 1 (load_data):      [1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0]
                              load data path read csv parse
Function 2 (transform_data): [0, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0]
                              transform data clean filter normalize
Function 3 (save_results):   [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1]
                              save results output write csv export
```

**Step 2: Compute pairwise cosine similarities**

```
cos(f1, f2):
  dot product = 0+1+0+0+0+0+0+0+0+0+0+0+0+0 = 1  (shared: "data")
  ||f1|| = sqrt(6), ||f2|| = sqrt(5)
  cos = 1 / (sqrt(6) * sqrt(5)) = 1 / sqrt(30) = 0.183

cos(f1, f3):
  dot product = 0+0+0+0+1+0+0+0+0+0+0+0+0+0 = 1  (shared: "csv")
  ||f1|| = sqrt(6), ||f3|| = sqrt(5)
  cos = 1 / (sqrt(6) * sqrt(5)) = 0.183

cos(f2, f3):
  dot product = 0+0+0+0+0+0+0+0+0+0+0+0+0+0 = 0  (no shared tokens)
  cos = 0.0
```

**Step 3: Compute mean coherence**

```
semantic_coherence = mean(0.183, 0.183, 0.0) = 0.122
```

**Interpretation**: semantic_coherence = 0.12. This is relatively low -- the functions share some vocabulary ("data," "csv") but each has its own domain-specific terms. The file is reasonably coherent as a data processing pipeline but not tightly themed. In a larger file with many unrelated function groups, coherence would drop further.

**High coherence example**: If all functions shared most tokens (e.g., all manipulating "database," "query," "connection"), cosine similarities would be 0.8+ and coherence would approach 0.85.

---

## Example 5: NCD Clone Detection

**Given**: Two files with content:

```
File A (100 bytes):  "def process_user(user): validate(user); save(user); return user"
File B (105 bytes):  "def process_order(order): validate(order); save(order); return order"
```

**Step 1: Compress individual files**

```
C(A) = len(zlib.compress(A)) = 85 bytes    (hypothetical)
C(B) = len(zlib.compress(B)) = 87 bytes    (hypothetical)
```

**Step 2: Compress concatenation**

```
C(AB) = len(zlib.compress(A + B)) = 95 bytes  (hypothetical)
```

The concatenation compresses much better than the sum of individual compressions because zlib recognizes the shared patterns.

**Step 3: Compute NCD**

```
NCD(A, B) = (C(AB) - min(C(A), C(B))) / max(C(A), C(B))
          = (95 - 85) / 87
          = 10 / 87
          = 0.115
```

**Interpretation**: NCD = 0.115 < 0.3 threshold. These files are flagged as COPY_PASTE_CLONE. The nearly identical structure with only variable name substitutions is detected by the compression-based similarity.

**Non-clone example**: If File B were completely different content:
```
C(AB) = 170 bytes  (no shared patterns to exploit)
NCD = (170 - 85) / 87 = 85/87 = 0.977
```

NCD near 1.0 means the files share no compressible structure. Not a clone.

---

## Example 6: God File Detection

**Given**: A file `mega_utils.py` with the following signals:

```
Across a 200-file codebase:

cognitive_load = 52.3
  (percentile: 0.94 -- in the top 6% of all files)

semantic_coherence = 0.08
  (percentile: 0.12 -- in the bottom 12%)

function_count = 38
concept_count = 5  (database, HTTP, parsing, validation, logging)
concept_entropy = 2.12 bits
lines = 1,450
```

**Step 1: Check GOD_FILE conditions**

```
pctl(cognitive_load) = 0.94 > 0.90  --> TRUE
pctl(semantic_coherence) = 0.12 < 0.20  --> TRUE (low coherence is bad)
```

Both conditions met. GOD_FILE finding fires.

**Step 2: Compute confidence**

```
Condition 1: cognitive_load, pctl=0.94, threshold=0.90, polarity=high_is_bad
  margin = (0.94 - 0.90) / (1.0 - 0.90) = 0.04 / 0.10 = 0.40

Condition 2: semantic_coherence, pctl=0.12, threshold=0.20, polarity=high_is_good
  margin = (0.20 - 0.12) / 0.20 = 0.08 / 0.20 = 0.40

confidence = mean(0.40, 0.40) = 0.40
```

**Step 3: Build finding**

```
Finding:
  type: GOD_FILE
  severity: 0.8
  confidence: 0.40
  file: mega_utils.py
  evidence:
    - cognitive_load: 52.3 (p94)
    - semantic_coherence: 0.08 (p12)
    - function_count: 38
    - concept_count: 5
    - concept_entropy: 2.12 bits
  suggestion: "Split by concept clusters: database, HTTP, parsing,
               validation, logging. Each concept = a candidate file."
```

**Interpretation**: This file is both highly complex (top 6% cognitive load) and unfocused (bottom 12% coherence, 5 distinct concept clusters). It should be split into ~5 focused modules, one per concept cluster.

---

## Example 7: Risk Score Computation

**Given**: A file `auth/session.py` in a 150-file codebase (FULL tier):

```
Raw signal values:
  pagerank = 0.032
  blast_radius_size = 28
  cognitive_load = 35.7
  churn_trajectory = CHURNING
  bus_factor = 1.2

Percentile values (across 150 files):
  pctl(pagerank) = 0.89
  pctl(blast_radius_size) = 0.85
  pctl(cognitive_load) = 0.77

max_bus_factor across codebase = 4.2
```

**Step 1: Compute instability_factor**

```
churn_trajectory = CHURNING, which is in {CHURNING, SPIKING}
instability_factor = 1.0
```

**Step 2: Apply risk_score formula**

```
risk_score = 0.25 * pctl(pagerank)
           + 0.20 * pctl(blast_radius_size)
           + 0.20 * pctl(cognitive_load)
           + 0.20 * instability_factor
           + 0.15 * (1 - bus_factor / max_bus_factor)

           = 0.25 * 0.89
           + 0.20 * 0.85
           + 0.20 * 0.77
           + 0.20 * 1.0
           + 0.15 * (1 - 1.2/4.2)

           = 0.2225
           + 0.1700
           + 0.1540
           + 0.2000
           + 0.15 * (1 - 0.286)

           = 0.2225
           + 0.1700
           + 0.1540
           + 0.2000
           + 0.15 * 0.714

           = 0.2225 + 0.1700 + 0.1540 + 0.2000 + 0.1071

           = 0.8536
```

**Step 3: Convert to display scale**

```
risk_score_display = 0.8536 * 10 = 8.5/10
```

**Interpretation**: This file scores 8.5/10 on risk. It has high centrality (PageRank p89), significant blast radius (p85), notable complexity (p77), active churning, and low bus factor (1.2 effective authors out of a maximum 4.2). This file is a candidate for HIGH_RISK_HUB and KNOWLEDGE_SILO findings.

---

## Example 8: Health Laplacian and Weak Link

**Given**: A small dependency subgraph:

```
A -> C
B -> C
C -> D
C -> E
```

With raw_risk values:
```
raw_risk(A) = 0.20
raw_risk(B) = 0.25
raw_risk(C) = 0.75   <-- the suspected weak link
raw_risk(D) = 0.15
raw_risk(E) = 0.18
```

**Step 1: Identify neighbors** (undirected: both import directions)

```
neighbors(C) = {A, B, D, E}  (A->C, B->C, C->D, C->E)
```

**Step 2: Compute delta_h for C**

```
mean_neighbor_risk = (0.20 + 0.25 + 0.15 + 0.18) / 4 = 0.78 / 4 = 0.195

delta_h(C) = raw_risk(C) - mean_neighbor_risk
           = 0.75 - 0.195
           = 0.555
```

**Step 3: Check WEAK_LINK threshold**

```
delta_h(C) = 0.555 > 0.4  --> WEAK_LINK finding fires
```

**Step 4: Compute delta_h for other nodes**

```
neighbors(A) = {C}
delta_h(A) = 0.20 - 0.75 = -0.55  (A is healthier than its neighbor C)

neighbors(D) = {C}
delta_h(D) = 0.15 - 0.75 = -0.60  (D is healthier than its neighbor C)
```

**Interpretation**: File C is significantly worse than all its neighbors (delta_h = 0.555). It is a local weak point in an otherwise healthy neighborhood. Improving C would have the highest marginal impact on the subgraph's overall health.

Note that A and D have negative delta_h, meaning they are healthier than their neighbors. This is expected -- they are being dragged toward C's poor health.

---

## Example 9: Martin Metrics and Zone of Pain

**Given**: Module `models/` with 6 files:

```
Files: user.py, order.py, product.py, base.py, types.py, constants.py

Cross-module edges (incoming from other modules):
  api/routes.py -> models/user.py
  api/routes.py -> models/order.py
  api/routes.py -> models/product.py
  services/auth.py -> models/user.py
  services/payment.py -> models/order.py
  services/inventory.py -> models/product.py
  db/migrations.py -> models/user.py
  db/migrations.py -> models/order.py
  Ca = 8  (8 incoming edges from other modules)

Cross-module edges (outgoing to other modules):
  models/base.py -> utils/validation.py
  Ce = 1  (1 outgoing edge to other modules)
```

**Step 1: Compute Instability**

```
I = Ce / (Ca + Ce) = 1 / (8 + 1) = 1/9 = 0.111
```

**Step 2: Compute Abstractness**

```
Symbols in models/:
  Total public symbols: 18 (6 classes + 12 public methods)
  Abstract symbols: 1 (base.py has ABC class with 1 abstract method)

A = 1 / 18 = 0.056
```

**Step 3: Compute Main Sequence Distance**

```
D = |A + I - 1| = |0.056 + 0.111 - 1| = |-0.833| = 0.833
```

**Step 4: Check Zone of Pain**

```
A = 0.056 < 0.3   --> TRUE (concrete)
I = 0.111 < 0.3   --> TRUE (stable)
I is not None      --> TRUE (has cross-module dependencies)
```

All conditions met. ZONE_OF_PAIN finding fires.

**Interpretation**: The `models/` module is concrete (only 1 abstract symbol out of 18) and stable (8 things depend on it, only 1 outgoing dependency). This makes it extremely hard to change -- any modification risks breaking 8 incoming dependents. The high D value (0.833) confirms it is far from the main sequence ideal.

**Recommendation**: Extract interfaces for the model classes (increase A) or reduce the number of external dependents (increase I toward flexibility). The models should expose abstract contracts that other modules import, rather than concrete implementations.

---

## Example 10: Co-change Lift and Hidden Coupling

**Given**: 500 total commits in the repository.

```
File A (api/auth.py): touched in 50 commits  -> P(A) = 50/500 = 0.10
File B (db/sessions.py): touched in 40 commits -> P(B) = 40/500 = 0.08
Both A and B in same commit: 15 times -> P(A,B) = 15/500 = 0.03

No import edge between api/auth.py and db/sessions.py.
```

**Step 1: Compute lift**

```
lift(A, B) = P(A,B) / (P(A) * P(B))
           = 0.03 / (0.10 * 0.08)
           = 0.03 / 0.008
           = 3.75
```

**Step 2: Compute confidence**

```
confidence(A -> B) = P(A,B) / P(A) = 0.03 / 0.10 = 0.30
confidence(B -> A) = P(A,B) / P(B) = 0.03 / 0.08 = 0.375

max_confidence = 0.375
```

**Step 3: Check HIDDEN_COUPLING conditions**

```
lift = 3.75 >= 2.0    --> TRUE
confidence = 0.375    --> FALSE (need >= 0.5)
```

The lift condition is met but confidence is below 0.5. HIDDEN_COUPLING does not fire.

**Alternative scenario**: If A and B co-changed 25 times:
```
P(A,B) = 25/500 = 0.05
lift = 0.05 / (0.10 * 0.08) = 6.25
confidence(A -> B) = 0.05 / 0.10 = 0.50
```

Now lift = 6.25 >= 2.0 AND confidence = 0.50 >= 0.5 AND no structural edge. HIDDEN_COUPLING fires.

**Interpretation**: These two files change together 6.25 times more often than expected by chance. Half of all commits touching auth.py also touch sessions.py. Yet there is no import between them. This strongly suggests an implicit dependency -- perhaps both files must be updated together when authentication logic changes. The fix is to either make the dependency explicit (one file imports the other) or extract the shared concept into a third file.

---

## Example 11: Louvain Modularity

**Given**: A dependency graph with 6 files and the following edges:

```
A -> B, A -> C    (A, B, C form a cluster)
B -> C
D -> E, D -> F    (D, E, F form a cluster)
E -> F
B -> D            (one cross-cluster edge)
```

Total edges (symmetrized for undirected Louvain): 7 edges, so m = 7.

**Step 1: Start with each node in its own community**

Communities: {A}, {B}, {C}, {D}, {E}, {F}
Q = 0 (trivially, since delta function is only 1 for same-community pairs, and there are no intra-community edges when each node is its own community).

Actually, in this initial state, Q sums over all pairs in the same community. Since each community has one node, there are no pairs, so Q captures only self-loops (which we do not have). Q starts negative.

**Step 2: Try moving A to B's community**

A connects to B (1 edge) and C (1 edge).
Moving A to B's community: gain from the A-B edge.

Without computing the full formula, the algorithm finds that merging {A, B, C} and {D, E, F} gives the maximum modularity.

**Step 3: Final state**

```
Community 1: {A, B, C}  -- 3 internal edges (A-B, A-C, B-C)
Community 2: {D, E, F}  -- 3 internal edges (D-E, D-F, E-F)
Cross-community: 1 edge (B-D)
```

**Step 4: Compute Q**

```
Q = (1/2m) * SUM [A_ij - k_i*k_j/(2m)] * delta(c_i, c_j)
```

For all pairs within the same community:

In Community 1 (A, B, C), degrees (in the undirected graph): A=2, B=3, C=2:
```
Pairs in C1: (A,B), (A,C), (B,C)
A_AB = 1, k_A*k_B/(2*7) = 2*3/14 = 0.429  -> contribution = 1 - 0.429 = 0.571
A_AC = 1, k_A*k_C/(2*7) = 2*2/14 = 0.286  -> contribution = 1 - 0.286 = 0.714
A_BC = 1, k_B*k_C/(2*7) = 3*2/14 = 0.429  -> contribution = 1 - 0.429 = 0.571
```

In Community 2 (D, E, F), degrees: D=3, E=2, F=2:
```
Pairs in C2: (D,E), (D,F), (E,F)
A_DE = 1, k_D*k_E/14 = 3*2/14 = 0.429  -> contribution = 1 - 0.429 = 0.571
A_DF = 1, k_D*k_F/14 = 3*2/14 = 0.429  -> contribution = 1 - 0.429 = 0.571
A_EF = 1, k_E*k_F/14 = 2*2/14 = 0.286  -> contribution = 1 - 0.286 = 0.714
```

Each pair contributes twice (both orderings), so sum each once and multiply by 2:

```
Q = (1/14) * 2 * (0.571 + 0.714 + 0.571 + 0.571 + 0.571 + 0.714)
  = (1/14) * 2 * 3.712
  = (1/14) * 7.424
  = 0.530
```

**Interpretation**: Q = 0.530 > 0.3, indicating strong community structure. The codebase naturally separates into two clusters with minimal cross-cluster dependency. Shannon Insight would report modularity = 0.53.

---

## Example 12: Confidence Score Calculation

**Given**: HIGH_RISK_HUB finder triggers with these conditions:

```
Condition 1: pctl(pagerank) = 0.95, threshold = 0.90, polarity = "high_is_bad"
Condition 2: pctl(blast_radius_size) = 0.98, threshold = 0.90, polarity = "high_is_bad"
Condition 3: pctl(cognitive_load) = 0.92, threshold = 0.90, polarity = "high_is_bad"
```

**Step 1: Compute margins**

```
margin_1 = (0.95 - 0.90) / (1.0 - 0.90) = 0.05 / 0.10 = 0.50
margin_2 = (0.98 - 0.90) / (1.0 - 0.90) = 0.08 / 0.10 = 0.80
margin_3 = (0.92 - 0.90) / (1.0 - 0.90) = 0.02 / 0.10 = 0.20
```

**Step 2: Compute confidence**

```
confidence = mean(0.50, 0.80, 0.20) = 1.50 / 3 = 0.50
```

**Interpretation**: Confidence 0.50 means the finding is moderately certain. PageRank is well above threshold (margin 0.50), blast radius is strongly above (margin 0.80), but cognitive load is only slightly above (margin 0.20). The finding is real but cognitive load is borderline.

**High confidence example**: If all percentiles were 0.99:
```
margins = (0.90, 0.90, 0.90)
confidence = 0.90
```

**Borderline example**: If all percentiles were 0.91:
```
margins = (0.10, 0.10, 0.10)
confidence = 0.10
```

Low confidence means the file barely crosses the threshold -- it might not be a true problem.

---

## Example 13: Churn Trajectory Classification

**Given**: A file `api/routes.py` with the following commit history over 8 four-week windows:

```
Window:   1   2   3   4   5   6   7   8
Changes:  2   5   3   8   12  4   15  20
```

**Step 1: Compute total changes**

```
total_changes = 2 + 5 + 3 + 8 + 12 + 4 + 15 + 20 = 69
```

total_changes > 1, so not DORMANT.

**Step 2: Compute velocity (linear regression slope)**

```
t = [1, 2, 3, 4, 5, 6, 7, 8]
c = [2, 5, 3, 8, 12, 4, 15, 20]

mean_t = 4.5
mean_c = 8.625

numerator = SUM((t_i - mean_t) * (c_i - mean_c))
  = (1-4.5)(2-8.625) + (2-4.5)(5-8.625) + (3-4.5)(3-8.625) + (4-4.5)(8-8.625)
  + (5-4.5)(12-8.625) + (6-4.5)(4-8.625) + (7-4.5)(15-8.625) + (8-4.5)(20-8.625)

  = (-3.5)(-6.625) + (-2.5)(-3.625) + (-1.5)(-5.625) + (-0.5)(-0.625)
  + (0.5)(3.375) + (1.5)(-4.625) + (2.5)(6.375) + (3.5)(11.375)

  = 23.188 + 9.063 + 8.438 + 0.313 + 1.688 + (-6.938) + 15.938 + 39.813
  = 91.500

denominator = SUM((t_i - mean_t)^2)
  = 12.25 + 6.25 + 2.25 + 0.25 + 0.25 + 2.25 + 6.25 + 12.25
  = 42.0

velocity = 91.500 / 42.0 = 2.179 changes per window
```

Velocity is positive (> threshold, say eps = 0.5).

**Step 3: Compute coefficient of variation**

```
mean_c = 8.625
std_c = sqrt(SUM((c_i - mean_c)^2) / n)
      = sqrt((44.141 + 13.141 + 31.641 + 0.391 + 11.391 + 21.391 + 40.641 + 129.391) / 8)
      = sqrt(292.125 / 8)
      = sqrt(36.516)
      = 6.043

CV = 6.043 / 8.625 = 0.701
```

**Step 4: Classify**

```
velocity = 2.179 > threshold (positive)
CV = 0.701 > 0.5

velocity > eps AND CV > 0.5 --> SPIKING
```

**Interpretation**: This file's change rate is both increasing (positive velocity) and erratic (CV > 0.5). The trajectory is SPIKING -- changes are accelerating in an unpredictable pattern. Combined with the CHURNING/SPIKING trajectory, the instability_factor in risk_score will be set to 1.0 (maximum).

**Stable counterexample**: Window changes = [5, 6, 5, 5, 6, 5, 6, 5]
```
velocity ~ 0 (flat)
CV = 0.08 (very low variance)
Classification: STABLE
```
