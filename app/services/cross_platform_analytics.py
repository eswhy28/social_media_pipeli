"""
Cross-Platform Analytics Service
Provides unified analytics across all social media sources
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc
from collections import Counter

from app.models.social_media_sources import (
    GoogleTrendsData,
    TikTokContent,
    FacebookContent,
    ApifyScrapedData,
    SocialMediaAggregation
)

logger = logging.getLogger(__name__)


class CrossPlatformAnalyticsService:
    """
    Service for analyzing data across multiple social media platforms
    Provides unified metrics and trend correlation
    """

    def __init__(self, db: AsyncSession):
        """Initialize the analytics service"""
        self.db = db

    async def get_cross_platform_summary(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get summary metrics across all platforms

        Args:
            start_date: Start date for analysis
            end_date: End date for analysis

        Returns:
            Summary metrics
        """
        try:
            if not start_date:
                start_date = datetime.utcnow() - timedelta(days=7)
            if not end_date:
                end_date = datetime.utcnow()

            summary = {
                "period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                },
                "platforms": {}
            }

            # Google Trends metrics
            trends_result = await self.db.execute(
                select(func.count(GoogleTrendsData.id))
                .where(and_(
                    GoogleTrendsData.collected_at >= start_date,
                    GoogleTrendsData.collected_at <= end_date
                ))
            )
            summary["platforms"]["google_trends"] = {
                "total_trends": trends_result.scalar() or 0
            }

            # TikTok metrics
            tiktok_result = await self.db.execute(
                select(
                    func.count(TikTokContent.id),
                    func.sum(TikTokContent.views),
                    func.sum(TikTokContent.likes),
                    func.sum(TikTokContent.comments),
                    func.avg(TikTokContent.engagement_rate)
                ).where(and_(
                    TikTokContent.collected_at >= start_date,
                    TikTokContent.collected_at <= end_date
                ))
            )
            tiktok_metrics = tiktok_result.first()
            summary["platforms"]["tiktok"] = {
                "total_videos": tiktok_metrics[0] or 0,
                "total_views": tiktok_metrics[1] or 0,
                "total_likes": tiktok_metrics[2] or 0,
                "total_comments": tiktok_metrics[3] or 0,
                "avg_engagement_rate": float(tiktok_metrics[4] or 0)
            }

            # Facebook metrics
            facebook_result = await self.db.execute(
                select(
                    func.count(FacebookContent.id),
                    func.sum(FacebookContent.likes),
                    func.sum(FacebookContent.comments),
                    func.sum(FacebookContent.shares),
                    func.sum(FacebookContent.total_engagement)
                ).where(and_(
                    FacebookContent.collected_at >= start_date,
                    FacebookContent.collected_at <= end_date
                ))
            )
            facebook_metrics = facebook_result.first()
            summary["platforms"]["facebook"] = {
                "total_posts": facebook_metrics[0] or 0,
                "total_likes": facebook_metrics[1] or 0,
                "total_comments": facebook_metrics[2] or 0,
                "total_shares": facebook_metrics[3] or 0,
                "total_engagement": facebook_metrics[4] or 0
            }

            # Apify metrics
            apify_result = await self.db.execute(
                select(
                    func.count(ApifyScrapedData.id),
                    ApifyScrapedData.platform
                )
                .where(and_(
                    ApifyScrapedData.collected_at >= start_date,
                    ApifyScrapedData.collected_at <= end_date
                ))
                .group_by(ApifyScrapedData.platform)
            )
            apify_metrics = apify_result.all()
            summary["platforms"]["apify"] = {
                platform: count for count, platform in apify_metrics
            }

            # Calculate totals
            summary["totals"] = {
                "total_content_items": (
                    summary["platforms"]["google_trends"]["total_trends"] +
                    summary["platforms"]["tiktok"]["total_videos"] +
                    summary["platforms"]["facebook"]["total_posts"] +
                    sum(summary["platforms"]["apify"].values())
                ),
                "total_engagement": (
                    summary["platforms"]["tiktok"]["total_likes"] +
                    summary["platforms"]["facebook"]["total_engagement"]
                )
            }

            return summary

        except Exception as e:
            logger.error(f"Error getting cross-platform summary: {e}")
            return {"error": str(e)}

    async def get_trending_hashtags(
        self,
        limit: int = 20,
        days: int = 7
    ) -> List[Dict[str, Any]]:
        """
        Get trending hashtags across all platforms

        Args:
            limit: Number of hashtags to return
            days: Number of days to analyze

        Returns:
            List of trending hashtags with metrics
        """
        try:
            start_date = datetime.utcnow() - timedelta(days=days)

            all_hashtags = []

            # TikTok hashtags
            tiktok_result = await self.db.execute(
                select(TikTokContent.hashtags, TikTokContent.likes, TikTokContent.views)
                .where(TikTokContent.collected_at >= start_date)
            )
            for row in tiktok_result.all():
                if row[0]:  # hashtags
                    for tag in row[0]:
                        all_hashtags.append({
                            "hashtag": tag,
                            "platform": "tiktok",
                            "likes": row[1] or 0,
                            "views": row[2] or 0
                        })

            # Facebook hashtags (extracted from post text)
            # Note: Facebook posts don't have structured hashtag data

            # Apify hashtags
            apify_result = await self.db.execute(
                select(ApifyScrapedData.hashtags, ApifyScrapedData.metrics_json, ApifyScrapedData.platform)
                .where(ApifyScrapedData.collected_at >= start_date)
            )
            for row in apify_result.all():
                if row[0]:  # hashtags
                    metrics = row[1] or {}
                    for tag in row[0]:
                        all_hashtags.append({
                            "hashtag": tag,
                            "platform": row[2],
                            "likes": metrics.get("likes", 0),
                            "views": metrics.get("views", 0)
                        })

            # Aggregate hashtags
            hashtag_stats = {}
            for item in all_hashtags:
                tag = item["hashtag"].lower()
                if tag not in hashtag_stats:
                    hashtag_stats[tag] = {
                        "hashtag": tag,
                        "count": 0,
                        "total_likes": 0,
                        "total_views": 0,
                        "platforms": set()
                    }

                hashtag_stats[tag]["count"] += 1
                hashtag_stats[tag]["total_likes"] += item["likes"]
                hashtag_stats[tag]["total_views"] += item["views"]
                hashtag_stats[tag]["platforms"].add(item["platform"])

            # Convert to list and sort
            trending = [
                {
                    "hashtag": stats["hashtag"],
                    "count": stats["count"],
                    "total_likes": stats["total_likes"],
                    "total_views": stats["total_views"],
                    "platforms": list(stats["platforms"]),
                    "score": stats["count"] * 10 + stats["total_likes"] / 100
                }
                for stats in hashtag_stats.values()
            ]

            trending.sort(key=lambda x: x["score"], reverse=True)

            return trending[:limit]

        except Exception as e:
            logger.error(f"Error getting trending hashtags: {e}")
            return []

    async def get_top_content(
        self,
        platform: Optional[str] = None,
        limit: int = 10,
        days: int = 7
    ) -> List[Dict[str, Any]]:
        """
        Get top content by engagement across platforms

        Args:
            platform: Specific platform or None for all
            limit: Number of items to return
            days: Number of days to analyze

        Returns:
            List of top content items
        """
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            top_content = []

            if not platform or platform == "tiktok":
                # TikTok top videos
                tiktok_result = await self.db.execute(
                    select(TikTokContent)
                    .where(TikTokContent.collected_at >= start_date)
                    .order_by(desc(TikTokContent.likes))
                    .limit(limit)
                )
                for video in tiktok_result.scalars():
                    top_content.append({
                        "platform": "tiktok",
                        "content_id": video.id,
                        "author": video.author_username,
                        "description": video.description[:100],
                        "likes": video.likes,
                        "views": video.views,
                        "engagement_rate": video.engagement_rate,
                        "posted_at": video.posted_at.isoformat() if video.posted_at else None
                    })

            if not platform or platform == "facebook":
                # Facebook top posts
                facebook_result = await self.db.execute(
                    select(FacebookContent)
                    .where(FacebookContent.collected_at >= start_date)
                    .order_by(desc(FacebookContent.total_engagement))
                    .limit(limit)
                )
                for post in facebook_result.scalars():
                    top_content.append({
                        "platform": "facebook",
                        "content_id": post.id,
                        "page": post.page_name,
                        "text": post.text[:100] if post.text else "",
                        "likes": post.likes,
                        "comments": post.comments,
                        "shares": post.shares,
                        "total_engagement": post.total_engagement,
                        "posted_at": post.posted_at.isoformat() if post.posted_at else None
                    })

            # Sort by engagement
            if top_content:
                top_content.sort(
                    key=lambda x: x.get("total_engagement") or x.get("likes", 0),
                    reverse=True
                )

            return top_content[:limit]

        except Exception as e:
            logger.error(f"Error getting top content: {e}")
            return []

    async def get_platform_comparison(
        self,
        days: int = 7
    ) -> Dict[str, Any]:
        """
        Compare metrics across platforms

        Args:
            days: Number of days to analyze

        Returns:
            Platform comparison data
        """
        try:
            start_date = datetime.utcnow() - timedelta(days=days)

            comparison = {
                "period_days": days,
                "platforms": [],
                "timestamp": datetime.utcnow().isoformat()
            }

            # TikTok metrics
            tiktok_result = await self.db.execute(
                select(
                    func.count(TikTokContent.id),
                    func.avg(TikTokContent.engagement_rate),
                    func.sum(TikTokContent.views)
                ).where(TikTokContent.collected_at >= start_date)
            )
            tiktok_metrics = tiktok_result.first()
            comparison["platforms"].append({
                "name": "tiktok",
                "content_count": tiktok_metrics[0] or 0,
                "avg_engagement_rate": float(tiktok_metrics[1] or 0),
                "total_views": tiktok_metrics[2] or 0
            })

            # Facebook metrics
            facebook_result = await self.db.execute(
                select(
                    func.count(FacebookContent.id),
                    func.avg(FacebookContent.engagement_score),
                    func.sum(FacebookContent.total_engagement)
                ).where(FacebookContent.collected_at >= start_date)
            )
            facebook_metrics = facebook_result.first()
            comparison["platforms"].append({
                "name": "facebook",
                "content_count": facebook_metrics[0] or 0,
                "avg_engagement_score": float(facebook_metrics[1] or 0),
                "total_engagement": facebook_metrics[2] or 0
            })

            # Google Trends metrics
            trends_result = await self.db.execute(
                select(
                    func.count(GoogleTrendsData.id),
                    func.avg(GoogleTrendsData.interest_value)
                ).where(GoogleTrendsData.collected_at >= start_date)
            )
            trends_metrics = trends_result.first()
            comparison["platforms"].append({
                "name": "google_trends",
                "content_count": trends_metrics[0] or 0,
                "avg_interest_value": float(trends_metrics[1] or 0)
            })

            return comparison

        except Exception as e:
            logger.error(f"Error getting platform comparison: {e}")
            return {"error": str(e)}

    async def aggregate_hourly_data(
        self,
        timestamp: datetime
    ) -> bool:
        """
        Aggregate data for a specific hour

        Args:
            timestamp: Hour to aggregate

        Returns:
            True if successful
        """
        try:
            hour_start = timestamp.replace(minute=0, second=0, microsecond=0)
            hour_end = hour_start + timedelta(hours=1)

            # Aggregate for each platform
            platforms = ["tiktok", "facebook", "google_trends", "apify"]

            for platform in platforms:
                if platform == "tiktok":
                    result = await self.db.execute(
                        select(
                            func.count(TikTokContent.id),
                            func.sum(TikTokContent.views),
                            func.sum(TikTokContent.likes),
                            func.sum(TikTokContent.comments),
                            func.avg(TikTokContent.engagement_rate)
                        ).where(and_(
                            TikTokContent.collected_at >= hour_start,
                            TikTokContent.collected_at < hour_end
                        ))
                    )
                    metrics = result.first()

                    if metrics[0]:  # If there's data
                        aggregation = SocialMediaAggregation(
                            timestamp=hour_start,
                            granularity="hour",
                            platform=platform,
                            total_posts=0,
                            total_videos=metrics[0],
                            total_views=metrics[1] or 0,
                            total_likes=metrics[2] or 0,
                            total_comments=metrics[3] or 0,
                            avg_engagement_rate=float(metrics[4] or 0),
                            geo_region="Nigeria"
                        )
                        self.db.add(aggregation)

                elif platform == "facebook":
                    result = await self.db.execute(
                        select(
                            func.count(FacebookContent.id),
                            func.sum(FacebookContent.likes),
                            func.sum(FacebookContent.comments),
                            func.sum(FacebookContent.shares),
                            func.avg(FacebookContent.engagement_score)
                        ).where(and_(
                            FacebookContent.collected_at >= hour_start,
                            FacebookContent.collected_at < hour_end
                        ))
                    )
                    metrics = result.first()

                    if metrics[0]:
                        aggregation = SocialMediaAggregation(
                            timestamp=hour_start,
                            granularity="hour",
                            platform=platform,
                            total_posts=metrics[0],
                            total_likes=metrics[1] or 0,
                            total_comments=metrics[2] or 0,
                            total_shares=metrics[3] or 0,
                            avg_engagement_rate=float(metrics[4] or 0),
                            geo_region="Nigeria"
                        )
                        self.db.add(aggregation)

            await self.db.commit()
            logger.info(f"Aggregated data for {hour_start}")
            return True

        except Exception as e:
            logger.error(f"Error aggregating hourly data: {e}")
            await self.db.rollback()
            return False


# Singleton instance
def get_cross_platform_analytics(db: AsyncSession) -> CrossPlatformAnalyticsService:
    """Get cross-platform analytics service instance"""
    return CrossPlatformAnalyticsService(db)
