# ============================================================
# Edge Cases Validation Test Suite (docs/edgecases.md)
# ============================================================

import pytest
import unittest.mock as mock
from fastapi.testclient import TestClient
from app.main import app
from app.models.review import ReviewRequest
from app.models.finding import Finding
from app.agents.models import PipelineContext, SpecialistAgentResponse, AgentFinding
from app.agents.base import BaseAgent
from app.agents.orchestrator import OrchestratorAgent
from app.agents.review_agent import ReviewAgent
from app.agents.historical_learning import HistoricalLearningAgent
from app.services.language_detector import detect_language
from app.services.csv_ingestion import parse_rules_csv, save_rules_to_firestore
from app.services.review_service import get_review_by_id, submit_review
from fastapi import HTTPException

client = TestClient(app)
AUTH_HEADER_USER_A = {"Authorization": "Bearer mock-test-token-user-a"}
AUTH_HEADER_USER_B = {"Authorization": "Bearer mock-test-token-user-b"}


# ============================================================
# 1. Submission Inputs Edge Cases
# ============================================================

def test_submission_empty_code_rejected():
    """Empty or whitespace-only code must be rejected early with 422."""
    res1 = client.post("/api/v1/reviews", json={"code": ""}, headers=AUTH_HEADER_USER_A)
    assert res1.status_code == 422

    res2 = client.post("/api/v1/reviews", json={"code": "   \n\t  \n  "}, headers=AUTH_HEADER_USER_A)
    assert res2.status_code == 422

    res3 = client.post("/api/v1/reviews", json={"title": "No Code Provided"}, headers=AUTH_HEADER_USER_A)
    assert res3.status_code == 422


def test_submission_oversized_payload_rejected():
    """Submissions exceeding 500,000 characters must be rejected with 422."""
    huge_code = "x = 1\n" * 100_001  # > 600,000 characters
    res = client.post("/api/v1/reviews", json={"code": huge_code}, headers=AUTH_HEADER_USER_A)
    assert res.status_code == 422


def test_submission_language_override():
    """User-specified language override should take precedence over auto-detection."""
    payload = {
        "code": "def hello(): print('world')",
        "language": "ruby",
    }
    res = client.post("/api/v1/reviews", json=payload, headers=AUTH_HEADER_USER_A)
    assert res.status_code == 202
    assert res.json()["language"] == "ruby"


# ============================================================
# 2. Authentication & Data Isolation Edge Cases
# ============================================================

def test_auth_missing_or_malformed_tokens():
    """Requests with missing, malformed, or invalid tokens fail closed with 401."""
    # Missing
    res = client.get("/api/v1/reviews")
    assert res.status_code == 401

    # Malformed prefix
    res = client.get("/api/v1/reviews", headers={"Authorization": "Token 12345"})
    assert res.status_code == 401

    # Empty Bearer
    res = client.get("/api/v1/reviews", headers={"Authorization": "Bearer"})
    assert res.status_code == 401

    # Bad token
    res = client.get("/api/v1/reviews", headers={"Authorization": "Bearer bad-token-xyz"})
    assert res.status_code == 401


def test_cross_user_review_isolation():
    """A user must never retrieve another user's review (403 Forbidden)."""
    # 1. User A submits a review
    payload = {"code": "def user_a_secret(): return 'secret-data'"}
    res_submit = client.post("/api/v1/reviews", json=payload, headers=AUTH_HEADER_USER_A)
    assert res_submit.status_code == 202
    review_id = res_submit.json()["reviewId"]

    # 2. User A can retrieve their own review (200)
    res_a = client.get(f"/api/v1/reviews/{review_id}", headers=AUTH_HEADER_USER_A)
    assert res_a.status_code == 200
    assert res_a.json()["reviewId"] == review_id

    # 3. User B attempting to access User A's review is rejected with 403
    res_b = client.get(f"/api/v1/reviews/{review_id}", headers=AUTH_HEADER_USER_B)
    assert res_b.status_code == 403
    assert "not authorized" in res_b.json()["detail"].lower()


def test_review_not_found_returns_404():
    """Non-existent review ID returns 404."""
    res = client.get("/api/v1/reviews/non-existent-uuid-999", headers=AUTH_HEADER_USER_A)
    assert res.status_code == 404


# ============================================================
# 3. Language Detection Edge Cases
# ============================================================

def test_language_detection_ambiguous_and_edge_cases():
    """Language detector degrades gracefully on edge cases."""
    # Empty string
    assert detect_language("") == "text"
    assert detect_language("   ") == "text"

    # Very short snippet
    assert detect_language("x = 10") in ("python", "text", "javascript")

    # Ambiguous snippet with explicit hint
    assert detect_language("x = 10", hint="typescript") == "typescript"
    assert detect_language("x = 10", hint="python") == "python"

    # Unsupported / rare language fallback
    detected = detect_language("unknown syntax @@@@ $$$$")
    assert isinstance(detected, str) and len(detected) > 0


# ============================================================
# 4. Agent Orchestration & Partial Degradation Edge Cases
# ============================================================

@pytest.mark.asyncio
async def test_orchestrator_partial_specialist_failure():
    """
    If one or more specialist agents fail or throw an exception,
    the orchestrator must degrade gracefully, not crash, and return remaining findings.
    """
    orchestrator = OrchestratorAgent()

    # Mock Security Agent to raise an unexpected runtime error (e.g. API timeout)
    with mock.patch.object(orchestrator.security_agent, "invoke", side_effect=RuntimeError("Security model timeout")):
        context = PipelineContext(
            reviewId="rev-failover-001",
            userId="user-001",
            code="def add(a, b): return a + b",
            language="python",
        )
        overall_score, breakdown, findings = await orchestrator.execute(context)

        # Pipeline should still complete successfully
        assert 1 <= overall_score <= 10
        assert isinstance(breakdown.security, int)
        assert isinstance(findings, list)


def test_agent_malformed_json_response_parsing():
    """
    When specialist returns malformed JSON or markdown fences,
    parse_response should return a safe fallback without crashing.
    """
    agent = ReviewAgent()

    # Invalid JSON
    res = agent.parse_response("This is not valid json at all {broken")
    assert isinstance(res, SpecialistAgentResponse)
    assert len(res.findings) == 0
    assert len(res.limitations) > 0

    # Markdown JSON fence parsing
    valid_fenced = '```json\n{"agent": "test", "summary": "ok", "findings": [], "strengths": [], "limitations": []}\n```'
    res2 = agent.parse_response(valid_fenced)
    assert res2.agent == "test"
    assert res2.summary == "ok"


def test_findings_deduplication_and_severity_sorting():
    """
    Duplicate findings across agents must be deduplicated,
    and output findings must be sorted strictly by severity.
    """
    review_agent = ReviewAgent()

    resp1 = SpecialistAgentResponse(
        agent="security",
        findings=[
            AgentFinding(
                category="injection",
                severity="critical",
                description="SQL injection via raw formatting",
                suggestedFix="Use parameterized query",
            ),
            AgentFinding(
                category="naming",
                severity="low",
                description="Single letter variable name 'x'",
                suggestedFix="Rename variable",
            ),
        ],
    )

    resp2 = SpecialistAgentResponse(
        agent="historical_learning",
        findings=[
            # Duplicate of SQL injection
            AgentFinding(
                category="injection",
                severity="critical",
                description="SQL injection via raw formatting in database call",
                suggestedFix="Use parameterized query",
            ),
            AgentFinding(
                category="performance",
                severity="high",
                description="N+1 query in loop",
                suggestedFix="Batch query",
            ),
        ],
    )

    findings = review_agent.deduplicate_and_sort_findings([resp1, resp2], review_id="test-rev")

    # 1. SQL injection should be deduplicated (only 1 critical finding)
    critical_findings = [f for f in findings if f.severity == "critical"]
    assert len(critical_findings) == 1

    # 2. Total findings: 1 critical + 1 high + 1 low = 3 findings
    assert len(findings) == 3

    # 3. Severity order: critical -> high -> medium -> low
    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    ranks = [severity_order[f.severity] for f in findings]
    assert ranks == sorted(ranks)


# ============================================================
# 5. Historical Learning & CSV Ingestion Edge Cases
# ============================================================

def test_csv_ingestion_edge_cases():
    """Test parsing CSV with empty content, missing fields, extra whitespace."""
    # Empty
    assert parse_rules_csv("") == []

    # Whitespace only
    assert parse_rules_csv("   \n\n  ") == []

    # Missing ID (should be ignored)
    csv_missing_id = "id,type,description\n,security,Some description"
    assert len(parse_rules_csv(csv_missing_id)) == 0

    # Missing description (should be ignored)
    csv_missing_desc = "id,type,description\n1,security,"
    assert len(parse_rules_csv(csv_missing_desc)) == 0

    # Missing type (should default to 'general')
    csv_missing_type = "id,type,description\n1,,Always sanitize input"
    parsed = parse_rules_csv(csv_missing_type)
    assert len(parsed) == 1
    assert parsed[0]["type"] == "general"
    assert parsed[0]["description"] == "Always sanitize input"


@pytest.mark.asyncio
async def test_historical_learning_empty_rules_store():
    """When no historical rules exist, agent completes gracefully with limitations noted."""
    agent = HistoricalLearningAgent()
    context = PipelineContext(
        reviewId="rev-empty-rules",
        userId="user-001",
        code="def foo(): pass",
        language="python",
        historicalRules=[],
    )
    res = await agent.invoke(context)
    assert isinstance(res, SpecialistAgentResponse)
    assert len(res.findings) == 0
    assert "No historical rules" in res.limitations[0]


def test_rules_upload_invalid_file_type():
    """Uploading non-CSV files to /api/v1/rules/upload returns 400."""
    files = {"file": ("test.txt", b"id,type,description\n1,sec,desc", "text/plain")}
    res = client.post("/api/v1/rules/upload", files=files, headers=AUTH_HEADER_USER_A)
    assert res.status_code == 400
    assert "must be a CSV" in res.json()["detail"]


# ============================================================
# 6. Pagination & Query Edge Cases
# ============================================================

def test_pagination_boundary_values():
    """Querying reviews with invalid pagination parameters returns 422."""
    # page < 1
    res = client.get("/api/v1/reviews?page=0", headers=AUTH_HEADER_USER_A)
    assert res.status_code == 422

    # pageSize > 50
    res2 = client.get("/api/v1/reviews?pageSize=100", headers=AUTH_HEADER_USER_A)
    assert res2.status_code == 422
