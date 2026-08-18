# ============================================================
# Agent Pipeline — Multi-Agent Parallel Orchestration
# ============================================================

import logging
from typing import List, Tuple, Optional
from app.models.finding import Finding, ScoreBreakdown
from app.agents.models import PipelineContext
from app.agents.orchestrator import OrchestratorAgent

logger = logging.getLogger(__name__)

# Global singleton orchestrator instance
_orchestrator = OrchestratorAgent()


async def run_agent_pipeline(
    code: str,
    language: str,
    user_id: str,
    review_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    guidelines: Optional[str] = None,
) -> Tuple[int, ScoreBreakdown, List[Finding]]:
    """
    Entry point for the Multi-Agent Review Pipeline.
    Constructs the pipeline context and invokes the Orchestrator for parallel fan-out.
    """
    logger.info(f"Triggering agent pipeline for review {review_id} (user: {user_id}, lang: {language})")

    context = PipelineContext(
        reviewId=review_id,
        userId=user_id,
        code=code,
        language=language,
        title=title,
        description=description,
        guidelines=guidelines,
    )

    return await _orchestrator.execute(context)
