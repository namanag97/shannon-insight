# Neuro-Symbolic AI: Complete Guide with Math

A comprehensive guide to understanding neuro-symbolic AI, from basic concepts to mathematical foundations.

---

## Table of Contents

1. [The Two Worlds](#the-two-worlds)
2. [Symbolic AI Basics](#symbolic-ai-basics)
3. [Neural Network Math](#neural-network-math-basics)
4. [The Fundamental Incompatibility](#the-fundamental-incompatibility)
5. [Approaches to Neuro-Symbolic Integration](#approaches-to-neuro-symbolic-integration)
6. [The Math of Differentiable Logic](#the-math-of-differentiable-logic)
7. [Neural + Fuzzy Logic Architecture](#neural--fuzzy-logic-architecture)
8. [DeepProbLog](#deepproblog---a-real-framework)
9. [Tensor Logic Networks](#tensor-logic-networks)
10. [Loss Functions for Neuro-Symbolic Systems](#loss-functions-for-neuro-symbolic-systems)
11. [Summary](#summary)

---

## The Two Worlds

### Neural (Subsymbolic)

| Aspect | Description |
|--------|-------------|
| **Representation** | Vectors of numbers |
| **Example** | `h = [0.2, -0.5, 0.8, 0.1, ...]` |
| **Operation** | Matrix multiplication, nonlinear functions, gradient descent |
| **Learning** | From data (examples) |
| **Strength** | Pattern recognition, perception |
| **Weakness** | No reasoning, black box |

### Symbolic (Logic-based)

| Aspect | Description |
|--------|-------------|
| **Representation** | Discrete symbols, rules |
| **Example** | `dog(X)`, `cat(Y)`, `sits_on(X, Y)` |
| **Operation** | Logical inference (AND, OR, NOT), rule application |
| **Learning** | From rules (humans define) |
| **Strength** | Reasoning, interpretability |
| **Weakness** | Can't handle noise, needs rules |

**Neuro-Symbolic = Combine them!**

---

## Symbolic AI Basics

### Symbols

A symbol is a discrete entity with meaning:

- **Constants**: `dog`, `cat`, `red`, `big`
- **Variables**: `X`, `Y`, `Z`
- **Predicates**: `animal(X)`, `color(X, red)`
- **Functions**: `father_of(X)`, `size(Y)`

### Propositional Logic

Simple true/false statements:

```
p = "It is raining"        (True or False)
q = "I have an umbrella"   (True or False)
```

**Operations:**

| Operation | Symbol | Name |
|-----------|--------|------|
| NOT p | `¬p` | Negation |
| p AND q | `p ∧ q` | Conjunction |
| p OR q | `p ∨ q` | Disjunction |
| p IMPLIES q | `p → q` | Implication |

**Truth Tables:**

| p | q | p ∧ q | p ∨ q | p → q |
|---|---|-------|-------|-------|
| T | T | T | T | T |
| T | F | F | T | F |
| F | T | F | T | T |
| F | F | F | F | T |

### First-Order Logic (FOL)

More powerful - can talk about objects and relations:

**Predicates:**
```
dog(fido)         → "fido is a dog"
animal(X)         → "X is an animal"
loves(X, Y)       → "X loves Y"
```

**Quantifiers:**
- `∀X` (for all X)
- `∃X` (there exists X)

**Examples:**
```
∀X: dog(X) → animal(X)
"All dogs are animals"

∃X: dog(X) ∧ name(X, fido)
"There exists a dog named Fido"

∀X∀Y: parent(X,Y) → ancestor(X,Y)
"If X is parent of Y, X is ancestor of Y"
```

**Inference:**

Given:
- `dog(fido)`
- `∀X: dog(X) → animal(X)`

Deduce: `animal(fido)`

This is **logical reasoning** - neural networks can't do this natively!

---

## Neural Network Math Basics

A neural network is a function:

```
f(x; θ) = output

x = input (e.g., image pixels)
θ = parameters (weights and biases)
```

### Single Neuron

```
y = σ(w·x + b)
    │  │   │
    │  │   └── bias (scalar)
    │  └── weights (vector)
    └── activation function
```

Where:
- `x = [x₁, x₂, ..., xₙ]` (input vector)
- `w = [w₁, w₂, ..., wₙ]` (weight vector)
- `w·x = Σᵢ wᵢxᵢ` (dot product)
- `σ(z)` = activation function

**Common activations:**

| Name | Formula |
|------|---------|
| Sigmoid | `σ(z) = 1/(1 + e⁻ᶻ)` |
| ReLU | `σ(z) = max(0, z)` |
| Tanh | `σ(z) = (eᶻ - e⁻ᶻ)/(eᶻ + e⁻ᶻ)` |

### Full Layer

```
h = σ(Wx + b)
    │  │   │
    │  │   └── bias vector
    │  └── weight MATRIX
    └── activation (applied element-wise)
```

- `W` is m×n matrix (n inputs → m outputs)
- `b` is m-dimensional vector
- `h` is m-dimensional output

### Multi-Layer Network

```
h₁ = σ₁(W₁x + b₁)     (layer 1)
h₂ = σ₂(W₂h₁ + b₂)    (layer 2)
h₃ = σ₃(W₃h₂ + b₃)    (layer 3)
y = softmax(W₄h₃ + b₄) (output layer)

Composition: y = f₄(f₃(f₂(f₁(x))))
```

---

## The Fundamental Incompatibility

| Property | Neural | Symbolic |
|----------|--------|----------|
| **Type** | Continuous | Discrete |
| **Example** | `h = [0.2, 0.8, ...]` | `p = True/False` |
| **Differentiability** | `∂L/∂w` exists | `∂(p ∧ q)/∂p = ???` |
| **Meaning** | Distributed across dimensions | Localized in symbols |
| **Concepts** | No explicit concepts | Explicit concepts |

**The Challenge:**

```
Neural output: h = [0.2, 0.8, -0.3, 0.5]

How do we get: dog(X) → True
               cat(X) → False
               animal(X) → True

The vector doesn't tell us what it means!
```

---

## Approaches to Neuro-Symbolic Integration

### Approach 1: Neural → Symbolic (Extraction)

```
Image → [Neural Net] → Vector → [Extract] → Symbols
                                │
                                ▼
                      Find concepts in vector
```

**Example:**
```
h = [0.2, 0.8, ...]
Extract: h[5:10] → "dog"
         h[15:20] → "brown"
         h[25:30] → "running"

Result: dog(X) ∧ brown(X) ∧ running(X)
```

### Approach 2: Symbolic → Neural (Embedding)

```
Symbols → [Embed] → Vector → [Neural Net] → Output
            │
            ▼
  Convert symbols to vectors
```

**Example:**
```
"dog" → v_dog = [0.5, -0.2, 0.8, ...]
"cat" → v_cat = [0.4, 0.1, 0.7, ...]
"dog loves cat" → v_dog ⊕ v_loves ⊕ v_cat

This is what word2vec, BERT, etc. do!
```

### Approach 3: Parallel (Side-by-Side)

```
Image ──→ [Neural] ──→ Prediction 1
   │                              │
   │                              ▼
   │                         [Combine] → Final
   │                              ▲
   │                              │
   └──→ [Extract → Symbolic] → Pred 2
```

Both systems work on same input, predictions are combined.

### Approach 4: Integrated (Differentiable Logic)

```
Make logic DIFFERENTIABLE so it can be trained!

p ∧ q  becomes  fuzzy_and(p, q)
p ∨ q  becomes  fuzzy_or(p, q)
¬p     becomes  1 - p

Now gradients flow through logic!
```

---

## The Math of Differentiable Logic

### The Problem

Traditional logic:
```
p ∧ q = 1 if both true, 0 otherwise
```

This is **NOT differentiable!**
- The gradient is 0 everywhere
- Undefined at boundaries

### The Solution: Fuzzy Logic

Instead of `{0, 1}`, use continuous values `[0, 1]`

#### Fuzzy AND (Product T-Norm)

```
p ∧̃ q = p · q
```

**Example:**
```
p = 0.8 (80% confident "dog")
q = 0.6 (60% confident "running")
p ∧̃ q = 0.8 × 0.6 = 0.48
        (48% confident "dog AND running")
```

**Gradient:**
```
∂(p·q)/∂p = q  ✓ Differentiable!
∂(p·q)/∂q = p  ✓ Differentiable!
```

#### Fuzzy OR (Probabilistic Sum)

```
p ∨̃ q = p + q - p·q
      = 1 - (1-p)(1-q)
```

**Example:**
```
p = 0.8 (80% confident "dog")
q = 0.6 (60% confident "cat")
p ∨̃ q = 0.8 + 0.6 - 0.48 = 0.92
        (92% confident "dog OR cat")
```

**Gradient:**
```
∂(p∨̃q)/∂p = 1 - q  ✓ Differentiable!
∂(p∨̃q)/∂q = 1 - p  ✓ Differentiable!
```

#### Fuzzy NOT

```
¬̃p = 1 - p
```

**Example:**
```
p = 0.8 (80% confident "dog")
¬̃p = 1 - 0.8 = 0.2
      (20% confident "NOT dog")
```

**Gradient:**
```
∂(1-p)/∂p = -1  ✓ Differentiable!
```

#### Fuzzy Implication (Reichenbach)

```
p →̃ q = 1 - p + p·q
```

**Example:**
```
p = 0.8 (dog), q = 0.9 (animal)
p →̃ q = 1 - 0.8 + 0.8×0.9 = 0.92
        (92% confident "dog → animal")
```

---

## Neural + Fuzzy Logic Architecture

**Example: Is this a dangerous animal?**

### Step 1: Neural Network extracts features

```
Image → [CNN] → h = [0.2, 0.8, ...]
```

### Step 2: Convert features to fuzzy predicates

```
P(dog)     = σ(w₁·h + b₁) = 0.85
P(snake)   = σ(w₂·h + b₂) = 0.10
P(venomous)= σ(w₃·h + b₃) = 0.05
P(angry)   = σ(w₄·h + b₄) = 0.70
```

### Step 3: Apply fuzzy logic rules

```
Rule 1: dog ∧ angry → dangerous
Rule 2: snake ∧ venomous → dangerous

Compute:
P(dangerous₁) = P(dog) · P(angry)
              = 0.85 × 0.70 = 0.595

P(dangerous₂) = P(snake) · P(venomous)
              = 0.10 × 0.05 = 0.005

P(dangerous) = P(dangerous₁) ∨ P(dangerous₂)
             = 0.595 + 0.005 - 0.595×0.005
             ≈ 0.597

Output: 59.7% confident this is dangerous
```

**The beauty:** Everything is differentiable! Can train end-to-end with gradient descent.

---

## DeepProbLog - A Real Framework

Problog is probabilistic logic programming. DeepProbLog adds neural networks.

### Basic Idea

```
nn(network_id, input, output)
This calls a neural network!
```

**Example:**

```prolog
% Neural predicate: classify digit
digit(X, Y) :- nn(digit_net, X, Y).

% Symbolic rule: addition
addition(X1, X2, Y) :-
    digit(X1, D1),
    digit(X2, D2),
    Y is D1 + D2.
```

**Meaning:**
"To add two images:
1. Use neural net to classify first image
2. Use neural net to classify second image
3. Add the results symbolically"

### The Math

**Query:** What is `P(addition(img1, img2, 7))`?

**Proof paths:**
```
img1 → 3 (prob 0.8)
img2 → 4 (prob 0.7)
3 + 4 = 7 ✓

P(addition(img1, img2, 7))
= P(digit(img1,3) ∧ digit(img2,4))
= 0.8 × 0.7 = 0.56
```

**Training:**
```
Maximize P(correct_answer)
Backprop through both logic AND neural net
```

---

## Tensor Logic Networks

Another approach: Encode logic operations as tensor ops.

### Grounding: Convert predicates to tensors

**Example domain:** `{alice, bob, charlie}`

**Predicate `likes(X, Y)`:**

```
        alice  bob   charlie
alice  [  1     1      0   ]
bob    [  0     1      1   ]  ← 3×3 matrix
charlie[  1     0      1   ]
```

This is a **TENSOR** representation!

### Logical Inference as Matrix Operations

**Rule:** `likes(X, Y) ∧ likes(Y, Z) → friends(X, Z)`

**In matrix form:**
```
friends = likes × likesᵀ
```

**Example:**
```
likes = [[1, 1, 0],
         [0, 1, 1],
         [1, 0, 1]]

friends = likes × likesᵀ
        = [[2, 1, 1],
           [1, 2, 1],
           [1, 1, 2]]

Threshold at 1:
friends = [[1, 1, 1],
           [1, 1, 1],
           [1, 1, 1]]

Everyone is (transitively) friends!
```

### With Neural Networks

```
likes(X, Y) is predicted by neural net

likes = neural_net(features)  → soft tensor
      = [[0.9, 0.8, 0.2],
         [0.1, 0.9, 0.7],
         [0.8, 0.3, 0.9]]

friends = likes × likesᵀ
        (differentiable!)

Can train the whole system end-to-end!
```

---

## Loss Functions for Neuro-Symbolic Systems

### Loss 1: Supervised Classification with Logic

**Given:**
- Neural prediction: `ŷ = f(x; θ)`
- Logic constraint: `C(ŷ)`
- Ground truth: `y`

**Loss:**
```
L = L_task + λ · L_logic

Where:
L_task = CrossEntropy(ŷ, y)
L_logic = 1 - C(ŷ)
```

**Example constraint:** "If dog, then animal"
```
C = 1 - max(0, P(dog) - P(animal))

If P(dog) = 0.9, P(animal) = 0.7
C = 1 - max(0, 0.9 - 0.7) = 1 - 0.2 = 0.8
(violated, high loss)

If P(dog) = 0.9, P(animal) = 0.95
C = 1 - max(0, 0.9 - 0.95) = 1 - 0 = 1
(satisfied, low loss)
```

### Loss 2: Semantic Loss

Encode propositional formula φ as circuit. Measure how much probability mass violates φ.

```
L_semantic = -log P(φ)

Where P(φ) is computed using arithmetic circuits
```

**Example:** `φ = "exactly one of {a, b, c} is true"`

```
P(φ) = P(a)(1-P(b))(1-P(c)) +
       (1-P(a))P(b)(1-P(c)) +
       (1-P(a))(1-P(b))P(c)

This is differentiable!
```

### Loss 3: Knowledge Distillation

Neural network learns to imitate symbolic system.

```
L_distill = KL(teacher || student)

Where:
teacher = symbolic reasoner
student = neural network

Benefit: Neural net learns to be consistent
         with symbolic reasoning
```

---

## Summary

### Key Insight: Make Logic Differentiable

| Symbolic | Fuzzy/Neural |
|----------|--------------|
| `p ∧ q` (discrete) | `p · q` (product) |
| `p ∨ q` (discrete) | `p + q - p·q` (probabilistic) |
| `¬p` (discrete) | `1 - p` (complement) |
| `p → q` (discrete) | `1 - p + p·q` (implication) |
| `∀x: P(x)` | `min_x P(x)` or mean |
| `∃x: P(x)` | `max_x P(x)` or sum |

### Architecture

```
Input → [Neural Net] → Fuzzy Predicates → [Logic] → Output
                              │
                              ▼
                        Differentiable!
                              │
                              ▼
                   Can train end-to-end
```

### Benefits

- ✅ Learning from data (neural)
- ✅ Reasoning with rules (symbolic)
- ✅ Interpretable (can trace logic)
- ✅ Data efficient (rules guide learning)

---

## Key Papers to Read

### On Disentanglement
- β-VAE (Higgins et al., 2017)
- FactorVAE (Kim & Mnih, 2018)
- A Framework for Disentanglement (Locatello et al., 2019)

### On Concept Learning
- Concept Bottleneck Models (Koh et al., 2020)
- TCAV: Interpretability Beyond Feature Attribution (Kim et al., 2018)
- Network Dissection (Bau et al., 2017)

### On Neuro-Symbolic
- Neural-Symbolic VQA (Yi et al., 2018)
- DeepProbLog (Manhaeve et al., 2018)
- DreamCoder (Ellis et al., 2021)

### On Slot Attention
- Object-Centric Learning with Slot Attention (Locatello et al., 2020)

---

## Further Reading

- [MAP-Elites Paper](https://arxiv.org/abs/1504.04909)
- [DreamFusion: SDS for 3D](https://arxiv.org/abs/2209.14988)
- [I-JEPA: Self-Supervised Learning](https://arxiv.org/abs/2301.08243)
- [Information Bottleneck Method](https://arxiv.org/abs/physics/0004057)
