# ============================================================
# Historical Learning Agent — Specialist Scaffolding
# ============================================================

import logging
from typing import List, Dict, Any, Optional
from google.cloud import firestore
from app.agents.base import BaseAgent
from app.agents.models import PipelineContext, SpecialistAgentResponse
from app.dependencies import get_firestore_client

logger = logging.getLogger(__name__)


class HistoricalLearningAgent(BaseAgent):
    """
    Evaluates submitted code against historical team rules stored in Firestore
    via Gemini LLM. Identifies recurring organizational patterns and cites matched rule IDs.
    """

    def __init__(self):
        super().__init__("historical_learning")

    def fetch_historical_rules(self, db: Optional[firestore.Client] = None) -> List[Dict[str, Any]]:
        """Fetch all historical team rules from Firestore 'rules' collection."""
        try:
            if db is None:
                db = get_firestore_client()
            docs = db.collection("rules").stream()
            rules = []
            for doc in docs:
                data = doc.to_dict()
                data["id"] = doc.id
                rules.append(data)
            return rules
        except Exception as e:
            logger.warning(f"Failed to query Firestore rules for historical learning: {e}")
            return []

    async def invoke(self, context: PipelineContext) -> SpecialistAgentResponse:
        logger.info(f"[{self.config.name}] Matching historical rules for review {context.reviewId}")

        # Retrieve historical rules if not already present in context
        if context.historicalRules is None:
            context.historicalRules = self.fetch_historical_rules()

        if len(context.historicalRules) == 0:
            return SpecialistAgentResponse(
                agent=self.agent_id,
                language=context.language,
                summary="No historical team rules available for evaluation.",
                findings=[],
                strengths=[],
                limitations=["No historical rules found in Firestore."],
            )

        return await super().invoke(context)
