#!/usr/bin/env python3
"""Quick script to check apify_scraped_data table contents."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from dotenv import load_dotenv
import os

load_dotenv()

async def main():
    DATABASE_URL = os.getenv("DATABASE_URL")
    engine = create_async_engine(DATABASE_URL, echo=False)
    
    async with engine.connect() as conn:
        # Check total records
        result = await conn.execute(text("SELECT count(*) FROM apify_scraped_data"))
        count = result.scalar()
        print(f"Total records in apify_scraped_data: {count}")
        print()
        
        # Get platform distribution
        result = await conn.execute(text("""
            SELECT platform, COUNT(*) as count 
            FROM apify_scraped_data 
            GROUP BY platform
        """))
        print("Platform Distribution:")
        for row in result:
            print(f"  {row[0]}: {row[1]} records")
        print()
        
        # Get sample records
        result = await conn.execute(text("""
            SELECT source_id, author, content, posted_at, 
                   metrics_json->'likes' as likes,
                   metrics_json->'retweets' as retweets
            FROM apify_scraped_data 
            ORDER BY posted_at DESC
            LIMIT 5
        """))
        print("Sample records (most recent):")
        for row in result:
            content_preview = row[2][:60] + "..." if len(row[2]) > 60 else row[2]
            print(f"\n  Tweet ID: {row[0]}")
            print(f"  Author: @{row[1]}")
            print(f"  Content: {content_preview}")
            print(f"  Posted: {row[3]}")
            print(f"  Likes: {row[4]}, Retweets: {row[5]}")
    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
