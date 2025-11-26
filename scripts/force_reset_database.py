#!/usr/bin/env python3
"""
Force reset database - Drop and recreate all tables (non-interactive)
WARNING: This will delete ALL data in the database!
Use this only in automated scripts or when you're sure you want to reset.
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


async def force_reset_database():
    """Drop all tables and recreate them without asking for confirmation"""
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    if not DATABASE_URL:
        print("❌ ERROR: DATABASE_URL not found in environment variables")
        sys.exit(1)
    
    print("=" * 70)
    print("Resetting Database...")
    print("=" * 70)
    print()
    
    # Create engine
    engine = create_async_engine(DATABASE_URL, echo=False)
    
    try:
        # Drop entire public schema and recreate (cleanest approach)
        print("  1. Dropping public schema (removes all tables, indexes, etc)...")
        async with engine.begin() as conn:
            # Drop schema cascade (removes everything)
            await conn.execute(text("DROP SCHEMA IF EXISTS public CASCADE"))
            # Recreate schema
            await conn.execute(text("CREATE SCHEMA public"))
            # Grant permissions
            await conn.execute(text("GRANT ALL ON SCHEMA public TO sa"))
            await conn.execute(text("GRANT ALL ON SCHEMA public TO public"))
        print("     ✓ Schema reset complete")

        # Recreate all tables
        print("  2. Creating fresh tables...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("     ✓ All tables created")
        
        print()
        print("✓ Database reset complete!")
        print()
        
    except Exception as e:
        print(f"❌ Error resetting database: {e}")
        sys.exit(1)
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(force_reset_database())

