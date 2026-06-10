# Fichero para gestionar variable de entorno, url de servicios y modos de ejecucion.

from functools import lru_cache
from typing import Literal

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env file."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    OPENAI_API_KEY: str | None = None
    ANTHROPIC_API_KEY: str | None = None
    LLM_MODEL: str = "openai/gpt-4o-mini"
    LLM_FALLBACK_MODEL: str | None = "anthropic/haiku 4.5"
    APP_ENV: Literal["development", "staging", "production"] = "development"
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "DEBUG"

    @model_validator(mode="after")
    def validate_api_key_for_provider(self) -> "Settings":
        for  model in filter(None, [self.LLM_MODEL, self.LLM_FALLBACK_MODEL]):
            if self.LLM_MODEL.startswith("openai/") and not self.OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY is required for openai models")
            if self.LLM_MODEL.startswith("anthropic/")and not self.ANTHROPIC_API_KEY:
                raise ValueError("ANTHROPIC_API_KEY is required for anthropic models")
        return self


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings (singleton)."""
    return Settings()