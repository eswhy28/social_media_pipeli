#!/usr/bin/env python3
"""
Create AI Analysis tables in the database
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine
from app.database import Base
from app.models.social_media_sources import ApifyScrapedData  # Import this first
from app.models.ai_analysis import (
    ApifyDataProcessingStatus,
    ApifySentimentAnalysis,
    ApifyLocationExtraction,
    ApifyEntityExtraction,
    ApifyKeywordExtraction,
    ApifyAIBatchJob
)
from dotenv import load_dotenv
import os

load_dotenv()

async def create_tables():
    """Create AI analysis tables"""
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    print("=" * 70)
    print("Creating AI Analysis Tables")
    print("=" * 70)
    print()
    
    engine = create_async_engine(DATABASE_URL, echo=True)
    
    print("Creating tables...")
    async with engine.begin() as conn:
        # Only create the new AI analysis tables
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
                await conn.run_sync(lambda sync_conn: table.create(sync_conn, checkfirst=True))
                print(f"  ✓ Created table: {table.name}")
            except Exception as e:
                if 'already exists' in str(e).lower():
                    print(f"  - Table {table.name} already exists, skipping")
                else:
                    print(f"  ✗ Error creating {table.name}: {e}")

    
    print()
    print("=" * 70)
    print("✓ AI Analysis tables created successfully!")
    print("=" * 70)
    print()
    print("New tables:")
    print("  - apify_data_processing_status (tracks processing status)")
    print("  - apify_sentiment_analysis (sentiment results)")
    print("  - apify_location_extractions (location extraction results)")
    print("  - apify_entity_extractions (entity recognition results)")
    print("  - apify_keyword_extractions (keyword extraction results)")
    print("  - apify_ai_batch_jobs (batch job tracking)")
    print()
    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(create_tables())
