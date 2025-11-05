from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class OllamaSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="OLLAMA_")
    
    host: str = "http://ollama:11434"
    model: str = "gemma3:270m"
    embedding_model: str = Field(default="nomic-embed-text")
    timeout: int = 60
    max_retries: int = 3
    temperature: float = 0.1

    class Config:
        env_prefix = "OLLAMA_"

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    app_name: str = "InMind"
    debug: bool = False
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    ollama: OllamaSettings = OllamaSettings()


def get_settings() -> Settings:
    return Settings()