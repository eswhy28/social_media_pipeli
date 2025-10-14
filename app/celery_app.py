from celery import Celery
from app.config import settings

celery_app = Celery(
    "social_monitor",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.data_ingestion",
        "app.tasks.sentiment_analysis",
        "app.tasks.report_generation",
        "app.tasks.anomaly_detection",
    ]
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
)

# Periodic tasks schedule
celery_app.conf.beat_schedule = {
    'fetch-social-media-data-every-5-minutes': {
        'task': 'app.tasks.data_ingestion.fetch_social_media_data',
        'schedule': 300.0,  # 5 minutes
    },
    'analyze-sentiment-every-10-minutes': {
        'task': 'app.tasks.sentiment_analysis.analyze_recent_posts',
        'schedule': 600.0,  # 10 minutes
    },
    'detect-anomalies-every-15-minutes': {
        'task': 'app.tasks.anomaly_detection.detect_anomalies',
        'schedule': 900.0,  # 15 minutes
    },
    'cleanup-old-data-daily': {
        'task': 'app.tasks.data_ingestion.cleanup_old_data',
        'schedule': 86400.0,  # 24 hours
    },
}
from pydantic_settings import BaseSettings
from typing import List
from functools import lru_cache


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Social Media Monitoring API"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/social_monitor"
    DB_ECHO: bool = False

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Rate Limiting
    RATE_LIMIT_STANDARD: int = 1000
    RATE_LIMIT_AI: int = 100
    RATE_LIMIT_REPORTS: int = 10
    RATE_LIMIT_EXPORT: int = 50

    # OpenAI
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4-turbo-preview"

    # Twitter/X API
    X_API_KEY: str = ""
    X_API_SECRET: str = ""
    X_ACCESS_TOKEN: str = ""
    X_ACCESS_TOKEN_SECRET: str = ""
    X_BEARER_TOKEN: str = ""

    # Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = "noreply@socialmonitor.com"

    # SMS
    SMS_GATEWAY_URL: str = ""
    SMS_API_KEY: str = ""

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # Monitoring
    ENABLE_METRICS: bool = True
    LOG_LEVEL: str = "INFO"

    # Data Retention
    RAW_DATA_RETENTION_DAYS: int = 90
    AGGREGATED_DATA_RETENTION_DAYS: int = 730

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

