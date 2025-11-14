#!/usr/bin/env python3
"""
Simplified Data Collection - Working Sources Only
Focuses on sources that are actually working (Apify)
"""

import asyncio
import sys
import logging
from datetime import datetime
import httpx

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000"


class WorkingDataCollector:
    """Collects data from working sources only"""

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=120.0)
        self.collected_stats = {
            "twitter": 0,
            "tiktok": 0,
            "facebook": 0,
            "total": 0
        }

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

    async def collect_twitter_apify(self, targets: list, limit: int = 20) -> dict:
        """Collect Twitter data using Apify"""
        logger.info("🐦 Collecting Twitter data via Apify...")

        all_tweets = []
        for target in targets:
            try:
                logger.info(f"   Scraping Twitter account: @{target}")
                response = await self.client.post(
                    f"{BASE_URL}/api/v1/social-media/apify/scrape",
                    json={
                        "platform": "twitter",
                        "target": target,
                        "limit": limit
                    }
                )

                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        tweets = data.get("data", {}).get("tweets", [])
                        all_tweets.extend(tweets)
                        logger.info(f"   ✅ Collected {len(tweets)} tweets from @{target}")
                    else:
                        logger.warning(f"   ⚠️  No tweets from @{target}: {data.get('error', 'Unknown error')}")
                else:
                    logger.warning(f"   ⚠️  Failed to scrape @{target}: HTTP {response.status_code}")

            except Exception as e:
                logger.error(f"   ❌ Error scraping @{target}: {e}")

            await asyncio.sleep(3)  # Rate limiting

        self.collected_stats["twitter"] = len(all_tweets)
        logger.info(f"   📊 Total Twitter: {len(all_tweets)} tweets")
        return {"tweets": all_tweets, "count": len(all_tweets)}

    async def collect_tiktok_apify(self, hashtags: list, limit: int = 20) -> dict:
        """Collect TikTok data using Apify"""
        logger.info("🎵 Collecting TikTok data via Apify...")

        all_videos = []
        for hashtag in hashtags:
            try:
                logger.info(f"   Scraping TikTok hashtag: #{hashtag}")
                response = await self.client.post(
                    f"{BASE_URL}/api/v1/social-media/apify/scrape",
                    json={
                        "platform": "tiktok",
                        "target": f"#{hashtag}",
                        "limit": limit
                    }
                )

                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        videos = data.get("data", {}).get("videos", [])
                        all_videos.extend(videos)
                        logger.info(f"   ✅ Collected {len(videos)} videos from #{hashtag}")
                    else:
                        logger.warning(f"   ⚠️  No videos from #{hashtag}: {data.get('error', 'Unknown error')}")
                else:
                    logger.warning(f"   ⚠️  Failed to scrape #{hashtag}: HTTP {response.status_code}")

            except Exception as e:
                logger.error(f"   ❌ Error scraping #{hashtag}: {e}")

            await asyncio.sleep(3)  # Rate limiting

        self.collected_stats["tiktok"] = len(all_videos)
        logger.info(f"   📊 Total TikTok: {len(all_videos)} videos")
        return {"videos": all_videos, "count": len(all_videos)}

    async def collect_facebook_apify(self, pages: list, limit: int = 20) -> dict:
        """Collect Facebook data using Apify"""
        logger.info("📘 Collecting Facebook data via Apify...")

        all_posts = []
        for page in pages:
            try:
                logger.info(f"   Scraping Facebook page: {page}")
                response = await self.client.post(
                    f"{BASE_URL}/api/v1/social-media/apify/scrape",
                    json={
                        "platform": "facebook",
                        "target": f"https://facebook.com/{page}",
                        "limit": limit
                    }
                )

                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        posts = data.get("data", {}).get("posts", [])
                        all_posts.extend(posts)
                        logger.info(f"   ✅ Collected {len(posts)} posts from {page}")
                    else:
                        logger.warning(f"   ⚠️  No posts from {page}: {data.get('error', 'Unknown error')}")
                else:
                    logger.warning(f"   ⚠️  Failed to scrape {page}: HTTP {response.status_code}")

            except Exception as e:
                logger.error(f"   ❌ Error scraping {page}: {e}")

            await asyncio.sleep(3)  # Rate limiting

        self.collected_stats["facebook"] = len(all_posts)
        logger.info(f"   📊 Total Facebook: {len(all_posts)} posts")
        return {"posts": all_posts, "count": len(all_posts)}

    async def collect_all(self):
        """Run complete data collection from working sources"""
        logger.info("\n" + "=" * 70)
        logger.info("🚀 WORKING DATA SOURCES COLLECTION - Via Apify")
        logger.info("=" * 70)
        logger.info(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        # Nigerian Twitter accounts
        twitter_accounts = [
            "NigeriaStories",
            "ChannelsTV",
            "PremiumTimesng",
            "thecableng"
        ]

        # Nigerian TikTok hashtags
        tiktok_hashtags = [
            "nigeria",
            "naija",
            "lagos"
        ]

        # Nigerian Facebook pages
        facebook_pages = [
            "legit.ng",
            "lindaikejisblog"
        ]

        # 1. Twitter via Apify
        twitter_data = await self.collect_twitter_apify(twitter_accounts, limit=10)
        await asyncio.sleep(5)

        # 2. TikTok via Apify
        tiktok_data = await self.collect_tiktok_apify(tiktok_hashtags, limit=10)
        await asyncio.sleep(5)

        # 3. Facebook via Apify
        facebook_data = await self.collect_facebook_apify(facebook_pages, limit=10)

        # Calculate total
        self.collected_stats["total"] = sum([
            self.collected_stats["twitter"],
            self.collected_stats["tiktok"],
            self.collected_stats["facebook"]
        ])

        # Print summary
        logger.info("\n" + "=" * 70)
        logger.info("📊 COLLECTION SUMMARY")
        logger.info("=" * 70)
        logger.info(f"Twitter Tweets: {self.collected_stats['twitter']}")
        logger.info(f"TikTok Videos: {self.collected_stats['tiktok']}")
        logger.info(f"Facebook Posts: {self.collected_stats['facebook']}")
        logger.info(f"Total Items: {self.collected_stats['total']}")
        logger.info("=" * 70)
        logger.info(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        if self.collected_stats["total"] > 0:
            logger.info("✅ SUCCESS: Data collection working!")
        else:
            logger.warning("⚠️  WARNING: No data collected. Check Apify account and actor configurations.")


async def main():
    """Main function"""
    print("\n🚀 Simplified Data Collection - Working Sources Only\n")
    print("This script collects data using Apify actors:")
    print("  • Twitter (via apidojo/tweet-scraper)")
    print("  • TikTok (via clockworks/tiktok-scraper)")
    print("  • Facebook (via apify/facebook-pages-scraper)")
    print("\nMake sure:")
    print("  1. API server is running at http://localhost:8000")
    print("  2. Apify API token is configured in .env")
    print("  3. You have enough Apify credits\n")

    collector = WorkingDataCollector()

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
