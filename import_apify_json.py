"""
Import real Apify data from JSON file to test transformation
This will help us verify the data transformation is working correctly
"""
import asyncio
import json
import sys
sys.path.insert(0, '.')

from app.services.apify_service import get_apify_service
from app.services.database_storage_service import DatabaseStorageService
from app.database import get_db

async def import_apify_json():
    """Import tweets from the Apify JSON dataset"""
    
    print("🔄 Loading tweets from Apify JSON dataset...")
    
    # Load the JSON file
    with open('dataset_tweet-scraper_2025-11-21_21-51-32-246.json', 'r', encoding='utf-8') as f:
        raw_tweets = json.load(f)
    
    print(f"✅ Loaded {len(raw_tweets)} tweets from JSON file")
    
    # Transform using Apify service
    apify_service = get_apify_service()
    transformed_tweets =  apify_service._transform_twitter_data(raw_tweets)
    
    print(f"✅ Transformed {len(transformed_tweets)} tweets")
    
    # Display sample transformed tweet
    if transformed_tweets:
        print("\n📝 Sample Transformed Tweet:")
        sample = transformed_tweets[0]
        print(f"   Author: @{sample.get('author')}")
        print(f"   Name: {sample.get('author_name')}")
        print(f"   Content: {sample.get('content')[:150]}...")
        print(f"   Likes: {sample.get('metrics', {}).get('likes')}")
        print(f"   Retweets: {sample.get('metrics', {}).get('retweets')}")
        print(f"   Hashtags: {sample.get('hashtags')}")
        print(f"   Posted: {sample.get('posted_at')}")
        print(f"   Has Raw Data: {bool(sample.get('raw_data'))}")
    
    # Store in database
    print(f"\n💾 Storing {len(transformed_tweets)} tweets to database...")
    
    db_gen = get_db()
    db = await db_gen.__anext__()
    
    storage_service = DatabaseStorageService(db)
    stored_count = await storage_service.store_twitter_posts(transformed_tweets)
    
    print(f"✅ Stored {stored_count} tweets to database")
    
    await db.close()
    
    print("\n🎉 Import complete! Run check_db_data.py to view the stored data")

if __name__ == "__main__":
    asyncio.run(import_apify_json())
