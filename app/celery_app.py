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
