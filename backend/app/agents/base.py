# ============================================================
# Base Agent — Abstract Scaffold for All AI Specialists
# ============================================================

import os
import re
import json
import logging
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List

from google import genai
from google.genai import types

from app.config import settings
from app.agents.config import AGENT_CONFIGS, AgentConfig
from app.agents.models import PipelineContext, SpecialistAgentResponse, AgentFinding

logger = logging.getLogger(__name__)

# Global singleton GenAI client
_genai_client: Optional[genai.Client] = None


def get_genai_client() -> Optional[genai.Client]:
    """Initialize or return the cached Google GenAI client instance."""
    global _genai_client
    if _genai_client is not None:
        return _genai_client

    api_key = settings.gemini_api_key or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        logger.warning("No GEMINI_API_KEY found in settings or environment.")
        return None

    try:
        _genai_client = genai.Client(api_key=api_key)
        logger.info("Initialized Google GenAI Client successfully.")
        return _genai_client
    except Exception as e:
        logger.error(f"Failed to initialize Google GenAI Client: {e}")
        return None


class BaseAgent(ABC):
    """
    Base class providing prompt loading, prompt rendering, Gemini LLM execution,
    and JSON output parsing for all review specialists.
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
            os.path.join(os.getcwd(), "backend", "app", "agents", "prompts"),
            os.path.join(os.getcwd(), "backend", "prompts"),
            os.path.join(os.getcwd(), "backend", "Prompts"),
            os.path.join(os.getcwd(), "prompts"),
            os.path.join(os.getcwd(), "Prompts"),
            os.path.abspath(os.path.join(os.path.dirname(__file__), "prompts")),
            os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "prompts")),
            os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "Prompts")),
        ]

        candidate_filenames = [
            self.config.prompt_file,
            f"{self.agent_id}_system.prompt.md",
            f"{self.agent_id}.md",
            f"{self.config.name.replace(' ', '')}.md",
        ]

        for directory in search_dirs:
            if not os.path.exists(directory):
                continue
            for filename in candidate_filenames:
                prompt_path = os.path.join(directory, filename)
                if os.path.exists(prompt_path):
                    try:
                        with open(prompt_path, "r", encoding="utf-8") as f:
                            content = f.read().strip()
                            if content:
                                self._prompt_cache = content
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

    def format_user_prompt(self, context: PipelineContext) -> str:
        """
        Render the runtime user context prompt template passed to the agent.
        """
        rules_text = "None provided"
        if context.historicalRules:
            rules_lines = []
            for r in context.historicalRules:
                r_id = r.get("id", "N/A")
                r_type = r.get("type", "General")
                r_desc = r.get("description", "")
                r_pat = r.get("pattern", "")
                rules_lines.append(f"- Rule #{r_id} [{r_type}]: {r_desc} (Pattern: {r_pat})")
            rules_text = "\n".join(rules_lines)

        return f"""Review the following code change for {self.config.name}.

## Programming Language
{context.language}

## Pull Request Title
{context.title or 'N/A'}

## Pull Request Description
{context.description or 'N/A'}

## Project Coding Guidelines
{context.guidelines or 'None provided'}

## Historical Team Rules
{rules_text}

## Changed Files
{context.title or 'snippet.' + context.language}

## Unified Diff / Source Code
{context.code}

## Linter or Static-Analysis Results
None provided

Return valid JSON according to the {self.config.name} output contract."""

    def parse_response(self, raw_text: str) -> SpecialistAgentResponse:
        """
        Parse raw model response text (expected JSON) into SpecialistAgentResponse model.
        """
        cleaned = raw_text.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        data = None
        # 1. Direct JSON parse with strict=False
        try:
            data = json.loads(cleaned, strict=False)
        except Exception:
            pass

        # 2. Fix invalid backslash escapes (e.g. \_ or \s or unescaped quotes)
        if data is None:
            try:
                fixed = re.sub(r'\\(?![/"\\bfnrtuU])', r'\\\\', cleaned)
                data = json.loads(fixed, strict=False)
            except Exception:
                pass

        # 3. Extract JSON object substring
        if data is None:
            try:
                start = cleaned.find("{")
                end = cleaned.rfind("}")
                if start != -1 and end != -1 and end > start:
                    sub = cleaned[start : end + 1]
                    data = json.loads(sub, strict=False)
            except Exception:
                pass

        if not isinstance(data, dict):
            logger.warning(f"Response from {self.config.name} was not a JSON object. Raw: {raw_text[:200]}")
            return SpecialistAgentResponse(
                agent=self.agent_id,
                language="unknown",
                summary=f"Analysis completed by {self.config.name}",
                findings=[],
                strengths=[],
                limitations=["Model returned non-object response."],
            )

        try:
            # Guarantee agent name is set
            if "agent" not in data or not data["agent"]:
                data["agent"] = self.agent_id

            # Normalize findings
            if "findings" in data and isinstance(data["findings"], list):
                for f in data["findings"]:
                    if isinstance(f, dict):
                        if not f.get("description"):
                            f["description"] = (
                                f.get("violation")
                                or f.get("issue")
                                or f.get("rationale")
                                or f.get("explanation")
                                or f.get("summary")
                                or f.get("details")
                                or f.get("message")
                                or f.get("title")
                                or "Issue identified."
                            )
                        if not f.get("suggestedFix"):
                            f["suggestedFix"] = (
                                f.get("suggestedTest")
                                or f.get("suggested_fix")
                                or f.get("suggested_test")
                                or f.get("remediation")
                                or f.get("fix")
                                or f.get("recommendation")
                                or f.get("solution")
                                or f.get("action")
                                or "Review and refactor accordingly."
                            )
                        if not f.get("title"):
                            f["title"] = f.get("description", "")[:60]
                        if not f.get("matchedRuleId"):
                            if isinstance(f.get("historicalRule"), dict) and f["historicalRule"].get("id"):
                                f["matchedRuleId"] = str(f["historicalRule"]["id"])
                            elif f.get("ruleId") or f.get("rule_id") or f.get("rule"):
                                f["matchedRuleId"] = str(f.get("ruleId") or f.get("rule_id") or f.get("rule"))
                        if f.get("matchedRuleId"):
                            # Normalize "Rule #3" or "Rule 3" to "3" if single number
                            m = re.search(r'\b\d+\b', str(f["matchedRuleId"]))
                            if m:
                                f["matchedRuleId"] = m.group(0)
                            else:
                                f["matchedRuleId"] = str(f["matchedRuleId"])
                        if not f.get("category") and (f.get("type") or f.get("rule_type")):
                            f["category"] = str(f.get("type") or f.get("rule_type"))

            return SpecialistAgentResponse(**data)
        except Exception as e:
            logger.warning(f"Failed to instantiate SpecialistAgentResponse for {self.config.name}: {e}")
            return SpecialistAgentResponse(
                agent=self.agent_id,
                language="unknown",
                summary=f"Analysis completed by {self.config.name}",
                findings=[],
                strengths=[],
                limitations=[f"Validation error: {str(e)}"],
            )

    async def invoke(self, context: PipelineContext) -> SpecialistAgentResponse:
        """
        Execute the agent logic against the Gemini API using the loaded system prompt
        and structured pipeline context.
        """
        logger.info(f"[{self.config.name}] Invoking Gemini LLM for review {context.reviewId} (model: {self.config.model})")
        client = get_genai_client()
        if client is None:
            logger.warning(f"[{self.config.name}] Gemini client unavailable. Returning fallback response.")
            return SpecialistAgentResponse(
                agent=self.agent_id,
                language=context.language,
                summary=f"Analysis could not be performed by {self.config.name}: Gemini client unavailable.",
                findings=[],
                strengths=[],
                limitations=["Gemini API client not configured or initialized."],
            )

        system_prompt = self.load_prompt()
        user_prompt = self.format_user_prompt(context)

        try:
            config = types.GenerateContentConfig(
                temperature=self.config.temperature,
                max_output_tokens=self.config.max_output_tokens,
                response_mime_type="application/json",
                safety_settings=[
                    types.SafetySetting(
                        category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                        threshold=types.HarmBlockThreshold.BLOCK_ONLY_HIGH,
                    ),
                    types.SafetySetting(
                        category=types.HarmCategory.HARM_CATEGORY_HARASSMENT,
                        threshold=types.HarmBlockThreshold.BLOCK_ONLY_HIGH,
                    ),
                    types.SafetySetting(
                        category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                        threshold=types.HarmBlockThreshold.BLOCK_ONLY_HIGH,
                    ),
                    types.SafetySetting(
                        category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                        threshold=types.HarmBlockThreshold.BLOCK_ONLY_HIGH,
                    ),
                ],
            )
            if system_prompt:
                config.system_instruction = system_prompt

            response = await client.aio.models.generate_content(
                model=self.config.model,
                contents=user_prompt,
                config=config,
            )

            raw_text = response.text or "{}"
            parsed = self.parse_response(raw_text)
            if not parsed.language:
                parsed.language = context.language
            return parsed

        except Exception as e:
            logger.error(f"[{self.config.name}] LLM invocation failed: {e}", exc_info=True)
            return SpecialistAgentResponse(
                agent=self.agent_id,
                language=context.language,
                summary=f"Analysis by {self.config.name} encountered an error.",
                findings=[],
                strengths=[],
                limitations=[f"Error during LLM invocation: {str(e)}"],
            )
