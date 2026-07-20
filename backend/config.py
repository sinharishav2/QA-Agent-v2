from pydantic_settings import BaseSettings
from typing import Optional
import os

_ENV_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")


class Settings(BaseSettings):
    fastapi_env: str = "development"
    fastapi_debug: bool = True
    fastapi_host: str = "0.0.0.0"
    fastapi_port: int = 8000

    database_url: str = "postgresql://user:password@localhost:5432/qa_ai_platform"
    redis_url: str = "redis://localhost:6379/0"

    # LLM Configuration
    llm_provider: Optional[str] = None
    openai_api_key: Optional[str] = None
    openai_model: Optional[str] = None
    azure_openai_api_key: Optional[str] = None
    azure_openai_endpoint: Optional[str] = None
    azure_openai_api_version: Optional[str] = None
    azure_openai_deployment: Optional[str] = None
    google_api_key: Optional[str] = None

    upload_dir: str = "./uploads"
    generated_projects_dir: str = "./generated_projects"
    reports_dir: str = "./reports"
    logs_dir: str = "./logs"

    secret_key: str = "your_secret_key_here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    log_level: str = "INFO"

    class Config:
        env_file = _ENV_FILE
        case_sensitive = False


settings = Settings()
