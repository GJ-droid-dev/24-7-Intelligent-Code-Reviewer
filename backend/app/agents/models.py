# ============================================================
# Agent Models & Structured Output Contracts
# ============================================================

from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field
from app.models.finding import Finding, ScoreBreakdown


class FindingLocation(BaseModel):
    """Location information for an individual finding."""

    file: Optional[str] = Field(None, description="Path to file")
    startLine: Optional[int] = Field(None, description="Starting line number")
    endLine: Optional[int] = Field(None, description="Ending line number")
    symbol: Optional[str] = Field(None, description="Function, method, class, or symbol name")
    snippet: Optional[str] = Field(None, description="Relevant code snippet excerpt")


class AgentFinding(BaseModel):
    """Structured finding emitted by a specialist agent."""

    category: str = Field(..., description="Finding category")
    severity: Literal["critical", "high", "medium", "low"] = Field(..., description="Severity level")
    title: Optional[str] = Field(None, description="Short summary title")
    location: Optional[FindingLocation] = Field(None, description="Code location reference")
    description: str = Field(..., description="Evidence-based explanation")
    impact: Optional[str] = Field(None, description="Impact explanation")
    suggestedFix: str = Field(..., description="Actionable remediation")
    confidence: Optional[float] = Field(1.0, ge=0.0, le=1.0, description="Confidence score 0.0–1.0")
    matchedRuleId: Optional[str] = Field(None, description="Matched historical rule ID if applicable")


class SpecialistAgentResponse(BaseModel):
    """Standard response contract from a specialist agent."""

    agent: str = Field(..., description="Name of the reporting agent")
    language: Optional[str] = Field(None, description="Detected or analyzed language")
    summary: Optional[str] = Field(None, description="Brief summary of assessment")
    findings: List[AgentFinding] = Field(default_factory=list, description="List of findings")
    strengths: List[str] = Field(default_factory=list, description="Positive observations")
    limitations: List[str] = Field(default_factory=list, description="Analysis limitations or missing context")


class PipelineContext(BaseModel):
    """Context payload passed across the agent pipeline."""

    reviewId: str
    userId: str
    code: str
    language: str
    title: Optional[str] = None
    description: Optional[str] = None
    guidelines: Optional[str] = None
    historicalRules: List[Dict[str, Any]] = Field(default_factory=list)
