import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Insurance LINE Assistant API"
    API_V1_STR: str = "/api/v1"
    
    SECRET_KEY: str = "insurance_line_assistant_secret_key_dev"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day

    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres_password"
    POSTGRES_DB: str = "insurance_assistant_db"
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres_password@localhost:5432/insurance_assistant_db"

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_URL: str = "redis://localhost:6379/0"

    LINE_CHANNEL_SECRET: str = "mock_line_channel_secret"
    LINE_CHANNEL_ACCESS_TOKEN: str = "mock_line_channel_access_token"
    LINE_LIFF_ID: str = "mock_line_liff_id"

    SMS_API_KEY: str = "mock_sms_api_key"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
