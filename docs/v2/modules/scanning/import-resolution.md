# scanning/ Import Resolution

How import declarations in source code are resolved to file paths within the project. This is the critical bridge between scanning/ (IR1) and graph/ (IR3) -- every resolved import becomes an IMPORT edge in the dependency graph.

---

## Overview

For each `ImportDecl` extracted by tree-sitter, the import resolver determines:

1. `resolved_path: str | None` -- the project-relative file path this import points to
2. `is_external: bool` -- whether the import targets a package outside the project tree
3. `is_relative: bool` -- whether the import uses relative syntax

The algorithm runs inside scanning/ as a post-processing step after all files have been parsed. It needs the full file list to resolve cross-file references.

---

## Resolution Algorithm

For each import declaration in each file:

```
1. CLASSIFY the import syntax:
   - Relative import?  (leading dots, ./, require_relative)
   - Absolute import?  (fully qualified path or module name)

2. If RELATIVE:
   a. Compute candidate path from importing file's directory + relative path
   b. Try candidate + language-specific suffixes (.py, /index.ts, etc.)
   c. If found → resolved_path = candidate, is_external = False
   d. If not found → resolved_path = None, is_external = False
      (broken relative import — will become phantom)

3. If ABSOLUTE:
   a. Search project file index for matching path
   b. Try language-specific resolution rules (see below)
   c. If found → resolved_path = match, is_external = False
   d. If not found:
      i.  Check against known external packages (stdlib + installed)
      ii. If known external → resolved_path = None, is_external = True
      iii. If unknown → resolved_path = None, is_external = False
           (phantom candidate — might be external, might be broken)
```

### Resolution priority

When multiple files could match an import, the resolver applies this priority:

1. Exact path match (with extension)
2. Package `__init__.py` / `index.ts` / `mod.rs` match
3. Same-directory match (shortest path)
4. Deepest common ancestor match

Ambiguous matches (multiple candidates at same priority) are resolved to the first match alphabetically and flagged with a warning.

---

## Per-Language Import Syntax

### Python

```python
# Relative imports — dot count determines parent directory levels
from . import utils              # same package
from ..models import User        # parent package
from ...core.db import engine    # grandparent package

# Absolute imports
import os.path                   # stdlib
from django.db import models     # external
from myapp.auth import service   # internal
```

**Resolution rules:**
- `from .X import Y` -> look in `dirname(importing_file)/X.py` or `dirname(importing_file)/X/__init__.py`
- `from ..X import Y` -> look in `dirname(dirname(importing_file))/X.py` or `.../X/__init__.py`
- `import X.Y.Z` -> search for `X/Y/Z.py`, `X/Y/Z/__init__.py` relative to project root and any `src/` directory
- Python packages are identified by `__init__.py` presence

**External detection:**
- Python stdlib modules: hardcoded list (~300 modules) for Python 3.9-3.13
- Installed packages: check `pyproject.toml` / `setup.cfg` / `requirements.txt` for declared dependencies

### Go

```go
import "fmt"                          // stdlib
import "github.com/gin-gonic/gin"     // external
import "myproject/internal/auth"      // internal

import (                              // grouped
    "fmt"
    "myproject/handlers"
)
```

**Resolution rules:**
- Go imports are full module paths
- Internal imports start with the module name from `go.mod`
- `import "myproject/pkg/auth"` -> look for `pkg/auth/*.go` files
- Go packages are directories (any `.go` file in the directory)

**External detection:**
- Read `go.mod` for module name; imports not starting with that prefix are external
- Stdlib: `fmt`, `os`, `net/http`, etc. (hardcoded list)

### TypeScript / JavaScript

```typescript
import { User } from './models';          // relative
import { Router } from 'express';         // external (bare specifier)
import config from '../config';           // relative, default import
import * as utils from './utils/index';   // relative, namespace import
```

**Resolution rules:**
- Relative imports: `./X` -> try `X.ts`, `X.tsx`, `X.js`, `X.jsx`, `X/index.ts`, `X/index.js`
- If `tsconfig.json` exists, read `paths` and `baseUrl` for alias resolution
- Bare specifiers (no `.` or `/` prefix) are external unless matched by `tsconfig.paths`

**External detection:**
- Read `package.json` `dependencies` + `devDependencies`
- Bare specifier not in package.json -> still external (transitive dependency or error)

### Java

```java
import java.util.List;                    // stdlib
import com.google.common.collect.ImmutableList;  // external
import com.myapp.auth.AuthService;         // internal
import static com.myapp.utils.Helpers.*;   // static import
```

**Resolution rules:**
- Convert dotted path to directory path: `com.myapp.auth.AuthService` -> `com/myapp/auth/AuthService.java`
- Search from source roots (`src/main/java/`, `src/`, project root)
- Static imports resolve to the containing class file

**External detection:**
- `java.*`, `javax.*`, `sun.*` -> stdlib
- Read `pom.xml` / `build.gradle` for declared dependencies

### Rust

```rust
use std::collections::HashMap;        // stdlib
use serde::Deserialize;               // external crate
use crate::auth::service;             // internal (crate-relative)
use super::models;                    // relative (parent module)
```

**Resolution rules:**
- `crate::X::Y` -> look for `src/X/Y.rs` or `src/X/Y/mod.rs`
- `super::X` -> look in parent directory
- `self::X` -> look in current directory

**External detection:**
- `std::*` -> stdlib
- Read `Cargo.toml` `[dependencies]` for external crates

### Ruby

```ruby
require 'json'                         # stdlib or gem
require 'rails/railtie'               # external gem
require_relative './models/user'       # relative
```

**Resolution rules:**
- `require_relative` paths are resolved from the requiring file's directory
- `require` paths are searched in `lib/` directory relative to project root
- Append `.rb` if no extension

**External detection:**
- Read `Gemfile` for declared gems
- Ruby stdlib modules: hardcoded list

### C/C++

```c
#include <stdio.h>                     // system header
#include "auth/service.h"              // project header
#include "../common/types.h"           // relative header
```

**Resolution rules:**
- `"..."` (quotes): search relative to including file, then project root
- `<...>` (angle brackets): always external (system headers)
- Try path as-is, then with common source directories (`src/`, `include/`)

**External detection:**
- Angle bracket includes are always external
- Quote includes not found in project are external

---

## Entry Point Detection

As a side effect of import resolution, scanning/ identifies entry point files. These are files that are never imported by other project files and serve as program entry points.

| Language | Entry point patterns |
|----------|---------------------|
| Python | `if __name__ == "__main__"` guard, or file named `__main__.py`, `wsgi.py`, `asgi.py`, `manage.py` |
| Go | `func main()` in `package main` |
| TypeScript/JS | File referenced in `package.json` `main`/`bin` fields |
| Java | `public static void main(String[] args)` |
| Rust | `fn main()` in `src/main.rs` or `src/bin/*.rs` |
| Ruby | File with `#!/usr/bin/env ruby` shebang or referenced in Gemfile `executables` |
| C/C++ | `int main(` function definition |

Entry points are tagged in `FileSyntax` (or communicated to semantics/ for role classification as `ENTRY_POINT`). graph/ uses entry points for DAG depth computation (signal #19 `depth`).

---

## Phantom Imports

An import where `resolved_path = None AND is_external = False` is a **phantom import** -- it references something that should be in the project but cannot be found. Possible causes:

1. Typo in import path
2. File was deleted but import was not updated
3. Code generated at build time (not present at analysis time)
4. Dynamic import pattern not recognized by the resolver

Phantom imports feed signal #21 `phantom_import_count` (see `registry/signals.md`). graph/ creates `UnresolvedEdge` entries for these.

### What exists today vs what's new

- **EXISTS TODAY**: `FileMetrics.imports` is a flat list of raw import strings. No resolution is performed in v1. graph/ does basic path matching to build edges.
- **NEW IN v2**: Import resolution runs inside scanning/ as a post-processing pass. `ImportDecl.resolved_path` gives graph/ pre-resolved edges. The file index required for resolution is built during the scanning pass itself.
