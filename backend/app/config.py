import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./lucid.db")
    newsapi_key: str | None = os.getenv("NEWSAPI_KEY", None)

    class Config:
        env_file = ".env"

settings = Settings()
