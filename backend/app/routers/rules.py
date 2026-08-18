# ============================================================
# Rules Router — Historical Rules Listing & CSV Upload
# ============================================================

import logging
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from app.dependencies import get_firestore_client
from app.middleware.auth import get_current_user
from app.services.csv_ingestion import parse_rules_csv, save_rules_to_firestore

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/rules", tags=["Rules"])


@router.get("", status_code=status.HTTP_200_OK)
async def list_rules(
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    List all historical review rules stored in Firestore.
    """
    db = get_firestore_client()
    rules: List[Dict[str, Any]] = []

    try:
        docs = db.collection("rules").stream()
        for doc in docs:
            rule_data = doc.to_dict()
            rules.append({
                "id": str(rule_data.get("id", doc.id)),
                "type": rule_data.get("type", "general"),
                "description": rule_data.get("description", ""),
            })
    except Exception as e:
        logger.warning(f"Error fetching rules from Firestore: {e}")

    # Fallback if Firestore collection is empty
    if not rules:
        rules = [
            {"id": "1", "type": "formatting", "description": "Avoid single-character variable names — they hurt readability"},
            {"id": "2", "type": "performance", "description": "Cache repeated database lookups inside the request loop"},
            {"id": "3", "type": "security", "description": "Never interpolate raw user input directly into SQL queries"},
            {"id": "4", "type": "security", "description": "Always verify user ownership before returning customer orders"},
            {"id": "5", "type": "testing", "description": "All new API endpoints must include negative unauthorized tests"},
            {"id": "6", "type": "performance", "description": "Enforce cursor or page limits on all list queries"},
        ]

    return {"rules": rules, "total": len(rules)}


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_rules_csv(
    file: UploadFile = File(...),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Upload a CSV file containing repository rules (id,type,description).
    Parses and saves records into Firestore.
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file must be a CSV file (.csv)",
        )

    try:
        content = await file.read()
        csv_text = content.decode("utf-8")
        rules = parse_rules_csv(csv_text)

        if not rules:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CSV contains no valid rule rows or is missing headers (id, type, description).",
            )

        count = save_rules_to_firestore(rules)
        return {
            "message": f"Successfully ingested {count} rules into Firestore.",
            "count": count,
        }
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File encoding error. Please upload a valid UTF-8 CSV.",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing CSV upload: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process CSV: {str(e)}",
        )
