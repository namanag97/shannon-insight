# The Math Toolbox: Intuitions for Non-Mathematicians

This document explains the branches of mathematics that show up when you
try to measure and understand complex systems (like software, networks,
organizations, or anything with many interacting parts).

No prerequisites assumed. Each section answers: what is it, what does it
look like, and why would anyone care?

---

## Table of Contents

1. [Graph Theory](#1-graph-theory)
2. [Spectral Graph Theory](#2-spectral-graph-theory)
3. [Community Detection](#3-community-detection)
4. [Information Theory](#4-information-theory)
5. [Statistics & Distributions](#5-statistics--distributions)
6. [Measurement Theory](#6-measurement-theory)
7. [Abstract Algebra](#7-abstract-algebra)
8. [Category Theory](#8-category-theory)
9. [Linear Algebra](#9-linear-algebra)
10. [Topology & Metric Spaces](#10-topology--metric-spaces)
11. [Process Mining & Sequence Analysis](#11-process-mining--sequence-analysis)
12. [Dynamical Systems](#12-dynamical-systems)

---

## 1. Graph Theory

### What is it?

A graph is dots connected by lines. That's it.

```
    A ------- B
    |         |
    |         |
    C ------- D ------- E
```

The dots are called **nodes** (or vertices). The lines are called
**edges**. If the lines have arrows, the graph is **directed** — the
relationship goes one way.

```
    A ------> B
    |         |
    v         v
    C ------> D ------> E
```

### Why would anyone care?

Anything that has relationships can be drawn as a graph:

- People who know each other (social network)
- Web pages that link to each other (the internet)
- Files that import other files (a codebase)
- Cities connected by roads (a map)

Once you draw something as a graph, you can ask precise questions:

**"Is there a path from A to E?"**

```
    A --> B --> D --> E       Yes, through B and D.
```

**"What's the shortest path?"**

Count the edges. A->B->D->E = 3 hops.

**"Which node is most connected?"**

Count edges per node. That node is a hub.

```
    A --- B
    |   / |
    |  /  |
    C --- D         C connects to A, B, D = 3 edges
          |         D connects to B, C, E = 3 edges
          E         A connects to B, C    = 2 edges
```

**"Are there cycles?"**

A cycle means you can follow arrows and end up where you started.

```
    A --> B
    ^     |
    |     v
    D <-- C         A -> B -> C -> D -> A  is a cycle
```

Cycles matter because they indicate circular dependencies — things that
depend on each other in a loop.

### Strongly Connected Components (Tarjan's Algorithm)

In a directed graph, a **strongly connected component** (SCC) is a group
of nodes where every node can reach every other node by following arrows.

```
    +-------------+
    | A --> B     |
    | ^     |     |        F --> G
    | |     v     |
    | D <-- C     |
    +-------------+
         SCC 1              SCC 2 (just F)
                            SCC 3 (just G)
```

A, B, C, D form an SCC because you can get from any of them to any other.
F and G are each their own SCC because there's no way back from G to F.

Tarjan's algorithm finds these groups efficiently by doing a depth-first
walk and keeping track of how far back each node can reach.

### Blast Radius

If a node changes, what else is affected? Follow all outgoing edges
recursively. Everything you can reach is the "blast radius."

```
    A --> B --> C
    |         ^
    v        /
    D ------+

    Blast radius of A = {B, C, D}    (everything)
    Blast radius of D = {C}          (only C)
    Blast radius of C = {}           (nothing)
```

---

## 2. Spectral Graph Theory

### What is it?

"Spectral" means "relating to eigenvalues" (we'll explain those in the
linear algebra section). The idea: take a graph, represent it as a matrix
of numbers, then analyze that matrix mathematically.

### The Adjacency Matrix

List all nodes across the top and down the side. Put a 1 where there's
an edge, 0 where there isn't.

```
    A --- B            A  B  C
    |     |        A [ 0  1  1 ]
    C-----+        B [ 1  0  1 ]
                   C [ 1  1  0 ]
```

### The Laplacian Matrix

A slightly modified version. Diagonal = how many edges each node has.
Off-diagonal = negative of the adjacency matrix.

```
                   A  B  C
               A [ 2 -1 -1 ]
               B [-1  2 -1 ]
               C [-1 -1  2 ]
```

### Why would anyone care?

The eigenvalues of the Laplacian tell you structural things about the
graph without you having to "look" at it:

- **Smallest eigenvalue** is always 0. The number of zeros tells you how
  many disconnected pieces the graph has.

- **Second smallest eigenvalue** (the "Fiedler value") measures how well-
  connected the graph is. Close to 0 = there's a weak point where the
  graph almost falls apart. Large = tightly connected.

```
    Tightly connected:          Loosely connected:

    A --- B                     A --- B     C --- D
    | \ / |                           |     |
    | / \ |                           E-----+
    C --- D

    Fiedler value: large        Fiedler value: near 0
```

- **The Fiedler vector** (the eigenvector for that second eigenvalue)
  tells you WHERE to cut. Nodes with positive values go on one side,
  negative on the other. This gives you a natural way to split a graph
  in two.

```
    Fiedler vector values:    [-0.5, -0.3, +0.4, +0.6]
                                A      B     C     D

    Split: {A, B} | {C, D}    <-- natural division
```

This is used everywhere — image segmentation, circuit partitioning,
clustering data, finding natural boundaries in networks.

---

## 3. Community Detection

### What is it?

Given a graph, find groups of nodes that are more connected to each other
than to the rest of the graph.

```
    Before:                     After (communities found):

    A---B   E---F              [ A---B ]   [ E---F ]
    |\ /|   |\ /|              [ |\ /| ]   [ |\ /| ]
    | X |   | X |              [ | X | ]   [ | X | ]
    |/ \|   |/ \|              [ |/ \| ]   [ |/ \| ]
    C---D---G---H              [ C---D-]-[-G---H ]
                                         ^
                              one weak link between communities
```

### Modularity

How do you measure whether a grouping is good? **Modularity** compares
the actual number of edges within groups to the expected number if edges
were placed randomly.

```
    Modularity Q ranges from -0.5 to 1.0

    Q = 0    -->  communities are no better than random
    Q = 0.3+ -->  meaningful community structure
    Q = 0.7+ -->  strong community structure
```

Think of it as: "Are there more within-group connections than chance
would predict?"

### Louvain Algorithm

A fast method for finding communities. It works in two phases that repeat:

```
    Phase 1: Move each node to the neighbor's community
             that gives the biggest modularity gain.

    Node A is in community 1.
    Its neighbors B (community 1) and E (community 2).
    Moving A to community 2 would decrease modularity.
    So A stays.

    Phase 2: Collapse each community into a single super-node.
             Edges between communities become edges between super-nodes.

    [ A B C ] ------- [ D E F ]     becomes     X ------- Y
```

Repeat until modularity stops improving.

---

## 4. Information Theory

### What is it?

A mathematical framework for measuring **surprise** and **uncertainty**.
Founded by Claude Shannon in 1948.

### Entropy

Entropy measures how unpredictable something is.

A coin that always lands heads:

```
    H H H H H H H H H H

    Entropy = 0 (no surprise, totally predictable)
```

A fair coin:

```
    H T H H T H T T H T

    Entropy = 1 bit (maximum surprise for two outcomes)
```

A die with six faces:

```
    Entropy = log2(6) = 2.58 bits
```

The formula: for each possible outcome, multiply its probability by
the log of its probability, sum them up, and negate.

```
    H(X) = - sum of [ p(x) * log2(p(x)) ] for each outcome x
```

### Why would anyone care?

Entropy quantifies complexity and diversity:

- **A file that uses 50 different syntax constructs** has higher entropy
  than one that repeats the same pattern. Higher entropy = more things
  your brain has to track.

- **A perfectly uniform distribution** (all outcomes equally likely) has
  maximum entropy. A spike at one value has zero entropy.

```
    Low entropy:              High entropy:

    ||||                      | | | | | | | | |
    ||||                      | | | | | | | | |
    ||||                      | | | | | | | | |
    ||||                      | | | | | | | | |
    -----                     -----------------
     A B C D                   A B C D E F G H I

    One thing dominates.       Everything is spread out.
```

### Compression and Kolmogorov Complexity

A related idea: the complexity of something is the length of its shortest
description.

```
    String 1: "AAAAAAAAAA"
    Compressed: "10 x A"  (short description = low complexity)

    String 2: "KXQWPZJFMR"
    Compressed: "KXQWPZJFMR" (can't compress = high complexity)
```

You can't compute true Kolmogorov complexity (it's provably uncomputable),
but you can approximate it using real compressors like gzip. If a file
compresses a lot, it's repetitive. If it barely compresses, it's complex.

---

## 5. Statistics & Distributions

### What is a distribution?

A distribution describes how values are spread out.

```
    Normal (bell curve):        Most values near the middle.

              ***
            **   **
           *       *
         **         **
       **             **
    ========================
```

```
    Power law (long tail):      A few huge values, many small ones.

    *
    *
    *
    **
     ***
       *****
            **************
    ========================
```

### Why the shape matters

**Normal distribution**: Mean and standard deviation summarize it well.
68% of data falls within 1 standard deviation of the mean.

```
    |     ****
    |    *    *          <- 68% of data is in here
    |   *      *
    |  *        *
    | *          *
    |*            *___
    +-----|---------|---
        mean-s    mean+s
```

**Power law distribution**: Mean and standard deviation are MISLEADING.
The mean gets pulled by extreme values. Standard deviation is enormous.

```
    If file sizes are:  1, 1, 2, 2, 3, 3, 5, 8, 500

    Mean = 58.3     (dominated by the 500)
    Median = 3      (much more representative)
```

This is why z-scores (which use mean and standard deviation) break down
on power-law data. A z-score of 5 might flag 20% of your data as
"outliers" — which defeats the purpose.

### Outlier Detection Approaches

**Z-score (assumes normal distribution)**:

```
    z = (value - mean) / std_deviation

    |z| > 3  -->  "outlier"

    Problem: garbage if data isn't normally distributed
```

**MAD (Median Absolute Deviation)**:

```
    1. Find the median
    2. Find each value's distance from the median
    3. The median of THOSE distances is the MAD

    modified_z = 0.6745 * (value - median) / MAD

    More robust than z-score. Resistant to extreme values.
```

**Percentile-based**:

```
    Just rank everything and take the top/bottom X%.
    No distribution assumptions at all.

    "Flag the top 5%" works regardless of shape.
```

**Log transform**:

```
    If data is:     1, 2, 5, 10, 50, 1000

    Take log:       0, 0.3, 0.7, 1.0, 1.7, 3.0

    Now it looks much more normal. Z-scores work again.
    But you need to make sure log(value) is meaningful.
```

---

## 6. Measurement Theory

### What is it?

The study of what numbers mean and what you're allowed to do with them.
Not all numbers are created equal.

### The Four Scale Types

**Nominal (names)**:

```
    Language: Python=1, Java=2, Rust=3

    The numbers are just labels.
    Python is not "less than" Java.
    You CANNOT average them. (1+2)/2 = 1.5 = ???
    You CAN count them: 5 Python files, 3 Java files.
```

**Ordinal (rankings)**:

```
    Severity: Low=1, Medium=2, High=3, Critical=4

    The ORDER matters: Critical > High > Medium > Low.
    But the GAPS are not equal.
    The difference between Low and Medium is NOT necessarily
    the same as between High and Critical.
    You CAN say "A is worse than B."
    You CANNOT say "A is twice as bad as B."
    Averaging is dubious: (Low + Critical) / 2 = Medium???
```

**Interval (equal gaps, no true zero)**:

```
    Temperature in Celsius: 10, 20, 30

    The gaps ARE equal: 20-10 = 30-20 = 10 degrees.
    You CAN average: (10+30)/2 = 20. Meaningful!
    But 0 C is not "no temperature."
    So you CANNOT say "30 C is three times as hot as 10 C."
    Ratios are meaningless.
```

**Ratio (equal gaps, true zero)**:

```
    Lines of code: 0, 100, 200, 500

    0 means truly "nothing."
    200 LOC IS twice as much as 100 LOC.
    Ratios are meaningful. Averages are meaningful.
    All arithmetic operations are valid.
```

### Why would anyone care?

Because violating scale rules gives you nonsense.

```
    Suppose you measure:
    - Complexity:   ordinal (Low, Medium, High)
    - File size:    ratio   (bytes)
    - Language:     nominal (Python, Java)

    "Average complexity" of a module?
        Only valid if you treat ordinal as interval (risky).

    "Complexity per byte"?
        Dividing ordinal by ratio = meaningless.

    "Sum of languages"?
        Python + Java = ??? (nonsense)
```

### Permissible Operations by Scale

```
    Scale      =, !=    <, >    +, -    *, /    mean    median
    --------   -----    ----    ----    ----    ----    ------
    Nominal     yes      no      no      no      no      no
    Ordinal     yes     yes      no      no      no     yes
    Interval    yes     yes     yes      no     yes     yes
    Ratio       yes     yes     yes     yes     yes     yes
```

---

## 7. Abstract Algebra

### What is it?

The study of **operations on sets** and the rules those operations follow.
Instead of studying specific numbers, you study the structure of how
things combine.

### Monoid

A monoid is three things:

1. A set of values
2. A way to combine two values into one (an operation)
3. A "do nothing" value (identity element)

Rules: combining must be associative — (a + b) + c = a + (b + c).

```
    Examples:

    (Numbers, +, 0)       3 + 0 = 3.     (2+3)+4 = 2+(3+4) = 9
    (Numbers, *, 1)       3 * 1 = 3.     (2*3)*4 = 2*(3*4) = 24
    (Strings, concat, "") "hi"+""="hi".  ("a"+"b")+"c" = "a"+("b"+"c")
```

### Why would anyone care?

Monoids show up whenever you're aggregating data:

```
    Summing metrics across files:
        total = file1 + file2 + file3

    This only works correctly if your metric forms a monoid:
    - Combining two values gives a valid value (closure)
    - Order of grouping doesn't matter (associativity)
    - There's a sensible "empty" value (identity)
```

If your metric doesn't satisfy these properties, aggregation is suspect.

### Semiring

A semiring has TWO operations (like + and *) that work together:

```
    (Set, +, *, zero, one)

    Examples:
    - (Numbers, +, *, 0, 1)              ordinary arithmetic
    - (Booleans, OR, AND, false, true)    logic
    - ({0,inf}, min, +, inf, 0)           shortest path!
```

That last one is key. Finding shortest paths in a graph is really just
"arithmetic" in a different number system where:
- "addition" means "take the minimum"
- "multiplication" means "add distances"

```
    Shortest path A->C:

    min(  A->B->C,  A->D->C  )     <-- "addition" = min
       = min( 3+2, 5+1 )           <-- "multiplication" = +
       = min( 5, 6 )
       = 5
```

Different semirings solve different graph problems:
- (min, +) = shortest paths
- (max, min) = widest paths (bottleneck)
- (boolean OR, AND) = reachability

---

## 8. Category Theory

### What is it?

The "mathematics of mathematics." Instead of studying objects directly,
it studies the **relationships** (arrows) between objects.

### Objects and Morphisms

```
    Objects: A, B, C     (things — could be anything)
    Morphisms: f, g      (arrows between things)

         f         g
    A -------> B -------> C

    f: A -> B    "f transforms A into B"
    g: B -> C    "g transforms B into C"
    g . f: A -> C  "do f, then g" (composition)
```

The key insight: you don't need to know what A, B, C ARE internally.
All that matters is the arrows and how they compose.

### Functors

A functor maps one category to another, preserving the structure.

```
    Category 1:              Category 2:

    A --f--> B               F(A) --F(f)--> F(B)
    |        |                |              |
    g        h      F -->    F(g)           F(h)
    |        |                |              |
    v        v                v              v
    C --k--> D               F(C) --F(k)--> F(D)
```

The functor F:
- Maps each object to a new object
- Maps each arrow to a new arrow
- Preserves composition: F(g . f) = F(g) . F(f)

### Why would anyone care?

Category theory gives you a language for **structure-preserving
transformations**. When you aggregate metrics from files to modules
to systems, you want to make sure the relationships between things
are preserved, not just the numbers.

```
    File level:                Module level:

    a.py --imports--> b.py     ModuleA --depends--> ModuleB
    a.py --imports--> c.py         |
    c.py --imports--> b.py         |
                                   v
                               ModuleC (if c.py is in a
                                        different module)

    The functor "maps" file-level relationships to module-level
    relationships. If it's a valid functor, no dependencies are
    lost or invented in the translation.
```

### Natural Transformation

A natural transformation converts between two functors. If you have
two different ways to summarize something (two functors), a natural
transformation says they're "compatible."

```
    Functor F: raw byte count per module
    Functor G: normalized percentage per module

    Natural transformation:  divide each F-value by the total
    This works the same way regardless of which module you pick.
    That uniformity IS the naturality condition.
```

---

## 9. Linear Algebra

### What is it?

The mathematics of **vectors, matrices, and linear transformations**.

### Vectors

A vector is just a list of numbers.

```
    v = [3, 5, 2]

    You can think of it as:
    - A point in 3D space
    - A direction and magnitude (an arrow)
    - A row of data (3 features of something)
```

### Matrices

A matrix is a grid of numbers. It represents a transformation.

```
    M = [ 2  0 ]
        [ 0  3 ]

    Applied to vector [1, 1]:

    [ 2  0 ] * [1]   =   [2]
    [ 0  3 ]   [1]       [3]

    It stretched horizontally by 2 and vertically by 3.
```

### Eigenvalues and Eigenvectors

This is the big one. An eigenvector of a matrix is a direction that
doesn't change when the matrix is applied — it only gets scaled.

```
    M * v = lambda * v

    M is the matrix
    v is the eigenvector (direction that survives)
    lambda is the eigenvalue (how much it gets scaled)
```

Visually:

```
    Before M:              After M:

       ^  /                   ^    /
       | / v                  |   / M*v (other vectors rotate)
       |/                     |  /
    ---+------->           ---+--------->
       |                      |
       | u (eigenvector)      | M*u (same direction, just longer!)
       v                      v
                              v (scaled by lambda)
```

### Why would anyone care?

Eigenvalues reveal the **essential structure** of a matrix.

When the matrix is a graph's Laplacian:
- Eigenvalues = natural frequencies of the graph
- Eigenvectors = natural groupings of nodes

When the matrix is a covariance matrix (data):
- Eigenvalues = how much variance each direction explains
- Eigenvectors = the principal directions (PCA)

```
    Data cloud:                First eigenvector:

    *  *    *                  *  *    *
      * *  *  *                  * *--*--*----> (direction of
    *    *  *                  *    *  *          most spread)
       *   *                      *   *
    *        *                 *        *

    The eigenvector points along the direction of maximum variation.
    The eigenvalue tells you how spread out the data is in that
    direction.
```

### Dimensionality Reduction

If you have 100 features but the first 3 eigenvalues capture 95% of the
variance, you can safely ignore the other 97 dimensions.

```
    Eigenvalues (sorted):

    |****                          Top 3 capture most info.
    |  ***
    |    **
    |      **
    |        ****
    |            ***************   These are noise.
    +---------------------------
     1  2  3  4  5 ... 100

    Project data onto top 3 eigenvectors.
    100 dimensions --> 3 dimensions with minimal information loss.
```

---

## 10. Topology & Metric Spaces

### Metric Spaces

A metric space is a set of objects with a **distance function** that
satisfies three rules:

```
    1. d(A, B) >= 0            (distances are non-negative)
       d(A, A) = 0             (distance to yourself is zero)

    2. d(A, B) = d(B, A)       (symmetric — same distance both ways)

    3. d(A, C) <= d(A,B)+d(B,C)  (triangle inequality — no shortcuts)

          A
         / \
        3    5           d(A,C) must be <= 3 + 5 = 8
         \ /
      B---C
        ?
```

### Why would anyone care?

If you define a valid distance between code files (maybe based on shared
dependencies, textual similarity, or co-change frequency), you can use
any algorithm that works on metric spaces:

- Clustering (group nearby files)
- Nearest-neighbor search (find similar files)
- Outlier detection (files far from everything else)

But if your "distance" violates the triangle inequality, these algorithms
may give wrong answers.

### Persistent Homology (Topological Data Analysis)

This is a method for finding **shapes** in data. The idea:

1. Start with data points. Imagine each one is a tiny ball.
2. Slowly grow the radius of every ball.
3. Watch when balls start overlapping and forming connections.

```
    Radius = 0:          Radius = small:       Radius = large:

    .   .   .            .---.   .             .---.---.
                                               |       |
    .   .   .            .   .---.             .---.---.

    No structure.        Some connections.      A loop appeared!
```

Track when features (clusters, loops, voids) **appear** and **disappear**
as the radius grows. Features that persist across many radius values are
"real" structure. Features that appear and vanish quickly are noise.

```
    Persistence diagram:

    death
    |         * (noise: born late, dies quick)
    |    *
    |                  * (real feature: born early, persists long)
    |
    +-------------------
    birth

    Points far from the diagonal = real structure.
    Points near the diagonal = noise.
```

---

## 11. Process Mining & Sequence Analysis

### What is it?

Process mining treats **logs of events** as data and discovers patterns
in how things happen over time.

### Traces

A trace is a sequence of events:

```
    Trace 1: [Edit A] -> [Edit B] -> [Edit C] -> [Commit]
    Trace 2: [Edit A] -> [Edit C] -> [Commit]
    Trace 3: [Edit B] -> [Edit D] -> [Edit B] -> [Commit]
```

### Co-change Analysis

If two files frequently change in the same commit, they might be coupled
even if there's no import between them.

```
    Co-change matrix (how often files change together):

              A    B    C    D
         A  [ -   .8   .2   .1 ]
         B  [.8    -   .3   .0 ]
         C  [.2   .3    -   .9 ]
         D  [.1   .0   .9    - ]

    A and B change together 80% of the time --> strong coupling
    C and D change together 90% of the time --> strong coupling
    B and D never change together            --> independent
```

Now compare this to the structural dependency graph:

```
    Structural:              Co-change:

    A --> B                  A --- B  (expected: A imports B)
    C --> D                  C --- D  (expected: C imports D)
                             A ...B   (wait, B and C also
                             C ... D   co-change a lot but
                                       no structural link!)

    Co-change without structural dependency = hidden coupling.
    Structural dependency without co-change = maybe dead code.
```

### Association Mining

Find rules like: "When file A changes, file B changes 80% of the time."

```
    Support:    How often A and B change together (absolute frequency)
    Confidence: P(B changes | A changed) = co-changes / A-changes
    Lift:       Is the co-change more than random chance?

    If A changes in 100 commits and B also changed in 80 of those:
        Confidence = 80%
        If B changes in 200/1000 total commits (20% base rate):
        Lift = 80% / 20% = 4.0  (4x more likely than chance)
```

---

## 12. Dynamical Systems

### What is it?

The study of how systems **change over time** according to rules.

### State and Evolution

A system has a **state** (where it is now) and a **rule** for how it
changes.

```
    State at time 0:    [10 files, 50 dependencies, 2 modules]
    Rule:               each week, files grow by ~5%, deps by ~8%

    Time 0:  [10,  50,   2]
    Time 1:  [10,  54,   2]
    Time 2:  [11,  58,   2]
    Time 3:  [11,  63,   2]    <-- dependencies growing faster
    ...                             than files. Coupling increasing.
    Time 10: [16,  108,  2]    <-- still only 2 modules. Problem.
```

### Attractors

An attractor is a state that the system tends toward over time.

```
    Healthy attractor:          Unhealthy attractor:

    Coupling                    Coupling
    |    .                      |              .
    |   . .                     |            . .
    |  .   .                    |          .  .
    | .     .  .  .             |        .   .
    |.       ..  .. .           |     .    .
    |          ...   ...        |   .    .     "Big ball of mud"
    +--------------->           +---.---.----->
         time                        time

    System settles into          System drifts toward
    stable complexity.           increasing entanglement.
```

### Churn Hotspots

A file that changes constantly is a "hotspot." But not all churn is equal:

```
    Churn over time:

    Changes
    |  *        *
    |  *   *    *           File A: periodic spikes (feature work)
    |  *   *    *    *
    +--*---*----*----*-->

    Changes
    |
    |****                   File B: burst then stable (initial dev)
    |    ****
    |        **********
    +-------------------->

    Changes
    |     *   *  * *
    |  * * * * ** * **      File C: constant churn (unstable, problem)
    | ** * ** *  **  * *
    +-------------------->
```

The trajectory matters more than the total count. File C is the one
that needs attention — not because it changed the most, but because
it never stabilizes.

### Feedback Loops

When the output of a system feeds back into its input:

```
    Positive feedback (amplifying):

    Complex code --> more bugs --> more patches --> more complex code
         ^                                              |
         |______________________________________________|

    Negative feedback (stabilizing):

    Complex code --> refactoring triggered --> simpler code
         ^                                        |
         |________________________________________|
```

Identifying whether a codebase's dynamics have positive or negative
feedback loops tells you whether it's heading toward stability or
collapse.

---

## Summary: How These Connect

```
    MEASUREMENT THEORY          What can you validly compute?
          |
          v
    STATISTICS                  What does the data look like?
          |                     What distribution? What outliers?
          v
    INFORMATION THEORY          How complex/surprising is it?
          |
          v
    GRAPH THEORY                What's connected to what?
       /      \
      v        v
  SPECTRAL    COMMUNITY         What are the natural groupings?
  METHODS     DETECTION         Where are the boundaries?
      \        /
       v      v
    LINEAR ALGEBRA              Eigenvalues, projections,
          |                     dimensionality reduction
          v
    CATEGORY THEORY             Do summaries preserve structure?
    ABSTRACT ALGEBRA            Do aggregations follow valid rules?
          |
          v
    TOPOLOGY                    What's the shape of the space?
          |
          v
    PROCESS MINING              How does it change over time?
    DYNAMICAL SYSTEMS           Where is it heading?
```

Each layer builds on the ones above. Measurement theory constrains what
statistics you can compute. Statistics inform your graph metrics. Graph
structure is analyzed with linear algebra. Category theory ensures your
summaries are faithful. And temporal analysis tracks how all of this
evolves.
