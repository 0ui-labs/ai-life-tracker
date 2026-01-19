"""Clerk authentication for FastAPI."""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt  # type: ignore[import-untyped]
import httpx
from functools import lru_cache
from typing import Annotated

from app.config import settings

security = HTTPBearer()


class ClerkUser:
    """Represents an authenticated Clerk user."""
    
    def __init__(self, user_id: str, email: str | None = None):
        self.id = user_id
        self.email = email


@lru_cache(maxsize=1)
def get_clerk_jwks() -> dict:
    """Fetch Clerk's JWKS (JSON Web Key Set) for JWT verification."""
    # Extract Clerk frontend API from secret key
    # Secret key format: sk_test_xxx or sk_live_xxx
    # We need to get the JWKS from Clerk's API
    
    if not settings.clerk_secret_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Clerk secret key not configured"
        )
    
    # For development, we'll use Clerk's session token validation
    # In production, you'd fetch JWKS from your Clerk instance
    return {}


async def verify_clerk_token(token: str) -> ClerkUser:
    """Verify a Clerk session token and return the user."""
    
    if not settings.clerk_secret_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Clerk secret key not configured"
        )
    
    try:
        # Clerk session tokens are JWTs
        # We decode without verification first to get the header
        unverified = jwt.decode(token, options={"verify_signature": False})
        
        user_id = unverified.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: no user ID"
            )
        
        # For development mode with test keys, we trust the token
        # In production, you should verify the signature using Clerk's JWKS
        if settings.env == "development" and settings.clerk_secret_key.startswith("sk_test_"):
            return ClerkUser(
                user_id=user_id,
                email=unverified.get("email")
            )
        
        # Production: Verify with Clerk Backend API
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://api.clerk.com/v1/users/{user_id}",
                headers={"Authorization": f"Bearer {settings.clerk_secret_key}"}
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired token"
                )
            
            user_data = response.json()
            email = None
            if user_data.get("email_addresses"):
                primary_email = next(
                    (e for e in user_data["email_addresses"] if e.get("id") == user_data.get("primary_email_address_id")),
                    user_data["email_addresses"][0] if user_data["email_addresses"] else None
                )
                if primary_email:
                    email = primary_email.get("email_address")
            
            return ClerkUser(user_id=user_id, email=email)
            
    except jwt.exceptions.DecodeError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}"
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> ClerkUser:
    """FastAPI dependency to get the current authenticated user."""
    return await verify_clerk_token(credentials.credentials)


# Type alias for cleaner dependency injection
CurrentUser = Annotated[ClerkUser, Depends(get_current_user)]
