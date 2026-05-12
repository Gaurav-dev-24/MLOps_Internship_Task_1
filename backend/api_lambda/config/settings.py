"""
config/settings.py

Centralised environment variable loading for api_lambda.
All settings are injected via Lambda environment configuration — never hardcoded.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # AWS Infrastructure
    S3_BUCKET_NAME: str
    DYNAMODB_TABLE_NAME: str
    AWS_REGION: str = "us-east-1"

    # S3 Presigned URL configuration
    PRESIGNED_URL_EXPIRY: int = 300  # seconds

    # File upload constraints
    MAX_FILE_SIZE_BYTES: int = 10 * 1024 * 1024  # 10 MB

    # Allowed file extensions (used for validation in schema)
    ALLOWED_EXTENSIONS: list[str] = [".pdf", ".png", ".jpg", ".jpeg"]


# Module-level singleton — imported everywhere in api_lambda
settings = Settings()
