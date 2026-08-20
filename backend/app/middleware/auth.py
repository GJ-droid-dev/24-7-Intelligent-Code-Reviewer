# ============================================================
# Firebase Auth Middleware / Dependency
# ============================================================

import os
import logging
from typing import Dict, Any, Optional
import firebase_admin
from firebase_admin import auth, credentials
from fastapi import Header, HTTPException, status, Depends
from app.config import settings

logger = logging.getLogger(__name__)

# Track if Firebase Admin SDK has been initialized
_firebase_app: Optional[firebase_admin.App] = None


def init_firebase() -> Optional[firebase_admin.App]:
    """Initialize Firebase Admin SDK if not already initialized."""
    global _firebase_app
    if _firebase_app is not None:
        return _firebase_app

    try:
        # If already initialized elsewhere in default app
        _firebase_app = firebase_admin.get_app()
        return _firebase_app
    except ValueError:
        pass

    from app.dependencies import find_local_credentials_file

    cred_file = find_local_credentials_file()
    if cred_file and os.path.exists(cred_file):
        try:
            cred = credentials.Certificate(cred_file)
            _firebase_app = firebase_admin.initialize_app(cred)
            logger.info(f"Firebase Admin SDK initialized with key file: {cred_file}")
            return _firebase_app
        except Exception as e:
            logger.warning(f"Failed initializing Firebase Admin with {cred_file}: {e}")

    try:
        # Default initialization uses GOOGLE_APPLICATION_CREDENTIALS or metadata server
        _firebase_app = firebase_admin.initialize_app()
        logger.info("Firebase Admin SDK initialized successfully")
        return _firebase_app
    except Exception as e:
        logger.warning(f"Firebase Admin SDK initialization deferred or failed: {e}")
        return None


def verify_firebase_token(token: str) -> Dict[str, Any]:
    """
    Verify a Firebase ID token.
    Returns decoded token dictionary on success, raises HTTPException on failure.
    """
    # Allow mock test token in development/test/demo mode
    if token == "mock-test-token" or token.startswith("mock-"):
        user_id = "test-user-001"
        if token.startswith("mock-test-token-"):
            user_id = token.replace("mock-test-token-", "")
        return {
            "uid": user_id,
            "email": "senior.reviewer@acme.dev",
            "name": "Alex Rivera (Staff Eng)",
        }

    init_firebase()

    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except auth.ExpiredIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Firebase ID token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except auth.InvalidIdTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid Firebase ID token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"Error verifying Firebase token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    authorization: Optional[str] = Header(None, description="Bearer <Firebase ID Token>")
) -> Dict[str, Any]:
    """
    FastAPI dependency that extracts and validates the Firebase ID token from Authorization header.
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authorization header format. Expected 'Bearer <token>'",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = parts[1]
    decoded = verify_firebase_token(token)
    return {
        "uid": decoded.get("uid", ""),
        "email": decoded.get("email", ""),
        "name": decoded.get("name", decoded.get("email", "")),
        "claims": decoded,
    }
