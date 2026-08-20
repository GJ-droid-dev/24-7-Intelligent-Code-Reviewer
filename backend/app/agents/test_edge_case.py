# ============================================================
# Test & Edge-Case Agent — Specialist Scaffolding
# ============================================================

import logging
from app.agents.base import BaseAgent
from app.agents.models import PipelineContext, SpecialistAgentResponse

logger = logging.getLogger(__name__)


class TestEdgeCaseAgent(BaseAgent):
    """
    Evaluates test coverage, edge-case handling, boundary value validation,
    and assertion quality via Gemini LLM.
    """

    __test__ = False

    def __init__(self):
        super().__init__("test_edge_case")

    async def invoke(self, context: PipelineContext) -> SpecialistAgentResponse:
        logger.info(f"[{self.config.name}] Evaluating test & edge cases for review {context.reviewId}")
        return await super().invoke(context)
