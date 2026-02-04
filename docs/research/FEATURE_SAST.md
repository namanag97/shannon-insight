# SAST (Static Application Security Testing) Implementation Research

## Executive Summary

Static Application Security Testing (SAST) is a critical security analysis technique that examines source code, bytecode, or binaries without executing the program to identify security vulnerabilities. This research document provides a comprehensive foundation for implementing SAST capabilities in Shannon Insight, covering mathematical foundations, language-agnostic design approaches, OWASP Top 10 vulnerability detection, and practical implementation strategies.

SAST represents one of the most effective security-first approaches in modern software development, enabling vulnerability detection early in the development lifecycle (shift-left security). Unlike Dynamic Application Security Testing (DAST), SAST analyzes the code structure to identify potential security flaws before deployment, significantly reducing remediation costs and preventing vulnerabilities from reaching production environments.

**Key Advantages of SAST:**
- Early vulnerability detection (during development)
- Comprehensive code coverage
- Minimal infrastructure requirements
- Integration with CI/CD pipelines
- Language-specific security pattern recognition
- Automated, repeatable analysis

**Challenges to Address:**
- High false positive rates
- Language and framework diversity
- Context-sensitive analysis requirements
- Configuration and tuning complexity
- Handling of dynamic code generation

This document provides actionable guidance for implementing SAST that balances comprehensive vulnerability detection with practical usability, leveraging modern static analysis techniques including taint analysis, data flow analysis, and pattern-based detection.

---

## Mathematical Foundations

### Control Flow Graphs (CFGs)

A **Control Flow Graph (CFG)** is a directed graph representation of all paths that might be traversed through a function during execution. CFGs form the foundation for many compiler optimizations and static analysis tools.

**Definition:**
A CFG consists of:
- **Nodes**: Basic blocks (sequences of statements with single entry/exit points)
- **Edges**: Control flow between basic blocks
- **Entry node**: Point where control enters the function
- **Exit node**: Point(s) where control exits the function

**Mathematical Properties:**
For a CFG with basic blocks B, edges E, entry block entry, and exit block exit:

```
Let G = (B, E) be a directed graph
entry ∈ B is the unique entry block
exit ∈ B are exit blocks

For any block b ∈ B:
- Predecessors: pred(b) = {p ∈ B | (p, b) ∈ E}
- Successors: succ(b) = {s ∈ B | (b, s) ∈ E}
```

**Dominance Relationships:**
Block M **dominates** block N if every path from entry that reaches N also visits M.

```
dom(M, N) = ∀path P from entry to N: M ∈ nodes(P)
```

**Reducibility:**
A CFG is **reducible** if all retreating edges (edges from a node to a dominator) are back edges. Reducible CFGs have stronger static properties and are easier to analyze.

```
Let (u, v) ∈ E be a retreating edge
(u, v) is a back edge iff dom(v, u)
```

**Example CFG for Security Analysis:**

```python
# Vulnerable authentication function
def authenticate(user, password):
    # Block 1: Entry
    if not validate_user(user):  # Conditional
        return False  # Block 2
    query = "SELECT * FROM users WHERE user='" + user + "'"  # Block 3: SQLi vulnerability
    result = execute_query(query)  # Block 4
    if not result:  # Block 5
        return False  # Block 6
    return check_password(result, password)  # Block 7: Exit
```

CFG structure:
- Block 1 → Block 2 (on validation failure)
- Block 1 → Block 3 → Block 4 → Block 5 → Block 6
- Block 5 → Block 7 (on success)

**Applications to Security:**
- **Path-sensitive analysis**: Consider different execution paths when evaluating security properties
- **Loop detection**: Identify iteration boundaries that could lead to infinite loops or resource exhaustion
- **Unreachable code detection**: Find code paths that cannot execute (potential dead code vulnerabilities)
- **Taint propagation boundaries**: Understand where tainted data can and cannot flow

### Taint Analysis

**Taint analysis** tracks data from untrusted sources (taint sources) through a program to identify when they reach sensitive sinks without proper sanitization. This is the foundational technique for detecting injection vulnerabilities.

**Formal Definition:**

```
Let P be a program with variables V, statements S
Let T ⊆ V be the set of tainted variables
Let Sources ⊆ S be taint source statements (e.g., user input)
Let Sinks ⊆ S be sensitive sink statements (e.g., SQL queries)

For each statement s ∈ S:
transfer(s, in_taint) = out_taint

where:
- in_taint ⊆ V is the set of tainted variables before s
- out_taint ⊆ V is the set of tainted variables after s

Taint propagation rules:
1. Source: s ∈ Sources → adds variables to T
2. Assignment: v = e → if any variable in e is tainted, v becomes tainted
3. Sanitization: s is sanitizer function → removes variables from T
4. Sink check: s ∈ Sinks ∧ vars(s) ∩ T ≠ ∅ → VULNERABILITY
```

**Example Taint Propagation:**

```python
# Source: HTTP request parameter
user_input = request.get_param('username')  # Taints: {'username'}

# Propagation through assignment
query = "SELECT * FROM users WHERE user = '" + user_input  # Taints: {'username', 'query'}

# Sink: SQL execution (no sanitization)
execute(query)  # ⚠️ VULNERABILITY: tainted data reaches SQL sink
```

**Taint Analysis Algorithm:**

```
Algorithm TaintAnalysis(program):
    Initialize tainted = {}
    worklist = [all statements]

    while worklist not empty:
        s = worklist.pop()
        old_taint = tainted

        # Compute taint propagation for statement s
        if s is source:
            tainted = tainted ∪ {s.output_variables}
        elif s is assignment v = e:
            if any(var in tainted for var in variables(e)):
                tainted = tainted ∪ {v}
            else:
                tainted = tainted - {v}
        elif s is sanitization call:
            tainted = tainted - {s.input_variables}
        elif s is sink:
            if vars(s) ∩ tainted ≠ ∅:
                report_vulnerability(s, tainted ∩ vars(s))

        if tainted != old_taint:
            add successors(s) to worklist
```

**Taint Unification:**
In taint mode analysis, metavariables in `pattern-sources` and `pattern-sinks` must unify consistently. Set `taint_unify_mvars: true` to enforce this:

```yaml
options:
  taint_unify_mvars: true
```

### Data Flow Analysis

**Data flow analysis** gathers information about possible sets of values calculated at various points in a program. It forms the foundation for tracking security-relevant data properties.

**Kildall's Algorithm (Iterative Data Flow):**

```
Let CFG have n blocks, numbered 1 to n
For each block i, define:
- in[i]: Data flow information entering block i
- out[i]: Data flow information leaving block i
- trans[i]: Transfer function of block i
- succ[i]: Successors of block i

Data flow equations:
out[i] = trans[i](in[i])  # Apply transfer function
in[i] = ∪_{j∈succ[i]} out[j]  # Join successor outputs (backward)

Forward analysis: in[i] depends on successors
Backward analysis: in[i] depends on predecessors

Algorithm:
Initialize in[i] = appropriate initial value
while any in[i] or out[i] changes:
    for i = 1 to n:
        in[i] = join(out[j] for all j in succ[i])  # or pred[i] for forward
        out[i] = trans[i](in[i])

Termination: When all in[i] and out[i] stabilize (fixpoint)
```

**Convergence Guarantee:**
The algorithm always converges if:
1. The value domain is a partial order with finite height
2. Transfer functions are monotonic
3. The join operator is monotonic

```
Let (D, ≤) be the value domain
If ∀x∈D: f(x) ≥ x (monotonic)
And ∀x,y∈D: x ∨ y ≥ x, x ∨ y ≥ y (join monotonic)
Then the algorithm reaches a fixpoint in O(height(D) × n) iterations
```

**Reaching Definitions Analysis:**

```
For each block i:
gen[i]: Set of definitions generated in block i
kill[i]: Set of definitions killed (overwritten) in block i
in[i]: Set of definitions reaching entry of block i
out[i]: Set of definitions reaching exit of block i

Transfer function:
out[i] = gen[i] ∪ (in[i] - kill[i])

Join operation: ∪ (union)
```

**Example:**

```python
# Block 1
user = request.get_param('user')  # Def: d1
password = request.get_param('pass')  # Def: d2

# Block 2
query = "SELECT * FROM users WHERE user = '" + user  # Uses: d1, Def: d3
# gen[2] = {d3}, kill[2] = {}

# Block 3
result = execute(query)  # Uses: d3

# Reaching definitions at Block 3:
# in[3] = out[2] = {d1, d2, d3}
# d1 (user) and d3 (query) both reach Block 3
# If d3 reaches SQL sink without sanitization → vulnerability
```

### Lattice Theory and Abstract Interpretation

**Abstract interpretation** provides a mathematical framework for sound approximation of program semantics, enabling decidable security analysis.

**Lattice-Based Abstraction:**

```
Let L = (D, ≤) be a lattice representing concrete values
Let L' = (D', ≤') be a lattice representing abstract values

Abstraction function: α: L → L'
Concretization function: γ: L' → L

Galois connection:
∀x∈L, x'∈D': x ≤ γ(x') ⇔ α(x) ≤' x'

Properties:
1. γ(α(x)) ≥ x  (concretization of abstraction is over-approximation)
2. α(γ(x')) ≤' x'  (abstraction of concretization is under-approximation)
```

**Example: Interval Abstraction**

```
Concrete domain: Z (integers)
Abstract domain: Intervals [l, h] where l ≤ h, l,h ∈ Z ∪ {-∞, +∞}

α(x) = [x, x]  # Abstract a single value
γ([l, h]) = {z ∈ Z | l ≤ z ≤ h}  # Concretize interval

Lattice operations on intervals:
[l1, h1] ≤ [l2, h2] iff l2 ≤ l1 ∧ h1 ≤ h2  # containment
[l1, h1] ⊔ [l2, h2] = [min(l1, l2), max(h1, h2)]  # least upper bound (union)
[l1, h1] ⊓ [l2, h2] = [max(l1, l2), min(h1, h2)]  # greatest lower bound (intersection)
```

**Abstract Transfer Functions:**

For arithmetic operations, define abstract semantics:

```
Concrete addition: +(x, y) = x + y
Abstract addition: +^I([l1, h1], [l2, h2]) = [l1 + l2, h1 + h2]

Concrete multiplication: *(x, y) = x * y
Abstract multiplication: *^I([l1, h1], [l2, h2]) = [
    min(l1*l2, l1*h2, h1*l2, h1*h2),
    max(l1*l2, l1*h2, h1*l2, h1*h2)
]
```

**Security Property Verification:**

```
Let P be a security property (e.g., "no SQL injection")
Let Abs(P) be abstract property (e.g., "query strings never contain tainted input")

If Abstract Interpretation proves Abs(P), then:
- Under-approximation: P definitely holds (sound for verification)
- Over-approximation: P might or might not hold (conservative for detection)

For SAST, we typically use over-approximation to ensure all potential vulnerabilities are reported.
```

---

## Language-Agnostic Design

### AST-Based Queries with Tree-sitter

**Tree-sitter** is an incremental parsing system that provides a language-agnostic approach to building concrete syntax trees. This enables cross-language security pattern detection.

**Architecture:**
```
Language-specific grammar (tree-sitter-* parsers)
        ↓
Concrete Syntax Tree (CST) for source code
        ↓
AST queries (language-agnostic patterns)
        ↓
Security vulnerability matches
```

**Tree-sitter Query API:**

```python
from tree_sitter import Language, Parser

# Load language-specific parser
parser = Parser(Language('python'))

# Parse source code
source_code = """
def query_user(user_id):
    return execute("SELECT * FROM users WHERE id = " + user_id)
"""
tree = parser.parse(bytes(source_code, "utf8"))

# Query for SQL injection patterns (language-agnostic)
# Pattern: string concatenation with variable in SQL context
pattern = """
(call_expression
  function: (identifier) @function_name
  arguments: (argument_list
    (binary_expression
      left: (string)
      operator: "+"
      right: (identifier) @variable_name
    )
  )
)
"""

# Match pattern
matches = query(tree.root_node, pattern)
for match in matches:
    function_name = match.captures['function_name'].text
    variable_name = match.captures['variable_name'].text
    print(f"Potential SQL injection: {function_name} uses concatenation with {variable_name}")
```

**Universal SQL Injection Pattern (Tree-sitter):**

```lisp
; This pattern works across languages that support string concatenation and function calls
(
  (call_expression
    function: (identifier)  # Matches: execute, query, run, etc.
    arguments: (argument_list
      (binary_expression
        left: (string)  # SQL string literal
        operator: "+"  # String concatenation
        right: (identifier)  # Variable (potentially tainted)
      )
    )
  )
)
```

**Advantages of Tree-sitter for SAST:**

1. **Incremental parsing**: Re-parse only changed portions during development
2. **Error recovery**: Useful trees even with syntax errors
3. **Language ecosystem**: Parsers for 40+ programming languages
4. **Cross-language patterns**: Write once, detect across languages
5. **Performance**: C implementation for fast parsing

### Semgrep Rule-Based Approach

**Semgrep** provides a rule-based, pattern-matching approach that's highly effective for security vulnerability detection. It uses a simple but powerful pattern syntax that works across languages.

**Core Concepts:**

1. **Pattern Matching**: Search for code patterns using syntactic matching
2. **Metavariables**: Capture and match code elements ($VAR, $FUNC, etc.)
3. **Ellipsis Operator**: Match sequences of code (...)
4. **Equivalences**: Match semantically equivalent code

**Pattern Syntax Examples:**

```yaml
# Match function calls with specific argument patterns
pattern: requests.get(..., verify=False, ...)

# Match string concatenation in SQL queries
pattern: $QUERY + $VAR

# Match unescaped output in templates
pattern: render_template($TEMPLATE, ..., unsafe_data=$INPUT)

# Match vulnerable crypto operations
pattern: CryptoJS.AES.encrypt($DATA, "hardcoded-key")
```

**SQL Injection Detection Rule:**

```yaml
rules:
  - id: python-sqli-string-format
    languages: [python]
    message: |
      SQL query constructed with string formatting.
      Use parameterized queries instead.
    severity: ERROR
    patterns:
      - pattern-either:
          # f-string with variable
          - pattern: |
              $FUNC($X + $Y, ...)
              metavariable-regex:
                  metavariable: $FUNC
                  regex: (execute|query|cursor\.execute|executemany)
          # format() method
          - pattern: |
              "SELECT ...".format($X)
          # % formatting
          - pattern: |
              "SELECT ... %s" % $X
```

**Cross-Language XSS Detection:**

```yaml
rules:
  - id: xss-direct-output
    languages: [javascript, typescript, python, ruby, php, java]
    message: Direct output of user input without sanitization
    severity: ERROR
    patterns:
      - pattern-either:
          # JavaScript: innerHTML, outerHTML
          - pattern: |
              $ELEMENT.innerHTML = $USER_INPUT
          # JavaScript: document.write
          - pattern: |
              document.write($USER_INPUT)
          # Python: Jinja2 template rendering
          - pattern: |
              render_template_string($USER_INPUT, ...)
          # PHP: echo
          - pattern: |
              echo $USER_INPUT
```

**Taint Mode Rules:**

```yaml
rules:
  - id: python-sqli-taint
    languages: [python]
    message: SQL injection via tainted user input
    severity: ERROR
    mode: taint
    pattern-sources:
      - pattern: flask.request.$X.get(...)
      - pattern: flask.request.form.get(...)
      - pattern: flask.request.args.get(...)
    pattern-sinks:
      - pattern: sqlite3.Cursor.execute($QUERY)
      - pattern: psycopg2.cursor.execute($QUERY)
    pattern-sanitizers:
      - pattern: re.sub(..., ...)
      - pattern: html.escape(...)
```

### Control Flow Patterns

**Universal control flow patterns** for vulnerability detection work across languages by abstracting the semantics rather than specific syntax.

**Pattern: Unvalidated Redirect (Open Redirect)**

```yaml
rules:
  - id: open-redirect-unvalidated
    languages: [javascript, typescript, python, ruby, php, go]
    message: Unvalidated redirect to user-controlled URL
    severity: ERROR
    patterns:
      - pattern-either:
          # JavaScript/TypeScript
          - pattern: |
              res.redirect($URL)
              metavariable-regex:
                  metavariable: $URL
                  regex: (request\.(params|query|body)\..+)
          # Python (Flask)
          - pattern: |
              redirect($URL)
              metavariable-regex:
                  metavariable: $URL
                  regex: (request\.(args|form|values)\..+)
          # Python (Django)
          - pattern: |
              HttpResponseRedirect($URL)
              metavariable-regex:
                  metavariable: $URL
                  regex: (request\.(GET|POST|COOKIES)\..+)
```

**Pattern: Path Traversal Detection**

```yaml
rules:
  - id: path-traversal
    languages: [javascript, typescript, python, php, java]
    message: File operation with unvalidated user input
    severity: ERROR
    patterns:
      - pattern-either:
          # fs.readFile in Node.js
          - pattern: |
              fs.$FUNC($DIR + $USER_INPUT, ...)
          # Python open()
          - pattern: |
              open($DIR + $USER_INPUT)
          # PHP file operations
          - pattern: |
              file_$FUNC($DIR . $USER_INPUT, ...)
          # Java File operations
          - pattern: |
              new File($DIR + $USER_INPUT)
```

### Universal Vulnerability Patterns

**Abstract patterns** capture the essence of vulnerabilities independent of language syntax:

1. **Injection Pattern**: Untrusted data + concatenation + sensitive sink
2. **XSS Pattern**: Untrusted data + output to web context
3. **Path Traversal Pattern**: Untrusted data + file system operation
4. **SSRF Pattern**: Untrusted data + network request
5. **XXE Pattern**: Untrusted data + XML parsing

**Language-Independent Detection Strategy:**

```
Step 1: Identify untrusted data sources (HTTP params, env vars, files)
Step 2: Track data flow through control flow graph
Step 3: Identify sensitive sinks (SQL, command execution, network calls)
Step 4: Check for sanitization/validation on the path
Step 5: Report if tainted data reaches sink without sanitization
```

---

## OWASP Top 10 Vulnerabilities and Detection

### A01:2021 - Broken Access Control

**Definition**: Failures in enforcing policies on what users are allowed to do.

**Vulnerability Pattern**: Missing or incorrect authorization checks.

**Detection Rules:**

```yaml
rules:
  - id: missing-authz-check
    message: Function accessing sensitive resource without authorization check
    severity: ERROR
    patterns:
      - pattern: |
          $SINK($USER_INPUT)
          pattern-not: |
              if (authz_check(...)):
                  ...
                  $SINK($USER_INPUT)
```

**Vulnerable Code:**

```python
# Python: Admin endpoint without authentication
@app.route('/admin/delete_user/<user_id>')
def delete_user(user_id):
    # Missing: if not current_user.is_admin:
    db.delete_user(user_id)  # ⚠️ Anyone can delete users
    return 'User deleted'
```

**Secure Code:**

```python
@app.route('/admin/delete_user/<user_id>')
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        return 'Unauthorized', 403
    db.delete_user(user_id)
    return 'User deleted'
```

### A02:2021 - Cryptographic Failures

**Definition**: Failures related to cryptography leading to sensitive data exposure or system compromise.

**Vulnerability Patterns**:
- Weak algorithms (DES, MD5, RC4)
- Hardcoded keys/secrets
- Insufficient key length
- Missing integrity verification

**Detection Rules:**

```yaml
rules:
  - id: weak-crypto-algorithm
    languages: [python, javascript, java, php]
    message: Weak cryptographic algorithm detected
    severity: ERROR
    patterns:
      - pattern-either:
          # MD5 hash
          - pattern: hashlib.md5($X)
          - pattern: crypto.createHash('md5')
          # SHA1 (deprecated)
          - pattern: hashlib.sha1($X)
          # DES encryption
          - pattern: DES.new($KEY)

  - id: hardcoded-secret
    languages: [python, javascript, java, ruby, go]
    message: Hardcoded secret detected in source code
    severity: ERROR
    patterns:
      - pattern-either:
          # API keys, passwords in strings
          - pattern: '"=~/[A-Za-z0-9]{32,}/"'  # Likely API key
          - pattern: '"password.+:.+"'
          - pattern: '"secret.+:.+"'
          - pattern: '"api_key.+:.+"'
```

**Vulnerable Code:**

```python
import hashlib

# Weak hashing algorithm
def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()  # ⚠️ MD5 is weak

# Hardcoded encryption key
ENCRYPTION_KEY = "s3cr3t-k3y-12345"  # ⚠️ Exposed in source

def encrypt_data(data):
    from Crypto.Cipher import DES
    cipher = DES.new(ENCRYPTION_KEY, DES.MODE_ECB)  # ⚠️ DES is weak, ECB mode is insecure
    return cipher.encrypt(data)
```

**Secure Code:**

```python
import hashlib
from cryptography.fernet import Fernet
import os

# Use environment variable for secrets
ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY')

def hash_password(password):
    # Use strong, modern hashing algorithm
    import bcrypt
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def encrypt_data(data):
    # Use AES with authenticated encryption
    cipher_suite = Fernet(ENCRYPTION_KEY)
    return cipher_suite.encrypt(data)
```

### A03:2021 - Injection

**Definition**: Injection vulnerabilities (SQL, NoSQL, OS command, LDAP) where untrusted data is sent to an interpreter.

#### SQL Injection (CWE-89)

**Pattern**: Untrusted input concatenated into SQL query.

**Detection Rules:**

```yaml
rules:
  - id: python-sqli-string-format
    languages: [python]
    message: SQL query constructed with string formatting
    severity: ERROR
    patterns:
      - pattern-either:
          # f-string format
          - pattern: f"SELECT ... { $VAR } ..."
          # .format() method
          - pattern: |
              "SELECT ...".format($VAR)
          # % operator
          - pattern: |
              "SELECT ... %s" % $VAR
          # + concatenation
          - pattern: |
              "SELECT ..." + $VAR

  - id: javascript-sqli-template-literal
    languages: [javascript]
    message: SQL query using template literal with variable
    severity: ERROR
    patterns:
      - pattern: |
          `SELECT ... ${ $VAR } ...`
```

**Vulnerable Code (Python):**

```python
# Direct string concatenation
def get_user(user_id):
    query = "SELECT * FROM users WHERE id = '" + user_id + "'"  # ⚠️ SQL injection
    cursor.execute(query)
    return cursor.fetchone()

# Using f-string
def search_users(search_term):
    query = f"SELECT * FROM products WHERE name LIKE '%{search_term}%'"  # ⚠️ SQL injection
    cursor.execute(query)
    return cursor.fetchall()
```

**Secure Code (Python):**

```python
# Parameterized queries
def get_user(user_id):
    query = "SELECT * FROM users WHERE id = %s"
    cursor.execute(query, (user_id,))  # ✓ Safe
    return cursor.fetchone()

# Using ORM (SQLAlchemy)
def search_users(search_term):
    return Product.query.filter(
        Product.name.like(f'%{search_term}%')
    ).all()  # ✓ ORM handles escaping
```

**Vulnerable Code (JavaScript/Node.js):**

```javascript
// Using template literals
const getUser = (userId) => {
    const query = `SELECT * FROM users WHERE id = '${userId}'`;  // ⚠️ SQL injection
    return db.execute(query);
};

// String concatenation
const searchProducts = (term) => {
    const query = "SELECT * FROM products WHERE name LIKE '%" + term + "%'";  // ⚠️ SQL injection
    return db.query(query);
};
```

**Secure Code (JavaScript/Node.js):**

```javascript
// Parameterized queries with pg
const getUser = async (userId) => {
    const query = 'SELECT * FROM users WHERE id = $1';
    return await db.query(query, [userId]);  // ✓ Safe
};

// Using parameterized query builder
const searchProducts = async (term) => {
    const query = {
        text: 'SELECT * FROM products WHERE name LIKE $1',
        values: [`%${term}%`]
    };
    return await db.query(query);
};
```

#### NoSQL Injection

**Pattern**: Injection in NoSQL database queries (MongoDB, etc.).

**Vulnerable Code:**

```javascript
// MongoDB with $where operator
const findUser = (username) => {
    return db.users.findOne({
        $where: `this.username === '${username}'`  // ⚠️ NoSQL injection
    });
};

// Direct object injection
const searchProducts = (query) => {
    return db.products.find(JSON.parse(query));  // ⚠️ NoSQL injection via query object
};
```

**Secure Code:**

```javascript
// Using Mongoose with schema validation
const findUser = async (username) => {
    return await User.findOne({ username });  // ✓ Schema validation
};

// Using typed queries with operators
const searchProducts = async (name) => {
    return await Product.find({
        name: { $regex: name, $options: 'i' }
    });
};
```

#### OS Command Injection

**Pattern**: Untrusted input used in system commands.

**Detection Rules:**

```yaml
rules:
  - id: python-command-injection
    languages: [python]
    message: OS command executed with untrusted input
    severity: ERROR
    patterns:
      - pattern-either:
          # os.system()
          - pattern: os.system($CMD + $VAR)
          # subprocess.run() with shell=True
          - pattern: subprocess.run($CMD + $VAR, shell=True)
          # subprocess.call()
          - pattern: subprocess.call($CMD + $VAR, shell=True)
```

**Vulnerable Code:**

```python
import os
import subprocess

# os.system() - highly vulnerable
def ping_host(hostname):
    os.system(f"ping -c 4 {hostname}")  # ⚠️ Command injection

# subprocess with shell=True
def process_file(filename):
    subprocess.run(f"cat {filename}", shell=True)  # ⚠️ Command injection
```

**Secure Code:**

```python
import subprocess

# Use list of arguments (no shell)
def ping_host(hostname):
    subprocess.run(['ping', '-c', '4', hostname])  # ✓ Safe

# Validate and sanitize
def process_file(filename):
    # Allow only alphanumeric, underscore, hyphen, dot
    if not re.match(r'^[A-Za-z0-9_\-\.]+$', filename):
        raise ValueError('Invalid filename')
    subprocess.run(['cat', filename])  # ✓ Safe
```

### A04:2021 - Insecure Design

**Definition**: New category for 2021 focusing on risks related to design flaws.

**Vulnerability Patterns**:
- Mass assignment
- Missing rate limiting
- Insecure direct object references (IDOR)
- Privilege escalation through weak design

**Detection Rules:**

```yaml
rules:
  - id: mass-assignment
    languages: [python, javascript, php]
    message: Potential mass assignment vulnerability
    severity: WARNING
    patterns:
      - pattern-either:
          # Flask: request.json directly assigned
          - pattern: |
              user_data = request.json
              user = User(**user_data)
          # Express: direct body assignment
          - pattern: |
              const user = new User(req.body)
```

**Vulnerable Code (Mass Assignment):**

```python
@app.route('/users', methods=['POST'])
def create_user():
    user_data = request.json  # Contains: {"username": "alice", "is_admin": true}
    user = User(**user_data)  # ⚠️ Attacker can set is_admin=True
    db.session.add(user)
    db.session.commit()
    return 'User created', 201
```

**Secure Code:**

```python
@app.route('/users', methods=['POST'])
def create_user():
    user_data = request.json
    # Whitelist allowed fields
    user = User(
        username=user_data.get('username'),
        email=user_data.get('email')
        # Explicitly exclude sensitive fields
    )
    db.session.add(user)
    db.session.commit()
    return 'User created', 201
```

### A05:2021 - Security Misconfiguration

**Definition**: Improperly configured security controls across all layers.

**Vulnerability Patterns**:
- Default credentials
- Debug mode enabled in production
- Verbose error messages
- CORS misconfiguration
- Missing security headers

**Detection Rules:**

```yaml
rules:
  - id: debug-mode-enabled
    languages: [python, javascript, php]
    message: Debug mode enabled (security risk in production)
    severity: WARNING
    patterns:
      - pattern-either:
          # Flask debug mode
          - pattern: app.run(debug=True)
          # Django debug
          - pattern: DEBUG = True
          # Express development error handler
          - pattern: app.use($ERRORHANDLER)

  - id: cors-permissive
    languages: [javascript, typescript]
    message: CORS allows all origins (security risk)
    severity: WARNING
    patterns:
      - pattern: |
          $APP.use(cors({ origin: "*" }))

  - id: default-credentials
    languages: [python, javascript, java, go]
    message: Default or example credentials detected
    severity: ERROR
    patterns:
      - pattern-either:
          - pattern: '"=~/admin.+:admin/"'
          - pattern: '"=~/root.+:root/"'
          - pattern: '"=~/password.+:123456/"'
```

**Vulnerable Code:**

```python
# Flask with debug mode
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)  # ⚠️ Debug mode exposes stack traces

# Django settings
DEBUG = True  # ⚠️ Detailed error messages
ALLOWED_HOSTS = ['*']  # ⚠️ Host header validation disabled
```

**Secure Code:**

```python
# Production configuration
import os

DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'  # ✓ Controlled by env var
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=DEBUG)
```

### A06:2021 - Vulnerable and Outdated Components

**Definition**: Using components with known vulnerabilities.

**Detection Strategy:**
This is typically handled by SCA (Software Composition Analysis), but SAST can detect:
- Use of vulnerable library functions
- Deprecated API usage

**Detection Rules:**

```yaml
rules:
  - id: vulnerable-library-import
    languages: [python, javascript, php, java]
    message: Import of library with known vulnerabilities
    severity: ERROR
    patterns:
      - pattern-either:
          # Pillow < 3.3.0 has PIL CVEs
          - pattern: from PIL import Image
          # lxml < 3.8.0 has multiple CVEs
          - pattern: import lxml

  - id: deprecated-api-usage
    languages: [python, javascript]
    message: Usage of deprecated API
    severity: WARNING
    patterns:
      - pattern-either:
          # Python: hashlib.md5 deprecated for passwords
          - pattern: hashlib.md5($PASSWORD)
          # Node.js: crypto.createHash deprecated in some contexts
          - pattern: crypto.createHash($ALGORITHM)
```

### A07:2021 - Identification and Authentication Failures

**Definition**: Confirmation of user identity, session management, and authentication.

**Vulnerability Patterns**:
- Weak passwords
- Hardcoded credentials
- Session fixation
- Missing authentication on sensitive endpoints

**Detection Rules:**

```yaml
rules:
  - id: weak-password-policy
    languages: [python, javascript, php, java]
    message: Password validation appears weak
    severity: WARNING
    patterns:
      - pattern-either:
          # Length check < 8 characters
          - pattern: |
              len($PASSWORD) < 8
          # No complexity requirements
          - pattern-either:
              - pattern: |
                  if $PASSWORD.isalnum():
              - pattern: |
                  if $PASSWORD.match(/[a-zA-Z0-9]+/):

  - id: session-fixation
    languages: [python, javascript, php]
    message: Potential session fixation - session ID not regenerated
    severity: ERROR
    patterns:
      - pattern-either:
          # Login doesn't set new session
          - pattern: |
              def login($USERNAME, $PASSWORD):
                  if check_credentials($USERNAME, $PASSWORD):
                      session['user_id'] = get_user_id($USERNAME)
                      return 'Login successful'
          # Missing session regeneration
          - pattern: |
              $SESSION['authenticated'] = True
```

**Vulnerable Code:**

```python
# Weak password check
@app.route('/register', methods=['POST'])
def register():
    password = request.json['password']
    if len(password) >= 6:  # ⚠️ Only length check, no complexity
        create_user(request.json)
        return 'User created', 201
    return 'Password too short', 400

# Session fixation
@app.route('/login', methods=['POST'])
def login():
    username = request.json['username']
    password = request.json['password']
    if check_credentials(username, password):
        session['user_id'] = get_user_id(username)
        # ⚠️ Session ID not regenerated, attacker can fix session
        return 'Login successful'
    return 'Invalid credentials', 401
```

**Secure Code:**

```python
import re

# Strong password policy
def is_strong_password(password):
    if len(password) < 12:
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'[0-9]', password):
        return False
    if not re.search(r'[!@#$%^&*]', password):
        return False
    return True

@app.route('/register', methods=['POST'])
def register():
    password = request.json['password']
    if not is_strong_password(password):
        return 'Password must be at least 12 characters and contain uppercase, lowercase, numbers, and special characters', 400
    create_user(request.json)
    return 'User created', 201

# Session management
@app.route('/login', methods=['POST'])
def login():
    username = request.json['username']
    password = request.json['password']
    if check_credentials(username, password):
        # Regenerate session ID to prevent fixation
        session.clear()  # ✓ Clear old session
        session['user_id'] = get_user_id(username)
        session['authenticated'] = True
        return 'Login successful'
    return 'Invalid credentials', 401
```

### A08:2021 - Software and Data Integrity Failures

**Definition**: Code and infrastructure without integrity protection.

**Vulnerability Patterns**:
- Insecure deserialization
- Insecure dependencies
- CI/CD pipeline vulnerabilities
- Unsigned or unverified updates

**Detection Rules:**

```yaml
rules:
  - id: insecure-deserialization
    languages: [python, javascript, php, java]
    message: Insecure deserialization of untrusted data
    severity: ERROR
    patterns:
      - pattern-either:
          # Python: pickle.load from user input
          - pattern: |
              pickle.loads($USER_INPUT)
          # Python: yaml.load (unsafe)
          - pattern: |
              yaml.load($USER_INPUT)
          # JavaScript: eval from user input
          - pattern: |
              eval($USER_INPUT)
          # JavaScript: JSON.parse is generally safe, but need context
          - pattern: |
              require('vm').runInThisContext($CODE)

  - id: library-without-integrity-check
    languages: [python, javascript]
    message: Installing dependencies without integrity verification
    severity: WARNING
    patterns:
      - pattern-either:
          # pip install without hash
          - pattern: |
              subprocess.run(["pip", "install", $PACKAGE])
          # npm install without --integrity
          - pattern: |
              subprocess.run(["npm", "install", $PACKAGE])
```

**Vulnerable Code (Insecure Deserialization):**

```python
import pickle

@app.route('/save_state', methods=['POST'])
def save_state():
    state = request.data  # User-provided serialized data
    data = pickle.loads(state)  # ⚠️ Arbitrary code execution via pickle
    # Process data...
    return 'State saved'
```

**Secure Code:**

```python
import json

@app.route('/save_state', methods=['POST'])
def save_state():
    state = request.data
    # Use safe deserialization (JSON)
    try:
        data = json.loads(state)  # ✓ Safe
    except json.JSONDecodeError:
        return 'Invalid JSON', 400
    # Process data...
    return 'State saved'
```

### A09:2021 - Security Logging and Monitoring Failures

**Definition**: Insufficient logging, monitoring, and integration with incident response.

**Vulnerability Patterns**:
- Missing logging for security events
- Logging sensitive data
- Insufficient error messages for debugging

**Detection Rules:**

```yaml
rules:
  - id: log-sensitive-data
    languages: [python, javascript, php, java]
    message: Logging potentially sensitive information
    severity: WARNING
    patterns:
      - pattern-either:
          # Logging passwords
          - pattern: |
              logger.info("Password: " + $PASSWORD)
          # Logging tokens
          - pattern: |
              logger.debug("Token: " + $TOKEN)
          # Logging full request with body
          - pattern: |
              logger.info(request.body)

  - id: missing-authz-logging
    languages: [python, javascript]
    message: Authorization failure not logged
    severity: WARNING
    patterns:
      - pattern-not-regex: |
          logger.(warn|error|critical)(.*unauthorized|forbidden)
      - pattern: |
          if not $CHECK:
              return Response("Unauthorized", 401)
```

**Vulnerable Code:**

```python
import logging

logger = logging.getLogger(__name__)

@app.route('/admin')
def admin_panel():
    if not current_user.is_admin:
        return 'Unauthorized', 403  # ⚠️ No logging of unauthorized access attempt
    # ... admin functionality ...

@app.route('/login', methods=['POST'])
def login():
    password = request.json['password']
    if check_password(password):
        logger.info(f"Successful login for {request.json['username']} with password {password}")  # ⚠️ Logging password!
        return 'Login successful'
    return 'Invalid credentials', 401
```

**Secure Code:**

```python
import logging

logger = logging.getLogger(__name__)

@app.route('/admin')
def admin_panel():
    if not current_user.is_admin:
        # ✓ Log security event
        logger.warning(f"Unauthorized admin access attempt by user {current_user.id} from {request.remote_addr}")
        return 'Unauthorized', 403
    # ... admin functionality ...

@app.route('/login', methods=['POST'])
def login():
    username = request.json['username']
    password = request.json['password']
    if check_password(username, password):
        # ✓ Log without sensitive data
        logger.info(f"Successful login for user {username} from {request.remote_addr}")
        return 'Login successful'
    # ✓ Log failed attempts (but not password)
    logger.warning(f"Failed login attempt for user {username} from {request.remote_addr}")
    return 'Invalid credentials', 401
```

### A10:2021 - Server-Side Request Forgery (SSRF)

**Definition**: Server fetches remote resource without validating URL.

**Vulnerability Pattern**: Untrusted URL passed to HTTP client or URL fetcher.

**Detection Rules:**

```yaml
rules:
  - id: ssrf-user-controlled-url
    languages: [python, javascript, php, go]
    message: URL fetched from user-controlled source (SSRF risk)
    severity: ERROR
    patterns:
      - pattern-either:
          # Python: requests.get with user input
          - pattern: |
              requests.get($URL)
              metavariable-regex:
                  metavariable: $URL
                  regex: (request\.(args|form|body|params)\..+)
          # Python: urllib
          - pattern: |
              urllib.request.urlopen($URL)
          # JavaScript: fetch
          - pattern: |
              fetch($URL)
          # PHP: file_get_contents
          - pattern: |
              file_get_contents($URL)
          # Go: http.Get
          - pattern: |
              http.Get($URL)
```

**Vulnerable Code (Python):**

```python
import requests

@app.route('/fetch_image')
def fetch_image():
    image_url = request.args.get('url')  # User-provided URL
    response = requests.get(image_url)  # ⚠️ SSRF - can access internal resources
    return response.content

@app.route('/proxy')
def proxy_request():
    target_url = request.json['url']  # User-provided URL
    response = requests.post(target_url, json=request.json)  # ⚠️ SSRF with POST
    return jsonify(response.json())
```

**Secure Code:**

```python
import requests
from urllib.parse import urlparse

# Whitelist of allowed domains
ALLOWED_DOMAINS = {'api.example.com', 'cdn.example.com'}

def is_safe_url(url):
    try:
        parsed = urlparse(url)
        # Check protocol
        if parsed.scheme not in ['http', 'https']:
            return False
        # Check domain against whitelist
        if parsed.netloc not in ALLOWED_DOMAINS:
            return False
        # Prevent accessing internal IPs
        if parsed.hostname in ['localhost', '127.0.0.1', '0.0.0.0']:
            return False
        return True
    except Exception:
        return False

@app.route('/fetch_image')
def fetch_image():
    image_url = request.args.get('url')
    if not is_safe_url(image_url):
        return 'Invalid URL', 400
    response = requests.get(image_url, timeout=5)  # ✓ Safe: validated URL
    return response.content
```

---

## Implementation Steps

### Phase 1: Architecture Design

**1.1 Core Components**

```
SAST Engine Components:

1. Parser Layer
   ├── Language-specific parsers (tree-sitter-*)
   ├── Source code extraction
   └── AST/CST generation

2. Analysis Layer
   ├── Pattern matching engine (Semgrep-style)
   ├── Taint analysis engine
   ├── Data flow analyzer
   └── Control flow graph builder

3. Rule Engine
   ├── Rule repository (YAML-based)
   ├── Rule loader and validator
   └── Rule execution engine

4. Reporting Layer
   ├── Vulnerability aggregator
   ├── False positive filter
   └── Report generator (SARIF, JSON, HTML)

5. Integration Layer
   ├── CI/CD adapters
   ├── IDE plugins
   └── API interface
```

**1.2 Data Flow Architecture**

```
Source Code Files
        ↓
Language Detection
        ↓
Parser Selection (tree-sitter-*)
        ↓
AST/CST Generation
        ↓
───────────────────────────┐
        ↓                       ↓
Pattern Matching          Taint Analysis Engine
(Semgrep rules)          (Source → Sink tracking)
        ↓                       ↓
Vulnerability Matches    Taint Flow Results
        ↓                       ↓
        └───────────┬──────────┘
                    ↓
            Vulnerability Aggregator
                    ↓
            Severity Scoring
                    ↓
            Report Generation
```

### Phase 2: Language Support Strategy

**2.1 Language-agnostic Parser**

```python
# Parser manager - language-agnostic entry point
class SASTParser:
    def __init__(self):
        self.parsers = {}
        self._load_parsers()

    def _load_parsers(self):
        """Load tree-sitter parsers for all supported languages"""
        supported_languages = [
            'python', 'javascript', 'typescript', 'java',
            'go', 'rust', 'c', 'cpp', 'php', 'ruby'
        ]
        for lang in supported_languages:
            try:
                self.parsers[lang] = self._get_parser(lang)
            except ImportError:
                logger.warning(f"Parser not available for {lang}")

    def _get_parser(self, language):
        """Get tree-sitter parser for language"""
        import tree_sitter
        from tree_sitter_languages import get_language

        lang_map = {
            'python': 'python',
            'javascript': 'javascript',
            'typescript': 'typescript',
            'java': 'java',
            'go': 'go',
            'rust': 'rust',
            'c': 'c',
            'cpp': 'cpp',
            'php': 'php',
            'ruby': 'ruby'
        }

        parser = tree_sitter.Parser()
        parser.set_language(get_language(lang_map[language]))
        return parser

    def parse(self, source_code, language):
        """Parse source code and return AST"""
        if language not in self.parsers:
            raise ValueError(f"Language {language} not supported")

        parser = self.parsers[language]
        tree = parser.parse(bytes(source_code, 'utf8'))
        return tree

    def detect_language(self, filepath):
        """Detect language from file extension"""
        ext_to_lang = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.go': 'go',
            '.rs': 'rust',
            '.c': 'c',
            '.cpp': 'cpp',
            '.h': 'c',
            '.php': 'php',
            '.rb': 'ruby'
        }
        for ext, lang in ext_to_lang.items():
            if filepath.endswith(ext):
                return lang
        return None
```

**2.2 Language-Specific Taint Sources and Sinks**

```python
# Taint configuration - language-specific security patterns
TAINT_CONFIG = {
    'python': {
        'sources': [
            'flask.request.args.get',
            'flask.request.form.get',
            'flask.request.values.get',
            'flask.request.cookies.get',
            'request.get_param',
            'cgi.FieldStorage.getvalue',
        ],
        'sinks': [
            'sqlite3.Cursor.execute',
            'psycopg2.cursor.execute',
            'pymongo.collection.Collection.find',
            'subprocess.run',
            'os.system',
            'eval',
            'exec',
        ],
        'sanitizers': [
            'html.escape',
            're.sub',
            'werkzeug.security.escape',
            'bleach.clean',
        ]
    },
    'javascript': {
        'sources': [
            'req.query',
            'req.body',
            'req.params',
            'req.cookies',
            'process.env',
        ],
        'sinks': [
            'query',
            'eval',
            'Function',
            'execSync',
            'spawn',
            'require("vm").runInThisContext',
        ],
        'sanitizers': [
            'validator.escape',
            'escape-html',
            'dompurify.sanitize',
        ]
    }
}
```

### Phase 3: Rule Engine Implementation

**3.1 Rule Loader**

```python
import yaml
from pathlib import Path

class RuleLoader:
    def __init__(self, rules_directory):
        self.rules_directory = Path(rules_directory)
        self.rules = {}

    def load_rules(self):
        """Load all YAML rules from directory"""
        for rule_file in self.rules_directory.glob('**/*.yaml'):
            self._load_rule_file(rule_file)
        return self.rules

    def _load_rule_file(self, rule_file):
        """Load a single rule file"""
        with open(rule_file, 'r') as yaml.safe_load() as f:
            rules = yaml.safe_load(f)

        for rule in rules:
            rule_id = rule.get('id', 'unknown')
            languages = rule.get('languages', [])
            for lang in languages:
                if lang not in self.rules:
                    self.rules[lang] = []
                self.rules[lang].append(rule)

    def get_rules_for_language(self, language):
        """Get all rules applicable to a language"""
        return self.rules.get(language, [])
```

**3.2 Pattern Matcher**

```python
import re
from tree_sitter import Node

class PatternMatcher:
    def __init__(self, rules):
        self.rules = rules

    def match(self, ast_root, language):
        """Match patterns against AST"""
        findings = []

        for rule in self.rules:
            if language in rule.get('languages', []):
                matches = self._match_rule(ast_root, rule)
                findings.extend(matches)

        return findings

    def _match_rule(self, ast_root, rule):
        """Match a single rule against AST"""
        pattern = rule.get('pattern', '')
        severity = rule.get('severity', 'ERROR')
        message = rule.get('message', 'Security issue detected')

        # Use tree-sitter query API for pattern matching
        # This is a simplified example
        matches = self._query_pattern(ast_root, pattern)

        findings = []
        for match in matches:
            findings.append({
                'rule_id': rule['id'],
                'severity': severity,
                'message': message,
                'location': match['location'],
                'code_snippet': match['snippet']
            })

        return findings

    def _query_pattern(self, root_node, pattern):
        """Query AST for pattern (simplified)"""
        # In a real implementation, this would use tree-sitter's
        # query language or a custom pattern matching engine
        matches = []

        # Simplified: traverse AST and find matching nodes
        # Real implementation would parse the pattern and execute queries
        def traverse(node):
            if self._node_matches_pattern(node, pattern):
                matches.append({
                    'location': f"{node.start_point[0]}:{node.start_point[1]}",
                    'snippet': node.text.decode('utf8')
                })
            for child in node.children:
                traverse(child)

        traverse(root_node)
        return matches

    def _node_matches_pattern(self, node, pattern):
        """Check if node matches pattern (simplified)"""
        # Real implementation would parse pattern syntax
        return True  # Placeholder
```

**3.3 Taint Analyzer**

```python
class TaintAnalyzer:
    def __init__(self, language):
        self.language = language
        self.config = TAINT_CONFIG.get(language, {})

    def analyze(self, ast_root):
        """Perform taint analysis on AST"""
        tainted_vars = set()
        findings = []

        # Find all source nodes (taint introduction)
        sources = self._find_sources(ast_root)
        for source in sources:
            var_name = source.get('variable')
            if var_name:
                tainted_vars.add(var_name)

        # Track taint propagation through data flow
        tainted_vars = self._track_taint_propagation(ast_root, tainted_vars)

        # Check if tainted variables reach sinks
        sinks = self._find_sinks(ast_root)
        for sink in sinks:
            if sink.get('variable') in tainted_vars:
                findings.append({
                    'type': 'taint-flow',
                    'source': sink.get('source_node'),
                    'sink': sink.get('location'),
                    'variable': sink.get('variable')
                })

        return findings

    def _find_sources(self, ast_root):
        """Find taint source nodes in AST"""
        sources = []
        source_patterns = self.config.get('sources', [])

        # Traverse AST and find source function calls
        def traverse(node):
            node_text = node.text.decode('utf8')
            for pattern in source_patterns:
                if pattern in node_text:
                    # Extract variable name (simplified)
                    sources.append({
                        'variable': self._extract_variable(node),
                        'location': f"{node.start_point[0]}:{node.start_point[1]}"
                    })
            for child in node.children:
                traverse(child)

        traverse(ast_root)
        return sources

    def _find_sinks(self, ast_root):
        """Find taint sink nodes in AST"""
        sinks = []
        sink_patterns = self.config.get('sinks', [])

        def traverse(node):
            node_text = node.text.decode('utf8')
            for pattern in sink_patterns:
                if pattern in node_text:
                    sinks.append({
                        'variable': self._extract_variable(node),
                        'location': f"{node.start_point[0]}:{node.start_point[1]}"
                    })
            for child in node.children:
                traverse(child)

        traverse(ast_root)
        return sinks

    def _track_taint_propagation(self, ast_root, tainted_vars):
        """Track taint propagation through assignments"""
        # Simplified: find assignments from tainted variables
        new_tainted = set(tainted_vars)

        def traverse(node):
            # Check for assignment: var = tainted_var
            node_text = node.text.decode('utf8')
            for tainted_var in tainted_vars:
                if f' = {tainted_var}' in node_text or f'={tainted_var}' in node_text:
                    # Extract assigned variable
                    assigned_var = self._extract_assignment_target(node)
                    if assigned_var:
                        new_tainted.add(assigned_var)
            for child in node.children:
                traverse(child)

        traverse(ast_root)
        return new_tainted

    def _extract_variable(self, node):
        """Extract variable name from node (simplified)"""
        # Real implementation would parse the AST node properly
        return "user_input"  # Placeholder

    def _extract_assignment_target(self, node):
        """Extract target variable from assignment node"""
        return "derived_input"  # Placeholder
```

### Phase 4: Integration and Testing

**4.1 Main SAST Engine**

```python
from pathlib import Path

class SASTEngine:
    def __init__(self, rules_dir):
        self.parser = SASTParser()
        self.rule_loader = RuleLoader(rules_dir)
        self.pattern_matcher = None  # Will be initialized with rules
        self.rules = {}

    def initialize(self):
        """Initialize the SAST engine"""
        self.rules = self.rule_loader.load_rules()
        self.pattern_matcher = PatternMatcher([])

    def scan_file(self, filepath):
        """Scan a single file for vulnerabilities"""
        # Read source code
        with open(filepath, 'r') as f:
            source_code = f.read()

        # Detect language
        language = self.parser.detect_language(filepath)
        if not language:
            return {'error': f'Unsupported file: {filepath}'}

        # Parse source code
        try:
            ast = self.parser.parse(source_code, language)
        except Exception as e:
            return {'error': f'Parse error in {filepath}: {str(e)}'}

        # Pattern matching
        rules = self.rule_loader.get_rules_for_language(language)
        pattern_findings = self.pattern_matcher.match(ast, language)

        # Taint analysis
        taint_analyzer = TaintAnalyzer(language)
        taint_findings = taint_analyzer.analyze(ast)

        # Aggregate findings
        all_findings = pattern_findings + taint_findings

        return {
            'file': filepath,
            'language': language,
            'findings': all_findings,
            'total_issues': len(all_findings)
        }

    def scan_directory(self, directory):
        """Scan all supported files in a directory"""
        results = []

        for filepath in Path(directory).rglob('*'):
            if filepath.is_file():
                result = self.scan_file(str(filepath))
                if 'error' not in result:
                    results.append(result)

        # Generate summary
        total_issues = sum(r['total_issues'] for r in results)
        return {
            'scanned_files': len(results),
            'total_issues': total_issues,
            'results': results
        }
```

**4.2 CI/CD Integration**

```yaml
# .github/workflows/sast.yml
name: SAST Scan

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  sast:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v3
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          pip install tree-sitter tree-sitter-languages pyyaml

      - name: Run SAST
        run: |
          python -m sast_engine --rules ./rules --scan ./src

      - name: Upload SARIF
        if: always()
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: results.sarif
```

**4.3 CLI Interface**

```python
import argparse
import json

def main():
    parser = argparse.ArgumentParser(description='SAST Scanner')
    parser.add_argument('--scan', required=True, help='Path to scan')
    parser.add_argument('--rules', required=True, help='Rules directory')
    parser.add_argument('--output', help='Output file (JSON)')
    parser.add_argument('--format', choices=['json', 'sarif'], default='json')

    args = parser.parse_args()

    # Initialize engine
    engine = SASTEngine(args.rules)
    engine.initialize()

    # Scan
    if Path(args.scan).is_file():
        result = engine.scan_file(args.scan)
        results = [result]
    else:
        results = engine.scan_directory(args.scan)

    # Output
    if args.format == 'json':
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
    elif args.format == 'sarif':
        sarif = convert_to_sarif(results)
        with open(args.output, 'w') as f:
            json.dump(sarif, f, indent=2)

if __name__ == '__main__':
    main()
```

### Phase 5: False Positive Mitigation

**5.1 False Positive Detection Strategies**

```python
class FalsePositiveFilter:
    def __init__(self, suppressions_file):
        self.suppressions = self._load_suppressions(suppressions_file)

    def _load_suppressions(self, filepath):
        """Load known false positive patterns"""
        with open(filepath, 'r') as f:
            return json.load(f)

    def filter_findings(self, findings):
        """Filter out known false positives"""
        filtered = []

        for finding in findings:
            if not self._is_suppressed(finding):
                filtered.append(finding)

        return filtered

    def _is_suppressed(self, finding):
        """Check if finding is a known false positive"""
        rule_id = finding.get('rule_id')
        location = finding.get('location')
        code_snippet = finding.get('code_snippet')

        for suppression in self.suppressions:
            if (suppression['rule_id'] == rule_id and
                suppression['code_pattern'] in code_snippet):
                return True

        return False
```

**5.2 Context-Aware Analysis**

```python
class ContextAnalyzer:
    def __init__(self):
        self.context_patterns = {
            'test_file': re.compile(r'(test_|tests?\.py|_test\.py)$'),
            'example_code': re.compile(r'(example|sample|demo)'),
            'migrations': re.compile(r'migrations?/')
        }

    def is_test_code(self, filepath):
        """Check if file is test code (might have intentional vulnerabilities)"""
        return self.context_patterns['test_file'].search(filepath) is not None

    def is_example_code(self, filepath):
        """Check if file is example/demo code"""
        return self.context_patterns['example_code'].search(filepath) is not None

    def should_suppress(self, finding, filepath):
        """Determine if finding should be suppressed based on context"""
        if self.is_test_code(filepath):
            return True  # Test files often have intentional vulnerabilities
        if self.is_example_code(filepath):
            return True  # Example code may not be security-critical
        return False
```

---

## References

### Academic and Theoretical References

1. **Allen, F. E.** (1970). "Control flow analysis." *SIGPLAN Notices*, 5(7), 1-19. doi:10.1145/390013.808479

2. **Cousot, P., & Cousot, R.** (1977). "Abstract interpretation: A unified lattice model for static analysis of programs by construction or approximation of fixpoints." *Conference Record of the Fourth ACM Symposium on Principles of Programming Languages*, 238-252.

3. **Kildall, G. A.** (1973). "A unified approach to global program optimization." *Proceedings of the 1st Annual ACM SIGACT-SIGPLAN Symposium on Principles of Programming Languages*, 194-206. doi:10.1145/512927.512945

4. **Nielson, F., Nielson, H. R., & Hankin, C.** (2005). *Principles of Program Analysis*. Springer. ISBN 978-3-540-65410-0.

5. **Sabelfeld, A., & Myers, A. C.** (2003). "Language-based information-flow security." *IEEE Journal on Selected Areas in Communications*, 21(1), 5-19.

6. **Ligatti, J., Bauer, L., & Walker, D.** (2005). "Edit automata: Enforcement mechanisms for run-time security policies." *International Journal of Information Security*, 4(1-2), 5-26.

### OWASP References

1. **OWASP Foundation.** "OWASP Top Ten 2021." https://owasp.org/Top10/
2. **OWASP Foundation.** "SQL Injection." https://owasp.org/www-community/attacks/SQL_Injection
3. **OWASP Foundation.** "Cross-Site Scripting (XSS)." https://owasp.org/www-community/attacks/xss/
4. **OWASP Foundation.** "Source Code Analysis Tools." https://owasp.org/www-community/Source_Code_Analysis_Tools
5. **OWASP Foundation.** "SQL Injection Prevention Cheat Sheet." https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html
6. **OWASP Foundation.** "Cross-Site Scripting (XSS) Prevention Cheat Sheet." https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html

### CWE References

1. **MITRE.** "CWE-89: Improper Neutralization of Special Elements used in an SQL Command ('SQL Injection')." https://cwe.mitre.org/data/definitions/89.html
2. **MITRE.** "CWE-79: Improper Neutralization of Input During Web Page Generation ('Cross-site Scripting')." https://cwe.mitre.org/data/definitions/79.html
3. **MITRE.** "CWE-78: Improper Neutralization of Special Elements used in an OS Command ('OS Command Injection')." https://cwe.mitre.org/data/definitions/78.html
4. **MITRE.** "CWE-22: Improper Limitation of a Pathname to a Restricted Directory ('Path Traversal')." https://cwe.mitre.org/data/definitions/22.html
5. **MITRE.** "CWE-918: Server-Side Request Forgery (SSRF)." https://cwe.mitre.org/data/definitions/918.html
6. **MITRE.** "CWE-502: Deserialization of Untrusted Data." https://cwe.mitre.org/data/definitions/502.html

### Tools and Frameworks References

1. **Semgrep.** "Semgrep Documentation." https://semgrep.dev/docs/
2. **Semgrep.** "Semgrep Rules Repository." https://github.com/returntocorp/semgrep-rules
3. **Tree-sitter.** "Tree-sitter Documentation." https://tree-sitter.github.io/
4. **SonarQube.** "SonarQube Documentation." https://docs.sonarqube.org/
5. **GitHub.** "GitHub Advanced Security." https://github.com/features/security
6. **OWASP.** "OWASP Dependency-Check." https://owasp.org/www-project-dependency-check/

### Additional Resources

1. **Aho, A. V., Lam, M. S., Sethi, R., & Ullman, J. D.** (2006). *Compilers: Principles, Techniques, and Tools* (2nd ed.). Pearson. ISBN 978-0321486813.

2. **Muchnick, S. S.** (1997). *Advanced Compiler Design and Implementation*. Morgan Kaufmann. ISBN 978-1-55860-3202.

3. **Dowd, M., McDonald, J., & Schuh, J.** (2006). *The Art of Software Security Assessment*. Addison-Wesley.

4. **OWASP.** "OWASP Testing Guide." https://owasp.org/www-project-web-security-testing-guide/

5. **CISA.** "Secure-by-Design Alert: Eliminating SQL Injection Vulnerabilities in Software." https://www.cisa.gov/resources-tools/resources/secure-design-alert-eliminating-sql-injection-vulnerabilities-software

---

## Appendix A: Quick Reference

### Common Vulnerability Patterns

| Vulnerability | Pattern | Severity | Example Sink |
|--------------|---------|-----------|--------------|
| SQL Injection | String concat + SQL query | Critical | `execute("... " + user_input)` |
| XSS | Untrusted data + HTML output | High | `innerHTML = user_input` |
| Command Injection | Untrusted data + system() | Critical | `os.system(cmd + user_input)` |
| Path Traversal | Untrusted data + file open | High | `open(path + user_input)` |
| SSRF | Untrusted data + HTTP request | Critical | `requests.get(user_url)` |
| Weak Crypto | MD5, SHA1, DES | Medium | `hashlib.md5(data)` |

### Rule Template

```yaml
rules:
  - id: unique-rule-id
    languages: [language1, language2]
    message: Description of the security issue
    severity: ERROR  # or WARNING, INFO
    metadata:
      cwe: "CWE-ID"
      owasp: "A01:2021"
      references:
        - "https://owasp.org/..."
    patterns:
      - pattern: |
          $VULNERABLE_CODE_PATTERN
      - pattern-not: |
          $SECURE_ALTERNATIVE
```

### Severity Classification

- **Critical**: Exploitable without authentication, can lead to full system compromise
- **High**: Exploitable with authentication, significant impact
- **Medium**: Limited exploitability, moderate impact
- **Low**: Minor security issues, low impact
- **Info**: Best practices, not directly exploitable

---

*Document Version: 1.0*
*Last Updated: February 2026*
*Author: SAST Research Team*
*License: Internal Use Only*
