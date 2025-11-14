"""
Dynamic Hashtag Discovery Service
Automatically discovers and tracks trending Nigerian hashtags in real-time
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from collections import Counter
import re
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
import asyncio

from app.models.social_media_sources import ApifyScrapedData, TikTokContent, FacebookContent

logger = logging.getLogger(__name__)


class HashtagDiscoveryService:
    """
    Discovers trending hashtags dynamically from:
    1. Google Trends API (Nigeria)
    2. Collected TikTok content
    3. Collected Facebook content
    4. Collected Twitter content
    5. Real-time social media monitoring
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.trend_threshold = 5  # Minimum occurrences to be considered trending

    async def get_trending_google_topics(self, region='NG', limit=20) -> List[str]:
        """
        Get trending topics from Google Trends for Nigeria

        Returns:
            List of trending search terms
        """
        try:
            from pytrends.request import TrendReq

            pytrends = TrendReq(hl='en-NG', tz=60)

            # Get trending searches for Nigeria
            trending_searches = pytrends.trending_searches(pn='nigeria')

            if trending_searches is not None and not trending_searches.empty:
                # Convert to hashtag format (lowercase, no spaces)
                hashtags = []
                for term in trending_searches[0].head(limit):
                    # Convert to hashtag format
                    hashtag = self._term_to_hashtag(term)
                    if hashtag:
                        hashtags.append(hashtag)

                logger.info(f"Found {len(hashtags)} trending topics from Google Trends")
                return hashtags

            return []

        except Exception as e:
            logger.error(f"Error getting Google Trends: {e}")
            return []

    async def get_trending_from_collected_content(
        self,
        hours_back: int = 24,
        min_occurrences: int = 5,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Extract trending hashtags from recently collected content

        Args:
            hours_back: How many hours of data to analyze
            min_occurrences: Minimum times a hashtag must appear
            limit: Maximum hashtags to return

        Returns:
            List of hashtag dictionaries with counts and engagement
        """
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours_back)

            # Get hashtags from Apify data (Twitter, TikTok, Facebook)
            query = select(
                ApifyScrapedData.hashtags,
                ApifyScrapedData.metrics_json,
                ApifyScrapedData.collected_at
            ).where(
                ApifyScrapedData.collected_at >= cutoff_time
            )

            result = await self.db.execute(query)
            records = result.all()

            # Count hashtag occurrences and engagement
            hashtag_stats = {}

            for hashtags, metrics, collected_at in records:
                if not hashtags:
                    continue

                for tag in hashtags:
                    tag_lower = tag.lower()

                    if tag_lower not in hashtag_stats:
                        hashtag_stats[tag_lower] = {
                            'count': 0,
                            'total_engagement': 0,
                            'last_seen': collected_at,
                            'platforms': set()
                        }

                    hashtag_stats[tag_lower]['count'] += 1

                    # Add engagement metrics
                    if metrics:
                        engagement = (
                            metrics.get('likes', 0) +
                            metrics.get('comments', 0) +
                            metrics.get('shares', 0) +
                            metrics.get('retweets', 0) +
                            metrics.get('views', 0) // 100  # Scale down views
                        )
                        hashtag_stats[tag_lower]['total_engagement'] += engagement

                    if collected_at > hashtag_stats[tag_lower]['last_seen']:
                        hashtag_stats[tag_lower]['last_seen'] = collected_at

            # Filter and sort by engagement and count
            trending = []
            for tag, stats in hashtag_stats.items():
                if stats['count'] >= min_occurrences:
                    # Calculate trend score (combination of count and engagement)
                    trend_score = (stats['count'] * 10) + (stats['total_engagement'] / 1000)

                    trending.append({
                        'hashtag': tag,
                        'count': stats['count'],
                        'total_engagement': stats['total_engagement'],
                        'trend_score': trend_score,
                        'last_seen': stats['last_seen']
                    })

            # Sort by trend score
            trending.sort(key=lambda x: x['trend_score'], reverse=True)

            logger.info(f"Found {len(trending)} trending hashtags from collected content")
            return trending[:limit]

        except Exception as e:
            logger.error(f"Error extracting trending hashtags: {e}")
            return []

    async def discover_nigerian_hashtags(
        self,
        include_google_trends: bool = True,
        include_collected: bool = True,
        limit: int = 50
    ) -> List[str]:
        """
        Discover currently trending Nigerian hashtags from all sources

        Args:
            include_google_trends: Include Google Trends data
            include_collected: Include analysis of collected content
            limit: Maximum hashtags to return

        Returns:
            List of trending hashtags
        """
        all_hashtags = []
        hashtag_scores = {}

        # 1. Get from Google Trends
        if include_google_trends:
            google_hashtags = await self.get_trending_google_topics(limit=30)
            for tag in google_hashtags:
                hashtag_scores[tag] = hashtag_scores.get(tag, 0) + 100  # High weight for Google Trends
                all_hashtags.append(tag)

        # 2. Get from collected content
        if include_collected:
            trending_data = await self.get_trending_from_collected_content(
                hours_back=24,
                min_occurrences=3,
                limit=50
            )

            for item in trending_data:
                tag = item['hashtag']
                score = item['trend_score']
                hashtag_scores[tag] = hashtag_scores.get(tag, 0) + score
                all_hashtags.append(tag)

        # 3. Add core Nigerian hashtags (always include these)
        core_hashtags = [
            'nigeria', 'naija', 'lagos', 'abuja', '9ja',
            'afrobeats', 'nollywood', 'tinubu', 'nigerianpolitics'
        ]
        for tag in core_hashtags:
            if tag not in hashtag_scores:
                hashtag_scores[tag] = 50  # Medium weight for core tags
                all_hashtags.append(tag)

        # Sort by score and remove duplicates
        unique_hashtags = list(set(all_hashtags))
        sorted_hashtags = sorted(
            unique_hashtags,
            key=lambda x: hashtag_scores.get(x, 0),
            reverse=True
        )

        result = sorted_hashtags[:limit]
        logger.info(f"Discovered {len(result)} trending Nigerian hashtags")

        return result

    async def get_hashtags_by_category(
        self,
        category: str,
        limit: int = 20
    ) -> List[str]:
        """
        Get trending hashtags for a specific category

        Args:
            category: Category name (politics, entertainment, sports, etc.)
            limit: Maximum hashtags to return

        Returns:
            List of category-specific hashtags
        """
        # Category keywords for filtering
        category_keywords = {
            'politics': ['politic', 'government', 'election', 'tinubu', 'apc', 'pdp', 'inec'],
            'entertainment': ['music', 'movie', 'nollywood', 'afrobeat', 'bbnaija', 'celeb'],
            'sports': ['football', 'soccer', 'eagles', 'sport', 'afcon', 'osimhen'],
            'economy': ['naira', 'dollar', 'fuel', 'price', 'economy', 'business'],
            'tech': ['tech', 'startup', 'innovation', 'fintech', 'digital'],
            'security': ['security', 'police', 'military', 'crime', 'safety'],
            'education': ['education', 'school', 'university', 'asuu', 'student'],
        }

        keywords = category_keywords.get(category.lower(), [])
        if not keywords:
            return await self.discover_nigerian_hashtags(limit=limit)

        # Get all trending hashtags
        all_trending = await self.discover_nigerian_hashtags(limit=100)

        # Filter by category keywords
        category_hashtags = []
        for tag in all_trending:
            if any(keyword in tag.lower() for keyword in keywords):
                category_hashtags.append(tag)

        return category_hashtags[:limit]

    async def get_engagement_metrics_for_hashtag(
        self,
        hashtag: str,
        hours_back: int = 24
    ) -> Dict[str, Any]:
        """
        Get engagement metrics for a specific hashtag

        Args:
            hashtag: Hashtag to analyze
            hours_back: Hours of data to analyze

        Returns:
            Dictionary with engagement metrics
        """
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours_back)

            # Query posts with this hashtag
            query = select(
                ApifyScrapedData.metrics_json,
                ApifyScrapedData.platform
            ).where(
                ApifyScrapedData.hashtags.contains([hashtag.lower()]),
                ApifyScrapedData.collected_at >= cutoff_time
            )

            result = await self.db.execute(query)
            records = result.all()

            total_engagement = {
                'likes': 0,
                'comments': 0,
                'shares': 0,
                'views': 0,
                'posts_count': len(records),
                'platforms': set()
            }

            for metrics, platform in records:
                if metrics:
                    total_engagement['likes'] += metrics.get('likes', 0)
                    total_engagement['comments'] += metrics.get('comments', 0)
                    total_engagement['shares'] += metrics.get('shares', 0)
                    total_engagement['views'] += metrics.get('views', 0)
                    total_engagement['platforms'].add(platform)

            total_engagement['platforms'] = list(total_engagement['platforms'])
            total_engagement['total_engagement'] = (
                total_engagement['likes'] +
                total_engagement['comments'] +
                total_engagement['shares']
            )

            # Calculate engagement rate
            if total_engagement['views'] > 0:
                total_engagement['engagement_rate'] = (
                    total_engagement['total_engagement'] / total_engagement['views'] * 100
                )
            else:
                total_engagement['engagement_rate'] = 0

            return total_engagement

        except Exception as e:
            logger.error(f"Error getting engagement for #{hashtag}: {e}")
            return {}

    def _term_to_hashtag(self, term: str) -> Optional[str]:
        """
        Convert a search term to hashtag format

        Args:
            term: Search term

        Returns:
            Hashtag string or None
        """
        if not term:
            return None

        # Remove special characters, keep only alphanumeric
        cleaned = re.sub(r'[^a-zA-Z0-9\s]', '', term)

        # Remove spaces and convert to lowercase
        hashtag = cleaned.replace(' ', '').lower()

        # Filter out very short hashtags
        if len(hashtag) < 3:
            return None

        return hashtag

    async def update_trending_cache(self) -> Dict[str, Any]:
        """
        Update the trending hashtags cache

        Returns:
            Dictionary with trending hashtags by category
        """
        try:
            trending_cache = {
                'all': await self.discover_nigerian_hashtags(limit=50),
                'politics': await self.get_hashtags_by_category('politics', limit=20),
                'entertainment': await self.get_hashtags_by_category('entertainment', limit=20),
                'sports': await self.get_hashtags_by_category('sports', limit=20),
                'economy': await self.get_hashtags_by_category('economy', limit=20),
                'updated_at': datetime.utcnow().isoformat()
            }

            logger.info("Updated trending hashtags cache")
            return trending_cache

        except Exception as e:
            logger.error(f"Error updating trending cache: {e}")
            return {}


# Singleton instance
_hashtag_service = None


def get_hashtag_discovery_service(db: AsyncSession) -> HashtagDiscoveryService:
    """Get hashtag discovery service instance"""
    return HashtagDiscoveryService(db)