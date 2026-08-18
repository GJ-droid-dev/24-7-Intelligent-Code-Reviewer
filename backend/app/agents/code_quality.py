# ============================================================
# Code Quality Agent — Specialist Scaffolding
# ============================================================

import logging
from typing import List
from app.agents.base import BaseAgent
from app.agents.models import PipelineContext, SpecialistAgentResponse, AgentFinding, FindingLocation

logger = logging.getLogger(__name__)


class CodeQualityAgent(BaseAgent):
    """
    Evaluates code structure, maintainability, readability, naming conventions,
    and separation of concerns.
    """

    def __init__(self):
        super().__init__("code_quality")

    async def invoke(self, context: PipelineContext) -> SpecialistAgentResponse:
        logger.info(f"[{self.config.name}] Evaluating code quality for review {context.reviewId} ({context.language})")
        prompt = self.load_prompt()

        findings: List[AgentFinding] = []

        # Baseline scaffolding heuristic inspection
        code = context.code

        # Check naming conventions / single-character variables
        import re
        bad_vars = re.findall(r"\b([a-zA-Z])\s*=\s*", code)
        single_char_vars = [v for v in bad_vars if v not in ("i", "j", "k", "e", "f", "_")]
        if single_char_vars:
            findings.append(
                AgentFinding(
                    category="naming",
                    severity="low",
                    title="Non-descriptive variable names detected",
                    location=FindingLocation(snippet=f"Variables: {', '.join(set(single_char_vars))}"),
                    description="Single-character variable names harm readability and maintainability.",
                    impact="Makes domain logic and variable lifecycle difficult to trace.",
                    suggestedFix="Rename variables to communicate domain meaning and intent.",
                    confidence=0.9,
                    matchedRuleId="1",
                )
            )

        # General maintainability finding
        findings.append(
            AgentFinding(
                category="maintainability",
                severity="medium",
                title="Ensure comprehensive interface contracts and type annotations",
                location=FindingLocation(symbol="root"),
                description=f"Standard {context.language.capitalize()} conventions: exported functions and modules should have clear documentation and type safety.",
                impact="Improves developer ergonomics and reduces runtime interface mismatches.",
                suggestedFix="Add explicit return types and docstrings to all exported functions.",
                confidence=0.85,
            )
        )

        return SpecialistAgentResponse(
            agent=self.agent_id,
            language=context.language,
            summary=f"Code quality assessment completed for {context.language} snippet.",
            findings=findings,
            strengths=[f"Idiomatic syntax structure for {context.language}."],
            limitations=[],
        )
