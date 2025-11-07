"""
Data Processing Pipeline Service
Handles data normalization, cleaning, and transformation for all social media sources
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import re
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert
import uuid

from app.models.social_media_sources import (
    GoogleTrendsData,
    TikTokContent,
    FacebookContent,
    ApifyScrapedData,
    SocialMediaAggregation
)

logger = logging.getLogger(__name__)


class DataPipelineService:
    """
    Service for processing and normalizing data from various social media sources
    Focused on Nigerian content detection and cleaning
    """

    def __init__(self, db: AsyncSession):
        """Initialize the data pipeline service"""
        self.db = db

        # Nigerian keywords for content detection
        self.nigerian_keywords = [
            'nigeria', 'nigerian', 'naija', '9ja', 'lagos', 'abuja', 'kano',
            'port harcourt', 'ibadan', 'kaduna', 'jos', 'warri', 'enugu',
            'calabar', 'benin', 'maiduguri', 'zaria', 'aba', 'ilorin',
            'super eagles', 'nollywood', 'afrobeat', 'jollof', 'bbn', 'bbnaija'
        ]

        # Nigerian states
        self.nigerian_states = [
            'abia', 'adamawa', 'akwa ibom', 'anambra', 'bauchi', 'bayelsa',
            'benue', 'borno', 'cross river', 'delta', 'ebonyi', 'edo', 'ekiti',
            'enugu', 'gombe', 'imo', 'jigawa', 'kaduna', 'kano', 'katsina',
            'kebbi', 'kogi', 'kwara', 'lagos', 'nasarawa', 'niger', 'ogun',
            'ondo', 'osun', 'oyo', 'plateau', 'rivers', 'sokoto', 'taraba',
            'yobe', 'zamfara', 'fct', 'abuja'
        ]

    def is_nigerian_content(self, text: str, location: str = None) -> bool:
        """
        Detect if content is related to Nigeria

        Args:
            text: Content text to analyze
            location: Location metadata

        Returns:
            Boolean indicating if content is Nigerian
        """
        if not text:
            return False

        text_lower = text.lower()

        # Check for Nigerian keywords
        for keyword in self.nigerian_keywords:
            if keyword in text_lower:
                return True

        # Check location if provided
        if location:
            location_lower = location.lower()
            for state in self.nigerian_states:
                if state in location_lower:
                    return True
            if 'nigeria' in location_lower:
                return True

        return False

    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text content

        Args:
            text: Raw text to clean

        Returns:
            Cleaned text
        """
        if not text:
            return ""

        # Remove URLs
        text = re.sub(r'http\S+|www.\S+', '', text)

        # Remove excessive whitespace
        text = ' '.join(text.split())

        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\.,!?\-@#]', '', text)

        return text.strip()

    def extract_hashtags(self, text: str) -> List[str]:
        """
        Extract hashtags from text

        Args:
            text: Text containing hashtags

        Returns:
            List of hashtags (without #)
        """
        if not text:
            return []

        hashtags = re.findall(r'#(\w+)', text)
        return list(set(hashtags))  # Remove duplicates

    def extract_mentions(self, text: str) -> List[str]:
        """
        Extract mentions from text

        Args:
            text: Text containing mentions

        Returns:
            List of mentions (without @)
        """
        if not text:
            return []

        mentions = re.findall(r'@(\w+)', text)
        return list(set(mentions))

    async def store_google_trends(
        self,
        trends_data: List[Dict[str, Any]]
    ) -> int:
        """
        Store Google Trends data in database

        Args:
            trends_data: List of trend data dictionaries

        Returns:
            Number of records stored
        """
        try:
            stored_count = 0

            for trend in trends_data:
                # Check if Nigerian content
                keyword = trend.get('keyword') or trend.get('term', '')
                if not self.is_nigerian_content(keyword, trend.get('region')):
                    continue

                trend_record = GoogleTrendsData(
                    id=str(uuid.uuid4()),
                    keyword=keyword,
                    trend_type=trend.get('trend_type', 'trending_search'),
                    data_json=trend.get('data', {}),
                    interest_value=trend.get('interest', 0),
                    rank=trend.get('rank'),
                    geo_region=trend.get('region', 'NG'),
                    sub_region=trend.get('sub_region'),
                    timeframe=trend.get('timeframe', 'today 3-m'),
                    trend_date=datetime.fromisoformat(trend.get('timestamp', datetime.utcnow().isoformat())),
                    collected_at=datetime.utcnow()
                )

                self.db.add(trend_record)
                stored_count += 1

            await self.db.commit()
            logger.info(f"Stored {stored_count} Google Trends records")
            return stored_count

        except Exception as e:
            logger.error(f"Error storing Google Trends data: {e}")
            await self.db.rollback()
            return 0

    async def store_tiktok_content(
        self,
        videos: List[Dict[str, Any]]
    ) -> int:
        """
        Store TikTok content in database

        Args:
            videos: List of TikTok video data

        Returns:
            Number of records stored
        """
        try:
            stored_count = 0

            for video in videos:
                video_id = video.get('video_id') or video.get('id')
                if not video_id:
                    continue

                # Check if already exists
                result = await self.db.execute(
                    select(TikTokContent).where(TikTokContent.id == video_id)
                )
                if result.scalar_one_or_none():
                    continue

                # Clean content
                description = self.clean_text(video.get('description', ''))

                # Filter Nigerian content
                if not self.is_nigerian_content(description, video.get('geo_location')):
                    continue

                # Extract hashtags
                hashtags = video.get('hashtags', [])
                if not hashtags and description:
                    hashtags = self.extract_hashtags(description)

                author = video.get('author', {})
                metrics = video.get('metrics', {})
                content = video.get('content', {})

                tiktok_record = TikTokContent(
                    id=video_id,
                    author_username=author.get('username'),
                    author_nickname=author.get('nickname'),
                    author_verified=author.get('verified', False),
                    author_follower_count=author.get('follower_count', 0),
                    description=description,
                    duration=content.get('duration', 0),
                    music_title=content.get('music', ''),
                    views=metrics.get('views', 0),
                    likes=metrics.get('likes', 0),
                    comments=metrics.get('comments', 0),
                    shares=metrics.get('shares', 0),
                    engagement_rate=video.get('engagement_rate', 0.0),
                    hashtags=hashtags,
                    geo_location=video.get('geo_location', 'Nigeria'),
                    posted_at=datetime.fromisoformat(video.get('created_at', datetime.utcnow().isoformat())),
                    collected_at=datetime.utcnow()
                )

                self.db.add(tiktok_record)
                stored_count += 1

            await self.db.commit()
            logger.info(f"Stored {stored_count} TikTok records")
            return stored_count

        except Exception as e:
            logger.error(f"Error storing TikTok data: {e}")
            await self.db.rollback()
            return 0

    async def store_facebook_content(
        self,
        posts: List[Dict[str, Any]]
    ) -> int:
        """
        Store Facebook content in database

        Args:
            posts: List of Facebook post data

        Returns:
            Number of records stored
        """
        try:
            stored_count = 0

            for post in posts:
                post_id = post.get('post_id') or post.get('id')
                if not post_id:
                    continue

                # Check if already exists
                result = await self.db.execute(
                    select(FacebookContent).where(FacebookContent.id == post_id)
                )
                if result.scalar_one_or_none():
                    continue

                # Get content
                content_data = post.get('content', {})
                text = content_data.get('text') or content_data.get('post_text', '')
                text = self.clean_text(text)

                # Filter Nigerian content
                if not self.is_nigerian_content(text, post.get('geo_location')):
                    continue

                metrics = post.get('metrics', {})
                timestamp = post.get('timestamp', {})
                media = post.get('media', {})

                facebook_record = FacebookContent(
                    id=post_id,
                    page_name=post.get('page'),
                    author=post.get('author'),
                    text=text,
                    post_text=text,
                    has_image=media.get('has_image', False) or content_data.get('has_image', False),
                    has_video=media.get('has_video', False) or content_data.get('has_video', False),
                    link=content_data.get('link'),
                    post_url=content_data.get('post_url') or post.get('url'),
                    likes=metrics.get('likes', 0),
                    comments=metrics.get('comments', 0),
                    shares=metrics.get('shares', 0),
                    total_engagement=metrics.get('total_engagement', 0),
                    engagement_score=metrics.get('engagement_score', 0.0),
                    reactions_json=metrics.get('reactions'),
                    images=media.get('images', []),
                    video_url=media.get('video'),
                    geo_location=post.get('geo_location', 'Nigeria'),
                    posted_at=datetime.fromisoformat(timestamp.get('posted_at', datetime.utcnow().isoformat())) if isinstance(timestamp.get('posted_at'), str) else timestamp.get('posted_at'),
                    collected_at=datetime.utcnow()
                )

                self.db.add(facebook_record)
                stored_count += 1

            await self.db.commit()
            logger.info(f"Stored {stored_count} Facebook records")
            return stored_count

        except Exception as e:
            logger.error(f"Error storing Facebook data: {e}")
            await self.db.rollback()
            return 0

    async def store_apify_data(
        self,
        platform: str,
        data: List[Dict[str, Any]]
    ) -> int:
        """
        Store Apify scraped data in database

        Args:
            platform: Platform name (instagram, tiktok, twitter, etc.)
            data: List of scraped data

        Returns:
            Number of records stored
        """
        try:
            stored_count = 0

            for item in data:
                source_id = item.get('source_id') or item.get('id')

                # Clean content
                content = self.clean_text(item.get('content', ''))

                # Filter Nigerian content
                if not self.is_nigerian_content(content, item.get('location')):
                    continue

                # Extract hashtags and mentions
                hashtags = item.get('hashtags', [])
                if not hashtags and content:
                    hashtags = self.extract_hashtags(content)

                mentions = self.extract_mentions(content) if content else []

                apify_record = ApifyScrapedData(
                    id=str(uuid.uuid4()),
                    platform=platform,
                    source_id=source_id,
                    actor_id=item.get('actor_id'),
                    run_id=item.get('run_id'),
                    author=item.get('author'),
                    account_name=item.get('account_name'),
                    content=content,
                    content_type=item.get('media_type') or item.get('content_type', 'post'),
                    metrics_json=item.get('metrics', {}),
                    hashtags=hashtags,
                    mentions=mentions,
                    media_urls=item.get('media_urls', []),
                    raw_data=item,
                    location=item.get('location'),
                    geo_location=item.get('geo_location', 'Nigeria'),
                    posted_at=datetime.fromisoformat(item.get('posted_at', datetime.utcnow().isoformat())) if isinstance(item.get('posted_at'), str) else item.get('posted_at'),
                    collected_at=datetime.utcnow()
                )

                self.db.add(apify_record)
                stored_count += 1

            await self.db.commit()
            logger.info(f"Stored {stored_count} Apify {platform} records")
            return stored_count

        except Exception as e:
            logger.error(f"Error storing Apify data: {e}")
            await self.db.rollback()
            return 0

    def normalize_data_format(
        self,
        data: List[Dict[str, Any]],
        source: str
    ) -> List[Dict[str, Any]]:
        """
        Normalize data from different sources to a unified format

        Args:
            data: Raw data from source
            source: Source name (google_trends, tiktok, facebook, etc.)

        Returns:
            Normalized data
        """
        normalized = []

        for item in data:
            try:
                if source == 'google_trends':
                    normalized_item = {
                        'source': 'google_trends',
                        'content': item.get('keyword') or item.get('term', ''),
                        'metrics': {
                            'interest': item.get('interest', 0),
                            'rank': item.get('rank', 0)
                        },
                        'timestamp': item.get('timestamp'),
                        'geo_location': 'Nigeria'
                    }

                elif source == 'tiktok':
                    metrics = item.get('metrics', {})
                    normalized_item = {
                        'source': 'tiktok',
                        'content': item.get('description', ''),
                        'author': item.get('author', {}).get('username'),
                        'metrics': {
                            'views': metrics.get('views', 0),
                            'likes': metrics.get('likes', 0),
                            'comments': metrics.get('comments', 0),
                            'shares': metrics.get('shares', 0)
                        },
                        'hashtags': item.get('hashtags', []),
                        'timestamp': item.get('created_at'),
                        'geo_location': 'Nigeria'
                    }

                elif source == 'facebook':
                    metrics = item.get('metrics', {})
                    content = item.get('content', {})
                    normalized_item = {
                        'source': 'facebook',
                        'content': content.get('text') or content.get('post_text', ''),
                        'author': item.get('author'),
                        'page': item.get('page'),
                        'metrics': {
                            'likes': metrics.get('likes', 0),
                            'comments': metrics.get('comments', 0),
                            'shares': metrics.get('shares', 0)
                        },
                        'timestamp': item.get('timestamp', {}).get('posted_at'),
                        'geo_location': 'Nigeria'
                    }

                else:
                    # Generic normalization
                    normalized_item = {
                        'source': source,
                        'content': self.clean_text(item.get('content', '')),
                        'author': item.get('author'),
                        'metrics': item.get('metrics', {}),
                        'timestamp': item.get('timestamp') or item.get('posted_at'),
                        'geo_location': 'Nigeria'
                    }

                normalized.append(normalized_item)

            except Exception as e:
                logger.error(f"Error normalizing {source} item: {e}")
                continue

        return normalized


# Singleton instance
_data_pipeline_service = None


def get_data_pipeline_service(db: AsyncSession) -> DataPipelineService:
    """Get data pipeline service instance"""
    return DataPipelineService(db)
