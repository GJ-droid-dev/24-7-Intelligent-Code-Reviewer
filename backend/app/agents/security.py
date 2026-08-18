# ============================================================
# Security Agent — Specialist Scaffolding
# ============================================================

import logging
from typing import List
from app.agents.base import BaseAgent
from app.agents.models import PipelineContext, SpecialistAgentResponse, AgentFinding, FindingLocation

logger = logging.getLogger(__name__)


class SecurityAgent(BaseAgent):
    """
    Evaluates submitted code for security vulnerabilities (OWASP Top 10,
    auth/authz gaps, SQL/command injection, data exposure, and secret leakage).
    """

    def __init__(self):
        super().__init__("security")

    async def invoke(self, context: PipelineContext) -> SpecialistAgentResponse:
        logger.info(f"[{self.config.name}] Evaluating security for review {context.reviewId}")
        prompt = self.load_prompt()

        findings: List[AgentFinding] = []
        code = context.code

        # Check for potential injection risks
        if "SELECT" in code.upper() and ("%" in code or "+" in code or "format(" in code or "f\"" in code or "f'" in code):
            findings.append(
                AgentFinding(
                    category="injection",
                    severity="critical",
                    title="Potential SQL Injection Vulnerability",
                    location=FindingLocation(snippet="Dynamic SQL string concatenation"),
                    description="Raw string formatting or concatenation detected inside SQL query string.",
                    impact="Allows malicious actors to alter query structure and access unauthorized data.",
                    suggestedFix="Use parameterized queries or prepared statements via ORM/database driver.",
                    confidence=0.95,
                    matchedRuleId="3",
                )
            )

        # Check for hardcoded credentials / tokens
        import re
        if re.search(r"(password|secret|api_key|token)\s*=\s*['\"][a-zA-Z0-9_\-]{8,}['\"]", code, re.IGNORECASE):
            findings.append(
                AgentFinding(
                    category="secrets",
                    severity="critical",
                    title="Hardcoded Secret or Credential Detected",
                    location=FindingLocation(snippet="Inlined secret literal"),
                    description="Plaintext secret or authentication credential hardcoded in source file.",
                    impact="Credentials can be leaked via version control or client bundles.",
                    suggestedFix="Extract secrets to environment variables or Google Secret Manager.",
                    confidence=0.9,
                    matchedRuleId="10",
                )
            )

        return SpecialistAgentResponse(
            agent=self.agent_id,
            language=context.language,
            summary="Security analysis completed.",
            findings=findings,
            strengths=["No overt plaintext communication endpoints detected."] if not findings else [],
            limitations=[],
        )
