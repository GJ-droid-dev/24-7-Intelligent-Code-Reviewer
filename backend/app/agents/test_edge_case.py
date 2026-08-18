# ============================================================
# Test & Edge-Case Agent — Specialist Scaffolding
# ============================================================

import logging
from typing import List
from app.agents.base import BaseAgent
from app.agents.models import PipelineContext, SpecialistAgentResponse, AgentFinding, FindingLocation

logger = logging.getLogger(__name__)


class TestEdgeCaseAgent(BaseAgent):
    """
    Evaluates test coverage, edge-case handling, boundary value validation,
    and assertion quality.
    """

    def __init__(self):
        super().__init__("test_edge_case")

    async def invoke(self, context: PipelineContext) -> SpecialistAgentResponse:
        logger.info(f"[{self.config.name}] Evaluating test & edge cases for review {context.reviewId}")
        prompt = self.load_prompt()

        findings: List[AgentFinding] = []
        code = context.code

        # Check for error handling presence
        has_error_handling = "try" in code or "except" in code or "catch" in code or "if err != nil" in code
        if not has_error_handling and len(code.splitlines()) > 10:
            findings.append(
                AgentFinding(
                    category="error_handling",
                    severity="medium",
                    title="Missing Explicit Exception / Error Boundary",
                    location=FindingLocation(snippet="Function execution body"),
                    description="Code lacks explicit error handling or recovery for potential runtime failures.",
                    impact="Unhandled exceptions may cause unexpected 500 crashes or corrupt state.",
                    suggestedFix="Wrap external I/O or critical business logic in structured error handling.",
                    confidence=0.85,
                    matchedRuleId="16",
                )
            )

        # General test coverage recommendation
        findings.append(
            AgentFinding(
                category="test_coverage",
                severity="low",
                title="Verify Edge-Case and Boundary Test Scenarios",
                location=FindingLocation(symbol="tests"),
                description="Ensure unit tests cover null/empty inputs, boundary values, and failure paths.",
                impact="Guarantees robustness when unexpected inputs are received in production.",
                suggestedFix="Add test cases verifying empty collections, negative numbers, and timeout scenarios.",
                confidence=0.8,
                matchedRuleId="17",
            )
        )

        return SpecialistAgentResponse(
            agent=self.agent_id,
            language=context.language,
            summary="Test & edge-case assessment completed.",
            findings=findings,
            strengths=[],
            limitations=[],
        )
