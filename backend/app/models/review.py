# ============================================================
# Review Models — Pydantic Schemas
# ============================================================

from datetime import datetime, timezone
from typing import List, Optional, Literal
from pydantic import BaseModel, Field, field_validator
from app.models.finding import Finding, ScoreBreakdown


class ReviewRequest(BaseModel):
    """Payload for submitting code for review."""

    code: str = Field(..., min_length=1, max_length=500_000, description="Source code snippet or PR diff to review")
    title: Optional[str] = Field(None, max_length=200, description="Optional title or PR title")
    description: Optional[str] = Field(None, max_length=2000, description="Optional description or PR summary")
    language: Optional[str] = Field(None, max_length=50, description="Optional override for programming language")

    @field_validator("code")
    @classmethod
    def validate_code_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Code submission cannot be empty or whitespace only.")
        return v


class ReviewSubmitResponse(BaseModel):
    """Immediate response (202 Accepted) returned when review is queued."""

    reviewId: str = Field(..., description="Unique review ID")
    status: Literal["processing", "complete", "error"] = Field("processing", description="Review status")
    language: str = Field(..., description="Detected or specified programming language")
    submittedAt: str = Field(..., description="ISO 8601 submission timestamp")


class ReviewResponse(BaseModel):
    """Full review report returned on GET /api/v1/reviews/{id}."""

    reviewId: str = Field(..., description="Unique review ID")
    userId: str = Field(..., description="Owner user UID")
    title: Optional[str] = Field(None, description="Review title")
    description: Optional[str] = Field(None, description="Review description")
    codeSnippet: str = Field(..., description="Code analyzed")
    language: str = Field(..., description="Programming language")
    status: Literal["processing", "complete", "error"] = Field(..., description="Current status")
    overallScore: Optional[int] = Field(None, ge=1, le=10, description="Overall weighted score 1–10")
    scoreBreakdown: Optional[ScoreBreakdown] = Field(None, description="Dimension score breakdown")
    findings: List[Finding] = Field(default_factory=list, description="List of findings sorted by severity")
    submittedAt: str = Field(..., description="ISO 8601 submission timestamp")
    completedAt: Optional[str] = Field(None, description="ISO 8601 completion timestamp")
    errorMessage: Optional[str] = Field(None, description="Error details if review failed")


class ReviewListItem(BaseModel):
    """Summary item for review history list."""

    reviewId: str
    userId: str
    title: Optional[str] = None
    language: str
    status: Literal["processing", "complete", "error"]
    overallScore: Optional[int] = None
    submittedAt: str


class ReviewListResponse(BaseModel):
    """Paginated list of user reviews."""

    reviews: List[ReviewListItem]
    total: int
    page: int
    pageSize: int
    hasMore: bool
