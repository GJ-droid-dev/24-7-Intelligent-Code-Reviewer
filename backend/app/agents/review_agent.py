# ============================================================
# Review Agent — Final Report Consolidation & Scoring
# ============================================================

import logging
from typing import List, Tuple, Dict, Any, Optional
from app.agents.base import BaseAgent
from app.agents.models import PipelineContext, SpecialistAgentResponse, AgentFinding
from app.models.finding import Finding, ScoreBreakdown

logger = logging.getLogger(__name__)


class ReviewAgent(BaseAgent):
    """
    Consolidates specialist findings, deduplicates issues, prioritizes severity,
    calculates dimensional scores, and computes the overall score (1–10).
    """

    def __init__(self):
        super().__init__("review")

    def deduplicate_and_sort_findings(
        self,
        specialist_responses: List[SpecialistAgentResponse],
        review_id: str,
    ) -> List[Finding]:
        """
        Merge findings across all 5 specialist agents, eliminate duplicates,
        and sort by severity (critical -> high -> medium -> low).
        """
        combined_findings: List[Finding] = []
        seen_descriptions = set()
        finding_counter = 1

        for response in specialist_responses:
            for f in response.findings:
                # Deduplication key based on normalized description substring
                desc_key = f.description[:60].lower().strip()
                if desc_key in seen_descriptions:
                    continue
                seen_descriptions.add(desc_key)

                combined_findings.append(
                    Finding(
                        id=f"{review_id}-f{finding_counter:02d}",
                        agentSource=self._map_agent_source(response.agent),
                        category=f.category,
                        severity=f.severity,
                        description=f.description,
                        suggestedFix=f.suggestedFix,
                        matchedRuleId=f.matchedRuleId,
                    )
                )
                finding_counter += 1

        # Sort by severity
        severity_rank = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        combined_findings.sort(key=lambda item: severity_rank.get(item.severity, 4))
        return combined_findings

    def compute_scores(self, findings: List[Finding]) -> Tuple[int, ScoreBreakdown]:
        """
        Compute weighted dimensional scores (1–10) and overall score according to scoring model.
        """
        # Baseline score starts at 10
        security_score = 10
        perf_score = 10
        quality_score = 10
        test_score = 10
        hist_score = 10

        for f in findings:
            if f.agentSource == "security":
                if f.severity == "critical":
                    security_score -= 5
                elif f.severity == "high":
                    security_score -= 3
                elif f.severity == "medium":
                    security_score -= 2
                else:
                    security_score -= 1
            elif f.agentSource == "performance":
                if f.severity == "critical":
                    perf_score -= 5
                elif f.severity == "high":
                    perf_score -= 3
                elif f.severity == "medium":
                    perf_score -= 2
                else:
                    perf_score -= 1
            elif f.agentSource == "codeQuality":
                if f.severity == "critical":
                    quality_score -= 4
                elif f.severity == "high":
                    quality_score -= 3
                elif f.severity == "medium":
                    quality_score -= 2
                else:
                    quality_score -= 1
            elif f.agentSource == "testCoverage":
                if f.severity in ("critical", "high"):
                    test_score -= 3
                elif f.severity == "medium":
                    test_score -= 2
                else:
                    test_score -= 1
            elif f.agentSource == "historical":
                if f.severity == "critical":
                    hist_score -= 4
                elif f.severity == "high":
                    hist_score -= 3
                else:
                    hist_score -= 1

        # Clamp all scores between 1 and 10
        breakdown = ScoreBreakdown(
            security=max(1, min(10, security_score)),
            performance=max(1, min(10, perf_score)),
            codeQuality=max(1, min(10, quality_score)),
            testCoverage=max(1, min(10, test_score)),
            historical=max(1, min(10, hist_score)),
        )

        # Weighted calculation from Architecture Section 7
        overall = round(
            (breakdown.security * 0.30)
            + (breakdown.performance * 0.25)
            + (breakdown.codeQuality * 0.20)
            + (breakdown.testCoverage * 0.15)
            + (breakdown.historical * 0.10)
        )
        overall_score = max(1, min(10, overall))

        return overall_score, breakdown

    def _map_agent_source(self, agent_id: str) -> str:
        mapping = {
            "code_quality": "codeQuality",
            "security": "security",
            "performance": "performance",
            "test_edge_case": "testCoverage",
            "historical_learning": "historical",
        }
        return mapping.get(agent_id, "review")

    async def invoke(self, context: PipelineContext) -> SpecialistAgentResponse:
        """Standard invoke placeholder required by BaseAgent."""
        return SpecialistAgentResponse(
            agent=self.agent_id,
            language=context.language,
            summary="Review Agent ready to consolidate findings.",
            findings=[],
        )
