# TypeScript/React Frontend - Test Fixture

This is a realistic, production-quality TypeScript/React codebase fixture for polyglot scanning tests.

## Architecture

### Entry Point
- **index.tsx** - React app initialization with root element mounting
- **App.tsx** - Main app component with routing, lazy loading, and authentication provider

### Pages
- **pages/Dashboard.tsx** - User dashboard with account overview
- **pages/UsersPage.tsx** - User management page with CRUD operations
- **pages/OrganizationsPage.tsx** - Organization management page with CRUD operations

### Components
- **components/Navbar.tsx** - Navigation bar with user menu and auth state
- **components/LoginForm.tsx** - Login form with email/password validation
- **components/UserForm.tsx** - User create/edit form with role selection
- **components/UserList.tsx** - Paginated user list with edit/delete actions
- **components/OrgForm.tsx** - Organization create/edit form
- **components/OrgList.tsx** - Paginated organization list
- **components/ProtectedRoute.tsx** - Route guard for authenticated pages

### Hooks
- **hooks/useAuth.ts** - Authentication context provider and hook with token refresh
- **hooks/useApi.ts** - Generic API fetch hook with pagination support
- **hooks/useForm.ts** - Form state management with validation support

### Utilities
- **utils/api.ts** - Axios instance with interceptors for auth and error handling
- **utils/storage.ts** - LocalStorage wrapper for token/user persistence
- **utils/validators.ts** - Form validation functions for email, password, name, slug, URL

### Types
- **types/api.ts** - API response and error types
- **types/user.ts** - User, auth, and role related types
- **types/organization.ts** - Organization and member related types

## Features

### Authentication
- Context-based auth state management
- JWT token handling with refresh flow
- Automatic token refresh on 401 responses
- Protected routes with role-based access control

### Forms
- Custom form hook with field state management
- Built-in validation with error messages
- Support for create and edit modes
- Async form submission with loading states

### API Integration
- Axios client with request/response interceptors
- Centralized error handling
- Automatic auth token injection
- Pagination support

### Validation
- Email validation with regex
- Password validation (8+ chars, uppercase, number)
- Name validation with length constraints
- Slug validation (lowercase, numbers, hyphens)
- URL validation with built-in URL API

## Code Quality

- Full TypeScript type coverage
- React hooks best practices
- Error boundaries and loading states
- Responsive Tailwind CSS styling
- Proper separation of concerns
- DRY principle in validators and API utilities
