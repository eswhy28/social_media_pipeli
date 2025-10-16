from app.celery_app import celery_app
from app.services.data_service import DataService
from app.database import AsyncSessionLocal
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


@celery_app.task(name="app.tasks.data_ingestion.fetch_and_store_tweets")
def fetch_and_store_tweets(query: str = "python OR javascript", max_results: int = 10):
    """
    Fetch tweets from Twitter API and store them in database
    Runs periodically (e.g., every 15 minutes for free tier)
    """
    logger.info(f"Starting tweet ingestion for query: {query}")

    import asyncio

    async def run_task():
        async with AsyncSessionLocal() as db:
            try:
                data_service = DataService(db)

                # Fetch recent tweets
                tweets = await data_service.fetch_recent_tweets(
                    query=query,
                    max_results=max_results
                )

                if not tweets:
                    logger.info("No tweets fetched")
                    return {"status": "success", "tweets_fetched": 0, "tweets_stored": 0}

                # Store tweets in database
                stored_count = await data_service.store_posts(tweets)

                logger.info(f"Ingestion complete: {len(tweets)} fetched, {stored_count} stored")

                return {
                    "status": "success",
                    "tweets_fetched": len(tweets),
                    "tweets_stored": stored_count,
                    "timestamp": datetime.utcnow().isoformat()
                }

            except Exception as e:
                logger.error(f"Error during tweet ingestion: {str(e)}")
                return {
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }

    return asyncio.run(run_task())


@celery_app.task(name="app.tasks.data_ingestion.cleanup_old_data")
def cleanup_old_data(retention_days: int = 30):
    """
    Clean up old data to manage storage for free tier
    Runs daily
    """
    logger.info(f"Starting data cleanup for posts older than {retention_days} days")

    import asyncio
    from app.models import SocialPost
    from sqlalchemy import delete

    async def run_task():
        async with AsyncSessionLocal() as db:
            try:
                cutoff_date = datetime.utcnow() - timedelta(days=retention_days)

                # Delete old posts
                result = await db.execute(
                    delete(SocialPost).where(SocialPost.posted_at < cutoff_date)
                )
                await db.commit()

                deleted_count = result.rowcount
                logger.info(f"Cleaned up {deleted_count} old posts")

                return {
                    "status": "success",
                    "deleted_count": deleted_count,
                    "cutoff_date": cutoff_date.isoformat()
                }

            except Exception as e:
                await db.rollback()
                logger.error(f"Error during cleanup: {str(e)}")
                return {"status": "error", "error": str(e)}

    return asyncio.run(run_task())

