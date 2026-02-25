"""Application settings loaded from environment variables."""

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration via environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "Blis Travel Agents"
    app_version: str = "1.0.0"
    debug: bool = False

    # LLM
    openai_api_key: SecretStr
    llm_model: str = "gpt-4o-mini"
    llm_temperature: float = 0.1

    # Web Search
    tavily_api_key: SecretStr

    # Redis
    redis_url: str = "redis://localhost:6379"

    # Vector Store
    vectorstore_path: str = "./data/vectorstore"
    embedding_model: str = "text-embedding-3-small"

    # RAG
    chunk_size: int = 1500
    chunk_overlap: int = 200
    retrieval_top_k: int = 5


def get_settings() -> Settings:
    """Create and return application settings."""
    return Settings()
