"""
TikTok Service for Nigerian Social Media Analysis
Scrapes TikTok content, trends, and engagement metrics focused on Nigeria
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import asyncio
from TikTokApi import TikTokApi
import json
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config import settings

logger = logging.getLogger(__name__)


class TikTokService:
    """
    Service for fetching TikTok data with focus on Nigerian content
    Uses TikTok-Api for scraping trending hashtags, videos, and user content
    """

    def __init__(self):
        """Initialize TikTok service"""
        self.api_key = settings.TIKTOK_API_KEY
        self.api_secret = settings.TIKTOK_API_SECRET
        self.access_token = settings.TIKTOK_ACCESS_TOKEN

        # Nigerian popular hashtags to monitor
        self.nigerian_hashtags = [
            "nigeria", "naija", "lagos", "abuja", "nigerian",
            "nigerianmusic", "nigerianwedding", "nigerianfood",
            "lagosnigeria", "9ja", "naijabrandchick", "naijatrends",
            "nigeriantiktok", "nigeriatrends", "hustlersquare"
        ]

        # Rate limiting
        self.request_delay = 2  # seconds between requests
        self.last_request_time = None

        logger.info("TikTok Service initialized")

    async def _rate_limit(self):
        """Implement rate limiting between requests"""
        if self.last_request_time:
            elapsed = (datetime.utcnow() - self.last_request_time).total_seconds()
            if elapsed < self.request_delay:
                await asyncio.sleep(self.request_delay - elapsed)
        self.last_request_time = datetime.utcnow()

    async def _get_api_instance(self) -> TikTokApi:
        """
        Create and configure TikTok API instance

        Returns:
            Configured TikTokApi instance
        """
        try:
            # Create API instance with supported parameters only
            api = TikTokApi(
                logging_level=logging.WARNING
            )

            return api

        except Exception as e:
            logger.error(f"Error creating TikTok API instance: {e}")
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=20)
    )
    async def search_hashtag(
        self,
        hashtag: str,
        count: int = 30,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Search for videos by hashtag

        Args:
            hashtag: Hashtag to search (without #)
            count: Number of videos to fetch (default: 30)
            offset: Offset for pagination

        Returns:
            List of video data dictionaries
        """
        try:
            logger.info(f"Searching TikTok hashtag: #{hashtag}")
            await self._rate_limit()

            videos = []
            api = await self._get_api_instance()

            # Create async context
            async with api:
                # Search by hashtag
                hashtag_obj = api.hashtag(name=hashtag)

                async for video in hashtag_obj.videos(count=count):
                    try:
                        video_data = await self._extract_video_data(video)
                        videos.append(video_data)
                    except Exception as e:
                        logger.warning(f"Error extracting video data: {e}")
                        continue

            logger.info(f"Retrieved {len(videos)} videos for #{hashtag}")
            return videos

        except Exception as e:
            logger.error(f"Error searching hashtag #{hashtag}: {e}")
            return []

    async def _extract_video_data(self, video) -> Dict[str, Any]:
        """
        Extract relevant data from TikTok video object

        Args:
            video: TikTok video object

        Returns:
            Structured video data dictionary
        """
        try:
            video_dict = video.as_dict

            return {
                "video_id": video_dict.get("id"),
                "author": {
                    "username": video_dict.get("author", {}).get("uniqueId"),
                    "nickname": video_dict.get("author", {}).get("nickname"),
                    "verified": video_dict.get("author", {}).get("verified", False),
                    "follower_count": video_dict.get("authorStats", {}).get("followerCount", 0)
                },
                "content": {
                    "description": video_dict.get("desc", ""),
                    "duration": video_dict.get("video", {}).get("duration", 0),
                    "music": video_dict.get("music", {}).get("title", "")
                },
                "metrics": {
                    "views": video_dict.get("stats", {}).get("playCount", 0),
                    "likes": video_dict.get("stats", {}).get("diggCount", 0),
                    "comments": video_dict.get("stats", {}).get("commentCount", 0),
                    "shares": video_dict.get("stats", {}).get("shareCount", 0)
                },
                "hashtags": [
                    tag.get("title", "") for tag in video_dict.get("challenges", [])
                ],
                "created_at": datetime.fromtimestamp(
                    video_dict.get("createTime", 0)
                ).isoformat(),
                "collected_at": datetime.utcnow().isoformat(),
                "source": "tiktok",
                "geo_location": "Nigeria"  # Inferred from hashtag search
            }

        except Exception as e:
            logger.error(f"Error extracting video data: {e}")
            return {}

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=20)
    )
    async def get_trending_hashtags(
        self,
        region: str = "NG",
        count: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get trending hashtags (uses predefined Nigerian hashtags)

        Args:
            region: Region code (NG for Nigeria)
            count: Number of hashtags to analyze

        Returns:
            List of trending hashtag data
        """
        try:
            logger.info(f"Fetching trending hashtags for {region}")

            trending_data = []

            # Analyze popular Nigerian hashtags
            for hashtag in self.nigerian_hashtags[:count]:
                try:
                    await self._rate_limit()

                    api = await self._get_api_instance()
                    async with api:
                        hashtag_obj = api.hashtag(name=hashtag)

                        # Get hashtag info (videos count would require iteration)
                        # For now, we'll collect basic info
                        trending_data.append({
                            "hashtag": hashtag,
                            "name": f"#{hashtag}",
                            "region": region,
                            "timestamp": datetime.utcnow().isoformat(),
                            "source": "tiktok"
                        })

                except Exception as e:
                    logger.warning(f"Error fetching hashtag {hashtag}: {e}")
                    continue

            logger.info(f"Retrieved {len(trending_data)} trending hashtags")
            return trending_data

        except Exception as e:
            logger.error(f"Error fetching trending hashtags: {e}")
            return []

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=20)
    )
    async def get_user_videos(
        self,
        username: str,
        count: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Get videos from a specific user

        Args:
            username: TikTok username
            count: Number of videos to fetch

        Returns:
            List of video data
        """
        try:
            logger.info(f"Fetching videos for user: {username}")
            await self._rate_limit()

            videos = []
            api = await self._get_api_instance()

            async with api:
                user = api.user(username=username)

                async for video in user.videos(count=count):
                    try:
                        video_data = await self._extract_video_data(video)
                        videos.append(video_data)
                    except Exception as e:
                        logger.warning(f"Error extracting video data: {e}")
                        continue

            logger.info(f"Retrieved {len(videos)} videos for user {username}")
            return videos

        except Exception as e:
            logger.error(f"Error fetching user videos: {e}")
            return []

    async def monitor_nigerian_content(
        self,
        max_videos_per_hashtag: int = 20,
        hashtags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Monitor Nigerian TikTok content across popular hashtags

        Args:
            max_videos_per_hashtag: Maximum videos to fetch per hashtag
            hashtags: Optional list of hashtags to monitor (if None, uses default Nigerian hashtags)

        Returns:
            Aggregated content data from Nigerian hashtags
        """
        try:
            logger.info("Starting Nigerian content monitoring")

            # Use provided hashtags or default Nigerian hashtags
            hashtags_to_monitor = hashtags if hashtags is not None else self.nigerian_hashtags

            all_videos = []
            hashtag_stats = []

            for hashtag in hashtags_to_monitor:
                try:
                    # Fetch videos for each hashtag
                    videos = await self.search_hashtag(
                        hashtag=hashtag,
                        count=max_videos_per_hashtag
                    )

                    all_videos.extend(videos)

                    # Calculate hashtag stats
                    if videos:
                        total_views = sum(v.get("metrics", {}).get("views", 0) for v in videos)
                        total_likes = sum(v.get("metrics", {}).get("likes", 0) for v in videos)

                        hashtag_stats.append({
                            "hashtag": hashtag,
                            "video_count": len(videos),
                            "total_views": total_views,
                            "total_likes": total_likes,
                            "avg_engagement": (total_likes / total_views * 100) if total_views > 0 else 0
                        })

                    # Rate limiting between hashtags
                    await asyncio.sleep(3)

                except Exception as e:
                    logger.error(f"Error monitoring hashtag {hashtag}: {e}")
                    continue

            result = {
                "videos": all_videos,
                "hashtag_stats": hashtag_stats,
                "total_videos": len(all_videos),
                "monitored_hashtags": len(hashtag_stats),
                "timestamp": datetime.utcnow().isoformat(),
                "region": "Nigeria"
            }

            logger.info(f"Monitoring complete: {len(all_videos)} videos from "
                       f"{len(hashtag_stats)} hashtags")
            return result

        except Exception as e:
            logger.error(f"Error in Nigerian content monitoring: {e}")
            return {
                "videos": [],
                "hashtag_stats": [],
                "error": str(e)
            }

    def calculate_engagement_rate(self, video_data: Dict[str, Any]) -> float:
        """
        Calculate engagement rate for a video

        Args:
            video_data: Video data dictionary

        Returns:
            Engagement rate as percentage
        """
        try:
            metrics = video_data.get("metrics", {})
            views = metrics.get("views", 0)

            if views == 0:
                return 0.0

            engagement = (
                metrics.get("likes", 0) +
                metrics.get("comments", 0) +
                metrics.get("shares", 0)
            )

            return (engagement / views) * 100

        except Exception as e:
            logger.error(f"Error calculating engagement rate: {e}")
            return 0.0

    def transform_to_social_media_format(
        self,
        videos: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Transform TikTok data to match social media pipeline format

        Args:
            videos: List of TikTok video data

        Returns:
            Transformed data matching pipeline schema
        """
        transformed = []

        for video in videos:
            try:
                engagement_rate = self.calculate_engagement_rate(video)

                transformed_item = {
                    "source": "tiktok",
                    "source_id": video.get("video_id"),
                    "author": video.get("author", {}).get("username"),
                    "content": video.get("content", {}).get("description", ""),
                    "metrics": {
                        "views": video.get("metrics", {}).get("views", 0),
                        "likes": video.get("metrics", {}).get("likes", 0),
                        "comments": video.get("metrics", {}).get("comments", 0),
                        "shares": video.get("metrics", {}).get("shares", 0),
                        "engagement_rate": engagement_rate
                    },
                    "hashtags": video.get("hashtags", []),
                    "created_at": video.get("created_at"),
                    "collected_at": video.get("collected_at"),
                    "geo_location": video.get("geo_location", "Nigeria"),
                    "media_type": "video",
                    "duration": video.get("content", {}).get("duration", 0)
                }

                transformed.append(transformed_item)

            except Exception as e:
                logger.error(f"Error transforming video data: {e}")
                continue

        return transformed

    async def get_hashtag_analytics(
        self,
        hashtag: str,
        days: int = 7
    ) -> Dict[str, Any]:
        """
        Get analytics for a specific hashtag over time

        Args:
            hashtag: Hashtag to analyze
            days: Number of days to analyze

        Returns:
            Hashtag analytics data
        """
        try:
            logger.info(f"Analyzing hashtag #{hashtag} for {days} days")

            # Fetch recent videos
            videos = await self.search_hashtag(hashtag=hashtag, count=100)

            if not videos:
                return {
                    "hashtag": hashtag,
                    "analytics": {},
                    "error": "No videos found"
                }

            # Calculate analytics
            total_views = sum(v.get("metrics", {}).get("views", 0) for v in videos)
            total_likes = sum(v.get("metrics", {}).get("likes", 0) for v in videos)
            total_comments = sum(v.get("metrics", {}).get("comments", 0) for v in videos)
            total_shares = sum(v.get("metrics", {}).get("shares", 0) for v in videos)

            avg_engagement = sum(
                self.calculate_engagement_rate(v) for v in videos
            ) / len(videos) if videos else 0

            analytics = {
                "hashtag": hashtag,
                "period_days": days,
                "total_videos": len(videos),
                "total_views": total_views,
                "total_likes": total_likes,
                "total_comments": total_comments,
                "total_shares": total_shares,
                "avg_engagement_rate": avg_engagement,
                "top_creators": self._get_top_creators(videos),
                "timestamp": datetime.utcnow().isoformat()
            }

            logger.info(f"Analytics completed for #{hashtag}")
            return analytics

        except Exception as e:
            logger.error(f"Error analyzing hashtag: {e}")
            return {"hashtag": hashtag, "error": str(e)}

    def _get_top_creators(
        self,
        videos: List[Dict[str, Any]],
        top_n: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get top creators from video list

        Args:
            videos: List of video data
            top_n: Number of top creators to return

        Returns:
            List of top creator data
        """
        try:
            # Aggregate by creator
            creator_stats = {}

            for video in videos:
                author = video.get("author", {})
                username = author.get("username")

                if not username:
                    continue

                if username not in creator_stats:
                    creator_stats[username] = {
                        "username": username,
                        "nickname": author.get("nickname"),
                        "video_count": 0,
                        "total_views": 0,
                        "total_likes": 0
                    }

                metrics = video.get("metrics", {})
                creator_stats[username]["video_count"] += 1
                creator_stats[username]["total_views"] += metrics.get("views", 0)
                creator_stats[username]["total_likes"] += metrics.get("likes", 0)

            # Sort by total views
            top_creators = sorted(
                creator_stats.values(),
                key=lambda x: x["total_views"],
                reverse=True
            )[:top_n]

            return top_creators

        except Exception as e:
            logger.error(f"Error getting top creators: {e}")
            return []


# Singleton instance
_tiktok_service = None


def get_tiktok_service() -> TikTokService:
    """Get or create TikTok service instance"""
    global _tiktok_service
    if _tiktok_service is None:
        _tiktok_service = TikTokService()
    return _tiktok_service
