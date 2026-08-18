# ============================================================
# Configuration & Settings — Pydantic Settings
# ============================================================

import os
from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment or .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # ─── GCP & Firebase ─────────────────────────────────────
    gcp_project_id: str = "daring-fiber-408912"
    gcp_region: str = "us-central1"
    firebase_project_id: str = "daring-fiber-408912"

    # ─── CORS ───────────────────────────────────────────────
    cors_allowed_origins: Union[List[str], str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    @field_validator("cors_allowed_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Union[List[str], str]) -> List[str]:
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    # ─── Storage & CSV Ingestion ────────────────────────────
    gcs_rules_bucket: str = "daring-fiber-408912-rules"
    gcs_rules_csv_path: str = "rules/historical_reviews.csv"

    # ─── Agent Defaults ─────────────────────────────────────
    gemini_model: str = "gemini-3.6-flash"
    agent_timeout_seconds: int = 30
    agent_max_retries: int = 2

    # ─── App Settings ───────────────────────────────────────
    log_level: str = "INFO"
    environment: str = "development"


# Global singleton settings instance
settings = Settings()
