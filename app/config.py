from pydantic_settings import BaseSettings
from pydantic import Field, ConfigDict
from typing import Optional, List
import os

class Settings(BaseSettings):
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="allow"
    )

    # App settings
    APP_NAME: str = "Social Media Pipeline POC"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: str = Field(default="development")
    DEBUG: bool = Field(default=True)
    HOST: str = Field(default="0.0.0.0")
    PORT: int = Field(default=8000)
    LOG_LEVEL: str = Field(default="INFO")

    # Database settings - SQLite for POC
    DATABASE_URL: str = Field(default="sqlite+aiosqlite:///./social_media.db")
    DB_ECHO: bool = Field(default=False)

    # Redis settings (free tier - local or RedisLabs free)
    REDIS_HOST: str = Field(default="localhost")
    REDIS_PORT: int = Field(default=6379)
    REDIS_PASSWORD: Optional[str] = Field(default=None)
    REDIS_DB: int = Field(default=0)

    @property
    def REDIS_URL(self) -> str:
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    # Twitter API v2 (free tier - 500k tweets/month)
    TWITTER_BEARER_TOKEN: str = Field(default="")
    TWITTER_API_KEY: Optional[str] = Field(default=None)
    TWITTER_API_SECRET: Optional[str] = Field(default=None)

    # Rate limiting for Twitter API (FREE TIER - ESSENTIAL ACCESS)
    # Actual limits from Twitter API documentation:
    # GET /2/tweets/search/recent: 1 request per 15 minutes (PER USER and PER APP)
    # Max 100 results per response
    TWITTER_REQUESTS_PER_15MIN: int = 1  # Free tier: 1 request per 15 minutes
    TWITTER_SEARCH_REQUESTS_PER_15MIN: int = 1  # Search endpoint limit
    TWITTER_SEARCH_REQUESTS_PER_MONTH: int = 2880  # Theoretical max: (60/15) * 24 * 30 = 2,880 requests/month
    TWITTER_MAX_RESULTS_PER_REQUEST: int = 100  # Get maximum tweets per request (Twitter API limit)

    # Celery settings
    CELERY_BROKER_URL: str = Field(default="redis://localhost:6379/0")
    CELERY_RESULT_BACKEND: str = Field(default="redis://localhost:6379/0")

    # API Settings
    API_V1_PREFIX: str = "/api/v1"

    # JWT Authentication
    SECRET_KEY: str = Field(default="your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # CORS
    CORS_ORIGINS: List[str] = Field(default=["http://localhost:3000", "http://localhost:8000"])

    # Cache settings - aggressive caching for free tier
    CACHE_TTL_SHORT: int = 60  # 1 minute for live data
    CACHE_TTL_MEDIUM: int = 300  # 5 minutes for aggregated data
    CACHE_TTL_LONG: int = 3600  # 1 hour for historical data

    # Rate limiting for API endpoints
    API_RATE_LIMIT: str = "100/minute"

    # Sentiment Analysis Settings
    SENTIMENT_POSITIVE_THRESHOLD: float = 0.1
    SENTIMENT_NEGATIVE_THRESHOLD: float = -0.1

    # Background Task Intervals (in seconds)
    TASK_FETCH_TWEETS_INTERVAL: int = 900  # 15 minutes
    TASK_ANALYZE_SENTIMENT_INTERVAL: int = 300  # 5 minutes
    TASK_AGGREGATE_DATA_INTERVAL: int = 3600  # 1 hour

    # Data retention (for free tier storage limits)
    DATA_RETENTION_DAYS: int = 30

settings = Settings()
