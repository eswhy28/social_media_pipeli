#!/usr/bin/env python3
"""
Create ALL database tables (base + AI analysis tables)
This script creates all tables defined in the models
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine
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


async def create_all_tables():
    """Create all database tables"""
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    if not DATABASE_URL:
        print("❌ ERROR: DATABASE_URL not found in environment variables")
        print("Please check your .env file")
        sys.exit(1)
    
    print("=" * 70)
    print("Creating ALL Database Tables")
    print("=" * 70)
    print()
    print(f"Database URL: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'localhost'}")
    print()
    
    # Create engine with echo=False to avoid too much output
    engine = create_async_engine(DATABASE_URL, echo=False)
    
    try:
        print("Creating all tables...")
        print()
        
        # Try to create tables, handling duplicate table/index errors
        try:
            async with engine.begin() as conn:
                # Create all tables defined in Base.metadata
                await conn.run_sync(lambda sync_conn: Base.metadata.create_all(sync_conn, checkfirst=True))

            print("✅ All tables created successfully!")

        except Exception as create_error:
            # Check if it's a duplicate table/index error
            error_str = str(create_error).lower()
            if 'already exists' in error_str or 'duplicate' in error_str:
                print("✅ Tables already exist (some may have been created previously)")

                # Verify tables actually exist by querying them
                async with engine.connect() as conn:
                    result = await conn.execute(
                        __import__('sqlalchemy').text(
                            "SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename"
                        )
                    )
                    existing_tables = [row[0] for row in result]

                    print(f"\n✓ Found {len(existing_tables)} existing tables in database")
            else:
                # Re-raise if it's a different error
                raise

        print()
        print("Available tables:")
        print("  Base Social Media Tables:")
        print("    - google_trends_data (Google Trends data)")
        print("    - tiktok_content (TikTok video content)")
        print("    - facebook_content (Facebook posts)")
        print("    - apify_scraped_data (Apify scraped social media data)")
        print("    - social_media_aggregation (aggregated social media data)")
        print("    - data_source_monitoring (data source monitoring)")
        print()
        print("  AI Analysis Tables:")
        print("    - apify_data_processing_status (tracks processing status)")
        print("    - apify_sentiment_analysis (sentiment analysis results)")
        print("    - apify_location_extractions (location extraction results)")
        print("    - apify_entity_extractions (entity recognition results)")
        print("    - apify_keyword_extractions (keyword extraction results)")
        print("    - apify_ai_batch_jobs (batch job tracking)")
        print()
        print("=" * 70)
        print("✓ Database setup complete!")
        print("=" * 70)
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        print()
        print("Troubleshooting:")
        print("  1. Check that PostgreSQL is running:")
        print("     docker ps | grep postgres")
        print()
        print("  2. Verify database connection:")
        print("     docker exec postgres psql -U sa -d social_media_pipeline -c '\\dt'")
        print()
        print("  3. Check DATABASE_URL in .env file")
        print(f"     Current: {DATABASE_URL}")
        print()
        print("  4. If tables are partially created, you can drop and recreate:")
        print("     docker exec postgres psql -U sa -d social_media_pipeline -c 'DROP SCHEMA public CASCADE; CREATE SCHEMA public;'")
        print()
        sys.exit(1)
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(create_all_tables())

