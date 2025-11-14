"""
Facebook Service for Nigerian Social Media Analysis
Scrapes public Facebook posts and engagement metrics focused on Nigeria
Now uses Apify for robust scraping
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config import settings
from app.services.apify_service import get_apify_service

logger = logging.getLogger(__name__)


class FacebookService:
    """
    Service for scraping Facebook public data with focus on Nigerian content
    Uses Apify for robust and scalable scraping
    """

    def __init__(self):
        """Initialize Facebook service"""
        self.apify_service = get_apify_service()

        # Nigerian pages and groups to monitor
        self.nigerian_pages = [
            "https://www.facebook.com/legit.ng",
            "https://www.facebook.com/lindaikejisblog",
            "https://www.facebook.com/punchng",
            "https://www.facebook.com/guardiannigeria",
            "https://www.facebook.com/thenationonlineng",
            "https://www.facebook.com/vanguardngrnews",
            "https://www.facebook.com/dailytrustng",
            "https://www.facebook.com/premiumtimesng"
        ]

        logger.info("Facebook Service initialized with Apify integration")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=4, max=30)
    )
    async def scrape_page_posts(
        self,
        page_url: str,
        posts_limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Scrape posts from a Facebook page using Apify

        Args:
            page_url: Facebook page URL
            posts_limit: Maximum number of posts to scrape

        Returns:
            List of post data dictionaries
        """
        try:
            logger.info(f"Scraping posts from page: {page_url} using Apify")

            # Use Apify service to scrape Facebook page
            result = await self.apify_service.scrape_facebook_page(
                page_url=page_url,
                posts_limit=posts_limit
            )

            if "error" in result:
                logger.error(f"Apify scraping error: {result['error']}")
                return []

            posts = result.get("posts", [])
            logger.info(f"Scraped {len(posts)} posts from {page_url}")
            return posts

        except Exception as e:
            logger.error(f"Error scraping page {page_url}: {e}")
            return []

    async def monitor_nigerian_pages(
        self,
        posts_per_page: int = 50,
        page_list: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Monitor multiple Nigerian Facebook pages for content using Apify

        Args:
            posts_per_page: Number of posts to scrape per page
            page_list: Optional list of page URLs to monitor (if None, uses default Nigerian pages)

        Returns:
            Aggregated post data from Nigerian pages
        """
        try:
            logger.info("Starting Nigerian Facebook pages monitoring with Apify")

            # Use provided page list or default Nigerian pages
            pages_to_monitor = page_list if page_list is not None else self.nigerian_pages

            all_posts = []
            page_stats = []

            for page_url in pages_to_monitor:
                try:
                    # Scrape posts from each page using Apify
                    posts = await self.scrape_page_posts(
                        page_url=page_url,
                        posts_limit=posts_per_page
                    )

                    all_posts.extend(posts)

                    # Calculate page stats
                    if posts:
                        total_engagement = sum(
                            p.get("metrics", {}).get("likes", 0) +
                            p.get("metrics", {}).get("comments", 0) +
                            p.get("metrics", {}).get("shares", 0)
                            for p in posts
                        )
                        avg_engagement = total_engagement / len(posts) if posts else 0

                        page_stats.append({
                            "page": page_url,
                            "post_count": len(posts),
                            "total_engagement": total_engagement,
                            "avg_engagement": avg_engagement
                        })

                    # Rate limiting between pages
                    await asyncio.sleep(10)  # Increased delay for Apify

                except Exception as e:
                    logger.error(f"Error monitoring page {page_url}: {e}")
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
