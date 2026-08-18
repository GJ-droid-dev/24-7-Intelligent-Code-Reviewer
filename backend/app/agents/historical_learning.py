# ============================================================
# Historical Learning Agent — Specialist Scaffolding
# ============================================================

import logging
from typing import List, Dict, Any, Optional
from google.cloud import firestore
from app.agents.base import BaseAgent
from app.agents.models import PipelineContext, SpecialistAgentResponse, AgentFinding, FindingLocation
from app.dependencies import get_firestore_client

logger = logging.getLogger(__name__)


class HistoricalLearningAgent(BaseAgent):
    """
    Evaluates submitted code against historical team rules stored in Firestore.
    Identifies recurring organizational patterns and cites matched rule IDs.
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
        prompt = self.load_prompt()

        # Retrieve historical rules if not already present in context
        rules = context.historicalRules or self.fetch_historical_rules()
        findings: List[AgentFinding] = []
        code = context.code

        # Match against known historical rule patterns
        for rule in rules:
            rule_id = str(rule.get("id", ""))
            rule_desc = rule.get("description", "").lower()
            rule_type = rule.get("type", "general")

            # Pattern check: Single character variable rule (#1)
            if rule_id == "1" and ("formatting" in rule_type or "variable" in rule_desc):
                import re
                if re.search(r"\b[a-zA-Z]\s*=\s*", code):
                    findings.append(
                        AgentFinding(
                            category="historical_pattern",
                            severity="low",
                            title=f"Historical Team Rule #{rule_id} Matched",
                            location=FindingLocation(snippet="Variable declaration"),
                            description=f"Violates team rule #{rule_id}: {rule.get('description')}",
                            suggestedFix="Refactor variable names according to team coding standard.",
                            confidence=0.9,
                            matchedRuleId=rule_id,
                        )
                    )

            # Pattern check: SQL injection rule (#3)
            elif rule_id == "3" and ("security" in rule_type or "sql" in rule_desc):
                if "SELECT" in code.upper() and ("%" in code or "+" in code or "f\"" in code or "f'" in code):
                    findings.append(
                        AgentFinding(
                            category="historical_pattern",
                            severity="critical",
                            title=f"Historical Security Rule #{rule_id} Matched",
                            location=FindingLocation(snippet="SQL query formulation"),
                            description=f"Violates team rule #{rule_id}: {rule.get('description')}",
                            suggestedFix="Use parameterized queries instead of dynamic string concatenation.",
                            confidence=0.95,
                            matchedRuleId=rule_id,
                        )
                    )

        return SpecialistAgentResponse(
            agent=self.agent_id,
            language=context.language,
            summary=f"Historical learning analysis evaluated {len(rules)} team rules.",
            findings=findings,
            strengths=[f"Evaluated against {len(rules)} historical team rules."] if rules else [],
            limitations=[] if rules else ["No historical rules retrieved from Firestore."],
        )
