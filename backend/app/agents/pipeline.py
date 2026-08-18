# ============================================================
# Agent Pipeline — Multi-Agent Orchestration (Phase 2 Stub)
# ============================================================

import logging
from typing import List, Tuple, Optional
from app.models.finding import Finding, ScoreBreakdown

logger = logging.getLogger(__name__)


async def run_agent_pipeline(
    code: str,
    language: str,
    user_id: str,
    review_id: str,
    title: Optional[str] = None,
) -> Tuple[int, ScoreBreakdown, List[Finding]]:
    """
    Orchestrates the 7 AI agents in the review pipeline.
    In Phase 2, this provides realistic baseline findings and scores.
    In Phase 3, this is replaced by the ADK v1.0 parallel fan-out orchestrator.
    """
    logger.info(f"Running agent pipeline for review {review_id} (language: {language}, user: {user_id})")

    # Generate baseline findings based on simple code heuristics
    findings: List[Finding] = []

    # 1. Security Check heuristic
    if "SELECT" in code.upper() and ("%" in code or "+" in code or "format(" in code or "f\"" in code):
        findings.append(
            Finding(
                id=f"{review_id}-f01",
                agentSource="security",
                category="Security Vulnerability",
                severity="critical",
                description="Possible SQL injection risk: raw string formatting detected in database query.",
                suggestedFix="Use parameterized queries or an ORM with prepared statements.",
                matchedRuleId="3",
            )
        )

    # 2. Performance Check heuristic
    if "for " in code and ("db." in code or "fetch" in code or "query" in code or "find" in code):
        findings.append(
            Finding(
                id=f"{review_id}-f02",
                agentSource="performance",
                category="Performance & Scalability",
                severity="high",
                description="Potential N+1 query pattern: database access detected inside a loop.",
                suggestedFix="Batch query operations or retrieve required relations with JOIN/IN clauses.",
                matchedRuleId="2",
            )
        )

    # 3. Code Quality Check
    findings.append(
        Finding(
            id=f"{review_id}-f03",
            agentSource="codeQuality",
            category="Maintainability",
            severity="medium",
            description=f"Standard {language.capitalize()} conventions: ensure comprehensive docstrings and explicit type hints.",
            suggestedFix="Add function docstrings and type annotations to all exported interfaces.",
            matchedRuleId="1",
        )
    )

    # 4. Test & Edge Case Check
    findings.append(
        Finding(
            id=f"{review_id}-f04",
            agentSource="testCoverage",
            category="Test Coverage",
            severity="low",
            description="Verify boundary conditions, null values, and exception handling paths in unit test suite.",
            suggestedFix="Add test cases covering error states and unexpected input payloads.",
            matchedRuleId="16",
        )
    )

    # Compute score breakdown
    security_score = 4 if any(f.severity == "critical" for f in findings) else 9
    performance_score = 6 if any(f.severity == "high" for f in findings) else 8
    quality_score = 8
    testing_score = 7
    historical_score = 8

    score_breakdown = ScoreBreakdown(
        security=security_score,
        performance=performance_score,
        codeQuality=quality_score,
        testCoverage=testing_score,
        historical=historical_score,
    )

    overall_score = round(
        (security_score * 0.3)
        + (performance_score * 0.25)
        + (quality_score * 0.2)
        + (testing_score * 0.15)
        + (historical_score * 0.1)
    )

    overall_score = max(1, min(10, overall_score))

    return overall_score, score_breakdown, findings
