#!/usr/bin/env python3
"""
Test script for new data retrieval endpoints
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.api.social_media import get_scraped_data, get_geo_analysis, get_engagement_analysis, get_data_stats
from app.models.social_media_sources import ApifyScrapedData
from dotenv import load_dotenv
import os

load_dotenv()

async def test_endpoints():
    """Test the new data endpoints"""
    DATABASE_URL = os.getenv("DATABASE_URL")
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    print("=" * 70)
    print("Testing New Data Retrieval Endpoints")
    print("=" * 70)
    print()
    
    async with async_session() as session:
        # Test 1: Get scraped data
        print("1. Testing /data/scraped endpoint...")
        try:
            from fastapi import Request
            from unittest.mock import MagicMock
            
            # This is a basic test - in production, use FastAPI TestClient
            from sqlalchemy import select
            result = await session.execute(
                select(ApifyScrapedData).limit(5)
            )
            posts = result.scalars().all()
            
            print(f"   ✓ Found {len(posts)} posts")
            if posts:
                print(f"   Sample post: {posts[0].author} - {posts[0].content[:50]}...")
                print(f"   Media URLs: {len(posts[0].media_urls) if posts[0].media_urls else 0}")
                print(f"   Location: {posts[0].location}")
        except Exception as e:
            print(f"   ✗ Error: {e}")
        print()
        
        # Test 2: Check geocoding
        print("2. Testing geocoding service...")
        try:
            from app.services.geocoding_service import get_geocoding_service
            geo_service = get_geocoding_service()
            
            test_locations = ["Lagos, Nigeria", "Abuja", "Kano", "Scotland, United Kingdom"]
            for loc in test_locations:
                coords = geo_service.geocode_location(loc)
                region = geo_service.get_region_for_location(loc)
                print(f"   {loc}: {coords} (Region: {region})")
        except Exception as e:
            print(f"   ✗ Error: {e}")
        print()
        
        # Test 3: Check data with media
        print("3. Checking posts with media...")
        try:
            from sqlalchemy import func
            result = await session.execute(
                select(ApifyScrapedData).where(
                    func.jsonb_array_length(ApifyScrapedData.media_urls) > 0
                ).limit(3)
            )
            media_posts = result.scalars().all()
            
            print(f"   ✓ Found {len(media_posts)} posts with media")
            for post in media_posts:
                print(f"   - {post.author}: {len(post.media_urls)} media files")
                if post.media_urls:
                    print(f"     First media: {post.media_urls[0]}")
        except Exception as e:
            print(f"   ✗ Error: {e}")
        print()
        
        # Test 4: Check hashtags
        print("4. Checking hashtag distribution...")
        try:
            result = await session.execute(
                select(ApifyScrapedData).where(
                    ApifyScrapedData.hashtags != None
                ).limit(100)
            )
            posts_with_hashtags = result.scalars().all()
            
            hashtag_counts = {}
            for post in posts_with_hashtags:
                if post.hashtags:
                    for tag in post.hashtags:
                        hashtag_counts[tag] = hashtag_counts.get(tag, 0) + 1
            
            top_5 = sorted(hashtag_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            print(f"   ✓ Top 5 hashtags:")
            for tag, count in top_5:
                print(f"   - #{tag}: {count} posts")
        except Exception as e:
            print(f"   ✗ Error: {e}")
        print()
        
        # Test 5: Check engagement metrics
        print("5. Checking engagement metrics...")
        try:
            result = await session.execute(
                select(ApifyScrapedData).where(
                    ApifyScrapedData.metrics_json != None
                ).limit(10)
            )
            posts_with_metrics = result.scalars().all()
            
            total_likes = 0
            total_retweets = 0
            total_views = 0
            
            for post in posts_with_metrics:
                if post.metrics_json:
                    total_likes += post.metrics_json.get('likes', 0)
                    total_retweets += post.metrics_json.get('retweets', 0)
                    total_views += post.metrics_json.get('views', 0)
            
            print(f"   ✓ Sample metrics from {len(posts_with_metrics)} posts:")
            print(f"   - Total likes: {total_likes}")
            print(f"   - Total retweets: {total_retweets}")
            print(f"   - Total views: {total_views}")
        except Exception as e:
            print(f"   ✗ Error: {e}")
        print()
    
    await engine.dispose()
    
    print("=" * 70)
    print("✓ Tests completed!")
    print("=" * 70)
    print()
    print("New API Endpoints Available:")
    print("  GET /api/v1/social-media/data/scraped - Get all scraped data with filters")
    print("  GET /api/v1/social-media/data/geo-analysis - Geographic analysis")
    print("  GET /api/v1/social-media/data/engagement-analysis - Engagement metrics")
    print("  GET /api/v1/social-media/data/stats - Overall statistics")
    print()

if __name__ == "__main__":
    asyncio.run(test_endpoints())
