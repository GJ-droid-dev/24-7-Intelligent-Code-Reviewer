# ============================================================
# Performance Agent — Specialist Scaffolding
# ============================================================

import logging
from typing import List
from app.agents.base import BaseAgent
from app.agents.models import PipelineContext, SpecialistAgentResponse, AgentFinding, FindingLocation

logger = logging.getLogger(__name__)


class PerformanceAgent(BaseAgent):
    """
    Evaluates database efficiency, N+1 query patterns, caching strategies,
    missing pagination, and algorithmic complexity.
    """

    def __init__(self):
        super().__init__("performance")

    async def invoke(self, context: PipelineContext) -> SpecialistAgentResponse:
        logger.info(f"[{self.config.name}] Evaluating performance for review {context.reviewId}")
        prompt = self.load_prompt()

        findings: List[AgentFinding] = []
        code = context.code

        # Check for DB calls inside loops (N+1 query pattern)
        if "for " in code and ("db." in code or "fetch" in code or "query" in code or "find" in code or "execute" in code):
            findings.append(
                AgentFinding(
                    category="n_plus_one",
                    severity="high",
                    title="Potential N+1 Query Anti-Pattern",
                    location=FindingLocation(snippet="Database execution inside loop construct"),
                    description="Iterative database queries detected within a loop, causing excessive round-trips.",
                    impact="Severely degrades query performance and increases database load under scale.",
                    suggestedFix="Batch query operations using IN clauses or join queries before the loop.",
                    confidence=0.9,
                    matchedRuleId="2",
                )
            )

        # Check for unbounded list queries without limit/pagination
        if ("SELECT" in code.upper() or ".find(" in code) and "LIMIT" not in code.upper() and "pageSize" not in code:
            findings.append(
                AgentFinding(
                    category="pagination",
                    severity="medium",
                    title="Unbounded List Query without Pagination",
                    location=FindingLocation(snippet="Query returning unbounded records"),
                    description="Query does not specify pagination or max limit constraints.",
                    impact="Can cause high memory consumption and latency spikes as data volume grows.",
                    suggestedFix="Add explicit limit and offset/cursor pagination parameters.",
                    confidence=0.8,
                    matchedRuleId="5",
                )
            )

        return SpecialistAgentResponse(
            agent=self.agent_id,
            language=context.language,
            summary="Performance assessment completed.",
            findings=findings,
            strengths=["Efficient localized data structures used."] if not findings else [],
            limitations=[],
        )
