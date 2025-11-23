"""
Clerk Authentication for FastAPI
Validates JWT tokens from Clerk
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.orm import Session
import requests
from functools import lru_cache
import os

from backend.database import get_db, User

security = HTTPBearer()

# Get Clerk configuration from environment
CLERK_PUBLISHABLE_KEY = os.getenv("CLERK_PUBLISHABLE_KEY", "")
CLERK_SECRET_KEY = os.getenv("CLERK_SECRET_KEY", "")

# Extract domain from publishable key
# Format: pk_test_xxx or pk_live_xxx encodes the domain
def get_clerk_domain():
    """Extract Clerk domain from publishable key"""
    # For now, we'll use a default. In production, parse from the key
    return "fond-chicken-6.clerk.accounts.dev"


@lru_cache()
def get_jwks():
    """Fetch Clerk's JWKS (JSON Web Key Set) for token validation"""
    domain = get_clerk_domain()
    jwks_url = f"https://{domain}/.well-known/jwks.json"
    try:
        response = requests.get(jwks_url, timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Failed to fetch JWKS: {e}")
        return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Validate Clerk JWT token and return user from database
    Creates user if doesn't exist
    """
    token = credentials.credentials
    
    # For development: Skip validation if no Clerk keys configured
    if not CLERK_PUBLISHABLE_KEY or CLERK_PUBLISHABLE_KEY == "your_actual_key_from_clerk_dashboard":
        # Get or create dev user
        dev_user = db.query(User).filter(User.email == "dev@example.com").first()
        if not dev_user:
            dev_user = User(
                email="dev@example.com",
                username="dev_user",
                full_name="Dev User",
                hashed_password="",  # No password for Clerk users
                clerk_user_id="dev_user"
            )
            db.add(dev_user)
            db.commit()
            db.refresh(dev_user)
        return dev_user
    
    try:
        # Decode token without verification (for development)
        # In production, verify with JWKS
        payload = jwt.decode(
            token,
            options={"verify_signature": False}  # Temporary for development
        )
        
        clerk_user_id = payload.get("sub")
        if not clerk_user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user ID"
            )
        
        email = payload.get("email", "")
        username = payload.get("username", email.split("@")[0])
        full_name = payload.get("name", "")
        
        # Find or create user in database
        user = db.query(User).filter(User.clerk_user_id == clerk_user_id).first()
        if not user:
            # Create new user
            user = User(
                email=email,
                username=username,
                full_name=full_name,
                hashed_password="",  # No password for Clerk users
                clerk_user_id=clerk_user_id
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            # Update user info if changed
            if user.email != email or user.username != username:
                user.email = email
                user.username = username
                user.full_name = full_name
                db.commit()
                db.refresh(user)
        
        return user
    
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


# Optional: Dependency for endpoints that don't require auth
async def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False))
):
    """Get current user if authenticated, otherwise return None"""
    if not credentials:
        return None
    return await get_current_user(credentials)

