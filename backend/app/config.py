from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    database_url: str = "postgresql://postgres:postgres@localhost:5432/ai_life_tracker"

    # Clerk Auth
    clerk_secret_key: str = ""
    clerk_publishable_key: str = ""  # e.g., pk_test_xxx or pk_live_xxx

    # Security: Only enable in explicitly controlled local development
    # WARNING: Setting this to True accepts unverified JWTs - NEVER use in production
    dev_allow_unverified_tokens: bool = False

    # Google Gemini
    gemini_api_key: str = ""

    # Redis
    redis_url: str = "redis://localhost:6379/0"
    context_ttl_seconds: int = 86400  # 24 hours TTL for inactive contexts

    # App
    env: str = "development"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
