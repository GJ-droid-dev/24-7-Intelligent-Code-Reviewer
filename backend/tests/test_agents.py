# ============================================================
# Tests — Multi-Agent Pipeline (Phase 3)
# ============================================================

import pytest
from app.agents.models import PipelineContext, SpecialistAgentResponse
from app.agents.code_quality import CodeQualityAgent
from app.agents.security import SecurityAgent
from app.agents.performance import PerformanceAgent
from app.agents.test_edge_case import TestEdgeCaseAgent
from app.agents.historical_learning import HistoricalLearningAgent
from app.agents.review_agent import ReviewAgent
from app.agents.orchestrator import OrchestratorAgent


@pytest.fixture
def sample_context():
    return PipelineContext(
        reviewId="rev-test-001",
        userId="user-test-001",
        code="""
def fetch_user_data(user_id):
    q = f"SELECT * FROM users WHERE id = {user_id}"
    for row in db.execute(q):
        print(row)
""",
        language="python",
        title="Sample Test Function",
    )


def test_prompt_loading():
    """Verify prompt loader successfully loads markdown prompt files."""
    cq = CodeQualityAgent()
    prompt = cq.load_prompt()
    assert "Code Quality Agent" in prompt
    assert len(prompt) > 50


@pytest.mark.asyncio
async def test_code_quality_agent(sample_context):
    """Test CodeQualityAgent produces structured findings."""
    agent = CodeQualityAgent()
    res = await agent.invoke(sample_context)
    assert isinstance(res, SpecialistAgentResponse)
    assert res.agent == "code_quality"
    assert len(res.findings) > 0


@pytest.mark.asyncio
async def test_security_agent(sample_context):
    """Test SecurityAgent identifies injection patterns."""
    agent = SecurityAgent()
    res = await agent.invoke(sample_context)
    assert isinstance(res, SpecialistAgentResponse)
    assert res.agent == "security"
    assert any(f.category == "injection" for f in res.findings)


@pytest.mark.asyncio
async def test_performance_agent(sample_context):
    """Test PerformanceAgent flags queries in loops."""
    agent = PerformanceAgent()
    res = await agent.invoke(sample_context)
    assert isinstance(res, SpecialistAgentResponse)
    assert res.agent == "performance"
    assert any(f.category == "n_plus_one" for f in res.findings)


@pytest.mark.asyncio
async def test_test_edge_case_agent(sample_context):
    """Test TestEdgeCaseAgent identifies missing error handling."""
    agent = TestEdgeCaseAgent()
    res = await agent.invoke(sample_context)
    assert isinstance(res, SpecialistAgentResponse)
    assert res.agent == "test_edge_case"
    assert len(res.findings) > 0


@pytest.mark.asyncio
async def test_historical_learning_agent(sample_context):
    """Test HistoricalLearningAgent matches rules with rule citations."""
    sample_context.historicalRules = [
        {"id": "3", "type": "security", "description": "Never interpolate raw user input directly into SQL"}
    ]
    agent = HistoricalLearningAgent()
    res = await agent.invoke(sample_context)
    assert isinstance(res, SpecialistAgentResponse)
    assert res.agent == "historical_learning"
    assert any(f.matchedRuleId == "3" for f in res.findings)


@pytest.mark.asyncio
async def test_orchestrator_parallel_fan_out(sample_context):
    """Test Orchestrator runs all specialists in parallel and returns scored report."""
    orchestrator = OrchestratorAgent()
    overall_score, breakdown, findings = await orchestrator.execute(sample_context)

    assert 1 <= overall_score <= 10
    assert breakdown.security <= 6  # Due to SQL injection
    assert breakdown.performance <= 8
    assert len(findings) >= 3
    # Check findings are sorted by severity
    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    ranks = [severity_order.get(f.severity, 4) for f in findings]
    assert ranks == sorted(ranks)
