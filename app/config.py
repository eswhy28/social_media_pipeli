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
    # ACTUAL limits from Twitter API Free Tier:
    # GET /2/tweets/search/recent: 10 requests per MONTH total
    # Max 10 results per request (Free Tier)
    TWITTER_REQUESTS_PER_15MIN: int = 1  # Free tier: effectively unlimited per 15min, but...
    TWITTER_SEARCH_REQUESTS_PER_15MIN: int = 1  # ...only 10 requests per MONTH total!
    TWITTER_SEARCH_REQUESTS_PER_MONTH: int = 10  # Free tier: 10 requests per MONTH (hard limit)
    TWITTER_MAX_RESULTS_PER_REQUEST: int = 10  # Free tier: max 10 tweets per request

    # TikTok API Configuration
    TIKTOK_API_KEY: Optional[str] = Field(default=None)
    TIKTOK_API_SECRET: Optional[str] = Field(default=None)
    TIKTOK_ACCESS_TOKEN: Optional[str] = Field(default=None)

    # Facebook/Instagram API Configuration
    FACEBOOK_APP_ID: Optional[str] = Field(default=None)
    FACEBOOK_APP_SECRET: Optional[str] = Field(default=None)
    FACEBOOK_ACCESS_TOKEN: Optional[str] = Field(default=None)

    # Apify API Configuration
    # Get your API token from: https://console.apify.com/account/integrations
    APIFY_API_TOKEN: Optional[str] = Field(default=None)

    # Google Trends Configuration
    # pytrends doesn't require API key, but we configure timeout and retry settings
    GOOGLE_TRENDS_TIMEOUT: int = Field(default=30)
    GOOGLE_TRENDS_RETRIES: int = Field(default=3)

    # Celery settings
    CELERY_BROKER_URL: str = Field(default="redis://localhost:6379/0")
    CELERY_RESULT_BACKEND: str = Field(default="redis://localhost:6379/0")

    # API Settings
    API_V1_PREFIX: str = "/api/v1"

    # JWT Authentication
    SECRET_KEY: str = Field(default="your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # Authentication toggle for POC
    DISABLE_AUTH: bool = Field(default=True)

    # CORS
    CORS_ORIGINS: List[str] = Field(default=["http://localhost:3000", "http://localhost:8000", "*"])

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
