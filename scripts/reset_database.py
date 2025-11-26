#!/usr/bin/env python3
"""
Reset Database - Drop and recreate all tables
WARNING: This will delete ALL data in the database!
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.database import Base
from dotenv import load_dotenv
import os

# Import all models to register them with Base.metadata
from app.models.social_media_sources import (
    ApifyScrapedData,
    GoogleTrendsData,
    TikTokContent,
    FacebookContent,
    SocialMediaAggregation,
    DataSourceMonitoring,
)
from app.models.ai_analysis import (
    ApifyDataProcessingStatus,
    ApifySentimentAnalysis,
    ApifyLocationExtraction,
    ApifyEntityExtraction,
    ApifyKeywordExtraction,
    ApifyAIBatchJob
)

load_dotenv()


async def reset_database():
    """Drop all tables and recreate them"""
    DATABASE_URL = os.getenv("DATABASE_URL")

    if not DATABASE_URL:
        print("❌ ERROR: DATABASE_URL not found in environment variables")
        print("Please check your .env file")
        sys.exit(1)

    print("=" * 70)
    print("⚠️  WARNING: DATABASE RESET ⚠️")
    print("=" * 70)
    print()
    print("This will DELETE ALL DATA in the database!")
    print(f"Database: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'localhost'}")
    print()

    # Ask for confirmation
    response = input("Are you sure you want to continue? Type 'YES' to confirm: ")
    if response != "YES":
        print("❌ Reset cancelled")
        sys.exit(0)

    print()
    print("Resetting database...")

    # Create engine
    engine = create_async_engine(DATABASE_URL, echo=False)

    try:
        # Drop all tables
        print("  1. Dropping all existing tables...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        print("     ✓ All tables dropped")

        # Recreate all tables
        print("  2. Creating fresh tables...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("     ✓ All tables created")

        print()
        print("=" * 70)
        print("✓ Database reset complete!")
        print("=" * 70)
        print()
        print("Created tables:")
        print("  - google_trends_data")
        print("  - tiktok_content")
        print("  - facebook_content")
        print("  - apify_scraped_data")
        print("  - social_media_aggregation")
        print("  - data_source_monitoring")
        print("  - apify_data_processing_status")
        print("  - apify_sentiment_analysis")
        print("  - apify_location_extractions")
        print("  - apify_entity_extractions")
        print("  - apify_keyword_extractions")
        print("  - apify_ai_batch_jobs")
        print()

    except Exception as e:
        print(f"❌ Error resetting database: {e}")
        sys.exit(1)
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(reset_database())

