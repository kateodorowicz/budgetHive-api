"""Application configuration."""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # JWT
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # Database
    DATABASE_URL: str = "sqlite:///./budgethive.db"

    # CORS - allow React frontend (Lovable)
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"

    # Google Gemini for budget analysis
    GEMINI_API_KEY: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra env vars (e.g. old OPENAI_* after migration)


settings = Settings()
