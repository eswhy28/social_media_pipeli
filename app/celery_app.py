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
        "app.tasks.social_media_collection",  # Nigerian data collection tasks
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
    # Dynamic Hashtag Discovery Tasks
    'update-hashtag-cache-hourly': {
        'task': 'update_hashtag_cache',
        'schedule': 3600.0,  # Every hour
    },
    'track-hashtag-history-every-6-hours': {
        'task': 'track_hashtag_history',
        'schedule': 21600.0,  # Every 6 hours
    },

    # Nigerian Data Collection Tasks
    'collect-google-trends-hourly': {
        'task': 'collect_google_trends',
        'schedule': 3600.0,  # Every hour
    },
    'collect-tiktok-content-every-2-hours': {
        'task': 'collect_tiktok_content',
        'schedule': 7200.0,  # Every 2 hours
    },
    'collect-facebook-content-every-3-hours': {
        'task': 'collect_facebook_content',
        'schedule': 10800.0,  # Every 3 hours
    },
    'aggregate-analytics-hourly': {
        'task': 'aggregate_analytics',
        'schedule': 3600.0,  # Every hour
    },
    'reset-counters-daily': {
        'task': 'reset_daily_counters',
        'schedule': 86400.0,  # Daily at midnight
    },

    # Legacy Tasks (keep for compatibility)
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
