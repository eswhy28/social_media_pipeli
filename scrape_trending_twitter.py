"""
Smart Twitter Scraper Based on Trending Topics
Uses Google Trends to find what's trending in Nigeria,
then scrapes relevant tweets (budget: $0.40 = ~1000 tweets)
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.apify_service import get_apify_service
from app.services.google_trends_service import get_google_trends_service
from app.services.database_storage_service import DatabaseStorageService
from app.database import get_db
from app.config import settings


async def get_trending_topics():
    """Get trending topics from Google Trends for Nigeria"""
    print("📊 Fetching trending topics from Google Trends (Nigeria)...")
    
    trends_service = get_google_trends_service()
    trending = await trends_service.get_trending_searches(region="NG")
    
    if not trending:
        print("⚠️  No trending topics found, using curated Nigerian hashtags")
        # Curated Nigerian hashtags with high engagement
        return [
            "#Nigeria",
            "#NigeriaNews", 
            "#Lagos",
            "#NigerianTwitter",
            "#Naija"
        ]
    
    # Extract top trending terms and convert to hashtags
    hashtags = []
    for trend in trending[:5]:  # Top 5 trends
        term = trend.get('term', '')
        if term:
            # Add # if not already present
            hashtag = term if term.startswith('#') else f"#{term.replace(' ', '')}"
            hashtags.append(hashtag)
    
    print(f"✅ Found {len(hashtags)} trending topics: {', '.join(hashtags)}")
    return hashtags


async def scrape_twitter_by_trends(max_tweets=1000):
    """
    Scrape Twitter based on trending topics
    
    Args:
        max_tweets: Maximum tweets to scrape (default: 1000 = $0.40 at $0.40/1000 tweets)
    """
    print("\n" + "="*70)
    print("🐦 SMART TWITTER SCRAPER - TRENDING TOPICS")
    print("="*70)
    print(f"Budget: $0.40 (up to {max_tweets} tweets)")
    print(f"Target: Nigerian trending topics")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("="*70 + "\n")
    
    # Step 1: Get trending topics
    trending_hashtags = await get_trending_topics()
    
    # Step 2: Scrape Twitter
    print(f"\n🔍 Scraping Twitter for trending topics...")
    print(f"Queries: {', '.join(trending_hashtags)}")
    print(f"Max tweets per query: {max_tweets // len(trending_hashtags)}")
    
    apify_service = get_apify_service()
    
    # Distribute tweet limit across all hashtags
    tweets_per_hashtag = max_tweets // len(trending_hashtags)
    
    result = await apify_service.scrape_twitter_search(
        search_queries=trending_hashtags,
        max_tweets=max_tweets  # Total limit
    )
    
    # Step 3: Display results
    print("\n" + "="*70)
    print("📈 SCRAPING RESULTS")
    print("="*70)
    
    if result.get('error'):
        print(f"❌ Error: {result['error']}")
        return None
    
    tweets = result.get('tweets', [])
    total_tweets = len(tweets)
    
    print(f"✅ Successfully scraped: {total_tweets} tweets")
    print(f"💰 Estimated cost: ${(total_tweets / 1000) * 0.40:.4f}")
    print(f"📊 Platform: {result.get('platform')}")
    print(f"🔍 Queries used: {', '.join(result.get('queries', []))}")
    
    if total_tweets > 0:
        print(f"\n📝 Sample tweet:")
        sample = tweets[0]
        print(f"   Author: @{sample.get('author', 'N/A')}")
        print(f"   Content: {sample.get('content', '')[:100]}...")
        print(f"   Likes: {sample.get('metrics', {}).get('likes', 0)}")
        print(f"   Retweets: {sample.get('metrics', {}).get('retweets', 0)}")
        print(f"   Hashtags: {', '.join(sample.get('hashtags', [])[:5])}")
    
    return result


async def store_tweets_to_database(tweets_data):
    """Store scraped tweets in the database"""
    if not tweets_data or tweets_data.get('error'):
        print("\n⚠️  No data to store")
        return 0
    
    tweets = tweets_data.get('tweets', [])
    if not tweets:
        print("\n⚠️  No tweets to store")
        return 0
    
    print(f"\n💾 Storing {len(tweets)} tweets to database...")
    
    try:
        # Get database session
        db_gen = get_db()
        db = await db_gen.__anext__()
        
        # Initialize storage service
        storage_service = DatabaseStorageService(db)
        
        # Store tweets
        stored_count = await storage_service.store_twitter_posts(tweets)
        
        # Commit changes
        await db.commit()
        
        print(f"✅ Successfully stored {stored_count} tweets to database")
        
        # Close database session
        await db.close()
        
        return stored_count
        
    except Exception as e:
        print(f"❌ Error storing tweets: {e}")
        import traceback
        traceback.print_exc()
        return 0


async def main():
    """Main execution function"""
    print("\n" + "="*70)
    print("🚀 TRENDING TWITTER SCRAPER FOR NIGERIA")
    print("="*70)
    
    # Check if API token is configured
    if not settings.APIFY_API_TOKEN:
        print("❌ ERROR: APIFY_API_TOKEN not configured in environment variables")
        print("Please set APIFY_API_TOKEN in your .env file")
        return
    
    print("✅ Apify API token configured")
    print("✅ Actor: apidojo/tweet-scraper (Tweet Scraper V2)")
    print("✅ Pricing: $0.40 per 1000 tweets")
    print("✅ Budget allocation: $0.40")
    
    try:
        # Step 1: Scrape Twitter based on trending topics
        result = await scrape_twitter_by_trends(max_tweets=1000)
        
        if not result:
            print("\n❌ Scraping failed")
            return
        
        # Step 2: Store in database
        stored = await store_tweets_to_database(result)
        
        # Step 3: Summary
        print("\n" + "="*70)
        print("📊 FINAL SUMMARY")
        print("="*70)
        print(f"✅ Tweets scraped: {len(result.get('tweets', []))}")
        print(f"✅ Tweets stored: {stored}")
        print(f"💰 Estimated cost: ${(len(result.get('tweets', [])) / 1000) * 0.40:.4f}")
        print(f"📅 Timestamp: {datetime.now().isoformat()}")
        print("="*70)
        
        print("\n🎉 Scraping complete! Check your database for the tweets.")
        
    except Exception as e:
        print(f"\n❌ Error during scraping: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════════════════════════════╗
    ║  SMART TWITTER SCRAPER - TRENDING TOPICS (NIGERIA)               ║
    ║                                                                  ║
    ║  • Gets trending topics from Google Trends                      ║
    ║  • Scrapes Twitter for those topics                             ║
    ║  • Stores tweets in PostgreSQL database                         ║
    ║  • Budget: $0.40 (up to 1000 tweets)                            ║
    ╚══════════════════════════════════════════════════════════════════╝
    """)
    
    asyncio.run(main())
