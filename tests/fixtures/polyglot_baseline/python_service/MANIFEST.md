# Python Service Fixture Manifest

## Overview
Production-quality Python FastAPI service codebase for testing shannon-insight analyzers.

Total: **16 files**, **1,766 lines of code**

## Files Created

### Root Level (3 files)
1. `__init__.py` (14 lines) - Package initialization with version info
2. `config.py` (60 lines) - Pydantic settings with environment configuration
3. `exceptions.py` (72 lines) - Custom exception hierarchy with HTTP status codes
4. `main.py` (86 lines) - FastAPI app factory and entry point

### API Module (4 files)
5. `api/__init__.py` (5 lines) - Router exports
6. `api/routes.py` (218 lines) - REST endpoints for users and organizations (CRUD)
7. `api/middleware.py` (101 lines) - Request logging, auth context, exception handling
8. `api/dependencies.py` (137 lines) - Dependency injection for services and auth

### Models Module (4 files)
9. `models/__init__.py` (20 lines) - Model exports
10. `models/user.py` (66 lines) - Pydantic User models (Create, Update, Response)
11. `models/organization.py` (71 lines) - Pydantic Org models (Create, Update, Response)
12. `models/permissions.py` (87 lines) - Role enums, Permission enums, role-permission mapping

### Services Module (4 files)
13. `services/__init__.py` (7 lines) - Service exports
14. `services/user_service.py` (200 lines) - User CRUD and business logic
15. `services/org_service.py` (204 lines) - Organization CRUD and member management
16. `services/auth_service.py` (130 lines) - JWT authentication and token management

### Utils Module (4 files)
17. `utils/__init__.py` (17 lines) - Utility exports
18. `utils/validators.py` (106 lines) - Email, password, username validation
19. `utils/crypto.py` (101 lines) - Password hashing, JWT token generation/verification
20. `utils/logging.py` (64 lines) - Structured JSON logging setup

### Documentation (1 file)
21. `README.md` - Full documentation with API endpoints and architecture

## Code Quality Metrics

### Imports & Dependencies
- ✅ Proper inter-module imports
- ✅ Relative imports within package
- ✅ FastAPI, Pydantic, PyJWT, Passlib dependencies

### Type Hints
- ✅ 100% function signatures typed
- ✅ Optional, dict, list, tuple used correctly
- ✅ Protocol interfaces for extensibility

### Validation
- ✅ Pydantic models for all API data
- ✅ Custom validators (email, password, username)
- ✅ Regex patterns for format validation

### Error Handling
- ✅ Custom exception hierarchy with HTTP status codes
- ✅ Graceful error responses
- ✅ Exception middleware for centralized handling

### Business Logic
- ✅ User CRUD with email/username uniqueness
- ✅ Password strength requirements
- ✅ Organization member management
- ✅ Role-based access control
- ✅ JWT authentication flow

### Architecture Patterns
- ✅ Service layer for business logic
- ✅ Dependency injection via FastAPI Depends
- ✅ Middleware stack for cross-cutting concerns
- ✅ Model-View-Controller (MVC) style
- ✅ Enum-based enumerations (not magic strings)

## Analysis Targets

This fixture is designed to exercise:

### Graph Analysis
- Multiple modules with clear dependencies
- Cross-module imports (api → services → models)
- Circular dependency detection (if introduced)
- Module coupling measurements

### Signal Computation
- Structural entropy (many vs. few dependencies)
- Cognitive load (complex functions with business logic)
- Network centrality (core services vs. utilities)
- Churn volatility (multiple files with high change frequency)
- Semantic coherence (coherent user/org namespaces)

### Finder Triggers
- God modules (could flag auth_service or user_service if metrics high)
- Highly coupled modules
- Hidden coupling via shared dependencies
- Architecture violations (if layering is defined)
- Boundary mismatches (API ↔ Services ↔ Models)

### Temporal Analysis
- Co-change patterns (services + models often change together)
- Bus factor calculation
- Author entropy
- Refactoring vs. bug-fix classification

### Role Classification
- Entry points: `main.py` with `if __name__`
- Models: `models/` module
- Utilities: `utils/` module
- Configuration: `config.py`
- Test-like patterns (validators, exception handling)

## Realistic Features

- ✅ Real password validation with strength requirements
- ✅ JWT token creation and verification
- ✅ Bcrypt password hashing
- ✅ Pydantic model validation
- ✅ CORS middleware setup
- ✅ Structured JSON logging
- ✅ Request tracing with X-Request-ID
- ✅ Role-based access control with dependency injection
- ✅ Exception mapping to HTTP status codes
- ✅ Database connection abstraction

## Not Included (Intentional)

- Database implementation (in-memory store for demo)
- Full ORM/SQLAlchemy integration
- Migration scripts
- Unit tests (tests are separate)
- Deployment configuration (Docker, k8s)
- Background tasks
- WebSocket support

These omissions keep the fixture focused on code structure analysis.
