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
        print("Creating tables individually...")
        print()
        
        # Get all table objects
        tables_to_create = [
            ('google_trends_data', GoogleTrendsData.__table__),
            ('tiktok_content', TikTokContent.__table__),
            ('facebook_content', FacebookContent.__table__),
            ('apify_scraped_data', ApifyScrapedData.__table__),
            ('social_media_aggregation', SocialMediaAggregation.__table__),
            ('data_source_monitoring', DataSourceMonitoring.__table__),
            ('apify_data_processing_status', ApifyDataProcessingStatus.__table__),
            ('apify_sentiment_analysis', ApifySentimentAnalysis.__table__),
            ('apify_location_extractions', ApifyLocationExtraction.__table__),
            ('apify_entity_extractions', ApifyEntityExtraction.__table__),
            ('apify_keyword_extractions', ApifyKeywordExtraction.__table__),
            ('apify_ai_batch_jobs', ApifyAIBatchJob.__table__),
        ]

        created_count = 0
        skipped_count = 0

        for table_name, table_obj in tables_to_create:
            try:
                async with engine.begin() as conn:
                    await conn.run_sync(lambda sync_conn, t=table_obj: t.create(sync_conn, checkfirst=True))
                print(f"  ✓ {table_name}")
                created_count += 1
            except Exception as e:
                error_str = str(e).lower()
                if 'already exists' in error_str or 'duplicate' in error_str:
                    print(f"  - {table_name} (already exists)")
                    skipped_count += 1
                else:
                    print(f"  ✗ {table_name}: {e}")

        print()
        print(f"✅ Created {created_count} table(s), skipped {skipped_count} existing table(s)")

        # Verify final table count
        async with engine.connect() as conn:
            result = await conn.execute(
                __import__('sqlalchemy').text(
                    "SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename"
                )
            )
            existing_tables = [row[0] for row in result]

            print(f"✓ Total tables in database: {len(existing_tables)}")
            if len(existing_tables) > 0:
                print()
                print("Existing tables:")
                for tbl in existing_tables:
                    print(f"  - {tbl}")

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

