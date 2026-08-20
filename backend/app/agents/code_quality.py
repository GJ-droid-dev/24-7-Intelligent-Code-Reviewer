# ============================================================
# Code Quality Agent — Specialist Scaffolding
# ============================================================

import logging
from app.agents.base import BaseAgent
from app.agents.models import PipelineContext, SpecialistAgentResponse

logger = logging.getLogger(__name__)


class CodeQualityAgent(BaseAgent):
    """
    Evaluates code structure, maintainability, readability, naming conventions,
    and separation of concerns via Gemini LLM.
    """

    def __init__(self):
        super().__init__("code_quality")

    async def invoke(self, context: PipelineContext) -> SpecialistAgentResponse:
        logger.info(f"[{self.config.name}] Evaluating code quality for review {context.reviewId} ({context.language})")
        return await super().invoke(context)
