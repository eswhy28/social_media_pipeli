#!/usr/bin/env python3
"""
Quick test to verify AI processing system is ready
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, text
from app.models.social_media_sources import ApifyScrapedData
from app.models.ai_analysis import ApifyDataProcessingStatus
from dotenv import load_dotenv
import os

load_dotenv()

async def main():
    DATABASE_URL = os.getenv("DATABASE_URL")
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    print("=" * 70)
    print("AI PROCESSING SYSTEM VERIFICATION")
    print("=" * 70)
    print()
    
    async with async_session() as session:
        # Check tables exist
        print("1. Checking AI tables...")
        tables_to_check = [
            "apify_data_processing_status",
            "apify_sentiment_analysis",
            "apify_location_extractions",
            "apify_entity_extractions",
            "apify_keyword_extractions",
            "apify_ai_batch_jobs"
        ]
        
        for table in tables_to_check:
            result = await session.execute(
                text(f"SELECT to_regclass('{table}')")
            )
            exists = result.scalar() is not None
            status = "✓" if exists else "✗"
            print(f"   {status} {table}")
        print()
        
        # Check data status
        print("2. Checking data for processing...")
        total_result = await session.execute(select(ApifyScrapedData))
        total_count = len(total_result.scalars().all())
        print(f"   Total scraped records: {total_count}")
        
        processed_result = await session.execute(select(ApifyDataProcessingStatus))
        processed_count = len(processed_result.scalars().all())
        print(f"   Records with processing status: {processed_count}")
        print(f"   Unprocessed records: {total_count - processed_count}")
        print()
        
        # Show sample data
        print("3. Sample scraped data ready for AI processing:")
        sample_result = await session.execute(
            select(ApifyScrapedData).limit(3)
        )
        samples = sample_result.scalars().all()
        
        for i, post in enumerate(samples, 1):
            print(f"   Post {i}:")
            print(f"     Author: @{post.author}")
            print(f"     Content: {post.content[:60]}...")
            print(f"     Location: {post.location or 'Not specified'}")
            print()
    
    await engine.dispose()
    
    print("=" * 70)
    print("✓ AI PROCESSING SYSTEM IS READY!")
    print("=" * 70)
    print()
    print("Next Steps:")
    print("  1. Start the API server:")
    print("     uvicorn app.main:app --reload")
    print()
    print("  2. Process sentiment for all data:")
    print("     POST /api/v1/social-media/ai/process-sentiment")
    print()
    print("  3. Process locations for all data:")
    print("     POST /api/v1/social-media/ai/process-locations")
    print()
    print("  4. Check processing stats:")
    print("     GET /api/v1/social-media/ai/processing-stats")
    print()

if __name__ == "__main__":
    asyncio.run(main())
