# Fichero para gestionar variable de entorno, url de servicios y modos de ejecucion.

from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    OPENAI_API_KEY: str
    LLM_PROVIDER: str = "openai"
    LLM_MODEL: str = "gpt-4o-mini"
    APP_ENV: str = "development"
    LOG_LEVEL: str = "DEBUG"

    class Config:
        env_file = ".env"

# el decorador @lru_cache make the configuration only load one time, and use the same in all connections.
@lru_cache
def get_settings() -> Settings:
    return Settings()