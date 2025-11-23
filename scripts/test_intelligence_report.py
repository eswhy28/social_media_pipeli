#!/usr/bin/env python3
"""
Test Intelligence Report Endpoint
Demonstrates comprehensive social media intelligence monitoring
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from app.models.social_media_sources import ApifyScrapedData
from app.models.ai_analysis import ApifySentimentAnalysis, ApifyLocationExtraction
from dotenv import load_dotenv
import os
import json

load_dotenv()

async def test_intelligence_endpoint():
    """Test the comprehensive intelligence report data"""
    DATABASE_URL = os.getenv("DATABASE_URL")
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    print("=" * 80)
    print("INTELLIGENCE REPORT - SOCIAL MEDIA MONITORING SYSTEM")
    print("=" * 80)
    print()
    
    async with async_session() as session:
        # Get sample posts with media
        query = select(ApifyScrapedData).where(
            ApifyScrapedData.media_urls.isnot(None)
        ).limit(5)
        
        result = await session.execute(query)
        posts_with_media = result.scalars().all()
        
        print(f"📊 FOUND {len(posts_with_media)} POSTS WITH MEDIA/IMAGES")
        print()
        
        for idx, post in enumerate(posts_with_media, 1):
            print(f"{'='*80}")
            print(f"POST #{idx}: Intelligence Report")
            print(f"{'='*80}")
            
            # Basic Info
            print(f"\n🔍 POST METADATA:")
            print(f"   Post ID: {post.id}")
            print(f"   Platform: {post.platform}")
            print(f"   Posted: {post.posted_at}")
            print(f"   Source URL: https://twitter.com/{post.author}/status/{post.source_id}")
            
            # Author
            print(f"\n👤 AUTHOR:")
            print(f"   Username: @{post.author}")
            print(f"   Account Name: {post.account_name}")
            print(f"   Location: {post.location or 'Not specified'}")
            
            # Content
            print(f"\n📝 CONTENT:")
            content_preview = post.content[:150] + "..." if len(post.content) > 150 else post.content
            print(f"   {content_preview}")
            
            # Media
            print(f"\n🖼️  MEDIA (Images/Videos):")
            if post.media_urls:
                print(f"   Media Count: {len(post.media_urls)}")
                for i, url in enumerate(post.media_urls, 1):
                    print(f"   [{i}] {url}")
            else:
                print(f"   No media attached")
            
            # Engagement
            print(f"\n📊 ENGAGEMENT METRICS:")
            if post.metrics_json:
                print(f"   Likes: {post.metrics_json.get('likes', 0):,}")
                print(f"   Retweets: {post.metrics_json.get('retweets', 0):,}")
                print(f"   Replies: {post.metrics_json.get('replies', 0):,}")
                print(f"   Views: {post.metrics_json.get('views', 0):,}")
                total_engagement = (
                    post.metrics_json.get('likes', 0) +
                    post.metrics_json.get('retweets', 0) +
                    post.metrics_json.get('replies', 0)
                )
                print(f"   TOTAL ENGAGEMENT: {total_engagement:,}")
            
            # Hashtags & Mentions
            print(f"\n🏷️  CONTEXT:")
            if post.hashtags:
                print(f"   Hashtags: {', '.join(['#' + h for h in post.hashtags])}")
            if post.mentions:
                print(f"   Mentions: {', '.join(['@' + m for m in post.mentions])}")
            
            # AI ANALYSIS - Sentiment
            print(f"\n🤖 AI ANALYSIS:")
            sentiment_result = await session.execute(
                select(ApifySentimentAnalysis).where(
                    ApifySentimentAnalysis.scraped_data_id == post.id
                )
            )
            sentiment = sentiment_result.scalar_one_or_none()
            
            if sentiment:
                print(f"   📈 SENTIMENT ANALYSIS:")
                print(f"      Label: {sentiment.label.upper()}")
                print(f"      Score: {sentiment.score:.3f}")
                print(f"      Confidence: {sentiment.confidence:.2%}")
                if sentiment.all_scores:
                    print(f"      Polarity: {sentiment.all_scores.get('polarity', 'N/A')}")
                    print(f"      Subjectivity: {sentiment.all_scores.get('subjectivity', 'N/A')}")
                print(f"      Model: {sentiment.model_name}")
            else:
                print(f"   📈 SENTIMENT: Not yet analyzed")
            
            # AI ANALYSIS - Location
            location_result = await session.execute(
                select(ApifyLocationExtraction).where(
                    ApifyLocationExtraction.scraped_data_id == post.id
                )
            )
            locations = location_result.scalars().all()
            
            if locations:
                print(f"   📍 LOCATION EXTRACTION:")
                for loc in locations:
                    print(f"      Location: {loc.location_text}")
                    print(f"      Type: {loc.location_type}")
                    print(f"      Region: {loc.region or 'Unknown'}")
                    if loc.coordinates:
                        print(f"      Coordinates: {loc.coordinates}")
                    print(f"      Confidence: {loc.confidence:.2%}")
            else:
                print(f"   📍 LOCATIONS: None extracted")
            
            print()
        
        # Summary Statistics
        print("=" * 80)
        print("SUMMARY STATISTICS")
        print("=" * 80)
        
        # Total in database
        total_result = await session.execute(select(ApifyScrapedData))
        total_posts = len(total_result.scalars().all())
        
        # With media
        media_result = await session.execute(
            select(ApifyScrapedData).where(ApifyScrapedData.media_urls.isnot(None))
        )
        media_posts = len(media_result.scalars().all())
        
        # With sentiment
        sentiment_result = await session.execute(select(ApifySentimentAnalysis))
        sentiment_count = len(sentiment_result.scalars().all())
        
        # With locations
        location_result = await session.execute(select(ApifyLocationExtraction))
        location_count = len(location_result.scalars().all())
        
        print(f"\n📊 DATABASE OVERVIEW:")
        print(f"   Total Posts: {total_posts}")
        print(f"   Posts with Media: {media_posts} ({media_posts/total_posts*100:.1f}%)")
        print(f"   Posts with Sentiment Analysis: {sentiment_count} ({sentiment_count/total_posts*100:.1f}%)")
        print(f"   Locations Extracted: {location_count}")
        print()
        
        print("=" * 80)
        print("✅ INTELLIGENCE SYSTEM READY")
        print("=" * 80)
        print()
        print("🔗 API ENDPOINT:")
        print("   GET http://localhost:8000/api/v1/social-media/intelligence/report")
        print()
        print("📝 USAGE EXAMPLES:")
        print("   # Get posts with media only")
        print("   ?has_media=true&limit=50")
        print()
        print("   # Get positive sentiment posts")
        print("   ?sentiment_filter=positive&include_ai_analysis=true")
        print()
        print("   # High engagement posts with media")
        print("   ?has_media=true&min_engagement=1000&limit=20")
        print()
        print("   # Last 48 hours with full AI analysis")
        print("   ?hours_back=48&include_ai_analysis=true&limit=100")
        print()
    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(test_intelligence_endpoint())
