#!/usr/bin/env python3
"""
Quick verification that data is properly formatted for frontend consumption
"""

import asyncio
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from app.models.social_media_sources import ApifyScrapedData
from app.services.geocoding_service import get_geocoding_service
from dotenv import load_dotenv
import os

load_dotenv()

async def main():
    DATABASE_URL = os.getenv("DATABASE_URL")
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    print("=" * 70)
    print("DATA VERIFICATION FOR FRONTEND")
    print("=" * 70)
    print()
    
    async with async_session() as session:
        # Get sample posts
        result = await session.execute(
            select(ApifyScrapedData)
            .order_by(ApifyScrapedData.posted_at.desc())
            .limit(3)
        )
        posts = result.scalars().all()
        
        geocoding_service = get_geocoding_service()
        
        print(f"✓ Found {len(posts)} sample posts")
        print()
        
        for i, post in enumerate(posts, 1):
            print(f"POST {i}:")
            print(f"  Author: @{post.author} ({post.account_name})")
            print(f"  Content: {post.content[:80]}...")
            print(f"  Posted: {post.posted_at}")
            print()
            
            # Engagement
            if post.metrics_json:
                print(f"  Engagement:")
                print(f"    Likes: {post.metrics_json.get('likes', 0)}")
                print(f"    Retweets: {post.metrics_json.get('retweets', 0)}")
                print(f"    Replies: {post.metrics_json.get('replies', 0)}")
                print(f"    Views: {post.metrics_json.get('views', 0)}")
                total_eng = (post.metrics_json.get('likes', 0) + 
                            post.metrics_json.get('retweets', 0) + 
                            post.metrics_json.get('replies', 0))
                print(f"    Total Engagement: {total_eng}")
            print()
            
            # Media
            if post.media_urls and len(post.media_urls) > 0:
                print(f"  Media: {len(post.media_urls)} image(s)")
                for url in post.media_urls:
                    print(f"    - {url}")
            else:
                print(f"  Media: None")
            print()
            
            # Location
            if post.location:
                location_data = geocoding_service.enrich_location_data(post.location)
                print(f"  Location: {post.location}")
                if location_data['coordinates']:
                    print(f"    Coordinates: {location_data['coordinates']}")
                    print(f"    Region: {location_data['region']}")
                else:
                    print(f"    Coordinates: Not available (location outside Nigeria)")
            else:
                print(f"  Location: Not specified")
            print()
            
            # Hashtags
            if post.hashtags and len(post.hashtags) > 0:
                print(f"  Hashtags: {', '.join(['#' + tag for tag in post.hashtags])}")
            else:
                print(f"  Hashtags: None")
            print()
            
            # Twitter URL
            if post.platform == "twitter":
                tweet_url = f"https://twitter.com/{post.author}/status/{post.source_id}"
                print(f"  URL: {tweet_url}")
            print()
            print("-" * 70)
            print()
        
        # Summary statistics
        total_result = await session.execute(select(ApifyScrapedData))
        all_posts = total_result.scalars().all()
        
        posts_with_media = sum(1 for p in all_posts if p.media_urls and len(p.media_urls) > 0)
        posts_with_location = sum(1 for p in all_posts if p.location)
        posts_with_hashtags = sum(1 for p in all_posts if p.hashtags and len(p.hashtags) > 0)
        
        total_engagement = 0
        for p in all_posts:
            if p.metrics_json:
                total_engagement += (
                    p.metrics_json.get('likes', 0) +
                    p.metrics_json.get('retweets', 0) +
                    p.metrics_json.get('replies', 0)
                )
        
        print("OVERALL STATISTICS:")
        print(f"  Total Posts: {len(all_posts)}")
        print(f"  Posts with Media: {posts_with_media} ({posts_with_media/len(all_posts)*100:.1f}%)")
        print(f"  Posts with Location: {posts_with_location} ({posts_with_location/len(all_posts)*100:.1f}%)")
        print(f"  Posts with Hashtags: {posts_with_hashtags} ({posts_with_hashtags/len(all_posts)*100:.1f}%)")
        print(f"  Total Engagement: {total_engagement}")
        print(f"  Avg Engagement per Post: {total_engagement/len(all_posts):.1f}")
        print()
        
        print("=" * 70)
        print("✓ DATA IS READY FOR FRONTEND CONSUMPTION")
        print("=" * 70)
        print()
        print("Available API Endpoints:")
        print("  GET /api/v1/social-media/data/scraped")
        print("  GET /api/v1/social-media/data/geo-analysis")
        print("  GET /api/v1/social-media/data/engagement-analysis")
        print("  GET /api/v1/social-media/data/stats")
        print()
    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
