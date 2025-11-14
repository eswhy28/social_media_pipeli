"""
Database Storage Service for Social Media Data
Handles saving data from various sources to PostgreSQL database
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
import uuid

from app.models.social_media_sources import (
    FacebookContent,
    TikTokContent,
    GoogleTrendsData,
    ApifyScrapedData,
    SocialMediaAggregation,
    DataSourceMonitoring
)
from app.models import SocialPost

logger = logging.getLogger(__name__)


class DatabaseStorageService:
    """
    Service for storing social media data in PostgreSQL
    Handles all data sources: Twitter, Facebook, TikTok, Google Trends, and Apify
    """

    def __init__(self, db: AsyncSession):
        """Initialize storage service with database session"""
        self.db = db

    async def store_facebook_posts(
        self,
        posts: List[Dict[str, Any]],
        source_name: str = "facebook"
    ) -> int:
        """
        Store Facebook posts in the database

        Args:
            posts: List of Facebook post data
            source_name: Source identifier for monitoring

        Returns:
            Number of posts stored
        """
        try:
            stored_count = 0

            for post in posts:
                try:
                    # Extract post data
                    source_id = post.get("source_id") or post.get("postId") or str(uuid.uuid4())
                    content = post.get("content", "")
                    page = post.get("page") or post.get("pageName", "")

                    # Parse posted_at timestamp
                    posted_at = None
                    if post.get("posted_at"):
                        if isinstance(post["posted_at"], str):
                            try:
                                posted_at = datetime.fromisoformat(post["posted_at"].replace('Z', '+00:00'))
                            except:
                                posted_at = datetime.utcnow()
                        else:
                            posted_at = post["posted_at"]
                    else:
                        posted_at = datetime.utcnow()

                    # Get metrics
                    metrics = post.get("metrics", {})

                    # Create Facebook content record
                    fb_content = FacebookContent(
                        id=source_id,
                        page_name=page,
                        author=post.get("author", ""),
                        text=content,
                        post_text=post.get("post_text", ""),
                        has_image=post.get("media", {}).get("has_image", False),
                        has_video=post.get("media", {}).get("has_video", False),
                        link=post.get("media", {}).get("link"),
                        post_url=post.get("url") or post.get("post_url"),
                        likes=metrics.get("likes", 0),
                        comments=metrics.get("comments", 0),
                        shares=metrics.get("shares", 0),
                        total_engagement=metrics.get("likes", 0) + metrics.get("comments", 0) + metrics.get("shares", 0),
                        engagement_score=metrics.get("engagement_score", 0.0),
                        reactions_json=metrics.get("reactions"),
                        images=post.get("media", {}).get("images", []),
                        video_url=post.get("media", {}).get("video"),
                        geo_location=post.get("geo_location", "Nigeria"),
                        posted_at=posted_at,
                        collected_at=datetime.utcnow()
                    )

                    # Use insert with on_conflict_do_update to handle duplicates
                    stmt = insert(FacebookContent).values(
                        id=fb_content.id,
                        page_name=fb_content.page_name,
                        author=fb_content.author,
                        text=fb_content.text,
                        post_text=fb_content.post_text,
                        has_image=fb_content.has_image,
                        has_video=fb_content.has_video,
                        link=fb_content.link,
                        post_url=fb_content.post_url,
                        likes=fb_content.likes,
                        comments=fb_content.comments,
                        shares=fb_content.shares,
                        total_engagement=fb_content.total_engagement,
                        engagement_score=fb_content.engagement_score,
                        reactions_json=fb_content.reactions_json,
                        images=fb_content.images,
                        video_url=fb_content.video_url,
                        geo_location=fb_content.geo_location,
                        posted_at=fb_content.posted_at,
                        collected_at=fb_content.collected_at
                    ).on_conflict_do_update(
                        index_elements=['id'],
                        set_={
                            'likes': fb_content.likes,
                            'comments': fb_content.comments,
                            'shares': fb_content.shares,
                            'total_engagement': fb_content.total_engagement,
                            'collected_at': fb_content.collected_at
                        }
                    )

                    await self.db.execute(stmt)
                    stored_count += 1

                except Exception as e:
                    logger.error(f"Error storing Facebook post {post.get('source_id')}: {e}")
                    continue

            # Commit all posts
            await self.db.commit()
            logger.info(f"Stored {stored_count} Facebook posts")

            # Update monitoring status
            await self._update_monitoring_status(
                source_type="facebook",
                source_name=source_name,
                items_collected=stored_count
            )

            return stored_count

        except Exception as e:
            logger.error(f"Error in store_facebook_posts: {e}")
            await self.db.rollback()
            return 0

    async def store_tiktok_videos(
        self,
        videos: List[Dict[str, Any]],
        source_name: str = "tiktok"
    ) -> int:
        """
        Store TikTok videos in the database

        Args:
            videos: List of TikTok video data
            source_name: Source identifier for monitoring

        Returns:
            Number of videos stored
        """
        try:
            stored_count = 0

            for video in videos:
                try:
                    # Extract video data
                    video_id = video.get("video_id") or video.get("source_id") or str(uuid.uuid4())
                    author = video.get("author", {})
                    content = video.get("content", {})
                    metrics = video.get("metrics", {})

                    # Parse posted_at timestamp
                    posted_at = None
                    if video.get("created_at") or video.get("posted_at"):
                        timestamp = video.get("created_at") or video.get("posted_at")
                        if isinstance(timestamp, str):
                            try:
                                posted_at = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                            except:
                                posted_at = datetime.utcnow()
                        else:
                            posted_at = timestamp
                    else:
                        posted_at = datetime.utcnow()

                    # Calculate engagement rate
                    views = metrics.get("views", 0)
                    engagement = metrics.get("likes", 0) + metrics.get("comments", 0) + metrics.get("shares", 0)
                    engagement_rate = (engagement / views * 100) if views > 0 else 0.0

                    # Create TikTok content record
                    tiktok_content = TikTokContent(
                        id=video_id,
                        author_username=author.get("username") if isinstance(author, dict) else video.get("author"),
                        author_nickname=author.get("nickname", ""),
                        author_verified=author.get("verified", False),
                        author_follower_count=author.get("follower_count", 0),
                        description=content.get("description") if isinstance(content, dict) else video.get("content", ""),
                        duration=content.get("duration", 0),
                        music_title=content.get("music", ""),
                        views=views,
                        likes=metrics.get("likes", 0),
                        comments=metrics.get("comments", 0),
                        shares=metrics.get("shares", 0),
                        engagement_rate=engagement_rate,
                        hashtags=video.get("hashtags", []),
                        geo_location=video.get("geo_location", "Nigeria"),
                        posted_at=posted_at,
                        collected_at=datetime.utcnow()
                    )

                    # Use insert with on_conflict_do_update
                    stmt = insert(TikTokContent).values(
                        id=tiktok_content.id,
                        author_username=tiktok_content.author_username,
                        author_nickname=tiktok_content.author_nickname,
                        author_verified=tiktok_content.author_verified,
                        author_follower_count=tiktok_content.author_follower_count,
                        description=tiktok_content.description,
                        duration=tiktok_content.duration,
                        music_title=tiktok_content.music_title,
                        views=tiktok_content.views,
                        likes=tiktok_content.likes,
                        comments=tiktok_content.comments,
                        shares=tiktok_content.shares,
                        engagement_rate=tiktok_content.engagement_rate,
                        hashtags=tiktok_content.hashtags,
                        geo_location=tiktok_content.geo_location,
                        posted_at=tiktok_content.posted_at,
                        collected_at=tiktok_content.collected_at
                    ).on_conflict_do_update(
                        index_elements=['id'],
                        set_={
                            'views': tiktok_content.views,
                            'likes': tiktok_content.likes,
                            'comments': tiktok_content.comments,
                            'shares': tiktok_content.shares,
                            'engagement_rate': tiktok_content.engagement_rate,
                            'collected_at': tiktok_content.collected_at
                        }
                    )

                    await self.db.execute(stmt)
                    stored_count += 1

                except Exception as e:
                    logger.error(f"Error storing TikTok video {video.get('video_id')}: {e}")
                    continue

            # Commit all videos
            await self.db.commit()
            logger.info(f"Stored {stored_count} TikTok videos")

            # Update monitoring status
            await self._update_monitoring_status(
                source_type="tiktok",
                source_name=source_name,
                items_collected=stored_count
            )

            return stored_count

        except Exception as e:
            logger.error(f"Error in store_tiktok_videos: {e}")
            await self.db.rollback()
            return 0

    async def store_google_trends(
        self,
        trends_data: List[Dict[str, Any]],
        trend_type: str = "trending_search",
        source_name: str = "google_trends"
    ) -> int:
        """
        Store Google Trends data in the database

        Args:
            trends_data: List of trends data
            trend_type: Type of trend data (trending_search, interest_over_time, etc.)
            source_name: Source identifier for monitoring

        Returns:
            Number of trends stored
        """
        try:
            stored_count = 0

            for trend in trends_data:
                try:
                    # Extract trend data
                    keyword = trend.get("term") or trend.get("keyword", "")

                    if not keyword:
                        continue

                    # Parse trend date
                    trend_date = None
                    if trend.get("date"):
                        if isinstance(trend["date"], str):
                            try:
                                trend_date = datetime.fromisoformat(trend["date"].replace('Z', '+00:00'))
                            except:
                                trend_date = datetime.utcnow()
                        else:
                            trend_date = trend["date"]
                    else:
                        trend_date = datetime.utcnow()

                    # Create Google Trends record
                    trends_record = GoogleTrendsData(
                        id=str(uuid.uuid4()),
                        keyword=keyword,
                        trend_type=trend_type,
                        data_json=trend,
                        interest_value=trend.get("interest") or trend.get("value", 0),
                        rank=trend.get("rank"),
                        geo_region=trend.get("region", "NG"),
                        sub_region=trend.get("sub_region"),
                        timeframe=trend.get("timeframe", "today"),
                        trend_date=trend_date,
                        collected_at=datetime.utcnow()
                    )

                    self.db.add(trends_record)
                    stored_count += 1

                except Exception as e:
                    logger.error(f"Error storing Google trend {trend.get('term')}: {e}")
                    continue

            # Commit all trends
            await self.db.commit()
            logger.info(f"Stored {stored_count} Google Trends records")

            # Update monitoring status
            await self._update_monitoring_status(
                source_type="google_trends",
                source_name=source_name,
                items_collected=stored_count
            )

            return stored_count

        except Exception as e:
            logger.error(f"Error in store_google_trends: {e}")
            await self.db.rollback()
            return 0

    async def store_twitter_posts(
        self,
        tweets: List[Dict[str, Any]],
        source_name: str = "twitter"
    ) -> int:
        """
        Store Twitter posts in the database using Apify data format

        Args:
            tweets: List of tweet data
            source_name: Source identifier for monitoring

        Returns:
            Number of tweets stored
        """
        try:
            stored_count = 0

            for tweet in tweets:
                try:
                    # Extract tweet data
                    tweet_id = tweet.get("source_id") or tweet.get("id") or str(uuid.uuid4())
                    content = tweet.get("content") or tweet.get("text", "")
                    author = tweet.get("author") or ""

                    # Parse posted_at timestamp
                    posted_at = None
                    if tweet.get("posted_at") or tweet.get("created_at"):
                        timestamp = tweet.get("posted_at") or tweet.get("created_at")
                        if isinstance(timestamp, str):
                            try:
                                posted_at = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                            except:
                                posted_at = datetime.utcnow()
                        else:
                            posted_at = timestamp
                    else:
                        posted_at = datetime.utcnow()

                    # Get metrics
                    metrics = tweet.get("metrics", {})

                    # Create Apify scraped data record for Twitter
                    apify_data = ApifyScrapedData(
                        id=str(uuid.uuid4()),
                        platform="twitter",
                        source_id=tweet_id,
                        author=author,
                        content=content,
                        content_type="tweet",
                        metrics_json=metrics,
                        hashtags=tweet.get("hashtags", []),
                        mentions=tweet.get("mentions", []),
                        raw_data=tweet,
                        geo_location=tweet.get("geo_location", "Nigeria"),
                        posted_at=posted_at,
                        collected_at=datetime.utcnow()
                    )

                    self.db.add(apify_data)
                    stored_count += 1

                except Exception as e:
                    logger.error(f"Error storing Twitter post {tweet.get('id')}: {e}")
                    continue

            # Commit all tweets
            await self.db.commit()
            logger.info(f"Stored {stored_count} Twitter posts")

            # Update monitoring status
            await self._update_monitoring_status(
                source_type="twitter",
                source_name=source_name,
                items_collected=stored_count
            )

            return stored_count

        except Exception as e:
            logger.error(f"Error in store_twitter_posts: {e}")
            await self.db.rollback()
            return 0

    async def _update_monitoring_status(
        self,
        source_type: str,
        source_name: str,
        items_collected: int,
        error_message: Optional[str] = None
    ):
        """
        Update data source monitoring status

        Args:
            source_type: Type of data source
            source_name: Name of the source
            items_collected: Number of items collected
            error_message: Error message if any
        """
        try:
            # Find existing monitoring record
            result = await self.db.execute(
                select(DataSourceMonitoring).where(
                    DataSourceMonitoring.source_type == source_type,
                    DataSourceMonitoring.source_name == source_name
                )
            )
            monitoring = result.scalar_one_or_none()

            if monitoring:
                # Update existing record
                monitoring.last_attempt = datetime.utcnow()
                if items_collected > 0:
                    monitoring.last_successful_fetch = datetime.utcnow()
                    monitoring.total_items_collected += items_collected
                    monitoring.items_collected_today += items_collected
                    monitoring.consecutive_failures = 0
                    monitoring.status = "active"
                else:
                    monitoring.consecutive_failures += 1
                    if monitoring.consecutive_failures >= 3:
                        monitoring.status = "failed"

                if error_message:
                    monitoring.last_error = error_message
                    monitoring.error_count += 1
            else:
                # Create new monitoring record
                monitoring = DataSourceMonitoring(
                    source_type=source_type,
                    source_name=source_name,
                    status="active" if items_collected > 0 else "failed",
                    last_successful_fetch=datetime.utcnow() if items_collected > 0 else None,
                    last_attempt=datetime.utcnow(),
                    total_items_collected=items_collected,
                    items_collected_today=items_collected,
                    consecutive_failures=0 if items_collected > 0 else 1,
                    last_error=error_message,
                    error_count=1 if error_message else 0
                )
                self.db.add(monitoring)

            await self.db.commit()

        except Exception as e:
            logger.error(f"Error updating monitoring status: {e}")
            await self.db.rollback()

    async def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about data collection

        Returns:
            Dictionary with collection statistics
        """
        try:
            # Get stats from monitoring table
            result = await self.db.execute(select(DataSourceMonitoring))
            monitoring_records = result.scalars().all()

            stats = {
                "total_sources": len(monitoring_records),
                "active_sources": sum(1 for m in monitoring_records if m.status == "active"),
                "failed_sources": sum(1 for m in monitoring_records if m.status == "failed"),
                "total_items_collected": sum(m.total_items_collected for m in monitoring_records),
                "items_collected_today": sum(m.items_collected_today for m in monitoring_records),
                "sources": [
                    {
                        "source_type": m.source_type,
                        "source_name": m.source_name,
                        "status": m.status,
                        "last_successful_fetch": m.last_successful_fetch.isoformat() if m.last_successful_fetch else None,
                        "total_items": m.total_items_collected,
                        "items_today": m.items_collected_today
                    }
                    for m in monitoring_records
                ]
            }

            return stats

        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {}


# Factory function for dependency injection
def get_storage_service(db: AsyncSession) -> DatabaseStorageService:
    """Get storage service instance with database session"""
    return DatabaseStorageService(db)