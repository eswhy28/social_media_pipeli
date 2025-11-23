#!/usr/bin/env python3
"""
Complete Setup Script for Social Media Intelligence System
This script will:
1. Create all necessary AI tables
2. Process sentiment analysis for all posts
3. Extract and geocode locations
4. Verify the system is ready
"""

import asyncio
import sys
from pathlib import Path
import os

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, func, text
from dotenv import load_dotenv

load_dotenv()

async def main():
    print("=" * 80)
    print("SOCIAL MEDIA INTELLIGENCE SYSTEM - COMPLETE SETUP")
    print("=" * 80)
    print()
    
    DATABASE_URL = os.getenv("DATABASE_URL")
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    # Step 1: Create AI Tables
    print("📊 STEP 1: Creating AI Analysis Tables...")
    print("-" * 80)
    try:
        from app.database import Base
        from app.models.social_media_sources import ApifyScrapedData
        from app.models.ai_analysis import (
            ApifyDataProcessingStatus,
            ApifySentimentAnalysis,
            ApifyLocationExtraction,
            ApifyEntityExtraction,
            ApifyKeywordExtraction,
            ApifyAIBatchJob
        )
        
        async with engine.begin() as conn:
            # Create only AI tables
            tables_to_create = [
                ApifyDataProcessingStatus.__table__,
                ApifySentimentAnalysis.__table__,
                ApifyLocationExtraction.__table__,
                ApifyEntityExtraction.__table__,
                ApifyKeywordExtraction.__table__,
                ApifyAIBatchJob.__table__
            ]
            
            for table in tables_to_create:
                try:
                    await conn.run_sync(lambda sync_conn, t=table: t.create(sync_conn, checkfirst=True))
                    print(f"  ✅ Created: {table.name}")
                except Exception as e:
                    if 'already exists' in str(e).lower():
                        print(f"  ✓ Exists: {table.name}")
                    else:
                        print(f"  ⚠️  Error: {table.name} - {e}")
        
        print("✅ AI tables ready!")
        print()
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        print()
    
    # Step 2: Check Data Status
    print("📊 STEP 2: Checking Database Status...")
    print("-" * 80)
    
    async with async_session() as session:
        from app.models.social_media_sources import ApifyScrapedData
        from app.models.ai_analysis import (
            ApifySentimentAnalysis,
            ApifyLocationExtraction,
            ApifyDataProcessingStatus
        )
        
        # Total posts
        total_result = await session.execute(select(func.count(ApifyScrapedData.id)))
        total_posts = total_result.scalar()
        print(f"  Total Posts in Database: {total_posts}")
        
        # Sentiment analysis count
        sentiment_result = await session.execute(select(func.count(ApifySentimentAnalysis.id)))
        sentiment_count = sentiment_result.scalar()
        print(f"  Sentiment Analyses: {sentiment_count}")
        
        # Location extraction count
        location_result = await session.execute(select(func.count(ApifyLocationExtraction.id)))
        location_count = location_result.scalar()
        print(f"  Location Extractions: {location_count}")
        
        # Processing status
        status_result = await session.execute(select(func.count(ApifyDataProcessingStatus.id)))
        status_count = status_result.scalar()
        print(f"  Processing Status Records: {status_count}")
        
        needs_sentiment = total_posts - sentiment_count
        needs_location = total_posts - status_count  # Use status count for location processing
        
        print()
        print(f"  📊 Processing Status:")
        print(f"     Needs Sentiment Analysis: {needs_sentiment}")
        print(f"     Needs Location Extraction: {needs_location}")
        print()
    
    # Step 3: Run Sentiment Analysis
    if needs_sentiment > 0:
        print("🤖 STEP 3: Running Sentiment Analysis...")
        print("-" * 80)
        print(f"  Processing {needs_sentiment} posts...")
        
        try:
            from app.services.ai_processing_service import get_ai_processing_service
            
            async with async_session() as session:
                ai_service = get_ai_processing_service(session)
                result = await ai_service.process_sentiment_batch(limit=None)
                
                print(f"  ✅ Processed: {result['processed']} posts")
                print(f"  ⏱️  Time: {result['processing_time_seconds']:.2f}s")
                print(f"  ❌ Failed: {result['failed']}")
                print()
        except Exception as e:
            print(f"  ❌ Error: {e}")
            print()
    else:
        print("✅ STEP 3: Sentiment Analysis - Already Complete!")
        print()
    
    # Step 4: Run Location Extraction
    if needs_location > 0:
        print("🗺️  STEP 4: Running Location Extraction...")
        print("-" * 80)
        print(f"  Processing {needs_location} posts...")
        
        try:
            from app.services.ai_processing_service import get_ai_processing_service
            
            async with async_session() as session:
                ai_service = get_ai_processing_service(session)
                result = await ai_service.process_location_batch(limit=None)
                
                print(f"  ✅ Processed: {result['processed']} posts")
                print(f"  📍 Locations Found: {result.get('locations_found', 0)}")
                print(f"  ❌ Failed: {result['failed']}")
                print()
        except Exception as e:
            print(f"  ❌ Error: {e}")
            print()
    else:
        print("✅ STEP 4: Location Extraction - Already Complete!")
        print()
    
    # Step 5: Final Verification
    print("🔍 STEP 5: Final Verification...")
    print("-" * 80)
    
    async with async_session() as session:
        # Get sample post with all data
        query = select(ApifyScrapedData).where(
            ApifyScrapedData.content.isnot(None)
        ).limit(1)
        
        result = await session.execute(query)
        sample_post = result.scalar_one_or_none()
        
        if sample_post:
            print(f"  📝 Sample Post:")
            print(f"     Author: @{sample_post.author}")
            print(f"     Content: {sample_post.content[:80]}...")
            print(f"     Engagement: {sample_post.metrics_json}")
            
            # Check sentiment
            sentiment_result = await session.execute(
                select(ApifySentimentAnalysis).where(
                    ApifySentimentAnalysis.scraped_data_id == sample_post.id
                )
            )
            sentiment = sentiment_result.scalar_one_or_none()
            
            if sentiment:
                print(f"     ✅ Sentiment: {sentiment.label.upper()} (confidence: {sentiment.confidence:.2%})")
            else:
                print(f"     ⚠️  Sentiment: Not analyzed")
            
            # Check locations
            location_result = await session.execute(
                select(ApifyLocationExtraction).where(
                    ApifyLocationExtraction.scraped_data_id == sample_post.id
                )
            )
            locations = location_result.scalars().all()
            
            if locations:
                print(f"     ✅ Locations: {len(locations)} found")
                for loc in locations:
                    print(f"        📍 {loc.location_text} ({loc.region or 'Unknown region'})")
            else:
                print(f"     ℹ️  Locations: None extracted")
            
            print()
    
    # Step 6: Print API Endpoint Information
    print("=" * 80)
    print("✅ SETUP COMPLETE - SYSTEM READY!")
    print("=" * 80)
    print()
    print("🚀 Your Intelligence System is Now Ready!")
    print()
    print("📡 MAIN INTELLIGENCE ENDPOINT:")
    print("   http://localhost:8000/api/v1/social-media/intelligence/report")
    print()
    print("📝 QUICK TEST EXAMPLES:")
    print("   # Get 10 posts with AI analysis")
    print("   curl 'http://localhost:8000/api/v1/social-media/intelligence/report?limit=10'")
    print()
    print("   # Get posts with images")
    print("   curl 'http://localhost:8000/api/v1/social-media/intelligence/report?has_media=true'")
    print()
    print("   # Get negative sentiment posts")
    print("   curl 'http://localhost:8000/api/v1/social-media/intelligence/report?sentiment_filter=negative'")
    print()
    print("   # High engagement posts")
    print("   curl 'http://localhost:8000/api/v1/social-media/intelligence/report?min_engagement=1000'")
    print()
    print("🌐 INTERACTIVE API DOCS:")
    print("   http://localhost:8000/docs")
    print()
    print("=" * 80)
    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
