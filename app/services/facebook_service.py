"""
Facebook Service for Nigerian Social Media Analysis
Scrapes public Facebook posts and engagement metrics focused on Nigeria
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import asyncio
from facebook_scraper import get_posts, set_user_agent, enable_logging
import random
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config import settings

logger = logging.getLogger(__name__)


class FacebookService:
    """
    Service for scraping Facebook public data with focus on Nigerian content
    Uses facebook-scraper for public post collection
    """

    def __init__(self):
        """Initialize Facebook service"""
        self.app_id = settings.FACEBOOK_APP_ID
        self.app_secret = settings.FACEBOOK_APP_SECRET
        self.access_token = settings.FACEBOOK_ACCESS_TOKEN

        # User agents for rotation
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X)",
        ]

        # Nigerian pages and groups to monitor
        self.nigerian_pages = [
            "legit.ng",
            "lindaikejisblog",
            "punchng",
            "guardiannigeria",
            "thenationonlineng",
            "vanguardngrnews",
            "dailytrustng",
            "premiumtimesng"
        ]

        # Rate limiting
        self.request_delay = 3  # seconds between requests
        self.last_request_time = None

        # Set default user agent
        set_user_agent(random.choice(self.user_agents))

        logger.info("Facebook Service initialized")

    async def _rate_limit(self):
        """Implement rate limiting between requests"""
        if self.last_request_time:
            elapsed = (datetime.utcnow() - self.last_request_time).total_seconds()
            if elapsed < self.request_delay:
                await asyncio.sleep(self.request_delay - elapsed)
        self.last_request_time = datetime.utcnow()

    def _rotate_user_agent(self):
        """Rotate user agent for each request"""
        set_user_agent(random.choice(self.user_agents))

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=4, max=30)
    )
    async def scrape_page_posts(
        self,
        page_name: str,
        pages: int = 2,
        timeout: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Scrape posts from a Facebook page

        Args:
            page_name: Facebook page username/id
            pages: Number of pages to scrape (each page ~2-10 posts)
            timeout: Request timeout in seconds

        Returns:
            List of post data dictionaries
        """
        try:
            logger.info(f"Scraping posts from page: {page_name}")
            await self._rate_limit()
            self._rotate_user_agent()

            posts_data = []

            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()

            def scrape():
                posts = []
                try:
                    for post in get_posts(
                        page_name,
                        pages=pages,
                        timeout=timeout,
                        options={
                            "comments": True,
                            "reactors": False,
                            "posts_per_page": 10
                        }
                    ):
                        posts.append(self._extract_post_data(post, page_name))

                        # Limit to prevent excessive scraping
                        if len(posts) >= pages * 10:
                            break
                except Exception as e:
                    logger.error(f"Error in scraping loop: {e}")

                return posts

            posts_data = await loop.run_in_executor(None, scrape)

            logger.info(f"Scraped {len(posts_data)} posts from {page_name}")
            return posts_data

        except Exception as e:
            logger.error(f"Error scraping page {page_name}: {e}")
            return []

    def _extract_post_data(
        self,
        post: Dict[str, Any],
        page_name: str
    ) -> Dict[str, Any]:
        """
        Extract and structure relevant data from Facebook post

        Args:
            post: Raw post data from facebook-scraper
            page_name: Name of the page

        Returns:
            Structured post data dictionary
        """
        try:
            # Extract engagement metrics
            likes = post.get("likes", 0) or 0
            comments = post.get("comments", 0) or 0
            shares = post.get("shares", 0) or 0

            # Calculate engagement rate (relative to typical page performance)
            total_engagement = likes + comments + shares

            return {
                "post_id": post.get("post_id"),
                "page": page_name,
                "author": post.get("username", page_name),
                "content": {
                    "text": post.get("text", ""),
                    "post_text": post.get("post_text", ""),
                    "has_image": bool(post.get("image")),
                    "has_video": bool(post.get("video")),
                    "link": post.get("link"),
                    "post_url": post.get("post_url")
                },
                "metrics": {
                    "likes": likes,
                    "comments": comments,
                    "shares": shares,
                    "total_engagement": total_engagement,
                    "reactions": post.get("reactions", {})
                },
                "timestamp": {
                    "posted_at": post.get("time").isoformat() if post.get("time") else None,
                    "collected_at": datetime.utcnow().isoformat()
                },
                "media": {
                    "images": post.get("images", []),
                    "video": post.get("video"),
                    "video_thumbnail": post.get("video_thumbnail")
                },
                "engagement_details": {
                    "comment_count": comments,
                    "top_comments": post.get("comments_full", [])[:5] if post.get("comments_full") else []
                },
                "source": "facebook",
                "geo_location": "Nigeria"  # Inferred from Nigerian page monitoring
            }

        except Exception as e:
            logger.error(f"Error extracting post data: {e}")
            return {
                "post_id": post.get("post_id"),
                "page": page_name,
                "error": str(e)
            }

    async def scrape_group_posts(
        self,
        group_id: str,
        pages: int = 2
    ) -> List[Dict[str, Any]]:
        """
        Scrape posts from a Facebook group (requires group to be public)

        Args:
            group_id: Facebook group ID
            pages: Number of pages to scrape

        Returns:
            List of post data dictionaries
        """
        try:
            logger.info(f"Scraping posts from group: {group_id}")
            await self._rate_limit()
            self._rotate_user_agent()

            posts_data = []
            loop = asyncio.get_event_loop()

            def scrape():
                posts = []
                try:
                    for post in get_posts(
                        group=group_id,
                        pages=pages,
                        options={"comments": True}
                    ):
                        posts.append(self._extract_post_data(post, f"group_{group_id}"))

                        if len(posts) >= pages * 10:
                            break
                except Exception as e:
                    logger.error(f"Error scraping group: {e}")

                return posts

            posts_data = await loop.run_in_executor(None, scrape)

            logger.info(f"Scraped {len(posts_data)} posts from group {group_id}")
            return posts_data

        except Exception as e:
            logger.error(f"Error scraping group {group_id}: {e}")
            return []

    async def monitor_nigerian_pages(
        self,
        pages_per_source: int = 2
    ) -> Dict[str, Any]:
        """
        Monitor multiple Nigerian Facebook pages for content

        Args:
            pages_per_source: Number of pages to scrape per source

        Returns:
            Aggregated post data from Nigerian pages
        """
        try:
            logger.info("Starting Nigerian Facebook pages monitoring")

            all_posts = []
            page_stats = []

            for page_name in self.nigerian_pages:
                try:
                    # Scrape posts from each page
                    posts = await self.scrape_page_posts(
                        page_name=page_name,
                        pages=pages_per_source
                    )

                    all_posts.extend(posts)

                    # Calculate page stats
                    if posts:
                        total_engagement = sum(
                            p.get("metrics", {}).get("total_engagement", 0)
                            for p in posts
                        )
                        avg_engagement = total_engagement / len(posts) if posts else 0

                        page_stats.append({
                            "page": page_name,
                            "post_count": len(posts),
                            "total_engagement": total_engagement,
                            "avg_engagement": avg_engagement
                        })

                    # Rate limiting between pages
                    await asyncio.sleep(5)

                except Exception as e:
                    logger.error(f"Error monitoring page {page_name}: {e}")
                    continue

            result = {
                "posts": all_posts,
                "page_stats": page_stats,
                "total_posts": len(all_posts),
                "monitored_pages": len(page_stats),
                "timestamp": datetime.utcnow().isoformat(),
                "region": "Nigeria"
            }

            logger.info(f"Monitoring complete: {len(all_posts)} posts from "
                       f"{len(page_stats)} pages")
            return result

        except Exception as e:
            logger.error(f"Error in Nigerian pages monitoring: {e}")
            return {
                "posts": [],
                "page_stats": [],
                "error": str(e)
            }

    def calculate_engagement_rate(self, post_data: Dict[str, Any]) -> float:
        """
        Calculate engagement rate for a post

        Args:
            post_data: Post data dictionary

        Returns:
            Engagement rate score
        """
        try:
            metrics = post_data.get("metrics", {})
            likes = metrics.get("likes", 0)
            comments = metrics.get("comments", 0)
            shares = metrics.get("shares", 0)

            # Weighted engagement score
            # Comments and shares are weighted more heavily
            engagement_score = (
                likes * 1.0 +
                comments * 3.0 +
                shares * 5.0
            )

            return engagement_score

        except Exception as e:
            logger.error(f"Error calculating engagement rate: {e}")
            return 0.0

    def transform_to_social_media_format(
        self,
        posts: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Transform Facebook data to match social media pipeline format

        Args:
            posts: List of Facebook post data

        Returns:
            Transformed data matching pipeline schema
        """
        transformed = []

        for post in posts:
            try:
                content_data = post.get("content", {})
                metrics = post.get("metrics", {})

                transformed_item = {
                    "source": "facebook",
                    "source_id": post.get("post_id"),
                    "author": post.get("author"),
                    "page": post.get("page"),
                    "content": content_data.get("text") or content_data.get("post_text", ""),
                    "metrics": {
                        "likes": metrics.get("likes", 0),
                        "comments": metrics.get("comments", 0),
                        "shares": metrics.get("shares", 0),
                        "total_engagement": metrics.get("total_engagement", 0),
                        "engagement_score": self.calculate_engagement_rate(post)
                    },
                    "media": {
                        "has_image": content_data.get("has_image", False),
                        "has_video": content_data.get("has_video", False),
                        "link": content_data.get("link")
                    },
                    "posted_at": post.get("timestamp", {}).get("posted_at"),
                    "collected_at": post.get("timestamp", {}).get("collected_at"),
                    "geo_location": post.get("geo_location", "Nigeria"),
                    "post_url": content_data.get("post_url")
                }

                transformed.append(transformed_item)

            except Exception as e:
                logger.error(f"Error transforming post data: {e}")
                continue

        return transformed

    async def get_page_analytics(
        self,
        page_name: str,
        pages: int = 5
    ) -> Dict[str, Any]:
        """
        Get analytics for a specific Facebook page

        Args:
            page_name: Facebook page name
            pages: Number of pages to analyze

        Returns:
            Page analytics data
        """
        try:
            logger.info(f"Analyzing Facebook page: {page_name}")

            # Scrape recent posts
            posts = await self.scrape_page_posts(page_name=page_name, pages=pages)

            if not posts:
                return {
                    "page": page_name,
                    "analytics": {},
                    "error": "No posts found"
                }

            # Calculate analytics
            total_likes = sum(p.get("metrics", {}).get("likes", 0) for p in posts)
            total_comments = sum(p.get("metrics", {}).get("comments", 0) for p in posts)
            total_shares = sum(p.get("metrics", {}).get("shares", 0) for p in posts)
            total_engagement = total_likes + total_comments + total_shares

            avg_engagement = total_engagement / len(posts) if posts else 0

            # Identify top posts
            top_posts = sorted(
                posts,
                key=lambda p: p.get("metrics", {}).get("total_engagement", 0),
                reverse=True
            )[:5]

            # Post type distribution
            posts_with_images = sum(1 for p in posts if p.get("content", {}).get("has_image"))
            posts_with_videos = sum(1 for p in posts if p.get("content", {}).get("has_video"))
            text_only_posts = len(posts) - posts_with_images - posts_with_videos

            analytics = {
                "page": page_name,
                "total_posts": len(posts),
                "engagement_summary": {
                    "total_likes": total_likes,
                    "total_comments": total_comments,
                    "total_shares": total_shares,
                    "total_engagement": total_engagement,
                    "avg_engagement_per_post": avg_engagement
                },
                "post_type_distribution": {
                    "with_images": posts_with_images,
                    "with_videos": posts_with_videos,
                    "text_only": text_only_posts
                },
                "top_posts": [
                    {
                        "post_id": p.get("post_id"),
                        "content_preview": p.get("content", {}).get("text", "")[:100],
                        "engagement": p.get("metrics", {}).get("total_engagement", 0)
                    }
                    for p in top_posts
                ],
                "timestamp": datetime.utcnow().isoformat()
            }

            logger.info(f"Analytics completed for {page_name}")
            return analytics

        except Exception as e:
            logger.error(f"Error analyzing page: {e}")
            return {"page": page_name, "error": str(e)}

    async def search_posts_by_keyword(
        self,
        page_name: str,
        keyword: str,
        pages: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Search for posts containing specific keyword from a page

        Args:
            page_name: Facebook page name
            keyword: Keyword to search for
            pages: Number of pages to search

        Returns:
            List of matching posts
        """
        try:
            logger.info(f"Searching for '{keyword}' in {page_name}")

            # Scrape posts
            all_posts = await self.scrape_page_posts(page_name=page_name, pages=pages)

            # Filter by keyword
            keyword_lower = keyword.lower()
            matching_posts = [
                post for post in all_posts
                if keyword_lower in post.get("content", {}).get("text", "").lower()
                or keyword_lower in post.get("content", {}).get("post_text", "").lower()
            ]

            logger.info(f"Found {len(matching_posts)} posts matching '{keyword}'")
            return matching_posts

        except Exception as e:
            logger.error(f"Error searching posts: {e}")
            return []


# Singleton instance
_facebook_service = None


def get_facebook_service() -> FacebookService:
    """Get or create Facebook service instance"""
    global _facebook_service
    if _facebook_service is None:
        _facebook_service = FacebookService()
    return _facebook_service
