# TypeScript/React Frontend Fixture - Complete Manifest

**Total Files:** 24 files  
**Total Lines:** 1,913 lines of code  
**Language:** TypeScript/React (TSX)

## File Structure with Line Counts

### Entry Points (79 lines)
- `index.tsx` (17 lines) - React root initialization
- `App.tsx` (62 lines) - Main app with routing and providers

### Pages (189 lines)
- `pages/Dashboard.tsx` (59 lines) - Dashboard with stats cards
- `pages/UsersPage.tsx` (65 lines) - User management interface
- `pages/OrganizationsPage.tsx` (65 lines) - Organization management interface

### Components (882 lines)
- `components/Navbar.tsx` (91 lines) - Navigation with user menu
- `components/ProtectedRoute.tsx` (32 lines) - Auth route wrapper
- `components/LoginForm.tsx` (105 lines) - Login with validation
- `components/UserForm.tsx` (189 lines) - User CRUD form
- `components/UserList.tsx` (131 lines) - Paginated user table
- `components/OrgForm.tsx` (202 lines) - Organization CRUD form
- `components/OrgList.tsx` (129 lines) - Paginated org table

### Custom Hooks (315 lines)
- `hooks/useAuth.ts` (95 lines) - Auth context and provider
- `hooks/useApi.ts` (104 lines) - Generic fetch hook with pagination
- `hooks/useForm.ts` (116 lines) - Form state management

### Utilities (272 lines)
- `utils/api.ts` (112 lines) - Axios client with interceptors
- `utils/validators.ts` (77 lines) - Form validation functions
- `utils/storage.ts` (83 lines) - LocalStorage token management

### Type Definitions (116 lines)
- `types/api.ts` (27 lines) - API response types
- `types/user.ts` (44 lines) - User and auth types
- `types/organization.ts` (44 lines) - Organization types
- `types/index.ts` (1 line) - Barrel export

## Key Features Demonstrated

### Authentication Flow
1. **useAuth Hook** - Context-based auth state (login, logout, user)
2. **Token Management** - JWT handling in localStorage with expiry checking
3. **Auto Refresh** - Axios interceptor with automatic token refresh on 401
4. **Protected Routes** - Higher-order component guarding authenticated pages
5. **Persistent State** - Auth state restored on app load

### Form Management
1. **useForm Hook** - Generic form state with validation
2. **Field State** - values, errors, touched tracking
3. **Async Submission** - Loading states during API calls
4. **Custom Validators** - Email, password, name, slug, URL patterns
5. **Edit/Create Modes** - Reusable forms for both operations

### API Integration
1. **Axios Client** - Configured base URL, timeouts, headers
2. **Request Interceptors** - Automatic Bearer token injection
3. **Response Interceptors** - Error handling and token refresh logic
4. **Error Handling** - Centralized error formatting
5. **Pagination** - usePaginatedApi hook with page/limit

### Component Patterns
1. **Lazy Loading** - React.lazy with Suspense fallback
2. **Error Boundaries** - Error display in forms and lists
3. **Loading States** - Disabled buttons, "Loading..." text
4. **Responsive Design** - Tailwind grid layouts
5. **Semantic HTML** - Proper form structure with labels

### Type Safety
- Full TypeScript coverage with no `any` abuse
- Generic types for API responses and pagination
- Union types for roles and plan types
- Interface segregation for component props
- Typed form field props

## Real-World Patterns

### State Management
- Context API for global auth state
- useState for local component state
- useCallback for memoized callbacks
- useEffect for side effects (token refresh)

### Error Handling
- Try-catch in async functions
- Form-level validation errors
- API error messages from backend
- Graceful degradation on auth failure

### Security Features
- HTTPS/Bearer token pattern
- Token refresh on 401
- Secure localStorage for tokens
- Protected routes with role checks
- Password validation (8+ chars, uppercase, number)

### Performance
- Lazy route loading with React.lazy
- UseCallback memoization for callbacks
- Suspense boundaries for async loading
- Pagination for large lists

## Testing Considerations

This fixture demonstrates:
- Component composition and reusability
- Hook patterns and custom hooks
- Type definitions for scanning tools
- Realistic import/export chains
- Cross-module dependencies
- Middleware patterns (interceptors)
- Higher-order components (ProtectedRoute)
- Context provider patterns
