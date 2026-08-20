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
        Merge findings across all specialist agents, eliminate duplicates,
        resolve severity conflicts, and sort by severity (critical -> high -> medium -> low).
        """
        severity_rank = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        combined_findings: List[Finding] = []

        def is_duplicate(f1: Finding, f2: AgentFinding) -> bool:
            # 1. Match by explicit historical/security rule ID
            if f1.matchedRuleId and f2.matchedRuleId and f1.matchedRuleId == f2.matchedRuleId:
                return True

            d1 = f1.description.lower().strip()
            d2 = f2.description.lower().strip()

            # 2. Exact or substring containment match
            if d1 == d2 or d1 in d2 or d2 in d1:
                return True

            # 3. Token overlap similarity
            words1 = set(d1.split())
            words2 = set(d2.split())
            if words1 and words2:
                overlap = len(words1 & words2) / min(len(words1), len(words2))
                if overlap >= 0.7:
                    return True

            return False

        for response in specialist_responses:
            for f in response.findings:
                # Check for existing duplicate finding
                duplicate_found = False
                for existing in combined_findings:
                    if is_duplicate(existing, f):
                        duplicate_found = True
                        # Conflict resolution: preserve higher severity
                        if severity_rank.get(f.severity, 4) < severity_rank.get(existing.severity, 4):
                            existing.severity = f.severity
                        if not existing.matchedRuleId and f.matchedRuleId:
                            existing.matchedRuleId = f.matchedRuleId
                        break

                if not duplicate_found:
                    combined_findings.append(
                        Finding(
                            id=f"{review_id}-f{len(combined_findings) + 1:02d}",
                            agentSource=self._map_agent_source(response.agent),
                            category=f.category,
                            severity=f.severity,
                            title=f.title or (f.description[:60] + "..." if len(f.description) > 60 else f.description),
                            description=f.description,
                            suggestedFix=f.suggestedFix,
                            matchedRuleId=f.matchedRuleId,
                        )
                    )

        # Sort by severity
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
