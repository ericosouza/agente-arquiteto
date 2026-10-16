"""Configuration settings for AI Software Architecture Designer backend."""

import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "AI Software Architecture Designer — ArchiMate"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # LLM Settings
    # Supported: "gemini", "openai", "anthropic", "ollama", "builtin"
    LLM_PROVIDER: str = "auto"

    # API Keys & URLs
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.0-flash"

    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"

    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_MODEL: str = "claude-3-5-sonnet-20241022"

    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.2"

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:8000", "http://127.0.0.1:8000", "*"]

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }

    def detect_active_provider(self) -> str:
        """Determines the active provider based on configuration or available API keys."""
        if self.LLM_PROVIDER and self.LLM_PROVIDER != "auto":
            return self.LLM_PROVIDER.lower()
        if self.GEMINI_API_KEY:
            return "gemini"
        if self.OPENAI_API_KEY:
            return "openai"
        if self.ANTHROPIC_API_KEY:
            return "anthropic"
        # If no cloud keys, default to built-in expert engine
        return "builtin"


settings = Settings()
