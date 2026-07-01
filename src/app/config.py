"""Application configuration from environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    Attributes:
        database_url: PostgreSQL connection string.
        app_name: Name of the application.
        debug: Enable debug mode.
    """

    database_url: str = (
        "postgresql+asyncpg://app:devpassword@localhost:5432/clinical_notes"
    )
    app_name: str = "Clinical Notes API"
    debug: bool = False

    model_config = {"env_file": ".env", "extra": "ignore"}


def get_settings() -> Settings:
    """Create and return application settings."""
    return Settings()
