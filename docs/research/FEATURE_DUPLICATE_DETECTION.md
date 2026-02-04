# Duplicate Code Detection - Research Document

## Executive Summary

Duplicate code detection, also known as clone detection (CCD), is a critical software engineering technique for identifying repeated code fragments across a codebase. Duplicate code (code clones) represents a significant maintenance burden, increases technical debt, and can lead to inconsistencies when bugs are fixed in one copy but not propagated to others.

Modern codebases often contain 5-20% duplicate code, particularly in large software projects with multiple developers and copy-paste programming practices. Effective duplicate detection tools must balance accuracy with performance, detecting all three major clone types across multiple programming languages.

This document provides comprehensive research findings on implementing language-agnostic duplicate code detection systems, covering mathematical foundations, clone classification, algorithms, and implementation strategies.

## Table of Contents

1. [Clone Types Classification](#clone-types-classification)
2. [Mathematical Foundations](#mathematical-foundations)
3. [Token-Based vs AST-Based Approaches](#token-based-vs-ast-based-approaches)
4. [Language-Agnostic Design](#language-agnostic-design)
5. [Detection Algorithms](#detection-algorithms)
6. [Clone Types in Detail](#clone-types-in-detail)
7. [Implementation Guidance](#implementation-guidance)
8. [Code Examples](#code-examples)
9. [References](#references)

---

## Clone Types Classification

Code clones are traditionally classified into three types based on the degree of similarity:

### Type 1: Exact Clones
**Definition:** Identical or nearly identical code fragments, differing only in whitespace, comments, or layout.

**Characteristics:**
- 100% syntactic match after normalization
- Variable names may be different (renamed)
- Only trivial formatting differences
- Example: Copy-paste with minor formatting changes

**Detection Complexity:** O(n) - O(n²)

**Use Cases:**
- Detecting copy-paste programming
- Identifying duplicated utilities/helper functions
- Finding repeated code blocks across files

### Type 2: Near-Miss Clones (Type 2)
**Definition:** Syntactically similar code fragments with minor modifications such as renamed variables, different literals, or added statements.

**Characteristics:**
- 90-95% syntactic similarity
- Variables may be renamed
- Constants may be changed
- Statement order may be slightly modified
- Minor control flow changes

**Detection Complexity:** O(n) - O(n³) depending on algorithm

**Use Cases:**
- Detecting code adapted to different contexts
- Finding implementations of similar algorithms
- Identifying boilerplate code with minor customizations

### Type 3: Semantic Clones (Type 3)
**Definition:** Functionally equivalent code fragments with potentially different implementations.

**Characteristics:**
- Same functional behavior/logic
- Different syntactic structure
- Different algorithms for same task
- Variable names and implementations differ significantly

**Detection Complexity:** O(n²) - O(n⁴) or undecidable in general case

**Use Cases:**
- Finding different implementations of same algorithms
- Detecting equivalent code across languages
- Identifying library alternatives implementing same functionality

---

## Mathematical Foundations

### String Similarity Metrics

#### Levenshtein Distance

**Formula:**

For strings A = a₁a₂...aₙ and B = b₁b₂...bₘ:

```
lev(a,b) = {
    |a| if |b| = 0,
    |b| if |a| = 0,
    lev(tail(a), tail(b)) if head(a) = head(b),
    1 + min(lev(tail(a), b), lev(a, tail(b)), lev(tail(a), tail(b))) otherwise
}
```

**Complexity:** O(m × n) where m = |A|, n = |B|

**Dynamic Programming Implementation:**
```
function levenshteinDistance(A, B):
    m = len(A)
    n = len(B)
    
    # Create (m+1) x (n+1) matrix
    d = [[0 for j in range(n+1)] for i in range(m+1)]
    
    for i in range(1, m+1):
        d[i][0] = i
        for j in range(1, n+1):
            if A[i-1] == B[j-1]:
                cost = 0
            else:
                cost = 1
            d[i][j] = min(
                d[i-1][j] + 1,      # deletion
                d[i][j-1] + 1,      # insertion
                d[i-1][j-1] + cost    # substitution
            )
    
    return d[m][n]
```

**Application:** Useful for Type 2 clone detection, measuring similarity between code fragments with minor modifications.

#### Jaccard Index

**Formula:**

For sets A and B:

```
J(A,B) = |A ∩ B| / |A ∪ B| = |A ∩ B| / (|A| + |B| - |A ∩ B|)
```

**Jaccard Distance:**
```
d_J(A,B) = 1 - J(A,B) = |A ∪ B| - |A ∩ B| / |A ∪ B|
```

**Complexity:** O(min(|A|, |B|)) for set intersection and union

**Weighted Jaccard (for multisets/token bags):**
```
J_W(x, y) = Σ_i min(x_i, y_i) / Σ_i max(x_i, y_i)
```

**Application:** Token-based clone detection, comparing sets of tokens between code fragments.

#### Cosine Similarity

**Formula:**

For vectors A = (a₁, a₂, ..., aₙ) and B = (b₁, b₂, ..., bₙ):

```
cos_sim(A, B) = (A · B) / (||A|| × ||B||) = Σ_i (a_i × b_i) / (Σ_i a_i² × Σ_i b_i²)
```

**Cosine Distance:**
```
cos_dist(A, B) = 1 - cos_sim(A, B)
```

**Angular Distance (proper metric):**
```
angular_dist(A, B) = arccos(cos_sim(A, B)) / π
angular_sim(A, B) = 1 - angular_dist(A, B)
```

**Complexity:** O(n) for sparse vectors, O(d) where d is dimensionality

**Application:** TF-IDF token similarity, feature-based clone detection, Type 3 semantic analysis.

#### Dice-Sørensen Coefficient

**Formula:**
```
DSC(A, B) = 2 × |A ∩ B| / (|A| + |B|)
```

**Complexity:** O(min(|A|, |B|))

**Application:** Token overlap similarity, sensitive to set sizes.

### Information Theory in Clone Detection

#### Normalized Compression Distance (NCD)

Based on Kolmogorov complexity, measuring how much a pair of code fragments compresses together:

```
C(x,y) = (K(x) + K(y) - K(x,y)) / K(xy)
```

Where K(z) is the compressed size of z using a compression algorithm.

**Application:** Type 3 semantic similarity detection, finding functionally equivalent code.

#### Shannon Entropy

Measuring code diversity using information entropy:

```
H(X) = -Σ_i p(x_i) × log₂(p(x_i))
```

Where p(x_i) is the probability of token x_i in the code.

**Application:** Assessing code uniqueness, identifying boilerplate code.

### Statistical Fingerprinting

#### Rolling Hash (Rabin Fingerprint)

Enables O(1) hash computation for sliding windows:

```
hash(s[i+1..i+m]) = ((hash(s[i..i+m-1]) - s[i] × base^{m-1} mod p + s[i+m-1]) mod p
```

Where:
- base is alphabet size (e.g., 256 for ASCII)
- p is a large prime
- m is window length

**Complexity:** O(n) for all rolling hashes

**Application:** Rabin-Karp string matching, Type 1 and Type 2 clone detection.

#### N-gram Analysis

Breaks code into overlapping subsequences of length n:

```
tokens_ngram(code, n) = {(code[i:i+n]) : i ∈ [0, len(code)-n]}
```

**Application:** Fast similarity comparison using n-gram Jaccard similarity.

---

## Token-Based vs AST-Based Approaches

### Token-Based Clone Detection

**Overview:** Converts source code to sequences of tokens and compares them using string matching algorithms.

**Advantages:**
- Fast O(n) to O(n²) complexity
- Language-agnostic after tokenization
- Detects Type 1 and Type 2 clones effectively
- Memory efficient
- Easy to implement with existing string algorithms

**Disadvantages:**
- Ignores semantic structure (control flow, data flow)
- May produce false positives in structurally similar but semantically different code
- Cannot detect Type 3 semantic clones reliably

**Tokenization Process:**
1. Remove comments
2. Remove whitespace
3. Normalize string literals
4. Tokenize using language-specific rules
5. Generate token stream: `[keyword, identifier, operator, literal, ...]`

**Example Token Types:**
- Keywords: `if`, `while`, `for`, `return`, `class`
- Identifiers: `variableName`, `functionName`, `ClassName`
- Operators: `+`, `-`, `*`, `/`, `=`, `==`
- Delimiters: `{`, `}`, `[`, `]`, `(`, `)`, `;`
- Literals: strings, numbers, booleans

**Token-Based Algorithm Examples:**
1. **CPD (Clone Pairs Detection):** Uses n-gram counting and suffix tree
2. **Baker's Algorithm:** Uses parameterized matching on token sequences
3. **Token Set Jaccard:** Direct Jaccard similarity on token sets

### AST-Based Clone Detection

**Overview:** Parses code into Abstract Syntax Trees and compares structural patterns.

**Advantages:**
- Captures semantic structure and relationships
- Robust to formatting and identifier renaming
- Can detect Type 3 semantic clones
- Supports anti-unification for pattern extraction
- Language-specific but more semantically accurate

**Disadvantages:**
- Slower O(n²) to O(n³) due to parsing
- Requires language-specific parsers
- More complex to implement
- Higher memory overhead

**AST Node Types for Clone Detection:**
- **Statement Nodes:** Control flow structures (if, while, for, try-catch)
- **Expression Nodes:** Arithmetic, logical, method calls
- **Declaration Nodes:** Variable declarations, function definitions
- **Type Nodes:** Type annotations, class/interface declarations

**AST Comparison Methods:**
1. **Subtree Isomorphism:** Exact structural match
2. **Anti-Unification:** Parameterized pattern matching
3. **Metric Calculation:** Tree edit distance between ASTs
4. **Fingerprinting:** Tree digest hashes

### Hybrid Approaches

**Token-AST Hybrid:**
- Use token-based for fast candidate detection
- Use AST-based for verification and Type 3 detection

**PDG (Program Dependence Graph) Based:**
- More sophisticated than AST
- Captures data and control dependencies
- Higher accuracy for semantic clones
- Complexity: O(n³) or worse

---

## Language-Agnostic Design

### Universal Tokenization Strategy

#### Normalization Techniques

1. **Comment Removal:**
   - Single-line: `//`
   - Multi-line: `/* ... */`, `# ... #`, `<!-- ... -->`
   - Language-specific: `"""`, `'''` in Python, `/* */` in C

2. **Whitespace Normalization:**
   - Spaces, tabs, newlines → single space
   - Preserve indentation as structural marker if needed
   - Remove trailing/leading whitespace from lines

3. **String Literal Normalization:**
   - Escape sequences: `\n`, `\t`, `\r`, `\\`
   - Different quote styles: `'` vs `"`
   - Character encoding normalization (Unicode)

4. **Identifier Normalization (Optional):**
   - For Type 2 detection: map identifiers to generic names
   - Preserve type information: `variableN`, `functionM`
   - Example: `userName`, `emailAddr` → `id1`, `id2`

#### Language-Independent Token Categories

**Universal Token Set (simplified):**
```
{
  "keywords": ["if", "else", "while", "for", "return", "break", "continue", "class", "function", "var", "let", "const"],
  "operators": ["+", "-", "*", "/", "%", "=", "==", "!=", "<=", ">", "<", ">=", "&&", "||", "!", "++", "--"],
  "delimiters": ["(", ")", "{", "}", "[", "]", ";", ",", ".", ":", "->", "::"],
  "literals": ["string", "number", "boolean", "null", "undefined", "true", "false"]
}
```

**Language-Specific Extensions:**
- C/C++: `struct`, `enum`, `typedef`, `#include`
- Java: `import`, `package`, `interface`, `extends`, `implements`
- Python: `def`, `class`, `import`, `from`, `as`
- JavaScript: `var`, `let`, `const`, `function`, `=>`, `=>`
- Go: `type`, `struct`, `interface`, `go`, `chan`

#### Cross-Language Clone Detection

**Challenges:**
- Different syntax for same concept (e.g., list comprehensions vs loops)
- Different standard libraries and idioms
- Different error handling patterns

**Approaches:**
1. **Token-Based with Language-Specific Rules:** Detect language-specific constructs
2. **Intermediate Representation:** Convert to common intermediate (e.g., control flow graphs)
3. **Semantic Signatures:** Use function call graphs, API usage patterns

### Universal Similarity Metrics

**Token Overlap Metrics (Language-Agnostic):**

1. **Jaccard on Token Sets:**
   ```
   similarity = len(tokens_A ∩ tokens_B) / len(tokens_A ∪ tokens_B)
   ```

2. **N-gram Cosine Similarity:**
   - Build TF-IDF vectors from n-grams
   - Compute cosine similarity
   - Works across languages

3. **Rabin-Karp Fingerprint Comparison:**
   - Compute rolling hashes of token sequences
   - Compare hash values for exact matches
   - O(n) similarity check

---

## Detection Algorithms

### Suffix Tree Based Detection

**Overview:** Suffix trees enable efficient substring search for exact and approximate matches.

**Properties:**
- Construction: O(n) time, O(n) space
- Search: O(m) where m is pattern length
- Finds longest repeated substrings efficiently
- Supports approximate matching with mismatches

**Application to Clone Detection:**

1. **Build Generalized Suffix Tree:**
   ```
   tokens = tokenize(code)
   gst = build_suffix_tree(tokens)
   
   def find_longest_common_substrings(gst):
       # Find nodes with multiple child paths
       # Each represents a repeated token sequence
   ```

2. **Suffix Tree Construction (Ukkonen's Algorithm):**
   ```python
   def build_suffix_tree(s):
       n = len(s)
       # Build tree incrementally with suffix links
       # O(n) time complexity
   ```

3. **LCP Array with Suffix Array:**
   - Build suffix array: O(n log n)
   - Build LCP (Longest Common Prefix) array: O(n)
   - Find maximal repeats: O(n)

**Pros:**
- Very fast for Type 1 clones
- Efficient memory usage
- Works well with token sequences

**Cons:**
- Complex to implement
- Primarily for exact matches
- Requires linear-time preprocessing

### Rabin-Karp Rolling Hash

**Overview:** Uses rolling hash for efficient pattern matching, extended to clone detection.

**Algorithm:**
```
function rabinKarp(text, patterns):
    n = len(text)
    m = len(patterns)
    base = 256  # ASCII
    mod = 101  # Small prime for demo
    
    # Precompute pattern hashes
    pattern_hashes = {hash(p) for p in patterns}
    
    # Rolling hash through text
    text_hash = hash(text[0:m])
    for i in range(0, n-m+1):
        if text_hash in pattern_hashes:
            # Verify match
            if text[i:i+m] in patterns:
                return (i, pattern)
        # Update rolling hash
        if i + m < n:
            # Remove old character
            text_hash = (text_hash - ord(text[i]) * base**(m-1)) % mod
            # Add new character
            text_hash = (text_hash * base + ord(text[i+m])) % mod
    
    return None
```

**Application:**
- Multi-pattern clone detection
- Fast Type 1 and Type 2 candidate filtering
- O(n + k) where k is number of patterns

### Baker's Algorithm for Parameterized Matching

**Overview:** Detects parameterized clones using pattern matching with wildcards for variables.

**Algorithm Steps:**
1. **Parameterization:** Replace identifiers/literals with parameters: `P0`, `P1`, `L0`, `L1`
2. **Fingerprinting:** Create signatures for parameterized patterns
3. **Matching:** Find all instances of each pattern
4. **Clustering:** Group matches into clone classes

**Example:**
```c
// Original code:
int sum_a = 0;
for (int i = 0; i < 4; i++) {
    sum_a += array_a[i];
}

int sum_b = 0;
for (int j = 0; j < 4; j++) {
    sum_b += array_b[j];
}

// Parameterized pattern:
P0 += L0;
for (int P1 = 0; P1 < 4; P1++) {
    P0 = P0 + L1;
}
```

**Pros:**
- Detects clones with renamed variables
- Captures systematic copy-paste with modifications
- Handles different loop indices

**Cons:**
- Limited to specific code patterns
- May miss semantic clones
- False positives with similar but unrelated code

### CPM (Clone Pairs Detection) Algorithm

**Overview:** Count matrix based detection using n-gram analysis.

**Algorithm:**
1. **Tokenize:** Convert code to token sequences
2. **Count N-grams:** Build frequency matrix of n-gram occurrences
3. **Build Pairs Matrix:** Count co-occurrences of n-gram pairs
4. **Filter:** Apply minimum frequency threshold
5. **Find Clones:** Extract frequent token sequences

**Complexity:** O(n × t) where n is code length and t is n-gram size

**Pseudocode:**
```
def cpm(tokens, min_len=4, threshold=2):
    ngrams = build_ngrams(tokens, min_len)
    
    # Build count matrix
    for i in range(len(ngrams)):
        for j in range(i+1, len(ngrams)):
            count_matrix[ngrams[i]][ngrams[j]] += 1
    
    # Find frequent pairs
    clones = []
    for pair, count in count_matrix.items():
        if count >= threshold:
            clones.append(pair)
    
    return merge_clones(clones)
```

### Count Matrix Clone Detection (CMCD)

**Overview:** Uses token frequency vectors for Jaccard-based similarity.

**Algorithm:**
1. **Count Tokens:** Compute token frequencies per file/function
2. **Build Vectors:** Create frequency vectors
3. **Compute Similarity:** Calculate Jaccard or Dice coefficient
4. **Threshold:** Report clones above similarity threshold

**Advantages:**
- Handles large codebases well
- Can detect Type 2 clones with different token frequencies
- Memory efficient with sparse vectors

### NiCad Clone Detector

**Overview:** A comprehensive tool combining multiple techniques:
1. Pretty-printing for normalization
2. Blind renaming for Type 2 detection
3. Format-aware parsing
4. N-gram based detection
5. Tree-based clustering

**Key Features:**
- Language-specific preprocessing
- Configurable similarity thresholds
- Multiple granularity levels (functions, blocks, files)
- Cross-language clone detection capability

**Detection Stages:**
```
Stage 1: Preprocessing
  - Pretty-print (normalize formatting)
  - Remove comments
  - Blind renaming (normalize identifiers)
  - Normalize whitespace
  
Stage 2: Tokenization
  - Language-specific lexical analysis
  - Build token streams
  
Stage 3: N-gram Analysis
  - Generate n-grams (typically 6-10 tokens)
  - Count occurrences
  - Find common sequences
  
Stage 4: Clustering
  - Group similar fragments
  - Apply similarity thresholds
  - Report clone pairs
  
Stage 5: Post-processing
  - Filter based on length
  - Merge adjacent clones
  - Generate reports
```

### Anti-Unification for Type 3 Clones

**Overview:** Finds common patterns by computing most general generalization of two code fragments.

**Definition:** Anti-unification of trees T₁ and T₂ is tree U such that T₁ ≤ U and T₂ ≤ U, and for any other U, if T₁ ≤ U and T₂ ≤ U, then T₁ ≤ U and T₂ ≤ U.

**Algorithm:**
```
def anti_unify(ast1, ast2):
    # Build generalization tree
    # Find least upper bound
    
    # Result contains:
    # - Abstracted values (e.g., L1, L2 for variables)
    # - Unified control structure
    # - Common expression patterns
```

**Applications:**
- Finding algorithmic patterns
- Type 3 semantic clone detection
- Design pattern extraction

---

## Clone Types in Detail

### Type 1: Exact Clones (Examples and Detection)

**Definition:** Code fragments that are identical after normalization (whitespace, comments, formatting).

**Real Examples:**

#### Example 1: Copy-Paste with Formatting
```python
# File: utils.py
def calculate_average(arr):
    total = 0
    for item in arr:
        total += item
    return total / len(arr)

# File: main.py
def calc_avg_a(values):
    total = 0
    for value in values:
        total += value
    return total / len(values)
```
**Analysis:** Identical logic with different function/variable names.

#### Example 2: Boilerplate Code
```javascript
// File: user.js
function validateEmail(email) {
    const pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return pattern.test(email);
}

function validatePhoneNumber(phone) {
    const pattern = /^\d{3}-\d{3}-\d{4}$/;
    return pattern.test(phone);
}
```
**Analysis:** Same validation pattern used multiple times with different parameters.

**Detection Strategy:** Token-based exact matching, suffix trees for large codebases.

### Type 2: Near-Miss Clones (Examples and Detection)

**Definition:** Code with minor modifications: renamed variables, changed constants, slight structural changes.

**Real Examples:**

#### Example 1: Renamed Variables
```c
// File: database.c
int calculate_sum(int* data, int size) {
    int total = 0;
    for (int i = 0; i < size; i++) {
        total += data[i];
    }
    return total;
}

// File: processor.c
int compute_total(int* values, int count) {
    int sum = 0;
    for (int j = 0; j < count; j++) {
        sum += values[j];
    }
    return sum;
}
```
**Analysis:** Same algorithm with different variable names (data→values, size→count).

**Detection Strategy:** Parameterized matching (Baker's algorithm), Levenshtein distance < threshold (e.g., < 20% changes).

#### Example 2: Added Statements
```java
// File: UserValidator.java
public class UserValidator {
    public boolean isValidEmail(String email) {
        String regex = "^[A-Za-z0-99._-]+@[A-Za-z0-99._-]+\\.[A-Za-z]{2,}$";
        return email.matches(regex);
    }
}

// File: AccountManager.java
public class AccountManager {
    public boolean checkEmail(String emailAddress) {
        String pattern = "^[A-Za-z0-99._-]+@[A-Za-z0-99._-]+\\.[A-Za-z]{2,}$";
        return emailAddress.matches(pattern);
    }
}
```
**Analysis:** Same validation logic with additional null check and different method naming.

**Detection Strategy:** Token similarity with Jaccard > 0.85, structural comparison with minor edits allowed.

#### Example 3: Modified Logic Flow
```python
# File: processor.py
def process_items(items):
    result = []
    for item in items:
        if item > 0:
            result.append(item * 2)
    return result

# File: handler.py
def handle_data(data):
    output = []
    for value in data:
        if value > 0:
            output.append(value * 2)
    return output
```
**Analysis:** Same logic with slight naming differences and structure.

**Detection Strategy:** AST comparison allowing minor modifications, Levenshtein on normalized tokens.

### Type 3: Semantic Clones (Examples and Detection)

**Definition:** Functionally equivalent code with different implementations.

**Real Examples:**

#### Example 1: Different Sorting Algorithms
```python
# File: sort_a.py
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr

# File: sort_b.py
def insertion_sort(arr):
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:
            arr[j+1] = arr[j]
            j -= 1
        arr[j+1] = key
    return arr
```
**Analysis:** Different implementations of sorting with O(n²) complexity, same function.

**Detection Strategy:** Anti-unification (finds pattern: "sort array with algorithm"), PDG analysis, compression distance, control flow graph isomorphism.

#### Example 2: Database Connections
```go
// File: mysql_connector.go
func connectMySQL(host, port, user, password) string {
    db, err := sql.Open("mysql", fmt.Sprintf("%s:%s@tcp(%s)", user, password, host, port))
    if err != nil {
        log.Fatal(err)
    }
    defer db.Close()
    return db
}

// File: postgresql.go
func connectPostgres(host, port, user, password) string {
    connStr := fmt.Sprintf("host=%s port=%s user=%s password=%s dbname=mydb", host, port, user, password)
    db, err := sql.Open("postgres", connStr)
    if err != nil {
        log.Fatal(err)
    }
    defer db.Close()
    return db
}
```
**Analysis:** Same database connection functionality with different SQL drivers and connection string formats.

**Detection Strategy:** PDG comparison (same I/O operations and error handling), semantic analysis of API calls, AST-based clone detection with library matching patterns.

#### Example 3: API Client Implementations
```typescript
// File: api_client_v1.ts
class HttpClient {
    async fetch(url: string): Promise<Response> {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        return await response.json();
    }
}

// File: api_client_v2.ts
class HttpService {
    async get(url: string): Promise<any> {
        try {
            const res = await fetch(url);
            if (res.status >= 400) {
                throw new Error(`Request failed with status ${res.status}`);
            }
            return await res.json();
        } catch (error) {
            throw error;
        }
    }
}
```
**Analysis:** Different implementations of HTTP client with same functionality but different error handling and return types.

**Detection Strategy:** Type 3 requires semantic analysis: execution trace comparison, input-output mapping, AST-based control flow matching, machine learning approaches using embeddings.

---

## Implementation Guidance

### Performance Optimization Strategies

#### 1. Incremental Processing
```python
class IncrementalCloneDetector:
    def __init__(self):
        self.token_index = {}
        self.clone_pairs = []
    
    def add_file(self, file_tokens):
        # Update token index incrementally
        # Only compare with existing files
        # O(n × m) where m is average file size
```

#### 2. Parallel Processing
```python
from concurrent.futures import ProcessPoolExecutor

def detect_clones_parallel(file_paths, workers=8):
    with ProcessPoolExecutor(max_workers=workers) as executor:
        results = list(executor.map(tokenize_file, file_paths))
    return compute_similarity_matrix(results)
```

#### 3. Memory-Efficient Data Structures
- **Use Sparse Matrices:** Store only non-zero Jaccard similarities
- **Streaming Tokenization:** Process large files without loading entirely
- **Bloom Filters:** Fast membership tests for seen tokens

#### 4. Approximate Algorithms
- **MinHash:** O(1) signature estimation of Jaccard similarity
- **Locality-Sensitive Hashing (LSH): High-dimensional similarity
- **Sampling:** Check random sample pairs, then full verification

### Configurable Similarity Thresholds

**Recommended Thresholds by Clone Type:**

| Clone Type | Algorithm | Jaccard | Cosine | Levenshtein | Notes |
|------------|----------|---------|---------|-------------|-------|
| Type 1 | ≥ 0.99 | ≥ 0.98 | 0 | Exact match required |
| Type 2 | ≥ 0.85 | ≥ 0.90 | ≤ 0.20 | Allow 20% variation |
| Type 3 | ≥ 0.70 | ≥ 0.80 | ≤ 0.35 | Semantic similarity needed |

### Reporting Format

**Standard Clone Report:**
```
Clone Pair:
  Location A: file:line_start-line_end
  Location B: file:line_start-line_end
  Clone Type: Type 1/2/3
  Similarity: 0.95 (Jaccard) / 0.92 (Cosine)
  Lines: 15
  Tokens: 87
  Matched Tokens: 82
  
  Code Preview:
    File A:
      lines 10-24
    File B:
      lines 45-59
```

### Handling Variations

**Renamed Variables (Blind Renaming):**
1. Build identifier mapping for each file
2. Replace identifiers with generic names
3. Compare normalized token sequences
4. Report original identifiers in output

**Different Constants/Literals:**
1. Extract string/numeric literals from tokenization
2. Treat literals as wildcards in pattern matching
3. Use approximate matching allowing literal differences
4. Weight similarity scores for structural matches

**Structural Changes:**
1. Use AST or control flow graph comparison
2. Allow insertion/deletion of statements
3. Compute tree edit distance
4. Use graph isomorphism for Type 3 detection

### Scalability for Large Codebases

**Tiered Approach:**
1. **Stage 1: File-level** - Use MinHash or rolling hash to find similar files
2. **Stage 2: Function-level** - Token-based Jaccard on function signatures
3. **Stage 3: Block-level** - CPM or suffix tree on code blocks
4. **Stage 4: Fine-grained** - Full AST comparison for Type 2/3

**Memory Management:**
```
Memory-Efficient Detection Pipeline:

1. Stream tokens → don't keep all tokens in memory
2. Build n-gram index with size limit
3. Use rolling hash for comparison
4. Process in batches, write results incrementally
5. Use disk-backed indexes for very large codebases
```

---

## Code Examples

### Complete Duplicate Examples with Variations

#### Example 1: Type 1 Exact Clone - Formatting Only

**Original Code (Python):**
```python
def calculate_discount(price, quantity):
    if quantity >= 100:
        return price * 0.90
    elif quantity >= 50:
        return price * 0.95
    elif quantity >= 20:
        return price * 0.97
    elif quantity >= 10:
        return price * 0.98
    else:
        return price
```

**Duplicate (Different File):**
```python
def get_discount_rate(amount, count):
    if count >= 100:
        return amount * 0.9
    elif count >= 50:
        return amount * 0.95
    elif count >= 20:
        return amount * 0.97
    elif count >= 10:
        return amount * 0.98
    else:
        return amount
```

**Detection:** Exact token match after removing comments and whitespace.

---

#### Example 2: Type 2 Clone - Renamed Variables

**Original Code (Java):**
```java
public class ArrayUtils {
    public static int sum(int[] array) {
        int total = 0;
        for (int i = 0; i < array.length; i++) {
            total += array[i];
        }
        return total;
    }
}
```

**Duplicate (Renamed Variables):**
```java
public class VectorUtils {
    public static int computeSum(int[] data) {
        int result = 0;
        for (int j = 0; j < data.length; j++) {
            result += data[j];
        }
        return result;
    }
}
```

**Detection:** Jaccard = 1.0 (same structure), but variable names differ. Levenshtein distance between normalized tokens = 0 after identifier normalization.

---

#### Example 3: Type 2 Clone - Modified Constants

**Original Code (JavaScript):**
```javascript
const CONFIG = {
    api_url: "https://api.example.com/v1",
    timeout: 5000,
    retries: 3
};

function fetchData(url) {
    return fetch(url, CONFIG.timeout);
}
```

**Duplicate (Changed Constants):**
```javascript
const SETTINGS = {
    endpoint: "https://api.example.com/v1",
    connection_timeout: 5000,
    max_attempts: 3
};

async function getData(target) {
    return fetch(target, SETTINGS.connection_timeout);
}
```

**Detection:** Token Jaccard = 0.85 (structural similarity), literals changed.

---

#### Example 4: Type 3 Clone - Different Algorithm

**Original Code (Python - Bubble Sort):**
```python
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr
```

**Duplicate (Selection Sort - Different Algorithm):**
```python
def selection_sort(data):
    n = len(data)
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            if data[j] < data[min_idx]:
                min_idx = j
        data[i], data[min_idx] = data[min_idx], data[i]
    return data
```

**Detection:** Type 3 requires semantic analysis. Both sort arrays in-place with O(n²) complexity. Anti-unification finds pattern: "sort array with algorithm O(n²)".

---

#### Example 5: Type 1 Clone - Boilerplate with Different Names

**Original (C++):**
```cpp
class RequestHandler {
public:
    void handleRequest() {
        std::cout << "Processing request..." << std::endl;
        validateInput();
        processData();
        generateResponse();
    }
    
private:
    void validateInput() {
        if (input.length() > 0) {
            std::cout << "Input valid" << std::endl;
        }
    }
    
    void processData() {
        std::cout << "Data: " << input << std::endl;
    }
    
    void generateResponse() {
        std::cout << "Response: OK" << std::endl;
    }
};
```

**Duplicate (C++):**
```cpp
class ResponseProcessor {
public:
    void processMessage() {
        std::cout << "Handling message..." << std::endl;
        checkRequest();
        transformData();
        createOutput();
    }
    
private:
    void checkRequest() {
        if (message.length() > 0) {
            std::cout << "Request received" << std::endl;
        }
    }
    
    void transformData() {
        std::cout << "Message content: " << message << std::endl;
    }
    
    void createOutput() {
        std::cout << "Output: Success" << std::endl;
    }
};
```

**Detection:** Type 1 exact match after normalization. Same structure, different naming.

---

#### Example 6: Type 2 Clone - Control Flow Variation

**Original (Go):**
```go
func processUser(name string, age int) (bool, error) {
    if age < 18 {
        return false, errors.New("User is underage")
    }
    if name == "" {
        return false, errors.New("Name required")
    }
    return true, nil
}

func main() {
    users := []User{{"Alice", 25}, {"Bob", 30}}
    
    for _, user := range users {
        valid, err := processUser(user.name, user.age)
        if !valid {
            fmt.Printf("Error: %v for user %s\n", err, user.name)
        } else {
            fmt.Printf("User %s is valid\n", user.name)
        }
    }
}
```

**Duplicate (Go):**
```go
func validatePerson(name string, years int) (bool, error) {
    if years < 18 {
        return false, errors.New("Person must be 18+")
    }
    if len(name) == 0 {
        return false, errors.New("Name cannot be empty")
    }
    return true, nil
}

func execute() {
    people := []struct{name string, age int}{{"Carol", 22}, {"David", 35}}
    
    for i, person := range people {
        ok, err := validatePerson(person.name, person.age)
        if ok {
            fmt.Printf("Valid: %s\n", person.name)
        } else {
            fmt.Printf("Invalid: %v - %s\n", err, person.name)
        }
    }
}
```

**Detection:** Token Jaccard ≈ 0.90 (high similarity). Control flow structure differs slightly (error returned earlier vs later). Levenshtein distance shows ~10% token differences.

---

#### Example 7: Type 3 Clone - Same Functionality, Different Implementation

**Original (Python - Custom Hash):**
```python
class CustomHash:
    def __init__(self):
        self.data = []
    
    def add(self, key, value):
        index = hash(key) % 100
        if index < len(self.data):
            self.data[index] = self.data[index] or []
        self.data[index].append((key, value))
    
    def get(self, key):
        index = hash(key) % 100
        for k, v in self.data[index]:
            if k == key:
                return v
        return None
```

**Duplicate (Python - Built-in dict):**
```python
class EfficientHash:
    def __init__(self):
        self.storage = {}
    
    def insert(self, key, value):
        self.storage[key] = value
    
    def retrieve(self, key):
        return self.storage.get(key, None)
```

**Detection:** Type 3 - both implement hash map functionality. Control flow graphs show same operations (add, get with hash lookup). AST structures differ but compute same hash. Anti-unification identifies pattern: "class with methods add and retrieve values using hash".

---

### Real-World Scenarios

#### Scenario 1: Library Duplication
```java
// library_a/DateHelper.java
public class DateHelper {
    public static boolean isLeapYear(int year) {
        if (year % 4 != 0) {
            return false;
        } else if (year % 100 != 0) {
            return false;
        } else if (year % 400 != 0) {
            return false;
        }
        return (year % 4 == 0) && (year % 100 != 0 || year % 400 == 0);
    }
}
```

```java
// library_b/DateUtil.java
public class DateUtil {
    public static boolean checkLeap(int y) {
        boolean div4 = (y % 4 == 0);
        boolean div100 = (y % 100 == 0);
        boolean div400 = (y % 400 == 0);
        return div4 && ((!div100) || div400);
    }
}
```

**Analysis:** Type 1 exact clone (same logic, different names).

#### Scenario 2: Generated Code Patterns

```typescript
// Generated API client - Service A
export class APIClientA {
    async get<T>(url: string): Promise<T> {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`Failed: ${response.status}`);
        }
        return await response.json();
    }
    
    async post<T>(url: string, data: any): Promise<T> {
        const response = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        return await response.json();
    }
}
```

```typescript
// Generated API client - Service B
export class APIClientB {
    async fetch<T>(endpoint: string): Promise<T> {
        try {
            const res = await fetch(endpoint);
            if (!res.ok) {
                throw new APIError(res.statusText);
            }
            return await res.json();
        } catch (e) {
            throw new APIError(e.message);
        }
    }
    
    async send<T>(url: string, payload: object): Promise<T> {
        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            return await response.json();
        } catch (err) {
            throw new APIError(err.toString());
        }
    }
}
```

**Analysis:** Type 3 semantic clone - same API client structure with different error handling and method naming.

---

## References

### Academic Papers

1. **Baker, Brenda S.** (1992) "A Program for Identifying Duplicated Code." Computing Science and Statistics. 24:49–57.
2. **Koschke, Rainer; et al.** (2006) "Clone Detection Using Abstract Syntax Trees." Proceedings of the 13th Working Conference on Reverse Engineering (WCRE 2006).
3. **Yuan, T.; Guo, Y.** (2011) "CMCD: Count Matrix Based Code Clone Detection." Asia-Pacific Software Engineering Conference (APSEC).
4. **Roy, Chanchal K.; Cordy, James R.** (2007) "A Survey on Software Clone Detection: Research and Practice." Journal of Systems and Software. 85:7–38.
5. **Juergens, Elmar; et al.** (2009) "Language-independent clone detection." 2009 16th Working Conference on Reverse Engineering (WCRE).

### Tools and Systems

1. **NiCad Clone Detector:** Comprehensive multi-language clone detector with Type 1, 2, and 3 detection.
2. **SonarQube:** Commercial static analysis tool with duplicate code detection.
3. **PMD:** Open-source static code analyzer with CPD (Copy-Paste Detection) support.
4. **CCFinder:** Text-based clone detection tool using token-based techniques.
5. **JPlag:** Language-agnostic plagiarism detection using n-gram analysis.

### Algorithm References

1. **Ukkonen, E.** (1995) "On-line construction of suffix trees." Algorithmica 61:489–502.
2. **McCreight, E. M.** (1976) "A Space-Economical Suffix Tree Construction Algorithm." Journal of the ACM. 23:262–272.
3. **Rabin, M. O.; Karp, R. M.** (1987) "Efficient Randomized Pattern-Matching Algorithms." IBM Journal of Research and Development. 31:369–375.
4. **Levenshtein, V. I.** (1965) "Binary codes capable of correcting deletions, insertions, and reversals." Doklady Akademii Nauk SSSR. 20:845–848.
5. **Jaccard, P.** (1912) "The distribution of the flora in the alpine zone." Bulletin de la Société Vaudoise des Sciences Naturelles. 67:241–270.

### Online Resources

1. **Wikipedia:** Duplicate code, Levenshtein distance, Jaccard index, Cosine similarity, Suffix tree, Rabin-Karp algorithm.
2. **Clone Detection Literature:** IEEE Xplore, ACM Digital Library.
3. **Source Code Analysis Tools:** Comparison of NiCad, CCFinder, PMD CPD.

---

## Implementation Checklist

For implementing duplicate code detection:

- [ ] Define clone types to detect (Type 1/2/3 or all)
- [ ] Select primary algorithm (token-based, AST-based, hybrid)
- [ ] Design tokenization strategy for target languages
- [ ] Implement similarity metrics (Jaccard, Cosine, Levenshtein)
- [ ] Set configurable similarity thresholds
- [ ] Handle language-specific syntax variations
- [ ] Implement performance optimizations (parallelization, caching)
- [ ] Design report format with clone locations and similarity scores
- [ ] Add filtering (minimum length, minimum lines, minimum tokens)
- [ ] Consider cross-language detection requirements
- [ ] Plan for incremental updates in CI/CD pipelines
- [ ] Handle false positive reduction (post-processing, clustering)

---

## Quick Reference: Clone Detection Algorithms Comparison

| Algorithm | Type Detection | Time Complexity | Space Complexity | Accuracy | Implementation Complexity |
|------------|---------------|------------------|-------------------|----------|------------------------|
| Exact Token Match | Type 1 | O(n) | O(n) | High | Low |
| CPM (n-gram) | Type 1, 2 | O(n × t) | O(n × t) | Medium | Medium |
| Suffix Tree | Type 1 | O(n+m) | O(n) | High | High |
| Rabin-Karp | Type 1 | O(n+m) | O(1) | High | Medium |
| Baker's Algorithm | Type 2 | O(n²) | O(n) | High | High |
| AST Comparison | Type 1, 2, 3 | O(n³) | O(n²) | Very High | Very High |
| Anti-Unification | Type 2, 3 | O(n³) | O(n²) | High | Very High |
| Levenshtein | Type 2 | O(m×n) | O(m×n) | Medium | Low |
| MinHash + Verify | Type 1, 2 | O(n + k) | O(k) | Medium | Medium |

*Where n = code size, m = pattern size, t = n-gram size, k = signature size*

---

**Document Version:** 1.0  
**Last Updated:** February 2025  
**Purpose:** Comprehensive research guide for implementing language-agnostic duplicate code detection systems
