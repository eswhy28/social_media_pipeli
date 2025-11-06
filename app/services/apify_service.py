"""
Apify Service for Advanced Social Media Scraping
Uses Apify platform for robust, scalable web scraping operations
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio
from apify_client import ApifyClient
from apify_client.client import ApifyClientAsync
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config import settings

logger = logging.getLogger(__name__)


class ApifyService:
    """
    Service for running Apify actors to scrape social media data
    Provides advanced scraping capabilities with built-in proxy rotation
    """

    def __init__(self):
        """Initialize Apify service"""
        self.api_token = settings.APIFY_API_TOKEN

        if not self.api_token:
            logger.warning("Apify API token not configured")
            self.client = None
            self.async_client = None
        else:
            # Initialize clients
            self.client = ApifyClient(self.api_token)
            self.async_client = ApifyClientAsync(self.api_token)
            logger.info("Apify Service initialized")

        # Popular Apify actors for social media
        self.actors = {
            "instagram": "apify/instagram-scraper",
            "tiktok": "apify/tiktok-scraper",
            "twitter": "apify/twitter-scraper",
            "facebook": "apify/facebook-pages-scraper",
            "youtube": "apify/youtube-scraper"
        }

    def _check_client(self):
        """Check if client is initialized"""
        if not self.client or not self.async_client:
            raise ValueError("Apify API token not configured. Please set APIFY_API_TOKEN in environment variables.")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=20)
    )
    async def run_actor(
        self,
        actor_id: str,
        run_input: Dict[str, Any],
        wait_for_finish: bool = True,
        timeout_secs: int = 300
    ) -> Dict[str, Any]:
        """
        Run an Apify actor with specified input

        Args:
            actor_id: Apify actor ID (e.g., 'apify/instagram-scraper')
            run_input: Input configuration for the actor
            wait_for_finish: Whether to wait for actor to complete
            timeout_secs: Maximum wait time in seconds

        Returns:
            Actor run result data
        """
        try:
            self._check_client()
            logger.info(f"Running Apify actor: {actor_id}")

            # Run the actor
            run = await self.async_client.actor(actor_id).call(
                run_input=run_input,
                timeout_secs=timeout_secs if wait_for_finish else None
            )

            if not wait_for_finish:
                return {
                    "status": "running",
                    "run_id": run.get("id"),
                    "actor_id": actor_id
                }

            # Get results
            result = {
                "status": run.get("status"),
                "run_id": run.get("id"),
                "actor_id": actor_id,
                "started_at": run.get("startedAt"),
                "finished_at": run.get("finishedAt"),
                "stats": run.get("stats", {}),
                "data": []
            }

            # Fetch dataset items
            if run.get("defaultDatasetId"):
                dataset_client = self.async_client.dataset(run["defaultDatasetId"])
                items = []

                async for item in dataset_client.iterate_items():
                    items.append(item)

                result["data"] = items
                result["item_count"] = len(items)

            logger.info(f"Actor run completed: {result['item_count']} items collected")
            return result

        except Exception as e:
            logger.error(f"Error running actor {actor_id}: {e}")
            return {
                "status": "failed",
                "actor_id": actor_id,
                "error": str(e)
            }

    async def scrape_instagram_profile(
        self,
        username: str,
        results_limit: int = 50
    ) -> Dict[str, Any]:
        """
        Scrape Instagram profile data

        Args:
            username: Instagram username to scrape
            results_limit: Maximum number of posts to scrape

        Returns:
            Instagram profile and posts data
        """
        try:
            logger.info(f"Scraping Instagram profile: {username}")

            run_input = {
                "username": [username],
                "resultsLimit": results_limit,
                "addParentData": True
            }

            result = await self.run_actor(
                actor_id=self.actors["instagram"],
                run_input=run_input,
                timeout_secs=300
            )

            # Transform data
            transformed_data = self._transform_instagram_data(result.get("data", []))

            return {
                "platform": "instagram",
                "username": username,
                "posts": transformed_data,
                "total_posts": len(transformed_data),
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Error scraping Instagram profile: {e}")
            return {"platform": "instagram", "username": username, "error": str(e)}

    async def scrape_tiktok_hashtag(
        self,
        hashtag: str,
        results_limit: int = 50
    ) -> Dict[str, Any]:
        """
        Scrape TikTok hashtag data using Apify

        Args:
            hashtag: Hashtag to scrape (without #)
            results_limit: Maximum number of videos to scrape

        Returns:
            TikTok hashtag data
        """
        try:
            logger.info(f"Scraping TikTok hashtag: #{hashtag}")

            run_input = {
                "hashtags": [hashtag],
                "resultsPerPage": results_limit,
                "shouldDownloadVideos": False,
                "shouldDownloadCovers": False
            }

            result = await self.run_actor(
                actor_id=self.actors["tiktok"],
                run_input=run_input,
                timeout_secs=300
            )

            # Transform data
            transformed_data = self._transform_tiktok_data(result.get("data", []))

            return {
                "platform": "tiktok",
                "hashtag": hashtag,
                "videos": transformed_data,
                "total_videos": len(transformed_data),
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Error scraping TikTok hashtag: {e}")
            return {"platform": "tiktok", "hashtag": hashtag, "error": str(e)}

    async def scrape_facebook_page(
        self,
        page_url: str,
        posts_limit: int = 50
    ) -> Dict[str, Any]:
        """
        Scrape Facebook page data using Apify

        Args:
            page_url: Facebook page URL
            posts_limit: Maximum number of posts to scrape

        Returns:
            Facebook page data
        """
        try:
            logger.info(f"Scraping Facebook page: {page_url}")

            run_input = {
                "startUrls": [{"url": page_url}],
                "maxPosts": posts_limit,
                "scrapeAbout": True,
                "scrapeReviews": False,
                "scrapeServices": False
            }

            result = await self.run_actor(
                actor_id=self.actors["facebook"],
                run_input=run_input,
                timeout_secs=300
            )

            # Transform data
            transformed_data = self._transform_facebook_data(result.get("data", []))

            return {
                "platform": "facebook",
                "page_url": page_url,
                "posts": transformed_data,
                "total_posts": len(transformed_data),
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Error scraping Facebook page: {e}")
            return {"platform": "facebook", "page_url": page_url, "error": str(e)}

    async def scrape_twitter_profile(
        self,
        username: str,
        tweets_limit: int = 50
    ) -> Dict[str, Any]:
        """
        Scrape Twitter profile data using Apify

        Args:
            username: Twitter username (without @)
            tweets_limit: Maximum number of tweets to scrape

        Returns:
            Twitter profile and tweets data
        """
        try:
            logger.info(f"Scraping Twitter profile: @{username}")

            run_input = {
                "startUrls": [f"https://twitter.com/{username}"],
                "tweetsDesired": tweets_limit,
                "proxyConfig": {"useApifyProxy": True}
            }

            result = await self.run_actor(
                actor_id=self.actors["twitter"],
                run_input=run_input,
                timeout_secs=300
            )

            # Transform data
            transformed_data = self._transform_twitter_data(result.get("data", []))

            return {
                "platform": "twitter",
                "username": username,
                "tweets": transformed_data,
                "total_tweets": len(transformed_data),
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Error scraping Twitter profile: {e}")
            return {"platform": "twitter", "username": username, "error": str(e)}

    def _transform_instagram_data(
        self,
        raw_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Transform Instagram data to standard format"""
        transformed = []

        for item in raw_data:
            try:
                transformed_item = {
                    "source": "instagram",
                    "source_id": item.get("id") or item.get("shortCode"),
                    "author": item.get("ownerUsername"),
                    "content": item.get("caption", ""),
                    "media_type": item.get("type", "post"),
                    "metrics": {
                        "likes": item.get("likesCount", 0),
                        "comments": item.get("commentsCount", 0),
                        "views": item.get("videoViewCount", 0)
                    },
                    "hashtags": item.get("hashtags", []),
                    "posted_at": item.get("timestamp"),
                    "collected_at": datetime.utcnow().isoformat(),
                    "url": item.get("url"),
                    "location": item.get("locationName"),
                    "geo_location": "Nigeria"  # If Nigerian account
                }
                transformed.append(transformed_item)
            except Exception as e:
                logger.error(f"Error transforming Instagram item: {e}")
                continue

        return transformed

    def _transform_tiktok_data(
        self,
        raw_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Transform TikTok data to standard format"""
        transformed = []

        for item in raw_data:
            try:
                transformed_item = {
                    "source": "tiktok",
                    "source_id": item.get("id"),
                    "author": item.get("authorMeta", {}).get("name"),
                    "content": item.get("text", ""),
                    "media_type": "video",
                    "metrics": {
                        "views": item.get("playCount", 0),
                        "likes": item.get("diggCount", 0),
                        "comments": item.get("commentCount", 0),
                        "shares": item.get("shareCount", 0)
                    },
                    "hashtags": [h.get("name") for h in item.get("hashtags", [])],
                    "music": item.get("musicMeta", {}).get("musicName"),
                    "posted_at": item.get("createTime"),
                    "collected_at": datetime.utcnow().isoformat(),
                    "url": item.get("webVideoUrl"),
                    "duration": item.get("videoMeta", {}).get("duration"),
                    "geo_location": "Nigeria"
                }
                transformed.append(transformed_item)
            except Exception as e:
                logger.error(f"Error transforming TikTok item: {e}")
                continue

        return transformed

    def _transform_facebook_data(
        self,
        raw_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Transform Facebook data to standard format"""
        transformed = []

        for item in raw_data:
            try:
                # Handle both page info and posts
                if item.get("posts"):
                    # Page with posts
                    for post in item.get("posts", []):
                        transformed_item = self._transform_facebook_post(post, item.get("name"))
                        transformed.append(transformed_item)
                else:
                    # Single post
                    transformed_item = self._transform_facebook_post(item)
                    transformed.append(transformed_item)

            except Exception as e:
                logger.error(f"Error transforming Facebook item: {e}")
                continue

        return transformed

    def _transform_facebook_post(
        self,
        post: Dict[str, Any],
        page_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Transform single Facebook post"""
        return {
            "source": "facebook",
            "source_id": post.get("postId"),
            "page": page_name or post.get("pageName"),
            "content": post.get("text", ""),
            "metrics": {
                "likes": post.get("likes", 0),
                "comments": post.get("comments", 0),
                "shares": post.get("shares", 0)
            },
            "media_type": post.get("type", "post"),
            "posted_at": post.get("time"),
            "collected_at": datetime.utcnow().isoformat(),
            "url": post.get("postUrl"),
            "geo_location": "Nigeria"
        }

    def _transform_twitter_data(
        self,
        raw_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Transform Twitter data to standard format"""
        transformed = []

        for item in raw_data:
            try:
                transformed_item = {
                    "source": "twitter",
                    "source_id": item.get("id"),
                    "author": item.get("user", {}).get("screen_name"),
                    "content": item.get("text", ""),
                    "metrics": {
                        "likes": item.get("favorite_count", 0),
                        "retweets": item.get("retweet_count", 0),
                        "replies": item.get("reply_count", 0)
                    },
                    "hashtags": [h.get("text") for h in item.get("entities", {}).get("hashtags", [])],
                    "posted_at": item.get("created_at"),
                    "collected_at": datetime.utcnow().isoformat(),
                    "url": item.get("url"),
                    "is_retweet": item.get("retweeted", False),
                    "geo_location": "Nigeria"
                }
                transformed.append(transformed_item)
            except Exception as e:
                logger.error(f"Error transforming Twitter item: {e}")
                continue

        return transformed

    async def scrape_nigerian_social_media(
        self,
        platforms: List[str] = None,
        items_per_platform: int = 50
    ) -> Dict[str, Any]:
        """
        Comprehensive scraping across multiple Nigerian social media sources

        Args:
            platforms: List of platforms to scrape (default: all)
            items_per_platform: Number of items to scrape per platform

        Returns:
            Aggregated social media data
        """
        try:
            if platforms is None:
                platforms = ["instagram", "tiktok", "facebook"]

            logger.info(f"Starting comprehensive Nigerian social media scraping: {platforms}")

            results = {
                "platforms": {},
                "timestamp": datetime.utcnow().isoformat(),
                "region": "Nigeria"
            }

            # Nigerian accounts/pages to monitor
            nigerian_accounts = {
                "instagram": ["lagosnigeria", "visitnigeria", "nigerianweddings"],
                "tiktok": ["nigeria", "lagos", "naija"],
                "facebook": [
                    "https://www.facebook.com/legit.ng",
                    "https://www.facebook.com/lindaikejisblog"
                ]
            }

            # Scrape each platform
            for platform in platforms:
                try:
                    if platform == "instagram" and platform in nigerian_accounts:
                        # Scrape first Instagram account
                        username = nigerian_accounts["instagram"][0]
                        data = await self.scrape_instagram_profile(
                            username=username,
                            results_limit=items_per_platform
                        )
                        results["platforms"]["instagram"] = data

                    elif platform == "tiktok" and platform in nigerian_accounts:
                        # Scrape first TikTok hashtag
                        hashtag = nigerian_accounts["tiktok"][0]
                        data = await self.scrape_tiktok_hashtag(
                            hashtag=hashtag,
                            results_limit=items_per_platform
                        )
                        results["platforms"]["tiktok"] = data

                    elif platform == "facebook" and platform in nigerian_accounts:
                        # Scrape first Facebook page
                        page_url = nigerian_accounts["facebook"][0]
                        data = await self.scrape_facebook_page(
                            page_url=page_url,
                            posts_limit=items_per_platform
                        )
                        results["platforms"]["facebook"] = data

                    # Rate limiting between platforms
                    await asyncio.sleep(5)

                except Exception as e:
                    logger.error(f"Error scraping {platform}: {e}")
                    results["platforms"][platform] = {"error": str(e)}

            logger.info("Comprehensive scraping completed")
            return results

        except Exception as e:
            logger.error(f"Error in comprehensive scraping: {e}")
            return {"error": str(e)}

    async def get_actor_status(self, run_id: str) -> Dict[str, Any]:
        """
        Get status of a running actor

        Args:
            run_id: Actor run ID

        Returns:
            Actor run status
        """
        try:
            self._check_client()

            run = await self.async_client.run(run_id).get()

            return {
                "run_id": run_id,
                "status": run.get("status"),
                "started_at": run.get("startedAt"),
                "finished_at": run.get("finishedAt"),
                "stats": run.get("stats", {})
            }

        except Exception as e:
            logger.error(f"Error getting actor status: {e}")
            return {"run_id": run_id, "error": str(e)}


# Singleton instance
_apify_service = None


def get_apify_service() -> ApifyService:
    """Get or create Apify service instance"""
    global _apify_service
    if _apify_service is None:
        _apify_service = ApifyService()
    return _apify_service
