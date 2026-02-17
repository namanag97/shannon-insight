"""
Configuration module for the service.

Loads settings from environment variables with sensible defaults.
Pydantic handles validation and type coercion.
"""

from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment."""

    # Server
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    debug: bool = Field(default=False, description="Enable debug mode")

    # Database
    database_url: str = Field(
        default="sqlite:///./app.db",
        description="Database connection URL"
    )
    db_echo: bool = Field(default=False, description="Echo SQL queries")

    # JWT
    secret_key: str = Field(
        default="dev-secret-key-change-in-production",
        description="Secret key for JWT signing"
    )
    algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(
        default=30, description="JWT expiration time in minutes"
    )

    # Security
    password_min_length: int = Field(default=8, description="Minimum password length")
    password_require_special: bool = Field(
        default=True, description="Require special characters in password"
    )

    # CORS
    cors_origins: list[str] = Field(
        default=["http://localhost:3000"],
        description="Allowed CORS origins"
    )

    # Logging
    log_level: str = Field(default="INFO", description="Log level")

    class Config:
        """Pydantic config."""
        env_file = ".env"
        case_sensitive = False


settings = Settings()
