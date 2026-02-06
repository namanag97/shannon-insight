# semantics/ -- Naming Drift

## Overview

Naming drift measures the alignment between a file's **name** and its **content**. A file named `auth_service.py` should contain authentication and service-related code. When the filename tells one story and the code tells another, the file has been repurposed without being renamed -- a maintenance smell.

This computes signal #11 (`naming_drift`) from registry/signals.md. Dimension: D3 NAMING.

## Formula

```
naming_drift = 1 - cosine_similarity(tfidf(filename_tokens), tfidf(content_concept_tokens))
```

See registry/signals.md #11 for the canonical definition. This document specifies the computation.

## Interpretation

| naming_drift | Meaning |
|-------------|---------|
| 0.0 | Perfect alignment -- filename accurately describes content. |
| 0.0 - 0.3 | Good alignment. Normal range for well-maintained code. |
| 0.3 - 0.7 | Moderate misalignment. File may have grown beyond its original scope. |
| 0.7 - 1.0 | Severe misalignment. Filename is misleading. Smell. |
| None | Not computable (file has < 20 unique identifiers). |

The absolute threshold in registry/signals.md is `> 0.7` (high drift = smell).

## Computation Steps

### Step 1: Extract Filename Tokens

Take the file's basename (no directory, no extension) and split it into tokens using the same normalization rules as concept extraction:

```
"auth_service.py"       -> stem: "auth_service"    -> tokens: ["auth", "service"]
"UserRepository.java"   -> stem: "UserRepository"  -> tokens: ["user", "repository"]
"http_utils.go"         -> stem: "http_utils"       -> tokens: ["http", "utils"]
"__init__.py"           -> stem: "__init__"          -> tokens: []  (excluded, naming_drift = None)
"models.py"             -> stem: "models"            -> tokens: ["models"]
"index.ts"              -> stem: "index"             -> tokens: ["index"]
```

**Splitting rules** (same as `concept-extraction.md` Step 2):
1. Split on `_` (snake_case).
2. Split on camelCase boundaries.
3. Split on acronym boundaries.
4. Lowercase all tokens.
5. Remove programming stopwords (`get`, `set`, `create`, etc.).

**Special cases**:
- `__init__.py`, `__main__.py`, `mod.rs`, `index.ts`, `index.js`: These are structural filenames with no semantic content. Set `naming_drift = None`.
- Single generic token (`models`, `utils`, `helpers`, `types`, `constants`): These are intentionally vague. Compute normally but expect low drift since the token is broad.

### Step 2: Extract Content Concept Tokens

Collect all tokens from the file's extracted concepts, weighted by concept weight:

```
content_tokens = {}
for concept in file_semantics.concepts:
    for token in concept.tokens:
        content_tokens[token] = content_tokens.get(token, 0) + concept.weight
```

This produces a weighted token bag representing what the file is *actually* about according to concept extraction.

**Prerequisite**: Concept extraction must have succeeded (file has 20+ unique identifiers). If concepts are empty, `naming_drift = None`.

### Step 3: Build TF-IDF Vectors

Both filename tokens and content concept tokens are projected into the same TF-IDF vector space using the **corpus-wide IDF weights** computed in Pass 1 of the SemanticAnalyzer.

**Filename vector**:
```
For each filename token t:
    filename_vec[t] = 1.0 * idf(t)

# All filename tokens get tf = 1.0 (equal weight within the filename).
# IDF still applies -- a filename token that appears in every file
# (like "utils") gets low weight.
```

**Content vector**:
```
For each content token t with aggregated weight w:
    content_vec[t] = w * idf(t)
```

Both vectors live in the same token space. They are sparse (most entries are zero).

### Step 4: Cosine Similarity

```
similarity = dot(filename_vec, content_vec) / (norm(filename_vec) * norm(content_vec))
naming_drift = 1 - similarity
```

If either vector has zero norm (no tokens after filtering), `naming_drift = None`.

**Implementation note**: Both vectors are sparse dictionaries. The dot product only iterates over tokens present in both vectors:

```python
dot = sum(filename_vec[t] * content_vec[t] for t in filename_vec if t in content_vec)
norm_f = sqrt(sum(v ** 2 for v in filename_vec.values()))
norm_c = sqrt(sum(v ** 2 for v in content_vec.values()))

if norm_f == 0 or norm_c == 0:
    return None

similarity = dot / (norm_f * norm_c)
naming_drift = 1.0 - similarity
```

## Examples

### Low drift (good)

File: `auth_service.py`

Filename tokens: `["auth", "service"]`

Content concepts:
- Concept("authenticate", tokens=["auth", "verify", "token", "session"], weight=0.7)
- Concept("password", tokens=["hash", "password", "salt"], weight=0.3)

Content token vector includes `auth` with weight `0.7 * idf("auth")`.

Filename vector includes `auth` with weight `1.0 * idf("auth")`.

Overlap on "auth" produces high cosine similarity. `naming_drift ~ 0.15`.

### High drift (smell)

File: `auth_service.py`

Content concepts:
- Concept("cache", tokens=["cache", "redis", "ttl", "evict"], weight=0.5)
- Concept("payment", tokens=["payment", "invoice", "charge", "stripe"], weight=0.5)

No content tokens overlap with filename tokens `["auth", "service"]`.

`naming_drift ~ 0.95`. The file has been repurposed.

### Moderate drift (scope creep)

File: `user_manager.py`

Content concepts:
- Concept("user", tokens=["user", "profile", "email"], weight=0.4)
- Concept("notification", tokens=["notify", "email", "template", "send"], weight=0.3)
- Concept("permission", tokens=["role", "access", "permission", "admin"], weight=0.3)

Overlap on "user" but notification and permission concepts are unrelated to filename.

`naming_drift ~ 0.55`. The file started as user management and grew to include notification and permission logic.

## Temporal Behavior

Naming drift changes over time as file content evolves while the filename stays the same:

```
naming_drift(f, t0) = 0.10   # file matches its name at creation
naming_drift(f, t1) = 0.25   # new concept added (scope creep begins)
naming_drift(f, t2) = 0.40   # another concept, filename increasingly misleading
naming_drift(f, t3) = 0.65   # original concept now minority of content
```

**Rising naming_drift trend** is a strong indicator of unmanaged scope creep. The delta and velocity temporal operators (see registry/temporal-operators.md) are meaningful for this signal:

- `delta(naming_drift)` > 0.1 in one snapshot: a significant content shift occurred.
- `velocity(naming_drift)` > 0: content is drifting away from the filename.
- `trend(naming_drift)` = WORSENING: naming drift increasing over time (since high is bad).

## Edge Cases

| Case | Behavior | Rationale |
|------|----------|-----------|
| File has < 20 unique identifiers | `naming_drift = None` | Concept extraction did not run; no content vector to compare. |
| Filename is `__init__.py` or `index.ts` | `naming_drift = None` | Structural filenames carry no semantic expectation. |
| Filename tokens are all stopwords | `naming_drift = None` | Nothing to compare after filtering. |
| Content tokens have zero overlap with filename | `naming_drift ~ 1.0` | Maximum drift. File is completely misnamed. |
| Single filename token matches single concept | `naming_drift ~ 0.0` | Ideal alignment. |
| File has only one concept token matching filename | Low drift | Even partial overlap reduces drift substantially via cosine similarity. |

## Relationship to Other Signals

Naming drift is most useful when combined with:

- **concept_count** (#9): High concept_count + high naming_drift = file has grown to cover topics not reflected in its name.
- **concept_entropy** (#10): High entropy + high drift = unfocused file with a misleading name.
- **role** (#8): A file classified as UTILITY named `auth_service` has a naming/role mismatch (different from naming drift, which measures content concepts vs filename).
- **total_changes** (#27): High churn + rising drift = active development is pushing the file away from its original purpose.
