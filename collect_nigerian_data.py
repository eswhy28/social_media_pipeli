#!/usr/bin/env python3
"""
Nigerian Data Collection Pipeline
Automated script to collect trending Nigerian content from all sources
"""

import asyncio
import sys
import logging
from datetime import datetime
from typing import Dict, List
import httpx

# Add project to path
sys.path.insert(0, '.')

from app.config import settings
from app.database import AsyncSessionLocal
from app.nigerian_topics_config import (
    NIGERIAN_TRENDING_CATEGORIES,
    NIGERIAN_NEWS_SOURCES,
    NIGERIAN_LOCATIONS,
    get_priority_topics_for_time,
    build_twitter_search_query
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000"


class NigerianDataCollector:
    """Collects Nigerian trending data from all sources"""

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=60.0)
        self.collected_stats = {
            "google_trends": 0,
            "tiktok": 0,
            "facebook": 0,
            "twitter": 0,
            "total": 0
        }

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

    async def collect_google_trends(self) -> Dict:
        """Collect Google Trends data for Nigeria"""
        logger.info("📊 Collecting Google Trends data...")

        try:
            # Get trending searches
            response = await self.client.get(
                f"{BASE_URL}/api/v1/social-media/trends/trending",
                params={"region": "NG"}
            )

            if response.status_code == 200:
                data = response.json()
                count = len(data.get("data", {}).get("trending_searches", []))
                self.collected_stats["google_trends"] += count
                logger.info(f"   ✅ Collected {count} trending searches")
                return data
            else:
                logger.error(f"   ❌ Failed: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"   ❌ Error collecting trends: {e}")
            return None

    async def analyze_trending_keywords(self) -> Dict:
        """Analyze Nigerian trending keywords"""
        logger.info("🔍 Analyzing trending keywords...")

        try:
            # Get priority topics for current time
            priority_topics = get_priority_topics_for_time()
            logger.info(f"   Priority topics: {', '.join(priority_topics)}")

            # Get keywords from first priority topic
            category = priority_topics[0] if priority_topics else "politics"
            keywords = NIGERIAN_TRENDING_CATEGORIES[category]["keywords"][:5]

            response = await self.client.post(
                f"{BASE_URL}/api/v1/social-media/trends/analyze",
                json={
                    "keywords": keywords,
                    "timeframe": "today 3-m",
                    "include_related": True,
                    "include_regional": True
                }
            )

            if response.status_code == 200:
                data = response.json()
                logger.info(f"   ✅ Analyzed {len(keywords)} keywords")
                self.collected_stats["google_trends"] += len(keywords)
                return data
            else:
                logger.error(f"   ❌ Failed: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"   ❌ Error analyzing keywords: {e}")
            return None

    async def collect_tiktok_nigerian_content(self) -> Dict:
        """Collect TikTok content for Nigerian hashtags"""
        logger.info("🎵 Collecting TikTok Nigerian content...")

        try:
            response = await self.client.get(
                f"{BASE_URL}/api/v1/social-media/tiktok/monitor",
                params={"max_videos": 20}
            )

            if response.status_code == 200:
                data = response.json()
                videos = data.get("data", {}).get("videos", [])
                self.collected_stats["tiktok"] += len(videos)
                logger.info(f"   ✅ Collected {len(videos)} TikTok videos")
                return data
            else:
                logger.error(f"   ❌ Failed: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"   ❌ Error collecting TikTok: {e}")
            return None

    async def collect_facebook_nigerian_pages(self) -> Dict:
        """Collect Facebook posts from Nigerian news pages"""
        logger.info("📘 Collecting Facebook Nigerian pages...")

        try:
            response = await self.client.get(
                f"{BASE_URL}/api/v1/social-media/facebook/monitor",
                params={"pages_per_source": 2}
            )

            if response.status_code == 200:
                data = response.json()
                posts = data.get("data", {}).get("posts", [])
                self.collected_stats["facebook"] += len(posts)
                logger.info(f"   ✅ Collected {len(posts)} Facebook posts")
                return data
            else:
                logger.error(f"   ❌ Failed: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"   ❌ Error collecting Facebook: {e}")
            return None

    async def collect_twitter_via_apify(self) -> Dict:
        """Collect Twitter data using Apify (Nigerian accounts)"""
        logger.info("🐦 Collecting Twitter data via Apify...")

        try:
            # Use Apify for Twitter scraping
            response = await self.client.post(
                f"{BASE_URL}/api/v1/social-media/apify/scrape",
                json={
                    "platform": "twitter",
                    "target": "NigeriaStories",  # Nigerian news account
                    "limit": 20
                }
            )

            if response.status_code == 200:
                data = response.json()
                tweets = data.get("data", {}).get("tweets", [])
                self.collected_stats["twitter"] += len(tweets)
                logger.info(f"   ✅ Collected {len(tweets)} tweets")
                return data
            else:
                logger.warning(f"   ⚠️  Twitter collection skipped (status: {response.status_code})")
                return None

        except Exception as e:
            logger.warning(f"   ⚠️  Twitter collection skipped: {e}")
            return None

    async def run_comprehensive_analysis(self, text_samples: List[str]) -> Dict:
        """Run AI analysis on collected content"""
        logger.info("🤖 Running AI analysis on collected content...")

        analyzed_count = 0
        for text in text_samples[:5]:  # Analyze first 5 samples
            try:
                response = await self.client.post(
                    f"{BASE_URL}/api/v1/ai/analyze/comprehensive",
                    json={"text": text}
                )

                if response.status_code == 200:
                    analyzed_count += 1

            except Exception as e:
                logger.debug(f"   Analysis skipped for one text: {e}")

        if analyzed_count > 0:
            logger.info(f"   ✅ Analyzed {analyzed_count} text samples")
        else:
            logger.info(f"   ℹ️  AI analysis not available yet")

        return {"analyzed": analyzed_count}

    async def collect_all(self):
        """Run complete data collection pipeline"""
        logger.info("\n" + "=" * 60)
        logger.info("🇳🇬 NIGERIAN DATA COLLECTION PIPELINE")
        logger.info("=" * 60)
        logger.info(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        # 1. Google Trends
        await self.collect_google_trends()
        await asyncio.sleep(2)

        # 2. Analyze trending keywords
        await self.analyze_trending_keywords()
        await asyncio.sleep(2)

        # 3. TikTok Nigerian content
        tiktok_data = await self.collect_tiktok_nigerian_content()
        await asyncio.sleep(2)

        # 4. Facebook Nigerian pages
        facebook_data = await self.collect_facebook_nigerian_pages()
        await asyncio.sleep(2)

        # 5. Twitter via Apify
        twitter_data = await self.collect_twitter_via_apify()
        await asyncio.sleep(2)

        # 6. Run AI analysis on samples
        text_samples = []
        if tiktok_data:
            videos = tiktok_data.get("data", {}).get("videos", [])
            text_samples.extend([v.get("description", "") for v in videos[:3]])

        if facebook_data:
            posts = facebook_data.get("data", {}).get("posts", [])
            text_samples.extend([p.get("text", "") for p in posts[:3]])

        if text_samples:
            await self.run_comprehensive_analysis(text_samples)

        # Calculate total
        self.collected_stats["total"] = sum([
            self.collected_stats["google_trends"],
            self.collected_stats["tiktok"],
            self.collected_stats["facebook"],
            self.collected_stats["twitter"]
        ])

        # Print summary
        logger.info("\n" + "=" * 60)
        logger.info("📊 COLLECTION SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Google Trends: {self.collected_stats['google_trends']}")
        logger.info(f"TikTok Videos: {self.collected_stats['tiktok']}")
        logger.info(f"Facebook Posts: {self.collected_stats['facebook']}")
        logger.info(f"Twitter Tweets: {self.collected_stats['twitter']}")
        logger.info(f"Total Items: {self.collected_stats['total']}")
        logger.info("=" * 60)
        logger.info(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")


async def main():
    """Main function"""
    print("\n🇳🇬 Nigerian Data Collection Pipeline\n")
    print("This script will collect trending Nigerian content from:")
    print("  • Google Trends (Nigeria region)")
    print("  • TikTok (Nigerian hashtags)")
    print("  • Facebook (Nigerian news pages)")
    print("  • Twitter (via Apify, Nigerian accounts)")
    print("\nMake sure the API server is running at http://localhost:8000\n")

    # input("Press Enter to start collection...")  # Commented for non-interactive execution

    collector = NigerianDataCollector()

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