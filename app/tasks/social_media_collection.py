"""
Background Tasks for Automated Social Media Data Collection
"""

import logging
from datetime import datetime
from celery import shared_task
from sqlalchemy.ext.asyncio import AsyncSession
import asyncio

from app.database import async_session_maker
from app.services.google_trends_service import get_google_trends_service
from app.services.tiktok_service import get_tiktok_service
from app.services.facebook_service import get_facebook_service
from app.services.data_pipeline_service import get_data_pipeline_service
from app.services.monitoring_service import get_monitoring_service
from app.services.cross_platform_analytics import get_cross_platform_analytics

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
        async with async_session_maker() as db:
            trends_service = get_google_trends_service()
            pipeline_service = get_data_pipeline_service(db)
            monitoring_service = get_monitoring_service(db)

            # Get trending searches
            trending = await trends_service.get_trending_searches("NG")

            if trending:
                # Store data
                stored = await pipeline_service.store_google_trends(trending)

                # Record success
                await monitoring_service.record_fetch_attempt(
                    source_type="google_trends",
                    source_name="trending_ng",
                    success=True,
                    items_collected=stored
                )

                logger.info(f"Collected {stored} Google Trends items")
            else:
                # Record failure
                await monitoring_service.record_fetch_attempt(
                    source_type="google_trends",
                    source_name="trending_ng",
                    success=False,
                    error_message="No trends returned"
                )

    except Exception as e:
        logger.error(f"Error in Google Trends collection: {e}")
        async with async_session_maker() as db:
            monitoring_service = get_monitoring_service(db)
            await monitoring_service.record_fetch_attempt(
                source_type="google_trends",
                source_name="trending_ng",
                success=False,
                error_message=str(e)
            )


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
        async with async_session_maker() as db:
            tiktok_service = get_tiktok_service()
            pipeline_service = get_data_pipeline_service(db)
            monitoring_service = get_monitoring_service(db)

            # Monitor Nigerian content
            result = await tiktok_service.monitor_nigerian_content(
                max_videos_per_hashtag=20
            )

            if result.get('videos'):
                # Store data
                stored = await pipeline_service.store_tiktok_content(result['videos'])

                # Record success
                await monitoring_service.record_fetch_attempt(
                    source_type="tiktok",
                    source_name="nigerian_hashtags",
                    success=True,
                    items_collected=stored
                )

                logger.info(f"Collected {stored} TikTok videos")
            else:
                # Record failure
                await monitoring_service.record_fetch_attempt(
                    source_type="tiktok",
                    source_name="nigerian_hashtags",
                    success=False,
                    error_message=result.get('error', 'No videos returned')
                )

    except Exception as e:
        logger.error(f"Error in TikTok collection: {e}")
        async with async_session_maker() as db:
            monitoring_service = get_monitoring_service(db)
            await monitoring_service.record_fetch_attempt(
                source_type="tiktok",
                source_name="nigerian_hashtags",
                success=False,
                error_message=str(e)
            )


@shared_task(name="collect_facebook_content")
def collect_facebook_content_task():
    """
    Collect Facebook content from Nigerian pages
    """
    asyncio.run(_collect_facebook_content())


async def _collect_facebook_content():
    """Async implementation of Facebook collection"""
    try:
        logger.info("Starting Facebook collection")
        async with async_session_maker() as db:
            facebook_service = get_facebook_service()
            pipeline_service = get_data_pipeline_service(db)
            monitoring_service = get_monitoring_service(db)

            # Monitor Nigerian pages
            result = await facebook_service.monitor_nigerian_pages(
                pages_per_source=2
            )

            if result.get('posts'):
                # Store data
                stored = await pipeline_service.store_facebook_content(result['posts'])

                # Record success
                await monitoring_service.record_fetch_attempt(
                    source_type="facebook",
                    source_name="nigerian_pages",
                    success=True,
                    items_collected=stored
                )

                logger.info(f"Collected {stored} Facebook posts")
            else:
                # Record failure
                await monitoring_service.record_fetch_attempt(
                    source_type="facebook",
                    source_name="nigerian_pages",
                    success=False,
                    error_message=result.get('error', 'No posts returned')
                )

    except Exception as e:
        logger.error(f"Error in Facebook collection: {e}")
        async with async_session_maker() as db:
            monitoring_service = get_monitoring_service(db)
            await monitoring_service.record_fetch_attempt(
                source_type="facebook",
                source_name="nigerian_pages",
                success=False,
                error_message=str(e)
            )


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
        async with async_session_maker() as db:
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
        async with async_session_maker() as db:
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
