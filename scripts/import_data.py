#!/usr/bin/env python3
"""
Script to import tweet scraper data from JSON files to the apify_scraped_data table.
This script reads all JSON files from the data directory and populates the database.
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from app.database import get_db, Base
from app.models.social_media_sources import ApifyScrapedData
from dotenv import load_dotenv
import uuid

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
DATA_DIR = Path(__file__).parent.parent / "data"


async def parse_twitter_date(date_str: str) -> datetime:
    """
    Parse Twitter's date format to datetime object.
    Twitter format: 'Sat Nov 22 20:41:53 +0000 2025'
    """
    try:
        # Try parsing Twitter's standard format
        dt = datetime.strptime(date_str, "%a %b %d %H:%M:%S %z %Y")
        return dt
    except ValueError:
        # Fallback to ISO format
        try:
            return datetime.fromisoformat(date_str.replace('+0000', '+00:00'))
        except:
            # Last resort - use current time
            print(f"Warning: Could not parse date '{date_str}', using current time")
            return datetime.utcnow()


async def extract_apify_data(tweet: Dict[str, Any], run_id: str = None) -> Dict[str, Any]:
    """
    Extract relevant data from a tweet JSON object and map to ApifyScrapedData model fields.
    """
    # Get basic tweet information
    tweet_id = tweet.get('id', '')
    text = tweet.get('fullText') or tweet.get('text', '')
    
    # Get author/handle information
    author = tweet.get('author', {})
    author_username = author.get('userName', '') if author else ''
    author_name = author.get('name', '') if author else ''
    
    # Parse posted_at timestamp
    created_at_str = tweet.get('createdAt', '')
    posted_at = await parse_twitter_date(created_at_str) if created_at_str else datetime.utcnow()
    
    # Get hashtags
    entities = tweet.get('entities', {})
    hashtags = [tag.get('text', '') for tag in entities.get('hashtags', [])]
    
    # Get mentions
    mentions = [mention.get('userName', '') for mention in entities.get('user_mentions', [])]
    
    # Get media URLs
    media_urls = tweet.get('media', [])
    
    # Get engagement metrics
    metrics = {
        'likes': tweet.get('likeCount', 0),
        'retweets': tweet.get('retweetCount', 0),
        'replies': tweet.get('replyCount', 0),
        'quotes': tweet.get('quoteCount', 0),
        'views': tweet.get('viewCount', 0),
        'bookmarks': tweet.get('bookmarkCount', 0),
    }
    
    # Store location information
    location = author.get('location', '') if author else ''
    
    return {
        'id': str(uuid.uuid4()),  # Generate new UUID for our database
        'platform': 'twitter',
        'source_id': tweet_id,  # Original tweet ID
        'actor_id': 'apify/tweet-scraper',
        'run_id': run_id or f'manual-import-{datetime.now().strftime("%Y%m%d")}',
        'author': author_username,
        'account_name': author_name,
        'content': text,
        'content_type': 'tweet',
        'metrics_json': metrics,
        'hashtags': hashtags,
        'mentions': mentions,
        'media_urls': media_urls,
        'raw_data': tweet,  # Store the complete original tweet data
        'location': location,
        'geo_location': 'Nigeria',  # Default based on your use case
        'posted_at': posted_at,
        'collected_at': datetime.utcnow(),
    }


async def load_json_file(file_path: Path) -> List[Dict[str, Any]]:
    """Load and parse a JSON file containing tweets."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            return [data]
        else:
            print(f"Warning: Unexpected data format in {file_path}")
            return []
    except Exception as e:
        print(f"Error loading {file_path}: {str(e)}")
        return []


async def import_tweets_to_db(session: AsyncSession, tweets: List[Dict[str, Any]], filename: str) -> tuple[int, int]:
    """
    Import tweets to apify_scraped_data table one at a time with proper transaction handling.
    Returns: (inserted_count, skipped_count)
    """
    inserted = 0
    skipped = 0
    
    # Extract run_id from filename if available
    run_id = f"import-{filename}"
    
    for i, tweet in enumerate(tweets):
        try:
            # Extract post data
            post_data = await extract_apify_data(tweet, run_id)
            source_id = post_data['source_id']
            
            # Start a fresh transaction for each tweet
            try:
                # Check if post already exists (by source_id and platform)
                result = await session.execute(
                    select(ApifyScrapedData).where(
                        ApifyScrapedData.source_id == source_id,
                        ApifyScrapedData.platform == 'twitter'
                    )
                )
                existing_post = result.scalar_one_or_none()
                
                if existing_post:
                    skipped += 1
                    continue
                
                # Create and insert new post
                new_post = ApifyScrapedData(**post_data)
                session.add(new_post)
                
                # Commit immediately after each insert
                await session.commit()
                inserted += 1
                
                # Print progress every 10 tweets
                if (i + 1) % 10 == 0:
                    print(f"  Progress: {i + 1}/{len(tweets)} tweets processed...")
                    
            except Exception as db_error:
                # Rollback this transaction and continue with next tweet
                await session.rollback()
                print(f"  ✗ DB Error for tweet {source_id}: {str(db_error)}")
                skipped += 1
                continue
                
        except Exception as e:
            # Error in data extraction phase
            tweet_id = tweet.get('id', 'unknown')
            print(f"  ✗ Data extraction error for tweet {tweet_id}: {str(e)}")
            skipped += 1
            continue
    
    if inserted > 0:
        print(f"✓ Successfully inserted {inserted} new posts to database")
    
    return inserted, skipped


async def main():
    """Main function to orchestrate the data import."""
    print("=" * 70)
    print("Apify Scraped Data Import Script")
    print("=" * 70)
    print()
    
    # Verify data directory exists
    if not DATA_DIR.exists():
        print(f"✗ Error: Data directory not found: {DATA_DIR}")
        sys.exit(1)
    
    # Get all JSON files
    json_files = list(DATA_DIR.glob('*.json'))
    
    if not json_files:
        print(f"✗ No JSON files found in {DATA_DIR}")
        sys.exit(1)
    
    print(f"Found {len(json_files)} JSON file(s) to process:")
    for file in json_files:
        print(f"  - {file.name} ({file.stat().st_size / 1024:.1f} KB)")
    print()
    
    # Create async engine and session
    if not DATABASE_URL:
        print("✗ Error: DATABASE_URL not set in environment variables")
        sys.exit(1)
    
    print(f"Connecting to database...")
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    print("✓ Database connection established")
    print()
    
    # Process each JSON file
    total_inserted = 0
    total_skipped = 0
    total_tweets = 0
    
    async with async_session() as session:
        for json_file in sorted(json_files):
            print(f"Processing: {json_file.name}")
            
            # Load tweets from file
            tweets = await load_json_file(json_file)
            total_tweets += len(tweets)
            print(f"  Loaded {len(tweets)} tweets from file")
            
            # Import to database
            inserted, skipped = await import_tweets_to_db(session, tweets, json_file.stem)
            total_inserted += inserted
            total_skipped += skipped
            
            print(f"  Inserted: {inserted}, Skipped (duplicates): {skipped}")
            print()
    
    # Print summary
    print("=" * 70)
    print("Import Summary")
    print("=" * 70)
    print(f"Total files processed: {len(json_files)}")
    print(f"Total tweets found: {total_tweets}")
    print(f"Successfully inserted: {total_inserted}")
    print(f"Skipped (duplicates): {total_skipped}")
    print()
    
    if total_inserted > 0:
        print("✓ Data import completed successfully!")
    else:
        print("! No new data was imported (all tweets already exist in database)")
    
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
