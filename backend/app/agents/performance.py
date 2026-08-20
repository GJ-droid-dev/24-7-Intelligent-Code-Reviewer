# ============================================================
# Performance Agent — Specialist Scaffolding
# ============================================================

import logging
from app.agents.base import BaseAgent
from app.agents.models import PipelineContext, SpecialistAgentResponse

logger = logging.getLogger(__name__)


class PerformanceAgent(BaseAgent):
    """
    Evaluates database efficiency, N+1 query patterns, caching strategies,
    missing pagination, and algorithmic complexity via Gemini LLM.
    """

    def __init__(self):
        super().__init__("performance")

    async def invoke(self, context: PipelineContext) -> SpecialistAgentResponse:
        logger.info(f"[{self.config.name}] Evaluating performance for review {context.reviewId}")
        return await super().invoke(context)
