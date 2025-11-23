#!/usr/bin/env python3
"""
Clean AI Analysis Tables
Deletes all AI processing records to allow fresh processing
Keeps the scraped data intact
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, func, delete
from dotenv import load_dotenv
import os

load_dotenv()

async def main():
    print("=" * 80)
    print("CLEANING AI ANALYSIS TABLES")
    print("=" * 80)
    print()
    print("⚠️  This will delete all AI processing records but keep your scraped data")
    print()
    
    DATABASE_URL = os.getenv("DATABASE_URL")
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        from app.models.ai_analysis import (
            ApifyDataProcessingStatus,
            ApifySentimentAnalysis,
            ApifyLocationExtraction,
            ApifyEntityExtraction,
            ApifyKeywordExtraction,
            ApifyAIBatchJob
        )
        from app.models.social_media_sources import ApifyScrapedData
        
        # Check current counts
        print("📊 Current Status:")
        print("-" * 80)
        
        # Scraped data count
        scraped_count = await session.execute(select(func.count(ApifyScrapedData.id)))
        scraped_total = scraped_count.scalar()
        print(f"  Scraped Data: {scraped_total} posts (WILL BE KEPT)")
        
        # AI analysis counts
        sentiment_count = await session.execute(select(func.count(ApifySentimentAnalysis.id)))
        sentiment_total = sentiment_count.scalar()
        print(f"  Sentiment Analysis: {sentiment_total} records (WILL BE DELETED)")
        
        location_count = await session.execute(select(func.count(ApifyLocationExtraction.id)))
        location_total = location_count.scalar()
        print(f"  Location Extractions: {location_total} records (WILL BE DELETED)")
        
        status_count = await session.execute(select(func.count(ApifyDataProcessingStatus.id)))
        status_total = status_count.scalar()
        print(f"  Processing Status: {status_total} records (WILL BE DELETED)")
        
        job_count = await session.execute(select(func.count(ApifyAIBatchJob.id)))
        job_total = job_count.scalar()
        print(f"  Batch Jobs: {job_total} records (WILL BE DELETED)")
        
        print()
        
        # Delete AI analysis records
        print("🗑️  Deleting AI Analysis Records...")
        print("-" * 80)
        
        # Delete in reverse order of dependencies
        tables_to_clean = [
            (ApifyLocationExtraction, "Location Extractions"),
            (ApifySentimentAnalysis, "Sentiment Analysis"),
            (ApifyEntityExtraction, "Entity Extractions"),
            (ApifyKeywordExtraction, "Keyword Extractions"),
            (ApifyDataProcessingStatus, "Processing Status"),
            (ApifyAIBatchJob, "Batch Jobs")
        ]
        
        for model, name in tables_to_clean:
            try:
                result = await session.execute(delete(model))
                count = result.rowcount
                print(f"  ✅ Deleted {count} records from {name}")
            except Exception as e:
                print(f"  ⚠️  Error deleting {name}: {e}")
        
        # Commit the deletions
        await session.commit()
        
        print()
        print("=" * 80)
        print("✅ CLEANUP COMPLETE")
        print("=" * 80)
        print()
        print("📊 Final Status:")
        
        # Verify deletion
        sentiment_count = await session.execute(select(func.count(ApifySentimentAnalysis.id)))
        print(f"  Sentiment Analysis: {sentiment_count.scalar()} records")
        
        location_count = await session.execute(select(func.count(ApifyLocationExtraction.id)))
        print(f"  Location Extractions: {location_count.scalar()} records")
        
        status_count = await session.execute(select(func.count(ApifyDataProcessingStatus.id)))
        print(f"  Processing Status: {status_count.scalar()} records")
        
        # Confirm scraped data is intact
        scraped_count = await session.execute(select(func.count(ApifyScrapedData.id)))
        print(f"  Scraped Data: {scraped_count.scalar()} posts (INTACT)")
        
        print()
        print("🚀 Ready to run setup_intelligence_system.py")
        print()
    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
