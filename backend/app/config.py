from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    database_url: str = "postgresql://postgres:postgres@localhost:5432/ai_life_tracker"

    # Clerk Auth
    clerk_secret_key: str = ""

    # Google Gemini
    gemini_api_key: str = ""

    # App
    env: str = "development"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
