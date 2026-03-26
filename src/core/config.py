from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn, RedisDsn, field_validator
from typing import Optional, List

class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = "CreatorIQ Backend"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"
    API_V1_STR: str = "/api/v1"
    CORS_ORIGINS: List[str] = ["*"]

    # Database
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "creatoriq"
    
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"

    # JWT
    SECRET_KEY: str = "development_secret_key_change_me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 90

    # Currently hardcoding API keys for testing, but these should be set via environment variables in production
    YOUTUBE_API_KEY: Optional[str] = "AIzaSyB1kLHFa6WiXm9jXY0s-rgxCgNHpIyLFHU"
    YOUTUBE_CLIENT_ID: Optional[str] = None
    YOUTUBE_CLIENT_SECRET: Optional[str] = None
    
    # For now i am putting it here 
    GEMINI_API_KEY: Optional[str] = "AIzaSyCdizPkpTLtuqFICqRGrFEwHptVJ5HGhkU"
    GEMINI_MODEL: str = "gemini-3-flash-preview"
    SERPAPI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True
    )

settings = Settings()
