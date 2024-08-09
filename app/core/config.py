import os
from typing import List

from pydantic.v1 import BaseSettings


class Settings(BaseSettings):
    # Project information
    PROJECT_NAME: str = "LLM Hub"
    PROJECT_VERSION: str = "1.0.0"
    PROJECT_DESCRIPTION: str = (
        "An API for interacting with large language models using Ollama."
    )

    # Database configuration
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "default_user")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "default_password")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "default_db")
    DATABASE_URL: str = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@db:5432/{POSTGRES_DB}"

    # Ollama configuration
    OLLAMA_URL: str = os.getenv("OLLAMA_URL", "http://ollama:11434")
    OLLAMA_KEEP_ALIVE: str = os.getenv("OLLAMA_KEEP_ALIVE", "24h")
    OLLAMA_HOST: str = os.getenv("OLLAMA_HOST", "0.0.0.0")
    OLLAMA_USE_GPU: bool = os.getenv("OLLAMA_USE_GPU", "false").lower() == "true"

    # Debug mode
    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")

    # Available models
    AVAILABLE_MODELS: List[str] = os.getenv(
        "AVAILABLE_MODELS", "llama3,mod_llama3,phi3"
    ).split(",")

    # Redis configuration
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://redis:6379/0")

    # Security
    SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "sD48VfmRgP")

    # Celery configuration
    CELERY_WORKER_CONCURRENCY: int = (
        4  # or any other value suitable for your environment
    )

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
