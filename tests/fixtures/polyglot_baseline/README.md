# Polyglot Baseline - Test Fixtures

Reference implementations for shannon-insight testing across multiple languages.

## Python Service

**Location**: `./python_service/`

Production-quality FastAPI service demonstrating:
- RESTful API design with proper HTTP semantics
- JWT authentication and role-based access control
- Service layer architecture with dependency injection
- Comprehensive input validation with Pydantic
- Structured error handling with custom exceptions
- Type-safe code with full type hints
- Organized module structure (api, models, services, utils)

**Statistics**:
- 22 files (1,766 lines of Python)
- 12 REST endpoints (Users and Organizations CRUD)
- 5 layers: HTTP, Business Logic, Data, Utilities, Configuration

**Ready for Analysis**:
- Python AST scanning and parsing
- Module dependency graph building
- Signal computation (cognitive load, entropy, centrality)
- Finder testing (god modules, tight coupling, boundary mismatches)
- Temporal analysis (co-change patterns, bus factor)
- Role classification (entry points, models, utilities)
- Architecture extraction (layered structure)

See `python_service/README.md` for full documentation.

## Intended Use

These fixtures provide realistic, production-quality code for:

1. **Baseline Testing**: Establish expected behavior on known-good code
2. **Regression Testing**: Ensure shannon-insight doesn't regress on realistic code
3. **Performance Testing**: Measure tool speed on multi-file codebases
4. **Feature Testing**: Validate new analyzers, finders, and signals
5. **Temporal Simulation**: Generate change history for time-based analysis
6. **Broken Variants**: Create intentional issues (dead code, violations) for finder validation

## Future Additions

- [ ] Go service implementation (similar architecture)
- [ ] TypeScript service implementation (similar architecture)
- [ ] Rust implementation (demonstrates different paradigms)
- [ ] Broken variants with known issues
- [ ] Git history simulation for temporal analysis
- [ ] Test files mirroring main code structure
- [ ] Configuration files (pyproject.toml, setup.py, etc.)

## Design Philosophy

- **Realistic**: Uses production frameworks (FastAPI, Pydantic, etc.)
- **Focused**: No bloat (no DB migrations, no Docker configs, no tests)
- **Analyzable**: Clear structure for signal computation and finder validation
- **Multi-purpose**: Suitable for multiple types of analysis
- **Well-documented**: README + docstrings for understanding

## File Organization

```
polyglot_baseline/
├── README.md (this file)
├── PYTHON_SERVICE_SUMMARY.md
└── python_service/
    ├── README.md
    ├── MANIFEST.md
    ├── __init__.py
    ├── main.py
    ├── config.py
    ├── exceptions.py
    ├── api/
    │   ├── routes.py
    │   ├── middleware.py
    │   └── dependencies.py
    ├── models/
    │   ├── user.py
    │   ├── organization.py
    │   └── permissions.py
    ├── services/
    │   ├── user_service.py
    │   ├── org_service.py
    │   └── auth_service.py
    └── utils/
        ├── validators.py
        ├── crypto.py
        └── logging.py
```

## Contributing New Fixtures

When adding new language implementations:

1. Follow the same service architecture (API → Services → Models → Utilities)
2. Implement user/organization management as the domain
3. Include authentication and authorization
4. Use language-native frameworks (not toy implementations)
5. Document with README and manifest
6. Aim for 1,500-2,000 lines of code
7. Ensure code compiles/runs without external configuration
8. Include type safety features for the language

This ensures consistency and maximum value for analysis testing.
