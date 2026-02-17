# User Management Service

A production-grade FastAPI service for managing users and organizations with JWT authentication, role-based access control, and comprehensive logging.

## Project Structure

```
python_service/
├── __init__.py              # Package initialization with version
├── main.py                  # FastAPI app entry point
├── config.py                # Pydantic settings with environment overrides
├── exceptions.py            # Custom exception hierarchy
├── api/
│   ├── __init__.py
│   ├── routes.py            # REST endpoints (CRUD operations)
│   ├── middleware.py        # Auth, logging, and exception handling middleware
│   └── dependencies.py      # Dependency injection for services and auth
├── models/
│   ├── __init__.py
│   ├── user.py              # Pydantic models for user data
│   ├── organization.py      # Pydantic models for org data
│   └── permissions.py       # Role and permission enums/models
├── services/
│   ├── __init__.py
│   ├── user_service.py      # User business logic (CRUD, validation)
│   ├── org_service.py       # Organization business logic (CRUD, members)
│   └── auth_service.py      # JWT token and authentication logic
└── utils/
    ├── __init__.py
    ├── validators.py        # Email, password, username validation
    ├── crypto.py            # Password hashing and token generation
    └── logging.py           # Structured JSON logging setup
```

## Key Features

### Authentication & Authorization
- JWT token-based authentication
- Role-based access control (Admin, Manager, Member)
- Fine-grained permissions system
- Token expiration and refresh support

### User Management
- CRUD operations on users
- Email and username uniqueness validation
- Password strength validation (uppercase, lowercase, digits, special chars)
- User activation/deactivation
- Role assignment

### Organization Management
- CRUD operations on organizations
- Member management with role assignment
- Org ownership and hierarchy
- Multi-tenancy support

### Infrastructure
- Structured JSON logging with context propagation
- Request tracing with unique request IDs
- CORS middleware configuration
- Exception handling with proper HTTP status codes
- Dependency injection pattern for services

## API Endpoints

### Users
- `POST /api/v1/users` - Create user
- `GET /api/v1/users/{user_id}` - Get user
- `GET /api/v1/users` - List users (admin only)
- `PUT /api/v1/users/{user_id}` - Update user
- `DELETE /api/v1/users/{user_id}` - Delete user (admin only)

### Organizations
- `POST /api/v1/organizations` - Create org
- `GET /api/v1/organizations/{org_id}` - Get org
- `GET /api/v1/organizations` - List orgs
- `PUT /api/v1/organizations/{org_id}` - Update org
- `DELETE /api/v1/organizations/{org_id}` - Delete org
- `POST /api/v1/organizations/{org_id}/members` - Add member
- `DELETE /api/v1/organizations/{org_id}/members/{user_id}` - Remove member

## Configuration

Settings are loaded from environment variables with `.env` file support:

```env
HOST=0.0.0.0
PORT=8000
DEBUG=false
DATABASE_URL=sqlite:///./app.db
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
LOG_LEVEL=INFO
```

## Code Characteristics

### Type Hints
- Full type annotations throughout
- Proper use of Optional, Union, List for type safety

### Validation
- Pydantic models for request/response validation
- Custom validators for email, password, username
- Automatic HTTP 422 responses for validation errors

### Error Handling
- Custom exception hierarchy (AppException base)
- Proper HTTP status codes (401, 403, 404, 409, 422, 500)
- Exception middleware for centralized handling
- Structured error responses

### Dependencies
- FastAPI for web framework
- Pydantic for data validation
- PyJWT for token handling
- Passlib + bcrypt for password hashing
- Uvicorn for ASGI server

### Design Patterns
- Service layer for business logic
- Dependency injection for loosely coupled components
- Middleware stack for cross-cutting concerns
- Enum-based roles and permissions
- Structured logging with context

## Production Considerations

- ✅ Proper password hashing with bcrypt
- ✅ JWT token-based authentication
- ✅ CORS configuration
- ✅ Structured logging for observability
- ✅ Comprehensive input validation
- ✅ Role-based access control
- ✅ Exception handling and error responses
- ✅ Request tracing with X-Request-ID
- ✅ Performance tracking (X-Process-Time header)
- ✅ Type hints for IDE support and type checking

## Testing Fixture Features

This fixture provides realistic production-quality code suitable for:
- Codebase analysis tools
- Graph algorithm testing (dependency graphs, centrality)
- Signal computation (complexity, coupling, cohesion)
- Module detection and architecture extraction
- Temporal analysis (churn, volatility)
- Role classification (entry points, models, tests)
