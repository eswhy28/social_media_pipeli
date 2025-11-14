"""
Background Tasks for Automated Social Media Data Collection
Focused on Nigerian Trending Topics and News
"""

import logging
from datetime import datetime
from celery import shared_task
from sqlalchemy.ext.asyncio import AsyncSession
import asyncio

from app.database import AsyncSessionLocal
from app.services.google_trends_service import get_google_trends_service
from app.services.tiktok_service import get_tiktok_service
from app.services.facebook_service import get_facebook_service
from app.services.apify_service import get_apify_service
from app.services.database_storage_service import get_storage_service
from app.services.data_pipeline_service import get_data_pipeline_service
from app.services.monitoring_service import get_monitoring_service
from app.services.cross_platform_analytics import get_cross_platform_analytics
from app.services.hashtag_discovery_service import get_hashtag_discovery_service
from app.nigerian_topics_config import (
    get_priority_topics_for_time,
    build_twitter_search_query,
    NIGERIAN_TRENDING_CATEGORIES,
    NIGERIAN_NEWS_SOURCES
)

logger = logging.getLogger(__name__)


@shared_task(name="collect_google_trends")
def collect_google_trends_task():
    """
    Collect Google Trends data for Nigeria
    """
    asyncio.run(_collect_google_trends())


async def _collect_google_trends():
    """Async implementation of Google Trends collection"""
    try:
        logger.info("Starting Google Trends collection")
        async with AsyncSessionLocal() as db:
            trends_service = get_google_trends_service()
            storage_service = get_storage_service(db)

            # Get trending searches
            trending = await trends_service.get_trending_searches("NG")

            if trending:
                # Store data in PostgreSQL
                stored = await storage_service.store_google_trends(
                    trends_data=trending,
                    trend_type="trending_search",
                    source_name="google_trends_ng"
                )

                logger.info(f"Collected and stored {stored} Google Trends items in Postgres")
            else:
                logger.warning("No Google Trends returned")

    except Exception as e:
        logger.error(f"Error in Google Trends collection: {e}")


@shared_task(name="collect_tiktok_content")
def collect_tiktok_content_task():
    """
    Collect TikTok content from Nigerian hashtags
    """
    asyncio.run(_collect_tiktok_content())


async def _collect_tiktok_content():
    """Async implementation of TikTok collection"""
    try:
        logger.info("Starting TikTok collection")
        async with AsyncSessionLocal() as db:
            tiktok_service = get_tiktok_service()
            storage_service = get_storage_service(db)

            # Monitor Nigerian content
            result = await tiktok_service.monitor_nigerian_content(
                max_videos_per_hashtag=20
            )

            if result.get('videos'):
                # Store data in PostgreSQL
                stored = await storage_service.store_tiktok_videos(
                    videos=result['videos'],
                    source_name="nigerian_hashtags"
                )

                logger.info(f"Collected and stored {stored} TikTok videos in Postgres")
            else:
                logger.warning(f"No TikTok videos returned: {result.get('error', 'Unknown error')}")

    except Exception as e:
        logger.error(f"Error in TikTok collection: {e}")


@shared_task(name="collect_facebook_content")
def collect_facebook_content_task():
    """
    Collect Facebook content from Nigerian pages
    """
    asyncio.run(_collect_facebook_content())


async def _collect_facebook_content():
    """Async implementation of Facebook collection"""
    try:
        logger.info("Starting Facebook collection with Apify")
        async with AsyncSessionLocal() as db:
            facebook_service = get_facebook_service()
            storage_service = get_storage_service(db)

            # Monitor Nigerian pages using Apify
            result = await facebook_service.monitor_nigerian_pages(
                posts_per_page=50  # Updated parameter for Apify
            )

            if result.get('posts'):
                # Store data in PostgreSQL
                stored = await storage_service.store_facebook_posts(
                    posts=result['posts'],
                    source_name="nigerian_pages"
                )

                logger.info(f"Collected and stored {stored} Facebook posts in Postgres")
            else:
                logger.warning(f"No Facebook posts returned: {result.get('error', 'Unknown error')}")

    except Exception as e:
        logger.error(f"Error in Facebook collection: {e}")


@shared_task(name="aggregate_analytics")
def aggregate_analytics_task():
    """
    Aggregate analytics data hourly
    """
    asyncio.run(_aggregate_analytics())


async def _aggregate_analytics():
    """Async implementation of analytics aggregation"""
    try:
        logger.info("Starting analytics aggregation")
        async with AsyncSessionLocal() as db:
            analytics_service = get_cross_platform_analytics(db)

            # Aggregate for current hour
            current_hour = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
            success = await analytics_service.aggregate_hourly_data(current_hour)

            if success:
                logger.info(f"Successfully aggregated analytics for {current_hour}")
            else:
                logger.error("Failed to aggregate analytics")

    except Exception as e:
        logger.error(f"Error in analytics aggregation: {e}")


@shared_task(name="reset_daily_counters")
def reset_daily_counters_task():
    """
    Reset daily counters for monitoring (runs at midnight)
    """
    asyncio.run(_reset_daily_counters())


async def _reset_daily_counters():
    """Async implementation of daily counter reset"""
    try:
        logger.info("Resetting daily counters")
        async with AsyncSessionLocal() as db:
            monitoring_service = get_monitoring_service(db)
            success = await monitoring_service.reset_daily_counters()

            if success:
                logger.info("Successfully reset daily counters")
            else:
                logger.error("Failed to reset daily counters")

    except Exception as e:
        logger.error(f"Error resetting daily counters: {e}")


@shared_task(name="comprehensive_collection")
def comprehensive_collection_task():
    """
    Comprehensive collection from all sources
    """
    asyncio.run(_comprehensive_collection())


async def _comprehensive_collection():
    """Run all collection tasks"""
    try:
        logger.info("Starting comprehensive data collection")

        # Run all collections
        await _collect_google_trends()
        await asyncio.sleep(5)  # Rate limiting

        await _collect_tiktok_content()
        await asyncio.sleep(5)

        await _collect_facebook_content()
        await asyncio.sleep(5)

        # Aggregate analytics
        await _aggregate_analytics()

        logger.info("Comprehensive collection completed")

    except Exception as e:
        logger.error(f"Error in comprehensive collection: {e}")


@shared_task(name="update_hashtag_cache")
def update_hashtag_cache_task():
    """
    Update trending hashtags cache
    Runs hourly to keep hashtag discovery fresh
    """
    asyncio.run(_update_hashtag_cache())


async def _update_hashtag_cache():
    """Async implementation of hashtag cache update"""
    try:
        logger.info("Starting hashtag cache update")
        async with AsyncSessionLocal() as db:
            hashtag_service = get_hashtag_discovery_service(db)
            monitoring_service = get_monitoring_service(db)

            # Update trending hashtags cache
            cache = await hashtag_service.update_trending_cache()

            if cache and cache.get('all'):
                hashtag_count = len(cache.get('all', []))

                # Record success
                await monitoring_service.record_fetch_attempt(
                    source_type="hashtag_discovery",
                    source_name="trending_cache",
                    success=True,
                    items_collected=hashtag_count
                )

                logger.info(f"Updated hashtag cache with {hashtag_count} trending hashtags")
            else:
                # Record failure
                await monitoring_service.record_fetch_attempt(
                    source_type="hashtag_discovery",
                    source_name="trending_cache",
                    success=False,
                    error_message="No hashtags in cache"
                )

    except Exception as e:
        logger.error(f"Error updating hashtag cache: {e}")
        async with AsyncSessionLocal() as db:
            monitoring_service = get_monitoring_service(db)
            await monitoring_service.record_fetch_attempt(
                source_type="hashtag_discovery",
                source_name="trending_cache",
                success=False,
                error_message=str(e)
            )


@shared_task(name="track_hashtag_history")
def track_hashtag_history_task():
    """
    Track hashtag performance history
    Runs every 6 hours to maintain historical trending data
    """
    asyncio.run(_track_hashtag_history())


async def _track_hashtag_history():
    """Async implementation of hashtag history tracking"""
    try:
        logger.info("Starting hashtag history tracking")
        async with AsyncSessionLocal() as db:
            hashtag_service = get_hashtag_discovery_service(db)
            pipeline_service = get_data_pipeline_service(db)

            # Get current trending hashtags with engagement data
            trending_data = await hashtag_service.get_trending_from_collected_content(
                hours_back=6,
                min_occurrences=3,
                limit=100
            )

            if trending_data:
                # Store historical snapshot
                # This data can be used for trend analysis and predictions
                historical_record = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "trending_hashtags": trending_data,
                    "total_hashtags": len(trending_data)
                }

                logger.info(f"Tracked {len(trending_data)} hashtags with engagement data")

                # You can extend this to store in a separate historical_trending table
                # For now, we log the data
                top_5 = trending_data[:5]
                logger.info(f"Top 5 trending: {[h['hashtag'] for h in top_5]}")

            else:
                logger.warning("No trending hashtags found for history tracking")

    except Exception as e:
        logger.error(f"Error tracking hashtag history: {e}")
