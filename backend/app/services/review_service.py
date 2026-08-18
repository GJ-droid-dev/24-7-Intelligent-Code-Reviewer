# ============================================================
# Review Service — Business Logic & Persistence
# ============================================================

import uuid
import logging
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from google.cloud import firestore
from fastapi import HTTPException, status

from app.models.review import (
    ReviewRequest,
    ReviewSubmitResponse,
    ReviewResponse,
    ReviewListItem,
    ReviewListResponse,
)
from app.models.finding import Finding, ScoreBreakdown
from app.services.language_detector import detect_language
from app.agents.pipeline import run_agent_pipeline
from app.dependencies import get_firestore_client

logger = logging.getLogger(__name__)


async def execute_review_pipeline_task(
    review_id: str,
    user_id: str,
    code: str,
    language: str,
    title: Optional[str] = None,
    db: Optional[firestore.Client] = None,
) -> None:
    """
    Background worker that runs the agent pipeline and persists the completed report.
    """
    if db is None:
        db = get_firestore_client()

    review_ref = db.collection("reviews").document(review_id)

    try:
        overall_score, score_breakdown, findings = await run_agent_pipeline(
            code=code,
            language=language,
            user_id=user_id,
            review_id=review_id,
            title=title,
        )

        completed_at = datetime.now(timezone.utc).isoformat()

        # 1. Update review document
        review_ref.update({
            "status": "complete",
            "overallScore": overall_score,
            "scoreBreakdown": score_breakdown.model_dump(),
            "completedAt": completed_at,
        })

        # 2. Persist findings to subcollection
        batch = db.batch()
        for finding in findings:
            finding_ref = review_ref.collection("findings").document(finding.id)
            batch.set(finding_ref, finding.model_dump())
        batch.commit()

        logger.info(f"Review {review_id} completed successfully with score {overall_score}/10")

    except Exception as e:
        logger.error(f"Review pipeline execution failed for {review_id}: {e}")
        review_ref.update({
            "status": "error",
            "errorMessage": str(e),
            "completedAt": datetime.now(timezone.utc).isoformat(),
        })


async def submit_review(
    user_id: str,
    request: ReviewRequest,
    db: Optional[firestore.Client] = None,
) -> ReviewSubmitResponse:
    """
    Handle code submission: validate, detect language, persist initial review doc,
    and trigger the agent pipeline.
    """
    if db is None:
        db = get_firestore_client()

    review_id = str(uuid.uuid4())
    language = request.language or detect_language(request.code)
    submitted_at = datetime.now(timezone.utc).isoformat()

    # Create initial review doc in Firestore
    review_doc_data = {
        "id": review_id,
        "userId": user_id,
        "title": request.title or "Untitled Review",
        "description": request.description,
        "codeSnippet": request.code,
        "language": language,
        "status": "processing",
        "overallScore": None,
        "scoreBreakdown": None,
        "submittedAt": submitted_at,
        "completedAt": None,
        "errorMessage": None,
    }

    db.collection("reviews").document(review_id).set(review_doc_data)
    logger.info(f"Created review {review_id} for user {user_id} (language: {language})")

    # In Phase 2, we execute the pipeline inline or async
    await execute_review_pipeline_task(
        review_id=review_id,
        user_id=user_id,
        code=request.code,
        language=language,
        title=request.title,
        db=db,
    )

    return ReviewSubmitResponse(
        reviewId=review_id,
        status="complete",
        language=language,
        submittedAt=submitted_at,
    )


def to_iso_string(val: Any) -> str:
    """Helper to convert datetime, DatetimeWithNanoseconds, or strings into ISO 8601 strings."""
    if val is None:
        return ""
    if hasattr(val, "isoformat"):
        return val.isoformat()
    return str(val)


def get_review_by_id(
    review_id: str,
    user_id: str,
    db: Optional[firestore.Client] = None,
) -> ReviewResponse:
    """
    Fetch a single review report with its findings and score breakdown.
    Enforces per-user ownership access control.
    """
    if db is None:
        db = get_firestore_client()

    doc_ref = db.collection("reviews").document(review_id)
    snapshot = doc_ref.get()

    if not snapshot.exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Review '{review_id}' not found",
        )

    data = snapshot.to_dict() or {}

    # Enforce authorization / data isolation
    if data.get("userId") != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to view this review",
        )

    # Fetch findings from subcollection
    findings_docs = doc_ref.collection("findings").stream()
    findings: List[Finding] = []
    for f_doc in findings_docs:
        f_data = f_doc.to_dict()
        try:
            findings.append(Finding(**f_data))
        except Exception as e:
            logger.warning(f"Error parsing finding {f_doc.id}: {e}")

    # Sort findings by severity: critical -> high -> medium -> low
    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    findings.sort(key=lambda f: severity_order.get(f.severity, 4))

    score_breakdown = None
    if data.get("scoreBreakdown"):
        score_breakdown = ScoreBreakdown(**data["scoreBreakdown"])

    return ReviewResponse(
        reviewId=review_id,
        userId=data.get("userId", user_id),
        title=data.get("title"),
        description=data.get("description"),
        codeSnippet=data.get("codeSnippet", ""),
        language=data.get("language", "unknown"),
        status=data.get("status", "processing"),
        overallScore=data.get("overallScore"),
        scoreBreakdown=score_breakdown,
        findings=findings,
        submittedAt=to_iso_string(data.get("submittedAt")),
        completedAt=to_iso_string(data.get("completedAt")) if data.get("completedAt") else None,
        errorMessage=data.get("errorMessage"),
    )


def list_user_reviews(
    user_id: str,
    page: int = 1,
    page_size: int = 10,
    db: Optional[firestore.Client] = None,
) -> ReviewListResponse:
    """
    Fetch paginated list of reviews submitted by the authenticated user.
    """
    if db is None:
        db = get_firestore_client()

    query = (
        db.collection("reviews")
        .where("userId", "==", user_id)
        .order_by("submittedAt", direction=firestore.Query.DESCENDING)
    )

    offset = (page - 1) * page_size
    docs = list(query.offset(offset).limit(page_size + 1).stream())

    has_more = len(docs) > page_size
    items_to_return = docs[:page_size]

    review_items: List[ReviewListItem] = []
    for doc in items_to_return:
        d = doc.to_dict()
        review_items.append(
            ReviewListItem(
                reviewId=doc.id,
                userId=d.get("userId", user_id),
                title=d.get("title"),
                language=d.get("language", "unknown"),
                status=d.get("status", "processing"),
                overallScore=d.get("overallScore"),
                submittedAt=to_iso_string(d.get("submittedAt")),
            )
        )

    # Estimate total count from items or count query if available
    total = offset + len(items_to_return) + (1 if has_more else 0)

    return ReviewListResponse(
        reviews=review_items,
        total=total,
        page=page,
        pageSize=page_size,
        hasMore=has_more,
    )
