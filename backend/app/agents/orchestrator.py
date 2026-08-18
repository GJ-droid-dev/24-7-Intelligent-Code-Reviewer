# ============================================================
# Orchestrator Agent — Parallel Fan-Out Coordinator
# ============================================================

import asyncio
import logging
from typing import List, Tuple, Optional
from app.agents.base import BaseAgent
from app.agents.models import PipelineContext, SpecialistAgentResponse
from app.agents.code_quality import CodeQualityAgent
from app.agents.security import SecurityAgent
from app.agents.performance import PerformanceAgent
from app.agents.test_edge_case import TestEdgeCaseAgent
from app.agents.historical_learning import HistoricalLearningAgent
from app.agents.review_agent import ReviewAgent
from app.models.finding import Finding, ScoreBreakdown

logger = logging.getLogger(__name__)


class OrchestratorAgent(BaseAgent):
    """
    Coordinates the multi-agent review pipeline:
    1. Fans out submitted code to 5 specialist agents in parallel.
    2. Collects and handles specialist results.
    3. Delegates to the Review Agent for deduplication and scoring.
    """

    def __init__(self):
        super().__init__("orchestrator")
        # Instantiate all specialist agents
        self.code_quality_agent = CodeQualityAgent()
        self.security_agent = SecurityAgent()
        self.performance_agent = PerformanceAgent()
        self.test_edge_case_agent = TestEdgeCaseAgent()
        self.historical_learning_agent = HistoricalLearningAgent()
        self.review_agent = ReviewAgent()

    async def execute(self, context: PipelineContext) -> Tuple[int, ScoreBreakdown, List[Finding]]:
        """
        Execute parallel fan-out across all specialists and consolidate report.
        """
        logger.info(f"Orchestrator beginning parallel fan-out for review {context.reviewId} ({context.language})")

        # 1. Parallel Fan-Out to 5 specialists
        tasks = [
            self.code_quality_agent.invoke(context),
            self.security_agent.invoke(context),
            self.performance_agent.invoke(context),
            self.test_edge_case_agent.invoke(context),
            self.historical_learning_agent.invoke(context),
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        specialist_responses: List[SpecialistAgentResponse] = []
        for i, res in enumerate(results):
            if isinstance(res, Exception):
                logger.error(f"Specialist agent #{i} failed with exception: {res}")
            elif isinstance(res, SpecialistAgentResponse):
                specialist_responses.append(res)

        logger.info(f"Collected {len(specialist_responses)}/5 specialist agent responses.")

        # 2. Consolidate and deduplicate findings via Review Agent
        findings = self.review_agent.deduplicate_and_sort_findings(
            specialist_responses=specialist_responses,
            review_id=context.reviewId,
        )

        # 3. Compute calibrated scores via Review Agent
        overall_score, score_breakdown = self.review_agent.compute_scores(findings)

        logger.info(f"Review {context.reviewId} finalized: Score={overall_score}/10, Findings={len(findings)}")
        return overall_score, score_breakdown, findings

    async def invoke(self, context: PipelineContext) -> SpecialistAgentResponse:
        """Standard invoke placeholder required by BaseAgent."""
        return SpecialistAgentResponse(
            agent=self.agent_id,
            language=context.language,
            summary="Orchestrator pipeline coordinator",
            findings=[],
        )
