# Clerk Authentication Integration

This document explains how Clerk authentication is integrated into the xunlong application.

## Overview

The application now uses Clerk for authentication instead of the custom JWT-based auth system. This provides:
- Social OAuth (Google, GitHub, Microsoft, etc.)
- Secure session management
- User management dashboard
- Multi-factor authentication support

## Frontend Changes

### 1. Clerk Provider Setup (`frontend/src/main.jsx`)

The app is wrapped with `ClerkProvider` with a custom dark theme:

```jsx
<ClerkProvider 
  publishableKey={import.meta.env.VITE_CLERK_PUBLISHABLE_KEY}
  appearance={{
    baseTheme: 'dark',
    variables: {
      colorPrimary: '#8b5cf6',
      colorBackground: '#0a0a0b',
      // ... more theme variables
    }
  }}
>
  <App />
</ClerkProvider>
```

### 2. Authentication Pages

- **SignInPage** (`frontend/src/pages/SignInPage.jsx`): Hosts Clerk's `<SignIn />` component
- **SignUpPage** (`frontend/src/pages/SignUpPage.jsx`): Hosts Clerk's `<SignUp />` component

Both use `routing="virtual"` to prevent redirect loops with React Router.

### 3. Protected Routes (`frontend/src/App.jsx`)

Protected routes use Clerk's `<SignedIn>` and `<SignedOut>` components:

```jsx
function ProtectedRoute({ children }) {
  const { isLoaded } = useAuth()
  
  if (!isLoaded) {
    return <div>Loading...</div>
  }
  
  return (
    <>
      <SignedIn>{children}</SignedIn>
      <SignedOut><RedirectToSignIn /></SignedOut>
    </>
  )
}
```

### 4. API Token Management

**ClerkTokenProvider** (`frontend/src/components/ClerkTokenProvider.jsx`):
- Automatically fetches Clerk session tokens
- Updates tokens every 50 minutes (tokens expire after 60 minutes)
- Injects tokens into API requests

**API Client** (`frontend/src/lib/api.js`):
- Updated to use Clerk tokens instead of custom JWT
- Removed dependency on `useAuthStore`
- Redirects to `/sign-in` on 401 errors

## Backend Changes

### 1. Clerk Authentication Middleware (`backend/clerk_auth.py`)

New authentication dependency that:
- Validates Clerk JWT tokens
- Decodes user information from token
- Creates/updates users in the database automatically
- Returns User objects for existing backend code compatibility

**Key function:**
```python
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    # Validates Clerk token
    # Creates/updates user in database
    # Returns User object
```

### 2. Database Schema Updates

**User Model** (`backend/database.py`):
- Added `clerk_user_id` field (unique, indexed)
- Made `hashed_password` nullable (Clerk users don't need passwords)

### 3. API Endpoints Updated

All API endpoints now use `get_current_user` instead of `get_current_active_user`:

- `backend/api/projects.py`
- `backend/api/analytics.py`
- `backend/api/documents.py`

## Environment Variables

### Frontend (`.env`)

```bash
VITE_CLERK_PUBLISHABLE_KEY=pk_test_...
```

### Backend (`.env`)

```bash
CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...
```

## How It Works

1. **User Signs In:**
   - User visits `/sign-in`
   - Clerk handles authentication (email/password or OAuth)
   - Clerk creates a session and issues a JWT token

2. **Frontend Makes API Request:**
   - `ClerkTokenProvider` fetches the current session token
   - Token is injected into API request headers via axios interceptor
   - Format: `Authorization: Bearer <clerk_jwt_token>`

3. **Backend Validates Request:**
   - `get_current_user` dependency extracts the token
   - Token is decoded (signature verification disabled for development)
   - User info (ID, email, username) extracted from token
   - User is looked up in database by `clerk_user_id`
   - If user doesn't exist, a new user is created
   - User object is returned to the endpoint

4. **Endpoint Processes Request:**
   - Endpoint receives authenticated `User` object
   - Continues with normal business logic
   - Returns response to frontend

## Security Notes

### Development Mode

⚠️ **WARNING:** Token signature verification is currently disabled for development.

In `backend/clerk_auth.py`:
```python
payload = jwt.decode(
    token,
    options={"verify_signature": False}  # Temporary for development
)
```

### Production Mode

For production, you should:

1. **Enable Token Verification:**
   - Fetch Clerk's JWKS (JSON Web Key Set)
   - Verify token signatures using the JWKS
   - See `get_jwks()` function in `clerk_auth.py`

2. **Use HTTPS:**
   - All API requests must use HTTPS
   - Clerk sessions require secure cookies

3. **Set Proper CORS:**
   - Configure allowed origins in FastAPI
   - Match your production domain

## Troubleshooting

### "401 Unauthorized" Errors

1. Check that `VITE_CLERK_PUBLISHABLE_KEY` is set in frontend `.env`
2. Verify the key starts with `pk_test_` or `pk_live_`
3. Restart the frontend dev server after changing `.env`
4. Check browser console for Clerk errors
5. Verify backend database is initialized (`python backend/init_db.py`)

### Redirect Loop Between `/sign-in` and `/dashboard`

- Ensure `routing="virtual"` is set on Clerk components
- Check that `isLoaded` is checked before rendering protected content
- Clear browser cookies and refresh

### Backend Not Accepting Tokens

1. Verify backend is running on port 8000
2. Check backend logs for errors
3. Ensure database has `clerk_user_id` column (run `init_db.py`)
4. Check that all API endpoints use `get_current_user`

## Testing

### Test Sign Up Flow

1. Go to http://localhost:3000
2. Click "Get Started" or "Sign In"
3. Click "Sign up" on Clerk form
4. Enter email and password
5. Verify email (if email verification is enabled)
6. Should redirect to `/dashboard`

### Test Dashboard API Calls

1. Sign in successfully
2. Open browser DevTools > Network tab
3. Navigate to Dashboard
4. Check API requests to `/api/analytics/dashboard` and `/api/projects`
5. Should return 200 OK with data (not 401 Unauthorized)

### Test Social OAuth

1. Enable OAuth providers in Clerk Dashboard:
   - Go to https://dashboard.clerk.dev
   - Click on your application
   - Go to "User & Authentication" > "Social Connections"
   - Enable Google, GitHub, etc.
2. Go to sign-in page
3. Click on social provider button
4. Complete OAuth flow
5. Should redirect to dashboard

## Migration from Custom Auth

### What Changed

- ❌ **Removed:** `useAuthStore` - No longer needed
- ❌ **Removed:** `LoginPage.jsx` / `RegisterPage.jsx` - Replaced by Clerk components
- ❌ **Removed:** `backend/api/auth.py` usage in other APIs
- ✅ **Added:** Clerk authentication throughout
- ✅ **Added:** `clerk_user_id` to User model
- ✅ **Added:** Automatic user creation on first sign-in

### Data Migration

No data migration is required because:
- New users are created with Clerk IDs when they first sign in
- Old users can be migrated by adding their Clerk ID when they sign in with Clerk

If you need to migrate existing users:
1. User signs in with Clerk
2. Backend checks if user exists by email
3. If exists, update their `clerk_user_id`
4. If not, create new user with Clerk ID

## Resources

- [Clerk Documentation](https://clerk.com/docs)
- [Clerk React SDK](https://clerk.com/docs/references/react/overview)
- [Clerk Backend API](https://clerk.com/docs/references/backend/overview)

