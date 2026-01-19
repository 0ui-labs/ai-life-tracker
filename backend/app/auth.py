"""Clerk authentication for FastAPI with proper JWT verification."""

import logging
import re
from typing import Annotated

import jwt  # type: ignore[import-untyped]
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import settings

logger = logging.getLogger(__name__)

security = HTTPBearer()

# Cache the JWKS client globally for performance
_jwks_client: jwt.PyJWKClient | None = None


class ClerkUser:
    """Represents an authenticated Clerk user."""

    def __init__(self, user_id: str, email: str | None = None):
        self.id = user_id
        self.email = email


def _extract_clerk_frontend_api(publishable_key: str) -> str:
    """
    Extract Clerk Frontend API URL from publishable key.

    Clerk publishable keys encode the frontend API:
    - pk_test_<base64_encoded_frontend_api>
    - pk_live_<base64_encoded_frontend_api>

    The base64 part decodes to something like: clerk.xxxxx.lcl.dev$ or xxxxx.clerk.accounts.dev$
    """
    import base64

    if not publishable_key:
        raise ValueError("Clerk publishable key is required")

    # Extract the base64 part after pk_test_ or pk_live_
    match = re.match(r"pk_(test|live)_(.+)", publishable_key)
    if not match:
        raise ValueError("Invalid Clerk publishable key format")

    encoded_part = match.group(2)

    try:
        # Add padding if necessary
        padded = encoded_part + "=" * (4 - len(encoded_part) % 4)
        decoded = base64.b64decode(padded).decode("utf-8")
        # Remove trailing $ if present
        frontend_api = decoded.rstrip("$")
        return f"https://{frontend_api}"
    except Exception as e:
        raise ValueError(f"Failed to decode Clerk publishable key: {e}") from e


def _get_jwks_client() -> jwt.PyJWKClient:
    """Get or create the cached JWKS client."""
    global _jwks_client

    if _jwks_client is not None:
        return _jwks_client

    if not settings.clerk_publishable_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Clerk publishable key not configured",
        )

    try:
        frontend_api = _extract_clerk_frontend_api(settings.clerk_publishable_key)
        jwks_uri = f"{frontend_api}/.well-known/jwks.json"

        _jwks_client = jwt.PyJWKClient(
            jwks_uri,
            cache_jwk_set=True,
            lifespan=3600,  # Cache JWKS for 1 hour
        )
        logger.info(f"Initialized JWKS client with URI: {jwks_uri}")
        return _jwks_client

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e


def _get_expected_issuer() -> str:
    """Get the expected issuer (iss) claim value for Clerk tokens."""
    if not settings.clerk_publishable_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Clerk publishable key not configured",
        )

    frontend_api = _extract_clerk_frontend_api(settings.clerk_publishable_key)
    return frontend_api


async def verify_clerk_token(token: str) -> ClerkUser:
    """
    Verify a Clerk session token using JWKS and return the user.

    Validates:
    - JWT signature using Clerk's public keys (JWKS)
    - Token expiration (exp)
    - Token not-before time (nbf)
    - Issuer (iss) matches Clerk frontend API
    """
    if not settings.clerk_secret_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Clerk secret key not configured",
        )

    # Development bypass - ONLY when explicitly enabled and using test keys
    # This should NEVER be enabled in production environments
    if (
        settings.dev_allow_unverified_tokens
        and settings.env == "development"
        and settings.clerk_secret_key.startswith("sk_test_")
    ):
        logger.warning(
            "SECURITY WARNING: Accepting unverified JWT token in development mode. "
            "This MUST NOT be enabled in production."
        )
        try:
            unverified = jwt.decode(token, options={"verify_signature": False})
            user_id = unverified.get("sub")
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token: no user ID",
                )
            return ClerkUser(user_id=user_id, email=unverified.get("email"))
        except jwt.exceptions.DecodeError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token format",
            ) from e

    # Production path: Full JWT verification with JWKS
    try:
        # Get the JWKS client (cached)
        jwks_client = _get_jwks_client()

        # Get the signing key from the JWT header's kid
        signing_key = jwks_client.get_signing_key_from_jwt(token)

        # Get expected issuer
        expected_issuer = _get_expected_issuer()

        # Decode and verify the token with all standard claims
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            issuer=expected_issuer,
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_nbf": True,
                "verify_iat": True,
                "verify_iss": True,
                "require": ["exp", "iat", "iss", "sub"],
            },
        )

        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: no user ID",
            )

        return ClerkUser(
            user_id=user_id,
            email=payload.get("email"),
        )

    except jwt.exceptions.ExpiredSignatureError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        ) from e
    except jwt.exceptions.ImmatureSignatureError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is not yet valid (nbf claim)",
        ) from e
    except jwt.exceptions.InvalidIssuerError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token issuer",
        ) from e
    except jwt.exceptions.InvalidAlgorithmError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token algorithm",
        ) from e
    except jwt.exceptions.DecodeError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format",
        ) from e
    except jwt.exceptions.PyJWKClientError as e:
        logger.error(f"JWKS client error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch signing keys",
        ) from e
    except jwt.exceptions.PyJWTError as e:
        logger.error(f"JWT verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token verification failed",
        ) from e
    except Exception as e:
        logger.error(f"Unexpected authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
        ) from e


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> ClerkUser:
    """FastAPI dependency to get the current authenticated user."""
    return await verify_clerk_token(credentials.credentials)


# Type alias for cleaner dependency injection
CurrentUser = Annotated[ClerkUser, Depends(get_current_user)]
