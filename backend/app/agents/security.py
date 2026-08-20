# ============================================================
# Security Agent — Specialist Scaffolding
# ============================================================

import logging
from app.agents.base import BaseAgent
from app.agents.models import PipelineContext, SpecialistAgentResponse

logger = logging.getLogger(__name__)


class SecurityAgent(BaseAgent):
    """
    Evaluates submitted code for security vulnerabilities (OWASP Top 10,
    auth/authz gaps, SQL/command injection, data exposure, and secret leakage)
    via Gemini LLM.
    """

    def __init__(self):
        super().__init__("security")

    async def invoke(self, context: PipelineContext) -> SpecialistAgentResponse:
        logger.info(f"[{self.config.name}] Evaluating security for review {context.reviewId}")
        return await super().invoke(context)
