# ============================================================
# Finding Models — Pydantic Schemas
# ============================================================

from typing import Optional, Literal
from pydantic import BaseModel, Field


class Finding(BaseModel):
    """An individual finding produced by an AI review agent."""

    id: str = Field(..., description="Unique finding ID (e.g. f-001)")
    agentSource: Literal[
        "security",
        "performance",
        "codeQuality",
        "testCoverage",
        "historical",
        "orchestrator",
        "review"
    ] = Field(..., description="Agent that produced this finding")
    category: str = Field(..., description="Category label (e.g. Blocking Issue, Optimization, Style)")
    severity: Literal["critical", "high", "medium", "low"] = Field(..., description="Severity level")
    description: str = Field(..., description="Detailed explanation of the finding")
    suggestedFix: str = Field(..., description="Concrete code or architecture fix suggestion")
    matchedRuleId: Optional[str] = Field(None, description="Referenced historical rule ID if applicable")


class ScoreBreakdown(BaseModel):
    """Dimensional score breakdown (1–10) across review categories."""

    security: int = Field(..., ge=1, le=10, description="Security score 1–10")
    performance: int = Field(..., ge=1, le=10, description="Performance score 1–10")
    codeQuality: int = Field(..., ge=1, le=10, description="Code quality / maintainability score 1–10")
    testCoverage: int = Field(..., ge=1, le=10, description="Test & edge-case score 1–10")
    historical: int = Field(..., ge=1, le=10, description="Historical rule adherence score 1–10")
