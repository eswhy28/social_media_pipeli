#!/usr/bin/env python3
"""
Dynamic Hashtag-Based Data Collection
Uses real-time trending hashtag discovery for targeted Nigerian content collection
"""

import asyncio
import sys
import logging
from datetime import datetime
import httpx
from typing import List, Dict, Any

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000"


class DynamicHashtagCollector:
    """Collects data using dynamically discovered trending hashtags"""

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=120.0)
        self.collected_stats = {
            "twitter": 0,
            "total": 0,
            "trending_hashtags": []
        }

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

    async def get_trending_hashtags(self, limit: int = 20) -> List[str]:
        """
        Get currently trending Nigerian hashtags from the API

        Returns:
            List of trending hashtags
        """
        try:
            logger.info("📊 Discovering trending Nigerian hashtags...")

            response = await self.client.get(
                f"{BASE_URL}/api/v1/social-media/hashtags/trending",
                params={
                    "include_google_trends": True,
                    "include_collected": True,
                    "limit": limit
                }
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    hashtags = data.get("data", {}).get("trending_hashtags", [])
                    logger.info(f"   ✅ Found {len(hashtags)} trending hashtags")

                    # Log first 10 for visibility
                    if hashtags:
                        logger.info(f"   Top 10: {', '.join(hashtags[:10])}")

                    return hashtags
                else:
                    logger.warning("   ⚠️  API returned success=False")
            else:
                logger.warning(f"   ⚠️  HTTP {response.status_code}")

        except Exception as e:
            logger.error(f"   ❌ Error getting trending hashtags: {e}")

        # Fallback to core Nigerian hashtags
        logger.info("   Using fallback core Nigerian hashtags")
        return ["nigeria", "naija", "lagos", "abuja", "nigerianpolitics"]

    async def get_hashtag_engagement(self, hashtag: str) -> Dict[str, Any]:
        """
        Get engagement metrics for a specific hashtag

        Returns:
            Dictionary with engagement metrics
        """
        try:
            response = await self.client.get(
                f"{BASE_URL}/api/v1/social-media/hashtags/engagement/{hashtag}",
                params={"hours_back": 24}
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    return data.get("data", {}).get("metrics", {})
        except Exception as e:
            logger.error(f"Error getting engagement for #{hashtag}: {e}")

        return {}

    async def collect_twitter_with_dynamic_hashtags(
        self,
        hashtags: List[str],
        tweets_per_hashtag: int = 10
    ) -> Dict[str, Any]:
        """
        Collect Twitter data using dynamically discovered hashtags

        Args:
            hashtags: List of trending hashtags
            tweets_per_hashtag: Number of tweets per hashtag

        Returns:
            Collection results
        """
        logger.info(f"🐦 Collecting Twitter data for {len(hashtags)} trending hashtags...")

        all_tweets = []
        hashtag_stats = []

        for hashtag in hashtags[:10]:  # Limit to top 10 to avoid excessive API usage
            try:
                logger.info(f"   Scraping Twitter for #{hashtag}...")

                # Collect tweets via Apify
                response = await self.client.post(
                    f"{BASE_URL}/api/v1/social-media/apify/scrape",
                    json={
                        "platform": "twitter",
                        "target": f"#{hashtag}",
                        "limit": tweets_per_hashtag
                    }
                )

                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        tweets = data.get("data", {}).get("tweets", [])
                        all_tweets.extend(tweets)

                        # Get engagement metrics
                        engagement = await self.get_hashtag_engagement(hashtag)

                        hashtag_stats.append({
                            "hashtag": hashtag,
                            "tweets_collected": len(tweets),
                            "engagement": engagement
                        })

                        logger.info(
                            f"   ✅ #{hashtag}: {len(tweets)} tweets, "
                            f"{engagement.get('total_engagement', 0)} total engagement"
                        )
                    else:
                        logger.warning(f"   ⚠️  No tweets for #{hashtag}")
                else:
                    logger.warning(f"   ⚠️  Failed #{hashtag}: HTTP {response.status_code}")

            except Exception as e:
                logger.error(f"   ❌ Error scraping #{hashtag}: {e}")

            await asyncio.sleep(3)  # Rate limiting

        self.collected_stats["twitter"] = len(all_tweets)
        self.collected_stats["trending_hashtags"] = hashtag_stats

        logger.info(f"   📊 Total Twitter: {len(all_tweets)} tweets from {len(hashtag_stats)} hashtags")

        return {
            "tweets": all_tweets,
            "count": len(all_tweets),
            "hashtag_stats": hashtag_stats
        }

    async def update_hashtag_cache(self):
        """Trigger hashtag cache update for future collections"""
        try:
            logger.info("♻️  Updating hashtag cache...")

            response = await self.client.post(
                f"{BASE_URL}/api/v1/social-media/hashtags/update-cache"
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    logger.info("   ✅ Hashtag cache update triggered")
                    return True
        except Exception as e:
            logger.error(f"   ❌ Error updating cache: {e}")

        return False

    async def collect_all(self):
        """Run complete data collection using dynamic hashtags"""
        logger.info("\n" + "=" * 80)
        logger.info("🚀 DYNAMIC HASHTAG-BASED COLLECTION")
        logger.info("=" * 80)
        logger.info(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        # 1. Get trending hashtags
        trending_hashtags = await self.get_trending_hashtags(limit=20)
        self.collected_stats["trending_hashtags"] = trending_hashtags

        if not trending_hashtags:
            logger.error("No trending hashtags found. Cannot proceed.")
            return

        await asyncio.sleep(2)

        # 2. Collect Twitter data using trending hashtags (Apify only for Twitter per user request)
        twitter_data = await self.collect_twitter_with_dynamic_hashtags(
            hashtags=trending_hashtags,
            tweets_per_hashtag=10
        )

        await asyncio.sleep(3)

        # 3. Update hashtag cache for next run
        await self.update_hashtag_cache()

        # Calculate total
        self.collected_stats["total"] = self.collected_stats["twitter"]

        # Print detailed summary
        logger.info("\n" + "=" * 80)
        logger.info("📊 COLLECTION SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Trending Hashtags Discovered: {len(trending_hashtags)}")
        logger.info(f"Twitter Tweets Collected: {self.collected_stats['twitter']}")
        logger.info(f"Total Items: {self.collected_stats['total']}")
        logger.info("\n📈 TOP HASHTAG PERFORMANCE:")

        for stat in twitter_data.get("hashtag_stats", [])[:5]:
            engagement = stat.get("engagement", {})
            logger.info(
                f"  #{stat['hashtag']}: "
                f"{stat['tweets_collected']} tweets, "
                f"{engagement.get('posts_count', 0)} total posts, "
                f"{engagement.get('total_engagement', 0):,} engagement"
            )

        logger.info("=" * 80)
        logger.info(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        if self.collected_stats["total"] > 0:
            logger.info("✅ SUCCESS: Dynamic hashtag collection working!")
            logger.info("💡 Hashtags are discovered in real-time from Google Trends and collected content")
        else:
            logger.warning("⚠️  WARNING: No data collected. Check Apify account and configuration.")


async def main():
    """Main function"""
    print("\n🚀 Dynamic Hashtag-Based Data Collection\n")
    print("This script:")
    print("  • Discovers currently trending Nigerian hashtags in real-time")
    print("  • Uses Google Trends API for Nigeria")
    print("  • Analyzes recently collected content for trending topics")
    print("  • Tracks engagement metrics (likes, comments, shares, views)")
    print("  • Collects Twitter data via Apify (per user requirement)")
    print("\nMake sure:")
    print("  1. API server is running at http://localhost:8000")
    print("  2. Apify API token is configured in .env")
    print("  3. PostgreSQL database is set up and running")
    print("  4. You have enough Apify credits\n")

    collector = DynamicHashtagCollector()

    try:
        await collector.collect_all()
        return 0
    except KeyboardInterrupt:
        logger.info("\n\n⚠️  Collection interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"\n\n❌ Error during collection: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        await collector.close()


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)