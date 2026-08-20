# ============================================================
# Agent Configurations & Prompt Paths
# ============================================================

from typing import Dict, Any
from pydantic import BaseModel, Field
from app.config import settings


class AgentConfig(BaseModel):
    """Configuration for a specific AI agent."""

    name: str
    prompt_file: str
    model: str = Field(default_factory=lambda: settings.gemini_model)
    temperature: float = 0.0
    max_output_tokens: int = 8192
    timeout_seconds: int = Field(default_factory=lambda: settings.agent_timeout_seconds)


# Configuration registry for all 7 agents in the pipeline
AGENT_CONFIGS: Dict[str, AgentConfig] = {
    "orchestrator": AgentConfig(
        name="Orchestrator Agent",
        prompt_file="OrchestratorAgent.md",
        temperature=0.0,
    ),
    "code_quality": AgentConfig(
        name="Code Quality Agent",
        prompt_file="CodeQualityAgent.md",
        temperature=0.0,
    ),
    "security": AgentConfig(
        name="Security Agent",
        prompt_file="SecurityAgent.md",
        temperature=0.0,
    ),
    "performance": AgentConfig(
        name="Performance Agent",
        prompt_file="PerformanceAgent.md",
        temperature=0.0,
    ),
    "test_edge_case": AgentConfig(
        name="Test & Edge-Case Agent",
        prompt_file="TestEdgeCaseAgent.md",
        temperature=0.0,
    ),
    "historical_learning": AgentConfig(
        name="Historical Learning Agent",
        prompt_file="HistoricalLearningAgent.md",
        temperature=0.0,
    ),
    "review": AgentConfig(
        name="Review Agent",
        prompt_file="ReviewAgent.md",
        temperature=0.0,
    ),
}
