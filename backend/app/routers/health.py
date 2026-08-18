# ============================================================
# Health Router — Health & Connectivity Check
# ============================================================

import logging
from typing import Dict, Any
from fastapi import APIRouter, status
from app.config import settings
from app.dependencies import get_firestore_client

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["Health"])


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint verifying application status and Firestore connectivity.
    """
    firestore_status = "healthy"
    try:
        db = get_firestore_client()
        # Perform lightweight check (list 1 document from rules)
        list(db.collection("rules").limit(1).stream())
    except Exception as e:
        logger.warning(f"Firestore health check ping warning: {e}")
        firestore_status = f"degraded: {str(e)}"

    return {
        "status": "healthy" if "degraded" not in firestore_status else "degraded",
        "version": "1.0.0",
        "service": "multi-agent-code-reviewer-api",
        "environment": settings.environment,
        "gcp_project": settings.gcp_project_id,
        "firestore": firestore_status,
    }
