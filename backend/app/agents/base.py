# ============================================================
# Base Agent — Abstract Scaffold for All AI Specialists
# ============================================================

import os
import json
import logging
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List

from app.agents.config import AGENT_CONFIGS, AgentConfig
from app.agents.models import PipelineContext, SpecialistAgentResponse, AgentFinding

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """
    Abstract base class providing prompt loading, execution scaffolding,
    and output validation for all review specialists.
    """

    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.config: AgentConfig = AGENT_CONFIGS.get(
            agent_id,
            AgentConfig(name=agent_id.capitalize(), prompt_file=f"{agent_id}.md")
        )
        self._prompt_cache: Optional[str] = None

    def load_prompt(self) -> str:
        """
        Load the system prompt markdown file from backend/prompts or backend/Prompts.
        """
        if self._prompt_cache is not None:
            return self._prompt_cache

        search_dirs = [
            os.path.join(os.getcwd(), "backend", "prompts"),
            os.path.join(os.getcwd(), "backend", "Prompts"),
            os.path.join(os.getcwd(), "prompts"),
            os.path.join(os.getcwd(), "Prompts"),
            os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "prompts")),
            os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "Prompts")),
        ]

        for directory in search_dirs:
            prompt_path = os.path.join(directory, self.config.prompt_file)
            if os.path.exists(prompt_path):
                try:
                    with open(prompt_path, "r", encoding="utf-8") as f:
                        self._prompt_cache = f.read().strip()
                        logger.info(f"Loaded prompt for {self.config.name} from {prompt_path}")
                        return self._prompt_cache
                except Exception as e:
                    logger.warning(f"Error reading prompt file {prompt_path}: {e}")

        logger.warning(f"No prompt file found for {self.config.name} ({self.config.prompt_file}). Using empty prompt.")
        self._prompt_cache = ""
        return self._prompt_cache

    def format_input_context(self, context: PipelineContext) -> Dict[str, Any]:
        """
        Convert pipeline context into the structured input dictionary expected by the agent prompt.
        """
        return {
            "language": context.language,
            "title": context.title,
            "description": context.description,
            "code": context.code,
            "guidelines": context.guidelines,
            "historicalRules": context.historicalRules,
        }

    def parse_response(self, raw_text: str) -> SpecialistAgentResponse:
        """
        Parse raw model response text (expected JSON) into SpecialistAgentResponse model.
        """
        # Clean markdown code fences if model enclosed JSON
        cleaned = raw_text.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        try:
            data = json.loads(cleaned)
            return SpecialistAgentResponse(**data)
        except Exception as e:
            logger.warning(f"Failed to parse structured JSON from {self.config.name}: {e}")
            return SpecialistAgentResponse(
                agent=self.agent_id,
                language="unknown",
                summary=f"Analysis completed by {self.config.name}",
                findings=[],
                strengths=[],
                limitations=[f"Raw response could not be parsed: {str(e)}"],
            )

    @abstractmethod
    async def invoke(self, context: PipelineContext) -> SpecialistAgentResponse:
        """
        Execute the agent logic and return the structured response.
        Subclasses implement agent-specific logic and tool integrations.
        """
        pass
