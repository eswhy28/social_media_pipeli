"""
Apify Service for Advanced Social Media Scraping
Uses Apify platform for robust, scalable web scraping operations
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio
import uuid
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

        # Official Apify actors for Twitter and Facebook scraping
        self.actors = {
            "twitter": "apidojo/tweet-scraper",  # Tweet Scraper V2 - X / Twitter Scraper
            "facebook": "apify/facebook-posts-scraper"  # Facebook Posts Scraper
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





    async def scrape_facebook_page(
        self,
        page_url: str,
        posts_limit: int = 50
    ) -> Dict[str, Any]:
        """
        Scrape Facebook page posts using official Facebook Posts Scraper
        
        Uses apify/facebook-posts-scraper actor with proper input format:
        - startUrls: Array of Facebook page/profile URLs
        - resultsLimit: Maximum number of posts to return

        Args:
            page_url: Facebook page URL (e.g., "https://www.facebook.com/nytimes")
            posts_limit: Maximum number of posts to scrape

        Returns:
            Facebook page posts data
        """
        try:
            logger.info(f"Scraping Facebook page: {page_url}")

            # Official Facebook Posts Scraper input format
            run_input = {
                "startUrls": [{"url": page_url}],  # Array of URLs to scrape
                "resultsLimit": posts_limit,  # Maximum posts to return
                "proxy": {
                    "useApifyProxy": True
                }
            }

            result = await self.run_actor(
                actor_id=self.actors["facebook"],
                run_input=run_input,
                timeout_secs=300
            )

            # Transform data to standardized format
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

    async def scrape_twitter_search(
        self,
        search_queries: List[str],
        max_tweets: int = 50,
        add_filters: bool = True
    ) -> Dict[str, Any]:
        """
        Scrape Twitter (X) search results using Tweet Scraper V2
        
        Uses official apidojo/tweet-scraper actor with proper input format:
        - searchTerms: Array of search queries/hashtags
        - maxItems: Maximum number of tweets to return
        - sort: Sort order (Latest)

        Args:
            search_queries: List of search terms or hashtags
            max_tweets: Maximum number of tweets to scrape
            add_filters: Add quality filters (min engagement, language, etc.)

        Returns:
            Twitter search results with transformed data
        """
        try:
            logger.info(f"Scraping Twitter (X) search: {search_queries}")

            # Add Nigeria-specific filters for better quality content
            if add_filters:
                filtered_queries = []
                for query in search_queries:
                    # Add advanced filters for Nigerian content
                    enhanced_query = f"{query} lang:en min_retweets:2 min_faves:5"
                    filtered_queries.append(enhanced_query)
                search_queries = filtered_queries
                logger.info(f"Enhanced queries with filters: {search_queries}")

            # Official Tweet Scraper V2 input format
            run_input = {
                "searchTerms": search_queries,  # Array of search queries
                "maxItems": max_tweets,  # Maximum tweets to return
                "sort": "Latest",  # Latest tweets first
                "onlyVerifiedUsers": False,  # Include all users
                "onlyImage": False,  # Include all tweet types
                "onlyVideo": False,
                "onlyQuote": False
            }

            result = await self.run_actor(
                actor_id=self.actors["twitter"],
                run_input=run_input,
                timeout_secs=300
            )

            # Transform data to standardized format
            transformed_data = self._transform_twitter_data(result.get("data", []))

            return {
                "platform": "twitter",
                "success": True,
                "queries": search_queries,
                "tweets": transformed_data,
                "total_tweets": len(transformed_data),
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Error scraping Twitter search: {e}")
            return {
                "platform": "twitter",
                "success": False,
                "queries": search_queries,
                "error": str(e)
            }

    async def scrape_twitter_profile(
        self,
        username: str,
        tweets_limit: int = 50
    ) -> Dict[str, Any]:
        """
        Scrape Twitter (X) profile data using Tweet Scraper V2
        
        Uses official apidojo/tweet-scraper actor with twitterHandles input

        Args:
            username: Twitter username (without @)
            tweets_limit: Maximum number of tweets to scrape

        Returns:
            Twitter profile and tweets data
        """
        try:
            logger.info(f"Scraping Twitter (X) profile: @{username}")

            # Official Tweet Scraper V2 input format for profiles
            run_input = {
                "twitterHandles": [username],  # Array of Twitter handles
                "maxItems": tweets_limit,  # Maximum tweets to return
                "sort": "Latest"  # Latest tweets first
            }

            result = await self.run_actor(
                actor_id=self.actors["twitter"],
                run_input=run_input,
                timeout_secs=300
            )

            # Transform data to standardized format
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





    def _transform_facebook_data(
        self,
        raw_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Transform Facebook data from Facebook Posts Scraper to standard format
        
        Facebook Posts Scraper returns posts with fields like:
        - postText, postUrl, likes, comments, shares, time, etc.
        """
        transformed = []

        for item in raw_data:
            try:
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
        """
        Transform single Facebook post from Facebook Posts Scraper
        
        Expected fields: postText, postUrl, likes, comments, shares, time, etc.
        """
        # Extract metrics
        likes = post.get("likes", 0)
        comments = post.get("comments", 0)
        shares = post.get("shares", 0)
        
        # Get post ID from URL or use a generated one
        post_url = post.get("postUrl") or post.get("url", "")
        post_id = post.get("postId") or post_url.split("/")[-1] if post_url else str(uuid.uuid4())
        
        return {
            "source": "facebook",
            "source_id": post_id,
            "page": page_name or post.get("pageName", ""),
            "author": post.get("profileName") or post.get("author", ""),
            "content": post.get("postText") or post.get("text", ""),
            "metrics": {
                "likes": likes,
                "comments": comments,
                "shares": shares,
                "reactions": post.get("reactions", 0)
            },
            "media_type": "video" if post.get("video") else ("image" if post.get("image") else "text"),
            "has_video": bool(post.get("video")),
            "has_image": bool(post.get("image")),
            "images": post.get("images", []),
            "video_url": post.get("video"),
            "posted_at": post.get("time") or post.get("timestamp"),
            "collected_at": datetime.utcnow().isoformat(),
            "url": post_url,
            "geo_location": "Nigeria"
        }

    def _transform_twitter_data(
        self,
        raw_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Transform Twitter (X) data from Tweet Scraper V2 to standard format
        
        Tweet Scraper V2 actual output format:
        - id, url, fullText/text
        - likeCount, retweetCount, replyCount, quoteCount, viewCount
        - author{userName, name, id, followers, etc.}
        - entities{hashtags, user_mentions, urls}
        - createdAt, lang, isRetweet, isQuote
        """
        transformed = []

        for item in raw_data:
            try:
                # Extract author info (nested object)
                author = item.get("author", {})
                
                # Extract metrics (exact field names from Apify)
                like_count = item.get("likeCount", 0)
                retweet_count = item.get("retweetCount", 0)
                reply_count = item.get("replyCount", 0)
                view_count = item.get("viewCount", 0)
                quote_count = item.get("quoteCount", 0)
                
                # Extract text content (fullText is primary, fallback to text)
                content = item.get("fullText") or item.get("text", "")
                
                # Extract entities
                entities = item.get("entities", {})
                
                # Extract hashtags (array of objects with 'text' field)
                hashtags_raw = entities.get("hashtags", [])
                hashtags = [h.get("text", "") for h in hashtags_raw] if isinstance(hashtags_raw, list) else []
                
                # Extract mentions (array of objects)
                mentions_raw = entities.get("user_mentions", [])
                mentions = [m.get("screen_name", "") for m in mentions_raw] if isinstance(mentions_raw, list) else []
                
                # Extract tweet ID
                tweet_id = item.get("id", "")
                
                # Extract username (author.userName is the @ handle)
                username = author.get("userName", "") or author.get("screen_name", "")
                
                transformed_item = {
                    "source": "twitter",
                    "source_id": str(tweet_id),
                    "author": username,
                    "author_name": author.get("name", ""),
                    "author_id": author.get("id", ""),
                    "author_followers": author.get("followers", 0),
                    "author_verified": author.get("isVerified", False) or author.get("isBlueVerified", False),
                    "content": content,
                    "metrics": {
                        "likes": like_count,
                        "retweets": retweet_count,
                        "replies": reply_count,
                        "quotes": quote_count,
                        "views": view_count
                    },
                    "hashtags": hashtags,
                    "mentions": mentions,
                    "posted_at": item.get("createdAt"),
                    "collected_at": datetime.utcnow().isoformat(),
                    "url": item.get("url") or item.get("twitterUrl", ""),
                    "is_retweet": item.get("isRetweet", False),
                    "is_quote": item.get("isQuote", False),
                    "is_reply": item.get("isReply", False),
                    "language": item.get("lang", ""),
                    "source_app": item.get("source", ""),
                    "geo_location": "Nigeria",
                    "raw_data": item  # CRITICAL: Store complete raw data
                }
                transformed.append(transformed_item)
            except Exception as e:
                logger.error(f"Error transforming Twitter item: {e}")
                logger.error(f"Problematic item: {item}")
                continue

        return transformed

    async def scrape_nigerian_social_media(
        self,
        platforms: List[str] = None,
        items_per_platform: int = 50
    ) -> Dict[str, Any]:
        """
        Comprehensive scraping across Twitter and Facebook for Nigerian content
        
        Only supports Twitter and Facebook platforms as per requirements.

        Args:
            platforms: List of platforms to scrape (default: ["twitter", "facebook"])
            items_per_platform: Number of items to scrape per platform

        Returns:
            Aggregated social media data from Twitter and Facebook
        """
        try:
            if platforms is None:
                platforms = ["twitter", "facebook"]
            
            # Filter to only supported platforms
            supported = ["twitter", "facebook"]
            platforms = [p for p in platforms if p in supported]

            logger.info(f"Starting Nigerian social media scraping for: {platforms}")

            results = {
                "platforms": {},
                "timestamp": datetime.utcnow().isoformat(),
                "region": "Nigeria"
            }

            # Nigerian accounts/pages to monitor
            nigerian_sources = {
                "twitter": [
                    "#Nigeria",
                    "#Lagos", 
                    "#Abuja",
                    "#Naija"
                ],
                "facebook": [
                    "https://www.facebook.com/legit.ng",
                    "https://www.facebook.com/lindaikejisblog",
                    "https://www.facebook.com/NigeriaNewsdesk"
                ]
            }

            # Scrape each platform
            for platform in platforms:
                try:
                    if platform == "twitter":
                        # Scrape Twitter using search terms
                        search_terms = nigerian_sources["twitter"]
                        data = await self.scrape_twitter_search(
                            search_queries=search_terms,
                            max_tweets=items_per_platform
                        )
                        results["platforms"]["twitter"] = data

                    elif platform == "facebook":
                        # Scrape first Facebook page
                        page_url = nigerian_sources["facebook"][0]
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

            logger.info("Nigerian social media scraping completed")
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
