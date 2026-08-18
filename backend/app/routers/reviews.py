# ============================================================
# Reviews Router — Submission, Retrieval, and History
# ============================================================

from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, Query, status
from app.models.review import (
    ReviewRequest,
    ReviewSubmitResponse,
    ReviewResponse,
    ReviewListResponse,
)
from app.middleware.auth import get_current_user
from app.services.review_service import (
    submit_review,
    get_review_by_id,
    list_user_reviews,
)

router = APIRouter(prefix="/api/v1/reviews", tags=["Reviews"])


@router.post("", response_model=ReviewSubmitResponse, status_code=status.HTTP_202_ACCEPTED)
async def create_review(
    request: ReviewRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> ReviewSubmitResponse:
    """
    Submit code for multi-agent automated review.
    Enforces authentication, detects language, and triggers the agent pipeline.
    """
    user_id = current_user["uid"]
    return await submit_review(user_id=user_id, request=request)


@router.get("/{review_id}", response_model=ReviewResponse, status_code=status.HTTP_200_OK)
async def get_review(
    review_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> ReviewResponse:
    """
    Retrieve full review report and findings for a given review ID.
    Enforces data isolation (users can only access their own reviews).
    """
    user_id = current_user["uid"]
    return get_review_by_id(review_id=review_id, user_id=user_id)


@router.get("", response_model=ReviewListResponse, status_code=status.HTTP_200_OK)
async def list_reviews(
    page: int = Query(1, ge=1, description="Page number"),
    pageSize: int = Query(10, ge=1, le=50, description="Items per page"),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> ReviewListResponse:
    """
    List past code reviews submitted by the authenticated user with pagination.
    """
    user_id = current_user["uid"]
    return list_user_reviews(user_id=user_id, page=page, page_size=pageSize)
